import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dependencies_check import check, fingerprint


class DependencyChecks(unittest.TestCase):
    def git(self, folder, *args):
        return subprocess.check_output(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                                        "-C", str(folder), *args], text=True, stderr=subprocess.PIPE).strip()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hunter-dependency-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.child = self.root / "libraries/Example"
        self.child.mkdir(parents=True)
        for folder in (self.root, self.child):
            self.git(folder, "init", "-q", "-b", "main")
            self.git(folder, "config", "core.autocrlf", "false")
        (self.child / "src").mkdir()
        self.header = self.child / "src/API.h"
        self.header.write_bytes(b"void function();\n")
        (self.child / "library.json").write_text('{"name":"Example"}', encoding="utf-8")
        (self.child / ".gitignore").write_bytes(b"src/ignored.cpp\n")
        self.git(self.child, "add", "--", "src/API.h", "library.json", ".gitignore")
        self.git(self.child, "commit", "-q", "-m", "fixture")
        self.sha = self.git(self.child, "rev-parse", "HEAD")
        self.git(self.root, "update-index", "--add", "--cacheinfo", "160000," + self.sha + ",libraries/Example")
        (self.root / ".gitmodules").write_text('[submodule "example"]\n path = libraries/Example\n url = https://example.invalid/Example.git\n', encoding="utf-8")
        self.lock = {"formatVersion": 2, "libraries": {"Example": {"path": "libraries/Example", "submodule": "example",
            "url": "https://example.invalid/Example.git", "revision": self.sha,
            "files": {"src/API.h": fingerprint(self.header), "library.json": fingerprint(self.child / "library.json")}}}}
        self.save()

    def save(self):
        (self.root / "dependencies.lock.json").write_text(json.dumps(self.lock), encoding="utf-8")

    def test_clean_pinned_source_passes(self):
        check(self.root)

    def test_windows_line_endings_pass_with_matching_git_settings(self):
        self.git(self.child, "config", "core.autocrlf", "true")
        self.header.unlink()
        self.git(self.child, "checkout", "--", "src/API.h")
        self.assertIn(b"\r\n", self.header.read_bytes())
        check(self.root)

    def test_content_hash_mismatch_fails(self):
        self.lock["libraries"]["Example"]["files"]["src/API.h"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "modified"):
            check(self.root)

    def test_dirty_source_fails(self):
        self.header.write_text("void changed();", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "local changes"):
            check(self.root)

    def test_ignored_extra_source_fails(self):
        (self.child / "src/ignored.cpp").write_text("void surprise() {}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "extra"):
            check(self.root)

    def test_new_commit_with_identical_sources_still_needs_recorded_pin(self):
        self.git(self.child, "commit", "--allow-empty", "-q", "-m", "metadata checkpoint")
        with self.assertRaisesRegex(ValueError, "checked-out revision"):
            check(self.root)

    def test_changed_lock_without_gitlink_update_fails(self):
        self.lock["libraries"]["Example"]["revision"] = "0" * 40
        self.save()
        with self.assertRaisesRegex(ValueError, "gitlink differs"):
            check(self.root)

    def test_missing_checkout_fails(self):
        target = self.root / "removed"
        self.child.resolve().relative_to(self.root)
        target.resolve().relative_to(self.root)
        self.child.rename(target)
        with self.assertRaisesRegex(ValueError, "submodule update --init"):
            check(self.root)


if __name__ == "__main__":
    unittest.main()

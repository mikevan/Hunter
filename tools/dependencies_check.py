"""Verify all shared-library build inputs against a product's content lock.

Usable as a PlatformIO pre-script or as `python tools/dependencies_check.py`.
Paths are relative to the product checkout. No download, checkout, or repair
is performed. A missing, modified, or extra library source stops the build.
"""
import hashlib
import json
from pathlib import Path
import sys
import subprocess


def fingerprint(path):
    data = path.read_bytes()
    if path.suffix.lower() in {".h", ".hpp", ".c", ".cpp", ".json", ".txt"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    result = subprocess.run(["git", "--no-optional-locks", "-c", "safe.directory=" + root.as_posix(),
                             "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Dependency Git lookup failed")
    return result.stdout.strip()


def verify_pin(root, name, spec):
    library = (root / spec["path"]).resolve()
    library.relative_to(root)
    prefix = "submodule." + spec["submodule"]
    for field, expected in (("path", spec["path"]), ("url", spec["url"])):
        if git(root, "config", "--file", ".gitmodules", "--get", prefix + "." + field) != expected:
            raise ValueError(name + ": submodule " + field + " differs from the lock")
    entry = git(root, "ls-files", "--stage", "--", spec["path"]).split()
    if len(entry) != 4 or entry[0] != "160000" or entry[2] != "0" or entry[3] != spec["path"] or entry[1] != spec["revision"]:
        raise ValueError(name + ": recorded gitlink differs from the lock")
    if not (library / ".git").exists():
        raise ValueError(name + ": missing checkout; run git submodule update --init --recursive")
    if Path(git(library, "rev-parse", "--show-toplevel")).resolve() != library:
        raise ValueError(name + ": dependency is not its own Git checkout")
    if git(library, "rev-parse", "HEAD") != spec["revision"]:
        raise ValueError(name + ": checked-out revision differs from the lock")
    if git(library, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError(name + ": dependency has local changes or untracked files")
    return library


def check(root):
    root = Path(root).resolve()
    lock = json.loads((root / "dependencies.lock.json").read_text(encoding="utf-8"))
    if lock.get("formatVersion") != 2:
        raise ValueError("Expected Git-pinned dependency lock format version 2")
    errors = []
    for name, spec in lock["libraries"].items():
        library = verify_pin(root, name, spec)
        want = spec["files"]
        have = {p.relative_to(library).as_posix() for p in (library / "src").rglob("*") if p.is_file()}
        have.add("library.json")
        if have != set(want):
            errors.append(f"{name}: missing {sorted(set(want)-have)}, extra {sorted(have-set(want))}")
        for relative in sorted(have & set(want)):
            p = library / relative
            if not p.is_file() or fingerprint(p) != want[relative]:
                errors.append(f"{name}: missing or modified {relative}")
    if errors:
        raise ValueError("Shared-library lock failed:\n" + "\n".join(errors))
    print("Shared-library lock verified: " + ", ".join(lock["libraries"]))


try:
    Import("env")  # noqa: F821 - PlatformIO/SCons
except NameError:
    env = None

if env is not None:
    try:
        check(Path(env.subst("$PROJECT_DIR")))
    except (OSError, ValueError, KeyError) as error:
        print(str(error))
        env.Exit(1)
elif __name__ == "__main__":
    try:
        check(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)

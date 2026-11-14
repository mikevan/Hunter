# Hunter

People need evidence they can keep, examine, and use to make informed decisions. Hunter puts wireless observation in their hands, making otherwise unseen activity available for local recording and analysis.

Hunter passively records supported Wi-Fi/BLE observations and preserves evidence locally. Vixen uses those observations for analysis; T-Ultra supplies an independent record for comparison. A detected signature is an indicator, not proof of who operates a device or what they intend.

This repository provides the dedicated capture product. Its contribution is accountable evidence: what was observed, when it was observed, and what was actually saved.

LilyGO T-Dongle-C5 sensor, SD logging, PCAP evidence and card-transfer product. The Hunter logo is unchanged.

Clone with `git clone --recurse-submodules https://github.com/mikevan/Hunter.git`, or run `git submodule update --init --recursive` in an existing checkout. Core and C5 board support live under `libraries/`; Sensors lives under `sensors/`. No sibling repositories are required.

Run `python tools/dependencies_check.py` before building. The build checks the recorded Git commits, clean dependency worktrees and the existing content hashes. Update each gitlink and its lock entry together when adopting a new library revision.

Run native host checks with `python test/run_host_tests.py` using a C++17 compiler.

Build with `pio run -e tdongle_c5_hunter`. No hardware is flashed by a build. The legacy `tdongle_c5_vixen` environment is the old fox-hunt beacon, not the Vixen flagship.

Source ancestry is recorded in `EXTRACTION.json`; original Git history remains in LayerTime. EXTRACTION.json records the initial local preparation; subsequent checkpoints are recorded in Git history.

GitHub Actions runs dependency guard tests, host checks and a clean firmware build on every push and pull request. Successful runs retain firmware, ELF files and logs for 14 days. Shared-library candidate runs test temporary pins without updating this product. See the [hardware acceptance checklist](https://github.com/mikevan/LayerTime/blob/main/docs/firmware/hardware-acceptance.md).

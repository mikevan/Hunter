# Hunter

LilyGO T-Dongle-C5 sensor, SD logging, PCAP evidence and card-transfer product. The Hunter logo is unchanged.

Keep LayerTime-Core, LayerTime-C5 and LayerTime-Sensors as sibling checkouts. Run `python tools/dependencies_check.py` before building. The build repeats this content-lock check.

Run native host checks with `python test/run_host_tests.py` using a C++17 compiler.

Build with `pio run -e tdongle_c5_hunter`. No hardware is flashed by a build. The legacy `tdongle_c5_vixen` environment is the old fox-hunt beacon, not the Vixen flagship.

Source ancestry is recorded in `EXTRACTION.json`; original Git history remains in LayerTime. EXTRACTION.json records the initial local preparation; subsequent checkpoints are recorded in Git history.

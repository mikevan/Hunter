# Hunter BLE stability after Start

On November 25, 2026, Vixen diagnostic build 150 closed its connection eight seconds after Hunter stopped sending Status updates. Hunter accepted Start, continued scanning and recorded hundreds of refused Data notifications. In that run, free internal heap fell to about 11.4 KB shortly after Start.

The Hunter run dump now allocates its event snapshot in PSRAM when requested and frees it after printing. The 40-record snapshot occupied 6,240 bytes of internal RAM with the expanded event schema. Events are copied under the existing lock and printed after releasing it. If the allocation fails, Hunter reports that the event snapshot is unavailable and continues the rest of the dump.

## Bench result

The instrumented Hunter build ran on the same T-Dongle-C5 with Vixen build 150. It held about 18 KB of free internal heap during Wi-Fi scanning. Vixen received Status and Data for 15 minutes with the phone awake and another 15 minutes with the phone locked in Android's dozing state. It reported zero stale warnings or unplanned reconnects. A deliberate disconnect followed by Connect restored Status updates. Hunter's USB serial capture ended about four minutes into the endurance run. Vixen's log covers both intervals and the reconnect.

The traced build reported brief NimBLE resource-exhaustion errors during BLE scans and recovered. A controlled change to Wi-Fi initialization order alone did not reproduce the original drop. The bench evidence supports reducing internal RAM pressure. It does not identify the exact source revision of the failing image or establish a concurrency fault as the trigger.

## Build provenance

- Hunter source base `f6f75de`, with the event-snapshot fix and existing evidence-session edits.
- Bench dependency revisions `034af47` for LayerTime-Core, `652eb8d` for LayerTime-C5 and `0097b6d` for LayerTime-Sensors.
- Instrumented Hunter firmware SHA-256 `f880fc416d933d49a6082484bffb0ade66f9b436881111c48b8cb685cd4de5d7`. The bench checkout passed 518 Hunter host checks.
- Normal Hunter firmware SHA-256 `394afc357749df7950f5ded77833eab4e64c941feea4e0c7b6841e7ae51c67b0`. The endurance result above applies to the instrumented image.

The bench used USB power for both devices. The captured logs are retained privately because they can contain device identifiers.

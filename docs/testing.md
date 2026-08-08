# Test evidence and current boundary

This document separates real prototype evidence from configuration/build-only checks. It intentionally does not turn an untested assumption into a compatibility claim.

## Real hardware evidence

The prototype was exercised with firmware 1.5.4 and later 1.5.6 on a Seeed Studio XIAO ESP32C6 connected to the documented fan electronics.

| Test | Observed result |
|---|---|
| Power button emulation | 50 ms active-low/open-drain pulse started the stopped fan at Stage 1 |
| Speed button emulation | One pulse advanced Stage 1 → Stage 2; outputs released afterward |
| Power-off emulation | One Power pulse stopped the running fan |
| Targeted stages | `3 → 1`, `1 → 2`, `2 → 3` reached the expected measured clusters without routine power reset |
| Rapid latest-target burst | `Stage 1 → Stage 3 → Off` within 0.99 s ended physically Off |
| Rapid speed burst | `Off → Stage 1 → Stage 2 → Stage 3` within 1.08 s ended at Stage 3, about 7.92 V |
| Hardware feedback | Original-button changes were reflected back into the ESPHome/Home Assistant fan state without generating a new button pulse |
| Charging state | Off during USB charging (4.636–4.683 V) remained distinguishable from Stage 1 (4.941–4.980 V) in the tested setup |
| Connectivity | Encrypted ESPHome Native API reconnect and OTA update succeeded |

Measured running clusters were approximately 4.94–4.98 V, 6.51–6.54 V and 7.91–7.96 V for Stages 1–3.

## Firmware 1.5.5 verification history

Firmware 1.5.5 adds a feedback guard to the low-battery sleep path and removes a prototype-only migration. The public configuration was:

- validated locally with ESPHome 2026.6.5;
- fully compiled locally for ESP32-C6;
- fully validated and compiled again in GitHub Actions.

At initial publication, 1.5.5 had **not** yet been installed and exercised on the physical prototype. The real command-burst evidence above therefore belongs to 1.5.4; the relevant worker logic is otherwise unchanged.

## Firmware 1.5.6 diagnostic verification

Firmware 1.5.6 was validated and fully compiled locally with ESPHome 2026.7.4 / ESP-IDF 5.5.5, then installed over encrypted LAN OTA on the real prototype. The live device reported configuration hash `0xccb9c359`.

The diagnostic release adds structured event logs for:

- incoming state/speed requests and request generations;
- worker start/end and freshly classified motor voltage;
- start and end of every 50 ms Power/Speed pulse;
- stable physical-feedback changes and UI synchronization;
- low-battery samples, recovery and deep-sleep entry;
- boot/reset reason, heap metrics and maximum main-loop time.

A persistent encrypted Native API collector captured a real `Off → Stage 1 → Off` test. Both directions logged request, fresh ADC classification, pulse start/end, worker completion and delayed hardware-feedback confirmation. Physical evidence was Stage 1 at approximately 4.95 V and final Off at approximately 4.66 V. The controller remained Off after the test.

The built-in ESP-IDF task watchdog remains enabled with its ESPHome default timeout. The external stale-telemetry automation documented in [home-assistant.md](home-assistant.md) is still useful because a scheduler/component stall can leave network tasks alive without necessarily starving the outer watched task.

## Firmware 1.5.7 Off-to-Stage-3 regression test

Firmware 1.5.7 fixes a dynamic-repeat-count defect found through the 1.5.6 event logs. ESPHome reevaluates a lambda-based `repeat.count` after every pass. Because the earlier expression derived the remaining count from an estimate that advanced after each pulse, a direct `Off → Stage 3` request stopped after one Speed pulse and physically reached only Stage 2.

The worker now snapshots the requested state/stage and the complete Speed-pulse count at worker start. A newer request remains pending as a later generation instead of changing the running sequence.

The fix was validated and compiled with ESPHome 2026.7.4 / ESP-IDF 5.5.5, installed over encrypted LAN OTA, and tested on the physical prototype:

- initial state Off / hardware stage 0 at approximately 4.66 V;
- direct Home Assistant request to Stage 3;
- one complete Power pulse followed by exactly two complete Speed pulses;
- worker estimate and filtered hardware feedback both reached Stage 3;
- measured motor rail approximately 7.912 V;
- final Power-off test returned to hardware stage 0 at approximately 4.69 V.

## Checks still required for another build

- Measure button idle/pressed levels and prove common ground before connecting GPIOs.
- Repeat motor-voltage clusters with the actual charger, cable, battery state and temperature range.
- Calibrate both ADC dividers against a trusted multimeter.
- Check for PWM/ripple with an oscilloscope when thresholds are narrow.
- Perform a controlled full undervoltage/deep-sleep/recovery test.
- Verify enclosure insulation, strain relief, clearance from moving parts and thermal behavior.

Unknown or overlapping voltage clusters must remain telemetry-only; never replace missing evidence with blind toggle sequences.
# Test evidence and current boundary

This document separates real prototype evidence from configuration/build-only checks. It intentionally does not turn an untested assumption into a compatibility claim.

## Real hardware evidence

The prototype was exercised with firmware 1.5.4 on a Seeed Studio XIAO ESP32C6 connected to the documented fan electronics.

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

## Firmware 1.5.5 verification

Firmware 1.5.5 adds a feedback guard to the low-battery sleep path and removes a prototype-only migration. The public configuration was:

- validated locally with ESPHome 2026.6.5;
- fully compiled locally for ESP32-C6;
- fully validated and compiled again in GitHub Actions.

At initial publication, 1.5.5 had **not** yet been installed and exercised on the physical prototype. The real command-burst evidence above therefore belongs to 1.5.4; the relevant worker logic is otherwise unchanged.

## Checks still required for another build

- Measure button idle/pressed levels and prove common ground before connecting GPIOs.
- Repeat motor-voltage clusters with the actual charger, cable, battery state and temperature range.
- Calibrate both ADC dividers against a trusted multimeter.
- Check for PWM/ripple with an oscilloscope when thresholds are narrow.
- Perform a controlled full undervoltage/deep-sleep/recovery test.
- Verify enclosure insulation, strain relief, clearance from moving parts and thermal behavior.

Unknown or overlapping voltage clusters must remain telemetry-only; never replace missing evidence with blind toggle sequences.
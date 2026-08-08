# Calibration and thresholds

Do not copy the included thresholds blindly to another fan.

## Measurement procedure

1. Deploy the motor-voltage sensor as telemetry only.
2. Record the ADC midpoint and reconstructed motor rail with the fan Off and at every speed.
3. Repeat with no charger and while charging.
4. Repeat at low, medium and high cell voltage when practical.
5. Capture ranges, not single readings; check for PWM with an oscilloscope if available.
6. Place initial thresholds at gaps between non-overlapping clusters.
7. Add hysteresis and stable-sample confirmation.

## Prototype thresholds

Initial cluster midpoints used by the immediate command path:

- Off / Stage 1: 4.804 V
- Stage 1 / Stage 2: 5.727 V
- Stage 2 / Stage 3: 7.213 V

The slow telemetry classifier uses state-dependent Schmitt thresholds. In particular, it enters Stage 1 from Off at 4.84 V and returns to Off below 4.77 V.

## Failure policy

If values enter an ambiguous gap, drift toward a threshold, or supported operating modes overlap, keep the state unknown/telemetry-only. Never emit a blind toggle sequence from an unknown stage.

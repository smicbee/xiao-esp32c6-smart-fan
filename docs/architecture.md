# Control architecture

![Architecture](diagrams/system-architecture.svg)

## Why optimistic control was not enough

The fan's original controls are toggle/cycle buttons. Home Assistant state can lag, an original hardware-button press bypasses Home Assistant, and the motor-voltage telemetry intentionally waits for stable samples. A naïve `mode: restart` script can be interrupted after a real pulse but before its software state is updated.

## Latest-target generation worker

The firmware keeps three monotonically compared values:

- `request_generation`: incremented by user state/speed events;
- `processing_generation`: captured at the beginning of a worker pass;
- `handled_generation`: advanced only to the captured generation after a valid pass.

A request arriving during an active pass therefore remains pending. The next pass obtains a new D1 measurement instead of continuing an obsolete plan.

## Two measurement paths

- **Command snapshot:** existing ADC is force-updated; `on_raw_value` captures the 16-sample average before temporal median filtering.
- **Public/authoritative telemetry:** multiply + five-value median + hysteresis + five consecutive classifications.

Hardware reconciliation is guarded so publication cannot become a command.

## Low-battery state flow

```text
Battery ADC every 5 s
        │
        ├─ value ≥ 3.10 V → reset consecutive-low counter
        │
        └─ value < 3.05 V → increment counter
                                  │
                             three samples
                                  │
                  stop command worker; enable feedback guard
                                  │
                  publish Fan=Off without a button pulse
                                  │
                         enter deep sleep for 60 s
                                  │
                         timer wake and fresh ADC read
                                  │
                 < 3.35 V ───────┴─────── ≥ 3.35 V
                 sleep again                normal boot
```

This firmware path supplements the original cell protection. It is not a charger, BMS or continuously awake undervoltage supervisor.

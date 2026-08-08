# Home Assistant

ESPHome exposes a native three-speed `fan` entity plus:

- motor voltage;
- confirmed hardware stage 0–3;
- hardware running state;
- battery voltage;
- estimated battery percentage;
- temperature and pressure;
- Wi-Fi diagnostics and uptime.

Use the standard Home Assistant fan tile/card with its native speed control. No helper buttons or stage scripts are required. The frontend sends intent; the controller determines the physical transition from a fresh hardware measurement.

The API is encrypted. Keep the Noise PSK and OTA password only in local `secrets.yaml`. Do not place them in dashboards, automations or Git.

## Optional stale-telemetry recovery

ESPHome enables the ESP-IDF Task Watchdog for the loop task. That watchdog catches a task which stops yielding, but it cannot prove that every ESPHome scheduler component continues to execute. A device can therefore remain reachable while sensor intervals and actuator automations have stopped.

The automation below detects that narrower failure mode through the uptime entity. It deliberately does **not** restart a device which is `unavailable`, because that may be intentional battery-protection deep sleep. It requests one controller restart after three stale minutes, waits for fresh telemetry, creates a persistent notification only if recovery fails, and then remains busy for ten minutes to prevent a reboot loop.

Entity IDs are installation-specific; select the uptime sensor and ESPHome restart button created for your device.

```yaml
alias: Fan Controller – Telemetry Watchdog
description: Recover an API-reachable controller whose ESPHome scheduler stopped publishing.
mode: single
max_exceeded: silent
triggers:
  - trigger: time_pattern
    minutes: /1
conditions:
  - condition: template
    value_template: >
      {% set s = states.sensor.xiao_esp32c6_smart_fan_uptime %}
      {{ s is not none
         and s.state not in ['unknown', 'unavailable', 'none']
         and states('button.xiao_esp32c6_smart_fan_restart') != 'unavailable'
         and (as_timestamp(now()) - as_timestamp(s.last_updated)) > 180 }}
actions:
  - variables:
      watchdog_before_updated: >
        {{ as_timestamp(states.sensor.xiao_esp32c6_smart_fan_uptime.last_updated) }}
  - action: button.press
    target:
      entity_id: button.xiao_esp32c6_smart_fan_restart
  - wait_template: >
      {% set s = states.sensor.xiao_esp32c6_smart_fan_uptime %}
      {{ s is not none
         and s.state not in ['unknown', 'unavailable', 'none']
         and as_timestamp(s.last_updated) > (watchdog_before_updated | float(0)) }}
    timeout: 00:01:30
    continue_on_timeout: true
  - choose:
      - conditions:
          - condition: template
            value_template: '{{ not wait.completed }}'
        sequence:
          - action: persistent_notification.create
            data:
              notification_id: fan_controller_watchdog_failed
              title: Fan controller did not recover
              message: >
                The telemetry watchdog requested a controller restart but received
                no fresh uptime value within 90 seconds. Check power and ESPHome.
  - delay: 00:10:00
```

Do not use this pattern for a controller whose boot path can actuate hardware. Verify first that reboot leaves all button outputs released and does not restore an unsafe command.

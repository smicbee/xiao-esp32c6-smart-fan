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

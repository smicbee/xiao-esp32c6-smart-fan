# XIAO ESP32C6 Smart Fan – deutsche Projektdokumentation

Dieses Projekt rüstet einen einfachen dreistufigen Akku-Tischventilator mit WLAN und Home Assistant nach. Die originale Motorsteuerung, Ladeelektronik, Zellschutzschaltung und die beiden Taster bleiben erhalten. Ein Seeed Studio XIAO ESP32C6 emuliert nur die aktiven Low-Taster und misst zusätzlich Motor- und Akkuspannung.

![Umgebauter Ventilator](images/fan-front.jpg)

## Funktionsumfang

- verschlüsselte ESPHome Native API und OTA
- native dreistufige Home-Assistant-Fan-Entity
- weiterhin nutzbare Originaltaster
- 50-ms-Impulse auf Power und Speed, anschließend elektrische Freigabe
- gezielte Stufenwechsel ohne routinemäßiges Aus-/Ein-Reset
- echte Stufenerkennung über Motor+ und Spannungsteiler an D1/GPIO1
- frische Istmessung vor jedem Controllerdurchlauf
- generationenbasierter Worker für schnelle Folgebefehle
- hardwarebasierte, impulsfreie Korrektur der HA-Anzeige
- BMP280 für Temperatur und Luftdruck
- Akkuspannung und geschätzter Ladezustand
- Unterspannungs-Deep-Sleep mit 60-s-Prüfintervall

## Wesentliche Architekturentscheidung

Home Assistant ist nur Sollwertgeber. Der Home-Assistant-Anzeigestand wird niemals als physischer Istzustand verwendet. Jede noch offene Sollanforderung führt zu einem neuen D1-ADC-Snapshot. Daraus berechnet der XIAO die minimale Aktion:

- **Aus → Zielstufe:** Power-Impuls, dann nötige Speed-Impulse
- **Stufe X → Stufe Y:** nur zyklisch nötige Speed-Impulse
- **Laufend → Aus:** genau ein Power-Impuls

Während eines 50-ms-Impulses besitzt genau ein Worker die Ausgänge. Neue Befehle erhöhen eine Generation und bleiben offen. Nach Abschluss erfolgt eine neue Istmessung für den neuesten Sollwert. Die langsame gefilterte Rückmeldung darf Home Assistant aktualisieren, aber niemals selbst einen Tasterimpuls auslösen.

## Hardware und Verdrahtung

Siehe [wiring.md](wiring.md) und [../hardware/BOM.csv](../hardware/BOM.csv).

![Verdrahtungsplan](diagrams/wiring.svg)

### Spannungsteiler

Motorfeedback:

```text
Motor+ ── 150 kΩ ──┬── D1 / GPIO1
                    │
                   22 kΩ
                    │
GND / Motor− ───────┴── GND
```

Akkumessung:

```text
BAT+ ── 220 kΩ ──┬── D0 / GPIO0
                  │
                 220 kΩ
                  │
BAT− / GND ───────┴── GND
```

Die Motor-Rückrechnung verwendet `(150k + 22k) / 22k ≈ 7,818`. Motor+ darf niemals direkt mit D1 verbunden werden.

## Gemessene Spannungen

| Zustand | Motorspannung |
|---|---:|
| Aus ohne USB in einer Messreihe | ca. 3,565 V |
| Aus während USB-Ladung | 4,636–4,683 V |
| Stufe 1 | 4,941–4,980 V |
| Stufe 2 | 6,513–6,536 V |
| Stufe 3 | 7,912–7,960 V |

Die Trennung zwischen USB-Aus und Stufe 1 ist knapp. Deshalb müssen andere Geräte zunächst passiv vermessen und neu kalibriert werden. Details: [calibration.md](calibration.md).

## Inbetriebnahme

1. Spannungen, gemeinsame Masse und Tasterpegel am eigenen Gerät messen.
2. Zunächst nur passive Telemetrie aktivieren und alle Zustände mit/ohne Ladegerät erfassen.
3. `esphome/secrets.example.yaml` nach `esphome/secrets.yaml` kopieren und eigene Werte einsetzen.
4. Einmalig per USB flashen.
5. WLAN, verschlüsselte API und OTA sofort real prüfen.
6. Danach direkt über WLAN weiterentwickeln; USB nur für Recovery/Seriell verwenden.
7. In Home Assistant die native Fan-Entity verwenden. Zusätzliche Stufenbuttons sind nicht nötig.

## Grenzen und Sicherheit

- Li-Ion-Geräte nur mit geeigneter Messtechnik und Brandschutz öffnen/modifizieren.
- Originale Lade- und Schutzschaltung nicht ersetzen oder umgehen.
- XIAO nicht direkt aus der Zelle an 3V3/5V speisen.
- Bei Tasterspannungen oberhalb der GPIO-Grenzen eine Transistor-/MOSFET-/Optokopplerstufe verwenden.
- Die vorhandenen Schwellwerte gelten nur für den vermessenen Prototyp.
- Akkuprozent ist eine Spannungsschätzung, keine Coulomb-Zählung.
- Deep Sleep ersetzt nicht den Hardware-Zellschutz.

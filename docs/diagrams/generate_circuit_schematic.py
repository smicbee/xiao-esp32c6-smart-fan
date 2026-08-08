#!/usr/bin/env python3
"""Generate the public electrical schematic with Schemdraw 0.21.

Blocks and pin rows use explicit coordinates. Schemdraw supplies the circuit
symbols and SVG renderer; fixed geometry prevents automatic IC-label placement
from changing the layout between renderer versions.
"""

from pathlib import Path

import schemdraw
import schemdraw.elements as elm

OUT = Path(__file__).with_name("circuit-schematic.svg")

INK = "#16303f"
BLUE = "#006b8f"
PURPLE = "#6840a0"
ORANGE = "#b76600"
RED = "#bd3038"
GREEN = "#087c54"
GRAY = "#516a77"
LIGHT = "#f5f8fa"
FAN_BG = "#effaf4"
SENSOR_BG = "#fff8ed"

schemdraw.config(unit=1.0, fontsize=14, color=INK, lw=2.0)
d = schemdraw.Drawing(show=False, file=OUT, backend="svg")
d.config(inches_per_unit=0.62, bgcolor="white", margin=0.35)


def box(x1: float, y1: float, x2: float, y2: float, color: str) -> None:
    """Draw an absolute, cursor-independent rectangular block outline."""
    d.add(elm.Line(color=color).at((x1, y1)).to((x2, y1)))
    d.add(elm.Line(color=color).at((x2, y1)).to((x2, y2)))
    d.add(elm.Line(color=color).at((x2, y2)).to((x1, y2)))
    d.add(elm.Line(color=color).at((x1, y2)).to((x1, y1)))

# ---------------------------------------------------------------------------
# Header
d += elm.Label("XIAO ESP32C6 smart fan — prototype schematic", fontsize=23, color=INK).at((8.3, 15.0))
d += elm.Label(
    "Button emulation and passive measurements only — the XIAO does not drive the motor",
    fontsize=13,
    color=GRAY,
).at((8.3, 14.55))

# ---------------------------------------------------------------------------
# 1. Button emulation
d += elm.Label("1  Original-button emulation", fontsize=19, color=INK).at((2.4, 13.85))

box(0.7, 10.8, 5.0, 13.25, INK)
box(11.6, 10.8, 15.9, 13.25, GREEN)
d += elm.Label("XIAO ESP32C6", fontsize=17, color=INK).at((2.85, 12.92))
d += elm.Label("open-drain GPIO", fontsize=12, color=GRAY).at((2.85, 12.56))
d += elm.Label("Original fan PCB", fontsize=17, color=INK).at((13.75, 12.92))
d += elm.Label("physical buttons remain installed", fontsize=12, color=GRAY).at((13.75, 12.56))

# Explicit straight signal rows.
for y, left_pin, function in (
    (11.85, "D6 / GPIO16", "POWER signal"),
    (11.25, "D5 / GPIO23", "SPEED signal"),
):
    d += elm.Label(left_pin, fontsize=13, color=BLUE).at((4.15, y + 0.14))
    d += elm.Line(color=BLUE).at((5.0, y)).to((11.6, y))
    d += elm.Label(function, fontsize=13, color=GREEN).at((12.55, y + 0.14))

d += elm.Label("50 ms LOW · output released to high impedance afterward", fontsize=12, color=BLUE).at((8.3, 13.42))

# Explicit common-ground path with one symbol and no signal crossings.
d += elm.Line(color=INK).at((2.85, 10.8)).to((2.85, 10.42))
d += elm.Line(color=INK).at((2.85, 10.42)).to((13.75, 10.42))
d += elm.Line(color=INK).at((13.75, 10.42)).to((13.75, 10.8))
d += elm.Ground(color=INK).at((8.3, 10.42))
d += elm.Label("verified common ground", fontsize=12, color=GRAY).at((8.3, 10.03))

# ---------------------------------------------------------------------------
# 2. Passive voltage measurements — independent rows and independent ground.
d += elm.Label("2  Passive voltage measurements", fontsize=19, color=INK).at((2.5, 9.5))

# Motor divider.
motor_y = 8.25
d += elm.Label("MOTOR+\nfan PCB", fontsize=13, color=GREEN).at((1.25, motor_y))
d += elm.Line(color=ORANGE).at((2.35, motor_y)).to((3.0, motor_y))
d += elm.Resistor(color=ORANGE).at((3.0, motor_y)).right(2.2).label("R1  150 kΩ", loc="top", fontsize=13)
motor_node = d.here
d += elm.Dot(color=ORANGE).at(motor_node)
d += elm.Line(color=ORANGE).at(motor_node).to((8.2, motor_y))
d += elm.Label("D1 / GPIO1\nADC", fontsize=13, color=BLUE).at((9.1, motor_y))
d += elm.Resistor(color=ORANGE).at(motor_node).down(1.25)
d += elm.Ground(color=INK)
d += elm.Label("R2  22 kΩ", fontsize=13, color=ORANGE).at((6.45, 7.55))
d += elm.Label("factor ≈ 7.818", fontsize=12, color=GRAY).at((12.2, motor_y))

# Battery divider.
battery_y = 5.95
d += elm.Label("BAT+\nfan PCB", fontsize=13, color=GREEN).at((1.25, battery_y))
d += elm.Line(color=RED).at((2.35, battery_y)).to((3.0, battery_y))
d += elm.Resistor(color=ORANGE).at((3.0, battery_y)).right(2.2).label("R3  220 kΩ", loc="top", fontsize=13)
battery_node = d.here
d += elm.Dot(color=ORANGE).at(battery_node)
d += elm.Line(color=ORANGE).at(battery_node).to((8.2, battery_y))
d += elm.Label("D0 / GPIO0\nADC", fontsize=13, color=BLUE).at((9.1, battery_y))
d += elm.Resistor(color=ORANGE).at(battery_node).down(1.25)
d += elm.Ground(color=INK)
d += elm.Label("R4  220 kΩ", fontsize=13, color=ORANGE).at((6.5, 5.25))
d += elm.Label("factor = 2.0", fontsize=12, color=GRAY).at((12.0, battery_y))

# Notes use open space to the right of each independent divider.
d += elm.Label("No 100 nF capacitor fitted at GPIO1", fontsize=11.5, color=GRAY).at((12.1, 7.55))
d += elm.Label("Never connect MOTOR+ or BAT+ directly to an ADC", fontsize=11.5, color=RED).at((12.0, 5.25))

# ---------------------------------------------------------------------------
# 3. BMP280 SPI — fixed matching pin rows, all horizontal.
d += elm.Label("3  BMP280 in SPI mode", fontsize=19, color=INK).at((2.0, 3.72))

box(0.7, 0.25, 5.0, 3.25, INK)
box(11.6, 0.25, 15.9, 3.25, ORANGE)
d += elm.Label("XIAO ESP32C6", fontsize=17, color=INK).at((2.85, 2.95))
d += elm.Label("BMP280 breakout", fontsize=17, color=INK).at((13.75, 2.95))

spi_rows = (
    (2.48, "D7 / GPIO17  MISO", "SDO / MISO", PURPLE),
    (2.05, "D8 / GPIO19  CS", "CSB", PURPLE),
    (1.62, "D9 / GPIO20  SCK", "SCL / SCK", PURPLE),
    (1.19, "D10 / GPIO18  MOSI", "SDA / MOSI", PURPLE),
    (0.76, "3V3", "VCC (3.3 V)", RED),
    (0.33, "GND", "GND", INK),
)
for y, xiao_pin, bmp_pin, color in spi_rows:
    d += elm.Label(xiao_pin, fontsize=12, color=color).at((3.72, y + 0.12))
    d += elm.Line(color=color).at((5.0, y)).to((11.6, y))
    d += elm.Label(bmp_pin, fontsize=12, color=color).at((12.6, y + 0.12))

# Footer: topology statements are separated from every circuit/net.
d += elm.Label(
    "XIAO power: USB-C only · no fan-battery feed to XIAO 3V3/5V · original charger, protection and motor driver unchanged",
    fontsize=11.5,
    color=GRAY,
).at((8.3, -0.22))
d += elm.Label(
    "Documented prototype only — re-measure button-pad voltage, common ground and divider values on every fan revision",
    fontsize=10.5,
    color=GRAY,
).at((8.3, -0.58))

d.save(OUT, transparent=False, dpi=180)
print(OUT)

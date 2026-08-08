#!/usr/bin/env python3
"""Capture ESPHome serial logs without asserting DTR/RTS."""
import argparse
import time
import serial

parser = argparse.ArgumentParser()
parser.add_argument("port", help="Serial port, for example /dev/ttyACM0 or COM3")
parser.add_argument("--seconds", type=float, default=30.0)
args = parser.parse_args()

ser = serial.Serial()
ser.port = args.port
ser.baudrate = 115200
ser.timeout = 0.25
ser.dtr = False
ser.rts = False
ser.open()
try:
    end = time.monotonic() + args.seconds
    while time.monotonic() < end:
        raw = ser.readline()
        if raw:
            print(raw.decode("utf-8", errors="replace").rstrip())
finally:
    ser.close()

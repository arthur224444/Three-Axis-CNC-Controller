"""Low-level USB-serial smoke test for the Pico 2 W firmware.

Prefer the FastAPI service in `cnc_api/` for normal use (see README.md).
This script is kept as a direct serial loop for firmware bring-up on a
desktop (hence COM3) without standing up the HTTP API.
"""

import time
import serial

ser = serial.Serial("/dev/ttyACM0", 115200, timeout=2)

MESSAGE_LENGTH = 10
MESSAGE_PADDING = "n"
MESSAGE_TIMEOUT_PER_COMMAND = 1
MESSAGE_TIMEOUT = MESSAGE_LENGTH * MESSAGE_TIMEOUT_PER_COMMAND

time.sleep(2)  # Pico resets when the port is opened

message = "SXxYysZz"
data = message.ljust(10, "n")[:10].encode("ascii")

try:
    while True:
        print("Sending data: ", data)
        ser.write(data)
        response = ser.read(1)
        print("Received: ", response)
        time.sleep(2)
finally:
    ser.close()

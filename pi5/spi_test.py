import time
import serial

ser = serial.Serial("/dev/ttyACM0", 115200, timeout=2)
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

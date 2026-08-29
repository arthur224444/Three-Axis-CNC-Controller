import spidev
import time

spi = spidev.SpiDev()

spi.open(0, 0)       # SPI bus 0, CE0
spi.max_speed_hz = 50000
spi.mode = 0

message = "HELLO"

# Make exactly 10 bytes
data = message.ljust(10, "n")[:10].encode("ascii")

try:
    while True:
        print("Sending data: ", data)
        spi.xfer2(data)
        time.sleep(2)
finally:
    spi.close()
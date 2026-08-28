import spidev
import time

spi = spidev.SpiDev()

spi.open(0, 0)       # SPI bus 0, CE0
spi.max_speed_hz = 500000
spi.mode = 0

message = "HELLO"

# Make exactly 10 bytes
data = message.ljust(10, "n")[:10].encode("ascii")

spi.xfer2(data)

spi.close()
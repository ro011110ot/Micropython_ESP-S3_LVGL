import time

import machine

t_sck = machine.Pin(12, machine.Pin.OUT)
t_mosi = machine.Pin(11, machine.Pin.OUT)
t_miso = machine.Pin(10, machine.Pin.IN)
t_cs = machine.Pin(4, machine.Pin.OUT, value=1)

spi = machine.SoftSPI(
    baudrate=50000, polarity=0, phase=0, sck=t_sck, mosi=t_mosi, miso=t_miso
)

print("Touch Test - 10 Messungen, bitte Display berühren...")

for i in range(10):
    # X lesen
    t_cs.value(0)
    time.sleep_us(100)
    spi.write(bytearray([0x90]))
    buf = bytearray(2)
    spi.readinto(buf)
    t_cs.value(1)
    x = ((buf[0] << 8) | buf[1]) >> 4

    # Y lesen
    t_cs.value(0)
    time.sleep_us(100)
    spi.write(bytearray([0xD0]))
    spi.readinto(buf)
    t_cs.value(1)
    y = ((buf[0] << 8) | buf[1]) >> 4

    print(f"  [{i + 1}] X={x}, Y={y}, MISO={t_miso.value()}")
    time.sleep_ms(500)

print("Fertig!")

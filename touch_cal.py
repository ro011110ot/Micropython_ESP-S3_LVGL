"""
Touch Kalibrierung - Tippe auf die angezeigten Ecken
und notiere die X/Y Rohwerte
"""
import time

import machine

t_sck = machine.Pin(12, machine.Pin.OUT)
t_mosi = machine.Pin(11, machine.Pin.OUT)
t_miso = machine.Pin(10, machine.Pin.IN)
t_cs = machine.Pin(4, machine.Pin.OUT, value=1)

spi = machine.SoftSPI(
    baudrate=50000, polarity=0, phase=0,
    sck=t_sck, mosi=t_mosi, miso=t_miso
)


def read_xy():
    t_cs.value(0)
    time.sleep_us(100)
    spi.write(bytearray([0x90]))
    buf = bytearray(2)
    spi.readinto(buf)
    t_cs.value(1)
    x = ((buf[0] << 8) | buf[1]) >> 4

    t_cs.value(0)
    time.sleep_us(100)
    spi.write(bytearray([0xD0]))
    spi.readinto(buf)
    t_cs.value(1)
    y = ((buf[0] << 8) | buf[1]) >> 4
    return x, y


def warte_auf_touch(label):
    print(f"\n>>> Bitte {label} berühren und gedrückt halten...")
    # Warte bis Touch erkannt
    while True:
        x, y = read_xy()
        if x != 2047 and 50 < x < 4000:
            # Mehrfach messen für Stabilität
            werte = []
            for _ in range(5):
                x, y = read_xy()
                if x != 2047:
                    werte.append((x, y))
                time.sleep_ms(50)
            if len(werte) >= 3:
                ax = sum(v[0] for v in werte) // len(werte)
                ay = sum(v[1] for v in werte) // len(werte)
                print(f"    -> Rohwert: X={ax}, Y={ay}")
                time.sleep_ms(500)  # Loslassen abwarten
                return ax, ay
        time.sleep_ms(100)


print("=" * 40)
print("TOUCH KALIBRIERUNG")
print("=" * 40)

tl_x, tl_y = warte_auf_touch("OBEN LINKS")
tr_x, tr_y = warte_auf_touch("OBEN RECHTS")
bl_x, bl_y = warte_auf_touch("UNTEN LINKS")
br_x, br_y = warte_auf_touch("UNTEN RECHTS")

print("\n" + "=" * 40)
print("ERGEBNISSE:")
print(f"  Oben Links  : X={tl_x}, Y={tl_y}")
print(f"  Oben Rechts : X={tr_x}, Y={tr_y}")
print(f"  Unten Links : X={bl_x}, Y={bl_y}")
print(f"  Unten Rechts: X={br_x}, Y={br_y}")

x_min = min(tl_x, bl_x)
x_max = max(tr_x, br_x)
y_min = min(tl_y, tr_y)
y_max = max(bl_y, br_y)

print("\nKalibrierungswerte für main.py:")
print(f"  X_MIN={x_min}, X_MAX={x_max}")
print(f"  Y_MIN={y_min}, Y_MAX={y_max}")
print("\nMapping Formel:")
print(f"  x = (raw_x - {x_min}) * 240 // ({x_max} - {x_min})")
print(f"  y = (raw_y - {y_min}) * 320 // ({y_max} - {y_min})")

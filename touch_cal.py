"""
Touch calibration utility for the XPT2046 resistive touch controller.

Tap the four screen corners and record the raw X/Y values.
Use the output to update calibration constants in display.py.
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
    """Read raw X/Y coordinates from the touch controller."""
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


def wait_for_touch(label):
    """Prompt user to touch a corner, then return averaged raw X/Y values."""
    print(f"\n>>> Please touch and hold: {label}")
    while True:
        x, y = read_xy()
        if x != 2047 and 50 < x < 4000:
            samples = []
            for _ in range(5):
                x, y = read_xy()
                if x != 2047:
                    samples.append((x, y))
                time.sleep_ms(50)
            if len(samples) >= 3:
                ax = sum(v[0] for v in samples) // len(samples)
                ay = sum(v[1] for v in samples) // len(samples)
                print(f"    -> Raw: X={ax}, Y={ay}")
                time.sleep_ms(500)
                return ax, ay
        time.sleep_ms(100)


print("=" * 40)
print("TOUCH CALIBRATION")
print("=" * 40)

tl_x, tl_y = wait_for_touch("TOP LEFT")
tr_x, tr_y = wait_for_touch("TOP RIGHT")
bl_x, bl_y = wait_for_touch("BOTTOM LEFT")
br_x, br_y = wait_for_touch("BOTTOM RIGHT")

print("\n" + "=" * 40)
print("RESULTS:")
print(f"  Top Left     : X={tl_x}, Y={tl_y}")
print(f"  Top Right    : X={tr_x}, Y={tr_y}")
print(f"  Bottom Left  : X={bl_x}, Y={bl_y}")
print(f"  Bottom Right : X={br_x}, Y={br_y}")

x_min = min(tl_x, bl_x)
x_max = max(tr_x, br_x)
y_min = min(tl_y, tr_y)
y_max = max(bl_y, br_y)

print("\nCalibration values for display.py:")
print(f"  X_MIN={x_min}, X_MAX={x_max}")
print(f"  Y_MIN={y_min}, Y_MAX={y_max}")
print("\nMapping formula:")
print(f"  x = (raw_x - {x_min}) * 240 // ({x_max} - {x_min})")
print(f"  y = (raw_y - {y_min}) * 320 // ({y_max} - {y_min})")

"""
ILI9341 Farb-Kombinationen Tester
Testet alle 8 möglichen Kombinationen automatisch.
Jede Kombination wird 3 Sekunden angezeigt.
Im Terminal siehst du welche Kombination gerade läuft.
Schreibe auf welche Kombination ROT als ROT zeigt!
"""

import time

import ili9341
import lcd_bus
import lvgl as lv
import machine

# Alle 8 Kombinationen
TESTS = [
    # (inversion,  byte_order,              byte_swap, beschreibung)
    (False, ili9341.BYTE_ORDER_BGR, True, "BGR + Swap + kein Invert"),
    (True, ili9341.BYTE_ORDER_BGR, True, "BGR + Swap + Invert"),
    (False, ili9341.BYTE_ORDER_BGR, False, "BGR + kein Swap + kein Invert"),
    (True, ili9341.BYTE_ORDER_BGR, False, "BGR + kein Swap + Invert"),
    (False, ili9341.BYTE_ORDER_RGB, True, "RGB + Swap + kein Invert"),
    (True, ili9341.BYTE_ORDER_RGB, True, "RGB + Swap + Invert"),
    (False, ili9341.BYTE_ORDER_RGB, False, "RGB + kein Swap + kein Invert"),
    (True, ili9341.BYTE_ORDER_RGB, False, "RGB + kein Swap + Invert"),
]

# Testfarben - sollten klar erkennbar sein
FARBEN = [
    (0xFF0000, "ROT"),
    (0x00FF00, "GRÜN"),
    (0x0000FF, "BLAU"),
]

WARTE_SEKUNDEN = 3


def make_driver(byte_order, byte_swap):
    spi_hw = machine.SPI.Bus(host=1, mosi=18, sck=17)
    display_bus = lcd_bus.SPIBus(
        spi_bus=spi_hw,
        freq=40_000_000,
        dc=16,
        cs=15,
    )
    d = ili9341.ILI9341(
        data_bus=display_bus,
        display_width=240,
        display_height=320,
        reset_pin=9,
        backlight_pin=21,
        color_space=lv.COLOR_FORMAT.RGB565,
        color_byte_order=byte_order,
        rgb565_byte_swap=byte_swap,
    )
    return d


def flush(scrn, color_hex):
    scrn.set_style_bg_color(lv.color_hex(color_hex), 0)
    scrn.invalidate()
    for _ in range(30):
        lv.timer_handler()
        time.sleep_ms(10)


# ── MAIN ──────────────────────────────────────────────────────
lv.init()
print("\n" + "=" * 50)
print("ILI9341 FARB-TEST GESTARTET")
print("Jede Kombination wird {}s angezeigt".format(WARTE_SEKUNDEN))
print("=" * 50)

for i, (invert, byte_order, byte_swap, desc) in enumerate(TESTS):
    print("\n[{}/{}] {}".format(i + 1, len(TESTS), desc))
    print("  Inversion: {}".format(invert))

    try:
        driver = make_driver(byte_order, byte_swap)
        driver.init(2)
        driver.set_color_inversion(invert)
        driver.set_backlight(100)

        scrn = lv.screen_active()

        for color_hex, color_name in FARBEN:
            print("  Zeige: {}".format(color_name))
            flush(scrn, color_hex)
            time.sleep_ms(WARTE_SEKUNDEN * 1000 // len(FARBEN))

    except Exception as e:
        print("  FEHLER: {}".format(e))

    # Treiber freigeben für nächste Iteration
    try:
        driver.deinit()
    except:
        pass

    time.sleep_ms(500)

print("\n" + "=" * 50)
print("TEST ABGESCHLOSSEN!")
print("Notiere welche Kombination korrekte Farben zeigte.")
print("=" * 50)

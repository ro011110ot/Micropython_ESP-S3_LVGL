# display.py
import fs_driver
import lcd_bus
import lvgl as lv
import machine
import st7789
import task_handler
from micropython import const

_WIDTH, _HEIGHT = const(240), const(320)
_FREQ = const(40_000_000)

if not lv.is_initialized():
    lv.init()

# SPI und Driver Setup
spi_bus = machine.SPI.Bus(host=1, mosi=11, miso=-1, sck=12)
display_bus = lcd_bus.SPIBus(spi_bus=spi_bus, freq=_FREQ, dc=9, cs=10)
driver = st7789.ST7789(
    data_bus=display_bus,
    display_width=_WIDTH,
    display_height=_HEIGHT,
    reset_pin=14,
    reset_state=st7789.STATE_LOW,
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=st7789.BYTE_ORDER_BGR,
    rgb565_byte_swap=True,
)
driver.init()
driver.set_backlight(100)

# WICHTIG: Filesystem fuer die Icons registrieren
try:
    fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(fs_drv, "S")
    print("Filesystem driver 'S:' registered successfully.")
except OSError as e:
    print("FS Driver Error:", e)

# Hintergrund-Task fuer LVGL
th = task_handler.TaskHandler()


class Display:
    def __init__(self):
        self.screens = {}

    def add_screen(self, name, instance):
        self.screens[name] = instance

    def show_screen(self, name):
        if name in self.screens:
            lv.screen_load(self.screens[name].get_screen())

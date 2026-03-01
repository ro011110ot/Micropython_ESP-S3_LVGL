# display.py
"""
Display Manager for ESP32-S3 with ILI9341 + XPT2046 Touch.
Navigation via direct touch polling instead of LVGL callbacks.
"""

import time

import fs_driver
import ili9341
import lcd_bus
import lvgl as lv
import machine
from micropython import const

import task_handler

_WIDTH = const(240)
_HEIGHT = const(320)
_NAV_HEIGHT = const(40)

# ── Display Pins ──────────────────────────────────────────────
_MOSI = const(18)
_SCK = const(17)
_CS = const(15)
_DC = const(16)
_RST = const(9)
_BL = const(21)

# ── Touch Pins (direct SPI polling) ──────────────────────────
_T_SCK = const(12)
_T_CS = const(4)
_T_MOSI = const(11)
_T_MISO = const(10)

# ── LVGL init ─────────────────────────────────────────────────
if not lv.is_initialized():
    lv.init()

# ── Backlight ─────────────────────────────────────────────────
_bl_pin = machine.Pin(_BL, machine.Pin.OUT)
_bl_pin.value(1)

# ── Manual Reset ─────────────────────────────────────────────
print("Display RST...")
_rst_pin = machine.Pin(_RST, machine.Pin.OUT)
_rst_pin.value(1)
time.sleep_ms(50)
_rst_pin.value(0)
time.sleep_ms(200)
_rst_pin.value(1)
time.sleep_ms(300)
print("Display RST done")

# ── Display SPI Bus ──────────────────────────────────────────
_display_spi = machine.SPI.Bus(host=1, mosi=_MOSI, sck=_SCK)
_display_bus = lcd_bus.SPIBus(
    spi_bus=_display_spi,
    freq=20_000_000,
    dc=_DC,
    cs=_CS,
)

driver = ili9341.ILI9341(
    data_bus=_display_bus,
    display_width=_WIDTH,
    display_height=_HEIGHT,
    reset_pin=None,
    backlight_pin=None,
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=ili9341.BYTE_ORDER_BGR,
    rgb565_byte_swap=True,
)
driver.set_power(True)
driver.init(2)
driver.set_color_inversion(True)
driver.set_rotation(lv.DISPLAY_ROTATION._0)
driver.set_backlight(100)
print("Display OK")

# ── Filesystem for Icons ─────────────────────────────────────
try:
    fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(fs_drv, "S")
    print("Filesystem 'S:' OK")
except Exception as e:  # noqa: BLE001
    print("FS Driver Error:", e)

# ── PNG Decoder ──────────────────────────────────────────────
try:
    lv.lodepng_init()
    print("PNG Decoder OK")
except Exception as e:  # noqa: BLE001
    print("PNG Decoder Error:", e)

# ── Touch: direct SPI polling ────────────────────────────────
_t_sck = machine.Pin(_T_SCK, machine.Pin.OUT)
_t_mosi = machine.Pin(_T_MOSI, machine.Pin.OUT)
_t_miso = machine.Pin(_T_MISO, machine.Pin.IN)
_t_cs = machine.Pin(_T_CS, machine.Pin.OUT, value=1)

_t_spi = machine.SoftSPI(
    baudrate=50000,
    polarity=0,
    phase=0,
    sck=_t_sck,
    mosi=_t_mosi,
    miso=_t_miso,
)

# Calibration values
_X_MIN = 288
_X_MAX = 1866
_Y_MIN = 246
_Y_MAX = 1794


def _read_touch_raw(cmd):
    _t_cs.value(0)
    time.sleep_us(100)
    _t_spi.write(bytearray([cmd]))
    buf = bytearray(2)
    _t_spi.readinto(buf)
    _t_cs.value(1)
    return ((buf[0] << 8) | buf[1]) >> 4


def get_touch():
    """Returns (x, y) if touched, else None."""
    raw_x = _read_touch_raw(0x90)
    raw_y = _read_touch_raw(0xD0)

    if raw_x == 2047 or raw_x <= _X_MIN or raw_x >= _X_MAX:
        return None
    if raw_y <= _Y_MIN or raw_y >= _Y_MAX:
        return None

    px = int((_Y_MAX - raw_y) * 240 // (_Y_MAX - _Y_MIN))
    py = int((raw_x - _X_MIN) * 320 // (_X_MAX - _X_MIN))
    px = max(0, min(239, px))
    py = max(0, min(319, py))
    return (px, py)


th = task_handler.TaskHandler()
print("Touch OK")


class Display:
    """Manages multiple screens with touch navigation."""

    _NAV_BG = 0x0A0E27
    _BTN_ACTIVE = 0x00D9FF
    _BTN_INACTIVE = 0x1A1F3A
    _TEXT_ACTIVE = 0x000000
    _TEXT_INACTIVE = 0xAAAAAA

    def __init__(self):
        self.screens = {}
        self.screen_order = []
        self.active_name = None
        self._nav_labels = {}
        self._was_touched = False

    def add_screen(self, name, instance):
        self.screens[name] = instance
        self.screen_order.append(name)

    def finalize_setup(self):
        """Build navigation bar for all screens."""
        for name in self.screen_order:
            scr_obj = self.screens[name].get_screen()
            self._build_nav(scr_obj, name)

    def _build_nav(self, scr_obj, owner_name):
        count = len(self.screen_order)
        if count == 0:
            return

        btn_width = _WIDTH // count
        btn_map = {}

        nav = lv.obj(scr_obj)
        nav.set_size(_WIDTH, _NAV_HEIGHT)
        nav.set_pos(0, _HEIGHT - _NAV_HEIGHT)
        nav.set_style_bg_color(lv.color_hex(self._NAV_BG), 0)
        nav.set_style_border_width(0, 0)
        nav.set_style_radius(0, 0)
        nav.set_style_pad_all(2, 0)
        nav.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        for i, sname in enumerate(self.screen_order):
            is_active = sname == owner_name

            btn = lv.obj(nav)
            btn.set_size(btn_width - 4, _NAV_HEIGHT - 4)
            btn.set_pos(i * btn_width + 2, 2)
            btn.set_style_radius(6, 0)
            btn.set_style_border_width(0, 0)
            btn.set_style_bg_color(
                lv.color_hex(self._BTN_ACTIVE if is_active else self._BTN_INACTIVE), 0
            )
            btn.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

            lbl = lv.label(btn)
            lbl.set_text(sname)
            lbl.set_style_text_color(
                lv.color_hex(self._TEXT_ACTIVE if is_active else self._TEXT_INACTIVE), 0
            )
            lbl.center()

            btn_map[sname] = btn

        self._nav_labels[owner_name] = btn_map

    def show_screen(self, name):
        if name not in self.screens:
            return
        lv.screen_load(self.screens[name].get_screen())
        self.active_name = name

    def check_touch(self):
        """Poll touch and switch screen if nav bar is hit."""
        touch = get_touch()

        if touch is None:
            self._was_touched = False
            return

        if self._was_touched:
            return

        x, y = touch

        if y < (_HEIGHT - _NAV_HEIGHT):
            return

        count = len(self.screen_order)
        btn_width = _WIDTH // count
        btn_idx = x // btn_width
        btn_idx = max(0, min(count - 1, btn_idx))

        target = self.screen_order[btn_idx]
        print(f"Nav Touch: x={x} y={y} -> {target}")

        if target != self.active_name:
            self.show_screen(target)

        self._was_touched = True

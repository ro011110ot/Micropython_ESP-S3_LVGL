# display.py
import lvgl as lv
import st7789
import lcd_bus
import machine
from micropython import const
import task_handler

# IMPORTANT: All values must be integers, not strings!
_WIDTH = const(240)
_HEIGHT = const(320)

# SPI Bus Pins - MUST be integers!
SPI_HOST = const(1)
MOSI = const(11)
MISO = const(-1)
SCK = const(12)

# Display Control Pins - MUST be integers!
CS = const(10)
DC = const(9)
RST = const(14)

_FREQ = const(40_000_000)

print("Initializing LVGL...")
# Check if LVGL is already initialized
if not lv.is_initialized():
    lv.init()

print("Creating SPI bus...")
spi_bus = machine.SPI.Bus(
    host=int(SPI_HOST),      # Ensure it is an int
    mosi=int(MOSI),          # Ensure it is an int
    miso=int(MISO),          # Ensure it is an int
    sck=int(SCK),            # Ensure it is an int
)

print("Creating display bus...")
display_bus = lcd_bus.SPIBus(
    spi_bus=spi_bus,
    freq=int(_FREQ),         # Ensure it is an int
    dc=int(DC),              # Ensure it is an int
    cs=int(CS),              # Ensure it is an int
)

print("Creating display driver...")
display_driver = st7789.ST7789(
    data_bus=display_bus,
    display_width=int(_WIDTH),
    display_height=int(_HEIGHT),
    reset_pin=int(RST),           # DIRECTLY as an integer, not as a Pin object!
    reset_state=st7789.STATE_LOW,
    backlight_pin=None,           # Also None instead of Pin object
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=st7789.BYTE_ORDER_BGR,
    rgb565_byte_swap=True,
)

print("Initializing display...")
display_driver.init()
display_driver.set_backlight(100)

print("Setting up LVGL display...")
# CRITICAL: LVGL needs to know where to render!
# Create an LVGL Display object linked to the driver
disp = lv.display_get_default()
if disp is None:
    print("ERROR: No default LVGL display found!")
else:
    print(f"LVGL display found: {disp}")

print("Creating task handler...")
th = task_handler.TaskHandler()
print("Task handler created and running automatically!")


# Register LVGL filesystem driver
print("Registering LVGL filesystem driver...")
try:
    from fs_driver import fs_register
    fs_drv = lv.fs_drv_t()
    fs_register(fs_drv, "S")
    print("Filesystem driver 'S:' registered successfully.")
except ImportError:
    print("ERROR: Could not import 'fs_driver'. Filesystem for LVGL not available.")
except Exception as e:
    print(f"ERROR registering filesystem driver: {e}")


class Display:
    """
    Manages the display and screens.
    """

    def __init__(self):
        """
        Initializes the Display manager.
        """
        self.screens = {}  # Will store the actual screen class instances
        self.current_screen_name = None
        print("Display manager initialized")

    def add_screen(self, name, screen_instance):
        """
        Adds a screen instance to the manager.
        """
        self.screens[name] = screen_instance
        print(f"Screen '{name}' added")

    def get_screen_instance(self, name):
        """
        Returns the instance of a stored screen.
        """
        return self.screens.get(name)

    def show_screen(self, name):
        """
        Shows the specified screen.
        """
        if name in self.screens:
            print(f"Loading screen '{name}'...")
            # Get the lv.obj from the stored instance
            screen_obj = self.screens[name].get_screen()
            lv.screen_load(screen_obj)
            self.current_screen_name = name
            print(f"Screen '{name}' loaded")
        else:
            print(f"ERROR: Screen '{name}' not found!")
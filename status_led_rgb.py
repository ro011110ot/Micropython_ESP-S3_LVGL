# status_led_rgb.py
import time

from machine import Pin
from neopixel import NeoPixel


class StatusLedRGB:
    def __init__(self, pin_number=48, num_pixels=1):
        self.pin = Pin(pin_number, Pin.OUT)
        self.np = NeoPixel(self.pin, num_pixels)
        self.off()

    def set_state(self, r, g, b):
        self.np[0] = (r, g, b)
        self.np.write()

    def off(self):
        self.set_state(0, 0, 0)

    # Erweitert: nutzt color für set_state
    def blink(self, color=(0, 255, 0), duration=0.5, num_blinks=3):
        for _ in range(num_blinks):
            self.set_state(*color)  # Entpackt das Tupel (R, G, B)
            time.sleep(duration)
            self.off()
            time.sleep(duration)

    def wifi_connecting(self):
        self.blink(color=(0, 255, 0), duration=0.1, num_blinks=3)

    def mqtt_connecting(self):
        self.blink(color=(0, 255, 255), duration=0.1, num_blinks=3)

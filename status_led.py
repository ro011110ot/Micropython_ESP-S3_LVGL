"""
Handle a simple status LED on a specific GPIO pin.

This module provides a class to control an LED for state indication,
such as Wi-Fi or MQTT connection statuses on an ESP32.
"""

import time

from machine import Pin


class StatusLed:
    """
    Handle a simple status LED on a specific GPIO pin.

    Provides methods for blinking and state indication.
    """

    def __init__(self, pin_number=2):
        """Initialize the LED pin and ensure it is off."""
        self.pin = Pin(pin_number, Pin.OUT)
        self.off()

    def on(self):
        """Turn the LED on."""
        self.pin.value(1)

    def off(self):
        """Turn the LED off."""
        self.pin.value(0)

    def set_state(self, r, g, b):
        """
        Interpret RGB values for a simple (single-color) LED.

        The LED turns on if any color component is greater than 0.
        """
        if (r + g + b) > 0:
            self.on()
        else:
            self.off()

    def blink(self, duration=0.2, num_blinks=1):
        """Blink the LED for a specific duration and count."""
        for _ in range(num_blinks):
            self.on()
            time.sleep_ms(int(duration * 1000))
            self.off()
            time.sleep_ms(int(duration * 1000))

    def wifi_connecting(self):
        """Indicate Wi-Fi connection attempt with short rapid blinks."""
        self.blink(duration=0.1, num_blinks=3)

    def mqtt_connecting(self):
        """Indicate MQTT connection attempt with longer blinks."""
        self.blink(duration=0.4, num_blinks=2)

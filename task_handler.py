"""
Handle LVGL task execution using an ESP32-S3 hardware timer.

This module ensures that the UI refresh cycle is consistently maintained
by a periodic hardware interrupt.
"""

import lvgl as lv
from machine import Timer


class TaskHandler:
    """
    Clean LVGL task handler using ESP32-S3 hardware timer.

    This class only handles the UI refresh cycle.
    """

    def __init__(self, refresh_rate_ms=5):
        """Initialize hardware timer 0 for LVGL."""
        self.refresh_rate_ms = refresh_rate_ms
        self.timer = Timer(0)

        # Initialize timer for periodic LVGL execution
        self.timer.init(
            mode=Timer.PERIODIC,
            period=int(self.refresh_rate_ms),
            callback=self._timer_callback,
        )
        # Using a simple print for initialization
        print(f"TaskHandler initialized ({refresh_rate_ms}ms period)")

    def _timer_callback(self, _timer):
        """
        Periodically called by the hardware timer to advance LVGL time.

        Args:
            _timer: The timer object (unused).

        """
        try:
            lv.tick_inc(self.refresh_rate_ms)
            lv.task_handler()
        except (RuntimeError, OSError) as e:
            # Catching Exception is allowed here if we want to prevent
            # the entire system from crashing, but we should log it once.
            print("LVGL Error:", e)

    def deinit(self):
        """Stop the hardware timer."""
        if self.timer:
            self.timer.deinit()

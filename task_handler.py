# task_handler.py
import lvgl as lv
from machine import Timer

class TaskHandler:
    """
    Clean LVGL task handler using ESP32-S3 hardware timer.
    This class only handles the UI refresh cycle.
    """
    def __init__(self, refresh_rate_ms=5):
        """
        Initialize hardware timer 0 for LVGL.
        """
        self.refresh_rate_ms = refresh_rate_ms
        self.timer = Timer(0)

        # Initialize timer for periodic LVGL execution
        self.timer.init(
            mode=Timer.PERIODIC,
            period=int(refresh_rate_ms),
            callback=self._timer_callback
        )
        print(f"TaskHandler initialized ({refresh_rate_ms}ms period)")

    def _timer_callback(self, timer):
        """
        Periodically called by the hardware timer to advance LVGL time.
        """
        try:
            lv.tick_inc(self.refresh_rate_ms)
            lv.task_handler()
        except Exception:
            pass

    def deinit(self):
        """Stop the hardware timer."""
        if self.timer:
            self.timer.deinit()
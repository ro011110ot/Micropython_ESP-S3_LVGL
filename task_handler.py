# task_handler.py
import lvgl as lv
from machine import Timer


class TaskHandler:
    """
    LVGL task handler using ESP32-S3 hardware timer.
    Uses Timer 0 with periodic callback.
    """

    def __init__(self, refresh_rate_ms=5):
        """
        Initialize the task handler with hardware timer.

        Args:
            refresh_rate_ms: How often to update LVGL (default 5ms = 200Hz)
        """
        self.refresh_rate_ms = refresh_rate_ms

        # Create hardware timer (ESP32-S3 has timers 0-3)
        self.timer = Timer(0)

        # Initialize with periodic mode
        # IMPORTANT: period must be a number, not a string!
        self.timer.init(
            mode=Timer.PERIODIC,
            period=int(refresh_rate_ms),  # Ensure it is an int
            callback=self._timer_callback
        )

        print(f"TaskHandler initialized (Hardware Timer 0, {refresh_rate_ms}ms period)")

    def _timer_callback(self, timer):
        """
        Called by the hardware timer periodically.
        This runs in interrupt context (hard IRQ).
        """
        try:
            lv.tick_inc(self.refresh_rate_ms)
            lv.task_handler()
        except Exception as e:
            print(f"TaskHandler error: {e}")

    def deinit(self):
        """
        Stop and deinitialize the timer.
        """
        if self.timer:
            self.timer.deinit()
            print("TaskHandler stopped")
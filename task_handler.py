# task_handler.py
"""
LVGL Task Handler using ESP32-S3 hardware timer.
"""

import lvgl as lv
from machine import Timer


class TaskHandler:
    def __init__(self, refresh_rate_ms=5):
        self.refresh_rate_ms = refresh_rate_ms
        self.timer = Timer(0)
        self.timer.init(
            mode=Timer.PERIODIC,
            period=self.refresh_rate_ms,
            callback=self._timer_callback,
        )

    def _timer_callback(self, _timer):
        try:
            lv.tick_inc(self.refresh_rate_ms)
            lv.task_handler()
        except Exception:  # noqa: BLE001
            pass

    def deinit(self):
        self.timer.deinit()

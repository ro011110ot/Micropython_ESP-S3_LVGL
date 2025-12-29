# timer.py
import lvgl as lv


class Timer:
    """
    A wrapper for lvgl timers.
    """

    def __init__(self, callback, period, user_data=None):
        self.timer = lv.timer_create(callback, period, user_data)

    def set_period(self, period):
        """
        Sets the timer period.
        """
        self.timer.set_period(period)

    def pause(self):
        """
        Pauses the timer.
        """
        self.timer.pause()

    def resume(self):
        """
        Resumes the timer.
        """
        self.timer.resume()

    def delete(self):
        """
        Deletes the timer.
        """
        self.timer.delete()

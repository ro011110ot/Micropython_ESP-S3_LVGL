"""
Display VPS metrics on an LVGL screen.

This module provides a visual representation of CPU, RAM, and disk usage
alongside formatted system uptime.
"""

import lvgl as lv


class VPSMonitorScreen:
    """
    VPS Monitor screen displaying CPU, RAM, and disk usage.

    Converts raw seconds into a human-readable format.
    """

    def __init__(self):
        """Initialize the UI components and set the dark theme."""
        self.screen = lv.obj()
        # Set dark theme background
        self.screen.set_style_bg_color(lv.color_hex(0x0A0E27), 0)
        self.screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        # Title label
        label = lv.label(self.screen)
        label.set_text("VPS STATUS")
        label.set_style_text_color(lv.color_hex(0x00D9FF), 0)
        label.align(lv.ALIGN.TOP_MID, 0, 10)

        # Metric Widgets (Progress Bars)
        self.cpu_bar = self._create_metric("CPU Usage", 55)
        self.ram_bar = self._create_metric("RAM Usage", 115)
        self.disk_bar = self._create_metric("Disk Usage", 175)

        # Uptime Section
        uptime_title = lv.label(self.screen)
        uptime_title.set_text("System Uptime:")
        uptime_title.set_style_text_color(lv.color_hex(0xA0A0C0), 0)
        uptime_title.align(lv.ALIGN.TOP_LEFT, 15, 235)

        self.uptime_label = lv.label(self.screen)
        self.uptime_label.set_text("Awaiting data...")
        self.uptime_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.uptime_label.align(lv.ALIGN.TOP_LEFT, 15, 260)
        self.uptime_label.set_width(210)

    @staticmethod
    def _format_uptime(seconds):
        """
        Convert raw seconds into a string: 'Xd Xh Xm'.

        Returns:
            str: Formatted uptime string or original value on error.

        """
        try:
            total_seconds = int(seconds)
        except (ValueError, TypeError):
            # Fallback if input is not a valid number (BLE001)
            return str(seconds)
        else:
            # Logic moved to else block (TRY300)
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60

            if days > 0:
                return f"{days:d}d {hours:d}h {minutes:d}m"
            return f"{hours:d}h {minutes:d}m"

    def _create_metric(self, name, y_pos):
        """Create a label and a bar for a specific metric."""
        lbl = lv.label(self.screen)
        lbl.set_text(name)
        lbl.set_style_text_color(lv.color_hex(0xAAAAAA), 0)
        lbl.align(lv.ALIGN.TOP_LEFT, 15, y_pos)

        bar = lv.bar(self.screen)
        bar.set_size(210, 15)
        bar.align(lv.ALIGN.TOP_LEFT, 15, y_pos + 25)
        bar.set_style_bg_color(lv.color_hex(0x1A1F3A), 0)
        bar.set_range(0, 100)
        return bar

    def update_values(self, cpu, ram, disk, uptime_raw="--"):
        """
        Update bars and format the uptime text.

        Uses 0 for animation parameter for LVGL v9 compatibility.
        """
        try:
            # Set bar values (0 = no animation)
            self.cpu_bar.set_value(int(cpu), 0)
            self.ram_bar.set_value(int(ram), 0)
            self.disk_bar.set_value(int(disk), 0)

            # Apply formatting to raw uptime seconds
            formatted_uptime = self._format_uptime(uptime_raw)
            self.uptime_label.set_text(formatted_uptime)
        except (ValueError, TypeError, OSError) as e:
            # Specific exceptions for data conversion and LVGL interaction
            print("Error updating VPS values:", e)

    def get_screen(self):
        """Return the screen instance for display management."""
        return self.screen

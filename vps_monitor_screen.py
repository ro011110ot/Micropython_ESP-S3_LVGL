"""
Display VPS metrics on an LVGL screen.
Nav-Bar (40px) am unteren Rand freigehalten.
"""

import lvgl as lv

_NAV_HEIGHT = 40
_CONTENT_HEIGHT = 320 - _NAV_HEIGHT  # 280px


class VPSMonitorScreen:
    """VPS Monitor screen displaying CPU, RAM, and disk usage."""

    def __init__(self):
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(0x0A0E27), 0)
        self.screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        # Titel
        label = lv.label(self.screen)
        label.set_text("VPS STATUS")
        label.set_style_text_color(lv.color_hex(0x00D9FF), 0)
        label.align(lv.ALIGN.TOP_MID, 0, 8)

        # Metric Widgets - innerhalb Content-Bereich
        self.cpu_bar = self._create_metric("CPU Usage", 45)
        self.ram_bar = self._create_metric("RAM Usage", 105)
        self.disk_bar = self._create_metric("Disk Usage", 165)

        # Uptime
        uptime_title = lv.label(self.screen)
        uptime_title.set_text("System Uptime:")
        uptime_title.set_style_text_color(lv.color_hex(0xA0A0C0), 0)
        uptime_title.align(lv.ALIGN.TOP_LEFT, 15, 225)

        self.uptime_label = lv.label(self.screen)
        self.uptime_label.set_text("Awaiting data...")
        self.uptime_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.uptime_label.align(lv.ALIGN.TOP_LEFT, 15, 248)
        self.uptime_label.set_width(210)

    @staticmethod
    def _format_uptime(seconds):
        try:
            total_seconds = int(seconds)
        except (ValueError, TypeError):
            return str(seconds)
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            if days > 0:
                return f"{days:d}d {hours:d}h {minutes:d}m"
            return f"{hours:d}h {minutes:d}m"

    def _create_metric(self, name, y_pos):
        lbl = lv.label(self.screen)
        lbl.set_text(name)
        lbl.set_style_text_color(lv.color_hex(0xAAAAAA), 0)
        lbl.align(lv.ALIGN.TOP_LEFT, 15, y_pos)

        bar = lv.bar(self.screen)
        bar.set_size(210, 15)
        bar.align(lv.ALIGN.TOP_LEFT, 15, y_pos + 22)
        bar.set_style_bg_color(lv.color_hex(0x1A1F3A), 0)
        bar.set_range(0, 100)
        return bar

    def update_values(self, cpu, ram, disk, uptime_raw="--"):
        try:
            self.cpu_bar.set_value(int(cpu), 0)
            self.ram_bar.set_value(int(ram), 0)
            self.disk_bar.set_value(int(disk), 0)
            self.uptime_label.set_text(self._format_uptime(uptime_raw))
        except (ValueError, TypeError, OSError) as e:
            print("Error updating VPS values:", e)

    def get_screen(self):
        return self.screen

# host_monitor_screen.py
"""
Display local host (Manjaro) metrics on an LVGL screen.
Shows per-core CPU bars, CPU/SSD temperature, RAM usage, and network speed.
"""

import lvgl as lv

COLOR_BG = 0x0A0E27
COLOR_CARD_BG = 0x1A1F3A
COLOR_CPU = 0x00D9FF
COLOR_RAM = 0xFFB800
COLOR_TEMP_GOOD = 0x2ECC71  # Green
COLOR_TEMP_WARM = 0xFFB800  # Yellow/Orange
COLOR_TEMP_HOT = 0xFF4500  # Red


class HostMonitorScreen:
    """LVGL screen for local Manjaro host monitoring."""

    def __init__(self):
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(COLOR_BG), 0)

        # Title
        lbl = lv.label(self.screen)
        lbl.set_text("Manjaro Host")
        lbl.align(lv.ALIGN.TOP_MID, 0, 10)

        # CPU Section (4 Bars)
        self.cpu_bars = []
        for i in range(4):
            bar = lv.bar(self.screen)
            bar.set_size(180, 15)
            bar.set_range(0, 100)
            bar.align(lv.ALIGN.TOP_MID, 0, 45 + (i * 22))
            bar.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), lv.PART.MAIN)
            bar.set_style_bg_color(lv.color_hex(COLOR_CPU), lv.PART.INDICATOR)
            self.cpu_bars.append(bar)

            label = lv.label(self.screen)
            label.set_text(f"C{i}")
            label.set_style_text_font(lv.font_montserrat_12, 0)
            label.align_to(bar, lv.ALIGN.OUT_LEFT_MID, -8, 0)

        # --- Temperature Section (before RAM) ---
        self.temp_info_label = lv.label(self.screen)
        self.temp_info_label.set_style_text_font(lv.font_montserrat_12, 0)
        self.temp_info_label.align(lv.ALIGN.TOP_LEFT, 30, 135)
        self.temp_info_label.set_text("CPU: --\xb0C  |  SSD: --\xb0C")

        self.temp_bar = lv.bar(self.screen)
        self.temp_bar.set_size(180, 12)
        self.temp_bar.set_range(0, 100)
        self.temp_bar.align(lv.ALIGN.TOP_MID, 0, 155)
        self.temp_bar.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), lv.PART.MAIN)
        self.temp_bar.set_style_bg_color(
            lv.color_hex(COLOR_TEMP_GOOD), lv.PART.INDICATOR
        )

        # RAM Section
        self.ram_label = lv.label(self.screen)
        self.ram_label.set_style_text_font(lv.font_montserrat_12, 0)
        self.ram_label.align(lv.ALIGN.TOP_LEFT, 30, 175)

        self.ram_bar = lv.bar(self.screen)
        self.ram_bar.set_size(180, 15)
        self.ram_bar.align(lv.ALIGN.TOP_MID, 0, 195)
        self.ram_bar.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), lv.PART.MAIN)
        self.ram_bar.set_style_bg_color(lv.color_hex(COLOR_RAM), lv.PART.INDICATOR)

        # Network Section
        self.net_label = lv.label(self.screen)
        self.net_label.align(lv.ALIGN.BOTTOM_MID, 0, -55)

    def update_values(self, cpu_list, ram_perc, net_speed, cpu_temp, ssd_temp):
        """Update UI with host metrics."""
        # CPU Update
        for i in range(min(len(cpu_list), 4)):
            self.cpu_bars[i].set_value(int(cpu_list[i]), True)

        # CPU Temp Update with color change
        t_val = int(cpu_temp)
        self.temp_bar.set_value(t_val, True)

        # Update combined temp info label
        ssd_str = "{:.1f}\xb0C".format(ssd_temp) if ssd_temp else "--\xb0C"
        self.temp_info_label.set_text("CPU: {}\xb0C  |  SSD: {}".format(t_val, ssd_str))

        if t_val < 55:
            color = COLOR_TEMP_GOOD
        elif t_val < 75:
            color = COLOR_TEMP_WARM
        else:
            color = COLOR_TEMP_HOT
        self.temp_bar.set_style_bg_color(lv.color_hex(color), lv.PART.INDICATOR)

        # RAM Update
        try:
            r_val = float(ram_perc)
            self.ram_bar.set_value(int(r_val), True)
            used_gb = (r_val / 100) * 32
            self.ram_label.set_text("RAM: {:.1f}GB / 32GB".format(used_gb))
        except Exception:
            pass

        # Network Update
        try:
            speed = float(net_speed)
            if speed > 1024:
                speed_text = "{:.2f} MB/s".format(speed / 1024)
            else:
                speed_text = "{:.1f} KB/s".format(speed)
            self.net_label.set_text("Download: " + speed_text)
        except Exception:
            pass

    def get_screen(self):
        return self.screen

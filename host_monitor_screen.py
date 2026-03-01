# host_monitor_screen.py
import lvgl as lv

COLOR_BG = 0x0A0E27
COLOR_CARD_BG = 0x1A1F3A
COLOR_CPU = 0x00D9FF
COLOR_RAM = 0xFFB800
COLOR_NET = 0x2ECC71


class HostMonitorScreen:
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
            bar.align(lv.ALIGN.TOP_MID, 0, 50 + (i * 25))

            # LVGL v9 Style Fix: Use bg_color with PART.INDICATOR
            bar.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), lv.PART.MAIN)
            bar.set_style_bg_color(lv.color_hex(COLOR_CPU), lv.PART.INDICATOR)
            self.cpu_bars.append(bar)

            label = lv.label(self.screen)
            label.set_text(f"C{i}")
            label.align_to(bar, lv.ALIGN.OUT_LEFT_MID, -10, 0)

        # RAM Section
        self.ram_label = lv.label(self.screen)
        self.ram_label.align(lv.ALIGN.TOP_LEFT, 20, 160)

        self.ram_bar = lv.bar(self.screen)
        self.ram_bar.set_size(200, 20)
        self.ram_bar.align(lv.ALIGN.TOP_MID, 0, 185)
        # LVGL v9 Style Fix: Use bg_color with PART.INDICATOR
        self.ram_bar.set_style_bg_color(lv.color_hex(COLOR_RAM), lv.PART.INDICATOR)

        # Network Section
        self.net_label = lv.label(self.screen)
        self.net_label.align(lv.ALIGN.BOTTOM_MID, 0, -60)

    def update_values(self, cpu_list, ram_perc, net_speed):
        """Update UI with host metrics."""
        for i in range(min(len(cpu_list), 4)):
            self.cpu_bars[i].set_value(int(cpu_list[i]), lv.ANIM.ON)

        used_gb = (ram_perc / 100) * 32
        self.ram_label.set_text("RAM: {:.1f}GB / 32GB".format(used_gb))
        self.ram_bar.set_value(int(ram_perc), lv.ANIM.ON)

        if net_speed > 1024:
            speed_text = "{:.2f} MB/s".format(net_speed / 1024)
        else:
            speed_text = "{:.1f} KB/s".format(net_speed)
        self.net_label.set_text("Download: " + speed_text)

    def get_screen(self):
        return self.screen

import lvgl as lv


class VPSMonitorScreen:
    def __init__(self):
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.palette_main(lv.PALETTE.GREY), 0)

        # Title (German as requested)
        label = lv.label(self.screen)
        label.set_text("VPS Status")
        label.align(lv.ALIGN.TOP_MID, 0, 10)

        # CPU Bar
        self.cpu_bar = self._create_metric_bar("CPU", 50)
        # RAM Bar
        self.ram_bar = self._create_metric_bar("RAM", 100)
        # Disk Bar
        self.disk_bar = self._create_metric_bar("Disk", 150)

    def _create_metric_bar(self, name, y_pos):
        # Label for the metric
        label = lv.label(self.screen)
        label.set_text(name)
        label.align(lv.ALIGN.TOP_LEFT, 20, y_pos)

        # The Bar
        bar = lv.bar(self.screen)
        bar.set_size(200, 20)
        bar.align(lv.ALIGN.TOP_LEFT, 80, y_pos)
        bar.set_range(0, 100)
        return bar

    def update_values(self, cpu, ram, disk):
        """Updates the visual bars with real-time data from MQTT."""
        self.cpu_bar.set_value(int(cpu), lv.ANIM.ON)
        self.ram_bar.set_value(int(ram), lv.ANIM.ON)
        self.disk_bar.set_value(int(disk), lv.ANIM.ON)

    def get_screen(self):
        return self.screen

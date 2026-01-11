# sensors_screen.py
import lvgl as lv


class SensorScreen:
    """Displays sensor data in a table using data from DataManager."""

    def __init__(self, mqtt, data_mgr):
        self.mqtt = mqtt
        self.data_mgr = data_mgr
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(0x121212), 0)

        self.table = lv.table(self.screen)
        self.table.set_column_count(2)
        self.table.set_column_width(0, 150)
        self.table.set_column_width(1, 80)
        self.table.align(lv.ALIGN.TOP_MID, 0, 45)

        self.table.set_cell_value(0, 0, "Sensor")
        self.table.set_cell_value(0, 1, "Wert")

        self.table.set_style_bg_color(lv.color_hex(0x1E1E1E), 0)
        self.table.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

        self.row_map = {}
        self.next_row = 1

    def update_ui(self):
        """Iterates over stored sensor data and updates the table."""
        all_data = self.data_mgr.get_all_data()
        sensors = all_data.get("sensors", {})

        for storage_key, info in sensors.items():
            if storage_key not in self.row_map:
                row = self.next_row
                self.row_map[storage_key] = row

                # Use the display name from DataManager
                name = info["display_name"].replace("Sensor_", "").replace("_", " ")
                self.table.set_cell_value(row, 0, name)
                self.next_row += 1

            target_row = self.row_map[storage_key]
            self.table.set_cell_value(target_row, 1, info["value"])

    def get_screen(self):
        return self.screen

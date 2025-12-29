# sensors_screen.py
import lvgl as lv
import ujson


class SensorScreen:
    """
    Display sensor data in a structured table with a dark theme.
    """

    def __init__(self, mqtt):
        self.mqtt = mqtt
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(0x121212), 0)

        # Turquoise Header
        title = lv.label(self.screen)
        title.set_text("SENSOREN")
        title.set_style_text_color(lv.color_hex(0x03DAC6), 0)
        title.align(lv.ALIGN.TOP_MID, 0, 10)

        # Create Table
        self.table = lv.table(self.screen)
        self.table.set_column_count(2)
        self.table.set_column_width(0, 110)
        self.table.set_column_width(1, 110)
        self.table.align(lv.ALIGN.TOP_MID, 0, 45)

        # Dark Table Styling
        self.table.set_style_bg_color(lv.color_hex(0x1E1E1E), 0)
        self.table.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.table.set_style_border_width(0, 0)

        self.sensor_map = {}  # Map sensor names to table rows

        # Register MQTT callback
        self.mqtt.set_callback(self.handle_msg)
        self.mqtt.subscribe("Sensors/#")

    def handle_msg(self, topic, msg):
        """Update table cells when MQTT data arrives."""
        try:
            data = ujson.loads(msg.decode())
            name = data.get("id", "Unknown").split("_")[-1]
            val = f"{data.get('value', '--')} {data.get('unit', '')}"

            if name not in self.sensor_map:
                row = len(self.sensor_map)
                self.sensor_map[name] = row
                self.table.set_cell_value(row, 0, name)

            row_idx = self.sensor_map[name]
            self.table.set_cell_value(row_idx, 1, val)
        except Exception as e:
            print(f"Sensor display error: {e}")

    def get_screen(self):
        """Returns the LVGL screen object for the display manager."""
        return self.screen
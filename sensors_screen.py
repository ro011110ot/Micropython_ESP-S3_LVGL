# sensors_screen.py
import lvgl as lv
import ujson


class SensorScreen:
    """
    A screen to display sensor data using a modern card-based layout.
    """

    def __init__(self, mqtt):
        self.mqtt = mqtt
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(0x1a1a1a), 0)
        self.screen.set_style_text_color(lv.color_hex(0xffffff), 0)

        # --- Title ---
        title = lv.label(self.screen)
        title.set_text("Sensoren")
        title.align(lv.ALIGN.TOP_MID, 0, 10)

        # --- Main Container for Cards ---
        self.main_container = lv.obj(self.screen)
        self.main_container.set_width(220)
        self.main_container.set_height(260)
        self.main_container.align(lv.ALIGN.TOP_MID, 0, 40)
        self.main_container.set_layout(lv.LAYOUT.FLEX)
        self.main_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.main_container.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.main_container.set_style_border_width(0, 0)
        self.main_container.set_style_pad_row(10, 0)

        # --- Sensor Storage ---
        self.sensors = {}  # Stores {'sensor_id': {'card': obj, 'value_label': label}}

        self.subscribe_to_topics()

    def get_screen(self):
        """
        Returns the screen object.
        """
        return self.screen

    def subscribe_to_topics(self):
        """
        Subscribes to the MQTT topics for the sensors.
        """
        self.mqtt.set_callback(self.handle_sensor_data)
        self.mqtt.subscribe("Sensors/#")

    def _create_sensor_card(self, parent, name):
        """
        Creates a new card widget for a sensor.
        """
        card = lv.obj(parent)
        card.set_width(220)
        card.set_height(40)
        card.set_style_bg_color(lv.color_hex(0x2c2c2c), 0)
        card.set_style_radius(8, 0)
        card.set_style_border_width(0, 0)
        card.set_style_pad_hor(10, 0)
        
        name_label = lv.label(card)
        name_label.set_text(name)
        name_label.align(lv.ALIGN.LEFT_MID, 0, 0)

        value_label = lv.label(card)
        value_label.set_text("--")
        value_label.align(lv.ALIGN.RIGHT_MID, 0, 0)

        return card, value_label

    def handle_sensor_data(self, topic, msg):
        """
        Handles the incoming sensor data from MQTT.
        Creates or updates sensor cards.
        """
        # The old debug prints are removed for clarity, can be re-added if needed
        try:
            msg_str = msg.decode('utf-8')
            data = ujson.loads(msg_str)
            sensor_id = data.get("id")

            if not sensor_id:
                return

            value = data.get("value")
            unit = data.get("unit", "")

            # Format DS18B20 value to one decimal place
            if "DS18B20" in sensor_id:
                try:
                    value = f"{float(value):.1f}"
                except (ValueError, TypeError):
                    pass  # Keep original value if conversion fails
            
            # Create a new card if sensor is seen for the first time
            if sensor_id not in self.sensors:
                display_name = sensor_id.replace("Sensor_", "").replace("_", " ")
                card, value_label = self._create_sensor_card(self.main_container, display_name)
                self.sensors[sensor_id] = {'card': card, 'value_label': value_label}
                print(f"[SensorScreen] Created card for new sensor: {display_name}")

            # Update the value on the card
            value_label = self.sensors[sensor_id]['value_label']
            value_label.set_text(f"{value} {unit}")

        except Exception as e:
            print(f"Error handling sensor data: {e}")


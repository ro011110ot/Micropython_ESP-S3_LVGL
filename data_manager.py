# data_manager.py
import ujson


class DataManager:
    """
    Central data storage. Handles incoming MQTT messages and
    prepares them for the UI screens.
    """

    def __init__(self):
        self.data_store = {
            "sensors": {},
            "vps": {}
        }

    def process_message(self, topic, msg):
        """
        Processes strings from MQTT. Includes fix for encoding issues.
        English comments and docstrings.
        """
        try:
            if not msg:
                return

            # Clean potential byte-string remnants or whitespace
            msg_str = str(msg).strip()
            payload = ujson.loads(msg_str)

            # 1. VPS Data
            if topic == "vps/monitor":
                for key in ["cpu", "ram", "disk", "uptime"]:
                    if key in payload:
                        # Convert keys to UPPERCASE for the UI display
                        self.data_store["vps"][key.upper()] = payload[key]

            # 2. Sensor Data
            elif "Sensors" in topic:
                sensor_id = payload.get("id", "")

                # CLEANING: Remove the long hex ID from DS18B20
                # e.g., "Sensor_DS18B20_28a09eb3913cd838" -> "Sensor_DS18B20"
                if "DS18B20" in sensor_id:
                    sensor_id = "_".join(sensor_id.split("_")[:2])

                if sensor_id:
                    value = payload.get("value", "--")
                    unit = payload.get("unit", "")
                    # Store formatted string for the UI screens
                    self.data_store["sensors"][sensor_id] = f"{value} {unit}"

        except Exception as e:
            print(f"DataManager JSON Error: {e} | Content: {msg}")

    def get_all_data(self):
        """Returns the current state of the data store."""
        return self.data_store
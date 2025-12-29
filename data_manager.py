# data_manager.py
import ujson


class DataManager:
    """
    Central data storage. Handles incoming MQTT messages and
    prepares them for the UI.
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
                        # Convert keys to UPPERCASE for the UI
                        self.data_store["vps"][key.upper()] = payload[key]

            # 2. Sensor Data
            elif "Sensors" in topic:
                sensor_id = payload.get("id", "")

                # CLEANING: Remove the long hex ID from DS18B20 (e.g., Sensor_DS18B20_28a0...)
                if "DS18B20" in sensor_id:
                    # Keeps "Sensor_DS18B20" and removes everything after the last underscore
                    sensor_id = "_".join(sensor_id.split("_")[:2])

                if sensor_id:
                    value = payload.get("value", "--")
                    unit = payload.get("unit", "")
                    # Save formatted string for the UI
                    self.data_store["sensors"][sensor_id] = f"{value} {unit}"

        except Exception as e:
            # If JSON fails, show exactly what was in the message
            print(f"DataManager JSON Error: {e} | Content: {msg}")

    def get_all_data(self):
        return self.data_store
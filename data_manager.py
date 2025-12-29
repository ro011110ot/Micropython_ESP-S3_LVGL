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
                        self.data_store["vps"][key.upper()] = payload[key]

            # 2. Sensor Data
            elif "Sensors" in topic:
                sensor_id = payload.get("id")
                if sensor_id:
                    value = payload.get("value", "--")
                    unit = payload.get("unit", "")
                    # Save formatted string
                    self.data_store["sensors"][sensor_id] = f"{value} {unit}"

        except Exception as e:
            # If JSON fails, show exactly what was in the message
            print(f"DataManager JSON Error: {e} | Content: {msg}")

    def get_all_data(self):
        return self.data_store
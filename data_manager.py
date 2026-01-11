# data_manager.py
import ujson


class DataManager:
    """
    Central data storage.

    Handles incoming MQTT messages and
    prepares them for the UI screens.
    """

    def __init__(self):
        self.data_store = {"sensors": {}, "vps": {}}

    def process_message(self, topic, msg):
        try:
            if not msg:
                return

            msg_str = str(msg).strip()
            payload = ujson.loads(msg_str)

            # 1. VPS Data
            if topic == "vps/monitor":
                for key in ["cpu", "ram", "disk", "uptime"]:
                    if key in payload:
                        self.data_store["vps"][key.upper()] = payload[key]

            # 2. Sensor Data (Optimized for Rust payload)
            elif "Sensors" in topic:
                sensor_id = payload.get("id", "")

                if "DS18B20" in sensor_id:
                    sensor_id = "_".join(sensor_id.split("_")[:2])

                if sensor_id:
                    # Look for value in different possible keys
                    # Rust sends "Temp" or "Humidity"
                    value = payload.get("value")
                    unit = payload.get("unit", "")

                    if "Temp" in payload:
                        value = payload["Temp"]
                        unit = "°C"
                    elif "Humidity" in payload:
                        value = payload["Humidity"]
                        unit = "%"

                    if value is not None:
                        self.data_store["sensors"][
                            sensor_id] = f"{value} {unit}"
                    else:
                        self.data_store["sensors"][sensor_id] = "--"

        except (ValueError, TypeError) as e:
            print(f"DataManager JSON Error: {e} | Content: {msg}")

    def get_all_data(self):
        """Returns the current state of the data store."""
        return self.data_store

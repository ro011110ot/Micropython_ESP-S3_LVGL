# data_manager.py
import ujson


class DataManager:
    """
    Central data storage.
    Handles incoming MQTT messages and prepares them for the UI screens.
    """

    def __init__(self):
        # Structure:
        # {'sensors': {'ID_Unit': {'label': '...', 'value': '...'}}, 'vps': {}}
        self.data_store = {"sensors": {}, "vps": {}}

    def get_all_data(self):
        """Return the entire data store."""
        return self.data_store

    def process_message(self, topic, msg):
        """Main entry point for incoming MQTT messages."""
        try:
            if not msg:
                return

            payload = ujson.loads(str(msg).strip())

            if topic == "vps/monitor":
                self._handle_vps_data(payload)
            elif "Sensors" in topic or "sensors" in topic:
                self._handle_sensor_data(payload)

        except (ValueError, TypeError) as e:
            print(f"DataManager JSON Error: {e} | Content: {msg}")

    def _handle_vps_data(self, payload):
        """Process system metrics for the VPS screen."""
        for key in ["cpu", "ram", "disk", "uptime"]:
            if key in payload:
                self.data_store["vps"][key.upper()] = payload[key]

    def _handle_sensor_data(self, payload):
        """Process environmental data from ESP32."""
        data = payload.get("data", payload)
        sensor_id = data.get("id", "Unknown")

        if "DS18B20" in sensor_id:
            sensor_id = "_".join(sensor_id.split("_")[:2])

        value, unit = self._extract_value_and_unit(data)

        if value is not None:
            # Unique key for storage (e.g., DHT11_C)
            clean_unit = unit.replace("°", "").strip()
            storage_key = f"{sensor_id}_{clean_unit}"

            # Save using 'label' and 'value' keys for UI
            self.data_store["sensors"][storage_key] = {
                "label": f"{sensor_id} ({unit})",
                "value": f"{value} {unit}",
            }

    @staticmethod
    def _extract_value_and_unit(data):
        """Extract value and determine unit based on keys."""
        if "Temp" in data:
            return data["Temp"], "°C"
        if "Humidity" in data:
            return data["Humidity"], "%"

        val = data.get("value")
        u = data.get("unit", "")
        return val, u

# main.py
import time
import machine
import gc
import wifi, ntp
from display import Display
from weather_screen import WeatherScreen
from sensors_screen import SensorScreen
from vps_monitor_screen import VPSMonitorScreen
from data_manager import DataManager
from mqtt_client import MQTT


def setup_mqtt(mqtt, data_mgr):
    """Initializes and connects MQTT with all subscriptions."""
    try:
        if mqtt.connect():
            # Subscriptions according to your logs
            mqtt.subscribe("Sensors/#")
            mqtt.subscribe("sensors/#")
            mqtt.subscribe("vps/monitor")
            print("Subscribed to all variants.")
            return True
    except Exception as e:
        print(f"MQTT Setup failed: {e}")
    return False


def main():
    wifi.connect()
    ntp.sync()

    data_mgr = DataManager()
    mqtt = MQTT()
    mqtt.set_callback(data_mgr.process_message)

    if not setup_mqtt(mqtt, data_mgr):
        print("Initial MQTT connection failed. Rebooting...")
        time.sleep(5)
        machine.reset()

    wdt = machine.WDT(timeout=8000)
    disp_man = Display()

    weather = WeatherScreen(mqtt)
    sensors = SensorScreen(mqtt, data_mgr)
    vps = VPSMonitorScreen()

    disp_man.add_screen("Weather", weather)
    disp_man.add_screen("Sensors", sensors)
    disp_man.add_screen("VPS", vps)

    screens = ["Weather", "Sensors", "VPS"]
    idx = 0

    while True:
        try:
            wdt.feed()
            current_name = screens[idx]
            disp_man.show_screen(current_name)

            for _ in range(100):
                wdt.feed()

                try:
                    mqtt.check_msg()
                except Exception as e:
                    print(f"MQTT Error: {e}. Reconnecting...")
                    setup_mqtt(mqtt, data_mgr)

                if current_name == "Weather":
                    weather.update_time()
                elif current_name == "Sensors":
                    sensors.update_ui()
                elif current_name == "VPS":
                    v_data = data_mgr.data_store.get("vps", {})
                    if v_data:
                        # FIX: Using UPPERCASE keys as defined in data_manager.py
                        vps.update_values(
                            v_data.get("CPU", 0),
                            v_data.get("RAM", 0),
                            v_data.get("DISK", 0),
                            v_data.get("UPTIME", 0)
                        )

                time.sleep_ms(100)

            idx = (idx + 1) % len(screens)
            gc.collect()

        except Exception as global_err:
            print(f"Global Loop Error: {global_err}")
            time.sleep(2)
            machine.reset()


if __name__ == "__main__":
    main()
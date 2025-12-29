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
            # Double subscription to be absolutely safe (Case Sensitivity)
            mqtt.subscribe("Sensors/#")
            mqtt.subscribe("sensors/#")
            mqtt.subscribe("vps/monitor")
            print("Subscribed to all variants.")
            return True
    except Exception as e:
        print(f"MQTT Setup failed: {e}")
    return False


def main():
    # Initial connection
    wifi.connect()
    ntp.sync()

    data_mgr = DataManager()
    mqtt = MQTT()
    mqtt.set_callback(data_mgr.process_message)

    # First connection attempt
    if not setup_mqtt(mqtt, data_mgr):
        print("Initial MQTT connection failed. Rebooting...")
        time.sleep(5)
        machine.reset()

    # Hardware Watchdog (8 seconds)
    wdt = machine.WDT(timeout=8000)
    disp_man = Display()

    # Initialize Screens
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

            # Screen display duration loop (approx 10 seconds)
            for _ in range(100):
                wdt.feed()

                try:
                    mqtt.check_msg()
                except Exception as e:
                    print(f"MQTT Loop Error: {e}. Attempting reconnect...")
                    # Try to reconnect without resetting the whole ESP32
                    if not setup_mqtt(mqtt, data_mgr):
                        # If reconnect fails, we let the loop continue
                        # and the WDT will eventually reset if it hangs
                        pass

                # UI Updates depending on active screen
                if current_name == "Weather":
                    weather.update_time()
                elif current_name == "Sensors":
                    sensors.update_ui()
                elif current_name == "VPS":
                    v_data = data_mgr.data_store.get("vps", {})
                    if v_data:
                        vps.update_values(
                            v_data.get("cpu", 0),
                            v_data.get("ram", 0),
                            v_data.get("disk", 0),
                            v_data.get("uptime", 0)
                        )

                time.sleep_ms(100)

            # Switch to next screen
            idx = (idx + 1) % len(screens)
            gc.collect()  # Periodical micro memory cleanup

        except Exception as global_err:
            print(f"Global Loop Error: {global_err}")
            time.sleep(2)
            machine.reset()


if __name__ == "__main__":
    main()
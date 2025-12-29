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


def setup_mqtt(mqtt, data_mgr, wdt=None):
    """
    Initializes and connects MQTT, feeding WDT to prevent SSL-related crashes.
    English comments and docstrings.
    """
    try:
        # Feed the watchdog before the heavy SSL handshake starts
        if wdt:
            wdt.feed()

        if mqtt.connect():
            # Subscribe to all necessary topics
            mqtt.subscribe("Sensors/#")
            mqtt.subscribe("sensors/#")
            mqtt.subscribe("vps/monitor")

            # Feed again after successful handshake and subscriptions
            if wdt:
                wdt.feed()
            print("Subscribed to all variants and fed WDT.")
            return True
    except Exception as e:
        print(f"MQTT Setup failed: {e}")
    return False


def main():
    # 1. Basic System Initialization
    wifi.connect()
    ntp.sync()

    # 2. Data and Communication Setup
    data_mgr = DataManager()
    mqtt = MQTT()
    mqtt.set_callback(data_mgr.process_message)

    # 3. Hardware Watchdog (8 seconds timeout)
    # This prevents the ESP32 from freezing permanently
    wdt = machine.WDT(timeout=8000)

    # 4. Initial MQTT Connection
    if not setup_mqtt(mqtt, data_mgr, wdt):
        print("Initial connection failed. Resetting in 5s...")
        time.sleep(5)
        machine.reset()

    # 5. UI Initialization
    disp_man = Display()
    weather = WeatherScreen(mqtt)
    sensors = SensorScreen(mqtt, data_mgr)
    vps = VPSMonitorScreen()

    disp_man.add_screen("Weather", weather)
    disp_man.add_screen("Sensors", sensors)
    disp_man.add_screen("VPS", vps)

    screens = ["Weather", "Sensors", "VPS"]
    idx = 0

    print("Entering main loop...")

    while True:
        try:
            # Feed WDT at the start of each screen cycle
            wdt.feed()
            current_name = screens[idx]
            disp_man.show_screen(current_name)

            # Internal loop for screen duration (approx. 10 seconds)
            for _ in range(100):
                wdt.feed()

                try:
                    # Check for new MQTT messages
                    mqtt.check_msg()
                except Exception as e:
                    # Handle OSError -1 or SSL timeouts without a full reboot
                    print(f"MQTT Loop Error: {e}. Reconnecting...")
                    wdt.feed()
                    setup_mqtt(mqtt, data_mgr, wdt)

                # Update UI elements based on the active screen
                if current_name == "Weather":
                    weather.update_time()

                elif current_name == "Sensors":
                    # DataManager now provides cleaned IDs like 'Sensor_DS18B20'
                    sensors.update_ui()

                elif current_name == "VPS":
                    v_data = data_mgr.data_store.get("vps", {})
                    if v_data:
                        # Using UPPERCASE keys provided by data_manager.py
                        vps.update_values(
                            v_data.get("CPU", 0),
                            v_data.get("RAM", 0),
                            v_data.get("DISK", 0),
                            v_data.get("UPTIME", 0)
                        )

                # Small delay to keep the system responsive
                time.sleep_ms(100)

            # Move to the next screen and clean up memory
            idx = (idx + 1) % len(screens)
            gc.collect()

        except Exception as global_err:
            print(f"Global Loop Error: {global_err}")
            time.sleep(2)
            machine.reset()


if __name__ == "__main__":
    main()
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
    """
    try:
        if wdt:
            wdt.feed()

        # Connect attempt (Blocking SSL handshake)
        if mqtt.connect():
            # Subscribe to all necessary topics
            mqtt.subscribe("Sensors/#")
            mqtt.subscribe("sensors/#")
            mqtt.subscribe("vps/monitor")

            if wdt:
                wdt.feed()
            print("Subscribed and fed WDT.")
            return True
    except Exception as e:
        print(f"MQTT Setup failed: {e}")
    return False


def main():
    # 1. Hardware Watchdog (Increased to 15 seconds for SSL stability)
    # 8 seconds is often too short for SSL handshakes on ESP32-S3
    wdt = machine.WDT(timeout=15000)

    # 2. Basic System Initialization
    wifi.connect()
    wdt.feed()

    # Small delay for network stack stability
    time.sleep(2)
    ntp.sync()
    wdt.feed()

    # 3. Data and Communication Setup
    data_mgr = DataManager()
    mqtt = MQTT()
    mqtt.set_callback(data_mgr.process_message)

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
            wdt.feed()
            current_name = screens[idx]
            disp_man.show_screen(current_name)

            # Screen cycle loop
            for _ in range(100):
                wdt.feed()

                try:
                    mqtt.check_msg()
                except Exception as e:
                    print(f"MQTT Loop Error: {e}. Reconnecting...")
                    wdt.feed()
                    setup_mqtt(mqtt, data_mgr, wdt)

                if current_name == "Weather":
                    weather.update_time()
                elif current_name == "Sensors":
                    sensors.update_ui()
                elif current_name == "VPS":
                    v_data = data_mgr.data_store.get("vps", {})
                    if v_data:
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
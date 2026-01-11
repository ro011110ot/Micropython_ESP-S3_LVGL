"""
Main entry point for the ESP32-S3 display system.
"""

import gc
import time
import machine
import ntp
import wifi
from data_manager import DataManager
from display import Display
from mqtt_client import MQTT
from sensors_screen import SensorScreen
from vps_monitor_screen import VPSMonitorScreen
from weather_screen import WeatherScreen


def setup_mqtt(mqtt, wdt=None):
    """Initialize and connect MQTT with WDT feeding."""
    if wdt:
        wdt.feed()

    if mqtt.connect():
        mqtt.subscribe("Sensors/#")
        mqtt.subscribe("sensors/#")
        mqtt.subscribe("vps/monitor")
        if wdt:
            wdt.feed()
        return True
    return False


def run_iteration(mqtt, wdt, iteration_count):
    """Perform background tasks and handle reconnection logic."""
    wdt.feed()
    try:
        if not mqtt.is_connected:
            print("MQTT not connected, attempting reconnect...")
            if setup_mqtt(mqtt, wdt):
                return
            time.sleep_ms(2000)  # Wait before next attempt
            return

        mqtt.check_msg()
        if iteration_count % 50 == 0:
            if not mqtt.ping():
                print("MQTT Ping failed.")

    except (OSError, AttributeError) as e:
        print(f"Iteration error: {e}")
        mqtt.is_connected = False


def main():
    """Run the main system loop and initialize hardware."""
    wdt = machine.WDT(timeout=15000)

    # 1. System Initialization
    wifi.connect(wdt)
    wdt.feed()
    time.sleep_ms(1000)
    ntp.sync()
    wdt.feed()

    # 2. Data and Communication
    data_mgr = DataManager()
    mqtt = MQTT()
    mqtt.set_callback(data_mgr.process_message)

    setup_mqtt(mqtt, wdt)

    # 3. UI Setup
    disp_man = Display()
    # weather, sensors, vps objects are created here
    weather = WeatherScreen(mqtt)
    sensors = SensorScreen(mqtt, data_mgr)
    vps = VPSMonitorScreen()

    screen_names = ["Weather", "Sensors", "VPS"]
    disp_man.add_screen("Weather", weather)
    disp_man.add_screen("Sensors", sensors)
    disp_man.add_screen("VPS", vps)

    idx = 0

    print("Entering main loop...")

    # 4. Global Loop
    try:
        while True:
            current_name = screen_names[idx]
            disp_man.show_screen(current_name)

            for i in range(100):
                run_iteration(mqtt, wdt, i)

                # Update UI based on active screen
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
                            v_data.get("UPTIME", 0),
                        )

                time.sleep_ms(100)

            idx = (idx + 1) % len(screen_names)
            gc.collect()

    except Exception as global_err:
        print(f"Global Loop Error: {global_err}")
        time.sleep_ms(2000)
        machine.reset()


if __name__ == "__main__":
    main()

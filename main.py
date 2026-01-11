"""
Main entry point for the ESP32-S3 display system.

Coordinates Wi-Fi, NTP, MQTT, and the LVGL-based UI screens while
ensuring system stability via a Hardware Watchdog.
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
    try:
        if wdt:
            wdt.feed()

        if mqtt.connect():
            mqtt.subscribe("Sensors/#")
            mqtt.subscribe("sensors/#")
            mqtt.subscribe("vps/monitor")
            if wdt:
                wdt.feed()
            return True
    except OSError as e:
        print(f"MQTT Setup failed: {e}")
    return False


def init_ui(disp_man, mqtt, data_mgr):
    """Initialize all UI screens and add them to the display manager."""
    weather = WeatherScreen(mqtt)
    sensors = SensorScreen(mqtt, data_mgr)
    vps = VPSMonitorScreen()

    disp_man.add_screen("Weather", weather)
    disp_man.add_screen("Sensors", sensors)
    disp_man.add_screen("VPS", vps)

    return ["Weather", "Sensors", "VPS"], weather, sensors, vps


def update_current_screen(name, weather, sensors, vps, data_mgr):
    """
    Handle logic for the active screen.

    Reduces complexity (C901) by moving branch logic out of main loop.
    """
    if name == "Weather":
        weather.update_time()
    elif name == "Sensors":
        sensors.update_ui()
    elif name == "VPS":
        v_data = data_mgr.data_store.get("vps", {})
        if v_data:
            vps.update_values(
                v_data.get("CPU", 0),
                v_data.get("RAM", 0),
                v_data.get("DISK", 0),
                v_data.get("UPTIME", 0),
            )


def run_iteration(mqtt, wdt, iteration_count):
    """Perform background tasks like MQTT checking and pinging."""
    wdt.feed()
    try:
        mqtt.check_msg()
        # Ping every ~5 seconds (at 100ms sleep) to prevent timeouts
        if iteration_count % 50 == 0:
            mqtt.ping()
    except (OSError, AttributeError):
        setup_mqtt(mqtt, wdt)


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

    if not setup_mqtt(mqtt, wdt):
        print("Initial connection failed. Resetting...")
        time.sleep_ms(5000)
        machine.reset()

    # 3. UI Setup
    disp_man = Display()
    screen_names, weather, sensors, vps = init_ui(disp_man, mqtt, data_mgr)
    idx = 0

    print("Entering main loop...")

    # 4. Global Loop
    try:
        while True:
            current_name = screen_names[idx]
            disp_man.show_screen(current_name)

            # Stay on one screen for about 10 seconds
            for i in range(100):
                run_iteration(mqtt, wdt, i)
                update_current_screen(current_name, weather, sensors, vps, data_mgr)
                time.sleep_ms(100)

            idx = (idx + 1) % len(screen_names)
            gc.collect()

    except Exception as global_err:  # noqa: BLE001
        print(f"Global Loop Error: {global_err}")
        time.sleep_ms(2000)
        machine.reset()


if __name__ == "__main__":
    main()

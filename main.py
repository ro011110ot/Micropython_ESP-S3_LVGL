# main.py
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
    if wdt:
        wdt.feed()
    if mqtt.connect():
        if wdt:
            wdt.feed()
        mqtt.subscribe("Sensors/#")
        if wdt:
            wdt.feed()
        mqtt.subscribe("sensors/#")
        if wdt:
            wdt.feed()
        mqtt.subscribe("vps/monitor")
        if wdt:
            wdt.feed()
        return True
    return False


def main():
    wdt = machine.WDT(timeout=30000)

    wifi.connect(wdt)
    wdt.feed()
    time.sleep_ms(500)
    ntp.sync()
    wdt.feed()

    data_mgr = DataManager()
    mqtt = MQTT()
    mqtt.set_callback(data_mgr.process_message)
    setup_mqtt(mqtt, wdt)
    wdt.feed()

    disp_man = Display()
    wdt.feed()

    weather = WeatherScreen(mqtt)
    wdt.feed()
    sensors = SensorScreen(mqtt, data_mgr)
    wdt.feed()
    vps = VPSMonitorScreen()
    wdt.feed()

    disp_man.add_screen("Weather", weather)
    disp_man.add_screen("Sensors", sensors)
    disp_man.add_screen("VPS", vps)
    disp_man.finalize_setup()
    wdt.feed()

    disp_man.show_screen("Weather")
    print("Entering main loop...")

    iteration = 0
    try:
        while True:
            wdt.feed()

            # ── Touch Navigation ──────────────────────────────
            disp_man.check_touch()

            # ── MQTT ──────────────────────────────────────────
            try:
                if not mqtt.is_connected:
                    print("MQTT reconnecting...")
                    setup_mqtt(mqtt, wdt)
                    time.sleep_ms(1000)
                else:
                    mqtt.check_msg()
                    if iteration % 100 == 0:
                        if not mqtt.ping():
                            print("MQTT Ping failed.")
            except (OSError, AttributeError) as e:
                print(f"MQTT error: {e}")
                mqtt.is_connected = False

            # ── UI Update ─────────────────────────────────────
            active = disp_man.active_name

            if active == "Weather":
                weather.update_time()
                if iteration % 3000 == 0:
                    wdt.feed()
                    weather.update_weather()
                    wdt.feed()

            elif active == "Sensors":
                sensors.update_ui()

            elif active == "VPS":
                v_data = data_mgr.data_store.get("vps", {})
                if v_data:
                    vps.update_values(
                        v_data.get("CPU", 0),
                        v_data.get("RAM", 0),
                        v_data.get("DISK", 0),
                        v_data.get("UPTIME", 0),
                    )

            time.sleep_ms(50)
            iteration += 1

            if iteration % 200 == 0:
                gc.collect()

    except Exception as e:
        print(f"Global Loop Error: {e}")
        time.sleep_ms(2000)
        machine.reset()


if __name__ == "__main__":
    main()

# main.py
import gc
import time

import machine

import ntp
import wifi
from data_manager import DataManager
from display import Display
from host_monitor_screen import HostMonitorScreen
from mqtt_client import MQTT
from sensors_screen import SensorScreen
from vps_monitor_screen import VPSMonitorScreen
from weather_screen import WeatherScreen


def setup_mqtt(mqtt, wdt=None):
    if wdt:
        wdt.feed()
    if mqtt.connect():
        topics = ["Sensors/#", "sensors/#", "vps/monitor", "host/monitor"]
        for topic in topics:
            if wdt:
                wdt.feed()
            mqtt.subscribe(topic)
        return True
    return False


def main():  # noqa: C901
    wdt = machine.WDT(timeout=30000)
    wifi.connect(wdt)
    ntp.sync()
    wdt.feed()

    data_mgr = DataManager()
    mqtt = MQTT()
    mqtt.set_callback(data_mgr.process_message)
    setup_mqtt(mqtt, wdt)

    disp_man = Display()

    # Init Screens
    weather = WeatherScreen(mqtt)
    sensors = SensorScreen(mqtt, data_mgr)
    vps = VPSMonitorScreen()
    host_screen = HostMonitorScreen()

    disp_man.add_screen("Weather", weather)
    disp_man.add_screen("Sensors", sensors)
    disp_man.add_screen("VPS", vps)
    disp_man.add_screen("Host", host_screen)
    disp_man.finalize_setup()

    disp_man.show_screen("Weather")
    print("Entering main loop...")

    iteration = 0
    while True:
        try:
            wdt.feed()
            disp_man.check_touch()

            # MQTT Handling
            try:
                if not mqtt.is_connected:
                    setup_mqtt(mqtt, wdt)
                    time.sleep_ms(1000)
                else:
                    mqtt.check_msg()
                    if iteration % 100 == 0:
                        mqtt.ping()
            except (OSError, AttributeError) as e:
                print(f"MQTT error: {e}")
                mqtt.is_connected = False

            # UI Update Logic
            active = disp_man.active_name
            if active == "Weather":
                weather.update_time()
                if iteration % 3000 == 0:
                    weather.update_weather()
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
                elif active == "Host":
                h_data = data_mgr.data_store.get("host", {})
                if h_data:
                    host_screen.update_values(
                        h_data.get("cpu", [0, 0, 0, 0]),
                        h_data.get("ram", 0),
                        h_data.get("net_down", 0),
                    )

            time.sleep_ms(50)
            iteration += 1
            if iteration % 200 == 0:
                gc.collect()

        except Exception as e:  # noqa: BLE001
            print(f"Global Loop Error: {e}")
            time.sleep_ms(2000)
            machine.reset()


if __name__ == "__main__":
    main()

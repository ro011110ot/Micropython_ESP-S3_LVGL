# main.py
import time
import machine
import gc
import wifi, ntp
from mqtt_client import MQTT
from display import Display
from weather_screen import WeatherScreen
from sensors_screen import SensorScreen
from vps_monitor_screen import VPSMonitorScreen


def main():
    # Network and time synchronization
    wifi.connect()
    ntp.sync()

    # Initialize MQTT client
    mqtt = MQTT()
    mqtt.connect()

    # Watchdog timer to prevent system freezes (8 seconds timeout)
    wdt = machine.WDT(timeout=8000)

    # Initialize the display manager
    disp_man = Display()

    # Initialize all screens and feed the watchdog during setup
    wdt.feed()
    weather = WeatherScreen(mqtt)
    wdt.feed()
    sensors = SensorScreen(mqtt)
    wdt.feed()
    vps = VPSMonitorScreen()

    # Register screens in the display manager
    disp_man.add_screen("Weather", weather)
    disp_man.add_screen("Sensors", sensors)
    disp_man.add_screen("VPS", vps)

    screens = ["Weather", "Sensors", "VPS"]
    idx = 0

    while True:
        wdt.feed()  # Reset watchdog timer
        mqtt.check_msg()

        # Update VPS data if new messages arrived via MQTT
        if mqtt.vps_data:
            cpu = mqtt.vps_data.get("cpu", 0)
            ram = mqtt.vps_data.get("ram", 0)
            disk = mqtt.vps_data.get("disk", 0)
            # Fetch raw uptime (seconds) from MQTT data
            uptime = mqtt.vps_data.get("uptime", 0)

            # Pass all values including uptime to the screen
            vps.update_values(cpu, ram, disk, uptime)
            mqtt.vps_data = None

        # Cycle through the registered screens
        disp_man.show_screen(screens[idx])
        idx = (idx + 1) % len(screens)

        # Internal loop for screen timing (approx. 10 seconds per screen)
        for _ in range(100):
            wdt.feed()
            mqtt.check_msg()
            weather.update_time()  # Keep the clock updated
            time.sleep_ms(100)

        # Clear memory after each screen cycle
        gc.collect()


if __name__ == "__main__":
    main()
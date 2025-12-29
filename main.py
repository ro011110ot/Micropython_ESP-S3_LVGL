import time

import lvgl as lv
import machine

import display
import ntp
import sensors_screen
import weather
import wifi
from mqtt_client import MQTT
from status_led_rgb import StatusLedRGB
from vps_monitor_screen import VPSMonitorScreen  # New import

# 1. Initialize Watchdog (Timeout 8 seconds)
# This will reset the ESP32 if the loop hangs for more than 8s
wdt = machine.WDT(timeout=8000)


def main():
    """
    Main function to initialize and run the application.
    """
    led = StatusLedRGB()

    # Connect to Wi-Fi
    wifi.connect()

    # Synchronize time with NTP
    ntp.sync()

    # Start the MQTT client
    led.mqtt_connecting()
    mqtt = MQTT()
    mqtt.connect()
    led.set_state(255, 255, 0)  # Yellow for connected
    time.sleep(1)
    led.off()

    print("=== Initializing Display Screens ===")
    # Start the display manager
    disp = display.Display()

    # Initialize screens
    weather_scr = weather.WeatherScreen(mqtt)
    sensor_scr = sensors_screen.SensorScreen(mqtt)
    vps_scr = VPSMonitorScreen()  # No MQTT needed in init, handled by task_handler/mqtt_client

    disp.add_screen("Weather", weather_scr)
    disp.add_screen("Sensors", sensor_scr)
    disp.add_screen("VPS", vps_scr)  # Add the new VPS screen

    disp.show_screen("Weather")

    print("Display initialized and running!")
    print("Screens will switch automatically every 10 seconds.")
    print("Press Ctrl+C to stop\n")

    # List of screens for automatic rotation (now including VPS)
    screen_names = ["Weather", "Sensors", "VPS"]
    current_screen_index = 0
    screen_switch_counter = 0
    SWITCH_INTERVAL = 100  # 100 * 100ms = 10 Seconds

    # Main loop
    while True:
        # Feed the watchdog at the start of every loop
        wdt.feed()

        # Check for MQTT connection and reconnect if necessary
        if not mqtt.is_connected:
            print("MQTT Verbindung verloren. Reconnect...")  # Kept German for UI/Console
            if mqtt.connect():
                print("MQTT Reconnected.")
                # Re-subscribe for Sensor data
                if sensor_scr:
                    sensor_scr.subscribe_to_topics()
            else:
                time.sleep(5)
                continue

        # Process incoming MQTT messages
        mqtt.check_msg()

        if mqtt.vps_data:
            data = mqtt.vps_data
            vps_scr = disp.get_screen_instance("VPS")
            mqtt.vps_data = None  # Reset, damit wir nicht doppelt updaten
        # Automatic screen switching
        screen_switch_counter += 1
        if screen_switch_counter >= SWITCH_INTERVAL:
            screen_switch_counter = 0
            current_screen_index = (current_screen_index + 1) % len(screen_names)
            next_screen = screen_names[current_screen_index]
            print(f"Wechsle zu: {next_screen}...")  # Kept German
            disp.show_screen(next_screen)

        time.sleep_ms(100)


if __name__ == "__main__":
    main()

# MicroPython ESP32-S3 LVGL Dashboard

This repository contains the central display unit for a multi-node sensor ecosystem.
It utilizes an ESP32-S3 and LVGL to visualize real-time environment data,
VPS metrics, and local host statistics.

## Features

- **Multi-Screen LVGL UI**: Fluid interface with dedicated screens for Weather,
  Sensors, VPS, and Host monitoring.
- **Touch Navigation**: Custom direct SPI-polling for the XPT2046 touch
  controller, integrated into the LVGL flow.
- **MQTT Integration**: Robust communication using `umqtt.simple` with SSL
  support, Last Will and Testament (LWT), and automated reconnection.
- **Host & VPS Monitor**: Real-time visualization of CPU load, RAM usage,
  and network throughput for both remote servers and local systems.
- **Weather Service**: Integration with OpenWeatherMap API including custom
  PNG icon rendering via `lodepng`.
- **System Stability**: Implements a Hardware Watchdog (WDT) and periodic
  Garbage Collection (GC) to ensure 24/7 operation.

## Hardware

- **MCU**: ESP32-S3 (with PSRAM recommended)
- **Display**: ILI9341 SPI (240x320)
- **Touch**: XPT2046 Resistive Touch

## Pin Mapping (Default)

| Component | Pin | Function  |
|:----------|:----|:----------|
| Display   | 18  | MOSI      |
| Display   | 17  | SCK       |
| Display   | 15  | CS        |
| Display   | 16  | DC        |
| Display   | 9   | RST       |
| Display   | 21  | Backlight |
| Touch     | 11  | MOSI      |
| Touch     | 10  | MISO      |
| Touch     | 12  | SCK       |
| Touch     | 4   | CS        |

## Configuration (`secrets.py`)

Sensitive credentials and API keys are stored in a `secrets.py` file, which should NOT be committed to version control.

Create this file in the root directory with the following structure:

```python
# Wi-Fi Credentials
WIFI_CREDENTIALS = [
    {"ssid": "YOUR_WIFI_SSID", "password": "YOUR_WIFI_PASSWORD"},
    # Add more networks if needed
]

# MQTT Broker Details
MQTT_BROKER = "your.mqtt.broker.com"
MQTT_PORT = 8883  # Or your MQTT port
MQTT_USER = "your_mqtt_username"
MQTT_PASS = "your_mqtt_password"
MQTT_CLIENT_ID = "esp32-s3-dashboard-1"
MQTT_USE_SSL = True  # Set to False if not using SSL

# OpenWeatherMap API Key
OPENWEATHERMAP_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
OPENWEATHERMAP_CITY = "YourCity"
OPENWEATHERMAP_COUNTRY = "YourCountryCode" # e.g., "de" for Germany
```

Replace the placeholder values with your actual credentials.

## File Structure

- `main.py`: Entry point, system initialization, and main loop.
- `display.py`: Display driver setup and touch navigation logic.
- `mqtt_client.py`: Robust MQTT wrapper for data synchronization.
- `task_handler.py`: Hardware timer-based LVGL refresh management.
- `*_screen.py`: Individual UI layout definitions for different data views.

## Future Improvements

- **Error Handling**: Implement more granular error handling and reporting for network
  and sensor data.
- **Configuration Management**: Allow dynamic configuration changes via MQTT or a
  web interface instead of relying solely on `secrets.py`.
- **UI Enhancements**: Add animations, more sophisticated transitions, and a wider
  range of widgets for a richer user experience.
- **Data Persistence**: Implement a mechanism to store sensor data locally (e.g., on
  SPIFFS or an external SD card) for historical analysis.
- **Code Modularity**: Further break down complex modules into smaller, more manageable
  units.
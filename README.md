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

| File                     | Description                                                                                           |
|:-------------------------|:------------------------------------------------------------------------------------------------------|
| `main.py`                | Entry point. Initializes Wi-Fi, NTP, MQTT, display, and runs the main loop.                           |
| `display.py`             | ILI9341 display driver, XPT2046 touch polling, and LVGL screen management with bottom navigation bar. |
| `data_manager.py`        | Central data store. Parses incoming MQTT messages and distributes data to UI screens.                 |
| `mqtt_client.py`         | MQTT wrapper with SSL, LWT, auto-reconnect, and multi-callback support.                               |
| `task_handler.py`        | Hardware timer-based LVGL tick and task handler (5 ms refresh).                                       |
| `wifi.py`                | Wi-Fi connection handler with automatic RGB LED status indication.                                    |
| `ntp.py`                 | NTP time synchronization with CET/CEST daylight-saving time adjustment.                               |
| `timer.py`               | LVGL timer wrapper for periodic callbacks.                                                            |
| `status_led_rgb.py`      | RGB NeoPixel status LED (Wi-Fi connecting, MQTT connecting states).                                   |
| `host_monitor_screen.py` | Host (Manjaro) metrics: per-core CPU, CPU/SSD temperature, RAM, network speed.                        |
| `vps_monitor_screen.py`  | VPS metrics: CPU, RAM, disk usage, and uptime.                                                        |
| `sensors_screen.py`      | Sensor data table (DHT11, DS18B20) displayed via DataManager.                                         |
| `weather_screen.py`      | OpenWeatherMap weather display with PNG icon rendering via lodepng.                                   |
| `touch_cal.py`           | Touch calibration utility — tap screen corners to derive X/Y raw values.                              |
| `boot.py`                | MicroPython boot script (executed on every startup).                                                  |

## MQTT Topics & Payloads

| Topic                | Direction  | Payload                                                                                                     |
|:---------------------|:-----------|:------------------------------------------------------------------------------------------------------------|
| `host/monitor`       | Receive    | `{"cpu": [34.3, 38.3, 34, 38.1], "cpu_temp": 91, "ram": 34.6, "ssd_temp": 30.85, "net_down": 4.59375}`      |
| `vps/monitor`        | Receive    | `{"cpu": 12.5, "ram": 45.3, "disk": 67.1, "uptime": 123456}`                                                |
| `Sensors/#`          | Receive    | Composite payload with `temperature` and `humidity`, or legacy per-sensor format with `id`, `Temp`/`value`. |
| `status/{client_id}` | Send (LWT) | `"online"` / `"offline"` (with retain)                                                                      |

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
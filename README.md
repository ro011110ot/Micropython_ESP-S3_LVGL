# MicroPython ESP32-S3 LVGL Dashboard

Central display unit for a multi-node sensor ecosystem.
Runs on an ESP32-S3 with an ILI9341 display and renders real-time weather,
sensor, VPS, and host metrics via LVGL.

## Features

- **Multi-Screen LVGL UI** — Dedicated screens for Weather, Sensors, VPS, and Host monitoring with touch-based navigation.
- **Touch Navigation** — Direct SPI polling for the XPT2046 resistive touch controller, integrated into the LVGL event loop.
- **MQTT Integration** — Robust communication via `umqtt.simple` with SSL, Last Will and Testament (LWT), automatic reconnection, and multi-callback dispatch.
- **Host & VPS Monitor** — Real-time CPU load, RAM usage, disk usage, temperature, and network throughput for local and remote systems.
- **Weather Service** — OpenWeatherMap integration with PNG icon rendering via `lodepng`.
- **System Stability** — Hardware Watchdog (WDT), periodic garbage collection, and global error handling with automatic reset.

## Hardware

| Component | Model               |
|:----------|:---------------------|
| MCU       | ESP32-S3 (PSRAM recommended) |
| Display   | ILI9341 SPI (240x320) |
| Touch     | XPT2046 Resistive    |
| LED       | NeoPixel RGB (GPIO48)|

## Pin Mapping

| Component | Pin | Function    |
|:----------|:----|:------------|
| Display   | 18  | MOSI        |
| Display   | 17  | SCK         |
| Display   | 15  | CS          |
| Display   | 16  | DC          |
| Display   | 9   | RST         |
| Display   | 21  | Backlight   |
| Touch     | 11  | MOSI        |
| Touch     | 10  | MISO        |
| Touch     | 12  | SCK         |
| Touch     | 4   | CS          |

## Configuration (`secrets.py`)

Sensitive credentials live in a `secrets.py` file at the project root (not tracked by git).

```python
WIFI_CREDENTIALS = [
    {"ssid": "YOUR_SSID", "password": "YOUR_PASSWORD"},
]

MQTT_BROKER = "your.broker.com"
MQTT_PORT = 8883
MQTT_USER = "username"
MQTT_PASS = "password"
MQTT_CLIENT_ID = "esp32-s3-dashboard-1"
MQTT_USE_SSL = True

OPENWEATHERMAP_API_KEY = "your_api_key"
OPENWEATHERMAP_CITY = "YourCity"
OPENWEATHERMAP_COUNTRY = "de"
```

## File Structure

| File                     | Description |
|:-------------------------|:------------|
| `main.py`                | Entry point — initializes Wi-Fi, NTP, MQTT, display, and runs the main loop. |
| `display.py`             | ILI9341 driver, XPT2046 touch polling, LVGL screen manager with bottom nav bar. |
| `data_manager.py`        | Central data store — parses MQTT payloads and feeds UI screens. |
| `mqtt_client.py`         | MQTT wrapper with SSL, LWT, auto-reconnect, and multi-callback dispatch. |
| `task_handler.py`        | Hardware-timer-based LVGL tick and task handler (5 ms refresh). |
| `wifi.py`                | Wi-Fi connection handler with automatic LED status feedback. |
| `ntp.py`                 | NTP synchronization with CET/CEST daylight-saving adjustment. |
| `timer.py`               | LVGL timer wrapper for periodic callbacks. |
| `status_led_rgb.py`      | NeoPixel RGB LED driver with Wi-Fi/MQTT connection patterns. |
| `host_monitor_screen.py` | Host metrics — per-core CPU, temperature, RAM, network speed. |
| `vps_monitor_screen.py`  | VPS metrics — CPU, RAM, disk usage, and uptime. |
| `sensors_screen.py`      | Sensor data table (DHT11, DS18B20) sourced from DataManager. |
| `weather_screen.py`      | OpenWeatherMap display with PNG icons via lodepng. |
| `touch_cal.py`           | Touch calibration utility — tap corners to derive raw X/Y ranges. |
| `boot.py`                | MicroPython boot script (executed on every startup). |

## MQTT Topics & Payloads

| Topic                | Direction | Payload |
|:---------------------|:----------|:--------|
| `host/monitor`       | Receive   | `{"cpu": [34.3, 38.3, 34, 38.1], "cpu_temp": 91, "ram": 34.6, "ssd_temp": 30.85, "net_down": 4.59375}` |
| `vps/monitor`        | Receive   | `{"cpu": 12.5, "ram": 45.3, "disk": 67.1, "uptime": 123456}` |
| `Sensors/#`          | Receive   | Composite payload with `temperature`/`humidity`, or legacy per-sensor format. |
| `status/{client_id}` | Send      | `"online"` / `"offline"` (retained LWT) |

## Future Improvements

- **Error Handling** — More granular network and sensor error recovery.
- **Configuration Management** — Dynamic reconfiguration via MQTT or web interface.
- **UI Enhancements** — Animations, transitions, and richer widget set.
- **Data Persistence** — Local storage on SPIFFS or SD card for historical analysis.

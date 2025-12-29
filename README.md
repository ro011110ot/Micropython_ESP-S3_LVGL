# ESP32-S3 LVGL Central Dashboard

This repository contains the firmware for a high-performance central monitoring unit built with **MicroPython** and **LVGL v9**. It serves as the visualization hub for an ESP32-based sensor ecosystem, displaying real-time weather data, local sensor metrics, and remote VPS server health.



## 🚀 Features

### 🖥️ User Interface (LVGL v9)
* **Multiscreen Navigation**: Smooth transitions between dedicated screens for Weather, Sensors, and VPS Monitoring.
* **Modern Tile Design**: Dark-themed UI using cards with rounded corners and no scrollbars for a clean look.
* **German Localization**: Full support for German UI labels with an integrated umlaut correction engine (`ae`, `oe`, `ue`) to ensure compatibility with standard fonts.

### ☁️ Weather & Environment
* **OpenWeatherMap Integration**: Fetches live weather data via REST API.
* **PNG Icon Support**: Dynamic loading of weather icons from the local flash storage using the LVGL `S:` filesystem driver.

### 🖥️ VPS Monitoring
* **Real-time Metrics**: Visualizes CPU, RAM, and Disk usage via MQTT subscription.
* **Uptime Formatting**: Automatically converts raw seconds from server telemetry into a human-readable format (e.g., `1d 3h 34m`).

### 🛡️ Reliability & Performance
* **Hardware Watchdog (WDT)**: 8-second timeout to ensure automatic recovery from network or software freezes.
* **Memory Management**: Optimized for ESP32-S3 with PSRAM, utilizing aggressive garbage collection to handle PNG decoding.
* **MQTT LWT**: Supports "Last Will and Testament" for status monitoring.

## 📂 Project Structure

```text
├── main.py                # System entry point: WiFi/NTP init and main task loop
├── display.py             # Display driver setup and LVGL FS driver registration
├── weather_screen.py      # Weather UI logic, API handling, and PNG icon management
├── vps_monitor_screen.py  # VPS metrics UI with custom uptime formatting logic
├── sensors_screen.py      # Visualization for local environment sensors
├── mqtt_client.py         # MQTT client for subscribing to sensor and VPS topics
├── secrets.py             # User credentials (WiFi, API Keys) - [DO NOT COMMIT]
└── icons_png/             # Directory for weather icons (e.g., 01d.png, 04n.png)
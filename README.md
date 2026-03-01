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

## Setup

1. **Firmware**: Ensure your ESP32-S3 is flashed with a MicroPython firmware
   that includes the `lvgl` and `lodepng` modules.
2. **Configuration**: Create a `secrets.py` based on your network and API
   credentials (Wi-Fi, MQTT, OpenWeatherMap).
3. **Assets**: Upload the `icons_png` folder to the root directory of the
   flash filesystem to enable weather icons.
4. **Deployment**: Upload all `.py` files and run `main.py`.

## File Structure

- `main.py`: Entry point, system initialization, and main loop.
- `display.py`: Display driver setup and touch navigation logic.
- `mqtt_client.py`: Robust MQTT wrapper for data synchronization.
- `task_handler.py`: Hardware timer-based LVGL refresh management.
- `*_screen.py`: Individual UI layout definitions for different data views.
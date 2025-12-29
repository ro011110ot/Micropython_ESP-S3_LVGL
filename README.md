# Micropython ESP-S3 LVGL Dashboard

This repository contains the central display unit for the ESP32 sensor ecosystem. It uses an ESP32-S3 and LVGL to
visualize environment data and server metrics.

## Features

- **LVGL UI**: Modern German user interface for weather, sensors, and VPS metrics.
- **MQTT Integration**: Subscribes to `vps/monitor` and sensor nodes.
- **Reliability**: Features a Hardware Watchdog (WDT) and MQTT Last Will (LWT).
- **VPS Monitor**: A dedicated screen for CPU, RAM, and Disk usage.

## Hardware

- ESP32-S3 (with PSRAM)
- ST7789 Display
- WS2812B NeoPixel (Status Indicator)

## Setup

1. Configure `secrets.py` (use `secrets.py_example` as a template).
2. Upload all `.py` files and the `icons_png` folder.
3. Ensure LVGL-enabled MicroPython firmware is flashed.
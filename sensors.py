"""
Provide sensor reading capabilities for ESP32.

This module handles the interaction with physical sensors like the DHT11
and returns structured data based on the provided configuration.
"""

import time

import dht
from config import SENSORS
from machine import Pin


def _read_dht11(config):
    """
    Read temperature and humidity from a DHT11 sensor.

    Returns:
            list: A list of reading dictionaries or an empty list on failure.

    """
    if dht is None:
        return []

    sensor = dht.DHT11(Pin(config["pin"]))

    try:
        # Micro-level delay for sensor stability
        time.sleep_ms(1000)
        sensor.measure()
    except OSError as e:
        # Catching specific OSError instead of blind Exception
        print(f"DHT11 hardware error on pin {config['pin']}: {e}")
        return []
    else:
        # This part only runs if sensor.measure() succeeded (TRY300)
        readings = [
            {
                "type": "DHT11",
                "data": {
                    "id": config["provides"]["temperature"]["id"],
                    "value": sensor.temperature(),
                    "unit": config["provides"]["temperature"]["unit"],
                },
            },
            {
                "type": "DHT11",
                "data": {
                    "id": config["provides"]["humidity"]["id"],
                    "value": sensor.humidity(),
                    "unit": config["provides"]["humidity"]["unit"],
                },
            },
        ]
        return readings


def read_all_sensors():
    """
    Read all sensors defined in config.py.

    Returns:
            list: All collected sensor readings.

    """
    all_readings = []

    print("\n--- Reading indoor sensors ---")
    for cfg in SENSORS.values():
        if not cfg.get("active", False):
            continue

        if cfg["type"] == "DHT11":
            all_readings.extend(_read_dht11(cfg))

    print("--- Finished reading sensors ---")
    return all_readings

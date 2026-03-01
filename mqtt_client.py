# mqtt_client.py
"""
Handle MQTT communication for ESP32.
"""

import gc
import json
import secrets

from umqtt.simple import MQTTClient


class MQTT:
    """Universal MQTT client for ESP32-S3."""

    def __init__(self):
        self.broker = secrets.MQTT_BROKER
        self.port = secrets.MQTT_PORT
        self.user = secrets.MQTT_USER
        self.password = secrets.MQTT_PASS
        self.device_id = secrets.MQTT_CLIENT_ID
        self.use_ssl = secrets.MQTT_USE_SSL

        self.is_connected = False
        self.callbacks = []
        self.client = None
        self._init_client()

    def _init_client(self):
        gc.collect()
        self.client = MQTTClient(
            client_id=self.device_id,
            server=self.broker,
            port=self.port,
            user=self.user,
            password=self.password,
            keepalive=60,
            ssl=self.use_ssl,
        )
        self.client.set_callback(self._internal_callback)

    def _internal_callback(self, topic, msg):
        try:
            t = topic.decode()
            m = msg.decode()
            # print(f"MQTT RECEIVE: [{t}] -> {m}")

            for cb in self.callbacks:
                try:
                    cb(t, m)
                except (ValueError, TypeError, OSError) as e:
                    print(f"Callback execution error: {e}")
        except (UnicodeError, AttributeError) as e:
            print(f"MQTT Decode error: {e}")

    def set_callback(self, cb):
        if cb not in self.callbacks:
            self.callbacks.append(cb)

    def connect(self):
        """Connect to the broker."""
        self.disconnect()
        print(f"Connecting to MQTT via {'SSL' if self.use_ssl else 'TCP'}...")
        gc.collect()
        try:
            lwt_topic = f"status/{self.device_id}"
            self.client.set_last_will(lwt_topic, "offline", retain=True)
            self.client.connect()
            self.client.publish(lwt_topic, "online", retain=True)
            self.is_connected = True
            print("MQTT connected successfully.")
        except OSError as e:
            print(f"MQTT Connection failed: {e}")
            self.is_connected = False
            return False
        else:
            return True

    def disconnect(self):
        self.is_connected = False
        if self.client:
            try:
                self.client.disconnect()
            except Exception:  # noqa: BLE001
                pass

    def subscribe(self, topic):
        if self.is_connected:
            try:
                self.client.subscribe(topic)
                print(f"Subscribed: {topic}")
            except OSError:
                self.is_connected = False
                return False
            else:
                return True
        return False

    def publish(self, data, topic="Sensors", *, retain=False):
        if not self.is_connected:
            return False
        try:
            payload = json.dumps(data)
            self.client.publish(topic, payload, retain=retain)
        except (OSError, ValueError):
            self.is_connected = False
            return False
        else:
            return True

    def ping(self):
        if not self.is_connected:
            return False
        try:
            self.client.ping()
        except OSError:
            self.is_connected = False
            return False
        else:
            return True

    def check_msg(self):
        if not self.is_connected:
            return

        try:
            self.client.check_msg()
        except OSError as e:
            print(f"MQTT connection lost: {e}")
            self.is_connected = False
            raise

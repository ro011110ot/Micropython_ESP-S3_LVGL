"""
Handle MQTT communication for ESP32.

This module provides a universal MQTT client supporting SSL and
dynamic callbacks, optimized for ESP32-S3 memory management.
"""

import gc
import json
import secrets

from umqtt.simple import MQTTClient


class MQTT:
    """
    Universal MQTT client for ESP32-S3.

    Supports SSL, Retained Messages, and dynamic Callbacks.
    """

    def __init__(self):
        """Initialize credentials and client state."""
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
        """
        Initialize the underlying MicroPython MQTT client.
        """
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
        """Route incoming messages to all registered listeners."""
        try:
            t = topic.decode()
            m = msg.decode()
            print(f"MQTT RECEIVE: [{t}] -> {m}")

            for cb in self.callbacks:
                try:
                    cb(t, m)
                except (ValueError, TypeError, OSError) as e:
                    print(f"Callback execution error: {e}")
        except (UnicodeError, AttributeError) as e:
            print(f"MQTT Decode error: {e}")

    def set_callback(self, cb):
        """Register a function to handle incoming messages."""
        if cb not in self.callbacks:
            self.callbacks.append(cb)

    def connect(self):
        """Connect to the broker with clean socket state."""
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
            return True
        except OSError as e:
            print(f"MQTT Connection failed: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Closes the connection and resets the client state."""
        self.is_connected = False
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass

    def subscribe(self, topic):
        """Subscribe to a specific topic."""
        if self.is_connected:
            try:
                self.client.subscribe(topic)
                print(f"Subscribed: {topic}")
                return True
            except OSError:
                self.is_connected = False
        return False

    def publish(self, data, topic="Sensors", *, retain=False):
        """Publish data as JSON."""
        if not self.is_connected:
            return False
        try:
            payload = json.dumps(data)
            self.client.publish(topic, payload, retain=retain)
            return True
        except (OSError, ValueError):
            self.is_connected = False
            return False

    def ping(self):
        """Send a keepalive ping to the broker."""
        if not self.is_connected:
            return False
        try:
            self.client.ping()
            return True
        except OSError:
            self.is_connected = False
            return False

    def check_msg(self):
        """Check for new messages and handle connection loss."""
        if not self.is_connected:
            return

        try:
            self.client.check_msg()
        except OSError as e:
            print(f"MQTT connection lost: {e}")
            self.is_connected = False
            raise

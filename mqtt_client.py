# mqtt_client.py
import json
import secrets
import time
import gc
from umqtt.simple import MQTTClient

class MQTT:
    """
    Universal MQTT client supporting SSL, Retained Messages, and dynamic Callbacks.
    Optimized for ESP32-S3 memory management during SSL handshakes.
    """

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
        """
        Initializes the underlying MicroPython MQTT client with clean memory.
        Crucial to prevent MemoryAllocation errors during SSL context creation.
        """
        gc.collect()
        self.client = MQTTClient(
            client_id=self.device_id,
            server=self.broker,
            port=self.port,
            user=self.user,
            password=self.password,
            keepalive=60,
            ssl=self.use_ssl
        )
        self.client.set_callback(self._internal_callback)

    def _internal_callback(self, topic, msg):
        """Routes incoming messages to all registered listeners."""
        try:
            t = topic.decode()
            m = msg.decode()
            print(f"MQTT RECEIVE: [{t}] -> {m}")

            for cb in self.callbacks:
                try:
                    cb(t, m)
                except Exception as e:
                    print(f"Callback error: {e}")
        except Exception as e:
            print(f"MQTT Decode error: {e}")

    def set_callback(self, cb):
        """Registers a function to handle incoming messages."""
        if cb not in self.callbacks:
            self.callbacks.append(cb)

    def connect(self):
        """
        Connects to the broker.
        Forces garbage collection before SSL handshake to maximize available heap.
        """
        print(f"Connecting to MQTT via {'SSL' if self.use_ssl else 'TCP'}...")
        gc.collect()
        try:
            lwt_topic = f"status/{self.device_id}"
            self.client.set_last_will(lwt_topic, "offline", retain=True)

            # This call is blocking and can take several seconds with SSL
            self.client.connect()

            self.client.publish(lwt_topic, "online", retain=True)
            self.is_connected = True
            print("MQTT connected successfully.")
            return True
        except Exception as e:
            print(f"MQTT Connection failed: {e}")
            self.is_connected = False
            return False

    def subscribe(self, topic):
        """Subscribes to a topic."""
        if self.is_connected:
            try:
                self.client.subscribe(topic)
                print(f"Subscribed: {topic}")
                return True
            except Exception as e:
                print(f"Subscription failed: {e}")
                self.is_connected = False
                return False
        return False

    def publish(self, data, topic="Sensors", retain=False):
        """Publishes data as JSON."""
        if not self.is_connected:
            return False
        try:
            payload = json.dumps(data)
            self.client.publish(topic, payload, retain=retain)
            return True
        except Exception as e:
            print(f"Publish failed: {e}")
            self.is_connected = False
            return False

    def check_msg(self):
        """
        Checks for new messages.
        Re-initializes client on OSError to clear corrupted socket states.
        """
        if not self.is_connected:
            return

        try:
            self.client.check_msg()
        except OSError as e:
            print(f"MQTT connection lost (OSError {e}).")
            self.is_connected = False
            self._init_client()
            raise e
        except Exception as e:
            print(f"MQTT check_msg error: {e}")
            self.is_connected = False
            raise e
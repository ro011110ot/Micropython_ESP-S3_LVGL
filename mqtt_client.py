import json
import machine
import secrets
from umqtt.simple import MQTTClient


class MQTT:
    """
    MQTT client with SSL support, Last Will (LWT), and multi-callback dispatching.
    """

    def __init__(self):
        # Credentials from secrets.py
        self.broker = secrets.MQTT_BROKER
        self.port = secrets.MQTT_PORT
        self.user = secrets.MQTT_USER
        self.password = secrets.MQTT_PASS
        self.device_id = secrets.MQTT_CLIENT_ID
        self.use_ssl = secrets.MQTT_USE_SSL

        self.is_connected = False
        self.vps_data = None
        self.callbacks = []  # List for external modules like SensorScreen

        # Initialize the MQTT client
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
        """Dispatches messages to VPS buffer and registered screen callbacks."""
        topic_str = topic.decode()

        # Internal handling for VPS Monitor data
        if topic_str == "vps/monitor":
            try:
                self.vps_data = json.loads(msg)
            except:
                pass

        # Dispatch to registered listeners (e.g. SensorScreen)
        for cb in self.callbacks:
            try:
                cb(topic, msg)
            except Exception as e:
                print(f"Callback error: {e}")

    def set_callback(self, cb):
        """Register a new function to receive MQTT messages."""
        if cb not in self.callbacks:
            self.callbacks.append(cb)

    def connect(self):
        """Connect with Last Will and Testament."""
        print(f"Connecting to MQTT via {'SSL' if self.use_ssl else 'TCP'}...")
        try:
            lwt_topic = f"status/{self.device_id}"
            self.client.set_last_will(lwt_topic, "offline", retain=True)
            self.client.connect()
            self.client.publish(lwt_topic, "online", retain=True)
            self.client.subscribe("vps/monitor")
            self.is_connected = True
            return True
        except Exception as e:
            print(f"MQTT Connection failed: {e}")
            self.is_connected = False
            return False

    def check_msg(self):
        if self.is_connected:
            try:
                self.client.check_msg()
            except:
                self.is_connected = False

    def subscribe(self, topic):
        if self.is_connected:
            self.client.subscribe(topic)
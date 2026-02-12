import paho.mqtt.client as mqtt
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud_intelligence.risk_classifier import RiskClassifier
from cloud_intelligence.decision_engine import DecisionEngine
from storage.storage_manager import StorageManager
import mqtt_config

# 🔥 Global variable for dashboard access
LATEST_EVENT = {}

class MQTTSubscriber:
    def __init__(self):
        """Initialize MQTT Subscriber with cloud intelligence"""
        self.classifier = RiskClassifier()
        self.decision_engine = DecisionEngine()
        self.storage = StorageManager(storage_dir=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'storage'
        ))

        self.client = mqtt.Client()
        # If USERNAME and PASSWORD are needed, set them here
        # self.client.username_pw_set(mqtt_config.USERNAME, mqtt_config.PASSWORD)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        """Callback when client connects to broker"""
        if rc == 0:
            print("✓ Connected to MQTT Broker!")
            for topic in mqtt_config.SUBSCRIBE_TOPICS:
                client.subscribe(topic, qos=mqtt_config.QOS)
                print(f"  Subscribed to: {topic}")
        else:
            print(f"✗ Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback when client disconnects"""
        if rc != 0:
            print(f"⚠ Unexpected disconnection (code {rc}). Reconnecting...")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        global LATEST_EVENT

        try:
            payload = json.loads(msg.payload.decode())

            risk_score = payload.get('risk_score', 0)
            motion_count = payload.get('motion_count', 0)

            # Cloud intelligence classification
            cloud_risk_level = self.classifier.classify(risk_score, motion_count)

            # Decision engine
            decision = self.decision_engine.make_decision(
                cloud_risk_level,
                risk_score,
                motion_count,
                context={'time_of_day': 14, 'day_of_week': 3}
            )

            # Prepare event data
            event_data = {
                'timestamp': payload.get('timestamp', ''),
                'device_id': payload.get('device_id', 'UNKNOWN'),
                'edge_risk_level': payload.get('risk_level', 'LOW'),
                'cloud_risk_level': cloud_risk_level,
                'risk_score': risk_score,
                'motion_count': motion_count,
                'relay_state': 'ON' if cloud_risk_level in ['HIGH', 'CRITICAL'] else 'OFF',
                'actions': ', '.join(decision['actions']),
                'alert_sent': decision['send_alert'],
                'severity': decision['severity']
            }

            # Save to CSV
            self.storage.log_event(event_data)

            # 🔥 Store latest event for dashboard API
            LATEST_EVENT = event_data

            print("\n📥 Event Processed:")
            print(f"   Edge Risk: {payload.get('risk_level', 'UNKNOWN')}")
            print(f"   Cloud Risk: {cloud_risk_level}")
            print(f"   Risk Score: {risk_score}")
            print(f"   Motion Count: {motion_count}")
            print(f"   Actions: {', '.join(decision['actions'])}")

        except json.JSONDecodeError:
            print(f"✗ Invalid JSON received: {msg.payload}")

        except Exception as e:
            print(f"✗ Error processing message: {e}")

    def start(self):
        """Connect to broker and start listening"""
        try:
            print(f"Connecting to MQTT broker: {mqtt_config.BROKER}:{mqtt_config.PORT}")
            self.client.connect(mqtt_config.BROKER, mqtt_config.PORT, keepalive=60)
            self.client.loop_forever()
        except Exception as e:
            print(f"✗ Connection error: {e}")

    def stop(self):
        """Disconnect safely"""
        self.client.disconnect()


# 🔥 Dashboard API will call this
def get_latest_event():
    return LATEST_EVENT


if __name__ == "__main__":
    subscriber = MQTTSubscriber()
    try:
        subscriber.start()
    except KeyboardInterrupt:
        print("\nStopping MQTT Subscriber...")
        subscriber.stop()

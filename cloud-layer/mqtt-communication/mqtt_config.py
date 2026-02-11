# mqtt_config.py

BROKER = "broker.hivemq.com"      # Public MQTT broker
PORT = 1883
TOPIC = "hybrid_edge_cloud/risk"  # Topic where edge publishes risk
CLIENT_ID = "cloud-subscriber-01"
KEEP_ALIVE = 60
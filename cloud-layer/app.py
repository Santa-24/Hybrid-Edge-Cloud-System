from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

MQTT_BROKER = "10.216.95.74"
MQTT_PORT = 1883

CONTROL_TOPIC = "hackathon/relay/control"
DATA_TOPIC = "hackathon/device/data"

latest = {"risk_score": 0, "motion_count": 0}
events = []

# ---------- MQTT ----------
def on_connect(client, userdata, flags, rc):
    print("✅ MQTT Connected")
    client.subscribe(DATA_TOPIC)

def on_message(client, userdata, msg):
    global latest
    payload = msg.payload.decode()
    print("📩 MQTT DATA:", payload)

    data = json.loads(payload)
    latest = data

    events.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "cloud_risk_level": "AUTO",
        "risk_score": data["risk_score"],
        "motion_count": data["motion_count"],
        "action": "ESP32"
    })

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# ---------- API ----------
@app.route("/api/command", methods=["POST"])
def command():
    cmd = request.json["command"]
    publish.single(CONTROL_TOPIC, cmd, hostname=MQTT_BROKER, port=MQTT_PORT)
    return jsonify({"status": "ok"})

@app.route("/api/stats")
def stats():
    return jsonify({
        "total_events": len(events),
        "high_risk_events": len([e for e in events if e["risk_score"] >= 20]),
        "alerts_sent": len(events),
        "avg_risk_score": latest["risk_score"]
    })

@app.route("/api/events")
def get_events():
    return jsonify({"events": events[-10:]})

if __name__ == "__main__":
    app.run(port=5000, debug=True)

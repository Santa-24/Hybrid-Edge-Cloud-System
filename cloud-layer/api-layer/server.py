"""
Hybrid Edge-Cloud System - API Server
Provides REST API and serves dashboard with manual relay control
"""

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.storage_manager import StorageManager
from cloud_intelligence.risk_classifier import RiskClassifier
from cloud_intelligence.decision_engine import DecisionEngine

app = Flask(__name__)
CORS(app)

# ================== INITIALIZE MODULES ==================
storage_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'storage'
)

storage = StorageManager(storage_dir=storage_dir)
classifier = RiskClassifier()
decision_engine = DecisionEngine()

# ================== RELAY STATE ==================
relay_state = {
    "status": "OFF"
}

# ================== DASHBOARD HTML ==================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hybrid Edge-Cloud System Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg,#667eea,#764ba2);
            padding: 20px;
        }
        .container {
            background: #fff;
            max-width: 1200px;
            margin: auto;
            padding: 30px;
            border-radius: 10px;
        }
        h1, h2 { text-align: center; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .card {
            background: #667eea;
            color: #fff;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        th { background: #f5f5f5; }
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            color: #fff;
            font-size: 12px;
        }
        .status-low { background: #4caf50; }
        .status-medium { background: #ffc107; color:#333; }
        .status-high { background: #ff9800; }
        .status-critical { background: #f44336; }
        .controls {
            margin-top: 30px;
            text-align: center;
        }
        button {
            padding: 10px 25px;
            margin: 10px;
            border: none;
            border-radius: 5px;
            color: #fff;
            cursor: pointer;
            font-size: 14px;
        }
        .on { background: #4caf50; }
        .off { background: #f44336; }
        footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 13px;
        }
    </style>
</head>

<body>
<div class="container">
    <h1>🔒 Hybrid Edge-Cloud System Dashboard</h1>

    <div class="grid">
        <div class="card">
            <h3>Total Events</h3>
            <div id="totalEvents">0</div>
        </div>
        <div class="card">
            <h3>Critical Alerts</h3>
            <div id="criticalEvents">0</div>
        </div>
        <div class="card">
            <h3>High Risk Events</h3>
            <div id="highRiskEvents">0</div>
        </div>
        <div class="card">
            <h3>Avg Risk Score</h3>
            <div id="avgRiskScore">0</div>
        </div>
    </div>

    <div class="controls">
        <h2>Manual Relay Control</h2>
        <button class="on" onclick="toggleRelay('ON')">Relay ON</button>
        <button class="off" onclick="toggleRelay('OFF')">Relay OFF</button>
        <p>Current Relay Status: <strong id="relayStatus">OFF</strong></p>
    </div>

    <h2>Recent Events</h2>
    <table>
        <thead>
            <tr>
                <th>Time</th>
                <th>Device</th>
                <th>Risk</th>
                <th>Score</th>
                <th>Severity</th>
            </tr>
        </thead>
        <tbody id="eventsList">
            <tr><td colspan="5">Loading...</td></tr>
        </tbody>
    </table>

    <footer>
        <p>✓ Cloud API Running | Last update: <span id="lastUpdate">--:--:--</span></p>
    </footer>
</div>

<script>
function updateDashboard() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(d => {
            totalEvents.textContent = d.total_events;
            criticalEvents.textContent = d.critical_events;
            highRiskEvents.textContent = d.high_risk_events;
            avgRiskScore.textContent = d.avg_risk_score;
        });

    fetch('/api/events')
        .then(r => r.json())
        .then(d => {
            const tbody = document.getElementById('eventsList');
            if (d.events.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5">No events</td></tr>';
                return;
            }
            tbody.innerHTML = d.events.map(e => {
                const cls = 'status-' + e.cloud_risk_level.toLowerCase();
                return `
                <tr>
                    <td>${e.timestamp}</td>
                    <td>${e.device_id}</td>
                    <td><span class="status-badge ${cls}">${e.cloud_risk_level}</span></td>
                    <td>${e.risk_score}</td>
                    <td>${e.severity}</td>
                </tr>`;
            }).join('');
        });

    document.getElementById('lastUpdate').textContent =
        new Date().toLocaleTimeString();
}

function toggleRelay(state) {
    fetch('/api/relay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: state })
    })
    .then(r => r.json())
    .then(d => {
        document.getElementById('relayStatus').textContent = d.relay_status;
        alert(d.message);
    });
}

fetch('/api/relay')
    .then(r => r.json())
    .then(d => relayStatus.textContent = d.status);

updateDashboard();
setInterval(updateDashboard, 5000);
</script>
</body>
</html>
"""

# ================== ROUTES ==================
@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/relay", methods=["GET", "POST"])
def relay_control():
    global relay_state

    if request.method == "POST":
        data = request.get_json()
        cmd = data.get("command")

        if cmd == "ON":
            relay_state["status"] = "ON"
        elif cmd == "OFF":
            relay_state["status"] = "OFF"

        return jsonify({
            "relay_status": relay_state["status"],
            "message": f"Relay turned {relay_state['status']}"
        })

    return jsonify(relay_state)

@app.route("/api/events")
def events():
    return jsonify({"events": storage.get_recent_events(20)})

@app.route("/api/stats")
def stats():
    return jsonify(storage.get_statistics())

@app.route("/api/health")
def health():
    return jsonify({"status": "OK"})

# ================== MAIN ==================
if __name__ == "__main__":
    print("🚀 Hybrid Edge-Cloud API Server running")
    print("🌐 Dashboard → http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)

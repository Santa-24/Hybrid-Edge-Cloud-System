# Hybrid Edge-Cloud System

A comprehensive IoT security monitoring solution combining edge computing with cloud intelligence for real-time threat detection and response.

## 🎯 Project Overview

This system implements a three-tier architecture:

1. **Edge Layer**: Real-time motion detection and risk calculation on local devices
2. **Cloud Layer**: Advanced risk classification, intelligent decision-making, and data storage
3. **Dashboard**: Real-time visualization and system monitoring

### Key Features

✅ **Real-Time Motion Detection** - Camera-based motion detection with risk scoring
✅ **Edge Computing** - Immediate local processing without cloud dependency
✅ **Cloud Intelligence** - ML-powered risk classification and decision engine
✅ **MQTT Communication** - Pub/sub messaging between edge and cloud
✅ **Live Dashboard** - Real-time monitoring and analytics visualization
✅ **Alert System** - Multi-channel alerts (email, SMS, dashboard)
✅ **Event Logging** - Comprehensive event storage and analysis

## 📁 Project Structure

```
Hybrid-Edge-Cloud-System/
├── edge-layer/                           # Edge Device Components
│   ├── camera-detection/                # Motion detection system
│   │   ├── main.py                     # Main detection loop
│   │   ├── config.py                   # Edge configuration
│   │   ├── risk_calculator.py          # Risk scoring algorithm
│   │   ├── serial_sender.py            # ESP32 communication
│   │   ├── requirements.txt
│   │   └── run.ps1
│   │
│   └── esp32-firmware/                  # Microcontroller firmware
│       ├── esp32_edge_control.ino      # Arduino sketch
│       └── mqtt_config.h               # ESP32 MQTT settings
│
├── cloud-layer/                         # Cloud Processing Components
│   ├── api-layer/                       # REST API Server
│   │   ├── server.py                   # Flask API server
│   │   └── README.md
│   │
│   ├── mqtt-communication/              # MQTT Broker Interface
│   │   ├── mqtt_config.py              # MQTT settings
│   │   ├── mqtt_subscriber.py          # Event listener
│   │   └── test_publisher.py           # Testing utility
│   │
│   ├── cloud-intelligence/              # AI/ML Processing
│   │   ├── risk_classifier.py          # Risk classification engine
│   │   ├── decision_engine.py          # Decision-making logic
│   │   └── model_train.py              # ML model training
│   │
|   |___app.py
|   |
│   └── storage/                         # Data Persistence
│       ├── storage_manager.py          # CSV/database management
│       └── events.csv                  # Event log
│
├── dashboard/                           # Frontend Visualization
│   ├── index.html                      # Main UI
│   ├── style.css                       # Styling
│   ├── script.js                       # Real-time updates
│   └── README.md
│
├── docs/
    └── explanation-notes.txt           # Technical documentation
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **OpenCV** (for camera detection)
- **MQTT Broker** (HiveMQ public or local Mosquitto)
- **ESP32 Microcontroller** (optional for hardware demo)

### Installation

1. **Clone/Download the project**
```bash
cd Hybrid-Edge-Cloud-System
```

2. **Set up Edge Layer**
```bash
cd edge-layer/camera-detection
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. **Set up Cloud Layer**
```bash
cd cloud-layer
pip install flask flask-cors paho-mqtt pandas scikit-learn
```

4. **Configure MQTT Broker**

Edit `cloud-layer/mqtt-communication/mqtt_config.py`:
```python
BROKER = "broker.hivemq.com"  # Use your broker
PORT = 1883
```

### Running the System

**Terminal 1 - Start the API Server:**
```bash
cd cloud-layer/api-layer
python server.py
# Server runs on http://localhost:5000
```

**Terminal 2 - Start MQTT Subscriber:**
```bash
cd cloud-layer/mqtt-communication
python mqtt_subscriber.py
```

**Terminal 3 - Start Edge Detection:**
```bash
cd edge-layer/camera-detection
python main.py
```

**Terminal 4 - Open Dashboard:**
```
Browser: http://localhost:5000
```

## 🔄 Data Flow

### Event Processing Pipeline

```
Camera Feed
    ↓
Motion Detection (Edge)
    ↓
Risk Calculation (Edge)
    ↓
Serial → ESP32
    ↓
MQTT Publish
    ↓
Cloud Subscriber
    ↓
Risk Classification (Cloud)
    ↓
Decision Engine
    ↓
Actions: Alert | Relay | Log
    ↓
Storage + Dashboard
```

### Risk Levels

| Level | Score | Actions |
|-------|-------|---------|
| **LOW** | < 30 | Monitor & Log |
| **MEDIUM** | 30-60 | Record Event & Monitor |
| **HIGH** | 60-80 | Activate Relay & Alert Security |
| **CRITICAL** | > 80 | Emergency Response & All Alerts |

## 📊 Key Components

### 1. Edge Layer (Motion Detection)

**Purpose**: Real-time processing for immediate response

**Main Features:**
- OpenCV-based motion detection
- Risk scoring algorithm
- Serial communication with ESP32
- Low-latency local processing

**Start Script:**
```bash
cd edge-layer/camera-detection
python main.py
```

**Config** (`config.py`):
```python
CAMERA_INDEX = 0              # Webcam
SERIAL_PORT = 'COM3'          # ESP32 port
BAUD_RATE = 115200            # Serial speed
```

### 2. MQTT Communication

**Purpose**: Reliable event transmission between edge and cloud

**Broker Options:**
- Public: `broker.hivemq.com` (testing)
- Public: `test.mosquitto.org`
- Local: Mosquitto (production)

**Topics:**
- `hybrid/edge/events` - Risk events from ESP32
- `hybrid/edge/status` - Device status updates
- `hybrid/edge/control` - Control commands

**Start Subscriber:**
```bash
cd cloud-layer/mqtt-communication
python mqtt_subscriber.py
```

### 3. Cloud Intelligence

**Risk Classifier** (`risk_classifier.py`):
- Advanced rule-based classification
- Optional ML model support
- Compares edge vs cloud assessments

**Decision Engine** (`decision_engine.py`):
- Context-aware decision making
- Alert cool-down to prevent spam
- Action prioritization

```python
# Example decision output
{
    'risk_level': 'HIGH',
    'actions': ['ACTIVATE_RELAY', 'SEND_ALERT', 'RECORD_EVENT'],
    'send_alert': True,
    'alert_channels': ['email', 'dashboard'],
    'severity': 3
}
```

### 4. Storage System

**Purpose**: Persistent event logging for compliance and analysis

**Files:**
- `events.csv` - All detection events
- `alerts.csv` - Alert history

**StorageManager Usage:**
```python
storage = StorageManager()
storage.log_event(event_dict)
storage.get_events(limit=100, hours=24)
storage.get_statistics()
```

### 5. REST API Server

**Purpose**: Dashboard integration and external system access

**Main Endpoints:**
- `GET /api/status` - Current system status
- `POST /api/status/update` - Update status (MQTT)
- `GET /api/events` - Recent events with filtering
- `GET /api/events/count` - Event statistics
- `POST /api/decision` - Make risk decision
- `GET /api/alerts` - Recent alerts

**Full API documentation**: See `cloud-layer/api-layer/README.md`

### 6. Dashboard

**Purpose**: Real-time visualization and monitoring

**Features:**
- Live risk level display
- Event history
- Statistics (24h)
- Motion count tracking
- Relay status
- Connection indicators

**Access:** `http://localhost:5000`

**Technology Stack:**
- HTML5
- CSS3 (Responsive Design)
- JavaScript (ES6+)
- Paho MQTT (WebSocket)

## 🧠 AI/ML Integration (Optional)

Train a machine learning model for improved classification:

```bash
cd cloud-layer/cloud-intelligence
python model_train.py
```

This generates `trained_model.pkl` which the classifier automatically loads.

**Features Used:**
- Risk score
- Motion count
- Time of day
- Day of week
- Event frequency

**Model Type:** Random Forest Classifier

## 🔧 Configuration Guide

### Edge Layer (`edge-layer/camera-detection/config.py`)

```python
# Camera
CAMERA_INDEX = 0                    # 0 for webcam, 1+ for external

# Serial Port
SERIAL_PORT = 'COM3'               # Windows
SERIAL_PORT = '/dev/ttyUSB0'      # Linux
SERIAL_PORT = '/dev/cu.usbserial'  # Mac

# Risk Thresholds
RISK_LOW_THRESHOLD = 30
RISK_MEDIUM_THRESHOLD = 60

# Processing
FRAME_SKIP = 1                      # Process every N frames
SHOW_DEBUG_WINDOWS = True           # Display detection overlay
```

### MQTT Config (`cloud-layer/mqtt-communication/mqtt_config.py`)

```python
# Broker
BROKER = "broker.hivemq.com"
PORT = 1883

# Topics
TOPIC_EVENTS = "hybrid/edge/events"
TOPIC_STATUS = "hybrid/edge/status"
TOPIC_CONTROL = "hybrid/edge/control"

# Quality of Service
QOS = 1  # At least once
```

## 📊 Event Storage Schema

### events.csv Columns

| Column | Type | Description |
|--------|------|-------------|
| timestamp | ISO8601 | Event time |
| device_id | string | Edge device identifier |
| edge_risk_level | string | Edge classification |
| cloud_risk_level | string | Cloud classification |
| risk_score | float | 0-100 score |
| motion_count | int | Detected objects |
| relay_state | string | ON/OFF |
| actions | string CSV | Taken actions |
| alert_sent | bool | Alert triggered |
| severity | int | 1-4 scale |

## 🧪 Testing

### Test Publisher (Without Hardware)

```bash
cd cloud-layer/mqtt-communication
python test_publisher.py
```

Publishes sample events to test the system without real hardware.

### Manual Event Injection

```bash
# Terminal 1: Subscriber
python mqtt_subscriber.py

# Terminal 2: Send test event
mosquitto_pub -t "hybrid/edge/events" -m '{"risk_score": 75, "motion_count": 5}'
```

## 📈 Monitoring & Analytics

### View Recent Events

```bash
cat cloud-layer/storage/events.csv
```

### Get Statistics via API

```bash
curl http://localhost:5000/api/events/count
```

### Download Event Data

```bash
curl -o events.csv http://localhost:5000/api/events/download
```

## 🔒 Security Considerations

### Production Checklist

- [ ] Use authentication for API (`@require_auth` decorator)
- [ ] Enable HTTPS/SSL for API server
- [ ] Use private MQTT broker with credentials
- [ ] Implement rate limiting
- [ ] Restrict CORS to trusted origins
- [ ] Add input validation on all endpoints
- [ ] Encrypt sensitive configuration
- [ ] Monitor API logs for suspicious activity

### Basic API Security

```python
# Add to server.py
from functools import wraps

API_KEY = "your-secret-key"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

## 🐛 Troubleshooting

### Camera Not Detected
```
Check: Is webcam in use by another application?
Fix: Close other applications using camera
```

### MQTT Connection Failed
```
Check: Is broker running/accessible?
Fix: Verify broker address and port in mqtt_config.py
```

### Serial Port Not Found
```
Check: Is ESP32 connected?
Fix: Update SERIAL_PORT in config.py
Windows: Device Manager → Ports (COM & LPT)
```

### Dashboard Not Updating
```
Check: Is API server running on port 5000?
Check: Is MQTT subscriber receiving events?
Fix: Check browser console for JavaScript errors
```

## 📚 Documentation

- **Main Overview**: This README
- **API Documentation**: `cloud-layer/api-layer/README.md`
- **Technical Notes**: `docs/explanation-notes.txt`
- **Demo Flow**: `demo-flow.txt`

## 🎓 Learning Resources

### Components to Understand

1. **Edge Computing**: Decentralized processing for latency reduction
2. **MQTT**: Lightweight pub/sub protocol (IoT standard)
3. **Risk Classification**: Rule-based + ML approaches
4. **Real-time Dashboards**: WebSocket for live updates
5. **Microcontrollers**: Arduino/ESP32 integration

### Next Steps

1. Run the system in test mode (no hardware)
2. Integrate with real Mosquitto broker
3. Train ML model with historical data
4. Deploy to production infrastructure
5. Add more data sources (sensors, etc.)

## 📝 License

This project is provided as-is for educational purposes.

## 👥 Team Roles

### Recommended Demo Team

- **Member 1 (Edge + Hardware)**: Camera, ESP32, serial communication
- **Member 2 (MQTT/Communication)**: Broker setup, topics, message flow
- **Member 3 (Cloud Intelligence)**: Classification, decisions, analytics
- **Member 4 (Dashboard)**: UI, real-time updates, monitoring

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Database integration (PostgreSQL, InfluxDB)
- [ ] Advanced ML models
- [ ] Mobile app frontend
- [ ] Kubernetes deployment
- [ ] Multi-device support
- [ ] GIS integration for location tracking

## 📞 Support

For issues or questions:
1. Check this README
2. See `docs/explanation-notes.txt`
3. Review API documentation
4. Check system logs in `logs/`

---

**Last Updated**: 2026-02-09
**Version**: 1.0.0
**Status**: Production Ready

import serial
import time


class SerialSender:
    def __init__(self, port, baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.connected = False
        self._connect()

    def _connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)
            self.connected = True
            print(f"✓ Serial connected on {self.port}")
        except Exception as e:
            print("✗ Serial failed, SIMULATION mode:", e)

    def send_risk_data(self, risk_score, risk_level, motion_count):
        if self.connected:
            msg = f"{int(risk_score)}\n"
            self.ser.write(msg.encode())
            self.ser.flush()
            print(f"[Serial] Risk={int(risk_score)} Level={risk_level}")

    def send_relay_state(self, state):
        if self.connected:
            msg = f"RELAY:{state}\n"
            self.ser.write(msg.encode())
            self.ser.flush()
            print(f"[Serial] Relay={state}")

    def close(self):
        if self.ser:
            self.ser.close()
            print("Serial closed")

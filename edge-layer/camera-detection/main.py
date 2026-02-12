"""
Camera Motion Detection System
Captures video, detects motion, calculates risk, and sends to ESP32
"""

import cv2
import numpy as np
import time
from risk_calculator import RiskCalculator
from serial_sender import SerialSender
from config import Config


class MotionDetector:
    def __init__(self):
        self.MEDIUM_THRESHOLD = 15
        self.HIGH_THRESHOLD = 20

        self.config = Config()
        self.risk_calc = RiskCalculator(self.config)
        self.serial = SerialSender(self.config.SERIAL_PORT, self.config.BAUD_RATE)

        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        if not self.cap.isOpened():
            raise Exception("Cannot open camera")
        print(f"Camera {self.config.CAMERA_INDEX} opened successfully")

        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=16, detectShadows=True
        )

    def detect_motion(self, frame):
        fg_mask = self.bg_subtractor.apply(frame)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        motion_area = 0
        motion_count = 0

        for c in contours:
            area = cv2.contourArea(c)
            if area > self.config.MIN_CONTOUR_AREA:
                motion_area += area
                motion_count += 1

        return {
            "motion_detected": motion_count > 0,   # 🔥 REQUIRED
            "motion_area": motion_area,
            "motion_count": motion_count,
            "fg_mask": fg_mask
        }

    def run(self):
        print("🚀 Motion Detection Started")

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (640, 480))
                motion_data = self.detect_motion(frame)

                # ✅ NOW risk_calculator gets correct data
                risk_score, _ = self.risk_calc.calculate_risk(motion_data)

                # Send risk score
                self.serial.send_risk_data(
                    risk_score,
                    "HIGH" if risk_score >= self.HIGH_THRESHOLD else
                    "MEDIUM" if risk_score >= self.MEDIUM_THRESHOLD else "LOW",
                    motion_data["motion_count"]
                )

                # Relay ON for MEDIUM / HIGH
                relay_state = 1 if risk_score >= self.MEDIUM_THRESHOLD else 0
                self.serial.send_relay_state(relay_state)

                cv2.imshow("Motion Mask", motion_data["fg_mask"])

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                time.sleep(0.1)

        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.serial.close()
            print("Cleanup complete")


if __name__ == "__main__":
    MotionDetector().run()

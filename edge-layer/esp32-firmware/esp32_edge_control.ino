#include <WiFi.h>

#define RELAY_PIN 5
#define RELAY_ON  LOW
#define RELAY_OFF HIGH

#define BUZZER_PIN 18   // 🔥 SAFE PIN
#define BUZZER_ON  HIGH
#define BUZZER_OFF LOW

bool buzzerActive = false;
bool highRisk = false;
int relayState = 0;

unsigned long lastBeep = 0;
bool buzzerState = false;

// ================= BUZZER =================
void buzzerControl() {
  if (!buzzerActive) {
    digitalWrite(BUZZER_PIN, BUZZER_OFF);
    return;
  }

  unsigned long interval = highRisk ? 150 : 400;

  if (millis() - lastBeep >= interval) {
    lastBeep = millis();
    buzzerState = !buzzerState;
    digitalWrite(BUZZER_PIN, buzzerState ? BUZZER_ON : BUZZER_OFF);
  }
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, RELAY_OFF);
  digitalWrite(BUZZER_PIN, BUZZER_OFF);

  Serial.println("ESP32 READY");
}

// ================= LOOP =================
void loop() {

  // SERIAL INPUT
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("RELAY:")) {
      relayState = input.substring(6).toInt();
    } else {
      int risk = input.toInt();

      buzzerActive = (risk >= 15);
      highRisk     = (risk >= 20);

      Serial.print("Risk=");
      Serial.println(risk);
    }
  }

  digitalWrite(RELAY_PIN, relayState == 1 ? RELAY_ON : RELAY_OFF);
  buzzerControl();
}

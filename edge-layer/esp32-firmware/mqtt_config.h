#ifndef MQTT_CONFIG_H
#define MQTT_CONFIG_H

/* ========= WIFI ========= */
#define WIFI_SSID     "WIFI_NAME"
#define WIFI_PASSWORD "WIFI_PASSWORD"

/* ========= MQTT (LOCAL MOSQUITTO) ========= */
#define MQTT_BROKER    "LAPTOP_IP"
#define MQTT_PORT      PORT_NO
#define MQTT_CLIENT_ID "ESP32_Edge_Node_01"

/* ========= TOPICS ========= */
#define MQTT_TOPIC_EVENTS  "project/risk"
#define MQTT_TOPIC_STATUS  "project/status"
#define MQTT_TOPIC_CONTROL "project/relay"

#endif

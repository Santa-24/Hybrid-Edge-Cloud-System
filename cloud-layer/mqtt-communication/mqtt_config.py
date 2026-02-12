BROKER = "xx.xx.xx.xx"
PORT = 1883

CLIENT_ID = "Cloud_Subscriber_01"

TOPIC_EVENTS  = "project/risk"
TOPIC_STATUS  = "project/status"
TOPIC_CONTROL = "project/relay"

SUBSCRIBE_TOPICS = [
    TOPIC_EVENTS,
    TOPIC_STATUS
]

QOS = 1

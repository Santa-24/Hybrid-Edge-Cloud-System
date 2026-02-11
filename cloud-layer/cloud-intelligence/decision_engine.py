class DecisionEngine:
    def _init_(self):
        self.alert_log = []

    def make_decision(self, risk_level):
        """
        Decide response based on risk
        """

        decision = {}

        if risk_level == "LOW":
            decision["action"] = "Ignore"
            decision["message"] = "Normal activity detected"

        elif risk_level == "MEDIUM":
            decision["action"] = "Send Warning"
            decision["message"] = "Suspicious activity detected"

        elif risk_level == "HIGH":
            decision["action"] = "Trigger Alarm + Notify Police"
            decision["message"] = "High Risk Intrusion Detected!"

        decision["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.alert_log.append(decision)
        return decision
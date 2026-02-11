class RiskClassifier:
    def _init_(self):
        self.low_threshold = 30
        self.medium_threshold = 70

    def classify_risk(self, risk_score, motion_count):
        """
        Classify into LOW / MEDIUM / HIGH risk
        """

        # Increase risk if motion is high
        if motion_count > 5:
            risk_score += 15

        # Classification rules
        if risk_score < self.low_threshold:
            return "LOW"
        elif risk_score < self.medium_threshold:
            return "MEDIUM"
        else:
            return "HIGH"
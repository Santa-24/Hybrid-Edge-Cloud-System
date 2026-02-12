"""
Risk Calculator
Converts motion metrics into risk scores and levels
"""

import time

class RiskCalculator:
    def __init__(self, config):
        self.config = config
        self.motion_history = []
        self.max_history = 30  # Keep last 30 detections
        
    def calculate_risk(self, motion_data):
        """
        Calculate risk score based on motion metrics
        
        Args:
            motion_data: Dict with motion_detected, motion_area, motion_count
            
        Returns:
            (risk_score, risk_level)
        """
        if not motion_data['motion_detected']:
            return 0.0, 'LOW'
        
        # Add to history
        self.motion_history.append({
            'time': time.time(),
            'area': motion_data['motion_area'],
            'count': motion_data['motion_count']
        })
        
        # Keep only recent history
        if len(self.motion_history) > self.max_history:
            self.motion_history.pop(0)
        
        # Calculate factors
        area_score = self._calculate_area_score(motion_data['motion_area'])
        count_score = self._calculate_count_score(motion_data['motion_count'])
        frequency_score = self._calculate_frequency_score()
        
        # Weighted combination
        risk_score = (
            area_score * 0.4 +      # 40% weight on area
            count_score * 0.3 +     # 30% weight on count
            frequency_score * 0.3   # 30% weight on frequency
        )
        
        # Clamp between 0 and 100
        risk_score = max(0, min(100, risk_score))
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_score)
        
        return risk_score, risk_level
    
    def _calculate_area_score(self, area):
        """Score based on motion area (0-100)"""
        # Normalize area to 0-100 scale
        # Assume max area is full frame (640*480 = 307200)
        max_area = 307200
        score = (area / max_area) * 100
        return min(100, score)
    
    def _calculate_count_score(self, count):
        """Score based on number of moving objects (0-100)"""
        # More objects = higher risk
        # Assume 10+ objects is maximum risk
        max_count = 10
        score = (count / max_count) * 100
        return min(100, score)
    
    def _calculate_frequency_score(self):
        """Score based on motion frequency (0-100)"""
        if len(self.motion_history) < 2:
            return 0
        
        # Calculate events per second over history
        time_span = self.motion_history[-1]['time'] - self.motion_history[0]['time']
        if time_span == 0:
            return 0
        
        events_per_second = len(self.motion_history) / time_span
        
        # Assume 5+ events/sec is maximum risk
        max_frequency = 5
        score = (events_per_second / max_frequency) * 100
        return min(100, score)
    
    def _get_risk_level(self, score):
        """Convert score to risk level"""
        if score < self.config.RISK_LOW_THRESHOLD:
            return 'LOW'
        elif score < self.config.RISK_MEDIUM_THRESHOLD:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def get_statistics(self):
        """Get current statistics"""
        if not self.motion_history:
            return {
                'avg_area': 0,
                'avg_count': 0,
                'total_events': 0
            }
        
        total_area = sum(h['area'] for h in self.motion_history)
        total_count = sum(h['count'] for h in self.motion_history)
        
        return {
            'avg_area': total_area / len(self.motion_history),
            'avg_count': total_count / len(self.motion_history),
            'total_events': len(self.motion_history)
        }

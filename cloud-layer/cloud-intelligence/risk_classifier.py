"""
Cloud Risk Classifier
Advanced risk classification using rules and optional ML
"""

import pickle
import os
from datetime import datetime

class RiskClassifier:
    def __init__(self, model_path='trained_model.pkl'):
        """
        Initialize classifier
        
        Args:
            model_path: Path to trained ML model (optional)
        """
        self.model = None
        self.use_ml = False
        
        # Try to load ML model if exists
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.use_ml = True
                print("✓ ML model loaded successfully")
            except Exception as e:
                print(f"⚠ Could not load ML model: {e}")
                print("  Using rule-based classification")
        else:
            print("ℹ No ML model found, using rule-based classification")
    
    def classify(self, risk_score, motion_count, additional_features=None):
        """
        Classify risk level using ML or rules
        
        Args:
            risk_score: Edge-computed risk score (0-100)
            motion_count: Number of moving objects
            additional_features: Dict of additional features for ML
            
        Returns:
            risk_level: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'
        """
        if self.use_ml and self.model:
            return self._classify_ml(risk_score, motion_count, additional_features)
        else:
            return self._classify_rules(risk_score, motion_count)
    
    def _classify_rules(self, risk_score, motion_count):
        """
        Rule-based classification
        Cloud adds extra intelligence beyond edge classification
        """
        # Enhanced thresholds (stricter than edge)
        if risk_score >= 80 or motion_count >= 8:
            return 'CRITICAL'  # New level for severe cases
        elif risk_score >= 60 or motion_count >= 5:
            return 'HIGH'
        elif risk_score >= 35 or motion_count >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _classify_ml(self, risk_score, motion_count, additional_features):
        """
        ML-based classification using trained model
        """
        try:
            # Prepare features
            features = [risk_score, motion_count]
            
            # Add additional features if provided
            if additional_features:
                features.extend([
                    additional_features.get('time_of_day', 12),  # Hour (0-23)
                    additional_features.get('day_of_week', 1),   # Day (0-6)
                    additional_features.get('frequency', 0),      # Events per minute
                ])
            
            # Predict
            prediction = self.model.predict([features])[0]
            
            # Map numeric prediction to level
            level_map = {0: 'LOW', 1: 'MEDIUM', 2: 'HIGH', 3: 'CRITICAL'}
            return level_map.get(prediction, 'MEDIUM')
            
        except Exception as e:
            print(f"⚠ ML prediction failed: {e}, falling back to rules")
            return self._classify_rules(risk_score, motion_count)
    
    def get_risk_details(self, risk_level):
        """Get detailed information about risk level"""
        details = {
            'LOW': {
                'severity': 1,
                'description': 'Minimal risk detected',
                'recommended_action': 'Monitor only',
                'alert_priority': 'none'
            },
            'MEDIUM': {
                'severity': 2,
                'description': 'Moderate risk detected',
                'recommended_action': 'Log event and monitor',
                'alert_priority': 'low'
            },
            'HIGH': {
                'severity': 3,
                'description': 'Significant risk detected',
                'recommended_action': 'Alert security personnel',
                'alert_priority': 'high'
            },
            'CRITICAL': {
                'severity': 4,
                'description': 'Critical risk - immediate attention required',
                'recommended_action': 'Emergency response',
                'alert_priority': 'critical'
            }
        }
        return details.get(risk_level, details['MEDIUM'])
    
    def compare_with_edge(self, edge_level, cloud_level):
        """
        Compare edge and cloud classifications
        
        Returns:
            agreement: True if classifications match
            upgrade: True if cloud upgraded the risk
            downgrade: True if cloud downgraded the risk
        """
        levels_order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        
        edge_index = levels_order.index(edge_level) if edge_level in levels_order else 1
        cloud_index = levels_order.index(cloud_level) if cloud_level in levels_order else 1
        
        return {
            'agreement': edge_index == cloud_index,
            'upgrade': cloud_index > edge_index,
            'downgrade': cloud_index < edge_index,
            'difference': cloud_index - edge_index
        }
    
    def analyze_trend(self, recent_events):
        """
        Analyze trend from recent events
        
        Args:
            recent_events: List of recent risk events
            
        Returns:
            trend_info: Dict with trend analysis
        """
        if len(recent_events) < 2:
            return {'trend': 'stable', 'confidence': 'low'}
        
        # Get risk scores
        scores = [e.get('risk_score', 0) for e in recent_events]
        
        # Calculate trend
        avg_first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
        avg_second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
        
        if avg_second_half > avg_first_half + 10:
            trend = 'increasing'
        elif avg_second_half < avg_first_half - 10:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'avg_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'confidence': 'high' if len(recent_events) >= 10 else 'medium'
        }

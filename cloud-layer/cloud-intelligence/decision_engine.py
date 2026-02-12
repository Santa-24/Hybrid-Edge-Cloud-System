"""
Decision Engine
Determines appropriate actions based on risk classification
"""

from datetime import datetime, timedelta

class DecisionEngine:
    def __init__(self):
        """Initialize decision engine"""
        self.recent_alerts = []
        self.alert_cooldown = 10  # Seconds between similar alerts
        
    def make_decision(self, risk_level, risk_score, motion_count, context=None):
        """
        Make decision on actions to take
        
        Args:
            risk_level: Cloud-classified risk level
            risk_score: Numeric risk score
            motion_count: Number of detected motions
            context: Additional context (time, location, etc.)
            
        Returns:
            decision: Dict with actions, alerts, and severity
        """
        decision = {
            'risk_level': risk_level,
            'actions': [],
            'send_alert': False,
            'alert_channels': [],
            'severity': self._get_severity(risk_level),
            'override_relay': None,
            'log_level': 'INFO'
        }
        
        # Determine actions based on risk level
        if risk_level == 'CRITICAL':
            decision['actions'] = [
                'ACTIVATE_RELAY',
                'SEND_EMERGENCY_ALERT',
                'RECORD_VIDEO',
                'NOTIFY_SECURITY',
                'LOG_INCIDENT'
            ]
            decision['send_alert'] = True
            decision['alert_channels'] = ['email', 'sms', 'dashboard']
            decision['log_level'] = 'CRITICAL'
            
            # Force relay on
            decision['override_relay'] = 'RELAY_ON'
            
        elif risk_level == 'HIGH':
            decision['actions'] = [
                'ACTIVATE_RELAY',
                'SEND_ALERT',
                'RECORD_EVENT',
                'LOG_INCIDENT'
            ]
            decision['send_alert'] = self._should_send_alert('HIGH')
            decision['alert_channels'] = ['dashboard', 'email']
            decision['log_level'] = 'WARNING'
            
        elif risk_level == 'MEDIUM':
            decision['actions'] = [
                'RECORD_EVENT',
                'MONITOR'
            ]
            decision['send_alert'] = self._should_send_alert('MEDIUM')
            decision['alert_channels'] = ['dashboard']
            decision['log_level'] = 'INFO'
            
        else:  # LOW
            decision['actions'] = ['LOG_EVENT']
            decision['send_alert'] = False
            decision['log_level'] = 'DEBUG'
        
        # Add context-based decisions
        if context:
            decision = self._apply_context(decision, context)
        
        # Record alert if sending
        if decision['send_alert']:
            self._record_alert(risk_level)
        
        return decision
    
    def _get_severity(self, risk_level):
        """Map risk level to numeric severity"""
        severity_map = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }
        return severity_map.get(risk_level, 2)
    
    def _should_send_alert(self, risk_level):
        """
        Determine if alert should be sent
        Implements cooldown to prevent alert spam
        """
        now = datetime.now()
        
        # Check recent alerts for same level
        for alert in self.recent_alerts:
            if alert['level'] == risk_level:
                time_diff = (now - alert['time']).total_seconds()
                if time_diff < self.alert_cooldown:
                    return False  # Still in cooldown
        
        return True
    
    def _record_alert(self, risk_level):
        """Record alert to track cooldowns"""
        self.recent_alerts.append({
            'level': risk_level,
            'time': datetime.now()
        })
        
        # Clean old alerts (older than 5 minutes)
        cutoff = datetime.now() - timedelta(minutes=5)
        self.recent_alerts = [
            a for a in self.recent_alerts 
            if a['time'] > cutoff
        ]
    
    def _apply_context(self, decision, context):
        """
        Modify decision based on context
        
        Context can include:
        - time_of_day: After hours = higher severity
        - location: Sensitive areas = stricter response
        - day_of_week: Weekend = different protocol
        """
        # Example: Upgrade severity for after-hours events
        hour = context.get('hour', 12)
        if (hour < 6 or hour > 22) and decision['severity'] >= 2:
            decision['severity'] += 1
            decision['actions'].append('AFTER_HOURS_PROTOCOL')
        
        # Example: Sensitive location
        location = context.get('location', '')
        if 'restricted' in location.lower() or 'secure' in location.lower():
            if 'NOTIFY_SECURITY' not in decision['actions']:
                decision['actions'].append('NOTIFY_SECURITY')
        
        # Example: Weekend vs weekday
        is_weekend = context.get('is_weekend', False)
        if is_weekend and decision['severity'] >= 3:
            decision['actions'].append('CONTACT_ON_CALL_STAFF')
        
        return decision
    
    def get_action_details(self, action):
        """Get implementation details for each action"""
        action_details = {
            'ACTIVATE_RELAY': {
                'description': 'Turn on relay/alarm system',
                'implementation': 'Send RELAY_ON command via MQTT',
                'priority': 'immediate'
            },
            'SEND_EMERGENCY_ALERT': {
                'description': 'Send emergency notification',
                'implementation': 'Email + SMS to security team',
                'priority': 'critical'
            },
            'SEND_ALERT': {
                'description': 'Send standard alert',
                'implementation': 'Email to admin, dashboard notification',
                'priority': 'high'
            },
            'RECORD_VIDEO': {
                'description': 'Start recording camera feed',
                'implementation': 'Save video buffer to storage',
                'priority': 'high'
            },
            'RECORD_EVENT': {
                'description': 'Record event details',
                'implementation': 'Save to database with metadata',
                'priority': 'medium'
            },
            'LOG_EVENT': {
                'description': 'Log event for analysis',
                'implementation': 'Write to log file',
                'priority': 'low'
            },
            'NOTIFY_SECURITY': {
                'description': 'Alert security personnel',
                'implementation': 'Push notification + SMS',
                'priority': 'critical'
            },
            'MONITOR': {
                'description': 'Continue monitoring',
                'implementation': 'Increase sampling rate',
                'priority': 'low'
            }
        }
        return action_details.get(action, {
            'description': action,
            'implementation': 'Custom action',
            'priority': 'medium'
        })
    
    def generate_summary(self, decision):
        """Generate human-readable summary of decision"""
        summary = f"Risk Level: {decision['risk_level']} (Severity: {decision['severity']})\n"
        summary += f"Actions to take:\n"
        for action in decision['actions']:
            details = self.get_action_details(action)
            summary += f"  - {action}: {details['description']}\n"
        
        if decision['send_alert']:
            summary += f"Alerts sent via: {', '.join(decision['alert_channels'])}\n"
        
        return summary

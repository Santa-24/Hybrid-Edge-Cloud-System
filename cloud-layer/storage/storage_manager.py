import csv
import os
from datetime import datetime

class StorageManager:
    """Manages event and alert storage"""
    
    def __init__(self, storage_dir=None):
        """
        Initialize storage manager
        
        Args:
            storage_dir: Directory for storing CSV files (defaults to current directory)
        """
        if storage_dir is None:
            storage_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.storage_dir = storage_dir
        self.events_file = os.path.join(storage_dir, 'events.csv')
        self.alerts_file = os.path.join(storage_dir, 'alerts.csv')
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize CSV files with headers if they don't exist
        self._init_csv_files()
    
    def _init_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        # Events CSV
        if not os.path.exists(self.events_file):
            with open(self.events_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'device_id', 'edge_risk_level', 'cloud_risk_level',
                    'risk_score', 'motion_count', 'relay_state', 'actions',
                    'alert_sent', 'severity'
                ])
                writer.writeheader()
        
        # Alerts CSV
        if not os.path.exists(self.alerts_file):
            with open(self.alerts_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'device_id', 'alert_level', 'channels', 'message'
                ])
                writer.writeheader()
    
    def log_event(self, event_data):
        """
        Log an event to the events CSV file
        
        Args:
            event_data: Dict with event information
        """
        try:
            with open(self.events_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'device_id', 'edge_risk_level', 'cloud_risk_level',
                    'risk_score', 'motion_count', 'relay_state', 'actions',
                    'alert_sent', 'severity'
                ])
                
                # Ensure timestamp exists
                if 'timestamp' not in event_data or not event_data['timestamp']:
                    event_data['timestamp'] = datetime.now().isoformat()
                
                writer.writerow(event_data)
            
            return True
        except Exception as e:
            print(f"✗ Error logging event: {e}")
            return False
    
    def log_alert(self, alert_data):
        """
        Log an alert to the alerts CSV file
        
        Args:
            alert_data: Dict with alert information
        """
        try:
            with open(self.alerts_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'device_id', 'alert_level', 'channels', 'message'
                ])
                
                # Ensure timestamp exists
                if 'timestamp' not in alert_data or not alert_data['timestamp']:
                    alert_data['timestamp'] = datetime.now().isoformat()
                
                writer.writerow(alert_data)
            
            return True
        except Exception as e:
            print(f"✗ Error logging alert: {e}")
            return False
    
    def get_recent_events(self, count=10):
        """
        Get the most recent events
        
        Args:
            count: Number of recent events to retrieve
            
        Returns:
            List of event dicts
        """
        try:
            events = []
            with open(self.events_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    events.append(row)
            
            return events[-count:] if events else []
        except Exception as e:
            print(f"✗ Error reading events: {e}")
            return []
    
    def get_statistics(self):
        """
        Get statistics about stored events
        
        Returns:
            Dict with statistics
        """
        try:
            events = []
            with open(self.events_file, 'r') as f:
                reader = csv.DictReader(f)
                events = list(reader)
            
            if not events:
                return {
                    'total_events': 0,
                    'critical_events': 0,
                    'high_risk_events': 0,
                    'avg_risk_score': 0
                }
            
            critical_count = sum(1 for e in events if e.get('cloud_risk_level') == 'CRITICAL')
            high_count = sum(1 for e in events if e.get('cloud_risk_level') == 'HIGH')
            
            risk_scores = []
            for event in events:
                try:
                    risk_scores.append(float(event.get('risk_score', 0)))
                except ValueError:
                    pass
            
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            return {
                'total_events': len(events),
                'critical_events': critical_count,
                'high_risk_events': high_count,
                'avg_risk_score': round(avg_risk, 2)
            }
        except Exception as e:
            print(f"✗ Error calculating statistics: {e}")
            return {}

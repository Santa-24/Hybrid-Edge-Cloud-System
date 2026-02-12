"""
Configuration File
All settings for camera detection system
"""

class Config:
    # Camera Settings
    CAMERA_INDEX = 0  # 0 for default webcam, 1 for external camera
    
    # Serial Communication
    SERIAL_PORT = 'COM16'  # Windows: 'COM16', Linux: '/dev/ttyUSB0', Mac: '/dev/cu.usbserial-*'
    BAUD_RATE = 115200
    
    # Motion Detection Thresholds
    MIN_CONTOUR_AREA = 500  # Minimum area to consider as motion (pixels)
    
    # Risk Thresholds (0-100 scale)
    RISK_LOW_THRESHOLD = 30      # Below this = LOW risk
    RISK_MEDIUM_THRESHOLD = 60   # Below this = MEDIUM, above = HIGH
    
    # Processing
    FRAME_SKIP = 1  # Process every N frames (1 = process all)
    
    # Display
    SHOW_DEBUG_WINDOWS = True
    
    # Logging
    LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
    
    @classmethod
    def get_serial_port_help(cls):
        """Helper to find serial port"""
        return """
        To find your ESP32 serial port:
        
        Windows:
        - Open Device Manager → Ports (COM & LPT)
        - Look for "USB-SERIAL CH340" or similar
        - Note the COM number (e.g., COM3)
        
        Linux:
        - Run: ls /dev/ttyUSB*
        - Usually /dev/ttyUSB0
        
        Mac:
        - Run: ls /dev/cu.usbserial*
        - Usually /dev/cu.usbserial-XXXX
        """

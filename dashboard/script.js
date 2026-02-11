// ===========================
// Configuration & State
// ===========================
const CONFIG = {
    // Demo mode settings
    DEMO_MODE: true,
    DEMO_UPDATE_INTERVAL: 5000, // Update every 5 seconds in demo mode
    
    // WebSocket/MQTT settings (for real connection)
    WS_URL: 'ws://localhost:8080',
    MQTT_TOPIC: 'safety/risk',
    
    // Risk thresholds (seconds)
    RISK_THRESHOLDS: {
        LOW: 3,
        MEDIUM: 7,
        HIGH: 10
    }
};

// Global state
let state = {
    connected: false,
    currentRisk: 'SAFE',
    duration: 0,
    relayActive: false,
    stats: {
        totalDetections: 0,
        highRiskCount: 0,
        mediumRiskCount: 0,
        lowRiskCount: 0
    },
    events: [],
    startTime: Date.now()
};

// WebSocket connection (for real implementation)
let ws = null;

// ===========================
// Initialization
// ===========================
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initializing...');
    
    // Initialize UI
    updateSystemStatus('Initializing...');
    
    // Start uptime counter
    startUptimeCounter();
    
    // Setup event listeners
    setupEventListeners();
    
    // Start demo mode or connect to real backend
    if (CONFIG.DEMO_MODE) {
        startDemoMode();
        updateSystemStatus('Demo Mode Active');
        document.getElementById('dataMode').textContent = 'Demo Mode';
    } else {
        connectWebSocket();
    }
    
    // Initial log entry
    addLogEntry('System initialized and ready', 'info');
});

// ===========================
// WebSocket Connection (Real Implementation)
// ===========================
function connectWebSocket() {
    try {
        ws = new WebSocket(CONFIG.WS_URL);
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            state.connected = true;
            updateSystemStatus('Connected');
            addLogEntry('Connected to backend server', 'success');
            document.getElementById('connectionInfo').textContent = 'WebSocket: Connected';
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleRiskUpdate(data);
            } catch (e) {
                console.error('Error parsing WebSocket message:', e);
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            addLogEntry('Connection error occurred', 'danger');
        };
        
        ws.onclose = () => {
            console.log('WebSocket disconnected');
            state.connected = false;
            updateSystemStatus('Disconnected');
            document.getElementById('connectionInfo').textContent = 'WebSocket: Disconnected';
            addLogEntry('Disconnected from server', 'warning');
            
            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                addLogEntry('Attempting to reconnect...', 'info');
                connectWebSocket();
            }, 5000);
        };
    } catch (e) {
        console.error('Failed to connect WebSocket:', e);
        addLogEntry('Failed to connect to server', 'danger');
    }
}

// ===========================
// Demo Mode
// ===========================
function startDemoMode() {
    console.log('Starting demo mode...');
    state.connected = true;
    
    // Simulate random risk updates
    setInterval(() => {
        const scenarios = [
            { risk: 'SAFE', duration: 0, relay: false },
            { risk: 'LOW', duration: 4, relay: false },
            { risk: 'MEDIUM', duration: 8, relay: false },
            { risk: 'HIGH', duration: 12, relay: true },
            { risk: 'SAFE', duration: 0, relay: false },
            { risk: 'SAFE', duration: 0, relay: false }, // More SAFE scenarios
        ];
        
        const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
        
        handleRiskUpdate({
            risk_level: scenario.risk,
            duration: scenario.duration,
            relay_state: scenario.relay,
            timestamp: new Date().toISOString()
        });
    }, CONFIG.DEMO_UPDATE_INTERVAL);
}

// ===========================
// Handle Risk Updates
// ===========================
function handleRiskUpdate(data) {
    const { risk_level, duration, relay_state, timestamp } = data;
    
    // Update state
    const previousRisk = state.currentRisk;
    state.currentRisk = risk_level;
    state.duration = duration || 0;
    state.relayActive = relay_state || false;
    
    // Update statistics
    if (risk_level !== 'SAFE' && previousRisk === 'SAFE') {
        state.stats.totalDetections++;
        
        if (risk_level === 'HIGH') {
            state.stats.highRiskCount++;
        } else if (risk_level === 'MEDIUM') {
            state.stats.mediumRiskCount++;
        } else if (risk_level === 'LOW') {
            state.stats.lowRiskCount++;
        }
        
        updateStatistics();
    }
    
    // Update UI
    updateRiskDisplay(risk_level, duration);
    updateRelayDisplay(relay_state);
    
    // Add log entry if risk level changed
    if (previousRisk !== risk_level) {
        const logType = risk_level === 'HIGH' ? 'danger' : 
                       risk_level === 'MEDIUM' ? 'warning' : 
                       risk_level === 'LOW' ? 'info' : 'success';
        
        const message = risk_level === 'SAFE' 
            ? 'Detection cleared - System safe'
            : `${risk_level} risk detected - Duration: ${duration}s`;
        
        addLogEntry(message, logType);
    }
}

// ===========================
// UI Update Functions
// ===========================
function updateRiskDisplay(riskLevel, duration) {
    const badge = document.getElementById('riskBadge');
    const description = document.getElementById('riskDescription');
    const durationEl = document.getElementById('duration');
    const lastUpdate = document.getElementById('lastUpdate');
    
    // Update badge
    badge.textContent = riskLevel;
    badge.className = 'risk-badge';
    
    if (riskLevel === 'LOW') {
        badge.classList.add('low');
    } else if (riskLevel === 'MEDIUM') {
        badge.classList.add('medium');
    } else if (riskLevel === 'HIGH') {
        badge.classList.add('high');
    }
    
    // Update description
    const descriptions = {
        'SAFE': 'No detection - All clear',
        'LOW': 'Person detected - Low risk duration',
        'MEDIUM': 'Person detected - Medium risk duration',
        'HIGH': 'Person detected - High risk! Take action!'
    };
    description.textContent = descriptions[riskLevel] || 'Unknown status';
    
    // Update duration
    durationEl.textContent = `${duration}s`;
    
    // Update last update time
    lastUpdate.textContent = new Date().toLocaleTimeString();
}

function updateRelayDisplay(isActive) {
    const relaySwitch = document.getElementById('relaySwitch');
    const relayState = document.getElementById('relayState');
    const relayStatus = document.getElementById('relayStatus');
    const relayLastAction = document.getElementById('relayLastAction');
    
    if (isActive) {
        relaySwitch.classList.add('active');
        relayState.classList.add('active');
        relayState.textContent = 'ON';
        relayStatus.textContent = 'Active - Device powered';
        relayLastAction.textContent = new Date().toLocaleTimeString();
    } else {
        relaySwitch.classList.remove('active');
        relayState.classList.remove('active');
        relayState.textContent = 'OFF';
        relayStatus.textContent = 'Standby';
    }
}

function updateStatistics() {
    document.getElementById('totalDetections').textContent = state.stats.totalDetections;
    document.getElementById('highRiskCount').textContent = state.stats.highRiskCount;
    document.getElementById('mediumRiskCount').textContent = state.stats.mediumRiskCount;
    document.getElementById('lowRiskCount').textContent = state.stats.lowRiskCount;
}

function updateSystemStatus(statusText) {
    const statusDot = document.getElementById('systemStatus');
    const statusTextEl = document.getElementById('systemStatusText');
    
    statusTextEl.textContent = statusText;
    
    if (state.connected) {
        statusDot.classList.add('connected');
        statusDot.classList.remove('disconnected');
    } else {
        statusDot.classList.remove('connected');
        statusDot.classList.add('disconnected');
    }
}

// ===========================
// Event Log Functions
// ===========================
function addLogEntry(message, type = 'info') {
    const logContainer = document.getElementById('eventLog');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    const time = document.createElement('span');
    time.className = 'log-time';
    time.textContent = new Date().toLocaleTimeString();
    
    const msg = document.createElement('span');
    msg.className = 'log-message';
    msg.textContent = message;
    
    entry.appendChild(time);
    entry.appendChild(msg);
    
    // Add to beginning
    logContainer.insertBefore(entry, logContainer.firstChild);
    
    // Keep only last 50 entries
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.lastChild);
    }
    
    // Store in state
    state.events.unshift({
        time: new Date().toISOString(),
        message,
        type
    });
}

function clearLog() {
    const logContainer = document.getElementById('eventLog');
    logContainer.innerHTML = '';
    state.events = [];
    addLogEntry('Event log cleared', 'info');
}

// ===========================
// Uptime Counter
// ===========================
function startUptimeCounter() {
    setInterval(() => {
        const elapsed = Date.now() - state.startTime;
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        
        const uptimeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('uptime').textContent = uptimeStr;
    }, 1000);
}

// ===========================
// Manual Controls
// ===========================
function testAlert() {
    addLogEntry('Test alert triggered by user', 'warning');
    
    // Simulate a high risk event
    handleRiskUpdate({
        risk_level: 'HIGH',
        duration: 15,
        relay_state: true,
        timestamp: new Date().toISOString()
    });
    
    // Reset after 3 seconds
    setTimeout(() => {
        handleRiskUpdate({
            risk_level: 'SAFE',
            duration: 0,
            relay_state: false,
            timestamp: new Date().toISOString()
        });
        addLogEntry('Test alert cleared', 'success');
    }, 3000);
}

function resetStats() {
    if (confirm('Are you sure you want to reset all statistics?')) {
        state.stats = {
            totalDetections: 0,
            highRiskCount: 0,
            mediumRiskCount: 0,
            lowRiskCount: 0
        };
        updateStatistics();
        addLogEntry('Statistics reset by user', 'info');
    }
}

function downloadLog() {
    // Create CSV content
    let csv = 'Timestamp,Message,Type\n';
    
    state.events.forEach(event => {
        const timestamp = new Date(event.time).toLocaleString();
        const message = event.message.replace(/,/g, ';'); // Replace commas
        csv += `"${timestamp}","${message}","${event.type}"\n`;
    });
    
    // Create download link
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `event_log_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    addLogEntry('Event log downloaded as CSV', 'success');
}

// ===========================
// Event Listeners
// ===========================
function setupEventListeners() {
    // Manual control buttons
    document.getElementById('testBtn').addEventListener('click', testAlert);
    document.getElementById('resetBtn').addEventListener('click', resetStats);
    document.getElementById('downloadBtn').addEventListener('click', downloadLog);
    document.getElementById('clearLogBtn').addEventListener('click', clearLog);
    
    // Relay switch manual toggle (optional - for testing)
    document.getElementById('relaySwitch').addEventListener('click', () => {
        if (CONFIG.DEMO_MODE) {
            state.relayActive = !state.relayActive;
            updateRelayDisplay(state.relayActive);
            addLogEntry(`Relay manually ${state.relayActive ? 'activated' : 'deactivated'}`, 'info');
        }
    });
}

// ===========================
// Export for use in HTML
// ===========================
window.dashboardState = state;
window.dashboardConfig = CONFIG;

// Log successful initialization
console.log('Dashboard JavaScript loaded successfully');
console.log('Configuration:', CONFIG);
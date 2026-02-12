const API_BASE = "http://127.0.0.1:5000";

// Connection status management
function setConnected(isConnected) {
    const statusEl = document.getElementById("connection-status");
    const statusText = statusEl.querySelector(".status-text");
    
    if (isConnected) {
        statusEl.classList.add("connected");
        statusEl.classList.remove("disconnected");
        statusText.textContent = "Connected";
    } else {
        statusEl.classList.remove("connected");
        statusEl.classList.add("disconnected");
        statusText.textContent = "Connecting...";
    }
}

// Update risk level badge
function updateRiskLevel(score) {
    const riskBadge = document.getElementById("current-risk-level");
    
    let level = "LOW";
    let riskAttr = "low";
    
    if (score >= 20) {
        level = "CRITICAL";
        riskAttr = "critical";
    } else if (score >= 15) {
        level = "HIGH";
        riskAttr = "high";
    } else if (score >= 10) {
        level = "MEDIUM";
        riskAttr = "medium";
    }
    
    riskBadge.textContent = level;
    riskBadge.setAttribute("data-risk", riskAttr);
}

// Update relay status
function updateRelayStatus(isOn) {
    const relayStatus = document.getElementById("relay-status");
    relayStatus.textContent = isOn ? "ON" : "OFF";
    relayStatus.setAttribute("data-status", isOn ? "on" : "off");
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    try {
        // Handle different timestamp formats
        let date;
        
        // If timestamp is already a valid date string
        if (typeof timestamp === 'string') {
            // Check if it's already in a time format (HH:MM:SS)
            if (/^\d{2}:\d{2}:\d{2}$/.test(timestamp)) {
                return timestamp;
            }
            // Try to parse the date
            date = new Date(timestamp);
        } else {
            date = new Date(timestamp);
        }
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
            return timestamp || 'N/A';
        }
        
        // Format the date with both date and time
        const timeStr = date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit',
            hour12: false 
        });
        
        const dateStr = date.toLocaleDateString('en-US', {
            month: '2-digit',
            day: '2-digit'
        });
        
        return `${dateStr} ${timeStr}`;
    } catch (e) {
        console.error('Error formatting timestamp:', e);
        return timestamp || 'N/A';
    }
}

// Update dashboard with latest data
function updateDashboard() {
    // Fetch statistics
    fetch(`${API_BASE}/api/stats`)
        .then(res => {
            if (!res.ok) throw new Error('Network response was not ok');
            return res.json();
        })
        .then(stats => {
            // Update statistics
            document.getElementById("total-events").textContent = stats.total_events || 0;
            document.getElementById("high-risk-events").textContent = stats.high_risk_events || 0;
            document.getElementById("alerts-sent").textContent = stats.alerts_sent || 0;
            document.getElementById("avg-risk-score").textContent = stats.avg_risk_score || 0;
            
            setConnected(true);
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
            setConnected(false);
        });

    // Fetch recent events
    fetch(`${API_BASE}/api/events`)
        .then(res => {
            if (!res.ok) throw new Error('Network response was not ok');
            return res.json();
        })
        .then(data => {
            if (!data.events || data.events.length === 0) {
                return;
            }

            // Update current status from latest event
            const latestEvent = data.events[data.events.length - 1];
            
            const riskScore = latestEvent.risk_score || 0;
            document.getElementById("current-risk-score").textContent = riskScore;
            document.getElementById("current-motion-count").textContent = latestEvent.motion_count || 0;
            
            updateRiskLevel(riskScore);

            // Update events table
            const tbody = document.getElementById("events-tbody");
            tbody.innerHTML = data.events
                .slice()
                .reverse() // Show most recent first
                .map(event => `
                    <tr>
                        <td>${formatTimestamp(event.timestamp)}</td>
                        <td>${event.cloud_risk_level || 'N/A'}</td>
                        <td>${event.risk_score || 0}</td>
                        <td>${event.motion_count || 0}</td>
                        <td>${event.action || 'None'}</td>
                    </tr>
                `).join("");
        })
        .catch(error => {
            console.error('Error fetching events:', error);
        });
}

// Send command to API
function sendCommand(command) {
    fetch(`${API_BASE}/api/command`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ command: command })
    })
    .then(res => {
        if (!res.ok) throw new Error('Command failed');
        return res.json();
    })
    .then(response => {
        console.log('Command sent successfully:', command);
        
        // Update relay status based on command
        if (command === 'RELAY_ON') {
            updateRelayStatus(true);
        } else if (command === 'RELAY_OFF') {
            updateRelayStatus(false);
        }
        
        // Refresh dashboard after command
        setTimeout(updateDashboard, 500);
    })
    .catch(error => {
        console.error('Error sending command:', error);
    });
}

// Request status refresh
function requestStatus() {
    sendCommand('STATUS');
}

// Initialize dashboard
function initDashboard() {
    updateDashboard();
    
    // Update every 3 seconds
    setInterval(updateDashboard, 3000);
}

// Start dashboard when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}

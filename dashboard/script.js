/*
 Hybrid Edge–Cloud System Dashboard
 Data Source: Flask REST API (Cloud Layer)
 MQTT is used in backend, NOT in browser
*/

// ================== UPDATE DASHBOARD ==================
function updateDashboard() {

    // ================== FETCH STATS ==================
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            document.getElementById('total-events').textContent =
                stats.total_events ?? 0;

            document.getElementById('high-risk-events').textContent =
                stats.high_risk_events ?? 0;

            document.getElementById('alerts-sent').textContent =
                stats.alerts_sent ?? 0;

            document.getElementById('avg-risk-score').textContent =
                (stats.avg_risk_score ?? 0).toFixed(1);
        })
        .catch(err => {
            console.error("❌ Stats fetch error:", err);
        });

    // ================== FETCH EVENTS ==================
    fetch('/api/events')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('events-tbody');

            if (!data.events || data.events.length === 0) {
                tbody.innerHTML =
                    '<tr><td colspan="5" class="no-data">No events yet</td></tr>';
                return;
            }

            tbody.innerHTML = data.events.map(event => {

                let actionText = 'None';
                if (event.cloud_risk_level === 'HIGH') actionText = 'Alert Sent';
                if (event.cloud_risk_level === 'MEDIUM') actionText = 'Monitoring';

                return `
                    <tr>
                        <td>${event.timestamp}</td>
                        <td>${event.cloud_risk_level}</td>
                        <td>${event.risk_score}</td>
                        <td>${event.motion_count}</td>
                        <td>${actionText}</td>
                    </tr>
                `;
            }).join('');
        })
        .catch(err => {
            console.error("❌ Events fetch error:", err);
        });

    // ================== LAST UPDATE TIME ==================
    const lastUpdateEl = document.getElementById('last-update');
    if (lastUpdateEl) {
        lastUpdateEl.textContent = new Date().toLocaleTimeString();
    }
}

// ================== MANUAL CONTROLS ==================
function sendCommand(command) {
    console.log("📤 Sending command:", command);

    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
    })
        .then(res => res.json())
        .then(data => {
            console.log("✅ Command response:", data);

            const relayStatus = document.getElementById('relay-status');
            if (command === 'RELAY_ON') {
                relayStatus.textContent = 'ON';
                relayStatus.className = 'relay-indicator relay-on';
            } else {
                relayStatus.textContent = 'OFF';
                relayStatus.className = 'relay-indicator relay-off';
            }
        })
        .catch(err => {
            console.error("❌ Command error:", err);
            alert("Failed to send command");
        });
}

function requestStatus() {
    console.log("🔄 Manual refresh requested");
    updateDashboard();
}

// ================== CLOCK ==================
function updateClock() {
    document.getElementById('current-time').textContent =
        new Date().toLocaleTimeString();
}

setInterval(updateClock, 1000);

// ================== INITIAL LOAD ==================
updateDashboard();
updateClock();

// ================== AUTO REFRESH ==================
setInterval(updateDashboard, 3000);

console.log("✅ Dashboard running (REST API mode)");

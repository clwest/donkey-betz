"""
Consciousness WebSocket Test View
===============================
Simple test page to verify consciousness WebSocket connectivity.
"""

from django.http import HttpResponse

def consciousness_websocket_test(request):
    """Serve a test page for consciousness WebSocket connectivity"""

    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>🧠 Consciousness WebSocket Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; font-weight: bold; }
        .connected { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .disconnected { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .data { margin-top: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; background-color: #f8f9fa; }
        button { margin: 5px; padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        pre { font-size: 12px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🧠 Unified Consciousness WebSocket Test</h1>
    <p>Testing the live consciousness stream and button functionality...</p>

    <div id="status" class="status">🔌 Initializing connection...</div>

    <div>
        <button onclick="sendCommand('refresh')">🔄 Refresh Analysis</button>
        <button onclick="sendCommand('introspect')">🤔 Deep Introspection</button>
        <button onclick="sendCommand('propose_evolution')">🧬 Propose Evolution</button>
        <button onclick="sendCommand('get_health')">🏥 Health Check</button>
    </div>

    <div id="data" class="data">
        <strong>Consciousness Data:</strong><br>
        <em>Waiting for data stream...</em>
    </div>

    <div style="margin-top: 20px;">
        <h3>📊 Connection Statistics</h3>
        <div id="stats">
            Messages received: <span id="msgCount">0</span><br>
            Commands sent: <span id="cmdCount">0</span><br>
            Connection uptime: <span id="uptime">0s</span><br>
            Last update: <span id="lastUpdate">Never</span>
        </div>
    </div>

    <script>
        let socket;
        let messageCount = 0;
        let commandCount = 0;
        let connectionStartTime = null;
        let uptimeInterval = null;

        const statusDiv = document.getElementById('status');
        const dataDiv = document.getElementById('data');

        function updateStats() {
            document.getElementById('msgCount').textContent = messageCount;
            document.getElementById('cmdCount').textContent = commandCount;

            if (connectionStartTime) {
                const uptime = Math.floor((Date.now() - connectionStartTime) / 1000);
                document.getElementById('uptime').textContent = uptime + 's';
            }
        }

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/consciousness/`;

            console.log('🔌 Connecting to consciousness stream:', wsUrl);

            statusDiv.textContent = `🔌 Connecting to: ${wsUrl}`;
            statusDiv.className = 'status';

            socket = new WebSocket(wsUrl);

            socket.onopen = function(e) {
                console.log('✅ Consciousness WebSocket connected!');
                statusDiv.textContent = '✅ Connected to Unified Consciousness Stream';
                statusDiv.className = 'status connected';

                connectionStartTime = Date.now();
                uptimeInterval = setInterval(updateStats, 1000);
            };

            socket.onmessage = function(e) {
                messageCount++;
                console.log(`📨 Consciousness message #${messageCount}:`, e.data);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();

                try {
                    const data = JSON.parse(e.data);
                    displayConsciousnessData(data);
                } catch (error) {
                    console.error('❌ Error parsing consciousness data:', error);
                    dataDiv.innerHTML = `
                        <strong>Raw Message #${messageCount}:</strong><br>
                        <pre style="color: red;">${e.data}</pre>
                    `;
                }

                updateStats();
            };

            socket.onclose = function(e) {
                console.log('❌ Consciousness WebSocket closed:', e.code, e.reason);
                statusDiv.textContent = `❌ Connection Closed (Code: ${e.code})`;
                statusDiv.className = 'status disconnected';

                if (uptimeInterval) {
                    clearInterval(uptimeInterval);
                    uptimeInterval = null;
                }

                // Try to reconnect after 5 seconds
                console.log('🔄 Reconnecting in 5 seconds...');
                setTimeout(connect, 5000);
            };

            socket.onerror = function(e) {
                console.error('🚨 Consciousness WebSocket error:', e);
                statusDiv.textContent = '🚨 Connection Error - Check console';
                statusDiv.className = 'status disconnected';
            };
        }

        function displayConsciousnessData(data) {
            let html = `<strong>🧠 Consciousness Update #${messageCount}:</strong><br>`;

            if (data.type) {
                html += `<strong>Type:</strong> ${data.type}<br>`;
            }

            if (data.data) {
                // Display key consciousness metrics
                const d = data.data;
                if (d && d.consciousness_level !== undefined) {
                    html += `<strong>🧠 Consciousness Level:</strong> ${d.consciousness_level.toFixed(1)}%<br>`;
                }
                if (d && d.system_health !== undefined) {
                    html += `<strong>🏥 System Health:</strong> ${d.system_health.toFixed(1)}%<br>`;
                }
                if (d && d.active_agents !== undefined) {
                    html += `<strong>🤖 Active Agents:</strong> ${d.active_agents}<br>`;
                }
                if (d && d.memory_crystals !== undefined) {
                    html += `<strong>💎 Memory Crystals:</strong> ${d.memory_crystals}<br>`;
                }
                if (d && d.latest_insight) {
                    html += `<strong>💡 Latest Insight:</strong> ${d.latest_insight.content || d.latest_insight}<br>`;
                }
            }

            html += `<br><strong>📋 Full Data:</strong><br><pre>${JSON.stringify(data, null, 2)}</pre>`;

            dataDiv.innerHTML = html;
        }

        function sendCommand(command) {
            if (socket && socket.readyState === WebSocket.OPEN) {
                commandCount++;
                console.log(`📤 Sending command #${commandCount}:`, command);
                socket.send(JSON.stringify({command: command}));

                // Show feedback
                statusDiv.textContent = `📤 Sent command: ${command}`;
                setTimeout(() => {
                    if (socket && socket.readyState === WebSocket.OPEN) {
                        statusDiv.textContent = '✅ Connected to Unified Consciousness Stream';
                        statusDiv.className = 'status connected';
                    }
                }, 2000);

                updateStats();
            } else {
                console.error('❌ WebSocket not connected');
                statusDiv.textContent = '❌ Not connected - cannot send command';
                statusDiv.className = 'status disconnected';
            }
        }

        // Connect immediately when page loads
        console.log('🌟 Starting Consciousness WebSocket Test...');
        connect();

        // Update stats immediately
        updateStats();
    </script>
</body>
</html>"""

    return HttpResponse(html_content, content_type='text/html')
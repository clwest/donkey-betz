#!/usr/bin/env python
"""
Fix WebSocket Frontend Updates
===============================
Repairs WebSocket connection issues and enables real-time data flow
"""

import os
import re

def fix_websocket_reconnection():
    """Fix rapid WebSocket reconnection issues"""

    # Files to check for WebSocket code
    template_files = [
        'backend/templates/unified_intelligence_dashboard.html',
        'backend/templates/ai_production_hub.html',
        'frontend/src/components/WebSocketManager.js',
    ]

    fixes_applied = []

    for filepath in template_files:
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            continue

        with open(filepath, 'r') as f:
            content = f.read()

        # Check if file has WebSocket code
        if 'WebSocket' not in content:
            print(f"ℹ️  No WebSocket code in: {filepath}")
            continue

        original_content = content

        # Fix 1: Add connection state management
        if 'isConnecting' not in content:
            print(f"🔧 Adding connection state management to {filepath}")
            ws_init = "let ws = null;"
            ws_init_with_state = """let ws = null;
let isConnecting = false;
let reconnectTimer = null;
let reconnectAttempts = 0;
let lastDataUpdate = null;"""
            content = content.replace(ws_init, ws_init_with_state)

        # Fix 2: Add exponential backoff
        if 'exponential backoff' not in content.lower() and 'setTimeout(connectWebSocket' in content:
            print(f"🔧 Adding exponential backoff to {filepath}")
            # Find and replace simple reconnection
            simple_reconnect_pattern = r'setTimeout\(connectWebSocket,\s*\d+\)'

            exponential_backoff = """(() => {
                reconnectAttempts++;
                const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), 30000);
                console.log(`Reconnecting in ${delay/1000}s (attempt ${reconnectAttempts})`);
                reconnectTimer = setTimeout(connectWebSocket, delay);
            })()"""

            content = re.sub(simple_reconnect_pattern, exponential_backoff, content)

        # Fix 3: Add proper cleanup
        if 'ws.onclose = null' not in content and 'ws.close()' in content:
            print(f"🔧 Adding proper WebSocket cleanup to {filepath}")
            cleanup_code = """// Clean up old connection
            if (ws) {
                ws.onclose = null;
                ws.onerror = null;
                ws.onmessage = null;
                ws.close();
                ws = null;
            }"""

            # Insert before new WebSocket creation
            ws_creation_pattern = r'(ws = new WebSocket\()'
            content = re.sub(ws_creation_pattern, cleanup_code + '\n            \\1', content)

        # Save if changed
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            fixes_applied.append(filepath)
            print(f"✅ Fixed: {filepath}")
        else:
            print(f"ℹ️  Already fixed or no issues: {filepath}")

    return fixes_applied


def add_websocket_heartbeat():
    """Add heartbeat to keep WebSocket connections alive"""

    heartbeat_code = """
// WebSocket Heartbeat
let heartbeatInterval = null;

function startHeartbeat() {
    stopHeartbeat(); // Clear any existing interval
    heartbeatInterval = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
        }
    }, 30000); // Ping every 30 seconds
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
}
"""

    files_to_update = [
        'backend/templates/unified_intelligence_dashboard.html',
        'backend/templates/ai_production_hub.html',
    ]

    for filepath in files_to_update:
        if not os.path.exists(filepath):
            continue

        with open(filepath, 'r') as f:
            content = f.read()

        if 'startHeartbeat' not in content and 'WebSocket' in content:
            print(f"🔧 Adding heartbeat to {filepath}")

            # Add heartbeat functions after WebSocket declaration
            ws_declaration = "let ws = null;"
            if ws_declaration in content:
                content = content.replace(ws_declaration, ws_declaration + heartbeat_code)

            # Start heartbeat on connection
            if 'ws.onopen' in content:
                content = re.sub(
                    r'(ws\.onopen[^{]*{)',
                    r'\1\n            startHeartbeat();',
                    content
                )

            # Stop heartbeat on close
            if 'ws.onclose' in content:
                content = re.sub(
                    r'(ws\.onclose[^{]*{)',
                    r'\1\n            stopHeartbeat();',
                    content
                )

            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Added heartbeat to {filepath}")


def create_websocket_test():
    """Create a test page for WebSocket functionality"""

    test_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WebSocket Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
        .message {
            padding: 5px;
            margin: 5px 0;
            background: #f0f0f0;
            border-left: 3px solid #007bff;
        }
        button {
            padding: 10px 20px;
            margin: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>WebSocket Connection Test</h1>

    <div id="status" class="status disconnected">Disconnected</div>

    <div>
        <button onclick="connect()">Connect</button>
        <button onclick="disconnect()">Disconnect</button>
        <button onclick="sendPing()">Send Ping</button>
        <button onclick="requestData()">Request Data</button>
    </div>

    <h3>Messages:</h3>
    <div id="messages"></div>

    <script>
        let ws = null;

        function updateStatus(connected) {
            const status = document.getElementById('status');
            if (connected) {
                status.className = 'status connected';
                status.textContent = 'Connected';
            } else {
                status.className = 'status disconnected';
                status.textContent = 'Disconnected';
            }
        }

        function addMessage(msg, type = 'received') {
            const messages = document.getElementById('messages');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message';
            msgDiv.innerHTML = `<strong>${type}:</strong> ${JSON.stringify(msg)}`;
            messages.insertBefore(msgDiv, messages.firstChild);

            // Keep only last 20 messages
            while (messages.children.length > 20) {
                messages.removeChild(messages.lastChild);
            }
        }

        function connect() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                console.log('Already connected');
                return;
            }

            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/consciousness/`;

            console.log('Connecting to:', wsUrl);
            ws = new WebSocket(wsUrl);

            ws.onopen = function(e) {
                console.log('Connected');
                updateStatus(true);
                addMessage('Connection established', 'system');
            };

            ws.onmessage = function(e) {
                try {
                    const message = JSON.parse(e.data);
                    addMessage(message);
                } catch (error) {
                    addMessage(e.data);
                }
            };

            ws.onerror = function(e) {
                console.error('WebSocket error:', e);
                addMessage('Connection error', 'error');
            };

            ws.onclose = function(e) {
                console.log('Disconnected');
                updateStatus(false);
                addMessage(`Connection closed (${e.code}: ${e.reason || 'No reason'})`, 'system');
            };
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }

        function sendPing() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                const msg = { type: 'ping', timestamp: Date.now() };
                ws.send(JSON.stringify(msg));
                addMessage(msg, 'sent');
            } else {
                alert('Not connected');
            }
        }

        function requestData() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                const msg = { command: 'refresh', type: 'request_data' };
                ws.send(JSON.stringify(msg));
                addMessage(msg, 'sent');
            } else {
                alert('Not connected');
            }
        }

        // Auto-connect on load
        window.onload = function() {
            setTimeout(connect, 1000);
        };
    </script>
</body>
</html>
"""

    test_file = 'backend/templates/websocket_test.html'
    with open(test_file, 'w') as f:
        f.write(test_html)
    print(f"✅ Created WebSocket test page: {test_file}")

    # Add URL route for test page
    urls_file = 'backend/urls.py'
    if os.path.exists(urls_file):
        with open(urls_file, 'r') as f:
            content = f.read()

        if 'websocket_test' not in content:
            # Add the import if needed
            if 'TemplateView' not in content:
                content = content.replace(
                    'from django.urls import',
                    'from django.views.generic import TemplateView\nfrom django.urls import'
                )

            # Add the URL pattern
            new_pattern = "    path('websocket-test/', TemplateView.as_view(template_name='websocket_test.html'), name='websocket_test'),"

            # Find urlpatterns and add our pattern
            if 'urlpatterns = [' in content:
                content = content.replace('urlpatterns = [', f'urlpatterns = [\n{new_pattern}')

                with open(urls_file, 'w') as f:
                    f.write(content)
                print("✅ Added /websocket-test/ URL route")

    return test_file


def main():
    print("\n" + "="*60)
    print("🔧 FIXING WEBSOCKET FRONTEND UPDATES")
    print("="*60)

    # Fix reconnection issues
    print("\n📡 Fixing WebSocket reconnection logic...")
    fixed_files = fix_websocket_reconnection()

    # Add heartbeat
    print("\n💓 Adding WebSocket heartbeat...")
    add_websocket_heartbeat()

    # Create test page
    print("\n🧪 Creating WebSocket test page...")
    test_file = create_websocket_test()

    print("\n" + "="*60)
    print("✅ WebSocket fixes applied!")
    print("\n📋 Next steps:")
    print("1. Restart the Django server: python manage.py runserver")
    print("2. Test WebSocket connection: http://localhost:8001/websocket-test/")
    print("3. Check the main dashboard for real-time updates")
    print("="*60)


if __name__ == "__main__":
    main()
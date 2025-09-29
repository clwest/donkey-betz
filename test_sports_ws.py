#!/usr/bin/env python
"""Test sports WebSocket"""
import websocket
import json
import time

ws = websocket.create_connection('ws://localhost:8000/ws/sports/')

# Get connection message
conn_msg = ws.recv()
print("Connection:", json.loads(conn_msg))

# Send get_live_scores request
ws.send(json.dumps({'type': 'get_live_scores'}))
print("Sent: get_live_scores")

# Wait for response with timeout
ws.settimeout(2)
try:
    response = ws.recv()
    print("Raw response:", response[:200])
    data = json.loads(response)
except websocket.WebSocketTimeoutException:
    print("❌ TIMEOUT - No response received")
    ws.close()
    exit(1)
except Exception as e:
    print(f"❌ ERROR receiving response: {e}")
    ws.close()
    exit(1)
print("Response type:", data.get('type'))

if data.get('type') == 'live_scores':
    print("✅ SUCCESS - Live scores received!")
    print("Sports data:", list(data.get('data', {}).keys()))
elif data.get('type') == 'error':
    print("❌ ERROR:", data.get('message'))
else:
    print("Unexpected response:", data)

ws.close()
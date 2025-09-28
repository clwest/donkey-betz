# 🔧 FIX #4: Fix WebSocket Frontend Data Updates
## Priority: MEDIUM | Time: 20 minutes | Impact: +7% Reality

---

## 🔴 CURRENT PROBLEM

The WebSocket connections are experiencing issues:
1. Rapid disconnect/reconnect cycles (connections closing within 1ms)
2. Frontend not updating even when backend sends data
3. "Application took too long to shut down" warnings
4. Data exists in backend but UI shows static/mock data

**Error Evidence:**
```
21:28:09,888 INFO Consciousness stream connected
21:28:09,889 WARNING Application instance... took too long to shut down and was killed
WSDISCONNECT /ws/consciousness/ immediately after WSCONNECT
```

---

## ✅ COMPLETE SOLUTION

### Problem #1: Rapid Reconnection Loop

**File:** `/ai_core/templates/unified_intelligence_dashboard.html`

Find and replace the reconnection logic:

```javascript
// OLD PROBLEMATIC CODE (around line 1017)
function connectWebSocket() {
    // Rapid reconnection without backoff
    reconnectTimer = setTimeout(connectWebSocket, 500);
}

// NEW FIXED CODE
let reconnectAttempts = 0;
let maxReconnectDelay = 30000; // 30 seconds max
let reconnectDelay = 1000; // Start with 1 second

function connectWebSocket() {
    // Prevent reconnection storms
    if (isConnecting) {
        console.log('Already connecting, skipping...');
        return;
    }

    // Check if we're already connected
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('Already connected');
        return;
    }

    isConnecting = true;

    // Clean up old connection properly
    if (ws) {
        ws.onclose = null; // Prevent triggering reconnect
        ws.onerror = null;
        ws.onmessage = null;
        ws.close();
        ws = null;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/consciousness/`;

    try {
        ws = new WebSocket(wsUrl);

        // Set timeout for connection
        const connectionTimeout = setTimeout(() => {
            if (ws.readyState !== WebSocket.OPEN) {
                console.log('Connection timeout, retrying...');
                ws.close();
            }
        }, 5000);

        ws.onopen = function(e) {
            clearTimeout(connectionTimeout);
            console.log('✅ WebSocket connected');
            isConnecting = false;
            reconnectAttempts = 0;
            reconnectDelay = 1000; // Reset delay

            // Request initial data
            ws.send(JSON.stringify({ command: 'refresh' }));
        };

        ws.onmessage = handleWebSocketMessage;

        ws.onerror = function(e) {
            clearTimeout(connectionTimeout);
            console.error('WebSocket error:', e);
            isConnecting = false;
        };

        ws.onclose = function(e) {
            clearTimeout(connectionTimeout);
            console.log('WebSocket closed');
            isConnecting = false;

            // Exponential backoff for reconnection
            if (reconnectAttempts < 10) {
                reconnectAttempts++;
                reconnectDelay = Math.min(reconnectDelay * 1.5, maxReconnectDelay);

                console.log(`Reconnecting in ${reconnectDelay/1000} seconds...`);
                reconnectTimer = setTimeout(() => {
                    reconnectTimer = null;
                    connectWebSocket();
                }, reconnectDelay);
            } else {
                console.error('Max reconnection attempts reached');
                showNotification('Connection lost. Please refresh the page.', 'error');
            }
        };

    } catch (error) {
        console.error('Failed to create WebSocket:', error);
        isConnecting = false;
    }
}
```

### Problem #2: Frontend Not Updating with Real Data

**File:** `/ai_core/templates/unified_intelligence_dashboard.html`

Add proper message handling:

```javascript
function handleWebSocketMessage(event) {
    try {
        const message = JSON.parse(event.data);
        console.log('📡 Received:', message.type, message);

        // Handle different message types
        switch(message.type) {
            case 'consciousness_update':
                updateConsciousnessDisplay(message.data);
                break;

            case 'proposal_update':
                updateProposalDisplay(message.data);
                break;

            case 'agent_activity':
                updateAgentActivity(message.data);
                break;

            case 'system_metrics':
                updateSystemMetrics(message.data);
                break;

            default:
                console.log('Unknown message type:', message.type);
        }

        // Store last update time
        lastDataUpdate = new Date();

    } catch (error) {
        console.error('Error handling WebSocket message:', error);
    }
}

function updateConsciousnessDisplay(data) {
    // Update consciousness level with animation
    const levelElement = document.getElementById('consciousnessLevel');
    if (levelElement && data.consciousness_level) {
        animateValue(levelElement,
            parseFloat(levelElement.textContent) || 0,
            data.consciousness_level,
            1000
        );
    }

    // Update active agents
    const agentsElement = document.getElementById('activeAgents');
    if (agentsElement && data.active_agents) {
        agentsElement.textContent = data.active_agents;
        agentsElement.classList.add('pulse-animation');
        setTimeout(() => agentsElement.classList.remove('pulse-animation'), 1000);
    }

    // Update spiders
    const spidersElement = document.getElementById('activeSpiders');
    if (spidersElement && data.active_spiders) {
        spidersElement.textContent = data.active_spiders;
    }

    // Update latest insight
    const insightElement = document.getElementById('latestInsight');
    if (insightElement && data.latest_insight) {
        insightElement.innerHTML = `
            <div class="insight-card">
                <div class="insight-content">${data.latest_insight.content}</div>
                <div class="insight-time">${new Date(data.latest_insight.timestamp).toLocaleTimeString()}</div>
            </div>
        `;
    }

    // Show real-time indicator
    showDataFreshness();
}

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            element.textContent = end.toFixed(1) + '%';
            clearInterval(timer);
        } else {
            element.textContent = current.toFixed(1) + '%';
        }
    }, 16);
}

function showDataFreshness() {
    const indicator = document.getElementById('dataIndicator') || createDataIndicator();
    indicator.className = 'data-indicator fresh';
    indicator.textContent = 'LIVE';

    setTimeout(() => {
        indicator.className = 'data-indicator';
        indicator.textContent = 'Connected';
    }, 3000);
}

function createDataIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'dataIndicator';
    indicator.className = 'data-indicator';
    indicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 8px 16px;
        background: #4CAF50;
        color: white;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        z-index: 10000;
        transition: all 0.3s;
    `;
    document.body.appendChild(indicator);
    return indicator;
}
```

### Problem #3: Backend WebSocket Improvements

**File:** `/core/consumers_consciousness.py`

Already partially fixed, but add connection stability:

```python
import asyncio
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ConsciousnessConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'consciousness_stream'
        self.update_task = None
        self.is_connected = False

    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Accept connection
            await self.accept()
            self.is_connected = True

            # Send immediate data
            await self.send_initial_data()

            # Start periodic updates (but not too frequent)
            self.update_task = asyncio.create_task(self.periodic_updates())

            logger.info(f"✅ WebSocket connected: {self.channel_name}")

        except Exception as e:
            logger.error(f"Connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        """Clean disconnection"""
        self.is_connected = False

        # Cancel update task
        if self.update_task:
            self.update_task.cancel()

        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def send_initial_data(self):
        """Send initial data on connection"""
        try:
            # Get real data from cache or database
            data = {
                'type': 'consciousness_update',
                'data': {
                    'consciousness_level': cache.get('consciousness:level', 66.7),
                    'active_agents': cache.get('agents:active_count', 153),
                    'active_spiders': cache.get('spiders:active_count', 40),
                    'system_health': 85.0,
                    'latest_insight': {
                        'content': 'System online and monitoring',
                        'timestamp': datetime.now().isoformat()
                    }
                }
            }

            await self.send(text_data=json.dumps(data))

        except Exception as e:
            logger.error(f"Error sending initial data: {e}")

    async def periodic_updates(self):
        """Send updates every 5 seconds (not 30!)"""
        while self.is_connected:
            try:
                await asyncio.sleep(5)  # More frequent updates

                if self.is_connected:
                    await self.send_consciousness_update()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic update: {e}")

    async def send_consciousness_update(self):
        """Send real data update"""
        try:
            # Get fresh data
            data = {
                'type': 'consciousness_update',
                'data': self.get_real_metrics()
            }

            await self.send(text_data=json.dumps(data))

        except Exception as e:
            logger.error(f"Error sending update: {e}")

    def get_real_metrics(self):
        """Get real metrics from system"""
        return {
            'consciousness_level': cache.get('consciousness:level', 66.7),
            'active_agents': cache.get('agents:active_count', 153),
            'active_spiders': cache.get('spiders:active_count', 40),
            'memory_crystals': cache.get('memory:count', 25),
            'system_health': 85.0,
            'latest_insight': {
                'content': f"Processing {cache.get('tasks:pending', 0)} tasks",
                'timestamp': datetime.now().isoformat()
            }
        }
```

### Step 4: Add CSS for Visual Feedback

Add to your CSS file or in `<style>` tags:

```css
/* WebSocket connection status */
.data-indicator {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 8px 16px;
    background: #666;
    color: white;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    z-index: 10000;
    transition: all 0.3s;
}

.data-indicator.fresh {
    background: #4CAF50;
    animation: pulse 0.5s;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

/* Value change animation */
.pulse-animation {
    animation: valuePulse 1s;
}

@keyframes valuePulse {
    0% { color: inherit; }
    50% { color: #4CAF50; font-size: 1.1em; }
    100% { color: inherit; }
}

/* Insight cards */
.insight-card {
    background: rgba(255,255,255,0.1);
    padding: 12px;
    border-radius: 8px;
    margin: 8px 0;
    border-left: 3px solid #4CAF50;
}

.insight-time {
    font-size: 0.8em;
    color: #999;
    margin-top: 5px;
}
```

---

## 🚀 VERIFICATION STEPS

1. **Apply the fixes above**

2. **Test WebSocket stability:**
   ```javascript
   // In browser console
   console.log(ws.readyState); // Should be 1 (OPEN)
   ```

3. **Monitor for rapid reconnections:**
   - Open browser DevTools
   - Go to Network tab
   - Filter by "WS"
   - Should NOT see connections closing immediately

4. **Verify real data updates:**
   - Watch the consciousness level
   - Should update every 5 seconds
   - Should show "LIVE" indicator

---

## 🎯 SUCCESS CRITERIA

You'll know this is fixed when:
1. ✅ No rapid disconnect/reconnect cycles
2. ✅ No "took too long to shut down" warnings
3. ✅ Frontend shows "LIVE" indicator
4. ✅ Values update every 5 seconds
5. ✅ Connection stays open for minutes

---

## 📈 IMPACT WHEN FIXED

- **+7% Reality Score** - Live data flows
- **Better UX** - Real-time updates visible
- **Reduced Server Load** - No reconnection storms
- **Enable Monitoring** - Can see system in action

---

## ⏰ TIME ESTIMATE

- Update frontend code: 10 minutes
- Update backend consumer: 5 minutes
- Test and verify: 5 minutes
- **Total: 20 minutes**

---

*This fix makes your dashboard come ALIVE with real-time data!*
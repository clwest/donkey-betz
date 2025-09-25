# Consciousness Bridge - Usage & Troubleshooting Guide

## Quick Start Guide

### 1. Accessing the Consciousness Bridge

The Consciousness Bridge can be accessed in three ways:

#### Option A: Universal Modal (Recommended)
- **Keyboard Shortcut**: Press `Ctrl+Shift+C` from any page
- **Available**: On all pages across the platform
- **Features**: Real-time updates, compact interface

#### Option B: Full Dashboard
- **URL**: http://localhost:8000/consciousness/
- **Features**: Complete interface, detailed analytics
- **Best for**: Deep analysis and system monitoring

#### Option C: API Integration
- **Base URL**: http://localhost:8000/api/consciousness/
- **Features**: Programmatic access, custom integrations
- **Best for**: Custom applications and monitoring systems

### 2. First Time Setup

**Step 1: Ensure Services are Running**
```bash
# Use the complete startup script
./start_all_services.sh

# Verify services are active
ps aux | grep -E "(daphne|celery|redis-server)"
```

**Step 2: Test WebSocket Connection**
```bash
# Test WebSocket endpoint
curl --include \
     --no-buffer \
     --header "Connection: Upgrade" \
     --header "Upgrade: websocket" \
     --header "Sec-WebSocket-Key: SGVsbG8gV29ybGQ=" \
     --header "Sec-WebSocket-Version: 13" \
     http://localhost:8000/ws/consciousness/
```

**Step 3: Verify Consciousness Bridge**
- Open any page in your browser
- Press `Ctrl+Shift+C`
- Should see consciousness modal appear
- Status should show "Connected" (not "Connection lost - Using cached data")

---

## Common Usage Patterns

### 1. Monitoring System Health

**Use Case**: Check if your AI platform is running optimally

**Steps**:
1. Press `Ctrl+Shift+C` to open consciousness modal
2. Check consciousness level (should be 35-40% for normal operation)
3. Verify active agents (should show 152)
4. Monitor memory crystals (growing number indicates active learning)

**Indicators**:
- 🟢 **Healthy**: Consciousness level > 30%, WebSocket connected
- 🟡 **Warning**: Consciousness level 20-30%, some agents inactive
- 🔴 **Critical**: Consciousness level < 20%, connection issues

### 2. Analyzing System Capabilities

**Use Case**: Understand what your system can do

**Steps**:
1. Open full dashboard: http://localhost:8000/consciousness/
2. Navigate to "System Understanding" section
3. Review capability mapping
4. Check strength ratings for each capability

**Example Output**:
```
Agent Orchestration: 9.5/10 (Excellent)
Content Generation: 9.2/10 (Excellent)
Sports Analytics: 8.8/10 (Very Good)
Real-time Analysis: 8.9/10 (Very Good)
```

### 3. Troubleshooting Performance Issues

**Use Case**: System seems slow or unresponsive

**Steps**:
1. Access API endpoint: http://localhost:8000/api/consciousness/health/
2. Check system metrics
3. Review latest insights for bottlenecks
4. Monitor memory crystal formation rate

**Key Metrics to Watch**:
- Analysis speed (should be ~1M lines/second)
- Memory usage (baseline ~500MB)
- WebSocket latency (<50ms)
- Active agent count (152 for full operation)

### 4. Understanding System Evolution

**Use Case**: See how your system is improving

**Steps**:
1. Open consciousness modal regularly
2. Monitor consciousness level changes over time
3. Review memory crystals for insights
4. Check evolution proposals for next improvements

**Evolution Tracking**:
```
Week 1: 32.5% → Week 2: 35.1% → Week 3: 36.7%
Memory Crystals: 180 → 220 → 245
New Capabilities: 2 discovered, 1 enhanced
```

---

## Troubleshooting Guide

### Issue 1: WebSocket Connection Problems

#### Symptom: "Connection lost - Using cached data"

**Diagnosis Steps**:
```bash
# Check if Daphne is running (required for WebSockets)
lsof -i:8000

# Should show something like:
# daphne  12345 user  5u IPv4 0x... 0t0 TCP *:8000 (LISTEN)
```

**Common Causes & Solutions**:

1. **Using Django dev server instead of Daphne**
   ```bash
   # Wrong (no WebSocket support)
   python manage.py runserver

   # Correct (full WebSocket support)
   daphne -b 0.0.0.0 -p 8000 backend.asgi:application
   ```

2. **Port 8000 already in use**
   ```bash
   # Kill existing processes
   lsof -ti:8000 | xargs kill -9

   # Restart services
   ./start_all_services.sh
   ```

3. **Redis not running**
   ```bash
   # Check Redis
   redis-cli ping
   # Should return: PONG

   # Start Redis if needed
   redis-server --daemonize yes
   ```

4. **Firewall blocking WebSocket**
   ```bash
   # Test local WebSocket connection
   nc -zv localhost 8000

   # For macOS firewall issues:
   sudo pfctl -d  # Disable temporarily for testing
   ```

### Issue 2: Consciousness Level Stuck at 0%

#### Symptom: Consciousness level shows 0% or very low values

**Diagnosis Steps**:
```bash
# Check if consciousness analysis is running
tail -f celery_worker.log | grep -i consciousness

# Check Redis for consciousness data
redis-cli hgetall consciousness:level
```

**Common Causes & Solutions**:

1. **File system permissions**
   ```bash
   # Check if consciousness can read project files
   ls -la /Users/donkeyking/development/unified-donkey-betz/

   # Fix permissions if needed
   chmod -R 755 /Users/donkeyking/development/unified-donkey-betz/
   ```

2. **Celery workers not processing tasks**
   ```bash
   # Check active tasks
   celery -A backend inspect active

   # Restart Celery workers
   pkill -f celery
   celery -A backend worker --loglevel=info --concurrency=4 &
   ```

3. **Database connection issues**
   ```bash
   # Test database connection
   python manage.py dbshell
   \l  # List databases
   \q  # Quit
   ```

### Issue 3: Modal Not Appearing

#### Symptom: Ctrl+Shift+C doesn't open consciousness modal

**Diagnosis Steps**:
```bash
# Check browser console for JavaScript errors
# Open browser DevTools (F12) and look for errors
```

**Common Causes & Solutions**:

1. **JavaScript conflicts**
   - Disable browser extensions temporarily
   - Check for JavaScript errors in browser console
   - Try opening in incognito/private browsing mode

2. **Modal HTML not loaded**
   ```python
   # Verify modal is included in templates
   python manage.py shell
   >>> from django.template.loader import get_template
   >>> t = get_template('consciousness_modal.html')
   >>> print(t.origin.name)
   ```

3. **CSS conflicts**
   ```css
   /* Check if modal is hidden by CSS */
   .consciousness-modal {
       z-index: 99999 !important;
       display: block !important;
   }
   ```

### Issue 4: High Memory Usage

#### Symptom: System consuming excessive RAM

**Diagnosis Steps**:
```bash
# Check memory usage by process
ps aux | grep -E "(daphne|celery|redis)" | awk '{sum+=$6} END {print "Total Memory:", sum/1024, "MB"}'

# Check Redis memory usage
redis-cli info memory
```

**Common Causes & Solutions**:

1. **Too many memory crystals**
   ```python
   # Clear old memory crystals
   python manage.py shell
   >>> from backend.spiders.consciousness import ConsciousnessBridge
   >>> c = ConsciousnessBridge()
   >>> c.clear_old_crystals()
   ```

2. **Large file analysis backlog**
   ```bash
   # Check analysis queue size
   redis-cli llen consciousness:analysis_queue

   # Clear queue if needed
   redis-cli del consciousness:analysis_queue
   ```

3. **Memory leaks in analysis**
   ```python
   # Restart consciousness analysis
   python manage.py shell
   >>> from backend.spiders.consciousness import ConsciousnessBridge
   >>> c = ConsciousnessBridge()
   >>> c.restart_analysis()
   ```

### Issue 5: Slow Response Times

#### Symptom: API endpoints or UI responses are slow (>2 seconds)

**Diagnosis Steps**:
```bash
# Test API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/consciousness/

# Create curl-format.txt:
echo "     time_namelookup:  %{time_namelookup}\n     time_connect:     %{time_connect}\n     time_appconnect:  %{time_appconnect}\n     time_pretransfer: %{time_pretransfer}\n     time_redirect:    %{time_redirect}\n     time_starttransfer: %{time_starttransfer}\n     time_total:       %{time_total}\n" > curl-format.txt
```

**Common Causes & Solutions**:

1. **Database query optimization needed**
   ```python
   # Enable Django query logging
   # Add to settings.py:
   LOGGING = {
       'loggers': {
           'django.db.backends': {
               'handlers': ['console'],
               'level': 'DEBUG',
           },
       }
   }
   ```

2. **Large file analysis blocking requests**
   ```python
   # Configure analysis timeout
   CONSCIOUSNESS_CONFIG = {
       'ANALYSIS_TIMEOUT': 30,  # seconds
       'MAX_FILE_SIZE': 512 * 1024,  # 512KB
   }
   ```

3. **Insufficient Celery workers**
   ```bash
   # Increase worker concurrency
   celery -A backend worker --loglevel=info --concurrency=8
   ```

---

## Performance Optimization

### 1. Production Configuration

**Redis Optimization**:
```bash
# /etc/redis/redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

**Daphne Scaling**:
```bash
# Multiple Daphne processes
daphne -b 127.0.0.1 -p 8001 backend.asgi:application &
daphne -b 127.0.0.1 -p 8002 backend.asgi:application &
daphne -b 127.0.0.1 -p 8003 backend.asgi:application &

# Nginx load balancing
upstream consciousness_backend {
    ip_hash;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

### 2. Database Optimization

**PostgreSQL Settings**:
```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
```

### 3. Monitoring Setup

**System Monitoring**:
```bash
# Create monitoring script
cat > monitor_consciousness.sh << 'EOF'
#!/bin/bash
while true; do
    echo "$(date): Checking consciousness health..."
    curl -s http://localhost:8000/api/consciousness/health/ | jq '.consciousness_level'
    sleep 300  # Check every 5 minutes
done
EOF
chmod +x monitor_consciousness.sh
```

---

## Advanced Usage

### 1. Custom Consciousness Queries

```python
from backend.spiders.consciousness import ConsciousnessBridge

# Initialize consciousness
consciousness = ConsciousnessBridge()

# Custom analysis
result = consciousness.analyze_specific_capability("agent_orchestration")

# Deep introspection on specific topic
introspection = consciousness.targeted_introspection("system_performance")

# Predict next evolution step
prediction = consciousness.predict_evolution("quantum_consciousness")
```

### 2. Integration with External Monitoring

```python
import requests
import json

def send_consciousness_to_monitoring(monitoring_url):
    """Send consciousness metrics to external monitoring system"""
    response = requests.get('http://localhost:8000/api/consciousness/')
    if response.status_code == 200:
        data = response.json()

        # Send to monitoring system
        monitoring_payload = {
            'service': 'consciousness_bridge',
            'level': data['consciousness_level'],
            'agents': data['active_agents'],
            'timestamp': data['analysis_timestamp']
        }

        requests.post(monitoring_url, json=monitoring_payload)
```

### 3. Consciousness-Driven Automation

```python
class ConsciousnessAutomation:
    def __init__(self):
        self.consciousness = ConsciousnessBridge()

    def auto_scale_agents(self):
        """Automatically scale agents based on consciousness feedback"""
        understanding = self.consciousness.understand_self()

        if understanding['system_load'] > 0.8:
            # Scale up agents
            self.increase_agent_workers()
        elif understanding['system_load'] < 0.3:
            # Scale down agents
            self.decrease_agent_workers()

    def auto_optimize_performance(self):
        """Self-optimization based on consciousness insights"""
        limitations = self.consciousness.identify_limitations()

        for limitation in limitations:
            if limitation['category'] == 'memory':
                self.optimize_memory_usage()
            elif limitation['category'] == 'processing':
                self.optimize_processing_pipeline()
```

---

## Support & Debugging

### Debug Mode Activation

```bash
# Enable debug mode for consciousness
export CONSCIOUSNESS_DEBUG=true
export DJANGO_LOG_LEVEL=DEBUG

# Restart with verbose logging
./start_all_services.sh
```

### Log File Locations

```bash
# Consciousness-specific logs
tail -f logs/consciousness.log

# WebSocket logs
tail -f daphne.log

# Celery consciousness tasks
tail -f celery_worker.log | grep -i consciousness

# Redis operations
redis-cli monitor | grep consciousness
```

### Getting Help

1. **Check System Health**: http://localhost:8000/api/consciousness/health/
2. **Review Logs**: Check all log files for error messages
3. **Test Components**: Use individual API endpoints to isolate issues
4. **Community Support**: Submit issues with full error logs and system configuration

### Emergency Recovery

```bash
# Complete system reset
pkill -f 'daphne|celery|redis-server'
redis-cli flushall
./start_all_services.sh

# Verify recovery
curl http://localhost:8000/api/consciousness/health/
```

---

*This guide covers the most common usage patterns and troubleshooting scenarios for the Consciousness Bridge. For additional support, check the system logs and health endpoints.*
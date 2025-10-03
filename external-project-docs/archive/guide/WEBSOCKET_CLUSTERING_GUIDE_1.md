# WebSocket Clustering Implementation Guide

## Overview

This guide covers the complete WebSocket clustering implementation for horizontal scaling of real-time communication in the Donkey Betz platform.

## 🏗️ Architecture

### Components
- **Redis Channel Layer**: Centralized message routing across server instances
- **Nginx Load Balancer**: WebSocket-aware load balancing with sticky sessions
- **Django Channels**: ASGI WebSocket consumers with clustering support
- **Connection Manager**: Redis-based connection state tracking
- **Health Monitoring**: Connection monitoring and cleanup services

### Key Features
- ✅ Horizontal scaling support
- ✅ Connection state management across instances
- ✅ Automatic failover and load balancing
- ✅ Connection health monitoring and cleanup
- ✅ Graceful reconnection handling
- ✅ Real-time connection statistics

## 🚀 Deployment Options

### Option 1: Single Instance (Current Default)
```bash
# Standard deployment - single backend instance
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Scaled Deployment (2 instances)
```bash
# Enable scaling profile for 2 backend instances
docker-compose -f docker-compose.prod.yml --profile scaling up -d
```

### Option 3: High Load (3 instances)
```bash
# Enable high-load profile for 3 backend instances
docker-compose -f docker-compose.prod.yml --profile high-load up -d
```

## ⚙️ Configuration

### Environment Variables

Add to `backend/.env.production`:

```env
# WebSocket Clustering Configuration
REDIS_WS_HOST=redis
REDIS_WS_PORT=6379
REDIS_WS_DB=6
SERVER_INSTANCE_ID=backend-1

# Channel Layer Settings
CHANNELS_REDIS_PREFIX=donkeybetz:channels
CHANNELS_CAPACITY=1500
CHANNELS_EXPIRY=10
CHANNELS_GROUP_EXPIRY=86400

# Connection Management
WS_MAX_CONNECTIONS_PER_USER=10
WS_CONNECTION_TIMEOUT=300
WS_HEARTBEAT_INTERVAL=30
WS_ENABLE_CONNECTION_TRACKING=true
WS_CONNECTION_TTL=3600

# Redis Sentinel (optional for HA)
REDIS_SENTINELS=sentinel1:26379,sentinel2:26379
REDIS_SENTINEL_SERVICE=mymaster
```

### Nginx Configuration

The provided `nginx/nginx.conf` includes:
- **Upstream clusters** for load balancing
- **WebSocket-specific routing** with sticky sessions
- **Health checks** and failover configuration
- **Connection upgrade handling**

### Redis Configuration

Dedicated Redis database (DB 6) for WebSocket channels:
- **Channel layer**: Message routing between instances
- **Connection state**: Active connection tracking
- **Health monitoring**: Connection cleanup and stats

## 🔧 Management Commands

### Start Heartbeat Monitor
```bash
# Start WebSocket heartbeat monitoring service
python manage.py start_websocket_heartbeat --interval 30
```

### Cleanup Stale Connections
```bash
# Manual cleanup (also done automatically)
curl -X POST http://localhost:8000/api/ai-partner/websocket/cleanup/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"max_age": 300}'
```

## 📊 Monitoring Endpoints

### User Connection Stats
```bash
GET /api/ai-partner/websocket/stats/
```
Returns current user's WebSocket connections and status.

### Global Statistics (Admin)
```bash
GET /api/ai-partner/websocket/stats/global/
```
Returns cluster-wide connection statistics and configuration.

### Health Check (Admin)
```bash
GET /api/ai-partner/websocket/health/
```
Returns Redis connectivity and system health status.

### Trigger Heartbeat
```bash
POST /api/ai-partner/websocket/heartbeat/
```
Manually trigger heartbeat for user's connections.

## 🧪 Testing

### Run Test Suite
```bash
cd backend
python test_websocket_clustering.py
```

The test suite verifies:
- Single WebSocket connections
- Multiple simultaneous connections
- Connection management APIs
- Load balancing functionality
- Heartbeat mechanisms

### Manual Testing

1. **Connect multiple WebSocket clients**:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/chat/test/');
   ws.onopen = () => console.log('Connected');
   ws.send(JSON.stringify({type: 'heartbeat'}));
   ```

2. **Check connection stats**:
   ```bash
   curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8000/api/ai-partner/websocket/stats/
   ```

3. **Monitor Nginx logs**:
   ```bash
   docker-compose logs -f nginx
   ```

## 🔍 Troubleshooting

### Common Issues

#### 1. WebSocket Connection Failed
```
❌ WebSocket connection failed: Connection refused
```

**Solution**: Check if backend services are running and Nginx is properly configured.

```bash
# Check service status
docker-compose ps

# Check backend logs
docker-compose logs backend

# Test direct backend connection
curl http://localhost:8000/api/health/
```

#### 2. Redis Connection Issues
```
❌ Redis connection: unhealthy
```

**Solution**: Verify Redis service and network connectivity.

```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Verify Redis DB 6 access
docker-compose exec redis redis-cli -n 6 info
```

#### 3. Load Balancing Not Working
```
⚠️ Only one instance detected
```

**Solution**: Ensure multiple backend instances are running.

```bash
# Start with scaling profile
docker-compose -f docker-compose.prod.yml --profile scaling up -d

# Check instance count
docker-compose ps | grep backend

# Update Nginx upstream (uncomment additional servers)
# Edit nginx/nginx.conf and restart nginx
```

#### 4. Stale Connections
```
❌ Connection timeout or stale connections
```

**Solution**: Run cleanup and check heartbeat service.

```bash
# Manual cleanup
curl -X POST http://localhost:8000/api/ai-partner/websocket/cleanup/ \
  -H "Authorization: Bearer TOKEN"

# Start heartbeat monitor
python manage.py start_websocket_heartbeat
```

### Debug Mode

Enable debug logging in `settings.py`:

```python
LOGGING = {
    'loggers': {
        'ai_partner.websocket_manager': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'channels': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## 📈 Performance Tuning

### Optimal Settings

For high-load scenarios:

```env
# Increase connection limits
WS_MAX_CONNECTIONS_PER_USER=20
CHANNELS_CAPACITY=3000

# Faster heartbeat for high availability
WS_HEARTBEAT_INTERVAL=15

# Shorter TTL for rapid cleanup
WS_CONNECTION_TTL=1800
```

### Nginx Tuning

```nginx
# Increase worker connections
events {
    worker_connections 2048;
}

# Optimize upstream settings
upstream websocket_cluster {
    least_conn;  # Use least connections instead of hash
    server backend:8000 max_fails=1 fail_timeout=5s;
    server backend-2:8000 max_fails=1 fail_timeout=5s;
    server backend-3:8000 max_fails=1 fail_timeout=5s;
    keepalive 64;
}
```

### Redis Optimization

```redis
# In docker-compose.prod.yml redis service
command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru --tcp-keepalive 60
```

## 🔐 Security Considerations

### Authentication
- All WebSocket connections require valid JWT tokens
- Connection state includes user isolation
- Admin endpoints require admin permissions

### Rate Limiting
- Nginx-level rate limiting for WebSocket connections
- Per-user connection limits enforced by connection manager
- Heartbeat rate limiting to prevent abuse

### Data Privacy
- Connection state data has configurable TTL
- Automatic cleanup of stale connection data
- No sensitive data stored in Redis connection state

## 🚀 Production Deployment

### Prerequisites
1. **Redis High Availability**: Consider Redis Sentinel or Cluster
2. **SSL/TLS**: Ensure WebSocket connections use WSS in production
3. **Monitoring**: Set up connection metrics and alerting
4. **Backup**: Regular Redis backups for connection state recovery

### Step-by-Step Deployment

1. **Update Environment Variables**:
   ```bash
   cp backend/.env.example backend/.env.production
   # Edit with production values
   ```

2. **Configure SSL Certificates**:
   ```bash
   # Ensure certificates exist in nginx/certs/
   # Update nginx.conf with correct certificate paths
   ```

3. **Deploy with Scaling**:
   ```bash
   docker-compose -f docker-compose.prod.yml --profile scaling up -d
   ```

4. **Verify Clustering**:
   ```bash
   python backend/test_websocket_clustering.py
   ```

5. **Start Monitoring**:
   ```bash
   docker-compose exec backend python manage.py start_websocket_heartbeat &
   ```

## 📚 Additional Resources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Redis Clustering Guide](https://redis.io/docs/manual/scaling/)
- [Nginx WebSocket Proxying](https://nginx.org/en/docs/http/websocket.html)
- [Docker Compose Scaling](https://docs.docker.com/compose/compose-file/deploy/)

---

**Note**: This clustering implementation provides robust horizontal scaling for WebSocket connections while maintaining compatibility with single-instance deployments.
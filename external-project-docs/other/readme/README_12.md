# Donkey Betz Load Testing Suite

This directory contains comprehensive load testing tools for the Donkey Betz platform using [Locust](https://locust.io/), a modern Python-based load testing framework.

## 🎯 Overview

The load testing suite validates the performance and scalability of key platform components:

- **Authentication System** - User login/logout flows
- **Stock Intelligence** - Real-time market data endpoints
- **Agent Orchestra** - AI agent orchestration and management
- **Content Creation** - Image/video generation services
- **Research Intelligence** - Search and research workflows
- **Memory System** - RAG and memory retrieval
- **Dashboard & Health** - System monitoring endpoints

## 📁 File Structure

```
load_tests/
├── README.md           # This documentation
├── locustfile.py       # Main Locust test scenarios
├── config.py           # Configuration and test data
├── run_tests.sh        # Test execution script
└── results/           # Test results and reports (created during testing)
```

## 🚀 Quick Start

### Prerequisites

1. **Backend Running**: Ensure the Django backend is running on port 8000
2. **Test User**: Create a test user account for authentication
3. **Dependencies**: Locust is already installed via `pip install locust`

### Basic Usage

```bash
# Navigate to backend directory
cd backend

# Run a smoke test (5 users, 2 minutes)
./load_tests/run_tests.sh smoke

# Run moderate load test (100 users, 10 minutes)
./load_tests/run_tests.sh moderate

# Run interactive test with web UI
./load_tests/run_tests.sh interactive
```

## 📊 Test Scenarios

### 1. Smoke Test 🔥
- **Users**: 5
- **Duration**: 2 minutes
- **Purpose**: Basic functionality verification
- **Usage**: `./load_tests/run_tests.sh smoke`

### 2. Light Load Test 🌤️
- **Users**: 25
- **Duration**: 5 minutes
- **Purpose**: Light load performance check
- **Usage**: `./load_tests/run_tests.sh light`

### 3. Moderate Load Test ⛅
- **Users**: 100
- **Duration**: 10 minutes
- **Purpose**: Normal usage simulation
- **Usage**: `./load_tests/run_tests.sh moderate`

### 4. Heavy Load Test 🌧️
- **Users**: 500
- **Duration**: 15 minutes
- **Purpose**: High load capacity testing
- **Usage**: `./load_tests/run_tests.sh heavy`

### 5. Stress Test ⛈️
- **Users**: 1000
- **Duration**: 20 minutes
- **Purpose**: Find system breaking points
- **Usage**: `./load_tests/run_tests.sh stress`

### 6. Spike Test ⚡
- **Users**: 2000
- **Duration**: 5 minutes
- **Purpose**: Sudden load increase handling
- **Usage**: `./load_tests/run_tests.sh spike`

### 7. Endurance Test 🏃‍♂️
- **Users**: 200
- **Duration**: 60 minutes
- **Purpose**: Long-running stability test
- **Usage**: `./load_tests/run_tests.sh endurance`

## 🎭 User Simulation Types

### DonkeyBetzUser (Main User)
- **Weight**: 4 (most common)
- **Behavior**: Realistic business user patterns
- **Wait Time**: 1-3 seconds between requests
- **Tasks**: Mixed workload across all features

### HighVolumeUser (Stress Testing)
- **Weight**: 1 (fewer instances)
- **Behavior**: Rapid-fire requests
- **Wait Time**: 0.1-0.5 seconds between requests
- **Tasks**: High-frequency health checks and market data

### BusinessUserSimulation (Workflow Testing)
- **Weight**: 3 (common)
- **Behavior**: Complete business workflows
- **Wait Time**: 2-5 seconds between requests
- **Tasks**: End-to-end business processes

## 📈 Monitored Endpoints

### Critical Endpoints (High Priority)
- `/api/core/health/simple/` - System health check
- `/api/auth/login/` - User authentication
- `/api/core/dashboard/stats/` - Dashboard statistics
- `/api/agent-orchestra/system-health/` - System health monitoring
- `/api/agent-orchestra/command-center/stats/` - Command center stats

### High Priority Endpoints
- `/api/agent-orchestra/stocks/market-overview/` - Market overview
- `/api/agent-orchestra/stocks/market-indices/` - Market indices
- `/api/agent-orchestra/stocks/quote/{ticker}/` - Real-time quotes
- `/api/agent-orchestra/stocks/batch-quotes/` - Batch quotes
- `/api/agent-orchestra/templates/` - Agent templates
- `/api/agent-orchestra/agents/available/` - Available agents

### Medium Priority Endpoints
- `/api/agent-orchestra/research/search/` - Research search
- `/api/agent-orchestra/reddit-ideas/` - Reddit ideas
- `/api/agent-orchestra/business-hub/statistics/` - Business hub stats
- `/api/content/images/visual-styles/` - Image generation styles
- `/api/content/generated-images/` - Generated images
- `/api/memory/` - Memory system

## 📊 Performance Thresholds

| Level | Response Time | Description |
|-------|---------------|-------------|
| **Excellent** | <200ms | Optimal performance |
| **Good** | <500ms | Good user experience |
| **Acceptable** | <1000ms | Acceptable for most users |
| **Poor** | <2000ms | Degraded experience |
| **Critical** | >5000ms | Unacceptable performance |

## 🔧 Configuration

### Test Environment Setup

1. **Update Test Credentials** in `config.py`:
```python
TEST_CREDENTIALS = {
    "username": "your_test_user",
    "password": "your_test_password",
    "email": "test@yourdomain.com"
}
```

2. **Set Target Host** (optional):
```bash
./load_tests/run_tests.sh moderate --host http://staging.yourdomain.com
```

### Environment Variables

```bash
# Optional: Set test credentials via environment variables
export LOAD_TEST_USERNAME="testuser"
export LOAD_TEST_PASSWORD="REDACTED"
export LOAD_TEST_EMAIL="test@example.com"
```

## 📋 Running Tests

### Command Line Interface

```bash
# Check if backend is running
./load_tests/run_tests.sh check

# Run specific scenario
./load_tests/run_tests.sh [scenario]

# Run all scenarios sequentially
./load_tests/run_tests.sh all

# Run interactive test (web UI at localhost:8089)
./load_tests/run_tests.sh interactive

# Generate summary report
./load_tests/run_tests.sh report

# Show help
./load_tests/run_tests.sh help
```

### Available Scenarios
- `smoke` - Basic functionality test
- `light` - Light load test
- `moderate` - Moderate load test
- `heavy` - Heavy load test
- `stress` - Stress test
- `spike` - Spike test
- `endurance` - Endurance test

### Interactive Mode

For fine-grained control, use interactive mode:

```bash
./load_tests/run_tests.sh interactive
```

Then open http://localhost:8089 in your browser to:
- Start/stop tests dynamically
- Adjust user count and spawn rate
- View real-time statistics
- Download detailed reports

## 📊 Results and Reports

### HTML Reports
- Generated automatically for each test
- Saved in `results/` directory
- Include detailed metrics and charts
- Timestamped for easy identification

### Key Metrics
- **Response Times**: 50th, 95th, 99th percentiles
- **Throughput**: Requests per second
- **Error Rate**: Failed requests percentage
- **Users**: Concurrent user simulation
- **Request Distribution**: Endpoint usage patterns

### Example Report Files
```
results/
├── load_test_smoke_20250710_143022.html
├── load_test_moderate_20250710_144532.html
├── load_test_summary_20250710_150145.md
└── ...
```

## 🔍 Monitoring During Tests

### Key Indicators to Watch

1. **Response Times**
   - 95th percentile should stay below thresholds
   - Watch for sudden spikes or degradation

2. **Error Rates**
   - Should remain below 1% for normal operations
   - Monitor 4xx and 5xx error patterns

3. **System Resources**
   - CPU usage on backend server
   - Memory consumption
   - Database connection pool utilization

4. **External APIs**
   - Polygon.io rate limits
   - OpenAI API quotas
   - Reddit API limitations

### Database Monitoring
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Check long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

### Redis Monitoring
```bash
# Check Redis connection info
redis-cli info clients

# Monitor Redis commands
redis-cli monitor
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend Not Running**
   ```bash
   # Error: Connection refused
   # Solution: Start the backend server
   cd backend && make run-backend
   ```

2. **Authentication Failures**
   ```bash
   # Error: 401 Unauthorized
   # Solution: Create test user or update credentials in config.py
   ```

3. **Rate Limiting**
   ```bash
   # Error: 429 Too Many Requests
   # Solution: Reduce test load or increase rate limits
   ```

4. **Database Connection Issues**
   ```bash
   # Error: Connection pool exhausted
   # Solution: Increase max_connections in PostgreSQL
   ```

5. **Memory Issues**
   ```bash
   # Error: Out of memory
   # Solution: Reduce concurrent users or increase system memory
   ```

### Performance Optimization Tips

1. **Database Optimization**
   - Add indexes for frequently queried fields
   - Optimize slow queries identified during testing
   - Configure connection pooling appropriately

2. **Caching Strategy**
   - Implement Redis caching for frequently accessed data
   - Use Django cache framework for expensive computations
   - Cache API responses with appropriate TTL

3. **API Rate Limiting**
   - Implement intelligent rate limiting
   - Use circuit breakers for external API calls
   - Batch API requests where possible

4. **WebSocket Optimization**
   - Limit WebSocket connections per user
   - Implement connection pooling for WebSocket servers
   - Use message queuing for high-volume real-time updates

## 📚 Best Practices

### Test Design
1. **Realistic User Behavior** - Simulate actual user workflows
2. **Gradual Load Increase** - Ramp up users gradually
3. **Mixed Workloads** - Test different endpoint combinations
4. **Data Variation** - Use diverse test data sets

### Performance Analysis
1. **Establish Baselines** - Record initial performance metrics
2. **Trend Analysis** - Monitor performance over time
3. **Bottleneck Identification** - Profile slow endpoints
4. **Capacity Planning** - Determine scaling requirements

### Continuous Testing
1. **Automated Testing** - Include load tests in CI/CD pipeline
2. **Regular Monitoring** - Schedule periodic performance tests
3. **Alert Thresholds** - Set up performance alerts
4. **Regression Testing** - Test after significant changes

## 🎯 Next Steps

After running load tests, consider:

1. **Performance Optimization** - Address identified bottlenecks
2. **Scaling Strategy** - Plan for horizontal/vertical scaling
3. **Monitoring Setup** - Implement production monitoring
4. **Alert Configuration** - Set up performance alerts
5. **Documentation** - Document findings and recommendations

## 📞 Support

For questions or issues with load testing:

1. Check the troubleshooting section above
2. Review Locust documentation: https://docs.locust.io/
3. Analyze the generated HTML reports for detailed metrics
4. Monitor system logs during test execution

---

**Happy Load Testing!** 🚀
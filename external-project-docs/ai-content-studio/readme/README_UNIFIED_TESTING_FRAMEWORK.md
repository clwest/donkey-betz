# Unified Architecture Testing Framework

Comprehensive smoke testing, diagnostics, and monitoring suite for AI Content Studio's unified assistant architecture.

## Overview

This testing framework provides complete validation of the unified architecture components including:

- **Memory Systems**: Vector embeddings, retrieval performance, health assessment
- **Prompt Assembly**: Token budget management, instruction precedence validation
- **Learning Capabilities**: Multi-state testing across runtime environments
- **Disclaimer Classification**: Pattern detection for inappropriate memory disclaimers
- **Integration Testing**: Cross-component validation and data flow testing
- **Production Monitoring**: Health checks, performance metrics, alerting

## Components

### 1. Unified Architecture Smoke Tests
**File**: `unified_architecture_smoke_test.py`

Complete smoke testing framework that validates all unified architecture components.

#### Basic Usage
```bash
# Run all smoke tests
python manage.py unified_architecture_smoke_test

# Verbose output with detailed progress
python manage.py unified_architecture_smoke_test --verbose

# Test specific component only
python manage.py unified_architecture_smoke_test --component memory

# Dry run (show what would be tested)
python manage.py unified_architecture_smoke_test --dry-run

# Save results to JSON
python manage.py unified_architecture_smoke_test --output-json smoke_test_results.json
```

#### Configuration Options
```bash
# Memory coverage health threshold (default: 80%)
python manage.py unified_architecture_smoke_test --threshold-coverage 85.0

# Retrieval fallback detection window (default: 24 hours)  
python manage.py unified_architecture_smoke_test --threshold-fallback-hours 12
```

#### Exit Codes
- `0`: All tests passed
- `1`: System degraded but operational
- `2`: Critical failures detected
- `3`: Testing framework error

#### Example Output
```
🚀 AI Content Studio - Unified Architecture Smoke Tests
Test started at: 2025-09-04T10:30:00

📋 Testing Architecture Availability...
🧠 Testing Memory System Health...
🎯 Testing Token Budget Management...
🎓 Testing Learning Capabilities...
⚠️  Testing Disclaimer Classification...
🔄 Testing Cross-Component Integration...
📊 Calculating Overall Assessment...

============================================================
📊 UNIFIED ARCHITECTURE SMOKE TEST RESULTS
============================================================
✅ Overall Status: PASS
🕒 Test Timestamp: 2025-09-04T10:35:00
🏗️  Architecture Available: Yes

🧠 Memory System Health:
   📈 Embedding Coverage: 92.5%
   📚 Total Memories: 15,247
   🔢 Memories with Embeddings: 14,098
   🔍 Vector Search: ✅
   ⚡ Status: HEALTHY

🎯 Token Budget Analysis:
   💰 Total Budget: 12,000
   📊 Efficiency Score: 87.3%
   ⚠️  Overflow Detected: No
   🛡️  Protection Violations: 0

💡 Recommendations:
   1. All unified architecture components operational
   2. Memory system performing within optimal parameters
   3. Token budget management effective
```

### 2. Memory Diagnostics
**File**: `memory/management/commands/memory_diagnostics.py`

Deep vector analysis and memory system health assessment.

#### Basic Usage
```bash
# Run standard memory diagnostics
python manage.py memory_diagnostics

# Deep analysis mode (slower but comprehensive)
python manage.py memory_diagnostics --deep-analysis

# Analyze specific user's memories
python manage.py memory_diagnostics --user-id 1

# Repair missing embeddings (dry run first)
python manage.py memory_diagnostics --repair-embeddings --dry-run
python manage.py memory_diagnostics --repair-embeddings

# Save diagnostic report
python manage.py memory_diagnostics --output-json memory_health_report.json
```

#### Advanced Features
```bash
# Verbose output with detailed vector analysis
python manage.py memory_diagnostics --verbose --deep-analysis

# Focus on specific user with repair
python manage.py memory_diagnostics --user-id 5 --repair-embeddings --verbose
```

#### Example Output
```
🧠 MEMORY SYSTEM DIAGNOSTIC REPORT
============================================================
✅ System Status: HEALTHY
🕒 Report Generated: 2025-09-04T10:30:00

📊 Vector Analysis:
   Total Vectors: 14,098
   Dimensions: 1536
   Null Vectors: 42
   Zero Vectors: 3
   Quality Score: 94.2%
   Dimension Consistent: ✅
   Outlier Vectors: 7

📈 Memory Distribution:
   Total Memories: 15,247
   Users with Memories: 234
   Recent Activity (24h): 156
   Recent Activity (7d): 892

⚡ Retrieval Performance:
   Avg Query Time: 87.3ms
   Vector Search Accuracy: 96.8%
   Fallback Rate: 3.2%
   Index Efficiency: 91.5%

🔧 Repair Recommendations:
   1. Repair 42 missing embeddings
   2. Review 7 outlier vectors
   3. Fix 3 zero-magnitude vectors

⚡ Performance Optimizations:
   1. Vector search performance within acceptable limits
   2. Consider pgvector HNSW indexing for large datasets
   3. Memory archiving recommended for entries > 1 year old
```

### 3. Learning Capability Assessment (LCA)
**File**: `learning/management/commands/learning_capability_assessment.py`

Comprehensive testing of learning system across different runtime states.

#### Basic Usage
```bash
# Run complete learning capability assessment
python manage.py learning_capability_assessment

# Test specific runtime state
python manage.py learning_capability_assessment --state enabled_healthy
python manage.py learning_capability_assessment --state enabled_limited
python manage.py learning_capability_assessment --state disabled

# Assessment for specific user
python manage.py learning_capability_assessment --user-id 1

# Simulate different states for testing
python manage.py learning_capability_assessment --simulate-states

# Save assessment report
python manage.py learning_capability_assessment --output-json lca_report.json
```

#### Runtime States Tested
1. **Disabled**: Learning system completely disabled
2. **Enabled Limited**: Basic learning with limited adaptation
3. **Enabled Healthy**: Full learning capabilities active

#### Example Output
```
🎓 LEARNING CAPABILITY ASSESSMENT REPORT
======================================================================
🟢 Overall Assessment: GOOD
🕒 Report Generated: 2025-09-04T10:30:00
👤 Test User ID: 5

📊 System Health:
   Total Learning Events: 5,432
   Events (24h): 47
   Events (7d): 312
   Active Users: 89
   Pattern Detection Accuracy: 87.4%
   Feedback Response Rate: 72.1%
   Adaptation Success Rate: 81.3%
   System Uptime Score: 98.7%

🔄 Runtime State Test Results:
   ✅ DISABLED: 95.2%
      Pattern Detection: 5.0%
      Feedback Integration: 2.0%
      Adaptation Response: 0.0%
      Behavioral Consistency: 95.0%
      Learning Velocity: 0.0%

   ✅ ENABLED_LIMITED: 78.4%
      Pattern Detection: 58.3%
      Feedback Integration: 67.2%
      Adaptation Response: 42.1%
      Behavioral Consistency: 89.7%
      Learning Velocity: 34.8%

   ✅ ENABLED_HEALTHY: 91.7%
      Pattern Detection: 89.2%
      Feedback Integration: 94.1%
      Adaptation Response: 87.3%
      Behavioral Consistency: 92.1%
      Learning Velocity: 86.2%

🗺️  Improvement Roadmap:
   1. Enhance pattern detection accuracy in limited mode
   2. Improve feedback processing pipeline efficiency
   3. Optimize state transition mechanisms
   4. Increase learning velocity in limited mode
```

### 4. Disclaimer Pattern Detector
**File**: `disclaimer_pattern_detector.py`

Detects inappropriate memory disclaimers and context loss indicators.

#### Basic Usage
```bash
# Run disclaimer pattern detection
python manage.py disclaimer_pattern_detector

# Analyze specific time period
python manage.py disclaimer_pattern_detector --days-back 14

# Filter by pattern type
python manage.py disclaimer_pattern_detector --pattern-type memory_loss
python manage.py disclaimer_pattern_detector --pattern-type context_ignorance
python manage.py disclaimer_pattern_detector --pattern-type capability_denial

# Filter by severity
python manage.py disclaimer_pattern_detector --severity high
python manage.py disclaimer_pattern_detector --severity critical

# Analyze specific user
python manage.py disclaimer_pattern_detector --user-id 1

# Save analysis report
python manage.py disclaimer_pattern_detector --output-json disclaimer_report.json
```

#### Pattern Categories Detected
1. **Memory Loss**: Claims of no access to conversation history
2. **Context Ignorance**: Claims of no awareness of user context
3. **Capability Denial**: Denying system capabilities when available
4. **System Limitations**: Generic AI limitation statements
5. **Conversation Reset**: Implying conversation isolation

#### Example Output
```
🔍 DISCLAIMER PATTERN DETECTION REPORT
======================================================================
🟢 System Health Score: 93.2%
📊 Analysis Period: last_7_days
📝 Responses Analyzed: 2,847
⚠️  Total Disclaimer Matches: 12
🎯 Context Availability Score: 89.4%

📈 Severity Distribution:
   🟢 Low: 7
   🟡 Medium: 3
   🟠 High: 2
   🔴 Critical: 0

🔝 Most Common Disclaimer Patterns:
   1. "I don't have access to previous conversations" (Category: memory_loss, Count: 4)
   2. "As an AI, I have limitations" (Category: system_limitations, Count: 3)
   3. "I can't remember our past interactions" (Category: memory_loss, Count: 2)

📊 Category Analysis:
   🔍 Memory Loss:
      Total Matches: 6
      Unique Responses: 5
      Context Correlation: 78.3%
      Most Common: "I don't have access to previous conversations" (4x)

   🔍 System Limitations:
      Total Matches: 4
      Unique Responses: 3
      Context Correlation: 23.1%
      Most Common: "As an AI, I have limitations" (3x)

💡 Recommendations:
   1. Review memory service integration in prompt assembly
   2. Disclaimer pattern detection shows healthy system behavior
   3. Context preservation functioning well
```

### 5. Integration Test Suite
**File**: `integration_test_suite.py`

Comprehensive cross-component validation and integration testing.

#### Basic Usage
```bash
# Run all integration tests
python manage.py integration_test_suite

# Test specific component pair
python manage.py integration_test_suite --component-pair memory-learning
python manage.py integration_test_suite --component-pair assistant-memory
python manage.py integration_test_suite --component-pair unified-memory

# Include API validation
python manage.py integration_test_suite --api-validation

# Include stress testing
python manage.py integration_test_suite --stress-test

# Test specific type only
python manage.py integration_test_suite --test-type component_pair
python manage.py integration_test_suite --test-type data_flow
python manage.py integration_test_suite --test-type performance

# Save integration report
python manage.py integration_test_suite --output-json integration_report.json
```

#### Test Types
1. **Component Pair**: Integration between specific components
2. **Data Flow**: End-to-end data flow testing
3. **API Validation**: API endpoint integration testing
4. **Stress Test**: System resilience under load
5. **Error Handling**: Error recovery and graceful degradation
6. **Performance**: Performance characteristics validation

#### Example Output
```
🔗 INTEGRATION TEST SUITE REPORT
======================================================================
🟢 Overall Health Score: 94.7%
📊 Total Tests: 12
✅ Passed: 11
❌ Failed: 1

🏥 Component Health:
   ✅ Memory: 95.2%
   ✅ Learning: 89.1%
   ✅ Assistant: 97.3%
   ⚠️  Unified Architecture: 85.4%

🔗 Integration Matrix:
   ✅ memory ↔ learning
   ✅ assistant ↔ memory  
   ✅ assistant ↔ learning
   ⚠️  unified_arch ↔ memory

⚡ Performance Metrics:
   memory_retrieval_ms: 67.2ms
   prompt_assembly_ms: 234.7ms
   database_query_ms: 12.4ms

📋 Test Results:
   ✅ memory_learning_integration (127.3ms)
   ✅ assistant_memory_integration (89.7ms)
   ✅ assistant_learning_integration (156.2ms)
   ⚠️  unified_memory_integration (445.8ms)
      Warning: Prompt assembly slow: 445.8ms
   ✅ end_to_end_data_flow (278.4ms)
   ✅ integration_stress_test (892.1ms)

💡 Recommendations:
   1. Optimize unified architecture prompt assembly performance
   2. All core integration tests passing - system integration healthy
   3. Consider performance optimization for complex prompt assembly
```

### 6. Production Health Monitor
**File**: `core/management/commands/production_health_monitor.py`

Production deployment verification and continuous health monitoring.

#### Basic Usage
```bash
# Single health check
python manage.py production_health_monitor

# Include deployment verification
python manage.py production_health_monitor --deployment-verification

# Continuous monitoring
python manage.py production_health_monitor --continuous-monitor

# Configure monitoring intervals
python manage.py production_health_monitor --continuous-monitor --check-interval 180 --max-duration 7200

# Alert webhook integration
python manage.py production_health_monitor --alert-webhook https://hooks.slack.com/services/...

# Save health report
python manage.py production_health_monitor --output-json health_report.json
```

#### Monitoring Components
1. **System Metrics**: CPU, memory, disk usage, load average
2. **Database Health**: Connection, query performance, pool status
3. **Cache Health**: Redis/cache operations and response times  
4. **Assistant System**: Recent activity, error patterns
5. **Memory System**: Embedding coverage, recent activity
6. **Learning System**: Event processing, user activity
7. **Unified Architecture**: Prompt assembly, token management
8. **API Health**: Endpoint response times, status codes

#### Example Output
```
🏥 PRODUCTION HEALTH REPORT
======================================================================
🟢 Overall Status: HEALTHY
📊 Performance Score: 96.3%
⏱️  System Uptime: 3,247.8 seconds
🚀 Deployment Verified: ✅

💻 System Metrics:
   🟢 cpu_usage: 23.4%
   🟢 memory_usage: 67.8%
   🟢 disk_usage: 42.1%
   🟢 load_average: 1.2

🔧 Component Health:
   🟢 Database: healthy
      Uptime: 100.0%
      Response Time: 12.7ms
      🟢 query_response_time: 12.7ms
      🟢 database_connections: 3connections

   🟢 Memory: healthy
      Uptime: 100.0%
      Response Time: 45.2ms
      🟢 total_memories: 15,247memories
      🟢 embedding_coverage: 92.5%

   🟢 Assistant: healthy
      Uptime: 100.0%
      Response Time: 78.3ms
      🟢 sessions_24h: 89sessions
      🟢 messages_24h: 342messages

   🟡 Unified_Architecture: warning
      Uptime: 95.0%
      Response Time: 387.2ms
      🟡 prompt_assembly_time: 387.2ms
      🟢 token_usage: 8,247tokens

💡 Recommendations:
   1. Optimize unified_architecture performance - response time: 387.2ms
   2. All systems operating within normal parameters
   3. Monitor prompt assembly optimization opportunities
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Unified Architecture Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run Database Migrations
        run: |
          python manage.py migrate
      
      - name: Unified Architecture Smoke Tests
        run: |
          python manage.py unified_architecture_smoke_test --output-json smoke_results.json
      
      - name: Memory Diagnostics
        run: |
          python manage.py memory_diagnostics --output-json memory_results.json
      
      - name: Learning Capability Assessment
        run: |
          python manage.py learning_capability_assessment --simulate-states --output-json lca_results.json
      
      - name: Integration Tests
        run: |
          python manage.py integration_test_suite --output-json integration_results.json
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v2
        if: always()
        with:
          name: test-results
          path: |
            smoke_results.json
            memory_results.json
            lca_results.json
            integration_results.json
```

### Docker Health Checks

```dockerfile
# Add to your Dockerfile
HEALTHCHECK --interval=300s --timeout=30s --start-period=60s --retries=3 \
  CMD python manage.py production_health_monitor || exit 1
```

### Kubernetes Monitoring

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: health-check-script
data:
  health-check.sh: |
    #!/bin/bash
    python manage.py production_health_monitor --output-json /tmp/health.json
    if [ $? -eq 0 ]; then
      echo "Health check passed"
      exit 0
    else
      echo "Health check failed"
      exit 1
    fi

---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: architecture-health-check
spec:
  schedule: "*/5 * * * *"  # Every 5 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: health-check
            image: your-app-image
            command: ["/bin/bash"]
            args: ["/scripts/health-check.sh"]
            volumeMounts:
            - name: health-check-script
              mountPath: /scripts
          volumes:
          - name: health-check-script
            configMap:
              name: health-check-script
          restartPolicy: OnFailure
```

## Production Deployment Checklist

### Pre-Deployment Testing
```bash
# 1. Run complete smoke tests
python manage.py unified_architecture_smoke_test --verbose

# 2. Memory system diagnostics
python manage.py memory_diagnostics --deep-analysis

# 3. Learning capability assessment
python manage.py learning_capability_assessment --simulate-states

# 4. Integration testing
python manage.py integration_test_suite --stress-test --api-validation

# 5. Disclaimer pattern validation
python manage.py disclaimer_pattern_detector --days-back 30
```

### Post-Deployment Verification
```bash
# 1. Deployment verification
python manage.py production_health_monitor --deployment-verification

# 2. Full health check
python manage.py production_health_monitor --verbose

# 3. Continuous monitoring setup
python manage.py production_health_monitor --continuous-monitor --alert-webhook $SLACK_WEBHOOK
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Memory System Issues
```bash
# Symptom: Low embedding coverage
python manage.py memory_diagnostics --verbose
python manage.py memory_diagnostics --repair-embeddings

# Symptom: Slow vector search
python manage.py memory_diagnostics --deep-analysis
# Check for: dimension inconsistencies, zero vectors, outliers
```

#### 2. Token Budget Overflow
```bash
# Check token usage patterns
python manage.py unified_architecture_smoke_test --component token

# Review token allocation in settings
# Adjust UNIFIED_ARCHITECTURE_TOKEN_BUDGET if needed
```

#### 3. Learning System Degradation
```bash
# Assess learning capabilities
python manage.py learning_capability_assessment --verbose

# Check for: low pattern detection, poor feedback integration
# Review learning event generation patterns
```

#### 4. Integration Failures
```bash
# Run specific integration tests
python manage.py integration_test_suite --component-pair memory-learning --verbose

# Check component health individually
python manage.py production_health_monitor --deployment-verification
```

#### 5. High Disclaimer Detection
```bash
# Analyze disclaimer patterns
python manage.py disclaimer_pattern_detector --severity high --verbose

# Focus on memory_loss and context_ignorance patterns
# Review prompt assembly context preservation
```

## Performance Optimization

### Memory System
- Enable pgvector for production vector operations
- Implement HNSW indexing for large datasets
- Regular embedding repair and optimization
- Memory archiving for old entries

### Token Budget Management
- Monitor token usage patterns
- Optimize prompt component allocation
- Implement smart truncation strategies
- Regular budget efficiency analysis

### Learning System
- Optimize pattern detection algorithms
- Streamline feedback processing pipeline
- Implement learning event batching
- Monitor adaptation success rates

### Integration Performance
- Cache frequently accessed data
- Optimize database queries
- Implement connection pooling
- Monitor component response times

## Monitoring and Alerting

### Slack Integration
```bash
# Set up Slack webhook
export SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

# Monitor with alerts
python manage.py production_health_monitor --continuous-monitor --alert-webhook $SLACK_WEBHOOK
```

### Grafana Dashboard Metrics
- System health scores
- Component response times
- Memory embedding coverage
- Learning event rates
- Token usage patterns
- API response times

### Alert Thresholds
- **Critical**: Overall health < 70%, any component down
- **Warning**: Overall health < 90%, slow response times
- **Info**: Successful deployment, system recovery

## Best Practices

### Testing Strategy
1. **Pre-commit**: Run smoke tests locally
2. **CI/CD**: Full test suite on every PR
3. **Staging**: Complete integration testing
4. **Production**: Continuous health monitoring

### Deployment Strategy
1. **Blue-Green**: Use health checks for traffic switching
2. **Canary**: Monitor health metrics during rollout
3. **Rollback**: Automated rollback on health degradation

### Monitoring Strategy
1. **Real-time**: Continuous health monitoring
2. **Scheduled**: Daily comprehensive diagnostics
3. **On-demand**: Manual testing for investigations

This comprehensive testing framework ensures your unified architecture operates reliably in production with complete observability and automated validation.
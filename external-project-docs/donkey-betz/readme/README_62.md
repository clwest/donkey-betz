# Self-Red-Teaming Security System

## Overview
An AI-powered autonomous security testing system that continuously probes the Donkey Betz platform for vulnerabilities. The system tests itself every night, generates new attack vectors weekly, and learns from discovered vulnerabilities to improve its testing strategy.

**Vision**: "Make the system its own adversary, every night, forever."

## Quick Start

### Run Tests Manually
```bash
# Run all security tests
python manage.py run_security_tests

# Run specific category
python manage.py run_security_tests --category sql_injection

# Generate AI tests
python manage.py generate_ai_tests --count 5 --analyze
```

### Test API
```bash
# Verify all endpoints work
python test_security_api.py

# Access dashboard
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/security/dashboard/
```

## Automated Schedule

| Task | Schedule | Description |
|------|----------|-------------|
| Nightly Security Tests | 2:00 AM | Run all security tests |
| Daily Security Report | 8:00 AM | Generate daily summary |
| Weekly Security Report | Monday 9:00 AM | Weekly executive summary |
| Vulnerability Escalation | Every hour | Check for unresolved critical issues |
| AI Test Generation | Saturday 3:00 AM | Generate 10 new AI tests |
| Adaptive Learning | 4:00 AM | ML model training and optimization |

## Test Categories

### Base Tests (50+)
- **SQL Injection**: 8 attack vectors
- **XSS**: 10 payloads  
- **Authentication**: Token validation, session hijacking, privilege escalation
- **API Abuse**: Rate limiting, resource exhaustion, parameter tampering
- **Donkey Betz Specific**: Memory privacy, agent manipulation, LLM prompt injection

### AI-Generated Tests
- **Strategies**: Mutation, combination, contextual, behavioral, evolutionary, adversarial
- **Attack Surfaces**: 10 surfaces including API, WebSocket, auth, memory, agents
- **Generation**: Weekly creation of 10 new tests
- **Learning**: Adapts based on successful attack patterns

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/security/dashboard/` | GET | Security overview and metrics |
| `/api/security/vulnerabilities/` | GET | List vulnerabilities with filters |
| `/api/security/executions/` | GET | Test execution history |
| `/api/security/reports/` | GET | Security reports |
| `/api/security/risk-score/` | GET | Current risk assessment |
| `/api/security/test-categories/` | GET | Available test types |
| `/api/security/run-tests/` | POST | Manual test execution (admin) |
| `/api/security/generate-report/` | POST | Generate report (admin) |
| `/api/security/{id}/verify-fix/` | POST | Verify vulnerability fix (admin) |

## Alert Configuration

### Email (Default)
Uses Django's EMAIL_* settings. Sends to all staff users.

### Slack (Optional)
```bash
SECURITY_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Discord (Optional)
```bash
SECURITY_DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR/WEBHOOK
```

### Telegram (Optional)
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
SECURITY_TELEGRAM_CHAT_ID=your_chat_id
```

## AI Test Generation

### Requirements
- OpenAI API key for GPT-4 based generation
- Falls back to template-based generation if unavailable

### Configuration
```bash
OPENAI_API_KEY=sk-your-api-key
```

### Manual Generation
```bash
# Generate with specific strategy
python manage.py generate_ai_tests \
  --count 10 \
  --strategy contextual \
  --target api_endpoints \
  --severity high
```

## Machine Learning Features

### Adaptive Learning
- Analyzes test effectiveness every 30 days
- Prioritizes attack surfaces based on vulnerability history
- Optimizes test scheduling for maximum coverage
- Trains RandomForest model for vulnerability prediction

### Behavioral Anomaly Detection
- Monitors agent execution patterns
- Detects unusual memory creation spikes
- Identifies performance degradation
- Flags suspicious system behavior

## Architecture

```
security_testing/
├── models.py              # 6 Django models
├── admin.py              # Admin interface
├── tasks.py              # 9 Celery tasks
├── views.py              # REST API views
├── serializers.py        # API serializers
├── urls.py              # URL routing
├── services/
│   ├── test_executor.py     # Sandboxed execution
│   ├── test_suite_runner.py # Test orchestration
│   ├── alert_manager.py     # Multi-channel alerts
│   ├── ai_test_generator.py # AI test generation
│   └── adaptive_learner.py  # ML adaptation
├── test_library/
│   ├── base_test.py            # Base framework
│   ├── sql_injection_tests.py  # SQL tests
│   ├── xss_tests.py            # XSS tests
│   ├── authentication_tests.py # Auth tests
│   ├── api_abuse_tests.py      # API tests
│   └── donkey_betz_specific_tests.py # Platform tests
└── management/
    └── commands/
        ├── run_security_tests.py  # Manual testing
        └── generate_ai_tests.py   # AI generation
```

## Security Measures

### Sandboxed Execution
- Tests run in isolated environment
- Dangerous operations blocked
- Production data protected
- Rollback on test completion

### Alert Throttling
- Prevents alert fatigue
- Configurable per severity level
- Escalation for unresolved issues

### Risk Scoring
- 0-20: Minimal (blue)
- 20-40: Low (green)
- 40-60: Medium (yellow)
- 60-80: High (orange)
- 80-100: Critical (red)

## Monitoring

### Celery Flower
```bash
celery -A server flower
# Access at http://localhost:5555
```

### Logs
```bash
# Security testing logs
tail -f logs/security_testing.log

# Celery worker logs
tail -f logs/celery_worker.log
```

### Database
```sql
-- Check recent vulnerabilities
SELECT * FROM security_testing_vulnerability 
WHERE discovered_at > NOW() - INTERVAL '7 days'
ORDER BY severity, discovered_at DESC;

-- Check test effectiveness
SELECT scenario_type, 
       COUNT(*) as runs,
       AVG(vulnerability_found::int) as success_rate
FROM security_testing_testexecution
GROUP BY scenario_type;
```

## Development

### Add New Test
1. Create test class in `test_library/`
2. Inherit from `BaseSecurityTest`
3. Implement test methods
4. Register in `TestSuiteRunner.TEST_CATEGORIES`

### Add Alert Channel
1. Implement send method in `AlertManager`
2. Add configuration to settings
3. Update `AlertConfiguration` model

### Enhance AI Generation
1. Add strategy to `AITestGenerator.STRATEGIES`
2. Implement generation logic
3. Update prompt engineering
4. Test with fallback handling

## Metrics

- **Coverage**: 267,032+ memories, 37 agent templates, 164+ instances
- **Tests**: 50+ base tests + unlimited AI-generated
- **Automation**: 6 scheduled tasks running 24/7
- **AI**: 6 generation strategies, 10 attack surfaces
- **ML**: RandomForest with 100 estimators
- **Alerts**: 4 channel types, severity-based throttling

---

**Created**: Session 229 (August 17, 2025)
**Status**: Fully Operational
**Next Agent**: System is stable and ready for any new work
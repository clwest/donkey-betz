# UKF Alerting Configuration Guide

## Overview

The UKF system includes comprehensive alerting capabilities to notify operators of system issues, performance degradation, and maintenance needs. This guide covers configuration, customization, and integration options.

## Alert Types

### Health Alerts
- **System Unhealthy**: Critical issues affecting system operation
- **System Degraded**: Performance or partial functionality issues
- **Component Failures**: Specific subsystem problems

### Performance Alerts
- **Slow Search**: Average response time exceeds thresholds
- **High Error Rate**: Search failures exceed acceptable levels
- **Resource Exhaustion**: Database, cache, or system resources

### Embedding Alerts
- **Low Coverage**: Embedding coverage drops below thresholds
- **Generation Failures**: High failure rate in embedding creation
- **Backlog Growth**: Unprocessed entries accumulating

### Maintenance Alerts
- **Task Failures**: Scheduled maintenance jobs failing
- **Data Growth**: Unusual data growth patterns
- **Cleanup Needed**: Old data accumulation

## Configuration

### Django Settings

Add to your `settings.py`:

```python
# Email Alerts
UKF_ALERT_EMAIL_RECIPIENTS = [
    'ops-team@example.com',
    'on-call@example.com'
]

# Slack Integration
UKF_SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

# Custom Webhook
UKF_WEBHOOK_URL = 'https://your-monitoring-system.com/webhooks/ukf'
UKF_WEBHOOK_HEADERS = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'X-Service': 'UKF'
}

# Alert Thresholds (optional - defaults shown)
UKF_ALERT_THRESHOLDS = {
    'health_unhealthy_duration': 300,  # 5 minutes
    'performance_slow_threshold': 2.0,  # seconds
    'embedding_coverage_warning': 0.95,  # 95%
    'error_rate_threshold': 0.05,  # 5%
}

# Suppression Rules (optional)
UKF_ALERT_SUPPRESSION = {
    'min_interval': 3600,  # 1 hour between same alerts
    'quiet_hours': {
        'enabled': True,
        'start': '22:00',
        'end': '07:00',
        'timezone': 'UTC'
    }
}
```

### Environment Variables

For sensitive configuration:

```bash
export UKF_SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export UKF_ALERT_EMAIL_RECIPIENTS="ops@example.com,alerts@example.com"
export UKF_WEBHOOK_AUTH_TOKEN="your-secret-token"
```

## Alert Handlers

### Email Handler

Sends detailed alerts via email. Requires email configuration:

```python
# Email backend configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'REDACTED'
DEFAULT_FROM_EMAIL = 'UKF Alerts <alerts@example.com>'
```

### Slack Handler

Posts alerts to Slack channel:

1. Create Slack webhook at https://api.slack.com/apps
2. Add webhook URL to settings
3. Alerts appear with color-coded severity

Example Slack message:
```
🚨 UKF Alert: Critical
Title: UKF System Unhealthy
Message: System health is critical with 3 issues
Type: health | Level: critical
Recommended Actions:
• Check system logs
• Run health diagnostics
• Review issues in health dashboard
```

### Custom Webhook Handler

Send alerts to any HTTP endpoint:

```python
from shared_memory.monitoring.alerting import WebhookAlertHandler, alert_manager

# Add custom webhook
custom_handler = WebhookAlertHandler(
    webhook_url='https://your-system.com/alerts',
    headers={
        'Authorization': 'Bearer token',
        'Content-Type': 'application/json'
    }
)
alert_manager.add_handler(custom_handler)
```

### PagerDuty Integration

```python
from shared_memory.monitoring.alerting import alert_manager

class PagerDutyHandler:
    def __init__(self, routing_key):
        self.routing_key = routing_key
        self.url = 'https://events.pagerduty.com/v2/enqueue'
    
    def __call__(self, alert):
        severity_map = {
            'critical': 'critical',
            'emergency': 'critical',
            'warning': 'warning',
            'info': 'info'
        }
        
        payload = {
            'routing_key': self.routing_key,
            'event_action': 'trigger',
            'payload': {
                'summary': alert['title'],
                'severity': severity_map.get(alert['level'], 'info'),
                'source': 'ukf',
                'custom_details': alert['details']
            }
        }
        
        requests.post(self.url, json=payload)

# Register handler
pagerduty = PagerDutyHandler('YOUR-ROUTING-KEY')
alert_manager.add_handler(pagerduty)
```

## Alert Rules

### Default Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Health Status | Degraded > 30min | Unhealthy > 5min |
| Search Performance | > 2s average | > 5s average |
| Embedding Coverage | < 95% | < 90% |
| Error Rate | > 5% | > 10% |
| DB Connections | > 80% max | > 95% max |

### Custom Rules

Create custom alert rules:

```python
from shared_memory.monitoring.alerting import alert_manager, AlertType, AlertLevel

def check_custom_metrics():
    # Your metric collection logic
    if custom_metric > threshold:
        alert_manager.send_alert(
            alert_type=AlertType.PERFORMANCE,
            level=AlertLevel.WARNING,
            title="Custom Metric Alert",
            message=f"Metric exceeded threshold: {custom_metric}",
            details={"metric": custom_metric, "threshold": threshold},
            actions=["Review custom metric dashboard"]
        )
```

## Testing Alerts

### Manual Alert Test

```python
python manage.py shell
>>> from shared_memory.monitoring.alerting import alert_manager, AlertType, AlertLevel
>>> alert_manager.send_alert(
...     alert_type=AlertType.HEALTH,
...     level=AlertLevel.INFO,
...     title="Test Alert",
...     message="This is a test of the UKF alerting system",
...     details={"test": True},
...     actions=["No action needed - this is a test"]
... )
```

### Trigger Real Alerts

```bash
# Trigger health alert
curl -X POST http://localhost:8000/api/shared-memory/health/webhook/ \
    -H "Content-Type: application/json" \
    -d '{"trigger": "test_unhealthy"}'

# Trigger performance alert
python -c "
from shared_memory.monitoring.search_performance import SearchPerformanceMonitor
monitor = SearchPerformanceMonitor()
monitor.record_search_query('test', 'semantic', 10.0, 0, error='Test error')
"
```

## Alert Suppression

### Time-based Suppression

Prevent alert fatigue:

```python
# In settings.py
UKF_ALERT_SUPPRESSION = {
    'rules': {
        'health:degraded': {
            'min_interval': 7200,  # 2 hours
            'max_per_day': 3
        },
        'performance:slow': {
            'min_interval': 1800,  # 30 minutes
            'escalate_after': 5  # Escalate to critical after 5 occurrences
        }
    }
}
```

### Conditional Suppression

```python
def custom_suppression_logic(alert):
    # Suppress non-critical alerts during maintenance
    if maintenance_mode and alert['level'] != 'critical':
        return True
    
    # Suppress known issues
    if alert['title'] in known_issues_list:
        return True
    
    return False

alert_manager.suppression_rules['custom'] = custom_suppression_logic
```

## Monitoring Alert Effectiveness

### Alert Metrics

Track alert system performance:

```sql
-- Alert frequency
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    alert_type,
    COUNT(*) as alert_count
FROM alert_history
GROUP BY hour, alert_type
ORDER BY hour DESC;

-- Response times
SELECT 
    alert_id,
    acknowledged_at - created_at as response_time,
    resolved_at - acknowledged_at as resolution_time
FROM alert_history
WHERE acknowledged_at IS NOT NULL;
```

### Alert Dashboard

Create monitoring dashboard:

```python
from shared_memory.monitoring.alerting import alert_manager

def get_alert_stats():
    return {
        'total_alerts_24h': len([a for a in alert_manager.alert_history 
                                if a['timestamp'] > (timezone.now() - timedelta(days=1))]),
        'by_level': Counter(a['level'] for a in alert_manager.alert_history),
        'by_type': Counter(a['type'] for a in alert_manager.alert_history),
        'suppressed_count': len(alert_manager.suppression_rules)
    }
```

## Best Practices

1. **Alert Fatigue Prevention**
   - Set appropriate thresholds
   - Use suppression rules
   - Group related alerts
   - Provide clear actions

2. **Alert Quality**
   - Include context in messages
   - Provide actionable steps
   - Link to runbooks
   - Include relevant metrics

3. **Escalation Paths**
   - Define clear severity levels
   - Set up on-call rotations
   - Document response procedures
   - Regular alert review

4. **Testing**
   - Test all alert channels monthly
   - Verify escalation works
   - Practice incident response
   - Update contact information

## Troubleshooting

### Alerts Not Sending

```bash
# Check handler configuration
python manage.py shell
>>> from shared_memory.monitoring.alerting import alert_manager
>>> print(f"Handlers configured: {len(alert_manager.handlers)}")
>>> for handler in alert_manager.handlers:
...     print(f"  - {handler.__class__.__name__}")

# Test specific handler
>>> from shared_memory.monitoring.alerting import ConsoleAlertHandler
>>> test_handler = ConsoleAlertHandler()
>>> test_handler({'level': 'info', 'title': 'Test', 'message': 'Testing'})
```

### Too Many Alerts

1. Review thresholds in settings
2. Check suppression rules
3. Identify root causes
4. Consider batching related alerts

### Missing Alerts

1. Verify monitoring is running
2. Check alert thresholds
3. Review handler errors in logs
4. Test alert pipeline manually

---

Last Updated: August 4, 2025
Version: 1.0
Phase C5 Alerting Configuration
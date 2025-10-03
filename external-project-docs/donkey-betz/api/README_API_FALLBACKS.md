# Content Pipeline API Fallback System

## Overview

The Content Pipeline includes a robust API fallback system that ensures content generation continues even when external APIs fail. The system includes:

- **Circuit Breakers**: Prevent cascading failures by temporarily blocking calls to failing APIs
- **Automatic Retries**: Exponential backoff with jitter for transient failures
- **Fallback Providers**: Automatic switching to alternative APIs when primary fails
- **Mock Mode**: Development and testing without consuming API credits
- **Health Monitoring**: Real-time tracking of API performance and availability

## Architecture

```
Request → Circuit Breaker → Retry Logic → Primary API
                                ↓ (on failure)
                          Fallback Provider
                                ↓ (if all fail)
                            Mock Response
```

## Configuration

### External APIs Supported

| API Key | Provider | Service | Fallback |
|---------|----------|---------|----------|
| `openai-completion` | OpenAI | Text generation | `anthropic-completion` |
| `openai-dalle` | OpenAI | Image generation | `stable-diffusion` |
| `anthropic-completion` | Anthropic | Text generation | `openai-completion` |
| `gemini-completion` | Google | Text generation | `openai-completion` |
| `groq-completion` | Groq | Fast text generation | `openai-completion` |
| `stable-diffusion` | Stability AI | Image generation | `openai-dalle` |
| `replicate-generation` | Replicate | Various models | `stable-diffusion` |

### Settings

Configure in `settings.py`:

```python
# Enable/disable mock mode globally
CONTENT_PIPELINE_MOCK_MODE = False

# Circuit breaker settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5  # Failures before opening
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60  # Seconds before retry

# Retry settings
API_MAX_RETRIES = 3
API_RETRY_DELAY = 1.0  # Initial delay in seconds
```

## Usage

### Basic Usage

The fallback system is automatically applied when using the content pipeline:

```python
# In stage_executor.py, AI generation automatically uses fallbacks
result = self._execute_ai_generation()
```

### Manual Usage with Decorator

```python
from content_pipeline.services.api_fallback_service import with_fallback

@with_fallback("openai-completion")
async def generate_content(prompt: str) -> str:
    # Your API call here
    response = await openai_client.completions.create(
        model="gpt-4",
        prompt=prompt
    )
    return response.choices[0].text
```

### Direct Service Usage

```python
from content_pipeline.services.api_fallback_service import api_fallback_service

# Call with automatic fallback
result = await api_fallback_service.call_with_fallback(
    "stable-diffusion",
    generate_image_function,
    prompt="A beautiful sunset"
)
```

## Mock Mode

### Enable Mock Mode

#### Via Management Command
```bash
# Enable for all APIs
python manage.py toggle_api_mock_mode --enable

# Enable for specific API
python manage.py toggle_api_mock_mode --api openai-completion --enable

# Check status
python manage.py toggle_api_mock_mode --status
```

#### Via API Endpoint
```bash
# Enable mock mode
curl -X POST http://localhost:8000/api/pipeline/api-health/mock-mode/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Enable for specific API
curl -X POST http://localhost:8000/api/pipeline/api-health/mock-mode/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "stable-diffusion", "enabled": true}'
```

#### Programmatically
```python
from content_pipeline.services.api_fallback_service import api_fallback_service

# Enable mock mode
api_fallback_service.enable_mock_mode()

# Enable for specific API
api_fallback_service.enable_mock_mode("openai-dalle")
```

### Mock Responses

Mock responses are defined in `external_api_config.py`. Example:

```python
def mock_stable_diffusion_generation(**kwargs) -> Dict[str, Any]:
    return {
        "finish_reason": "SUCCESS",
        "seed": 12345,
        "image": "data:image/png;base64,..."  # Base64 encoded placeholder
    }
```

## Health Monitoring

### Dashboard Endpoint

```bash
# Get comprehensive health dashboard
curl http://localhost:8000/api/pipeline/api-health/dashboard/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "summary": {
    "total_apis": 7,
    "healthy_apis": 5,
    "degraded_apis": 1,
    "unhealthy_apis": 1,
    "overall_success_rate": 94.5
  },
  "apis": {
    "openai-completion": {
      "health_status": "healthy",
      "success_rate": 98.5,
      "avg_response_time": 0.842,
      "total_requests": 1523
    }
  },
  "circuit_breakers": {
    "open_circuits": 1,
    "circuits": {
      "stable-diffusion": {
        "state": "open",
        "failure_count": 5,
        "last_failure_time": 1234567890
      }
    }
  }
}
```

### Individual API Status

```bash
# Get status for specific API
curl http://localhost:8000/api/pipeline/api-health/status/openai-dalle/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Trigger Health Check

```bash
# Check all APIs
curl -X POST http://localhost:8000/api/pipeline/api-health/check/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check specific APIs
curl -X POST http://localhost:8000/api/pipeline/api-health/check/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"api_keys": ["openai-completion", "stable-diffusion"]}'
```

## Circuit Breaker Management

### Reset Circuit Breaker

```bash
# Reset circuit for specific API
curl -X POST http://localhost:8000/api/pipeline/api-health/circuit-breaker/stable-diffusion/reset/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Circuit Breaker States

- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Service failing, requests rejected immediately
- **HALF_OPEN**: Testing recovery, limited requests allowed

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Success Rate**: Below 95% indicates problems
2. **Response Time**: Track P95 and P99 latencies
3. **Circuit State**: Alert when circuits open
4. **Fallback Usage**: High fallback usage indicates primary API issues

### Example Monitoring Query

```python
from content_pipeline.services.api_health_monitor import api_health_monitor

# Get all metrics
metrics = api_health_monitor.get_dashboard_data()

# Check specific API
status = api_health_monitor.get_api_status("openai-completion")
if status["success_rate"] < 95:
    send_alert(f"API degraded: {status}")
```

## Troubleshooting

### Common Issues

1. **Circuit Breaker Stuck Open**
   - Check API health: `python manage.py toggle_api_mock_mode --status`
   - Manually reset: `curl -X POST .../circuit-breaker/API_KEY/reset/`
   - Review logs for actual errors

2. **Fallbacks Not Working**
   - Verify fallback configuration in `external_api_config.py`
   - Check if fallback API keys are set
   - Review fallback chain in logs

3. **Mock Mode Not Working**
   - Verify `CONTENT_PIPELINE_MOCK_MODE` setting
   - Check individual API mock status
   - Ensure mock response generators are defined

### Debug Logging

Enable detailed logging:

```python
import logging
logging.getLogger('content_pipeline.services').setLevel(logging.DEBUG)
```

## Best Practices

1. **Configure Appropriate Timeouts**
   - Image generation: 60 seconds
   - Text generation: 30 seconds
   - Health checks: 10 seconds

2. **Set Realistic Thresholds**
   - Circuit breaker: 5 failures
   - Recovery timeout: 60 seconds
   - Retry attempts: 3

3. **Monitor Fallback Usage**
   - High fallback usage indicates primary API issues
   - Consider switching primary/fallback if pattern persists

4. **Test Failure Scenarios**
   - Use mock mode to test fallback behavior
   - Simulate circuit breaker scenarios
   - Verify error handling

5. **Production Deployment**
   - Start with mock mode enabled
   - Gradually enable real APIs
   - Monitor metrics closely
   - Have manual overrides ready

## Development Workflow

1. **Local Development**
   ```bash
   # Enable mock mode
   export CONTENT_PIPELINE_MOCK_MODE=True
   python manage.py runserver
   ```

2. **Testing with Real APIs**
   ```bash
   # Disable mock for specific API
   python manage.py toggle_api_mock_mode --api openai-completion --disable
   ```

3. **Simulating Failures**
   ```python
   # Force circuit breaker open
   from content_pipeline.services.circuit_breaker import circuit_registry
   breaker = circuit_registry.get("stable-diffusion")
   breaker._state = CircuitState.OPEN
   ```

## Performance Considerations

- Mock responses are returned immediately (0.5s simulated delay)
- Circuit breakers prevent wasteful retries to failing services
- Exponential backoff prevents thundering herd
- Response caching reduces API calls (configurable TTL)

## Security Notes

- API keys are never logged
- Mock mode reveals no sensitive data
- Health endpoints require authentication
- Circuit breaker state is not exposed publicly
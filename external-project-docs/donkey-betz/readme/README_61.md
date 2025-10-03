# API Cost Tracking

This module provides comprehensive API usage and cost tracking for all AI service providers.

## Features

- **Real-time Usage Tracking**: Automatically tracks every API call with token counts
- **Cost Calculation**: Calculates costs based on current provider pricing
- **Daily Summaries**: Aggregates usage data for efficient dashboard queries
- **Multi-Provider Support**: Tracks OpenAI, Anthropic, Google, ElevenLabs, Stability AI, Replicate, and Runway
- **Dashboard Integration**: Displays costs in the Unified Dashboard

## Components

### Models
- `APIProvider`: Stores API provider information
- `APIPricing`: Current pricing tiers for each model
- `APIUsage`: Individual API call records
- `DailyAPIUsageSummary`: Aggregated daily usage data

### Services
- `APITrackingService`: Main service for tracking and querying usage
- `APITrackingMixin`: Mixin for easy integration into service classes

### Integration
The tracking is integrated into `UnifiedAIService` and automatically tracks all API calls made through the system.

## Usage

```python
# The tracking happens automatically when using UnifiedAIService
from api_services.unified_ai_service import UnifiedAIService

ai_service = UnifiedAIService()
response = ai_service.generate_sync(
    prompt="Hello world",
    user=request.user,
    task_type='general'
)

# Query usage data
from api_tracking.tracking_service import APITrackingService

tracking_service = APITrackingService()
daily_cost = tracking_service.get_daily_cost(user)
dashboard_data = tracking_service.get_user_dashboard_data(user)
```

## Pricing Data

Current pricing is defined in `tracking_service.py` and includes:
- OpenAI: GPT-4, GPT-4o, GPT-3.5-turbo, DALL-E, Whisper
- Anthropic: Claude 3 models
- Google: Gemini Pro
- ElevenLabs: Voice synthesis
- Stability AI: Image generation
- Replicate: Open source models
- Runway: Video generation

## Dashboard Display

The costs are displayed in the Mission Control widget with:
- Daily API costs with automatic formatting for small values
- Provider breakdown
- Monthly totals
- Real-time updates as API calls are made
# API Reference

Complete API documentation for the Unified AI & Sports Analytics Platform.

## Base URL

```
https://api.your-domain.com/api/v1
```

## Authentication

All API requests require authentication using Bearer tokens:

```http
Authorization: Bearer <your-token>
```

## Response Format

All responses follow this structure:

```json
{
  "success": boolean,
  "data": object | array,
  "error": string | null,
  "meta": {
    "timestamp": "ISO 8601",
    "version": "1.0.0"
  }
}
```

---

## AI Provider Endpoints

### Get AI Completion

Generate text completion using AI providers.

**Endpoint:** `POST /ai/completion/`

**Request Body:**
```json
{
  "prompt": "string",
  "model": "gpt-3.5-turbo | gpt-4 | claude-3-haiku | claude-3-sonnet",
  "temperature": 0.0-1.0,
  "max_tokens": 1-4096,
  "provider": "openai | anthropic | auto"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "content": "Generated text response",
    "model": "gpt-3.5-turbo",
    "provider": "openai",
    "usage": {
      "prompt_tokens": 50,
      "completion_tokens": 100,
      "total_tokens": 150
    },
    "cost": 0.0025
  }
}
```

**Example:**
```bash
curl -X POST https://api.your-domain.com/api/v1/ai/completion/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain machine learning in simple terms",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  }'
```

### Get Embedding

Generate text embeddings for similarity search.

**Endpoint:** `POST /ai/embedding/`

**Request Body:**
```json
{
  "text": "string",
  "model": "text-embedding-ada-002"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "embedding": [0.001, -0.002, ...],
    "dimension": 1536,
    "model": "text-embedding-ada-002"
  }
}
```

---

## Sports Analytics Endpoints

### Convert Odds

Convert between different odds formats.

**Endpoint:** `POST /sports/convert_odds/`

**Request Body:**
```json
{
  "odds": number,
  "from_format": "american | decimal | fractional",
  "to_format": "american | decimal | fractional"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original": -110,
    "from_format": "american",
    "to_format": "decimal",
    "converted": 1.909
  }
}
```

### Calculate Expected Value

Calculate the expected value of a bet.

**Endpoint:** `POST /sports/calculate_ev/`

**Request Body:**
```json
{
  "odds": number,
  "win_probability": 0.0-1.0,
  "stake": number
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "odds": -110,
    "win_probability": 0.55,
    "implied_probability": 0.524,
    "edge": 0.026,
    "stake": 100,
    "expected_value": 4.55,
    "ev_percentage": 4.55,
    "recommendation": "Value bet"
  }
}
```

### Find Arbitrage

Detect arbitrage opportunities across bookmakers.

**Endpoint:** `POST /sports/find_arbitrage/`

**Request Body:**
```json
{
  "odds_set": [
    {
      "book": "BookA",
      "outcome": "Team1",
      "odds": 120
    },
    {
      "book": "BookB",
      "outcome": "Team2",
      "odds": 110
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "arbitrage_found": true,
    "opportunity": {
      "roi_percentage": 2.38,
      "total_stake": 1000,
      "stakes": [
        {
          "book": "BookA",
          "outcome": "Team1",
          "stake": 476.19
        },
        {
          "book": "BookB",
          "outcome": "Team2",
          "stake": 523.81
        }
      ],
      "guaranteed_profit": 23.81
    }
  }
}
```

### Kelly Criterion

Calculate optimal bet size using Kelly Criterion.

**Endpoint:** `POST /sports/kelly_criterion/`

**Request Body:**
```json
{
  "bankroll": number,
  "win_probability": 0.0-1.0,
  "odds": number,
  "fraction": 0.0-1.0
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "full_kelly": {
      "recommended_percentage": 0.05,
      "recommended_stake": 50,
      "edge": 0.026,
      "expected_growth": 0.0013,
      "risk_of_ruin": 0.02
    },
    "fractional_kelly": {
      "recommended_percentage": 0.0125,
      "recommended_stake": 12.50,
      "edge": 0.026,
      "expected_growth": 0.0003,
      "risk_of_ruin": 0.005
    },
    "fraction_used": 0.25,
    "recommendation": {
      "strategy": "Quarter Kelly",
      "stake": 12.50,
      "percentage": 1.25
    }
  }
}
```

### Calculate Parlay

Calculate combined odds and payout for parlays.

**Endpoint:** `POST /sports/calculate_parlay/`

**Request Body:**
```json
{
  "legs": [
    {"odds": -110, "description": "Lakers -5.5"},
    {"odds": 150, "description": "Over 220.5"}
  ],
  "stake": 100
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "parlay": {
      "legs": [...],
      "combined_odds": 257,
      "decimal_odds": 3.57,
      "implied_probability": 0.28,
      "potential_payout": 357.27,
      "potential_profit": 257.27,
      "stake": 100
    }
  }
}
```

### Round Robin

Generate round robin bet combinations.

**Endpoint:** `POST /sports/round_robin/`

**Request Body:**
```json
{
  "legs": [
    {"odds": -110},
    {"odds": 100},
    {"odds": 150}
  ],
  "parlay_size": 2,
  "stake_per_parlay": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "round_robin": {
      "legs": [...],
      "parlay_size": 2,
      "number_of_parlays": 3,
      "parlays": [...],
      "stake_per_parlay": 10,
      "total_stake": 30,
      "total_potential_payout": 107.27,
      "total_potential_profit": 77.27,
      "max_roi": 257.57
    }
  }
}
```

### Track Line Movement

Analyze odds movement over time.

**Endpoint:** `POST /sports/track_line_movement/`

**Request Body:**
```json
{
  "opening_line": -110,
  "current_line": -105,
  "time_elapsed_hours": 24
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "line_movement": {
      "opening_line": -110,
      "current_line": -105,
      "movement": 5,
      "movement_percentage": 2.17,
      "volume_indicator": "moderate",
      "timestamp": "2025-01-09T12:00:00Z"
    }
  }
}
```

### Analyze Performance

Analyze historical betting performance.

**Endpoint:** `POST /sports/analyze_performance/`

**Request Body:**
```json
{
  "bet_history": [
    {
      "result": "win",
      "stake": 100,
      "return": 190,
      "odds": -110,
      "profit": 90
    },
    {
      "result": "loss",
      "stake": 100,
      "return": 0,
      "odds": 150,
      "profit": -100
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "performance": {
      "total_bets": 2,
      "wins": 1,
      "losses": 1,
      "pushes": 0,
      "win_rate": 0.5,
      "total_staked": 200,
      "total_returned": 190,
      "total_profit": -10,
      "roi_percentage": -5.0,
      "average_odds": 20,
      "current_streak": {"type": "loss", "count": 1},
      "longest_win_streak": 1,
      "longest_loss_streak": 1,
      "profitable": false
    }
  }
}
```

### Calculate Juice

Calculate bookmaker margin (juice/vig).

**Endpoint:** `POST /sports/calculate_juice/`

**Request Body:**
```json
{
  "odds1": -110,
  "odds2": -110
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "juice_percentage": 4.76,
    "true_probabilities": {
      "outcome1": 0.5,
      "outcome2": 0.5
    },
    "no_vig_odds": {
      "outcome1": -100,
      "outcome2": 100
    }
  }
}
```

### Optimal Strategy

Get optimal betting strategy recommendation.

**Endpoint:** `POST /sports/optimal_strategy/`

**Request Body:**
```json
{
  "bankroll": 1000,
  "win_probability": 0.55,
  "odds": -110,
  "risk_tolerance": "low | medium | high"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "strategy": {
      "recommended_strategy": "Quarter Kelly",
      "recommended_stake": 12.50,
      "recommended_percentage": 1.25,
      "alternatives": {
        "full_kelly": 50,
        "half_kelly": 25,
        "quarter_kelly": 12.50,
        "fixed_2_percent": 20
      },
      "edge": 0.026,
      "expected_growth": 0.0003,
      "risk_of_ruin": 0.005
    }
  }
}
```

---

## WebSocket Endpoints

### Real-time Odds Updates

Connect to receive live odds updates.

**Endpoint:** `ws://api.your-domain.com/ws/odds/`

**Message Format:**
```json
{
  "type": "odds_update",
  "data": {
    "game_id": "12345",
    "book": "BookA",
    "home_odds": -110,
    "away_odds": -110,
    "timestamp": "2025-01-09T12:00:00Z"
  }
}
```

### Arbitrage Alerts

Receive real-time arbitrage notifications.

**Endpoint:** `ws://api.your-domain.com/ws/arbitrage/`

**Message Format:**
```json
{
  "type": "arbitrage_alert",
  "data": {
    "opportunity_id": "arb_123",
    "roi_percentage": 2.5,
    "expires_at": "2025-01-09T12:05:00Z",
    "stakes": [...]
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Rate Limiting

- **Default**: 100 requests per minute
- **Authenticated**: 1000 requests per minute
- **Premium**: 10000 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641700000
```

## SDK Examples

### Python
```python
from unified_sdk import UnifiedClient

client = UnifiedClient(api_key="your-key")

# AI completion
response = client.ai.get_completion(
    prompt="Hello",
    model="gpt-3.5-turbo"
)

# Sports analytics
ev = client.sports.calculate_ev(
    odds=-110,
    probability=0.55,
    stake=100
)
```

### JavaScript
```javascript
import { UnifiedClient } from 'unified-sdk';

const client = new UnifiedClient({ apiKey: 'your-key' });

// AI completion
const response = await client.ai.getCompletion({
  prompt: 'Hello',
  model: 'gpt-3.5-turbo'
});

// Sports analytics
const ev = await client.sports.calculateEV({
  odds: -110,
  probability: 0.55,
  stake: 100
});
```

---

*Next: [User Guide](./user-guide.md) →*
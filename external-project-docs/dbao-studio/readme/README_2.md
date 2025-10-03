# DBAO Tools Manifest Documentation

This directory contains the comprehensive tools manifest and SDK documentation for the Donkey Betz Agent Orchestra (DBAO) system.

## Overview

The DBAO system provides a unified API for AI agent orchestration, sports betting analytics, and AI Studio compatibility. This manifest catalogs all available endpoints, WebSocket connections, and external integrations.

## Files

- `tools-manifest.json` - Complete API and tools catalog in JSON format
- `README.md` - This documentation file

## API Categories

### Agent Orchestration
- **Execute Agent** (`POST /api/execute/`) - Execute single agent tasks
- **Orchestrate Task** (`POST /api/orchestrate/`) - Multi-agent workflows
- **Suggest Agent** (`POST /api/suggest/`) - Intelligent agent routing

### Odds & Sports Betting
- **Convert Odds** (`POST /api/v1/odds/convert-odds/`) - Format conversion with implied probability
- **Kelly Criterion** (`POST /api/v1/odds/kelly-criterion/`) - Optimal bet sizing calculations
- **Game Analysis** (`POST /api/v1/sports/analyze-game/`) - AI-powered sports analysis

### Content Generation (AI Studio Compatible)
- **Generate Content** (`POST /api/content/generate/`) - Text content generation
- **Generate Image** (`POST /api/images/generate/`) - AI image creation
- **Generate Video** (`POST /api/videos/generate/`) - Video generation (planned)

### System
- **Health Check** (`GET /api/health/`) - System status and monitoring

## WebSocket Connections

### Assistant WebSocket (`/ws/assistant/`)
Real-time updates for agent execution, content generation, and AI Studio compatibility.

**Message Types:**
- `ping` → `pong` (heartbeat)
- `subscribe_instance` - Agent instance updates
- `subscribe_orchestration` - Multi-agent workflow updates

**Event Types:**
- `agent_instance_update` - Agent execution progress
- `content_generation_update` - Content creation status
- `sports_betting_update` - Sports analysis results

### Dashboard WebSocket (`/ws/dashboard/`)
Real-time dashboard statistics and user activity updates (requires authentication).

## Authentication

The system supports multiple authentication methods:
- **Token Authentication**: DRF tokens via `/api/auth/token/`
- **Session Authentication**: Django sessions
- **Anonymous Access**: Allowed for testing endpoints

## CORS Configuration

Configured for UCWSF (Unified Content & WebSocket Frontend) compatibility:
- **Allowed Origins**: localhost:3000, 8080, 8081
- **Custom Headers**: `X-Orchestrator`, `X-Request-ID`, `X-Client-Version`, `X-Agent-Request`
- **Credentials**: Supported for authenticated requests

## External Integrations

### AI Providers
- **OpenAI API**: Primary provider (GPT-3.5/4, DALL-E)
- **Anthropic Claude**: Alternative provider (requires configuration)

### Infrastructure
- **Redis**: Cache layer and Celery broker (127.0.0.1:6379)
- **Celery**: Asynchronous task processing
- **Channels**: WebSocket support via Django Channels

## Deployment

- **Server**: Daphne ASGI server
- **Port**: 8000 (configurable)
- **WebSocket**: Full support via Channels
- **Health Check**: `/api/health/` for monitoring

## Usage Examples

### Execute an Agent
```bash
curl -X POST http://localhost:8000/api/execute/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"agent_type": "business", "task_description": "Create a marketing plan"}'
```

### Convert Odds
```bash
curl -X POST http://localhost:8000/api/v1/odds/convert-odds/ \
  -H "Content-Type: application/json" \
  -H "X-Orchestrator: dbao-client" \
  -d '{"odds": "110", "from_format": "american"}'
```

### Test WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/assistant/');
ws.onopen = () => ws.send(JSON.stringify({type: 'ping'}));
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## SDK Generation

TypeScript and Python SDKs are automatically generated from this manifest to provide type-safe client libraries for web and native applications.

## Notes

- All endpoints support optional trailing slashes
- CORS is configured for development origins (localhost:3000, 8080, 8081)
- WebSocket connections support anonymous access for testing
- System includes comprehensive error handling and validation
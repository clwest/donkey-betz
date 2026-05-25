# API Documentation

**Generated:** December 23, 2025
**Session:** 538
**Status:** Security Hardened + Intelligence APIs Public

---

## Authentication

All API endpoints require authentication unless explicitly listed as public.

### Authentication Methods

1. **Session Authentication** (Browser)
   - Login via `/accounts/login/`
   - Session cookie automatically sent with requests

2. **Token Authentication** (API Clients)
   ```
   Authorization: Token <your-token>
   # or
   Authorization: Bearer <your-token>
   ```

3. **API Key Header**
   ```
   X-API-KEY: <your-api-key>
   ```

### Getting a Token
```bash
curl -X POST /api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

---

## Public Endpoints (No Auth Required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health/` | GET | Health check |
| `/health/` | GET | Simple ping |
| `/api/v1/auth/login/` | POST | User login |
| `/api/v1/auth/register/` | POST | User registration |
| `/api/v1/auth/forgot-password/` | POST | Password reset request |
| `/api/v1/auth/reset-password/` | POST | Password reset confirmation |
| `/api/public-stats/` | GET | Public platform statistics |
| `/api/spider-intelligence/dashboard-stats/` | GET | Spider network statistics |
| `/api/spider-intelligence/detail/<name>/` | GET | Spider detail with articles |
| `/api/agent-intelligence/detail/<name>/` | GET | ~~Removed Session 1009~~ |
| `/api/situation-intelligence/detail/<type>/` | GET | Situation detail with triggers |
| `/api/intelligence/cross-references/` | GET | Cross-reference mappings |

---

## Core API Endpoints

### Agent APIs

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/agents/` | GET | List all agents | Required |
| `/api/agents/<id>/` | GET | Get agent details | Required |
| `/api/agent-dashboard/` | GET | Agent dashboard data | Required |
| `/api/agent-evolution/` | GET | Agent evolution status | Required |
| `/api/agent-mood/` | GET | ~~Removed Session 1009~~ | N/A |
| `/api/agent-relationships/` | GET | Agent relationships | Required |
| `/api/agent-conversations/` | GET | Agent conversations | Required |
| `/api/agent-dreams/` | GET | Agent dreams | Required |

### Content APIs

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/projects/` | GET, POST | List/create projects | Required |
| `/api/projects/<id>/` | GET, PUT, DELETE | Project CRUD | Required |
| `/api/creative-projects/` | GET, POST | Creative projects | Required |
| `/api/content/generate/` | POST | Generate content | Required |

### Income Builder APIs

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/income/` | GET | Income opportunities | Required |
| `/api/income/action/` | POST | Take action on opportunity | Required |
| `/api/opportunities/` | GET | List opportunities | Required |
| `/api/job-applications/` | GET, POST | Job applications | Required |

### Revenue APIs

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/revenue-tracking/` | GET | Revenue tracking | Required |
| `/api/revenue-analytics/` | GET | Revenue analytics | Required |
| `/api/roi-metrics/` | GET | ROI metrics | Required |

### Spider APIs

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/spider-dashboard/` | GET | Spider dashboard | Required |
| `/api/spider-intelligence/` | GET | Spider intelligence | Required |
| `/api/spider-data/` | GET | Raw spider data | Required |

### Intelligence Command Center APIs (Session 537-538)

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/spider-intelligence/dashboard-stats/` | GET | Spider counts by category | Public |
| `/api/spider-intelligence/detail/<name>/` | GET | Spider articles/data | Public |
| `/api/agent-intelligence/detail/<name>/` | GET | ~~Removed Session 1009~~ | N/A |
| `/api/situation-intelligence/detail/<type>/` | GET | Situation triggers, fires, events | Public |
| `/api/intelligence/cross-references/` | GET | Spider→Agent→Situation mappings | Public |

**Response Examples:**

Spider Detail:
```json
{
  "status": "success",
  "spider_name": "techcrunch",
  "items": [
    {"title": "...", "description": "...", "url": "https://..."}
  ]
}
```

Agent Detail:
```json
{
  "status": "success",
  "agent": {"name": "...", "effectiveness": 100, "total_executions": 5},
  "knowledge": [...],
  "transfers": {"taught": [...], "learned": [...]}
}
```

### Learning APIs

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/learning/` | GET | Learning feed | Required |
| `/api/learning-loop/` | GET | Learning loop status | Required |
| `/api/memory-palace/` | GET | Memory palace data | Required |
| `/api/collective/` | GET | Collective intelligence | Required |

### Autonomous Systems

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/autonomous-dashboard/` | GET | Autonomous system status | Required |
| `/api/monitoring/` | GET | Monitoring dashboard | Optional |
| `/api/super-platform/` | GET | Super platform status | Required |
| `/api/boardroom/` | GET | Boardroom decisions | Required |

---

## WebSocket Endpoints

All WebSocket connections require authentication via token in query string:

```javascript
const ws = new WebSocket('wss://example.com/ws/agent/?token=YOUR_TOKEN');
```

| Endpoint | Description |
|----------|-------------|
| `/ws/agent/` | Agent real-time updates |
| `/ws/dashboard/` | Dashboard updates |
| `/ws/project/<id>/` | Project real-time |
| `/ws/collaboration/` | Team collaboration |
| `/ws/assistant/` | AI Assistant |

---

## Error Responses

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "Staff access required"
}
```

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid request parameters"
}
```

### 500 Server Error
```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse:

| Tier | Limit |
|------|-------|
| Anonymous | 100 requests/hour |
| Authenticated | 1000 requests/hour |
| Staff | 10000 requests/hour |

Rate limit headers included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640102400
```

---

## Security Notes

1. **HTTPS Required**: All API requests must use HTTPS in production
2. **Token Security**: Never expose tokens in URLs or logs
3. **CSRF**: API endpoints use token auth, CSRF exempt
4. **CORS**: Configured for allowed origins only

---

*Generated by Session 528 - API Security Hardening*

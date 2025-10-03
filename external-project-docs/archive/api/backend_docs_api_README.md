# Donkey Betz API Documentation

Welcome to the Donkey Betz API documentation. This guide provides comprehensive information about our REST API endpoints, authentication methods, and best practices for integration.

## 🚀 Quick Start

### Base URL
```
Development: http://localhost:8000
Production: https://api.donkeybetz.com
```

### API Documentation Interfaces
- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

## 📋 Table of Contents

1. [Authentication](./authentication.md) - JWT tokens, 2FA, and security
2. [Code Examples](./examples/) - Examples in cURL, Python, JavaScript
3. [WebSocket APIs](./websockets.md) - Real-time updates and streaming
4. [Rate Limiting](./rate-limiting.md) - API limits and best practices
5. [Error Handling](./errors.md) - Error codes and responses

## 🏗️ Architecture Overview

The Donkey Betz API is organized into the following main sections:

### Core Services
- **Authentication** (`/api/auth/`) - User authentication and registration
- **User Management** (`/api/user/`) - Profile and settings management
- **Core Platform** (`/api/core/`) - Dashboard, analytics, and system features

### AI Services
- **Agent Orchestra** (`/api/agent-orchestra/`) - 21+ specialized AI agents
- **AI Partner** (`/api/ai-partner/`) - Personal AI chat and memory palace
- **Content Studio** (`/api/content/`) - Image and video generation
- **Universal Builder** (`/api/universal-builder/`) - Dynamic business generation

### Business Intelligence
- **Stock Intelligence** (`/api/agent-orchestra/stocks/`) - Real-time market analysis
- **Research Intelligence** (`/api/agent-orchestra/research/`) - Unified search platform
- **Reddit Scout** (`/api/agent-orchestra/reddit/`) - Startup idea discovery

### Additional Features
- **Memory Palace** (`/api/memory/`) - Personal knowledge management
- **Privacy Controls** (`/api/privacy/`) - Data management and GDPR compliance
- **Walking Companion** (`/api/walking-companion/`) - Exercise tracking

## 🔑 Authentication

All API endpoints (except registration and login) require authentication using JWT tokens.

### Obtaining Tokens
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

### Using Tokens
Include the access token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 📊 Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data here
  },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_name": ["This field is required."]
    }
  }
}
```

## 🚦 Rate Limiting

The API implements rate limiting to ensure fair usage:

| User Type | Limit | Window |
|-----------|-------|--------|
| Anonymous | 20 requests | 1 minute |
| Authenticated | 200 requests | 1 minute |
| Stock APIs | 300 requests | 1 minute |
| Auth endpoints | 3 requests | 1 minute |

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 150
X-RateLimit-Reset: 1640995200
```

## 🔄 Pagination

List endpoints support pagination using query parameters:

```http
GET /api/agent-orchestra/orchestrations/?page=2&page_size=20
```

Response includes pagination metadata:
```json
{
  "count": 150,
  "next": "http://api.donkeybetz.com/api/agent-orchestra/orchestrations/?page=3",
  "previous": "http://api.donkeybetz.com/api/agent-orchestra/orchestrations/?page=1",
  "results": [...]
}
```

## 🌐 CORS Policy

The API supports CORS for the following origins:
- `http://localhost:5173` (Development)
- `https://app.donkeybetz.com` (Production)
- `https://donkeybetz.com` (Main site)

Custom origins can be requested for integration partners.

## 📱 WebSocket Support

Real-time updates are available via WebSocket connections:

```javascript
const ws = new WebSocket('wss://api.donkeybetz.com/ws/agent-activity/');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent update:', data);
};
```

See [WebSocket Documentation](./websockets.md) for details.

## 🛡️ Security Best Practices

1. **Never expose tokens in client-side code**
2. **Use HTTPS in production**
3. **Implement token refresh logic**
4. **Store tokens securely (HttpOnly cookies or secure storage)**
5. **Validate and sanitize all inputs**
6. **Implement request signing for sensitive operations**

## 📚 API Sections

### [Authentication & User Management](./authentication.md)
- User registration and login
- Password management
- Two-factor authentication
- Profile and settings

### [AI Agent Orchestra](./agent-orchestra.md)
- Deploy specialized AI agents
- Task orchestration
- Agent templates and customization
- Real-time progress tracking

### [Stock Intelligence](./stock-intelligence.md)
- Real-time market data
- Technical analysis
- Portfolio management
- Price alerts

### [Content Creation](./content-studio.md)
- AI image generation (DALL-E, Stable Diffusion)
- Video creation
- Visual styles library
- Media management

### [Memory Palace](./memory-palace.md)
- Personal AI chat
- Semantic memory search
- Document ingestion
- Knowledge management

## 🚀 Getting Started Examples

### 1. Register a New User
```bash
curl -X POST https://api.donkeybetz.com/api/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password1": "SecurePass123!",
    "password2": "SecurePass123!",
    "username": "newuser"
  }'
```

### 2. Deploy an AI Agent
```bash
curl -X POST https://api.donkeybetz.com/api/agent-orchestra/execute/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Analyze AAPL stock and provide investment recommendations",
    "task_type": "stock_analysis"
  }'
```

### 3. Search Memories
```bash
curl -X POST https://api.donkeybetz.com/api/ai-partner/memory/search/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "meetings about product launch",
    "limit": 10
  }'
```

## 📞 Support

- **Email**: support@donkeybetz.com
- **Documentation**: https://docs.donkeybetz.com
- **Status Page**: https://status.donkeybetz.com

## 🔄 Changelog

### Version 1.0.0 (Current)
- Initial API release
- 250+ endpoints
- WebSocket support
- Complete AI agent integration
- Real-time market data
- Content generation studio

---

For detailed endpoint documentation, use the interactive [Swagger UI](http://localhost:8000/api/docs/) or refer to the specific section documentation.
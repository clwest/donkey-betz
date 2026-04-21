# API Endpoints Reference

## Base URL
- **Development**: `http://localhost:8000/api/`
- **Production**: `https://your-app.onrender.com/api/`

## Authentication

All endpoints except registration and login require authentication via token in header:
```
Authorization: Token YOUR_TOKEN_HERE
```

---

## 1. User Registration

### `POST /api/auth/register/`

Create a new user account.

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "securepassword123",
    "email": "john@example.com"
}
```

**Response (201 Created):**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com"
    },
    "token": "<redacted-993f8273-2026-04-20>"
}
```

**Errors:**
- `400 Bad Request`: Username already exists or invalid data
- `422 Unprocessable Entity`: Missing required fields

---

## 2. User Login

### `POST /api/auth/login/`

Authenticate and receive access token.

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com"
    },
    "token": "<redacted-993f8273-2026-04-20>"
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials

---

## 3. Create Content

### `POST /api/content/create/`

Generate AI content (text or image).

**Headers:**
```
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json
```

**Request Body (Text):**
```json
{
    "type": "text",
    "prompt": "Write a haiku about artificial intelligence"
}
```

**Request Body (Image):**
```json
{
    "type": "image",
    "prompt": "A futuristic city with flying cars at sunset, cyberpunk style"
}
```

**Response (200 OK) - Text:**
```json
{
    "id": 1,
    "type": "text",
    "prompt": "Write a haiku about artificial intelligence",
    "result": "Silicon dreams wake\nAlgorithms learn to think\nFuture blooms in code",
    "created_at": "2025-08-27T10:30:00Z"
}
```

**Response (200 OK) - Image:**
```json
{
    "id": 2,
    "type": "image",
    "prompt": "A futuristic city with flying cars at sunset, cyberpunk style",
    "result": "https://oaidalleapiprodscus.blob.core.windows.net/...",
    "created_at": "2025-08-27T10:31:00Z"
}
```

**Errors:**
- `400 Bad Request`: Invalid type or missing prompt
- `401 Unauthorized`: Missing or invalid token
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: OpenAI API error

---

## 4. List Content

### `GET /api/content/list/`

Get all content created by the authenticated user.

**Headers:**
```
Authorization: Token YOUR_TOKEN_HERE
```

**Query Parameters (Optional):**
- `limit`: Maximum number of results (default: 100)
- `offset`: Skip first N results (for pagination)
- `type`: Filter by content type (`text` or `image`)

**Response (200 OK):**
```json
{
    "count": 2,
    "contents": [
        {
            "id": 2,
            "type": "image",
            "prompt": "A futuristic city...",
            "result": "https://oaidalleapiprodscus.blob.core.windows.net/...",
            "created_at": "2025-08-27T10:31:00Z"
        },
        {
            "id": 1,
            "type": "text",
            "prompt": "Write a haiku...",
            "result": "Silicon dreams wake...",
            "created_at": "2025-08-27T10:30:00Z"
        }
    ]
}
```

**Errors:**
- `401 Unauthorized`: Missing or invalid token

---

## 5. Search Memory

### `POST /api/memory/search/`

Search through stored memories using vector similarity (or importance-based in SQLite).

**Headers:**
```
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json
```

**Request Body:**
```json
{
    "query": "artificial intelligence poetry",
    "limit": 10
}
```

**Response (200 OK):**
```json
{
    "count": 3,
    "results": [
        {
            "id": 5,
            "content": "Silicon dreams wake\nAlgorithms learn to think\nFuture blooms in code",
            "similarity": 0.89,
            "created_at": "2025-08-27T10:30:00Z"
        },
        {
            "id": 3,
            "content": "AI poetry combines the precision of algorithms...",
            "similarity": 0.76,
            "created_at": "2025-08-27T09:15:00Z"
        }
    ]
}
```

**Notes:**
- In development (SQLite), `similarity` is based on importance score
- In production (PostgreSQL + pgvector), `similarity` is true cosine similarity
- Memories are automatically created from generated content

**Errors:**
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Embedding generation failed

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- **Authentication**: 10 requests per minute
- **Content Creation**: 20 requests per hour
- **Memory Search**: 60 requests per minute
- **Content List**: 120 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 18
X-RateLimit-Reset: 1693226400
```

---

## Error Response Format

All errors follow a consistent format:

```json
{
    "error": "Detailed error message",
    "code": "ERROR_CODE",
    "details": {
        "field": ["Specific field error"]
    }
}
```

Common error codes:
- `INVALID_TOKEN`: Authentication token is invalid or expired
- `RATE_LIMITED`: Too many requests
- `INVALID_INPUT`: Request data validation failed
- `OPENAI_ERROR`: OpenAI API error
- `PAYMENT_REQUIRED`: Subscription or credits needed

---

## Testing

Use the provided test script:
```bash
python backend/test_api.py
```

Or test manually with curl:
```bash
# Get your token first
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' \
  | jq -r '.token')

# Create content
curl -X POST http://localhost:8000/api/content/create/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"text","prompt":"Write a joke about APIs"}'

# Search memories
curl -X POST http://localhost:8000/api/memory/search/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"joke","limit":5}'
```
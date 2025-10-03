# API Endpoints Reference

## 🎯 **Purpose**
Complete reference of all API endpoints in the Donkey Betz platform, their authentication requirements, and response formats.

---

## 🔐 **Authentication**

### **Token Endpoint**
```
POST /api/auth/token/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "jwt-token-here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John"
  }
}
```

### **Required Headers for Authenticated Requests**
```
Authorization: Bearer {token}
Content-Type: application/json
```

---

## 📡 **Agent Orchestra API**

### **Templates**
```
GET /api/agent-orchestra/templates/
Auth: Required
Response: List of agent templates

GET /api/agent-orchestra/templates/{id}/
Auth: Required
Response: Single template details
```

### **Orchestration**
```
POST /api/agent-orchestra/orchestration/execute/
Auth: Required
Body: {
  "template_id": "template-uuid",
  "inputs": {
    "query": "user query"
  }
}

GET /api/agent-orchestra/orchestration/{id}/
Auth: Required
Response: Orchestration status and results

POST /api/agent-orchestra/orchestration/{id}/cancel/
Auth: Required
Response: Cancellation confirmation
```

### **Agent Progress**
```
GET /api/agent-orchestra/agent-progress/{orchestration_id}/
Auth: Required
Response: Real-time agent execution progress
```

### **Stock Scout**
```
POST /api/agent-orchestra/stocks/scout/execute/
Auth: Required
Body: {
  "scout_type": "trending" | "value" | "growth",
  "sectors": ["technology", "healthcare"]
}

GET /api/agent-orchestra/stocks/scout/{orchestration_id}/results/
Auth: Required
Response: Stock opportunities found

GET /api/agent-orchestra/stocks/scout/missions/
Auth: Required
Response: User's scout mission history
```

### **Stock Analysis**
```
POST /api/agent-orchestra/stocks/analyze/
Auth: Required
Body: {
  "ticker": "AAPL",
  "analysis_type": "comprehensive" | "quick"
}

GET /api/agent-orchestra/stocks/analyses/
Auth: Required
Response: User's stock analyses

GET /api/agent-orchestra/stocks/analyses/{id}/
Auth: Required
Response: Detailed analysis results
```

### **Stock Opportunities**
```
GET /api/agent-orchestra/stocks/opportunities/
Auth: Required
Query: ?status=pending&scout_orchestration={id}
Response: List of stock opportunities

PATCH /api/agent-orchestra/stocks/opportunities/{id}/
Auth: Required
Body: {
  "user_rating": 1-5,
  "notes": "User notes"
}
```

---

## 💼 **Business Hub API**

### **Business Plans**
```
POST /api/core/business-plans/
Auth: Required
Body: {
  "reddit_idea_id": "uuid",
  "business_type": "saas" | "ecommerce" | "marketplace"
}

GET /api/core/business-plans/
Auth: Required
Response: User's business plans

GET /api/core/business-plans/{id}/
Auth: Required
Response: Detailed business plan

DELETE /api/core/business-plans/{id}/
Auth: Required
Response: 204 No Content
```

### **Reddit Ideas**
```
GET /api/core/reddit-ideas/
Auth: Required
Query: ?has_business_plan=false&min_score=100
Response: Reddit ideas list

POST /api/core/reddit-ideas/
Auth: Required
Body: {
  "title": "Idea title",
  "content": "Idea description",
  "source": "reddit"
}

PATCH /api/core/reddit-ideas/{id}/
Auth: Required
Body: {
  "user_rating": 1-5,
  "notes": "User notes"
}

DELETE /api/core/reddit-ideas/{id}/
Auth: Required
Response: 204 No Content
```

---

## 🧠 **Memory Palace API**

### **Conversations**
```
GET /api/ai-partner/conversations/
Auth: Required
Response: User's conversations

POST /api/ai-partner/conversations/
Auth: Required
Body: {
  "query": "User message",
  "context_ids": ["memory-id-1", "memory-id-2"]
}

GET /api/ai-partner/conversations/{id}/messages/
Auth: Required
Response: Conversation messages
```

### **Memories**
```
GET /api/ai-partner/memories/
Auth: Required
Query: ?search=keyword&category=business
Response: User's memories

POST /api/ai-partner/memories/
Auth: Required
Body: {
  "content": "Memory content",
  "category": "business" | "personal" | "research",
  "tags": ["tag1", "tag2"]
}

GET /api/ai-partner/memories/search/
Auth: Required
Query: ?q=search+query&semantic=true
Response: Search results with relevance scores
```

### **Documents**
```
POST /api/ai-partner/documents/upload/
Auth: Required
Content-Type: multipart/form-data
Body: file upload

GET /api/ai-partner/documents/
Auth: Required
Response: User's documents

DELETE /api/ai-partner/documents/{id}/
Auth: Required
Response: 204 No Content
```

---

## 🔬 **Research Intelligence API**

### **Research Queries**
```
POST /api/ai-partner/research/query/
Auth: Required
Body: {
  "query": "Research question",
  "sources": ["web", "memory", "academic"],
  "include_memory": true
}

GET /api/ai-partner/research/history/
Auth: Required
Response: Research query history
```

### **Knowledge Integration**
```
POST /api/ai-partner/research/save-to-memory/
Auth: Required
Body: {
  "research_id": "uuid",
  "selected_results": ["result-id-1", "result-id-2"]
}
```

---

## 🎨 **Content Studio API**

### **Image Generation**
```
POST /api/content/images/generate/
Auth: Required
Body: {
  "prompt": "Image description",
  "model": "dall-e-3" | "stable-diffusion",
  "size": "1024x1024"
}

GET /api/content/images/
Auth: Required
Response: User's generated images
```

### **Video Generation**
```
POST /api/content/videos/generate/
Auth: Required
Body: {
  "script": "Video script",
  "style": "professional" | "casual",
  "duration": 30
}

GET /api/content/videos/
Auth: Required
Response: User's generated videos
```

### **Content Items**
```
GET /api/content/items/
Auth: Required
Query: ?type=image&status=completed
Response: All content items

DELETE /api/content/items/{id}/
Auth: Required
Response: 204 No Content
```

---

## 🤖 **AI Assistant Hub API**

### **Agent Interactions**
```
POST /api/ai-partner/assistants/chat/
Auth: Required
Body: {
  "message": "User message",
  "agent_type": "financial" | "health" | "productivity",
  "session_id": "optional-session-id"
}

GET /api/ai-partner/assistants/sessions/
Auth: Required
Response: Chat sessions

GET /api/ai-partner/assistants/sessions/{id}/
Auth: Required
Response: Session messages
```

---

## 🏗️ **Universal Builder API**

### **Code Generation**
```
POST /api/universal-builder/generate/
Auth: Required
Body: {
  "description": "What to build",
  "framework": "react" | "django" | "flutter",
  "complexity": "simple" | "moderate" | "complex"
}

GET /api/universal-builder/projects/
Auth: Required
Response: Generated projects

GET /api/universal-builder/projects/{id}/files/
Auth: Required
Response: Project files and code
```

### **Deployment**
```
POST /api/universal-builder/deploy/
Auth: Required
Body: {
  "project_id": "uuid",
  "platform": "netlify" | "vercel" | "heroku"
}

GET /api/universal-builder/deployments/{id}/status/
Auth: Required
Response: Deployment status
```

---

## 🔄 **WebSocket Endpoints**

### **Agent Activity**
```
ws://localhost:8000/ws/agent-activity/{orchestration_id}/

Messages:
{
  "type": "agent_update",
  "agent_id": "uuid",
  "status": "executing" | "completed" | "failed",
  "progress": 0-100,
  "output": "Agent output text"
}
```

### **Real-time Notifications**
```
ws://localhost:8000/ws/notifications/

Messages:
{
  "type": "notification",
  "title": "Notification title",
  "message": "Notification message",
  "category": "success" | "error" | "info"
}
```

---

## 📊 **Response Formats**

### **Success Response**
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Optional success message"
}
```

### **Error Response**
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    // Additional error details
  }
}
```

### **Paginated Response**
```json
{
  "success": true,
  "data": {
    "results": [...],
    "count": 100,
    "next": "/api/endpoint/?page=2",
    "previous": null,
    "page_size": 20
  }
}
```

---

## 🚨 **Common Error Codes**

- `401` - Authentication required or invalid token
- `403` - Permission denied
- `404` - Resource not found
- `400` - Bad request / Validation error
- `429` - Rate limit exceeded
- `500` - Internal server error

---

## 🔑 **Environment Variables**

Required for API functionality:
```bash
# Backend
SECRET_KEY=django-secret-key
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
POLYGON_API_KEY=...
SERPER_API_KEY=...

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```
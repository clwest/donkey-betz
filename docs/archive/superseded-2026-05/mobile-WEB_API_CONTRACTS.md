# Web API Contracts for Mobile App

Extracted from `frontend/src/lib/api.ts`, `frontend/src/lib/apiClient.ts`, page components, and `frontend/src/stores/authStore.ts`. Verified against source code — not assumed.

---

## 1. HTTP Client Configuration

```
Base URL:       /api  (configurable via VITE_API_URL / EXPO_PUBLIC_API_BASE_URL)
Timeout:        90 seconds
Credentials:    withCredentials: true (cookies for session auth)
Content-Type:   application/json
```

### Required Headers

| Header | Value | When |
|--------|-------|------|
| `Content-Type` | `application/json` | All requests |
| `Authorization` | `Token <token>` | All authenticated requests |
| `X-UI-Scope` | `<scope>` | Optional — for request log filtering |

**IMPORTANT:** Auth token format is `Token <token>` (NOT `Bearer`). This is Django REST Framework TokenAuthentication.

---

## 2. Authentication

### Token Type
- **DRF TokenAuth** — stateful, stored in DB (`rest_framework.authtoken.models.Token`)
- **No JWT. No refresh token.** Token doesn't expire. Invalid token = re-login.
- On mobile: store in `expo-secure-store`

### Endpoints

#### POST `/api/v1/auth/login/`
```json
// Request
{ "username": "string", "password": "string" }

// Response 200
{
  "token": "string",
  "user": {
    "id": "string (UUID)",
    "username": "string",
    "email": "string",
    "credits": "number",
    "subscription": "string",
    "platform_role": "string"
  }
}

// Response 401
{ "detail": "Invalid credentials for user: {username}" }
```

#### POST `/api/v1/auth/login-enhanced/`
```json
// Request
{ "username": "string", "password": "string", "remember_me": true }

// Response 200
{
  "token": "string",
  "user": { /* same as above */ },
  "remember_me": true,
  "remember_token": "string",
  "expires_at": "ISO8601"
}
```

#### POST `/api/v1/auth/logout/`
```json
// Request: empty body
// Response 200
{ "detail": "Successfully logged out" }
```

#### GET `/api/v1/auth/user/`
```json
// Response 200
{
  "user": {
    "id": "string (UUID)",
    "username": "string",
    "email": "string",
    "credits": "number",
    "subscription": "string",
    "platform_role": "string"
  }
}
```

#### POST `/api/v1/auth/validate-token/`
```json
// Request
{ "token": "string" }

// Response 200
{ "valid": true, "user": { "id", "username", "email", "first_name", "last_name" } }
// or
{ "valid": false, "error": "Invalid token" }
```

#### POST `/api/v1/auth/register/`
```json
// Request
{
  "username": "string (min 3, alphanumeric + _-)",
  "email": "string",
  "password": "string (min 8, 1 digit, 1 uppercase)",
  "confirm_password": "string",
  "first_name": "string (optional)",
  "last_name": "string (optional)"
}

// Response 201 (DEBUG)
{ "message": "...", "token": "string", "user": { ... } }

// Response 201 (PRODUCTION — no token, must verify email)
{ "message": "Please check your email to verify your account.", "email": "string" }
```

#### POST `/api/v1/auth/change-password/`
```json
// Request (authed)
{ "old_password": "string", "new_password": "string" }

// Response 200
{ "message": "Password changed successfully", "token": "string (new token)" }
```

#### POST `/api/v1/auth/forgot-password/`
```json
{ "email": "string" }
// Always returns 200 (security: doesn't reveal if email exists)
```

#### POST `/api/v1/auth/reset-password/`
```json
{ "uid": "string", "token": "string", "new_password": "string", "confirm_password": "string" }
```

### Auth State (Zustand Store)
```typescript
interface AuthState {
  token: string | null
  user: { id: number; username: string; email: string; platform_role?: string } | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
}
```

### 401 Handling
- On auth endpoints (`/auth/`, `/login`): force logout + redirect to `/login`
- On other endpoints: log warning, let component handle

---

## 3. Manifest

### GET `/api/app/manifest/`
RBAC-filtered by user role. Admins see all routes; non-admins get admin routes stripped.

```json
{
  "build_sha": "string",
  "build_timestamp": "ISO8601",
  "env": "production",
  "route_count": 30,
  "routes": [
    {
      "path": "/boardroom",
      "label": "Boardroom",
      "authRequired": true,
      "category": "command",
      "roles": ["admin"]
    }
  ],
  "studios": {
    "image": { "enabled": true, "path": "/image-studio", "models": ["stability-ai", "dall-e-3", "replicate"], "endpoint": "/api/v1/gallery/" },
    "video": { "enabled": true, "path": "/video-studio", "models": ["runway-ml", "ffmpeg-edit"], "endpoint": "/api/v1/video/" },
    "audio": { "enabled": true, "path": "", "models": ["elevenlabs-tts"], "endpoint": "/api/v1/audio/" }
  },
  "capabilities": {
    "pa_chat": true,
    "websocket": true,
    "media_library": true,
    "resolve_node": true,
    "deliberation_pipeline": true,
    "initiative_pipeline": true,
    "spider_network": true,
    "body_systems": true
  },
  "api_dependencies": {
    "/boardroom": [
      { "method": "GET", "path": "/api/human/attention/", "toolSurface": "boardroom_tool.list_attention", "writes": false }
    ]
  },
  "user_role": "admin",
  "user_id": "UUID"
}
```

### Route Categories
`command` | `studio` | `intelligence` | `domain` | `reference` | `admin` | `auth`

---

## 4. PA Chat (Async Pattern)

### POST `/api/pa/chat/`
Dispatches async. Returns immediately with task_id.

```json
// Request
{
  "message": "string",
  "context": { "current_page": "/workspace" },
  "generate_audio": false,
  "conversation_id": "UUID (optional — threads into existing conversation)"
}

// Response 200
{
  "success": true,
  "task_id": "UUID",
  "status": "processing"
}
```

### GET `/api/pa/chat/status/{taskId}/`
Poll every 2 seconds until `status != 'processing'`.

```json
// Response (processing)
{ "success": true, "status": "processing" }

// Response (completed)
{
  "success": true,
  "status": "completed",
  "content": "string (markdown response)",
  "trace_id": "string",
  "tool_runs": [
    { "tool": "boardroom_tool", "ok": true, "latency_ms": 120, "error_code": null, "error_message": null }
  ],
  "audio_url": "string | null",
  "intent": "string | null",
  "routed_to": "string | null",
  "profile_completeness": 0.85,
  "latency_ms": 3200,
  "conversation_id": "UUID",
  "error": null
}

// Response (failed)
{ "success": true, "status": "failed", "error": "string" }
```

### Conversation Threading Pattern
1. First message: omit `conversation_id`
2. Server creates conversation, returns `conversation_id` in completion response
3. Subsequent messages: include `conversation_id` to thread

### GET `/api/pa/conversations/`
```json
{
  "success": true,
  "conversations": [
    {
      "conversation_id": "UUID",
      "title": "string",
      "message_count": 5,
      "last_message_at": "ISO8601",
      "preview": "string"
    }
  ],
  "total": 12
}
```

### GET `/api/pa/conversations/{conversationId}/`
```json
{
  "success": true,
  "conversation_id": "UUID",
  "title": "string",
  "messages": [
    {
      "id": "string",
      "role": "user | assistant",
      "content": "string",
      "timestamp": "ISO8601",
      "tools_used": ["boardroom_tool"]
    }
  ]
}
```

### POST `/api/pa/conversations/new/`
```json
// Request: empty body
// Response
{ "success": true, "conversation_id": "UUID" }
```

### Voice Endpoints

#### POST `/api/assistant/transcribe/` (FormData)
```
audio: Blob (recording.webm)
// Response: { "text": "string", "transcription": "string" }
```

#### POST `/api/assistant/voice/` (FormData)
```
audio: Blob (recording.webm)
// Response: { "user_text": "string", "assistant_message": { "response": "string", "tools_used": [] } }
```

#### POST `/api/tts/speak/`
```json
// Request
{ "text": "string", "voice_id": "string (optional)", "skip_summarize": false }

// Response
{ "success": true, "audio": "base64-encoded audio", "audio_format": "audio/mpeg" }
```

#### POST `/api/assistant/feedback/`
```json
{ "message_id": "string", "rating": "positive | negative", "comment": "string (optional)" }
```

---

## 5. Boardroom

### GET `/api/human/attention/`
```
Query params: ?limit=50&urgency=critical,high&status=pending
```

```json
{
  "items": [
    {
      "id": "string",
      "title": "string",
      "summary": "string",
      "item_type": "review | insight | alert | opportunity",
      "source_type": "assistant | spider | agent",
      "source_agent": "string",
      "urgency": "critical | high | medium | low",
      "status": "string",
      "created_at": "ISO8601",
      "ml_recommendation": "approve | ignore | uncertain",
      "ml_confidence": 0.85,
      "ml_prediction": {
        "prediction": "approve",
        "confidence": 0.85,
        "approval_probability": 0.92,
        "reasoning": "string",
        "similar_items": [{ "id": "string", "title": "string", "decision": "string", "similarity": 0.8 }],
        "predicted_at": "ISO8601"
      },
      "payload": {}
    }
  ],
  "last_visited_at": "ISO8601"
}
```

### GET `/api/human/attention/stats/`
```json
{
  "total_items": 42,
  "pending_count": 15,
  "by_urgency": { "critical": 2, "high": 8, "medium": 3, "low": 2 },
  "by_status": { "pending": 15, "reviewed": 20, "decided": 7 },
  "by_item_type": { "review": 5, "insight": 3, "alert": 4, "opportunity": 3 }
}
```

### GET `/api/human/attention/{itemId}/`
Returns full attention item (same shape as list item).

### POST `/api/human/attention/{itemId}/decide/`
```json
// Request
{ "decision": "approve | ignore | defer", "feedback": "string (optional)", "confidence": 0.9 }
```

### POST `/api/human/attention/bulk-decide/`
```json
// Request
{ "decision": "string", "item_ids": ["id1", "id2"] }
// Response
{ "success": true, "updated_count": 2 }
```

### POST `/api/human/attention/{itemId}/defer/`
```json
{ "remind_at": "ISO8601" }
```

### POST `/api/human/attention/{itemId}/verify/`
```json
{ "outcome": "profitable | loss | neutral", "profit": 150.0, "notes": "string" }
```

### POST `/api/human/attention/` (mark visited)
```json
// Request: empty body {}
// Used for tracking "NEW" badges
```

### GET `/api/boardroom/decisions/?limit=50`
```json
{
  "decisions": [
    {
      "id": "string",
      "topic": "string",
      "decision_type": "string",
      "decision_type_display": "string",
      "impact_area": "string",
      "impact_area_display": "string",
      "key_insights": ["string"],
      "recommended_stance": "string",
      "suggested_feature": "string",
      "status": "draft | approved | rejected | promoted",
      "created_at": "ISO8601",
      "participants": ["string"]
    }
  ]
}
```

### POST `/api/boardroom/decisions/{decisionId}/approve/`
Empty body. Returns `{ success, decision }`.

### POST `/api/boardroom/decisions/{decisionId}/reject/`
```json
{ "reason": "string (optional)" }
```

### POST `/api/boardroom/decisions/{decisionId}/promote/`
Empty body.

### POST `/api/boardroom/decisions/bulk-promote/`
```json
{ "decision_ids": ["id1", "id2"] }
```

### POST `/api/boardroom/decisions/bulk-reject/`
```json
{ "decision_ids": ["id1", "id2"] }
```

### GET `/api/boardroom/governance-stats/`
```json
{
  "total_decisions": 100,
  "draft_count": 20,
  "approved_count": 50,
  "rejected_count": 15,
  "promoted_count": 10,
  "pending_review_count": 5,
  "by_impact_area": {},
  "by_decision_type": {}
}
```

---

## 6. Governance

### GET `/api/platform/governance/`
```json
{
  "owner": {
    "username": "string",
    "email": "string",
    "override_level": "string",
    "contact": "string"
  },
  "emergency_controls": {
    "skin_lock": false,
    "skin_status": "locked | unlocked",
    "quarantined_agents": [],
    "quarantined_count": 0,
    "system_paused": false,
    "pending_critical_decisions": 3
  },
  "pending_decisions": [
    { "id": "string", "title": "string", "summary": "string", "urgency": "string", "item_type": "string", "source_type": "string", "source_agent": "string", "created_at": "ISO8601", "ml_recommendation": "string" }
  ],
  "pending_decisions_count": 3,
  "authority_escalation_path": [
    { "level": 1, "entity": "string", "scope": "string" }
  ]
}
```

### POST `/api/platform/emergency-halt/`
```json
// Empty body
// Response: { "success": true, "message": "string", "attention_item_id": "string" }
```

### POST `/api/platform/skin-lock/`
```json
// Request
{ "action": "lock | unlock | toggle" }
// Response
{ "success": true, "locked": true, "status": "locked", "message": "string" }
```

### GET `/api/artifacts/needs-classification/?limit=50`
```json
{
  "artifacts": [
    {
      "id": "string",
      "type": "string",
      "type_display": "string",
      "title": "string",
      "description": "string",
      "source_agent": "string",
      "composite_score": 0.75,
      "classified": false,
      "classification": {},
      "extracted_at": "ISO8601"
    }
  ]
}
```

### POST `/api/artifacts/{artifactId}/classify/`
```json
// Request
{
  "what_is_this": "research_finding | actionable_recommendation | scope_change | risk_flag | informational",
  "who_is_it_for": "platform | end_users | founder | agents | public",
  "data_allowed": "public_only | internal_ops | api_data | user_data | all",
  "phase_approved": "research | prototype | pilot | production | none",
  "auto_approve": false
}

// Response
{ "success": true, "artifact": { "id": "string", "classified": true, "classification": {}, "auto_approved": false } }
```

### GET `/api/platform/remediation/status/`
```json
{
  "findings": { "total": 20, "by_status": {}, "by_priority": {} },
  "remediation_tasks": { "total": 15, "by_status": {} },
  "progress": { "completed": 10, "total": 15, "percentage": 66.7 }
}
```

### GET `/api/self-healing/progress/`
```json
{
  "total_tasks": 50,
  "completed_tasks": 40,
  "in_progress_tasks": 5,
  "pending_tasks": 3,
  "failed_tasks": 2,
  "completion_percentage": 80.0,
  "by_agent": {},
  "last_updated": "ISO8601"
}
```

### POST `/api/platform/actions/run-remediation/`
```json
{ "agent": "string (optional)", "limit": 20, "write_files": false }
```

### POST `/api/platform/actions/run-self-audit/`
Empty body.

---

## 7. Dashboard / Home

### GET `/api/home/boot/`
```json
{
  "greeting": { "user_name": "string", "time_of_day": "morning | afternoon | evening" },
  "while_away": {
    "spider_findings": 15,
    "high_score_dreams": 3,
    "initiatives_progressed": 2,
    "pending_decisions": 8,
    "hours_since_visit": 12.5,
    "intelligence_desks_ready": 4
  },
  "quick_stats": { "agents_active": 218, "system_health": "healthy | degraded" }
}
```

### GET `/api/body/vitals/`
System health metrics. Response varies.

### GET `/api/human/control/`
Control panel state (quiet mode, review mode, thresholds).

### GET `/api/orchestration/workflows/`
Active orchestration workflows.

### GET `/api/home/intelligence-desks/`
Intelligence desk statuses.

### POST `/api/home/trigger-desks/`
Trigger intelligence desk refresh.

---

## 8. RBAC Behavior

The web app does **NOT** enforce RBAC client-side. All mutation buttons render unconditionally. Permission enforcement is server-side only (returns 401/403).

For mobile, recommended approach:
- Use manifest `roles` field + `user_role` from auth to **hide** mutation buttons
- Server enforcement remains mandatory as fallback
- Admin routes: only show if `user_role === 'admin'`

---

## 9. Polling / Refresh Patterns

| Data | Interval | Pattern |
|------|----------|---------|
| Attention items | 30s | `refetchInterval: 30000` |
| Decisions | 30s | `refetchInterval: 30000` |
| Governance data | 12s | `refetchInterval: 12000` (pauseable) |
| Self-healing progress | 12s | `refetchInterval: 12000` (pauseable) |
| Remediation status | 30s | `refetchInterval: 30000` |
| PA chat status | 2s | Manual polling until completed/failed |

All mutations invalidate relevant react-query cache keys.

---

## 10. Error Response Shapes

```json
// Auth errors
{ "detail": "string" }

// Validation errors
{ "errors": { "field_name": "error message" } }

// Generic errors
{ "error": "string" }

// Success with optional error
{ "success": false, "error": "string" }
```

---

## Source Files

| File | What it provides |
|------|-----------------|
| `frontend/src/lib/api.ts` | All endpoint definitions (~3500 lines) |
| `frontend/src/lib/apiClient.ts` | Scoped request helpers, X-UI-Scope |
| `frontend/src/stores/authStore.ts` | Auth state shape (Zustand) |
| `frontend/src/appManifest.ts` | Route definitions, studio config, capabilities, API deps |
| `frontend/src/pages/CommandCenterPage.tsx` | PA chat polling pattern |
| `frontend/src/pages/BoardroomPage.tsx` | Boardroom API usage |
| `frontend/src/pages/GovernancePage.tsx` | Governance API usage |
| `core/auth_views.py` | Backend auth endpoints |
| `core/auth_views_enhanced.py` | Enhanced auth (remember me) |

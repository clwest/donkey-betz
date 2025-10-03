# Content Studio Authentication Fix

## Issues Found:

1. **Incorrect API endpoint path**: Frontend is using `/api/content-pipeline/pipelines/` but backend expects `/api/pipeline/pipelines/`
2. **Missing authentication token**: The frontend is not sending the authentication token with requests to `/api/content/ai-pipeline/available_content/`

## Solutions:

### 1. Frontend API Path Fix
The frontend needs to update its API calls from:
- `/api/content-pipeline/pipelines/` → `/api/pipeline/pipelines/`

### 2. Authentication Token Fix
The frontend needs to include the authentication token in all API requests. The token should be sent as:
```
Authorization: Token <token_value>
```

## Backend URLs:
- Pipeline endpoints: `/api/pipeline/` (from content_pipeline app)
- AI Pipeline endpoints: `/api/content/ai-pipeline/` (from content app)
- Both require authentication via Token header

## Testing:
Your authentication token is: `73d9b35d53b95e79de1537fc03b889ba37ad1c70`

Test with curl:
```bash
# Test pipeline endpoint
curl -H "Authorization: Token 73d9b35d53b95e79de1537fc03b889ba37ad1c70" \
     http://localhost:8000/api/pipeline/pipelines/

# Test AI pipeline available content
curl -H "Authorization: Token 73d9b35d53b95e79de1537fc03b889ba37ad1c70" \
     http://localhost:8000/api/content/ai-pipeline/available_content/
```

## Frontend Fix Required:
1. Update API service to use correct pipeline URL
2. Ensure authentication token is included in all requests
3. Check that the token is being stored and retrieved correctly from localStorage/sessionStorage
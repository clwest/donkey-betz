# Frontend Fixes Needed for donkey-betz-frontend

## API Path Updates Required

In the `donkey-betz-frontend` repository, you need to update the following:

### 1. Pipeline API Path
Change all occurrences of:
```javascript
/api/content-pipeline/
```
To:
```javascript
/api/pipeline/
```

### 2. Files to Check
Look for these API calls in:
- API service files (e.g., `src/services/pipelineService.js` or similar)
- Store files (e.g., `src/stores/pipelineStore.js` if using Pinia/Vuex)
- Component files that make direct API calls
- Any configuration files that define API endpoints

### 3. Authentication Token
Ensure all API calls include the authentication token:

```javascript
// Example with fetch
fetch('/api/pipeline/pipelines/', {
  headers: {
    'Authorization': `Token ${localStorage.getItem('authToken')}`,
    'Content-Type': 'application/json'
  }
})

// Example with axios
axios.get('/api/pipeline/pipelines/', {
  headers: {
    'Authorization': `Token ${localStorage.getItem('authToken')}`
  }
})
```

### 4. Specific Endpoints to Update

| Old Endpoint | New Endpoint |
|--------------|--------------|
| `/api/content-pipeline/pipelines/` | `/api/pipeline/pipelines/` |
| `/api/content-pipeline/stages/` | `/api/pipeline/stages/` |
| `/api/content-pipeline/templates/` | `/api/pipeline/templates/` |

### 5. AI Pipeline Endpoints (these are correct but need auth)
- `/api/content/ai-pipeline/available_content/` - Requires authentication token
- `/api/content/ai-pipeline/generate_for_pipeline/` - Requires authentication token
- `/api/content/ai-pipeline/link_to_pipeline/` - Requires authentication token

## Search Commands for Frontend Repo

Run these in the `donkey-betz-frontend` directory:

```bash
# Find all files with content-pipeline
grep -r "content-pipeline" src/ --include="*.js" --include="*.ts" --include="*.vue" --include="*.jsx" --include="*.tsx"

# Find API service files
find src -name "*api*" -o -name "*service*" | grep -E "\.(js|ts|vue)$"

# Check for pipeline-related files
find src -name "*pipeline*" | grep -E "\.(js|ts|vue|jsx|tsx)$"
```

## Testing After Fix

1. Clear browser cache and local storage
2. Log in again to get a fresh token
3. Open browser DevTools Network tab
4. Navigate to Content Studio
5. Verify all API calls return 200/201 status codes
6. Check that the Authorization header is present in requests
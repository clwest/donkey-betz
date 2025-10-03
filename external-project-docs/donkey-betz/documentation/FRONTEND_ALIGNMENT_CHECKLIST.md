# Frontend Alignment Checklist - Session 93

## Pre-Flight Checks

### Backend Status
- [ ] Redis server running (`redis-server --daemonize yes`)
- [ ] Django server running (`python manage.py runserver`)
- [ ] All migrations applied (`python manage.py migrate`)
- [ ] Static files collected (`python manage.py collectstatic`)

### Frontend Setup
- [ ] Dependencies installed (`cd donkey-betz-frontend && npm install`)
- [ ] Environment variables configured (`.env` file)
- [ ] API base URL points to backend (`http://localhost:8000`)

## API Endpoint Updates

### 1. Remove Deprecated Endpoints ❌

#### In `src/services/api.js` or `src/config/api.config.js`:
```javascript
// REMOVE these test/debug endpoints:
- /api/ai-partner/test-emotional/
- /api/ai-partner/test-cors-upload/  
- /api/ai-partner/debug-auth/
```

#### In components using test endpoints:
- [ ] Search for `test-emotional` - Remove or update
- [ ] Search for `test-cors-upload` - Remove or update
- [ ] Search for `debug-auth` - Remove or update

### 2. Update Service Endpoints ✅

#### Memory Service Updates
```javascript
// OLD endpoints (multiple services):
/api/memory/enhanced/
/api/memory/reliable/
/api/memory/ukf/
/api/memory/optimized/

// NEW unified endpoint:
/api/memory/unified/
```

- [ ] Update `memoryService.js`
- [ ] Update memory-related Redux actions
- [ ] Update MemoryPalace component

#### Agent Execution Updates
```javascript
// OLD endpoints (multiple executors):
/api/agent/sync-executor/
/api/agent/fast-executor/
/api/agent/business-executor/

// NEW unified endpoint:
/api/agent/execute/
```

- [ ] Update `agentService.js`
- [ ] Update agent deployment actions
- [ ] Update AgentOrchestra component

#### Cache Service Updates
```javascript
// OLD endpoints (multiple cache services):
/api/cache/manager/
/api/cache/response/
/api/cache/weather/

// NEW unified endpoint:
/api/cache/
```

- [ ] Update cache-related API calls
- [ ] Update cache utility functions

## Component Updates

### 3. Main Chat Interface
**File**: `src/components/ChatInterface/ChatInterface.jsx`

- [ ] Verify chat messages send correctly
- [ ] Check message history loads
- [ ] Verify suggestions API works
- [ ] Test file upload functionality
- [ ] Check real-time updates (WebSocket)

### 4. Agent Orchestra
**File**: `src/components/AgentOrchestra/AgentOrchestra.jsx`

- [ ] Agent list loads correctly
- [ ] Deployment modal works
- [ ] Status updates display
- [ ] Progress bars update
- [ ] Results display properly

### 5. Memory Palace
**File**: `src/components/MemoryPalace/MemoryPalace.jsx`

- [ ] Memory search works
- [ ] Memory entries display
- [ ] Filtering functions
- [ ] Memory creation works
- [ ] Memory deletion works

### 6. Content Creator
**File**: `src/components/ContentCreator/ContentCreator.jsx`

- [ ] Project creation works
- [ ] Pipeline stages display
- [ ] Asset generation works
- [ ] Progress tracking works
- [ ] Export functionality works

## Redux Store Updates

### 7. Update Action Creators
**Directory**: `src/store/slices/`

#### agentSlice.js
- [ ] Update `deployAgent` action
- [ ] Update `getAgentStatus` action
- [ ] Update `cancelAgent` action

#### memorySlice.js
- [ ] Update `searchMemories` action
- [ ] Update `createMemory` action
- [ ] Update `deleteMemory` action

#### chatSlice.js
- [ ] Update `sendMessage` action
- [ ] Update `loadHistory` action
- [ ] Update `getSuggestions` action

## Service Layer Updates

### 8. API Service Files
**Directory**: `src/services/`

#### api.js (Base Configuration)
```javascript
// Update base endpoints
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const endpoints = {
  // Update to unified services
  memory: '/api/memory/unified/',
  agent: '/api/agent/execute/',
  cache: '/api/cache/',
  chat: '/api/ai-partner/chat/',
};
```

- [ ] Update base configuration
- [ ] Update endpoint mappings
- [ ] Update error handling
- [ ] Update auth headers

#### agentService.js
- [ ] Update deployment endpoint
- [ ] Update status checking
- [ ] Update result fetching

#### memoryService.js
- [ ] Update CRUD operations
- [ ] Update search endpoint
- [ ] Update embedding endpoint

## Testing Checklist

### 9. Functional Testing

#### Authentication Flow
- [ ] User can register
- [ ] User can login
- [ ] JWT tokens work
- [ ] Logout works
- [ ] Password reset works

#### Main Features
- [ ] Chat interface responsive
- [ ] Agent deployment succeeds
- [ ] Memory search returns results
- [ ] Content creation pipeline works
- [ ] File uploads work

#### Error Handling
- [ ] 404 errors handled gracefully
- [ ] Network errors show messages
- [ ] Loading states display
- [ ] Error boundaries catch crashes

### 10. Console & Network Testing

#### Browser Console
- [ ] No red errors in console
- [ ] No deprecated API warnings
- [ ] No missing dependencies
- [ ] No CORS errors

#### Network Tab
- [ ] All API calls return 200/201
- [ ] No 404 responses
- [ ] No 500 errors
- [ ] Response times < 1s

## Performance Checks

### 11. Load Time Metrics
- [ ] Initial page load < 3s
- [ ] API responses < 500ms
- [ ] No memory leaks
- [ ] Bundle size reasonable

### 12. User Experience
- [ ] All buttons clickable
- [ ] Forms validate properly
- [ ] Modals open/close
- [ ] Animations smooth
- [ ] Mobile responsive

## Final Verification

### 13. End-to-End Test Flow

1. **Login Flow**
   - [ ] Navigate to login
   - [ ] Enter credentials
   - [ ] Successfully authenticate
   - [ ] Redirect to dashboard

2. **Chat Flow**
   - [ ] Send message
   - [ ] Receive response
   - [ ] View history
   - [ ] Clear conversation

3. **Agent Flow**
   - [ ] View available agents
   - [ ] Deploy an agent
   - [ ] Monitor progress
   - [ ] View results

4. **Memory Flow**
   - [ ] Search memories
   - [ ] Create new memory
   - [ ] Edit memory
   - [ ] Delete memory

5. **Content Flow**
   - [ ] Create project
   - [ ] Add stages
   - [ ] Generate content
   - [ ] Export results

## Rollback Plan

If issues arise:

1. **Backend Rollback**
   ```bash
   git stash  # Save current changes
   git checkout main
   git reset --hard HEAD~2  # Go back 2 commits
   ```

2. **Frontend Rollback**
   ```bash
   git stash
   git checkout main
   git reset --hard HEAD~1
   ```

3. **Quick Fixes**
   - Restore deprecated endpoints temporarily
   - Add redirect rules in nginx/Apache
   - Use API gateway for translation

## Sign-Off

### Completion Criteria
- [ ] All checklist items completed
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] User experience unchanged
- [ ] Documentation updated

### Approval
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing complete
- [ ] Ready for deployment

---

**Note**: This checklist should be completed in order. Each section builds on the previous one. If any critical issues are found, stop and fix before proceeding.
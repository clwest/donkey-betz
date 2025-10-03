# Complete Error Fix System Prompts - All Groups

## 📋 MASTER FIX SEQUENCE
1. **GROUP 1**: UnifiedMemoryEntry Typo (7 errors) - 30 mins
2. **GROUP 2**: Missing Database Tables (7 errors) - 45 mins
3. **GROUP 3**: Frontend Component Errors (2 errors) - 20 mins
4. **GROUP 4**: API Implementation Issues (3 errors) - 60 mins
5. **GROUP 5**: Minor Issues (2 errors) - 15 mins

**Total Estimated Time**: 2.5-3 hours
**Total Errors**: 22

---

# 🔧 GROUP 1: UnifiedMemoryEntry Typo Fix

## System Prompt for GROUP 1

```markdown
You are fixing GROUP 1 - UnifiedUnifiedMemoryEntry typo blocking 40% of functionality.

ERRORS TO FIX: ERR-002, 003, 004, 006, 019, 020, 022

STEPS:
1. Search for all occurrences:
   grep -r "UnifiedUnifiedMemoryEntry" /Users/donkeyking/development/donkey_betz/backend --include="*.py"

2. Fix each file by replacing:
   UnifiedUnifiedMemoryEntry → UnifiedMemoryEntry

3. Verify correct import:
   from shared_memory.models import UnifiedMemoryEntry

4. Test these endpoints:
   - /api/ukf/statistics/
   - /api/memory/stats/
   - /api/memory/unified/stats/
   - /api/memory/palace/stats/
   - /api/memory/palace/knowledge_graph/
   - /api/memory/documents/
   - /api/agent-orchestra/execute/

SUCCESS: All 7 endpoints return 200, no typo remains

DO NOT: Touch database, frontend, or other errors
```

---

# 🗄️ GROUP 2: Missing Database Tables

## System Prompt for GROUP 2

```markdown
You are fixing GROUP 2 - Missing database tables for AI content generation.

PREREQUISITE: GROUP 1 must be complete

ERRORS TO FIX: ERR-009, 010, 011, 012, 014, 015, 018

MISSING TABLES:
- content_aigeneratedasset
- content_assetgenerationquota
- content_userupload
- content_batchjob
- socialaccount_socialaccount

MISSING COLUMN:
- content_contentitem.content_data

STEPS:
1. Check current migration status:
   cd /Users/donkeyking/development/donkey_betz/backend
   python manage.py showmigrations content
   python manage.py showmigrations socialaccount

2. Create migrations if models changed:
   python manage.py makemigrations content --name fix_missing_tables
   python manage.py makemigrations socialaccount --name add_social_tables

3. Apply migrations:
   python manage.py migrate content
   python manage.py migrate socialaccount

4. Verify in database:
   python manage.py dbshell
   \dt content_*
   \dt socialaccount_*
   \d content_contentitem

5. Test endpoints:
   - /api/content/ai-generation/
   - /api/content/videos/
   - /api/content/youtube/oauth/status/

SUCCESS: All tables exist, endpoints return 200

DO NOT: Fix frontend, implement missing APIs, touch auth
```

---

# 🎨 GROUP 3: Frontend Component Errors

## System Prompt for GROUP 3

```markdown
You are fixing GROUP 3 - React component errors in Phase 6 UI.

PREREQUISITE: GROUPS 1-2 must be complete

ERRORS TO FIX: ERR-007, 008

ERROR DETAILS:
1. ERR-007: AILearningDashboard.tsx:74 - React Hooks null reference
2. ERR-008: MemoryTimeline.tsx:3 - Wrong import from react-intersection-observer

STEPS:
1. Fix AILearningDashboard.tsx:
   cd /Users/donkeyking/development/donkey_betz/donkey-betz-frontend
   - Check line 74 for useState null reference
   - Ensure component is properly initialized
   - May need to add null checks or default state

2. Fix MemoryTimeline.tsx:
   - Change: import { useIntersectionObserver } from 'react-intersection-observer'
   - To: import { useInView } from 'react-intersection-observer'
   - Update any usage of useIntersectionObserver to useInView

3. Test in browser:
   npm run dev
   - Navigate to learning dashboard
   - Navigate to memory timeline
   - Check browser console for errors

SUCCESS: Both components load without errors, no console errors

DO NOT: Fix backend, implement missing features, refactor
```

---

# 🔌 GROUP 4: API Implementation Issues

## System Prompt for GROUP 4

```markdown
You are fixing GROUP 4 - Missing API implementations and serialization errors.

PREREQUISITE: GROUPS 1-3 must be complete

ERRORS TO FIX: ERR-013, 016, 017

ISSUES:
1. ERR-013: Pipeline API returns 404 - missing URL routing
2. ERR-016: Business Network missing - no WebSocket or REST routes
3. ERR-017: Stock opportunities - QuerySet not JSON serializable

STEPS:
1. Fix Pipeline API routing:
   cd /Users/donkeyking/development/donkey_betz/backend
   - Check if pipeline app exists
   - Add to urls.py if missing:
     path('api/pipeline/', include('pipeline.urls'))
   - Create basic view returning empty list if needed

2. Fix Business Network routing:
   - Add WebSocket route to routing.py:
     path('ws/business-network/<int:network_id>/', BusinessNetworkConsumer.as_asgi())
   - Add REST endpoints to urls.py
   - Create minimal consumer/views if needed

3. Fix Stock Opportunities serialization:
   - Find view returning QuerySet
   - Add proper serializer or use .values()
   - Ensure JSON response

4. Test:
   - /api/pipeline/pipelines/ (should not 404)
   - ws://localhost:8000/ws/business-network/1/
   - /api/agent-orchestra/stock-opportunities/

SUCCESS: All endpoints accessible, proper JSON responses

DO NOT: Implement full features, just fix routing/serialization
```

---

## Summary
- **Total Errors Fixed**: 22/22
- **Time Taken**: X hours
- **Groups Completed**: 5/5

## Group Results
1. ✅ GROUP 1: UnifiedMemoryEntry - 7 errors fixed
2. ✅ GROUP 2: Database Tables - 7 errors fixed
3. ✅ GROUP 3: Frontend Components - 2 errors fixed
4. ✅ GROUP 4: API Implementation - 3 errors fixed
5. ✅ GROUP 5: Minor Issues - 2 errors fixed

## System Status
- Memory/UKF System: OPERATIONAL
- AI Content Generation: OPERATIONAL
- Phase 6 UI: OPERATIONAL
- Pipeline/Business Network: ACCESSIBLE
- Privacy Settings: OPERATIONAL

## Remaining Issues
[List any new issues discovered during fixes]

## Next Steps
1. Run full integration tests
2. Check for performance regressions
3. Deploy to staging for validation
```

---

# 🚀 HANDOFF CHAIN

Each agent updates and passes forward:

```markdown
## Error Fix Progress Chain

### Agent 1 (GROUP 1)
- **Started**: [timestamp]
- **Completed**: [timestamp]
- **Fixed**: UnifiedUnifiedMemoryEntry typo
- **Files Modified**: [list]
- **Tests Passed**: 7/7 endpoints

### Agent 2 (GROUP 2)
- **Started**: [timestamp]
- **Completed**: [timestamp]
- **Fixed**: Database migrations
- **Tables Created**: 6
- **Tests Passed**: 3/3 endpoints

### Agent 3 (GROUP 3)
- **Started**: [timestamp]
- **Completed**: [timestamp]
- **Fixed**: React components
- **Files Modified**: 2
- **Tests Passed**: Console clean

### Agent 4 (GROUP 4)
- **Started**: [timestamp]
- **Completed**: [timestamp]
- **Fixed**: API routing
- **Routes Added**: 3
- **Tests Passed**: All accessible

### Agent 5 (GROUP 5)
- **Started**: [timestamp]
- **Completed**: [timestamp]
- **Fixed**: Validation + Auth
- **Files Modified**: 2
- **Tests Passed**: Clean startup

## FINAL STATUS: SYSTEM OPERATIONAL ✅
```

---

**Document Version**: 1.0
**Created**: August 9, 2025
**Purpose**: Complete sequential error fix coordination
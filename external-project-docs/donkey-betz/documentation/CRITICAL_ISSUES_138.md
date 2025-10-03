# CRITICAL SYSTEM ERRORS - Session 138

**Date Identified**: August 12, 2025  
**Severity**: 🔴 CRITICAL - Core Services Failing  
**Source**: External Agent Review

## Error Priority Matrix

| Priority | Error | Impact | Services Affected | Fix Complexity |
|----------|-------|--------|------------------|----------------|
| 1 | Async Context Conflicts | HIGH | Stock data, Pattern stats, Memory search, Feedback | MEDIUM |
| 2 | WebSocket Route Missing | HIGH | Real-time collab, Business network, Agent updates | LOW |
| 3 | Timezone Attribute | MEDIUM | Stock services, Scheduled tasks | LOW |
| 4 | Feedback Threading | MEDIUM | User feedback, Agent learning | MEDIUM |
| 5 | Response Type Mismatch | LOW | Response formatting | LOW |

## Detailed Error Analysis

### 1. Async Context Execution Errors 🔴

**Error Messages**:
```
Cannot run the event loop while another loop is running
You cannot call this from an async context - use a thread or sync_to_async
```

**Root Cause Analysis**:
- Attempting to use `asyncio.run()` inside an already running async context
- Missing `sync_to_async` decorators on synchronous database operations
- Nested event loop creation

**Affected Code Patterns**:
```python
# WRONG - This causes the error
async def some_async_function():
    result = asyncio.run(another_async_function())  # ❌

# CORRECT - Proper async handling
async def some_async_function():
    result = await another_async_function()  # ✅
```

**Files to Check**:
- `agent_orchestra/services/quick_stock_data_service.py`
- `ai_partner/services/pattern_statistics.py`
- `ai_partner/services/response_validator.py`
- `shared_memory/services.py`
- `ai_partner/services/feedback_collector.py`

### 2. WebSocket Routing Configuration Error 🔴

**Error Message**:
```
ValueError: No route found for path 'ws/business-network/e7b35888/'
```

**Root Cause**:
Missing WebSocket route definition in routing configuration

**Fix Required**:
```python
# In agent_orchestra/routing.py or server/routing.py
from business_network.consumers import BusinessNetworkConsumer

websocket_urlpatterns = [
    # ... existing patterns ...
    path('ws/business-network/<str:network_id>/', BusinessNetworkConsumer.as_asgi()),
]
```

### 3. Timezone Attribute Error 🟡

**Error Message**:
```
module 'django.utils.timezone' has no attribute 'utc'
```

**Root Cause**:
Django API change or incorrect import

**Fix Options**:
```python
# Option 1: Use datetime timezone
from datetime import timezone as dt_timezone
utc = dt_timezone.utc

# Option 2: Use pytz
import pytz
utc = pytz.UTC

# Option 3: Use Django's current timezone
from django.utils import timezone
utc = timezone.get_current_timezone()
```

### 4. Feedback Submission Threading Error 🟡

**Error Message**:
```
You cannot submit onto CurrentThreadExecutor from its own thread
```

**Root Cause**:
Attempting to submit work to an executor from within that executor's thread

**Fix Strategy**:
```python
# Replace CurrentThreadExecutor with ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

# Or use sync_to_async properly
from asgiref.sync import sync_to_async

@sync_to_async
def sync_operation():
    # Database operations here
    pass
```

### 5. Response Validation Type Error 🟢

**Error Message**:
```
can only concatenate str (not "list") to str
```

**Root Cause**:
Type mismatch in string concatenation

**Fix Pattern**:
```python
# Add type checking
if isinstance(value, list):
    formatted_value = ', '.join(str(v) for v in value)
else:
    formatted_value = str(value)
```

## Investigation Commands

```bash
# Find all timezone.utc usage
grep -r "timezone.utc" backend/

# Find async context issues
grep -r "asyncio.run" backend/
grep -r "CurrentThreadExecutor" backend/

# Check WebSocket routing
grep -r "websocket_urlpatterns" backend/
grep -r "business-network" backend/

# Find string concatenation issues
grep -r "can only concatenate" backend/*.log
```

## Testing After Fixes

```bash
# Test async operations
python manage.py test agent_orchestra.tests.test_async

# Test WebSocket connections
python manage.py test business_network.tests.test_websocket

# Test feedback system
python manage.py test ai_partner.tests.test_feedback

# Run integration tests
python manage.py test --tag=integration
```

## Impact on User Experience

### Currently Broken:
- ❌ Real-time stock updates
- ❌ Business network collaboration
- ❌ Agent learning from feedback
- ❌ Live agent status updates
- ❌ Pattern analysis features

### Still Working:
- ✅ ChatGPT import
- ✅ Basic agent deployment
- ✅ Database operations (sync)
- ✅ Authentication
- ✅ Static content serving

## Recovery Plan

1. **Immediate** (30 min):
   - Fix WebSocket routing
   - Fix timezone references

2. **Short-term** (1 hour):
   - Fix async context conflicts in critical paths
   - Fix response type validation

3. **Medium-term** (2 hours):
   - Fix feedback threading
   - Comprehensive testing
   - Deploy fixes

## Monitoring After Fix

```python
# Add logging to track async issues
import logging
logger = logging.getLogger(__name__)

async def monitored_async_function():
    logger.info(f"Event loop running: {asyncio.get_running_loop()}")
    # ... rest of function
```

## Prevention Strategies

1. **Async Best Practices**:
   - Never use `asyncio.run()` inside async functions
   - Always use `await` for async calls
   - Use `sync_to_async` for database operations

2. **WebSocket Routes**:
   - Document all WebSocket paths
   - Add route tests for each consumer

3. **Type Safety**:
   - Add type hints
   - Validate types before operations
   - Use proper serializers

4. **Testing**:
   - Add async context tests
   - Test WebSocket connections
   - Mock timezone operations
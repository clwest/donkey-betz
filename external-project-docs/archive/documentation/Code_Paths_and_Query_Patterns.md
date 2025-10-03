# Code Paths and Query Patterns Reference

## Critical Code Paths

### 1. AI Assistant Conversation Flow
```
User Input → WebSocket → Django Channels → AI Service → Response

Detailed Path:
1. Frontend: donkey-betz-frontend/src/features/ai-assistant/components/ChatInterface.tsx
   ↓ WebSocket message
2. Backend: backend/ai_partner/consumers.py::ChatConsumer.receive()
   ↓ Process message
3. Service: backend/ai_partner/services/conversation_service.py::process_message()
   ↓ Build context
4. Memory: backend/ukf_system/services/unified_memory_search.py::search()
   ↓ Retrieve relevant memories
5. AI: backend/ai_services/enhanced_ai_service.py::generate_response()
   ↓ Get AI response
6. Return: WebSocket → Frontend update
```

### 2. Agent Orchestra Execution Flow
```
User Request → API → Orchestration → Agent Selection → Execution → Response

Detailed Path:
1. API: backend/agent_orchestra/api.py → /api/agent-orchestra/deploy/
   ↓ POST request
2. Orchestration: backend/agent_orchestra/services/orchestration_service.py::create_orchestration()
   ↓ Parse request
3. Selection: backend/agent_orchestra/services/agent_selector.py::select_agent()
   ↓ Choose agent
4. Factory: backend/agent_orchestra/services/agent_factory.py::create_agent()
   ↓ Instantiate
5. Execution: backend/agent_orchestra/services/enhanced_sync_executor.py::execute()
   ↓ Run agent
6. Tools: backend/agent_orchestra/services/tool_service.py::execute_tool()
   ↓ Call external APIs
7. Progress: backend/agent_orchestra/consumers.py → WebSocket updates
```

### 3. Memory Creation and Retrieval
```
Conversation → Memory Extraction → Embedding → Storage → Search

Detailed Path:
1. Trigger: backend/ai_partner/signals.py → post_save on Message
   ↓ Signal
2. Extract: backend/memory/services/conversation_memory_service.py::create_from_message()
   ↓ Process content
3. Embed: backend/memory/services/embedding_service.py::generate_embedding()
   ↓ Create vector
4. Store: backend/memory/models/memory.py::ConversationMemory.save()
   ↓ Database + pgvector
5. Search: backend/ukf_system/services/unified_memory_search.py::vector_search()
   ↓ Similarity search
6. API: backend/api/ukf_memory/views/memory_views.py::search()
```

## Essential Query Patterns

### Finding Entry Points
```bash
# Find all API endpoints
grep -r "@api_view\|APIView\|ViewSet" backend/ --include="*.py" | grep -v test

# Find WebSocket consumers
find backend -name "consumers.py" -exec grep -l "WebsocketConsumer\|AsyncWebsocketConsumer" {} \;

# Find Celery tasks
grep -r "@shared_task\|@app.task" backend/ --include="*.py"

# Find Django signals
grep -r "post_save\|pre_save\|Signal" backend/ --include="*.py" | grep -v migrations
```

### Tracing Data Flow
```bash
# Follow a model through the system
MODEL_NAME="ConversationMemory"
grep -r "$MODEL_NAME" backend/ --include="*.py" | grep -v migrations | sort

# Find all serializers for a model
grep -r "class.*Serializer.*$MODEL_NAME" backend/ --include="*.py"

# Track a service method usage
METHOD="process_message"
grep -r "\\.$METHOD\\|$METHOD(" backend/ --include="*.py"
```

### Debugging Specific Issues
```bash
# Find error handling
grep -r "try:\|except\|raise" backend/ai_partner/ --include="*.py" -A 2 -B 2

# Find TODOs and FIXMEs
grep -r "TODO\|FIXME\|HACK\|XXX" backend/ --include="*.py"

# Find hardcoded values
grep -r "'http\|\"http\|localhost\|127.0.0.1" backend/ --include="*.py" | grep -v test

# Find potential security issues
grep -r "password\|secret\|token\|api_key" backend/ --include="*.py" | grep -v test
```

### Performance Investigation
```bash
# Find database queries
grep -r "\.objects\.\|\.filter(\|\.get(\|\.all()" backend/ --include="*.py" | grep -v migrations

# Find N+1 query potential
grep -r "for.*in.*\.objects\|for.*in.*\.all()" backend/ --include="*.py"

# Find missing select_related/prefetch_related
grep -r "\.objects\.filter\|\.objects\.get" backend/ --include="*.py" | grep -v "select_related\|prefetch_related"

# Find synchronous operations in async code
grep -r "async def" backend/ --include="*.py" -A 10 | grep -v await
```

### Testing Coverage
```bash
# Find untested files
for file in $(find backend -name "*.py" -not -path "*/test*" -not -path "*/migrations/*"); do
    base=$(basename $file .py)
    dir=$(dirname $file)
    if ! find $dir -path "*/test*" -name "*test*$base*" | grep -q .; then
        echo "No test for: $file"
    fi
done

# Find test files
find backend -name "*test*.py" -o -name "test_*.py" | grep -v __pycache__

# Count test vs implementation files
echo "Implementation files: $(find backend -name "*.py" -not -path "*/test*" -not -path "*/migrations/*" | wc -l)"
echo "Test files: $(find backend -name "*test*.py" -o -name "test_*.py" | wc -l)"
```

## Django Shell Queries

### Memory System Investigation
```python
# Check memory statistics
from memory.models import ConversationMemory
from django.db.models import Count, Avg

# Memory count by user
ConversationMemory.objects.values('user__username').annotate(count=Count('id')).order_by('-count')

# Check embedding coverage
total = ConversationMemory.objects.count()
with_embedding = ConversationMemory.objects.exclude(embedding__isnull=True).count()
print(f"Embedding coverage: {with_embedding}/{total} ({with_embedding/total*100:.1f}%)")

# Find memories without source
orphaned = ConversationMemory.objects.filter(metadata__conversation_id__isnull=True).count()
print(f"Orphaned memories: {orphaned}")
```

### Agent System Investigation
```python
# Check agent usage
from agent_orchestra.models import AgentExecution

# Most used agents
AgentExecution.objects.values('agent_name').annotate(
    count=Count('id'),
    avg_duration=Avg('duration')
).order_by('-count')

# Failed executions
failed = AgentExecution.objects.filter(status='failed')
for failure in failed[:10]:
    print(f"{failure.agent_name}: {failure.error_message}")

# Tool usage statistics
from agent_orchestra.models import ToolExecution
ToolExecution.objects.values('tool_name').annotate(count=Count('id')).order_by('-count')
```

### Conversation Analysis
```python
# Conversation statistics
from ai_partner.models import ConversationSession, Message

# Active conversations
active = ConversationSession.objects.filter(is_active=True).count()
print(f"Active conversations: {active}")

# Messages per conversation
from django.db.models import Count
stats = ConversationSession.objects.annotate(
    message_count=Count('messages')
).aggregate(
    avg_messages=Avg('message_count'),
    max_messages=Max('message_count')
)
print(f"Average messages per conversation: {stats['avg_messages']:.1f}")

# Check for conversation style learning
sessions_with_style = ConversationSession.objects.exclude(
    metadata__conversation_style__isnull=True
).count()
print(f"Sessions with learned style: {sessions_with_style}")
```

## Common Debugging Patterns

### Pattern 1: Trace WebSocket Message
```python
# Add to consumers.py
import logging
logger = logging.getLogger(__name__)

async def receive(self, text_data):
    logger.info(f"[TRACE] Received: {text_data[:100]}")
    # ... existing code ...
    logger.info(f"[TRACE] Sending: {response[:100]}")
```

### Pattern 2: Track Database Queries
```python
# In Django shell or view
from django.db import connection
from django.conf import settings

settings.DEBUG = True  # Temporarily

# Your code here
result = YourModel.objects.complex_query()

# See queries
for query in connection.queries:
    print(f"Time: {query['time']}s")
    print(f"SQL: {query['sql'][:200]}")
```

### Pattern 3: Profile Slow Operations
```python
import time
from functools import wraps

def profile_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"[PROFILE] {func.__name__} took {duration:.3f}s")
        return result
    return wrapper

# Usage
@profile_time
def slow_operation():
    # ... code ...
```

## Quick Reference Commands

### Service Status
```bash
# Check Redis
redis-cli ping

# Check Celery workers
celery -A server inspect active

# Check PostgreSQL
psql -U postgres -c "SELECT version();"

# Check Django
python manage.py check
```

### Common Fixes
```bash
# Reset migrations
python manage.py migrate app_name zero
python manage.py migrate

# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Reindex search
python manage.py update_index

# Recreate embeddings
python manage.py generate_embeddings --force
```

### Emergency Debugging
```bash
# Tail all logs
tail -f backend/logs/*.log

# Watch specific errors
tail -f backend/logs/error.log | grep -i "error\|exception"

# Monitor memory usage
watch -n 1 'ps aux | grep python | grep -v grep'

# Check disk space
df -h | grep -E "/$|/var"
```
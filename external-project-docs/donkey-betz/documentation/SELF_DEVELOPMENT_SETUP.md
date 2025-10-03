# 🤖 Self-Development Agent Complete Setup Guide

## Overview
The Self-Development Agent gives your AI assistant complete awareness of your codebase, allowing it to:
- Analyze and understand your entire code structure
- Generate contextually appropriate code
- Fix bugs and implement features
- Deploy specialized agents to make changes
- Maintain code consistency and patterns

## Prerequisites

### 1. Core Services Running
```bash
# 1. Django Backend
cd /Users/donkeyking/development/donkey_betz/backend
python manage.py runserver

# 2. Celery Workers (in separate terminal)
celery -A server worker --loglevel=info

# 3. Redis (in separate terminal)
redis-server

# 4. Frontend (in separate terminal)
cd /Users/donkeyking/development/donkey_betz/donkey-betz-frontend
npm run dev
```

### 2. Database Migrations
```bash
# Make sure all migrations are applied
python manage.py migrate
```

## Step 1: Initial Codebase Ingestion

### Basic Ingestion
```bash
cd /Users/donkeyking/development/donkey_betz/backend
python manage.py ingest_codebase
```

### Advanced Ingestion with Analysis
```bash
# Ingest and immediately analyze
python manage.py ingest_codebase --analyze

# Ingest and find all TODOs
python manage.py ingest_codebase --find-todos

# Ingest specific paths only
python manage.py ingest_codebase --paths ai_partner agent_orchestra

# Full analysis
python manage.py ingest_codebase --analyze --find-todos
```

## Step 2: Verify Ingestion

### Check Memory Entries
```python
# Django shell
python manage.py shell

from shared_memory.models import UnifiedMemoryEntry
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='self_dev_agent')

# Check ingested code files
code_memories = UnifiedMemoryEntry.objects.filter(
    user=user,
    source_system='code_analysis'
).count()

print(f"Code files in memory: {code_memories}")

# Sample a few entries
samples = UnifiedMemoryEntry.objects.filter(
    user=user,
    source_system='code_analysis'
)[:5]

for memory in samples:
    print(f"- {memory.title}: {memory.content_type}")
```

## Step 3: Enable in Main Assistant

The Self-Development Agent is already integrated! Use these trigger phrases:

### Code Analysis Commands
- **"Analyze the codebase"** - Full analysis
- **"Check code quality"** - Quality review
- **"Review code for security issues"** - Security audit
- **"Analyze performance bottlenecks"** - Performance review

### TODO Management
- **"Find all TODOs"** - Lists all TODOs/FIXMEs
- **"What needs to be done?"** - Prioritized task list
- **"Show me high priority TODOs"** - Critical items

### Code Generation
- **"Implement [feature description]"** - Generates implementation
- **"Create a feature for [requirement]"** - Full feature code
- **"Generate code for [functionality]"** - Code generation
- **"Build [component name]"** - Component creation

### Bug Fixing
- **"Fix bug in [file/feature]"** - Debug assistance
- **"Debug [error message]"** - Error resolution
- **"Solve [problem description]"** - Problem solving
- **"Resolve error in [location]"** - Targeted fixes

## Step 4: Test the Integration

### Quick Test Script
```python
# test_self_dev.py
import os
import sys
import django
import asyncio

sys.path.insert(0, '/Users/donkeyking/development/donkey_betz/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from ai_partner.personal_ai_services import PersonalAIService

async def test_code_analysis():
    User = get_user_model()
    user = User.objects.filter(username='testuser').first()
    if not user:
        user = User.objects.create_user('testuser', 'test@example.com', 'pass')
    
    ai_service = PersonalAIService(user)
    
    # Test code analysis
    result = await ai_service.process_code_analysis_request(
        user, 
        "analyze the codebase for quality issues"
    )
    
    print("Code Analysis Result:")
    print(result.get('message', 'No message'))
    
    return result

asyncio.run(test_code_analysis())
```

## Step 5: Advanced Features

### Deploy Agent to Make Changes
```python
# The assistant can now deploy agents that understand your code
"Deploy Self-Development Agent to refactor the authentication system"
"Deploy Technical Agent to optimize database queries"
"Deploy Code Quality Agent to improve test coverage"
```

### Continuous Monitoring
```bash
# Set up periodic re-ingestion (cron job)
0 0 * * * cd /path/to/backend && python manage.py ingest_codebase --analyze
```

### Custom Analysis Focus
```python
# In chat:
"Analyze codebase focusing on performance"
"Check code for security vulnerabilities"
"Review error handling patterns"
"Find duplicate code"
```

## Troubleshooting

### Issue: No code found in memory
```bash
# Re-run ingestion with verbose output
python manage.py ingest_codebase --verbosity=2
```

### Issue: Agent can't access code
```python
# Check user association
from shared_memory.models import UnifiedMemoryEntry
entries = UnifiedMemoryEntry.objects.filter(
    source_system='code_analysis'
)
print(f"Total code entries: {entries.count()}")
print(f"Users with code: {entries.values('user').distinct().count()}")
```

### Issue: Ingestion fails
```bash
# Check file permissions
ls -la /Users/donkeyking/development/donkey_betz/

# Check Python path
python -c "import sys; print(sys.path)"

# Try selective ingestion
python manage.py ingest_codebase --paths ai_partner
```

## Usage Examples

### Example 1: Find and Fix a Bug
```
User: "There's a bug in user authentication"
Assistant: *Analyzes authentication code*
User: "Fix the session timeout issue"
Assistant: *Generates fix with proper context*
```

### Example 2: Implement New Feature
```
User: "Implement user notifications"
Assistant: *Understands existing patterns*
User: "Deploy agent to add email notifications"
Assistant: *Deploys agent with codebase knowledge*
```

### Example 3: Code Review
```
User: "Review the agent orchestration system"
Assistant: *Analyzes architecture and patterns*
User: "What improvements would you suggest?"
Assistant: *Provides contextual recommendations*
```

## Best Practices

1. **Regular Re-ingestion**: Run weekly to keep memory current
2. **Selective Ingestion**: Focus on actively developed modules
3. **Clear Requests**: Be specific about what you want analyzed
4. **Incremental Changes**: Test small changes before large refactors
5. **Backup First**: Always backup before automated changes

## Next Steps

1. Run initial ingestion: `python manage.py ingest_codebase --analyze`
2. Test with simple query: "Find all TODOs"
3. Try code analysis: "Analyze code quality"
4. Deploy agent for task: "Deploy agent to fix authentication"

## Notes

- Ingestion may take 5-10 minutes for large codebases
- First analysis after ingestion builds the index
- Subsequent queries are much faster (cached)
- The more specific your request, the better the results
- Agent deployment + codebase knowledge = powerful automation

---

Ready to give your AI assistant superpowers? Start with the ingestion command!
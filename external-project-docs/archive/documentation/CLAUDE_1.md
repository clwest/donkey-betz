# CLAUDE.md - Donkey Betz Development Guide

## 🎯 Project Overview

**Donkey Betz** - AI-powered business creation platform where exercise IS productive work.
- **Architecture**: Django REST API + React Web + Flutter Mobile
- **Status**: ~97% Complete, ⚠️ DATABASE RESET - All data lost (July 16, 2025)
- **Port Configuration**: Backend (8000), Frontend (5173), Mobile (Flutter)

## 🚀 Quick Start

```bash
# Backend
cd backend && source .venv/bin/activate
make run-backend  # Starts Django + Redis + Celery

# Frontend
cd donkey-betz-frontend
npm run dev  # Port 5173

# Services
make restart-services  # After code changes
make status          # Check services
```

## 📁 Key Directories

```
move_that_ass/
├── backend/                    # Django REST API
│   ├── agent_orchestra/       # 21 AI agents
│   ├── ai_evolution/          # Darwin-Gödel Framework
│   └── security/              # Encryption & Privacy
├── donkey-betz-frontend/      # React (Vite + TypeScript)
├── docs/                      # Production guides
└── PROJECT_REVIEW_SECTIONS/   # System documentation
```

## ⚠️ Critical Guidelines

### 1. API Endpoints - Always Include `/api/`
```typescript
// ✅ CORRECT
await apiClient.get('/api/agent-orchestra/templates/');

// ❌ WRONG
await apiClient.get('/agent-orchestra/templates/');
```

### 2. Environment Variables
Essential in `backend/.env`:
```bash
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-django-secret
OPENAI_API_KEY=your-key
ENABLE_AI_EVOLUTION=True
```

### 3. Common Import Patterns
```python
# Django
from django.contrib.auth import get_user_model
User = get_user_model()

# UUID Handling
import uuid
if isinstance(id, str):
    id = uuid.UUID(id)

# Async/Sync Database
from asgiref.sync import sync_to_async
result = await sync_to_async(Model.objects.create)(**data)
```

## 🔧 Common Issues & Solutions

### Server Won't Start
1. Check `django.log` for import errors
2. Verify all apps in INSTALLED_APPS exist
3. Ensure Redis is running: `redis-cli ping`
4. Check `.env` file syntax - ensure each variable is on its own line

### Migration Errors
If you encounter "relation does not exist" errors:
```bash
# Use --fake flag for problematic migrations
python manage.py migrate <app_name> <migration_number> --fake
# Then run remaining migrations
python manage.py migrate
```

### WebSocket Errors
```typescript
// Use import.meta.env for Vite
const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
```

### Database Encryption Issues
- Empty strings must be encrypted (not None)
- Use ConversationMemoryManager for creation
- Check EncryptedTextField implementations

### API Rate Limiting
- Stock APIs: Cache with 5-10 second TTL
- Use batch endpoints when available
- Implement frontend request batching

## 🏗️ System Architecture

### Core Systems (All Operational)
1. **Memory Palace** - RAG system with 18,175+ memories (rebuilt July 16, 2025)
2. **Agent Orchestra** - 25 specialized AI agents (fully populated)
3. **Scout Hub** - Reddit & Stock discovery platform
4. **Business Hub** - Business plan generation & export
5. **AI Evolution** - Response optimization framework
6. **Security Framework** - Encryption, PII detection, privacy controls

### Database Recovery (July 16, 2025)
- Successfully rebuilt after complete data loss
- 25 AI agents created
- 14 content templates loaded
- 18,175 memories ingested from markdown files
- Automated backup system now in place

### Real-Time Features
- WebSocket connections for live updates
- Redis pub/sub for cross-instance messaging
- Celery for async task processing

## 🧪 Testing

```bash
# Quick validation
cd backend
python manage.py check
python manage.py test

# Frontend
cd donkey-betz-frontend
npm test
```

## 📚 Key Documentation

### Production Readiness
- `/docs/MONITORING_GUIDE.md` - Prometheus/Grafana setup
- `/docs/SSL_TLS_CONFIGURATION.md` - HTTPS configuration
- `/docs/BACKUP_AND_RECOVERY.md` - Backup procedures
- `/docs/TWO_FACTOR_AUTHENTICATION.md` - 2FA implementation

### Development
- `/METHOD_INDEX.md` - Common code patterns
- `/PROJECT_REVIEW_SECTIONS/` - System analyses
- `/EVOLUTION_FRAMEWORK_ANALYSIS.md` - AI evolution system
- `/CLAUDE_ARCHIVE_JULY_2025.md` - Historical context

## 🎨 UI/UX Standards

### Colors
- Primary: `#2563eb` (Blue)
- Secondary: `#7c3aed` (Purple)  
- Background: `#0a0a0a` (Dark)
- Success: `#10b981`, Danger: `#ef4444`

### Component Patterns
- Always show loading states
- Implement empty states (visual, not text)
- Use dismissible alerts for errors
- Keep components under 300 lines (ESLint enforced)

## 🚨 Production Configuration

### Required Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Monitoring Stack
- Prometheus metrics collection
- Grafana dashboards
- ELK stack for centralized logging
- Health check endpoints

## 💡 Development Philosophy

1. **Real Data Only** - No mock data in production
2. **Complete > Perfect** - 100% functional before optimization
3. **User First** - Clear feedback, helpful errors
4. **Performance** - Cache aggressively, batch API calls

---

For detailed implementation history, see `CLAUDE_ARCHIVE_JULY_2025.md`
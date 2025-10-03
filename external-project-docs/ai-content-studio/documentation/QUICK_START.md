# 🚀 AI Content Studio - Quick Start

## First Time Setup (30 seconds)
```bash
cd /Users/donkeyking/development/ai-content-studio
make setup    # Creates venv, installs deps, runs migrations
make dev      # Start development server
```

## Daily Development
```bash
make dev      # Start server (http://127.0.0.1:8000)
make stop     # Stop server
make status   # Check if running
```

## Quick Commands
- `make dev` or `make d` - Start development server
- `make test` or `make t` - Run tests  
- `make shell` - Django interactive shell
- `make api-test` - Test all API endpoints

## API Testing
```bash
# Quick test (server must be running)
make quick-test

# Full API test suite
make api-test

# Manual test
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

## What the Makefile Does

### Simplified from 500+ lines → 200 lines
The original Makefile had:
- ❌ Redis management (not needed)
- ❌ PgBouncer (not needed for SQLite)
- ❌ Celery workers (not using async)
- ❌ Flutter/iPhone commands (no mobile app)
- ❌ Multiple server configurations
- ❌ Complex service orchestration

### Our Makefile has:
- ✅ Simple dev server start/stop
- ✅ Database management
- ✅ API testing
- ✅ Code quality tools
- ✅ Deployment preparation

## Key Differences

| Command | Old Makefile | New Makefile |
|---------|-------------|--------------|
| Start server | `make run-backend-ws-dual` | `make dev` |
| Dependencies | Redis, PgBouncer, Celery | None |
| Complexity | 500+ lines, 40+ targets | 200 lines, 20 targets |
| Setup | Multiple services | Single command |

## Server Management

### Start in foreground (see logs)
```bash
make dev
```

### Start in background
```bash
make run-bg
# View logs: tail -f /tmp/django.log
# Stop: make stop
```

### Check status
```bash
make status
# Shows if server is running and database size
```

## Database Commands

```bash
make migrate      # Apply migrations
make migrations   # Create new migrations  
make superuser    # Create admin user
make shell        # Django shell
make reset-db     # ⚠️ Delete all data and reset
```

## Testing & Quality

```bash
make test         # Run Django tests
make api-test     # Test API endpoints
make format       # Format with black
make lint         # Check code quality
```

## Production Prep

```bash
make deploy-check  # Pre-deployment checklist
make prod-settings # Generate production config
```

## Tips

1. **Always use `make dev`** - ensures correct settings (SQLite)
2. **One terminal** - no need for multiple terminals
3. **Simple is better** - removed 95% of complexity
4. **Focus on coding** - not on infrastructure

---

The beauty of this setup: **You can focus on building features, not managing services!** 🎯
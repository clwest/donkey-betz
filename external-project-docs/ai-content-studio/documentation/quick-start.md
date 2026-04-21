# Quick Start Guide

## ⚡ 30-Second Setup

```bash
# 1. Navigate to backend
cd /Users/donkeyking/development/ai-content-studio/backend

# 2. Activate virtual environment
source ../.venv/bin/activate

# 3. Start development server (uses SQLite)
./run_dev.sh

# Or manually:
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py runserver
```

Your API is now running at: http://127.0.0.1:8000

## 🔑 Test the API

```bash
# Test with existing user
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# Response:
# {"user_id":2,"username":"testuser","token":"<redacted-993f8273-2026-04-20>"}
```

## 📝 Important Notes

### Development vs Production Settings

**Development** (`core.settings_dev`):
- Uses SQLite database (no PostgreSQL needed)
- Debug mode enabled
- Localhost only
- Perfect for local development

**Production** (`core.settings`):
- Uses PostgreSQL with pgvector
- Debug disabled
- Requires database setup
- For deployment only

### Common Issues

**Issue**: "role 'postgres' does not exist"
- **Cause**: Running with production settings instead of development
- **Fix**: Use `DJANGO_SETTINGS_MODULE=core.settings_dev`

**Issue**: "That port is already in use"
- **Fix**: Kill existing process:
```bash
lsof -i :8000
kill -9 <PID>
```

## 🎯 What's Working

✅ User authentication (login/register)
✅ Content generation (text with GPT-4)
✅ Content listing
✅ Memory search (with SQLite fallback)
✅ Token-based API authentication

## 🚀 Next Steps

1. **Create content**: Use the API to generate AI content
2. **Test memory search**: Store and search memories
3. **Build frontend**: Connect React/Next.js to the API
4. **Deploy**: When ready, deploy to Render with PostgreSQL

## 📚 Full Documentation

- [Development Setup](development-setup.md) - Detailed setup guide
- [API Documentation](../api/endpoints.md) - All endpoints
- [Deployment Guide](deployment.md) - Production deployment
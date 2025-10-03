# Development Setup Guide

Get AI Content Studio running locally in 5 minutes!

## Prerequisites

- Python 3.11+ installed
- pip package manager
- Git
- A text editor (VS Code recommended)
- OpenAI API key

## Quick Start

### 1. Clone the Repository

```bash
# If you have the code locally
cd /Users/donkeyking/development/ai-content-studio

# Or clone from GitHub
git clone https://github.com/YOUR_USERNAME/ai-content-studio.git
cd ai-content-studio
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Verify activation (should show .venv path)
which python
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in the backend directory:

```bash
cd backend
cp .env.example .env  # If example exists
# Or create new:
touch .env
```

Edit `.env` with your settings:

```env
# Required
SECRET_KEY=your-secret-key-here-make-it-long-and-random
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_OPENAI_KEY_HERE

# Optional (for payments)
STRIPE_SECRET_KEY=sk_test_YOUR_STRIPE_TEST_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_STRIPE_TEST_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# Development settings
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS (for frontend)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. Run Database Migrations

```bash
# Using development settings (SQLite)
python manage.py migrate

# You should see:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, ...
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ...
```

### 6. Create a Test User

```bash
# Option 1: Create superuser (admin access)
python manage.py createsuperuser
# Follow prompts for username, email, password

# Option 2: Use the test script
python test_api.py
# This will create testuser/testpass123
```

### 7. Start the Development Server

```bash
python manage.py runserver

# You should see:
# Watching for file changes with StatReloader
# Performing system checks...
# System check identified no issues (0 silenced).
# August 27, 2025 - 10:30:00
# Django version 5.1, using settings 'core.settings_dev'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CONTROL-C.
```

### 8. Verify Installation

Open a new terminal and test the API:

```bash
# Test registration
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser2","password":"testpass123","email":"test2@example.com"}'

# Or use the test script
python test_api.py
```

Visit the admin panel: http://127.0.0.1:8000/admin/

## Detailed Setup

### OpenAI API Key

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to `.env` file
3. Keep it secret! Never commit to Git

### Database Options

#### SQLite (Default - Development)

No setup needed! It just works.

```python
# backend/core/settings_dev.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### PostgreSQL with pgvector (Production-like)

1. Install PostgreSQL:
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb aicontentstudio
```

2. Install pgvector:
```bash
# macOS
brew install pgvector

# Or from source
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
```

3. Enable extension:
```sql
psql aicontentstudio
CREATE EXTENSION vector;
```

4. Update `.env`:
```env
DATABASE_URL=postgresql://localhost/aicontentstudio
```

5. Install Python PostgreSQL adapter:
```bash
pip install psycopg2-binary pgvector
```

## IDE Setup

### VS Code

Recommended extensions:
- Python (Microsoft)
- Pylance
- Django
- Thunder Client (for API testing)

`.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.linting.pylintArgs": [
        "--load-plugins=pylint_django",
        "--django-settings-module=core.settings_dev"
    ],
    "[python]": {
        "editor.formatOnSave": true
    }
}
```

### PyCharm

1. Open project
2. Settings → Project → Python Interpreter
3. Select your .venv interpreter
4. Mark `backend` as Sources Root
5. Enable Django support:
   - Settings → Languages & Frameworks → Django
   - Enable Django Support
   - Django project root: `backend`
   - Settings: `core/settings_dev.py`

## Common Development Tasks

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test memory
python manage.py test content

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Management

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (careful!)
rm db.sqlite3
python manage.py migrate

# Database shell
python manage.py dbshell
```

### Django Shell

```bash
# Interactive Python shell with Django loaded
python manage.py shell

# Example usage:
>>> from django.contrib.auth.models import User
>>> from memory.services import MemoryService
>>> 
>>> user = User.objects.get(username='testuser')
>>> service = MemoryService()
>>> service.store_memory(user, "Test memory content", importance=0.8)
>>> results = service.search_memories(user, "test", limit=5)
>>> print(results)
```

### Generate Sample Data

```python
# create_sample_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_dev')
django.setup()

from django.contrib.auth.models import User
from content.models import Content
from memory.services import MemoryService

# Create user if not exists
user, created = User.objects.get_or_create(
    username='demo',
    defaults={'email': 'demo@example.com'}
)
if created:
    user.set_password('demo123')
    user.save()
    print(f"Created user: demo/demo123")

# Generate some content
content_prompts = [
    "Write a haiku about coding",
    "Explain quantum computing in simple terms",
    "Create a recipe for happiness"
]

for prompt in content_prompts:
    content = Content.objects.create(
        user=user,
        type='text',
        prompt=prompt,
        result=f"Sample result for: {prompt}"
    )
    print(f"Created content: {content.id}")

    # Store as memory
    service = MemoryService()
    service.store_memory(user, content.result, importance=0.7)

print("Sample data created!")
```

## Troubleshooting

### Issue: "No module named 'django'"

**Solution**: Activate your virtual environment
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Issue: "OPENAI_API_KEY not set"

**Solution**: Check your .env file
```bash
cat .env | grep OPENAI
# Should show: OPENAI_API_KEY=sk-proj-...
```

### Issue: "port 8000 already in use"

**Solution**: Kill the process or use different port
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

### Issue: Database errors

**Solution**: Reset migrations
```bash
# Delete migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Delete database
rm db.sqlite3

# Recreate
python manage.py makemigrations
python manage.py migrate
```

### Issue: "ImportError: cannot import name 'CosineDistance'"

**Solution**: This is normal with SQLite. The code handles it gracefully.

## Performance Tips

### 1. Use Python 3.11+
Significant performance improvements over 3.9

### 2. Enable Django Debug Toolbar
```bash
pip install django-debug-toolbar
```

Add to `INSTALLED_APPS` and middleware in settings.

### 3. Database Indexing
Already configured on frequently queried fields

### 4. Caching (Optional)
```python
# settings_dev.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

## Security Notes for Development

⚠️ **Never commit these to Git:**
- `.env` file
- `db.sqlite3`
- `*.pyc` files
- `.venv/` directory
- Any file with API keys

Add to `.gitignore`:
```gitignore
*.pyc
__pycache__/
.env
db.sqlite3
.venv/
venv/
*.log
.DS_Store
```

## Next Steps

1. ✅ Backend running
2. → [Test the API](../api/endpoints.md)
3. → [Set up frontend](frontend-integration.md)
4. → [Configure payments](payment-integration.md)
5. → [Deploy to production](deployment.md)

## Quick Reference

```bash
# Start server
cd backend && source ../.venv/bin/activate && python manage.py runserver

# Test API
python test_api.py

# Admin panel
open http://127.0.0.1:8000/admin/

# Django shell
python manage.py shell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

*Happy coding! If you encounter issues not covered here, check the [API documentation](../api/endpoints.md) or create an issue on GitHub.*
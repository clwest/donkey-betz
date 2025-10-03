# Deployment Guide - Render + PostgreSQL

This guide walks you through deploying AI Content Studio to Render with PostgreSQL and pgvector support.

## Prerequisites

- GitHub account
- Render account (free tier works)
- Stripe account (for payments)
- OpenAI API key

## Step 1: Prepare Your Code

### 1.1 Create GitHub Repository

```bash
cd /Users/donkeyking/development/ai-content-studio
git init
git add .
git commit -m "Initial commit - AI Content Studio"
```

Create a new repository on GitHub and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-content-studio.git
git branch -M main
git push -u origin main
```

### 1.2 Create Production Settings

Create `backend/core/settings_prod.py`:

```python
"""
Production settings for AI Content Studio
"""
import os
import dj_database_url
from .settings import *

# Security
DEBUG = False
ALLOWED_HOSTS = [
    '.onrender.com',
    'your-domain.com',  # Add your custom domain if you have one
]

# Database - Render provides DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS - Update with your frontend URL
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.vercel.app",
    "https://your-domain.com",
]

# Ensure environment variables are loaded
SECRET_KEY = os.environ.get('SECRET_KEY', 'generate-a-secure-key-here')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
```

### 1.3 Update requirements.txt

Add production dependencies:

```bash
echo "dj-database-url==2.2.0" >> backend/requirements.txt
echo "whitenoise==6.6.0" >> backend/requirements.txt
echo "gunicorn==21.2.0" >> backend/requirements.txt
echo "psycopg2-binary==2.9.9" >> backend/requirements.txt
```

### 1.4 Create render.yaml

Create `render.yaml` in the root directory:

```yaml
databases:
  - name: aicontentstudio-db
    plan: free
    databaseName: aicontentstudio
    user: aicontentstudio
    region: oregon
    postgresMajorVersion: 15

services:
  - type: web
    name: aicontentstudio-api
    plan: free
    env: python
    region: oregon
    buildCommand: |
      cd backend
      pip install -r requirements.txt
      python manage.py collectstatic --no-input
      python manage.py migrate
    startCommand: |
      cd backend
      gunicorn core.wsgi:application
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: core.settings_prod
      - key: DATABASE_URL
        fromDatabase:
          name: aicontentstudio-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false  # Set manually in dashboard
      - key: STRIPE_SECRET_KEY
        sync: false  # Set manually in dashboard
      - key: STRIPE_WEBHOOK_SECRET
        sync: false  # Set manually in dashboard
      - key: PYTHON_VERSION
        value: 3.11.6
```

## Step 2: Set Up PostgreSQL with pgvector

### 2.1 Create Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: `aicontentstudio-db`
   - Database: `aicontentstudio`
   - User: `aicontentstudio`
   - Region: Oregon (US West)
   - PostgreSQL Version: 15
   - Plan: Free ($0/month)
4. Click "Create Database"

### 2.2 Enable pgvector Extension

Once database is created:

1. Copy the "External Database URL" from your database dashboard
2. Connect using psql:

```bash
# Install psql if needed
brew install postgresql  # macOS
# or
sudo apt-get install postgresql-client  # Ubuntu/Debian

# Connect to your database
psql "your-external-database-url-here"

# Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

# Verify it's installed
\dx

# Exit
\q
```

Alternatively, use Render's built-in SQL console:
1. Go to your database dashboard
2. Click "Connect" → "PSQL Command"
3. Run: `CREATE EXTENSION IF NOT EXISTS vector;`

## Step 3: Deploy the Application

### 3.1 Connect GitHub to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Select "Build and deploy from a Git repository"
4. Connect your GitHub account if not already connected
5. Select your `ai-content-studio` repository

### 3.2 Configure Web Service

1. **Name**: `aicontentstudio-api`
2. **Region**: Oregon (US West) - same as database
3. **Branch**: main
4. **Root Directory**: backend
5. **Runtime**: Python 3
6. **Build Command**: 
   ```bash
   pip install -r requirements.txt
   python manage.py collectstatic --no-input
   python manage.py migrate
   ```
7. **Start Command**: 
   ```bash
   gunicorn core.wsgi:application
   ```
8. **Plan**: Free ($0/month)

### 3.3 Set Environment Variables

In the Environment section, add:

| Key | Value | Notes |
|-----|-------|-------|
| `DJANGO_SETTINGS_MODULE` | `core.settings_prod` | Required |
| `PYTHON_VERSION` | `3.11.6` | Required |
| `SECRET_KEY` | Click "Generate" | Auto-generate |
| `DATABASE_URL` | Auto-linked from database | Automatic |
| `OPENAI_API_KEY` | Your OpenAI API key | From OpenAI dashboard |
| `STRIPE_SECRET_KEY` | Your Stripe secret key | From Stripe dashboard |
| `STRIPE_PUBLISHABLE_KEY` | Your Stripe publishable key | From Stripe dashboard |
| `STRIPE_WEBHOOK_SECRET` | Your webhook secret | After setting up webhook |

### 3.4 Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Run migrations
   - Start the server
3. Wait for "Deploy successful" (usually 3-5 minutes)

## Step 4: Verify Deployment

### 4.1 Test API Endpoints

Your API will be available at: `https://aicontentstudio-api.onrender.com`

Test registration:
```bash
curl -X POST https://aicontentstudio-api.onrender.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"prodtest","password":"testpass123","email":"test@example.com"}'
```

### 4.2 Create Superuser

SSH into your service:
1. Go to your web service dashboard on Render
2. Click "Shell" tab
3. Run:
```bash
cd backend
python manage.py createsuperuser
```

### 4.3 Access Admin Panel

Visit: `https://aicontentstudio-api.onrender.com/admin/`

## Step 5: Set Up Stripe Webhook

### 5.1 Create Webhook Endpoint

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Endpoint URL: `https://aicontentstudio-api.onrender.com/api/payment/stripe-webhook/`
4. Events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Click "Add endpoint"

### 5.2 Update Webhook Secret

1. Copy the webhook signing secret (starts with `whsec_`)
2. Go to Render dashboard → Environment
3. Update `STRIPE_WEBHOOK_SECRET` with the new value
4. Click "Save Changes" (triggers redeploy)

## Step 6: Custom Domain (Optional)

### 6.1 Add Custom Domain

1. Go to your web service settings on Render
2. Click "Add Custom Domain"
3. Enter your domain: `api.yourdomain.com`
4. Add the provided DNS records to your domain provider

### 6.2 Update Settings

Update `backend/core/settings_prod.py`:
```python
ALLOWED_HOSTS = [
    '.onrender.com',
    'api.yourdomain.com',
    'yourdomain.com',
]

CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

## Step 7: Monitoring and Maintenance

### 7.1 View Logs

- **Live Logs**: Render dashboard → "Logs" tab
- **Download Logs**: Available in dashboard

### 7.2 Database Backups

For production use, upgrade to a paid plan for automatic backups, or manually backup:

```bash
# Backup
pg_dump "your-database-url" > backup_$(date +%Y%m%d).sql

# Restore
psql "your-database-url" < backup_20250827.sql
```

### 7.3 Performance Monitoring

Free tier limitations:
- Spins down after 15 minutes of inactivity
- First request after spindown takes 30-50 seconds
- 750 hours/month (enough for one service)

For production, consider upgrading to:
- **Starter**: $7/month (no spindowns)
- **Standard**: $25/month (more resources)

## Troubleshooting

### Common Issues

**1. "No module named 'pgvector'"**
- Solution: Add `pgvector==0.2.5` to requirements.txt

**2. "FATAL: password authentication failed"**
- Solution: Check DATABASE_URL is correctly set

**3. "DisallowedHost" error**
- Solution: Add your Render URL to ALLOWED_HOSTS

**4. Static files not loading**
- Solution: Ensure whitenoise is installed and configured

**5. "relation does not exist" errors**
- Solution: Run migrations manually via Shell

### Debug Mode

If you need to debug, temporarily enable debug mode:

1. Set environment variable: `DEBUG=True`
2. Check logs for detailed error messages
3. **Remember to disable after debugging!**

## Production Checklist

- [ ] pgvector extension enabled on PostgreSQL
- [ ] All environment variables set
- [ ] Stripe webhook configured
- [ ] Migrations run successfully
- [ ] Admin superuser created
- [ ] API endpoints tested
- [ ] CORS origins configured for frontend
- [ ] Debug mode disabled
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up

## Next Steps

1. [Frontend Integration](frontend-integration.md) - Connect your React/Next.js app
2. [Payment Integration](payment-integration.md) - Set up Stripe subscriptions
3. [API Documentation](../api/endpoints.md) - Full API reference

## Support Resources

- [Render Documentation](https://render.com/docs)
- [PostgreSQL + pgvector Guide](https://github.com/pgvector/pgvector)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)

---

*Remember: The free tier is perfect for testing and small projects. For production use with consistent performance, consider upgrading to a paid plan.*
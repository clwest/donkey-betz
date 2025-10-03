# Step 7: Deployment - Handoff Document

## 🎯 Objective
Get it live in 1 hour. Use the simplest possible deployment that can handle payments.

## 🚀 The 1-Hour Deployment Plan

### Option A: Render.com (Recommended - Free tier + auto-SSL)

```bash
# 15 minutes total

# 1. Create account at render.com
# 2. Connect GitHub repo
# 3. Create new Web Service

# 4. Add build command:
pip install -r requirements.txt

# 5. Add start command:
python manage.py migrate && python manage.py runserver 0.0.0.0:$PORT

# 6. Add environment variables:
OPENAI_KEY=sk-...
STRIPE_KEY=sk-...
SECRET_KEY=random-string-here

# 7. Click Deploy

# Done. You have SSL, custom domain support, auto-deploy on git push
```

### Option B: Railway.app (Even simpler)

```bash
# 10 minutes total

# 1. Go to railway.app
# 2. Login with GitHub
# 3. Click "New Project"
# 4. Select your repo
# 5. Add environment variables
# 6. Done - deploys automatically
```

### Option C: Heroku (Classic choice)

```bash
# 20 minutes if you know Heroku

# 1. Install Heroku CLI
brew install heroku/brew/heroku

# 2. Create app
heroku create ai-content-studio

# 3. Add buildpacks
heroku buildpacks:set heroku/python

# 4. Create Procfile
echo "web: python manage.py runserver 0.0.0.0:\$PORT" > Procfile

# 5. Deploy
git push heroku main

# 6. Set environment variables
heroku config:set OPENAI_KEY=sk-...
heroku config:set STRIPE_KEY=sk-...
```

### Option D: DigitalOcean App Platform (If you have $5)

```bash
# 15 minutes

# 1. Create app in DigitalOcean dashboard
# 2. Connect GitHub
# 3. Auto-detects Python
# 4. Add environment variables
# 5. Deploy
# $5/month but rock solid
```

## 🔧 The Entire Requirements.txt

```txt
# requirements.txt - That's it
django==4.2.0
openai==1.0.0
stripe==5.0.0
gunicorn==21.0.0
whitenoise==6.0.0
dj-database-url==2.0.0
python-dotenv==1.0.0
```

## 🌍 Production Settings (Keep it simple)

```python
# settings.py additions for production

import dj_database_url
import os

# Security (bare minimum)
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']  # Fix later when you have a domain

# Database (use postgres in production, sqlite in dev)
if os.getenv('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.parse(os.getenv('DATABASE_URL'))

# Static files (whitenoise handles this)
STATIC_ROOT = 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# That's literally all you need
```

## 🔗 Domain Setup (After it's working)

### Option A: Use the free subdomain
- Render: `ai-content-studio.onrender.com`
- Railway: `ai-content-studio.up.railway.app`
- Heroku: `ai-content-studio.herokuapp.com`

**Just use these for launch!**

### Option B: Custom domain (Do this Week 2)
```bash
# 1. Buy domain on Namecheap ($10/year)
# 2. Add to your platform:
   - Render: Settings → Custom Domain
   - Railway: Settings → Domain
   - Heroku: Settings → Domains

# 3. Update DNS:
   - Add CNAME record pointing to platform URL
   
# 4. Wait 10 minutes
# 5. SSL automatically configured
```

## 💳 Stripe Setup (Critical!)

```python
# The only payment code you need

# views.py
def create_checkout_session(request):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'AI Content Studio - Monthly',
                },
                'unit_amount': 19900,  # $199.00
                'recurring': {
                    'interval': 'month',
                },
            },
            'quantity': 1,
        }],
        mode='subscription',
        success_url='https://yoursite.com/success',
        cancel_url='https://yoursite.com/cancel',
    )
    return redirect(session.url)

# That's the entire payment system for MVP
```

## 📊 Monitoring (Bare minimum)

### Option A: Just check if it's up
```python
# Use UptimeRobot.com (free)
# 1. Add your URL
# 2. Get emailed if it goes down
# That's it
```

### Option B: See errors (if you have 5 minutes)
```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Now errors show in platform logs
```

## 🚨 Emergency Fixes (When it breaks)

```bash
# Site is down
heroku restart  # or click restart in dashboard

# Database is corrupted
heroku run python manage.py migrate --run-syncdb

# Out of memory
# Upgrade to $7/month plan

# Too slow
# Add time.sleep(0) to make user think it's "processing"
# Fix actual performance later

# SSL not working
# Just wait, it takes 10 minutes sometimes
```

## ✅ Launch Checklist

### Before Deploy (5 minutes)
- [ ] Remove all print() statements
- [ ] Set DEBUG=False
- [ ] Add your domain to ALLOWED_HOSTS
- [ ] Test payment flow locally
- [ ] Have Stripe in test mode

### Deploy (15 minutes)
- [ ] Push to GitHub
- [ ] Connect to platform
- [ ] Add environment variables
- [ ] Click deploy
- [ ] Wait for build

### After Deploy (10 minutes)
- [ ] Test the URL works
- [ ] Create one piece of content
- [ ] Test payment flow
- [ ] Set up UptimeRobot
- [ ] Post on Twitter

## 🎯 Success Criteria

```python
def is_launched():
    return (
        website_loads() and
        payment_works() and
        content_generates() and
        you_posted_on_twitter()
    )
```

## 📱 The Launch Announcement

```tweet
🚀 Just launched AI Content Studio!

Create content with AI agents that remember your style and context.

- 📝 Blog posts in seconds
- 🎨 Images from text
- 📊 Data analysis
- 🧠 Memory of your previous work

$199/month → $99 for first 10 customers (use code EARLY)

Try it: aicontentstudio.com
```

## 🔥 Day 1 Hotfixes

```python
# These WILL happen, here's how to fix:

# "It's too slow"
def fix_slow():
    # Add a progress bar animation
    # Actually fix performance in v2

# "I can't log in"  
def fix_login():
    # Send them a magic link
    # Build real auth in v2

# "It crashed"
def fix_crash():
    # Restart the server
    # Add error handling in v2

# "Feature X is missing"
def fix_missing_feature():
    # Add to roadmap
    # Say "Great idea! Coming in next update!"
```

## 📅 Timeline
**Duration**: 1 hour to deploy, 30 minutes to verify
**Output**: Live production site

---

## Next Step
Move to `step-08-monetization/` once deployed.
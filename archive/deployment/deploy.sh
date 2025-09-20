#!/bin/bash

# Unified Donkey Betz Platform - Quick Deployment Script
# This script helps you deploy the platform quickly

set -e

echo "🚀 Unified Donkey Betz Platform - Quick Deployment"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.production template..."
    cp .env.production .env
    echo "✅ Created .env file. Please edit it with your production values."
    echo "   Required: SECRET_KEY, DATABASE_URL, REDIS_URL, ALLOWED_HOSTS"
    echo ""
    echo "Generate a secret key with:"
    echo "python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    exit 1
fi

# Select deployment method
echo "Choose deployment method:"
echo "1) Docker Compose (Local/VPS)"
echo "2) Railway"
echo "3) Render"
echo "4) Heroku"
echo "5) Manual Setup"
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo "🐳 Deploying with Docker Compose..."

        # Check Docker installation
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not installed. Please install Docker first."
            exit 1
        fi

        # Build images
        echo "Building Docker images..."
        docker-compose build

        # Start services
        echo "Starting services..."
        docker-compose up -d

        # Run migrations
        echo "Running database migrations..."
        docker-compose exec backend python manage.py migrate

        # Collect static files
        echo "Collecting static files..."
        docker-compose exec backend python manage.py collectstatic --noinput

        # Create superuser
        echo "Would you like to create a superuser? (y/n)"
        read -p "Choice: " create_super
        if [ "$create_super" = "y" ]; then
            docker-compose exec backend python manage.py createsuperuser
        fi

        echo "✅ Deployment complete!"
        echo "   Backend: http://localhost:8000"
        echo "   Frontend: http://localhost:3000"
        echo "   Admin: http://localhost:8000/admin"
        ;;

    2)
        echo "🚂 Deploying to Railway..."

        # Check Railway CLI
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi

        echo "Logging in to Railway..."
        railway login

        echo "Initializing Railway project..."
        railway init

        echo "Deploying..."
        railway up

        echo "Setting up domain..."
        railway domain

        echo "✅ Railway deployment initiated!"
        echo "   Configure environment variables in Railway dashboard"
        ;;

    3)
        echo "🎯 Deploying to Render..."
        echo ""
        echo "Steps to deploy on Render:"
        echo "1. Go to https://render.com and sign up/login"
        echo "2. Connect your GitHub repository"
        echo "3. Create a new Web Service"
        echo "4. Select 'Docker' as the environment"
        echo "5. Set build command: docker build -t app ."
        echo "6. Set start command: daphne -b 0.0.0.0 -p 8000 core.asgi:application"
        echo "7. Add environment variables from .env.production"
        echo "8. Create a PostgreSQL database"
        echo "9. Create a Redis instance"
        echo "10. Connect services and deploy"
        ;;

    4)
        echo "🟣 Deploying to Heroku..."

        # Check Heroku CLI
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not installed. Please install it first."
            echo "   Visit: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi

        echo "Creating Heroku app..."
        heroku create unified-donkey-betz-$(date +%s)

        echo "Adding buildpacks..."
        heroku buildpacks:add heroku/python
        heroku buildpacks:add heroku/nodejs

        echo "Adding PostgreSQL..."
        heroku addons:create heroku-postgresql:mini

        echo "Adding Redis..."
        heroku addons:create heroku-redis:mini

        echo "Setting environment variables..."
        heroku config:set DEBUG=False
        heroku config:set DJANGO_SETTINGS_MODULE=core.settings

        echo "Deploying..."
        git push heroku main

        echo "Running migrations..."
        heroku run python manage.py migrate

        echo "✅ Heroku deployment complete!"
        heroku open
        ;;

    5)
        echo "📋 Manual Setup Instructions:"
        echo ""
        echo "Backend Setup:"
        echo "1. Create Python virtual environment:"
        echo "   python -m venv .venv"
        echo "   source .venv/bin/activate"
        echo ""
        echo "2. Install dependencies:"
        echo "   pip install -r requirements.txt"
        echo ""
        echo "3. Setup database:"
        echo "   - Install PostgreSQL"
        echo "   - Create database: createdb donkeybetz"
        echo "   - Update DATABASE_URL in .env"
        echo ""
        echo "4. Setup Redis:"
        echo "   - Install Redis"
        echo "   - Start Redis: redis-server"
        echo "   - Update REDIS_URL in .env"
        echo ""
        echo "5. Run migrations:"
        echo "   python manage.py migrate"
        echo ""
        echo "6. Collect static files:"
        echo "   python manage.py collectstatic"
        echo ""
        echo "7. Create superuser:"
        echo "   python manage.py createsuperuser"
        echo ""
        echo "8. Start backend:"
        echo "   daphne -b 0.0.0.0 -p 8000 core.asgi:application"
        echo ""
        echo "Frontend Setup:"
        echo "1. Navigate to frontend:"
        echo "   cd frontend"
        echo ""
        echo "2. Install dependencies:"
        echo "   npm install"
        echo ""
        echo "3. Build for production:"
        echo "   npm run build"
        echo ""
        echo "4. Serve with nginx or:"
        echo "   npm run preview"
        ;;
esac

echo ""
echo "📚 For more detailed instructions, see DEPLOYMENT_GUIDE.md"
echo "❓ Need help? Check the troubleshooting section in the guide."
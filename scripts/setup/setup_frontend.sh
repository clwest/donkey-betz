#!/bin/bash

# Unified Donkey Betz - Frontend Quick Setup Script
# This script automates the entire frontend setup process

echo "=========================================="
echo "🚀 UNIFIED DONKEY BETZ - FRONTEND SETUP"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Step 1: Run the implementation script
echo "📦 Step 1: Running frontend implementation script..."
echo "=========================================="
python3 implement_frontend.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Frontend implementation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend structure created successfully${NC}"
echo ""

# Step 2: Navigate to frontend directory
echo "📁 Step 2: Navigating to frontend directory..."
cd frontend

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Frontend directory not found${NC}"
    exit 1
fi

# Step 3: Install dependencies
echo "📦 Step 3: Installing npm dependencies..."
echo "=========================================="
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ npm install failed${NC}"
    echo "Try running: npm install --force"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
echo ""

# Step 4: Check if backend is running
echo "🔍 Step 4: Checking backend connection..."
echo "=========================================="

# Try to hit the health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health/)

if [ "$response" = "200" ] || [ "$response" = "401" ]; then
    echo -e "${GREEN}✅ Backend is running on port 8000${NC}"
else
    echo -e "${YELLOW}⚠️  Backend might not be running on port 8000${NC}"
    echo "Make sure to run your Django backend with:"
    echo "  cd .. && python manage.py runserver"
    echo ""
    read -p "Continue anyway? (y/n): " continue_choice
    if [ "$continue_choice" != "y" ]; then
        exit 0
    fi
fi

echo ""

# Step 5: Create .env.local file if needed
echo "🔐 Step 5: Setting up environment variables..."
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    cat > .env.local << EOL
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_AUTH_TOKEN=<redacted-0fb2390d-2026-04-20>
EOL
    echo -e "${GREEN}✅ Environment file created${NC}"
else
    echo -e "${GREEN}✅ Environment file already exists${NC}"
fi

echo ""

# Step 6: Display launch options
echo "=========================================="
echo -e "${GREEN}🎉 FRONTEND SETUP COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Launch Options:"
echo ""
echo "1. Start Frontend Only:"
echo -e "   ${YELLOW}npm start${NC}"
echo ""
echo "2. Start Frontend + Backend (in separate terminals):"
echo "   Terminal 1 (Backend):"
echo -e "   ${YELLOW}cd .. && python manage.py runserver${NC}"
echo ""
echo "   Terminal 2 (Frontend):"
echo -e "   ${YELLOW}npm start${NC}"
echo ""
echo "3. Development Mode with Hot Reload:"
echo -e "   ${YELLOW}npm run dev${NC}"
echo ""
echo "4. Build for Production:"
echo -e "   ${YELLOW}npm run build${NC}"
echo ""
echo "=========================================="
echo "The app will open automatically at:"
echo -e "${GREEN}http://localhost:3000${NC}"
echo ""
echo "Backend API available at:"
echo -e "${GREEN}http://localhost:8000${NC}"
echo "=========================================="
echo ""

# Ask if user wants to start now
read -p "Would you like to start the frontend now? (y/n): " start_choice

if [ "$start_choice" = "y" ]; then
    echo ""
    echo -e "${GREEN}🚀 Starting React development server...${NC}"
    echo "Press Ctrl+C to stop"
    echo ""
    npm start
else
    echo ""
    echo "To start later, run:"
    echo -e "${YELLOW}cd frontend && npm start${NC}"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
fi
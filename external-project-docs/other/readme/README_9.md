# Donkey Betz - AI-Powered Business Platform

**AI-powered business creation platform where exercise IS productive work time.**

Build business empires while building physical health through our comprehensive AI agent system.

**Platform Status: 75% Complete** (Production-ready core features)

**Architecture:** Django API + React Web + Flutter Mobile

## ✅ **Completed Systems**

- **Stock Intelligence** (100%) - Real-time market data via Polygon.io
- **Content Creation** (100%) - DALL-E + Stable Diffusion with 32 visual styles  
- **AI Command Center** (100%) - Real-time orchestration dashboard
- **Scout Hub** (100%) - Reddit Scout + Stock Scout unified platform
- **Business Hub** (100%) - Business plan generation with PDF/CSV export
- **AI Assistant Hub** (100%) - Multi-agent chat with specialized assistants

## ⚠️ **Systems In Progress**

- **Authentication** (60%) - API access works, needs comprehensive testing
- **Memory/RAG System** (50%) - Vector search returning 0 results
- **Agent-Memory Integration** (30%) - Agent outputs not saved to Memory Palace
- **Research Intelligence** (75%) - Data reliability needs improvement

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ 
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Docker 24+ (for containerized deployment)

### System Requirements
- **Development**: 4.75 CPU cores, 4.89 GB RAM
- **Production**: 9.0 CPU cores, 10.02 GB RAM
- **Storage**: 20 GB minimum (database + media files)

### Monitoring
- **Prometheus**: System and application metrics
- **Grafana**: Visualization dashboards  
- **Exporters**: Node, PostgreSQL, Redis metrics

### Backend Setup

1. **Environment Configuration:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys (see Security section)
   ```

2. **Install Dependencies:**
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Database Setup:**
   ```bash
   # Create PostgreSQL database
   createdb donkey_betz_db
   
   # Run migrations
   make migrate
   ```

4. **Start Services:**
   ```bash
   # Option 1: Docker Compose (Recommended)
   docker-compose up -d
   
   # Option 2: Manual Setup
   make run-backend    # Start Redis + Celery + Django
   
   # Or start individually:
   make check-redis    # Start Redis
   make celery-start   # Start Celery workers  
   make status        # Check service status
   ```

5. **Monitoring Setup:**
   ```bash
   # Test monitoring configuration
   ./test-monitoring.sh
   
   # Start monitoring services
   ./start-monitoring.sh
   
   # Access monitoring dashboards
   # Grafana: http://localhost:3001 (admin/admin)
   # Prometheus: http://localhost:9090
   ```

### Frontend Setup

**React Web App:**
```bash
cd donkey-betz-frontend
npm install
npm run dev  # Runs on port 5173
```

**Flutter Mobile App:**
```bash
cd frontend/momentum_flutter
flutter pub get
flutter run
```

### Service Management

**Docker Compose:**
```bash
docker-compose up -d     # Start all services
docker-compose down      # Stop all services
docker-compose restart   # Restart all services
docker stats            # Monitor resource usage
```

**Manual Management:**
```bash
make status           # Check all services
make restart-services # Restart Redis + Celery after code changes
make stop-services    # Stop all background services
```

## 🧪 Testing

```bash
# Backend tests
make test-backend

# Frontend tests  
cd donkey-betz-frontend && npm test

# Flutter tests
make test-frontend
```

## 🏗️ Architecture

```
move_that_ass/
├── backend/                    # Django REST API
│   ├── agent_orchestra/       # 21 AI agents + orchestration
│   ├── ai_partner/           # Memory + RAG system
│   ├── content/              # Content creation system
│   ├── universal_builder/    # Code generation
│   └── server/              # Django settings
├── donkey-betz-frontend/      # React web app (Vite + TypeScript)
│   └── src/features/         # Feature-based organization
├── frontend/                 # Flutter mobile app
│   └── momentum_flutter/     # Main Flutter project
└── CLAUDE.md                 # Development guidelines
```

## 🔑 API Usage

**Create Account:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/registration/ \
   -H 'Content-Type: application/json' \
   -d '{"username":"alice","email":"a@b.com","password1":"Demo1234!","password2":"Demo1234!"}'
```

**Access Dashboard:**
- React Web: http://localhost:5173
- Django Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/

## 📋 Key Features

### 🤖 AI Agent Orchestra
- **21 Specialized Agents** for business automation
- **Real-time Orchestration** with WebSocket updates
- **Batch Processing** for 50-80% API cost reduction

### 💰 Financial Intelligence
- **Real-time Stock Data** via Polygon.io API
- **Market Analysis** with technical indicators
- **Portfolio Management** with alerts and analytics

### 🎨 Content Creation
- **DALL-E 3 + Stable Diffusion** integration
- **32 Professional Visual Styles** 
- **Video Generation** pipeline (Runway ML)

### 🧠 Memory + RAG System
- **Semantic Search** across all conversations
- **Document Ingestion** with pgvector embeddings
- **Context-aware Responses** with memory integration

### 🔍 Discovery Platform
- **Reddit Scout** for opportunity discovery
- **Stock Scout** for market insights
- **Business Plan Generation** from discovered opportunities

## 🚨 Troubleshooting

**Authentication Issues:**
- Check API tokens in backend/.env
- Verify JWT token storage in frontend
- See [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for details

**Memory/RAG Not Working:**
- Vector search returning 0 results - see [TRULY_COMPLETE/MEMORY_RAG_SYSTEM.md](TRULY_COMPLETE/MEMORY_RAG_SYSTEM.md)
- Check PostgreSQL pgvector extension installed

**Service Issues:**
```bash
# Docker Compose
docker-compose logs <service>  # Check service logs
docker stats                   # Monitor resource usage
docker-compose restart <service>  # Restart specific service

# Manual Management
make status           # Check all services
make restart-services # Restart after code changes
```

**Container Resource Issues:**
See [docs/RESOURCE_LIMITS.md](docs/RESOURCE_LIMITS.md) for comprehensive resource management and troubleshooting.

For detailed troubleshooting, see [CLAUDE.md](CLAUDE.md) and [REALISTIC_PROJECT_STATUS_JULY_9_2025.md](REALISTIC_PROJECT_STATUS_JULY_9_2025.md).


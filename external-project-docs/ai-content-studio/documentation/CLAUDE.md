# 🤖 CLAUDE.md - AI Content Studio Development Guide

## 📋 Project Overview

 **Important Note GPT-5 Is a real model that has recently been released!**

**AI Content Studio** is a comprehensive multi-modal content generation platform with enterprise-grade features.

### Core Stack
- **Backend**: Django 4.2+ with DRF, PostgreSQL + pgvector
- **Frontend**: React Web App + Original Vanilla JS
- **Mobile**: React Native Web with Expo 
- **AI APIs**: OpenAI, Stability AI, Anthropic, Gemini, Groq, Runway ML
- **Status**: 100% Complete - Production Ready

## ✅ Platform Complete - All Features Operational

### 🎙️ Voice Studio (PRODUCTION READY)
- Voice recording, Whisper transcription (95%+ accuracy), GPT-4 speaker diarization
- Voice-to-content pipeline (blogs, social, summaries), Memory integration
- Gallery management, Mobile PWA support, ElevenLabs TTS

### 🧠 Intelligent Prompting System (FULLY IMPLEMENTED) 
- Smart enhancement (Basic/Advanced/Expert), Memory integration
- Dedicated AI Settings page, Statistics dashboard, Test lab
- Integrated with all generators, Real-time enhancement

### 🎨 Image Style Memory Agent (PRODUCTION READY)
- AI learns personal style preferences, Style DNA extraction
- Smart suggestions, Style lineage tracking, 5-star feedback
- Keyboard shortcuts (L=love, S=similar, R=recipe)

### 📚 Personal Knowledge System (FULLY INTEGRATED)
- 236+ documents uploaded and indexed
- Document analysis tools for large codebases
- Batch upload support for bulk documentation
- Integration with all content generation

## 🚀 Quick Start

```bash
make full-stack   # Start all services
# Backend: http://localhost:8001
# React App: http://localhost:8080 (PRIMARY)
# Mobile App: http://localhost:8081

make dev         # Backend + React app + services
make mobile      # Mobile app only
make stop        # Stop all
make status      # Check status
```

## 📁 Key Structure

```
ai-content-studio/
├── backend/                 # Django API
│   ├── api/                # Endpoints (batch, styles, editing)
│   ├── content/            # Models & generators
│   └── core/               # Settings
├── ai-studio-web/          # React Web App (PRIMARY)
├── ai-studio-premium/      # React Native Mobile
├── documentation/          # Complete dev history
└── .env                   # API keys
```

## 📱 Platform Applications

### React Web App (PRIMARY - http://localhost:8080)
- Complete feature set with dark theme
- Blog generation, Social media, eBooks
- Gallery, Voice Studio, Memory system
- Dashboard with real-time analytics

### Mobile App (http://localhost:8081)
- Cross-platform (Web/iOS/Android)
- Glass morphism UI, Premium animations
- Full content generation, Gallery
- PWA support, App store ready


## 🏆 Complete Feature Set (100% Operational)

### Content Generation
- **Text**: Blogs, Social media, eBooks, Campaigns, Podcasts
- **Images**: SD3/SDXL, 53+ styles, Batch generation, Custom styles  
- **Video**: Runway ML (Text/Image-to-video), Progress tracking
- **Voice**: Whisper transcription, Speaker diarization, TTS

### AI Features
- **Stability AI Suite**: Upscale, Inpaint, Background removal, 3D gen
- **Memory System**: Vector search, Cross-agent sharing
- **Style Memory**: AI learns preferences, Smart suggestions
- **Intelligent Prompting**: 3-level enhancement, Test lab

### Platform Features  
- **Dashboard**: Real-time analytics, Activity tracking
- **Gallery**: Multi-format content library, Voice transcripts
- **Campaigns**: Multi-channel, A/B testing, Analytics
- **eBooks**: Chapter management, Version control, Publishing
- **Feedback System**: 5-star ratings, Community stats
- **Mobile PWA**: Cross-platform, Premium UI

### ⚙️ Configuration

**Required API Keys** (.env):
- `OPENAI_API_KEY` - GPT + Whisper
- `STABILITY_API_KEY` - Image generation  
- `RUNWAY_API_KEY` - Video generation
- Optional: `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`

**Database**: PostgreSQL + pgvector (dev: SQLite auto)

## 💻 Development Workflow

### New Session Checklist
1. Check `documentation/` for latest features
2. Review git status and platform status  
3. Start with `make dev` or `make full-stack`

### Development Pattern
- **Backend**: Add views to `api/views_*.py`, run migrations
- **Frontend**: Use React app (`ai-studio-web`) for new features
- **Documentation**: Update `NEW_FEATURES.md` and session notes

### Testing
```bash
make api-test     # API endpoints
make quick-test   # Platform health
# Auth token: <redacted-cff3e844-2026-04-20>
```

## 🔧 Common Issues

| Issue | Solution |
|-------|----------|
| "Failed to fetch" | Check backend running, CORS, API token |
| No images generated | Verify API keys, restart server |
| Database errors | Run `make migrate` or `make reset-db` |
| Empty content display | Check console logs, API responses |
| JSON showing in UI | Check content parsing, clear cache |

## 📋 Key Information

**For AI Assistants:**
- Documentation in `/documentation/` is source of truth
- Use Makefile commands, React app is primary frontend
- Ports: Backend 8001, React 8080, Mobile 8081
- Auth token: `<redacted-cff3e844-2026-04-20>`
- Test user: `testuser` / `testpass123`

### Key API Endpoints

**Content Generation:**
```
# Core generation
POST /api/content/create/         # Single image/text
POST /api/content/batch/          # Batch images
POST /api/content/blog/generate/  # Blog posts
POST /api/content/social/generate/# Social media

# Voice & Video
POST /api/voice/transcribe/       # Voice transcription
POST /api/video/text-to-video/    # Video generation
POST /api/video/image-to-video/   # Video from images

# Advanced Features
POST /api/stability/*             # 15+ Stability AI features
POST /api/style-memory/           # Style learning
GET  /api/dashboard/*             # Analytics & stats
POST /api/feedback/*              # Rating system
```

## 🚀 Platform Status: PRODUCTION READY

**Current Status**: 100% Complete - Enterprise Grade
- All features operational and tested
- Mobile PWA deployment ready
- Real-time analytics dashboard
- Comprehensive feedback system
- Complete documentation

**Potential Enhancements**:
- Redis caching for performance
- 3D model viewer (Three.js)
- Enterprise user management
- API rate limiting & credits

## 📚 Resources

- **Documentation**: `/documentation/` (complete dev history)
- **Feature Reference**: `documentation/NEW_FEATURES.md`
- **Session Notes**: `documentation/sessions/`

## 📊 Last Updated: September 3, 2025

**Status**: PRODUCTION READY - Multi-Tenant Enterprise Platform
- **🔐 Multi-Tenancy**: Complete data isolation between users implemented and tested
- **👤 User Onboarding**: Automatic welcome content and sample templates for new users
- **🛡️ Security**: All API endpoints properly filter by authenticated user
- **📊 Dashboard**: Real-time analytics with user-scoped data
- **🗃️ Database**: PostgreSQL + pgvector with full user isolation
- **📱 Mobile**: Cross-platform PWA ready for app stores
- **📚 Documentation**: Complete development history preserved

**Latest Sessions**:

**September 3, 2025**: Multi-Tenancy Implementation & ChatWidget Fix
- **🔐 Multi-Tenancy**: Complete implementation with data isolation between users
- **👋 User Onboarding**: Automatic welcome content (3 docs, 3 memories, templates)
- **🎯 Empty States**: Contextual UI components for new users with helpful tips
- **🧪 Testing Suite**: Comprehensive multi-tenancy tests verify complete isolation
- **🔧 Migration Tools**: Command to assign existing data to admin user
- **🐛 Performance Fix**: Resolved ChatWidget infinite loop causing API spam
- **📋 Management**: Django command for data migration with dry-run support

**September 3, 2025**: Document Analysis & Knowledge Integration
- **📊 Document Analysis**: Created tools to analyze 2,500+ documents from main projects
- **🔄 Knowledge Integration**: Successfully uploaded 236 documents to Personal Knowledge
- **🛠️ New Tools**: 8 utility scripts for document processing and analysis
- **📦 Batch Upload**: Added API endpoint for bulk document uploads
- **🧪 Testing Suite**: Comprehensive verification tools for embeddings and search

**September 2, 2025**: Content Transformation & Editor Enhancements
- **🎨 Medium-Style Block Editor**: Complete implementation for blogs and eBooks with precise image placement
- **⚡ Content Transformation**: Blog-to-Social/Podcast/eBook conversion from Content Library (✨ sparkles icon)
- **🔧 OpenAI API Fixes**: Resolved GPT-4/5 compatibility issues across all generators
- **📱 React Components**: Fixed TypeScript errors and improved Markdown rendering
- **⏱️ Performance**: Optimized API timeouts and error handling for reliable generation
- **🎙️ Podcast Generation**: Complete multi-segment scripts with show notes and timestamps


---

**Remember**: Platform is production-ready. Focus on optimization and enterprise features.
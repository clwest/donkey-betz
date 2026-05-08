# DonkeyOS Unified Monorepo Structure

**Session 100 Part 13 - Monorepo Organization**
**Created:** November 15, 2025
**Status:** Complete ✅

---

## 📁 Repository Structure

```
unified-donkey-betz/                    # Monorepo root
│
├── mobile/                             # Flutter mobile app (Session 100 Part 13)
│   ├── lib/                           # Dart source code
│   │   ├── core/                      # API client, config, theme
│   │   ├── models/                    # Freezed data models
│   │   ├── providers/                 # Riverpod state management
│   │   ├── services/                  # API service layer
│   │   ├── features/                  # UI screens
│   │   ├── app.dart                   # App configuration
│   │   └── main.dart                  # Entry point
│   ├── test/                          # Flutter tests
│   ├── pubspec.yaml                   # Flutter dependencies
│   ├── .env                           # Mobile environment config
│   ├── README.md                      # Mobile app documentation
│   └── BUILD_INSTRUCTIONS.md          # How to build mobile app
│
├── docs/                              # Complete platform documentation
│   ├── 00-START-HERE/                # Quick start guides
│   ├── features/                      # Feature documentation
│   ├── apis/                          # API references
│   ├── architecture/                  # System architecture
│   ├── sessions/                      # Session summaries
│   ├── FLUTTER_COCKPIT_PHASE1_PLAN.md
│   ├── SESSION_100_PART13_*.md        # Latest session docs
│   └── COMPLETE_SYSTEM_MAP.md
│
├── ai_core/                           # Django AI core app
│   ├── agents/                        # AI agents
│   ├── templates/                     # HTML templates
│   ├── static/                        # Frontend assets
│   └── views.py                       # Web views
│
├── core/                              # Django core app
│   ├── views_image.py                 # Image generation views
│   ├── views_video.py                 # Video generation views
│   ├── views_audio.py                 # Audio generation views
│   └── urls.py                        # URL routing
│
├── content/                           # Content management
│   ├── models.py                      # Project, Session models
│   ├── image_generation.py            # Image generation
│   ├── video_provider.py              # Video generation
│   └── davinci_provider.py            # Video editing
│
├── coleadership/                      # Co-Leadership system (Session 99)
│   ├── models.py                      # Decision, Outcome models
│   ├── views.py                       # REST API endpoints
│   ├── services.py                    # Business logic
│   └── urls.py                        # API routes
│
├── agents/                            # Agent system
│   ├── models.py                      # Agent templates
│   ├── meeting_coordinator_agent.py   # Boardroom meetings
│   └── unified_agent_template.py      # Agent framework
│
├── intelligence/                      # Intelligence layer
│   ├── shared_memory.py              # Redis shared memory
│   └── agent_orchestration.py        # Agent coordination
│
├── scripts/                           # Utility scripts
│   ├── test_api_keys.py              # API validation
│   └── test_*.py                      # Various tests
│
├── .env                               # Backend environment (NOT in git)
├── .gitignore                         # Git exclusions
├── manage.py                          # Django management
├── Makefile                           # Build commands
├── requirements.txt                   # Python dependencies
├── CLAUDE.md                          # AI session entry point
├── 00-START-NEXT-SESSION.md          # Current priorities
├── ACTUAL_WORKING_FEATURES.md        # Feature inventory
├── MONOREPO_STRUCTURE.md             # This file
└── README.md                          # Platform overview
```

---

## 🎯 Quick Navigation

### Working on Backend?
```bash
cd /Users/donkeyking/development/unified-donkey-betz
make start
```

### Working on Mobile?
```bash
cd /Users/donkeyking/development/unified-donkey-betz/mobile
flutter run
```

### Need Documentation?
```bash
cd /Users/donkeyking/development/unified-donkey-betz/docs
cat 00-START-HERE/README.md
```

---

## 🚀 Commands Cheat Sheet

### Backend (Django)
```bash
# From monorepo root
make start              # Start all services
make stop               # Stop all services
make restart            # Restart services
make status             # Check status
make logs               # View logs

# Django specific
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

### Mobile (Flutter)
```bash
# From mobile/ directory
flutter pub get                                           # Install dependencies
flutter pub run build_runner build --delete-conflicting-outputs  # Generate code
flutter run                                               # Run app
flutter test                                              # Run tests
flutter clean                                             # Clean build
flutter devices                                           # List devices
```

### Git Workflow
```bash
# From monorepo root
git status                    # Check what changed
git add .                     # Stage all changes
git commit -m "message"       # Commit
git push                      # Push to remote

# View changes
git diff                      # Unstaged changes
git diff --staged             # Staged changes
```

---

## 🔄 Development Workflow

### Starting Work
1. **Backend First**
   ```bash
   cd /Users/donkeyking/development/unified-donkey-betz
   make start
   # Verify: http://localhost:8000/ai-studio/
   ```

2. **Then Mobile**
   ```bash
   cd mobile
   flutter run
   ```

### Making Changes

**Backend Changes:**
- Edit Django files in root
- Backend auto-reloads on save
- Check http://localhost:8000

**Mobile Changes:**
- Edit Flutter files in `mobile/lib/`
- Press `r` in terminal for hot reload
- Press `R` for hot restart

**Model Changes (Mobile):**
- Edit model files
- Run: `flutter pub run build_runner build --delete-conflicting-outputs`
- Restart app

### Committing

**One Repository = One Commit**

```bash
# From monorepo root
git add .
git commit -m "feat: Add mobile support for feature X

- Backend: Added API endpoint
- Mobile: Created UI screen
- Docs: Updated documentation
"
git push
```

---

## 📚 Documentation Organization

### For AI Sessions
- **Start:** `/CLAUDE.md`
- **Current Priorities:** `/00-START-NEXT-SESSION.md`
- **Session History:** `/docs/sessions/`

### For Development
- **Backend APIs:** `/docs/apis/`
- **Features:** `/docs/features/`
- **Architecture:** `/docs/architecture/`

### For Mobile
- **Quick Start:** `/mobile/README.md`
- **Build Guide:** `/mobile/BUILD_INSTRUCTIONS.md`
- **Implementation Plan:** `/docs/FLUTTER_COCKPIT_PHASE1_PLAN.md`

---

## 🔧 Environment Configuration

### Backend (.env in root)
```env
# Django
SECRET_KEY=...
DEBUG=True
DJANGO_SETTINGS_MODULE=core.settings

# Database
DATABASE_URL=postgresql://...

# APIs
STABILITY_API_KEY=...
RUNWAY_API_KEY=...
ELEVENLABS_API_KEY=...
OPENAI_API_KEY=...
```

### Mobile (mobile/.env)
```env
# API Base URL
API_BASE_URL=http://localhost:8000

# iOS Simulator: use Mac's IP
# API_BASE_URL=http://192.168.1.100:8000

# Android Emulator: use special IP
# API_BASE_URL=http://10.0.2.2:8000
```

---

## 🎨 Technology Stack

### Backend
- **Framework:** Django 5.0
- **Database:** PostgreSQL (production), SQLite (dev)
- **Cache:** Redis
- **Task Queue:** Celery
- **API:** REST (Django REST Framework)

### Mobile
- **Framework:** Flutter 3.x
- **Language:** Dart 3.x
- **State Management:** Riverpod
- **HTTP Client:** Dio + http
- **Serialization:** Freezed + json_serializable
- **UI:** Material Design 3

### Shared
- **Version Control:** Git
- **Documentation:** Markdown
- **Testing:** Automated + Manual

---

## 🔒 Security Notes

### Files NEVER Committed
```
.env                    # Backend secrets
mobile/.env             # Mobile config
*.key, *.pem           # Certificates
secrets/               # Secrets directory
db.sqlite3             # Development database
```

### Git Ignore
Both `.gitignore` (root) and `mobile/.gitignore` are configured to:
- Exclude environment files
- Exclude generated code
- Exclude build artifacts
- Exclude secrets and keys

---

## 📱 Mobile-Backend Integration

### API Endpoints Used by Mobile

**Base URL:** `http://localhost:8000` (dev)

1. **Leadership Stats**
   - `GET /api/v1/coleadership/stats/`
   - Used by: Home screen

2. **Start Meeting**
   - `POST /api/v1/coleadership/boardroom/start/`
   - Used by: Boardroom form

3. **Commit Decision**
   - `POST /api/v1/coleadership/decisions/{id}/human_decision/`
   - Used by: Decision commit screen

4. **Log Outcome**
   - `POST /api/v1/coleadership/decisions/{id}/outcome/`
   - Used by: Outcome screen

5. **Get Projects**
   - `GET /api/creative-projects/`
   - Used by: Project dropdown

---

## 🚦 Status Indicators

**Backend:** Check with `make status`
- ✅ Django running on :8000
- ✅ Redis running on :6379
- ✅ Daphne WebSocket server

**Mobile:** Check with `flutter doctor`
- ✅ Flutter SDK installed
- ✅ Dart SDK installed
- ✅ Connected devices available

---

## 🎯 Next Steps

### Phase 1 Complete ✅
- Backend: 100% ready
- Mobile: Core features complete
- Documentation: Comprehensive

### Phase 2 Planning
- Projects screen in mobile
- Leadership dashboard expansion
- Authentication system
- Offline support
- Push notifications

---

## 📞 Getting Help

### Backend Issues
```bash
make status             # Check what's running
make logs               # View logs
python manage.py check  # Check for problems
```

### Mobile Issues
```bash
flutter doctor -v       # Detailed diagnostics
flutter clean           # Clean build
flutter pub get         # Reinstall dependencies
```

### Both Not Working?
```bash
# Full restart
make stop
make clean
make start
cd mobile && flutter clean && flutter pub get
```

---

## 🎉 Benefits of Monorepo

1. **Single Source of Truth**
   - One repository
   - One version history
   - One place for all code

2. **Easier Development**
   - Edit backend and mobile together
   - Commit related changes together
   - No version sync issues

3. **Better Documentation**
   - All docs in one place
   - Cross-reference easily
   - Unified structure

4. **Simpler Deployment**
   - Clone once
   - Deploy both
   - Version together

---

**Monorepo Structure:** ✅ COMPLETE
**Backend Location:** `/`
**Mobile Location:** `/mobile/`
**Documentation:** `/docs/`
**Reality Score:** 100% (Unified organization!)

**Created:** Session 100 Part 13 - November 15, 2025
**Author:** Claude Code + Chris Partnership 🤝

**"One repo to rule them all!"** 🏢✨

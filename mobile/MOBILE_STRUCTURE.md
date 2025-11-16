# DonkeyOS Flutter Mobile - Project Structure

**Last Updated:** Session 113 - November 15, 2025
**Status:** Demo-Ready! ✅ (Golden Paths + Donkey Cockpit + Co-Leadership + Pipelines + Galleries + Personal Assistant + Voice Input)

---

## 📁 Directory Structure

```
mobile/
├── lib/                              # Main source code
│   ├── core/                         # Core infrastructure
│   │   ├── api_client.dart          # HTTP client with authentication
│   │   ├── api_config.dart          # API endpoints and configuration
│   │   └── app_theme.dart           # Deep purple Material Design theme
│   │
│   ├── models/                       # Freezed data models
│   │   ├── project.dart             # Project model
│   │   ├── session.dart             # AISession model
│   │   ├── image_asset.dart         # ImageAsset + SessionAssetsResponse (Session 101)
│   │   ├── video_asset.dart         # VideoAsset model (Session 101)
│   │   ├── gallery.dart             # GalleryAsset + GalleryResponse + GalleryFilters (Session 111)
│   │   ├── personal_assistant.dart  # AssistantMessage + Conversation + Context + LearningSummary (Session 112)
│   │   ├── assistant_voice.dart     # VoiceResult + MessageData models (Session 113: Voice Input MVP)
│   │   ├── render_job.dart          # RenderJob model with status/progress (Session 105-106)
│   │   ├── pipeline_template.dart   # Pipeline template model (Session 109)
│   │   ├── pipeline_run.dart        # Pipeline run with status tracking (Session 109)
│   │   ├── boardroom_meeting.dart   # Boardroom meeting models
│   │   ├── coleadership.dart        # Decision/outcome models
│   │   ├── connection_status.dart   # Connection status enum (Session 102)
│   │   └── settings_state.dart      # Settings state models (Session 102)
│   │
│   ├── providers/                    # Riverpod state providers
│   │   ├── api_provider.dart        # API client providers (Session 102: uses settings + Session 112: Personal Assistant)
│   │   ├── projects_provider.dart   # Project/session/assets providers
│   │   ├── gallery_provider.dart    # Gallery assets + filters providers (Session 111)
│   │   ├── personal_assistant_provider.dart  # Chat conversation + context providers (Session 112)
│   │   ├── assistant_voice_provider.dart  # Voice recording state provider (Session 113)
│   │   ├── render_providers.dart    # Render job providers (Session 105-106)
│   │   ├── pipelines_provider.dart  # Pipeline templates + runs providers (Session 109)
│   │   ├── boardroom_provider.dart  # Boardroom state
│   │   ├── coleadership_provider.dart  # Co-leadership state
│   │   └── settings_provider.dart   # Settings state + storage (Session 102)
│   │
│   ├── services/                     # API service layer
│   │   └── api/
│   │       ├── projects_api.dart    # Projects, sessions, assets API
│   │       ├── gallery_api.dart     # Unified gallery API (images/videos/audio) (Session 111)
│   │       ├── personal_assistant_api.dart  # Chat, context, learning summary API (Session 112)
│   │       ├── assistant_voice_api.dart  # Voice recording upload API (Session 113)
│   │       ├── render_api.dart      # Render job API calls (Session 105-106)
│   │       ├── pipelines_api.dart   # Pipeline templates + runs API (Session 109)
│   │       ├── boardroom_api.dart   # Boardroom API calls
│   │       └── coleadership_api.dart  # Co-leadership API
│   │
│   ├── features/                     # UI screens by feature
│   │   ├── cockpit/                 # Session 107+110+111+112: Donkey Cockpit (Unified Home)
│   │   │   └── donkey_cockpit_screen.dart  # Command center with 7 cards (added Personal Assistant in S112)
│   │   │
│   │   ├── home/
│   │   │   └── home_screen.dart     # Deprecated: Replaced by Cockpit (Session 107)
│   │   │
│   │   ├── projects/                # Session 101: Project Browser
│   │   │   ├── project_list_screen.dart       # Browse all projects
│   │   │   ├── project_detail_screen.dart     # Project + sessions
│   │   │   ├── session_assets_screen.dart     # View session assets (Session 105: +Render FAB)
│   │   │   └── widgets/
│   │   │       ├── asset_grid.dart            # Image/video grid
│   │   │       └── asset_viewer.dart          # Full-screen viewer
│   │   │
│   │   ├── render/                  # Session 105-106: Video Render Pipeline
│   │   │   ├── video_studio_screen.dart       # Main render hub (Session 106)
│   │   │   ├── render_job_detail_screen.dart  # Live job status with polling
│   │   │   └── render_jobs_screen.dart        # Render queue list
│   │   │
│   │   ├── settings/                # Session 102: Auth & Connection Settings
│   │   │   └── settings_screen.dart           # API config + testing
│   │   │
│   │   ├── boardroom/
│   │   │   ├── boardroom_form_screen.dart     # Start meeting
│   │   │   └── boardroom_result_screen.dart   # Meeting results (Session 108: +Navigate to detail)
│   │   │
│   │   ├── pipelines/                   # Session 109: Creative Pipelines
│   │   │   ├── pipelines_screen.dart         # Template list + recent runs (tabbed)
│   │   │   └── pipeline_run_detail_screen.dart  # Run details with live polling
│   │   │
│   │   ├── gallery/                     # Session 111: Galleries & Assets
│   │   │   ├── galleries_screen.dart         # Unified gallery (images/videos/audio) with filters
│   │   │   └── asset_detail_screen.dart      # Asset detail with metadata + actions
│   │   │
│   │   ├── assistant/                   # Session 112: Personal Assistant
│   │   │   └── personal_assistant_screen.dart  # Chat interface with AI assistant
│   │   │
│   │   ├── coleadership/                # Deprecated: Replaced by leadership/ (Session 108)
│   │   │   ├── decision_commit_screen.dart    # Legacy decision commit
│   │   │   └── outcome_screen.dart            # Legacy outcome logging
│   │   │
│   │   ├── leadership/                  # Session 108: Co-Leadership Mobile UI
│   │   │   ├── decisions_list_screen.dart         # List all decisions with filters
│   │   │   ├── decision_detail_screen.dart        # Full decision detail + forms
│   │   │   ├── coleadership_settings_screen.dart  # ITYS preferences
│   │   │   └── leadership_dashboard.dart          # Leadership stats (future)
│   │
│   ├── widgets/                       # Shared reusable widgets
│   │   └── video_player_widget.dart  # Video player with controls (Session 111)
│   │
│   ├── app.dart                      # App configuration
│   └── main.dart                     # Entry point
│
├── test/                             # Tests (Session 101, 102, 106, 109, 112)
│   ├── models/
│   │   ├── asset_models_test.dart   # Asset model serialization tests (Session 101)
│   │   ├── settings_models_test.dart  # Settings model tests (Session 102)
│   │   ├── render_job_test.dart     # RenderJob model tests (Session 106: 21 tests)
│   │   └── pipeline_models_test.dart  # Pipeline model tests (Session 109: 20 tests)
│   ├── providers/
│   │   ├── settings_provider_test.dart  # Settings provider tests (Session 102)
│   │   └── personal_assistant_provider_test.dart  # Personal Assistant provider tests (Session 112: 10 tests)
│   ├── services/
│   │   ├── projects_api_test.dart   # API integration tests
│   │   ├── render_api_test.dart     # Render API tests (Session 106: 27 tests)
│   │   └── personal_assistant_api_test.dart  # Personal Assistant API tests (Session 112: 8 tests)
│   └── features/
│       ├── donkey_cockpit_screen_test.dart  # Donkey Cockpit UI tests (Session 107: 38 tests)
│       ├── project_list_screen_test.dart    # Project browser widget tests (Session 101)
│       ├── settings_screen_test.dart        # Settings UI widget tests (Session 102)
│       ├── video_studio_screen_test.dart    # Video Studio UI tests (Session 106: 25 tests)
│       └── personal_assistant_screen_test.dart  # Personal Assistant widget tests (Session 112: 8 tests)
│
├── .env                              # Environment configuration (NOT in git)
├── .env.example                      # Example environment config
├── pubspec.yaml                      # Flutter dependencies
├── BUILD_INSTRUCTIONS.md             # Build and run instructions
├── MOBILE_STRUCTURE.md              # This file
└── README.md                         # Mobile app overview
```

---

## 🎯 Feature Organization

### Session 112: Personal Assistant Mobile MVP ⭐ NEW!
**Directory:** `lib/features/assistant/`

**Screen:**
- **PersonalAssistantScreen** (~480 lines) - Chat interface with AI assistant
  - Chat message bubbles (user/assistant)
  - Empty state with suggestion chips
  - Text input with send button
  - Stub microphone button (voice coming soon)
  - Clear conversation option
  - Real-time message updates
  - Error handling with inline messages
  - Confidence indicators for AI responses
  - Suggested actions as chips
  - Timestamp display

**Models:**
- AssistantMessage - Single chat message
- AssistantConversation - Client-side conversation history
- AssistantContext - User preferences and activity context
- LearningSummary - Skills/preferences learned from user

**Providers:**
- assistantConversationProvider - StateNotifier for chat state management
- assistantContextProvider - FutureProvider for user context
- learningSummaryProvider - FutureProvider for learning stats
- personalAssistantApiProvider - PersonalAssistantApi service (in api_provider.dart)

**APIs (Django Backend):**
- `POST /api/assistant/chat/` - Send message, get AI response
- `GET /api/assistant/context/` - Get user context
- `GET /api/assistant/learning/` - Get learning summary
- `POST /api/assistant/feedback/` - Provide feedback on responses

**Integration:**
- Donkey Cockpit Card 4: Personal Assistant card with stats + "Open Chat" button
- Stats: Total chats, skills learned (from learningSummary)
- Navigation from DonkeyCockpitScreen

**Tests:** 26 comprehensive tests (Session 112) - ALL PASSING ✅
- 8 PersonalAssistantApi tests (sendMessage, getContext, getLearningSummary, provideFeedback)
- 10 Provider tests (conversation management, state updates, error handling)
- 8 Widget tests (empty state, message display, input handling, navigation)

**Features:**
- Client-side message history (backend is stateless)
- Optimistic UI updates (user message shows immediately)
- Error messages shown as system messages in chat
- Suggestion chips for common questions
- Material Design 3 styling
- Pull-to-refresh in Cockpit card

**Documentation:** `/docs/SESSION_112_PERSONAL_ASSISTANT_MOBILE.md` (~500 lines)

---

### Session 108: Co-Leadership Mobile UI
**Directory:** `lib/features/leadership/` (+ `lib/features/boardroom/` integration)

**Screens:**
1. **DecisionsListScreen** (~300 lines)
   - ListView of all leadership decisions
   - Status chips (PENDING DECISION, PENDING OUTCOME, COMPLETE)
   - Attribution chips (AI CORRECT, HUMAN CORRECT, BOTH CORRECT)
   - Project chips when linked
   - Empty state, error state, pull-to-refresh
   - Navigation to detail screen

2. **DecisionDetailScreen** (~1000 lines)
   - Complete decision lifecycle screen
   - Decision metadata (title, dates, project)
   - Agent recommendations with stance/confidence
   - Human decision form (commit decision, justification, override tracking)
   - Outcome form (status, attribution, summary)
   - "I Told You So" reflection card (purple, when triggered)
   - Full form validation and state management

3. **CoLeadershipSettingsScreen** (~420 lines)
   - Switch: Allow "I Told You So" reflections
   - Radio buttons: Communication tone (serious/playful)
   - Save/reset functionality
   - Success/error messaging

**Integration:**
- BoardroomResultScreen: "Open Leadership Decision" button → DecisionDetailScreen
- SettingsScreen: "Co-Leadership Preferences" link → CoLeadershipSettingsScreen

**Models:**
- CoLeadershipDecision (list view - lightweight)
- CoLeadershipDecisionDetail (full detail)
- ProjectInfo, AgentRecommendation, HumanDecision, DecisionOutcome
- CoLeadershipPreferences, ToneChoice

**New APIs (Session 108):**
- `GET /api/v1/coleadership/decisions/` - List decisions (paginated)
- `GET /api/v1/coleadership/decisions/{id}/` - Get decision detail
- `GET /api/v1/coleadership/preferences/` - Get preferences
- `POST /api/v1/coleadership/preferences/` - Update preferences

**Existing APIs (Session 99):**
- `POST /api/v1/coleadership/boardroom/start/`
- `POST /api/v1/coleadership/decisions/{id}/human_decision/`
- `POST /api/v1/coleadership/decisions/{id}/outcome/`
- `GET /api/v1/coleadership/stats/`

**Decision Flow:**
1. Run boardroom meeting → Decision created
2. View decision detail → Review agent recommendations
3. Commit human decision → Optional override tracking
4. Log outcome → Attribution (AI/Human/Both)
5. Receive "I Told You So" reflection (if opted-in and AI was correct)

---

### Session 101: Project Browser ⭐ NEW!
**Directory:** `lib/features/projects/`

**Screens:**
1. **ProjectListScreen**
   - Grid view of all projects
   - Loading/error/empty states
   - Pull-to-refresh
   - Navigation to project details

2. **ProjectDetailScreen**
   - Project metadata display
   - Sessions list
   - Statistics (image/video counts)
   - Navigation to session assets

3. **SessionAssetsScreen**
   - Session info header
   - Separate sections for images and videos
   - AssetGrid integration
   - Loading/error states

**Widgets:**
1. **AssetGrid** (`widgets/asset_grid.dart`)
   - 3-column grid layout
   - Image thumbnails with caching
   - Video thumbnails with play icons
   - Favorite indicators
   - Tap to view full-screen

2. **AssetViewer** (`widgets/asset_viewer.dart`)
   - Full-screen image/video viewing
   - Swipe navigation (PageView)
   - Pinch-to-zoom for images
   - Asset metadata display
   - Favorite toggle

**Models:**
- ImageAsset - Image with metadata
- VideoAsset - Video with thumbnail
- SessionAssetsResponse - Complete session assets
- SessionInfo - Session metadata

**APIs:**
- `GET /api/creative-projects/` - List all projects
- `GET /api/creative-projects/{id}/` - Get project details
- `GET /api/v1/sessions/project/{project_id}/` - Get project sessions
- `GET /api/v1/sessions/{session_id}/assets/` - Get session assets ⭐ NEW!

---

### Session 102: Auth & Connection Settings
**Directory:** `lib/features/settings/`

**Screen:**
- **SettingsScreen** - API configuration and connection testing
  - Dynamic API base URL configuration
  - Secure API key storage (FlutterSecureStorage)
  - Real-time connection testing with /health/ping/
  - Form validation and status indicators
  - Save/reset functionality

**Models:**
- ConnectionStatus - Enum (disconnected, connecting, connected, error)
- SettingsState - Settings state management

**Features:**
- FlutterSecureStorage for secure credential storage
- X-API-Key header authentication (replaced Bearer token)
- Real-time connection health checks
- Material Design form validation

**Tests:** 6 Django + 27 Flutter tests (Session 102)

---

### Session 107: Donkey Cockpit v1 (Unified Home) ⭐ NEW!
**Directory:** `lib/features/cockpit/`

**Screen:**
- **DonkeyCockpitScreen** (640 lines) - Unified command center replacing HomeScreen
  - Welcome header with "Command Center" branding
  - 4 main cards: Leadership, Projects, Video Studio, System
  - Pull-to-refresh for all data sources
  - 6 navigation buttons to all major features
  - Material Design 3 with stat chips
  - Graceful degradation when APIs fail

**Card Structure:**
1. **Leadership & Decisions**
   - Stats from `leadershipStatsProvider` (total decisions, override rate, success rate)
   - Navigate to LeadershipDashboard (Session 104)
   - Start Boardroom Meeting (Session 100)

2. **Projects & Sessions**
   - Stats from `projectsProvider` (active projects, recent activity)
   - Navigate to ProjectListScreen (Session 101)

3. **Video Studio & Renders**
   - Stats from `renderJobListProvider` (active jobs, recent renders)
   - Navigate to VideoStudioScreen (Session 106)
   - Navigate to RenderJobsScreen (Session 105)

4. **System & Agents**
   - Static stats (v1: "10+" agents, "34" features)
   - Navigate to SettingsScreen (Session 102)

**Integration:**
- Replaced HomeScreen as app entry point in `app.dart`
- Added named route `/cockpit`
- ConsumerStatefulWidget with initState for data fetching
- Pull-to-refresh refreshes all 3 providers simultaneously

**Tests:** 38 structural tests (Session 107)
- Welcome Header (1 test)
- Leadership & Decisions card (8 tests)
- Projects & Sessions card (6 tests)
- Video Studio & Renders card (8 tests)
- System & Agents card (4 tests)
- Pull-to-Refresh (2 tests)
- Data Initialization (2 tests)
- Navigation Integration (2 tests)
- UI Styling (4 tests)
- Error Handling (3 tests)

**Documentation:** `/docs/SESSION_107_DONKEY_COCKPIT_V1.md` (380+ lines)

---

### Session 105-106: Video Render Pipeline
**Directory:** `lib/features/render/`

#### Backend (Session 105)
**Django RenderJob API:**
- `POST /api/v1/render-jobs/create/` - Create render job with Resolve Node dispatch
- `GET /api/v1/render-jobs/<uuid>/` - Get job status (live polling of Resolve Node)
- `GET /api/v1/render-jobs/` - List user's render jobs with filtering

**RenderJob Model:**
- Status flow: `queued` → `dispatching` → `rendering` → `done`/`error`
- Progress tracking (0.0-1.0)
- Auto-generated titles (Session 106): "Session render: {title}"
- Integration with DaVinci Resolve Node (Session 103)

#### Mobile Screens (Session 105-106)

1. **VideoStudioScreen** (Session 106 - 444 lines)
   - Main hub for video rendering features
   - **Quick Actions:** View Queue, New Render (info dialog)
   - **Recent Renders:** Last 5 jobs with status, progress, error states
   - **Coming Soon:** 5 future features (batch rendering, templates, notifications, analytics, settings)
   - Pull-to-refresh support
   - Material Design 3 with status color-coding

2. **RenderJobDetailScreen** (Session 105)
   - Live job status with 3-second polling
   - Real-time progress updates
   - Status cards (queued, dispatching, rendering, done, error)
   - Download button when complete (url_launcher)
   - Automatic polling cleanup on dispose

3. **RenderJobsScreen** (Session 105)
   - List all user's render jobs
   - Optional project filtering
   - Pull-to-refresh
   - Status badges with color-coded icons
   - Progress bars for active jobs
   - Error messages for failed jobs

**Integration:**
- SessionAssetsScreen (Session 105): Added "Render Video" FAB when assets exist
- Navigates to RenderJobDetailScreen with initialJob (no flicker)

**Models:**
- RenderJob (Freezed) - Job status, progress, title, timestamps
- RenderJobStatus enum - 5 states with colors and icons

**Providers:**
- renderApiProvider - RenderApi service
- renderJobProvider (family) - Single job tracking with live polling
- renderJobListProvider - Job list management
- createRenderJobProvider - Job creation function

**APIs:**
- POST /api/v1/render-jobs/create/ - Create with sessionId, projectId?, timeline Name?, template?
- GET /api/v1/render-jobs/<uuid>/ - Get with backend→node polling
- GET /api/v1/render-jobs/?project_id=<uuid>&limit=20 - List with filters

**Tests:** 73 comprehensive tests (Session 106)
- 21 RenderJob model tests (serialization, getters, edge cases)
- 27 RenderApi service tests (create, get, list, poll, errors)
- 25 VideoStudioScreen widget tests (Quick Actions, Recent Renders, Coming Soon)

---

## 📦 Dependencies

### Production
```yaml
# State Management
flutter_riverpod: ^2.4.0           # Reactive state management
riverpod_annotation: ^2.3.0        # Code generation support

# Networking
http: ^1.1.0                        # HTTP client
dio: ^5.3.3                         # Advanced HTTP client with interceptors

# JSON Serialization
json_annotation: ^4.8.1             # JSON annotations
freezed_annotation: ^2.4.1          # Immutable data classes

# Local Storage
shared_preferences: ^2.2.2          # Key-value storage
flutter_secure_storage: ^9.0.0      # Secure storage for tokens

# Environment Configuration
flutter_dotenv: ^5.1.0              # .env file support

# UI Components
cupertino_icons: ^1.0.6             # iOS-style icons
intl: ^0.18.1                       # Internationalization and date formatting
cached_network_image: ^3.3.0        # Efficient image loading (Session 101)
url_launcher: ^6.2.0                 # Open URLs in browser (Session 106)
video_player: ^2.8.1                 # Video playback with controls (Session 111)
```

### Development
```yaml
# Code Generation
build_runner: ^2.4.6                # Build system
json_serializable: ^6.7.1           # JSON code generation
riverpod_generator: ^2.3.0          # Riverpod code generation
freezed: ^2.4.5                     # Freezed code generation

# Linting
flutter_lints: ^3.0.0               # Official Flutter lints

# Testing
flutter_test: sdk: flutter          # Flutter testing framework
```

---

## 🔄 State Management (Riverpod)

### Provider Hierarchy

```dart
// API Clients
apiClientProvider              // ApiClient instance
projectsApiProvider            // ProjectsApi instance
boardroomApiProvider          // BoardroomApi instance
coleadershipApiProvider       // ColeadershipApi instance

// Project/Session Data
projectsProvider                                  // FutureProvider<List<Project>>
  └─> projectProvider(projectId)                 // FutureProvider.family<Project, String>
      └─> projectSessionsProvider(projectId)     // FutureProvider.family<List<AISession>, String>
          └─> sessionAssetsProvider(sessionId)   // FutureProvider.family<SessionAssetsResponse, String>

// Leadership Data (Session 99 + Session 108)
leadershipStatsProvider                         // FutureProvider<LeadershipStats>
decisionsListProvider                           // FutureProvider<List<CoLeadershipDecision>>
decisionDetailProvider(decisionId)              // FutureProvider.family<CoLeadershipDecisionDetail, String>
coLeadershipPreferencesProvider                 // FutureProvider<CoLeadershipPreferences>
updatePreferencesProvider                       // Provider<Future<CoLeadershipPreferences> Function()>
decisionCommitControllerProvider                // StateNotifierProvider<DecisionCommitController, DecisionCommitState>
outcomeLogControllerProvider                    // StateNotifierProvider<OutcomeLogController, OutcomeLogState>
```

### Provider Pattern

**Example: Loading Projects**
```dart
final projectsProvider = FutureProvider<List<Project>>((ref) async {
  final api = ref.watch(projectsApiProvider);
  return await api.getProjects();
});

// In UI:
final projectsAsync = ref.watch(projectsProvider);

projectsAsync.when(
  loading: () => CircularProgressIndicator(),
  error: (error, stack) => ErrorWidget(),
  data: (projects) => ProjectGrid(projects),
)
```

---

## 🎨 UI Architecture

### Theme System

**Location:** `lib/core/app_theme.dart`

**Colors:**
```dart
primaryColor: Color(0xFF673AB7)      // Deep Purple
accentColor: Color(0xFF9C27B0)       // Purple
errorColor: Color(0xFFD32F2F)        // Red
textPrimary: Color(0xFF212121)       // Almost Black
textSecondary: Color(0xFF757575)     // Gray
```

**Components:**
- Material Design 3
- Consistent button styles
- Card elevation and shadows
- Typography hierarchy

---

## 🌐 API Integration

### Base Configuration

**Location:** `lib/core/api_config.dart`

```dart
class ApiConfig {
  static String get baseUrl => env['API_BASE_URL'] ?? 'http://localhost:8000';

  // Endpoints
  static const projectsEndpoint = '/api/creative-projects/';
  static const sessionsEndpoint = '/api/v1/sessions/';
  static const coleadershipEndpoint = '/api/v1/coleadership/';
  static const boardroomEndpoint = '/api/v1/coleadership/boardroom/';
}
```

### HTTP Client

**Location:** `lib/core/api_client.dart`

**Features:**
- Authentication token injection
- Error handling
- Request/response logging
- Timeout configuration
- Retry logic

---

## 🌟 Golden Paths (Session 110)

**Purpose:** Official demo-ready user flows that showcase the platform's unique value in 5-10 minutes.

### Golden Path #1: Strategic Decision Loop
**Tagline:** AI-Human Co-Leadership: Collaborative Decision-Making with Outcome Tracking

**Entry Point:** Donkey Cockpit → Strategic Co-Leadership Card → "Start Boardroom Meeting"

**Flow:**
```
1. DonkeyCockpitScreen → Tap "Start Boardroom Meeting"
2. BoardroomFormScreen → Enter topic, submit
3. DecisionDetailScreen → Review AI agent recommendations (CTO, COO, PM)
4. DecisionCommitScreen → Commit decision with justification
5. DecisionDetailScreen → Log outcome when ready
6. LeadershipDashboard → View stats and reflection
```

**Demo Duration:** 4-6 minutes

**Value Shown:**
- AI and human work as equals
- Full accountability (outcomes tracked and attributed)
- Learning loop (system gets smarter over time)

### Golden Path #2: Idea to Publish-Ready Assets
**Tagline:** One-Tap Creative Workflows: From Concept to Professional Content

**Entry Point:** Donkey Cockpit → Creative Pipelines Card → "Idea → Images" or "View All Pipelines"

**Flow:**
```
1. DonkeyCockpitScreen → Tap "Idea → Images" shortcut
2. PipelinesScreen → View "Idea to Image Set" template
3. LaunchPipelineDialog → Enter idea and parameters, launch
4. PipelineRunDetailScreen → Watch live progress (3-second polling)
5. Outputs Card → View generated images and prompts
6. Recent Runs Tab → See completed run history
```

**Demo Duration:** 2-4 minutes (including 45-60 seconds of actual execution)

**Value Shown:**
- One-tap workflows (vs manual multi-step processes)
- Real AI service orchestration (GPT-4o + Stability AI)
- 45-second execution (vs 30+ minutes manual)

**Setup:** Run `python manage.py seed_golden_path_demo` to create demo data for both paths.

---

## 📱 Screen Flow

### Main Navigation Flow (Session 107+110: Updated with Creative Pipelines)

```
DonkeyCockpitScreen (Unified Home - Session 107)
  ├─> Leadership Card
  │   ├─> "Open Leadership Cockpit"
  │   │     └─> LeadershipDashboard (Session 104)
  │   │           └─> Can navigate to projects/sessions
  │   │
  │   └─> "Start Boardroom Meeting"
  │         └─> BoardroomFormScreen
  │               └─> BoardroomResultScreen
  │                     └─> "Open Leadership Decision" (Session 108)
  │                           └─> DecisionDetailScreen
  │                                 ├─> Commit decision form
  │                                 └─> Log outcome form
  │
  │ (NEW: Session 108)
  │   └─> DecisionsListScreen (accessible from Leadership Dashboard)
  │         └─> DecisionDetailScreen
  │               ├─> View agent recommendations
  │               ├─> Commit human decision (if not committed)
  │               ├─> Log outcome (if committed but no outcome)
  │               └─> See "I Told You So" reflection (if triggered)
  │
  ├─> Projects Card
  │   └─> "Open Project Browser" (Session 101)
  │         └─> ProjectListScreen
  │               └─> ProjectDetailScreen
  │                     └─> SessionAssetsScreen
  │                           ├─> AssetGrid
  │                           │     └─> AssetViewer (full-screen)
  │                           │
  │                           └─> "Render Video" FAB (Session 105)
  │                                 └─> RenderJobDetailScreen
  │
  ├─> Video Studio Card (Session 106)
  │   ├─> "Open Video Studio"
  │   │     └─> VideoStudioScreen
  │   │           ├─> Recent Renders → RenderJobDetailScreen
  │   │           └─> "View Queue" → RenderJobsScreen
  │   │
  │   └─> "View Render Queue"
  │         └─> RenderJobsScreen
  │               └─> Tap job → RenderJobDetailScreen
  │
  └─> System Card
      └─> "Settings" (Session 102 + Session 108)
            └─> SettingsScreen
                  ├─> API configuration & connection testing
                  └─> "Co-Leadership Preferences" (Session 108)
                        └─> CoLeadershipSettingsScreen
                              ├─> Allow "I Told You So" reflections
                              └─> Communication tone (serious/playful)
```

---

## 🧪 Testing Strategy

### Test Organization

```
test/
├── models/                    # Model tests
│   └── asset_models_test.dart
├── services/                  # API service tests
│   └── projects_api_test.dart
└── features/                  # Widget/integration tests
    └── project_list_screen_test.dart
```

### Test Coverage (Session 101)

**Model Tests (6 tests):**
- ImageAsset JSON serialization
- VideoAsset JSON serialization
- SessionAssetsResponse parsing
- Null handling

**API Tests (6 tests):**
- Get projects
- Get project detail
- Get project sessions
- Get session assets
- Error handling
- Timeout handling

**Widget Tests (6 tests):**
- Loading states
- Empty states
- Error states
- Data rendering
- Pull-to-refresh
- Navigation

**Total:** 18 tests ✅

---

## 🏗️ Code Generation

### Freezed Models

**Pattern:**
```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'model_name.freezed.dart';
part 'model_name.g.dart';

@freezed
class ModelName with _$ModelName {
  const factory ModelName({
    required String id,
    String? optionalField,
  }) = _ModelName;

  factory ModelName.fromJson(Map<String, dynamic> json) =>
      _$ModelNameFromJson(json);
}
```

**Generate:**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

**Watch:**
```bash
flutter pub run build_runner watch
```

---

## 🔐 Environment Configuration

### .env File

**Location:** `mobile/.env` (NOT in git)

```env
API_BASE_URL=http://localhost:8000

# iOS Simulator: Use Mac's IP address
# API_BASE_URL=http://192.168.1.100:8000

# Android Emulator: Use special IP
# API_BASE_URL=http://10.0.2.2:8000
```

**Usage in Code:**
```dart
import 'package:flutter_dotenv/flutter_dotenv.dart';

final baseUrl = env['API_BASE_URL'];
```

---

## 📊 Performance Optimizations

1. **Lazy Loading**
   - GridView.builder for efficient list rendering
   - Only visible items are built

2. **Image Caching**
   - cached_network_image for automatic caching
   - Reduces network requests

3. **Provider Caching**
   - Riverpod caches provider results
   - Automatic invalidation on refresh

4. **Code Generation**
   - Freezed generates optimized code
   - JSON serialization is fast

5. **Efficient State Management**
   - Riverpod rebuilds only affected widgets
   - No unnecessary rebuilds

---

## 🚀 Build and Deploy

### Development Build

```bash
flutter run
# or
flutter run -d <device-id>
```

### Debug Build

```bash
# iOS
flutter build ios --debug

# Android
flutter build apk --debug
```

### Release Build

```bash
# iOS (requires Mac + Xcode)
flutter build ios --release

# Android
flutter build apk --release
flutter build appbundle --release  # For Google Play
```

---

## 📚 Documentation

- **README.md** - Overview and quick start
- **BUILD_INSTRUCTIONS.md** - Detailed build instructions
- **MOBILE_STRUCTURE.md** - This file
- **/docs/SESSION_100_UNIFIED_SYSTEM_INTEGRATION.md** - Session 100: Boardroom + Co-Leadership
- **/docs/SESSION_101_PROJECT_BROWSER.md** - Session 101: Project Browser
- **/docs/SESSION_102_AUTH_AND_SETTINGS.md** - Session 102: Auth & Settings
- **/docs/SESSION_104_LEADERSHIP_COCKPIT.md** - Session 104: Leadership Dashboard
- **/docs/SESSION_105_RENDER_PIPELINE_MVP.md** - Session 105: Render Backend
- **/docs/SESSION_106_VIDEO_STUDIO_V1.md** - Session 106: Video Studio
- **/docs/SESSION_107_DONKEY_COCKPIT_V1.md** - Session 107: Donkey Cockpit
- **/docs/SESSION_108_COLEADERSHIP_MOBILE_UI.md** - Session 108: Co-Leadership Mobile UI ⭐ NEW!

---

## 🎯 Development Workflow

### 1. Create New Feature

```bash
# 1. Create feature directory
mkdir -p lib/features/my_feature

# 2. Create screen file
touch lib/features/my_feature/my_feature_screen.dart

# 3. Create model (if needed)
touch lib/models/my_model.dart

# 4. Create provider (if needed)
touch lib/providers/my_feature_provider.dart

# 5. Generate code
flutter pub run build_runner build --delete-conflicting-outputs

# 6. Create tests
touch test/features/my_feature_screen_test.dart

# 7. Run tests
flutter test
```

### 2. Modify Models

```bash
# 1. Edit model file
# 2. Run code generation
flutter pub run build_runner build --delete-conflicting-outputs

# 3. Restart app (hot restart won't pick up generated code)
flutter run
```

### 3. Add Dependencies

```bash
# 1. Add to pubspec.yaml
# 2. Get packages
flutter pub get

# 3. If dependency requires code generation
flutter pub run build_runner build --delete-conflicting-outputs
```

---

## 🐛 Common Issues and Solutions

### Issue: "Waiting for another flutter command"

```bash
killall -9 dart
flutter pub get
```

### Issue: Build errors after pulling new code

```bash
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### Issue: Images not loading

- Check API_BASE_URL in .env
- For iOS Simulator: Use Mac's IP, not localhost
- For Android Emulator: Use 10.0.2.2

### Issue: Tests failing

```bash
# Run specific test
flutter test test/features/project_list_screen_test.dart

# Run with verbose output
flutter test --verbose
```

---

## 📈 Future Enhancements

### Planned Features
- [ ] Video playback (currently shows placeholder)
- [ ] Favorite toggle (wire to backend)
- [ ] Create/edit project forms
- [ ] Search and filter projects
- [ ] Sort options
- [ ] Share assets
- [ ] Download to device
- [ ] Offline mode
- [ ] Push notifications
- [ ] Analytics

### Technical Improvements
- [ ] Pagination for large datasets
- [ ] Infinite scroll
- [ ] Background sync
- [ ] Image optimization
- [ ] Video streaming

---

**Structure Version:** 3.1
**Last Updated:** Session 112 - November 15, 2025
**Maintained By:** Claude Code + Chris Partnership 🤝

**"Unified command center with your personal AI assistant!"** 🏗️💬✨

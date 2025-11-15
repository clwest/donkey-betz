# DonkeyOS Flutter Mobile - Project Structure

**Last Updated:** Session 102 - November 15, 2025
**Status:** Complete ✅ (with Auth & Settings)

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
│   │   ├── boardroom_meeting.dart   # Boardroom meeting models
│   │   ├── coleadership.dart        # Decision/outcome models
│   │   ├── connection_status.dart   # Connection status enum (Session 102)
│   │   └── settings_state.dart      # Settings state models (Session 102)
│   │
│   ├── providers/                    # Riverpod state providers
│   │   ├── api_provider.dart        # API client providers (Session 102: uses settings)
│   │   ├── projects_provider.dart   # Project/session/assets providers
│   │   ├── boardroom_provider.dart  # Boardroom state
│   │   ├── coleadership_provider.dart  # Co-leadership state
│   │   └── settings_provider.dart   # Settings state + storage (Session 102)
│   │
│   ├── services/                     # API service layer
│   │   └── api/
│   │       ├── projects_api.dart    # Projects, sessions, assets API
│   │       ├── boardroom_api.dart   # Boardroom API calls
│   │       └── coleadership_api.dart  # Co-leadership API
│   │
│   ├── features/                     # UI screens by feature
│   │   ├── home/
│   │   │   └── home_screen.dart     # Main dashboard (Session 102: Settings icon)
│   │   │
│   │   ├── projects/                # Session 101: Project Browser
│   │   │   ├── project_list_screen.dart       # Browse all projects
│   │   │   ├── project_detail_screen.dart     # Project + sessions
│   │   │   ├── session_assets_screen.dart     # View session assets
│   │   │   └── widgets/
│   │   │       ├── asset_grid.dart            # Image/video grid
│   │   │       └── asset_viewer.dart          # Full-screen viewer
│   │   │
│   │   ├── settings/                # Session 102: Auth & Connection Settings
│   │   │   └── settings_screen.dart           # API config + testing
│   │   │
│   │   ├── boardroom/
│   │   │   ├── boardroom_form_screen.dart     # Start meeting
│   │   │   └── boardroom_result_screen.dart   # Meeting results
│   │   │
│   │   ├── coleadership/
│   │   │   ├── decision_commit_screen.dart    # Commit decisions
│   │   │   └── outcome_screen.dart            # Log outcomes
│   │   │
│   │   └── leadership/
│   │       └── leadership_dashboard.dart  # Leadership stats (future)
│   │
│   ├── app.dart                      # App configuration
│   └── main.dart                     # Entry point
│
├── test/                             # Tests (Session 101, 102)
│   ├── models/
│   │   ├── asset_models_test.dart   # Asset model serialization tests (Session 101)
│   │   └── settings_models_test.dart  # Settings model tests (Session 102)
│   ├── providers/
│   │   └── settings_provider_test.dart  # Settings provider tests (Session 102)
│   ├── services/
│   │   └── projects_api_test.dart   # API integration tests
│   └── features/
│       ├── project_list_screen_test.dart  # Project browser widget tests (Session 101)
│       └── settings_screen_test.dart      # Settings UI widget tests (Session 102)
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

### Session 100 Part 13: Co-Leadership Features
**Directory:** `lib/features/boardroom/` and `lib/features/coleadership/`

**Screens:**
- BoardroomFormScreen - Start executive meetings
- BoardroomResultScreen - View meeting perspectives
- DecisionCommitScreen - Commit human decisions
- OutcomeScreen - Log decision outcomes

**Models:**
- BoardroomMeeting
- ExecutivePerspective
- Decision
- Outcome

**APIs:**
- `POST /api/v1/coleadership/boardroom/start/`
- `POST /api/v1/coleadership/decisions/{id}/human_decision/`
- `POST /api/v1/coleadership/decisions/{id}/outcome/`

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

// Leadership Data
leadershipStatsProvider        // FutureProvider<LeadershipStats>
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

## 📱 Screen Flow

### Main Navigation Flow

```
Home Screen
  ├─> "Start Executive Meeting"
  │     └─> BoardroomFormScreen
  │           └─> BoardroomResultScreen
  │                 └─> DecisionCommitScreen
  │                       └─> OutcomeScreen
  │
  └─> "Browse Projects" (Session 101)
        └─> ProjectListScreen
              └─> ProjectDetailScreen
                    └─> SessionAssetsScreen
                          └─> AssetGrid
                                └─> AssetViewer (full-screen)
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
- **/docs/SESSION_101_PROJECT_BROWSER.md** - Session 101 documentation

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

**Structure Version:** 2.0
**Last Updated:** Session 101 - November 15, 2025
**Maintained By:** Claude Code + Chris Partnership 🤝

**"Clean structure, clean code, clean mind!"** 🏗️✨

# DonkeyOS Flutter Cockpit - Phase 1 Implementation Plan

**Date:** November 15, 2025
**Status:** Ready to Implement
**Backend Reality Score:** 95% Complete ✅

---

## Executive Summary

The Django backend is **95% ready** for Flutter integration! Almost all required APIs already exist from Sessions 96-100. We only need to create **1 new endpoint** for standalone boardroom meeting creation.

### Backend Status
- ✅ **Projects API** - Complete (Session 60)
- ✅ **Sessions API** - Complete (Session 96-97)
- ✅ **Co-Leadership API** - Complete (Session 99)
- ✅ **Leadership Dashboard API** - Complete (Session 100 Part 11)
- ⚠️  **Boardroom Start Endpoint** - Need to create (30 min)

---

## Phase 0: Backend Completion (30 minutes)

### Create Boardroom Start Endpoint

**File:** `coleadership/views.py` (add new view)

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_boardroom_meeting(request):
    """
    Start an executive boardroom meeting via REST API.

    POST body:
    {
        "topic": "Q4 Product Launch Strategy",
        "project_id": "uuid-optional",
        "participants": ["CTOAgent", "CFOAgent", "MarketingAgent"]
    }

    Returns:
    {
        "success": true,
        "topic": "Q4 Product Launch Strategy",
        "project_id": "uuid",
        "participants": ["CTOAgent", "CFOAgent"],
        "agent_responses": {
            "CTOAgent": "Technical perspective...",
            "CFOAgent": "Financial analysis..."
        },
        "summary": "The executive team discussed...",
        "decisions": ["Launch in Q4", "Budget: $50K"],
        "action_items": [
            {
                "task": "Prepare technical roadmap",
                "owner": "CTOAgent",
                "priority": "high"
            }
        ],
        "session_id": "uuid",
        "decision_id": "uuid"
    }
    """
```

**Implementation:**
1. Extract topic, project_id (optional), participants from request.data
2. Call MeetingCoordinatorAgent.start_meeting()
3. Create CoLeadershipDecision record
4. Log agent recommendations
5. Return complete meeting data

**URL:** Add to `coleadership/urls.py`:
```python
path('boardroom/start/', start_boardroom_meeting, name='start-boardroom-meeting'),
```

---

## Phase 1: Backend API Reference

### 1. Projects API

**Base URL:** `/api/creative-projects/`

#### List Projects
```http
GET /api/creative-projects/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "project_id": "uuid",
      "name": "Brand Launch Campaign",
      "description": "Complete branding package",
      "goal": "Establish brand identity",
      "status": "in_progress",
      "category": "Branding",
      "tags": ["branding", "logo", "social"],
      "is_quick_starts": false,
      "created_at": "2025-11-15T10:00:00Z",
      "deadline": "2025-12-31T23:59:59Z"
    }
  ]
}
```

#### Get Project Sessions
```http
GET /api/v1/sessions/project/{project_id}/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": "uuid",
    "name": "Brand Launch Campaign"
  },
  "sessions": [
    {
      "session_id": "uuid",
      "title": "CTO and COO Meeting",
      "session_type": "boardroom",
      "participants": ["CTOAgent", "COOAgent"],
      "meeting_topic": "Technical architecture decision",
      "created_at": "2025-11-15T10:00:00Z",
      "total_images": 0,
      "total_videos": 0,
      "total_audio": 0
    }
  ]
}
```

---

### 2. Boardroom Meeting API

**Base URL:** `/api/v1/boardroom/`

#### Start Meeting (NEW - TO BE CREATED)
```http
POST /api/v1/boardroom/start/
Authorization: Bearer {token}
Content-Type: application/json

{
  "topic": "Q4 Product Launch Strategy",
  "project_id": "uuid-optional",
  "participants": ["CTOAgent", "CFOAgent", "MarketingAgent"]
}
```

**Response:**
```json
{
  "success": true,
  "topic": "Q4 Product Launch Strategy",
  "project_id": "uuid",
  "participants": ["CTOAgent", "CFOAgent", "MarketingAgent"],
  "agent_responses": {
    "CTOAgent": "From a technical standpoint, I recommend...",
    "CFOAgent": "Financially, we need to consider...",
    "MarketingAgent": "Market positioning suggests..."
  },
  "summary": "The executive team discussed the Q4 product launch...",
  "decisions": [
    "Launch in Q4 2025",
    "Allocate $50K budget"
  ],
  "action_items": [
    {
      "task": "Prepare technical roadmap",
      "owner": "CTOAgent",
      "priority": "high"
    },
    {
      "task": "Finalize budget allocation",
      "owner": "CFOAgent",
      "priority": "high"
    }
  ],
  "met_at": "2025-11-15T10:30:00Z",
  "session_id": "uuid",
  "decision_id": "uuid"
}
```

#### List Meetings (EXISTING)
```http
GET /api/leadership/meetings/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "meetings": [
    {
      "key": "shared_memory:agent:meeting_coordinator:boardroom_meeting_20251115_103000",
      "topic": "Q4 Product Launch Strategy",
      "participants": ["CTOAgent", "CFOAgent"],
      "met_at": "2025-11-15T10:30:00Z",
      "summary": "The executive team discussed...",
      "decision_count": 2,
      "action_item_count": 3,
      "project_id": "uuid"
    }
  ],
  "total": 1
}
```

#### Get Meeting Details (EXISTING)
```http
GET /api/leadership/meetings/{meeting_key}/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "meeting": {
    "topic": "Q4 Product Launch Strategy",
    "participants": ["CTOAgent", "CFOAgent"],
    "agent_responses": {
      "CTOAgent": "Full perspective...",
      "CFOAgent": "Full analysis..."
    },
    "summary": "Complete summary...",
    "decisions": ["Decision 1", "Decision 2"],
    "action_items": [
      {
        "task": "Task description",
        "owner": "CTOAgent",
        "priority": "high"
      }
    ],
    "met_at": "2025-11-15T10:30:00Z",
    "project_id": "uuid"
  }
}
```

---

### 3. Co-Leadership API

**Base URL:** `/api/v1/coleadership/`

#### Commit Human Decision (EXISTING)
```http
POST /api/v1/coleadership/decisions/{decision_id}/human_decision/
Authorization: Bearer {token}
Content-Type: application/json

{
  "chosen_path_summary": "I'm going with option B because...",
  "justification": "Market data supports this approach",
  "is_override": true,
  "overridden_agent_id": "cto"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Decision recorded",
  "decision_id": "uuid",
  "frozen_at": "2025-11-15T10:35:00Z",
  "is_override": true
}
```

#### Log Outcome (EXISTING)
```http
POST /api/v1/coleadership/decisions/{decision_id}/outcome/
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "success",
  "outcome_summary": "Product launched successfully with 40% user adoption",
  "attribution": "human",
  "metrics": {
    "user_adoption": 40,
    "revenue_increase": 25
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Outcome recorded",
  "decision_id": "uuid",
  "status": "success",
  "attribution": "human",
  "told_you_so_triggered": false,
  "told_you_so_message": ""
}
```

#### Get Leadership Stats (EXISTING)
```http
GET /api/v1/coleadership/stats/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_decisions": 14,
    "overrides": 6,
    "override_rate": 42.9,
    "ai_correct": 3,
    "human_correct": 5,
    "both_correct": 2,
    "pending": 4,
    "success_rate": 71.4,
    "avg_ai_confidence": 0.78
  }
}
```

---

## Phase 2: Flutter Project Setup

### 1. Create Flutter Project

```bash
flutter create donkey_os_cockpit
cd donkey_os_cockpit
```

### 2. Add Dependencies

**File:** `pubspec.yaml`

```yaml
name: donkey_os_cockpit
description: Mobile cockpit for DonkeyOS AI platform
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter

  # State Management
  flutter_riverpod: ^2.4.0
  riverpod_annotation: ^2.3.0

  # Networking
  http: ^1.1.0
  dio: ^5.3.3  # For advanced HTTP features

  # JSON Serialization
  json_annotation: ^4.8.1
  freezed_annotation: ^2.4.1

  # Local Storage
  shared_preferences: ^2.2.2
  flutter_secure_storage: ^9.0.0

  # Environment Configuration
  flutter_dotenv: ^5.1.0

  # UI
  cupertino_icons: ^1.0.6
  intl: ^0.18.1  # Date formatting

dev_dependencies:
  flutter_test:
    sdk: flutter

  # Code Generation
  build_runner: ^2.4.6
  json_serializable: ^6.7.1
  riverpod_generator: ^2.3.0
  freezed: ^2.4.5

  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
```

### 3. Environment Configuration

**File:** `.env`

```env
# Development
API_BASE_URL=http://localhost:8000

# Production
# API_BASE_URL=https://api.donkeyos.com
```

### 4. Folder Structure

```
lib/
├── core/
│   ├── api_client.dart          # HTTP client wrapper
│   ├── api_config.dart          # Base URL configuration
│   ├── api_interceptors.dart    # Auth, logging interceptors
│   └── app_theme.dart           # Deep purple theme
│
├── models/
│   ├── project.dart             # Project model
│   ├── project.freezed.dart     # Generated
│   ├── project.g.dart           # Generated
│   ├── session.dart             # Session model
│   ├── boardroom_meeting.dart   # Meeting models
│   ├── coleadership_decision.dart
│   ├── leadership_stats.dart
│   └── action_item.dart
│
├── providers/
│   ├── auth_provider.dart       # Auth state
│   ├── projects_provider.dart   # Projects state
│   ├── boardroom_provider.dart  # Boardroom state
│   ├── coleadership_provider.dart
│   └── leadership_provider.dart
│
├── services/
│   ├── api/
│   │   ├── projects_api.dart
│   │   ├── boardroom_api.dart
│   │   ├── coleadership_api.dart
│   │   └── leadership_api.dart
│   └── storage_service.dart     # SharedPreferences wrapper
│
├── features/
│   ├── home/
│   │   ├── home_screen.dart
│   │   └── widgets/
│   │       ├── stats_card.dart
│   │       └── quick_actions.dart
│   │
│   ├── projects/
│   │   ├── projects_screen.dart
│   │   ├── project_detail_screen.dart
│   │   └── widgets/
│   │       ├── project_card.dart
│   │       └── session_list.dart
│   │
│   ├── boardroom/
│   │   ├── boardroom_form_screen.dart
│   │   ├── boardroom_result_screen.dart
│   │   └── widgets/
│   │       ├── participant_selector.dart
│   │       ├── agent_response_card.dart
│   │       └── action_item_card.dart
│   │
│   ├── coleadership/
│   │   ├── decision_commit_screen.dart
│   │   ├── outcome_screen.dart
│   │   └── widgets/
│   │       ├── decision_form.dart
│   │       └── outcome_form.dart
│   │
│   └── leadership/
│       ├── leadership_screen.dart
│       └── widgets/
│           ├── stats_overview.dart
│           └── meeting_history_card.dart
│
├── app.dart                     # MaterialApp configuration
└── main.dart                    # Entry point
```

---

## Phase 3: Flutter Models

### Example: Project Model

**File:** `lib/models/project.dart`

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'project.freezed.dart';
part 'project.g.dart';

@freezed
class Project with _$Project {
  const factory Project({
    required String projectId,
    required String name,
    required String description,
    required String goal,
    required String status,
    required String category,
    required List<String> tags,
    required bool isQuickStarts,
    required DateTime createdAt,
    DateTime? deadline,
  }) = _Project;

  factory Project.fromJson(Map<String, dynamic> json) =>
      _$ProjectFromJson(json);
}
```

**Code Generation:**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

---

## Phase 4: Flutter API Client

### API Configuration

**File:** `lib/core/api_config.dart`

```dart
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConfig {
  static String get baseUrl => dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000';

  static const String projectsEndpoint = '/api/creative-projects/';
  static const String sessionsEndpoint = '/api/v1/sessions/';
  static const String boardroomEndpoint = '/api/v1/boardroom/';
  static const String coleadershipEndpoint = '/api/v1/coleadership/';
  static const String leadershipEndpoint = '/api/leadership/';
}
```

### HTTP Client

**File:** `lib/core/api_client.dart`

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_config.dart';

class ApiClient {
  final String? _token;

  ApiClient({String? token}) : _token = token;

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (_token != null) 'Authorization': 'Bearer $_token',
  };

  Future<Map<String, dynamic>> get(String endpoint) async {
    final url = Uri.parse('${ApiConfig.baseUrl}$endpoint');
    final response = await http.get(url, headers: _headers);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        statusCode: response.statusCode,
        message: response.body,
      );
    }
  }

  Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    final url = Uri.parse('${ApiConfig.baseUrl}$endpoint');
    final response = await http.post(
      url,
      headers: _headers,
      body: json.encode(body),
    );

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        statusCode: response.statusCode,
        message: response.body,
      );
    }
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}
```

### Boardroom API Service

**File:** `lib/services/api/boardroom_api.dart`

```dart
import '../../core/api_client.dart';
import '../../core/api_config.dart';
import '../../models/boardroom_meeting.dart';

class BoardroomApi {
  final ApiClient _client;

  BoardroomApi(this._client);

  Future<BoardroomMeetingResult> startMeeting({
    required String topic,
    String? projectId,
    required List<String> participants,
  }) async {
    final response = await _client.post(
      '${ApiConfig.boardroomEndpoint}start/',
      {
        'topic': topic,
        if (projectId != null) 'project_id': projectId,
        'participants': participants,
      },
    );

    return BoardroomMeetingResult.fromJson(response);
  }

  Future<List<BoardroomMeetingSummary>> listMeetings() async {
    final response = await _client.get('${ApiConfig.leadershipEndpoint}meetings/');

    final meetings = response['meetings'] as List;
    return meetings
        .map((m) => BoardroomMeetingSummary.fromJson(m))
        .toList();
  }

  Future<BoardroomMeetingDetail> getMeetingDetails(String meetingKey) async {
    final response = await _client.get(
      '${ApiConfig.leadershipEndpoint}meetings/$meetingKey/',
    );

    return BoardroomMeetingDetail.fromJson(response['meeting']);
  }
}
```

---

## Phase 5: State Management

### Riverpod Providers

**File:** `lib/providers/boardroom_provider.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/boardroom_meeting.dart';
import '../services/api/boardroom_api.dart';

// API client provider
final boardroomApiProvider = Provider<BoardroomApi>((ref) {
  // Get API client from auth provider
  final client = ref.watch(apiClientProvider);
  return BoardroomApi(client);
});

// Meeting result state
class BoardroomState {
  final bool isLoading;
  final BoardroomMeetingResult? result;
  final String? error;

  BoardroomState({
    this.isLoading = false,
    this.result,
    this.error,
  });

  BoardroomState copyWith({
    bool? isLoading,
    BoardroomMeetingResult? result,
    String? error,
  }) {
    return BoardroomState(
      isLoading: isLoading ?? this.isLoading,
      result: result ?? this.result,
      error: error,
    );
  }
}

// Boardroom controller
class BoardroomController extends StateNotifier<BoardroomState> {
  final BoardroomApi _api;

  BoardroomController(this._api) : super(BoardroomState());

  Future<void> startMeeting({
    required String topic,
    String? projectId,
    required List<String> participants,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await _api.startMeeting(
        topic: topic,
        projectId: projectId,
        participants: participants,
      );

      state = state.copyWith(
        isLoading: false,
        result: result,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void clearResult() {
    state = BoardroomState();
  }
}

// Provider
final boardroomControllerProvider =
    StateNotifierProvider<BoardroomController, BoardroomState>((ref) {
  final api = ref.watch(boardroomApiProvider);
  return BoardroomController(api);
});
```

---

## Phase 6: UI Screens

### Home Screen

**File:** `lib/features/home/home_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/leadership_provider.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final leadershipStats = ref.watch(leadershipStatsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('DonkeyOS Cockpit'),
        backgroundColor: Theme.of(context).colorScheme.primary,
      ),
      body: leadershipStats.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
        data: (stats) => RefreshIndicator(
          onRefresh: () => ref.refresh(leadershipStatsProvider.future),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Greeting
              _buildGreetingCard(context),
              const SizedBox(height: 16),

              // Quick Actions
              _buildQuickActionsCard(context),
              const SizedBox(height: 16),

              // Stats Snapshot
              _buildStatsSnapshot(context, stats),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGreetingCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Welcome to Your AI Executive Team',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Human-AI Co-Leadership Dashboard',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionsCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            ElevatedButton.icon(
              onPressed: () => Navigator.pushNamed(context, '/boardroom'),
              icon: const Icon(Icons.meeting_room),
              label: const Text('Start Executive Meeting'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 50),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsSnapshot(BuildContext context, LeadershipStats stats) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Leadership Stats',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _StatCard(
                title: 'Total Decisions',
                value: stats.totalDecisions.toString(),
                icon: Icons.analytics,
                color: Colors.blue,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                title: 'Overrides',
                value: '${stats.overrideRate.toStringAsFixed(1)}%',
                icon: Icons.alt_route,
                color: Colors.orange,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _StatCard(
                title: 'AI Correct',
                value: stats.aiCorrect.toString(),
                icon: Icons.smart_toy,
                color: Colors.purple,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                title: 'Human Correct',
                value: stats.humanCorrect.toString(),
                icon: Icons.person,
                color: Colors.amber,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.bodySmall,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## Phase 7: Testing Strategy

### Widget Tests

**File:** `test/widgets/boardroom_result_screen_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/features/boardroom/boardroom_result_screen.dart';
import 'package:donkey_os_cockpit/models/boardroom_meeting.dart';

void main() {
  group('BoardroomResultScreen', () {
    testWidgets('displays meeting topic and summary', (WidgetTester tester) async {
      final meeting = BoardroomMeetingResult(
        topic: 'Test Meeting',
        participants: ['CTOAgent', 'CFOAgent'],
        agentResponses: {
          'CTOAgent': 'Technical perspective',
          'CFOAgent': 'Financial perspective',
        },
        summary: 'Test summary',
        decisions: ['Decision 1'],
        actionItems: [],
        sessionId: 'test-session',
        decisionId: 'test-decision',
        metAt: DateTime.now(),
      );

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: BoardroomResultScreen(meeting: meeting),
          ),
        ),
      );

      expect(find.text('Test Meeting'), findsOneWidget);
      expect(find.text('Test summary'), findsOneWidget);
      expect(find.text('CTOAgent'), findsOneWidget);
      expect(find.text('CFOAgent'), findsOneWidget);
    });
  });
}
```

### JSON Parsing Tests

**File:** `test/models/boardroom_meeting_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:donkey_os_cockpit/models/boardroom_meeting.dart';

void main() {
  group('BoardroomMeetingResult', () {
    test('fromJson parses correctly', () {
      final json = {
        'topic': 'Test Meeting',
        'participants': ['CTOAgent'],
        'agent_responses': {'CTOAgent': 'Response'},
        'summary': 'Summary',
        'decisions': ['Decision 1'],
        'action_items': [
          {'task': 'Task 1', 'owner': 'CTOAgent', 'priority': 'high'}
        ],
        'session_id': 'session-123',
        'decision_id': 'decision-123',
        'met_at': '2025-11-15T10:00:00Z',
      };

      final meeting = BoardroomMeetingResult.fromJson(json);

      expect(meeting.topic, 'Test Meeting');
      expect(meeting.participants, ['CTOAgent']);
      expect(meeting.actionItems.length, 1);
      expect(meeting.actionItems[0].priority, 'high');
    });
  });
}
```

---

## Phase 8: Timeline & Deliverables

### Week 1: Backend & Foundation (Days 1-2)
- ✅ **Day 1 Morning:** Create `/api/v1/boardroom/start/` endpoint (30 min)
- ✅ **Day 1 Afternoon:** Test all endpoints manually with Postman (1 hour)
- ✅ **Day 2:** Flutter project setup, dependencies, folder structure (4 hours)

### Week 2: Models & API Layer (Days 3-5)
- ✅ **Day 3:** Define all Flutter models with Freezed (Project, Session, Meeting, etc.) (6 hours)
- ✅ **Day 4:** Build API client layer and services (6 hours)
- ✅ **Day 5:** Set up Riverpod providers and state management (6 hours)

### Week 3: UI Screens (Days 6-10)
- ✅ **Day 6:** Home screen + Stats cards (4 hours)
- ✅ **Day 7:** Projects screen + Project detail (6 hours)
- ✅ **Day 8:** Boardroom Form + Result screens (6 hours)
- ✅ **Day 9:** Decision Commit + Outcome screens (6 hours)
- ✅ **Day 10:** Leadership Dashboard screen (4 hours)

### Week 4: Testing & Polish (Days 11-14)
- ✅ **Day 11:** Widget tests for all screens (4 hours)
- ✅ **Day 12:** JSON parsing tests for all models (2 hours)
- ✅ **Day 13:** End-to-end manual testing (4 hours)
- ✅ **Day 14:** Polish, bug fixes, documentation (4 hours)

**Total Time:** ~14 days (56 hours)

---

## Phase 9: Success Criteria

### MVP Complete When:
1. ✅ User can login
2. ✅ User can view list of projects
3. ✅ User can see project details with sessions
4. ✅ User can start an executive meeting
5. ✅ User can see all agent perspectives
6. ✅ User can commit their decision
7. ✅ User can log outcome
8. ✅ User can view leadership stats
9. ✅ All widget tests pass
10. ✅ Manual E2E flow works without errors

---

## Non-Goals for Phase 1

**DO NOT implement:**
- ❌ Image/video generation UI
- ❌ Audio generation UI
- ❌ Character training UI
- ❌ Content gallery views
- ❌ Assistant chat interface
- ❌ Agent directory view
- ❌ WebSocket real-time updates
- ❌ Push notifications
- ❌ Offline mode
- ❌ Multi-user collaboration

**These are Phase 2+ features.**

---

## Next Steps

1. **Create the boardroom start endpoint** (30 minutes)
2. **Test with Postman/curl** (15 minutes)
3. **Set up Flutter project** (1 hour)
4. **Start implementing models** (Day 3)

---

**Document Version:** 1.0
**Created:** November 15, 2025
**Author:** Claude Code + Chris Partnership 🤝

# Session 112: Personal Assistant Mobile MVP

**Date:** November 16, 2025
**Status:** 🚧 IN PROGRESS
**Goal:** Add Personal Assistant chat to Flutter mobile app

---

## 🎯 Objectives

1. ✅ Survey backend Personal Assistant APIs
2. 🚧 Create Flutter data layer (models, API client, providers)
3. ⏳ Build chat UI screen
4. ⏳ Add to Donkey Cockpit navigation
5. ⏳ Write tests and documentation

---

## 📡 Backend API Survey

### Existing Endpoints

The Personal Assistant APIs already exist in Django:

#### 1. **POST `/api/assistant/chat/`**
Main chat endpoint for sending messages to the assistant.

**Request:**
```json
{
  "message": "User's message text",
  "context": {}  // Optional additional context
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Assistant's response text",
    "confidence": 0.95,
    "context_used": {...},
    "suggested_actions": [...]
  }
}
```

**Implementation:** `core/views_personal_assistant.py:chat_with_assistant()`
- Uses `PersonalAIAssistant` class (cached per user for 30 minutes)
- Processes message with user context and learning
- Returns formatted response with confidence and suggestions

#### 2. **GET `/api/assistant/context/`**
Get personalized context for the current user.

**Response:**
```json
{
  "success": true,
  "context": {
    "user_preferences": {...},
    "recent_activity": [...],
    "personalization_level": "high"
  }
}
```

**Implementation:** `core/views_personal_assistant.py:get_assistant_context()`

#### 3. **GET `/api/assistant/learning/`**
Get summary of what assistant has learned about user.

**Response:**
```json
{
  "success": true,
  "summary": {
    "skills_learned": [...],
    "preferences_learned": [...],
    "total_interactions": 142
  }
}
```

**Implementation:** `core/views_personal_assistant.py:get_learning_summary()`

#### 4. **POST `/api/assistant/feedback/`**
Provide feedback on assistant responses.

**Request:**
```json
{
  "message_id": "uuid",
  "feedback": "positive" | "negative",
  "details": "Optional feedback details"
}
```

**Implementation:** `core/views_personal_assistant.py:provide_feedback()`

#### 5. **POST `/api/assistant/transcribe/`** (Future - Voice)
Voice transcription endpoint (not implemented in MVP).

### Key Observations:

1. **No Conversation History Endpoint:** Backend doesn't expose message history API
   - Assistant maintains state in server-side cache
   - Mobile app will maintain conversation history client-side

2. **Stateful Assistant:** PersonalAIAssistant is cached per user (30 min TTL)
   - Remembers conversation context between requests
   - Uses user profile and learning data

3. **Authentication:** All endpoints require `IsAuthenticated` permission
   - Uses standard authentication middleware
   - Mobile app must send auth headers

4. **Response Format:** Consistent structure across endpoints
   - `success: true/false`
   - `data` or specific field (context, summary)
   - `error` field on failures

---

## 📱 Flutter Architecture

### Data Models (`mobile/lib/models/personal_assistant.dart`)

```dart
/// Chat message model
@freezed
class AssistantMessage with _$AssistantMessage {
  const factory AssistantMessage({
    required String id,
    required String text,
    required bool isUser,
    required DateTime timestamp,
    double? confidence,
    List<String>? suggestedActions,
    Map<String, dynamic>? contextUsed,
  }) = _AssistantMessage;

  factory AssistantMessage.fromJson(Map<String, dynamic> json) =>
      _$AssistantMessageFromJson(json);
}

/// Chat conversation model (client-side state)
@freezed
class AssistantConversation with _$AssistantConversation {
  const factory AssistantConversation({
    @Default([]) List<AssistantMessage> messages,
    DateTime? lastActivity,
    @Default(0) int totalMessages,
  }) = _AssistantConversation;
}

/// Assistant context model
@freezed
class AssistantContext with _$AssistantContext {
  const factory AssistantContext({
    Map<String, dynamic>? userPreferences,
    List<dynamic>? recentActivity,
    String? personalizationLevel,
  }) = _AssistantContext;

  factory AssistantContext.fromJson(Map<String, dynamic> json) =>
      _$AssistantContextFromJson(json);
}

/// Learning summary model
@freezed
class LearningSummary with _$LearningSummary {
  const factory LearningSummary({
    @Default([]) List<String> skillsLearned,
    @Default([]) List<String> preferencesLearned,
    @Default(0) int totalInteractions,
  }) = _LearningSummary;

  factory LearningSummary.fromJson(Map<String, dynamic> json) =>
      _$LearningSummaryFromJson(json);
}
```

### API Client (`mobile/lib/services/api/personal_assistant_api.dart`)

```dart
class PersonalAssistantApi {
  final ApiClient _client;

  PersonalAssistantApi(this._client);

  /// Send message to assistant
  Future<AssistantMessage> sendMessage(String message, {Map<String, dynamic>? context}) async {
    final response = await _client.post(
      '/api/assistant/chat/',
      {
        'message': message,
        if (context != null) 'context': context,
      },
    );

    if (response['success'] == true && response['data'] != null) {
      final data = response['data'];
      return AssistantMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: data['response'],
        isUser: false,
        timestamp: DateTime.now(),
        confidence: data['confidence']?.toDouble(),
        suggestedActions: (data['suggested_actions'] as List?)?.cast<String>(),
        contextUsed: data['context_used'],
      );
    }

    throw ApiException(
      message: 'Failed to get response from assistant',
      details: response,
    );
  }

  /// Get assistant context
  Future<AssistantContext> getContext() async {
    final response = await _client.get('/api/assistant/context/');

    if (response['success'] == true && response['context'] != null) {
      return AssistantContext.fromJson(response['context']);
    }

    throw ApiException(
      message: 'Failed to get assistant context',
      details: response,
    );
  }

  /// Get learning summary
  Future<LearningSummary> getLearningSummary() async {
    final response = await _client.get('/api/assistant/learning/');

    if (response['success'] == true && response['summary'] != null) {
      return LearningSummary.fromJson(response['summary']);
    }

    throw ApiException(
      message: 'Failed to get learning summary',
      details: response,
    );
  }

  /// Provide feedback on a message
  Future<void> provideFeedback(String messageId, bool isPositive, {String? details}) async {
    final response = await _client.post(
      '/api/assistant/feedback/',
      {
        'message_id': messageId,
        'feedback': isPositive ? 'positive' : 'negative',
        if (details != null) 'details': details,
      },
    );

    if (response['success'] != true) {
      throw ApiException(
        message: 'Failed to provide feedback',
        details: response,
      );
    }
  }
}
```

### Riverpod Providers (`mobile/lib/providers/personal_assistant_provider.dart`)

```dart
/// Assistant API provider
final personalAssistantApiProvider = Provider<PersonalAssistantApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return PersonalAssistantApi(client);
});

/// Chat conversation state provider (client-side history)
final assistantConversationProvider = StateNotifierProvider<AssistantConversationNotifier, AssistantConversation>((ref) {
  return AssistantConversationNotifier(ref);
});

/// Assistant context provider
final assistantContextProvider = FutureProvider<AssistantContext>((ref) async {
  final api = ref.watch(personalAssistantApiProvider);
  return await api.getContext();
});

/// Learning summary provider
final learningSummaryProvider = FutureProvider<LearningSummary>((ref) async {
  final api = ref.watch(personalAssistantApiProvider);
  return await api.getLearningSummary();
});

/// Conversation notifier for managing chat state
class AssistantConversationNotifier extends StateNotifier<AssistantConversation> {
  final Ref _ref;

  AssistantConversationNotifier(this._ref) : super(const AssistantConversation());

  Future<void> sendMessage(String text) async {
    // Add user message immediately
    final userMessage = AssistantMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: text,
      isUser: true,
      timestamp: DateTime.now(),
    );

    state = state.copyWith(
      messages: [...state.messages, userMessage],
    );

    try {
      // Get assistant response
      final api = _ref.read(personalAssistantApiProvider);
      final assistantMessage = await api.sendMessage(text);

      // Add assistant message
      state = state.copyWith(
        messages: [...state.messages, assistantMessage],
        lastActivity: DateTime.now(),
        totalMessages: state.totalMessages + 2,
      );
    } catch (e) {
      // Handle error - could add error message to chat
      rethrow;
    }
  }

  void clearConversation() {
    state = const AssistantConversation();
  }
}
```

---

## 🎨 UI Design

### PersonalAssistantScreen Layout

```
┌─────────────────────────────────┐
│ Personal Assistant     [≡] [⟳]  │ AppBar (menu, refresh)
├─────────────────────────────────┤
│                                 │
│  👤 Hi! How can I help?         │ Initial greeting (system)
│                                 │
│  ┌─────────────────────────┐   │ User message bubble (right)
│  │ What projects am I      │   │
│  │ working on?             │   │
│  └─────────────────────────┘   │
│                                 │
│ 🤖 You have 5 active projects:  │ Assistant message (left)
│    • Brand Launch Campaign      │
│    • Client Portfolio           │
│    • Social Media Series        │
│    [View All Projects →]        │ Suggested action chip
│                                 │
│  ┌─────────────────────────┐   │
│  │ Tell me more about the  │   │
│  │ Brand Launch Campaign   │   │
│  └─────────────────────────┘   │
│                                 │
│ 🤖 The Brand Launch Campaign... │
│    ⋮                            │ (Scrollable content)
│                                 │
├─────────────────────────────────┤
│ Type a message...        [🎤]  │ Input field + mic (stub)
└─────────────────────────────────┘
```

### UI Components:

1. **Message Bubbles**
   - User: Right-aligned, blue background
   - Assistant: Left-aligned, gray background
   - Avatar icons (👤/🤖)
   - Timestamp below
   - Confidence indicator for assistant (optional)

2. **Suggested Action Chips**
   - Display below assistant messages if provided
   - Tappable to auto-fill or navigate
   - Example: "View Projects", "Create Image", "Check Revenue"

3. **Input Bar**
   - TextField with hint text
   - Send button (enabled when text present)
   - Mic button (shows "Coming soon" toast for MVP)

4. **Loading State**
   - Typing indicator (animated dots) when waiting for response
   - Shown as temporary message in chat

5. **Error Handling**
   - Error message shown as system message (red background)
   - Retry button
   - Network connectivity check

6. **Empty State**
   - Welcome message on first load
   - Conversation starters as suggestion chips
   - Example: "Tell me about my projects", "What can you do?"

---

## 🔧 Implementation Plan

### Phase 1: Data Layer ✅
1. Create `personal_assistant.dart` with Freezed models
2. Run `build_runner` to generate code
3. Create `personal_assistant_api.dart` with API methods
4. Create `personal_assistant_provider.dart` with Riverpod state
5. Add providers to `api_provider.dart`

### Phase 2: UI Layer ⏳
1. Create `PersonalAssistantScreen` in `features/assistant/`
2. Implement chat ListView with reversed scroll
3. Build message bubble widgets
4. Add input TextField and send button
5. Add mic button (stub with toast)
6. Implement loading indicator
7. Handle errors gracefully

### Phase 3: Navigation ⏳
1. Add Personal Assistant card to Donkey Cockpit
2. Show total interactions count (from learning summary)
3. Primary action: "Open Chat"
4. Wire up navigation route

### Phase 4: Testing ⏳
1. API client tests (mock responses)
2. Provider notifier tests
3. Widget test for PersonalAssistantScreen
4. Smoke test: send message → receive response

---

## 🚀 Future Enhancements (Not in MVP)

1. **Voice Input** - Implement `/api/assistant/transcribe/` endpoint
2. **Conversation Search** - Search through message history
3. **Message Persistence** - Save conversation to local storage
4. **Deep Links** - Launch assistant with pre-filled query
5. **Rich Responses** - Support markdown, images, links
6. **Typing Indicator** - Real-time indication of assistant typing
7. **Multi-Session** - Support multiple conversation sessions
8. **Export Chat** - Download conversation as text/PDF
9. **Customization** - Choose assistant personality/avatar
10. **Feedback UI** - Thumbs up/down on messages

---

## 📊 Success Criteria

**MVP Must Have:**
- ✅ User can send text message
- ✅ User receives AI-generated response
- ✅ Conversation displays in chat UI
- ✅ Messages persist during app session
- ✅ Error states handled gracefully
- ✅ Accessible from Donkey Cockpit
- ✅ Mic button present (stub)

**Nice to Have:**
- Suggested action chips work
- Confidence displayed on responses
- Loading indicator while processing
- Smooth scroll animations
- Empty state with conversation starters

---

## 🧪 Testing Instructions

### Backend Test:
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/assistant/chat/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test context endpoint
curl http://localhost:8000/api/assistant/context/ \
  -H "Authorization: Bearer <token>"
```

### Mobile Test:
```bash
cd mobile
flutter test

# Run app
flutter run

# In app:
1. Go to Donkey Cockpit
2. Tap "Personal Assistant"
3. Type "What projects am I working on?"
4. Verify response appears
5. Send another message
6. Verify conversation history maintained
```

---

## 📁 Files to Create/Modify

### New Files:
- `mobile/lib/models/personal_assistant.dart` (~120 lines)
- `mobile/lib/services/api/personal_assistant_api.dart` (~150 lines)
- `mobile/lib/providers/personal_assistant_provider.dart` (~100 lines)
- `mobile/lib/features/assistant/personal_assistant_screen.dart` (~400 lines)
- `mobile/test/services/personal_assistant_api_test.dart` (~80 lines)
- `mobile/test/providers/personal_assistant_provider_test.dart` (~60 lines)

### Modified Files:
- `mobile/lib/providers/api_provider.dart` (add provider)
- `mobile/lib/features/cockpit/donkey_cockpit_screen.dart` (add card)
- `mobile/MOBILE_STRUCTURE.md` (document new feature)
- `docs/SESSION_112_PERSONAL_ASSISTANT_MOBILE.md` (this file)

**Estimated Total:** ~900 lines of production code + ~150 lines of tests

---

## 💡 Key Implementation Notes

1. **Client-Side History:** Since backend doesn't expose message history endpoint, maintain conversation in Flutter state
2. **Session Management:** Backend uses 30-min cache TTL, mobile should match or handle stale sessions
3. **Error Recovery:** Network errors should allow retry without losing conversation
4. **Performance:** Use ListView.builder with reversed scroll for efficient rendering
5. **Authentication:** Ensure ApiClient sends proper auth headers (X-API-Key)

---

**Status:** 🚧 IN PROGRESS
**Next Steps:** Create Freezed models and run build_runner

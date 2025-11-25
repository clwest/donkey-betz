# Personal Assistant Mobile Integration Plan

**Session:** 111
**Status:** PLANNING ONLY - Ready for Implementation
**Estimated Effort:** 2-3 hours for MVP

---

## 🎯 Goal

Bring the Personal AI Assistant to the Flutter mobile app, enabling users to:
- Chat with their personalized AI assistant
- View conversation history
- Get context-aware responses based on user profile and learning
- Provide feedback on responses
- (Future) Use voice input for queries

---

## 📡 Backend APIs (Already Exist!)

### Main Chat Endpoint
```
POST /api/assistant/chat/
```

**Request:**
```json
{
  "message": "User's message",
  "context": {} // Optional additional context
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Assistant's response",
    "confidence": 0.95,
    "context_used": {...},
    "suggested_actions": [...]
  }
}
```

### Get Assistant Context
```
GET /api/assistant/context/
```

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

### Get Learning Summary
```
GET /api/assistant/learning/
```

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

### Provide Feedback
```
POST /api/assistant/feedback/
```

**Request:**
```json
{
  "message_id": "uuid",
  "feedback": "positive" | "negative",
  "details": "Optional feedback text"
}
```

### Voice Input (Future)
```
POST /api/assistant/transcribe/
```

**Request:** Multipart form with audio file

---

## 📱 Proposed Flutter Structure

### 1. Data Models (`mobile/lib/models/assistant.dart`)

```dart
/// Chat message model
@freezed
class ChatMessage with _$ChatMessage {
  const factory ChatMessage({
    required String id,
    required String text,
    required bool isUser,
    required DateTime timestamp,
    double? confidence,
    List<String>? suggestedActions,
    Map<String, dynamic>? metadata,
  }) = _ChatMessage;

  factory ChatMessage.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageFromJson(json);
}

/// Chat conversation model
@freezed
class ChatConversation with _$ChatConversation {
  const factory ChatConversation({
    @Default([]) List<ChatMessage> messages,
    DateTime? lastActivity,
    int? totalMessages,
  }) = _ChatConversation;
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

### 2. API Client (`mobile/lib/services/api/assistant_api.dart`)

```dart
class AssistantApi {
  final ApiClient _client;

  AssistantApi(this._client);

  /// Send message to assistant
  Future<ChatMessage> sendMessage(String message, {Map<String, dynamic>? context}) async {
    final response = await _client.post(
      '/api/assistant/chat/',
      {
        'message': message,
        if (context != null) 'context': context,
      },
    );

    if (response['success'] == true && response['data'] != null) {
      final data = response['data'];
      return ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: data['response'],
        isUser: false,
        timestamp: DateTime.now(),
        confidence: data['confidence']?.toDouble(),
        suggestedActions: (data['suggested_actions'] as List?)?.cast<String>(),
        metadata: data['context_used'],
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

### 3. Riverpod Providers (`mobile/lib/providers/assistant_provider.dart`)

```dart
/// Assistant API provider
final assistantApiProvider = Provider<AssistantApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return AssistantApi(client);
});

/// Chat conversation state provider
final chatConversationProvider = StateNotifierProvider<ChatNotifier, ChatConversation>((ref) {
  return ChatNotifier(ref);
});

/// Assistant context provider
final assistantContextProvider = FutureProvider<AssistantContext>((ref) async {
  final api = ref.watch(assistantApiProvider);
  return await api.getContext();
});

/// Learning summary provider
final learningSummaryProvider = FutureProvider<LearningSummary>((ref) async {
  final api = ref.watch(assistantApiProvider);
  return await api.getLearningSummary();
});

/// Chat notifier for managing conversation state
class ChatNotifier extends StateNotifier<ChatConversation> {
  final Ref _ref;

  ChatNotifier(this._ref) : super(const ChatConversation());

  Future<void> sendMessage(String text) async {
    // Add user message immediately
    final userMessage = ChatMessage(
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
      final api = _ref.read(assistantApiProvider);
      final assistantMessage = await api.sendMessage(text);

      // Add assistant message
      state = state.copyWith(
        messages: [...state.messages, assistantMessage],
        lastActivity: DateTime.now(),
        totalMessages: (state.totalMessages ?? 0) + 2,
      );
    } catch (e) {
      // Handle error - could add error message to chat
      rethrow;
    }
  }

  void clearConversation() {
    state = const ChatConversation();
  }
}
```

### 4. UI Screen (`mobile/lib/features/assistant/personal_assistant_screen.dart`)

**Layout:**
```
┌─────────────────────────────────┐
│ Personal Assistant     [Info] [•] │ AppBar
├─────────────────────────────────┤
│                                 │
│  👤 How can I help you today?   │ System message
│                                 │
│  ┌─────────────────────────┐   │
│  │ What projects am I      │   │ User message
│  │ working on?             │   │
│  └─────────────────────────┘   │
│                                 │
│ 🤖 You have 5 active projects:  │ Assistant message
│    • Brand Launch Campaign      │
│    • Client Portfolio           │
│    • Social Media Series        │
│    ...                          │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Show me the latest      │   │ User message
│  │ creative assets         │   │
│  └─────────────────────────┘   │
│                                 │
│ 🤖 Here are your recent...      │ Assistant message (with suggested actions)
│    [View Gallery] [Create More] │
│                                 │
├─────────────────────────────────┤
│ [Message input field]    [🎤]  │ Input bar
└─────────────────────────────────┘
```

**Key UI Components:**
1. **Message List** - Scrollable chat interface
2. **Message Bubbles** - Distinct styling for user vs assistant
3. **Input Field** - Text input with send button
4. **Mic Button** - Voice input (future feature, show as disabled for MVP)
5. **Action Chips** - Suggested actions from assistant
6. **Loading Indicator** - Show when waiting for response
7. **Context Drawer** - Show learning summary and preferences (optional)

**Features:**
- Auto-scroll to latest message
- Pull-to-refresh to reload context
- Tap message for details (confidence, metadata)
- Long-press for feedback (thumbs up/down)
- Haptic feedback on send

### 5. Integration Points

**From Donkey Cockpit:**
- Add "Personal Assistant" card (similar to other cards)
- Show: Total interactions count, personalization level
- Primary action: "Open Assistant"

**From Other Screens:**
- "Ask Assistant" quick action button (floating action button)
- Deep link with pre-filled questions:
  - From Projects: "Tell me about [project name]"
  - From Galleries: "Create something like [asset]"
  - From Co-Leadership: "Explain this decision"

**Integration with Existing Features:**
- **Memory System:** Assistant already uses user preferences/learning
- **Co-Leadership:** Can reference decisions and outcomes
- **Projects:** Can query project status and sessions
- **Galleries:** Can suggest content creation based on history

---

## 🚀 Implementation Phases

### Phase 1: MVP (2-3 hours)
1. Create data models (Freezed) - 30 min
2. Create API client - 30 min
3. Create Riverpod providers - 30 min
4. Create basic chat screen UI - 60 min
5. Add to Donkey Cockpit - 15 min
6. Basic testing - 15 min

**MVP Deliverables:**
- ✅ Send/receive messages
- ✅ Display conversation history
- ✅ Basic chat UI
- ✅ Access from Donkey Cockpit

### Phase 2: Enhanced Features (1-2 hours)
1. Add suggested action chips - 20 min
2. Add message feedback (thumbs up/down) - 20 min
3. Show confidence levels - 15 min
4. Add learning summary view - 30 min
5. Polish UI and animations - 15 min

### Phase 3: Advanced Features (Future)
1. Voice input integration
2. Multi-modal responses (images, videos, links)
3. Conversation search
4. Export conversation
5. Customizable assistant personality

---

## 📋 Technical Considerations

### State Management
- Use `StateNotifier` for chat conversation (mutable state)
- Use `FutureProvider` for context/learning summary (cached data)
- Local message storage for offline persistence (optional)

### Performance
- Pagination for long conversations (load in chunks)
- Debounce typing indicator
- Cancel in-flight requests if new message sent
- Cache assistant responses locally

### Error Handling
- Show retry button on failed messages
- Graceful degradation if context unavailable
- Timeout handling for slow responses
- Network connectivity checks

### Accessibility
- Screen reader support for messages
- Keyboard navigation
- High contrast mode support
- Text scaling support

### Testing Strategy
1. **Unit Tests:**
   - Message serialization/deserialization
   - API client methods
   - Provider state changes

2. **Widget Tests:**
   - Message bubble rendering
   - Send button enabled/disabled states
   - Error state display

3. **Integration Tests:**
   - End-to-end message flow
   - Context loading
   - Feedback submission

---

## 🎨 UI/UX Design Notes

### Message Styling
- **User messages:** Right-aligned, blue bubble
- **Assistant messages:** Left-aligned, gray bubble with AI icon
- **System messages:** Centered, light gray text
- **Timestamps:** Small, gray text below message
- **Confidence:** Progress bar or percentage badge (optional)

### Animations
- Fade in new messages
- Typing indicator (3 animated dots)
- Smooth scroll to new messages
- Bounce on send button tap

### Empty States
- Welcome message on first load
- Conversation starters as chips
- "No internet" state
- "Service unavailable" state

---

## 🔗 Dependencies

**Flutter Packages (likely already in pubspec.yaml):**
- `flutter_riverpod` - State management ✅
- `freezed` - Data models ✅
- `json_serializable` - JSON parsing ✅
- `http` - API calls ✅
- `intl` - Date formatting ✅
- (Future) `speech_to_text` - Voice input
- (Future) `flutter_markdown` - Formatted responses

**Backend Dependencies:**
- None! All APIs already exist ✅

---

## 🎯 Success Criteria

**MVP Success:**
- [ ] User can send message from mobile app
- [ ] User receives AI-generated response
- [ ] Conversation persists during session
- [ ] Error states handled gracefully
- [ ] Accessible from Donkey Cockpit

**Enhanced Success:**
- [ ] Suggested actions work correctly
- [ ] Feedback system functional
- [ ] Learning summary displayed
- [ ] Smooth, polished UX

**Advanced Success:**
- [ ] Voice input working
- [ ] Conversation search implemented
- [ ] Offline mode functional
- [ ] Deep links from other screens working

---

## 📝 Next Steps (When Ready to Implement)

1. **Create branch:** `feature/session-112-personal-assistant-mobile`
2. **Create models:** Start with `assistant.dart` Freezed models
3. **Run build_runner:** Generate Freezed/JSON code
4. **Create API client:** Follow existing patterns (ProjectsApi, GalleryApi)
5. **Create providers:** Chat state + context providers
6. **Create UI:** Start with minimal chat screen
7. **Add to Cockpit:** Wire up navigation
8. **Test end-to-end:** Send message → receive response
9. **Polish:** Add animations, suggested actions, feedback
10. **Document:** Update MOBILE_STRUCTURE.md

---

## 💡 Key Insights

1. **Backend is ready!** All APIs already exist - no backend work needed
2. **Follow existing patterns** - GalleryApi/ProjectsApi structure works perfectly
3. **Start minimal** - Basic chat UI first, enhance later
4. **Leverage learning** - Assistant already knows user preferences
5. **Mobile-first UX** - Optimize for one-handed use, quick interactions

---

**Status:** READY FOR IMPLEMENTATION
**Next Session:** Session 112 - Personal Assistant Mobile MVP

**Estimated Total Time:** 2-3 hours for complete MVP

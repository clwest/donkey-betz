/// Personal Assistant Providers
///
/// Session 112: Personal Assistant Mobile MVP
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/personal_assistant.dart';
import 'api_provider.dart';

/// Chat conversation state provider (client-side history)
final assistantConversationProvider =
    StateNotifierProvider<AssistantConversationNotifier, AssistantConversation>(
  (ref) {
    return AssistantConversationNotifier(ref);
  },
);

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
  bool _isSending = false;

  AssistantConversationNotifier(this._ref)
      : super(const AssistantConversation());

  /// Send a message to the assistant
  Future<void> sendMessage(String text) async {
    if (_isSending) return; // Prevent duplicate sends
    _isSending = true;

    try {
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
      // Add error message to conversation
      final errorMessage = AssistantMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: 'Sorry, I encountered an error: ${e.toString()}',
        isUser: false,
        timestamp: DateTime.now(),
      );

      state = state.copyWith(
        messages: [...state.messages, errorMessage],
      );

      rethrow;
    } finally {
      _isSending = false;
    }
  }

  /// Clear conversation history
  void clearConversation() {
    state = const AssistantConversation();
  }

  /// Add a system message (for UI feedback)
  void addSystemMessage(String text) {
    final systemMessage = AssistantMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: text,
      isUser: false,
      timestamp: DateTime.now(),
    );

    state = state.copyWith(
      messages: [...state.messages, systemMessage],
    );
  }

  /// Add a message directly to conversation (Session 113: for voice input)
  void addMessage(AssistantMessage message) {
    state = state.copyWith(
      messages: [...state.messages, message],
      lastActivity: DateTime.now(),
      totalMessages: state.totalMessages + 1,
    );
  }

  /// Get whether currently sending a message
  bool get isSending => _isSending;
}

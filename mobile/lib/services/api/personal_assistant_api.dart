/// Personal Assistant API Client
///
/// Session 112: Personal Assistant Mobile MVP
library;

import '../../core/api_client.dart';
import '../../models/personal_assistant.dart';

class PersonalAssistantApi {
  final ApiClient _client;

  PersonalAssistantApi(this._client);

  /// Send message to assistant and get response
  Future<AssistantMessage> sendMessage(
    String message, {
    Map<String, dynamic>? context,
  }) async {
    try {
      final response = await _client.post(
        '/api/assistant/chat/',
        {
          'message': message,
          if (context != null) 'context': context,
        },
      );

      if (response['success'] == true && response['data'] != null) {
        final data = response['data'];

        // Backend returns 'suggestions' and 'actions', combine them
        List<String>? suggestedActions;
        final suggestions = data['suggestions'] as List?;
        final actions = data['actions'] as List?;

        if (suggestions != null || actions != null) {
          suggestedActions = [
            ...?suggestions?.map((e) => e.toString()),
            ...?actions?.map((e) => e.toString()),
          ];
        }

        // Create assistant message from response
        return AssistantMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: data['response'] ?? '',
          isUser: false,
          timestamp: DateTime.now(),
          confidence: data['confidence']?.toDouble(),
          suggestedActions: suggestedActions,
          contextUsed: data['context_used'] as Map<String, dynamic>?,
        );
      }

      throw ApiException(
        message: 'Failed to get response from assistant',
        details: response,
      );
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Failed to send message',
        details: {'error': e.toString()},
      );
    }
  }

  /// Get assistant context for current user
  Future<AssistantContext> getContext() async {
    try {
      final response = await _client.get('/api/assistant/context/');

      if (response['success'] == true && response['context'] != null) {
        return AssistantContext.fromJson(
          response['context'] as Map<String, dynamic>,
        );
      }

      throw ApiException(
        message: 'Failed to get assistant context',
        details: response,
      );
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Failed to get context',
        details: {'error': e.toString()},
      );
    }
  }

  /// Get learning summary showing what assistant knows about user
  Future<LearningSummary> getLearningSummary() async {
    try {
      final response = await _client.get('/api/assistant/learning/');

      if (response['success'] == true && response['summary'] != null) {
        return LearningSummary.fromJson(
          response['summary'] as Map<String, dynamic>,
        );
      }

      throw ApiException(
        message: 'Failed to get learning summary',
        details: response,
      );
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Failed to get learning summary',
        details: {'error': e.toString()},
      );
    }
  }

  /// Provide feedback on an assistant response
  Future<void> provideFeedback(
    String messageId,
    bool isPositive, {
    String? details,
  }) async {
    try {
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
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Failed to provide feedback',
        details: {'error': e.toString()},
      );
    }
  }
}

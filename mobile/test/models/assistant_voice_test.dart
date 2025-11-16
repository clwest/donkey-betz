/// Tests for Assistant Voice Models
///
/// Session 113: Voice Input MVP
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:donkey_os_cockpit/models/assistant_voice.dart';
import 'package:donkey_os_cockpit/models/personal_assistant.dart';

void main() {
  group('AssistantVoiceResult', () {
    test('fromJson creates instance correctly', () {
      final json = {
        'success': true,
        'user_text': 'Create a logo',
        'assistant_message': {
          'response': 'I can help with that',
          'suggestions': ['Generate', 'See examples'],
          'actions': ['start_project'],
          'confidence': 0.95,
          'ai_generated': true,
          'model': 'gpt-5-mini',
        },
      };

      final result = AssistantVoiceResult.fromJson(json);

      expect(result.success, true);
      expect(result.userText, 'Create a logo');
      expect(result.assistantMessage.response, 'I can help with that');
    });

    test('handles error case', () {
      final json = {
        'success': false,
        'user_text': 'Test',
        'assistant_message': {
          'response': 'Error occurred',
        },
        'error': 'Transcription failed',
      };

      final result = AssistantVoiceResult.fromJson(json);

      expect(result.success, false);
      expect(result.error, 'Transcription failed');
    });
  });

  group('AssistantMessageData', () {
    test('fromJson creates instance correctly', () {
      final json = {
        'response': 'Test response',
        'suggestions': ['Suggestion 1', 'Suggestion 2'],
        'actions': ['Action 1'],
        'confidence': 0.9,
        'ai_generated': true,
        'model': 'gpt-5',
      };

      final data = AssistantMessageData.fromJson(json);

      expect(data.response, 'Test response');
      expect(data.suggestions, ['Suggestion 1', 'Suggestion 2']);
      expect(data.actions, ['Action 1']);
      expect(data.confidence, 0.9);
      expect(data.aiGenerated, true);
      expect(data.model, 'gpt-5');
    });

    test('toAssistantMessage converts correctly', () {
      final data = AssistantMessageData(
        response: 'Test response',
        suggestions: ['Sug 1', 'Sug 2'],
        actions: ['Action 1'],
        confidence: 0.85,
      );

      final message = data.toAssistantMessage();

      expect(message.text, 'Test response');
      expect(message.isUser, false);
      expect(message.confidence, 0.85);
      expect(message.suggestedActions, ['Sug 1', 'Sug 2', 'Action 1']);
    });

    test('toAssistantMessage handles null suggestions and actions', () {
      final data = AssistantMessageData(
        response: 'Simple response',
      );

      final message = data.toAssistantMessage();

      expect(message.text, 'Simple response');
      expect(message.isUser, false);
      expect(message.suggestedActions, null);
    });

    test('toAssistantMessage handles only suggestions', () {
      final data = AssistantMessageData(
        response: 'Response',
        suggestions: ['Only suggestion'],
      );

      final message = data.toAssistantMessage();

      expect(message.suggestedActions, ['Only suggestion']);
    });

    test('toAssistantMessage handles only actions', () {
      final data = AssistantMessageData(
        response: 'Response',
        actions: ['Only action'],
      );

      final message = data.toAssistantMessage();

      expect(message.suggestedActions, ['Only action']);
    });
  });
}

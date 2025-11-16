/// Tests for PersonalAssistantApi
///
/// Session 112: Personal Assistant Mobile MVP
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:donkey_os_cockpit/services/api/personal_assistant_api.dart';
import 'package:donkey_os_cockpit/models/personal_assistant.dart';
import 'package:donkey_os_cockpit/core/api_client.dart' show ApiClient, ApiException;

class MockApiClient extends ApiClient {
  MockApiClient() : super(baseUrl: 'http://test', apiKey: 'test-key');

  Map<String, dynamic>? nextResponse;
  Exception? nextError;
  String? lastPath;
  Map<String, dynamic>? lastBody;

  @override
  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body) async {
    lastPath = path;
    lastBody = body;
    if (nextError != null) {
      throw nextError!;
    }
    if (nextResponse != null) {
      return nextResponse!;
    }
    throw Exception('No mock response configured');
  }

  @override
  Future<Map<String, dynamic>> get(String path) async {
    lastPath = path;
    if (nextError != null) {
      throw nextError!;
    }
    if (nextResponse != null) {
      return nextResponse!;
    }
    throw Exception('No mock response configured');
  }
}

void main() {
  group('PersonalAssistantApi', () {
    late MockApiClient mockClient;
    late PersonalAssistantApi api;

    setUp(() {
      mockClient = MockApiClient();
      api = PersonalAssistantApi(mockClient);
    });

    tearDown(() {
      mockClient.nextResponse = null;
      mockClient.nextError = null;
    });

    group('sendMessage', () {
      test('sends POST request to /api/assistant/chat/', () async {
        mockClient.nextResponse = {
          'success': true,
          'data': {
            'response': 'Hello! How can I help you?',
            'confidence': 0.95,
            'suggested_actions': ['Tell me more', 'Start a project'],
            'context_used': {'user_preferences': {}},
          }
        };

        await api.sendMessage('Hello');

        expect(mockClient.lastPath, '/api/assistant/chat/');
        expect(mockClient.lastBody, {'message': 'Hello'});
      });

      test('returns AssistantMessage on success', () async {
        mockClient.nextResponse = {
          'success': true,
          'data': {
            'response': 'Hello! How can I help you?',
            'confidence': 0.95,
          }
        };

        final message = await api.sendMessage('Hello');

        expect(message.text, 'Hello! How can I help you?');
        expect(message.isUser, false);
        expect(message.confidence, 0.95);
      });

      test('includes suggested actions when present', () async {
        mockClient.nextResponse = {
          'success': true,
          'data': {
            'response': 'I can help with that',
            'suggested_actions': ['Action 1', 'Action 2'],
          }
        };

        final message = await api.sendMessage('Help me');

        expect(message.suggestedActions, ['Action 1', 'Action 2']);
      });

      test('throws ApiException on failure', () async {
        mockClient.nextResponse = {
          'success': false,
          'error': 'Something went wrong',
        };

        expect(
          () => api.sendMessage('Hello'),
          throwsA(isA<ApiException>()),
        );
      });
    });

    group('getContext', () {
      test('sends GET request and returns AssistantContext on success', () async {
        mockClient.nextResponse = {
          'success': true,
          'context': {
            'user_preferences': {'theme': 'dark'},
            'recent_activity': ['project_1'],
            'personalization_level': 'advanced',
          }
        };

        final context = await api.getContext();

        expect(mockClient.lastPath, '/api/assistant/context/');
        expect(context.userPreferences, {'theme': 'dark'});
        expect(context.recentActivity, ['project_1']);
        expect(context.personalizationLevel, 'advanced');
      });
    });

    group('getLearningSummary', () {
      test('sends GET request and returns LearningSummary on success', () async {
        mockClient.nextResponse = {
          'success': true,
          'summary': {
            'skills_learned': ['video editing', 'image generation'],
            'preferences_learned': ['cinematic style'],
            'total_interactions': 42,
          }
        };

        final summary = await api.getLearningSummary();

        expect(mockClient.lastPath, '/api/assistant/learning/');
        expect(summary.skillsLearned, ['video editing', 'image generation']);
        expect(summary.preferencesLearned, ['cinematic style']);
        expect(summary.totalInteractions, 42);
      });
    });

    group('provideFeedback', () {
      test('sends POST request to /api/assistant/feedback/', () async {
        mockClient.nextResponse = {'success': true};

        await api.provideFeedback('msg-123', true, details: 'Very helpful');

        expect(mockClient.lastPath, '/api/assistant/feedback/');
        expect(mockClient.lastBody, {
          'message_id': 'msg-123',
          'feedback': 'positive',
          'details': 'Very helpful',
        });
      });

      test('sends feedback without details', () async {
        mockClient.nextResponse = {'success': true};

        await api.provideFeedback('msg-456', false);

        expect(mockClient.lastBody, {
          'message_id': 'msg-456',
          'feedback': 'negative',
        });
      });
    });
  });
}

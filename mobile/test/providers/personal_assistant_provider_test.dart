/// Tests for Personal Assistant Providers
///
/// Session 112: Personal Assistant Mobile MVP
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/providers/personal_assistant_provider.dart';
import 'package:donkey_os_cockpit/models/personal_assistant.dart';
import 'package:donkey_os_cockpit/services/api/personal_assistant_api.dart';
import 'package:donkey_os_cockpit/core/api_client.dart';
import 'package:donkey_os_cockpit/providers/api_provider.dart' show personalAssistantApiProvider;

class MockPersonalAssistantApi extends PersonalAssistantApi {
  MockPersonalAssistantApi() : super(ApiClient(baseUrl: 'test', apiKey: 'test'));

  AssistantMessage? nextMessage;
  Exception? nextError;

  @override
  Future<AssistantMessage> sendMessage(
    String message, {
    Map<String, dynamic>? context,
  }) async {
    if (nextError != null) {
      throw nextError!;
    }
    return nextMessage ??
        AssistantMessage(
          id: 'test-id',
          text: 'Test response',
          isUser: false,
          timestamp: DateTime.now(),
        );
  }

  @override
  Future<AssistantContext> getContext() async {
    return const AssistantContext();
  }

  @override
  Future<LearningSummary> getLearningSummary() async {
    return const LearningSummary();
  }
}

void main() {
  group('AssistantConversationNotifier', () {
    late ProviderContainer container;
    late MockPersonalAssistantApi mockApi;

    setUp(() {
      mockApi = MockPersonalAssistantApi();
      container = ProviderContainer(
        overrides: [
          personalAssistantApiProvider.overrideWithValue(mockApi),
        ],
      );
    });

    tearDown(() {
      container.dispose();
    });

    test('initial state is empty conversation', () {
      final state = container.read(assistantConversationProvider);
      expect(state.messages, isEmpty);
      expect(state.totalMessages, 0);
      expect(state.lastActivity, isNull);
    });

    test('sendMessage adds user message immediately', () async {
      final notifier = container.read(assistantConversationProvider.notifier);

      // Don't await - check state while sending
      notifier.sendMessage('Hello');

      // Give it a moment to process user message
      await Future.delayed(const Duration(milliseconds: 10));

      final state = container.read(assistantConversationProvider);
      expect(state.messages.length, greaterThan(0));
      expect(state.messages.first.text, 'Hello');
      expect(state.messages.first.isUser, true);
    });

    test('sendMessage adds assistant response', () async {
      mockApi.nextMessage = AssistantMessage(
        id: 'assistant-1',
        text: 'How can I help?',
        isUser: false,
        timestamp: DateTime.now(),
      );

      final notifier = container.read(assistantConversationProvider.notifier);
      await notifier.sendMessage('Hello');

      final state = container.read(assistantConversationProvider);
      expect(state.messages.length, 2);
      expect(state.messages.last.text, 'How can I help?');
      expect(state.messages.last.isUser, false);
      expect(state.totalMessages, 2);
    });

    test('sendMessage updates lastActivity', () async {
      final before = DateTime.now();
      final notifier = container.read(assistantConversationProvider.notifier);
      await notifier.sendMessage('Test');
      final after = DateTime.now();

      final state = container.read(assistantConversationProvider);
      expect(state.lastActivity, isNotNull);
      expect(state.lastActivity!.isAfter(before), true);
      expect(state.lastActivity!.isBefore(after), true);
    });

    test('sendMessage adds error message on failure', () async {
      mockApi.nextError = Exception('Network error');

      final notifier = container.read(assistantConversationProvider.notifier);

      // Expect the error to be thrown
      expect(
        () => notifier.sendMessage('Test'),
        throwsA(isA<Exception>()),
      );

      // Wait for state to update
      await Future.delayed(const Duration(milliseconds: 100));

      final state = container.read(assistantConversationProvider);
      expect(state.messages.length, 2); // User message + error message
      expect(state.messages.last.text, contains('error'));
      expect(state.messages.last.isUser, false);
    });

    test('clearConversation resets state', () async {
      final notifier = container.read(assistantConversationProvider.notifier);

      // Add some messages
      await notifier.sendMessage('Hello');

      // Clear
      notifier.clearConversation();

      final state = container.read(assistantConversationProvider);
      expect(state.messages, isEmpty);
      expect(state.totalMessages, 0);
      expect(state.lastActivity, isNull);
    });

    test('addSystemMessage adds non-user message', () {
      final notifier = container.read(assistantConversationProvider.notifier);

      notifier.addSystemMessage('System notification');

      final state = container.read(assistantConversationProvider);
      expect(state.messages.length, 1);
      expect(state.messages.first.text, 'System notification');
      expect(state.messages.first.isUser, false);
    });

    test('prevents duplicate sends when already sending', () async {
      final notifier = container.read(assistantConversationProvider.notifier);

      // Start two sends rapidly
      final future1 = notifier.sendMessage('Message 1');
      final future2 = notifier.sendMessage('Message 2');

      await Future.wait([future1, future2]);

      final state = container.read(assistantConversationProvider);
      // Should only process first message (user + assistant = 2)
      // Second call should be ignored
      expect(state.messages.length, 2);
    });
  });

  group('learningSummaryProvider', () {
    test('fetches learning summary', () async {
      final container = ProviderContainer(
        overrides: [
          personalAssistantApiProvider.overrideWithValue(MockPersonalAssistantApi()),
        ],
      );

      final summary = await container.read(learningSummaryProvider.future);

      expect(summary, isA<LearningSummary>());
      container.dispose();
    });
  });

  group('assistantContextProvider', () {
    test('fetches assistant context', () async {
      final container = ProviderContainer(
        overrides: [
          personalAssistantApiProvider.overrideWithValue(MockPersonalAssistantApi()),
        ],
      );

      final context = await container.read(assistantContextProvider.future);

      expect(context, isA<AssistantContext>());
      container.dispose();
    });
  });
}

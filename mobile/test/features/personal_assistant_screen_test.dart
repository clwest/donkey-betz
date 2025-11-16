/// Widget Tests for PersonalAssistantScreen
///
/// Session 112: Personal Assistant Mobile MVP
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/features/assistant/personal_assistant_screen.dart';
import 'package:donkey_os_cockpit/providers/personal_assistant_provider.dart';
import 'package:donkey_os_cockpit/models/personal_assistant.dart';

void main() {
  group('PersonalAssistantScreen', () {
    testWidgets('renders empty state initially', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: PersonalAssistantScreen(),
          ),
        ),
      );

      // Check for empty state elements
      expect(find.byIcon(Icons.chat_bubble_outline), findsOneWidget);
      expect(find.text('Hi! I\'m your Personal Assistant'), findsOneWidget);
      expect(find.text('I can help you with your projects, content creation, and more!'), findsOneWidget);
    });

    testWidgets('displays suggestion chips in empty state', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: PersonalAssistantScreen(),
          ),
        ),
      );

      // Check for suggestion chips
      expect(find.byType(ActionChip), findsWidgets);
      expect(find.text('What projects am I working on?'), findsOneWidget);
      expect(find.text('Tell me about my recent work'), findsOneWidget);
    });

    testWidgets('displays text input field and buttons', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: PersonalAssistantScreen(),
          ),
        ),
      );

      // Check for input elements
      expect(find.byType(TextField), findsOneWidget);
      expect(find.byIcon(Icons.mic), findsOneWidget);
      expect(find.byIcon(Icons.send), findsOneWidget);
    });

    testWidgets('shows mic coming soon message when tapped', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: PersonalAssistantScreen(),
          ),
        ),
      );

      // Tap mic button
      await tester.tap(find.byIcon(Icons.mic));
      await tester.pumpAndSettle();

      // Check for snackbar
      expect(find.text('🎤 Voice input coming soon!'), findsOneWidget);
    });

    testWidgets('has app bar with title and actions', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: PersonalAssistantScreen(),
          ),
        ),
      );

      // Check app bar
      expect(find.text('Personal Assistant'), findsOneWidget);
      expect(find.byIcon(Icons.delete_outline), findsOneWidget);
      expect(find.byType(PopupMenuButton<String>), findsOneWidget);
    });

    testWidgets('displays messages when conversation has messages', (WidgetTester tester) async {
      // Create test conversation with messages
      final testConversation = AssistantConversation(
        messages: [
          AssistantMessage(
            id: '1',
            text: 'Hello',
            isUser: true,
            timestamp: DateTime.now(),
          ),
          AssistantMessage(
            id: '2',
            text: 'Hi! How can I help?',
            isUser: false,
            timestamp: DateTime.now(),
          ),
        ],
        totalMessages: 2,
      );

      // Create a container with pre-populated messages
      final container = ProviderContainer(
        overrides: [
          assistantConversationProvider.overrideWith(
            (ref) => _TestConversationNotifier(ref, testConversation),
          ),
        ],
      );

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: const MaterialApp(
            home: PersonalAssistantScreen(),
          ),
        ),
      );

      // Check for messages
      expect(find.text('Hello'), findsOneWidget);
      expect(find.text('Hi! How can I help?'), findsOneWidget);

      // Check for avatars
      expect(find.byIcon(Icons.person), findsOneWidget); // User avatar
      expect(find.byIcon(Icons.smart_toy), findsOneWidget); // Assistant avatar

      container.dispose();
    });

    testWidgets('sends message when send button tapped', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: PersonalAssistantScreen(),
          ),
        ),
      );

      // Enter text
      await tester.enterText(find.byType(TextField), 'Test message');
      await tester.pump();

      // Tap send button
      await tester.tap(find.byIcon(Icons.send));
      await tester.pump();

      // Message should appear in conversation (user message bubble)
      expect(find.text('Test message'), findsWidgets);
    });

    testWidgets('text field is cleared after sending', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: PersonalAssistantScreen(),
          ),
        ),
      );

      // Enter text and send
      await tester.enterText(find.byType(TextField), 'Test message');
      await tester.tap(find.byIcon(Icons.send));
      await tester.pump();

      // Get the text field widget and check its value is empty
      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.controller?.text, isEmpty);
    });
  });
}

// Test notifier that returns a preset state
class _TestConversationNotifier extends AssistantConversationNotifier {
  _TestConversationNotifier(Ref ref, AssistantConversation testState) : super(ref) {
    state = testState;
  }

  @override
  Future<void> sendMessage(String text) async {
    // No-op for testing
  }
}

/// Settings Screen Widget Test
///
/// Session 102 - Mobile Auth & Connection Settings
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:donkey_os_cockpit/features/settings/settings_screen.dart';
import 'package:donkey_os_cockpit/models/settings_state.dart';
import 'package:donkey_os_cockpit/providers/settings_provider.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('SettingsScreen', () {
    testWidgets('renders with default state', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const SettingsScreen(),
          ),
        ),
      );

      // Give providers time to initialize
      await tester.pumpAndSettle();

      // Check for key UI elements
      expect(find.text('Settings'), findsOneWidget);
      expect(find.text('API Endpoint'), findsOneWidget);
      expect(find.text('API Key'), findsOneWidget);
      expect(find.text('Test Connection'), findsOneWidget);
      expect(find.text('Save'), findsOneWidget);
    });

    testWidgets('shows validation errors for empty fields', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const SettingsScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Find and tap the Save button
      final saveButton = find.text('Save');
      expect(saveButton, findsOneWidget);
      await tester.tap(saveButton);
      await tester.pumpAndSettle();

      // Should show validation errors
      expect(find.text('API base URL is required'), findsOneWidget);
      expect(find.text('API key is required'), findsOneWidget);
    });

    testWidgets('validates URL format', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const SettingsScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Enter invalid URL
      final urlField = find.widgetWithText(TextFormField, '');
      await tester.enterText(urlField.first, 'invalid-url');

      // Tap Save
      await tester.tap(find.text('Save'));
      await tester.pumpAndSettle();

      // Should show URL validation error
      expect(
        find.text('URL must start with http:// or https://'),
        findsOneWidget,
      );
    });

    testWidgets('can toggle API key visibility', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const SettingsScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Find the visibility toggle button (suffixIcon of API key field)
      final visibilityButton = find.byIcon(Icons.visibility);
      expect(visibilityButton, findsOneWidget);

      // Tap to toggle
      await tester.tap(visibilityButton);
      await tester.pumpAndSettle();

      // Icon should change to visibility_off
      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
    });

    testWidgets('shows clear settings confirmation dialog', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const SettingsScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Find and tap the clear button (delete icon in app bar)
      final clearButton = find.byIcon(Icons.delete_outline);
      expect(clearButton, findsOneWidget);
      await tester.tap(clearButton);
      await tester.pumpAndSettle();

      // Should show confirmation dialog
      expect(find.text('Clear Settings'), findsWidgets);
      expect(
        find.text(
          'Are you sure you want to clear all settings? This will remove your API endpoint and key.',
        ),
        findsOneWidget,
      );
      expect(find.text('Cancel'), findsOneWidget);
      expect(find.text('Clear'), findsOneWidget);
    });

    testWidgets('displays connection status correctly', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const SettingsScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Should show Connection Status card
      expect(find.text('Connection Status'), findsOneWidget);
    });

    testWidgets('shows configuration help info', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const SettingsScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Should show help card
      expect(find.text('Configuration Help'), findsOneWidget);
      expect(
        find.text('• Default development endpoint: http://localhost:8000\n'
            '• For production, use your backend URL (e.g., https://api.example.com)\n'
            '• The API key authenticates all requests to the backend\n'
            '• Use "Test Connection" to verify your configuration'),
        findsOneWidget,
      );
    });
  });
}

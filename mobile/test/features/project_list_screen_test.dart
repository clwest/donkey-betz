/// Project List Screen Widget Test
///
/// Session 101: Project Browser - Mobile Flutter App
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/features/projects/project_list_screen.dart';
import 'package:donkey_os_cockpit/models/project.dart';
import 'package:donkey_os_cockpit/providers/projects_provider.dart';

void main() {
  group('ProjectListScreen', () {
    testWidgets('shows loading indicator when projects are loading',
        (WidgetTester tester) async {
      // Override the provider to return loading state
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            projectsProvider.overrideWith(
              (ref) => Future.delayed(
                const Duration(seconds: 10),
                () => [],
              ),
            ),
          ],
          child: const MaterialApp(
            home: ProjectListScreen(),
          ),
        ),
      );

      await tester.pump();

      // Should show loading indicator
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Loading projects...'), findsOneWidget);
    });

    testWidgets('shows empty state when no projects exist',
        (WidgetTester tester) async {
      // Override provider to return empty list
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            projectsProvider.overrideWith((ref) => Future.value([])),
          ],
          child: const MaterialApp(
            home: ProjectListScreen(),
          ),
        ),
      );

      // Wait for the future to complete
      await tester.pumpAndSettle();

      // Should show empty state
      expect(find.text('No Projects Yet'), findsOneWidget);
      expect(find.text('Create your first project to get started'),
          findsOneWidget);
    });

    testWidgets('shows error state when API fails',
        (WidgetTester tester) async {
      // Override provider to throw error
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            projectsProvider.overrideWith(
              (ref) => Future.error('API Error'),
            ),
          ],
          child: const MaterialApp(
            home: ProjectListScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Should show error state
      expect(find.text('Error loading projects'), findsOneWidget);
      expect(find.byIcon(Icons.error_outline), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });

    testWidgets('displays project grid when projects are loaded',
        (WidgetTester tester) async {
      final mockProjects = [
        Project(
          projectId: 'proj_1',
          name: 'Test Project 1',
          description: 'Description 1',
          goal: 'Goal 1',
          category: 'art',
          tags: ['tag1'],
          imageCount: 5,
          videoCount: 2,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        ),
        Project(
          projectId: 'proj_2',
          name: 'Test Project 2',
          description: 'Description 2',
          goal: 'Goal 2',
          category: 'video',
          tags: ['tag2'],
          imageCount: 3,
          videoCount: 1,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        ),
      ];

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            projectsProvider.overrideWith((ref) => Future.value(mockProjects)),
          ],
          child: const MaterialApp(
            home: ProjectListScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Should show project cards
      expect(find.text('Test Project 1'), findsOneWidget);
      expect(find.text('Test Project 2'), findsOneWidget);
      expect(find.text('Description 1'), findsOneWidget);
      expect(find.text('Description 2'), findsOneWidget);
    });

    testWidgets('has refresh functionality', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            projectsProvider.overrideWith((ref) => Future.value([])),
          ],
          child: const MaterialApp(
            home: ProjectListScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Should have RefreshIndicator
      expect(find.byType(RefreshIndicator), findsOneWidget);
    });

    testWidgets('navigates to project detail on card tap',
        (WidgetTester tester) async {
      final mockProjects = [
        Project(
          projectId: 'proj_test',
          name: 'Tappable Project',
          description: 'Tap me',
          goal: 'Test goal',
          category: null,
          tags: [],
          imageCount: 1,
          videoCount: 0,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        ),
      ];

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            projectsProvider.overrideWith((ref) => Future.value(mockProjects)),
          ],
          child: const MaterialApp(
            home: ProjectListScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Find and tap the project card
      final projectCard = find.text('Tappable Project');
      expect(projectCard, findsOneWidget);

      // Tap should trigger navigation (though we can't fully test navigation without more setup)
      await tester.tap(projectCard);
      await tester.pumpAndSettle();

      // If navigation worked, the detail screen would be pushed
      // For this simple test, we just verify the tap doesn't crash
    });
  });
}

# Session 112: Donkey Cockpit Integration Guide

## Required Edits to donkey_cockpit_screen.dart

### 1. Add Imports (after line 19)

```dart
import '../../providers/gallery_provider.dart';
import '../../providers/personal_assistant_provider.dart';  // ADD THIS
import '../leadership/leadership_dashboard.dart';
import '../boardroom/boardroom_form_screen.dart';
import '../projects/project_list_screen.dart';
import '../pipelines/pipelines_screen.dart';
import '../render/video_studio_screen.dart';
import '../render/render_jobs_screen.dart';
import '../settings/settings_screen.dart';
import '../gallery/galleries_screen.dart';
import '../assistant/personal_assistant_screen.dart';  // ADD THIS
```

### 2. Add Card to Layout (after line 92 - after Galleries card)

```dart
              // Card 3: Galleries & Assets
              _buildGalleriesCard(context, ref),
              const SizedBox(height: 16),

              // Card 4: Personal Assistant  // ADD THIS SECTION
              _buildPersonalAssistantCard(context, ref),
              const SizedBox(height: 16),

              // Card 5: Creative Pipelines
              _buildCreativePipelinesCard(context, ref),
```

### 3. Add Card Builder Method (add after _buildGalleriesCard method)

```dart
  Widget _buildPersonalAssistantCard(BuildContext context, WidgetRef ref) {
    final summaryAsync = ref.watch(learningSummaryProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(
                  Icons.chat_bubble,
                  size: 28,
                  color: AppTheme.primaryColor,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Personal Assistant',
                        style:
                            Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Chat with your AI assistant for personalized help.',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppTheme.textSecondary,
                            ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Stats
            summaryAsync.when(
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (error, _) => Text(
                'Stats unavailable',
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
              data: (summary) => Row(
                children: [
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Total Chats',
                      summary.totalInteractions.toString(),
                      Icons.forum,
                      AppTheme.primaryColor,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Skills Learned',
                      summary.skillsLearned.length.toString(),
                      Icons.school,
                      AppTheme.successColor,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Actions
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => _navigateToAssistant(context),
                    icon: const Icon(Icons.chat, size: 20),
                    label: const Text('Open Chat'),
                    style: FilledButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
```

### 4. Add Navigation Method (add with other navigation methods)

```dart
  void _navigateToAssistant(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => const PersonalAssistantScreen(),
      ),
    );
  }
```

### 5. Update Refresh Method (add to onRefresh)

Add this line to the existing `onRefresh` method where other providers are refreshed:

```dart
  Future<void> _onRefresh() async {
    ref.refresh(decisionsFutureProvider.future);
    ref.refresh(projectsProvider.future);
    ref.refresh(recentAssetsCountProvider.future);
    ref.refresh(learningSummaryProvider.future);  // ADD THIS LINE
    // ... rest of refreshes
  }
```

## Testing the Integration

After making these edits:

1. Run `flutter analyze` to check for errors
2. Run the app: `flutter run`
3. Navigate to Donkey Cockpit
4. Verify "Personal Assistant" card appears
5. Tap "Open Chat" to test navigation
6. Send a test message

## File Locations

- Screen: `mobile/lib/features/assistant/personal_assistant_screen.dart`
- Providers: `mobile/lib/providers/personal_assistant_provider.dart`
- Models: `mobile/lib/models/personal_assistant.dart`
- API: `mobile/lib/services/api/personal_assistant_api.dart`

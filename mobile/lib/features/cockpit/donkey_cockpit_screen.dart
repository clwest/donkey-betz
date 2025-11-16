/// Donkey Cockpit Screen - Unified Mobile Home + Navigation
///
/// Session 107+110: Main command center screen that surfaces:
/// - Strategic Co-Leadership (decisions, boardroom meetings, AI-human collaboration)
/// - Projects & Sessions (creative work browser)
/// - Creative Pipelines (one-tap workflows from idea to assets)
/// - Video Studio & Renders (render queue + progress)
/// - System & Agents (system health + settings)

library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../providers/leadership_providers.dart';
import '../../providers/projects_provider.dart';
import '../../providers/render_providers.dart';
import '../../providers/pipelines_provider.dart';
import '../../providers/gallery_provider.dart';
import '../../providers/personal_assistant_provider.dart';
import '../leadership/leadership_dashboard.dart';
import '../assistant/personal_assistant_screen.dart';
import '../boardroom/boardroom_form_screen.dart';
import '../projects/project_list_screen.dart';
import '../pipelines/pipelines_screen.dart';
import '../render/video_studio_screen.dart';
import '../render/render_jobs_screen.dart';
import '../settings/settings_screen.dart';
import '../gallery/galleries_screen.dart';
import '../ai_studio/ai_studio_hub_screen.dart';

class DonkeyCockpitScreen extends ConsumerStatefulWidget {
  const DonkeyCockpitScreen({super.key});

  @override
  ConsumerState<DonkeyCockpitScreen> createState() =>
      _DonkeyCockpitScreenState();
}

class _DonkeyCockpitScreenState extends ConsumerState<DonkeyCockpitScreen> {
  @override
  void initState() {
    super.initState();
    // Fetch data on mount
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(renderJobListProvider.notifier).fetchJobs(limit: 10);
      ref.read(pipelineRunListProvider.notifier).fetchRuns(limit: 10);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Donkey Betz Cockpit'),
        backgroundColor: AppTheme.primaryColor,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _navigateToSettings(context),
            tooltip: 'Settings',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          // Refresh all data providers
          await Future.wait([
            ref.refresh(leadershipStatsProvider.future),
            ref.refresh(projectsProvider.future),
            ref.refresh(recentAssetsCountProvider.future),
            ref.refresh(learningSummaryProvider.future),
            ref.read(pipelineRunListProvider.notifier).refresh(),
            ref.read(renderJobListProvider.notifier).refresh(),
          ]);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Greeting / Welcome
              _buildWelcomeHeader(context),
              const SizedBox(height: 20),

              // Card 1: Leadership & Decisions
              _buildLeadershipCard(context, ref),
              const SizedBox(height: 16),

              // Card 2: Projects & Sessions
              _buildProjectsCard(context, ref),
              const SizedBox(height: 16),

              // Card 3: Galleries & Assets
              _buildGalleriesCard(context, ref),
              const SizedBox(height: 16),

              // Card 3.5: AI Studio (Session 115!)
              _buildAIStudioCard(context),
              const SizedBox(height: 16),

              // Card 4: Personal Assistant
              _buildPersonalAssistantCard(context, ref),
              const SizedBox(height: 16),

              // Card 5: Creative Pipelines
              _buildCreativePipelinesCard(context, ref),
              const SizedBox(height: 16),

              // Card 6: Video Studio & Renders
              _buildVideoStudioCard(context, ref),
              const SizedBox(height: 16),

              // Card 7: System & Agents
              _buildSystemCard(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeHeader(BuildContext context) {
    return Card(
      elevation: 0,
      color: AppTheme.primaryColor.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Icon(
              Icons.dashboard,
              size: 40,
              color: AppTheme.primaryColor,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Command Center',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppTheme.primaryColor,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Human-AI Co-Leadership Platform',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppTheme.textSecondary,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Card 1: Leadership & Decisions
  Widget _buildLeadershipCard(BuildContext context, WidgetRef ref) {
    final leadershipStats = ref.watch(leadershipStatsProvider);

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
                  Icons.balance,
                  size: 28,
                  color: AppTheme.primaryColor,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Strategic Co-Leadership',
                        style:
                            Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'AI-human collaboration on strategic decisions. Track performance, start boardroom meetings.',
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
            leadershipStats.when(
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
              data: (stats) => Row(
                children: [
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Total Decisions',
                      stats.totalDecisions.toString(),
                      Icons.analytics,
                      AppTheme.infoColor,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Overrides',
                      '${stats.overrideRate.toStringAsFixed(0)}%',
                      Icons.alt_route,
                      AppTheme.warningColor,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Success Rate',
                      '${stats.successRate.toStringAsFixed(0)}%',
                      Icons.trending_up,
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
                    onPressed: () => _navigateToLeadershipCockpit(context),
                    icon: const Icon(Icons.insights, size: 20),
                    label: const Text('Open Leadership Cockpit'),
                    style: FilledButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _navigateToBoardroom(context),
                    icon: const Icon(Icons.meeting_room, size: 20),
                    label: const Text('Start Boardroom Meeting'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Card 2: Projects & Sessions
  Widget _buildProjectsCard(BuildContext context, WidgetRef ref) {
    final projectsAsync = ref.watch(projectsProvider);

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
                  Icons.folder_open,
                  size: 28,
                  color: AppTheme.accentColor,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Projects & Sessions',
                        style:
                            Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Jump into your active projects and creative sessions.',
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
            projectsAsync.when(
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (error, _) => Text(
                'Projects unavailable',
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
              data: (projects) => Row(
                children: [
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Active Projects',
                      projects.length.toString(),
                      Icons.work,
                      AppTheme.accentColor,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Recent Activity',
                      projects.isEmpty ? '0' : '${projects.length}',
                      Icons.schedule,
                      AppTheme.infoColor,
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
                    onPressed: () => _navigateToProjectBrowser(context),
                    icon: const Icon(Icons.grid_view, size: 20),
                    label: const Text('Open Project Browser'),
                    style: FilledButton.styleFrom(
                      backgroundColor: AppTheme.accentColor,
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

  /// Card 3: Galleries & Assets
  Widget _buildGalleriesCard(BuildContext context, WidgetRef ref) {
    final assetCountAsync = ref.watch(recentAssetsCountProvider);

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
                  Icons.photo_library,
                  size: 28,
                  color: Colors.orange,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Galleries & Assets',
                        style:
                            Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Browse all AI-generated images, videos, and audio.',
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
            assetCountAsync.when(
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (error, _) => Text(
                'Count unavailable',
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
              data: (count) => Row(
                children: [
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Total Assets',
                      count.toString(),
                      Icons.collections,
                      Colors.orange,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildStatChip(
                      context,
                      'Media Types',
                      '3',
                      Icons.category,
                      AppTheme.infoColor,
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
                    onPressed: () => _navigateToGalleries(context),
                    icon: const Icon(Icons.grid_view, size: 20),
                    label: const Text('View All Assets'),
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.orange,
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

  /// Card 3.5: AI Studio (Session 115 - Full Feature Parity!)
  Widget _buildAIStudioCard(BuildContext context) {
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
                  Icons.auto_awesome,
                  size: 28,
                  color: Colors.deepPurple,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'AI Studio',
                        style:
                            Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Access all 34 AI features: images, video, audio, character training.',
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
            Row(
              children: [
                Expanded(
                  child: _buildStatChip(
                    context,
                    'Image Features',
                    '12',
                    Icons.image,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatChip(
                    context,
                    'Video Features',
                    '3',
                    Icons.videocam,
                    Colors.red,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatChip(
                    context,
                    'Character AI',
                    '3',
                    Icons.person,
                    Colors.blueGrey,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Actions
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => _navigateToAIStudio(context),
                    icon: const Icon(Icons.apps, size: 20),
                    label: const Text('Open AI Studio'),
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.deepPurple,
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

  /// Card 4: Personal Assistant
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

  /// Card 5: Creative Pipelines
  Widget _buildCreativePipelinesCard(BuildContext context, WidgetRef ref) {
    final templatesState = ref.watch(pipelineTemplatesProvider);
    final runsState = ref.watch(pipelineRunListProvider);

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
                  Icons.auto_awesome,
                  size: 28,
                  color: Colors.purple,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Creative Pipelines',
                        style:
                            Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'One-tap workflows: from idea to publish-ready assets.',
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
            Row(
              children: [
                Expanded(
                  child: _buildStatChip(
                    context,
                    'Templates',
                    templatesState.templates.length.toString(),
                    Icons.view_module,
                    Colors.purple,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatChip(
                    context,
                    'Active Runs',
                    runsState.runs.where((run) => run.isActive).length.toString(),
                    Icons.play_circle,
                    AppTheme.infoColor,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatChip(
                    context,
                    'Recent Runs',
                    runsState.runs.length.toString(),
                    Icons.history,
                    AppTheme.successColor,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Actions - Template Shortcuts
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _launchPipeline(context, 'idea_to_image_set'),
                    icon: const Icon(Icons.image, size: 18),
                    label: const Text('Idea → Images', style: TextStyle(fontSize: 12)),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.purple,
                      side: BorderSide(color: Colors.purple.withOpacity(0.5)),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _launchPipeline(context, 'idea_to_promo_video'),
                    icon: const Icon(Icons.movie, size: 18),
                    label: const Text('Idea → Video', style: TextStyle(fontSize: 12)),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.purple,
                      side: BorderSide(color: Colors.purple.withOpacity(0.5)),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // View All Button
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => _navigateToPipelines(context),
                    icon: const Icon(Icons.grid_view, size: 20),
                    label: const Text('View All Pipelines'),
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.purple,
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

  /// Card 4: Video Studio & Renders
  Widget _buildVideoStudioCard(BuildContext context, WidgetRef ref) {
    final renderJobListState = ref.watch(renderJobListProvider);

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
                  Icons.movie_creation,
                  size: 28,
                  color: Colors.deepPurple,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Video Studio',
                        style:
                            Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Manage renders, monitor progress, and open finished videos.',
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
            renderJobListState.isLoading
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: CircularProgressIndicator(),
                    ),
                  )
                : Row(
                    children: [
                      Expanded(
                        child: _buildStatChip(
                          context,
                          'Active Jobs',
                          renderJobListState.jobs
                              .where((job) => job.isActive)
                              .length
                              .toString(),
                          Icons.play_circle,
                          Colors.deepPurple,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _buildStatChip(
                          context,
                          'Recent Renders',
                          renderJobListState.jobs.length.toString(),
                          Icons.video_library,
                          AppTheme.successColor,
                        ),
                      ),
                    ],
                  ),
            const SizedBox(height: 16),

            // Actions
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => _navigateToVideoStudio(context),
                    icon: const Icon(Icons.video_settings, size: 20),
                    label: const Text('Open Video Studio'),
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.deepPurple,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _navigateToRenderQueue(context),
                    icon: const Icon(Icons.queue_play_next, size: 20),
                    label: const Text('View Render Queue'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Card 5: System & Agents
  Widget _buildSystemCard(BuildContext context) {
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
                  Icons.hub,
                  size: 28,
                  color: AppTheme.infoColor,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'System & Agents',
                        style:
                            Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'High-level overview of agents, features, and system health.',
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

            // Static stats for v1
            Row(
              children: [
                Expanded(
                  child: _buildStatChip(
                    context,
                    'Creative Agents',
                    '10+',
                    Icons.smart_toy,
                    AppTheme.primaryColor,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatChip(
                    context,
                    'AI Features',
                    '34',
                    Icons.auto_awesome,
                    AppTheme.accentColor,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _navigateToSettings(context),
                    icon: const Icon(Icons.settings, size: 20),
                    label: const Text('Settings'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Helper: Build stat chip widget
  Widget _buildStatChip(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(
              fontSize: 10,
              color: AppTheme.textSecondary,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  // Navigation methods

  void _navigateToLeadershipCockpit(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const LeadershipDashboard(),
      ),
    );
  }

  void _navigateToBoardroom(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const BoardroomFormScreen(),
      ),
    );
  }

  void _navigateToProjectBrowser(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const ProjectListScreen(),
      ),
    );
  }

  void _navigateToVideoStudio(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const VideoStudioScreen(),
      ),
    );
  }

  void _navigateToRenderQueue(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const RenderJobsScreen(),
      ),
    );
  }

  void _navigateToPipelines(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const PipelinesScreen(),
      ),
    );
  }

  void _launchPipeline(BuildContext context, String templateSlug) {
    // Navigate to pipelines screen
    // TODO: Add initialTemplateSlug parameter to PipelinesScreen to pre-select template
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const PipelinesScreen(),
      ),
    );
  }

  void _navigateToSettings(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const SettingsScreen(),
      ),
    );
  }

  void _navigateToGalleries(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const GalleriesScreen(),
      ),
    );
  }

  void _navigateToAssistant(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const PersonalAssistantScreen(),
      ),
    );
  }

  void _navigateToAIStudio(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const AIStudioHubScreen(),
      ),
    );
  }
}

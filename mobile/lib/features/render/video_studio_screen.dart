/// Video Studio Screen - Session 106
///
/// Main hub for video rendering features.
/// Shows quick actions, recent renders, and future features.

library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/core/app_theme.dart';
import 'package:donkey_os_cockpit/models/render_job.dart';
import 'package:donkey_os_cockpit/providers/render_providers.dart';
import 'render_job_detail_screen.dart';
import 'render_jobs_screen.dart';

class VideoStudioScreen extends ConsumerStatefulWidget {
  const VideoStudioScreen({super.key});

  @override
  ConsumerState<VideoStudioScreen> createState() => _VideoStudioScreenState();
}

class _VideoStudioScreenState extends ConsumerState<VideoStudioScreen> {
  @override
  void initState() {
    super.initState();
    // Fetch recent jobs on mount
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(renderJobListProvider.notifier).fetchJobs(limit: 5);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Video Studio'),
        backgroundColor: AppTheme.primaryColor,
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(renderJobListProvider.notifier).refresh(),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildQuickActions(),
              const SizedBox(height: 32),
              _buildRecentRenders(),
              const SizedBox(height: 32),
              _buildComingSoon(),
            ],
          ),
        ),
      ),
    );
  }

  /// Section 1: Quick Actions
  Widget _buildQuickActions() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.flash_on, color: AppTheme.primaryColor, size: 28),
                const SizedBox(width: 12),
                const Text(
                  'Quick Actions',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'Manage your video renders and queue',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => const RenderJobsScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.queue_play_next),
                    label: const Text('View Queue'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _showNewRenderInfo,
                    icon: const Icon(Icons.add_circle_outline),
                    label: const Text('New Render'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      side: const BorderSide(color: AppTheme.primaryColor),
                      foregroundColor: AppTheme.primaryColor,
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

  /// Section 2: Recent Renders
  Widget _buildRecentRenders() {
    final jobListState = ref.watch(renderJobListProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.history, color: AppTheme.accentColor, size: 24),
            const SizedBox(width: 8),
            const Text(
              'Recent Renders',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Spacer(),
            if (jobListState.jobs.isNotEmpty)
              TextButton(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (context) => const RenderJobsScreen(),
                    ),
                  );
                },
                child: const Text('View All'),
              ),
          ],
        ),
        const SizedBox(height: 12),
        if (jobListState.isLoading && jobListState.jobs.isEmpty)
          const Center(
            child: Padding(
              padding: EdgeInsets.all(32),
              child: CircularProgressIndicator(),
            ),
          )
        else if (jobListState.error != null && jobListState.jobs.isEmpty)
          _buildErrorCard(jobListState.error!)
        else if (jobListState.jobs.isEmpty)
          _buildEmptyRenders()
        else
          ...jobListState.jobs.take(5).map((job) => _buildRenderCard(job)),
      ],
    );
  }

  /// Section 3: Coming Soon
  Widget _buildComingSoon() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.upcoming, color: Colors.orange, size: 24),
                const SizedBox(width: 8),
                const Text(
                  'Coming Soon',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildFeatureItem(
              Icons.batch_prediction,
              'Batch Rendering',
              'Queue multiple sessions for rendering',
            ),
            _buildFeatureItem(
              Icons.palette,
              'Custom Templates',
              'Choose render presets (4K, 1080p, social media)',
            ),
            _buildFeatureItem(
              Icons.notifications,
              'Push Notifications',
              'Get notified when renders complete',
            ),
            _buildFeatureItem(
              Icons.analytics,
              'Render Analytics',
              'Track render times and success rates',
            ),
            _buildFeatureItem(
              Icons.settings,
              'Advanced Settings',
              'Control resolution, codec, bitrate',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String title, String description) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Icon(icon, color: Colors.grey[600], size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRenderCard(RenderJob job) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => RenderJobDetailScreen(
                jobId: job.id,
                initialJob: job,
              ),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  _buildStatusBadge(job),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      job.title ?? job.sessionTitle ?? 'Render Job',
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Icon(
                    Icons.chevron_right,
                    color: Colors.grey[400],
                  ),
                ],
              ),
              if (job.isActive) ...[
                const SizedBox(height: 12),
                LinearProgressIndicator(
                  value: job.progress,
                  backgroundColor: Colors.grey[300],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    Color(job.statusColor),
                  ),
                  minHeight: 4,
                ),
                const SizedBox(height: 4),
                Text(
                  '${job.progressPercentage.toStringAsFixed(0)}% complete',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                ),
              ],
              if (job.isFailed && job.errorMessage != null) ...[
                const SizedBox(height: 8),
                Text(
                  job.errorMessage!,
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppTheme.errorColor,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(RenderJob job) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Color(job.statusColor).withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Color(job.statusColor),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getStatusIcon(job.status),
            size: 14,
            color: Color(job.statusColor),
          ),
          const SizedBox(width: 4),
          Text(
            job.statusText.split(' ')[0],
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: Color(job.statusColor),
            ),
          ),
        ],
      ),
    );
  }

  IconData _getStatusIcon(RenderJobStatus status) {
    switch (status) {
      case RenderJobStatus.queued:
        return Icons.schedule;
      case RenderJobStatus.dispatching:
        return Icons.rocket_launch;
      case RenderJobStatus.rendering:
        return Icons.video_settings;
      case RenderJobStatus.done:
        return Icons.check_circle;
      case RenderJobStatus.error:
        return Icons.error;
    }
  }

  Widget _buildErrorCard(String error) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Icon(
              Icons.error_outline,
              size: 48,
              color: AppTheme.errorColor,
            ),
            const SizedBox(height: 12),
            Text(
              error,
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppTheme.errorColor),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () =>
                  ref.read(renderJobListProvider.notifier).refresh(),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyRenders() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          children: [
            Icon(
              Icons.video_library,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            const Text(
              'No Renders Yet',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Start a render from any session with images or videos',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showNewRenderInfo() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.info_outline, color: AppTheme.primaryColor),
            SizedBox(width: 12),
            Text('Start a Render'),
          ],
        ),
        content: const Text(
          'To create a new render:\n\n'
          '1. Navigate to Projects\n'
          '2. Select a project\n'
          '3. Choose a session with images/videos\n'
          '4. Tap the "Render Video" button\n\n'
          'Your render will appear in the queue and you can track progress here.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }
}

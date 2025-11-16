/// Render Jobs List Screen - Session 105
///
/// Shows all user's render jobs with filtering and status.
/// Allows navigating to detail view for any job.

library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/core/app_theme.dart';
import 'package:donkey_os_cockpit/models/render_job.dart';
import 'package:donkey_os_cockpit/providers/render_providers.dart';
import 'render_job_detail_screen.dart';

class RenderJobsScreen extends ConsumerStatefulWidget {
  final String? projectId; // Optional filter

  const RenderJobsScreen({
    super.key,
    this.projectId,
  });

  @override
  ConsumerState<RenderJobsScreen> createState() => _RenderJobsScreenState();
}

class _RenderJobsScreenState extends ConsumerState<RenderJobsScreen> {
  @override
  void initState() {
    super.initState();
    // Fetch jobs on mount
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(renderJobListProvider.notifier).fetchJobs(
            projectId: widget.projectId,
          );
    });
  }

  @override
  Widget build(BuildContext context) {
    final jobListState = ref.watch(renderJobListProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.projectId != null ? 'Project Renders' : 'All Renders'),
        backgroundColor: AppTheme.primaryColor,
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(renderJobListProvider.notifier).refresh(
              projectId: widget.projectId,
            ),
        child: jobListState.isLoading && jobListState.jobs.isEmpty
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Loading render jobs...'),
                  ],
                ),
              )
            : jobListState.error != null && jobListState.jobs.isEmpty
                ? _buildErrorState(jobListState.error!)
                : jobListState.jobs.isEmpty
                    ? _buildEmptyState()
                    : _buildJobList(jobListState.jobs),
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: AppTheme.errorColor,
            ),
            const SizedBox(height: 16),
            const Text(
              'Error loading jobs',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppTheme.errorColor),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => ref.read(renderJobListProvider.notifier).refresh(
                    projectId: widget.projectId,
                  ),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.video_library,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            const Text(
              'No Render Jobs',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              widget.projectId != null
                  ? 'No renders for this project yet'
                  : 'You haven\'t created any renders yet',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildJobList(List<RenderJob> jobs) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: jobs.length,
      itemBuilder: (context, index) {
        final job = jobs[index];
        return _buildJobCard(job);
      },
    );
  }

  Widget _buildJobCard(RenderJob job) {
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
              // Status badge and title
              Row(
                children: [
                  _buildStatusBadge(job),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          job.sessionTitle ?? job.projectName ?? 'Render Job',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _formatDateTime(job.createdAt),
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    Icons.chevron_right,
                    color: Colors.grey[400],
                  ),
                ],
              ),

              // Progress bar (if active)
              if (job.isActive) ...[
                const SizedBox(height: 12),
                LinearProgressIndicator(
                  value: job.progress,
                  backgroundColor: Colors.grey[300],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    Color(job.statusColor),
                  ),
                  minHeight: 6,
                ),
                const SizedBox(height: 4),
                Text(
                  '${job.progressPercentage.toStringAsFixed(0)}% complete',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],

              // Error message (if failed)
              if (job.isFailed && job.errorMessage != null) ...[
                const SizedBox(height: 8),
                Text(
                  job.errorMessage!,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppTheme.errorColor,
                  ),
                  maxLines: 2,
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
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Color(job.statusColor).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
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
            size: 16,
            color: Color(job.statusColor),
          ),
          const SizedBox(width: 6),
          Text(
            job.statusText.split(' ')[0], // First word only
            style: TextStyle(
              fontSize: 12,
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

  String _formatDateTime(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);

    if (diff.inMinutes < 1) {
      return 'Just now';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inDays < 1) {
      return '${diff.inHours}h ago';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}d ago';
    } else {
      return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-'
          '${dt.day.toString().padLeft(2, '0')}';
    }
  }
}

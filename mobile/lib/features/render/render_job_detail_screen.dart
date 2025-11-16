/// Render Job Detail Screen - Session 105
///
/// Shows live render progress with polling from backend/Resolve Node.
/// Updates every 3 seconds while job is active.

library;

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/core/app_theme.dart';
import 'package:donkey_os_cockpit/models/render_job.dart';
import 'package:donkey_os_cockpit/providers/render_providers.dart';
import 'package:url_launcher/url_launcher.dart';

class RenderJobDetailScreen extends ConsumerStatefulWidget {
  final String jobId;
  final RenderJob? initialJob; // Optional - avoids initial load

  const RenderJobDetailScreen({
    super.key,
    required this.jobId,
    this.initialJob,
  });

  @override
  ConsumerState<RenderJobDetailScreen> createState() => _RenderJobDetailScreenState();
}

class _RenderJobDetailScreenState extends ConsumerState<RenderJobDetailScreen> {
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();

    // Set initial job if provided (avoids flickering)
    if (widget.initialJob != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(renderJobProvider(widget.jobId).notifier).state =
            RenderJobState(job: widget.initialJob);
      });
    }

    // Fetch initial status
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(renderJobProvider(widget.jobId).notifier).fetchStatus();
    });

    // Start polling every 3 seconds
    _pollTimer = Timer.periodic(const Duration(seconds: 3), (_) {
      if (mounted) {
        final state = ref.read(renderJobProvider(widget.jobId));
        if (state.job != null && !state.job!.isComplete) {
          ref.read(renderJobProvider(widget.jobId).notifier).fetchStatus();
        }
      }
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final jobState = ref.watch(renderJobProvider(widget.jobId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Render Job'),
        backgroundColor: AppTheme.primaryColor,
      ),
      body: jobState.isLoading && jobState.job == null
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Loading job status...'),
                ],
              ),
            )
          : jobState.error != null && jobState.job == null
              ? _buildErrorState(jobState.error!)
              : jobState.job != null
                  ? _buildJobDetails(context, jobState.job!)
                  : const Center(child: Text('No job data')),
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
              'Error loading job',
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
              onPressed: () =>
                  ref.read(renderJobProvider(widget.jobId).notifier).fetchStatus(),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildJobDetails(BuildContext context, RenderJob job) {
    return RefreshIndicator(
      onRefresh: () =>
          ref.read(renderJobProvider(widget.jobId).notifier).fetchStatus(),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Status card
              _buildStatusCard(job),
              const SizedBox(height: 16),

              // Progress card (only if active)
              if (job.isActive) ...[
                _buildProgressCard(job),
                const SizedBox(height: 16),
              ],

              // Details card
              _buildDetailsCard(job),
              const SizedBox(height: 16),

              // Result card (only if done)
              if (job.isSuccess && job.resultUrl != null) ...[
                _buildResultCard(job),
                const SizedBox(height: 16),
              ],

              // Error card (only if failed)
              if (job.isFailed && job.errorMessage != null) ...[
                _buildErrorCard(job),
                const SizedBox(height: 16),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusCard(RenderJob job) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _getStatusIcon(job.status),
                  color: Color(job.statusColor),
                  size: 32,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        job.statusText,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _getStatusDescription(job.status),
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressCard(RenderJob job) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Progress',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text(
                  '${job.progressPercentage.toStringAsFixed(0)}%',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            LinearProgressIndicator(
              value: job.progress,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation<Color>(
                Color(job.statusColor),
              ),
              minHeight: 8,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailsCard(RenderJob job) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Job Details',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildDetailRow('Job ID', job.id),
            if (job.projectName != null) _buildDetailRow('Project', job.projectName!),
            if (job.sessionTitle != null) _buildDetailRow('Session', job.sessionTitle!),
            _buildDetailRow(
              'Created',
              _formatDateTime(job.createdAt),
            ),
            if (job.completedAt != null)
              _buildDetailRow(
                'Completed',
                _formatDateTime(job.completedAt!),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard(RenderJob job) {
    return Card(
      color: Colors.green[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.check_circle, color: Colors.green[700], size: 28),
                const SizedBox(width: 12),
                const Text(
                  'Render Complete!',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _downloadResult(job.resultUrl!),
                icon: const Icon(Icons.download),
                label: const Text('Download Video'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  padding: const EdgeInsets.all(16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorCard(RenderJob job) {
    return Card(
      color: Colors.red[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.error, color: AppTheme.errorColor, size: 28),
                const SizedBox(width: 12),
                const Text(
                  'Render Failed',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              job.errorMessage!,
              style: const TextStyle(color: AppTheme.errorColor),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.grey[700],
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.normal),
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

  String _getStatusDescription(RenderJobStatus status) {
    switch (status) {
      case RenderJobStatus.queued:
        return 'Waiting to start...';
      case RenderJobStatus.dispatching:
        return 'Sending to Resolve Node...';
      case RenderJobStatus.rendering:
        return 'DaVinci Resolve is rendering your video';
      case RenderJobStatus.done:
        return 'Your video is ready!';
      case RenderJobStatus.error:
        return 'Something went wrong';
    }
  }

  String _formatDateTime(DateTime dt) {
    return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-'
        '${dt.day.toString().padLeft(2, '0')} '
        '${dt.hour.toString().padLeft(2, '0')}:'
        '${dt.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _downloadResult(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Cannot open URL: $url'),
          backgroundColor: AppTheme.errorColor,
        ),
      );
    }
  }
}

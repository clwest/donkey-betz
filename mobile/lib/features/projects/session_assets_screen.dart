/// Session Assets Screen - View all images and videos for a session
///
/// Session 101: Project Browser - Mobile Flutter App
/// Session 105: Added "Render Video" FAB
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../providers/projects_provider.dart';
import '../../providers/render_providers.dart';
import 'widgets/asset_grid.dart';
import '../render/render_job_detail_screen.dart';

class SessionAssetsScreen extends ConsumerWidget {
  final String sessionId;
  final String sessionTitle;

  const SessionAssetsScreen({
    super.key,
    required this.sessionId,
    required this.sessionTitle,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final assetsAsync = ref.watch(sessionAssetsProvider(sessionId));

    return Scaffold(
      appBar: AppBar(
        title: Text(sessionTitle),
        backgroundColor: AppTheme.primaryColor,
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.refresh(sessionAssetsProvider(sessionId).future),
        child: assetsAsync.when(
          loading: () => const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Loading assets...'),
              ],
            ),
          ),
          error: (error, stack) => Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.error_outline,
                    size: 64,
                    color: AppTheme.errorColor,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Error loading assets',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    error.toString(),
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: AppTheme.errorColor),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () => ref.refresh(sessionAssetsProvider(sessionId).future),
                    icon: const Icon(Icons.refresh),
                    label: const Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
          data: (response) {
            final hasAssets = response.totalImages > 0 || response.totalVideos > 0;

            if (!hasAssets) {
              return _buildEmptyState(context);
            }

            return SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Session info header
                  _buildSessionInfo(context, response),

                  const SizedBox(height: 16),

                  // Images section
                  if (response.images.isNotEmpty) ...[
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'Images (${response.images.length})',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                    ),
                    const SizedBox(height: 8),
                    AssetGrid(
                      images: response.images,
                      videos: const [],
                    ),
                    const SizedBox(height: 24),
                  ],

                  // Videos section
                  if (response.videos.isNotEmpty) ...[
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'Videos (${response.videos.length})',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                    ),
                    const SizedBox(height: 8),
                    AssetGrid(
                      images: const [],
                      videos: response.videos,
                    ),
                  ],

                  const SizedBox(height: 16),
                ],
              ),
            );
          },
        ),
      ),
      // Session 105: Render Video FAB
      floatingActionButton: assetsAsync.when(
        data: (response) {
          final hasVideos = response.totalVideos > 0;
          final hasImages = response.totalImages > 0;

          if (!hasVideos && !hasImages) {
            return null; // No assets to render
          }

          return FloatingActionButton.extended(
            onPressed: () => _handleRenderVideo(context, ref),
            icon: const Icon(Icons.video_library),
            label: const Text('Render Video'),
            backgroundColor: AppTheme.primaryColor,
          );
        },
        loading: () => null,
        error: (_, __) => null,
      ),
    );
  }

  /// Handle render video button press
  Future<void> _handleRenderVideo(BuildContext context, WidgetRef ref) async {
    try {
      // Show loading dialog
      if (!context.mounted) return;
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(
          child: Card(
            child: Padding(
              padding: EdgeInsets.all(32),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Creating render job...'),
                ],
              ),
            ),
          ),
        ),
      );

      // Create render job via provider
      final createJob = ref.read(createRenderJobProvider);
      final job = await createJob(
        sessionId: sessionId,
        timelineName: sessionTitle,
        template: 'default_mp4',
      );

      // Close loading dialog
      if (!context.mounted) return;
      Navigator.of(context).pop();

      // Navigate to job detail screen
      if (!context.mounted) return;
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => RenderJobDetailScreen(
            jobId: job.id,
            initialJob: job,
          ),
        ),
      );
    } catch (e) {
      // Close loading dialog if open
      if (!context.mounted) return;
      Navigator.of(context).pop();

      // Show error snackbar
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to create render job: ${e.toString()}'),
          backgroundColor: AppTheme.errorColor,
          action: SnackBarAction(
            label: 'Retry',
            onPressed: () => _handleRenderVideo(context, ref),
          ),
        ),
      );
    }
  }

  Widget _buildSessionInfo(BuildContext context, response) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildInfoItem(
              Icons.image,
              response.totalImages.toString(),
              'Images',
            ),
            Container(
              width: 1,
              height: 40,
              color: Colors.grey[300],
            ),
            _buildInfoItem(
              Icons.videocam,
              response.totalVideos.toString(),
              'Videos',
            ),
            Container(
              width: 1,
              height: 40,
              color: Colors.grey[300],
            ),
            _buildInfoItem(
              Icons.collections,
              (response.totalImages + response.totalVideos).toString(),
              'Total',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: AppTheme.primaryColor),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.photo_library,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'No Assets',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'This session doesn\'t have any images or videos yet',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }
}

/// MiniFigs Screen - Session 111
///
/// Shows user's mini-fig assets (3D-printable characters from images).
/// Displays status (pending, processing, completed, failed) and allows browsing.

library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/core/app_theme.dart';
import 'package:donkey_os_cockpit/models/minifig_asset.dart';
import 'package:donkey_os_cockpit/providers/minifigs_provider.dart';
import 'package:intl/intl.dart';
import 'minifig_detail_screen.dart';

class MiniFigsScreen extends ConsumerStatefulWidget {
  const MiniFigsScreen({super.key});

  @override
  ConsumerState<MiniFigsScreen> createState() => _MiniFigsScreenState();
}

class _MiniFigsScreenState extends ConsumerState<MiniFigsScreen> {
  String? _statusFilter;

  @override
  Widget build(BuildContext context) {
    final minifigsState = ref.watch(minifigsListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('MiniFigs Gallery'),
        backgroundColor: AppTheme.primaryColor,
        actions: [
          PopupMenuButton<String?>(
            icon: const Icon(Icons.filter_list),
            tooltip: 'Filter by status',
            onSelected: (value) {
              setState(() {
                _statusFilter = value;
              });
              ref.read(minifigsListProvider.notifier).fetchMiniFigs(
                    status: value,
                  );
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: null,
                child: Text('All MiniFigs'),
              ),
              const PopupMenuItem(
                value: 'completed',
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green, size: 18),
                    SizedBox(width: 8),
                    Text('Completed'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'processing',
                child: Row(
                  children: [
                    Icon(Icons.sync, color: Colors.blue, size: 18),
                    SizedBox(width: 8),
                    Text('Processing'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'pending',
                child: Row(
                  children: [
                    Icon(Icons.schedule, color: Colors.grey, size: 18),
                    SizedBox(width: 8),
                    Text('Pending'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'failed',
                child: Row(
                  children: [
                    Icon(Icons.error, color: Colors.red, size: 18),
                    SizedBox(width: 8),
                    Text('Failed'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: _buildBody(minifigsState),
    );
  }

  Widget _buildBody(MiniFigsListState state) {
    // Loading state (initial load)
    if (state.isLoading && state.minifigs.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading mini-figs...'),
          ],
        ),
      );
    }

    // Error state (with no cached data)
    if (state.error != null && state.minifigs.isEmpty) {
      return _buildErrorState(state.error!);
    }

    // Empty state
    if (state.minifigs.isEmpty) {
      return _buildEmptyState();
    }

    // Success state - show list
    return RefreshIndicator(
      onRefresh: () =>
          ref.read(minifigsListProvider.notifier).refresh(status: _statusFilter),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: state.minifigs.length,
        itemBuilder: (context, index) {
          final minifig = state.minifigs[index];
          return _buildMiniFigCard(minifig);
        },
      ),
    );
  }

  Widget _buildMiniFigCard(MiniFigAsset minifig) {
    final dateFormatter = DateFormat('MMM d, y • h:mm a');

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _navigateToDetail(minifig.id),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Preview image or placeholder icon
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: minifig.hasPreview
                      ? Colors.transparent
                      : Color(minifig.statusColor).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: Color(minifig.statusColor).withOpacity(0.3),
                    width: 2,
                  ),
                ),
                child: minifig.hasPreview
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(6),
                        child: Image.network(
                          minifig.previewImageUrl!,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return _buildPlaceholderIcon(minifig);
                          },
                        ),
                      )
                    : _buildPlaceholderIcon(minifig),
              ),
              const SizedBox(width: 16),
              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title
                    Text(
                      minifig.title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    // Status badge
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Color(minifig.statusColor).withOpacity(0.15),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            minifig.statusText,
                            style: TextStyle(
                              fontSize: 12,
                              color: Color(minifig.statusColor),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        if (minifig.isFavorite) ...[
                          const SizedBox(width: 8),
                          const Icon(
                            Icons.favorite,
                            size: 16,
                            color: Colors.pink,
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 8),
                    // Metadata
                    Row(
                      children: [
                        Icon(
                          Icons.file_download,
                          size: 14,
                          color: Colors.grey[600],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${minifig.downloadCount}',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                        const SizedBox(width: 12),
                        Icon(
                          Icons.remove_red_eye,
                          size: 14,
                          color: Colors.grey[600],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${minifig.viewCount}',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                        const SizedBox(width: 12),
                        Icon(
                          Icons.insert_drive_file,
                          size: 14,
                          color: Colors.grey[600],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          minifig.fileFormat,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    // Date
                    Text(
                      dateFormatter.format(minifig.createdAt),
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey[500],
                      ),
                    ),
                  ],
                ),
              ),
              // Chevron
              Icon(
                Icons.chevron_right,
                color: Colors.grey[400],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPlaceholderIcon(MiniFigAsset minifig) {
    return Center(
      child: Icon(
        minifig.isReady
            ? Icons.view_in_ar
            : minifig.isProcessing
                ? Icons.hourglass_empty
                : Icons.error_outline,
        size: 40,
        color: Color(minifig.statusColor),
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
              Icons.view_in_ar_outlined,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            const Text(
              'No MiniFigs Yet',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              _statusFilter != null
                  ? 'No mini-figs with status "$_statusFilter".'
                  : 'Create your first 3D mini-fig from character images using Creative Pipelines.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            if (_statusFilter != null) ...[
              const SizedBox(height: 16),
              TextButton.icon(
                onPressed: () {
                  setState(() {
                    _statusFilter = null;
                  });
                  ref.read(minifigsListProvider.notifier).refresh();
                },
                icon: const Icon(Icons.clear),
                label: const Text('Clear Filter'),
              ),
            ],
          ],
        ),
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
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            const Text(
              'Failed to Load MiniFigs',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                ref
                    .read(minifigsListProvider.notifier)
                    .refresh(status: _statusFilter);
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _navigateToDetail(String minifigId) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => MiniFigDetailScreen(minifigId: minifigId),
      ),
    );
  }
}

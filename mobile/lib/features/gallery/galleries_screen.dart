/// Galleries Screen - Browse all AI-generated assets
///
/// Session 111: Galleries & Assets - Mobile Integration
/// Displays unified gallery of images, videos, and audio with filtering
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../models/gallery.dart';
import '../../providers/gallery_provider.dart';
import 'asset_detail_screen.dart';

class GalleriesScreen extends ConsumerStatefulWidget {
  const GalleriesScreen({super.key});

  @override
  ConsumerState<GalleriesScreen> createState() => _GalleriesScreenState();
}

class _GalleriesScreenState extends ConsumerState<GalleriesScreen> {
  String _selectedFilter = 'all';

  @override
  Widget build(BuildContext context) {
    final galleryAsync = ref.watch(galleryAssetsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Galleries & Assets'),
        backgroundColor: AppTheme.accentColor,
      ),
      body: Column(
        children: [
          // Filter Chips
          _buildFilterChips(),

          // Gallery Grid
          Expanded(
            child: RefreshIndicator(
              onRefresh: () async {
                ref.invalidate(galleryAssetsProvider);
              },
              child: galleryAsync.when(
                loading: () => const Center(
                  child: CircularProgressIndicator(),
                ),
                error: (error, stack) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.error_outline,
                          size: 64,
                          color: AppTheme.errorColor,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Failed to load assets',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          error.toString(),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AppTheme.textSecondary,
                              ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton.icon(
                          onPressed: () {
                            ref.invalidate(galleryAssetsProvider);
                          },
                          icon: const Icon(Icons.refresh),
                          label: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                ),
                data: (gallery) {
                  if (gallery.results.isEmpty) {
                    return _buildEmptyState();
                  }

                  return GridView.builder(
                    padding: const EdgeInsets.all(16),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 0.85,
                    ),
                    itemCount: gallery.results.length,
                    itemBuilder: (context, index) {
                      final asset = gallery.results[index];
                      return _buildAssetCard(asset);
                    },
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Filter chips for media type
  Widget _buildFilterChips() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        border: Border(
          bottom: BorderSide(color: Colors.grey[300]!),
        ),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            _buildFilterChip('All', 'all', Icons.grid_view),
            const SizedBox(width: 8),
            _buildFilterChip('Images', 'images', Icons.image),
            const SizedBox(width: 8),
            _buildFilterChip('Videos', 'videos', Icons.movie),
            const SizedBox(width: 8),
            _buildFilterChip('Audio', 'audio', Icons.audiotrack),
            const SizedBox(width: 8),
            _buildFilterChip(
              'Favorites',
              'favorites',
              Icons.favorite,
              color: Colors.red,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(
    String label,
    String filterValue,
    IconData icon, {
    Color? color,
  }) {
    final isSelected = _selectedFilter == filterValue;
    final chipColor = color ?? AppTheme.accentColor;

    return FilterChip(
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 16,
            color: isSelected ? Colors.white : chipColor,
          ),
          const SizedBox(width: 6),
          Text(label),
        ],
      ),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _selectedFilter = filterValue;
        });

        // Update filters based on selection
        final filters = ref.read(galleryFiltersProvider.notifier);
        if (filterValue == 'favorites') {
          filters.state = const GalleryFilters(favorite: true);
        } else {
          filters.state = GalleryFilters(type: filterValue);
        }

        // Refresh gallery
        ref.invalidate(galleryAssetsProvider);
      },
      selectedColor: chipColor,
      checkmarkColor: Colors.white,
      backgroundColor: Colors.white,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : Colors.black87,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }

  /// Build asset card for grid
  Widget _buildAssetCard(GalleryAsset asset) {
    return GestureDetector(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => AssetDetailScreen(asset: asset),
          ),
        );
      },
      child: Card(
        clipBehavior: Clip.antiAlias,
        elevation: 2,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Thumbnail
            Expanded(
              child: Stack(
                fit: StackFit.expand,
                children: [
                  // Image placeholder or actual thumbnail
                  if (asset.thumbnailUrl != null && asset.thumbnailUrl!.isNotEmpty)
                    Image.network(
                      asset.thumbnailUrl!,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return _buildPlaceholder(asset.type);
                      },
                    )
                  else
                    _buildPlaceholder(asset.type),

                  // Type badge
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: _getTypeColor(asset.type).withOpacity(0.9),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            _getTypeIcon(asset.type),
                            size: 12,
                            color: Colors.white,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            asset.type.name.toUpperCase(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Favorite badge
                  if (asset.isFavorite)
                    const Positioned(
                      top: 8,
                      left: 8,
                      child: Icon(
                        Icons.favorite,
                        color: Colors.red,
                        size: 20,
                      ),
                    ),
                ],
              ),
            ),

            // Info
            Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    asset.prompt ?? 'No prompt',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        Icons.access_time,
                        size: 12,
                        color: AppTheme.textSecondary,
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          _formatDate(asset.createdAt),
                          style: TextStyle(
                            fontSize: 10,
                            color: AppTheme.textSecondary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlaceholder(MediaType type) {
    return Container(
      color: Colors.grey[200],
      child: Center(
        child: Icon(
          _getTypeIcon(type),
          size: 64,
          color: _getTypeColor(type),
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
              Icons.photo_library_outlined,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'No assets yet',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Create images, videos, or audio using the Creative Pipelines to see them here.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Color _getTypeColor(MediaType type) {
    switch (type) {
      case MediaType.image:
        return AppTheme.successColor;
      case MediaType.video:
        return Colors.deepPurple;
      case MediaType.audio:
        return AppTheme.infoColor;
    }
  }

  IconData _getTypeIcon(MediaType type) {
    switch (type) {
      case MediaType.image:
        return Icons.image;
      case MediaType.video:
        return Icons.movie;
      case MediaType.audio:
        return Icons.audiotrack;
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays > 7) {
      return '${date.month}/${date.day}/${date.year}';
    } else if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
}

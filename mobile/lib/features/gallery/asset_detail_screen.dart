/// Asset Detail Screen - View individual asset with full metadata
///
/// Session 111: Galleries & Assets - Mobile Integration
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../models/gallery.dart';
import '../../providers/gallery_provider.dart';
import '../../services/api/gallery_api.dart';
import '../../providers/api_provider.dart';
import '../../widgets/video_player_widget.dart';

class AssetDetailScreen extends ConsumerWidget {
  final GalleryAsset asset;

  const AssetDetailScreen({
    super.key,
    required this.asset,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_getTitle()),
        backgroundColor: _getTypeColor(asset.type),
        actions: [
          // Favorite toggle
          IconButton(
            icon: Icon(
              asset.isFavorite ? Icons.favorite : Icons.favorite_border,
              color: asset.isFavorite ? Colors.red : Colors.white,
            ),
            onPressed: () async {
              try {
                final api = ref.read(galleryApiProvider);
                await api.toggleFavorite(asset.id, asset.type);
                // Refresh gallery
                ref.invalidate(galleryAssetsProvider);
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        asset.isFavorite ? 'Removed from favorites' : 'Added to favorites',
                      ),
                      duration: const Duration(seconds: 2),
                    ),
                  );
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Failed to toggle favorite: $e'),
                      backgroundColor: AppTheme.errorColor,
                    ),
                  );
                }
              }
            },
            tooltip: asset.isFavorite ? 'Remove from favorites' : 'Add to favorites',
          ),

          // Share/Copy URL
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              _copyToClipboard(context);
            },
            tooltip: 'Copy URL',
          ),

          // More options
          PopupMenuButton<String>(
            onSelected: (value) async {
              switch (value) {
                case 'delete':
                  _showDeleteConfirmation(context, ref);
                  break;
                case 'details':
                  _showDetailsDialog(context);
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'details',
                child: Row(
                  children: [
                    Icon(Icons.info_outline, size: 20),
                    SizedBox(width: 12),
                    Text('View Details'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete_outline, size: 20, color: Colors.red),
                    SizedBox(width: 12),
                    Text('Delete', style: TextStyle(color: Colors.red)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Asset preview
            _buildAssetPreview(context),

            // Metadata
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Prompt
                  if (asset.prompt != null) ...[
                    _buildMetadataSection(
                      'Prompt',
                      asset.prompt!,
                      Icons.lightbulb_outline,
                    ),
                    const SizedBox(height: 16),
                  ],

                  // Model
                  if (asset.modelUsed != null) ...[
                    _buildMetadataRow(
                      'Model',
                      asset.modelUsed!,
                      Icons.smart_toy,
                    ),
                    const SizedBox(height: 8),
                  ],

                  // Created date
                  _buildMetadataRow(
                    'Created',
                    _formatFullDate(asset.createdAt),
                    Icons.access_time,
                  ),
                  const SizedBox(height: 8),

                  // Type-specific metadata
                  ..._buildTypeSpecificMetadata(),

                  // Stats
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _buildStatCard(
                          'Views',
                          asset.viewCount.toString(),
                          Icons.visibility,
                          AppTheme.infoColor,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildStatCard(
                          'Downloads',
                          asset.downloadCount.toString(),
                          Icons.download,
                          AppTheme.successColor,
                        ),
                      ),
                    ],
                  ),

                  // Tags (if available)
                  if (asset.tags != null && asset.tags!.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _buildTagsSection(),
                  ],

                  // User notes (if available)
                  if (asset.userNotes != null && asset.userNotes!.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _buildMetadataSection(
                      'Notes',
                      asset.userNotes!,
                      Icons.note,
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAssetPreview(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.5,
      ),
      color: Colors.black,
      child: Center(
        child: asset.type == MediaType.video
            ? _buildVideoPlaceholder(context)
            : Image.network(
                asset.url,
                fit: BoxFit.contain,
                errorBuilder: (context, error, stackTrace) {
                  return _buildErrorPlaceholder();
                },
              ),
      ),
    );
  }

  Widget _buildVideoPlaceholder(BuildContext context) {
    // Session 111: Video playback implementation
    return VideoPlayerWidget(
      videoUrl: asset.url,
      autoPlay: false,
      showControls: true,
    );
  }

  Widget _buildErrorPlaceholder() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.broken_image,
          size: 80,
          color: Colors.white.withOpacity(0.5),
        ),
        const SizedBox(height: 16),
        Text(
          'Failed to load asset',
          style: TextStyle(
            color: Colors.white.withOpacity(0.7),
            fontSize: 14,
          ),
        ),
      ],
    );
  }

  Widget _buildMetadataSection(String label, String value, IconData icon) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 18, color: AppTheme.primaryColor),
            const SizedBox(width: 8),
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            value,
            style: const TextStyle(fontSize: 14),
          ),
        ),
      ],
    );
  }

  Widget _buildMetadataRow(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 18, color: AppTheme.textSecondary),
        const SizedBox(width: 8),
        Text(
          '$label:',
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: AppTheme.textSecondary,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(fontSize: 14),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
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
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              color: AppTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTagsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.label_outline, size: 18, color: AppTheme.primaryColor),
            const SizedBox(width: 8),
            const Text(
              'Tags',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: asset.tags!.map((tag) {
            return Chip(
              label: Text(
                tag,
                style: const TextStyle(fontSize: 12),
              ),
              backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
              side: BorderSide(
                color: AppTheme.primaryColor.withOpacity(0.3),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  List<Widget> _buildTypeSpecificMetadata() {
    final widgets = <Widget>[];

    if (asset.type == MediaType.image) {
      if (asset.width != null && asset.height != null) {
        widgets.add(_buildMetadataRow(
          'Dimensions',
          '${asset.width} × ${asset.height}',
          Icons.aspect_ratio,
        ));
        widgets.add(const SizedBox(height: 8));
      }
      if (asset.style != null) {
        widgets.add(_buildMetadataRow(
          'Style',
          asset.style!,
          Icons.palette,
        ));
        widgets.add(const SizedBox(height: 8));
      }
    } else if (asset.type == MediaType.video) {
      if (asset.duration != null) {
        widgets.add(_buildMetadataRow(
          'Duration',
          '${asset.duration}s',
          Icons.timer,
        ));
        widgets.add(const SizedBox(height: 8));
      }
    }

    return widgets;
  }

  String _getTitle() {
    switch (asset.type) {
      case MediaType.image:
        return 'Image Details';
      case MediaType.video:
        return 'Video Details';
      case MediaType.audio:
        return 'Audio Details';
    }
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

  String _formatFullDate(DateTime date) {
    return '${date.month}/${date.day}/${date.year} at ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }

  void _copyToClipboard(BuildContext context) {
    Clipboard.setData(ClipboardData(text: asset.url));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('URL copied to clipboard'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _showDeleteConfirmation(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Asset?'),
        content: const Text(
          'This will permanently delete this asset. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop(); // Close dialog

              try {
                final api = ref.read(galleryApiProvider);
                await api.deleteAsset(asset.id, asset.type);

                // Refresh gallery and go back
                ref.invalidate(galleryAssetsProvider);

                if (context.mounted) {
                  Navigator.of(context).pop(); // Go back to gallery
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Asset deleted successfully'),
                    ),
                  );
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Failed to delete: $e'),
                      backgroundColor: AppTheme.errorColor,
                    ),
                  );
                }
              }
            },
            style: TextButton.styleFrom(
              foregroundColor: Colors.red,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  void _showDetailsDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Technical Details'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow('Asset ID', asset.id),
              _buildDetailRow('Type', asset.type.name),
              if (asset.imageType != null)
                _buildDetailRow('Image Type', asset.imageType!),
              if (asset.videoType != null)
                _buildDetailRow('Video Type', asset.videoType!),
              if (asset.filename != null)
                _buildDetailRow('Filename', asset.filename!),
              if (asset.parameters != null)
                _buildDetailRow('Parameters', asset.parameters.toString()),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: AppTheme.textSecondary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(fontSize: 13),
          ),
        ],
      ),
    );
  }
}

/// Asset Grid Widget - Display images and videos in a grid
///
/// Session 101: Project Browser - Mobile Flutter App
library;

import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../models/image_asset.dart';
import '../../../models/video_asset.dart';
import 'asset_viewer.dart';

class AssetGrid extends StatelessWidget {
  final List<ImageAsset> images;
  final List<VideoAsset> videos;

  const AssetGrid({
    super.key,
    required this.images,
    required this.videos,
  });

  @override
  Widget build(BuildContext context) {
    final allAssets = <dynamic>[...images, ...videos];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
        childAspectRatio: 1,
      ),
      itemCount: allAssets.length,
      itemBuilder: (context, index) {
        final asset = allAssets[index];

        if (asset is ImageAsset) {
          return _buildImageThumbnail(context, asset, index, allAssets);
        } else if (asset is VideoAsset) {
          return _buildVideoThumbnail(context, asset, index, allAssets);
        }

        return const SizedBox.shrink();
      },
    );
  }

  Widget _buildImageThumbnail(
    BuildContext context,
    ImageAsset image,
    int index,
    List<dynamic> allAssets,
  ) {
    return GestureDetector(
      onTap: () {
        _showAssetViewer(context, index, allAssets);
      },
      child: Stack(
        fit: StackFit.expand,
        children: [
          if (image.filePath != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: CachedNetworkImage(
                imageUrl: image.filePath!,
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  color: Colors.grey[200],
                  child: const Center(
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
                errorWidget: (context, url, error) => Container(
                  color: Colors.grey[300],
                  child: const Icon(Icons.error, color: Colors.red),
                ),
              ),
            )
          else
            Container(
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Center(
                child: Icon(Icons.image, color: Colors.grey),
              ),
            ),

          // Favorite indicator
          if (image.isFavorite)
            Positioned(
              top: 4,
              right: 4,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.favorite,
                  size: 12,
                  color: Colors.red,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildVideoThumbnail(
    BuildContext context,
    VideoAsset video,
    int index,
    List<dynamic> allAssets,
  ) {
    return GestureDetector(
      onTap: () {
        _showAssetViewer(context, index, allAssets);
      },
      child: Stack(
        fit: StackFit.expand,
        children: [
          if (video.thumbnailPath != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: CachedNetworkImage(
                imageUrl: video.thumbnailPath!,
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  color: Colors.grey[200],
                  child: const Center(
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
                errorWidget: (context, url, error) => Container(
                  color: Colors.grey[300],
                  child: const Icon(Icons.videocam, color: Colors.grey),
                ),
              ),
            )
          else
            Container(
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Center(
                child: Icon(Icons.videocam, color: Colors.grey),
              ),
            ),

          // Video play indicator
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withOpacity(0.3),
                  ],
                ),
              ),
              child: const Center(
                child: Icon(
                  Icons.play_circle_outline,
                  color: Colors.white,
                  size: 32,
                ),
              ),
            ),
          ),

          // Duration indicator
          if (video.duration != null)
            Positioned(
              bottom: 4,
              right: 4,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.black87,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  _formatDuration(video.duration!),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                  ),
                ),
              ),
            ),

          // Favorite indicator
          if (video.isFavorite)
            Positioned(
              top: 4,
              right: 4,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.favorite,
                  size: 12,
                  color: Colors.red,
                ),
              ),
            ),
        ],
      ),
    );
  }

  void _showAssetViewer(
    BuildContext context,
    int initialIndex,
    List<dynamic> assets,
  ) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AssetViewer(
          assets: assets,
          initialIndex: initialIndex,
        ),
      ),
    );
  }

  String _formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final remainingSeconds = seconds % 60;

    if (minutes > 0) {
      return '$minutes:${remainingSeconds.toString().padLeft(2, '0')}';
    }
    return '0:${remainingSeconds.toString().padLeft(2, '0')}';
  }
}

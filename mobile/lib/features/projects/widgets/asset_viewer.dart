/// Asset Viewer - Full screen image/video viewer with swipe
///
/// Session 101: Project Browser - Mobile Flutter App
library;

import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../models/image_asset.dart';
import '../../../models/video_asset.dart';

class AssetViewer extends StatefulWidget {
  final List<dynamic> assets;
  final int initialIndex;

  const AssetViewer({
    super.key,
    required this.assets,
    required this.initialIndex,
  });

  @override
  State<AssetViewer> createState() => _AssetViewerState();
}

class _AssetViewerState extends State<AssetViewer> {
  late PageController _pageController;
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
    _pageController = PageController(initialPage: widget.initialIndex);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final currentAsset = widget.assets[_currentIndex];

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        title: Text(
          '${_currentIndex + 1} / ${widget.assets.length}',
          style: const TextStyle(color: Colors.white),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          if (currentAsset is ImageAsset)
            IconButton(
              icon: Icon(
                currentAsset.isFavorite ? Icons.favorite : Icons.favorite_border,
                color: currentAsset.isFavorite ? Colors.red : Colors.white,
              ),
              onPressed: () {
                // TODO: Toggle favorite
              },
            ),
          if (currentAsset is VideoAsset)
            IconButton(
              icon: Icon(
                currentAsset.isFavorite ? Icons.favorite : Icons.favorite_border,
                color: currentAsset.isFavorite ? Colors.red : Colors.white,
              ),
              onPressed: () {
                // TODO: Toggle favorite
              },
            ),
        ],
      ),
      body: PageView.builder(
        controller: _pageController,
        itemCount: widget.assets.length,
        onPageChanged: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        itemBuilder: (context, index) {
          final asset = widget.assets[index];

          if (asset is ImageAsset) {
            return _buildImageView(asset);
          } else if (asset is VideoAsset) {
            return _buildVideoView(asset);
          }

          return const Center(
            child: Text(
              'Unknown asset type',
              style: TextStyle(color: Colors.white),
            ),
          );
        },
      ),
      bottomNavigationBar: _buildAssetInfo(currentAsset),
    );
  }

  Widget _buildImageView(ImageAsset image) {
    if (image.filePath == null) {
      return const Center(
        child: Icon(Icons.image, color: Colors.white, size: 64),
      );
    }

    return InteractiveViewer(
      child: Center(
        child: CachedNetworkImage(
          imageUrl: image.filePath!,
          fit: BoxFit.contain,
          placeholder: (context, url) => const Center(
            child: CircularProgressIndicator(color: Colors.white),
          ),
          errorWidget: (context, url, error) => const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.error, color: Colors.red, size: 64),
                SizedBox(height: 16),
                Text(
                  'Failed to load image',
                  style: TextStyle(color: Colors.white),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildVideoView(VideoAsset video) {
    // For now, show the thumbnail with a message
    // TODO: Implement actual video player
    return Stack(
      alignment: Alignment.center,
      children: [
        if (video.thumbnailPath != null)
          CachedNetworkImage(
            imageUrl: video.thumbnailPath!,
            fit: BoxFit.contain,
            placeholder: (context, url) => const Center(
              child: CircularProgressIndicator(color: Colors.white),
            ),
            errorWidget: (context, url, error) => const Center(
              child: Icon(Icons.videocam, color: Colors.white, size: 64),
            ),
          )
        else
          const Icon(Icons.videocam, color: Colors.white, size: 64),

        Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.play_circle_outline,
              color: Colors.white,
              size: 80,
            ),
            const SizedBox(height: 16),
            if (video.duration != null)
              Text(
                _formatDuration(video.duration!),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Text(
                'Tap to play (coming soon)',
                style: TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAssetInfo(dynamic asset) {
    String prompt = '';
    String model = '';

    if (asset is ImageAsset) {
      prompt = asset.prompt;
      model = asset.model;
    } else if (asset is VideoAsset) {
      prompt = asset.prompt;
      model = asset.model;
    }

    return Container(
      color: Colors.black,
      padding: const EdgeInsets.all(16),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  asset is ImageAsset ? Icons.image : Icons.videocam,
                  color: Colors.white70,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Text(
                  model,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              prompt,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
              ),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ],
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

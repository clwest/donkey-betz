/// Video Player Widget - Plays video assets
///
/// Session 111: Galleries & Assets - Video Playback
library;

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

class VideoPlayerWidget extends StatefulWidget {
  final String videoUrl;
  final bool autoPlay;
  final bool showControls;

  const VideoPlayerWidget({
    super.key,
    required this.videoUrl,
    this.autoPlay = false,
    this.showControls = true,
  });

  @override
  State<VideoPlayerWidget> createState() => _VideoPlayerWidgetState();
}

class _VideoPlayerWidgetState extends State<VideoPlayerWidget> {
  late VideoPlayerController _controller;
  bool _isInitialized = false;
  bool _hasError = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initializeVideo();
  }

  Future<void> _initializeVideo() async {
    try {
      _controller = VideoPlayerController.networkUrl(Uri.parse(widget.videoUrl));
      await _controller.initialize();

      if (mounted) {
        setState(() {
          _isInitialized = true;
        });

        if (widget.autoPlay) {
          _controller.play();
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _hasError = true;
          _errorMessage = e.toString();
        });
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_hasError) {
      return _buildErrorWidget();
    }

    if (!_isInitialized) {
      return _buildLoadingWidget();
    }

    return Column(
      children: [
        // Video player
        AspectRatio(
          aspectRatio: _controller.value.aspectRatio,
          child: Stack(
            alignment: Alignment.center,
            children: [
              VideoPlayer(_controller),

              // Play/Pause overlay
              if (widget.showControls)
                _buildControlsOverlay(),
            ],
          ),
        ),

        // Progress bar and controls
        if (widget.showControls)
          _buildControlsBar(),
      ],
    );
  }

  Widget _buildLoadingWidget() {
    return Container(
      color: Colors.black,
      child: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.white),
            SizedBox(height: 16),
            Text(
              'Loading video...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorWidget() {
    return Container(
      color: Colors.black,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              const Text(
                'Failed to load video',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                _errorMessage ?? 'Unknown error',
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () {
                  setState(() {
                    _hasError = false;
                    _errorMessage = null;
                  });
                  _initializeVideo();
                },
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildControlsOverlay() {
    return GestureDetector(
      onTap: () {
        setState(() {
          if (_controller.value.isPlaying) {
            _controller.pause();
          } else {
            _controller.play();
          }
        });
      },
      child: Container(
        color: Colors.transparent,
        child: Center(
          child: AnimatedOpacity(
            opacity: _controller.value.isPlaying ? 0.0 : 1.0,
            duration: const Duration(milliseconds: 300),
            child: Container(
              decoration: BoxDecoration(
                color: Colors.black45,
                shape: BoxShape.circle,
              ),
              padding: const EdgeInsets.all(16),
              child: Icon(
                _controller.value.isPlaying ? Icons.pause : Icons.play_arrow,
                size: 48,
                color: Colors.white,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildControlsBar() {
    return Container(
      color: Colors.black87,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        children: [
          // Progress bar
          VideoProgressIndicator(
            _controller,
            allowScrubbing: true,
            colors: const VideoProgressColors(
              playedColor: Colors.deepPurple,
              bufferedColor: Colors.white24,
              backgroundColor: Colors.white12,
            ),
          ),
          const SizedBox(height: 8),

          // Time and controls
          Row(
            children: [
              // Play/Pause button
              IconButton(
                onPressed: () {
                  setState(() {
                    if (_controller.value.isPlaying) {
                      _controller.pause();
                    } else {
                      _controller.play();
                    }
                  });
                },
                icon: Icon(
                  _controller.value.isPlaying ? Icons.pause : Icons.play_arrow,
                  color: Colors.white,
                ),
              ),

              // Current time
              Text(
                _formatDuration(_controller.value.position),
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
              const Text(
                ' / ',
                style: TextStyle(color: Colors.white38, fontSize: 12),
              ),
              Text(
                _formatDuration(_controller.value.duration),
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),

              const Spacer(),

              // Mute/Unmute button
              IconButton(
                onPressed: () {
                  setState(() {
                    _controller.setVolume(_controller.value.volume == 0 ? 1.0 : 0.0);
                  });
                },
                icon: Icon(
                  _controller.value.volume == 0 ? Icons.volume_off : Icons.volume_up,
                  color: Colors.white,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$minutes:$seconds';
  }
}

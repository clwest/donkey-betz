/// Video Extend Screen - Extend videos beyond 10 seconds
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:video_player/video_player.dart';
import '../../providers/api_provider.dart';
import '../../widgets/dual_source_video_picker.dart';
import 'dart:typed_data';

class VideoExtendScreen extends ConsumerStatefulWidget {
  const VideoExtendScreen({super.key});

  @override
  ConsumerState<VideoExtendScreen> createState() => _VideoExtendScreenState();
}

class _VideoExtendScreenState extends ConsumerState<VideoExtendScreen> {
  final _videoIdController = TextEditingController();
  Uint8List? _videoBytes;
  String? _fileName;
  String? _extendedVideoUrl;
  bool _isExtending = false;
  String? _errorMessage;
  int _extendSeconds = 5;
  VideoPlayerController? _videoController;

  void _onVideoSelected(Uint8List bytes, String fileName) {
    setState(() {
      _videoBytes = bytes;
      _fileName = fileName;
      _errorMessage = null;
    });
  }

  Future<void> _extendVideo() async {
    // Check if we have either video bytes or video ID
    if (_videoBytes == null && _videoIdController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please select a video or enter a video ID');
      return;
    }

    setState(() {
      _isExtending = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      Map<String, dynamic> response;

      if (_videoBytes != null) {
        // Upload video file with multipart
        response = await apiClient.postMultipart(
          '/api/v1/video/extend/',
          fileBytes: {'video': _videoBytes!},
          fileName: _fileName ?? 'video.mp4',
          fields: {
            'extend_seconds': _extendSeconds.toString(),
          },
        );
      } else {
        // Use video ID
        response = await apiClient.post(
          '/api/v1/video/extend/',
          {
            'video_id': _videoIdController.text.trim(),
            'extend_seconds': _extendSeconds,
          },
        );
      }

      if (response['success'] == true && response['video_url'] != null) {
        setState(() {
          _extendedVideoUrl = response['video_url'];
          _isExtending = false;
        });
        _initializeVideoPlayer(_extendedVideoUrl!);
      } else {
        throw Exception(response['error'] ?? 'Video extension failed');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isExtending = false;
      });
    }
  }

  void _initializeVideoPlayer(String url) {
    _videoController?.dispose();
    _videoController = VideoPlayerController.networkUrl(Uri.parse(url))
      ..initialize().then((_) {
        setState(() {});
        _videoController!.play();
      });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Extend Video'),
        backgroundColor: Colors.amber,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Info Card
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.amber),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.amber, size: 20),
                      SizedBox(width: 8),
                      Text('How it works',
                          style: TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Extend your existing video beyond 10 seconds using AI prediction. The AI will analyze the last frames and continue the motion naturally.',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Dual-Source Video Picker
            DualSourceVideoPicker(
              currentVideoBytes: _videoBytes,
              onVideoSelected: _onVideoSelected,
              placeholderText: 'Select a video to extend',
              height: 150,
            ),
            const SizedBox(height: 16),

            const Center(
              child: Text(
                'OR',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.grey,
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Video ID Input (Manual)
            TextField(
              controller: _videoIdController,
              decoration: const InputDecoration(
                labelText: 'Video ID (Optional)',
                hintText: 'Or enter a video ID manually',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.videocam),
              ),
            ),
            const SizedBox(height: 16),

            // Extension Duration
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Extend by:',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('$_extendSeconds seconds',
                        style: const TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)),
                  ],
                ),
                const SizedBox(height: 8),
                Slider(
                  value: _extendSeconds.toDouble(),
                  min: 5,
                  max: 20,
                  divisions: 3,
                  activeColor: Colors.amber,
                  label: '$_extendSeconds sec',
                  onChanged: (value) => setState(() => _extendSeconds = value.toInt()),
                ),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('5s', style: TextStyle(fontSize: 11, color: Colors.grey)),
                    Text('10s', style: TextStyle(fontSize: 11, color: Colors.grey)),
                    Text('15s', style: TextStyle(fontSize: 11, color: Colors.grey)),
                    Text('20s', style: TextStyle(fontSize: 11, color: Colors.grey)),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Extend Button
            ElevatedButton.icon(
              onPressed: _isExtending ? null : _extendVideo,
              icon: _isExtending
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.add_to_queue),
              label: Text(_isExtending ? 'Extending...' : 'Extend Video'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.amber,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Video Player
            if (_videoController != null && _videoController!.value.isInitialized) ...[
              const SizedBox(height: 24),
              const Text('Extended Video:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              AspectRatio(
                aspectRatio: _videoController!.value.aspectRatio,
                child: VideoPlayer(_videoController!),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  IconButton(
                    icon: Icon(
                      _videoController!.value.isPlaying ? Icons.pause : Icons.play_arrow,
                      size: 32,
                    ),
                    onPressed: () {
                      setState(() {
                        _videoController!.value.isPlaying
                            ? _videoController!.pause()
                            : _videoController!.play();
                      });
                    },
                  ),
                ],
              ),
            ],

            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  border: Border.all(color: Colors.red),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
              ),
            ],
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _videoIdController.dispose();
    _videoController?.dispose();
    super.dispose();
  }
}

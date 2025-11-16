/// Video Chain Screen - Chain multiple videos together
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:video_player/video_player.dart';
import '../../providers/api_provider.dart';

class VideoChainScreen extends ConsumerStatefulWidget {
  const VideoChainScreen({super.key});

  @override
  ConsumerState<VideoChainScreen> createState() => _VideoChainScreenState();
}

class _VideoChainScreenState extends ConsumerState<VideoChainScreen> {
  final List<String> _videoIds = [];
  final _videoIdController = TextEditingController();
  String? _chainedVideoUrl;
  bool _isChaining = false;
  String? _errorMessage;
  VideoPlayerController? _videoController;
  String _transitionType = 'cut';

  void _addVideoId() {
    if (_videoIdController.text.trim().isNotEmpty) {
      setState(() {
        _videoIds.add(_videoIdController.text.trim());
        _videoIdController.clear();
      });
    }
  }

  void _removeVideoId(int index) {
    setState(() => _videoIds.removeAt(index));
  }

  Future<void> _chainVideos() async {
    if (_videoIds.length < 2) {
      setState(() => _errorMessage = 'Please add at least 2 videos to chain');
      return;
    }

    setState(() {
      _isChaining = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.post(
        '/api/v1/video/chain/',
        {
          'video_ids': _videoIds,
          'transition': _transitionType,
        },
      );

      if (response['success'] == true && response['video_url'] != null) {
        setState(() {
          _chainedVideoUrl = response['video_url'];
          _isChaining = false;
        });
        _initializeVideoPlayer(_chainedVideoUrl!);
      } else {
        throw Exception(response['error'] ?? 'Video chaining failed');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isChaining = false;
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
        title: const Text('Chain Videos'),
        backgroundColor: Colors.deepOrange,
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
                color: Colors.deepOrange.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.deepOrange),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.link, color: Colors.deepOrange, size: 20),
                      SizedBox(width: 8),
                      Text('Chain Videos Together',
                          style: TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Combine multiple videos into one seamless sequence. Videos will be joined in the order you add them.',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Video ID Input
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _videoIdController,
                    decoration: const InputDecoration(
                      labelText: 'Video ID',
                      hintText: 'Enter video ID',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: _addVideoId,
                  icon: const Icon(Icons.add),
                  label: const Text('Add'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.deepOrange,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Video List
            if (_videoIds.isNotEmpty) ...[
              const Text('Videos to chain (in order):',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Container(
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ReorderableListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _videoIds.length,
                  onReorder: (oldIndex, newIndex) {
                    setState(() {
                      if (newIndex > oldIndex) newIndex--;
                      final item = _videoIds.removeAt(oldIndex);
                      _videoIds.insert(newIndex, item);
                    });
                  },
                  itemBuilder: (context, index) {
                    return ListTile(
                      key: ValueKey(_videoIds[index]),
                      leading: CircleAvatar(
                        backgroundColor: Colors.deepOrange,
                        child: Text('${index + 1}'),
                      ),
                      title: Text(_videoIds[index]),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        onPressed: () => _removeVideoId(index),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Drag to reorder • Tap delete to remove',
                style: TextStyle(fontSize: 11, color: Colors.grey),
              ),
              const SizedBox(height: 16),
            ],

            // Transition Type
            const Text('Transition:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: 'cut',
                  label: Text('Cut'),
                  icon: Icon(Icons.content_cut),
                ),
                ButtonSegment(
                  value: 'fade',
                  label: Text('Fade'),
                  icon: Icon(Icons.blur_on),
                ),
                ButtonSegment(
                  value: 'dissolve',
                  label: Text('Dissolve'),
                  icon: Icon(Icons.gradient),
                ),
              ],
              selected: {_transitionType},
              onSelectionChanged: (Set<String> selection) {
                setState(() => _transitionType = selection.first);
              },
            ),
            const SizedBox(height: 24),

            // Chain Button
            ElevatedButton.icon(
              onPressed: _isChaining || _videoIds.length < 2 ? null : _chainVideos,
              icon: _isChaining
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.video_library),
              label: Text(_isChaining
                  ? 'Chaining ${_videoIds.length} videos...'
                  : 'Chain ${_videoIds.length} Videos'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepOrange,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Video Player
            if (_videoController != null && _videoController!.value.isInitialized) ...[
              const SizedBox(height: 24),
              const Text('Chained Video:', style: TextStyle(fontWeight: FontWeight.bold)),
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

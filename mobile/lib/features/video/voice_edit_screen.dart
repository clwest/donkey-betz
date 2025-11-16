/// Voice-Controlled Video Editing Screen - Natural language DaVinci commands
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:video_player/video_player.dart';
import '../../providers/api_provider.dart';

class VoiceEditScreen extends ConsumerStatefulWidget {
  const VoiceEditScreen({super.key});

  @override
  ConsumerState<VoiceEditScreen> createState() => _VoiceEditScreenState();
}

class _VoiceEditScreenState extends ConsumerState<VoiceEditScreen> {
  final _videoIdController = TextEditingController();
  final _commandController = TextEditingController();
  String? _editedVideoUrl;
  bool _isProcessing = false;
  String? _errorMessage;
  VideoPlayerController? _videoController;
  final List<Map<String, String>> _commandHistory = [];

  final List<String> _exampleCommands = [
    'Add text "Hello World" at 5 seconds for 3 seconds',
    'Add music from library at start',
    'Trim video from 2 to 8 seconds',
    'Add fade in at start and fade out at end',
    'Speed up video 2x',
    'Add color grade cinematic',
  ];

  Future<void> _executeCommand() async {
    if (_videoIdController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter a video ID');
      return;
    }

    if (_commandController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter a command');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.post(
        '/api/v1/video/voice-edit/',
        {
          'video_id': _videoIdController.text.trim(),
          'command': _commandController.text.trim(),
        },
      );

      if (response['success'] == true) {
        setState(() {
          _editedVideoUrl = response['video_url'];
          _commandHistory.insert(0, {
            'command': _commandController.text.trim(),
            'time': DateTime.now().toString(),
          });
          _isProcessing = false;
        });
        _initializeVideoPlayer(_editedVideoUrl!);
        _commandController.clear();
      } else {
        throw Exception(response['error'] ?? 'Command execution failed');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isProcessing = false;
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

  void _useExampleCommand(String command) {
    setState(() {
      _commandController.text = command;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Edit'),
        backgroundColor: Colors.redAccent,
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
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.redAccent),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.record_voice_over, color: Colors.redAccent, size: 20),
                      SizedBox(width: 8),
                      Text('Natural Language Editing',
                          style: TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Edit videos using natural language commands. Powered by DaVinci Resolve with frame-accurate timing.',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Video ID Input
            TextField(
              controller: _videoIdController,
              decoration: const InputDecoration(
                labelText: 'Video ID',
                hintText: 'Enter the video ID to edit',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.videocam),
              ),
            ),
            const SizedBox(height: 16),

            // Command Input
            TextField(
              controller: _commandController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Edit Command',
                hintText: 'Describe what you want to do...',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.mic),
              ),
            ),
            const SizedBox(height: 16),

            // Example Commands
            const Text('Example Commands:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _exampleCommands
                  .map((cmd) => ActionChip(
                        label: Text(cmd, style: const TextStyle(fontSize: 11)),
                        backgroundColor: Colors.red.shade50,
                        onPressed: () => _useExampleCommand(cmd),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 24),

            // Execute Button
            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _executeCommand,
              icon: _isProcessing
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.auto_fix_high),
              label: Text(_isProcessing ? 'Processing...' : 'Execute Command'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.redAccent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Command History
            if (_commandHistory.isNotEmpty) ...[
              const SizedBox(height: 24),
              const Text('Recent Commands:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Container(
                constraints: const BoxConstraints(maxHeight: 150),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ListView.separated(
                  shrinkWrap: true,
                  itemCount: _commandHistory.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final item = _commandHistory[index];
                    return ListTile(
                      dense: true,
                      leading: const Icon(Icons.check_circle, color: Colors.green, size: 20),
                      title: Text(item['command']!,
                          style: const TextStyle(fontSize: 12)),
                      subtitle: Text(
                        DateTime.parse(item['time']!).toLocal().toString().split('.')[0],
                        style: const TextStyle(fontSize: 10, color: Colors.grey),
                      ),
                    );
                  },
                ),
              ),
            ],

            // Video Player
            if (_videoController != null && _videoController!.value.isInitialized) ...[
              const SizedBox(height: 24),
              const Text('Edited Video:', style: TextStyle(fontWeight: FontWeight.bold)),
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
    _commandController.dispose();
    _videoController?.dispose();
    super.dispose();
  }
}

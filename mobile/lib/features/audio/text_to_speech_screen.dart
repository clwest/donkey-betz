/// Text-to-Speech Screen (ElevenLabs)
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:audioplayers/audioplayers.dart';
import '../../providers/api_provider.dart';

class TextToSpeechScreen extends ConsumerStatefulWidget {
  const TextToSpeechScreen({super.key});

  @override
  ConsumerState<TextToSpeechScreen> createState() => _TextToSpeechScreenState();
}

class _TextToSpeechScreenState extends ConsumerState<TextToSpeechScreen> {
  final _textController = TextEditingController();
  final _audioPlayer = AudioPlayer();
  String? _audioUrl;
  bool _isGenerating = false;
  bool _isPlaying = false;
  String? _errorMessage;
  String _selectedVoice = 'Rachel'; // Default voice

  final List<Map<String, String>> _voices = [
    {'id': 'Rachel', 'name': 'Rachel (Female, Calm)'},
    {'id': 'Adam', 'name': 'Adam (Male, Deep)'},
    {'id': 'Domi', 'name': 'Domi (Female, Strong)'},
    {'id': 'Elli', 'name': 'Elli (Female, Emotional)'},
    {'id': 'Josh', 'name': 'Josh (Male, Young)'},
    {'id': 'Arnold', 'name': 'Arnold (Male, Crisp)'},
    {'id': 'Antoni', 'name': 'Antoni (Male, Well-rounded)'},
    {'id': 'Sam', 'name': 'Sam (Male, Dynamic)'},
  ];

  Future<void> _generateSpeech() async {
    if (_textController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter text');
      return;
    }

    setState(() {
      _isGenerating = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.post(
        '/api/v1/audio/text-to-speech/',
        {
          'text': _textController.text.trim(),
          'voice': _selectedVoice,
        },
      );

      if (response['success'] == true && response['audio_url'] != null) {
        setState(() {
          _audioUrl = response['audio_url'];
          _isGenerating = false;
        });
      } else {
        throw Exception(response['error'] ?? 'Speech generation failed');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isGenerating = false;
      });
    }
  }

  Future<void> _playAudio() async {
    if (_audioUrl == null) return;

    try {
      if (_isPlaying) {
        await _audioPlayer.pause();
        setState(() => _isPlaying = false);
      } else {
        await _audioPlayer.play(UrlSource(_audioUrl!));
        setState(() => _isPlaying = true);
      }
    } catch (e) {
      setState(() => _errorMessage = 'Playback error: ${e.toString()}');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Text-to-Speech'),
        backgroundColor: Colors.orange,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Text Input
            TextField(
              controller: _textController,
              maxLines: 6,
              decoration: const InputDecoration(
                labelText: 'Enter text to convert to speech',
                hintText: 'Hello, welcome to DonkeyOS...',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),

            // Voice Selection
            const Text('Voice:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedVoice,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
              ),
              items: _voices.map((voice) {
                return DropdownMenuItem(
                  value: voice['id'],
                  child: Text(voice['name']!),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() => _selectedVoice = value);
                }
              },
            ),
            const SizedBox(height: 24),

            // Generate Button
            ElevatedButton.icon(
              onPressed: _isGenerating ? null : _generateSpeech,
              icon: _isGenerating
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, valueColor: AlwaysStoppedAnimation(Colors.white)),
                    )
                  : const Icon(Icons.mic),
              label: Text(_isGenerating ? 'Generating...' : 'Generate Speech'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Audio Player
            if (_audioUrl != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    const Icon(Icons.headphones, size: 48, color: Colors.orange),
                    const SizedBox(height: 8),
                    const Text('Audio Ready!', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _playAudio,
                      icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
                      label: Text(_isPlaying ? 'Pause' : 'Play'),
                    ),
                  ],
                ),
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
    _textController.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }
}

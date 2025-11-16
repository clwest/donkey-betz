/// Character Image Generation Screen - Generate images with trained characters
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/api_provider.dart';

class CharacterImageScreen extends ConsumerStatefulWidget {
  const CharacterImageScreen({super.key});

  @override
  ConsumerState<CharacterImageScreen> createState() => _CharacterImageScreenState();
}

class _CharacterImageScreenState extends ConsumerState<CharacterImageScreen> {
  final _promptController = TextEditingController();
  String? _resultImageUrl;
  bool _isGenerating = false;
  String? _errorMessage;
  List<Map<String, dynamic>> _trainedCharacters = [];
  String? _selectedCharacterId;
  bool _isLoadingCharacters = false;

  @override
  void initState() {
    super.initState();
    _loadTrainedCharacters();
  }

  Future<void> _loadTrainedCharacters() async {
    setState(() => _isLoadingCharacters = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.get('/api/v1/character/list/');

      if (response['success'] == true && response['characters'] != null) {
        setState(() {
          _trainedCharacters = List<Map<String, dynamic>>.from(response['characters']);
          _isLoadingCharacters = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load characters: ${e.toString()}';
        _isLoadingCharacters = false;
      });
    }
  }

  Future<void> _generateWithCharacter() async {
    if (_selectedCharacterId == null) {
      setState(() => _errorMessage = 'Please select a trained character');
      return;
    }

    if (_promptController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter a prompt');
      return;
    }

    setState(() {
      _isGenerating = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.post(
        '/api/v1/character/generate/',
        {
          'character_id': _selectedCharacterId,
          'prompt': _promptController.text.trim(),
        },
      );

      if (response['success'] == true && response['image_url'] != null) {
        setState(() {
          _resultImageUrl = response['image_url'];
          _isGenerating = false;
        });
      } else {
        throw Exception(response['error'] ?? 'Generation failed');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isGenerating = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Character Images'),
        backgroundColor: Colors.lightBlue,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTrainedCharacters,
            tooltip: 'Refresh characters',
          ),
        ],
      ),
      body: _isLoadingCharacters
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Info Card
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.lightBlue.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.lightBlue),
                    ),
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.person, color: Colors.lightBlue, size: 20),
                            SizedBox(width: 8),
                            Text('Generate with Your Character',
                                style: TextStyle(fontWeight: FontWeight.bold)),
                          ],
                        ),
                        SizedBox(height: 8),
                        Text(
                          'Use your trained characters in any scene or style. Include the trigger word in your prompt.',
                          style: TextStyle(fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Character Selection
                  const Text('Select Character:',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),

                  if (_trainedCharacters.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey.shade300),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Column(
                        children: [
                          Icon(Icons.person_off, size: 48, color: Colors.grey),
                          SizedBox(height: 8),
                          Text('No trained characters',
                              style: TextStyle(color: Colors.grey)),
                          SizedBox(height: 4),
                          Text('Train a character first using the Train Character screen',
                              style: TextStyle(fontSize: 12, color: Colors.grey),
                              textAlign: TextAlign.center),
                        ],
                      ),
                    )
                  else
                    DropdownButtonFormField<String>(
                      value: _selectedCharacterId,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                      ),
                      hint: const Text('Choose a character'),
                      items: _trainedCharacters.map((char) {
                        return DropdownMenuItem(
                          value: char['id'].toString(),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(char['name'] ?? 'Unnamed',
                                  style: const TextStyle(fontWeight: FontWeight.bold)),
                              Text('Trigger: ${char['trigger_word'] ?? 'N/A'}',
                                  style: const TextStyle(fontSize: 11, color: Colors.grey)),
                            ],
                          ),
                        );
                      }).toList(),
                      onChanged: (value) => setState(() => _selectedCharacterId = value),
                    ),
                  const SizedBox(height: 16),

                  // Display selected character info
                  if (_selectedCharacterId != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.lightBlue.shade50,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('💡 Tip:',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                          const SizedBox(height: 4),
                          Text(
                            'Include "${_trainedCharacters.firstWhere((c) => c['id'].toString() == _selectedCharacterId)['trigger_word']}" in your prompt to invoke this character.',
                            style: const TextStyle(fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  // Prompt
                  TextField(
                    controller: _promptController,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      labelText: 'Prompt (include trigger word)',
                      hintText: 'TOK as a superhero flying over the city',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.edit),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Generate Button
                  ElevatedButton.icon(
                    onPressed: _isGenerating || _trainedCharacters.isEmpty
                        ? null
                        : _generateWithCharacter,
                    icon: _isGenerating
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2))
                        : const Icon(Icons.auto_awesome),
                    label: Text(_isGenerating
                        ? 'Generating...'
                        : 'Generate with Character'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.lightBlue,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.all(16),
                    ),
                  ),

                  // Result
                  if (_resultImageUrl != null) ...[
                    const SizedBox(height: 24),
                    const Text('Result:',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.network(_resultImageUrl!),
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
                      child: Text(_errorMessage!,
                          style: const TextStyle(color: Colors.red)),
                    ),
                  ],
                ],
              ),
            ),
    );
  }

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }
}

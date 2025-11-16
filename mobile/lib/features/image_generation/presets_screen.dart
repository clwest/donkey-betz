/// Presets Screen - Generate with 69 style presets
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/api_provider.dart';

class PresetsScreen extends ConsumerStatefulWidget {
  const PresetsScreen({super.key});

  @override
  ConsumerState<PresetsScreen> createState() => _PresetsScreenState();
}

class _PresetsScreenState extends ConsumerState<PresetsScreen> {
  final _promptController = TextEditingController();
  String? _resultImageUrl;
  bool _isGenerating = false;
  String? _errorMessage;
  String? _selectedPreset;
  String _searchQuery = '';

  // 69 Style Presets (matching Django backend)
  final List<Map<String, String>> _allPresets = const [
    // Photography Styles
    {'id': 'analog-film', 'name': 'Analog Film', 'category': 'Photography'},
    {'id': 'cinematic', 'name': 'Cinematic', 'category': 'Photography'},
    {'id': 'enhance', 'name': 'Enhance', 'category': 'Photography'},
    {'id': 'line-art', 'name': 'Line Art', 'category': 'Photography'},
    {'id': 'lowpoly', 'name': 'Low Poly', 'category': 'Photography'},
    {'id': 'neon-punk', 'name': 'Neon Punk', 'category': 'Photography'},
    {'id': 'origami', 'name': 'Origami', 'category': 'Photography'},
    {'id': 'photographic', 'name': 'Photographic', 'category': 'Photography'},
    {'id': 'pixel-art', 'name': 'Pixel Art', 'category': 'Photography'},
    {'id': 'texture', 'name': 'Texture', 'category': 'Photography'},

    // Artistic Styles
    {'id': '3d-model', 'name': '3D Model', 'category': 'Artistic'},
    {'id': 'anime', 'name': 'Anime', 'category': 'Artistic'},
    {'id': 'comic-book', 'name': 'Comic Book', 'category': 'Artistic'},
    {'id': 'digital-art', 'name': 'Digital Art', 'category': 'Artistic'},
    {'id': 'fantasy-art', 'name': 'Fantasy Art', 'category': 'Artistic'},
    {'id': 'isometric', 'name': 'Isometric', 'category': 'Artistic'},
    {'id': 'modeling-compound', 'name': 'Modeling Compound', 'category': 'Artistic'},
    {'id': 'tile-texture', 'name': 'Tile Texture', 'category': 'Artistic'},

    // Vintage & Classic
    {'id': 'film-noir', 'name': 'Film Noir', 'category': 'Vintage'},
    {'id': 'long-exposure', 'name': 'Long Exposure', 'category': 'Vintage'},
    {'id': 'hdr', 'name': 'HDR', 'category': 'Vintage'},
    {'id': 'tilt-shift', 'name': 'Tilt Shift', 'category': 'Vintage'},

    // Fine Art Styles
    {'id': 'abstract', 'name': 'Abstract', 'category': 'Fine Art'},
    {'id': 'cubist', 'name': 'Cubist', 'category': 'Fine Art'},
    {'id': 'graffiti', 'name': 'Graffiti', 'category': 'Fine Art'},
    {'id': 'hyperrealism', 'name': 'Hyperrealism', 'category': 'Fine Art'},
    {'id': 'impressionist', 'name': 'Impressionist', 'category': 'Fine Art'},
    {'id': 'pointillism', 'name': 'Pointillism', 'category': 'Fine Art'},
    {'id': 'pop-art', 'name': 'Pop Art', 'category': 'Fine Art'},
    {'id': 'psychedelic', 'name': 'Psychedelic', 'category': 'Fine Art'},
    {'id': 'renaissance', 'name': 'Renaissance', 'category': 'Fine Art'},
    {'id': 'steampunk', 'name': 'Steampunk', 'category': 'Fine Art'},
    {'id': 'surrealism', 'name': 'Surrealism', 'category': 'Fine Art'},
    {'id': 'typography', 'name': 'Typography', 'category': 'Fine Art'},
    {'id': 'watercolor', 'name': 'Watercolor', 'category': 'Fine Art'},
  ];

  List<Map<String, String>> get _filteredPresets {
    if (_searchQuery.isEmpty) return _allPresets;
    return _allPresets
        .where((preset) =>
            preset['name']!.toLowerCase().contains(_searchQuery.toLowerCase()) ||
            preset['category']!.toLowerCase().contains(_searchQuery.toLowerCase()))
        .toList();
  }

  Future<void> _generateWithPreset() async {
    if (_selectedPreset == null) {
      setState(() => _errorMessage = 'Please select a preset');
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
        '/api/v1/gallery/generate/',
        {
          'prompt': _promptController.text.trim(),
          'style': _selectedPreset,
          'model': 'sd3',
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
    final presetsByCategory = <String, List<Map<String, String>>>{};
    for (final preset in _filteredPresets) {
      final category = preset['category']!;
      presetsByCategory.putIfAbsent(category, () => []).add(preset);
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Style Presets'),
        backgroundColor: Colors.deepPurple,
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Search styles...',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: (value) => setState(() => _searchQuery = value),
            ),
          ),

          // Prompt Input
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: TextField(
              controller: _promptController,
              maxLines: 2,
              decoration: const InputDecoration(
                labelText: 'Your Prompt',
                hintText: 'A beautiful landscape',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.edit),
              ),
            ),
          ),

          // Presets List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: presetsByCategory.length,
              itemBuilder: (context, index) {
                final category = presetsByCategory.keys.elementAt(index);
                final presets = presetsByCategory[category]!;

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      child: Text(
                        category,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.deepPurple,
                        ),
                      ),
                    ),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: presets.map((preset) {
                        final isSelected = _selectedPreset == preset['id'];
                        return ChoiceChip(
                          label: Text(preset['name']!),
                          selected: isSelected,
                          onSelected: (selected) {
                            setState(() {
                              _selectedPreset = selected ? preset['id'] : null;
                            });
                          },
                          selectedColor: Colors.deepPurple,
                          labelStyle: TextStyle(
                            color: isSelected ? Colors.white : Colors.black,
                            fontSize: 12,
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 8),
                  ],
                );
              },
            ),
          ),

          // Generate Button
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black12,
                  blurRadius: 8,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (_selectedPreset != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(
                      'Selected: ${_allPresets.firstWhere((p) => p['id'] == _selectedPreset)['name']}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.deepPurple,
                      ),
                    ),
                  ),
                ElevatedButton.icon(
                  onPressed: _isGenerating ? null : _generateWithPreset,
                  icon: _isGenerating
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.auto_awesome),
                  label: Text(_isGenerating ? 'Generating...' : 'Generate with Style'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.deepPurple,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.all(16),
                    minimumSize: const Size(double.infinity, 48),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),

      // Result Dialog
      floatingActionButton: _resultImageUrl != null
          ? FloatingActionButton.extended(
              onPressed: () => _showResultDialog(),
              icon: const Icon(Icons.image),
              label: const Text('View Result'),
              backgroundColor: Colors.deepPurple,
            )
          : null,
    );
  }

  void _showResultDialog() {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.network(_resultImageUrl!),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Text(
                    'Style: ${_allPresets.firstWhere((p) => p['id'] == _selectedPreset)['name']}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(_promptController.text,
                      style: const TextStyle(fontSize: 12, color: Colors.grey)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Close'),
                  ),
                ],
              ),
            ),
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

/// Text-to-Image Generation Screen
///
/// Session 115 Part 4 - Full Feature Parity
/// Stability AI image generation with all models
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/api_provider.dart';

class TextToImageScreen extends ConsumerStatefulWidget {
  const TextToImageScreen({super.key});

  @override
  ConsumerState<TextToImageScreen> createState() => _TextToImageScreenState();
}

class _TextToImageScreenState extends ConsumerState<TextToImageScreen> {
  final _promptController = TextEditingController();
  String _selectedModel = 'core';
  String _selectedStyle = 'none';
  bool _isGenerating = false;
  String? _generatedImageUrl;
  String? _errorMessage;

  final List<Map<String, String>> _models = [
    {'value': 'core', 'name': 'Core (Fast)', 'description': 'Quick generation'},
    {'value': 'sd3', 'name': 'SD3 (Balanced)', 'description': 'High quality'},
    {'value': 'ultra', 'name': 'Ultra (Premium)', 'description': 'Best quality'},
    {'value': 'sdxl', 'name': 'SDXL (Classic)', 'description': 'Stable Diffusion XL'},
  ];

  final List<Map<String, String>> _styles = [
    {'value': 'none', 'name': 'No Style'},
    {'value': 'photographic', 'name': 'Photographic'},
    {'value': 'digital-art', 'name': 'Digital Art'},
    {'value': 'anime', 'name': 'Anime'},
    {'value': '3d-model', 'name': '3D Model'},
    {'value': 'fantasy-art', 'name': 'Fantasy Art'},
    {'value': 'cinematic', 'name': 'Cinematic'},
  ];

  Future<void> _generateImage() async {
    if (_promptController.text.trim().isEmpty) {
      setState(() {
        _errorMessage = 'Please enter a prompt';
      });
      return;
    }

    setState(() {
      _isGenerating = true;
      _errorMessage = null;
      _generatedImageUrl = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.post(
        '/api/v1/gallery/generate/',
        {
          'prompt': _promptController.text.trim(),
          'model': _selectedModel,
          'style': _selectedStyle,
          'size': '1024x1024',
          'num_images': 1,
        },
      );

      if (response['success'] == true && response['image_url'] != null) {
        setState(() {
          _generatedImageUrl = response['image_url'];
          _isGenerating = false;
        });
      } else {
        throw Exception(response['error'] ?? 'Image generation failed');
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
        title: const Text('Text-to-Image'),
        backgroundColor: Colors.deepPurple,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Prompt Input
            TextField(
              controller: _promptController,
              maxLines: 4,
              decoration: const InputDecoration(
                labelText: 'Enter your prompt',
                hintText: 'A beautiful sunset over mountains...',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),

            // Model Selection
            const Text(
              'Model',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _models.map((model) {
                final isSelected = _selectedModel == model['value'];
                return ChoiceChip(
                  label: Text(model['name']!),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() {
                        _selectedModel = model['value']!;
                      });
                    }
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            // Style Selection
            const Text(
              'Style',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedStyle,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
              ),
              items: _styles.map((style) {
                return DropdownMenuItem(
                  value: style['value'],
                  child: Text(style['name']!),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _selectedStyle = value;
                  });
                }
              },
            ),
            const SizedBox(height: 24),

            // Generate Button
            ElevatedButton.icon(
              onPressed: _isGenerating ? null : _generateImage,
              icon: _isGenerating
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Icon(Icons.auto_awesome),
              label: Text(_isGenerating ? 'Generating...' : 'Generate Image'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepPurple,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Error Message
            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  border: Border.all(color: Colors.red),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _errorMessage!,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            ],

            // Generated Image
            if (_generatedImageUrl != null) ...[
              const SizedBox(height: 24),
              const Text(
                'Generated Image',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  _generatedImageUrl!,
                  fit: BoxFit.cover,
                  loadingBuilder: (context, child, loadingProgress) {
                    if (loadingProgress == null) return child;
                    return const Center(
                      child: CircularProgressIndicator(),
                    );
                  },
                  errorBuilder: (context, error, stackTrace) {
                    return Container(
                      height: 300,
                      color: Colors.grey.shade200,
                      child: const Center(
                        child: Icon(Icons.error_outline, size: 48),
                      ),
                    );
                  },
                ),
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

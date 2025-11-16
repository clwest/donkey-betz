/// Sketch-to-Image Screen - Convert sketches to detailed images
/// Session 115 Part 5 - Dual-Source Image Picker Integration
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:typed_data';
import '../../providers/api_provider.dart';
import '../../widgets/dual_source_image_picker.dart';

class SketchToImageScreen extends ConsumerStatefulWidget {
  const SketchToImageScreen({super.key});

  @override
  ConsumerState<SketchToImageScreen> createState() => _SketchToImageScreenState();
}

class _SketchToImageScreenState extends ConsumerState<SketchToImageScreen> {
  final _promptController = TextEditingController();
  Uint8List? _imageBytes;
  String? _fileName;
  String? _resultImageUrl;
  bool _isProcessing = false;
  String? _errorMessage;
  double _controlStrength = 0.7;

  void _onImageSelected(Uint8List bytes, String fileName) {
    setState(() {
      _imageBytes = bytes;
      _fileName = fileName;
      _errorMessage = null;
    });
  }

  Future<void> _generateFromSketch() async {
    if (_imageBytes == null) {
      setState(() => _errorMessage = 'Please select a sketch');
      return;
    }

    if (_promptController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter a prompt');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.postMultipart(
        '/api/v1/gallery/sketch-to-image/',
        fileBytes: {'image': _imageBytes!},
        fileName: _fileName ?? 'sketch.jpg',
        fields: {
          'prompt': _promptController.text.trim(),
          'control_strength': _controlStrength.toString(),
        },
      );

      if (response['success'] == true) {
        setState(() {
          _resultImageUrl = response['image_url'];
          _isProcessing = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isProcessing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sketch to Image'),
        backgroundColor: Colors.purple,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Dual-Source Image Picker
            DualSourceImagePicker(
              currentImageBytes: _imageBytes,
              onImageSelected: _onImageSelected,
              placeholderText: 'Upload sketch (line drawing or wireframe)',
              height: 200,
            ),
            const SizedBox(height: 16),

            // Prompt
            TextField(
              controller: _promptController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Describe the final image',
                hintText: 'A futuristic cityscape at sunset',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.edit),
              ),
            ),
            const SizedBox(height: 16),

            // Control Strength
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Control Strength:',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('${(_controlStrength * 100).toInt()}%',
                        style: const TextStyle(color: Colors.purple)),
                  ],
                ),
                Slider(
                  value: _controlStrength,
                  min: 0.1,
                  max: 1.0,
                  divisions: 9,
                  activeColor: Colors.purple,
                  label: '${(_controlStrength * 100).toInt()}%',
                  onChanged: (value) => setState(() => _controlStrength = value),
                ),
                const Text(
                  'Higher = more faithful to sketch | Lower = more creative',
                  style: TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Generate Button
            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _generateFromSketch,
              icon: _isProcessing
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.auto_awesome),
              label: Text(_isProcessing ? 'Generating...' : 'Generate Image'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.purple,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Result
            if (_resultImageUrl != null) ...[
              const SizedBox(height: 24),
              const Text('Result:', style: TextStyle(fontWeight: FontWeight.bold)),
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
    _promptController.dispose();
    super.dispose();
  }
}

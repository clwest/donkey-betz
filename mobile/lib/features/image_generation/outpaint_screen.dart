/// Outpaint Screen - Extend images beyond their borders
/// Session 115 Part 5 - Dual-Source Image Picker Integration
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:typed_data';
import '../../providers/api_provider.dart';
import '../../widgets/dual_source_image_picker.dart';

class OutpaintScreen extends ConsumerStatefulWidget {
  const OutpaintScreen({super.key});

  @override
  ConsumerState<OutpaintScreen> createState() => _OutpaintScreenState();
}

class _OutpaintScreenState extends ConsumerState<OutpaintScreen> {
  final _promptController = TextEditingController();
  Uint8List? _imageBytes;
  String? _fileName;
  String? _resultImageUrl;
  bool _isProcessing = false;
  String? _errorMessage;
  String _direction = 'all';
  double _creativity = 0.7;

  void _onImageSelected(Uint8List bytes, String fileName) {
    setState(() {
      _imageBytes = bytes;
      _fileName = fileName;
      _errorMessage = null;
    });
  }

  Future<void> _outpaint() async {
    if (_imageBytes == null) {
      setState(() => _errorMessage = 'Please select an image');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.postMultipart(
        '/api/v1/gallery/outpaint/',
        fileBytes: {'image': _imageBytes!},
        fileName: _fileName ?? 'image.jpg',
        fields: {
          'prompt': _promptController.text.trim(),
          'direction': _direction,
          'creativity': _creativity.toString(),
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
        title: const Text('Outpaint'),
        backgroundColor: Colors.lime,
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
              placeholderText: 'Select image to expand beyond borders',
              height: 200,
            ),
            const SizedBox(height: 16),

            // Direction Selection
            const Text('Expand Direction:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: 'all',
                  label: Text('All'),
                  icon: Icon(Icons.open_in_full),
                ),
                ButtonSegment(
                  value: 'horizontal',
                  label: Text('H'),
                  icon: Icon(Icons.swap_horiz),
                ),
                ButtonSegment(
                  value: 'vertical',
                  label: Text('V'),
                  icon: Icon(Icons.swap_vert),
                ),
              ],
              selected: {_direction},
              onSelectionChanged: (Set<String> selection) {
                setState(() => _direction = selection.first);
              },
            ),
            const SizedBox(height: 16),

            // Optional Prompt
            TextField(
              controller: _promptController,
              maxLines: 2,
              decoration: const InputDecoration(
                labelText: 'Optional: Describe what to add (optional)',
                hintText: 'Mountain landscape, blue sky...',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.edit),
              ),
            ),
            const SizedBox(height: 16),

            // Creativity Slider
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Creativity:',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('${(_creativity * 100).toInt()}%',
                        style: const TextStyle(color: Colors.lime)),
                  ],
                ),
                Slider(
                  value: _creativity,
                  min: 0.1,
                  max: 1.0,
                  divisions: 9,
                  activeColor: Colors.lime,
                  label: '${(_creativity * 100).toInt()}%',
                  onChanged: (value) => setState(() => _creativity = value),
                ),
                const Text(
                  'Higher = more creative continuation | Lower = closer match to original',
                  style: TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Outpaint Button
            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _outpaint,
              icon: _isProcessing
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.expand),
              label: Text(_isProcessing ? 'Expanding...' : 'Outpaint'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.lime,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Result
            if (_resultImageUrl != null) ...[
              const SizedBox(height: 24),
              const Text('Result (Expanded):',
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

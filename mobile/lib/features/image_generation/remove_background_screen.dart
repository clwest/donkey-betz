/// Remove Background Screen
/// Session 115 Part 5 - Dual-Source Image Picker Integration
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:typed_data';
import '../../providers/api_provider.dart';
import '../../widgets/dual_source_image_picker.dart';

class RemoveBackgroundScreen extends ConsumerStatefulWidget {
  const RemoveBackgroundScreen({super.key});

  @override
  ConsumerState<RemoveBackgroundScreen> createState() => _RemoveBackgroundScreenState();
}

class _RemoveBackgroundScreenState extends ConsumerState<RemoveBackgroundScreen> {
  Uint8List? _imageBytes;
  String? _fileName;
  String? _resultImageUrl;
  bool _isProcessing = false;
  String? _errorMessage;

  void _onImageSelected(Uint8List bytes, String fileName) {
    setState(() {
      _imageBytes = bytes;
      _fileName = fileName;
      _errorMessage = null;
    });
  }

  Future<void> _removeBackground() async {
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
        '/api/v1/gallery/remove-background/',
        fileBytes: {'image': _imageBytes!},
        fileName: _fileName ?? 'image.jpg',
        fields: {},
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
        title: const Text('Remove Background'),
        backgroundColor: Colors.green,
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
              placeholderText: 'Select image to remove background',
              height: 300,
            ),
            const SizedBox(height: 24),

            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _removeBackground,
              icon: _isProcessing
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.layers_clear),
              label: Text(_isProcessing ? 'Removing...' : 'Remove Background'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            if (_resultImageUrl != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Result (transparent background):',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Container(
                      decoration: BoxDecoration(
                        // Checkered pattern to show transparency
                        color: Colors.white,
                        image: const DecorationImage(
                          image: AssetImage('assets/transparency_grid.png'),
                          repeat: ImageRepeat.repeat,
                        ),
                      ),
                      child: Image.network(_resultImageUrl!),
                    ),
                  ],
                ),
              ),
            ],

            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
            ],
          ],
        ),
      ),
    );
  }
}

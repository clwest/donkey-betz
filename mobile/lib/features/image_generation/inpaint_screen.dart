/// Inpaint Screen - Mask-based editing
/// Session 115 Part 5 - Dual-Source Image Picker Integration
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:typed_data';
import '../../providers/api_provider.dart';
import '../../widgets/dual_source_image_picker.dart';

class InpaintScreen extends ConsumerStatefulWidget {
  const InpaintScreen({super.key});

  @override
  ConsumerState<InpaintScreen> createState() => _InpaintScreenState();
}

class _InpaintScreenState extends ConsumerState<InpaintScreen> {
  final _promptController = TextEditingController();
  Uint8List? _sourceImageBytes;
  String? _sourceFileName;
  Uint8List? _maskImageBytes;
  String? _maskFileName;
  String? _resultImageUrl;
  bool _isProcessing = false;
  String? _errorMessage;

  void _onSourceImageSelected(Uint8List bytes, String fileName) {
    setState(() {
      _sourceImageBytes = bytes;
      _sourceFileName = fileName;
      _errorMessage = null;
    });
  }

  void _onMaskImageSelected(Uint8List bytes, String fileName) {
    setState(() {
      _maskImageBytes = bytes;
      _maskFileName = fileName;
      _errorMessage = null;
    });
  }

  Future<void> _inpaint() async {
    if (_sourceImageBytes == null || _maskImageBytes == null) {
      setState(() => _errorMessage = 'Please select both source and mask images');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.postMultipart(
        '/api/v1/gallery/inpaint/',
        fileBytes: {
          'image': _sourceImageBytes!,
          'mask': _maskImageBytes!,
        },
        fileName: _sourceFileName ?? 'image.jpg',
        fields: {
          'prompt': _promptController.text.trim(),
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
        title: const Text('Inpaint'),
        backgroundColor: Colors.indigo,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('1. Source Image:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DualSourceImagePicker(
              currentImageBytes: _sourceImageBytes,
              onImageSelected: _onSourceImageSelected,
              placeholderText: 'Select source image',
              height: 150,
            ),
            const SizedBox(height: 16),

            const Text('2. Mask Image (area to change):', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DualSourceImagePicker(
              currentImageBytes: _maskImageBytes,
              onImageSelected: _onMaskImageSelected,
              placeholderText: 'Select mask image',
              height: 150,
            ),
            const SizedBox(height: 16),

            TextField(
              controller: _promptController,
              maxLines: 2,
              decoration: const InputDecoration(
                labelText: 'What to put in masked area',
                hintText: 'A red sports car',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),

            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _inpaint,
              icon: _isProcessing
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.auto_fix_high),
              label: Text(_isProcessing ? 'Processing...' : 'Inpaint'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.indigo,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            if (_resultImageUrl != null) ...[
              const SizedBox(height: 16),
              const Text('Result:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Image.network(_resultImageUrl!),
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

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }
}

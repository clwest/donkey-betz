/// Inpaint Screen - Mask-based editing
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../providers/api_provider.dart';

class InpaintScreen extends ConsumerStatefulWidget {
  const InpaintScreen({super.key});

  @override
  ConsumerState<InpaintScreen> createState() => _InpaintScreenState();
}

class _InpaintScreenState extends ConsumerState<InpaintScreen> {
  final _promptController = TextEditingController();
  File? _sourceImage;
  File? _maskImage;
  String? _resultImageUrl;
  bool _isProcessing = false;
  String? _errorMessage;

  Future<void> _pickImage(bool isMask) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    if (pickedFile != null) {
      setState(() {
        if (isMask) {
          _maskImage = File(pickedFile.path);
        } else {
          _sourceImage = File(pickedFile.path);
        }
      });
    }
  }

  Future<void> _inpaint() async {
    if (_sourceImage == null || _maskImage == null) {
      setState(() => _errorMessage = 'Please select both source and mask images');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.post(
        '/api/v1/gallery/inpaint/',
        {
          'prompt': _promptController.text.trim(),
          'image_url': 'temp', // TODO: File upload
          'mask_url': 'temp',
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
            GestureDetector(
              onTap: () => _pickImage(false),
              child: Container(
                height: 150,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.indigo),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: _sourceImage != null
                    ? Image.file(_sourceImage!, fit: BoxFit.cover)
                    : const Center(child: Icon(Icons.add_photo_alternate, size: 48)),
              ),
            ),
            const SizedBox(height: 16),

            const Text('2. Mask Image (area to change):', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () => _pickImage(true),
              child: Container(
                height: 150,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.indigo),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: _maskImage != null
                    ? Image.file(_maskImage!, fit: BoxFit.cover)
                    : const Center(child: Icon(Icons.brush, size: 48)),
              ),
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

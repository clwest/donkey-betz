/// Search & Replace Screen - Object replacement with prompts
/// Session 115 Part 5 - Dual-Source Image Picker Integration
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:typed_data';
import '../../providers/api_provider.dart';
import '../../widgets/dual_source_image_picker.dart';

class SearchReplaceScreen extends ConsumerStatefulWidget {
  const SearchReplaceScreen({super.key});

  @override
  ConsumerState<SearchReplaceScreen> createState() => _SearchReplaceScreenState();
}

class _SearchReplaceScreenState extends ConsumerState<SearchReplaceScreen> {
  final _searchController = TextEditingController();
  final _replaceController = TextEditingController();
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

  Future<void> _searchAndReplace() async {
    if (_imageBytes == null) {
      setState(() => _errorMessage = 'Please select an image');
      return;
    }

    if (_searchController.text.trim().isEmpty || _replaceController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter both search and replace prompts');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.postMultipart(
        '/api/v1/gallery/search-replace/',
        fileBytes: {'image': _imageBytes!},
        fileName: _fileName ?? 'image.jpg',
        fields: {
          'search': _searchController.text.trim(),
          'replace': _replaceController.text.trim(),
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
        title: const Text('Search & Replace'),
        backgroundColor: Colors.cyan,
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
              placeholderText: 'Select image for search & replace',
              height: 200,
            ),
            const SizedBox(height: 16),

            TextField(
              controller: _searchController,
              decoration: const InputDecoration(
                labelText: 'Search for (object to replace)',
                hintText: 'red car',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.search),
              ),
            ),
            const SizedBox(height: 12),

            const Icon(Icons.arrow_downward, color: Colors.cyan),
            const SizedBox(height: 12),

            TextField(
              controller: _replaceController,
              decoration: const InputDecoration(
                labelText: 'Replace with',
                hintText: 'blue motorcycle',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.auto_fix_high),
              ),
            ),
            const SizedBox(height: 24),

            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _searchAndReplace,
              icon: _isProcessing
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.find_replace),
              label: Text(_isProcessing ? 'Processing...' : 'Search & Replace'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.cyan,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

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
    _searchController.dispose();
    _replaceController.dispose();
    super.dispose();
  }
}

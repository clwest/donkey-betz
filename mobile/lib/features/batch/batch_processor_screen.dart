/// Batch Processor Screen - Process multiple images with the same operation
/// Session 115 Part 5 - Advanced Features
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../providers/api_provider.dart';

class BatchProcessorScreen extends ConsumerStatefulWidget {
  const BatchProcessorScreen({super.key});

  @override
  ConsumerState<BatchProcessorScreen> createState() => _BatchProcessorScreenState();
}

class _BatchProcessorScreenState extends ConsumerState<BatchProcessorScreen> {
  final List<File> _selectedImages = [];
  final List<String> _resultUrls = [];
  bool _isProcessing = false;
  String? _errorMessage;
  String _operation = 'upscale';
  int _processedCount = 0;

  final List<Map<String, String>> _operations = const [
    {'id': 'upscale', 'name': 'Upscale 4x', 'icon': '🔍'},
    {'id': 'remove-bg', 'name': 'Remove Background', 'icon': '🎭'},
    {'id': 'enhance', 'name': 'Enhance Quality', 'icon': '✨'},
    {'id': 'compress', 'name': 'Compress/Optimize', 'icon': '📦'},
  ];

  Future<void> _pickImages() async {
    final picker = ImagePicker();
    final pickedFiles = await picker.pickMultiImage();

    if (pickedFiles.isNotEmpty) {
      setState(() {
        _selectedImages.addAll(pickedFiles.map((file) => File(file.path)));
      });
    }
  }

  void _removeImage(int index) {
    setState(() => _selectedImages.removeAt(index));
  }

  Future<void> _processBatch() async {
    if (_selectedImages.isEmpty) {
      setState(() => _errorMessage = 'Please select images');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
      _processedCount = 0;
      _resultUrls.clear();
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      // Process each image
      for (int i = 0; i < _selectedImages.length; i++) {
        final response = await apiClient.post(
          '/api/v1/batch/$_operation/',
          {
            'image_url': 'temp', // TODO: File upload
            'batch_index': i,
            'total_count': _selectedImages.length,
          },
        );

        if (response['success'] == true && response['image_url'] != null) {
          setState(() {
            _resultUrls.add(response['image_url']);
            _processedCount = i + 1;
          });
        }

        // Small delay to avoid overwhelming the server
        await Future.delayed(const Duration(milliseconds: 500));
      }

      setState(() => _isProcessing = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Batch complete! Processed ${_selectedImages.length} images'),
            backgroundColor: Colors.green,
          ),
        );
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
    final progress = _selectedImages.isEmpty
        ? 0.0
        : _processedCount / _selectedImages.length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Batch Processor'),
        backgroundColor: Colors.indigo,
      ),
      body: Column(
        children: [
          // Progress Indicator
          if (_isProcessing)
            LinearProgressIndicator(
              value: progress,
              backgroundColor: Colors.grey.shade200,
              valueColor: const AlwaysStoppedAnimation(Colors.indigo),
            ),

          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Info Card
                  Card(
                    color: Colors.indigo.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.batch_prediction,
                                  color: Colors.indigo, size: 28),
                              const SizedBox(width: 12),
                              const Text(
                                'Batch Processing',
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Apply the same operation to multiple images at once. Perfect for bulk editing!',
                            style: TextStyle(fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Operation Selection
                  const Text('Select Operation:',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _operations.map((op) {
                      final isSelected = _operation == op['id'];
                      return ChoiceChip(
                        label: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(op['icon']!),
                            const SizedBox(width: 6),
                            Text(op['name']!),
                          ],
                        ),
                        selected: isSelected,
                        onSelected: _isProcessing
                            ? null
                            : (selected) {
                                if (selected) {
                                  setState(() => _operation = op['id']!);
                                }
                              },
                        selectedColor: Colors.indigo,
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.white : Colors.black,
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),

                  // Image Selection
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Selected Images (${_selectedImages.length})',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      TextButton.icon(
                        onPressed: _isProcessing ? null : _pickImages,
                        icon: const Icon(Icons.add_photo_alternate),
                        label: const Text('Add Images'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Image Grid
                  if (_selectedImages.isEmpty)
                    Container(
                      height: 200,
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey.shade300),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.photo_library,
                                size: 48, color: Colors.grey),
                            SizedBox(height: 12),
                            Text('No images selected',
                                style: TextStyle(color: Colors.grey)),
                            SizedBox(height: 4),
                            Text('Tap "Add Images" to get started',
                                style: TextStyle(
                                    fontSize: 12, color: Colors.grey)),
                          ],
                        ),
                      ),
                    )
                  else
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 3,
                        crossAxisSpacing: 8,
                        mainAxisSpacing: 8,
                      ),
                      itemCount: _selectedImages.length,
                      itemBuilder: (context, index) {
                        final isProcessed = index < _processedCount;
                        return Stack(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Stack(
                                fit: StackFit.expand,
                                children: [
                                  Image.file(
                                    _selectedImages[index],
                                    fit: BoxFit.cover,
                                  ),
                                  if (isProcessed)
                                    Container(
                                      color: Colors.green.withOpacity(0.3),
                                      child: const Icon(
                                        Icons.check_circle,
                                        color: Colors.white,
                                        size: 32,
                                      ),
                                    ),
                                  if (_isProcessing && index == _processedCount)
                                    Container(
                                      color: Colors.black54,
                                      child: const Center(
                                        child: CircularProgressIndicator(
                                          color: Colors.white,
                                          strokeWidth: 2,
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                            ),
                            if (!_isProcessing)
                              Positioned(
                                top: 4,
                                right: 4,
                                child: CircleAvatar(
                                  radius: 12,
                                  backgroundColor: Colors.red,
                                  child: IconButton(
                                    padding: EdgeInsets.zero,
                                    icon: const Icon(Icons.close,
                                        size: 16, color: Colors.white),
                                    onPressed: () => _removeImage(index),
                                  ),
                                ),
                              ),
                          ],
                        );
                      },
                    ),

                  const SizedBox(height: 24),

                  // Process Button
                  ElevatedButton.icon(
                    onPressed:
                        _isProcessing || _selectedImages.isEmpty ? null : _processBatch,
                    icon: _isProcessing
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2))
                        : const Icon(Icons.play_arrow),
                    label: Text(_isProcessing
                        ? 'Processing... ($_processedCount/${_selectedImages.length})'
                        : 'Process ${_selectedImages.length} Images'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.indigo,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.all(16),
                    ),
                  ),

                  // Results Section
                  if (_resultUrls.isNotEmpty) ...[
                    const SizedBox(height: 32),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Results:',
                            style: TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 18)),
                        TextButton.icon(
                          onPressed: () {
                            // TODO: Download all results
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                  content: Text('Download all feature coming!')),
                            );
                          },
                          icon: const Icon(Icons.download),
                          label: const Text('Download All'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate:
                          const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                      ),
                      itemCount: _resultUrls.length,
                      itemBuilder: (context, index) {
                        return ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.network(
                            _resultUrls[index],
                            fit: BoxFit.cover,
                          ),
                        );
                      },
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
          ),
        ],
      ),
    );
  }
}

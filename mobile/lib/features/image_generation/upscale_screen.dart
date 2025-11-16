/// Image Upscale Screen
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../../providers/api_provider.dart';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
// Platform-specific imports
import 'package:file_picker/file_picker.dart' if (dart.library.html) 'package:file_picker/file_picker.dart';
import 'dart:html' as html if (dart.library.io) 'dart:io';

class UpscaleScreen extends ConsumerStatefulWidget {
  const UpscaleScreen({super.key});

  @override
  ConsumerState<UpscaleScreen> createState() => _UpscaleScreenState();
}

class _UpscaleScreenState extends ConsumerState<UpscaleScreen> {
  Uint8List? _imageBytes; // Store image bytes
  String? _fileName; // Store filename
  String? _upscaledImageUrl;
  bool _isUpscaling = false;
  String? _errorMessage;
  String _mode = 'fast'; // fast, conservative, or creative

  Future<void> _selectFromGallery() async {
    try {
      final apiClient = ref.read(apiClientProvider);

      // Fetch gallery images
      final response = await apiClient.get('/api/v1/gallery/all/');

      if (!mounted) return;

      // Response format: { "count": N, "results": [...] }
      final results = (response['results'] as List?) ?? [];

      // Filter to only show images (exclude videos/audio)
      final images = results.where((item) => item['type'] == 'image').toList();

      if (images.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No images in gallery. Generate some images first!'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      // Show gallery selection dialog
      final selectedImageUrl = await showDialog<String>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Select from Gallery'),
          content: SizedBox(
            width: double.maxFinite,
            height: 400,
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                crossAxisSpacing: 8,
                mainAxisSpacing: 8,
              ),
              itemCount: images.length,
              itemBuilder: (context, index) {
                final image = images[index];
                final imageUrl = image['url'] as String;

                return InkWell(
                  onTap: () => Navigator.pop(context, imageUrl),
                  child: Image.network(
                    imageUrl,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => const Icon(Icons.error),
                  ),
                );
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
          ],
        ),
      );

      if (selectedImageUrl != null && mounted) {
        // Download the image as bytes
        final response = await http.get(Uri.parse(selectedImageUrl));

        if (response.statusCode == 200) {
          setState(() {
            _imageBytes = response.bodyBytes;
            _fileName = selectedImageUrl.split('/').last;
            _errorMessage = null;
          });

          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Image selected from gallery'),
                backgroundColor: Colors.green,
              ),
            );
          }
        }
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error loading gallery: ${e.toString()}';
      });
    }
  }

  Future<void> _pickImageFromDevice() async {
    if (kIsWeb) {
      // Web: Use native HTML file input
      try {
        final html.FileUploadInputElement uploadInput = html.FileUploadInputElement();
        uploadInput.accept = 'image/*';
        uploadInput.click();

        uploadInput.onChange.listen((e) {
          final files = uploadInput.files;
          if (files != null && files.isNotEmpty) {
            final file = files[0];
            final reader = html.FileReader();

            reader.onLoadEnd.listen((e) {
              setState(() {
                _imageBytes = reader.result as Uint8List;
                _fileName = file.name;
                _errorMessage = null;
              });

              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Image selected: ${file.name}'),
                    backgroundColor: Colors.green,
                    duration: const Duration(seconds: 1),
                  ),
                );
              }
            });

            reader.readAsArrayBuffer(file);
          }
        });
      } catch (e) {
        setState(() {
          _errorMessage = 'Error picking image: ${e.toString()}';
        });
      }
    } else {
      // Mobile: Use file_picker
      try {
        final result = await FilePicker.platform.pickFiles(
          type: FileType.image,
          allowMultiple: false,
        );

        if (result != null && result.files.isNotEmpty) {
          setState(() {
            _imageBytes = result.files.first.bytes;
            _fileName = result.files.first.name;
            _errorMessage = null;
          });

          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Image selected: ${result.files.first.name}'),
                backgroundColor: Colors.green,
                duration: const Duration(seconds: 1),
              ),
            );
          }
        }
      } catch (e) {
        setState(() {
          _errorMessage = 'Error picking image: ${e.toString()}';
        });
      }
    }
  }

  Future<void> _upscaleImage() async {
    if (_imageBytes == null) {
      setState(() => _errorMessage = 'Please select an image');
      return;
    }

    setState(() {
      _isUpscaling = true;
      _errorMessage = null;
      _upscaledImageUrl = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      // Session 115: Use bytes upload for both web and mobile
      final response = await apiClient.postMultipart(
        '/api/stability/upscale/',
        fileBytes: {'image': _imageBytes!},
        fileName: _fileName ?? 'image.jpg',
        fields: {'method': _mode}, // Backend expects 'method', not 'mode'
      );

      if (response['success'] == true && response['image_url'] != null) {
        setState(() {
          _upscaledImageUrl = response['image_url'];
          _isUpscaling = false;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Image upscaled successfully!'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        throw Exception(response['error'] ?? 'Upscale failed');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isUpscaling = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Upscale Image'),
        backgroundColor: Colors.teal,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Preview
            Container(
              height: 250,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.teal, width: 2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: _imageBytes != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: Image.memory(_imageBytes!, fit: BoxFit.contain),
                    )
                  : const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.add_photo_alternate, size: 64, color: Colors.teal),
                          SizedBox(height: 12),
                          Text(
                            'No image selected',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.teal,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Choose an image to upscale 4x',
                            style: TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
            ),
            const SizedBox(height: 16),

            // Selection Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _selectFromGallery,
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Gallery'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.teal,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _pickImageFromDevice,
                    icon: const Icon(Icons.upload_file),
                    label: const Text('Upload'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.teal.shade700,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Mode Selection
            const Text('Upscale Mode:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Column(
              children: [
                RadioListTile(
                  title: const Text('Fast (4x)'),
                  subtitle: const Text('Quick upscaling'),
                  value: 'fast',
                  groupValue: _mode,
                  onChanged: (value) => setState(() => _mode = value!),
                ),
                RadioListTile(
                  title: const Text('Conservative (4K)'),
                  subtitle: const Text('Preserve original details'),
                  value: 'conservative',
                  groupValue: _mode,
                  onChanged: (value) => setState(() => _mode = value!),
                ),
                RadioListTile(
                  title: const Text('Creative (AI Enhanced)'),
                  subtitle: const Text('Add intelligent details'),
                  value: 'creative',
                  groupValue: _mode,
                  onChanged: (value) => setState(() => _mode = value!),
                ),
              ],
            ),
            const SizedBox(height: 16),

            ElevatedButton.icon(
              onPressed: _isUpscaling ? null : _upscaleImage,
              icon: _isUpscaling
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.auto_fix_high),
              label: Text(_isUpscaling ? 'Upscaling...' : 'Upscale 4x'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            if (_upscaledImageUrl != null) ...[
              const SizedBox(height: 24),
              const Text('Upscaled Result:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Image.network(_upscaledImageUrl!),
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

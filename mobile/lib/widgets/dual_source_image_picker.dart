/// Dual-Source Image Picker Widget
/// Session 115 Part 5 - Reusable component for gallery + upload
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'dart:html' as html if (dart.library.io) 'dart:io';
import '../providers/api_provider.dart';

/// Callback when image is selected
typedef OnImageSelected = void Function(Uint8List imageBytes, String fileName);

/// Dual-source image picker: Gallery + Upload
class DualSourceImagePicker extends ConsumerStatefulWidget {
  final Uint8List? currentImageBytes;
  final OnImageSelected onImageSelected;
  final String? placeholderText;
  final double height;

  const DualSourceImagePicker({
    super.key,
    this.currentImageBytes,
    required this.onImageSelected,
    this.placeholderText,
    this.height = 250,
  });

  @override
  ConsumerState<DualSourceImagePicker> createState() => _DualSourceImagePickerState();
}

class _DualSourceImagePickerState extends ConsumerState<DualSourceImagePicker> {
  bool _isLoading = false;

  Future<void> _selectFromGallery() async {
    setState(() => _isLoading = true);

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
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('No images in gallery. Generate some images first!'),
              backgroundColor: Colors.orange,
            ),
          );
        }
        setState(() => _isLoading = false);
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
          final fileName = selectedImageUrl.split('/').last;
          widget.onImageSelected(response.bodyBytes, fileName);

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
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading gallery: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _pickImageFromDevice() async {
    setState(() => _isLoading = true);

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
              if (mounted) {
                final bytes = reader.result as Uint8List;
                widget.onImageSelected(bytes, file.name);

                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Image selected: ${file.name}'),
                    backgroundColor: Colors.green,
                    duration: const Duration(seconds: 1),
                  ),
                );

                setState(() => _isLoading = false);
              }
            });

            reader.readAsArrayBuffer(file);
          } else {
            setState(() => _isLoading = false);
          }
        });
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: ${e.toString()}'),
              backgroundColor: Colors.red,
            ),
          );
          setState(() => _isLoading = false);
        }
      }
    } else {
      // Mobile: Use file_picker
      try {
        final result = await FilePicker.platform.pickFiles(
          type: FileType.image,
          allowMultiple: false,
        );

        if (result != null && result.files.isNotEmpty) {
          final bytes = result.files.first.bytes;
          final fileName = result.files.first.name;

          if (bytes != null) {
            widget.onImageSelected(bytes, fileName);

            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Image selected: $fileName'),
                  backgroundColor: Colors.green,
                  duration: const Duration(seconds: 1),
                ),
              );
            }
          }
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: ${e.toString()}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } finally {
        if (mounted) {
          setState(() => _isLoading = false);
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Image Preview
        Container(
          height: widget.height,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.deepPurple, width: 2),
            borderRadius: BorderRadius.circular(12),
          ),
          child: widget.currentImageBytes != null
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: Image.memory(widget.currentImageBytes!, fit: BoxFit.contain),
                )
              : Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.add_photo_alternate, size: 64, color: Colors.deepPurple),
                      const SizedBox(height: 12),
                      const Text(
                        'No image selected',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.deepPurple,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        widget.placeholderText ?? 'Select an image to continue',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
        ),
        const SizedBox(height: 16),

        // Selection Buttons
        _isLoading
            ? const Center(child: CircularProgressIndicator())
            : Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _selectFromGallery,
                      icon: const Icon(Icons.photo_library),
                      label: const Text('Gallery'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.deepPurple,
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
                        backgroundColor: Colors.deepPurple.shade700,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.all(16),
                      ),
                    ),
                  ),
                ],
              ),
      ],
    );
  }
}

/// Dual-Source Video Picker Widget
/// Session 115 Part 8 - Reusable component for gallery + upload (videos)
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'dart:html' as html if (dart.library.io) 'dart:io';
import '../providers/api_provider.dart';

/// Callback when video is selected
typedef OnVideoSelected = void Function(Uint8List videoBytes, String fileName);

/// Dual-source video picker: Gallery + Upload
class DualSourceVideoPicker extends ConsumerStatefulWidget {
  final Uint8List? currentVideoBytes;
  final OnVideoSelected onVideoSelected;
  final String? placeholderText;
  final double height;

  const DualSourceVideoPicker({
    super.key,
    this.currentVideoBytes,
    required this.onVideoSelected,
    this.placeholderText,
    this.height = 250,
  });

  @override
  ConsumerState<DualSourceVideoPicker> createState() => _DualSourceVideoPickerState();
}

class _DualSourceVideoPickerState extends ConsumerState<DualSourceVideoPicker> {
  bool _isLoading = false;

  Future<void> _selectFromGallery() async {
    setState(() => _isLoading = true);

    try {
      final apiClient = ref.read(apiClientProvider);

      // Fetch gallery items
      final response = await apiClient.get('/api/v1/gallery/all/');

      if (!mounted) return;

      // Response format: { "count": N, "results": [...] }
      final results = (response['results'] as List?) ?? [];

      // Filter to only show videos
      final videos = results.where((item) => item['type'] == 'video').toList();

      if (videos.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('No videos in gallery. Generate some videos first!'),
              backgroundColor: Colors.orange,
            ),
          );
        }
        setState(() => _isLoading = false);
        return;
      }

      // Show gallery selection dialog
      final selectedVideoUrl = await showDialog<String>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Select from Gallery'),
          content: SizedBox(
            width: double.maxFinite,
            height: 400,
            child: ListView.builder(
              itemCount: videos.length,
              itemBuilder: (context, index) {
                final video = videos[index];
                final videoUrl = video['url'] as String;
                final videoId = video['id']?.toString() ?? 'unknown';
                final createdAt = video['created_at'] as String?;

                return Card(
                  margin: const EdgeInsets.symmetric(vertical: 4),
                  child: ListTile(
                    leading: const CircleAvatar(
                      backgroundColor: Colors.deepPurple,
                      child: Icon(Icons.videocam, color: Colors.white),
                    ),
                    title: Text('Video #$videoId'),
                    subtitle: createdAt != null
                        ? Text(
                            DateTime.parse(createdAt).toLocal().toString().split('.')[0],
                            style: const TextStyle(fontSize: 11),
                          )
                        : null,
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.pop(context, videoUrl),
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

      if (selectedVideoUrl != null && mounted) {
        // Download the video as bytes
        final response = await http.get(Uri.parse(selectedVideoUrl));

        if (response.statusCode == 200) {
          final fileName = selectedVideoUrl.split('/').last;
          widget.onVideoSelected(response.bodyBytes, fileName);

          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Video selected from gallery'),
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

  Future<void> _pickVideoFromDevice() async {
    setState(() => _isLoading = true);

    if (kIsWeb) {
      // Web: Use native HTML file input
      try {
        final html.FileUploadInputElement uploadInput = html.FileUploadInputElement();
        uploadInput.accept = 'video/*';
        uploadInput.click();

        uploadInput.onChange.listen((e) {
          final files = uploadInput.files;
          if (files != null && files.isNotEmpty) {
            final file = files[0];
            final reader = html.FileReader();

            reader.onLoadEnd.listen((e) {
              if (mounted) {
                final bytes = reader.result as Uint8List;
                widget.onVideoSelected(bytes, file.name);

                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Video selected: ${file.name}'),
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
          type: FileType.video,
          allowMultiple: false,
        );

        if (result != null && result.files.isNotEmpty) {
          final bytes = result.files.first.bytes;
          final fileName = result.files.first.name;

          if (bytes != null) {
            widget.onVideoSelected(bytes, fileName);

            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Video selected: $fileName'),
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
        // Video Preview/Placeholder
        Container(
          height: widget.height,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.deepPurple, width: 2),
            borderRadius: BorderRadius.circular(12),
            color: Colors.grey.shade100,
          ),
          child: widget.currentVideoBytes != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.videocam, size: 64, color: Colors.deepPurple),
                      const SizedBox(height: 12),
                      const Text(
                        'Video selected',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.deepPurple,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${(widget.currentVideoBytes!.length / 1024 / 1024).toStringAsFixed(2)} MB',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                )
              : Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.video_library, size: 64, color: Colors.grey),
                      const SizedBox(height: 12),
                      const Text(
                        'No video selected',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        widget.placeholderText ?? 'Select a video to continue',
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
                      onPressed: _pickVideoFromDevice,
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

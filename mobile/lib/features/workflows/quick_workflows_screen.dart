/// Quick Workflows Screen - One-tap common tasks
/// Session 115 Part 5 - Power User Features
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../providers/api_provider.dart';

class QuickWorkflowsScreen extends ConsumerStatefulWidget {
  const QuickWorkflowsScreen({super.key});

  @override
  ConsumerState<QuickWorkflowsScreen> createState() => _QuickWorkflowsScreenState();
}

class _QuickWorkflowsScreenState extends ConsumerState<QuickWorkflowsScreen> {
  File? _sourceImage;
  bool _isProcessing = false;
  String? _errorMessage;
  String? _resultUrl;

  final List<Map<String, dynamic>> _workflows = const [
    {
      'id': 'social-ready',
      'name': 'Social Media Ready',
      'description': 'Upscale + Enhance + Optimize',
      'icon': Icons.share,
      'color': Colors.blue,
      'steps': ['upscale', 'enhance', 'optimize'],
    },
    {
      'id': 'product-photo',
      'name': 'Product Photo',
      'description': 'Remove BG + White BG + Enhance',
      'icon': Icons.shopping_bag,
      'color': Colors.green,
      'steps': ['remove-bg', 'white-bg', 'enhance'],
    },
    {
      'id': 'profile-pic',
      'name': 'Profile Picture',
      'description': 'Remove BG + Face Enhance + Compress',
      'icon': Icons.person,
      'color': Colors.purple,
      'steps': ['remove-bg', 'face-enhance', 'compress'],
    },
    {
      'id': 'thumbnail',
      'name': 'YouTube Thumbnail',
      'description': 'Upscale + Saturate + Text Space',
      'icon': Icons.video_library,
      'color': Colors.red,
      'steps': ['upscale', 'saturate', 'text-space'],
    },
    {
      'id': 'print-ready',
      'name': 'Print Ready',
      'description': 'Upscale 4x + High DPI + Color Correct',
      'icon': Icons.print,
      'color': Colors.orange,
      'steps': ['upscale-4x', 'high-dpi', 'color-correct'],
    },
    {
      'id': 'web-optimized',
      'name': 'Web Optimized',
      'description': 'Resize + Compress + WebP',
      'icon': Icons.language,
      'color': Colors.teal,
      'steps': ['resize', 'compress', 'webp'],
    },
  ];

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    if (pickedFile != null) {
      setState(() => _sourceImage = File(pickedFile.path));
    }
  }

  Future<void> _runWorkflow(String workflowId) async {
    if (_sourceImage == null) {
      setState(() => _errorMessage = 'Please select an image first');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
      _resultUrl = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.post(
        '/api/v1/workflows/$workflowId/',
        {
          'image_url': 'temp', // TODO: File upload
        },
      );

      if (response['success'] == true && response['result_url'] != null) {
        setState(() {
          _resultUrl = response['result_url'];
          _isProcessing = false;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Workflow complete!'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        throw Exception(response['error'] ?? 'Workflow failed');
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
        title: const Text('Quick Workflows'),
        backgroundColor: Colors.deepOrange,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Info Card
            Card(
              color: Colors.deepOrange.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.flash_on, color: Colors.deepOrange, size: 28),
                        const SizedBox(width: 12),
                        const Text(
                          'Quick Workflows',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'One-tap workflows for common tasks. Each workflow runs multiple operations automatically.',
                      style: TextStyle(fontSize: 13),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Image Upload
            GestureDetector(
              onTap: _pickImage,
              child: Container(
                height: 200,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.deepOrange, width: 2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: _sourceImage != null
                    ? Image.file(_sourceImage!, fit: BoxFit.contain)
                    : const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.add_photo_alternate,
                                size: 64, color: Colors.deepOrange),
                            SizedBox(height: 12),
                            Text('Tap to select image',
                                style: TextStyle(fontWeight: FontWeight.bold)),
                            SizedBox(height: 4),
                            Text('Then choose a workflow below',
                                style:
                                    TextStyle(fontSize: 12, color: Colors.grey)),
                          ],
                        ),
                      ),
              ),
            ),
            const SizedBox(height: 24),

            // Workflows Grid
            const Text('Available Workflows:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 12),

            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 0.9,
              ),
              itemCount: _workflows.length,
              itemBuilder: (context, index) {
                final workflow = _workflows[index];
                return _buildWorkflowCard(workflow);
              },
            ),

            // Processing Indicator
            if (_isProcessing) ...[
              const SizedBox(height: 24),
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      const CircularProgressIndicator(),
                      const SizedBox(height: 12),
                      const Text('Running workflow...',
                          style: TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      const Text('This may take a few moments',
                          style: TextStyle(fontSize: 12, color: Colors.grey)),
                    ],
                  ),
                ),
              ),
            ],

            // Result
            if (_resultUrl != null) ...[
              const SizedBox(height: 24),
              const Text('Result:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(_resultUrl!),
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: () {
                  // TODO: Download
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Download feature coming!')),
                  );
                },
                icon: const Icon(Icons.download),
                label: const Text('Download Result'),
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
                child:
                    Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildWorkflowCard(Map<String, dynamic> workflow) {
    final color = workflow['color'] as Color;

    return Card(
      elevation: 2,
      child: InkWell(
        onTap: _isProcessing || _sourceImage == null
            ? null
            : () => _runWorkflow(workflow['id']),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(workflow['icon'] as IconData, size: 40, color: color),
              const SizedBox(height: 12),
              Text(
                workflow['name'],
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 6),
              Text(
                workflow['description'],
                style: const TextStyle(
                  fontSize: 11,
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${(workflow['steps'] as List).length} steps',
                  style: TextStyle(
                    fontSize: 10,
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

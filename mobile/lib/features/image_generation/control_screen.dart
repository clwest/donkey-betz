/// Control Screen - Generate images with structural control (Canny, depth, pose)
/// Session 115 Part 5 - Dual-Source Image Picker Integration
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:typed_data';
import '../../providers/api_provider.dart';
import '../../widgets/dual_source_image_picker.dart';

class ControlScreen extends ConsumerStatefulWidget {
  const ControlScreen({super.key});

  @override
  ConsumerState<ControlScreen> createState() => _ControlScreenState();
}

class _ControlScreenState extends ConsumerState<ControlScreen> {
  final _promptController = TextEditingController();
  Uint8List? _imageBytes;
  String? _fileName;
  String? _resultImageUrl;
  bool _isProcessing = false;
  String? _errorMessage;
  String _controlMode = 'canny';
  double _controlStrength = 0.7;

  final List<Map<String, dynamic>> _controlModes = [
    {
      'value': 'canny',
      'name': 'Canny Edge',
      'icon': Icons.border_outer,
      'description': 'Extract and follow edge structure',
    },
    {
      'value': 'depth',
      'name': 'Depth Map',
      'icon': Icons.layers,
      'description': 'Preserve depth and spatial layout',
    },
    {
      'value': 'pose',
      'name': 'Pose Control',
      'icon': Icons.accessibility_new,
      'description': 'Match human pose and skeleton',
    },
    {
      'value': 'structure',
      'name': 'Structure',
      'icon': Icons.grid_on,
      'description': 'Overall composition guidance',
    },
  ];

  void _onImageSelected(Uint8List bytes, String fileName) {
    setState(() {
      _imageBytes = bytes;
      _fileName = fileName;
      _errorMessage = null;
    });
  }

  Future<void> _generateWithControl() async {
    if (_imageBytes == null) {
      setState(() => _errorMessage = 'Please select a control image');
      return;
    }

    if (_promptController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter a prompt');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.postMultipart(
        '/api/v1/gallery/control/',
        fileBytes: {'image': _imageBytes!},
        fileName: _fileName ?? 'control.jpg',
        fields: {
          'prompt': _promptController.text.trim(),
          'control_mode': _controlMode,
          'control_strength': _controlStrength.toString(),
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
        title: const Text('Control Generation'),
        backgroundColor: Colors.teal,
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
              placeholderText: 'Upload control image for structural guidance',
              height: 200,
            ),
            const SizedBox(height: 16),

            // Control Mode Selection
            const Text('Control Mode:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ..._controlModes.map((mode) => RadioListTile<String>(
                  title: Row(
                    children: [
                      Icon(mode['icon'] as IconData, size: 20, color: Colors.teal),
                      const SizedBox(width: 8),
                      Text(mode['name'] as String),
                    ],
                  ),
                  subtitle: Text(mode['description'] as String,
                      style: const TextStyle(fontSize: 12)),
                  value: mode['value'] as String,
                  groupValue: _controlMode,
                  activeColor: Colors.teal,
                  onChanged: (value) => setState(() => _controlMode = value!),
                )),
            const SizedBox(height: 16),

            // Prompt
            TextField(
              controller: _promptController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Describe the desired image',
                hintText: 'A cyberpunk character in neon city',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.edit),
              ),
            ),
            const SizedBox(height: 16),

            // Control Strength
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Control Strength:',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('${(_controlStrength * 100).toInt()}%',
                        style: const TextStyle(color: Colors.teal)),
                  ],
                ),
                Slider(
                  value: _controlStrength,
                  min: 0.1,
                  max: 1.0,
                  divisions: 9,
                  activeColor: Colors.teal,
                  label: '${(_controlStrength * 100).toInt()}%',
                  onChanged: (value) => setState(() => _controlStrength = value),
                ),
                const Text(
                  'Higher = strict control | Lower = more creative freedom',
                  style: TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Generate Button
            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _generateWithControl,
              icon: _isProcessing
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.auto_awesome),
              label: Text(_isProcessing ? 'Generating...' : 'Generate with Control'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Result
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
    _promptController.dispose();
    super.dispose();
  }
}

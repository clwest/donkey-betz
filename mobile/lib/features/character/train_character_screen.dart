/// Train Character Screen - FLUX LoRA character training
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../providers/api_provider.dart';

class TrainCharacterScreen extends ConsumerStatefulWidget {
  const TrainCharacterScreen({super.key});

  @override
  ConsumerState<TrainCharacterScreen> createState() => _TrainCharacterScreenState();
}

class _TrainCharacterScreenState extends ConsumerState<TrainCharacterScreen> {
  final _characterNameController = TextEditingController();
  final _triggerWordController = TextEditingController();
  final List<File> _trainingImages = [];
  bool _isTraining = false;
  String? _errorMessage;
  String? _trainingId;
  int _steps = 1000;

  Future<void> _pickImages() async {
    final picker = ImagePicker();
    final pickedFiles = await picker.pickMultiImage();

    if (pickedFiles.isNotEmpty) {
      setState(() {
        _trainingImages.addAll(pickedFiles.map((file) => File(file.path)));
      });
    }
  }

  void _removeImage(int index) {
    setState(() => _trainingImages.removeAt(index));
  }

  Future<void> _startTraining() async {
    if (_characterNameController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter a character name');
      return;
    }

    if (_triggerWordController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter a trigger word');
      return;
    }

    if (_trainingImages.length < 5) {
      setState(() =>
          _errorMessage = 'Please upload at least 5 training images (10-20 recommended)');
      return;
    }

    setState(() {
      _isTraining = true;
      _errorMessage = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);

      final response = await apiClient.post(
        '/api/v1/character/train/',
        {
          'character_name': _characterNameController.text.trim(),
          'trigger_word': _triggerWordController.text.trim(),
          'training_images': 'temp', // TODO: File upload
          'steps': _steps,
        },
      );

      if (response['success'] == true && response['training_id'] != null) {
        setState(() {
          _trainingId = response['training_id'];
          _isTraining = false;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Training started! ID: $_trainingId'),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      } else {
        throw Exception(response['error'] ?? 'Training failed to start');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isTraining = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Train Character'),
        backgroundColor: Colors.blueGrey,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Info Card
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blueGrey.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blueGrey),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.person_add, color: Colors.blueGrey, size: 20),
                      SizedBox(width: 8),
                      Text('FLUX LoRA Character Training',
                          style: TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Train a custom character model using 5-20 images. Training takes ~10 minutes and creates a reusable character for future generations.',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Character Name
            TextField(
              controller: _characterNameController,
              decoration: const InputDecoration(
                labelText: 'Character Name',
                hintText: 'My Character',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.badge),
              ),
            ),
            const SizedBox(height: 16),

            // Trigger Word
            TextField(
              controller: _triggerWordController,
              decoration: const InputDecoration(
                labelText: 'Trigger Word',
                hintText: 'TOK (unique identifier in prompts)',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.label),
                helperText: 'Use this word in prompts to invoke your character',
              ),
            ),
            const SizedBox(height: 24),

            // Training Images
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Training Images (${_trainingImages.length})',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                TextButton.icon(
                  onPressed: _pickImages,
                  icon: const Icon(Icons.add_photo_alternate),
                  label: const Text('Add Images'),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // Image Grid
            if (_trainingImages.isEmpty)
              Container(
                height: 150,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300, style: BorderStyle.solid),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.photo_library, size: 48, color: Colors.grey),
                      SizedBox(height: 8),
                      Text('No images selected',
                          style: TextStyle(color: Colors.grey)),
                      SizedBox(height: 4),
                      Text('Add 5-20 high-quality images',
                          style: TextStyle(fontSize: 12, color: Colors.grey)),
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
                itemCount: _trainingImages.length,
                itemBuilder: (context, index) {
                  return Stack(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.file(
                          _trainingImages[index],
                          fit: BoxFit.cover,
                          width: double.infinity,
                          height: double.infinity,
                        ),
                      ),
                      Positioned(
                        top: 4,
                        right: 4,
                        child: CircleAvatar(
                          radius: 12,
                          backgroundColor: Colors.red,
                          child: IconButton(
                            padding: EdgeInsets.zero,
                            icon: const Icon(Icons.close, size: 16, color: Colors.white),
                            onPressed: () => _removeImage(index),
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),
            const SizedBox(height: 24),

            // Training Steps
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Training Steps:',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('$_steps steps',
                        style: const TextStyle(color: Colors.blueGrey)),
                  ],
                ),
                const SizedBox(height: 8),
                Slider(
                  value: _steps.toDouble(),
                  min: 500,
                  max: 2000,
                  divisions: 3,
                  activeColor: Colors.blueGrey,
                  label: '$_steps',
                  onChanged: (value) => setState(() => _steps = value.toInt()),
                ),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('500\n(Fast)', style: TextStyle(fontSize: 10), textAlign: TextAlign.center),
                    Text('1000\n(Balanced)', style: TextStyle(fontSize: 10), textAlign: TextAlign.center),
                    Text('1500\n(Quality)', style: TextStyle(fontSize: 10), textAlign: TextAlign.center),
                    Text('2000\n(Best)', style: TextStyle(fontSize: 10), textAlign: TextAlign.center),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Start Training Button
            ElevatedButton.icon(
              onPressed: _isTraining ? null : _startTraining,
              icon: _isTraining
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.play_arrow),
              label: Text(_isTraining ? 'Starting Training...' : 'Start Training (~10 min)'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueGrey,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
            ),

            // Training ID Result
            if (_trainingId != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.green),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.check_circle, color: Colors.green, size: 28),
                        SizedBox(width: 8),
                        Text('Training Started!',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text('Training ID: $_trainingId',
                        style: const TextStyle(fontFamily: 'monospace')),
                    const SizedBox(height: 8),
                    const Text(
                      'Your character is training now! Check the Training Status screen to monitor progress.',
                      style: TextStyle(fontSize: 12),
                    ),
                  ],
                ),
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
    _characterNameController.dispose();
    _triggerWordController.dispose();
    super.dispose();
  }
}

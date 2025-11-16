/// AI Studio Hub Screen - Access all 34 AI features
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';

// Image Generation
import '../image_generation/text_to_image_screen.dart';
import '../image_generation/image_to_image_screen.dart';
import '../image_generation/upscale_screen.dart';
import '../image_generation/sketch_to_image_screen.dart';
import '../image_generation/control_screen.dart';
import '../image_generation/image_to_3d_screen.dart';
import '../image_generation/inpaint_screen.dart';
import '../image_generation/remove_background_screen.dart';
import '../image_generation/search_replace_screen.dart';
import '../image_generation/outpaint_screen.dart';
import '../image_generation/favorites_screen.dart';
import '../image_generation/presets_screen.dart';

// Video
import '../video/video_extend_screen.dart';
import '../video/video_chain_screen.dart';
import '../video/voice_edit_screen.dart';

// Audio
import '../audio/text_to_speech_screen.dart';

// Character Training
import '../character/train_character_screen.dart';
import '../character/character_image_screen.dart';
import '../character/training_status_screen.dart';

// Advanced Features
import '../batch/batch_processor_screen.dart';
import '../workflows/quick_workflows_screen.dart';

class AIStudioHubScreen extends StatelessWidget {
  const AIStudioHubScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Studio'),
        backgroundColor: Colors.deepPurple,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Welcome Card
          Card(
            color: Colors.deepPurple.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.auto_awesome, size: 32, color: Colors.deepPurple),
                      const SizedBox(width: 12),
                      const Text(
                        'AI Studio',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Access all 34 AI features: image generation, video creation, character training, and more.',
                    style: TextStyle(fontSize: 14, color: Colors.black87),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // IMAGE GENERATION SECTION
          _buildSectionHeader('Image Generation', Icons.image, Colors.blue),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Text to Image', Icons.text_fields, Colors.blue, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const TextToImageScreen()));
            }),
            _FeatureTile('Image to Image', Icons.transform, Colors.blue, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const ImageToImageScreen()));
            }),
            _FeatureTile('Upscale 4x', Icons.zoom_in, Colors.blue, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const UpscaleScreen()));
            }),
            _FeatureTile('Sketch to Image', Icons.draw, Colors.purple, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const SketchToImageScreen()));
            }),
            _FeatureTile('Control Modes', Icons.control_camera, Colors.teal, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const ControlScreen()));
            }),
            _FeatureTile('Image to 3D', Icons.view_in_ar, Colors.deepPurple, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const ImageTo3DScreen()));
            }),
            _FeatureTile('Inpaint', Icons.auto_fix_high, Colors.indigo, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const InpaintScreen()));
            }),
            _FeatureTile('Remove BG', Icons.layers_clear, Colors.green, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const RemoveBackgroundScreen()));
            }),
            _FeatureTile('Search & Replace', Icons.find_replace, Colors.cyan, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const SearchReplaceScreen()));
            }),
            _FeatureTile('Outpaint', Icons.expand, Colors.lime, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const OutpaintScreen()));
            }),
            _FeatureTile('Style Presets', Icons.palette, Colors.deepPurple, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const PresetsScreen()));
            }),
            _FeatureTile('Favorites', Icons.favorite, Colors.pink, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const FavoritesScreen()));
            }),
          ]),

          const SizedBox(height: 24),

          // VIDEO SECTION
          _buildSectionHeader('Video Creation', Icons.videocam, Colors.red),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Extend Video', Icons.add_to_queue, Colors.amber, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const VideoExtendScreen()));
            }),
            _FeatureTile('Chain Videos', Icons.video_library, Colors.deepOrange, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const VideoChainScreen()));
            }),
            _FeatureTile('Voice Edit', Icons.record_voice_over, Colors.redAccent, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const VoiceEditScreen()));
            }),
          ]),

          const SizedBox(height: 24),

          // AUDIO SECTION
          _buildSectionHeader('Audio Generation', Icons.mic, Colors.orange),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Text to Speech', Icons.record_voice_over, Colors.orange, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const TextToSpeechScreen()));
            }),
          ]),

          const SizedBox(height: 24),

          // ADVANCED FEATURES SECTION
          _buildSectionHeader('Advanced Features', Icons.auto_fix_high, Colors.deepOrange),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Batch Processor', Icons.batch_prediction, Colors.indigo, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const BatchProcessorScreen()));
            }),
            _FeatureTile('Quick Workflows', Icons.flash_on, Colors.deepOrange, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const QuickWorkflowsScreen()));
            }),
          ]),

          const SizedBox(height: 24),

          // CHARACTER TRAINING SECTION
          _buildSectionHeader('Character Training', Icons.person, Colors.blueGrey),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Train Character', Icons.school, Colors.blueGrey, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const TrainCharacterScreen()));
            }),
            _FeatureTile('Generate with Character', Icons.auto_awesome, Colors.lightBlue, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const CharacterImageScreen()));
            }),
            _FeatureTile('Training Status', Icons.timeline, Colors.brown, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const TrainingStatusScreen()));
            }),
          ]),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, Color color) {
    return Row(
      children: [
        Icon(icon, color: color, size: 28),
        const SizedBox(width: 12),
        Text(
          title,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildFeatureGrid(BuildContext context, List<_FeatureTile> tiles) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.2,
      children: tiles
          .map((tile) => Card(
                elevation: 2,
                child: InkWell(
                  onTap: tile.onTap,
                  borderRadius: BorderRadius.circular(12),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(tile.icon, size: 40, color: tile.color),
                        const SizedBox(height: 12),
                        Text(
                          tile.label,
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ),
              ))
          .toList(),
    );
  }
}

class _FeatureTile {
  final String label;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  _FeatureTile(this.label, this.icon, this.color, this.onTap);
}

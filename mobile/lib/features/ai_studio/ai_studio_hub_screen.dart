/// AI Studio Hub Screen - Access all 34 AI features
/// Session 115 Part 7 - Visual Redesign
library;

import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

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
            _FeatureTile('Text to Image', 'Generate images from text prompts', Icons.text_fields, Colors.blue, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const TextToImageScreen()));
            }),
            _FeatureTile('Image to Image', 'Transform images with AI style transfer', Icons.transform, Colors.blue, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const ImageToImageScreen()));
            }),
            _FeatureTile('Upscale 4x', 'Enhance image resolution up to 4x', Icons.zoom_in, Colors.blue, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const UpscaleScreen()));
            }),
            _FeatureTile('Sketch to Image', 'Convert sketches into realistic images', Icons.draw, Colors.purple, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const SketchToImageScreen()));
            }),
            _FeatureTile('Control Modes', 'Guide generation with edge/depth maps', Icons.control_camera, Colors.teal, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const ControlScreen()));
            }),
            _FeatureTile('Image to 3D', 'Create 3D models from images', Icons.view_in_ar, Colors.deepPurple, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const ImageTo3DScreen()));
            }),
            _FeatureTile('Inpaint', 'Fill or modify specific image areas', Icons.auto_fix_high, Colors.indigo, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const InpaintScreen()));
            }),
            _FeatureTile('Remove BG', 'Remove image backgrounds instantly', Icons.layers_clear, Colors.green, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const RemoveBackgroundScreen()));
            }),
            _FeatureTile('Search & Replace', 'Find and replace objects in images', Icons.find_replace, Colors.cyan, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const SearchReplaceScreen()));
            }),
            _FeatureTile('Outpaint', 'Extend images beyond their borders', Icons.expand, Colors.lime, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const OutpaintScreen()));
            }),
            _FeatureTile('Style Presets', 'Pre-configured artistic styles', Icons.palette, Colors.deepPurple, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const PresetsScreen()));
            }),
            _FeatureTile('Favorites', 'Your saved favorite images', Icons.favorite, Colors.pink, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const FavoritesScreen()));
            }),
          ]),

          const SizedBox(height: 24),

          // VIDEO SECTION
          _buildSectionHeader('Video Creation', Icons.videocam, Colors.red),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Extend Video', 'Extend video length with AI', Icons.add_to_queue, Colors.amber, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const VideoExtendScreen()));
            }),
            _FeatureTile('Chain Videos', 'Combine multiple videos seamlessly', Icons.video_library, Colors.deepOrange, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const VideoChainScreen()));
            }),
            _FeatureTile('Voice Edit', 'Edit videos with voice commands', Icons.record_voice_over, Colors.redAccent, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const VoiceEditScreen()));
            }),
          ]),

          const SizedBox(height: 24),

          // AUDIO SECTION
          _buildSectionHeader('Audio Generation', Icons.mic, Colors.orange),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Text to Speech', 'Convert text to natural speech', Icons.record_voice_over, Colors.orange, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const TextToSpeechScreen()));
            }),
          ]),

          const SizedBox(height: 24),

          // ADVANCED FEATURES SECTION
          _buildSectionHeader('Advanced Features', Icons.auto_fix_high, Colors.deepOrange),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Batch Processor', 'Process multiple images at once', Icons.batch_prediction, Colors.indigo, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const BatchProcessorScreen()));
            }),
            _FeatureTile('Quick Workflows', 'One-tap automated pipelines', Icons.flash_on, Colors.deepOrange, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const QuickWorkflowsScreen()));
            }),
          ]),

          const SizedBox(height: 24),

          // CHARACTER TRAINING SECTION
          _buildSectionHeader('Character Training', Icons.person, Colors.blueGrey),
          const SizedBox(height: 12),
          _buildFeatureGrid(context, [
            _FeatureTile('Train Character', 'Create custom character models', Icons.school, Colors.blueGrey, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const TrainCharacterScreen()));
            }),
            _FeatureTile('Generate with Character', 'Generate images with your character', Icons.auto_awesome, Colors.lightBlue, () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const CharacterImageScreen()));
            }),
            _FeatureTile('Training Status', 'View model training progress', Icons.timeline, Colors.brown, () {
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
      childAspectRatio: 1.3, // Wider cards (was 0.85)
      children: tiles.map((tile) => _EnhancedFeatureCard(tile: tile)).toList(),
    );
  }
}

class _FeatureTile {
  final String label;
  final String description;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  _FeatureTile(this.label, this.description, this.icon, this.color, this.onTap);
}

class _EnhancedFeatureCard extends StatefulWidget {
  final _FeatureTile tile;

  const _EnhancedFeatureCard({required this.tile});

  @override
  State<_EnhancedFeatureCard> createState() => _EnhancedFeatureCardState();
}

class _EnhancedFeatureCardState extends State<_EnhancedFeatureCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      cursor: SystemMouseCursors.click,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        transform: _isHovered ? (Matrix4.identity()..scale(1.05)) : Matrix4.identity(),
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                widget.tile.color.withOpacity(0.1),
                widget.tile.color.withOpacity(0.05),
              ],
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: _isHovered ? widget.tile.color : widget.tile.color.withOpacity(0.3),
              width: 2,
            ),
            boxShadow: _isHovered
                ? [
                    BoxShadow(
                      color: widget.tile.color.withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
                    ),
                  ]
                : [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: widget.tile.onTap,
              borderRadius: BorderRadius.circular(16),
              child: Padding(
                padding: const EdgeInsets.all(10),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: widget.tile.color.withOpacity(0.15),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        widget.tile.icon,
                        size: 24,
                        color: widget.tile.color,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      widget.tile.label,
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade900,
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.tile.description,
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey.shade600,
                        height: 1.2,
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

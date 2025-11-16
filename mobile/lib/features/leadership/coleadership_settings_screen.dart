/// Co-Leadership Settings Screen
///
/// Session 108 - Co-Leadership Mobile UI
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../models/coleadership.dart';
import '../../providers/coleadership_provider.dart';

class CoLeadershipSettingsScreen extends ConsumerStatefulWidget {
  const CoLeadershipSettingsScreen({super.key});

  @override
  ConsumerState<CoLeadershipSettingsScreen> createState() =>
      _CoLeadershipSettingsScreenState();
}

class _CoLeadershipSettingsScreenState
    extends ConsumerState<CoLeadershipSettingsScreen> {
  bool _allowToldYouSo = false;
  String _tone = 'serious';
  bool _isLoading = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  Widget build(BuildContext context) {
    final preferencesAsync = ref.watch(coLeadershipPreferencesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Co-Leadership Settings'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: preferencesAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(),
        ),
        error: (error, stack) => Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.error_outline,
                  color: AppTheme.errorColor,
                  size: 48,
                ),
                const SizedBox(height: 16),
                Text(
                  'Failed to load settings',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  error.toString(),
                  style: Theme.of(context).textTheme.bodyMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: () {
                    ref.invalidate(coLeadershipPreferencesProvider);
                  },
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
        data: (preferences) {
          // Initialize state from preferences on first load
          if (!_isLoading &&
              (_allowToldYouSo != preferences.allowToldYouSo ||
                  _tone != preferences.tone)) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              setState(() {
                _allowToldYouSo = preferences.allowToldYouSo;
                _tone = preferences.tone;
              });
            });
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Card
                Card(
                  color: AppTheme.primaryColor.withOpacity(0.1),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        Icon(
                          Icons.psychology,
                          color: AppTheme.primaryColor,
                          size: 32,
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'AI-Human Partnership',
                                style: Theme.of(context)
                                    .textTheme
                                    .titleMedium
                                    ?.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: AppTheme.primaryColor,
                                    ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Customize how your AI co-leader interacts with you',
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Error/Success Messages
                if (_errorMessage != null) ...[
                  Card(
                    color: AppTheme.errorColor.withOpacity(0.1),
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline,
                              color: AppTheme.errorColor),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _errorMessage!,
                              style: const TextStyle(color: AppTheme.errorColor),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, size: 20),
                            onPressed: () {
                              setState(() {
                                _errorMessage = null;
                              });
                            },
                            color: AppTheme.errorColor,
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                if (_successMessage != null) ...[
                  Card(
                    color: AppTheme.successColor.withOpacity(0.1),
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle,
                              color: AppTheme.successColor),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _successMessage!,
                              style:
                                  const TextStyle(color: AppTheme.successColor),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, size: 20),
                            onPressed: () {
                              setState(() {
                                _successMessage = null;
                              });
                            },
                            color: AppTheme.successColor,
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Reflection Feedback Setting
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.lightbulb_outline,
                                color: Colors.purple),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Reflection Feedback',
                                style: Theme.of(context)
                                    .textTheme
                                    .titleMedium
                                    ?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        const Divider(),
                        SwitchListTile(
                          value: _allowToldYouSo,
                          onChanged: (value) {
                            setState(() {
                              _allowToldYouSo = value;
                            });
                          },
                          title: const Text('Allow "I Told You So" reflections'),
                          subtitle: const Text(
                            'When outcomes prove the AI was correct, receive respectful reflection messages to help you learn',
                          ),
                          activeColor: Colors.purple,
                          contentPadding: EdgeInsets.zero,
                        ),
                        if (_allowToldYouSo) ...[
                          const SizedBox(height: 8),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.purple.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              children: [
                                const Icon(
                                  Icons.info_outline,
                                  size: 20,
                                  color: Colors.purple,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    'Reflections are designed to be constructive, not judgmental. They help build mutual learning.',
                                    style:
                                        Theme.of(context).textTheme.bodySmall,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Tone Setting
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.chat_bubble_outline,
                                color: AppTheme.accentColor),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Communication Tone',
                                style: Theme.of(context)
                                    .textTheme
                                    .titleMedium
                                    ?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        const Divider(),
                        const SizedBox(height: 8),
                        Text(
                          'Choose how your AI co-leader communicates:',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                        const SizedBox(height: 16),
                        ...preferences.toneChoices.map((toneChoice) {
                          return RadioListTile<String>(
                            value: toneChoice.value,
                            groupValue: _tone,
                            onChanged: (value) {
                              if (value != null) {
                                setState(() {
                                  _tone = value;
                                });
                              }
                            },
                            title: Text(toneChoice.label),
                            subtitle: Text(
                              _getToneDescription(toneChoice.value),
                            ),
                            activeColor: AppTheme.accentColor,
                            contentPadding: EdgeInsets.zero,
                          );
                        }).toList(),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Save Button
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: _isLoading ? null : _savePreferences,
                    icon: _isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : const Icon(Icons.save),
                    label: Text(_isLoading ? 'Saving...' : 'Save Preferences'),
                    style: FilledButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  String _getToneDescription(String tone) {
    switch (tone) {
      case 'serious':
        return 'Professional and formal communication style';
      case 'playful':
        return 'Friendly and conversational style with personality';
      default:
        return '';
    }
  }

  Future<void> _savePreferences() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final updatePrefs = ref.read(updatePreferencesProvider);
      await updatePrefs(
        allowToldYouSo: _allowToldYouSo,
        tone: _tone,
      );

      if (!mounted) return;

      setState(() {
        _isLoading = false;
        _successMessage = 'Preferences saved successfully!';
      });

      // Clear success message after 3 seconds
      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() {
            _successMessage = null;
          });
        }
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isLoading = false;
        _errorMessage = 'Failed to save preferences: ${e.toString()}';
      });
    }
  }
}

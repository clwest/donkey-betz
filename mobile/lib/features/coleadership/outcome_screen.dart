/// Outcome Screen - Log decision outcome
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../providers/coleadership_provider.dart';

class OutcomeScreen extends ConsumerStatefulWidget {
  final String decisionId;
  final String topic;

  const OutcomeScreen({
    super.key,
    required this.decisionId,
    required this.topic,
  });

  @override
  ConsumerState<OutcomeScreen> createState() => _OutcomeScreenState();
}

class _OutcomeScreenState extends ConsumerState<OutcomeScreen> {
  final _formKey = GlobalKey<FormState>();
  final _summaryController = TextEditingController();
  String _status = 'pending';
  String _attribution = 'unknown';

  @override
  void dispose() {
    _summaryController.dispose();
    super.dispose();
  }

  Future<void> _submitOutcome() async {
    if (!_formKey.currentState!.validate()) return;

    await ref.read(outcomeLogControllerProvider.notifier).logOutcome(
          decisionId: widget.decisionId,
          status: _status,
          outcomeSummary: _summaryController.text.trim(),
          attribution: _attribution,
        );

    final state = ref.read(outcomeLogControllerProvider);

    if (state.error != null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(state.error!),
          backgroundColor: AppTheme.errorColor,
        ),
      );
    } else if (state.isSuccess) {
      if (!mounted) return;

      // Show "I told you so" message if present
      if (state.toldYouSoMessage != null &&
          state.toldYouSoMessage!.isNotEmpty) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.smart_toy, color: AppTheme.primaryColor),
                SizedBox(width: 8),
                Text('AI Reflection'),
              ],
            ),
            content: Text(state.toldYouSoMessage!),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }

      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Outcome logged successfully!'),
          backgroundColor: AppTheme.successColor,
        ),
      );

      // Navigate back to home
      Navigator.popUntil(context, (route) => route.isFirst);
    }
  }

  @override
  Widget build(BuildContext context) {
    final outcomeState = ref.watch(outcomeLogControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Log Outcome'),
        backgroundColor: AppTheme.primaryColor,
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Topic Card
            Card(
              color: AppTheme.backgroundColor,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Decision Topic',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppTheme.textSecondary,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.topic,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Status Dropdown
            DropdownButtonFormField<String>(
              value: _status,
              decoration: const InputDecoration(
                labelText: 'Outcome Status *',
                prefixIcon: Icon(Icons.trending_up),
              ),
              items: const [
                DropdownMenuItem(value: 'pending', child: Text('Pending')),
                DropdownMenuItem(value: 'success', child: Text('Success')),
                DropdownMenuItem(value: 'failure', child: Text('Failure')),
                DropdownMenuItem(value: 'mixed', child: Text('Mixed Results')),
              ],
              onChanged: (value) {
                setState(() {
                  _status = value ?? 'pending';
                });
              },
            ),
            const SizedBox(height: 16),

            // Outcome Summary
            TextFormField(
              controller: _summaryController,
              decoration: const InputDecoration(
                labelText: 'What actually happened? *',
                hintText: 'Describe the outcome...',
                prefixIcon: Icon(Icons.description),
              ),
              maxLines: 4,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please describe the outcome';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            // Attribution Dropdown
            DropdownButtonFormField<String>(
              value: _attribution,
              decoration: const InputDecoration(
                labelText: 'Who was more correct? *',
                prefixIcon: Icon(Icons.psychology),
              ),
              items: const [
                DropdownMenuItem(
                  value: 'ai',
                  child: Row(
                    children: [
                      Icon(Icons.smart_toy, size: 20, color: AppTheme.primaryColor),
                      SizedBox(width: 8),
                      Text('AI more correct'),
                    ],
                  ),
                ),
                DropdownMenuItem(
                  value: 'human',
                  child: Row(
                    children: [
                      Icon(Icons.person, size: 20, color: AppTheme.accentColor),
                      SizedBox(width: 8),
                      Text('Human more correct'),
                    ],
                  ),
                ),
                DropdownMenuItem(
                  value: 'both',
                  child: Row(
                    children: [
                      Icon(Icons.handshake, size: 20, color: AppTheme.successColor),
                      SizedBox(width: 8),
                      Text('Both partly correct'),
                    ],
                  ),
                ),
                DropdownMenuItem(
                  value: 'unknown',
                  child: Row(
                    children: [
                      Icon(Icons.help, size: 20, color: AppTheme.textSecondary),
                      SizedBox(width: 8),
                      Text('Unknown/unclear'),
                    ],
                  ),
                ),
              ],
              onChanged: (value) {
                setState(() {
                  _attribution = value ?? 'unknown';
                });
              },
            ),
            const SizedBox(height: 24),

            // Submit Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: outcomeState.isLoading ? null : _submitOutcome,
                icon: outcomeState.isLoading
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
                label: Text(
                  outcomeState.isLoading
                      ? 'Logging Outcome...'
                      : 'Log Outcome',
                ),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Later Button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: outcomeState.isLoading
                    ? null
                    : () => Navigator.popUntil(context, (route) => route.isFirst),
                icon: const Icon(Icons.schedule),
                label: const Text('Do It Later'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Decision Commit Screen - Human decision input
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../core/api_config.dart';
import '../../providers/coleadership_provider.dart';
import 'outcome_screen.dart';

class DecisionCommitScreen extends ConsumerStatefulWidget {
  final String decisionId;
  final String topic;

  const DecisionCommitScreen({
    super.key,
    required this.decisionId,
    required this.topic,
  });

  @override
  ConsumerState<DecisionCommitScreen> createState() =>
      _DecisionCommitScreenState();
}

class _DecisionCommitScreenState extends ConsumerState<DecisionCommitScreen> {
  final _formKey = GlobalKey<FormState>();
  final _decisionController = TextEditingController();
  final _justificationController = TextEditingController();
  bool _isOverride = false;
  String? _overriddenAgent;

  @override
  void dispose() {
    _decisionController.dispose();
    _justificationController.dispose();
    super.dispose();
  }

  Future<void> _submitDecision() async {
    if (!_formKey.currentState!.validate()) return;

    await ref.read(decisionCommitControllerProvider.notifier).commitDecision(
          decisionId: widget.decisionId,
          chosenPathSummary: _decisionController.text.trim(),
          justification: _justificationController.text.trim(),
          isOverride: _isOverride,
          overriddenAgentId: _overriddenAgent,
        );

    final state = ref.read(decisionCommitControllerProvider);

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
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Decision recorded successfully!'),
          backgroundColor: AppTheme.successColor,
        ),
      );

      // Navigate to outcome screen
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => OutcomeScreen(
            decisionId: widget.decisionId,
            topic: widget.topic,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final commitState = ref.watch(decisionCommitControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Commit Your Decision'),
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
                      'Meeting Topic',
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

            // Decision Field
            TextFormField(
              controller: _decisionController,
              decoration: const InputDecoration(
                labelText: 'What did you decide? *',
                hintText: 'Describe your final decision...',
                prefixIcon: Icon(Icons.how_to_vote),
              ),
              maxLines: 4,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter your decision';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            // Justification Field
            TextFormField(
              controller: _justificationController,
              decoration: const InputDecoration(
                labelText: 'Why? (Optional)',
                hintText: 'Explain your reasoning...',
                prefixIcon: Icon(Icons.notes),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 20),

            // Override Checkbox
            CheckboxListTile(
              value: _isOverride,
              onChanged: (value) {
                setState(() {
                  _isOverride = value ?? false;
                  if (!_isOverride) {
                    _overriddenAgent = null;
                  }
                });
              },
              title: const Text('I overrode the AI\'s recommendation'),
              subtitle: const Text(
                'Check if you chose a different path than recommended',
              ),
              activeColor: AppTheme.warningColor,
            ),

            // Override Agent Selection
            if (_isOverride) ...[
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _overriddenAgent,
                decoration: const InputDecoration(
                  labelText: 'Which executive did you override?',
                  prefixIcon: Icon(Icons.person),
                ),
                items: ApiConfig.executiveAgents.map((agent) {
                  return DropdownMenuItem<String>(
                    value: agent,
                    child: Row(
                      children: [
                        Icon(
                          AppTheme.getAgentIcon(agent),
                          size: 20,
                          color: AppTheme.primaryColor,
                        ),
                        const SizedBox(width: 8),
                        Text(ApiConfig.getAgentDisplayName(agent)),
                      ],
                    ),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _overriddenAgent = value;
                  });
                },
                validator: _isOverride
                    ? (value) {
                        if (value == null) {
                          return 'Please select which agent you overrode';
                        }
                        return null;
                      }
                    : null,
              ),
            ],
            const SizedBox(height: 24),

            // Submit Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: commitState.isLoading ? null : _submitDecision,
                icon: commitState.isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Icon(Icons.check_circle),
                label: Text(
                  commitState.isLoading
                      ? 'Saving Decision...'
                      : 'Commit Decision',
                ),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Cancel Button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: commitState.isLoading
                    ? null
                    : () => Navigator.pop(context),
                icon: const Icon(Icons.cancel),
                label: const Text('Cancel'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

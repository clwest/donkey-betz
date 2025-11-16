/// Leadership Decision Detail Screen
///
/// Session 108 - Co-Leadership Mobile UI
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../core/app_theme.dart';
import '../../models/coleadership.dart';
import '../../providers/coleadership_provider.dart';

class DecisionDetailScreen extends ConsumerWidget {
  final String decisionId;

  const DecisionDetailScreen({
    super.key,
    required this.decisionId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(decisionDetailProvider(decisionId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Decision Detail'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(decisionDetailProvider(decisionId));
        },
        child: detailAsync.when(
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
                    'Failed to load decision',
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
                      ref.invalidate(decisionDetailProvider(decisionId));
                    },
                    icon: const Icon(Icons.refresh),
                    label: const Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
          data: (detail) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Decision metadata
                  _DecisionMetaSection(detail: detail),
                  const SizedBox(height: 24),

                  // Agent recommendations
                  _AgentRecommendationsSection(
                    recommendations: detail.agentRecommendations,
                  ),
                  const SizedBox(height: 24),

                  // Human decision section
                  _HumanDecisionSection(
                    detail: detail,
                    decisionId: decisionId,
                  ),
                  const SizedBox(height: 24),

                  // Outcome section
                  _OutcomeSection(
                    detail: detail,
                    decisionId: decisionId,
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

/// Decision metadata card
class _DecisionMetaSection extends StatelessWidget {
  final CoLeadershipDecisionDetail detail;

  const _DecisionMetaSection({required this.detail});

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('MMM d, yyyy \'at\' h:mm a');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.info_outline, color: AppTheme.primaryColor),
                const SizedBox(width: 8),
                Text(
                  'Decision Info',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              detail.title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            if (detail.description.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                detail.description,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
            const SizedBox(height: 16),
            _buildInfoRow(
              context,
              icon: Icons.calendar_today,
              label: 'Created',
              value: dateFormat.format(detail.createdAt),
            ),
            if (detail.frozenAt != null) ...[
              const SizedBox(height: 8),
              _buildInfoRow(
                context,
                icon: Icons.lock,
                label: 'Committed',
                value: dateFormat.format(detail.frozenAt!),
              ),
            ],
            if (detail.project != null) ...[
              const SizedBox(height: 8),
              _buildInfoRow(
                context,
                icon: Icons.folder,
                label: 'Project',
                value: detail.project!.name,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 16, color: AppTheme.textSecondary),
        const SizedBox(width: 8),
        Text(
          '$label: ',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.textSecondary,
                fontWeight: FontWeight.w600,
              ),
        ),
        Expanded(
          child: Text(
            value,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
      ],
    );
  }
}

/// Agent recommendations section
class _AgentRecommendationsSection extends StatelessWidget {
  final List<AgentRecommendation> recommendations;

  const _AgentRecommendationsSection({required this.recommendations});

  @override
  Widget build(BuildContext context) {
    if (recommendations.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.groups, color: AppTheme.accentColor),
            const SizedBox(width: 8),
            Text(
              'Agent Recommendations',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.accentColor,
                  ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ...recommendations.map((rec) => _AgentRecommendationCard(rec: rec)),
      ],
    );
  }
}

class _AgentRecommendationCard extends StatelessWidget {
  final AgentRecommendation rec;

  const _AgentRecommendationCard({required this.rec});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Agent name and stance
            Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: _getStanceColor().withOpacity(0.2),
                  child: Icon(
                    Icons.smart_toy,
                    color: _getStanceColor(),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        rec.agentName,
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 4),
                      _buildStanceChip(),
                    ],
                  ),
                ),
                if (rec.confidence != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppTheme.infoColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${(rec.confidence! * 100).toInt()}%',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.infoColor,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),

            // Summary
            Text(
              rec.summary,
              style: Theme.of(context).textTheme.bodyMedium,
            ),

            // Risk analysis (if present)
            if (rec.riskAnalysis.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: Colors.orange.withOpacity(0.3),
                  ),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.warning_amber, color: Colors.orange, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        rec.riskAnalysis,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getStanceColor() {
    switch (rec.stance) {
      case 'support':
        return Colors.green;
      case 'concern':
        return Colors.orange;
      case 'objection':
        return Colors.red;
      case 'alternative':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  Widget _buildStanceChip() {
    final color = _getStanceColor();
    return Chip(
      label: Text(
        rec.stanceDisplay.toUpperCase(),
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.bold,
          color: color,
        ),
      ),
      backgroundColor: color.withOpacity(0.1),
      side: BorderSide(color: color.withOpacity(0.3)),
      padding: EdgeInsets.zero,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      visualDensity: VisualDensity.compact,
    );
  }
}

/// Human decision section (form or display)
class _HumanDecisionSection extends ConsumerStatefulWidget {
  final CoLeadershipDecisionDetail detail;
  final String decisionId;

  const _HumanDecisionSection({
    required this.detail,
    required this.decisionId,
  });

  @override
  ConsumerState<_HumanDecisionSection> createState() => _HumanDecisionSectionState();
}

class _HumanDecisionSectionState extends ConsumerState<_HumanDecisionSection> {
  final _formKey = GlobalKey<FormState>();
  final _summaryController = TextEditingController();
  final _justificationController = TextEditingController();
  bool _isOverride = false;
  String? _overriddenAgentId;

  @override
  void dispose() {
    _summaryController.dispose();
    _justificationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final commitState = ref.watch(decisionCommitControllerProvider);

    // If human decision already exists, show it
    if (widget.detail.humanDecision != null) {
      return _buildHumanDecisionDisplay(widget.detail.humanDecision!);
    }

    // Otherwise, show the commit form
    return Card(
      color: Colors.amber.withOpacity(0.05),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.person, color: Colors.amber),
                  const SizedBox(width: 8),
                  Text(
                    'Commit Your Decision',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.amber.shade800,
                        ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Summary field
              TextFormField(
                controller: _summaryController,
                decoration: const InputDecoration(
                  labelText: 'What did you decide? *',
                  hintText: 'Describe your decision in a few sentences',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Please describe your decision';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Justification field
              TextFormField(
                controller: _justificationController,
                decoration: const InputDecoration(
                  labelText: 'Why? (optional)',
                  hintText: 'Optional explanation of your reasoning',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),

              // Override checkbox
              CheckboxListTile(
                value: _isOverride,
                onChanged: (value) {
                  setState(() {
                    _isOverride = value ?? false;
                    if (!_isOverride) {
                      _overriddenAgentId = null;
                    }
                  });
                },
                title: const Text('I overrode an agent recommendation'),
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
              ),

              // Agent dropdown (if override)
              if (_isOverride && widget.detail.agentRecommendations.isNotEmpty) ...[
                const SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  value: _overriddenAgentId,
                  decoration: const InputDecoration(
                    labelText: 'Which agent did you override?',
                    border: OutlineInputBorder(),
                  ),
                  items: widget.detail.agentRecommendations
                      .map((rec) => DropdownMenuItem(
                            value: rec.agentId,
                            child: Text(rec.agentName),
                          ))
                      .toList(),
                  onChanged: (value) {
                    setState(() {
                      _overriddenAgentId = value;
                    });
                  },
                  validator: (value) {
                    if (_isOverride && value == null) {
                      return 'Please select which agent you overrode';
                    }
                    return null;
                  },
                ),
              ],

              const SizedBox(height: 16),

              // Submit button
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: commitState.isLoading ? null : _submitDecision,
                  icon: commitState.isLoading
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.save),
                  label: Text(commitState.isLoading ? 'Saving...' : 'Save My Decision'),
                ),
              ),

              // Error message
              if (commitState.error != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.errorColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: AppTheme.errorColor),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          commitState.error!,
                          style: const TextStyle(color: AppTheme.errorColor),
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              // Success message
              if (commitState.isSuccess) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle, color: Colors.green),
                      const SizedBox(width: 8),
                      const Expanded(
                        child: Text(
                          'Decision committed successfully!',
                          style: TextStyle(color: Colors.green),
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
    );
  }

  Widget _buildHumanDecisionDisplay(HumanDecision decision) {
    return Card(
      color: Colors.green.withOpacity(0.05),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.green),
                const SizedBox(width: 8),
                Text(
                  'Your Decision',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.green.shade800,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              decision.chosenPathSummary,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            if (decision.justification.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Justification: ${decision.justification}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            ],
            if (decision.isOverride) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.amber.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.amber),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.warning_amber, size: 16, color: Colors.amber),
                    const SizedBox(width: 8),
                    Text(
                      'Overrode: ${decision.overriddenAgent ?? "an agent"}',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Colors.amber,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Future<void> _submitDecision() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    await ref.read(decisionCommitControllerProvider.notifier).commitDecision(
          decisionId: widget.decisionId,
          chosenPathSummary: _summaryController.text.trim(),
          justification: _justificationController.text.trim(),
          isOverride: _isOverride,
          overriddenAgentId: _overriddenAgentId,
        );

    // Refresh the decision detail to show the committed decision
    if (ref.read(decisionCommitControllerProvider).isSuccess) {
      ref.invalidate(decisionDetailProvider(widget.decisionId));
      ref.invalidate(decisionsListProvider);
    }
  }
}

/// Outcome section (form or display)
class _OutcomeSection extends ConsumerStatefulWidget {
  final CoLeadershipDecisionDetail detail;
  final String decisionId;

  const _OutcomeSection({
    required this.detail,
    required this.decisionId,
  });

  @override
  ConsumerState<_OutcomeSection> createState() => _OutcomeSectionState();
}

class _OutcomeSectionState extends ConsumerState<_OutcomeSection> {
  final _formKey = GlobalKey<FormState>();
  final _summaryController = TextEditingController();
  String _status = 'success';
  String _attribution = 'both';

  @override
  void dispose() {
    _summaryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final outcomeState = ref.watch(outcomeLogControllerProvider);

    // If outcome already exists, show it
    if (widget.detail.outcome != null) {
      return _buildOutcomeDisplay(widget.detail.outcome!);
    }

    // If decision not yet committed, show pending message
    if (!widget.detail.isFrozen) {
      return Card(
        color: Colors.grey.withOpacity(0.05),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              const Icon(Icons.lock, color: Colors.grey),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Commit your decision first before logging the outcome.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppTheme.textSecondary,
                      ),
                ),
              ),
            ],
          ),
        ),
      );
    }

    // Otherwise, show the outcome form
    return Card(
      color: AppTheme.infoColor.withOpacity(0.05),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.analytics, color: AppTheme.infoColor),
                  const SizedBox(width: 8),
                  Text(
                    'Log Outcome',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppTheme.infoColor,
                        ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Status dropdown
              DropdownButtonFormField<String>(
                value: _status,
                decoration: const InputDecoration(
                  labelText: 'How did it turn out?',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'success', child: Text('Success')),
                  DropdownMenuItem(value: 'failure', child: Text('Failure')),
                  DropdownMenuItem(value: 'mixed', child: Text('Mixed')),
                  DropdownMenuItem(value: 'pending', child: Text('Still Pending')),
                ],
                onChanged: (value) {
                  setState(() {
                    _status = value!;
                  });
                },
              ),
              const SizedBox(height: 16),

              // Attribution dropdown
              DropdownButtonFormField<String>(
                value: _attribution,
                decoration: const InputDecoration(
                  labelText: 'Who was more correct?',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'ai', child: Text('AI was more correct')),
                  DropdownMenuItem(value: 'human', child: Text('Human was more correct')),
                  DropdownMenuItem(value: 'both', child: Text('Both partly correct')),
                  DropdownMenuItem(value: 'unknown', child: Text('Unknown/Unclear')),
                ],
                onChanged: (value) {
                  setState(() {
                    _attribution = value!;
                  });
                },
              ),
              const SizedBox(height: 16),

              // Summary field
              TextFormField(
                controller: _summaryController,
                decoration: const InputDecoration(
                  labelText: 'What actually happened? *',
                  hintText: 'Describe the outcome',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Please describe the outcome';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Submit button
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: outcomeState.isLoading ? null : _submitOutcome,
                  icon: outcomeState.isLoading
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.save),
                  label: Text(outcomeState.isLoading ? 'Saving...' : 'Save Outcome'),
                ),
              ),

              // Error message
              if (outcomeState.error != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.errorColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: AppTheme.errorColor),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          outcomeState.error!,
                          style: const TextStyle(color: AppTheme.errorColor),
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              // Success message
              if (outcomeState.isSuccess) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle, color: Colors.green),
                      const SizedBox(width: 8),
                      const Expanded(
                        child: Text(
                          'Outcome logged successfully!',
                          style: TextStyle(color: Colors.green),
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
    );
  }

  Widget _buildOutcomeDisplay(DecisionOutcome outcome) {
    Color statusColor;
    switch (outcome.status) {
      case 'success':
        statusColor = Colors.green;
        break;
      case 'failure':
        statusColor = Colors.red;
        break;
      case 'mixed':
        statusColor = Colors.orange;
        break;
      default:
        statusColor = Colors.grey;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Card(
          color: statusColor.withOpacity(0.05),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.analytics, color: statusColor),
                    const SizedBox(width: 8),
                    Text(
                      'Outcome',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: statusColor,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Status and attribution chips
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    Chip(
                      label: Text(
                        outcome.statusDisplay.toUpperCase(),
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: statusColor,
                        ),
                      ),
                      backgroundColor: statusColor.withOpacity(0.2),
                      side: BorderSide(color: statusColor),
                    ),
                    Chip(
                      label: Text(
                        outcome.attributionDisplay.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.primaryColor,
                        ),
                      ),
                      backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
                      side: const BorderSide(color: AppTheme.primaryColor),
                    ),
                  ],
                ),

                const SizedBox(height: 12),
                Text(
                  outcome.outcomeSummary,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
        ),

        // "I Told You So" message (if present)
        if (outcome.toldYouSoTriggered && outcome.toldYouSoMessage != null) ...[
          const SizedBox(height: 12),
          Card(
            color: Colors.purple.withOpacity(0.05),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.lightbulb, color: Colors.purple),
                      const SizedBox(width: 8),
                      Text(
                        'Reflection',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.purple,
                            ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    outcome.toldYouSoMessage!,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }

  Future<void> _submitOutcome() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    await ref.read(outcomeLogControllerProvider.notifier).logOutcome(
          decisionId: widget.decisionId,
          status: _status,
          outcomeSummary: _summaryController.text.trim(),
          attribution: _attribution,
        );

    // Refresh the decision detail to show the logged outcome
    if (ref.read(outcomeLogControllerProvider).isSuccess) {
      ref.invalidate(decisionDetailProvider(widget.decisionId));
      ref.invalidate(decisionsListProvider);
      ref.invalidate(leadershipStatsProvider);
    }
  }
}

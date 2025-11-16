/// Leadership Decisions List Screen
///
/// Session 108 - Co-Leadership Mobile UI
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../core/app_theme.dart';
import '../../models/coleadership.dart';
import '../../providers/coleadership_provider.dart';
import 'decision_detail_screen.dart';

class DecisionsListScreen extends ConsumerStatefulWidget {
  const DecisionsListScreen({super.key});

  @override
  ConsumerState<DecisionsListScreen> createState() =>
      _DecisionsListScreenState();
}

class _DecisionsListScreenState extends ConsumerState<DecisionsListScreen> {
  bool _showHintBanner = true;

  @override
  Widget build(BuildContext context) {
    final decisionsAsync = ref.watch(decisionsListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Leadership Decisions'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(decisionsListProvider);
        },
        child: decisionsAsync.when(
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
                    'Failed to load decisions',
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
                      ref.invalidate(decisionsListProvider);
                    },
                    icon: const Icon(Icons.refresh),
                    label: const Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
          data: (decisions) {
            if (decisions.isEmpty) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.balance,
                        size: 64,
                        color: AppTheme.primaryColor.withOpacity(0.3),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'No decisions yet',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Start a Boardroom Meeting from the Donkey Cockpit to create one.',
                        style: Theme.of(context).textTheme.bodyMedium,
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              );
            }

            return Column(
              children: [
                if (_showHintBanner) _buildHintBanner(),
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: decisions.length,
                    itemBuilder: (context, index) {
                      final decision = decisions[index];
                      return _DecisionCard(
                        decision: decision,
                        onTap: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (context) => DecisionDetailScreen(
                                decisionId: decision.id,
                              ),
                            ),
                          );
                        },
                      );
                    },
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildHintBanner() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.primaryColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.primaryColor.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.lightbulb_outline, color: AppTheme.primaryColor, size: 20),
          const SizedBox(width: 12),
          const Expanded(
            child: Text(
              'Pro Tip: Decisions from Boardroom Meetings show up here with AI + Human perspectives.',
              style: TextStyle(fontSize: 13, color: AppTheme.textPrimary),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            onPressed: () {
              setState(() {
                _showHintBanner = false;
              });
            },
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
        ],
      ),
    );
  }
}

class _DecisionCard extends StatelessWidget {
  final CoLeadershipDecision decision;
  final VoidCallback onTap;

  const _DecisionCard({
    required this.decision,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('MMM d, yyyy');

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title and date
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          decision.title,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          dateFormat.format(decision.createdAt),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AppTheme.textSecondary,
                              ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    Icons.chevron_right,
                    color: AppTheme.textSecondary,
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // Status chips
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildStatusChip(context),
                  if (decision.outcomeAttribution != null)
                    _buildAttributionChip(context),
                  if (decision.projectName != null)
                    _buildProjectChip(context),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(BuildContext context) {
    Color chipColor;
    String label;
    IconData icon;

    switch (decision.status) {
      case 'pending_decision':
        chipColor = Colors.orange;
        label = 'PENDING DECISION';
        icon = Icons.pending_actions;
        break;
      case 'pending_outcome':
        chipColor = Colors.blue;
        label = 'PENDING OUTCOME';
        icon = Icons.hourglass_empty;
        break;
      case 'complete':
        chipColor = Colors.green;
        label = 'COMPLETE';
        icon = Icons.check_circle;
        break;
      default:
        chipColor = Colors.grey;
        label = 'UNKNOWN';
        icon = Icons.help_outline;
    }

    return Chip(
      avatar: Icon(icon, size: 16, color: chipColor),
      label: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: chipColor,
        ),
      ),
      backgroundColor: chipColor.withOpacity(0.1),
      side: BorderSide(color: chipColor.withOpacity(0.3)),
      padding: const EdgeInsets.symmetric(horizontal: 4),
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }

  Widget _buildAttributionChip(BuildContext context) {
    final attribution = decision.outcomeAttribution;
    if (attribution == null) return const SizedBox.shrink();

    Color chipColor;
    String label;
    IconData icon;

    switch (attribution) {
      case 'ai':
        chipColor = AppTheme.primaryColor;
        label = 'AI CORRECT';
        icon = Icons.psychology;
        break;
      case 'human':
        chipColor = Colors.amber;
        label = 'HUMAN CORRECT';
        icon = Icons.person;
        break;
      case 'both':
        chipColor = Colors.purple;
        label = 'BOTH CORRECT';
        icon = Icons.people;
        break;
      default:
        chipColor = Colors.grey;
        label = 'UNCLEAR';
        icon = Icons.help_outline;
    }

    return Chip(
      avatar: Icon(icon, size: 16, color: chipColor),
      label: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: chipColor,
        ),
      ),
      backgroundColor: chipColor.withOpacity(0.1),
      side: BorderSide(color: chipColor.withOpacity(0.3)),
      padding: const EdgeInsets.symmetric(horizontal: 4),
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }

  Widget _buildProjectChip(BuildContext context) {
    return Chip(
      avatar: const Icon(Icons.folder, size: 16, color: AppTheme.accentColor),
      label: Text(
        decision.projectName!,
        style: const TextStyle(
          fontSize: 11,
          color: AppTheme.accentColor,
        ),
      ),
      backgroundColor: AppTheme.accentColor.withOpacity(0.1),
      side: BorderSide(color: AppTheme.accentColor.withOpacity(0.3)),
      padding: const EdgeInsets.symmetric(horizontal: 4),
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }
}

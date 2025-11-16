/// Leadership Dashboard - AI vs Human Performance Cockpit
///
/// Session 104 - Leadership Cockpit & Decision Timeline MVP
///
/// Shows:
/// - Performance overview stats (decisions, overrides, success rate)
/// - AI vs Human attribution
/// - Recent decisions timeline
/// - Navigation to projects and sessions
///
/// Author: Claude Code + Chris Partnership
/// Created: November 15, 2025 - Session 104
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../core/app_theme.dart';
import '../../models/leadership_models.dart';
import '../../providers/leadership_providers.dart';
import '../projects/project_detail_screen.dart';
import '../projects/session_assets_screen.dart';

class LeadershipDashboard extends ConsumerWidget {
  const LeadershipDashboard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statsAsync = ref.watch(leadershipStatsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Leadership Dashboard'),
        backgroundColor: AppTheme.primaryColor,
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.refresh(leadershipStatsProvider.future),
        child: statsAsync.when(
          loading: () => const Center(
            child: CircularProgressIndicator(),
          ),
          error: (error, stack) => _buildErrorState(context, error, ref),
          data: (stats) => _buildDashboard(context, stats),
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, Object error, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: AppTheme.errorColor,
            ),
            const SizedBox(height: 16),
            const Text(
              'Failed to Load Leadership Stats',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              error.toString(),
              style: const TextStyle(color: AppTheme.textSecondary),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => ref.refresh(leadershipStatsProvider),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboard(BuildContext context, LeadershipStats stats) {
    if (stats.totalDecisions == 0) {
      return _buildEmptyState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Section 1: Performance Overview
          Text(
            'Performance Overview',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          _buildKeyMetricsRow(context, stats),
          const SizedBox(height: 24),

          // Section 2: Attribution Breakdown
          _buildAttributionCard(context, stats),
          const SizedBox(height: 24),

          // Section 3: Recent Decisions
          Text(
            'Recent Decisions',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          _buildRecentDecisionsList(context, stats.recentDecisions),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.insights_outlined,
              size: 80,
              color: AppTheme.primaryColor.withOpacity(0.5),
            ),
            const SizedBox(height: 24),
            const Text(
              'No Decisions Yet',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Start making strategic decisions with your AI executive team to see performance metrics here.',
              style: TextStyle(
                fontSize: 16,
                color: AppTheme.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                _showHowToStartDecisions(context);
              },
              icon: const Icon(Icons.help_outline),
              label: const Text('How to Start'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKeyMetricsRow(BuildContext context, LeadershipStats stats) {
    return Row(
      children: [
        // Total Decisions
        Expanded(
          child: _buildMetricCard(
            context,
            title: 'Total',
            value: stats.totalDecisions.toString(),
            subtitle: 'Decisions',
            gradient: const LinearGradient(
              colors: [Color(0xFF9333ea), Color(0xFF6b21a8)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        const SizedBox(width: 12),
        // Overrides
        Expanded(
          child: _buildMetricCard(
            context,
            title: 'Overrides',
            value: stats.overrides.toString(),
            subtitle: '${stats.overrideRate.toStringAsFixed(0)}%',
            gradient: const LinearGradient(
              colors: [Color(0xFFec4899), Color(0xFFbe185d)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMetricCard(
    BuildContext context, {
    required String title,
    required String value,
    required String subtitle,
    required Gradient gradient,
  }) {
    return Container(
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 32,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAttributionCard(BuildContext context, LeadershipStats stats) {
    return Card(
      color: const Color(0xFF1a1a1a),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade800),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.analytics_outlined,
                  color: AppTheme.primaryColor,
                  size: 20,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Decision Attribution',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildAttributionItem(
                    'AI Correct',
                    stats.aiCorrect,
                    const Color(0xFF9333ea),
                  ),
                ),
                Expanded(
                  child: _buildAttributionItem(
                    'Human Correct',
                    stats.humanCorrect,
                    const Color(0xFF10b981),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildAttributionItem(
                    'Both Correct',
                    stats.bothCorrect,
                    const Color(0xFF3b82f6),
                  ),
                ),
                Expanded(
                  child: _buildAttributionItem(
                    'Pending',
                    stats.pending,
                    const Color(0xFF6b7280),
                  ),
                ),
              ],
            ),
            const Divider(height: 24, color: Colors.grey),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Success Rate',
                  style: TextStyle(color: Colors.white70),
                ),
                Text(
                  '${stats.successRate.toStringAsFixed(1)}%',
                  style: const TextStyle(
                    color: Color(0xFF10b981),
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Avg AI Confidence',
                  style: TextStyle(color: Colors.white70),
                ),
                Text(
                  stats.avgAiConfidence.toStringAsFixed(2),
                  style: const TextStyle(
                    color: Color(0xFF3b82f6),
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAttributionItem(String label, int count, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Padding(
          padding: const EdgeInsets.only(left: 16),
          child: Text(
            count.toString(),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRecentDecisionsList(
    BuildContext context,
    List<DecisionSummary> decisions,
  ) {
    if (decisions.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Center(
            child: Text('No recent decisions'),
          ),
        ),
      );
    }

    return Column(
      children: decisions.map((decision) {
        return _buildDecisionCard(context, decision);
      }).toList(),
    );
  }

  Widget _buildDecisionCard(BuildContext context, DecisionSummary decision) {
    final dateFormat = DateFormat('MMM d, y');
    final timeFormat = DateFormat('h:mm a');

    // Determine status color
    Color statusColor;
    if (decision.status.toLowerCase().contains('success')) {
      statusColor = const Color(0xFF10b981);
    } else if (decision.status.toLowerCase().contains('failure')) {
      statusColor = const Color(0xFFef4444);
    } else if (decision.status.toLowerCase().contains('mixed')) {
      statusColor = const Color(0xFFf59e0b);
    } else {
      statusColor = const Color(0xFF6b7280);
    }

    // Determine attribution color
    Color attributionColor;
    if (decision.attribution.toLowerCase().contains('ai')) {
      attributionColor = const Color(0xFF9333ea);
    } else if (decision.attribution.toLowerCase().contains('human')) {
      attributionColor = const Color(0xFF10b981);
    } else if (decision.attribution.toLowerCase().contains('both')) {
      attributionColor = const Color(0xFF3b82f6);
    } else {
      attributionColor = const Color(0xFF6b7280);
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _onDecisionTapped(context, decision),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title row
              Row(
                children: [
                  Expanded(
                    child: Text(
                      decision.title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (decision.isOverride)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFec4899).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(
                          color: const Color(0xFFec4899),
                        ),
                      ),
                      child: const Text(
                        'OVERRIDE',
                        style: TextStyle(
                          color: Color(0xFFec4899),
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 8),

              // Date/time
              Row(
                children: [
                  Icon(
                    Icons.access_time,
                    size: 14,
                    color: AppTheme.textSecondary,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${dateFormat.format(decision.createdAt)} at ${timeFormat.format(decision.createdAt)}',
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Status and attribution chips
              Row(
                children: [
                  _buildChip(
                    label: decision.status,
                    color: statusColor,
                  ),
                  const SizedBox(width: 8),
                  _buildChip(
                    label: decision.attribution,
                    color: attributionColor,
                  ),
                  const Spacer(),
                  if (decision.projectName != null)
                    Icon(
                      Icons.folder_outlined,
                      size: 16,
                      color: AppTheme.textSecondary,
                    ),
                ],
              ),

              // Project name if available
              if (decision.projectName != null) ...[
                const SizedBox(height: 8),
                Text(
                  'Project: ${decision.projectName}',
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppTheme.textSecondary,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildChip({required String label, required Color color}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  void _onDecisionTapped(BuildContext context, DecisionSummary decision) {
    // Navigation logic
    if (decision.projectId != null) {
      // Navigate to project detail
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ProjectDetailScreen(
            projectId: decision.projectId!,
          ),
        ),
      );
    } else if (decision.sessionId != null) {
      // Navigate to session assets
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => SessionAssetsScreen(
            sessionId: decision.sessionId!,
            sessionTitle: decision.title, // Use decision title as fallback
          ),
        ),
      );
    } else {
      // Show detail dialog if no navigation target
      _showDecisionDetail(context, decision);
    }
  }

  void _showDecisionDetail(BuildContext context, DecisionSummary decision) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Decision Details'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              decision.title,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildDetailRow('Status', decision.status),
            _buildDetailRow('Attribution', decision.attribution),
            _buildDetailRow('Override', decision.isOverride ? 'Yes' : 'No'),
            _buildDetailRow(
              'Frozen',
              decision.frozen ? 'Yes' : 'No',
            ),
            _buildDetailRow(
              'Has Outcome',
              decision.hasOutcome ? 'Yes' : 'No',
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 14,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.w500,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  void _showHowToStartDecisions(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.info_outline, color: AppTheme.primaryColor),
            SizedBox(width: 8),
            Text('How to Start'),
          ],
        ),
        content: const Text(
          'To create decisions and track your AI vs Human performance:\n\n'
          '1. Navigate to the Boardroom feature\n'
          '2. Start an executive meeting about a strategic topic\n'
          '3. Review AI recommendations from your executive team\n'
          '4. Make your decision (agree or override)\n'
          '5. Later, log the outcome to see who was more correct\n\n'
          'Your performance stats will appear here after your first decision!',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }
}

/// Leadership Data Providers - Session 104
///
/// Provides reactive access to leadership statistics and decision timeline.
///
/// Author: Claude Code + Chris Partnership
/// Created: November 15, 2025 - Session 104
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/leadership_models.dart';
import 'api_provider.dart';

/// Leadership statistics provider
///
/// Fetches and caches leadership stats including:
/// - Total decisions, overrides, success rate
/// - AI vs Human performance metrics
/// - Recent decisions (last 10)
///
/// Automatically refetches when dependencies change.
/// Use `ref.refresh(leadershipStatsProvider)` to manually refresh.
final leadershipStatsProvider = FutureProvider<LeadershipStats>((ref) async {
  final api = ref.watch(leadershipApiProvider);
  return await api.getLeadershipStats();
});

/// Recent decisions provider (convenience)
///
/// Extracts just the recent decisions list from the stats.
/// Useful for displaying decision timeline without full stats.
final recentDecisionsProvider = FutureProvider<List<DecisionSummary>>((ref) async {
  final stats = await ref.watch(leadershipStatsProvider.future);
  return stats.recentDecisions;
});

/// Project decisions provider (family)
///
/// Fetches all decisions for a specific project.
/// Includes full decision details, recommendations, outcomes.
///
/// Usage: `ref.watch(projectDecisionsProvider(projectId))`
final projectDecisionsProvider = FutureProvider.family<List<Map<String, dynamic>>, String>(
  (ref, projectId) async {
    final api = ref.watch(leadershipApiProvider);
    return await api.getProjectDecisions(projectId);
  },
);

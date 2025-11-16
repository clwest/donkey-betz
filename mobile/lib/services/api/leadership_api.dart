/// Leadership API Service - Session 104
///
/// Provides access to co-leadership statistics and decision timeline.
///
/// Author: Claude Code + Chris Partnership
/// Created: November 15, 2025 - Session 104
library;

import '../../core/api_client.dart';
import '../../core/api_config.dart';
import '../../models/leadership_models.dart';

class LeadershipApi {
  final ApiClient _client;

  LeadershipApi(this._client);

  /// Get leadership statistics for the current user
  ///
  /// Returns stats including:
  /// - Total decisions made
  /// - Override rate (AI vs Human)
  /// - Success rate
  /// - Recent decisions (last 10)
  ///
  /// Endpoint: GET /api/v1/coleadership/stats/
  Future<LeadershipStats> getLeadershipStats() async {
    final response = await _client.get('${ApiConfig.coleadershipEndpoint}stats/');

    if (response['success'] == true && response['stats'] != null) {
      return LeadershipStats.fromJson(response['stats'] as Map<String, dynamic>);
    }

    throw ApiException(
      message: 'Invalid response format from leadership stats endpoint',
      details: response,
    );
  }

  /// Get recent decisions (convenience method)
  ///
  /// Returns the last 10 decisions from the stats endpoint.
  /// For more flexible decision queries, use getProjectDecisions.
  ///
  /// Note: This is extracted from the stats endpoint, not a separate call.
  Future<List<DecisionSummary>> getRecentDecisions() async {
    final stats = await getLeadershipStats();
    return stats.recentDecisions;
  }

  /// Get all decisions for a specific project
  ///
  /// Returns complete decision timeline including:
  /// - Agent recommendations
  /// - Human decisions
  /// - Outcomes
  ///
  /// Endpoint: GET /api/v1/coleadership/projects/{projectId}/decisions/
  Future<List<Map<String, dynamic>>> getProjectDecisions(String projectId) async {
    final response = await _client.get(
      '${ApiConfig.coleadershipEndpoint}projects/$projectId/decisions/',
    );

    if (response['success'] == true && response['decisions'] != null) {
      return List<Map<String, dynamic>>.from(response['decisions'] as List);
    }

    throw ApiException(
      message: 'Invalid response format from project decisions endpoint',
      details: response,
    );
  }
}

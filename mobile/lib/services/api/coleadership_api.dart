/// Co-Leadership API Service
///
/// Session 100 Part 13 - Flutter Cockpit
/// Session 108 - Extended with list/detail/preferences
library;

import '../../core/api_client.dart';
import '../../core/api_config.dart';
import '../../models/coleadership.dart';

class CoLeadershipApi {
  final ApiClient _client;

  CoLeadershipApi(this._client);

  /// Commit a human decision
  Future<void> commitDecision({
    required String decisionId,
    required String chosenPathSummary,
    String justification = '',
    bool isOverride = false,
    String? overriddenAgentId,
  }) async {
    final response = await _client.post(
      '${ApiConfig.coleadershipEndpoint}decisions/$decisionId/human_decision/',
      {
        'chosen_path_summary': chosenPathSummary,
        'justification': justification,
        'is_override': isOverride,
        if (overriddenAgentId != null) 'overridden_agent_id': overriddenAgentId,
      },
    );

    if (response['success'] != true) {
      throw ApiException(
        message: response['error'] ?? 'Failed to commit decision',
        details: response,
      );
    }
  }

  /// Log the outcome of a decision
  Future<Map<String, dynamic>> logOutcome({
    required String decisionId,
    required String status,
    required String outcomeSummary,
    required String attribution,
    Map<String, dynamic>? metrics,
  }) async {
    final response = await _client.post(
      '${ApiConfig.coleadershipEndpoint}decisions/$decisionId/outcome/',
      {
        'status': status,
        'outcome_summary': outcomeSummary,
        'attribution': attribution,
        if (metrics != null) 'metrics': metrics,
      },
    );

    if (response['success'] != true) {
      throw ApiException(
        message: response['error'] ?? 'Failed to log outcome',
        details: response,
      );
    }

    return response;
  }

  /// Get leadership statistics for the current user
  Future<LeadershipStats> getStats() async {
    final response = await _client.get('${ApiConfig.coleadershipEndpoint}stats/');

    if (response['success'] == true && response['stats'] != null) {
      return LeadershipStats.fromJson(response['stats']);
    }

    throw ApiException(
      message: 'Invalid response format from stats endpoint',
      details: response,
    );
  }

  /// Get all decisions for a specific project
  Future<List<CoLeadershipDecision>> getProjectDecisions(String projectId) async {
    final response = await _client.get(
      '${ApiConfig.coleadershipEndpoint}projects/$projectId/decisions/',
    );

    if (response['success'] == true && response['decisions'] != null) {
      final decisions = response['decisions'] as List;
      return decisions
          .map((d) => CoLeadershipDecision.fromJson(d))
          .toList();
    }

    throw ApiException(
      message: 'Invalid response format from project decisions endpoint',
      details: response,
    );
  }

  /// List all decisions for the current user (Session 108)
  Future<List<CoLeadershipDecision>> listDecisions({
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _client.get(
      '${ApiConfig.coleadershipEndpoint}decisions/?limit=$limit&offset=$offset',
    );

    if (response['success'] == true && response['decisions'] != null) {
      final decisions = response['decisions'] as List;
      return decisions
          .map((d) => CoLeadershipDecision.fromJson(d))
          .toList();
    }

    throw ApiException(
      message: 'Invalid response format from decisions list endpoint',
      details: response,
    );
  }

  /// Get full detail for a single decision (Session 108)
  Future<CoLeadershipDecisionDetail> getDecisionDetail(String decisionId) async {
    final response = await _client.get(
      '${ApiConfig.coleadershipEndpoint}decisions/$decisionId/',
    );

    if (response['success'] == true && response['decision'] != null) {
      return CoLeadershipDecisionDetail.fromJson(response['decision']);
    }

    throw ApiException(
      message: 'Invalid response format from decision detail endpoint',
      details: response,
    );
  }

  /// Get user's co-leadership preferences (Session 108)
  Future<CoLeadershipPreferences> getPreferences() async {
    final response = await _client.get(
      '${ApiConfig.coleadershipEndpoint}preferences/',
    );

    if (response['success'] == true && response['preferences'] != null) {
      return CoLeadershipPreferences.fromJson(response['preferences']);
    }

    throw ApiException(
      message: 'Invalid response format from preferences endpoint',
      details: response,
    );
  }

  /// Update user's co-leadership preferences (Session 108)
  Future<CoLeadershipPreferences> updatePreferences({
    required bool allowToldYouSo,
    required String tone,
  }) async {
    final response = await _client.post(
      '${ApiConfig.coleadershipEndpoint}preferences/',
      {
        'allow_told_you_so': allowToldYouSo,
        'tone': tone,
      },
    );

    if (response['success'] == true && response['preferences'] != null) {
      return CoLeadershipPreferences.fromJson(response['preferences']);
    }

    throw ApiException(
      message: response['error'] ?? 'Failed to update preferences',
      details: response,
    );
  }
}

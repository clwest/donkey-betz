/// Co-Leadership Decision Models
///
/// Session 100 Part 13 - Flutter Cockpit
/// Session 108 - Extended with list/detail support
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'coleadership.freezed.dart';
part 'coleadership.g.dart';

/// Co-Leadership Decision (List view - lightweight)
@freezed
class CoLeadershipDecision with _$CoLeadershipDecision {
  const factory CoLeadershipDecision({
    required String id,
    required String title,
    @JsonKey(name: 'meeting_topic') String? meetingTopic,
    @Default('') String description,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'frozen_at') DateTime? frozenAt,
    @JsonKey(name: 'has_human_decision') required bool hasHumanDecision,
    @JsonKey(name: 'has_outcome') required bool hasOutcome,
    @Default('pending_decision') String status,  // "pending_decision" | "pending_outcome" | "complete"
    @JsonKey(name: 'outcome_attribution') String? outcomeAttribution,  // "ai" | "human" | "both" | "unknown"
    @JsonKey(name: 'project_id') String? projectId,
    @JsonKey(name: 'project_name') String? projectName,
    @JsonKey(name: 'session_id') String? sessionId,
  }) = _CoLeadershipDecision;

  factory CoLeadershipDecision.fromJson(Map<String, dynamic> json) =>
      _$CoLeadershipDecisionFromJson(json);
}

/// Co-Leadership Decision Detail (Full detail view)
@freezed
class CoLeadershipDecisionDetail with _$CoLeadershipDecisionDetail {
  const factory CoLeadershipDecisionDetail({
    required String id,
    required String title,
    @Default('') String description,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'frozen_at') DateTime? frozenAt,
    @JsonKey(name: 'is_frozen') required bool isFrozen,
    @JsonKey(name: 'has_outcome') required bool hasOutcome,
    @JsonKey(name: 'session_id') String? sessionId,
    ProjectInfo? project,
    @JsonKey(name: 'agent_recommendations') @Default([]) List<AgentRecommendation> agentRecommendations,
    @JsonKey(name: 'human_decision') HumanDecision? humanDecision,
    DecisionOutcome? outcome,
  }) = _CoLeadershipDecisionDetail;

  factory CoLeadershipDecisionDetail.fromJson(Map<String, dynamic> json) =>
      _$CoLeadershipDecisionDetailFromJson(json);
}

/// Project Info (lightweight for decision detail)
@freezed
class ProjectInfo with _$ProjectInfo {
  const factory ProjectInfo({
    required String id,
    required String name,
  }) = _ProjectInfo;

  factory ProjectInfo.fromJson(Map<String, dynamic> json) =>
      _$ProjectInfoFromJson(json);
}

/// Agent Recommendation (detailed from API)
@freezed
class AgentRecommendation with _$AgentRecommendation {
  const factory AgentRecommendation({
    @Default(0) int id,
    @JsonKey(name: 'agent_name') required String agentName,
    @JsonKey(name: 'agent_id') required String agentId,
    required String stance,
    @JsonKey(name: 'stance_display') required String stanceDisplay,
    required String summary,
    @JsonKey(name: 'recommendation_text') required String recommendationText,
    @JsonKey(name: 'risk_analysis') @Default('') String riskAnalysis,
    @JsonKey(name: 'alternative_paths') @Default([]) List<dynamic> alternativePaths,
    double? confidence,
    @JsonKey(name: 'time_horizon') @Default('') String timeHorizon,
    @JsonKey(name: 'created_at') DateTime? createdAt,
  }) = _AgentRecommendation;

  factory AgentRecommendation.fromJson(Map<String, dynamic> json) =>
      _$AgentRecommendationFromJson(json);
}

/// Human Decision (detailed from API)
@freezed
class HumanDecision with _$HumanDecision {
  const factory HumanDecision({
    @JsonKey(name: 'chosen_path_summary') required String chosenPathSummary,
    @Default('') String justification,
    @JsonKey(name: 'is_override') required bool isOverride,
    @JsonKey(name: 'overridden_agent') String? overriddenAgent,
    @JsonKey(name: 'overridden_agent_id') String? overriddenAgentId,
    @JsonKey(name: 'created_at') DateTime? createdAt,
  }) = _HumanDecision;

  factory HumanDecision.fromJson(Map<String, dynamic> json) =>
      _$HumanDecisionFromJson(json);
}

/// Decision Outcome (detailed from API)
@freezed
class DecisionOutcome with _$DecisionOutcome {
  const factory DecisionOutcome({
    required String status,
    @JsonKey(name: 'status_display') required String statusDisplay,
    required String attribution,
    @JsonKey(name: 'attribution_display') required String attributionDisplay,
    @JsonKey(name: 'outcome_summary') required String outcomeSummary,
    @Default({}) Map<String, dynamic> metrics,
    @JsonKey(name: 'told_you_so_triggered') @Default(false) bool toldYouSoTriggered,
    @JsonKey(name: 'told_you_so_message') String? toldYouSoMessage,
    @JsonKey(name: 'created_at') DateTime? createdAt,
  }) = _DecisionOutcome;

  factory DecisionOutcome.fromJson(Map<String, dynamic> json) =>
      _$DecisionOutcomeFromJson(json);
}

/// Request to commit human decision
@freezed
class HumanDecisionRequest with _$HumanDecisionRequest {
  const factory HumanDecisionRequest({
    @JsonKey(name: 'chosen_path_summary') required String chosenPathSummary,
    required String justification,
    @JsonKey(name: 'is_override') required bool isOverride,
    @JsonKey(name: 'overridden_agent_id') String? overriddenAgentId,
  }) = _HumanDecisionRequest;

  factory HumanDecisionRequest.fromJson(Map<String, dynamic> json) =>
      _$HumanDecisionRequestFromJson(json);
}

/// Request to log outcome
@freezed
class OutcomeRequest with _$OutcomeRequest {
  const factory OutcomeRequest({
    required String status,
    @JsonKey(name: 'outcome_summary') required String outcomeSummary,
    required String attribution,
    Map<String, dynamic>? metrics,
  }) = _OutcomeRequest;

  factory OutcomeRequest.fromJson(Map<String, dynamic> json) =>
      _$OutcomeRequestFromJson(json);
}

/// Leadership Statistics
@freezed
class LeadershipStats with _$LeadershipStats {
  const factory LeadershipStats({
    @JsonKey(name: 'total_decisions') @Default(0) int totalDecisions,
    @Default(0) int overrides,
    @JsonKey(name: 'override_rate') @Default(0.0) double overrideRate,
    @JsonKey(name: 'ai_correct') @Default(0) int aiCorrect,
    @JsonKey(name: 'human_correct') @Default(0) int humanCorrect,
    @JsonKey(name: 'both_correct') @Default(0) int bothCorrect,
    @Default(0) int pending,
    @JsonKey(name: 'success_rate') @Default(0.0) double successRate,
    @JsonKey(name: 'avg_ai_confidence') @Default(0.0) double avgAiConfidence,
  }) = _LeadershipStats;

  factory LeadershipStats.fromJson(Map<String, dynamic> json) =>
      _$LeadershipStatsFromJson(json);
}

/// Co-Leadership Preferences (Session 108)
@freezed
class CoLeadershipPreferences with _$CoLeadershipPreferences {
  const factory CoLeadershipPreferences({
    @JsonKey(name: 'allow_told_you_so') @Default(false) bool allowToldYouSo,
    @Default('serious') String tone,  // "serious" | "playful"
    @JsonKey(name: 'tone_choices') @Default([]) List<ToneChoice> toneChoices,
  }) = _CoLeadershipPreferences;

  factory CoLeadershipPreferences.fromJson(Map<String, dynamic> json) =>
      _$CoLeadershipPreferencesFromJson(json);
}

/// Tone Choice option
@freezed
class ToneChoice with _$ToneChoice {
  const factory ToneChoice({
    required String value,
    required String label,
  }) = _ToneChoice;

  factory ToneChoice.fromJson(Map<String, dynamic> json) =>
      _$ToneChoiceFromJson(json);
}

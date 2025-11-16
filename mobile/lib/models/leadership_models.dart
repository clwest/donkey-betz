// ignore_for_file: dangling_library_doc_comment
/// Leadership and Co-Leadership Models - Session 104
///
/// Models for AI vs Human performance tracking and decision timeline.
///
/// Author: Claude Code + Chris Partnership
/// Created: November 15, 2025 - Session 104

library leadership_models;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'leadership_models.freezed.dart';
part 'leadership_models.g.dart';

/// Leadership statistics showing AI vs Human performance
@Freezed(fromJson: true, toJson: true)
class LeadershipStats with _$LeadershipStats {
  const factory LeadershipStats({
    /// Total number of decisions made
    @Default(0) int totalDecisions,

    /// Number of times human overrode AI recommendation
    @Default(0) int overrides,

    /// Percentage of decisions that were overrides
    @Default(0.0) double overrideRate,

    /// Times AI's recommendation proved more correct
    @Default(0) int aiCorrect,

    /// Times human's override proved more correct
    @Default(0) int humanCorrect,

    /// Times both AI and human were partly correct
    @Default(0) int bothCorrect,

    /// Decisions still pending outcome
    @Default(0) int pending,

    /// Percentage of successful outcomes
    @Default(0.0) double successRate,

    /// Average AI confidence score (0.0-1.0)
    @Default(0.0) double avgAiConfidence,

    /// Recent decisions (last 10)
    @Default([]) List<DecisionSummary> recentDecisions,
  }) = _LeadershipStats;

  factory LeadershipStats.fromJson(Map<String, dynamic> json) =>
      _$LeadershipStatsFromJson(json);
}

/// Summary of a single decision for timeline display
@Freezed(fromJson: true, toJson: true)
class DecisionSummary with _$DecisionSummary {
  const factory DecisionSummary({
    /// Decision ID
    required String id,

    /// Decision title/topic
    required String title,

    /// When decision was created
    required DateTime createdAt,

    /// Whether decision has been committed
    required bool frozen,

    /// Whether outcome has been logged
    required bool hasOutcome,

    /// Whether human overrode AI
    required bool isOverride,

    /// Outcome status (display text)
    required String status,

    /// Attribution (display text)
    required String attribution,

    /// Project ID (nullable)
    String? projectId,

    /// Project name (nullable)
    String? projectName,

    /// Session ID (nullable)
    String? sessionId,
  }) = _DecisionSummary;

  factory DecisionSummary.fromJson(Map<String, dynamic> json) =>
      _$DecisionSummaryFromJson(json);
}

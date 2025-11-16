/// Personal Assistant Models
///
/// Session 112: Personal Assistant Mobile MVP
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'personal_assistant.freezed.dart';
part 'personal_assistant.g.dart';

/// Chat message model
@freezed
class AssistantMessage with _$AssistantMessage {
  const factory AssistantMessage({
    required String id,
    required String text,
    required bool isUser,
    required DateTime timestamp,
    double? confidence,
    @JsonKey(name: 'suggested_actions') List<String>? suggestedActions,
    @JsonKey(name: 'context_used') Map<String, dynamic>? contextUsed,
  }) = _AssistantMessage;

  factory AssistantMessage.fromJson(Map<String, dynamic> json) =>
      _$AssistantMessageFromJson(json);
}

/// Chat conversation model (client-side state)
@freezed
class AssistantConversation with _$AssistantConversation {
  const factory AssistantConversation({
    @Default([]) List<AssistantMessage> messages,
    DateTime? lastActivity,
    @Default(0) int totalMessages,
  }) = _AssistantConversation;
}

/// Assistant context model
@freezed
class AssistantContext with _$AssistantContext {
  const factory AssistantContext({
    @JsonKey(name: 'user_preferences') Map<String, dynamic>? userPreferences,
    @JsonKey(name: 'recent_activity') List<dynamic>? recentActivity,
    @JsonKey(name: 'personalization_level') String? personalizationLevel,
  }) = _AssistantContext;

  factory AssistantContext.fromJson(Map<String, dynamic> json) =>
      _$AssistantContextFromJson(json);
}

/// Learning summary model
@freezed
class LearningSummary with _$LearningSummary {
  const factory LearningSummary({
    @JsonKey(name: 'skills_learned') @Default([]) List<String> skillsLearned,
    @JsonKey(name: 'preferences_learned') @Default([]) List<String> preferencesLearned,
    @JsonKey(name: 'total_interactions') @Default(0) int totalInteractions,
  }) = _LearningSummary;

  factory LearningSummary.fromJson(Map<String, dynamic> json) =>
      _$LearningSummaryFromJson(json);
}

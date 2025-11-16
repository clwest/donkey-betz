/// Boardroom Meeting Models
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'boardroom_meeting.freezed.dart';
part 'boardroom_meeting.g.dart';

/// Complete boardroom meeting result from start_meeting endpoint
@freezed
class BoardroomMeetingResult with _$BoardroomMeetingResult {
  const factory BoardroomMeetingResult({
    required bool success,
    required String topic,
    @JsonKey(name: 'project_id') String? projectId,
    required List<String> participants,
    @JsonKey(name: 'agent_responses') required Map<String, String> agentResponses,
    required String summary,
    required List<String> decisions,
    @JsonKey(name: 'action_items') required List<ActionItem> actionItems,
    @JsonKey(name: 'met_at') required DateTime metAt,
    @JsonKey(name: 'session_id') required String sessionId,
    @JsonKey(name: 'decision_id') required String decisionId,
  }) = _BoardroomMeetingResult;

  factory BoardroomMeetingResult.fromJson(Map<String, dynamic> json) =>
      _$BoardroomMeetingResultFromJson(json);
}

/// Meeting summary for list view
@freezed
class BoardroomMeetingSummary with _$BoardroomMeetingSummary {
  const factory BoardroomMeetingSummary({
    required String key,
    required String topic,
    required List<String> participants,
    @JsonKey(name: 'met_at') required String metAt,
    required String summary,
    @JsonKey(name: 'decision_count') @Default(0) int decisionCount,
    @JsonKey(name: 'action_item_count') @Default(0) int actionItemCount,
    @JsonKey(name: 'project_id') String? projectId,
  }) = _BoardroomMeetingSummary;

  factory BoardroomMeetingSummary.fromJson(Map<String, dynamic> json) =>
      _$BoardroomMeetingSummaryFromJson(json);
}

/// Full meeting details
@freezed
class BoardroomMeetingDetail with _$BoardroomMeetingDetail {
  const factory BoardroomMeetingDetail({
    required String topic,
    required List<String> participants,
    @JsonKey(name: 'agent_responses') required Map<String, String> agentResponses,
    required String summary,
    required List<String> decisions,
    @JsonKey(name: 'action_items') required List<ActionItem> actionItems,
    @JsonKey(name: 'met_at') required String metAt,
    @JsonKey(name: 'project_id') String? projectId,
  }) = _BoardroomMeetingDetail;

  factory BoardroomMeetingDetail.fromJson(Map<String, dynamic> json) =>
      _$BoardroomMeetingDetailFromJson(json);
}

/// Action item from meeting
@freezed
class ActionItem with _$ActionItem {
  const factory ActionItem({
    required String task,
    required String owner,
    required String priority,
  }) = _ActionItem;

  factory ActionItem.fromJson(Map<String, dynamic> json) =>
      _$ActionItemFromJson(json);
}

/// Request payload for starting a meeting
@freezed
class StartMeetingRequest with _$StartMeetingRequest {
  const factory StartMeetingRequest({
    required String topic,
    @JsonKey(name: 'project_id') String? projectId,
    required List<String> participants,
  }) = _StartMeetingRequest;

  factory StartMeetingRequest.fromJson(Map<String, dynamic> json) =>
      _$StartMeetingRequestFromJson(json);

  /// Convert to JSON for API request
  Map<String, dynamic> toJson() => {
        'topic': topic,
        if (projectId != null) 'project_id': projectId,
        'participants': participants,
      };
}

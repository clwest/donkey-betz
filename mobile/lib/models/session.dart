/// AI Session Model
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'session.freezed.dart';
part 'session.g.dart';

@freezed
class AISession with _$AISession {
  const factory AISession({
    @JsonKey(name: 'session_id') required String sessionId,
    required String title,
    @Default('') String description,
    @JsonKey(name: 'session_type') @Default('general') String sessionType,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    @JsonKey(name: 'ended_at') DateTime? endedAt,
    @JsonKey(name: 'total_images') int? totalImages,
    @JsonKey(name: 'total_videos') int? totalVideos,
    @JsonKey(name: 'total_audio') int? totalAudio,
    // Aliases for convenience (Session 101)
    @JsonKey(name: 'image_count') @Default(0) int imageCount,
    @JsonKey(name: 'video_count') @Default(0) int videoCount,
    @JsonKey(name: 'project_id') String? projectId,
    // Project session details (from get_project_sessions endpoint)
    @JsonKey(name: 'last_activity') String? lastActivity,
    @JsonKey(name: 'project_images') @Default(0) int projectImages,
    @JsonKey(name: 'project_videos') @Default(0) int projectVideos,
    @JsonKey(name: 'has_project') @Default(false) bool hasProject,
    @JsonKey(name: 'conversation_length') @Default(0) int conversationLength,
    // Boardroom specific fields
    List<String>? participants,
    @JsonKey(name: 'meeting_topic') String? meetingTopic,
    @JsonKey(name: 'meeting_summary') String? meetingSummary,
    List<String>? decisions,
    @JsonKey(name: 'action_items') List<Map<String, dynamic>>? actionItems,
    @JsonKey(name: 'agent_responses') Map<String, dynamic>? agentResponses,
  }) = _AISession;

  factory AISession.fromJson(Map<String, dynamic> json) =>
      _$AISessionFromJson(json);
}

/// Session type enum
enum SessionType {
  @JsonValue('default')
  defaultSession,
  boardroom,
  branding,
  @JsonValue('logo_design')
  logoDesign,
  @JsonValue('video_creation')
  videoCreation,
  @JsonValue('content_package')
  contentPackage,
  exploration,
  refinement,
  general;

  String get displayName {
    switch (this) {
      case SessionType.defaultSession:
        return 'Default Session';
      case SessionType.boardroom:
        return 'Executive Boardroom Meeting';
      case SessionType.branding:
        return 'Branding Package';
      case SessionType.logoDesign:
        return 'Logo Design';
      case SessionType.videoCreation:
        return 'Video Creation';
      case SessionType.contentPackage:
        return 'Content Package';
      case SessionType.exploration:
        return 'Creative Exploration';
      case SessionType.refinement:
        return 'Content Refinement';
      case SessionType.general:
        return 'General Creation';
    }
  }
}

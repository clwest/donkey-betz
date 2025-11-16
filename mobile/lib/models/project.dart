/// Creative Project Model
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'project.freezed.dart';
part 'project.g.dart';

// Helper to extract ID from backend response
String _idFromJson(dynamic value) => value.toString();

@freezed
class Project with _$Project {
  const factory Project({
    // Backend returns 'id', Flutter expects 'project_id'
    @JsonKey(name: 'id', fromJson: _idFromJson) required String projectId,
    required String name,
    required String description,
    required String goal,
    required String status,
    required String category,
    @Default([]) List<String> tags,
    @JsonKey(name: 'is_quick_starts') @Default(false) bool isQuickStarts,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'updated_at') DateTime? updatedAt,
    DateTime? deadline,
    @JsonKey(name: 'total_workflows') int? totalWorkflows,
    @JsonKey(name: 'completed_workflows') int? completedWorkflows,
    @JsonKey(name: 'image_count') @Default(0) int imageCount,
    @JsonKey(name: 'video_count') @Default(0) int videoCount,
  }) = _Project;

  factory Project.fromJson(Map<String, dynamic> json) =>
      _$ProjectFromJson(json);
}

/// Project status enum
enum ProjectStatus {
  planning,
  @JsonValue('in_progress')
  inProgress,
  review,
  completed,
  archived;

  String get displayName {
    switch (this) {
      case ProjectStatus.planning:
        return 'Planning';
      case ProjectStatus.inProgress:
        return 'In Progress';
      case ProjectStatus.review:
        return 'Under Review';
      case ProjectStatus.completed:
        return 'Completed';
      case ProjectStatus.archived:
        return 'Archived';
    }
  }
}

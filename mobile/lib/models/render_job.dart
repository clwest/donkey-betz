/// Session 105: RenderJob Model
///
/// Represents a video render job from the backend.
/// Status flow: queued → dispatching → rendering → done/error
///
/// Freezed model with JSON serialization (snake_case via build.yaml).

import 'package:freezed_annotation/freezed_annotation.dart';

part 'render_job.freezed.dart';
part 'render_job.g.dart';

/// Render job status values (must match Django model)
enum RenderJobStatus {
  queued,
  dispatching,
  rendering,
  done,
  error,
}

@Freezed(fromJson: true, toJson: true)
class RenderJob with _$RenderJob {
  const RenderJob._(); // Private constructor for adding getters

  const factory RenderJob({
    required String id,
    String? title, // Session 106: Auto-generated human-friendly title
    required RenderJobStatus status,
    @Default(0.0) double progress,
    @Default(0.0) double progressPercentage,
    String? resultUrl,
    String? errorMessage,
    required DateTime createdAt,
    required DateTime updatedAt,
    DateTime? completedAt,
    // Optional linked entities
    String? projectName,
    String? sessionTitle,
  }) = _RenderJob;

  factory RenderJob.fromJson(Map<String, dynamic> json) => _$RenderJobFromJson(json);

  /// Job is in a terminal state (done or error)
  bool get isComplete => status == RenderJobStatus.done || status == RenderJobStatus.error;

  /// Job is currently being processed (dispatching or rendering)
  bool get isActive => status == RenderJobStatus.dispatching || status == RenderJobStatus.rendering;

  /// Job succeeded
  bool get isSuccess => status == RenderJobStatus.done;

  /// Job failed
  bool get isFailed => status == RenderJobStatus.error;

  /// Get user-friendly status text
  String get statusText {
    switch (status) {
      case RenderJobStatus.queued:
        return 'Queued';
      case RenderJobStatus.dispatching:
        return 'Starting...';
      case RenderJobStatus.rendering:
        return 'Rendering ${progressPercentage.toStringAsFixed(0)}%';
      case RenderJobStatus.done:
        return 'Complete';
      case RenderJobStatus.error:
        return 'Failed';
    }
  }

  /// Get status color (Material color values)
  int get statusColor {
    switch (status) {
      case RenderJobStatus.queued:
        return 0xFF607D8B; // Grey
      case RenderJobStatus.dispatching:
        return 0xFF2196F3; // Blue
      case RenderJobStatus.rendering:
        return 0xFF9C27B0; // Purple
      case RenderJobStatus.done:
        return 0xFF4CAF50; // Green
      case RenderJobStatus.error:
        return 0xFFF44336; // Red
    }
  }
}

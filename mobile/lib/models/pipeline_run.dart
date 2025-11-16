/// Session 109: PipelineRun Model
///
/// Represents a single execution of a pipeline template.
/// Status flow: pending → running → completed/failed
///
/// Freezed model with JSON serialization (snake_case via build.yaml).

import 'package:freezed_annotation/freezed_annotation.dart';

part 'pipeline_run.freezed.dart';
part 'pipeline_run.g.dart';

/// Pipeline run status values (must match Django model)
enum PipelineRunStatus {
  pending,
  running,
  completed,
  failed,
}

@Freezed(fromJson: true, toJson: true)
class PipelineRun with _$PipelineRun {
  const PipelineRun._(); // Private constructor for adding getters

  const factory PipelineRun({
    required String id,
    required String templateSlug,
    required String templateName,
    required PipelineRunStatus status,
    @Default(0) int currentStep,
    @Default(0) int totalSteps,
    @Default(0) int progressPercentage,
    @Default({}) Map<String, dynamic> inputPayload,
    @Default({}) Map<String, dynamic> outputPayload,
    @Default('') String log,
    String? errorMessage,
    required DateTime createdAt,
    required DateTime updatedAt,
    DateTime? completedAt,
    double? duration,
    String? projectId,
    String? projectName,
    String? sessionId,
    String? sessionTitle,
  }) = _PipelineRun;

  factory PipelineRun.fromJson(Map<String, dynamic> json) =>
      _$PipelineRunFromJson(json);

  /// Run is in a terminal state (completed or failed)
  bool get isComplete =>
      status == PipelineRunStatus.completed ||
      status == PipelineRunStatus.failed;

  /// Run is currently being processed
  bool get isActive =>
      status == PipelineRunStatus.running ||
      status == PipelineRunStatus.pending;

  /// Run succeeded
  bool get isSuccess => status == PipelineRunStatus.completed;

  /// Run failed
  bool get isFailed => status == PipelineRunStatus.failed;

  /// Get user-friendly status text
  String get statusText {
    switch (status) {
      case PipelineRunStatus.pending:
        return 'Queued';
      case PipelineRunStatus.running:
        return 'Running step $currentStep/$totalSteps';
      case PipelineRunStatus.completed:
        return 'Complete';
      case PipelineRunStatus.failed:
        return 'Failed';
    }
  }

  /// Get detailed progress text
  String get progressText {
    if (status == PipelineRunStatus.completed) {
      return 'Completed in ${_formatDuration()}';
    }
    if (status == PipelineRunStatus.failed) {
      return errorMessage ?? 'Pipeline failed';
    }
    if (status == PipelineRunStatus.running) {
      return 'Step $currentStep of $totalSteps ($progressPercentage%)';
    }
    return 'Waiting to start...';
  }

  /// Get status color (Material color values)
  int get statusColor {
    switch (status) {
      case PipelineRunStatus.pending:
        return 0xFF607D8B; // Grey
      case PipelineRunStatus.running:
        return 0xFF2196F3; // Blue
      case PipelineRunStatus.completed:
        return 0xFF4CAF50; // Green
      case PipelineRunStatus.failed:
        return 0xFFF44336; // Red
    }
  }

  /// Get icon for current status
  String get statusIcon {
    switch (status) {
      case PipelineRunStatus.pending:
        return '⏳';
      case PipelineRunStatus.running:
        return '⚙️';
      case PipelineRunStatus.completed:
        return '✅';
      case PipelineRunStatus.failed:
        return '❌';
    }
  }

  /// Format duration for display
  String _formatDuration() {
    if (duration == null) return 'N/A';
    if (duration! < 60) {
      return '${duration!.toStringAsFixed(1)}s';
    }
    final minutes = (duration! / 60).floor();
    final seconds = (duration! % 60).floor();
    return '${minutes}m ${seconds}s';
  }

  /// Get list of generated image URLs from output_payload
  List<String> get generatedImageUrls {
    final images = outputPayload['images'];
    if (images is List) {
      return images
          .whereType<Map>()
          .map((img) => img['url'] as String?)
          .whereType<String>()
          .toList();
    }
    return [];
  }

  /// Get generated video URL from output_payload
  String? get generatedVideoUrl {
    return outputPayload['video_url'] as String?;
  }

  /// Get expanded prompts from output_payload
  List<String> get expandedPrompts {
    final prompts = outputPayload['prompts'];
    if (prompts is List) {
      return prompts.whereType<String>().toList();
    }
    return [];
  }

  /// Check if run has generated content
  bool get hasGeneratedContent =>
      generatedImageUrls.isNotEmpty ||
      generatedVideoUrl != null ||
      expandedPrompts.isNotEmpty;
}

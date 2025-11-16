/// Session 109: PipelineTemplate Model
///
/// Represents a creative pipeline template from the backend.
/// Templates define reusable workflow "recipes" that chain AI operations.
///
/// Freezed model with JSON serialization (snake_case via build.yaml).

import 'package:freezed_annotation/freezed_annotation.dart';

part 'pipeline_template.freezed.dart';
part 'pipeline_template.g.dart';

@Freezed(fromJson: true, toJson: true)
class PipelineTemplate with _$PipelineTemplate {
  const PipelineTemplate._(); // Private constructor for adding getters

  const factory PipelineTemplate({
    required String slug,
    required String name,
    required String description,
    @Default(0) int totalSteps,
    @Default({}) Map<String, dynamic> inputs,
    @Default({}) Map<String, dynamic> outputs,
  }) = _PipelineTemplate;

  factory PipelineTemplate.fromJson(Map<String, dynamic> json) =>
      _$PipelineTemplateFromJson(json);

  /// Get user-friendly step count text
  String get stepCountText =>
      '$totalSteps step${totalSteps == 1 ? '' : 's'}';

  /// Check if template has required inputs
  bool get hasRequiredInputs =>
      inputs.values.any((input) =>
          input is Map && input['required'] == true);

  /// Get list of required input keys
  List<String> get requiredInputKeys => inputs.entries
      .where((e) => e.value is Map && e.value['required'] == true)
      .map((e) => e.key)
      .toList();
}

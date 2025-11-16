/// Voice Input Result Model
///
/// Session 113: Voice Input MVP
library;

import 'package:freezed_annotation/freezed_annotation.dart';
import 'personal_assistant.dart';

part 'assistant_voice.freezed.dart';
part 'assistant_voice.g.dart';

@freezed
class AssistantVoiceResult with _$AssistantVoiceResult {
  const factory AssistantVoiceResult({
    required bool success,
    required String userText,
    required AssistantMessageData assistantMessage,
    String? error,
  }) = _AssistantVoiceResult;

  factory AssistantVoiceResult.fromJson(Map<String, dynamic> json) =>
      _$AssistantVoiceResultFromJson(json);
}

/// Assistant message data from backend
@freezed
class AssistantMessageData with _$AssistantMessageData {
  const factory AssistantMessageData({
    required String response,
    List<String>? suggestions,
    List<String>? actions,
    double? confidence,
    @JsonKey(name: 'ai_generated') bool? aiGenerated,
    String? model,
  }) = _AssistantMessageData;

  factory AssistantMessageData.fromJson(Map<String, dynamic> json) =>
      _$AssistantMessageDataFromJson(json);
}

/// Extension for converting AssistantMessageData to AssistantMessage
extension AssistantMessageDataX on AssistantMessageData {
  /// Convert to AssistantMessage for display
  AssistantMessage toAssistantMessage() {
    // Combine suggestions and actions into suggestedActions
    List<String>? suggestedActions;
    if ((suggestions?.isNotEmpty ?? false) || (actions?.isNotEmpty ?? false)) {
      suggestedActions = [
        ...?suggestions,
        ...?actions,
      ];
    }

    return AssistantMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: response,
      isUser: false,
      timestamp: DateTime.now(),
      confidence: confidence,
      suggestedActions: suggestedActions,
    );
  }
}

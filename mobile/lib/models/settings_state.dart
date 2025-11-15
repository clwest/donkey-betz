/// Settings State Model
///
/// Session 102 - Mobile Auth & Connection Settings
library;

import 'package:freezed_annotation/freezed_annotation.dart';
import 'connection_status.dart';

part 'settings_state.freezed.dart';
part 'settings_state.g.dart';

/// Application settings state
@freezed
class SettingsState with _$SettingsState {
  const factory SettingsState({
    /// API base URL (e.g., http://localhost:8000)
    String? apiBaseUrl,

    /// API key for authentication
    String? apiKey,

    /// Whether settings are currently being saved
    @Default(false) bool isSaving,

    /// Whether a connection test is in progress
    @Default(false) bool isTesting,

    /// Last connection test result
    ConnectionStatus? lastTestResult,

    /// Last connection test message (error or success details)
    String? lastTestMessage,

    /// When the last successful connection was made
    DateTime? lastSuccessfulConnection,
  }) = _SettingsState;

  factory SettingsState.fromJson(Map<String, dynamic> json) =>
      _$SettingsStateFromJson(json);
}

/// Settings form data (for editing)
@freezed
class SettingsFormData with _$SettingsFormData {
  const factory SettingsFormData({
    /// API base URL being edited
    @Default('') String apiBaseUrl,

    /// API key being edited
    @Default('') String apiKey,
  }) = _SettingsFormData;

  factory SettingsFormData.fromJson(Map<String, dynamic> json) =>
      _$SettingsFormDataFromJson(json);
}

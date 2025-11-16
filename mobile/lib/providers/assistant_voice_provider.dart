/// Personal Assistant Voice Input Provider
///
/// Session 113: Voice Input MVP
library;

import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import '../services/api/assistant_voice_api.dart';
import '../providers/settings_provider.dart' show settingsControllerProvider;
import '../providers/personal_assistant_provider.dart';
import '../models/personal_assistant.dart';
import '../models/assistant_voice.dart'; // For AssistantMessageDataX extension
import '../core/api_client.dart' show ApiException;

/// Voice recording state
enum VoiceRecordingState {
  idle,
  recording,
  uploading,
  error,
}

/// Voice recording state with error message
class VoiceState {
  final VoiceRecordingState state;
  final String? errorMessage;
  final String? recordingPath;

  const VoiceState({
    required this.state,
    this.errorMessage,
    this.recordingPath,
  });

  VoiceState copyWith({
    VoiceRecordingState? state,
    String? errorMessage,
    String? recordingPath,
  }) {
    return VoiceState(
      state: state ?? this.state,
      errorMessage: errorMessage ?? this.errorMessage,
      recordingPath: recordingPath ?? this.recordingPath,
    );
  }
}

/// Voice recording provider
final voiceRecordingProvider =
    StateNotifierProvider<VoiceRecordingNotifier, VoiceState>((ref) {
  return VoiceRecordingNotifier(ref);
});

/// Voice recording notifier
class VoiceRecordingNotifier extends StateNotifier<VoiceState> {
  final Ref _ref;
  final AudioRecorder _recorder = AudioRecorder();
  String? _currentRecordingPath;

  VoiceRecordingNotifier(this._ref)
      : super(const VoiceState(state: VoiceRecordingState.idle));

  /// Start recording
  Future<void> startRecording() async {
    try {
      // Check permission
      if (!await _recorder.hasPermission()) {
        state = VoiceState(
          state: VoiceRecordingState.error,
          errorMessage: 'Microphone permission denied. Please enable it in Settings.',
        );
        return;
      }

      // Get temp directory for recording
      final tempDir = await getTemporaryDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      _currentRecordingPath = '${tempDir.path}/voice_$timestamp.m4a';

      // Start recording
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.aacLc, // AAC for iOS
          bitRate: 128000,
          sampleRate: 44100,
        ),
        path: _currentRecordingPath!,
      );

      state = VoiceState(
        state: VoiceRecordingState.recording,
        recordingPath: _currentRecordingPath,
      );
    } catch (e) {
      state = VoiceState(
        state: VoiceRecordingState.error,
        errorMessage: 'Failed to start recording: ${e.toString()}',
      );
    }
  }

  /// Stop recording and send to backend
  Future<void> stopAndSend() async {
    try {
      if (state.state != VoiceRecordingState.recording) {
        return;
      }

      // Stop recording
      final path = await _recorder.stop();

      if (path == null || !File(path).existsSync()) {
        state = VoiceState(
          state: VoiceRecordingState.error,
          errorMessage: 'Recording failed - no audio file created',
        );
        return;
      }

      // Update state to uploading
      state = const VoiceState(state: VoiceRecordingState.uploading);

      // Get API configuration
      final settings = _ref.read(settingsControllerProvider);
      final apiUrl = settings.apiBaseUrl ?? 'http://127.0.0.1:8000';
      final apiKey = settings.apiKey ?? '';

      if (apiUrl.isEmpty || apiKey.isEmpty) {
        state = VoiceState(
          state: VoiceRecordingState.error,
          errorMessage: 'API not configured. Please check Settings.',
        );
        return;
      }

      // Create API client
      final voiceApi = AssistantVoiceApi(
        baseUrl: apiUrl,
        apiKey: apiKey,
      );

      // Send voice to backend
      final result = await voiceApi.sendVoice(filePath: path);

      // Add messages to conversation
      final conversationNotifier =
          _ref.read(assistantConversationProvider.notifier);

      // Add user message (transcribed text)
      final userMessage = AssistantMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: result.userText,
        isUser: true,
        timestamp: DateTime.now(),
      );

      // Add assistant response
      final assistantMessage = result.assistantMessage.toAssistantMessage();

      // Add both messages to conversation
      conversationNotifier.addMessage(userMessage);
      conversationNotifier.addMessage(assistantMessage);

      // Clean up recording file
      try {
        await File(path).delete();
      } catch (_) {
        // Ignore cleanup errors
      }

      // Reset to idle
      state = const VoiceState(state: VoiceRecordingState.idle);
    } on ApiException catch (e) {
      state = VoiceState(
        state: VoiceRecordingState.error,
        errorMessage: e.message,
      );
    } catch (e) {
      state = VoiceState(
        state: VoiceRecordingState.error,
        errorMessage: 'Failed to process voice: ${e.toString()}',
      );
    }
  }

  /// Cancel recording without sending
  Future<void> cancelRecording() async {
    try {
      if (state.state == VoiceRecordingState.recording) {
        final path = await _recorder.stop();

        // Clean up recording file
        if (path != null && File(path).existsSync()) {
          try {
            await File(path).delete();
          } catch (_) {
            // Ignore cleanup errors
          }
        }
      }

      state = const VoiceState(state: VoiceRecordingState.idle);
    } catch (e) {
      state = VoiceState(
        state: VoiceRecordingState.error,
        errorMessage: 'Failed to cancel recording: ${e.toString()}',
      );
    }
  }

  /// Reset error state
  void clearError() {
    if (state.state == VoiceRecordingState.error) {
      state = const VoiceState(state: VoiceRecordingState.idle);
    }
  }

  @override
  void dispose() {
    _recorder.dispose();
    super.dispose();
  }
}

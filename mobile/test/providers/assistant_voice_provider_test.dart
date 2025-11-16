/// Tests for Assistant Voice Provider
///
/// Session 113: Voice Input MVP
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:donkey_os_cockpit/providers/assistant_voice_provider.dart';

void main() {
  group('VoiceState', () {
    test('creates with initial state', () {
      const state = VoiceState(state: VoiceRecordingState.idle);

      expect(state.state, VoiceRecordingState.idle);
      expect(state.errorMessage, null);
      expect(state.recordingPath, null);
    });

    test('copyWith updates state', () {
      const initial = VoiceState(state: VoiceRecordingState.idle);

      final updated = initial.copyWith(
        state: VoiceRecordingState.recording,
        recordingPath: '/path/to/recording.m4a',
      );

      expect(updated.state, VoiceRecordingState.recording);
      expect(updated.recordingPath, '/path/to/recording.m4a');
      expect(updated.errorMessage, null);
    });

    test('copyWith with error', () {
      const initial = VoiceState(state: VoiceRecordingState.idle);

      final updated = initial.copyWith(
        state: VoiceRecordingState.error,
        errorMessage: 'Permission denied',
      );

      expect(updated.state, VoiceRecordingState.error);
      expect(updated.errorMessage, 'Permission denied');
    });
  });

  group('VoiceRecordingState', () {
    test('has all expected states', () {
      expect(VoiceRecordingState.idle, isNotNull);
      expect(VoiceRecordingState.recording, isNotNull);
      expect(VoiceRecordingState.uploading, isNotNull);
      expect(VoiceRecordingState.error, isNotNull);
    });

    test('states are distinct', () {
      expect(VoiceRecordingState.idle, isNot(VoiceRecordingState.recording));
      expect(VoiceRecordingState.recording, isNot(VoiceRecordingState.uploading));
      expect(VoiceRecordingState.uploading, isNot(VoiceRecordingState.error));
    });
  });

  // Note: Full provider tests would require mocking AudioRecorder and file system
  // For MVP, we focus on model and state tests
  // Integration tests can be done manually with real device
}

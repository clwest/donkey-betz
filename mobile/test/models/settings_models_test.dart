/// Settings Models Test
///
/// Session 102 - Mobile Auth & Connection Settings
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:donkey_os_cockpit/models/connection_status.dart';
import 'package:donkey_os_cockpit/models/settings_state.dart';

void main() {
  group('ConnectionStatus', () {
    test('display names are correct', () {
      expect(ConnectionStatus.connected.displayName, 'Connected');
      expect(ConnectionStatus.failed.displayName, 'Connection Failed');
      expect(ConnectionStatus.notConfigured.displayName, 'Not Configured');
    });

    test('isSuccess returns true only for connected', () {
      expect(ConnectionStatus.connected.isSuccess, true);
      expect(ConnectionStatus.failed.isSuccess, false);
      expect(ConnectionStatus.notConfigured.isSuccess, false);
    });

    test('isError returns true only for failed', () {
      expect(ConnectionStatus.connected.isError, false);
      expect(ConnectionStatus.failed.isError, true);
      expect(ConnectionStatus.notConfigured.isError, false);
    });
  });

  group('SettingsState', () {
    test('creates default state correctly', () {
      const state = SettingsState();

      expect(state.apiBaseUrl, null);
      expect(state.apiKey, null);
      expect(state.isSaving, false);
      expect(state.isTesting, false);
      expect(state.lastTestResult, null);
      expect(state.lastTestMessage, null);
      expect(state.lastSuccessfulConnection, null);
    });

    test('creates state with values correctly', () {
      final now = DateTime.now();
      final state = SettingsState(
        apiBaseUrl: 'http://localhost:8000',
        apiKey: 'test-api-key',
        isSaving: true,
        isTesting: false,
        lastTestResult: ConnectionStatus.connected,
        lastTestMessage: 'Success',
        lastSuccessfulConnection: now,
      );

      expect(state.apiBaseUrl, 'http://localhost:8000');
      expect(state.apiKey, 'test-api-key');
      expect(state.isSaving, true);
      expect(state.isTesting, false);
      expect(state.lastTestResult, ConnectionStatus.connected);
      expect(state.lastTestMessage, 'Success');
      expect(state.lastSuccessfulConnection, now);
    });

    test('copyWith updates only specified fields', () {
      const initialState = SettingsState(
        apiBaseUrl: 'http://localhost:8000',
        apiKey: 'old-key',
      );

      final updatedState = initialState.copyWith(
        apiKey: 'new-key',
        isSaving: true,
      );

      expect(updatedState.apiBaseUrl, 'http://localhost:8000'); // Unchanged
      expect(updatedState.apiKey, 'new-key'); // Updated
      expect(updatedState.isSaving, true); // Updated
    });

    test('serializes to JSON correctly', () {
      final now = DateTime.now();
      final state = SettingsState(
        apiBaseUrl: 'http://localhost:8000',
        apiKey: 'test-key',
        lastSuccessfulConnection: now,
      );

      final json = state.toJson();

      expect(json['apiBaseUrl'], 'http://localhost:8000');
      expect(json['apiKey'], 'test-key');
      expect(json['lastSuccessfulConnection'], now.toIso8601String());
    });

    test('deserializes from JSON correctly', () {
      final now = DateTime.now();
      final json = {
        'apiBaseUrl': 'http://localhost:8000',
        'apiKey': 'test-key',
        'isSaving': false,
        'isTesting': false,
        'lastSuccessfulConnection': now.toIso8601String(),
      };

      final state = SettingsState.fromJson(json);

      expect(state.apiBaseUrl, 'http://localhost:8000');
      expect(state.apiKey, 'test-key');
      expect(state.lastSuccessfulConnection, now);
    });
  });

  group('SettingsFormData', () {
    test('creates default form data correctly', () {
      const formData = SettingsFormData();

      expect(formData.apiBaseUrl, '');
      expect(formData.apiKey, '');
    });

    test('creates form data with values correctly', () {
      const formData = SettingsFormData(
        apiBaseUrl: 'http://localhost:8000',
        apiKey: 'test-key',
      );

      expect(formData.apiBaseUrl, 'http://localhost:8000');
      expect(formData.apiKey, 'test-key');
    });

    test('serializes to JSON correctly', () {
      const formData = SettingsFormData(
        apiBaseUrl: 'http://localhost:8000',
        apiKey: 'test-key',
      );

      final json = formData.toJson();

      expect(json['apiBaseUrl'], 'http://localhost:8000');
      expect(json['apiKey'], 'test-key');
    });
  });
}

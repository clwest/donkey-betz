/// Settings Provider Test
///
/// Session 102 - Mobile Auth & Connection Settings
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:donkey_os_cockpit/providers/settings_provider.dart';
import 'package:donkey_os_cockpit/models/connection_status.dart';

void main() {
  group('SettingsController', () {
    late FlutterSecureStorage secureStorage;
    late SharedPreferences prefs;

    setUp(() async {
      // Initialize test storage
      SharedPreferences.setMockInitialValues({});
      prefs = await SharedPreferences.getInstance();
      secureStorage = const FlutterSecureStorage();
    });

    tearDown(() async {
      // Clean up
      await prefs.clear();
      await secureStorage.deleteAll();
    });

    test('initial state is empty', () {
      final controller = SettingsController(
        secureStorage: secureStorage,
        prefs: prefs,
      );

      expect(controller.state.apiBaseUrl, null);
      expect(controller.state.apiKey, null);
      expect(controller.state.isSaving, false);
      expect(controller.state.isTesting, false);
    });

    test('saveSettings stores values correctly', () async {
      final controller = SettingsController(
        secureStorage: secureStorage,
        prefs: prefs,
      );

      await controller.saveSettings(
        apiBaseUrl: 'http://localhost:8000',
        apiKey: 'test-api-key',
      );

      expect(controller.state.apiBaseUrl, 'http://localhost:8000');
      expect(controller.state.apiKey, 'test-api-key');
      expect(controller.state.isSaving, false);

      // Verify storage
      final storedUrl = prefs.getString(SettingsKeys.apiBaseUrl);
      final storedKey = await secureStorage.read(key: SettingsKeys.apiKey);

      expect(storedUrl, 'http://localhost:8000');
      expect(storedKey, 'test-api-key');
    });

    test('saveSettings validates empty inputs', () async {
      final controller = SettingsController(
        secureStorage: secureStorage,
        prefs: prefs,
      );

      await controller.saveSettings(
        apiBaseUrl: '',
        apiKey: '',
      );

      expect(controller.state.lastTestResult, ConnectionStatus.failed);
      expect(
        controller.state.lastTestMessage,
        'API base URL and API key are required',
      );
    });

    test('loadSettings retrieves stored values', () async {
      // Store values first
      await prefs.setString(SettingsKeys.apiBaseUrl, 'http://localhost:8000');
      await secureStorage.write(key: SettingsKeys.apiKey, value: 'test-key');

      final controller = SettingsController(
        secureStorage: secureStorage,
        prefs: prefs,
      );

      await controller.loadSettings();

      expect(controller.state.apiBaseUrl, 'http://localhost:8000');
      expect(controller.state.apiKey, 'test-key');
    });

    test('loadSettings sets notConfigured when values missing', () async {
      final controller = SettingsController(
        secureStorage: secureStorage,
        prefs: prefs,
      );

      await controller.loadSettings();

      expect(controller.state.lastTestResult, ConnectionStatus.notConfigured);
    });

    test('clearSettings removes all values', () async {
      // Store values first
      await prefs.setString(SettingsKeys.apiBaseUrl, 'http://localhost:8000');
      await secureStorage.write(key: SettingsKeys.apiKey, value: 'test-key');

      final controller = SettingsController(
        secureStorage: secureStorage,
        prefs: prefs,
      );

      await controller.loadSettings();
      expect(controller.state.apiBaseUrl, 'http://localhost:8000');

      await controller.clearSettings();

      expect(controller.state.apiBaseUrl, null);
      expect(controller.state.apiKey, null);
      expect(controller.state.lastTestResult, ConnectionStatus.notConfigured);

      // Verify storage is cleared
      final storedUrl = prefs.getString(SettingsKeys.apiBaseUrl);
      final storedKey = await secureStorage.read(key: SettingsKeys.apiKey);

      expect(storedUrl, null);
      expect(storedKey, null);
    });

    test('testConnection requires configuration', () async {
      final controller = SettingsController(
        secureStorage: secureStorage,
        prefs: prefs,
      );

      await controller.testConnection();

      expect(controller.state.lastTestResult, ConnectionStatus.notConfigured);
      expect(
        controller.state.lastTestMessage,
        'Please configure API endpoint and key first',
      );
    });
  });
}

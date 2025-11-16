/// Settings State Provider
///
/// Session 102 - Mobile Auth & Connection Settings
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/settings_state.dart';
import '../models/connection_status.dart';

/// Storage keys
class SettingsKeys {
  static const String apiBaseUrl = 'api_base_url';
  static const String apiKey = 'api_key';
  static const String lastSuccessfulConnection = 'last_successful_connection';
}

/// Settings controller
class SettingsController extends StateNotifier<SettingsState> {
  final FlutterSecureStorage _secureStorage;
  final SharedPreferences _prefs;

  SettingsController({
    required FlutterSecureStorage secureStorage,
    required SharedPreferences prefs,
  })  : _secureStorage = secureStorage,
        _prefs = prefs,
        super(const SettingsState());

  /// Load settings from storage
  Future<void> loadSettings() async {
    try {
      // Load API base URL from shared preferences
      final apiBaseUrl = _prefs.getString(SettingsKeys.apiBaseUrl);

      // Load API key from secure storage
      final apiKey = await _secureStorage.read(key: SettingsKeys.apiKey);

      // Load last successful connection timestamp
      final lastConnectionStr =
          _prefs.getString(SettingsKeys.lastSuccessfulConnection);
      final lastConnection = lastConnectionStr != null
          ? DateTime.tryParse(lastConnectionStr)
          : null;

      // Determine connection status
      ConnectionStatus? status;
      if (apiBaseUrl == null || apiKey == null) {
        status = ConnectionStatus.notConfigured;
      }

      state = state.copyWith(
        apiBaseUrl: apiBaseUrl,
        apiKey: apiKey,
        lastSuccessfulConnection: lastConnection,
        lastTestResult: status,
      );
    } catch (e) {
      state = state.copyWith(
        lastTestResult: ConnectionStatus.failed,
        lastTestMessage: 'Failed to load settings: ${e.toString()}',
      );
    }
  }

  /// Save settings to storage
  Future<void> saveSettings({
    required String apiBaseUrl,
    required String apiKey,
  }) async {
    state = state.copyWith(isSaving: true);

    try {
      // Validate inputs
      if (apiBaseUrl.isEmpty || apiKey.isEmpty) {
        state = state.copyWith(
          isSaving: false,
          lastTestResult: ConnectionStatus.failed,
          lastTestMessage: 'API base URL and API key are required',
        );
        return;
      }

      // Save API base URL to shared preferences
      await _prefs.setString(SettingsKeys.apiBaseUrl, apiBaseUrl);

      // Save API key to secure storage
      await _secureStorage.write(key: SettingsKeys.apiKey, value: apiKey);

      state = state.copyWith(
        isSaving: false,
        apiBaseUrl: apiBaseUrl,
        apiKey: apiKey,
        lastTestMessage: 'Settings saved successfully',
      );
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        lastTestResult: ConnectionStatus.failed,
        lastTestMessage: 'Failed to save settings: ${e.toString()}',
      );
    }
  }

  /// Test connection to the backend
  Future<void> testConnection() async {
    if (state.apiBaseUrl == null || state.apiKey == null) {
      state = state.copyWith(
        lastTestResult: ConnectionStatus.notConfigured,
        lastTestMessage: 'Please configure API endpoint and key first',
      );
      return;
    }

    state = state.copyWith(isTesting: true, lastTestMessage: null);

    try {
      // Test connection using the health endpoint
      final url = Uri.parse('${state.apiBaseUrl}/health/ping/');
      final response = await http.get(
        url,
        headers: {
          'X-API-Key': state.apiKey!,
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['ok'] == true) {
          // Connection successful
          final now = DateTime.now();
          await _prefs.setString(
            SettingsKeys.lastSuccessfulConnection,
            now.toIso8601String(),
          );

          state = state.copyWith(
            isTesting: false,
            lastTestResult: ConnectionStatus.connected,
            lastTestMessage: 'Successfully connected to backend',
            lastSuccessfulConnection: now,
          );
          return;
        }
      }

      // Connection failed
      state = state.copyWith(
        isTesting: false,
        lastTestResult: ConnectionStatus.failed,
        lastTestMessage:
            'Connection failed: Server returned status ${response.statusCode}',
      );
    } catch (e) {
      state = state.copyWith(
        isTesting: false,
        lastTestResult: ConnectionStatus.failed,
        lastTestMessage: 'Connection failed: ${e.toString()}',
      );
    }
  }

  /// Clear all settings
  Future<void> clearSettings() async {
    await _prefs.remove(SettingsKeys.apiBaseUrl);
    await _prefs.remove(SettingsKeys.lastSuccessfulConnection);
    await _secureStorage.delete(key: SettingsKeys.apiKey);

    state = const SettingsState(
      lastTestResult: ConnectionStatus.notConfigured,
    );
  }

  /// Get the current API base URL (for use in ApiClient)
  String? get apiBaseUrl => state.apiBaseUrl;

  /// Get the current API key (for use in ApiClient)
  String? get apiKey => state.apiKey;
}

/// Secure storage provider
final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

/// Shared preferences provider
final sharedPreferencesProvider = FutureProvider<SharedPreferences>((ref) async {
  return await SharedPreferences.getInstance();
});

/// Settings controller provider
final settingsControllerProvider =
    StateNotifierProvider<SettingsController, SettingsState>((ref) {
  // Get shared preferences - wait for it to be available
  final prefsAsync = ref.watch(sharedPreferencesProvider);
  final secureStorage = ref.watch(secureStorageProvider);

  return prefsAsync.when(
    data: (prefs) {
      final controller = SettingsController(
        secureStorage: secureStorage,
        prefs: prefs,
      );
      // Load settings on initialization
      controller.loadSettings();
      return controller;
    },
    loading: () {
      // Return a controller with defaults while SharedPreferences loads
      // This is a temporary workaround - in production we'd want a loading state
      throw UnimplementedError('SharedPreferences still loading');
    },
    error: (err, stack) {
      throw Exception('Failed to initialize SharedPreferences: $err');
    },
  );
});

/// Current API base URL provider (for use in ApiClient)
final apiBaseUrlProvider = Provider<String?>((ref) {
  try {
    final settings = ref.watch(settingsControllerProvider);
    return settings.apiBaseUrl ?? 'http://127.0.0.1:8000'; // Fallback updated for iOS Simulator
  } catch (e) {
    // If settings controller isn't ready yet, use the default from ApiConfig
    return 'http://127.0.0.1:8000'; // Default for iOS Simulator compatibility
  }
});

/// Current API key provider (for use in ApiClient)
final apiKeyProvider = Provider<String?>((ref) {
  try {
    final settings = ref.watch(settingsControllerProvider);
    return settings.apiKey;
  } catch (e) {
    // If settings controller isn't ready yet, return null (will use header-based auth)
    return null;
  }
});

/// Authentication Provider
///
/// Session 111 Part 3 - User Authentication
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/auth_state.dart';
import 'settings_provider.dart';

/// Storage keys for authentication
class AuthKeys {
  static const String authToken = 'auth_token';
  static const String userId = 'user_id';
  static const String username = 'username';
  static const String userEmail = 'user_email';
}

/// Auth controller
class AuthController extends StateNotifier<AuthState> {
  final FlutterSecureStorage _secureStorage;
  final String _baseUrl;

  AuthController({
    required FlutterSecureStorage secureStorage,
    required String baseUrl,
  })  : _secureStorage = secureStorage,
        _baseUrl = baseUrl,
        super(const AuthState());

  /// Initialize auth state from storage
  Future<void> initialize() async {
    try {
      final token = await _secureStorage.read(key: AuthKeys.authToken);
      if (token != null && token.isNotEmpty) {
        final userId = await _secureStorage.read(key: AuthKeys.userId);
        final username = await _secureStorage.read(key: AuthKeys.username);
        final email = await _secureStorage.read(key: AuthKeys.userEmail);

        if (userId != null && username != null && email != null) {
          // Verify token is still valid
          final isValid = await _verifyToken(token);
          if (isValid && mounted) {
            state = AuthState(
              isAuthenticated: true,
              token: token,
              user: AuthUser(
                id: userId,
                username: username,
                email: email,
              ),
            );
            return;
          }
        }
      }

      // If we get here, no valid auth found
      if (mounted) {
        state = const AuthState();
      }
    } catch (e) {
      if (mounted) {
        state = AuthState(errorMessage: 'Failed to load auth: ${e.toString()}');
      }
    }
  }

  /// Verify token is still valid
  Future<bool> _verifyToken(String token) async {
    try {
      final url = Uri.parse('$_baseUrl/api/v1/auth/user/');
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Login with username and password
  Future<bool> login({
    required String username,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final url = Uri.parse('$_baseUrl/api/v1/auth/login/');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['token'] as String;
        final userData = data['user'] as Map<String, dynamic>;
        final user = AuthUser.fromJson(userData);

        // Store credentials securely
        await _secureStorage.write(key: AuthKeys.authToken, value: token);
        await _secureStorage.write(key: AuthKeys.userId, value: user.id);
        await _secureStorage.write(key: AuthKeys.username, value: user.username);
        await _secureStorage.write(key: AuthKeys.userEmail, value: user.email);

        state = AuthState(
          isAuthenticated: true,
          isLoading: false,
          token: token,
          user: user,
        );

        return true;
      } else {
        final errorData = json.decode(response.body);
        state = state.copyWith(
          isLoading: false,
          errorMessage: errorData['detail'] ?? 'Login failed',
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Login error: ${e.toString()}',
      );
      return false;
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      // Call backend logout if we have a token
      if (state.token != null) {
        final url = Uri.parse('$_baseUrl/api/v1/auth/logout/');
        await http.post(
          url,
          headers: {
            'Authorization': 'Token ${state.token}',
            'Content-Type': 'application/json',
          },
        ).timeout(const Duration(seconds: 10));
      }
    } catch (e) {
      // Ignore logout errors - we'll clear local state anyway
    } finally {
      // Clear stored credentials
      await _secureStorage.delete(key: AuthKeys.authToken);
      await _secureStorage.delete(key: AuthKeys.userId);
      await _secureStorage.delete(key: AuthKeys.username);
      await _secureStorage.delete(key: AuthKeys.userEmail);

      // Reset state
      state = const AuthState();
    }
  }

  /// Get current auth token (for API requests)
  String? get token => state.token;

  /// Check if user is authenticated
  bool get isAuthenticated => state.isAuthenticated;
}

/// Auth controller provider
final authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  // Get dependencies
  final secureStorage = ref.watch(secureStorageProvider);

  // Get API base URL from settings (or use default)
  String baseUrl = 'http://127.0.0.1:8000';
  try {
    final settings = ref.watch(settingsControllerProvider);
    baseUrl = settings.apiBaseUrl ?? baseUrl;
  } catch (e) {
    // Use default if settings not ready
  }

  final controller = AuthController(
    secureStorage: secureStorage,
    baseUrl: baseUrl,
  );

  // Initialize on creation (scheduled to avoid dispose race condition)
  Future.microtask(() => controller.initialize());

  return controller;
});

/// Secure storage provider (shared with settings)
final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

/// Current auth token provider (for API client)
final authTokenProvider = Provider<String?>((ref) {
  final authState = ref.watch(authControllerProvider);
  return authState.token;
});

/// Is authenticated provider
final isAuthenticatedProvider = Provider<bool>((ref) {
  final authState = ref.watch(authControllerProvider);
  return authState.isAuthenticated;
});

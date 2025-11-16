/// API Client Provider
///
/// Session 111 Part 3 - Unified API Client with Authentication
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api_client.dart';
import 'settings_provider.dart';
import 'auth_provider.dart';

/// Authenticated API client provider
/// Automatically includes auth token and API key from settings
final apiClientProvider = Provider<ApiClient>((ref) {
  // Get base URL and API key from settings
  final baseUrl = ref.watch(apiBaseUrlProvider);
  final apiKey = ref.watch(apiKeyProvider);

  // Get auth token from auth state
  final authToken = ref.watch(authTokenProvider);

  return ApiClient(
    baseUrl: baseUrl,
    apiKey: apiKey,
    authToken: authToken,
  );
});

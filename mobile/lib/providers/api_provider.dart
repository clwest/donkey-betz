/// API Client Providers
///
/// Session 100 Part 13 - Flutter Cockpit
/// Session 102 - Mobile Auth & Connection Settings (Dynamic config integration)
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api_client.dart';
import '../services/api/projects_api.dart';
import '../services/api/boardroom_api.dart';
import '../services/api/coleadership_api.dart';
import '../services/api/leadership_api.dart';
import 'settings_provider.dart';

/// API Client provider (uses settings for dynamic config)
final apiClientProvider = Provider<ApiClient>((ref) {
  final baseUrl = ref.watch(apiBaseUrlProvider);
  final apiKey = ref.watch(apiKeyProvider);
  return ApiClient(baseUrl: baseUrl, apiKey: apiKey);
});

/// Projects API provider
final projectsApiProvider = Provider<ProjectsApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return ProjectsApi(client);
});

/// Boardroom API provider
final boardroomApiProvider = Provider<BoardroomApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return BoardroomApi(client);
});

/// Co-Leadership API provider
final coleadershipApiProvider = Provider<CoLeadershipApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return CoLeadershipApi(client);
});

/// Leadership API provider (Session 104)
final leadershipApiProvider = Provider<LeadershipApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return LeadershipApi(client);
});

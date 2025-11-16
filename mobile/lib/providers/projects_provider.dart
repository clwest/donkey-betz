/// Projects State Provider
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/project.dart';
import '../models/session.dart';
import '../models/image_asset.dart';
import 'api_provider.dart';

/// Projects list provider
final projectsProvider = FutureProvider<List<Project>>((ref) async {
  final api = ref.watch(projectsApiProvider);
  return await api.getProjects();
});

/// Single project provider
final projectProvider = FutureProvider.family<Project, String>((ref, projectId) async {
  final api = ref.watch(projectsApiProvider);
  return await api.getProject(projectId);
});

/// Project sessions provider
final projectSessionsProvider =
    FutureProvider.family<List<AISession>, String>((ref, projectId) async {
  final api = ref.watch(projectsApiProvider);
  return await api.getProjectSessions(projectId);
});

/// Session assets provider
/// Session 101: Project Browser - Mobile Flutter App
final sessionAssetsProvider =
    FutureProvider.family<SessionAssetsResponse, String>((ref, sessionId) async {
  final api = ref.watch(projectsApiProvider);
  return await api.getSessionAssets(sessionId);
});

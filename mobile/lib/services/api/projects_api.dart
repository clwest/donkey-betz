/// Projects API Service
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import '../../core/api_client.dart';
import '../../core/api_config.dart';
import '../../models/project.dart';
import '../../models/session.dart';
import '../../models/image_asset.dart';
import '../../models/video_asset.dart';

class ProjectsApi {
  final ApiClient _client;

  ProjectsApi(this._client);

  /// Get all projects for the current user
  Future<List<Project>> getProjects() async {
    final response = await _client.get(ApiConfig.projectsEndpoint);

    // Handle both formats: with and without 'success' field
    if (response['projects'] != null) {
      final projects = response['projects'] as List;
      return projects.map((p) => Project.fromJson(p)).toList();
    }

    throw ApiException(
      message: 'Invalid response format from projects endpoint',
      details: response,
    );
  }

  /// Get a specific project by ID
  Future<Project> getProject(String projectId) async {
    final response = await _client.get('${ApiConfig.projectsEndpoint}$projectId/');

    // Handle both formats: with and without 'success' field
    if (response['project'] != null) {
      return Project.fromJson(response['project']);
    }

    throw ApiException(
      message: 'Invalid response format from project detail endpoint',
      details: response,
    );
  }

  /// Get all sessions for a specific project
  Future<List<AISession>> getProjectSessions(String projectId) async {
    final response = await _client.get(
      '${ApiConfig.sessionsEndpoint}project/$projectId/',
    );

    if (response['success'] == true && response['sessions'] != null) {
      final sessions = response['sessions'] as List;
      return sessions.map((s) => AISession.fromJson(s)).toList();
    }

    throw ApiException(
      message: 'Invalid response format from project sessions endpoint',
      details: response,
    );
  }

  /// Create a new project
  Future<Project> createProject({
    required String name,
    required String description,
    required String goal,
    String? category,
    List<String>? tags,
  }) async {
    final response = await _client.post(
      '${ApiConfig.projectsEndpoint}create/',
      {
        'name': name,
        'description': description,
        'goal': goal,
        if (category != null) 'category': category,
        if (tags != null) 'tags': tags,
      },
    );

    if (response['success'] == true && response['project'] != null) {
      return Project.fromJson(response['project']);
    }

    throw ApiException(
      message: 'Failed to create project',
      details: response,
    );
  }

  /// Get all assets (images and videos) for a specific session
  /// Session 101: Project Browser - Mobile Flutter App
  Future<SessionAssetsResponse> getSessionAssets(String sessionId) async {
    final response = await _client.get(
      '${ApiConfig.sessionsEndpoint}$sessionId/assets/',
    );

    if (response['success'] == true) {
      return SessionAssetsResponse.fromJson(response);
    }

    throw ApiException(
      message: 'Failed to fetch session assets',
      details: response,
    );
  }
}

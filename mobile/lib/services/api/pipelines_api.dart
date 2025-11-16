/// Session 109: Pipelines API Service
///
/// HTTP client for creative pipeline endpoints:
/// - GET /api/v1/pipelines/templates/ (list available templates)
/// - POST /api/v1/pipelines/runs/ (create pipeline run)
/// - GET /api/v1/pipelines/runs/ (list user's runs)
/// - GET /api/v1/pipelines/runs/<id>/ (get run details with live poll)

import 'package:donkey_os_cockpit/core/api_client.dart';
import 'package:donkey_os_cockpit/core/api_config.dart';
import 'package:donkey_os_cockpit/models/pipeline_template.dart';
import 'package:donkey_os_cockpit/models/pipeline_run.dart';

class PipelinesApi {
  final ApiClient _client;

  PipelinesApi(this._client);

  /// List all available pipeline templates
  ///
  /// GET /api/v1/pipelines/templates/
  ///
  /// Returns: List of active PipelineTemplates
  Future<List<PipelineTemplate>> listTemplates() async {
    final response = await _client.get(
      '${ApiConfig.pipelinesEndpoint}templates/',
    );

    final success = response['success'] as bool?;
    if (success != true) {
      throw ApiException(
        message: response['error']?.toString() ?? 'Unknown error listing templates',
      );
    }

    final templatesData = response['templates'] as List<dynamic>?;
    if (templatesData == null) {
      throw ApiException(
        message: 'Missing templates data in response',
      );
    }

    return templatesData
        .map((json) => PipelineTemplate.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  /// Create a new pipeline run
  ///
  /// POST /api/v1/pipelines/runs/
  ///
  /// Parameters:
  /// - [templateSlug]: Template identifier (e.g., "idea_to_image_set")
  /// - [inputPayload]: Input parameters matching template inputs schema
  /// - [projectId]: Optional project UUID
  /// - [sessionId]: Optional session UUID
  ///
  /// Returns: Created PipelineRun in pending status
  Future<PipelineRun> createRun({
    required String templateSlug,
    required Map<String, dynamic> inputPayload,
    String? projectId,
    String? sessionId,
  }) async {
    final body = {
      'template_slug': templateSlug,
      'input_payload': inputPayload,
      if (projectId != null) 'project_id': projectId,
      if (sessionId != null) 'session_id': sessionId,
    };

    final response = await _client.post(
      '${ApiConfig.pipelinesEndpoint}runs/',
      body,
    );

    final success = response['success'] as bool?;
    if (success != true) {
      throw ApiException(
        message: response['error']?.toString() ?? 'Unknown error creating run',
      );
    }

    final runData = response['run'] as Map<String, dynamic>?;
    if (runData == null) {
      throw ApiException(
        message: 'Missing run data in response',
      );
    }

    return PipelineRun.fromJson(runData);
  }

  /// List user's pipeline runs
  ///
  /// GET /api/v1/pipelines/runs/?status=<status>&limit=<int>&offset=<int>
  ///
  /// Query parameters:
  /// - [status]: Optional filter by status (pending, running, completed, failed)
  /// - [limit]: Max runs to return (default 20, max 100)
  /// - [offset]: Pagination offset (default 0)
  ///
  /// Returns: List of PipelineRuns sorted by created_at desc
  Future<List<PipelineRun>> listRuns({
    String? status,
    int limit = 20,
    int offset = 0,
  }) async {
    // Build query string manually
    final params = <String>[];
    if (status != null) params.add('status=$status');
    params.add('limit=$limit');
    params.add('offset=$offset');
    final queryString = params.join('&');

    final response = await _client.get(
      '${ApiConfig.pipelinesEndpoint}runs/?$queryString',
    );

    final success = response['success'] as bool?;
    if (success != true) {
      throw ApiException(
        message: response['error']?.toString() ?? 'Unknown error listing runs',
      );
    }

    final runsData = response['runs'] as List<dynamic>?;
    if (runsData == null) {
      throw ApiException(
        message: 'Missing runs data in response',
      );
    }

    return runsData
        .map((json) => PipelineRun.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  /// Get pipeline run details by ID
  ///
  /// GET /api/v1/pipelines/runs/<id>/
  ///
  /// Returns complete run details including:
  /// - Full execution log
  /// - Input and output payloads
  /// - Error message (if failed)
  /// - Associated project and session
  Future<PipelineRun> getRun(String runId) async {
    final response = await _client.get(
      '${ApiConfig.pipelinesEndpoint}runs/$runId/',
    );

    final success = response['success'] as bool?;
    if (success != true) {
      throw ApiException(
        message: response['error']?.toString() ?? 'Unknown error getting run',
      );
    }

    final runData = response['run'] as Map<String, dynamic>?;
    if (runData == null) {
      throw ApiException(
        message: 'Missing run data in response',
      );
    }

    return PipelineRun.fromJson(runData);
  }

  /// Poll pipeline run until complete or timeout
  ///
  /// Polls getRun() at [intervalSeconds] until run is complete
  /// or [maxAttempts] is reached.
  ///
  /// Use this for simple blocking UI scenarios. For continuous monitoring,
  /// use the provider with Timer polling instead.
  Future<PipelineRun> pollUntilComplete(
    String runId, {
    int intervalSeconds = 3,
    int maxAttempts = 100,
  }) async {
    int attempts = 0;

    while (attempts < maxAttempts) {
      final run = await getRun(runId);

      if (run.isComplete) {
        return run;
      }

      await Future.delayed(Duration(seconds: intervalSeconds));
      attempts++;
    }

    throw ApiException(
      message: 'Pipeline run polling timeout after ${maxAttempts * intervalSeconds}s',
    );
  }
}

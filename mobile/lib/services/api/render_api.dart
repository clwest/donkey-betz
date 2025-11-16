/// Session 105: Render API Service
///
/// HTTP client for render job endpoints:
/// - POST /api/v1/render-jobs/create/ (create job)
/// - GET /api/v1/render-jobs/<id>/ (get job with live poll)
/// - GET /api/v1/render-jobs/ (list jobs)

import 'package:donkey_os_cockpit/core/api_client.dart';
import 'package:donkey_os_cockpit/core/api_config.dart';
import 'package:donkey_os_cockpit/models/render_job.dart';

class RenderApi {
  final ApiClient _client;

  RenderApi(this._client);

  /// Create a new render job
  ///
  /// POST /api/v1/render-jobs/create/
  ///
  /// Parameters:
  /// - [sessionId]: Session UUID (required for media collection)
  /// - [projectId]: Optional project UUID
  /// - [timelineName]: Optional timeline name (default: "Timeline 1")
  /// - [template]: Render template (default: "default_mp4")
  ///
  /// Returns: Created RenderJob
  Future<RenderJob> createRenderJob({
    required String sessionId,
    String? projectId,
    String? timelineName,
    String? template,
  }) async {
    final body = {
      'session_id': sessionId,
      if (projectId != null) 'project_id': projectId,
      if (timelineName != null) 'timeline_name': timelineName,
      if (template != null) 'template': template,
    };

    final response = await _client.post(
      '${ApiConfig.renderJobsEndpoint}create/',
      body,
    );

    // Backend returns RenderJob directly in response
    return RenderJob.fromJson(response);
  }

  /// Get render job by ID (with live polling from Resolve Node)
  ///
  /// GET /api/v1/render-jobs/<id>/
  ///
  /// If job is active, backend will poll Resolve Node for latest status
  /// before returning. This keeps the mobile client simple.
  Future<RenderJob> getRenderJob(String jobId) async {
    final response = await _client.get(
      '${ApiConfig.renderJobsEndpoint}$jobId/',
    );

    return RenderJob.fromJson(response);
  }

  /// List user's render jobs
  ///
  /// GET /api/v1/render-jobs/?project_id=<uuid>&limit=<int>
  ///
  /// Query parameters:
  /// - [projectId]: Optional filter by project
  /// - [limit]: Max jobs to return (default 20)
  ///
  /// Returns: List of RenderJobs sorted by created_at desc
  Future<List<RenderJob>> listRenderJobs({
    String? projectId,
    int limit = 20,
  }) async {
    // Build query string manually
    final params = <String>[];
    if (projectId != null) params.add('project_id=$projectId');
    params.add('limit=$limit');
    final queryString = params.join('&');

    final response = await _client.get(
      '${ApiConfig.renderJobsEndpoint}?$queryString',
    );

    final success = response['success'] as bool?;
    if (success != true) {
      throw ApiException(
        message: response['error']?.toString() ?? 'Unknown error listing render jobs',
      );
    }

    final jobsData = response['jobs'] as List<dynamic>?;
    if (jobsData == null) {
      throw ApiException(
        message: 'Missing jobs data in response',
      );
    }

    return jobsData
        .map((json) => RenderJob.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  /// Poll render job until complete or timeout
  ///
  /// Polls getRenderJob() at [intervalSeconds] until job is complete
  /// or [maxAttempts] is reached.
  ///
  /// Use this for simple blocking UI scenarios. For continuous monitoring,
  /// use the provider with Timer polling instead.
  Future<RenderJob> pollUntilComplete(
    String jobId, {
    int intervalSeconds = 3,
    int maxAttempts = 100,
  }) async {
    int attempts = 0;

    while (attempts < maxAttempts) {
      final job = await getRenderJob(jobId);

      if (job.isComplete) {
        return job;
      }

      await Future.delayed(Duration(seconds: intervalSeconds));
      attempts++;
    }

    throw ApiException(
      message: 'Render job polling timeout after ${maxAttempts * intervalSeconds}s',
    );
  }
}

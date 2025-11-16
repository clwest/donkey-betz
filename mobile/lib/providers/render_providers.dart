/// Session 105: Render Job Providers
///
/// Riverpod providers for render job state management.
/// Includes service provider and state notifier for job tracking.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/models/render_job.dart';
import 'package:donkey_os_cockpit/providers/api_provider.dart';
import 'package:donkey_os_cockpit/services/api/render_api.dart';

/// Provider for RenderApi service
final renderApiProvider = Provider<RenderApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return RenderApi(apiClient);
});

/// State for a single render job being tracked
class RenderJobState {
  final RenderJob? job;
  final bool isLoading;
  final String? error;

  const RenderJobState({
    this.job,
    this.isLoading = false,
    this.error,
  });

  RenderJobState copyWith({
    RenderJob? job,
    bool? isLoading,
    String? error,
  }) {
    return RenderJobState(
      job: job ?? this.job,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// Notifier for tracking a single render job with live polling
class RenderJobNotifier extends StateNotifier<RenderJobState> {
  final RenderApi _api;
  final String jobId;

  RenderJobNotifier(this._api, this.jobId)
      : super(const RenderJobState(isLoading: true));

  /// Fetch job status from backend (which polls Resolve Node)
  Future<void> fetchStatus() async {
    try {
      final job = await _api.getRenderJob(jobId);
      state = RenderJobState(job: job, isLoading: false);
    } catch (e) {
      state = RenderJobState(
        job: state.job, // Keep old job if we had one
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Poll job status every [intervalSeconds] until complete
  ///
  /// This is a simple timer-based polling implementation.
  /// For production, consider using WebSocket updates instead.
  Stream<RenderJob> pollUntilComplete({int intervalSeconds = 3}) async* {
    while (true) {
      await fetchStatus();

      if (state.job != null) {
        yield state.job!;

        if (state.job!.isComplete) {
          break; // Job is done or errored
        }
      }

      if (state.error != null) {
        throw Exception(state.error);
      }

      await Future.delayed(Duration(seconds: intervalSeconds));
    }
  }
}

/// Provider family for tracking individual render jobs
final renderJobProvider =
    StateNotifierProvider.family<RenderJobNotifier, RenderJobState, String>(
  (ref, jobId) {
    final api = ref.watch(renderApiProvider);
    return RenderJobNotifier(api, jobId);
  },
);

/// State for render job list
class RenderJobListState {
  final List<RenderJob> jobs;
  final bool isLoading;
  final String? error;

  const RenderJobListState({
    this.jobs = const [],
    this.isLoading = false,
    this.error,
  });

  RenderJobListState copyWith({
    List<RenderJob>? jobs,
    bool? isLoading,
    String? error,
  }) {
    return RenderJobListState(
      jobs: jobs ?? this.jobs,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// Notifier for managing list of render jobs
class RenderJobListNotifier extends StateNotifier<RenderJobListState> {
  final RenderApi _api;

  RenderJobListNotifier(this._api) : super(const RenderJobListState());

  /// Fetch list of render jobs
  Future<void> fetchJobs({String? projectId, int limit = 20}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final jobs = await _api.listRenderJobs(
        projectId: projectId,
        limit: limit,
      );
      state = RenderJobListState(jobs: jobs, isLoading: false);
    } catch (e) {
      state = RenderJobListState(
        jobs: state.jobs, // Keep old jobs
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Refresh job list
  Future<void> refresh({String? projectId}) async {
    await fetchJobs(projectId: projectId);
  }
}

/// Provider for render job list
final renderJobListProvider =
    StateNotifierProvider<RenderJobListNotifier, RenderJobListState>(
  (ref) {
    final api = ref.watch(renderApiProvider);
    return RenderJobListNotifier(api);
  },
);

/// Helper to create a new render job
final createRenderJobProvider = Provider<
    Future<RenderJob> Function({
  required String sessionId,
  String? projectId,
  String? timelineName,
  String? template,
})>((ref) {
  final api = ref.watch(renderApiProvider);
  return ({
    required String sessionId,
    String? projectId,
    String? timelineName,
    String? template,
  }) =>
      api.createRenderJob(
        sessionId: sessionId,
        projectId: projectId,
        timelineName: timelineName,
        template: template,
      );
});

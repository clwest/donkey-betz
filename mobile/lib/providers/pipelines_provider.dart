/// Session 109: Pipeline Providers
///
/// Riverpod providers for creative pipeline state management.
/// Includes providers for templates, runs, and state tracking.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/models/pipeline_template.dart';
import 'package:donkey_os_cockpit/models/pipeline_run.dart';
import 'package:donkey_os_cockpit/providers/api_provider.dart';
import 'package:donkey_os_cockpit/services/api/pipelines_api.dart';

/// Provider for PipelinesApi service
final pipelinesApiProvider = Provider<PipelinesApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return PipelinesApi(apiClient);
});

// ============================================================================
// PIPELINE TEMPLATES
// ============================================================================

/// State for pipeline template list
class PipelineTemplatesState {
  final List<PipelineTemplate> templates;
  final bool isLoading;
  final String? error;

  const PipelineTemplatesState({
    this.templates = const [],
    this.isLoading = false,
    this.error,
  });

  PipelineTemplatesState copyWith({
    List<PipelineTemplate>? templates,
    bool? isLoading,
    String? error,
  }) {
    return PipelineTemplatesState(
      templates: templates ?? this.templates,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// Notifier for managing pipeline templates
class PipelineTemplatesNotifier extends StateNotifier<PipelineTemplatesState> {
  final PipelinesApi _api;

  PipelineTemplatesNotifier(this._api) : super(const PipelineTemplatesState());

  /// Fetch list of available templates
  Future<void> fetchTemplates() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final templates = await _api.listTemplates();
      state = PipelineTemplatesState(templates: templates, isLoading: false);
    } catch (e) {
      state = PipelineTemplatesState(
        templates: state.templates, // Keep old templates
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Refresh template list
  Future<void> refresh() async {
    await fetchTemplates();
  }
}

/// Provider for pipeline template list
final pipelineTemplatesProvider =
    StateNotifierProvider<PipelineTemplatesNotifier, PipelineTemplatesState>(
  (ref) {
    final api = ref.watch(pipelinesApiProvider);
    final notifier = PipelineTemplatesNotifier(api);
    // Auto-fetch on creation
    notifier.fetchTemplates();
    return notifier;
  },
);

// ============================================================================
// PIPELINE RUNS - INDIVIDUAL RUN TRACKING
// ============================================================================

/// State for a single pipeline run being tracked
class PipelineRunState {
  final PipelineRun? run;
  final bool isLoading;
  final String? error;

  const PipelineRunState({
    this.run,
    this.isLoading = false,
    this.error,
  });

  PipelineRunState copyWith({
    PipelineRun? run,
    bool? isLoading,
    String? error,
  }) {
    return PipelineRunState(
      run: run ?? this.run,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// Notifier for tracking a single pipeline run with live polling
class PipelineRunNotifier extends StateNotifier<PipelineRunState> {
  final PipelinesApi _api;
  final String runId;

  PipelineRunNotifier(this._api, this.runId)
      : super(const PipelineRunState(isLoading: true));

  /// Fetch run status from backend
  Future<void> fetchStatus() async {
    try {
      final run = await _api.getRun(runId);
      state = PipelineRunState(run: run, isLoading: false);
    } catch (e) {
      state = PipelineRunState(
        run: state.run, // Keep old run if we had one
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Poll run status every [intervalSeconds] until complete
  ///
  /// This is a simple timer-based polling implementation.
  /// For production, consider using WebSocket updates instead.
  Stream<PipelineRun> pollUntilComplete({int intervalSeconds = 3}) async* {
    while (true) {
      await fetchStatus();

      if (state.run != null) {
        yield state.run!;

        if (state.run!.isComplete) {
          break; // Run is done or failed
        }
      }

      if (state.error != null) {
        throw Exception(state.error);
      }

      await Future.delayed(Duration(seconds: intervalSeconds));
    }
  }
}

/// Provider family for tracking individual pipeline runs
final pipelineRunProvider =
    StateNotifierProvider.family<PipelineRunNotifier, PipelineRunState, String>(
  (ref, runId) {
    final api = ref.watch(pipelinesApiProvider);
    return PipelineRunNotifier(api, runId);
  },
);

// ============================================================================
// PIPELINE RUNS - LIST MANAGEMENT
// ============================================================================

/// State for pipeline run list
class PipelineRunListState {
  final List<PipelineRun> runs;
  final bool isLoading;
  final String? error;

  const PipelineRunListState({
    this.runs = const [],
    this.isLoading = false,
    this.error,
  });

  PipelineRunListState copyWith({
    List<PipelineRun>? runs,
    bool? isLoading,
    String? error,
  }) {
    return PipelineRunListState(
      runs: runs ?? this.runs,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// Notifier for managing list of pipeline runs
class PipelineRunListNotifier extends StateNotifier<PipelineRunListState> {
  final PipelinesApi _api;

  PipelineRunListNotifier(this._api) : super(const PipelineRunListState());

  /// Fetch list of pipeline runs
  Future<void> fetchRuns({
    String? status,
    int limit = 20,
    int offset = 0,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final runs = await _api.listRuns(
        status: status,
        limit: limit,
        offset: offset,
      );
      state = PipelineRunListState(runs: runs, isLoading: false);
    } catch (e) {
      state = PipelineRunListState(
        runs: state.runs, // Keep old runs
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Refresh run list
  Future<void> refresh({String? status}) async {
    await fetchRuns(status: status);
  }
}

/// Provider for pipeline run list
final pipelineRunListProvider =
    StateNotifierProvider<PipelineRunListNotifier, PipelineRunListState>(
  (ref) {
    final api = ref.watch(pipelinesApiProvider);
    return PipelineRunListNotifier(api);
  },
);

// ============================================================================
// HELPER PROVIDERS
// ============================================================================

/// Helper to create a new pipeline run
final createPipelineRunProvider = Provider<
    Future<PipelineRun> Function({
  required String templateSlug,
  required Map<String, dynamic> inputPayload,
  String? projectId,
  String? sessionId,
})>((ref) {
  final api = ref.watch(pipelinesApiProvider);
  return ({
    required String templateSlug,
    required Map<String, dynamic> inputPayload,
    String? projectId,
    String? sessionId,
  }) =>
      api.createRun(
        templateSlug: templateSlug,
        inputPayload: inputPayload,
        projectId: projectId,
        sessionId: sessionId,
      );
});

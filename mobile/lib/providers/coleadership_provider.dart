/// Co-Leadership State Provider
///
/// Session 100 Part 13 - Flutter Cockpit
/// Session 108 - Extended with list/detail/preferences providers
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/coleadership.dart';
import '../core/api_client.dart';
import '../services/api/coleadership_api.dart';
import 'api_provider.dart';

/// Decision commit state
class DecisionCommitState {
  final bool isLoading;
  final bool isSuccess;
  final String? error;

  DecisionCommitState({
    this.isLoading = false,
    this.isSuccess = false,
    this.error,
  });

  DecisionCommitState copyWith({
    bool? isLoading,
    bool? isSuccess,
    String? error,
  }) {
    return DecisionCommitState(
      isLoading: isLoading ?? this.isLoading,
      isSuccess: isSuccess ?? this.isSuccess,
      error: error,
    );
  }
}

/// Decision commit controller
class DecisionCommitController extends StateNotifier<DecisionCommitState> {
  final CoLeadershipApi _api;

  DecisionCommitController(this._api) : super(DecisionCommitState());

  /// Commit a human decision
  Future<void> commitDecision({
    required String decisionId,
    required String chosenPathSummary,
    String justification = '',
    bool isOverride = false,
    String? overriddenAgentId,
  }) async {
    state = state.copyWith(isLoading: true, error: null, isSuccess: false);

    try {
      await _api.commitDecision(
        decisionId: decisionId,
        chosenPathSummary: chosenPathSummary,
        justification: justification,
        isOverride: isOverride,
        overriddenAgentId: overriddenAgentId,
      );

      state = state.copyWith(
        isLoading: false,
        isSuccess: true,
      );
    } on ApiException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.userMessage,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to commit decision: ${e.toString()}',
      );
    }
  }

  void reset() {
    state = DecisionCommitState();
  }
}

/// Outcome log state
class OutcomeLogState {
  final bool isLoading;
  final bool isSuccess;
  final String? error;
  final String? toldYouSoMessage;

  OutcomeLogState({
    this.isLoading = false,
    this.isSuccess = false,
    this.error,
    this.toldYouSoMessage,
  });

  OutcomeLogState copyWith({
    bool? isLoading,
    bool? isSuccess,
    String? error,
    String? toldYouSoMessage,
  }) {
    return OutcomeLogState(
      isLoading: isLoading ?? this.isLoading,
      isSuccess: isSuccess ?? this.isSuccess,
      error: error,
      toldYouSoMessage: toldYouSoMessage ?? this.toldYouSoMessage,
    );
  }
}

/// Outcome log controller
class OutcomeLogController extends StateNotifier<OutcomeLogState> {
  final CoLeadershipApi _api;

  OutcomeLogController(this._api) : super(OutcomeLogState());

  /// Log an outcome
  Future<void> logOutcome({
    required String decisionId,
    required String status,
    required String outcomeSummary,
    required String attribution,
    Map<String, dynamic>? metrics,
  }) async {
    state = state.copyWith(isLoading: true, error: null, isSuccess: false);

    try {
      final response = await _api.logOutcome(
        decisionId: decisionId,
        status: status,
        outcomeSummary: outcomeSummary,
        attribution: attribution,
        metrics: metrics,
      );

      state = state.copyWith(
        isLoading: false,
        isSuccess: true,
        toldYouSoMessage: response['told_you_so_message'],
      );
    } on ApiException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.userMessage,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to log outcome: ${e.toString()}',
      );
    }
  }

  void reset() {
    state = OutcomeLogState();
  }
}

/// Decision commit controller provider
final decisionCommitControllerProvider =
    StateNotifierProvider<DecisionCommitController, DecisionCommitState>((ref) {
  final api = ref.watch(coleadershipApiProvider);
  return DecisionCommitController(api);
});

/// Outcome log controller provider
final outcomeLogControllerProvider =
    StateNotifierProvider<OutcomeLogController, OutcomeLogState>((ref) {
  final api = ref.watch(coleadershipApiProvider);
  return OutcomeLogController(api);
});

/// Leadership stats provider
final leadershipStatsProvider = FutureProvider<LeadershipStats>((ref) async {
  final api = ref.watch(coleadershipApiProvider);
  return await api.getStats();
});

/// Project decisions provider
final projectDecisionsProvider =
    FutureProvider.family<List<CoLeadershipDecision>, String>((ref, projectId) async {
  final api = ref.watch(coleadershipApiProvider);
  return await api.getProjectDecisions(projectId);
});

/// All decisions list provider (Session 108)
final decisionsListProvider = FutureProvider<List<CoLeadershipDecision>>((ref) async {
  final api = ref.watch(coleadershipApiProvider);
  return await api.listDecisions(limit: 20, offset: 0);
});

/// Decision detail provider (Session 108)
final decisionDetailProvider =
    FutureProvider.family<CoLeadershipDecisionDetail, String>((ref, decisionId) async {
  final api = ref.watch(coleadershipApiProvider);
  return await api.getDecisionDetail(decisionId);
});

/// Co-Leadership preferences provider (Session 108)
final coLeadershipPreferencesProvider = FutureProvider<CoLeadershipPreferences>((ref) async {
  final api = ref.watch(coleadershipApiProvider);
  return await api.getPreferences();
});

/// Update preferences function provider (Session 108)
final updatePreferencesProvider = Provider<Future<CoLeadershipPreferences> Function({
  required bool allowToldYouSo,
  required String tone,
})>((ref) {
  final api = ref.watch(coleadershipApiProvider);
  return ({required bool allowToldYouSo, required String tone}) async {
    final prefs = await api.updatePreferences(
      allowToldYouSo: allowToldYouSo,
      tone: tone,
    );
    // Invalidate the preferences provider to force a refresh
    ref.invalidate(coLeadershipPreferencesProvider);
    return prefs;
  };
});

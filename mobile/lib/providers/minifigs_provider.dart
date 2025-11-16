/// Session 111: MiniFigs Providers
///
/// Riverpod providers for mini-fig asset state management.
/// Includes providers for list and detail views.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/models/minifig_asset.dart';
import 'package:donkey_os_cockpit/providers/api_provider.dart';
import 'package:donkey_os_cockpit/services/api/minifigs_api.dart';

/// Provider for MiniFigsApi service
final minifigsApiProvider = Provider<MiniFigsApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return MiniFigsApi(apiClient);
});

// ============================================================================
// MINIFIGS LIST MANAGEMENT
// ============================================================================

/// State for mini-fig asset list
class MiniFigsListState {
  final List<MiniFigAsset> minifigs;
  final bool isLoading;
  final String? error;

  const MiniFigsListState({
    this.minifigs = const [],
    this.isLoading = false,
    this.error,
  });

  MiniFigsListState copyWith({
    List<MiniFigAsset>? minifigs,
    bool? isLoading,
    String? error,
  }) {
    return MiniFigsListState(
      minifigs: minifigs ?? this.minifigs,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// Notifier for managing list of mini-figs
class MiniFigsListNotifier extends StateNotifier<MiniFigsListState> {
  final MiniFigsApi _api;

  MiniFigsListNotifier(this._api) : super(const MiniFigsListState());

  /// Fetch list of mini-figs
  Future<void> fetchMiniFigs({
    String? status,
    int limit = 20,
    int offset = 0,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final minifigs = await _api.listMiniFigs(
        status: status,
        limit: limit,
        offset: offset,
      );
      state = MiniFigsListState(minifigs: minifigs, isLoading: false);
    } catch (e) {
      state = MiniFigsListState(
        minifigs: state.minifigs, // Keep old minifigs
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Refresh mini-fig list
  Future<void> refresh({String? status}) async {
    await fetchMiniFigs(status: status);
  }

  /// Filter by status
  List<MiniFigAsset> filterByStatus(MiniFigStatus status) {
    return state.minifigs.where((mf) => mf.status == status).toList();
  }

  /// Get completed mini-figs
  List<MiniFigAsset> get completed =>
      filterByStatus(MiniFigStatus.completed);

  /// Get processing mini-figs
  List<MiniFigAsset> get processing =>
      state.minifigs.where((mf) => mf.isProcessing).toList();

  /// Get failed mini-figs
  List<MiniFigAsset> get failed =>
      filterByStatus(MiniFigStatus.failed);
}

/// Provider for mini-fig list
final minifigsListProvider =
    StateNotifierProvider<MiniFigsListNotifier, MiniFigsListState>(
  (ref) {
    final api = ref.watch(minifigsApiProvider);
    final notifier = MiniFigsListNotifier(api);
    // Auto-fetch on creation
    notifier.fetchMiniFigs();
    return notifier;
  },
);

// ============================================================================
// MINIFIG DETAIL - INDIVIDUAL ASSET TRACKING
// ============================================================================

/// State for a single mini-fig asset
class MiniFigDetailState {
  final MiniFigAsset? minifig;
  final bool isLoading;
  final String? error;

  const MiniFigDetailState({
    this.minifig,
    this.isLoading = false,
    this.error,
  });

  MiniFigDetailState copyWith({
    MiniFigAsset? minifig,
    bool? isLoading,
    String? error,
  }) {
    return MiniFigDetailState(
      minifig: minifig ?? this.minifig,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// Notifier for tracking a single mini-fig asset
class MiniFigDetailNotifier extends StateNotifier<MiniFigDetailState> {
  final MiniFigsApi _api;
  final String minifigId;

  MiniFigDetailNotifier(this._api, this.minifigId)
      : super(const MiniFigDetailState(isLoading: true));

  /// Fetch mini-fig details from backend
  Future<void> fetchDetails() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final minifig = await _api.getMiniFig(minifigId);
      state = MiniFigDetailState(minifig: minifig, isLoading: false);
    } catch (e) {
      state = MiniFigDetailState(
        minifig: state.minifig, // Keep old data if we had it
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Refresh mini-fig details
  Future<void> refresh() async {
    await fetchDetails();
  }
}

/// Provider family for tracking individual mini-figs
final minifigDetailProvider =
    StateNotifierProvider.family<MiniFigDetailNotifier, MiniFigDetailState, String>(
  (ref, minifigId) {
    final api = ref.watch(minifigsApiProvider);
    final notifier = MiniFigDetailNotifier(api, minifigId);
    // Auto-fetch on creation
    notifier.fetchDetails();
    return notifier;
  },
);

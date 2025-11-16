/// Boardroom State Provider
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/boardroom_meeting.dart';
import '../core/api_client.dart';
import '../services/api/boardroom_api.dart';
import 'api_provider.dart';

/// Boardroom state
class BoardroomState {
  final bool isLoading;
  final BoardroomMeetingResult? result;
  final String? error;

  BoardroomState({
    this.isLoading = false,
    this.result,
    this.error,
  });

  BoardroomState copyWith({
    bool? isLoading,
    BoardroomMeetingResult? result,
    String? error,
  }) {
    return BoardroomState(
      isLoading: isLoading ?? this.isLoading,
      result: result ?? this.result,
      error: error,
    );
  }
}

/// Boardroom controller
class BoardroomController extends StateNotifier<BoardroomState> {
  final BoardroomApi _api;

  BoardroomController(this._api) : super(BoardroomState());

  /// Start a new executive meeting
  Future<void> startMeeting({
    required String topic,
    String? projectId,
    required List<String> participants,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await _api.startMeeting(
        topic: topic,
        projectId: projectId,
        participants: participants,
      );

      state = state.copyWith(
        isLoading: false,
        result: result,
      );
    } on ApiException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.userMessage,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to start meeting: ${e.toString()}',
      );
    }
  }

  /// Clear the current result
  void clearResult() {
    state = BoardroomState();
  }
}

/// Boardroom controller provider
final boardroomControllerProvider =
    StateNotifierProvider<BoardroomController, BoardroomState>((ref) {
  final api = ref.watch(boardroomApiProvider);
  return BoardroomController(api);
});

/// Meetings list provider
final meetingsListProvider =
    FutureProvider<List<BoardroomMeetingSummary>>((ref) async {
  final api = ref.watch(boardroomApiProvider);
  return await api.listMeetings();
});

/// Meeting details provider
final meetingDetailsProvider =
    FutureProvider.family<BoardroomMeetingDetail, String>((ref, meetingKey) async {
  final api = ref.watch(boardroomApiProvider);
  return await api.getMeetingDetails(meetingKey);
});

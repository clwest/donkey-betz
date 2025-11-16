/// Boardroom API Service
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import '../../core/api_client.dart';
import '../../core/api_config.dart';
import '../../models/boardroom_meeting.dart';

class BoardroomApi {
  final ApiClient _client;

  BoardroomApi(this._client);

  /// Start a new executive boardroom meeting
  Future<BoardroomMeetingResult> startMeeting({
    required String topic,
    String? projectId,
    required List<String> participants,
  }) async {
    final response = await _client.post(
      '${ApiConfig.boardroomEndpoint}start/',
      {
        'topic': topic,
        if (projectId != null) 'project_id': projectId,
        'participants': participants,
      },
    );

    if (response['success'] == true) {
      return BoardroomMeetingResult.fromJson(response);
    }

    throw ApiException(
      message: response['error'] ?? 'Failed to start meeting',
      details: response,
    );
  }

  /// List all meetings for the current user
  Future<List<BoardroomMeetingSummary>> listMeetings() async {
    final response = await _client.get('${ApiConfig.leadershipEndpoint}meetings/');

    if (response['success'] == true && response['meetings'] != null) {
      final meetings = response['meetings'] as List;
      return meetings
          .map((m) => BoardroomMeetingSummary.fromJson(m))
          .toList();
    }

    throw ApiException(
      message: 'Invalid response format from meetings list endpoint',
      details: response,
    );
  }

  /// Get full details of a specific meeting
  Future<BoardroomMeetingDetail> getMeetingDetails(String meetingKey) async {
    final response = await _client.get(
      '${ApiConfig.leadershipEndpoint}meetings/$meetingKey/',
    );

    if (response['success'] == true && response['meeting'] != null) {
      return BoardroomMeetingDetail.fromJson(response['meeting']);
    }

    throw ApiException(
      message: 'Invalid response format from meeting details endpoint',
      details: response,
    );
  }
}

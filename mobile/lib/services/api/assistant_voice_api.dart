/// Personal Assistant Voice API Client
///
/// Session 113: Voice Input MVP
library;

import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../core/api_client.dart' show ApiException;
import '../../models/assistant_voice.dart';

class AssistantVoiceApi {
  final String baseUrl;
  final String apiKey;

  AssistantVoiceApi({
    required this.baseUrl,
    required this.apiKey,
  });

  /// Send voice recording to backend for transcription + assistant response
  ///
  /// [filePath] - Path to the audio file (webm/m4a/wav)
  /// [sessionId] - Optional session ID for conversation threading
  ///
  /// Returns [AssistantVoiceResult] with transcribed text and assistant response
  Future<AssistantVoiceResult> sendVoice({
    required String filePath,
    String? sessionId,
  }) async {
    try {
      // Prepare multipart request
      final uri = Uri.parse('$baseUrl/api/assistant/voice/');
      final request = http.MultipartRequest('POST', uri);

      // Add headers
      request.headers['X-API-Key'] = apiKey;

      // Add audio file
      final audioFile = File(filePath);
      if (!await audioFile.exists()) {
        throw ApiException(
          message: 'Audio file not found',
          details: {'path': filePath},
        );
      }

      final multipartFile = await http.MultipartFile.fromPath(
        'audio',
        filePath,
        filename: 'recording.webm',
      );
      request.files.add(multipartFile);

      // Add optional session ID
      if (sessionId != null) {
        request.fields['session_id'] = sessionId;
      }

      // Send request
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      // Parse response
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);

        // Check if backend returned success
        if (data['success'] == true) {
          // Extract assistant_message from response
          final assistantMessageData = data['assistant_message'] as Map<String, dynamic>;

          return AssistantVoiceResult(
            success: true,
            userText: data['user_text'] as String,
            assistantMessage: AssistantMessageData.fromJson(assistantMessageData),
          );
        } else {
          throw ApiException(
            message: data['error'] as String? ?? 'Voice processing failed',
            details: data,
          );
        }
      } else {
        final Map<String, dynamic>? errorData =
            response.body.isNotEmpty ? json.decode(response.body) : null;

        throw ApiException(
          message: errorData?['error'] as String? ?? 'Failed to process voice input',
          details: errorData ?? {'statusCode': response.statusCode},
        );
      }
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(
        message: 'Failed to send voice recording',
        details: {'error': e.toString()},
      );
    }
  }
}

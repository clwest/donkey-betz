/// HTTP API Client for DonkeyOS Backend
///
/// Session 100 Part 13 - Flutter Cockpit
/// Session 102 - Mobile Auth & Connection Settings (Dynamic config + API key auth)
/// Provides authenticated HTTP requests with error handling
library;

import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'api_config.dart';

/// Exception thrown when API request fails
class ApiException implements Exception {
  final int? statusCode;
  final String message;
  final dynamic details;

  ApiException({
    this.statusCode,
    required this.message,
    this.details,
  });

  @override
  String toString() {
    if (statusCode != null) {
      return 'ApiException($statusCode): $message';
    }
    return 'ApiException: $message';
  }

  /// User-friendly error message
  String get userMessage {
    if (statusCode == 400) {
      return 'Invalid request. Please check your input.';
    } else if (statusCode == 401) {
      return 'Authentication required. Please check your API key.';
    } else if (statusCode == 403) {
      return 'Access denied. Invalid API key.';
    } else if (statusCode == 404) {
      return 'Resource not found.';
    } else if (statusCode == 500) {
      return 'Server error. Please try again later.';
    } else if (statusCode != null && statusCode! >= 500) {
      return 'Server error. Please try again later.';
    }
    return message;
  }
}

/// HTTP Client for DonkeyOS API
class ApiClient {
  final String _baseUrl;
  final String? _apiKey;
  final String? _authToken;
  final http.Client _httpClient;

  ApiClient({
    String? baseUrl,
    String? apiKey,
    String? authToken,
    http.Client? httpClient,
  })  : _baseUrl = baseUrl ?? ApiConfig.defaultBaseUrl,
        _apiKey = apiKey,
        _authToken = authToken,
        _httpClient = httpClient ?? http.Client();

  /// Request headers with authentication
  /// Session 115: Use Authorization header for DRF compatibility
  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        // Always use Authorization header (DRF standard)
        if (_authToken != null) 'Authorization': 'Token $_authToken',
        if (_apiKey != null) 'Authorization': 'Token $_apiKey',
      };

  /// GET request
  Future<Map<String, dynamic>> get(String endpoint) async {
    try {
      final url = Uri.parse('$_baseUrl$endpoint');
      final response = await _httpClient
          .get(url, headers: _headers)
          .timeout(ApiConfig.receiveTimeout);

      return _handleResponse(response);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        details: e,
      );
    }
  }

  /// POST request
  Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    try {
      final url = Uri.parse('$_baseUrl$endpoint');
      final response = await _httpClient
          .post(
            url,
            headers: _headers,
            body: json.encode(body),
          )
          .timeout(ApiConfig.receiveTimeout);

      return _handleResponse(response);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        details: e,
      );
    }
  }

  /// PUT request
  Future<Map<String, dynamic>> put(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    try {
      final url = Uri.parse('$_baseUrl$endpoint');
      final response = await _httpClient
          .put(
            url,
            headers: _headers,
            body: json.encode(body),
          )
          .timeout(ApiConfig.receiveTimeout);

      return _handleResponse(response);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        details: e,
      );
    }
  }

  /// DELETE request
  Future<Map<String, dynamic>> delete(String endpoint) async {
    try {
      final url = Uri.parse('$_baseUrl$endpoint');
      final response = await _httpClient
          .delete(url, headers: _headers)
          .timeout(ApiConfig.receiveTimeout);

      return _handleResponse(response);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        details: e,
      );
    }
  }

  /// POST request with multipart file upload
  /// Session 115: For image/video file uploads to Stability AI endpoints
  /// Supports both file paths (mobile) and bytes (web)
  Future<Map<String, dynamic>> postMultipart(
    String endpoint, {
    Map<String, String>? fields,
    Map<String, String>? files, // file field name -> file path (mobile)
    Map<String, Uint8List>? fileBytes, // file field name -> bytes (web)
    String? fileName, // filename for bytes upload
  }) async {
    try {
      final url = Uri.parse('$_baseUrl$endpoint');
      final request = http.MultipartRequest('POST', url);

      // Add authentication headers
      if (_authToken != null) {
        request.headers['Authorization'] = 'Token $_authToken';
      } else if (_apiKey != null) {
        request.headers['Authorization'] = 'Token $_apiKey';
      }

      // Add form fields
      if (fields != null) {
        request.fields.addAll(fields);
      }

      // Add files from path (mobile)
      if (files != null) {
        for (final entry in files.entries) {
          final file = await http.MultipartFile.fromPath(
            entry.key,
            entry.value,
          );
          request.files.add(file);
        }
      }

      // Add files from bytes (web)
      if (fileBytes != null) {
        for (final entry in fileBytes.entries) {
          final file = http.MultipartFile.fromBytes(
            entry.key,
            entry.value,
            filename: fileName ?? 'upload.jpg',
          );
          request.files.add(file);
        }
      }

      // Send request
      final streamedResponse =
          await request.send().timeout(ApiConfig.receiveTimeout);
      final response = await http.Response.fromStream(streamedResponse);

      return _handleResponse(response);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Network error: ${e.toString()}',
        details: e,
      );
    }
  }

  /// Handle HTTP response
  Map<String, dynamic> _handleResponse(http.Response response) {
    final statusCode = response.statusCode;

    // Success (2xx)
    if (statusCode >= 200 && statusCode < 300) {
      if (response.body.isEmpty) {
        return {'success': true};
      }

      try {
        final data = json.decode(response.body) as Map<String, dynamic>;
        return data;
      } catch (e) {
        throw ApiException(
          statusCode: statusCode,
          message: 'Failed to parse response',
          details: e,
        );
      }
    }

    // Error response
    String errorMessage = 'Request failed with status $statusCode';
    dynamic errorDetails;

    if (response.body.isNotEmpty) {
      try {
        final errorData = json.decode(response.body);
        if (errorData is Map<String, dynamic>) {
          errorMessage = errorData['error'] ??
              errorData['message'] ??
              errorData['detail'] ??
              errorMessage;
          errorDetails = errorData;
        }
      } catch (_) {
        errorMessage = response.body;
      }
    }

    throw ApiException(
      statusCode: statusCode,
      message: errorMessage,
      details: errorDetails,
    );
  }

  /// Close the HTTP client
  void dispose() {
    _httpClient.close();
  }
}

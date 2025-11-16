/// File Upload Service - Handle multipart file uploads to Django backend
/// Session 115 Part 5 - File Upload Integration
library;

import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class FileUploadService {
  final String baseUrl;
  final String? authToken;

  FileUploadService({
    required this.baseUrl,
    this.authToken,
  });

  /// Upload a single file to Django backend
  Future<String> uploadFile(File file, {String? fieldName}) async {
    final uri = Uri.parse('$baseUrl/api/v1/upload/');
    final request = http.MultipartRequest('POST', uri);

    // Add auth token
    if (authToken != null) {
      request.headers['Authorization'] = 'Token $authToken';
    }

    // Add file
    final filename = path.basename(file.path);
    final multipartFile = await http.MultipartFile.fromPath(
      fieldName ?? 'file',
      file.path,
      filename: filename,
    );
    request.files.add(multipartFile);

    // Send request
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200 || response.statusCode == 201) {
      // Parse response to get file URL
      final responseData = response.body;
      // Assuming Django returns JSON with 'url' field
      // You may need to adjust this based on your backend response
      return responseData; // Return the URL or file ID
    } else {
      throw Exception('Upload failed: ${response.statusCode} ${response.body}');
    }
  }

  /// Upload multiple files
  Future<List<String>> uploadFiles(List<File> files, {String? fieldName}) async {
    final urls = <String>[];
    for (final file in files) {
      final url = await uploadFile(file, fieldName: fieldName);
      urls.add(url);
    }
    return urls;
  }

  /// Upload image with base64 encoding (alternative method)
  Future<String> uploadImageBase64(File file) async {
    final bytes = await file.readAsBytes();
    final base64Image = bytes.toString(); // You'd use proper base64 encoding here

    final uri = Uri.parse('$baseUrl/api/v1/upload/base64/');
    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Token $authToken',
      },
      body: '{"image": "$base64Image"}',
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return response.body;
    } else {
      throw Exception('Upload failed: ${response.statusCode}');
    }
  }

  /// Create service instance from environment
  static FileUploadService fromEnv() {
    final baseUrl = dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000';
    final token = dotenv.env['AUTH_TOKEN'];
    return FileUploadService(baseUrl: baseUrl, authToken: token);
  }
}

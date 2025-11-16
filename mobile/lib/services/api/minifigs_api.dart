/// Session 111: MiniFigs API Service
///
/// HTTP client for mini-fig assets endpoints:
/// - GET /api/v1/content/minifigs/ (list user's mini-figs)
/// - GET /api/v1/content/minifigs/<id>/ (get mini-fig details)

import 'package:donkey_os_cockpit/core/api_client.dart';
import 'package:donkey_os_cockpit/models/minifig_asset.dart';

class MiniFigsApi {
  final ApiClient _client;

  MiniFigsApi(this._client);

  /// List user's mini-fig assets
  ///
  /// GET /api/v1/content/minifigs/?status=<status>&limit=<int>&offset=<int>
  ///
  /// Query parameters:
  /// - [status]: Optional filter by status (pending, processing, completed, failed)
  /// - [limit]: Max assets to return (default 20, max 100)
  /// - [offset]: Pagination offset (default 0)
  ///
  /// Returns: List of MiniFigAssets sorted by created_at desc
  Future<List<MiniFigAsset>> listMiniFigs({
    String? status,
    int limit = 20,
    int offset = 0,
  }) async {
    // Build query string manually
    final params = <String>[];
    if (status != null) params.add('status=$status');
    params.add('limit=$limit');
    params.add('offset=$offset');
    final queryString = params.join('&');

    final response = await _client.get(
      '/api/v1/content/minifigs/?$queryString',
    );

    final success = response['success'] as bool?;
    if (success != true) {
      throw ApiException(
        message: response['error']?.toString() ?? 'Unknown error listing minifigs',
      );
    }

    final minifigsData = response['minifigs'] as List<dynamic>?;
    if (minifigsData == null) {
      throw ApiException(
        message: 'Missing minifigs data in response',
      );
    }

    return minifigsData
        .map((json) => MiniFigAsset.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  /// Get mini-fig asset details by ID
  ///
  /// GET /api/v1/content/minifigs/<id>/
  ///
  /// Returns complete asset details including:
  /// - Metadata (style, scale, generation params)
  /// - User notes and tags
  /// - Source references (pipeline run, image asset)
  /// - View and download counts
  ///
  /// Note: This endpoint auto-increments the view count
  Future<MiniFigAsset> getMiniFig(String minifigId) async {
    final response = await _client.get(
      '/api/v1/content/minifigs/$minifigId/',
    );

    final success = response['success'] as bool?;
    if (success != true) {
      throw ApiException(
        message: response['error']?.toString() ?? 'Unknown error getting minifig',
      );
    }

    final minifigData = response['minifig'] as Map<String, dynamic>?;
    if (minifigData == null) {
      throw ApiException(
        message: 'Missing minifig data in response',
      );
    }

    return MiniFigAsset.fromJson(minifigData);
  }
}

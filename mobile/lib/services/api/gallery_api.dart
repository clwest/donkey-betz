/// Gallery API Service
///
/// Session 111: Galleries & Assets - Mobile Integration
/// Provides access to unified gallery endpoint combining images, videos, and audio
library;

import '../../core/api_client.dart';
import '../../models/gallery.dart';

class GalleryApi {
  final ApiClient _client;

  GalleryApi(this._client);

  /// Get gallery assets with filters and pagination
  ///
  /// Backend endpoint: GET /api/v1/gallery/all/
  /// Supports query parameters: type, favorite, search, sort_by, limit, offset
  Future<GalleryResponse> getGalleryAssets({
    GalleryFilters? filters,
  }) async {
    // Use default filters if none provided
    final appliedFilters = filters ?? const GalleryFilters();

    // Build endpoint with query parameters
    final queryParams = appliedFilters.toQueryParameters();
    final queryString = queryParams.entries
        .map((e) => '${e.key}=${Uri.encodeComponent(e.value)}')
        .join('&');

    final endpoint = '/api/v1/gallery/all/?$queryString';

    try {
      final response = await _client.get(endpoint);
      return GalleryResponse.fromJson(response);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Failed to fetch gallery assets: ${e.toString()}',
        details: e,
      );
    }
  }

  /// Get next page of gallery assets
  Future<GalleryResponse> getNextPage(GalleryFilters currentFilters) async {
    return getGalleryAssets(filters: currentFilters.nextPage());
  }

  /// Toggle favorite status for an asset
  ///
  /// For images: POST /api/images/{asset_id}/favorite/
  /// For videos: POST /api/v1/video/{asset_id}/favorite/
  Future<bool> toggleFavorite(String assetId, MediaType type) async {
    final endpoint = type == MediaType.image
        ? '/api/images/$assetId/favorite/'
        : '/api/v1/video/$assetId/favorite/';

    try {
      final response = await _client.post(endpoint, {});

      if (response['success'] == true) {
        return response['is_favorite'] == true;
      }

      throw ApiException(
        message: 'Failed to toggle favorite status',
        details: response,
      );
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Failed to toggle favorite: ${e.toString()}',
        details: e,
      );
    }
  }

  /// Delete an asset
  ///
  /// For images: DELETE /api/images/{asset_id}/
  /// For videos: DELETE /api/v1/video/{asset_id}/
  Future<void> deleteAsset(String assetId, MediaType type) async {
    final endpoint = type == MediaType.image
        ? '/api/images/$assetId/'
        : '/api/v1/video/$assetId/';

    try {
      final response = await _client.delete(endpoint);

      if (response['success'] != true) {
        throw ApiException(
          message: 'Failed to delete asset',
          details: response,
        );
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        message: 'Failed to delete asset: ${e.toString()}',
        details: e,
      );
    }
  }

  /// Get images only
  Future<GalleryResponse> getImages({
    bool? favorite,
    String? search,
    int limit = 20,
    int offset = 0,
  }) async {
    return getGalleryAssets(
      filters: GalleryFilters(
        type: 'images',
        favorite: favorite,
        search: search,
        limit: limit,
        offset: offset,
      ),
    );
  }

  /// Get videos only
  Future<GalleryResponse> getVideos({
    bool? favorite,
    String? search,
    int limit = 20,
    int offset = 0,
  }) async {
    return getGalleryAssets(
      filters: GalleryFilters(
        type: 'videos',
        favorite: favorite,
        search: search,
        limit: limit,
        offset: offset,
      ),
    );
  }

  /// Get audio only
  Future<GalleryResponse> getAudio({
    bool? favorite,
    String? search,
    int limit = 20,
    int offset = 0,
  }) async {
    return getGalleryAssets(
      filters: GalleryFilters(
        type: 'audio',
        favorite: favorite,
        search: search,
        limit: limit,
        offset: offset,
      ),
    );
  }

  /// Get favorites only (all types)
  Future<GalleryResponse> getFavorites({
    String? type,
    int limit = 20,
    int offset = 0,
  }) async {
    return getGalleryAssets(
      filters: GalleryFilters(
        type: type ?? 'all',
        favorite: true,
        limit: limit,
        offset: offset,
      ),
    );
  }
}

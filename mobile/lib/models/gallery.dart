import 'package:freezed_annotation/freezed_annotation.dart';

part 'gallery.freezed.dart';
part 'gallery.g.dart';

/// Media type enum for gallery assets
enum MediaType {
  @JsonValue('image')
  image,
  @JsonValue('video')
  video,
  @JsonValue('audio')
  audio,
}

/// Unified gallery asset model matching backend /api/v1/gallery/all/ response
/// Session 111: Galleries & Assets - Mobile Integration
@freezed
class GalleryAsset with _$GalleryAsset {
  const factory GalleryAsset({
    required String id,
    required MediaType type,
    required String url,
    @JsonKey(name: 'thumbnail_url') String? thumbnailUrl,
    String? prompt,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'is_favorite') @Default(false) bool isFavorite,
    @JsonKey(name: 'view_count') @Default(0) int viewCount,
    @JsonKey(name: 'download_count') @Default(0) int downloadCount,
    @JsonKey(name: 'model_used') String? modelUsed,
    Map<String, dynamic>? parameters,

    // Image-specific fields (only present when type=image)
    @JsonKey(name: 'image_type') String? imageType,
    String? style,
    int? width,
    int? height,
    String? filename,
    @JsonKey(name: 'user_notes') String? userNotes,
    List<String>? tags,

    // Video-specific fields (only present when type=video)
    @JsonKey(name: 'video_type') String? videoType,
    int? duration,
    String? videoModel,

    // Audio-specific fields (only present when type=audio)
    @JsonKey(name: 'audio_type') String? audioType,
    String? voice,
    int? audioDuration,
  }) = _GalleryAsset;

  factory GalleryAsset.fromJson(Map<String, dynamic> json) =>
      _$GalleryAssetFromJson(json);
}

/// Response model for unified gallery endpoint
@freezed
class GalleryResponse with _$GalleryResponse {
  const factory GalleryResponse({
    required int count,
    String? next,
    String? previous,
    @Default([]) List<GalleryAsset> results,
  }) = _GalleryResponse;

  factory GalleryResponse.fromJson(Map<String, dynamic> json) =>
      _$GalleryResponseFromJson(json);
}

/// Filter options for gallery queries
@freezed
class GalleryFilters with _$GalleryFilters {
  const factory GalleryFilters({
    @Default('all') String type, // 'all', 'images', 'videos', 'audio'
    bool? favorite,
    String? search,
    @Default('-created_at') String sortBy,
    @Default(20) int limit,
    @Default(0) int offset,
  }) = _GalleryFilters;

  const GalleryFilters._();

  /// Convert filters to query parameters for API call
  Map<String, String> toQueryParameters() {
    final params = <String, String>{
      'type': type,
      'sort_by': sortBy,
      'limit': limit.toString(),
      'offset': offset.toString(),
    };

    if (favorite != null) {
      params['favorite'] = favorite.toString();
    }

    if (search != null && search!.isNotEmpty) {
      params['search'] = search!;
    }

    return params;
  }

  /// Create a copy with updated offset for pagination
  GalleryFilters nextPage() {
    return copyWith(offset: offset + limit);
  }

  /// Create a copy with offset reset for new query
  GalleryFilters reset() {
    return copyWith(offset: 0);
  }
}

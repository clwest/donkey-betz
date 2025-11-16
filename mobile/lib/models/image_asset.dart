import 'package:freezed_annotation/freezed_annotation.dart';
import 'video_asset.dart';

part 'image_asset.freezed.dart';
part 'image_asset.g.dart';

/// Image asset model for session assets
/// Session 101: Project Browser - Mobile Flutter App
@freezed
class ImageAsset with _$ImageAsset {
  const factory ImageAsset({
    @JsonKey(includeFromJson: false, includeToJson: false) @Default(0) int id,
    @JsonKey(name: 'id') required String imageId,
    String? filePath,
    required String prompt,
    @JsonKey(name: 'model_used') @Default('stable-diffusion') String model,
    String? aspectRatio,
    String? stylePreset,
    @Default(false) bool isFavorite,
    required DateTime createdAt,
  }) = _ImageAsset;

  factory ImageAsset.fromJson(Map<String, dynamic> json) =>
      _$ImageAssetFromJson(json);
}

/// Response model for session assets endpoint
@freezed
class SessionAssetsResponse with _$SessionAssetsResponse {
  const factory SessionAssetsResponse({
    required bool success,
    required SessionInfo session,
    required List<ImageAsset> images,
    required List<VideoAsset> videos,
    @Default(0) int totalImages,
    @Default(0) int totalVideos,
  }) = _SessionAssetsResponse;

  factory SessionAssetsResponse.fromJson(Map<String, dynamic> json) =>
      _$SessionAssetsResponseFromJson(json);
}

/// Session info included in assets response
@freezed
class SessionInfo with _$SessionInfo {
  const factory SessionInfo({
    required String sessionId,
    required String title,
    required DateTime createdAt,
    @Default(0) int imageCount,
    @Default(0) int videoCount,
  }) = _SessionInfo;

  factory SessionInfo.fromJson(Map<String, dynamic> json) =>
      _$SessionInfoFromJson(json);
}

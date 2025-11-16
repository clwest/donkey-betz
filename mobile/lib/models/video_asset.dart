import 'package:freezed_annotation/freezed_annotation.dart';

part 'video_asset.freezed.dart';
part 'video_asset.g.dart';

/// Video asset model for session assets
/// Session 101: Project Browser - Mobile Flutter App
@freezed
class VideoAsset with _$VideoAsset {
  const factory VideoAsset({
    @JsonKey(includeFromJson: false, includeToJson: false) @Default(0) int id,
    @JsonKey(name: 'id') required String videoId,
    String? filePath,
    String? thumbnailPath,
    required String prompt,
    @JsonKey(name: 'model_used') @Default('runway') String model,
    int? duration,
    @Default(false) bool isFavorite,
    required DateTime createdAt,
  }) = _VideoAsset;

  factory VideoAsset.fromJson(Map<String, dynamic> json) =>
      _$VideoAssetFromJson(json);
}

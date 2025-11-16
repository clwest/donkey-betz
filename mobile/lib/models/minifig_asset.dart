/// Session 111: MiniFigAsset Model
///
/// Represents a 3D-printable mini-fig asset created from character images.
/// Status flow: pending → processing → completed/failed
///
/// Freezed model with JSON serialization (snake_case via build.yaml).

import 'package:freezed_annotation/freezed_annotation.dart';

part 'minifig_asset.freezed.dart';
part 'minifig_asset.g.dart';

/// MiniFig asset status values (must match Django model)
enum MiniFigStatus {
  pending,
  processing,
  completed,
  failed,
}

/// MiniFig provider types
enum MiniFigProvider {
  placeholder,  // v1: Placeholder 3D files
  externalService,  // v2+: Real 3D generation service
}

@Freezed(fromJson: true, toJson: true)
class MiniFigAsset with _$MiniFigAsset {
  const MiniFigAsset._(); // Private constructor for adding getters

  const factory MiniFigAsset({
    required String id,
    required String title,
    required MiniFigProvider provider,
    required MiniFigStatus status,
    required String threeDFile,
    String? previewImageUrl,
    @Default({}) Map<String, dynamic> metadata,
    String? errorMessage,
    @Default(false) bool isFavorite,
    @Default(0) int viewCount,
    @Default(0) int downloadCount,
    @Default('') String userNotes,
    @Default([]) List<String> tags,
    required DateTime createdAt,
    required DateTime updatedAt,
    String? sourcePipelineRunId,
    String? sourceImageAssetId,
  }) = _MiniFigAsset;

  factory MiniFigAsset.fromJson(Map<String, dynamic> json) =>
      _$MiniFigAssetFromJson(json);

  /// Asset is ready to use (completed successfully)
  bool get isReady => status == MiniFigStatus.completed;

  /// Asset is still being generated
  bool get isProcessing =>
      status == MiniFigStatus.processing ||
      status == MiniFigStatus.pending;

  /// Asset generation failed
  bool get isFailed => status == MiniFigStatus.failed;

  /// Get user-friendly status text
  String get statusText {
    switch (status) {
      case MiniFigStatus.pending:
        return 'Queued';
      case MiniFigStatus.processing:
        return 'Generating 3D model...';
      case MiniFigStatus.completed:
        return 'Ready to download';
      case MiniFigStatus.failed:
        return 'Generation failed';
    }
  }

  /// Get status color (Material color values)
  int get statusColor {
    switch (status) {
      case MiniFigStatus.pending:
        return 0xFF607D8B; // Grey
      case MiniFigStatus.processing:
        return 0xFF2196F3; // Blue
      case MiniFigStatus.completed:
        return 0xFF4CAF50; // Green
      case MiniFigStatus.failed:
        return 0xFFF44336; // Red
    }
  }

  /// Get provider display name
  String get providerName {
    switch (provider) {
      case MiniFigProvider.placeholder:
        return 'Placeholder (v1)';
      case MiniFigProvider.externalService:
        return '3D Generation Service';
    }
  }

  /// Get style from metadata
  String get style => (metadata['style'] as String?) ?? 'Unknown';

  /// Get scale from metadata
  String get scale => (metadata['scale'] as String?) ?? 'Unknown';

  /// Get 3D file format from URL
  String get fileFormat {
    final url = threeDFile.toLowerCase();
    if (url.endsWith('.stl')) return 'STL';
    if (url.endsWith('.obj')) return 'OBJ';
    if (url.endsWith('.3mf')) return '3MF';
    return 'Unknown';
  }

  /// Has a preview image
  bool get hasPreview => previewImageUrl != null && previewImageUrl!.isNotEmpty;
}

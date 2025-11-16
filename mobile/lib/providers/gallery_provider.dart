/// Gallery State Provider
///
/// Session 111: Galleries & Assets - Mobile Integration
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/gallery.dart';
import 'api_provider.dart';

/// Gallery filters state provider
final galleryFiltersProvider = StateProvider<GalleryFilters>((ref) {
  return const GalleryFilters(); // Default filters
});

/// Gallery assets provider with filters
final galleryAssetsProvider = FutureProvider<GalleryResponse>((ref) async {
  final api = ref.watch(galleryApiProvider);
  final filters = ref.watch(galleryFiltersProvider);
  return await api.getGalleryAssets(filters: filters);
});

/// Images only provider
final imagesProvider = FutureProvider<GalleryResponse>((ref) async {
  final api = ref.watch(galleryApiProvider);
  return await api.getImages();
});

/// Videos only provider
final videosProvider = FutureProvider<GalleryResponse>((ref) async {
  final api = ref.watch(galleryApiProvider);
  return await api.getVideos();
});

/// Audio only provider
final audioProvider = FutureProvider<GalleryResponse>((ref) async {
  final api = ref.watch(galleryApiProvider);
  return await api.getAudio();
});

/// Favorites only provider
final favoritesProvider = FutureProvider<GalleryResponse>((ref) async {
  final api = ref.watch(galleryApiProvider);
  return await api.getFavorites();
});

/// Asset count provider (extracted from gallery response)
final assetCountProvider = Provider<int>((ref) {
  final galleryAsync = ref.watch(galleryAssetsProvider);
  return galleryAsync.when(
    data: (gallery) => gallery.count,
    loading: () => 0,
    error: (_, __) => 0,
  );
});

/// Recent assets count (for dashboard card)
final recentAssetsCountProvider = FutureProvider<int>((ref) async {
  final api = ref.watch(galleryApiProvider);
  final response = await api.getGalleryAssets(
    filters: const GalleryFilters(
      limit: 1, // Just get the count, not the full list
      sortBy: '-created_at',
    ),
  );
  return response.count;
});

/// Search query provider
final searchQueryProvider = StateProvider<String>((ref) => '');

/// Media type filter provider
final mediaTypeFilterProvider = StateProvider<String>((ref) => 'all');

/// Favorite filter provider
final favoriteFilterProvider = StateProvider<bool?>((ref) => null);

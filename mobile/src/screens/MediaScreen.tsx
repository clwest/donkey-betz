import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Dimensions,
  FlatList,
  Image,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import * as mediaApi from '../api/media';
import type { MediaItem } from '../api/media';
import MediaDetailModal from '../components/MediaDetailModal';
import { toast } from '../components/Toast';

const SCREEN_WIDTH = Dimensions.get('window').width;
const GRID_GAP = 4;
const NUM_COLUMNS = 3;
const CELL_SIZE = (SCREEN_WIDTH - 16 * 2 - GRID_GAP * (NUM_COLUMNS - 1)) / NUM_COLUMNS;
const PAGE_SIZE = 30;

type Filter = 'all' | 'image' | 'video';
const FILTERS: { key: Filter; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'image', label: 'Images' },
  { key: 'video', label: 'Videos' },
];

export default function MediaScreen() {
  const [items, setItems] = useState<MediaItem[]>([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState<Filter>('all');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedItem, setSelectedItem] = useState<MediaItem | null>(null);

  const fetchMedia = useCallback(
    async (offset = 0, append = false) => {
      try {
        const typeParam = filter === 'all' ? undefined : filter;
        const result = await mediaApi.getAllMedia({
          limit: PAGE_SIZE,
          offset,
          type: typeParam,
        });
        setItems((prev) => (append ? [...prev, ...result.items] : result.items));
        setTotal(result.total);
      } catch (e: any) {
        toast.error('Failed to load media');
      }
    },
    [filter],
  );

  useEffect(() => {
    setLoading(true);
    fetchMedia(0).finally(() => setLoading(false));
  }, [fetchMedia]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchMedia(0);
    setRefreshing(false);
  }, [fetchMedia]);

  const onEndReached = useCallback(async () => {
    if (loadingMore || items.length >= total) return;
    setLoadingMore(true);
    await fetchMedia(items.length, true);
    setLoadingMore(false);
  }, [fetchMedia, items.length, loadingMore, total]);

  const renderCell = useCallback(
    ({ item }: { item: MediaItem }) => (
      <TouchableOpacity
        style={s.cell}
        activeOpacity={0.7}
        onPress={() => setSelectedItem(item)}
      >
        {item.thumbnailUrl ? (
          <Image source={{ uri: item.thumbnailUrl }} style={s.cellImage} />
        ) : (
          <View style={s.cellPlaceholder}>
            <Text style={s.cellPlaceholderIcon}>
              {item.type === 'video' ? '🎬' : '🖼'}
            </Text>
          </View>
        )}
        {item.type === 'video' && (
          <View style={s.videoBadge}>
            <Text style={s.videoBadgeText}>▶</Text>
          </View>
        )}
      </TouchableOpacity>
    ),
    [],
  );

  return (
    <View style={s.container}>
      {/* Header */}
      <View style={s.header}>
        <Text style={s.headerTitle}>Media</Text>
        <Text style={s.headerCount}>{total} items</Text>
      </View>

      {/* Filter chips */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={s.filterRow}
      >
        {FILTERS.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[s.chip, filter === f.key && s.chipActive]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[s.chipText, filter === f.key && s.chipTextActive]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Grid */}
      {loading ? (
        <View style={s.centered}>
          <ActivityIndicator size="large" color="#6366f1" />
        </View>
      ) : items.length === 0 ? (
        <View style={s.centered}>
          <Text style={s.emptyText}>No media yet</Text>
          <Text style={s.emptySubtext}>
            Ask the PA to generate images or videos
          </Text>
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => `${item.type}-${item.id}`}
          renderItem={renderCell}
          numColumns={NUM_COLUMNS}
          columnWrapperStyle={s.row}
          contentContainerStyle={s.grid}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor="#6366f1"
            />
          }
          onEndReached={onEndReached}
          onEndReachedThreshold={0.3}
          ListFooterComponent={
            loadingMore ? (
              <ActivityIndicator
                size="small"
                color="#6366f1"
                style={{ marginVertical: 16 }}
              />
            ) : null
          }
        />
      )}

      {/* Detail modal */}
      <MediaDetailModal
        item={selectedItem}
        onClose={() => setSelectedItem(null)}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a2e',
  },
  headerTitle: { color: '#d1d5db', fontSize: 15, fontWeight: '600' },
  headerCount: { color: '#6b7280', fontSize: 13 },
  filterRow: { paddingHorizontal: 16, paddingVertical: 10, gap: 8 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#1a1a2e',
    marginRight: 8,
  },
  chipActive: { backgroundColor: '#6366f1' },
  chipText: { color: '#6b7280', fontSize: 13, fontWeight: '500' },
  chipTextActive: { color: '#ffffff' },
  grid: { paddingHorizontal: 16, paddingTop: 4, paddingBottom: 20 },
  row: { gap: GRID_GAP, marginBottom: GRID_GAP },
  cell: {
    width: CELL_SIZE,
    height: CELL_SIZE,
    borderRadius: 6,
    overflow: 'hidden',
    backgroundColor: '#1a1a2e',
  },
  cellImage: { width: '100%', height: '100%' },
  cellPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cellPlaceholderIcon: { fontSize: 24 },
  videoBadge: {
    position: 'absolute',
    bottom: 4,
    right: 4,
    backgroundColor: 'rgba(0,0,0,0.6)',
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  videoBadgeText: { color: '#ffffff', fontSize: 10 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  emptyText: { color: '#d1d5db', fontSize: 16, fontWeight: '500' },
  emptySubtext: { color: '#6b7280', fontSize: 13, marginTop: 4 },
});

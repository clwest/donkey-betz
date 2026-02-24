import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { AttentionItem } from '../../api/boardroom';
import * as boardroomApi from '../../api/boardroom';

// ── Helpers ──────────────────────────────────────────────────────────────────

function urgencyStyle(u: string) {
  switch (u) {
    case 'critical': return { bg: 'rgba(239,68,68,0.2)', fg: '#ef4444' };
    case 'high':     return { bg: 'rgba(249,115,22,0.2)', fg: '#f97316' };
    case 'medium':   return { bg: 'rgba(234,179,8,0.2)',  fg: '#eab308' };
    default:         return { bg: 'rgba(107,114,128,0.2)', fg: '#6b7280' };
  }
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'now';
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}

// ── Component ────────────────────────────────────────────────────────────────

interface Props {
  onSelect: (item: AttentionItem) => void;
}

export default function AttentionList({ onSelect }: Props) {
  const [items, setItems] = useState<AttentionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setError(null);
    try {
      const res = await boardroomApi.listAttention({ limit: 50 });
      setItems(res.items ?? []);
    } catch {
      setError('Failed to load attention items');
    }
  }, []);

  useEffect(() => {
    fetch().finally(() => setLoading(false));
  }, [fetch]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetch();
    setRefreshing(false);
  }, [fetch]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="small" color="#6366f1" />
      </View>
    );
  }

  return (
    <FlatList
      data={items}
      keyExtractor={(item) => item.id}
      contentContainerStyle={items.length === 0 ? styles.center : styles.list}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" />
      }
      ListEmptyComponent={
        <Text style={styles.emptyText}>{error ?? 'No attention items'}</Text>
      }
      renderItem={({ item }) => {
        const u = urgencyStyle(item.urgency);
        return (
          <TouchableOpacity style={styles.row} onPress={() => onSelect(item)} activeOpacity={0.7}>
            <View style={styles.rowHeader}>
              <Text style={[styles.urgencyBadge, { backgroundColor: u.bg, color: u.fg }]}>
                {item.urgency}
              </Text>
              <Text style={styles.time}>{timeAgo(item.created_at)}</Text>
            </View>
            <Text style={styles.title} numberOfLines={2}>{item.title}</Text>
            {item.summary ? (
              <Text style={styles.summary} numberOfLines={2}>{item.summary}</Text>
            ) : null}
            <View style={styles.meta}>
              <Text style={styles.metaText}>{item.item_type}</Text>
              {item.status !== 'pending' && (
                <Text style={styles.metaText}>{item.status}</Text>
              )}
              {item.ml_recommendation ? (
                <Text style={styles.mlBadge}>ML: {item.ml_recommendation}</Text>
              ) : null}
            </View>
          </TouchableOpacity>
        );
      }}
    />
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  list: { paddingVertical: 4 },
  emptyText: { color: '#6b7280', fontSize: 14 },
  row: {
    backgroundColor: '#1a1a2e',
    marginHorizontal: 12,
    marginVertical: 4,
    borderRadius: 10,
    padding: 14,
  },
  rowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  urgencyBadge: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 6,
    overflow: 'hidden',
  },
  time: { color: '#4b5563', fontSize: 11 },
  title: { color: '#e5e7eb', fontSize: 15, fontWeight: '600', marginBottom: 4 },
  summary: { color: '#9ca3af', fontSize: 13, lineHeight: 18, marginBottom: 6 },
  meta: { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  metaText: { color: '#6b7280', fontSize: 11 },
  mlBadge: {
    color: '#818cf8',
    fontSize: 11,
    fontWeight: '600',
  },
});

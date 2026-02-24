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
import type { Artifact } from '../../api/governance';
import * as governanceApi from '../../api/governance';

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'now';
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}

interface Props {
  onSelect: (artifact: Artifact) => void;
}

export default function NeedsClassificationList({ onSelect }: Props) {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [totalUnclassified, setTotalUnclassified] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setError(null);
    try {
      const res = await governanceApi.listNeedsClassification({ limit: 50 });
      setArtifacts(res.artifacts ?? []);
      setTotalUnclassified(res.total_unclassified ?? 0);
    } catch {
      setError('Failed to load artifacts');
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
      data={artifacts}
      keyExtractor={(a) => a.id}
      contentContainerStyle={artifacts.length === 0 ? styles.center : styles.list}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" />
      }
      ListHeaderComponent={
        totalUnclassified > 0 ? (
          <View style={styles.headerBanner}>
            <Text style={styles.headerText}>
              {totalUnclassified} artifact{totalUnclassified !== 1 ? 's' : ''} need classification
            </Text>
          </View>
        ) : null
      }
      ListEmptyComponent={
        <Text style={styles.emptyText}>{error ?? 'All artifacts classified'}</Text>
      }
      renderItem={({ item }) => (
        <TouchableOpacity style={styles.row} onPress={() => onSelect(item)} activeOpacity={0.7}>
          <View style={styles.rowHeader}>
            <Text style={styles.scoreBadge}>
              {Math.round((item.composite_score ?? 0) * 100)}%
            </Text>
            <Text style={styles.time}>{timeAgo(item.created_at)}</Text>
          </View>
          <Text style={styles.title} numberOfLines={2}>{item.title}</Text>
          {item.content ? (
            <Text style={styles.content} numberOfLines={2}>{item.content}</Text>
          ) : null}
          <View style={styles.meta}>
            {item.source_agent ? (
              <Text style={styles.metaText}>{item.source_agent}</Text>
            ) : null}
            <Text style={styles.metaText}>{item.status}</Text>
          </View>
        </TouchableOpacity>
      )}
    />
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  list: { paddingVertical: 4 },
  emptyText: { color: '#6b7280', fontSize: 14 },
  headerBanner: {
    backgroundColor: 'rgba(234,179,8,0.1)',
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginHorizontal: 12,
    marginBottom: 4,
    borderRadius: 8,
  },
  headerText: { color: '#eab308', fontSize: 13, fontWeight: '600', textAlign: 'center' },
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
  scoreBadge: {
    fontSize: 11,
    fontWeight: '700',
    color: '#818cf8',
    backgroundColor: 'rgba(99,102,241,0.2)',
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 6,
    overflow: 'hidden',
  },
  time: { color: '#4b5563', fontSize: 11 },
  title: { color: '#e5e7eb', fontSize: 15, fontWeight: '600', marginBottom: 4 },
  content: { color: '#9ca3af', fontSize: 13, lineHeight: 18, marginBottom: 6 },
  meta: { flexDirection: 'row', gap: 8 },
  metaText: { color: '#6b7280', fontSize: 11 },
});

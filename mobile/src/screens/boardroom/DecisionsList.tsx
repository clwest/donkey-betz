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
import type { Decision } from '../../api/boardroom';
import * as boardroomApi from '../../api/boardroom';

function statusStyle(s: string) {
  switch (s) {
    case 'canonical': return { bg: 'rgba(34,197,94,0.2)', fg: '#22c55e' };
    case 'review':    return { bg: 'rgba(99,102,241,0.2)', fg: '#818cf8' };
    case 'rejected':  return { bg: 'rgba(239,68,68,0.2)', fg: '#ef4444' };
    default:          return { bg: 'rgba(234,179,8,0.2)', fg: '#eab308' }; // draft
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

interface Props {
  onSelect: (decision: Decision) => void;
}

export default function DecisionsList({ onSelect }: Props) {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setError(null);
    try {
      const res = await boardroomApi.listDecisions({ limit: 50 });
      setDecisions(res.decisions ?? []);
    } catch {
      setError('Failed to load decisions');
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
      data={decisions}
      keyExtractor={(d) => d.id}
      contentContainerStyle={decisions.length === 0 ? styles.center : styles.list}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" />
      }
      ListEmptyComponent={
        <Text style={styles.emptyText}>{error ?? 'No decisions'}</Text>
      }
      renderItem={({ item }) => {
        const s = statusStyle(item.status);
        return (
          <TouchableOpacity style={styles.row} onPress={() => onSelect(item)} activeOpacity={0.7}>
            <View style={styles.rowHeader}>
              <Text style={[styles.statusBadge, { backgroundColor: s.bg, color: s.fg }]}>
                {item.status}
              </Text>
              <Text style={styles.time}>{timeAgo(item.created_at)}</Text>
            </View>
            <Text style={styles.topic} numberOfLines={2}>{item.topic}</Text>
            {item.key_insights && item.key_insights.length > 0 && (
              <Text style={styles.insight} numberOfLines={1}>
                {item.key_insights[0]}
              </Text>
            )}
            <View style={styles.meta}>
              <Text style={styles.metaText}>{item.decision_type_display || item.decision_type}</Text>
              <Text style={styles.metaText}>{item.impact_area_display || item.impact_area}</Text>
              {item.participants.length > 0 && (
                <Text style={styles.metaText}>
                  {item.participants.length} participant{item.participants.length > 1 ? 's' : ''}
                </Text>
              )}
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
  statusBadge: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 6,
    overflow: 'hidden',
  },
  time: { color: '#4b5563', fontSize: 11 },
  topic: { color: '#e5e7eb', fontSize: 15, fontWeight: '600', marginBottom: 4 },
  insight: { color: '#9ca3af', fontSize: 13, lineHeight: 18, marginBottom: 6, fontStyle: 'italic' },
  meta: { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  metaText: { color: '#6b7280', fontSize: 11 },
});

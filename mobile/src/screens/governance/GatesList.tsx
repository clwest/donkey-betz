import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import type { PilotGate } from '../../api/governance';
import * as governanceApi from '../../api/governance';

function statusStyle(s: string) {
  switch (s) {
    case 'approved':    return { bg: 'rgba(34,197,94,0.2)',  fg: '#22c55e' };
    case 'ready':       return { bg: 'rgba(99,102,241,0.2)', fg: '#818cf8' };
    case 'in_progress': return { bg: 'rgba(234,179,8,0.2)',  fg: '#eab308' };
    case 'blocked':     return { bg: 'rgba(239,68,68,0.2)',  fg: '#ef4444' };
    case 'waived':      return { bg: 'rgba(107,114,128,0.2)', fg: '#6b7280' };
    default:            return { bg: 'rgba(75,85,99,0.2)',   fg: '#4b5563' }; // not_started
  }
}

function riskColor(r: string) {
  switch (r) {
    case 'critical': return '#ef4444';
    case 'high':     return '#f97316';
    case 'medium':   return '#eab308';
    default:         return '#22c55e';
  }
}

export default function GatesList() {
  const [gates, setGates] = useState<PilotGate[]>([]);
  const [byStatus, setByStatus] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setError(null);
    try {
      const res = await governanceApi.listGates({ limit: 50 });
      setGates(res.gates ?? []);
      setByStatus(res.by_status ?? {});
    } catch {
      setError('Failed to load gates');
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
      data={gates}
      keyExtractor={(g) => g.id}
      contentContainerStyle={gates.length === 0 ? styles.center : styles.list}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" />
      }
      ListHeaderComponent={
        Object.keys(byStatus).length > 0 ? (
          <View style={styles.summaryRow}>
            {Object.entries(byStatus).map(([status, count]) => {
              const s = statusStyle(status);
              return (
                <View key={status} style={[styles.summaryChip, { backgroundColor: s.bg }]}>
                  <Text style={[styles.summaryCount, { color: s.fg }]}>{count}</Text>
                  <Text style={styles.summaryLabel}>{status.replace('_', ' ')}</Text>
                </View>
              );
            })}
          </View>
        ) : null
      }
      ListEmptyComponent={
        <Text style={styles.emptyText}>{error ?? 'No pilot gates'}</Text>
      }
      renderItem={({ item }) => {
        const s = statusStyle(item.status);
        const prog = item.checklist_progress;
        return (
          <View style={styles.row}>
            <View style={styles.rowHeader}>
              <Text style={[styles.statusBadge, { backgroundColor: s.bg, color: s.fg }]}>
                {item.status.replace('_', ' ')}
              </Text>
              <Text style={[styles.riskBadge, { color: riskColor(item.risk_level) }]}>
                {item.risk_level} risk
              </Text>
            </View>

            {/* Progress bar */}
            <View style={styles.progressContainer}>
              <View style={styles.progressBg}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${Math.min(prog.percentage, 100)}%` },
                  ]}
                />
              </View>
              <Text style={styles.progressText}>
                {prog.completed}/{prog.total} ({Math.round(prog.percentage)}%)
              </Text>
            </View>

            <Text style={styles.gateId}>Gate {item.id.slice(0, 8)}</Text>
          </View>
        );
      }}
    />
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  list: { paddingVertical: 4 },
  emptyText: { color: '#6b7280', fontSize: 14 },

  summaryRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  summaryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    gap: 4,
  },
  summaryCount: { fontSize: 14, fontWeight: '700' },
  summaryLabel: { color: '#9ca3af', fontSize: 11, textTransform: 'capitalize' },

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
    marginBottom: 10,
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
  riskBadge: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'capitalize',
  },

  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 6,
  },
  progressBg: {
    flex: 1,
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6366f1',
    borderRadius: 3,
  },
  progressText: { color: '#9ca3af', fontSize: 11, minWidth: 80, textAlign: 'right' },

  gateId: { color: '#4b5563', fontSize: 10 },
});

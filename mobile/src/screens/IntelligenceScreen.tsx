import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import http from '../api/http';

// ── Types ────────────────────────────────────────────────────────────────────

interface IntelligenceStats {
  spiders: {
    total: number;
    categories: number;
    by_category: Record<string, number>;
  };
  agents: {
    total: number;
    legacy: number;
    clean: number;
  };
  data: {
    total_points: number;
    last_24h: number;
    success_rate: number;
  };
  learning: {
    collaborations: number;
    collaboration_sessions: number;
    learning_events: number;
    agent_memories: number;
    knowledge_sources: number;
    learning_connections: number;
    knowledge_transfers: number;
    synthesized_insights: number;
  };
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

// ── Main ─────────────────────────────────────────────────────────────────────

export default function IntelligenceScreen() {
  const [stats, setStats] = useState<IntelligenceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      // This endpoint is in PUBLIC_PATHS — works without auth
      const { data } = await http.get('/spider-intelligence/dashboard-stats/');
      setStats(data.stats);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load intelligence data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = () => { setRefreshing(true); fetchData(); };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#818cf8" />
      </View>
    );
  }

  if (error || !stats) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error ?? 'No data'}</Text>
      </View>
    );
  }

  const topCategories = Object.entries(stats.spiders.by_category)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
    >
      <Text style={styles.title}>Intelligence</Text>

      {/* Spider Network */}
      <Text style={styles.sectionHeader}>Spider Network</Text>
      <View style={styles.statsGrid}>
        <StatCard label="Spiders" value={String(stats.spiders.total)} color="#06b6d4" />
        <StatCard label="Categories" value={String(stats.spiders.categories)} color="#a855f7" />
        <StatCard label="Data Points" value={formatNumber(stats.data.total_points)} color="#22c55e" />
        <StatCard label="Last 24h" value={formatNumber(stats.data.last_24h)} color="#f59e0b" />
      </View>

      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Success Rate</Text>
          <Text style={[styles.successRate, { color: stats.data.success_rate >= 90 ? '#22c55e' : '#f59e0b' }]}>
            {stats.data.success_rate}%
          </Text>
        </View>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${stats.data.success_rate}%` }]} />
        </View>
      </View>

      {/* Top categories */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Top Categories</Text>
        {topCategories.map(([name, count]) => (
          <View key={name} style={styles.categoryRow}>
            <Text style={styles.categoryName}>{name}</Text>
            <View style={styles.categoryBarContainer}>
              <View
                style={[
                  styles.categoryBar,
                  { width: `${(count / topCategories[0][1]) * 100}%` },
                ]}
              />
            </View>
            <Text style={styles.categoryCount}>{count}</Text>
          </View>
        ))}
      </View>

      {/* Agent Network */}
      <Text style={styles.sectionHeader}>Agent Network</Text>
      <View style={styles.statsGrid}>
        <StatCard label="Total Agents" value={String(stats.agents.total)} color="#818cf8" />
        <StatCard label="Memories" value={formatNumber(stats.learning.agent_memories)} color="#ec4899" />
        <StatCard label="Knowledge" value={formatNumber(stats.learning.knowledge_sources)} color="#06b6d4" />
        <StatCard label="Collabs" value={formatNumber(stats.learning.collaborations)} color="#22c55e" />
      </View>

      {/* Learning stats */}
      <Text style={styles.sectionHeader}>Learning Loop</Text>
      <View style={styles.card}>
        <MetricRow label="Collaboration Sessions" value={formatNumber(stats.learning.collaboration_sessions)} />
        <MetricRow label="Learning Events" value={formatNumber(stats.learning.learning_events)} />
        <MetricRow label="Knowledge Transfers" value={formatNumber(stats.learning.knowledge_transfers)} />
        <MetricRow label="Learning Connections" value={formatNumber(stats.learning.learning_connections)} />
        <MetricRow label="Synthesized Insights" value={formatNumber(stats.learning.synthesized_insights)} />
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ── Components ───────────────────────────────────────────────────────────────

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <View style={styles.statCard}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.metricRow}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 16 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0a0f' },

  title: { color: '#ffffff', fontSize: 22, fontWeight: '700', marginBottom: 16 },
  sectionHeader: { color: '#818cf8', fontSize: 12, fontWeight: '700', textTransform: 'uppercase', marginBottom: 8, marginTop: 12 },

  errorText: { color: '#ef4444', fontSize: 14 },

  // Stats grid (2x2)
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 10 },
  statCard: {
    width: '48%',
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
    flexGrow: 1,
  },
  statValue: { fontSize: 22, fontWeight: '700' },
  statLabel: { color: '#6b7280', fontSize: 10, marginTop: 4 },

  // Card
  card: { backgroundColor: '#1a1a2e', borderRadius: 10, padding: 14, marginBottom: 10 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  cardTitle: { color: '#d1d5db', fontSize: 13, fontWeight: '600', marginBottom: 8 },
  successRate: { fontSize: 18, fontWeight: '700' },

  // Progress bar
  progressBar: { height: 6, backgroundColor: '#0f0f1a', borderRadius: 3, overflow: 'hidden' },
  progressFill: { height: '100%', backgroundColor: '#22c55e', borderRadius: 3 },

  // Category bar chart
  categoryRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
  categoryName: { color: '#6b7280', fontSize: 11, width: 70 },
  categoryBarContainer: { flex: 1, height: 8, backgroundColor: '#0f0f1a', borderRadius: 4, marginHorizontal: 8, overflow: 'hidden' },
  categoryBar: { height: '100%', backgroundColor: '#818cf8', borderRadius: 4 },
  categoryCount: { color: '#d1d5db', fontSize: 11, fontWeight: '600', width: 24, textAlign: 'right' },

  // Metric row
  metricRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
  metricLabel: { color: '#6b7280', fontSize: 13 },
  metricValue: { color: '#d1d5db', fontSize: 13, fontWeight: '600' },
});

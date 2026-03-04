import React, { useState, useCallback, useMemo } from 'react';
import {
  View, Text, ScrollView, RefreshControl, TouchableOpacity,
  StyleSheet, ActivityIndicator, Dimensions,
} from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Feather } from '@expo/vector-icons';
import { useScreenAnalytics } from '../observability/analytics';
import ScreenState from '../components/ScreenState';
import {
  getStats, getPlatforms, getRevenueDashboard,
  getRecommendations, comparePlatforms, getContent,
  type PortfolioStats, type Platform, type Revenue,
  type Recommendation, type PlatformComparison, type Distribution,
} from '../api/portfolio';

type TabKey = 'overview' | 'platforms' | 'revenue';

const TABS: { key: TabKey; label: string; icon: keyof typeof Feather.glyphMap }[] = [
  { key: 'overview', label: 'Overview', icon: 'pie-chart' },
  { key: 'platforms', label: 'Platforms', icon: 'globe' },
  { key: 'revenue', label: 'Revenue', icon: 'dollar-sign' },
];

// ── Helpers ──────────────────────────────────────────────────────────────────

function fmt(n: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD',
    minimumFractionDigits: 0, maximumFractionDigits: 0,
  }).format(n);
}

function statusColor(status: string): string {
  switch (status) {
    case 'published': return '#22c55e';
    case 'pending': return '#f59e0b';
    default: return '#6b7280';
  }
}

// ── Main Screen ──────────────────────────────────────────────────────────────

export default function PortfolioScreen() {
  useScreenAnalytics('Portfolio');
  const [tab, setTab] = useState<TabKey>('overview');

  // ── Queries ──────────────────────────────────────────────────────────────
  const statsQ = useQuery({ queryKey: ['portfolio-stats'], queryFn: getStats });
  const platformsQ = useQuery({ queryKey: ['portfolio-platforms'], queryFn: getPlatforms });
  const revenueQ = useQuery({
    queryKey: ['portfolio-revenue'], queryFn: getRevenueDashboard,
    enabled: tab === 'overview' || tab === 'revenue',
  });
  const contentQ = useQuery({
    queryKey: ['portfolio-content'], queryFn: getContent,
    enabled: tab === 'overview',
  });
  const recsQ = useQuery({
    queryKey: ['portfolio-recs'], queryFn: getRecommendations,
    enabled: tab === 'overview',
  });
  const compareQ = useQuery({
    queryKey: ['portfolio-compare'], queryFn: comparePlatforms,
    enabled: tab === 'revenue',
  });

  const loading = statsQ.isLoading;
  const error = statsQ.error;

  const onRefresh = useCallback(() => {
    statsQ.refetch();
    platformsQ.refetch();
    revenueQ.refetch();
    contentQ.refetch();
    recsQ.refetch();
    compareQ.refetch();
  }, [statsQ, platformsQ, revenueQ, contentQ, recsQ, compareQ]);

  const refreshing = statsQ.isFetching || platformsQ.isFetching;

  const stats: PortfolioStats = statsQ.data ?? { total_revenue: 0, platforms: 0, connected: 0, distributions: 0 };
  const platforms: Platform[] = platformsQ.data ?? [];
  const revenue: Revenue = revenueQ.data ?? { total: 0, this_month: 0, last_month: 0, pending: 0, by_platform: {} };
  const content: Distribution[] = contentQ.data ?? [];
  const recommendations: Recommendation[] = recsQ.data ?? [];
  const comparison: PlatformComparison[] = compareQ.data ?? [];

  return (
    <View style={s.root}>
      {/* Tab bar */}
      <View style={s.tabBar}>
        {TABS.map(({ key, label, icon }) => (
          <TouchableOpacity
            key={key}
            style={[s.tab, tab === key && s.tabActive]}
            onPress={() => setTab(key)}
          >
            <Feather name={icon} size={14} color={tab === key ? '#fff' : '#9ca3af'} />
            <Text style={[s.tabLabel, tab === key && s.tabLabelActive]}>{label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScreenState loading={loading} error={error ? String(error) : null} onRetry={onRefresh}>
        <ScrollView
          contentContainerStyle={s.scroll}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
        >
          {tab === 'overview' && (
            <OverviewTab
              stats={stats}
              revenue={revenue}
              platforms={platforms}
              content={content}
              recommendations={recommendations}
            />
          )}
          {tab === 'platforms' && <PlatformsTab platforms={platforms} />}
          {tab === 'revenue' && (
            <RevenueTab revenue={revenue} comparison={comparison} loadingCompare={compareQ.isLoading} />
          )}
        </ScrollView>
      </ScreenState>
    </View>
  );
}

// ── Overview Tab ─────────────────────────────────────────────────────────────

function OverviewTab({ stats, revenue, platforms, content, recommendations }: {
  stats: PortfolioStats; revenue: Revenue; platforms: Platform[];
  content: Distribution[]; recommendations: Recommendation[];
}) {
  return (
    <View style={{ gap: 16 }}>
      {/* Stats grid */}
      <View style={s.grid2}>
        <StatCard label="Total Revenue" value={fmt(stats.total_revenue || revenue.total || 0)} color="#22c55e" icon="dollar-sign" />
        <StatCard label="Platforms" value={String(stats.platforms || platforms.length)} color="#818cf8" icon="globe" />
        <StatCard label="Connected" value={String(stats.connected)} color="#06b6d4" icon="link-2" />
        <StatCard label="Distributions" value={String(stats.distributions || content.length)} color="#f59e0b" icon="package" />
      </View>

      {/* Platforms preview */}
      <View style={s.card}>
        <Text style={s.cardTitle}>Distribution Platforms</Text>
        {platforms.length > 0 ? (
          platforms.slice(0, 4).map((p) => (
            <View key={p.id} style={s.listRow}>
              <View style={s.listRowLeft}>
                <View style={[s.iconCircle, { backgroundColor: 'rgba(129,140,248,0.15)' }]}>
                  <Feather name="globe" size={16} color="#818cf8" />
                </View>
                <View>
                  <Text style={s.listPrimary}>{p.name}</Text>
                  <Text style={s.listSecondary}>{p.slug || p.description || 'Platform'}</Text>
                </View>
              </View>
              <View style={[s.badge, { backgroundColor: p.connected ? 'rgba(34,197,94,0.15)' : 'rgba(107,114,128,0.15)' }]}>
                <Text style={[s.badgeText, { color: p.connected ? '#22c55e' : '#6b7280' }]}>
                  {p.connected ? 'Connected' : 'Available'}
                </Text>
              </View>
            </View>
          ))
        ) : (
          <EmptyBlock icon="globe" text="No platforms available" />
        )}
      </View>

      {/* Recent distributions */}
      <View style={s.card}>
        <Text style={s.cardTitle}>Recent Distributions</Text>
        {content.length > 0 ? (
          content.slice(0, 4).map((d) => (
            <View key={d.id} style={s.listRow}>
              <View style={s.listRowLeft}>
                <Feather name="package" size={16} color="#f59e0b" />
                <View>
                  <Text style={s.listPrimary}>{d.title || 'Untitled'}</Text>
                  <Text style={s.listSecondary}>{d.content_type || 'Content'}</Text>
                </View>
              </View>
              <View style={[s.badge, { backgroundColor: statusColor(d.status) + '26' }]}>
                <Text style={[s.badgeText, { color: statusColor(d.status) }]}>{d.status}</Text>
              </View>
            </View>
          ))
        ) : (
          <EmptyBlock icon="package" text="No distributions yet" />
        )}
      </View>

      {/* Recommendations */}
      <View style={s.card}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Feather name="zap" size={18} color="#f59e0b" />
          <Text style={s.cardTitle}>Recommendations</Text>
        </View>
        {recommendations.length > 0 ? (
          recommendations.slice(0, 4).map((rec, idx) => {
            const score = rec.confidence_score || 0;
            const color = score >= 0.8 ? '#22c55e' : score >= 0.5 ? '#f59e0b' : '#6b7280';
            return (
              <View key={rec.platform?.id || String(idx)} style={s.listRow}>
                <View style={s.listRowLeft}>
                  <View style={[s.iconCircle, { backgroundColor: color + '26' }]}>
                    <Feather name="zap" size={14} color={color} />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={s.listPrimary}>{rec.platform?.name || 'Platform'}</Text>
                    <Text style={s.listSecondary} numberOfLines={1}>
                      {rec.reasoning || `${rec.platform?.type || 'content'} recommendation`}
                    </Text>
                  </View>
                </View>
                {score > 0 && (
                  <Text style={[s.badgeText, { color: '#22c55e', fontWeight: '600' }]}>
                    {Math.round(score * 100)}%
                  </Text>
                )}
              </View>
            );
          })
        ) : (
          <EmptyBlock icon="zap" text="No recommendations yet" />
        )}
      </View>
    </View>
  );
}

// ── Platforms Tab ─────────────────────────────────────────────────────────────

function PlatformsTab({ platforms }: { platforms: Platform[] }) {
  if (platforms.length === 0) {
    return (
      <View style={s.card}>
        <EmptyBlock icon="globe" text="No platforms available" sub="Check back later for distribution platforms" />
      </View>
    );
  }

  return (
    <View style={{ gap: 12 }}>
      {platforms.map((p) => (
        <View key={p.id} style={s.card}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 }}>
            <View style={[s.iconCircle, { backgroundColor: 'rgba(129,140,248,0.15)', width: 40, height: 40 }]}>
              <Feather name="globe" size={20} color="#818cf8" />
            </View>
            <View style={[s.badge, { backgroundColor: p.connected ? 'rgba(34,197,94,0.15)' : 'rgba(107,114,128,0.15)' }]}>
              <Text style={[s.badgeText, { color: p.connected ? '#22c55e' : '#6b7280' }]}>
                {p.connected ? 'Connected' : 'Available'}
              </Text>
            </View>
          </View>
          <Text style={[s.listPrimary, { fontSize: 16, marginBottom: 4 }]}>{p.name}</Text>
          <Text style={[s.listSecondary, { marginBottom: 8 }]}>{p.description || 'Distribution platform'}</Text>
          <View style={s.statusRow}>
            <Feather name="check-circle" size={14} color={p.connected ? '#22c55e' : '#6b7280'} />
            <Text style={{ color: '#9ca3af', fontSize: 12 }}>
              {p.connected ? 'Integration active' : 'Not connected'}
            </Text>
          </View>
        </View>
      ))}
    </View>
  );
}

// ── Revenue Tab ──────────────────────────────────────────────────────────────

function RevenueTab({ revenue, comparison, loadingCompare }: {
  revenue: Revenue; comparison: PlatformComparison[]; loadingCompare: boolean;
}) {
  const maxRev = useMemo(() => Math.max(...comparison.map((c) => c.revenue), 1), [comparison]);

  return (
    <View style={{ gap: 16 }}>
      {/* Revenue stats */}
      <View style={s.grid2}>
        <View style={[s.statCard, { borderColor: 'rgba(34,197,94,0.3)' }]}>
          <Text style={s.statLabel}>Total Revenue</Text>
          <Text style={[s.statValue, { color: '#22c55e', fontSize: 22 }]}>{fmt(revenue.total)}</Text>
        </View>
        <View style={s.statCard}>
          <Text style={s.statLabel}>This Month</Text>
          <Text style={s.statValue}>{fmt(revenue.this_month)}</Text>
        </View>
        <View style={s.statCard}>
          <Text style={s.statLabel}>Last Month</Text>
          <Text style={s.statValue}>{fmt(revenue.last_month)}</Text>
        </View>
        <View style={s.statCard}>
          <Text style={s.statLabel}>Pending</Text>
          <Text style={[s.statValue, { color: '#f59e0b' }]}>{fmt(revenue.pending)}</Text>
        </View>
      </View>

      {/* Revenue by platform */}
      <View style={s.card}>
        <Text style={s.cardTitle}>Revenue by Platform</Text>
        {Object.keys(revenue.by_platform).length > 0 ? (
          Object.entries(revenue.by_platform).map(([platform, amount]) => (
            <View key={platform} style={[s.listRow, { paddingVertical: 8 }]}>
              <View style={s.listRowLeft}>
                <Feather name="globe" size={16} color="#818cf8" />
                <Text style={[s.listPrimary, { textTransform: 'capitalize' }]}>{platform}</Text>
              </View>
              <Text style={{ color: '#22c55e', fontWeight: '600', fontSize: 14 }}>{fmt(amount)}</Text>
            </View>
          ))
        ) : (
          <EmptyBlock icon="bar-chart-2" text="No revenue data available" />
        )}
      </View>

      {/* Platform comparison */}
      <View style={s.card}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Feather name="trending-up" size={18} color="#06b6d4" />
          <Text style={s.cardTitle}>Platform Comparison</Text>
          {loadingCompare && <ActivityIndicator size="small" color="#818cf8" />}
        </View>
        {comparison.length > 0 ? (
          comparison.map((item, idx) => {
            const pct = (item.revenue / maxRev) * 100;
            return (
              <View key={idx} style={{ marginBottom: 12 }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
                  <Text style={[s.listPrimary, { textTransform: 'capitalize' }]}>{item.platform}</Text>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                    <Text style={{ color: '#e5e7eb', fontWeight: '600', fontSize: 13 }}>{fmt(item.revenue)}</Text>
                    {item.growth_percent != null && (
                      <Text style={{ color: item.growth_percent >= 0 ? '#22c55e' : '#ef4444', fontSize: 11 }}>
                        {item.growth_percent >= 0 ? '+' : ''}{item.growth_percent}%
                      </Text>
                    )}
                  </View>
                </View>
                <View style={s.barBg}>
                  <View style={[s.barFill, { width: `${Math.max(pct, 2)}%` as any }]} />
                </View>
              </View>
            );
          })
        ) : (
          <EmptyBlock icon="trending-up" text="No comparison data yet" sub="Connect multiple platforms to compare" />
        )}
      </View>
    </View>
  );
}

// ── Shared Pieces ────────────────────────────────────────────────────────────

function StatCard({ label, value, color, icon }: { label: string; value: string; color: string; icon: keyof typeof Feather.glyphMap }) {
  return (
    <View style={s.statCard}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <View>
          <Text style={s.statLabel}>{label}</Text>
          <Text style={[s.statValue, { color }]}>{value}</Text>
        </View>
        <Feather name={icon} size={20} color={color} />
      </View>
    </View>
  );
}

function EmptyBlock({ icon, text, sub }: { icon: keyof typeof Feather.glyphMap; text: string; sub?: string }) {
  return (
    <View style={{ alignItems: 'center', paddingVertical: 24 }}>
      <Feather name={icon} size={28} color="#4b5563" style={{ marginBottom: 8 }} />
      <Text style={{ color: '#6b7280', fontSize: 13 }}>{text}</Text>
      {sub && <Text style={{ color: '#4b5563', fontSize: 11, marginTop: 4 }}>{sub}</Text>}
    </View>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const { width } = Dimensions.get('window');

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0f172a' },
  scroll: { padding: 16, paddingBottom: 32 },

  // Tabs
  tabBar: {
    flexDirection: 'row', gap: 4,
    paddingHorizontal: 16, paddingVertical: 8,
    borderBottomWidth: 1, borderBottomColor: '#1e293b',
  },
  tab: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8,
  },
  tabActive: { backgroundColor: '#4f46e5' },
  tabLabel: { color: '#9ca3af', fontSize: 13, fontWeight: '500' },
  tabLabelActive: { color: '#fff' },

  // Cards
  card: {
    backgroundColor: '#1e293b', borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: '#334155',
  },
  cardTitle: { color: '#e5e7eb', fontSize: 15, fontWeight: '600', marginBottom: 12 },

  // Grid
  grid2: {
    flexDirection: 'row', flexWrap: 'wrap', gap: 10,
  },
  statCard: {
    backgroundColor: '#1e293b', borderRadius: 10, padding: 14,
    borderWidth: 1, borderColor: '#334155',
    width: (width - 42) / 2,
  },
  statLabel: { color: '#9ca3af', fontSize: 11, marginBottom: 4 },
  statValue: { color: '#e5e7eb', fontSize: 18, fontWeight: '700' },

  // List rows
  listRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#1e293b22',
  },
  listRowLeft: { flexDirection: 'row', alignItems: 'center', gap: 10, flex: 1 },
  listPrimary: { color: '#e5e7eb', fontSize: 13, fontWeight: '500' },
  listSecondary: { color: '#6b7280', fontSize: 11 },

  // Badges
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  badgeText: { fontSize: 11, fontWeight: '500' },

  // Icons
  iconCircle: {
    width: 32, height: 32, borderRadius: 16,
    alignItems: 'center', justifyContent: 'center',
  },

  // Status
  statusRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },

  // Bar chart
  barBg: {
    height: 6, backgroundColor: '#1e293b', borderRadius: 3, overflow: 'hidden',
  },
  barFill: {
    height: '100%', borderRadius: 3,
    backgroundColor: '#818cf8',
  },
});

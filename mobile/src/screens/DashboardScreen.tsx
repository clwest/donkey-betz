import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Feather } from '@expo/vector-icons';
import type {
  ActivityItem,
  AttentionStats,
  BodySummary,
  DashboardStats,
  GovernanceStats,
  Initiative,
} from '../api/dashboard';
import * as dashboardApi from '../api/dashboard';
import { getStats as getBettingStats, type BettingStats } from '../api/betting';
import { getHub, type StockHub } from '../api/stocks';
import { getRevenueDashboard, type Revenue } from '../api/portfolio';
import { useScreenAnalytics } from '../observability/analytics';
import { useDemo } from '../demo/useDemo';
import * as demo from '../demo/demoData';
import { formatMoney } from '../utils/format';
import DataStatusChip, { type DataStatus } from '../components/DataStatusChip';

// ── Helpers ──────────────────────────────────────────────────────────────────

function healthColor(score: number): string {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#eab308';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}

function urgencyColor(level: string): string {
  switch (level) {
    case 'critical': return '#ef4444';
    case 'high': return '#f97316';
    case 'medium': return '#eab308';
    default: return '#6b7280';
  }
}

function statusColor(status: string): string {
  switch (status.toUpperCase()) {
    case 'ACTIVE': return '#22c55e';
    case 'COMPLETED': return '#6366f1';
    case 'PAUSED': return '#eab308';
    default: return '#6b7280';
  }
}

function timeAgo(timestamp: string): string {
  const diff = Date.now() - new Date(timestamp).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

// ── Main ─────────────────────────────────────────────────────────────────────

export default function DashboardScreen() {
  useScreenAnalytics('Dashboard');
  const navigation = useNavigation<any>();
  const isDemo = useDemo();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [health, setHealth] = useState<BodySummary | null>(null);
  const [attention, setAttention] = useState<AttentionStats | null>(null);
  const [governance, setGovernance] = useState<GovernanceStats | null>(null);
  const [initiatives, setInitiatives] = useState<Initiative[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  // Money-making verticals
  const [betting, setBetting] = useState<BettingStats | null>(null);
  const [stockHub, setStockHub] = useState<StockHub | null>(null);
  const [revenue, setRevenue] = useState<Revenue | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [dataStatus, setDataStatus] = useState<DataStatus>('live');

  const fetchAll = useCallback(async () => {
    setError(null);

    if (isDemo) {
      setHealth(demo.DEMO_BODY_SUMMARY);
      setAttention(demo.DEMO_ATTENTION_STATS);
      setGovernance(demo.DEMO_GOVERNANCE_STATS);
      setInitiatives(demo.DEMO_INITIATIVES);
      setActivity(demo.DEMO_ACTIVITY.activities);
      setStats(demo.DEMO_DASHBOARD_STATS);
      setBetting(demo.DEMO_BETTING_STATS);
      setStockHub(demo.DEMO_STOCK_HUB as any);
      setRevenue(demo.DEMO_REVENUE);
      setLastUpdated(new Date());
      return;
    }

    const results = await Promise.allSettled([
      dashboardApi.getBodySummary(),
      dashboardApi.getAttentionStats(),
      dashboardApi.getGovernanceStats(),
      dashboardApi.getInitiatives(),
      dashboardApi.getRecentActivity(),
      dashboardApi.getDashboardStats(),
      getBettingStats(),
      getHub(),
      getRevenueDashboard(),
    ]);

    // Accept partial data — show what we can
    if (results[0].status === 'fulfilled') setHealth(results[0].value);
    if (results[1].status === 'fulfilled') setAttention(results[1].value);
    if (results[2].status === 'fulfilled') setGovernance(results[2].value);
    if (results[3].status === 'fulfilled') setInitiatives(results[3].value);
    if (results[4].status === 'fulfilled') setActivity(results[4].value.activities ?? []);
    if (results[5].status === 'fulfilled') setStats(results[5].value);
    if (results[6].status === 'fulfilled') setBetting(results[6].value);
    if (results[7].status === 'fulfilled') setStockHub(results[7].value);
    if (results[8].status === 'fulfilled') setRevenue(results[8].value);

    const allFailed = results.every((r) => r.status === 'rejected');
    if (allFailed) {
      setError('Failed to load dashboard data. Pull to retry.');
      setDataStatus('error');
    } else {
      setLastUpdated(new Date());
      setDataStatus('live');
    }
  }, [isDemo]);

  useEffect(() => {
    fetchAll().finally(() => setLoading(false));
  }, [fetchAll]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchAll();
    setRefreshing(false);
  }, [fetchAll]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366f1" />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          tintColor="#6366f1"
          colors={['#6366f1']}
        />
      }
    >
      <DataStatusChip status={dataStatus} lastUpdated={lastUpdated} />

      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* ── Money-Making Verticals ────────────────────────── */}
      <View style={styles.verticalsRow}>
        {/* Betting snapshot */}
        <TouchableOpacity
          style={[styles.verticalCard, { borderColor: 'rgba(99,102,241,0.3)' }]}
          activeOpacity={0.7}
          onPress={() => navigation.navigate('/betting')}
        >
          <Feather name="trending-up" size={18} color="#818cf8" />
          <Text style={styles.verticalLabel}>Betting</Text>
          {betting ? (
            <>
              <Text style={[styles.verticalValue, { color: betting.total_profit_loss >= 0 ? '#22c55e' : '#ef4444' }]}>
                {betting.total_profit_loss >= 0 ? '+' : ''}{formatMoney(betting.total_profit_loss)}
              </Text>
              <Text style={styles.verticalMeta}>
                {betting.win_rate > 0 ? `${Math.round(betting.win_rate)}% WR` : `${betting.pending} pending`}
              </Text>
            </>
          ) : (
            <Text style={styles.verticalMeta}>--</Text>
          )}
        </TouchableOpacity>

        {/* Stocks snapshot */}
        <TouchableOpacity
          style={[styles.verticalCard, { borderColor: 'rgba(6,182,212,0.3)' }]}
          activeOpacity={0.7}
          onPress={() => navigation.navigate('/stocks')}
        >
          <Feather name="activity" size={18} color="#06b6d4" />
          <Text style={styles.verticalLabel}>Stocks</Text>
          {stockHub ? (
            <>
              <Text style={[styles.verticalValue, { color: '#06b6d4' }]}>
                {stockHub.stats.total_alerts}
              </Text>
              <Text style={styles.verticalMeta}>
                {stockHub.stats.accuracy_7d != null
                  ? `${Math.round(stockHub.stats.accuracy_7d)}% acc`
                  : `${stockHub.stats.total_predictions} pred`}
              </Text>
            </>
          ) : (
            <Text style={styles.verticalMeta}>--</Text>
          )}
        </TouchableOpacity>

        {/* Portfolio snapshot */}
        <TouchableOpacity
          style={[styles.verticalCard, { borderColor: 'rgba(34,197,94,0.3)' }]}
          activeOpacity={0.7}
          onPress={() => navigation.navigate('/portfolio')}
        >
          <Feather name="dollar-sign" size={18} color="#22c55e" />
          <Text style={styles.verticalLabel}>Portfolio</Text>
          {revenue ? (
            <>
              <Text style={[styles.verticalValue, { color: '#22c55e' }]}>
                {formatMoney(revenue.total)}
              </Text>
              <Text style={styles.verticalMeta}>
                {revenue.this_month > 0 ? `${formatMoney(revenue.this_month)} /mo` : 'revenue'}
              </Text>
            </>
          ) : (
            <Text style={styles.verticalMeta}>--</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* ── System Health ────────────────────────────────── */}
      <TouchableOpacity style={styles.card} activeOpacity={0.7}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>System Health</Text>
          {health && (
            <Text style={[styles.badge, { backgroundColor: healthColor(health.health_score) + '30', color: healthColor(health.health_score) }]}>
              {health.overall_health}
            </Text>
          )}
        </View>
        {health ? (
          <View>
            <View style={styles.scoreRow}>
              <Text style={[styles.bigNumber, { color: healthColor(health.health_score) }]}>
                {health.health_score}%
              </Text>
              <Text style={styles.mutedText}>
                {health.healthy_systems}/{health.total_systems} systems healthy
              </Text>
            </View>
            {health.alert_count > 0 && (
              <Text style={styles.alertText}>
                {health.alert_count} alert{health.alert_count > 1 ? 's' : ''}
              </Text>
            )}
            {Object.entries(health.systems).length > 0 && (
              <View style={styles.systemGrid}>
                {Object.entries(health.systems).map(([name, sys]: [string, any]) => (
                  <View key={name} style={styles.systemChip}>
                    <Text style={styles.systemEmoji}>{sys.emoji}</Text>
                    <Text style={styles.systemName}>{name}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        ) : (
          <Text style={styles.mutedText}>Unavailable</Text>
        )}
      </TouchableOpacity>

      {/* ── Boardroom ────────────────────────────────────── */}
      <TouchableOpacity
        style={styles.card}
        activeOpacity={0.7}
        onPress={() => navigation.navigate('/boardroom')}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Boardroom</Text>
          {attention && attention.pending_count > 0 && (
            <Text style={[styles.badge, styles.badgeCritical]}>
              {attention.pending_count} pending
            </Text>
          )}
        </View>
        {attention ? (
          <View>
            <View style={styles.statRow}>
              <StatBox label="Critical" value={attention.by_urgency.critical} color="#ef4444" />
              <StatBox label="High" value={attention.by_urgency.high} color="#f97316" />
              <StatBox label="Medium" value={attention.by_urgency.medium} color="#eab308" />
              <StatBox label="Low" value={attention.by_urgency.low} color="#6b7280" />
            </View>
            <Text style={styles.mutedText}>
              {attention.total_items} total attention items
            </Text>
          </View>
        ) : (
          <Text style={styles.mutedText}>Unavailable</Text>
        )}
      </TouchableOpacity>

      {/* ── Governance ───────────────────────────────────── */}
      <TouchableOpacity
        style={styles.card}
        activeOpacity={0.7}
        onPress={() => navigation.navigate('/governance')}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Governance</Text>
          {governance && governance.pending_review_count > 0 && (
            <Text style={[styles.badge, styles.badgeWarning]}>
              {governance.pending_review_count} pending
            </Text>
          )}
        </View>
        {governance ? (
          <View style={styles.statRow}>
            <StatBox label="Total" value={governance.total_decisions} color="#d1d5db" />
            <StatBox label="Approved" value={governance.approved_count} color="#22c55e" />
            <StatBox label="Draft" value={governance.draft_count} color="#eab308" />
            <StatBox label="Rejected" value={governance.rejected_count} color="#ef4444" />
          </View>
        ) : (
          <Text style={styles.mutedText}>Unavailable</Text>
        )}
      </TouchableOpacity>

      {/* ── Quick Stats ──────────────────────────────────── */}
      {stats && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Platform Stats</Text>
          <View style={styles.statRow}>
            <StatBox label="Agents" value={stats.active_agents} color="#818cf8" />
            <StatBox label="Executions" value={stats.agent_executions_24h} color="#22c55e" />
            <StatBox label="Spider Data" value={stats.spider_data_points} color="#06b6d4" />
            <StatBox label="Opportunities" value={stats.active_opportunities} color="#f97316" />
          </View>
        </View>
      )}

      {/* ── Initiatives ──────────────────────────────────── */}
      <TouchableOpacity
        style={styles.card}
        activeOpacity={0.7}
        onPress={() => navigation.navigate('/initiatives')}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Initiatives</Text>
          <Text style={styles.mutedText}>{initiatives.length} total</Text>
        </View>
        {initiatives.length > 0 ? (
          initiatives.slice(0, 5).map((init) => (
            <View key={init.id} style={styles.initiativeRow}>
              <View style={[styles.statusDot, { backgroundColor: statusColor(init.status) }]} />
              <View style={styles.initiativeInfo}>
                <Text style={styles.initiativeName} numberOfLines={1}>
                  {init.name}
                </Text>
                <Text style={styles.initiativeMeta}>
                  {init.status} — {init.current_stage}
                </Text>
              </View>
            </View>
          ))
        ) : (
          <Text style={styles.mutedText}>No initiatives</Text>
        )}
      </TouchableOpacity>

      {/* ── Recent Activity ──────────────────────────────── */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Recent Activity</Text>
        {activity.length > 0 ? (
          activity.slice(0, 10).map((item, i) => (
            <View key={i} style={styles.activityRow}>
              <Text style={styles.activityIcon}>{item.icon || '•'}</Text>
              <View style={styles.activityInfo}>
                <Text style={styles.activityTitle} numberOfLines={1}>
                  {item.title}
                </Text>
                {item.subtitle ? (
                  <Text style={styles.activitySubtitle} numberOfLines={1}>
                    {item.subtitle}
                  </Text>
                ) : null}
              </View>
              <Text style={styles.activityTime}>{timeAgo(item.timestamp)}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.mutedText}>No recent activity</Text>
        )}
      </View>

      {/* Bottom spacer */}
      <View style={{ height: 24 }} />
    </ScrollView>
  );
}

// ── Stat box component ───────────────────────────────────────────────────────

function StatBox({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <View style={styles.statBox}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
  },
  content: {
    padding: 12,
  },
  center: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    color: '#6b7280',
    fontSize: 14,
    marginTop: 12,
  },

  // Error
  errorBanner: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  errorText: {
    color: '#ef4444',
    fontSize: 13,
    textAlign: 'center',
  },

  // Cards
  card: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },

  // Badges
  badge: {
    fontSize: 11,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    overflow: 'hidden',
  },
  badgeCritical: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    color: '#ef4444',
  },
  badgeWarning: {
    backgroundColor: 'rgba(234, 179, 8, 0.2)',
    color: '#eab308',
  },

  // Score
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 10,
    marginBottom: 6,
  },
  bigNumber: {
    fontSize: 32,
    fontWeight: '800',
  },

  // Stat grid
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statBox: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '700',
  },
  statLabel: {
    color: '#6b7280',
    fontSize: 11,
    marginTop: 2,
  },

  // Systems
  systemGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 8,
  },
  systemChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(99, 102, 241, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  systemEmoji: {
    fontSize: 14,
    marginRight: 4,
  },
  systemName: {
    color: '#9ca3af',
    fontSize: 11,
    textTransform: 'capitalize',
  },

  // Alerts
  alertText: {
    color: '#f97316',
    fontSize: 12,
    fontWeight: '600',
  },

  // Initiatives
  initiativeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 10,
  },
  initiativeInfo: {
    flex: 1,
  },
  initiativeName: {
    color: '#d1d5db',
    fontSize: 14,
    fontWeight: '500',
  },
  initiativeMeta: {
    color: '#6b7280',
    fontSize: 11,
    marginTop: 2,
  },

  // Activity
  activityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  activityIcon: {
    fontSize: 16,
    width: 26,
    textAlign: 'center',
  },
  activityInfo: {
    flex: 1,
    marginLeft: 6,
  },
  activityTitle: {
    color: '#d1d5db',
    fontSize: 13,
    fontWeight: '500',
  },
  activitySubtitle: {
    color: '#6b7280',
    fontSize: 11,
    marginTop: 1,
  },
  activityTime: {
    color: '#4b5563',
    fontSize: 11,
    marginLeft: 8,
  },

  // Money-making verticals
  verticalsRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  verticalCard: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    alignItems: 'center',
    gap: 4,
  },
  verticalLabel: {
    color: '#9ca3af',
    fontSize: 11,
    fontWeight: '600',
  },
  verticalValue: {
    fontSize: 18,
    fontWeight: '800',
  },
  verticalMeta: {
    color: '#6b7280',
    fontSize: 10,
  },

  // Shared
  mutedText: {
    color: '#6b7280',
    fontSize: 13,
  },
});

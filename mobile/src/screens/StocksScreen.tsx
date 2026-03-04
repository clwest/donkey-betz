import React, { useCallback, useEffect, useState } from 'react';
import {
  Linking,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useScreenAnalytics } from '../observability/analytics';
import ScreenState from '../components/ScreenState';
import { SkeletonStatRow, SkeletonCard, SkeletonList } from '../components/Skeleton';
import * as stocksApi from '../api/stocks';
import type { StockHub, StockAlert, TickerLookup } from '../api/stocks';
import { useDemo } from '../demo/useDemo';
import * as demo from '../demo/demoData';

// ── Helpers ─────────────────────────────────────────────────────────────────

function alertTypeColor(type: string): { bg: string; text: string } {
  switch (type) {
    case 'high_conviction_bull': return { bg: 'rgba(34,197,94,0.15)', text: '#22c55e' };
    case 'high_conviction_bear': return { bg: 'rgba(239,68,68,0.15)', text: '#ef4444' };
    case 'debate_zone': return { bg: 'rgba(168,85,247,0.15)', text: '#a855f7' };
    case 'risk_alert': return { bg: 'rgba(249,115,22,0.15)', text: '#f97316' };
    case 'momentum_shift': return { bg: 'rgba(59,130,246,0.15)', text: '#3b82f6' };
    case 'institutional_activity': return { bg: 'rgba(6,182,212,0.15)', text: '#06b6d4' };
    case 'anomaly_detected': return { bg: 'rgba(234,179,8,0.15)', text: '#eab308' };
    case 'earnings_alert': return { bg: 'rgba(99,102,241,0.15)', text: '#6366f1' };
    default: return { bg: 'rgba(107,114,128,0.15)', text: '#6b7280' };
  }
}

function formatAlertType(type: string): string {
  return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function healthColor(health: string): string {
  switch (health.toLowerCase()) {
    case 'bullish': case 'strong': return '#22c55e';
    case 'bearish': case 'weak': return '#ef4444';
    case 'neutral': case 'mixed': return '#eab308';
    default: return '#6b7280';
  }
}

// ── Tabs ────────────────────────────────────────────────────────────────────

type Tab = 'hub' | 'alerts' | 'lookup';
const TABS: { key: Tab; label: string }[] = [
  { key: 'hub', label: 'Hub' },
  { key: 'alerts', label: 'Alerts' },
  { key: 'lookup', label: 'Ticker' },
];

// ── Main ────────────────────────────────────────────────────────────────────

export default function StocksScreen() {
  useScreenAnalytics('StocksScreen');
  const isDemo = useDemo();

  const [tab, setTab] = useState<Tab>('hub');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hub, setHub] = useState<StockHub | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchHub = useCallback(async () => {
    setError(null);

    if (isDemo) {
      setHub(demo.DEMO_STOCK_HUB as any);
      setLastUpdated(new Date());
      return;
    }

    try {
      const data = await stocksApi.getHub();
      setHub(data);
      setLastUpdated(new Date());
    } catch {
      setError('Failed to load stock intelligence.');
    }
  }, [isDemo]);

  useEffect(() => {
    fetchHub().finally(() => setLoading(false));
  }, [fetchHub]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchHub();
    setRefreshing(false);
  }, [fetchHub]);

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.content}>
          <View style={styles.tabBar}>
            {TABS.map((t) => (
              <View key={t.key} style={[styles.tab, t.key === 'hub' && styles.tabActive]}>
                <Text style={[styles.tabText, t.key === 'hub' && styles.tabTextActive]}>{t.label}</Text>
              </View>
            ))}
          </View>
          <SkeletonStatRow count={4} />
          <SkeletonCard lines={5} />
          <SkeletonList rows={4} />
        </View>
      </View>
    );
  }

  return (
    <ScreenState loading={false} error={error} onRetry={fetchHub}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" colors={['#6366f1']} />
        }
      >
        {/* Last updated */}
        {lastUpdated && (
          <Text style={styles.updatedText}>
            Updated {lastUpdated.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}
          </Text>
        )}

        <View style={styles.tabBar}>
          {TABS.map((t) => (
            <TouchableOpacity
              key={t.key}
              style={[styles.tab, tab === t.key && styles.tabActive]}
              onPress={() => setTab(t.key)}
            >
              <Text style={[styles.tabText, tab === t.key && styles.tabTextActive]}>{t.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {tab === 'hub' && <HubTab hub={hub} />}
        {tab === 'alerts' && <AlertsTab alerts={hub?.top_alerts ?? []} />}
        {tab === 'lookup' && <TickerTab />}

        <View style={{ height: 24 }} />
      </ScrollView>
    </ScreenState>
  );
}

// ── Hub Tab ─────────────────────────────────────────────────────────────────

function HubTab({ hub }: { hub: StockHub | null }) {
  if (!hub) return <Text style={styles.muted}>No data</Text>;

  const { stats, latest_brief, top_predictions, market_news } = hub;

  return (
    <>
      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <StatCard label="Briefs" value={String(stats.total_briefs)} color="#818cf8" />
        <StatCard label="Alerts" value={String(stats.total_alerts)} color="#f97316" />
        <StatCard label="7D Acc" value={stats.accuracy_7d !== null ? `${stats.accuracy_7d.toFixed(0)}%` : '--'} color="#22c55e" />
        <StatCard label="SEC" value={String(stats.sec_filings_count)} color="#06b6d4" />
      </View>

      {/* Latest Brief */}
      {latest_brief && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Latest Brief</Text>
            <Text style={[styles.healthBadge, { color: healthColor(latest_brief.situation_health) }]}>
              {latest_brief.situation_health}
            </Text>
          </View>
          <Text style={styles.briefDate}>{latest_brief.brief_date}</Text>
          <Text style={styles.briefSummary} numberOfLines={6}>{latest_brief.executive_summary}</Text>
          <View style={styles.briefStats}>
            <Text style={styles.briefStat}>{latest_brief.total_stocks_analyzed} stocks analyzed</Text>
            <Text style={styles.briefStat}>{latest_brief.debate_zone_count} in debate zone</Text>
          </View>
        </View>
      )}

      {/* Prediction Scorecard */}
      {top_predictions.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Prediction Scorecard</Text>
          {top_predictions.slice(0, 8).map((p) => (
            <View key={p.id} style={styles.predRow}>
              <Text style={styles.predTicker}>{p.ticker}</Text>
              <Text style={[styles.predType, {
                color: p.prediction_type === 'BULL' ? '#22c55e' : '#ef4444',
                backgroundColor: p.prediction_type === 'BULL' ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)',
              }]}>
                {p.prediction_type}
              </Text>
              <Text style={styles.predMove}>{p.predicted_move > 0 ? '+' : ''}{p.predicted_move.toFixed(1)}%</Text>
              <Text style={styles.predActual}>
                {p.actual_move_7_days !== null ? `${p.actual_move_7_days > 0 ? '+' : ''}${p.actual_move_7_days.toFixed(1)}%` : '...'}
              </Text>
              {p.was_correct_7_days !== null && (
                <Text style={[styles.predResult, { color: p.was_correct_7_days ? '#22c55e' : '#ef4444' }]}>
                  {p.was_correct_7_days ? 'W' : 'L'}
                </Text>
              )}
            </View>
          ))}
        </View>
      )}

      {/* Market News */}
      {market_news.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Market News</Text>
          {market_news.slice(0, 5).map((n, i) => (
            <TouchableOpacity
              key={i}
              style={styles.newsRow}
              onPress={() => n.link ? Linking.openURL(n.link) : null}
            >
              <Text style={styles.newsTitle} numberOfLines={2}>{n.title}</Text>
              <Text style={styles.newsMeta}>{n.source}{n.published ? ` · ${new Date(n.published).toLocaleDateString()}` : ''}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </>
  );
}

// ── Alerts Tab ──────────────────────────────────────────────────────────────

function AlertsTab({ alerts }: { alerts: StockAlert[] }) {
  if (alerts.length === 0) return <Text style={styles.muted}>No alerts</Text>;

  return (
    <>
      {alerts.map((alert) => {
        const typeStyle = alertTypeColor(alert.alert_type);
        const totalScore = alert.bull_score + alert.bear_score || 1;
        const bullPct = (alert.bull_score / totalScore) * 100;

        return (
          <View key={alert.id} style={styles.alertCard}>
            <View style={styles.alertHeader}>
              <Text style={styles.alertSymbol}>{alert.symbol}</Text>
              <Text style={[styles.alertType, { backgroundColor: typeStyle.bg, color: typeStyle.text }]}>
                {formatAlertType(alert.alert_type)}
              </Text>
            </View>
            <Text style={styles.alertTitle} numberOfLines={2}>{alert.title}</Text>
            <Text style={styles.alertSummary} numberOfLines={3}>{alert.summary}</Text>

            {/* Bull/Bear Bar */}
            <View style={styles.bbBar}>
              <View style={[styles.bbFill, { width: `${bullPct}%`, backgroundColor: '#22c55e' }]} />
              <View style={[styles.bbFill, { width: `${100 - bullPct}%`, backgroundColor: '#ef4444' }]} />
            </View>
            <View style={styles.bbLabels}>
              <Text style={styles.bbLabel}>Bull {alert.bull_score.toFixed(0)}</Text>
              <Text style={styles.bbLabel}>Bear {alert.bear_score.toFixed(0)}</Text>
            </View>

            <View style={styles.alertFooter}>
              <Text style={styles.alertConfidence}>Confidence: {(alert.confidence_score * 100).toFixed(0)}%</Text>
              {alert.current_price !== null && (
                <Text style={styles.alertPrice}>
                  ${alert.current_price.toFixed(2)}
                  {alert.price_change_24h !== null && (
                    <Text style={{ color: alert.price_change_24h >= 0 ? '#22c55e' : '#ef4444' }}>
                      {' '}{alert.price_change_24h >= 0 ? '+' : ''}{alert.price_change_24h.toFixed(2)}%
                    </Text>
                  )}
                </Text>
              )}
            </View>
          </View>
        );
      })}
    </>
  );
}

// ── Ticker Lookup Tab ───────────────────────────────────────────────────────

function TickerTab() {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [result, setResult] = useState<TickerLookup | null>(null);

  async function handleSearch() {
    const symbol = query.trim().toUpperCase();
    if (!symbol) return;
    setSearching(true);
    try {
      const data = await stocksApi.lookupTicker(symbol);
      setResult(data);
    } catch {
      setResult(null);
    } finally {
      setSearching(false);
    }
  }

  return (
    <>
      <View style={styles.searchRow}>
        <TextInput
          style={styles.searchInput}
          placeholder="Enter ticker (AAPL, TSLA...)"
          placeholderTextColor="#6b7280"
          value={query}
          onChangeText={setQuery}
          autoCapitalize="characters"
          returnKeyType="search"
          onSubmitEditing={handleSearch}
        />
        <TouchableOpacity style={styles.searchBtn} onPress={handleSearch} disabled={searching}>
          <Text style={styles.searchBtnText}>{searching ? '...' : 'Go'}</Text>
        </TouchableOpacity>
      </View>

      {result && result.live_quote && (
        <View style={styles.card}>
          <Text style={styles.tickerSymbol}>{result.symbol}</Text>
          <Text style={styles.tickerName}>{result.live_quote.company_name}</Text>
          <View style={styles.quoteRow}>
            <Text style={styles.tickerPrice}>${result.live_quote.current_price.toFixed(2)}</Text>
            <Text style={[styles.tickerChange, {
              color: result.live_quote.change_percent >= 0 ? '#22c55e' : '#ef4444',
            }]}>
              {result.live_quote.change_percent >= 0 ? '+' : ''}{result.live_quote.change_percent.toFixed(2)}%
            </Text>
          </View>
          <Text style={styles.tickerMeta}>{result.live_quote.sector} · {result.live_quote.industry}</Text>
        </View>
      )}

      {result && result.alerts.results.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Alerts ({result.alerts.total})</Text>
          {result.alerts.results.slice(0, 5).map((a) => {
            const typeStyle = alertTypeColor(a.alert_type);
            return (
              <View key={a.id} style={styles.miniAlertRow}>
                <Text style={[styles.alertType, { backgroundColor: typeStyle.bg, color: typeStyle.text }]}>
                  {formatAlertType(a.alert_type)}
                </Text>
                <Text style={styles.miniAlertTitle} numberOfLines={1}>{a.title}</Text>
              </View>
            );
          })}
        </View>
      )}

      {result && result.predictions.results.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Predictions ({result.predictions.total})</Text>
          {result.predictions.results.slice(0, 5).map((p) => (
            <View key={p.id} style={styles.predRow}>
              <Text style={[styles.predType, {
                color: p.prediction_type === 'BULL' ? '#22c55e' : '#ef4444',
                backgroundColor: p.prediction_type === 'BULL' ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)',
              }]}>
                {p.prediction_type}
              </Text>
              <Text style={styles.predMove}>{p.predicted_move > 0 ? '+' : ''}{p.predicted_move.toFixed(1)}%</Text>
              <Text style={styles.predActual}>
                {p.actual_move_7_days !== null ? `${p.actual_move_7_days > 0 ? '+' : ''}${p.actual_move_7_days.toFixed(1)}%` : 'pending'}
              </Text>
              <Text style={styles.predDate}>{p.prediction_date}</Text>
            </View>
          ))}
        </View>
      )}

      {result && !result.success && (
        <Text style={styles.muted}>No data found for {result.symbol}</Text>
      )}
    </>
  );
}

// ── Shared Subcomponents ────────────────────────────────────────────────────

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <View style={styles.statCard}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

// ── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 12 },
  muted: { color: '#6b7280', fontSize: 14, textAlign: 'center', marginTop: 40 },
  updatedText: { color: '#4b5563', fontSize: 10, textAlign: 'right', marginBottom: 4 },

  tabBar: { flexDirection: 'row', marginBottom: 12, gap: 8 },
  tab: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 8, backgroundColor: '#1a1a2e' },
  tabActive: { backgroundColor: '#6366f1' },
  tabText: { color: '#9ca3af', fontSize: 13, fontWeight: '600' },
  tabTextActive: { color: '#ffffff' },

  statsGrid: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  statCard: { flex: 1, backgroundColor: '#1a1a2e', borderRadius: 10, padding: 12, alignItems: 'center' },
  statValue: { fontSize: 18, fontWeight: '800' },
  statLabel: { color: '#6b7280', fontSize: 11, marginTop: 4 },

  card: { backgroundColor: '#1a1a2e', borderRadius: 12, padding: 14, marginBottom: 10 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  cardTitle: { color: '#ffffff', fontSize: 15, fontWeight: '700', marginBottom: 10 },

  // Brief
  healthBadge: { fontSize: 12, fontWeight: '700', textTransform: 'uppercase' },
  briefDate: { color: '#6b7280', fontSize: 12, marginBottom: 8 },
  briefSummary: { color: '#d1d5db', fontSize: 13, lineHeight: 20 },
  briefStats: { flexDirection: 'row', gap: 16, marginTop: 10 },
  briefStat: { color: '#9ca3af', fontSize: 12 },

  // Predictions
  predRow: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 6, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)' },
  predTicker: { color: '#ffffff', fontSize: 13, fontWeight: '700', width: 50 },
  predType: { fontSize: 10, fontWeight: '700', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  predMove: { color: '#d1d5db', fontSize: 12, width: 50, textAlign: 'right' },
  predActual: { color: '#9ca3af', fontSize: 12, flex: 1, textAlign: 'right' },
  predResult: { fontSize: 12, fontWeight: '800', width: 20, textAlign: 'center' },
  predDate: { color: '#6b7280', fontSize: 10 },

  // News
  newsRow: { paddingVertical: 10, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)' },
  newsTitle: { color: '#d1d5db', fontSize: 13, fontWeight: '500' },
  newsMeta: { color: '#6b7280', fontSize: 11, marginTop: 4 },

  // Alerts
  alertCard: { backgroundColor: '#1a1a2e', borderRadius: 12, padding: 14, marginBottom: 10 },
  alertHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  alertSymbol: { color: '#ffffff', fontSize: 18, fontWeight: '800' },
  alertType: { fontSize: 10, fontWeight: '700', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  alertTitle: { color: '#d1d5db', fontSize: 14, fontWeight: '600', marginBottom: 6 },
  alertSummary: { color: '#9ca3af', fontSize: 13, lineHeight: 19, marginBottom: 10 },
  bbBar: { flexDirection: 'row', height: 6, borderRadius: 3, overflow: 'hidden' },
  bbFill: { height: 6 },
  bbLabels: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 },
  bbLabel: { color: '#6b7280', fontSize: 10 },
  alertFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 10 },
  alertConfidence: { color: '#818cf8', fontSize: 11, fontWeight: '600' },
  alertPrice: { color: '#d1d5db', fontSize: 12, fontWeight: '500' },

  // Ticker Lookup
  searchRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  searchInput: { flex: 1, backgroundColor: '#1a1a2e', borderRadius: 8, paddingHorizontal: 14, paddingVertical: 12, color: '#ffffff', fontSize: 16, fontWeight: '600' },
  searchBtn: { backgroundColor: '#6366f1', borderRadius: 8, paddingHorizontal: 20, justifyContent: 'center' },
  searchBtnText: { color: '#ffffff', fontSize: 14, fontWeight: '700' },
  tickerSymbol: { color: '#ffffff', fontSize: 24, fontWeight: '800' },
  tickerName: { color: '#9ca3af', fontSize: 14, marginTop: 2 },
  quoteRow: { flexDirection: 'row', alignItems: 'baseline', gap: 10, marginTop: 8 },
  tickerPrice: { color: '#ffffff', fontSize: 28, fontWeight: '800' },
  tickerChange: { fontSize: 16, fontWeight: '700' },
  tickerMeta: { color: '#6b7280', fontSize: 12, marginTop: 6 },

  miniAlertRow: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 6, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)' },
  miniAlertTitle: { color: '#d1d5db', fontSize: 12, flex: 1 },
});

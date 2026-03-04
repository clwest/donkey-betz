import React, { useCallback, useEffect, useState } from 'react';
import {
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useScreenAnalytics } from '../observability/analytics';
import ScreenState from '../components/ScreenState';
import { SkeletonStatRow, SkeletonCard, SkeletonList } from '../components/Skeleton';
import * as bettingApi from '../api/betting';
import type { BettingStats, Game, Wager } from '../api/betting';
import { useDemo } from '../demo/useDemo';
import * as demo from '../demo/demoData';

// ── Helpers ─────────────────────────────────────────────────────────────────

function currency(n: number): string {
  return n >= 0 ? `$${n.toFixed(2)}` : `-$${Math.abs(n).toFixed(2)}`;
}

function pct(n: number): string {
  return `${n.toFixed(1)}%`;
}

function statusColor(status: string): string {
  switch (status) {
    case 'won': return '#22c55e';
    case 'lost': return '#ef4444';
    case 'push': return '#a855f7';
    case 'pending': return '#eab308';
    case 'cancelled': return '#6b7280';
    default: return '#6b7280';
  }
}

function gameTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

// ── Tabs ────────────────────────────────────────────────────────────────────

type Tab = 'overview' | 'games' | 'wagers';
const TABS: { key: Tab; label: string }[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'games', label: "Today's Games" },
  { key: 'wagers', label: 'My Wagers' },
];

// ── Main ────────────────────────────────────────────────────────────────────

export default function BettingScreen() {
  useScreenAnalytics('BettingScreen');
  const isDemo = useDemo();

  const [tab, setTab] = useState<Tab>('overview');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [stats, setStats] = useState<BettingStats | null>(null);
  const [games, setGames] = useState<Game[]>([]);
  const [wagers, setWagers] = useState<Wager[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchAll = useCallback(async () => {
    setError(null);

    if (isDemo) {
      setStats(demo.DEMO_BETTING_STATS);
      setGames(demo.DEMO_GAMES);
      setWagers(demo.DEMO_WAGERS as any);
      setLastUpdated(new Date());
      return;
    }

    const results = await Promise.allSettled([
      bettingApi.getStats(),
      bettingApi.getTodaysGames(),
      bettingApi.getRecentWagers(20),
    ]);
    if (results[0].status === 'fulfilled') setStats(results[0].value);
    if (results[1].status === 'fulfilled') setGames(results[1].value);
    if (results[2].status === 'fulfilled') setWagers(results[2].value);
    if (results.every((r) => r.status === 'rejected')) {
      setError('Failed to load betting data. Pull to retry.');
    } else {
      setLastUpdated(new Date());
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
      <View style={styles.container}>
        <View style={styles.content}>
          <View style={styles.tabBar}>
            {TABS.map((t) => (
              <View key={t.key} style={[styles.tab, t.key === 'overview' && styles.tabActive]}>
                <Text style={[styles.tabText, t.key === 'overview' && styles.tabTextActive]}>{t.label}</Text>
              </View>
            ))}
          </View>
          <SkeletonStatRow count={4} />
          <SkeletonCard lines={4} />
          <SkeletonList rows={3} />
        </View>
      </View>
    );
  }

  return (
    <ScreenState loading={false} error={error} onRetry={fetchAll}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" colors={['#6366f1']} />
        }
      >
        {/* Last updated */}
        {lastUpdated && (
          <Text style={styles.updatedText}>Updated {timeAgo(lastUpdated.toISOString())}</Text>
        )}

        {/* Tab Bar */}
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

        {tab === 'overview' && <OverviewTab stats={stats} wagers={wagers} />}
        {tab === 'games' && <GamesTab games={games} />}
        {tab === 'wagers' && <WagersTab wagers={wagers} />}

        <View style={{ height: 24 }} />
      </ScrollView>
    </ScreenState>
  );
}

// ── Overview Tab ────────────────────────────────────────────────────────────

function OverviewTab({ stats, wagers }: { stats: BettingStats | null; wagers: Wager[] }) {
  if (!stats) return <Text style={styles.muted}>No stats available</Text>;

  const plColor = stats.total_profit_loss >= 0 ? '#22c55e' : '#ef4444';
  const streakColor = stats.current_streak >= 0 ? '#22c55e' : '#ef4444';
  const streakText = stats.current_streak >= 0 ? `W${stats.current_streak}` : `L${Math.abs(stats.current_streak)}`;

  return (
    <>
      {/* Primary Stats */}
      <View style={styles.statsGrid}>
        <StatCard label="Total P/L" value={currency(stats.total_profit_loss)} color={plColor} />
        <StatCard label="Win Rate" value={pct(stats.win_rate)} color="#818cf8" />
        <StatCard label="ROI" value={pct(stats.roi)} color={stats.roi >= 0 ? '#22c55e' : '#ef4444'} />
        <StatCard label="Pending" value={String(stats.pending)} color="#eab308" />
      </View>

      {/* Streak & Records */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Record</Text>
        <View style={styles.recordRow}>
          <RecordItem label="Wins" value={stats.wins} color="#22c55e" />
          <RecordItem label="Losses" value={stats.losses} color="#ef4444" />
          <RecordItem label="Pushes" value={stats.pushes} color="#a855f7" />
          <RecordItem label="Streak" value={streakText} color={streakColor} isText />
        </View>
      </View>

      {/* Singles vs Parlays */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Singles vs Parlays</Text>
        <View style={styles.compareRow}>
          <View style={styles.compareCol}>
            <Text style={styles.compareLabel}>Singles</Text>
            <Text style={styles.compareValue}>
              {stats.singles_record.wins}W - {stats.singles_record.losses}L
            </Text>
            <Text style={[styles.comparePL, { color: stats.singles_record.profit >= 0 ? '#22c55e' : '#ef4444' }]}>
              {currency(stats.singles_record.profit)}
            </Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.compareCol}>
            <Text style={styles.compareLabel}>Parlays</Text>
            <Text style={styles.compareValue}>
              {stats.parlays_record.wins}W - {stats.parlays_record.losses}L
            </Text>
            <Text style={[styles.comparePL, { color: stats.parlays_record.profit >= 0 ? '#22c55e' : '#ef4444' }]}>
              {currency(stats.parlays_record.profit)}
            </Text>
          </View>
        </View>
      </View>

      {/* Recent Wagers Preview */}
      {wagers.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recent Wagers</Text>
          {wagers.slice(0, 5).map((w) => (
            <WagerRow key={w.id} wager={w} />
          ))}
        </View>
      )}
    </>
  );
}

// ── Today's Games Tab ───────────────────────────────────────────────────────

function GamesTab({ games }: { games: Game[] }) {
  if (games.length === 0) return <Text style={styles.muted}>No games today</Text>;

  const live = games.filter((g) => !g.completed && g.home_score !== null);
  const upcoming = games.filter((g) => !g.completed && g.home_score === null);
  const completed = games.filter((g) => g.completed);

  return (
    <>
      {/* Stats Strip */}
      <View style={styles.statsGrid}>
        <StatCard label="Live" value={String(live.length)} color="#ef4444" />
        <StatCard label="Upcoming" value={String(upcoming.length)} color="#818cf8" />
        <StatCard label="AI Picks" value={String(games.filter((g) => g.predicted_winner).length)} color="#a855f7" />
        <StatCard label="Final" value={String(completed.length)} color="#6b7280" />
      </View>

      {/* Live Games */}
      {live.length > 0 && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Live</Text>
            <View style={styles.liveDot} />
          </View>
          {live.map((g) => <GameRow key={g.event_id} game={g} />)}
        </View>
      )}

      {/* Upcoming */}
      {upcoming.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Upcoming</Text>
          {upcoming.map((g) => <GameRow key={g.event_id} game={g} />)}
        </View>
      )}

      {/* Completed */}
      {completed.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Completed</Text>
          {completed.map((g) => <GameRow key={g.event_id} game={g} />)}
        </View>
      )}
    </>
  );
}

// ── Wagers Tab ──────────────────────────────────────────────────────────────

function WagersTab({ wagers }: { wagers: Wager[] }) {
  if (wagers.length === 0) return <Text style={styles.muted}>No wagers yet</Text>;

  const pending = wagers.filter((w) => w.status === 'pending');
  const settled = wagers.filter((w) => w.status !== 'pending');

  return (
    <>
      {pending.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Pending ({pending.length})</Text>
          {pending.map((w) => <WagerRow key={w.id} wager={w} expanded />)}
        </View>
      )}
      {settled.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Settled</Text>
          {settled.map((w) => <WagerRow key={w.id} wager={w} />)}
        </View>
      )}
    </>
  );
}

// ── Subcomponents ───────────────────────────────────────────────────────────

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <View style={styles.statCard}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function RecordItem({ label, value, color, isText }: { label: string; value: number | string; color: string; isText?: boolean }) {
  return (
    <View style={styles.recordItem}>
      <Text style={[styles.recordValue, { color }]}>{isText ? value : String(value)}</Text>
      <Text style={styles.recordLabel}>{label}</Text>
    </View>
  );
}

function GameRow({ game }: { game: Game }) {
  const isLive = !game.completed && game.home_score !== null;
  const hasScore = game.home_score !== null && game.away_score !== null;

  return (
    <View style={styles.gameRow}>
      <View style={styles.gameInfo}>
        <View style={styles.gameTeams}>
          <Text style={styles.teamName} numberOfLines={1}>{game.away_team}</Text>
          <Text style={styles.vsText}>@</Text>
          <Text style={styles.teamName} numberOfLines={1}>{game.home_team}</Text>
        </View>
        <View style={styles.gameMeta}>
          <Text style={[styles.sportBadge, { backgroundColor: 'rgba(99,102,241,0.15)' }]}>
            {game.sport_name || game.sport_key}
          </Text>
          {isLive && <Text style={styles.liveTag}>LIVE</Text>}
          {!isLive && !game.completed && (
            <Text style={styles.gameTimeText}>{gameTime(game.commence_time)}</Text>
          )}
          {game.predicted_winner && (
            <Text style={styles.aiPick}>AI: {game.predicted_winner}</Text>
          )}
        </View>
      </View>
      {hasScore && (
        <View style={styles.scoreBox}>
          <Text style={styles.score}>{game.away_score}</Text>
          <Text style={styles.scoreDash}>-</Text>
          <Text style={styles.score}>{game.home_score}</Text>
        </View>
      )}
    </View>
  );
}

function WagerRow({ wager, expanded }: { wager: Wager; expanded?: boolean }) {
  const isParlay = wager.type === 'parlay' && wager.legs.length > 0;
  const pick = isParlay ? `${wager.legs.length}-Leg Parlay` : (wager.pick || wager.matchup || wager.bet_type);

  return (
    <View style={styles.wagerRow}>
      <View style={styles.wagerInfo}>
        <Text style={styles.wagerPick} numberOfLines={1}>{pick}</Text>
        <Text style={styles.wagerMeta}>
          {wager.sport ? `${wager.sport} · ` : ''}{currency(wager.stake)} @ {wager.odds > 0 ? '+' : ''}{wager.odds}
        </Text>
        {expanded && isParlay && wager.legs.map((leg, i) => (
          <Text key={i} style={styles.wagerLeg} numberOfLines={1}>
            {leg.matchup}: {leg.pick} ({leg.odds > 0 ? '+' : ''}{leg.odds})
          </Text>
        ))}
      </View>
      <View style={styles.wagerRight}>
        <Text style={[styles.wagerStatus, { color: statusColor(wager.status) }]}>
          {wager.status.toUpperCase()}
        </Text>
        {wager.profit_loss !== null && (
          <Text style={[styles.wagerPL, { color: wager.profit_loss >= 0 ? '#22c55e' : '#ef4444' }]}>
            {currency(wager.profit_loss)}
          </Text>
        )}
        <Text style={styles.wagerTime}>{timeAgo(wager.placed_at || wager.created_at)}</Text>
      </View>
    </View>
  );
}

// ── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 12 },
  muted: { color: '#6b7280', fontSize: 14, textAlign: 'center', marginTop: 40 },
  updatedText: { color: '#4b5563', fontSize: 10, textAlign: 'right', marginBottom: 4 },

  // Tabs
  tabBar: { flexDirection: 'row', marginBottom: 12, gap: 8 },
  tab: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 8, backgroundColor: '#1a1a2e' },
  tabActive: { backgroundColor: '#6366f1' },
  tabText: { color: '#9ca3af', fontSize: 13, fontWeight: '600' },
  tabTextActive: { color: '#ffffff' },

  // Stats Grid
  statsGrid: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  statCard: { flex: 1, backgroundColor: '#1a1a2e', borderRadius: 10, padding: 12, alignItems: 'center' },
  statValue: { fontSize: 18, fontWeight: '800' },
  statLabel: { color: '#6b7280', fontSize: 11, marginTop: 4 },

  // Cards
  card: { backgroundColor: '#1a1a2e', borderRadius: 12, padding: 14, marginBottom: 10 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  cardTitle: { color: '#ffffff', fontSize: 15, fontWeight: '700', marginBottom: 10 },

  // Record
  recordRow: { flexDirection: 'row', justifyContent: 'space-around' },
  recordItem: { alignItems: 'center' },
  recordValue: { fontSize: 22, fontWeight: '800' },
  recordLabel: { color: '#6b7280', fontSize: 11, marginTop: 2 },

  // Compare
  compareRow: { flexDirection: 'row', alignItems: 'center' },
  compareCol: { flex: 1, alignItems: 'center' },
  compareLabel: { color: '#818cf8', fontSize: 12, fontWeight: '700', textTransform: 'uppercase', marginBottom: 6 },
  compareValue: { color: '#d1d5db', fontSize: 14, fontWeight: '600' },
  comparePL: { fontSize: 16, fontWeight: '700', marginTop: 4 },
  divider: { width: 1, height: 50, backgroundColor: 'rgba(255,255,255,0.1)' },

  // Games
  gameRow: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingVertical: 10, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)',
  },
  gameInfo: { flex: 1 },
  gameTeams: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  teamName: { color: '#d1d5db', fontSize: 14, fontWeight: '500', maxWidth: '40%' },
  vsText: { color: '#6b7280', fontSize: 12 },
  gameMeta: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 4 },
  sportBadge: { color: '#818cf8', fontSize: 10, fontWeight: '600', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  liveTag: { color: '#ef4444', fontSize: 10, fontWeight: '800', backgroundColor: 'rgba(239,68,68,0.15)', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  gameTimeText: { color: '#6b7280', fontSize: 11 },
  aiPick: { color: '#a855f7', fontSize: 10, fontWeight: '600', backgroundColor: 'rgba(168,85,247,0.15)', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  scoreBox: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  score: { color: '#ffffff', fontSize: 18, fontWeight: '800' },
  scoreDash: { color: '#6b7280', fontSize: 14 },
  liveDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#ef4444' },

  // Wagers
  wagerRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    paddingVertical: 10, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)',
  },
  wagerInfo: { flex: 1, marginRight: 12 },
  wagerPick: { color: '#d1d5db', fontSize: 14, fontWeight: '500' },
  wagerMeta: { color: '#6b7280', fontSize: 12, marginTop: 2 },
  wagerLeg: { color: '#9ca3af', fontSize: 11, marginTop: 2, marginLeft: 8 },
  wagerRight: { alignItems: 'flex-end' },
  wagerStatus: { fontSize: 11, fontWeight: '700' },
  wagerPL: { fontSize: 14, fontWeight: '700', marginTop: 2 },
  wagerTime: { color: '#4b5563', fontSize: 10, marginTop: 2 },
});

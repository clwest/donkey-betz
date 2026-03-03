import React, { useCallback, useEffect, useState } from 'react';
import {
  FlatList,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import {
  getFailureStats,
  listSessions,
  getSession,
  type FailureStats,
  type DeliberationSession,
  type SessionDetail,
} from '../../api/deliberation';

// ── Reason code labels & colors ──────────────────────────────────────────────

const REASON_META: Record<string, { label: string; color: string }> = {
  TIMEOUT: { label: 'Timeout', color: '#f59e0b' },
  LLM_UPSTREAM: { label: 'LLM Error', color: '#ef4444' },
  EMPTY_TURN: { label: 'Empty Turn', color: '#ec4899' },
  TOOL_ERROR: { label: 'Tool Error', color: '#f97316' },
  GATE_REJECT: { label: 'Gate Reject', color: '#8b5cf6' },
  DRAFT_FAILED: { label: 'Draft Failed', color: '#64748b' },
  UNKNOWN: { label: 'Unknown', color: '#6b7280' },
};

function reasonLabel(code: string) {
  return REASON_META[code]?.label ?? code;
}

function reasonColor(code: string) {
  return REASON_META[code]?.color ?? '#6b7280';
}

function statusColor(status: string) {
  switch (status) {
    case 'completed': return '#22c55e';
    case 'active': return '#3b82f6';
    case 'failed': return '#ef4444';
    default: return '#6b7280';
  }
}

function timeAgo(iso: string | null): string {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── View state ───────────────────────────────────────────────────────────────

type HomeView =
  | { screen: 'overview' }
  | { screen: 'sessions' }
  | { screen: 'detail'; id: string };

type Tab = 'failures' | 'sessions';

// ── Main Screen ──────────────────────────────────────────────────────────────

export default function DeliberationHomeScreen() {
  const [tab, setTab] = useState<Tab>('failures');
  const [view, setView] = useState<HomeView>({ screen: 'overview' });

  if (view.screen === 'detail') {
    return <SessionDetailView sessionId={view.id} onBack={() => setView({ screen: 'overview' })} />;
  }

  return (
    <View style={styles.container}>
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, tab === 'failures' && styles.tabActive]}
          onPress={() => setTab('failures')}
        >
          <Text style={[styles.tabText, tab === 'failures' && styles.tabTextActive]}>
            Failures (24h)
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, tab === 'sessions' && styles.tabActive]}
          onPress={() => setTab('sessions')}
        >
          <Text style={[styles.tabText, tab === 'sessions' && styles.tabTextActive]}>
            Sessions
          </Text>
        </TouchableOpacity>
      </View>

      {tab === 'failures' ? (
        <FailuresTab onSelect={(id) => setView({ screen: 'detail', id })} />
      ) : (
        <SessionsTab onSelect={(id) => setView({ screen: 'detail', id })} />
      )}
    </View>
  );
}

// ── Failures Tab ─────────────────────────────────────────────────────────────

function FailuresTab({ onSelect }: { onSelect: (id: string) => void }) {
  const [stats, setStats] = useState<FailureStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetch = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getFailureStats(24);
      setStats(data);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  if (loading && !stats) {
    return <Text style={styles.muted}>Loading failure stats...</Text>;
  }
  if (error) {
    return <Text style={styles.errorText}>{error}</Text>;
  }
  if (!stats) return null;

  const maxCount = Math.max(...Object.values(stats.by_reason), 1);
  const sortedReasons = Object.entries(stats.by_reason).sort((a, b) => b[1] - a[1]);

  return (
    <ScrollView
      style={styles.scrollFlex}
      contentContainerStyle={styles.scrollContent}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={fetch} tintColor="#6366f1" />}
    >
      {/* Summary cards */}
      <View style={styles.statsRow}>
        <StatCard label="Total" value={String(stats.total_sessions)} color="#d1d5db" />
        <StatCard label="Failed" value={String(stats.total_failed)} color="#ef4444" />
        <StatCard
          label="Rate"
          value={`${(stats.failure_rate * 100).toFixed(1)}%`}
          color={stats.failure_rate > 0.1 ? '#ef4444' : '#22c55e'}
        />
      </View>

      {/* Breakdown bars */}
      {sortedReasons.length > 0 ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Breakdown by Reason</Text>
          {sortedReasons.map(([code, count]) => (
            <View key={code} style={styles.barRow}>
              <View style={styles.barLabel}>
                <View style={[styles.dot, { backgroundColor: reasonColor(code) }]} />
                <Text style={styles.barLabelText}>{reasonLabel(code)}</Text>
              </View>
              <View style={styles.barTrack}>
                <View
                  style={[
                    styles.barFill,
                    {
                      width: `${(count / maxCount) * 100}%`,
                      backgroundColor: reasonColor(code),
                    },
                  ]}
                />
              </View>
              <Text style={styles.barCount}>{count}</Text>
            </View>
          ))}
        </View>
      ) : (
        <View style={styles.section}>
          <Text style={styles.successText}>No failures in the last 24 hours</Text>
        </View>
      )}

      {/* Recent failures */}
      {stats.recent_failures.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Failures</Text>
          {stats.recent_failures.map((f) => (
            <TouchableOpacity
              key={f.id}
              style={styles.failureRow}
              onPress={() => onSelect(f.id)}
            >
              <View style={styles.failureHeader}>
                <View style={[styles.badge, { backgroundColor: `${reasonColor(f.failure_reason_code)}30` }]}>
                  <Text style={[styles.badgeText, { color: reasonColor(f.failure_reason_code) }]}>
                    {reasonLabel(f.failure_reason_code)}
                  </Text>
                </View>
                <Text style={styles.timeText}>{timeAgo(f.created_at)}</Text>
              </View>
              <Text style={styles.objectiveText} numberOfLines={2}>
                {f.objective || 'No objective'}
              </Text>
              {f.failure_detail ? (
                <Text style={styles.detailText} numberOfLines={2}>
                  {f.failure_detail}
                </Text>
              ) : null}
            </TouchableOpacity>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

// ── Sessions Tab ─────────────────────────────────────────────────────────────

function SessionsTab({ onSelect }: { onSelect: (id: string) => void }) {
  const [sessions, setSessions] = useState<DeliberationSession[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listSessions({ limit: 30 });
      setSessions(data.sessions);
    } catch {
      // swallow
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const renderItem = useCallback(({ item }: { item: DeliberationSession }) => (
    <TouchableOpacity style={styles.sessionRow} onPress={() => onSelect(item.id)}>
      <View style={styles.sessionHeader}>
        <View style={[styles.badge, { backgroundColor: `${statusColor(item.status)}30` }]}>
          <Text style={[styles.badgeText, { color: statusColor(item.status) }]}>
            {item.status}
          </Text>
        </View>
        <Text style={styles.sessionMeta}>
          {item.turn_count}t · {item.participant_count}p
        </Text>
        <Text style={styles.timeText}>{timeAgo(item.created_at)}</Text>
      </View>
      <Text style={styles.objectiveText} numberOfLines={2}>
        {item.objective || 'No objective'}
      </Text>
      {item.failure_reason_code ? (
        <View style={[styles.badge, { backgroundColor: `${reasonColor(item.failure_reason_code)}30`, marginTop: 6 }]}>
          <Text style={[styles.badgeText, { color: reasonColor(item.failure_reason_code) }]}>
            {reasonLabel(item.failure_reason_code)}
          </Text>
        </View>
      ) : null}
      {item.blog ? (
        <Text style={styles.blogLink}>
          Blog: {item.blog.title?.slice(0, 40)} ({item.blog.status})
        </Text>
      ) : null}
    </TouchableOpacity>
  ), [onSelect]);

  return (
    <FlatList
      data={sessions}
      keyExtractor={(s) => s.id}
      renderItem={renderItem}
      contentContainerStyle={{ paddingVertical: 8 }}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={fetch} tintColor="#6366f1" />}
      ListEmptyComponent={
        loading ? null : <Text style={styles.muted}>No sessions found</Text>
      }
    />
  );
}

// ── Session Detail ───────────────────────────────────────────────────────────

function SessionDetailView({ sessionId, onBack }: { sessionId: string; onBack: () => void }) {
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getSession(sessionId);
        setSession(data);
      } catch {
        // swallow
      } finally {
        setLoading(false);
      }
    })();
  }, [sessionId]);

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.muted}>Loading session...</Text>
      </View>
    );
  }

  if (!session) {
    return (
      <View style={styles.container}>
        <TouchableOpacity onPress={onBack} style={styles.backBtn}>
          <Text style={styles.backText}>Back</Text>
        </TouchableOpacity>
        <Text style={styles.errorText}>Session not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <TouchableOpacity onPress={onBack} style={styles.backBtn}>
        <Text style={styles.backText}>Back</Text>
      </TouchableOpacity>

      {/* Header */}
      <View style={styles.detailHeader}>
        <View style={[styles.badge, { backgroundColor: `${statusColor(session.status)}30` }]}>
          <Text style={[styles.badgeText, { color: statusColor(session.status) }]}>
            {session.status}
          </Text>
        </View>
        <Text style={styles.detailType}>{session.session_type}</Text>
        <Text style={styles.timeText}>{timeAgo(session.created_at)}</Text>
      </View>

      {/* Objective */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Objective</Text>
        <Text style={styles.detailBody} selectable>{session.objective || 'None'}</Text>
      </View>

      {/* Failure info */}
      {session.failure_reason_code ? (
        <View style={[styles.section, { borderLeftWidth: 3, borderLeftColor: reasonColor(session.failure_reason_code) }]}>
          <Text style={styles.sectionTitle}>Failure</Text>
          <View style={[styles.badge, { backgroundColor: `${reasonColor(session.failure_reason_code)}30`, marginBottom: 8 }]}>
            <Text style={[styles.badgeText, { color: reasonColor(session.failure_reason_code) }]}>
              {reasonLabel(session.failure_reason_code)}
            </Text>
          </View>
          {session.failure_detail ? (
            <Text style={styles.detailBody} selectable>{session.failure_detail}</Text>
          ) : (
            <Text style={styles.muted}>No detail provided</Text>
          )}
        </View>
      ) : null}

      {/* Participants */}
      {session.participants?.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Participants ({session.participants.length})
          </Text>
          {session.participants.map((p, i) => (
            <Text key={i} style={styles.participant}>
              {typeof p === 'string' ? p : p.name ?? 'Unknown'}{p.type ? ` (${p.type})` : ''}
            </Text>
          ))}
        </View>
      )}

      {/* Turns */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Turns ({session.turns?.length ?? 0})</Text>
        {session.turns?.length ? (
          session.turns.map((t) => (
            <View key={t.turn_number} style={styles.turnCard}>
              <View style={styles.turnHeader}>
                <Text style={styles.turnAgent}>{t.agent_name}</Text>
                <Text style={styles.turnRole}>{t.role}</Text>
                <Text style={styles.turnNum}>#{t.turn_number}</Text>
              </View>
              <Text style={styles.turnContent} numberOfLines={6} selectable>
                {t.content}
              </Text>
            </View>
          ))
        ) : (
          <Text style={styles.muted}>No turns recorded (zero-turn session)</Text>
        )}
      </View>

      {/* Contracts */}
      {session.contracts?.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Contracts ({session.contracts.length})</Text>
          {session.contracts.map((c, i) => (
            <View key={i} style={styles.contractCard}>
              <Text style={styles.contractType}>{c.contract_type}</Text>
              <Text style={styles.detailBody} numberOfLines={4}>
                {JSON.stringify(c.contract_data, null, 2)}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* Trace ID */}
      {session.trace_id ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Trace</Text>
          <Text style={styles.detailBody} selectable>{session.trace_id}</Text>
        </View>
      ) : null}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ── Stat card helper ─────────────────────────────────────────────────────────

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <View style={styles.statCard}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  scrollFlex: { flex: 1 },
  scrollContent: { padding: 14 },
  muted: { color: '#6b7280', fontSize: 13, padding: 16 },
  errorText: { color: '#ef4444', fontSize: 13, padding: 16 },
  successText: { color: '#22c55e', fontSize: 14, textAlign: 'center', padding: 20 },

  // Tab bar
  tabBar: { flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: '#1a1a2e' },
  tab: {
    flex: 1, paddingVertical: 12, alignItems: 'center',
    borderBottomWidth: 2, borderBottomColor: 'transparent',
  },
  tabActive: { borderBottomColor: '#6366f1' },
  tabText: { color: '#6b7280', fontSize: 15, fontWeight: '600' },
  tabTextActive: { color: '#6366f1' },

  // Stats row
  statsRow: { flexDirection: 'row', gap: 8, marginBottom: 14 },
  statCard: {
    flex: 1, backgroundColor: '#1a1a2e', borderRadius: 10, padding: 14, alignItems: 'center',
  },
  statValue: { fontSize: 22, fontWeight: '700' },
  statLabel: { color: '#6b7280', fontSize: 11, marginTop: 4 },

  // Section
  section: {
    backgroundColor: '#1a1a2e', borderRadius: 10, padding: 14, marginBottom: 10,
  },
  sectionTitle: {
    color: '#818cf8', fontSize: 12, fontWeight: '700',
    textTransform: 'uppercase', marginBottom: 10,
  },

  // Bar chart
  barRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  barLabel: { flexDirection: 'row', alignItems: 'center', width: 100 },
  dot: { width: 8, height: 8, borderRadius: 4, marginRight: 6 },
  barLabelText: { color: '#d1d5db', fontSize: 12 },
  barTrack: {
    flex: 1, height: 14, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 4,
    marginHorizontal: 8, overflow: 'hidden',
  },
  barFill: { height: '100%', borderRadius: 4, minWidth: 4 },
  barCount: { color: '#9ca3af', fontSize: 12, width: 28, textAlign: 'right' },

  // Failure row
  failureRow: {
    backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 8,
    padding: 12, marginBottom: 8,
  },
  failureHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6,
  },

  // Badge
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, alignSelf: 'flex-start' },
  badgeText: { fontSize: 11, fontWeight: '700', textTransform: 'uppercase' },

  // Text
  objectiveText: { color: '#e5e7eb', fontSize: 13, lineHeight: 18 },
  detailText: { color: '#9ca3af', fontSize: 12, marginTop: 4, lineHeight: 16 },
  timeText: { color: '#6b7280', fontSize: 11 },

  // Session row
  sessionRow: {
    backgroundColor: '#1a1a2e', borderRadius: 10, padding: 14,
    marginHorizontal: 12, marginVertical: 4,
  },
  sessionHeader: {
    flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 6,
  },
  sessionMeta: { color: '#9ca3af', fontSize: 11, flex: 1 },
  blogLink: { color: '#818cf8', fontSize: 11, marginTop: 6 },

  // Detail view
  backBtn: { paddingHorizontal: 14, paddingVertical: 12 },
  backText: { color: '#6366f1', fontSize: 15, fontWeight: '600' },
  detailHeader: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingHorizontal: 14, marginBottom: 10,
  },
  detailType: { color: '#9ca3af', fontSize: 13, flex: 1 },
  detailBody: { color: '#d1d5db', fontSize: 13, lineHeight: 18 },

  // Participants
  participant: { color: '#d1d5db', fontSize: 13, paddingVertical: 2 },

  // Turns
  turnCard: {
    backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 8,
    padding: 10, marginBottom: 8,
  },
  turnHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 6 },
  turnAgent: { color: '#818cf8', fontSize: 12, fontWeight: '600' },
  turnRole: { color: '#6b7280', fontSize: 11, flex: 1 },
  turnNum: { color: '#6b7280', fontSize: 11 },
  turnContent: { color: '#d1d5db', fontSize: 12, lineHeight: 17 },

  // Contracts
  contractCard: {
    backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 8,
    padding: 10, marginBottom: 8,
  },
  contractType: {
    color: '#f59e0b', fontSize: 11, fontWeight: '700',
    textTransform: 'uppercase', marginBottom: 6,
  },
});

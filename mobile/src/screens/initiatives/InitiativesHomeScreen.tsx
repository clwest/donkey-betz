import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import Markdown from 'react-native-markdown-display';
import * as initiativesApi from '../../api/initiatives';
import CopyId from '../../components/CopyId';
import { toast } from '../../components/Toast';
import type {
  ActionItemsResponse,
  InitiativeActionItem,
  InitiativeListItem,
  InitiativeListResponse,
  InitiativeStatus,
} from '../../api/types/initiatives';

// ── Helpers ──────────────────────────────────────────────────────────────────

function statusColor(s: string): string {
  switch (s.toUpperCase()) {
    case 'ACTIVE':    return '#22c55e';
    case 'COMPLETED': return '#6366f1';
    case 'ON_HOLD':   return '#eab308';
    case 'TRIAGE':    return '#f97316';
    case 'ARCHIVED':  return '#6b7280';
    case 'CANCELLED': return '#ef4444';
    default:          return '#6b7280';
  }
}

function priorityColor(p: string): string {
  switch (p) {
    case 'critical': return '#ef4444';
    case 'high':     return '#f97316';
    case 'medium':   return '#eab308';
    default:         return '#6b7280';
  }
}

function healthColor(h: string): string {
  switch (h) {
    case 'healthy': return '#22c55e';
    case 'stale':   return '#eab308';
    case 'blocked': return '#ef4444';
    default:        return '#6b7280';
  }
}

function stageStatusColor(s: string): string {
  switch (s) {
    case 'APPROVED':    return '#22c55e';
    case 'IN_REVIEW':   return '#6366f1';
    case 'DRAFT':       return '#eab308';
    case 'REJECTED':    return '#ef4444';
    case 'BLOCKED':     return '#ef4444';
    case 'SUPERSEDED':  return '#6b7280';
    default:            return '#4b5563'; // PENDING / NOT_STARTED
  }
}

function actionStatusColor(s: string): string {
  switch (s) {
    case 'completed':   return '#22c55e';
    case 'in_progress': return '#6366f1';
    case 'blocked':     return '#ef4444';
    case 'cancelled':   return '#6b7280';
    default:            return '#eab308'; // pending
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

const STAGE_NAMES: Record<number, string> = {
  1: 'Research Brief',
  2: 'Prototype Plan',
  3: 'Evaluation Protocol',
  4: 'Technical Design',
  5: 'Pilot Execution',
};

// ── View state ───────────────────────────────────────────────────────────────

type ViewState =
  | { screen: 'home' }
  | { screen: 'list'; status: InitiativeStatus | 'all' }
  | { screen: 'detail'; id: string }
  | { screen: 'actionItems'; id: string; name: string }
  | { screen: 'stageDoc'; documentId: string; title: string };

// ── Main Screen ──────────────────────────────────────────────────────────────

export default function InitiativesHomeScreen() {
  const [view, setView] = useState<ViewState>({ screen: 'home' });
  const [listData, setListData] = useState<InitiativeListResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      const res = await initiativesApi.listInitiatives({ limit: 500, sort: 'priority' });
      setListData(res);
    } catch {
      // Stats unavailable — show zeros
    }
  }, []);

  useEffect(() => {
    fetchStats().finally(() => setLoading(false));
  }, [fetchStats]);

  const handleBack = () => {
    if (view.screen === 'stageDoc' || view.screen === 'actionItems') {
      // Go back to detail — but we don't have the id. Go to list.
      setView({ screen: 'list', status: 'all' });
    } else if (view.screen === 'detail') {
      setView({ screen: 'list', status: 'all' });
    } else if (view.screen === 'list') {
      setView({ screen: 'home' });
    } else {
      setView({ screen: 'home' });
    }
  };

  if (view.screen === 'list') {
    return (
      <InitiativesList
        status={view.status}
        allData={listData}
        onSelect={(item) => setView({ screen: 'detail', id: item.id })}
        onBack={handleBack}
        onRefresh={fetchStats}
      />
    );
  }

  if (view.screen === 'detail') {
    return (
      <InitiativeDetail
        initiativeId={view.id}
        allData={listData}
        onBack={handleBack}
        onViewActions={(id, name) => setView({ screen: 'actionItems', id, name })}
        onViewDoc={(documentId, title) => setView({ screen: 'stageDoc', documentId, title })}
      />
    );
  }

  if (view.screen === 'actionItems') {
    return (
      <ActionItemsScreen
        initiativeId={view.id}
        initiativeName={view.name}
        onBack={handleBack}
      />
    );
  }

  if (view.screen === 'stageDoc') {
    return (
      <StageDocumentScreen
        documentId={view.documentId}
        title={view.title}
        onBack={handleBack}
      />
    );
  }

  // Home view
  const stats = listData?.stats;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Initiatives</Text>

      {loading ? (
        <ActivityIndicator size="small" color="#6366f1" style={{ marginTop: 20 }} />
      ) : (
        <>
          {/* Stats cards */}
          <View style={styles.statsRow}>
            <StatCard
              label="Active"
              value={stats?.active ?? 0}
              color="#22c55e"
              onPress={() => setView({ screen: 'list', status: 'ACTIVE' })}
            />
            <StatCard
              label="Triage"
              value={(listData?.initiatives.filter((i) => i.status === 'TRIAGE').length) ?? 0}
              color="#f97316"
              onPress={() => setView({ screen: 'list', status: 'TRIAGE' })}
            />
          </View>
          <View style={styles.statsRow}>
            <StatCard
              label="On Hold"
              value={stats?.on_hold ?? 0}
              color="#eab308"
              onPress={() => setView({ screen: 'list', status: 'ON_HOLD' })}
            />
            <StatCard
              label="Completed"
              value={stats?.completed ?? 0}
              color="#6366f1"
              onPress={() => setView({ screen: 'list', status: 'COMPLETED' })}
            />
          </View>

          <TouchableOpacity
            style={styles.allButton}
            onPress={() => setView({ screen: 'list', status: 'all' })}
          >
            <Text style={styles.allButtonText}>
              View All ({listData?.total_count ?? 0})
            </Text>
          </TouchableOpacity>

          {/* Priority summary */}
          {stats?.by_priority && (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>By Priority</Text>
              <View style={styles.priorityRow}>
                {(['critical', 'high', 'medium', 'low'] as const).map((p) => (
                  <View key={p} style={styles.priorityChip}>
                    <View style={[styles.dot, { backgroundColor: priorityColor(p) }]} />
                    <Text style={styles.priorityLabel}>{p}</Text>
                    <Text style={[styles.priorityCount, { color: priorityColor(p) }]}>
                      {stats.by_priority[p] ?? 0}
                    </Text>
                  </View>
                ))}
              </View>
            </View>
          )}
        </>
      )}
    </ScrollView>
  );
}

// ── Stat Card ────────────────────────────────────────────────────────────────

function StatCard({ label, value, color, onPress }: {
  label: string; value: number; color: string; onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.statCard} onPress={onPress} activeOpacity={0.7}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </TouchableOpacity>
  );
}

// ── Initiatives List ─────────────────────────────────────────────────────────

function InitiativesList({
  status,
  allData,
  onSelect,
  onBack,
  onRefresh,
}: {
  status: InitiativeStatus | 'all';
  allData: InitiativeListResponse | null;
  onSelect: (item: InitiativeListItem) => void;
  onBack: () => void;
  onRefresh: () => Promise<void>;
}) {
  const [refreshing, setRefreshing] = useState(false);

  const items = allData?.initiatives.filter(
    (i) => status === 'all' || i.status === status,
  ) ?? [];

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await onRefresh();
    setRefreshing(false);
  }, [onRefresh]);

  const title = status === 'all' ? 'All Initiatives' : `${status} Initiatives`;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.backButton}>Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{title}</Text>
        <Text style={styles.headerCount}>{items.length}</Text>
      </View>
      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        contentContainerStyle={items.length === 0 ? styles.center : styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} tintColor="#6366f1" />
        }
        ListEmptyComponent={
          <Text style={styles.emptyText}>No {status === 'all' ? '' : status.toLowerCase() + ' '}initiatives</Text>
        }
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.row} onPress={() => onSelect(item)} activeOpacity={0.7}>
            <View style={styles.rowHeader}>
              <Text style={[styles.badge, {
                backgroundColor: statusColor(item.status) + '30',
                color: statusColor(item.status),
              }]}>
                {item.status}
              </Text>
              <View style={styles.rowRight}>
                <Text style={[styles.stageBadge, {
                  backgroundColor: 'rgba(99,102,241,0.2)',
                  color: '#818cf8',
                }]}>
                  Stage {item.current_stage}/5
                </Text>
                <Text style={[styles.healthDot, { color: healthColor(item.health) }]}>
                  {item.health === 'healthy' ? '' : item.health}
                </Text>
              </View>
            </View>
            <Text style={styles.title} numberOfLines={2}>{item.name}</Text>
            <View style={styles.meta}>
              {item.human_id && <Text style={styles.metaText}>{item.human_id}</Text>}
              <Text style={styles.metaText}>{item.program_display || item.program}</Text>
              <Text style={styles.metaText}>{timeAgo(item.updated_at)}</Text>
              {item.priority_level !== 'low' && (
                <Text style={[styles.metaText, { color: priorityColor(item.priority_level) }]}>
                  {item.priority_level}
                </Text>
              )}
            </View>
            {/* Progress bar */}
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: `${item.completion_percentage}%` }]} />
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

// ── Initiative Detail ────────────────────────────────────────────────────────

function InitiativeDetail({
  initiativeId,
  allData,
  onBack,
  onViewActions,
  onViewDoc,
}: {
  initiativeId: string;
  allData: InitiativeListResponse | null;
  onBack: () => void;
  onViewActions: (id: string, name: string) => void;
  onViewDoc: (documentId: string, title: string) => void;
}) {
  const item = allData?.initiatives.find((i) => i.id === initiativeId);

  if (!item) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={styles.emptyText}>Initiative not found</Text>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.backButton}>Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const stages = Object.entries(item.stages)
    .sort(([a], [b]) => Number(a) - Number(b));

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.detailTopRow}>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.backButton}>Back</Text>
        </TouchableOpacity>
        <CopyId value={initiativeId} label="Initiative ID" />
      </View>

      <View style={styles.detailHeader}>
        <Text style={[styles.badge, {
          backgroundColor: statusColor(item.status) + '30',
          color: statusColor(item.status),
        }]}>
          {item.status}
        </Text>
        {item.human_id && <Text style={styles.humanId}>{item.human_id}</Text>}
      </View>

      <Text style={styles.detailName}>{item.name}</Text>

      {/* Scores */}
      <View style={styles.scoresRow}>
        <ScoreBox label="Impact" value={item.impact_score} />
        <ScoreBox label="Urgency" value={item.urgency} />
        <ScoreBox label="Confidence" value={item.confidence} />
        <ScoreBox label="Revenue" value={item.revenue_potential} />
      </View>

      {/* Progress */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Progress</Text>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${item.completion_percentage}%` }]} />
        </View>
        <Text style={styles.mutedText}>
          {item.completion_percentage}% complete | Stage {item.current_stage}/5 | {item.stages_with_work} stages with work
        </Text>
      </View>

      {/* Description */}
      {item.description ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Description</Text>
          <Text style={styles.descriptionText} numberOfLines={12}>
            {item.description}
          </Text>
        </View>
      ) : null}

      {/* Stages */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Stages</Text>
        {stages.map(([num, stage]) => (
          <TouchableOpacity
            key={num}
            style={styles.stageRow}
            disabled={!stage.document_id}
            onPress={() => stage.document_id && onViewDoc(stage.document_id, stage.stage_name || STAGE_NAMES[Number(num)] || `Stage ${num}`)}
            activeOpacity={0.7}
          >
            <View style={[styles.stageNum, { backgroundColor: stageStatusColor(stage.status) + '30' }]}>
              <Text style={[styles.stageNumText, { color: stageStatusColor(stage.status) }]}>{num}</Text>
            </View>
            <View style={styles.stageInfo}>
              <Text style={styles.stageName}>
                {stage.stage_name || STAGE_NAMES[Number(num)] || `Stage ${num}`}
              </Text>
              <Text style={[styles.stageStatus, { color: stageStatusColor(stage.status) }]}>
                {stage.status}
              </Text>
            </View>
            {stage.document_id && <Text style={styles.docLink}>View</Text>}
          </TouchableOpacity>
        ))}
      </View>

      {/* Action Items button */}
      <TouchableOpacity
        style={styles.actionButton}
        onPress={() => onViewActions(item.id, item.name)}
      >
        <Text style={styles.actionButtonText}>View Action Items</Text>
      </TouchableOpacity>

      {/* Meta */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Details</Text>
        <MetaRow label="Program" value={item.program_display || item.program} />
        <MetaRow label="Purpose" value={item.purpose_display || item.purpose} />
        <MetaRow label="Priority" value={item.priority_level} />
        <MetaRow label="Health" value={item.health} />
        <MetaRow label="Days since update" value={String(item.days_since_update)} />
        <MetaRow label="Created" value={new Date(item.created_at).toLocaleDateString()} />
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

function ScoreBox({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  return (
    <View style={styles.scoreBox}>
      <Text style={styles.scoreValue}>{pct}%</Text>
      <Text style={styles.scoreLabel}>{label}</Text>
    </View>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.metaRow}>
      <Text style={styles.metaRowLabel}>{label}</Text>
      <Text style={styles.metaRowValue}>{value}</Text>
    </View>
  );
}

// ── Action Items Screen ──────────────────────────────────────────────────────

function ActionItemsScreen({
  initiativeId,
  initiativeName,
  onBack,
}: {
  initiativeId: string;
  initiativeName: string;
  onBack: () => void;
}) {
  const [data, setData] = useState<ActionItemsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busyItem, setBusyItem] = useState<string | null>(null);

  const fetchItems = useCallback(async () => {
    setError(null);
    try {
      const res = await initiativesApi.getActionItems(initiativeId);
      setData(res);
    } catch {
      setError('Failed to load action items');
    }
  }, [initiativeId]);

  useEffect(() => {
    fetchItems().finally(() => setLoading(false));
  }, [fetchItems]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchItems();
    setRefreshing(false);
  }, [fetchItems]);

  const handleUpdateStatus = useCallback(async (item: InitiativeActionItem, newStatus: string) => {
    setBusyItem(item.id);
    try {
      await initiativesApi.updateActionItem(item.id, { status: newStatus as any });
      toast.success(`Action item ${newStatus}`);
      await fetchItems();
    } catch {
      toast.error(`Failed to update action item to ${newStatus}`);
    } finally {
      setBusyItem(null);
    }
  }, [fetchItems]);

  if (loading) {
    return (
      <View style={[styles.container, styles.center]}>
        <ActivityIndicator size="small" color="#6366f1" />
      </View>
    );
  }

  const items = data?.action_items ?? [];
  const stats = data?.stats;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.backButton}>Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>Action Items</Text>
        <Text style={styles.headerCount}>{items.length}</Text>
      </View>

      {/* Stats bar */}
      {stats && (
        <View style={styles.actionStatsBar}>
          <Text style={[styles.actionStat, { color: '#eab308' }]}>{stats.pending} pending</Text>
          <Text style={[styles.actionStat, { color: '#6366f1' }]}>{stats.in_progress} active</Text>
          <Text style={[styles.actionStat, { color: '#22c55e' }]}>{stats.completed} done</Text>
          <Text style={[styles.actionStat, { color: '#ef4444' }]}>{stats.blocked} blocked</Text>
        </View>
      )}

      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        contentContainerStyle={items.length === 0 ? styles.center : styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" />
        }
        ListEmptyComponent={
          <Text style={styles.emptyText}>{error ?? 'No action items'}</Text>
        }
        renderItem={({ item }) => {
          const isBusy = busyItem === item.id;
          return (
            <View style={styles.row}>
              <View style={styles.rowHeader}>
                <Text style={[styles.badge, {
                  backgroundColor: actionStatusColor(item.status) + '30',
                  color: actionStatusColor(item.status),
                }]}>
                  {item.status.replace('_', ' ')}
                </Text>
                <Text style={[styles.badge, {
                  backgroundColor: priorityColor(item.priority) + '30',
                  color: priorityColor(item.priority),
                }]}>
                  {item.priority}
                </Text>
              </View>
              <Text style={styles.title} numberOfLines={2}>{item.title}</Text>
              {item.description ? (
                <Text style={styles.descriptionText} numberOfLines={3}>{item.description}</Text>
              ) : null}
              <View style={styles.meta}>
                {item.assigned_agent ? <Text style={styles.metaText}>{item.assigned_agent}</Text> : null}
                {item.due_date ? (
                  <Text style={[styles.metaText, item.is_overdue && { color: '#ef4444' }]}>
                    Due: {item.due_date}{item.is_overdue ? ' (overdue)' : ''}
                  </Text>
                ) : null}
              </View>

              {/* Action buttons */}
              <View style={styles.actionButtons}>
                {item.status === 'pending' && (
                  <TouchableOpacity
                    style={[styles.smallButton, { backgroundColor: 'rgba(99,102,241,0.2)' }]}
                    onPress={() => handleUpdateStatus(item, 'in_progress')}
                    disabled={isBusy}
                  >
                    {isBusy ? (
                      <ActivityIndicator size="small" color="#818cf8" />
                    ) : (
                      <Text style={[styles.smallButtonText, { color: '#818cf8' }]}>Start</Text>
                    )}
                  </TouchableOpacity>
                )}
                {item.status === 'in_progress' && (
                  <TouchableOpacity
                    style={[styles.smallButton, { backgroundColor: 'rgba(34,197,94,0.2)' }]}
                    onPress={() => handleUpdateStatus(item, 'completed')}
                    disabled={isBusy}
                  >
                    {isBusy ? (
                      <ActivityIndicator size="small" color="#22c55e" />
                    ) : (
                      <Text style={[styles.smallButtonText, { color: '#22c55e' }]}>Complete</Text>
                    )}
                  </TouchableOpacity>
                )}
              </View>
            </View>
          );
        }}
      />
    </View>
  );
}

// ── Stage Document Screen ────────────────────────────────────────────────────

function StageDocumentScreen({
  documentId,
  title,
  onBack,
}: {
  documentId: string;
  title: string;
  onBack: () => void;
}) {
  const [content, setContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const doc = await initiativesApi.getStageDocument(documentId);
        setContent(doc.full_text || doc.content || 'No content');
      } catch {
        setError('Failed to load document');
      } finally {
        setLoading(false);
      }
    })();
  }, [documentId]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.backButton}>Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>{title}</Text>
        <View />
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="small" color="#6366f1" />
        </View>
      ) : error ? (
        <View style={styles.center}>
          <Text style={styles.emptyText}>{error}</Text>
        </View>
      ) : (
        <ScrollView style={styles.docScroll} contentContainerStyle={styles.docContent}>
          <Markdown style={markdownStyles}>{content ?? ''}</Markdown>
        </ScrollView>
      )}
    </View>
  );
}

// ── Markdown styles ──────────────────────────────────────────────────────────

const markdownStyles = StyleSheet.create({
  body: { color: '#d1d5db', fontSize: 14, lineHeight: 22 },
  heading1: { color: '#ffffff', fontSize: 20, fontWeight: '700', marginBottom: 8, marginTop: 16 },
  heading2: { color: '#ffffff', fontSize: 17, fontWeight: '700', marginBottom: 6, marginTop: 14 },
  heading3: { color: '#e5e7eb', fontSize: 15, fontWeight: '600', marginBottom: 4, marginTop: 12 },
  code_inline: { backgroundColor: 'rgba(99,102,241,0.15)', color: '#818cf8', borderRadius: 4, paddingHorizontal: 4 },
  fence: { backgroundColor: '#111122', borderRadius: 8, padding: 12 },
  code_block: { color: '#d1d5db', fontSize: 13 },
  link: { color: '#6366f1' },
  bullet_list: { marginLeft: 8 },
  ordered_list: { marginLeft: 8 },
  list_item: { marginBottom: 4 },
  blockquote: { borderLeftWidth: 3, borderLeftColor: '#6366f1', paddingLeft: 12, marginLeft: 0 },
  hr: { backgroundColor: '#1a1a2e', height: 1, marginVertical: 12 },
  strong: { fontWeight: '700', color: '#ffffff' },
});

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 12 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  list: { paddingVertical: 4 },
  heading: { color: '#ffffff', fontSize: 22, fontWeight: '800', margin: 12 },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a2e',
  },
  headerTitle: { color: '#ffffff', fontSize: 16, fontWeight: '700', flex: 1, textAlign: 'center' },
  headerCount: { color: '#6b7280', fontSize: 13, minWidth: 30, textAlign: 'right' },
  backButton: { color: '#6366f1', fontSize: 15, fontWeight: '600' },

  // Stats
  statsRow: { flexDirection: 'row', gap: 10, marginHorizontal: 12, marginBottom: 10 },
  statCard: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  statValue: { fontSize: 28, fontWeight: '800' },
  statLabel: { color: '#6b7280', fontSize: 12, marginTop: 4 },

  allButton: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    marginHorizontal: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginBottom: 12,
  },
  allButtonText: { color: '#6366f1', fontSize: 15, fontWeight: '600' },

  // Card
  card: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 14,
    marginHorizontal: 12,
    marginBottom: 10,
  },
  cardTitle: { color: '#ffffff', fontSize: 15, fontWeight: '700', marginBottom: 10 },

  // Priority row
  priorityRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  priorityChip: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  priorityLabel: { color: '#9ca3af', fontSize: 12, textTransform: 'capitalize' },
  priorityCount: { fontSize: 13, fontWeight: '700' },

  // List rows
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
  rowRight: { flexDirection: 'row', gap: 6, alignItems: 'center' },
  badge: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 6,
    overflow: 'hidden',
  },
  stageBadge: {
    fontSize: 10,
    fontWeight: '600',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
    overflow: 'hidden',
  },
  healthDot: { fontSize: 10, fontWeight: '600', textTransform: 'capitalize' },
  title: { color: '#e5e7eb', fontSize: 15, fontWeight: '600', marginBottom: 4 },
  meta: { flexDirection: 'row', gap: 8, flexWrap: 'wrap', marginTop: 4 },
  metaText: { color: '#6b7280', fontSize: 11 },
  emptyText: { color: '#6b7280', fontSize: 14 },
  mutedText: { color: '#6b7280', fontSize: 13, marginTop: 4 },

  // Progress bar
  progressBar: {
    height: 4,
    backgroundColor: 'rgba(99,102,241,0.15)',
    borderRadius: 2,
    marginTop: 8,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6366f1',
    borderRadius: 2,
  },

  // Detail
  detailTopRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  detailHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 12,
    marginHorizontal: 12,
  },
  humanId: { color: '#6b7280', fontSize: 12, fontWeight: '600' },
  detailName: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: '800',
    marginHorizontal: 12,
    marginTop: 8,
    marginBottom: 12,
  },
  descriptionText: { color: '#9ca3af', fontSize: 13, lineHeight: 20 },

  // Scores
  scoresRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginHorizontal: 12,
    marginBottom: 10,
  },
  scoreBox: { alignItems: 'center', flex: 1 },
  scoreValue: { color: '#e5e7eb', fontSize: 18, fontWeight: '700' },
  scoreLabel: { color: '#6b7280', fontSize: 10, marginTop: 2 },

  // Stages
  stageRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  stageNum: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  stageNumText: { fontSize: 13, fontWeight: '700' },
  stageInfo: { flex: 1 },
  stageName: { color: '#d1d5db', fontSize: 14, fontWeight: '500' },
  stageStatus: { fontSize: 11, marginTop: 2 },
  docLink: { color: '#6366f1', fontSize: 12, fontWeight: '600' },

  // Action Items
  actionButton: {
    backgroundColor: 'rgba(99,102,241,0.2)',
    borderRadius: 10,
    marginHorizontal: 12,
    marginBottom: 10,
    paddingVertical: 14,
    alignItems: 'center',
  },
  actionButtonText: { color: '#6366f1', fontSize: 15, fontWeight: '600' },
  actionStatsBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a2e',
  },
  actionStat: { fontSize: 11, fontWeight: '600' },
  actionButtons: { flexDirection: 'row', gap: 8, marginTop: 8 },
  smallButton: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 6,
  },
  smallButtonText: { fontSize: 13, fontWeight: '600' },

  // Meta rows
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  metaRowLabel: { color: '#6b7280', fontSize: 13 },
  metaRowValue: { color: '#d1d5db', fontSize: 13, fontWeight: '500', textTransform: 'capitalize' },

  // Document
  docScroll: { flex: 1 },
  docContent: { padding: 16 },
});

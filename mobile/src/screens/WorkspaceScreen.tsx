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
import * as workspaceApi from '../api/workspace';
import type { Workspace, WorkspaceOperation } from '../api/workspace';
import { useDemo } from '../demo/useDemo';
import * as demo from '../demo/demoData';
import { toast } from '../components/Toast';

// ── View state ───────────────────────────────────────────────────────────────

type WorkspaceView = 'overview' | 'operations' | 'reviews';

// ── Helpers ──────────────────────────────────────────────────────────────────

function timeAgo(timestamp: string | null): string {
  if (!timestamp) return '—';
  const diff = Date.now() - new Date(timestamp).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function opTypeLabel(type: string): string {
  switch (type) {
    case 'file_create': return 'Create';
    case 'file_modify': return 'Modify';
    case 'file_delete': return 'Delete';
    case 'git_commit': return 'Commit';
    case 'git_branch': return 'Branch';
    default: return type.replace(/_/g, ' ');
  }
}

function opTypeColor(type: string): string {
  switch (type) {
    case 'file_create': return '#22c55e';
    case 'file_modify': return '#6366f1';
    case 'file_delete': return '#ef4444';
    case 'git_commit': return '#06b6d4';
    case 'git_branch': return '#a855f7';
    default: return '#6b7280';
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────

export default function WorkspaceScreen() {
  const isDemo = useDemo();
  const [view, setView] = useState<WorkspaceView>('overview');
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [operations, setOperations] = useState<WorkspaceOperation[]>([]);
  const [pendingReviews, setPendingReviews] = useState<WorkspaceOperation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activeWorkspace = workspaces.find((w) => w.is_active) ?? workspaces[0];

  const fetchData = useCallback(async () => {
    if (isDemo) {
      setWorkspaces(demo.DEMO_WORKSPACES as any);
      setOperations(demo.DEMO_WORKSPACE_OPERATIONS as any);
      setPendingReviews([]);
      setLoading(false);
      setRefreshing(false);
      return;
    }
    try {
      setError(null);
      const [wsRes, opsRes, reviewRes] = await Promise.all([
        workspaceApi.listWorkspaces(),
        workspaceApi.listOperations({ limit: 20 }),
        workspaceApi.getPendingReviews(),
      ]);
      setWorkspaces(wsRes.results);
      setOperations(opsRes.results);
      setPendingReviews(reviewRes.results);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load workspace data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [isDemo]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = () => { setRefreshing(true); fetchData(); };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#818cf8" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryBtn} onPress={fetchData}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Workspace</Text>

      {/* Tab bar */}
      <View style={styles.tabBar}>
        {(['overview', 'operations', 'reviews'] as WorkspaceView[]).map((t) => (
          <TouchableOpacity
            key={t}
            style={[styles.tab, view === t && styles.tabActive]}
            onPress={() => setView(t)}
          >
            <Text style={[styles.tabText, view === t && styles.tabTextActive]}>
              {t === 'reviews' ? `Reviews (${pendingReviews.length})` : t.charAt(0).toUpperCase() + t.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {view === 'overview' && (
        <OverviewTab
          workspace={activeWorkspace}
          workspaces={workspaces}
          totalOps={operations.length}
          pendingCount={pendingReviews.length}
          recentOps={operations.slice(0, 5)}
          refreshing={refreshing}
          onRefresh={onRefresh}
        />
      )}
      {view === 'operations' && (
        <OperationsTab
          operations={operations}
          refreshing={refreshing}
          onRefresh={onRefresh}
        />
      )}
      {view === 'reviews' && (
        <ReviewsTab
          reviews={pendingReviews}
          refreshing={refreshing}
          onRefresh={onRefresh}
          onReview={async (id, approved) => {
            try {
              await workspaceApi.reviewOperation(id, approved);
              toast.success(approved ? 'Operation approved' : 'Operation rejected');
              fetchData();
            } catch {
              toast.error('Failed to submit review');
            }
          }}
        />
      )}
    </View>
  );
}

// ── Overview Tab ─────────────────────────────────────────────────────────────

function OverviewTab({
  workspace,
  workspaces,
  totalOps,
  pendingCount,
  recentOps,
  refreshing,
  onRefresh,
}: {
  workspace: Workspace | undefined;
  workspaces: Workspace[];
  totalOps: number;
  pendingCount: number;
  recentOps: WorkspaceOperation[];
  refreshing: boolean;
  onRefresh: () => void;
}) {
  return (
    <FlatList
      data={recentOps}
      keyExtractor={(op) => op.id}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
      ListHeaderComponent={
        <>
          {/* Active workspace card */}
          {workspace ? (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>{workspace.name}</Text>
              {workspace.description ? (
                <Text style={styles.cardSub}>{workspace.description}</Text>
              ) : null}
              <View style={styles.statsRow}>
                <StatBox label="Operations" value={String(workspace.total_operations)} />
                <StatBox label="Files Written" value={String(workspace.total_files_written)} />
                <StatBox label="Commits" value={String(workspace.total_commits)} />
              </View>
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>Type</Text>
                <Text style={styles.metaValue}>{workspace.workspace_type}</Text>
              </View>
              {workspace.current_branch ? (
                <View style={styles.metaRow}>
                  <Text style={styles.metaLabel}>Branch</Text>
                  <Text style={[styles.metaValue, { color: '#a855f7' }]}>
                    {workspace.current_branch}
                  </Text>
                </View>
              ) : null}
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>Last Activity</Text>
                <Text style={styles.metaValue}>{timeAgo(workspace.last_operation_at)}</Text>
              </View>
            </View>
          ) : (
            <View style={styles.card}>
              <Text style={styles.cardSub}>No workspace found</Text>
            </View>
          )}

          {/* Summary stats */}
          <View style={styles.summaryRow}>
            <View style={styles.summaryCard}>
              <Text style={styles.summaryNumber}>{workspaces.length}</Text>
              <Text style={styles.summaryLabel}>Workspaces</Text>
            </View>
            <View style={styles.summaryCard}>
              <Text style={styles.summaryNumber}>{totalOps}</Text>
              <Text style={styles.summaryLabel}>Recent Ops</Text>
            </View>
            <View style={[styles.summaryCard, pendingCount > 0 && styles.summaryHighlight]}>
              <Text style={[styles.summaryNumber, pendingCount > 0 && { color: '#f59e0b' }]}>
                {pendingCount}
              </Text>
              <Text style={styles.summaryLabel}>Pending</Text>
            </View>
          </View>

          <Text style={styles.sectionHeader}>Recent Operations</Text>
        </>
      }
      renderItem={({ item }) => <OperationRow op={item} />}
      ListEmptyComponent={
        <Text style={styles.emptyText}>No recent operations</Text>
      }
      contentContainerStyle={styles.listContent}
    />
  );
}

// ── Operations Tab ───────────────────────────────────────────────────────────

function OperationsTab({
  operations,
  refreshing,
  onRefresh,
}: {
  operations: WorkspaceOperation[];
  refreshing: boolean;
  onRefresh: () => void;
}) {
  return (
    <FlatList
      data={operations}
      keyExtractor={(op) => op.id}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
      renderItem={({ item }) => <OperationRow op={item} showWorkspace />}
      ListEmptyComponent={
        <Text style={styles.emptyText}>No operations recorded</Text>
      }
      contentContainerStyle={styles.listContent}
    />
  );
}

// ── Reviews Tab ──────────────────────────────────────────────────────────────

function ReviewsTab({
  reviews,
  refreshing,
  onRefresh,
  onReview,
}: {
  reviews: WorkspaceOperation[];
  refreshing: boolean;
  onRefresh: () => void;
  onReview: (id: string, approved: boolean) => Promise<void>;
}) {
  const [reviewingId, setReviewingId] = useState<string | null>(null);

  const handleReview = async (id: string, approved: boolean) => {
    setReviewingId(id);
    try {
      await onReview(id, approved);
    } finally {
      setReviewingId(null);
    }
  };

  return (
    <FlatList
      data={reviews}
      keyExtractor={(op) => op.id}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
      renderItem={({ item }) => (
        <View style={styles.reviewCard}>
          <View style={styles.opHeader}>
            <View style={[styles.opTypeBadge, { backgroundColor: opTypeColor(item.operation_type) + '22' }]}>
              <Text style={[styles.opTypeText, { color: opTypeColor(item.operation_type) }]}>
                {opTypeLabel(item.operation_type)}
              </Text>
            </View>
            <Text style={styles.opAgent}>{item.agent_name}</Text>
          </View>
          <Text style={styles.opFile} numberOfLines={2}>{item.file_path}</Text>
          <Text style={styles.opTime}>{timeAgo(item.created_at)}</Text>
          <View style={styles.reviewActions}>
            {reviewingId === item.id ? (
              <ActivityIndicator size="small" color="#818cf8" />
            ) : (
              <>
                <TouchableOpacity
                  style={[styles.reviewBtn, styles.approveBtn]}
                  onPress={() => handleReview(item.id, true)}
                >
                  <Text style={styles.approveBtnText}>Approve</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.reviewBtn, styles.rejectBtn]}
                  onPress={() => handleReview(item.id, false)}
                >
                  <Text style={styles.rejectBtnText}>Reject</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      )}
      ListEmptyComponent={
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>✓</Text>
          <Text style={styles.emptyTitle}>All caught up</Text>
          <Text style={styles.emptyText}>No operations pending review</Text>
        </View>
      }
      contentContainerStyle={styles.listContent}
    />
  );
}

// ── Shared Components ────────────────────────────────────────────────────────

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.statBox}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function OperationRow({ op, showWorkspace }: { op: WorkspaceOperation; showWorkspace?: boolean }) {
  return (
    <View style={styles.opRow}>
      <View style={styles.opHeader}>
        <View style={[styles.opTypeBadge, { backgroundColor: opTypeColor(op.operation_type) + '22' }]}>
          <Text style={[styles.opTypeText, { color: opTypeColor(op.operation_type) }]}>
            {opTypeLabel(op.operation_type)}
          </Text>
        </View>
        {!op.success && <Text style={styles.failBadge}>FAILED</Text>}
        <Text style={styles.opAgent}>{op.agent_name}</Text>
      </View>
      <Text style={styles.opFile} numberOfLines={1}>{op.file_path}</Text>
      <View style={styles.opFooter}>
        {showWorkspace && <Text style={styles.opWorkspace}>{op.workspace_name}</Text>}
        <Text style={styles.opTime}>{timeAgo(op.created_at)}</Text>
      </View>
    </View>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0a0f' },
  listContent: { padding: 16, paddingBottom: 40 },

  title: { color: '#ffffff', fontSize: 22, fontWeight: '700', paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },

  errorText: { color: '#ef4444', fontSize: 14, marginBottom: 12 },
  retryBtn: { backgroundColor: '#1e1e3a', paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 },
  retryText: { color: '#818cf8', fontWeight: '600' },

  // Tab bar
  tabBar: { flexDirection: 'row', paddingHorizontal: 16, marginBottom: 4 },
  tab: { paddingVertical: 8, paddingHorizontal: 14, marginRight: 6, borderRadius: 8 },
  tabActive: { backgroundColor: '#1e1e3a' },
  tabText: { color: '#6b7280', fontSize: 13, fontWeight: '600' },
  tabTextActive: { color: '#818cf8' },

  // Card
  card: { backgroundColor: '#1a1a2e', borderRadius: 10, padding: 14, marginBottom: 12 },
  cardTitle: { color: '#ffffff', fontSize: 16, fontWeight: '700', marginBottom: 4 },
  cardSub: { color: '#6b7280', fontSize: 12, marginBottom: 10 },

  statsRow: { flexDirection: 'row', justifyContent: 'space-around', marginVertical: 12 },
  statBox: { alignItems: 'center' },
  statValue: { color: '#ffffff', fontSize: 20, fontWeight: '700' },
  statLabel: { color: '#6b7280', fontSize: 10, marginTop: 2 },

  metaRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)' },
  metaLabel: { color: '#6b7280', fontSize: 12 },
  metaValue: { color: '#d1d5db', fontSize: 12, fontWeight: '500' },

  // Summary row
  summaryRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  summaryCard: { flex: 1, backgroundColor: '#1a1a2e', borderRadius: 8, padding: 12, alignItems: 'center' },
  summaryHighlight: { borderWidth: 1, borderColor: '#f59e0b33' },
  summaryNumber: { color: '#ffffff', fontSize: 18, fontWeight: '700' },
  summaryLabel: { color: '#6b7280', fontSize: 10, marginTop: 2 },

  sectionHeader: { color: '#818cf8', fontSize: 12, fontWeight: '700', textTransform: 'uppercase', marginBottom: 8, marginTop: 4 },

  // Operation row
  opRow: { backgroundColor: '#1a1a2e', borderRadius: 8, padding: 12, marginBottom: 6 },
  opHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
  opTypeBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4, marginRight: 8 },
  opTypeText: { fontSize: 10, fontWeight: '700', textTransform: 'uppercase' },
  failBadge: { color: '#ef4444', fontSize: 9, fontWeight: '700', marginRight: 8 },
  opAgent: { color: '#6b7280', fontSize: 11, flex: 1, textAlign: 'right' },
  opFile: { color: '#d1d5db', fontSize: 12, fontFamily: 'monospace' },
  opFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 },
  opWorkspace: { color: '#6b7280', fontSize: 10 },
  opTime: { color: '#6b7280', fontSize: 10, textAlign: 'right', flex: 1 },

  // Review card
  reviewCard: { backgroundColor: '#1a1a2e', borderRadius: 8, padding: 12, marginBottom: 8, borderLeftWidth: 3, borderLeftColor: '#f59e0b' },
  reviewActions: { flexDirection: 'row', justifyContent: 'flex-end', gap: 8, marginTop: 10 },
  reviewBtn: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 6 },
  approveBtn: { backgroundColor: '#22c55e22' },
  approveBtnText: { color: '#22c55e', fontSize: 13, fontWeight: '600' },
  rejectBtn: { backgroundColor: '#ef444422' },
  rejectBtnText: { color: '#ef4444', fontSize: 13, fontWeight: '600' },

  // Empty state
  emptyState: { alignItems: 'center', paddingVertical: 40 },
  emptyIcon: { color: '#22c55e', fontSize: 32, marginBottom: 8 },
  emptyTitle: { color: '#ffffff', fontSize: 16, fontWeight: '600', marginBottom: 4 },
  emptyText: { color: '#6b7280', fontSize: 13, textAlign: 'center' },
});

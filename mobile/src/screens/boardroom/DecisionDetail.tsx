import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Clipboard,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { Decision } from '../../api/boardroom';
import * as boardroomApi from '../../api/boardroom';
import CopyId from '../../components/CopyId';
import { toast } from '../../components/Toast';

interface Props {
  decisionId: string;
  canMutate: boolean;
  onBack: () => void;
}

export default function DecisionDetail({ decisionId, canMutate, onBack }: Props) {
  const [decision, setDecision] = useState<(Decision & { suggested_feature?: string; rationale?: string }) | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [acting, setActing] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const fetchDecision = useCallback(async () => {
    try {
      setFetchError(null);
      const res = await boardroomApi.getDecision(decisionId);
      setDecision(res.decision);
    } catch (e: any) {
      const status = e?.response?.status;
      if (status === 500) {
        setFetchError('Server error loading decision. The backend may still be deploying.');
      } else if (status === 404) {
        setFetchError('Decision not found.');
      } else {
        setFetchError(e?.message ?? 'Failed to load decision');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [decisionId]);

  useEffect(() => { fetchDecision(); }, [fetchDecision]);

  const onRefresh = () => { setRefreshing(true); fetchDecision(); };

  const handlePromote = async () => {
    if (acting) return;
    setActing(true);
    try {
      await boardroomApi.promoteDecision(decisionId);
      toast.success('Decision promoted to canonical');
      onBack();
    } catch {
      toast.error('Failed to promote decision');
    } finally {
      setActing(false);
    }
  };

  const handleReject = async () => {
    if (acting) return;
    setActing(true);
    try {
      await boardroomApi.rejectDecision(decisionId);
      toast.success('Decision rejected');
      onBack();
    } catch {
      toast.error('Failed to reject decision');
    } finally {
      setActing(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  // Error fallback card
  if (fetchError) {
    return (
      <View style={styles.center}>
        <View style={styles.errorCard}>
          <Text style={styles.errorIcon}>!</Text>
          <Text style={styles.errorTitle}>Decision Unavailable</Text>
          <Text style={styles.errorBody}>{fetchError}</Text>
          <View style={styles.errorIdRow}>
            <Text style={styles.errorIdLabel}>ID:</Text>
            <TouchableOpacity
              onPress={() => {
                Clipboard.setString(decisionId);
                toast.info('Decision ID copied');
              }}
            >
              <Text style={styles.errorIdValue}>{decisionId}</Text>
              <Text style={styles.copyHint}>Tap to copy</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.errorActions}>
            <TouchableOpacity style={styles.retryBtn} onPress={fetchDecision}>
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={onBack}>
              <Text style={styles.linkText}>Go back</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  }

  if (!decision) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorBody}>Decision not found</Text>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.linkText}>Go back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const s = statusStyle(decision.status);
  const showActions = (decision.status === 'draft' || decision.status === 'review');

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
    >
      <View style={styles.topRow}>
        <TouchableOpacity onPress={onBack} style={styles.backBtn}>
          <Text style={styles.backText}>Back</Text>
        </TouchableOpacity>
        <CopyId value={decisionId} label="Decision ID" />
      </View>

      {/* Header */}
      <View style={styles.headerRow}>
        <Text style={[styles.statusBadge, { backgroundColor: s.bg, color: s.fg }]}>
          {decision.status}
        </Text>
        {decision.is_canonical && (
          <Text style={styles.canonicalBadge}>Canonical</Text>
        )}
      </View>
      <Text style={styles.title}>{decision.topic}</Text>

      {/* Type & Impact */}
      <View style={styles.section}>
        <MetaRow label="Type" value={decision.decision_type_display || decision.decision_type} />
        <MetaRow label="Impact Area" value={decision.impact_area_display || decision.impact_area} />
        <MetaRow label="Source" value={decision.source_type} />
        <MetaRow label="Created" value={new Date(decision.created_at).toLocaleString()} />
        {decision.promoted_at && (
          <MetaRow label="Promoted" value={new Date(decision.promoted_at).toLocaleString()} />
        )}
      </View>

      {/* Recommended Stance */}
      {decision.recommended_stance ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recommended Stance</Text>
          <Text style={styles.body}>{decision.recommended_stance}</Text>
        </View>
      ) : null}

      {/* Rationale */}
      {decision.rationale ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Rationale</Text>
          <Text style={styles.body}>{decision.rationale}</Text>
        </View>
      ) : null}

      {/* Key Insights */}
      {decision.key_insights && decision.key_insights.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Key Insights</Text>
          {decision.key_insights.map((insight, i) => (
            <View key={i} style={styles.insightRow}>
              <Text style={styles.insightBullet}>•</Text>
              <Text style={styles.insightText}>{insight}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Suggested Feature */}
      {decision.suggested_feature ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Suggested Feature</Text>
          <Text style={styles.body}>{decision.suggested_feature}</Text>
        </View>
      ) : null}

      {/* Participants */}
      {decision.participants.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Participants</Text>
          <View style={styles.chipRow}>
            {decision.participants.map((p, i) => (
              <Text key={i} style={styles.chip}>{p}</Text>
            ))}
          </View>
        </View>
      )}

      {/* Actions */}
      {showActions && (
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.actionBtn, styles.promoteBtn, !canMutate && styles.disabledBtn]}
            onPress={canMutate ? handlePromote : undefined}
            disabled={!canMutate || acting}
          >
            {acting ? (
              <ActivityIndicator size="small" color="#ffffff" />
            ) : (
              <Text style={styles.actionText}>Promote</Text>
            )}
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.actionBtn, styles.rejectBtn, !canMutate && styles.disabledBtn]}
            onPress={canMutate ? handleReject : undefined}
            disabled={!canMutate || acting}
          >
            <Text style={styles.actionText}>Reject</Text>
          </TouchableOpacity>
          {!canMutate && (
            <Text style={styles.rbacHint}>Requires admin or owner role</Text>
          )}
        </View>
      )}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.metaRow}>
      <Text style={styles.metaLabel}>{label}</Text>
      <Text style={styles.metaValue}>{value}</Text>
    </View>
  );
}

function statusStyle(s: string) {
  switch (s) {
    case 'canonical': return { bg: 'rgba(34,197,94,0.2)', fg: '#22c55e' };
    case 'review':    return { bg: 'rgba(99,102,241,0.2)', fg: '#818cf8' };
    case 'rejected':  return { bg: 'rgba(239,68,68,0.2)', fg: '#ef4444' };
    default:          return { bg: 'rgba(234,179,8,0.2)', fg: '#eab308' };
  }
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 16 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#0a0a0f', padding: 16 },

  topRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  backBtn: {},
  backText: { color: '#6366f1', fontSize: 14, fontWeight: '600' },
  linkText: { color: '#6366f1', fontSize: 14, fontWeight: '600', marginTop: 8 },

  // Error fallback card
  errorCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ef444433',
    width: '100%',
    maxWidth: 360,
  },
  errorIcon: {
    color: '#ef4444',
    fontSize: 28,
    fontWeight: '700',
    width: 44,
    height: 44,
    lineHeight: 44,
    textAlign: 'center',
    backgroundColor: '#ef444422',
    borderRadius: 22,
    overflow: 'hidden',
    marginBottom: 12,
  },
  errorTitle: { color: '#ffffff', fontSize: 16, fontWeight: '700', marginBottom: 6 },
  errorBody: { color: '#9ca3af', fontSize: 13, textAlign: 'center', lineHeight: 18, marginBottom: 16 },
  errorIdRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 6, marginBottom: 16 },
  errorIdLabel: { color: '#6b7280', fontSize: 11 },
  errorIdValue: { color: '#818cf8', fontSize: 11, fontFamily: 'monospace' },
  copyHint: { color: '#6366f1', fontSize: 9, textAlign: 'right', marginTop: 2 },
  errorActions: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  retryBtn: { backgroundColor: '#1e1e3a', paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 },
  retryText: { color: '#818cf8', fontWeight: '600', fontSize: 13 },

  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 8 },
  statusBadge: {
    fontSize: 11, fontWeight: '700', textTransform: 'uppercase',
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, overflow: 'hidden',
  },
  canonicalBadge: {
    fontSize: 11, fontWeight: '700', color: '#22c55e',
    backgroundColor: 'rgba(34,197,94,0.15)', paddingHorizontal: 8, paddingVertical: 3,
    borderRadius: 6, overflow: 'hidden',
  },
  title: { color: '#ffffff', fontSize: 20, fontWeight: '700', marginBottom: 16 },

  section: { marginBottom: 16 },
  sectionTitle: { color: '#818cf8', fontSize: 13, fontWeight: '600', marginBottom: 8, textTransform: 'uppercase' },
  body: { color: '#d1d5db', fontSize: 14, lineHeight: 20 },

  metaRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
  metaLabel: { color: '#6b7280', fontSize: 13 },
  metaValue: { color: '#d1d5db', fontSize: 13, fontWeight: '500', maxWidth: '60%', textAlign: 'right' },

  insightRow: { flexDirection: 'row', marginBottom: 4 },
  insightBullet: { color: '#818cf8', fontSize: 14, marginRight: 8, lineHeight: 20 },
  insightText: { color: '#d1d5db', fontSize: 14, lineHeight: 20, flex: 1 },

  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  chip: {
    color: '#9ca3af', fontSize: 12, backgroundColor: 'rgba(99,102,241,0.1)',
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6, overflow: 'hidden',
  },

  actions: { marginTop: 16 },
  actionBtn: { flex: 1, paddingVertical: 14, borderRadius: 10, alignItems: 'center', marginBottom: 8 },
  promoteBtn: { backgroundColor: '#22c55e' },
  rejectBtn: { backgroundColor: '#ef4444' },
  disabledBtn: { opacity: 0.4 },
  actionText: { color: '#ffffff', fontSize: 15, fontWeight: '700' },
  rbacHint: { color: '#6b7280', fontSize: 11, textAlign: 'center', marginTop: 4 },
});

import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { AttentionItem } from '../../api/boardroom';
import * as boardroomApi from '../../api/boardroom';

interface Props {
  itemId: string;
  canMutate: boolean;
  onBack: () => void;
}

export default function AttentionDetail({ itemId, canMutate, onBack }: Props) {
  const [item, setItem] = useState<AttentionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState(false);

  const fetch = useCallback(async () => {
    try {
      const res = await boardroomApi.getAttention(itemId);
      setItem(res.item);
    } catch {
      Alert.alert('Error', 'Failed to load attention item');
    } finally {
      setLoading(false);
    }
  }, [itemId]);

  useEffect(() => { fetch(); }, [fetch]);

  const handleDecide = async (decision: string) => {
    if (acting) return;
    setActing(true);
    try {
      await boardroomApi.decideAttention(itemId, decision);
      Alert.alert('Done', `Item ${decision}`);
      onBack();
    } catch {
      Alert.alert('Error', `Failed to ${decision} item`);
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

  if (!item) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Item not found</Text>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.linkText}>Go back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const u = urgencyStyle(item.urgency);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Back button */}
      <TouchableOpacity onPress={onBack} style={styles.backBtn}>
        <Text style={styles.backText}>Back</Text>
      </TouchableOpacity>

      {/* Header */}
      <View style={styles.headerRow}>
        <Text style={[styles.urgencyBadge, { backgroundColor: u.bg, color: u.fg }]}>
          {item.urgency}
        </Text>
        <Text style={styles.statusText}>{item.status}</Text>
      </View>
      <Text style={styles.title}>{item.title}</Text>

      {/* Summary */}
      {item.summary ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Summary</Text>
          <Text style={styles.body}>{item.summary}</Text>
        </View>
      ) : null}

      {/* ML Recommendation */}
      {item.ml_recommendation ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>ML Recommendation</Text>
          <View style={styles.mlBox}>
            <Text style={styles.mlRec}>{item.ml_recommendation}</Text>
            {item.ml_confidence > 0 && (
              <Text style={styles.mlConf}>
                Confidence: {Math.round(item.ml_confidence * 100)}%
              </Text>
            )}
          </View>
        </View>
      ) : null}

      {/* Metadata */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Details</Text>
        <MetaRow label="Type" value={item.item_type} />
        <MetaRow label="Source" value={item.source_type} />
        {item.source_agent ? <MetaRow label="Agent" value={item.source_agent} /> : null}
        <MetaRow label="Priority" value={String(item.priority_score)} />
        <MetaRow label="Created" value={new Date(item.created_at).toLocaleString()} />
        {item.expires_at ? (
          <MetaRow label="Expires" value={new Date(item.expires_at).toLocaleString()} />
        ) : null}
      </View>

      {/* Decision history */}
      {item.decided_at ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Decision</Text>
          <MetaRow label="Decision" value={item.decision} />
          <MetaRow label="At" value={new Date(item.decided_at).toLocaleString()} />
          {item.decision_feedback ? (
            <Text style={styles.body}>{item.decision_feedback}</Text>
          ) : null}
        </View>
      ) : null}

      {/* Actions */}
      {item.status === 'pending' && (
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.actionBtn, styles.approveBtn, !canMutate && styles.disabledBtn]}
            onPress={() => canMutate && handleDecide('approved')}
            disabled={!canMutate || acting}
          >
            <Text style={styles.actionText}>
              {canMutate ? 'Approve' : 'Approve (no permission)'}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.actionBtn, styles.ignoreBtn, !canMutate && styles.disabledBtn]}
            onPress={() => canMutate && handleDecide('ignored')}
            disabled={!canMutate || acting}
          >
            <Text style={styles.actionText}>
              {canMutate ? 'Ignore' : 'Ignore (no permission)'}
            </Text>
          </TouchableOpacity>
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

function urgencyStyle(u: string) {
  switch (u) {
    case 'critical': return { bg: 'rgba(239,68,68,0.2)', fg: '#ef4444' };
    case 'high':     return { bg: 'rgba(249,115,22,0.2)', fg: '#f97316' };
    case 'medium':   return { bg: 'rgba(234,179,8,0.2)',  fg: '#eab308' };
    default:         return { bg: 'rgba(107,114,128,0.2)', fg: '#6b7280' };
  }
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 16 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#0a0a0f' },
  errorText: { color: '#ef4444', fontSize: 15, marginBottom: 8 },
  linkText: { color: '#6366f1', fontSize: 14, fontWeight: '600' },

  backBtn: { marginBottom: 12 },
  backText: { color: '#6366f1', fontSize: 14, fontWeight: '600' },

  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 8 },
  urgencyBadge: {
    fontSize: 11, fontWeight: '700', textTransform: 'uppercase',
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, overflow: 'hidden',
  },
  statusText: { color: '#9ca3af', fontSize: 13, textTransform: 'capitalize' },
  title: { color: '#ffffff', fontSize: 20, fontWeight: '700', marginBottom: 16 },

  section: { marginBottom: 16 },
  sectionTitle: { color: '#818cf8', fontSize: 13, fontWeight: '600', marginBottom: 8, textTransform: 'uppercase' },
  body: { color: '#d1d5db', fontSize: 14, lineHeight: 20 },

  mlBox: { backgroundColor: '#1a1a2e', borderRadius: 8, padding: 12 },
  mlRec: { color: '#a5b4fc', fontSize: 14, fontWeight: '600', marginBottom: 4 },
  mlConf: { color: '#6b7280', fontSize: 12 },

  metaRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
  metaLabel: { color: '#6b7280', fontSize: 13 },
  metaValue: { color: '#d1d5db', fontSize: 13, fontWeight: '500', maxWidth: '60%', textAlign: 'right' },

  actions: { flexDirection: 'row', gap: 10, marginTop: 16 },
  actionBtn: { flex: 1, paddingVertical: 14, borderRadius: 10, alignItems: 'center' },
  approveBtn: { backgroundColor: '#22c55e' },
  ignoreBtn: { backgroundColor: '#6b7280' },
  disabledBtn: { opacity: 0.4 },
  actionText: { color: '#ffffff', fontSize: 15, fontWeight: '700' },
});

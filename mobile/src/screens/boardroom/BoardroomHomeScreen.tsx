import React, { useState } from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useAuthStore } from '../../auth/authStore';
import AttentionList from './AttentionList';
import AttentionDetail from './AttentionDetail';
import DecisionsList from './DecisionsList';
import DecisionDetail from './DecisionDetail';
import type { AttentionItem, Decision } from '../../api/boardroom';

// ── Navigation state (internal to boardroom) ─────────────────────────────────

type BoardroomView =
  | { screen: 'list' }
  | { screen: 'attentionDetail'; id: string }
  | { screen: 'decisionDetail'; id: string };

type Tab = 'attention' | 'decisions';

// ── Screen ───────────────────────────────────────────────────────────────────

export default function BoardroomHomeScreen() {
  const user = useAuthStore((s) => s.user);
  const canMutate = user?.platform_role === 'admin' || user?.platform_role === 'owner';

  const [tab, setTab] = useState<Tab>('attention');
  const [view, setView] = useState<BoardroomView>({ screen: 'list' });

  const handleSelectAttention = (item: AttentionItem) => {
    setView({ screen: 'attentionDetail', id: item.id });
  };

  const handleSelectDecision = (decision: Decision) => {
    setView({ screen: 'decisionDetail', id: decision.id });
  };

  const handleBack = () => {
    setView({ screen: 'list' });
  };

  // Detail views
  if (view.screen === 'attentionDetail') {
    return (
      <AttentionDetail
        itemId={view.id}
        canMutate={canMutate}
        onBack={handleBack}
      />
    );
  }

  if (view.screen === 'decisionDetail') {
    return (
      <DecisionDetail
        decisionId={view.id}
        canMutate={canMutate}
        onBack={handleBack}
      />
    );
  }

  // List view with tabs
  return (
    <View style={styles.container}>
      {/* Tab bar */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, tab === 'attention' && styles.tabActive]}
          onPress={() => setTab('attention')}
        >
          <Text style={[styles.tabText, tab === 'attention' && styles.tabTextActive]}>
            Attention
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, tab === 'decisions' && styles.tabActive]}
          onPress={() => setTab('decisions')}
        >
          <Text style={[styles.tabText, tab === 'decisions' && styles.tabTextActive]}>
            Decisions
          </Text>
        </TouchableOpacity>
      </View>

      {/* RBAC hint */}
      {!canMutate && (
        <View style={styles.rbacBanner}>
          <Text style={styles.rbacText}>Read-only — mutation actions require admin role</Text>
        </View>
      )}

      {/* Tab content */}
      {tab === 'attention' ? (
        <AttentionList onSelect={handleSelectAttention} />
      ) : (
        <DecisionsList onSelect={handleSelectDecision} />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
  },
  tabBar: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a2e',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomColor: '#6366f1',
  },
  tabText: {
    color: '#6b7280',
    fontSize: 15,
    fontWeight: '600',
  },
  tabTextActive: {
    color: '#6366f1',
  },
  rbacBanner: {
    backgroundColor: 'rgba(234,179,8,0.1)',
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  rbacText: {
    color: '#eab308',
    fontSize: 11,
    textAlign: 'center',
  },
});

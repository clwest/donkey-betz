import React, { useState } from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useAuthStore } from '../../auth/authStore';
import NeedsClassificationList from './NeedsClassificationList';
import ClassificationDetail from './ClassificationDetail';
import GatesList from './GatesList';
import type { Artifact } from '../../api/governance';

// ── Navigation state ─────────────────────────────────────────────────────────

type GovernanceView =
  | { screen: 'list' }
  | { screen: 'classificationDetail'; artifact: Artifact };

type Tab = 'classification' | 'gates';

// ── Screen ───────────────────────────────────────────────────────────────────

export default function GovernanceHomeScreen() {
  const user = useAuthStore((s) => s.user);
  const canMutate = user?.platform_role === 'admin' || user?.platform_role === 'owner';

  const [tab, setTab] = useState<Tab>('classification');
  const [view, setView] = useState<GovernanceView>({ screen: 'list' });

  const handleSelectArtifact = (artifact: Artifact) => {
    setView({ screen: 'classificationDetail', artifact });
  };

  const handleBack = () => {
    setView({ screen: 'list' });
  };

  const handleClassified = () => {
    // Return to list — it will re-fetch on mount
    setView({ screen: 'list' });
  };

  // Detail view
  if (view.screen === 'classificationDetail') {
    return (
      <ClassificationDetail
        artifact={view.artifact}
        canMutate={canMutate}
        onBack={handleBack}
        onClassified={handleClassified}
      />
    );
  }

  // List view with tabs
  return (
    <View style={styles.container}>
      {/* Tab bar */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, tab === 'classification' && styles.tabActive]}
          onPress={() => setTab('classification')}
        >
          <Text style={[styles.tabText, tab === 'classification' && styles.tabTextActive]}>
            Classification
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, tab === 'gates' && styles.tabActive]}
          onPress={() => setTab('gates')}
        >
          <Text style={[styles.tabText, tab === 'gates' && styles.tabTextActive]}>
            Gates
          </Text>
        </TouchableOpacity>
      </View>

      {/* RBAC hint */}
      {!canMutate && tab === 'classification' && (
        <View style={styles.rbacBanner}>
          <Text style={styles.rbacText}>Read-only — classification requires admin role</Text>
        </View>
      )}

      {/* Tab content */}
      {tab === 'classification' ? (
        <NeedsClassificationList onSelect={handleSelectArtifact} />
      ) : (
        <GatesList />
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

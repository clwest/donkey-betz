import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useRoute } from '@react-navigation/native';
import * as agentsApi from '../api/agents';
import CopyId from '../components/CopyId';
import { useDemo } from '../demo/useDemo';
import * as demo from '../demo/demoData';
import type {
  AgentExecution,
  AgentListItem,
  BodySummary,
} from '../api/types/agents';

// ── View state ───────────────────────────────────────────────────────────────

type AgentsView = 'overview' | 'list' | 'detail' | 'executions';

// ── Helpers ──────────────────────────────────────────────────────────────────

function statusColor(status: string): string {
  switch (status) {
    case 'completed': return '#22c55e';
    case 'failed':    return '#ef4444';
    case 'in_progress': return '#6366f1';
    case 'pending':   return '#eab308';
    default:          return '#6b7280';
  }
}

function healthColor(score: number): string {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#eab308';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}

function formatDuration(ms: number | null): string {
  if (ms == null) return '—';
  if (ms < 1000) return `${ms}ms`;
  const secs = Math.round(ms / 1000);
  if (secs < 60) return `${secs}s`;
  const mins = Math.floor(secs / 60);
  return `${mins}m ${secs % 60}s`;
}

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

function specializationColor(spec: string): string {
  switch (spec) {
    case 'content':   return '#818cf8';
    case 'research':  return '#06b6d4';
    case 'trading':   return '#22c55e';
    case 'sports-analytics': return '#f97316';
    case 'financial': return '#eab308';
    case 'business':  return '#ec4899';
    case 'technical': return '#a855f7';
    default:          return '#6b7280';
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────

export default function AgentsScreen() {
  const route = useRoute<any>();
  const initialAgentId = route.params?.agentId as string | undefined;
  const isDemo = useDemo();

  const [view, setView] = useState<AgentsView>(initialAgentId ? 'detail' : 'overview');
  const [previousView, setPreviousView] = useState<AgentsView>('overview');

  // ── Overview state ───────────────────────────────────────────────────────
  const [body, setBody] = useState<BodySummary | null>(null);
  const [overviewAgents, setOverviewAgents] = useState<AgentListItem[]>([]);
  const [recentExecs, setRecentExecs] = useState<AgentExecution[]>([]);
  const [overviewLoading, setOverviewLoading] = useState(true);
  const [overviewError, setOverviewError] = useState<string | null>(null);

  // ── List state ───────────────────────────────────────────────────────────
  const [agents, setAgents] = useState<AgentListItem[]>([]);
  const [agentsLoading, setAgentsLoading] = useState(false);
  const [agentsRefreshing, setAgentsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [specFilter, setSpecFilter] = useState<string>('all');

  // ── Detail state ─────────────────────────────────────────────────────────
  const [selectedAgent, setSelectedAgent] = useState<AgentListItem | null>(null);
  const [agentExecs, setAgentExecs] = useState<AgentExecution[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);

  // ── Executions feed state ────────────────────────────────────────────────
  const [executions, setExecutions] = useState<AgentExecution[]>([]);
  const [execLoading, setExecLoading] = useState(false);
  const [execRefreshing, setExecRefreshing] = useState(false);
  const [execStatusFilter, setExecStatusFilter] = useState<string>('all');

  // ── Data fetching ──────────────────────────────────────────────────────────

  const fetchOverview = useCallback(async () => {
    setOverviewError(null);

    if (isDemo) {
      setOverviewAgents(demo.DEMO_AGENTS as any);
      setBody({ ...demo.DEMO_BODY_SUMMARY, success: true, timestamp: new Date().toISOString() } as any);
      setRecentExecs(demo.DEMO_AGENT_EXECUTIONS as any);
      return;
    }

    try {
      const [agentRes, bodyRes, execRes] = await Promise.allSettled([
        agentsApi.listAgents({ page_size: 250 }),
        agentsApi.getBodySummary(),
        agentsApi.getExecutions({ limit: 10 }),
      ]);
      if (agentRes.status === 'fulfilled') setOverviewAgents(agentRes.value.agents ?? []);
      if (bodyRes.status === 'fulfilled') setBody(bodyRes.value);
      if (execRes.status === 'fulfilled') setRecentExecs(execRes.value.data?.executions ?? []);
      const allFailed = [agentRes, bodyRes, execRes].every((r) => r.status === 'rejected');
      if (allFailed) setOverviewError('Failed to load overview. Pull to retry.');
    } catch {
      setOverviewError('Failed to load overview.');
    }
  }, [isDemo]);

  const fetchAgents = useCallback(async () => {
    if (isDemo) {
      setAgents(demo.DEMO_AGENTS as any);
      return;
    }
    setAgentsLoading(true);
    try {
      const res = await agentsApi.listAgents({ page_size: 250 });
      setAgents(res.agents ?? []);
    } catch { /* empty */ }
    setAgentsLoading(false);
  }, [isDemo]);

  const fetchAgentDetail = useCallback(async (agent: AgentListItem) => {
    setDetailLoading(true);
    setSelectedAgent(agent);
    try {
      const res = await agentsApi.getExecutions({ agent_name: agent.name, limit: 20 });
      setAgentExecs(res.data?.executions ?? []);
    } catch { /* empty */ }
    setDetailLoading(false);
  }, []);

  const fetchExecutionsFeed = useCallback(async (status?: string) => {
    if (isDemo) {
      setExecutions(demo.DEMO_AGENT_EXECUTIONS as any);
      return;
    }
    setExecLoading(true);
    try {
      const params: { limit: number; status?: string } = { limit: 50 };
      if (status && status !== 'all') params.status = status;
      const res = await agentsApi.getExecutions(params);
      setExecutions(res.data?.executions ?? []);
    } catch { /* empty */ }
    setExecLoading(false);
  }, [isDemo]);

  // ── Initial load ─────────────────────────────────────────────────────────

  useEffect(() => {
    if (initialAgentId) {
      // Deep link: need to fetch agents to find the one, then show detail
      agentsApi.listAgents({ page_size: 250 }).then((res) => {
        const found = (res.agents ?? []).find((a) => a.id === initialAgentId || a.name === initialAgentId);
        if (found) {
          fetchAgentDetail(found);
        } else {
          setView('overview');
          fetchOverview().finally(() => setOverviewLoading(false));
        }
      }).catch(() => {
        setView('overview');
        fetchOverview().finally(() => setOverviewLoading(false));
      });
    } else {
      fetchOverview().finally(() => setOverviewLoading(false));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Navigation helpers ───────────────────────────────────────────────────

  const goTo = useCallback((target: AgentsView) => {
    setPreviousView(view);
    setView(target);
  }, [view]);

  const goBack = useCallback(() => {
    setView(previousView);
  }, [previousView]);

  const openAgent = useCallback((agent: AgentListItem) => {
    setPreviousView(view);
    setView('detail');
    fetchAgentDetail(agent);
  }, [view, fetchAgentDetail]);

  // ── Computed data ──────────────────────────────────────────────────────────

  const agentStats = useMemo(() => {
    const list = overviewAgents.length > 0 ? overviewAgents : agents;
    const active = list.filter((a) => a.is_active).length;
    const totalExecs = list.reduce((s, a) => s + (a.total_executions || 0), 0);
    const avgSuccess = list.length > 0
      ? Math.round(list.reduce((s, a) => s + (a.success_rate || 0), 0) / list.length)
      : 0;
    const specs = new Set(list.map((a) => a.specialization).filter(Boolean));
    return { total: list.length, active, totalExecs, avgSuccess, specCount: specs.size };
  }, [overviewAgents, agents]);

  const filteredAgents = useMemo(() => {
    let list = agents;
    if (specFilter !== 'all') {
      list = list.filter((a) => a.specialization === specFilter);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (a) =>
          a.name.toLowerCase().includes(q) ||
          a.display_name?.toLowerCase().includes(q) ||
          a.description?.toLowerCase().includes(q),
      );
    }
    return list;
  }, [agents, specFilter, searchQuery]);

  const specializations = useMemo(() => {
    const specs = new Set(agents.map((a) => a.specialization).filter(Boolean));
    return ['all', ...Array.from(specs).sort()];
  }, [agents]);

  // ── Tab bar ────────────────────────────────────────────────────────────────

  const tabs: Array<{ key: AgentsView; label: string }> = [
    { key: 'overview', label: 'Overview' },
    { key: 'list', label: 'Agents' },
    { key: 'executions', label: 'Feed' },
  ];

  function renderTabs() {
    const currentTab = view === 'detail' ? 'list' : view;
    return (
      <View style={styles.tabBar}>
        {tabs.map((t) => (
          <TouchableOpacity
            key={t.key}
            style={[styles.tab, currentTab === t.key && styles.tabActive]}
            onPress={() => {
              if (t.key === 'list' && agents.length === 0) fetchAgents();
              if (t.key === 'executions' && executions.length === 0) fetchExecutionsFeed();
              goTo(t.key);
            }}
          >
            <Text style={[styles.tabText, currentTab === t.key && styles.tabTextActive]}>
              {t.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  }

  // ── Overview view ──────────────────────────────────────────────────────────

  function renderOverview() {
    if (overviewLoading) {
      return (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#6366f1" />
          <Text style={styles.loadingText}>Loading agents...</Text>
        </View>
      );
    }

    return (
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={false}
            onRefresh={() => { fetchOverview(); }}
            tintColor="#6366f1"
          />
        }
      >
        {overviewError && (
          <View style={styles.errorBanner}>
            <Text style={styles.errorText}>{overviewError}</Text>
          </View>
        )}

        {/* Stats */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Agent Fleet</Text>
          <View style={styles.statRow}>
            <View style={styles.statBox}>
              <Text style={[styles.statValue, { color: '#818cf8' }]}>{agentStats.total}</Text>
              <Text style={styles.statLabel}>Total</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statValue, { color: '#22c55e' }]}>{agentStats.active}</Text>
              <Text style={styles.statLabel}>Active</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statValue, { color: '#06b6d4' }]}>{agentStats.totalExecs}</Text>
              <Text style={styles.statLabel}>Executions</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statValue, { color: '#eab308' }]}>{agentStats.avgSuccess}%</Text>
              <Text style={styles.statLabel}>Avg Success</Text>
            </View>
          </View>
        </View>

        {/* Body Systems Health */}
        {body && (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>System Health</Text>
              <Text style={[styles.badge, { backgroundColor: healthColor(body.health_score) + '30', color: healthColor(body.health_score) }]}>
                {body.health_score}%
              </Text>
            </View>
            <View style={styles.systemGrid}>
              {Object.entries(body.systems).map(([name, sys]) => (
                <View key={name} style={[styles.systemChip, !sys.healthy && styles.systemChipWarn]}>
                  <Text style={styles.systemEmoji}>{sys.emoji}</Text>
                  <Text style={[styles.systemName, !sys.healthy && { color: '#ef4444' }]}>{name}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Top Agents by Executions */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Top Agents</Text>
            <TouchableOpacity onPress={() => { if (agents.length === 0) fetchAgents(); goTo('list'); }}>
              <Text style={styles.linkText}>View all</Text>
            </TouchableOpacity>
          </View>
          {overviewAgents
            .filter((a) => a.total_executions > 0)
            .sort((a, b) => b.total_executions - a.total_executions)
            .slice(0, 8)
            .map((agent) => (
              <TouchableOpacity key={agent.id} style={styles.agentRow} onPress={() => openAgent(agent)}>
                <View style={styles.agentRowLeft}>
                  <Text style={styles.agentName} numberOfLines={1}>{agent.display_name || agent.name}</Text>
                  <Text style={styles.agentMeta}>{agent.specialization || agent.agent_type}</Text>
                </View>
                <View style={styles.agentRowRight}>
                  <Text style={styles.execCount}>{agent.total_executions} runs</Text>
                  <Text style={[styles.successRate, { color: healthColor(agent.success_rate) }]}>
                    {Math.round(agent.success_rate)}%
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
        </View>

        {/* Recent Executions */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Recent Executions</Text>
            <TouchableOpacity onPress={() => { fetchExecutionsFeed(); goTo('executions'); }}>
              <Text style={styles.linkText}>View all</Text>
            </TouchableOpacity>
          </View>
          {recentExecs.length > 0 ? (
            recentExecs.slice(0, 5).map((exec) => (
              <View key={exec.id} style={styles.execRow}>
                <View style={[styles.statusDot, { backgroundColor: statusColor(exec.status) }]} />
                <View style={styles.execInfo}>
                  <Text style={styles.execAgent} numberOfLines={1}>{exec.agent_name}</Text>
                  <Text style={styles.execTask} numberOfLines={1}>{exec.task_summary || exec.task}</Text>
                </View>
                <View style={styles.execMeta}>
                  <Text style={styles.execTime}>{timeAgo(exec.created_at)}</Text>
                  <Text style={styles.execDuration}>{formatDuration(exec.execution_time_ms)}</Text>
                </View>
              </View>
            ))
          ) : (
            <Text style={styles.mutedText}>No recent executions</Text>
          )}
        </View>

        <View style={{ height: 24 }} />
      </ScrollView>
    );
  }

  // ── List view ──────────────────────────────────────────────────────────────

  function renderList() {
    return (
      <View style={styles.container}>
        {/* Search */}
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Search agents..."
            placeholderTextColor="#6b7280"
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoCapitalize="none"
            autoCorrect={false}
          />
        </View>

        {/* Specialization filters */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll} contentContainerStyle={styles.filterRow}>
          {specializations.map((spec) => (
            <TouchableOpacity
              key={spec}
              style={[styles.filterChip, specFilter === spec && styles.filterChipActive]}
              onPress={() => setSpecFilter(spec)}
            >
              <Text style={[styles.filterChipText, specFilter === spec && styles.filterChipTextActive]}>
                {spec === 'all' ? 'All' : spec}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {agentsLoading && agents.length === 0 ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#6366f1" />
          </View>
        ) : (
          <FlatList
            data={filteredAgents}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.content}
            refreshControl={
              <RefreshControl
                refreshing={agentsRefreshing}
                onRefresh={async () => { setAgentsRefreshing(true); await fetchAgents(); setAgentsRefreshing(false); }}
                tintColor="#6366f1"
              />
            }
            renderItem={({ item }) => (
              <TouchableOpacity style={styles.card} onPress={() => openAgent(item)}>
                <View style={styles.cardHeader}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.agentName} numberOfLines={1}>{item.display_name || item.name}</Text>
                    <Text style={styles.agentMeta}>{item.specialization || item.agent_type}</Text>
                  </View>
                  <View style={[styles.statusPill, { backgroundColor: item.is_active ? 'rgba(34,197,94,0.2)' : 'rgba(107,114,128,0.2)' }]}>
                    <Text style={[styles.statusPillText, { color: item.is_active ? '#22c55e' : '#6b7280' }]}>
                      {item.is_active ? 'Active' : 'Inactive'}
                    </Text>
                  </View>
                </View>
                {item.description ? (
                  <Text style={styles.agentDesc} numberOfLines={2}>{item.description}</Text>
                ) : null}
                <View style={styles.agentFooter}>
                  <Text style={styles.footerStat}>{item.total_executions} runs</Text>
                  <Text style={[styles.footerStat, { color: healthColor(item.success_rate) }]}>
                    {Math.round(item.success_rate)}% success
                  </Text>
                  {item.effectiveness_score > 0 && (
                    <Text style={styles.footerStat}>eff: {item.effectiveness_score}</Text>
                  )}
                </View>
              </TouchableOpacity>
            )}
            ListEmptyComponent={
              <View style={styles.emptyState}>
                <Text style={styles.emptyText}>
                  {searchQuery ? 'No agents match your search' : 'No agents found'}
                </Text>
              </View>
            }
          />
        )}
      </View>
    );
  }

  // ── Detail view ────────────────────────────────────────────────────────────

  function renderDetail() {
    if (!selectedAgent) return null;

    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        {/* Back + Copy ID */}
        <View style={styles.detailTopRow}>
          <TouchableOpacity style={styles.backButton} onPress={goBack}>
            <Text style={styles.backText}>{'< Back'}</Text>
          </TouchableOpacity>
          <CopyId value={selectedAgent.name} label="Agent name" />
        </View>

        {/* Header */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.detailTitle}>{selectedAgent.display_name || selectedAgent.name}</Text>
            <View style={[styles.statusPill, { backgroundColor: selectedAgent.is_active ? 'rgba(34,197,94,0.2)' : 'rgba(107,114,128,0.2)' }]}>
              <Text style={[styles.statusPillText, { color: selectedAgent.is_active ? '#22c55e' : '#6b7280' }]}>
                {selectedAgent.is_active ? 'Active' : 'Inactive'}
              </Text>
            </View>
          </View>
          {selectedAgent.description ? (
            <Text style={styles.detailDesc}>{selectedAgent.description}</Text>
          ) : null}
          <View style={styles.detailMeta}>
            {selectedAgent.specialization ? (
              <View style={[styles.specChip, { backgroundColor: specializationColor(selectedAgent.specialization) + '25' }]}>
                <Text style={[styles.specChipText, { color: specializationColor(selectedAgent.specialization) }]}>
                  {selectedAgent.specialization}
                </Text>
              </View>
            ) : null}
            {selectedAgent.agent_type ? (
              <View style={styles.specChip}>
                <Text style={styles.specChipText}>{selectedAgent.agent_type}</Text>
              </View>
            ) : null}
          </View>
        </View>

        {/* Performance */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Performance</Text>
          <View style={styles.statRow}>
            <View style={styles.statBox}>
              <Text style={[styles.statValue, { color: '#818cf8' }]}>{selectedAgent.total_executions}</Text>
              <Text style={styles.statLabel}>Runs</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statValue, { color: '#22c55e' }]}>{selectedAgent.successful_executions}</Text>
              <Text style={styles.statLabel}>Success</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statValue, { color: healthColor(selectedAgent.success_rate) }]}>
                {Math.round(selectedAgent.success_rate)}%
              </Text>
              <Text style={styles.statLabel}>Rate</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statValue, { color: '#06b6d4' }]}>{selectedAgent.effectiveness_score}</Text>
              <Text style={styles.statLabel}>Effective</Text>
            </View>
          </View>
          {selectedAgent.lastActive && (
            <Text style={styles.mutedText}>Last active: {timeAgo(selectedAgent.lastActive)}</Text>
          )}
        </View>

        {/* Recent Executions */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Recent Executions</Text>
            {agentExecs.length > 5 && (
              <Text style={styles.mutedText}>{agentExecs.length} total</Text>
            )}
          </View>
          {detailLoading ? (
            <ActivityIndicator color="#6366f1" style={{ marginVertical: 12 }} />
          ) : agentExecs.length > 0 ? (
            agentExecs.slice(0, 10).map((exec) => (
              <View key={exec.id} style={styles.execRow}>
                <View style={[styles.statusDot, { backgroundColor: statusColor(exec.status) }]} />
                <View style={styles.execInfo}>
                  <Text style={styles.execTask} numberOfLines={2}>{exec.task_summary || exec.task}</Text>
                  {exec.error_message && (
                    <Text style={styles.execError} numberOfLines={1}>{exec.error_message}</Text>
                  )}
                </View>
                <View style={styles.execMeta}>
                  <Text style={styles.execTime}>{timeAgo(exec.created_at)}</Text>
                  <Text style={styles.execDuration}>{formatDuration(exec.execution_time_ms)}</Text>
                </View>
              </View>
            ))
          ) : (
            <Text style={styles.mutedText}>No executions found</Text>
          )}
        </View>

        <View style={{ height: 24 }} />
      </ScrollView>
    );
  }

  // ── Executions feed view ───────────────────────────────────────────────────

  function renderExecutionsFeed() {
    const statusFilters = ['all', 'completed', 'failed', 'in_progress', 'pending'];

    return (
      <View style={styles.container}>
        {/* Status filters */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll} contentContainerStyle={styles.filterRow}>
          {statusFilters.map((s) => (
            <TouchableOpacity
              key={s}
              style={[styles.filterChip, execStatusFilter === s && styles.filterChipActive]}
              onPress={() => { setExecStatusFilter(s); fetchExecutionsFeed(s); }}
            >
              <Text style={[styles.filterChipText, execStatusFilter === s && styles.filterChipTextActive]}>
                {s === 'all' ? 'All' : s.replace('_', ' ')}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {execLoading && executions.length === 0 ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#6366f1" />
          </View>
        ) : (
          <FlatList
            data={executions}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.content}
            refreshControl={
              <RefreshControl
                refreshing={execRefreshing}
                onRefresh={async () => { setExecRefreshing(true); await fetchExecutionsFeed(execStatusFilter); setExecRefreshing(false); }}
                tintColor="#6366f1"
              />
            }
            renderItem={({ item }) => (
              <View style={styles.execCard}>
                <View style={styles.execCardHeader}>
                  <View style={[styles.statusDot, { backgroundColor: statusColor(item.status) }]} />
                  <Text style={styles.execAgent} numberOfLines={1}>{item.agent_name}</Text>
                  <Text style={[styles.statusBadge, { color: statusColor(item.status) }]}>{item.status}</Text>
                </View>
                <Text style={styles.execTask} numberOfLines={2}>{item.task_summary || item.task}</Text>
                {item.error_message && (
                  <Text style={styles.execError} numberOfLines={2}>{item.error_message}</Text>
                )}
                <View style={styles.execCardFooter}>
                  <Text style={styles.execTime}>{timeAgo(item.created_at)}</Text>
                  <Text style={styles.execDuration}>{formatDuration(item.execution_time_ms)}</Text>
                  {item.tokens_used != null && (
                    <Text style={styles.execTokens}>{item.tokens_used} tokens</Text>
                  )}
                </View>
              </View>
            )}
            ListEmptyComponent={
              <View style={styles.emptyState}>
                <Text style={styles.emptyText}>No executions found</Text>
              </View>
            }
          />
        )}
      </View>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <View style={styles.root}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Agents</Text>
        <Text style={styles.headerSubtitle}>{agentStats.total} registered agents</Text>
      </View>

      {view !== 'detail' && renderTabs()}

      {view === 'overview' && renderOverview()}
      {view === 'list' && renderList()}
      {view === 'detail' && renderDetail()}
      {view === 'executions' && renderExecutionsFeed()}
    </View>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#0a0a0f',
  },
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
  },
  content: {
    padding: 12,
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    color: '#6b7280',
    fontSize: 14,
    marginTop: 12,
  },

  // Header
  header: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
  },
  headerTitle: {
    color: '#ffffff',
    fontSize: 22,
    fontWeight: '800',
  },
  headerSubtitle: {
    color: '#6b7280',
    fontSize: 13,
    marginTop: 2,
  },

  // Tabs
  tabBar: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    marginBottom: 4,
    gap: 6,
  },
  tab: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#1a1a2e',
  },
  tabActive: {
    backgroundColor: '#6366f1',
  },
  tabText: {
    color: '#9ca3af',
    fontSize: 13,
    fontWeight: '600',
  },
  tabTextActive: {
    color: '#ffffff',
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
    marginBottom: 10,
  },
  cardTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
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

  // Body systems
  systemGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 4,
  },
  systemChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(99, 102, 241, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  systemChipWarn: {
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
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

  // Badge
  badge: {
    fontSize: 12,
    fontWeight: '700',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
    overflow: 'hidden',
  },

  // Agent rows (overview)
  agentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  agentRowLeft: {
    flex: 1,
  },
  agentRowRight: {
    alignItems: 'flex-end',
  },
  agentName: {
    color: '#d1d5db',
    fontSize: 14,
    fontWeight: '600',
  },
  agentMeta: {
    color: '#6b7280',
    fontSize: 11,
    marginTop: 2,
    textTransform: 'capitalize',
  },
  execCount: {
    color: '#9ca3af',
    fontSize: 12,
  },
  successRate: {
    fontSize: 12,
    fontWeight: '600',
  },

  // Agent detail
  detailTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '800',
    flex: 1,
  },
  detailDesc: {
    color: '#9ca3af',
    fontSize: 13,
    lineHeight: 20,
  },
  detailMeta: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 10,
  },

  // Agent list items
  agentDesc: {
    color: '#9ca3af',
    fontSize: 12,
    lineHeight: 18,
    marginBottom: 8,
  },
  agentFooter: {
    flexDirection: 'row',
    gap: 12,
  },
  footerStat: {
    color: '#6b7280',
    fontSize: 11,
  },

  // Status pill
  statusPill: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
  },
  statusPillText: {
    fontSize: 11,
    fontWeight: '600',
  },

  // Specialization chip
  specChip: {
    backgroundColor: 'rgba(107,114,128,0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  specChipText: {
    color: '#9ca3af',
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'capitalize',
  },

  // Execution rows
  execRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 10,
  },
  execInfo: {
    flex: 1,
  },
  execAgent: {
    color: '#d1d5db',
    fontSize: 13,
    fontWeight: '600',
  },
  execTask: {
    color: '#9ca3af',
    fontSize: 12,
    marginTop: 2,
  },
  execError: {
    color: '#ef4444',
    fontSize: 11,
    marginTop: 2,
  },
  execMeta: {
    alignItems: 'flex-end',
    marginLeft: 8,
  },
  execTime: {
    color: '#6b7280',
    fontSize: 11,
  },
  execDuration: {
    color: '#4b5563',
    fontSize: 11,
    marginTop: 2,
  },
  execTokens: {
    color: '#4b5563',
    fontSize: 10,
    marginTop: 1,
  },

  // Execution feed cards
  execCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
  },
  execCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  statusBadge: {
    fontSize: 11,
    fontWeight: '600',
    marginLeft: 'auto',
    textTransform: 'capitalize',
  },
  execCardFooter: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
  },

  // Search
  searchContainer: {
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  searchInput: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    color: '#ffffff',
    fontSize: 14,
    borderWidth: 1,
    borderColor: 'rgba(99,102,241,0.2)',
  },

  // Filter chips
  filterScroll: {
    maxHeight: 44,
    marginBottom: 4,
  },
  filterRow: {
    paddingHorizontal: 12,
    gap: 6,
  },
  filterChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    backgroundColor: '#1a1a2e',
  },
  filterChipActive: {
    backgroundColor: '#6366f1',
  },
  filterChipText: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  filterChipTextActive: {
    color: '#ffffff',
  },

  // Empty/muted
  emptyState: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: '#6b7280',
    fontSize: 14,
  },
  mutedText: {
    color: '#6b7280',
    fontSize: 13,
  },

  // Back button
  detailTopRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  backButton: {
    paddingVertical: 8,
  },
  backText: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600',
  },

  // Link
  linkText: {
    color: '#6366f1',
    fontSize: 13,
    fontWeight: '600',
  },
});

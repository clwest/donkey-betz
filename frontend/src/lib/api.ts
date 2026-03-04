import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

// Session 968: Extend axios config to carry request-log metadata
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: { requestId: number; startTime: number }
  }
}

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Session 802: Add 90-second timeout to prevent browser default (2 min) timeout
  // This ensures we get a proper error before the browser silently times out
  timeout: 90000,
  // Session 819: Include credentials (cookies) for session authentication
  // This allows Django session auth to work for cross-origin requests
  withCredentials: true,
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    // Session 819: Debug logging for auth issues
    if (process.env.NODE_ENV === 'development' || config.url?.includes('/platform/')) {
      console.log('[API Auth]', config.url, token ? 'Token present' : 'No token', 'withCredentials:', config.withCredentials)
    }
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Session 819: Only redirect to login for explicit auth endpoints
    // Other 401s should be handled by the component (user might just need to refresh)
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      const isAuthEndpoint = url.includes('/auth/') || url.includes('/login')

      // Only force logout/redirect for auth-related 401s
      if (isAuthEndpoint) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
      // For other endpoints, just log the error - component can handle it
      console.warn('Authentication required for:', url)
    }
    return Promise.reject(error)
  }
)

// API endpoints

// Session 884: Home Page Boot API
export const homeApi = {
  boot: () => api.get('/home/boot/'),
  intelligenceDesks: () => api.get('/home/intelligence-desks/'),
  triggerDesks: () => api.post('/home/trigger-desks/'),
}

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/v1/auth/login/', { username, password }),
  logout: () => api.post('/v1/auth/logout/'),
  getUser: () => api.get('/v1/auth/user/'),
  validateToken: () => api.post('/v1/auth/validate-token/'),
}

export const agentsApi = {
  list: () => api.get('/v1/agents/list/'),
  comprehensive: () => api.get('/v1/agents/comprehensive/'),
  health: () => api.get('/v1/agents/health/'),
  execute: (agentName: string, task: string) =>
    api.post('/v1/agents/execute/', { agent_name: agentName, task }),
  executionHistory: (limit = 20) => api.get(`/v1/agents/execution-history/?limit=${limit}`),
  // Session 760: Unified executions with full output_data for Output Modal
  unifiedExecutions: (params?: { limit?: number; agent_name?: string; status?: string }) =>
    api.get('/v1/agents/unified-executions/', { params }),
  executionDetail: (executionId: string) => api.get(`/v1/agents/execution/${executionId}/`),
}

// Session 734: Agent Channels API - "Slack for AI Agents"
export const agentChannelsApi = {
  // Channels
  list: (params?: { channel_type?: string; search?: string }) =>
    api.get('/v1/agents/channels/', { params }),
  create: (data: { name: string; display_name?: string; description?: string; channel_type?: string }) =>
    api.post('/v1/agents/channels/', data),
  detail: (id: string) => api.get(`/v1/agents/channels/${id}/`),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/v1/agents/channels/${id}/`, data),
  delete: (id: string) => api.delete(`/v1/agents/channels/${id}/`),
  join: (id: string) => api.post(`/v1/agents/channels/${id}/join/`),
  leave: (id: string) => api.post(`/v1/agents/channels/${id}/leave/`),

  // Messages
  messages: (channelId: string, params?: { limit?: number; before?: string }) =>
    api.get('/v1/agents/messages/', { params: { channel: channelId, ...params } }),
  sendMessage: (data: { channel: string; content: string; message_type?: string }) =>
    api.post('/v1/agents/messages/', data),
  messageDetail: (id: string) => api.get(`/v1/agents/messages/${id}/`),

  // Memberships
  memberships: (channelId: string) =>
    api.get('/v1/agents/memberships/', { params: { channel: channelId } }),
  addMember: (data: { channel: string; agent?: string; role?: string }) =>
    api.post('/v1/agents/memberships/', data),
}

// Session 734: Agent Monitoring API - Performance dashboards and metrics
export const agentMonitoringApi = {
  // Dashboard & Metrics
  dashboard: (period?: '1h' | '24h' | '7d' | '30d') =>
    api.get('/v1/agents/monitoring/dashboard/', { params: { period } }),
  agentPerformance: (agentName: string) =>
    api.get(`/v1/agents/monitoring/agent/${agentName}/`),
  report: () => api.get('/v1/agents/monitoring/report/'),

  // Real-time & Alerts
  realTime: () => api.get('/v1/agents/monitoring/real-time/'),
  alerts: () => api.get('/v1/agents/monitoring/alerts/'),

  // Actions
  clearCache: () => api.post('/v1/agents/monitoring/cache/clear/'),
}

// Session 734: Agent Tools API - Tool registry and configuration
export const agentToolsApi = {
  list: (params?: { tool_type?: string; is_active?: boolean }) =>
    api.get('/v1/agents/tools/', { params }),
  detail: (id: string) => api.get(`/v1/agents/tools/${id}/`),
  create: (data: {
    name: string
    display_name: string
    description: string
    tool_type: string
    endpoint_url?: string
    tool_config?: Record<string, unknown>
  }) => api.post('/v1/agents/tools/', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/v1/agents/tools/${id}/`, data),
  delete: (id: string) => api.delete(`/v1/agents/tools/${id}/`),
}

// Session 734: Agent Templates API - CRUD for agent templates
export const agentTemplatesApi = {
  list: (params?: {
    specialization?: string
    llm_provider?: string
    is_active?: boolean
    is_public?: boolean
    search?: string
  }) => api.get('/v1/agents/templates/', { params }),
  detail: (id: string) => api.get(`/v1/agents/templates/${id}/`),
  create: (data: {
    name: string
    display_name: string
    description: string
    specialization?: string
    capabilities?: string
    system_prompt?: string
    personality_traits?: string
    llm_provider?: string
    llm_model?: string
    routing_keywords?: string
    is_public?: boolean
    learning_enabled?: boolean
  }) => api.post('/v1/agents/templates/', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/v1/agents/templates/${id}/`, data),
  delete: (id: string) => api.delete(`/v1/agents/templates/${id}/`),
}

// Session 734: Agent Orchestrations API - Multi-agent workflow management
// Session 735: Added output action for viewing full results
export const agentOrchestrationsApi = {
  list: (params?: { status?: string; execution_strategy?: string }) =>
    api.get('/v1/agents/orchestrations/', { params }),
  detail: (id: string) => api.get(`/v1/agents/orchestrations/${id}/`),
  create: (data: {
    name: string
    description?: string
    workflow_definition?: Record<string, unknown>
    agent_sequence?: string[]
    execution_strategy?: string
  }) => api.post('/v1/agents/orchestrations/', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/v1/agents/orchestrations/${id}/`, data),
  delete: (id: string) => api.delete(`/v1/agents/orchestrations/${id}/`),
  execute: (id: string) => api.post(`/v1/agents/orchestrations/${id}/execute/`),
  reset: (id: string) => api.post(`/v1/agents/orchestrations/${id}/reset/`),
  output: (id: string) => api.get(`/v1/agents/orchestrations/${id}/output/`),
}

export const activityApi = {
  recent: (limit = 20, hours = 72) => api.get(`/recent-activity/?limit=${limit}&hours=${hours}`),
  learning: (limit = 20) => api.get(`/agent-learning/activity/?limit=${limit}`),
}

// Session 695: Dreams API for Dream Gallery Modal
// Session 716: Enhanced with trigger, rate, and preferences
// Session 735: Added time_range and pagination support
export type TimeRange = '24h' | '7d' | '30d' | 'all'

export const dreamsApi = {
  list: (params?: {
    limit?: number
    offset?: number
    timeRange?: TimeRange
    agentId?: string
    unreadOnly?: boolean
  }) => {
    const { limit = 20, offset = 0, timeRange = '24h', agentId, unreadOnly = false } = params || {}
    const queryParams = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
      time_range: timeRange,
    })
    if (agentId) queryParams.append('agent_id', agentId)
    if (unreadOnly) queryParams.append('unread_only', 'true')
    return api.get(`/agent-dreams/?${queryParams.toString()}`)
  },
  detail: (dreamId: string) => api.get(`/agent-dreams/${dreamId}/`),
  react: (dreamId: string, reaction: string) => api.post(`/agent-dreams/${dreamId}/react/`, { reaction }),
  rate: (dreamId: string, rating: number) => api.post(`/agent-dreams/${dreamId}/rate/`, { rating }),
  markShown: (dreamIds: string[]) => api.post('/agent-dreams/mark-shown/', { dream_ids: dreamIds }),
  trigger: () => api.post('/agent-dreams/trigger/'),
  preferences: () => api.get('/agent-dreams/preferences/'),
  exploration: (explorationId: string) => api.get(`/agent-dreams/explorations/${explorationId}/`),
}

// Session 695: Conversations API for Conversation Thread Viewer
// Session 716: Enhanced with trigger
// Session 735: Added time_range and pagination support
// Session 826: Enhanced with goal-driven conversation creation
export const conversationsApi = {
  list: (params?: {
    limit?: number
    offset?: number
    timeRange?: TimeRange
    status?: string
  }) => {
    const { limit = 20, offset = 0, timeRange = '7d', status } = params || {}
    const queryParams = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
      time_range: timeRange,
    })
    if (status) queryParams.append('status', status)
    return api.get(`/agent-conversations/?${queryParams.toString()}`)
  },
  detail: (conversationId: string) => api.get(`/agent-conversations/${conversationId}/`),
  trigger: () => api.post('/agent-conversations/trigger/'),
  // Session 826: Create goal-driven conversation
  create: (params: {
    topic: string
    conversation_type?: 'analytical' | 'creative' | 'debate' | 'planning' | 'critique' | 'general'
    objective?: string
    success_criteria?: string[]
    auto_select_agents?: boolean
  }) => api.post('/agent-conversations/trigger/', params),
}

// Session 717: Conversation Contract API - Quality analytics for agent conversations
export const conversationContractApi = {
  // Get overview with compliance stats and recent conversations
  overview: (days = 30) => api.get(`/conversation-contract/overview/?days=${days}`),
  // Get detailed contract analysis for a specific conversation
  detail: (conversationId: string) => api.get(`/conversation-contract/${conversationId}/`),
}

// Session 715: Hive Mind API - Multi-agent collaborative sessions
export const hiveMindApi = {
  // List recent sessions
  list: (limit = 20) => api.get(`/hive-mind/sessions/?limit=${limit}`),

  // Get session details and contributions
  detail: (sessionId: string) => api.get(`/hive-mind/session/${sessionId}/`),

  // Start a new hive mind session
  start: (data: { question: string; context?: string; max_agents?: number }) =>
    api.post('/hive-mind/start/', data),

  // Preview which agents would be selected for a question
  preview: (data: { question: string; max_agents?: number }) =>
    api.post('/hive-mind/preview/', data),

  // Get list of available agents for hive mind
  agents: () => api.get('/hive-mind/agents/'),
}

// Session 716: Memory Palace API - Agent memory visualization
export const memoryPalaceApi = {
  // Overview of all agents' memory palaces
  overview: () => api.get('/memory-palace/'),

  // Session 860: List all memories with filters
  listMemories: (params?: { safety_class?: string; memory_type?: string; valence?: string; limit?: number; offset?: number }) =>
    api.get('/memory-palace/memories/', { params }),

  // Agent-specific endpoints
  // Session 753: Added outcome and sort_by parameters
  // Session 754: Added tag filter parameter
  agentMemories: (agentId: string, params?: { type?: string; valence?: string; outcome?: string; sort_by?: string; tag?: string; limit?: number }) =>
    api.get(`/memory-palace/agent/${agentId}/memories/`, { params }),
  agentRooms: (agentId: string) => api.get(`/memory-palace/agent/${agentId}/rooms/`),
  agentSummary: (agentId: string, limit = 10) =>
    api.get(`/memory-palace/agent/${agentId}/summary/?limit=${limit}`),

  // Memory-specific endpoints
  memoryDetail: (memoryId: string) => api.get(`/memory-palace/memory/${memoryId}/`),
  memoryConnections: (memoryId: string) => api.get(`/memory-palace/memory/${memoryId}/connections/`),
  deleteMemory: (memoryId: string) => api.delete(`/memory-palace/memory/${memoryId}/delete/`),

  // Room memories
  roomMemories: (roomId: string) => api.get(`/memory-palace/room/${roomId}/memories/`),

  // Actions
  createMemory: (data: {
    agent_id: string
    title: string
    content: string
    memory_type?: string
    valence?: string
    importance?: number
    context?: string
  }) => api.post('/memory-palace/create/', data),

  searchMemories: (data: { agent_id: string; query: string; memory_types?: string[]; limit?: number }) =>
    api.post('/memory-palace/search/', data),

  assignToRoom: (memoryId: string, roomId: string) =>
    api.post('/memory-palace/assign/', { memory_id: memoryId, room_id: roomId }),

  connectMemories: (sourceId: string, targetId: string, connectionType = 'similar', strength = 0.5) =>
    api.post('/memory-palace/connect/', {
      source_id: sourceId,
      target_id: targetId,
      connection_type: connectionType,
      strength,
    }),
}

// Session 718: Memory Clusters API - Semantic memory grouping via embedding-based clustering
export const memoryClustersApi = {
  // Overview of all clusters across agents
  overview: () => api.get('/memory-clusters/'),

  // Agent-specific clusters
  agentClusters: (agentId: string) => api.get(`/memory-clusters/agent/${agentId}/`),
  generateClusters: (agentId: string, data?: { n_clusters?: number; method?: string; min_memories?: number }) =>
    api.post(`/memory-clusters/agent/${agentId}/`, data || {}),

  // Cluster detail
  detail: (clusterId: string) => api.get(`/memory-clusters/cluster/${clusterId}/`),

  // Visualization data for D3.js force-directed graph
  visualization: (agentId?: string) =>
    agentId
      ? api.get(`/memory-clusters/visualization/${agentId}/`)
      : api.get('/memory-clusters/visualization/'),

  // Generate clusters for all agents
  generateAll: (data?: { min_memories?: number; method?: string }) =>
    api.post('/memory-clusters/generate-all/', data || {}),

  // Manage cluster memberships
  addMemory: (clusterId: string, memoryId: string) =>
    api.post(`/memory-clusters/cluster/${clusterId}/add-memory/`, { memory_id: memoryId }),
  removeMemory: (clusterId: string, memoryId: string) =>
    api.delete(`/memory-clusters/cluster/${clusterId}/memory/${memoryId}/`),

  // Evolution history
  evolution: (agentId: string) => api.get(`/memory-clusters/evolution/${agentId}/`),

  // Find similar clusters
  findSimilar: (data: { query?: string; memory_id?: string; limit?: number }) =>
    api.post('/memory-clusters/find-similar/', data),
}

// Session 716: Agent Evolution API - XP, Levels, Abilities, Prestige
export const evolutionApi = {
  // Overview of entire evolution system
  overview: () => api.get('/agent-evolution/'),

  // Agent-specific evolution data
  agentDetail: (agentId: string) => api.get(`/agent-evolution/agent/${agentId}/`),

  // XP & Progression
  awardXp: (agentId: string, data: { xp_amount: number; reason: string }) =>
    api.post(`/agent-evolution/agent/${agentId}/award-xp/`, data),
  prestige: (agentId: string) =>
    api.post(`/agent-evolution/agent/${agentId}/prestige/`),
  recordTask: (agentId: string, data: { task_type: string; success: boolean; metrics?: Record<string, unknown> }) =>
    api.post(`/agent-evolution/agent/${agentId}/task/`, data),

  // Abilities
  availableAbilities: () => api.get('/agent-evolution/abilities/'),
  createAbility: (data: {
    name: string
    description: string
    level_required: number
    xp_cost: number
    ability_type: string
  }) => api.post('/agent-evolution/abilities/create/', data),
  unlockAbility: (agentId: string, abilityId: string) =>
    api.post(`/agent-evolution/agent/${agentId}/unlock/${abilityId}/`),

  // Leaderboard & Stats
  leaderboard: (limit = 20) => api.get(`/agent-evolution/leaderboard/?limit=${limit}`),
  recentXpGains: (limit = 50) => api.get(`/agent-evolution/xp-gains/?limit=${limit}`),

  // Admin
  initializeAll: () => api.post('/agent-evolution/initialize/'),
}

// Session 716: Agent Mood API - Emotional state and personality
export const moodApi = {
  // Overview of all agent moods
  overview: () => api.get('/agent-mood/'),

  // Agent-specific mood data
  agentMood: (agentId: string) => api.get(`/agent-mood/agent/${agentId}/`),
  setMood: (agentId: string, data: { mood: string; intensity?: number; reason?: string }) =>
    api.post(`/agent-mood/agent/${agentId}/set/`, data),
  moodHistory: (agentId: string, limit = 50) =>
    api.get(`/agent-mood/agent/${agentId}/history/?limit=${limit}`),
  promptContext: (agentId: string) =>
    api.get(`/agent-mood/agent/${agentId}/prompt-context/`),

  // Mood rules
  rules: () => api.get('/agent-mood/rules/'),
  createRule: (data: {
    name: string
    description?: string
    agent_id?: string | null
    condition_type: string
    condition_value?: Record<string, unknown>
    target_mood: string
    target_intensity?: number  // 0-1 decimal
    duration_minutes?: number
    priority?: number
  }) => api.post('/agent-mood/rules/create/', data),
  deleteRule: (ruleId: string) => api.delete(`/agent-mood/rules/${ruleId}/delete/`),

  // Trigger mood from memory
  triggerFromMemory: (data: { agent_id: string; memory_id: string }) =>
    api.post('/agent-mood/trigger-from-memory/', data),
}

// Session 716: Time Travel API - Decision tracking and session replay
export const timeTravelApi = {
  // Overview
  overview: () => api.get('/time-travel/'),

  // Sessions
  sessionDetail: (sessionId: string) => api.get(`/time-travel/session/${sessionId}/`),
  startSession: (data: { agent_id: string; context?: string }) =>
    api.post('/time-travel/session/start/', data),
  endSession: (sessionId: string) => api.post(`/time-travel/session/${sessionId}/end/`),
  toggleBookmarkSession: (sessionId: string) =>
    api.post(`/time-travel/session/${sessionId}/bookmark/`),

  // Decisions
  recordDecision: (data: {
    session_id: string
    decision_type: string
    description: string
    options_considered?: string[]
    chosen_option?: string
    reasoning?: string
  }) => api.post('/time-travel/decision/', data),
  updateOutcome: (decisionId: string, data: { outcome: string; success?: boolean }) =>
    api.post(`/time-travel/decision/${decisionId}/outcome/`, data),
  flagDecision: (decisionId: string, data: { reason: string }) =>
    api.post(`/time-travel/decision/${decisionId}/flag/`, data),

  // Bookmarks & Annotations
  createBookmark: (data: { session_id: string; label: string; notes?: string }) =>
    api.post('/time-travel/bookmark/', data),
  deleteBookmark: (bookmarkId: string) => api.delete(`/time-travel/bookmark/${bookmarkId}/`),
  addAnnotation: (data: { decision_id: string; text: string }) =>
    api.post('/time-travel/annotation/', data),
  deleteAnnotation: (annotationId: string) =>
    api.delete(`/time-travel/annotation/${annotationId}/`),

  // Search & Filters
  searchSessions: (data: { query?: string; agent_id?: string; date_from?: string; date_to?: string }) =>
    api.post('/time-travel/search/', data),
  flaggedDecisions: (limit = 50) => api.get(`/time-travel/flagged/?limit=${limit}`),

  // Agent-specific
  agentSessions: (agentId: string, limit = 20) =>
    api.get(`/time-travel/agent/${agentId}/sessions/?limit=${limit}`),
  simulateSession: (agentId: string, data: { scenario: string }) =>
    api.post(`/time-travel/agent/${agentId}/simulate/`, data),
}

// Session 716: Time Capsules API - Agent messages to the future
export const timeCapsuleApi = {
  // Overview of all time capsules
  overview: () => api.get('/time-capsules/'),

  // Agent-specific capsules
  agentCapsules: (agentId: string) => api.get(`/time-capsules/agent/${agentId}/`),

  // Capsule operations
  detail: (capsuleId: string) => api.get(`/time-capsules/${capsuleId}/`),
  reveal: (capsuleId: string) => api.post(`/time-capsules/${capsuleId}/reveal/`),
  react: (capsuleId: string, data: { reaction: string; message?: string }) =>
    api.post(`/time-capsules/${capsuleId}/react/`, data),

  // Ready to reveal
  readyToReveal: () => api.get('/time-capsules/ready-to-reveal/'),

  // Generate new capsule
  generate: (data: { agent_id: string; open_after_days?: number }) =>
    api.post('/time-capsules/generate/', data),

  // Admin
  expireOld: () => api.post('/time-capsules/expire-old/'),
}

// Session 696: Decisions API for Decision Insights Panel
// Session 1070: Decision Gate Classification API
export const classificationApi = {
  listUnclassified: (limit = 50) =>
    api.get(`/artifacts/needs-classification/?limit=${limit}`),
  classifyArtifact: (artifactId: string, classification: {
    what_is_this: string
    who_is_it_for: string
    data_allowed: string
    phase_approved: string
  }, autoApprove = false) =>
    api.post(`/artifacts/${artifactId}/classify/`, { ...classification, auto_approve: autoApprove }),
}

export const decisionsApi = {
  list: (limit = 50) => api.get(`/boardroom/decisions/?limit=${limit}`),
  detail: (decisionId: string) => api.get(`/boardroom/decisions/${decisionId}/`),
  approve: (decisionId: string) => api.post(`/boardroom/decisions/${decisionId}/approve/`),
  reject: (decisionId: string, reason?: string) => api.post(`/boardroom/decisions/${decisionId}/reject/`, { reason }),
  promote: (decisionId: string) => api.post(`/boardroom/decisions/${decisionId}/promote/`),
  // Session 942: Bulk actions
  bulkPromote: (decisionIds: string[]) => api.post('/boardroom/decisions/bulk-promote/', { decision_ids: decisionIds }),
  bulkReject: (decisionIds: string[]) => api.post('/boardroom/decisions/bulk-reject/', { decision_ids: decisionIds }),
  // Session 1067: Governance stats for full-page view
  governanceStats: () => api.get('/boardroom/governance-stats/'),
}

// Session 710: Body Health Dashboard API
export const bodyApi = {
  vitals: (includeDetails = false) => api.get(`/body/vitals/?include_details=${includeDetails}`),
  alerts: (severity = 'info', limit = 50) => api.get(`/body/alerts/?severity=${severity}&limit=${limit}`),
  history: (hours = 24, system?: string) => {
    const params = new URLSearchParams({ hours: String(hours) })
    if (system) params.append('system', system)
    return api.get(`/body/history/?${params}`)
  },
  summary: () => api.get('/body/summary/'),
  system: (systemName: string) => api.get(`/body/${systemName}/`),
  // Session 711: Body Coordination API
  coordination: {
    status: () => api.get('/body/coordination/status/'),
    run: () => api.get('/body/coordination/run/'),
    log: (limit = 20) => api.get(`/body/coordination/log/?limit=${limit}`),
  },
  throttle: () => api.get('/body/throttle/'),
}

export const intelligenceApi = {
  status: () => api.get('/v1/intelligence/skynet/status/'),
  opportunities: () => api.get('/v1/intelligence/opportunities/'),
  predictions: () => api.get('/v1/intelligence/predictions/'),
}

// Session 734: Income Builder API - Revenue generation and action plans
export const incomeBuilderApi = {
  // Analysis and opportunities
  analyze: () => api.get('/v1/intelligence/income-builder/'),
  realOpportunities: () => api.get('/v1/intelligence/real-income-builder/'),
  analyzeOpportunities: () => api.get('/v1/intelligence/real-income-builder/analyze/'),

  // Action plans
  getActionPlan: () => api.get('/v1/intelligence/income-builder/action-plan/'),
  createActionPlan: (data: { opportunity_id?: string; focus_area?: string }) =>
    api.post('/v1/intelligence/income-builder/action-plan/', data),
  listPlans: () => api.get('/v1/intelligence/income-builder/plans/'),
  executePlan: (planId: string) =>
    api.post('/v1/intelligence/income-builder/execute/', { plan_id: planId }),

  // Generated files
  viewFile: (filename: string) => api.get(`/v1/intelligence/income-builder/file/${filename}/`),

  // Automation
  analyzePlanForAutomation: (planId: string) =>
    api.post('/v1/intelligence/income-builder/analyze-plan/', { plan_id: planId }),
  executePlanAutomation: (planId: string) =>
    api.post('/v1/intelligence/income-builder/process-plan/', { plan_id: planId }),
}

// Session 688: Opportunity detail and actions
export const opportunitiesApi = {
  list: (params?: { status?: string; category?: string; min_score?: number }) =>
    api.get('/opportunities/', { params }),
  detail: (id: string) => api.get(`/opportunities/${id}/`),
  act: (id: string, data?: { workflow?: string; content_types?: string[]; notes?: string }) =>
    api.post(`/opportunities/${id}/act/`, data || {}),
  dismiss: (id: string, reason?: string) =>
    api.post(`/opportunities/${id}/dismiss/`, { reason }),
  top: (limit = 10) => api.get(`/opportunities/top/?limit=${limit}`),
}

export const ecosystemApi = {
  stats: () => api.get('/ecosystem/stats/'),
  liveFeed: () => api.get('/ecosystem/live-feed/'),
}

export const dashboardApi = {
  stats: () => api.get('/dashboard/stats/'),
  health: () => api.get('/v1/health/'),
  runAgentCycle: () => api.post('/v1/agents/force-cycle/'),
  // Session 774: Connect unused rich endpoints
  summary: () => api.get('/dashboard/summary/'),  // Personalized greeting + "While You Were Away"
  liveAgentActivity: () => api.get('/dashboard/agents/'),  // Real-time agent status
  advisorInsights: () => api.get('/dashboard/advisors/'),  // Advisor recommendations
}

export const spidersApi = {
  status: () => api.get('/v1/intelligence/spider-status/'),
  report: () => api.get('/spider-intelligence/report/'),
}

// Session 718: Spider Integration API - Comprehensive spider network management
export const spiderIntegrationApi = {
  // Dashboard & Overview
  network: () => api.get('/spider-dashboard/network/'),
  dashboardStats: () => api.get('/spider-intelligence/dashboard-stats/'),
  registry: () => api.get('/spider-intelligence/registry/'),

  // Health Monitoring
  healthSummary: () => api.get('/spider-health/summary/'),
  executionLogs: (params?: { hours?: number; spider_name?: string; status?: string; limit?: number }) =>
    api.get('/spider-health/executions/', { params }),
  embeddingCoverage: () => api.get('/spider-health/embedding-coverage/'),

  // Data Feed
  dataFeed: (params?: { category?: string; source?: string; limit?: number; offset?: number; sort?: string }) =>
    api.get('/spider-intelligence/feed/', { params }),
  timeline: (range?: '24h' | '7d' | '30d') =>
    api.get('/spider-intelligence/timeline/', { params: { range } }),
  knowledge: (params?: { type?: string; limit?: number }) =>
    api.get('/spider-intelligence/knowledge/', { params }),

  // Spider Details
  detail: (spiderName: string, params?: { hours?: number; limit?: number }) =>
    api.get(`/spider-intelligence/detail/${spiderName}/`, { params }),

  // Actions
  runSpider: (spiderName: string) => api.post(`/spider-health/run/${spiderName}/`),
  runAllSpiders: () => api.post('/spider-intelligence/run-all/'),

  // Activity
  activityFeed: () => api.get('/spider-dashboard/activity/'),

  // Intelligence Endpoints
  trends: (params?: { category?: string; hours?: number; limit?: number }) =>
    api.get('/spider-intelligence/trends/', { params }),
  marketInsights: () => api.get('/spider-intelligence/market/'),
  techTrends: (params?: { hours?: number; limit?: number }) =>
    api.get('/spider-intelligence/tech/', { params }),
  jobs: (params?: { hours?: number; limit?: number }) =>
    api.get('/spider-intelligence/jobs/', { params }),

  // Search
  search: (params: { q: string; category?: string; hours?: number; limit?: number }) =>
    api.get('/spider-intelligence/search/', { params }),
}

// Session 783: Spider News Feed API - Human-facing feed with agent annotations
export const spiderFeedApi = {
  // Main feed with filters & pagination
  list: (params?: {
    page?: number
    per_page?: number
    source?: string
    category?: string
    annotation_type?: string
    search?: string
    sort?: 'newest' | 'popular' | 'trending'
    hours?: number
  }) => api.get('/spider-feed/', { params }),

  // Trending items (most annotated in last 24h)
  trending: (params?: { hours?: number; limit?: number }) =>
    api.get('/spider-feed/trending/', { params }),

  // Single item detail
  detail: (itemId: string) => api.get(`/spider-feed/item/${itemId}/`),

  // Vote on an annotation
  vote: (itemId: string, annotationId: string, direction: 'up' | 'down') =>
    api.post(`/spider-feed/${itemId}/vote/`, { annotation_id: annotationId, direction }),

  // Feed statistics
  stats: () => api.get('/spider-feed/stats/'),
}

export const pilotsApi = {
  dashboard: () => api.get('/pilots/dashboard/'),
  gates: () => api.get('/pilot-gates/'),  // List of gates, not dashboard
  // Session 696: Pilot gates list with limit for Pilot Activity Modal
  list: (limit = 50) => api.get(`/pilot-gates/?limit=${limit}`),
  progress: () => api.get('/pilots/progress/'),
  gateDetail: (gateId: string) => api.get(`/pilot-gates/${gateId}/`),
  updateGateStatus: (gateId: string, action: string, notes?: string) =>
    api.post(`/pilot-gates/${gateId}/status/`, { action, notes, approved_by: 'UI User' }),
  approveAllItems: (gateId: string) =>
    api.post(`/pilot-gates/${gateId}/approve-all/`),
  startPilot: (gateId: string) =>
    api.post(`/pilot-gates/${gateId}/pilot/`),
  // Session 691: Implementation review
  implementationDetail: (pilotId: string) =>
    api.get(`/pilots/${pilotId}/implementation/`),
}

export const experimentsApi = {
  // Session 692: Use /pilot-experiments/ to get pilot experiments (not A/B experiments)
  list: () => api.get('/pilot-experiments/'),
  portfolio: () => api.get('/experiments/portfolio/'),
  updateKpi: (experimentId: string, kpiValue: number) =>
    api.post(`/experiments/${experimentId}/update-kpi/`, { kpi_value: kpiValue }),
  complete: (experimentId: string, outcome: string) =>
    api.post(`/experiments/${experimentId}/complete/`, { outcome }),
  halt: (experimentId: string, reason: string) =>
    api.post(`/experiments/${experimentId}/halt/`, { reason }),
  learnings: () => api.get('/experiments/learnings/'),
  patterns: () => api.get('/experiments/patterns/'),
  triggerKpiUpdate: () => api.post('/experiments/kpis/update/'),
}

export const learningApi = {
  dashboard: () => api.get('/learning/dashboard/'),
  feed: () => api.get('/learning/feed/'),
  activity: () => api.get('/agent-learning/activity/'),
  stats: () => api.get('/learning/stats/'),
  velocity: () => api.get('/learning/velocity/'),
  // Session 860: Added patterns and insights endpoints
  patterns: (limit = 50) => api.get('/learning/patterns/', { params: { limit } }),
  insights: (limit = 20) => api.get('/learning/insights/', { params: { limit } }),
  // Session 972: Learning loop effectiveness stats
  loopStats: () => api.get('/learning/loop/stats/'),
}

// Session 935: User Learning System API (Session 930 backend)
export interface FeedbackRequest {
  agent_id?: string      // Either agent_id or agent_name required
  agent_name?: string    // Alternative to agent_id (looked up server-side)
  rating: 1 | 0 | -1     // 1=helpful, 0=neutral, -1=not helpful
  execution_id?: string
  deliverable_id?: string
  feedback_text?: string
  task_description?: string
  context_snapshot?: Record<string, unknown>
}

export interface GoalProgressRequest {
  progress_delta: number
  milestone?: string
  notes?: string
}

export interface SkillDemonstrationRequest {
  skill_name: string
  category?: 'technical' | 'creative' | 'analytical' | 'communication' | 'leadership' | 'domain'
  quality_score?: number
  context?: string
  deliverable_id?: string
}

export const userLearningApi = {
  // Feedback
  recordFeedback: (data: FeedbackRequest) =>
    api.post('/user-learning/feedback/', data),
  getAgentEffectiveness: (agentId: string) =>
    api.get(`/user-learning/effectiveness/${agentId}/`),
  getAgentSummary: () =>
    api.get('/user-learning/agent-summary/'),

  // Profile
  getProfileCompleteness: () =>
    api.get('/user-learning/profile-completeness/'),
  getNextProfileQuestion: (context?: string) =>
    api.get('/user-learning/profile-next-question/', { params: context ? { context } : {} }),
  recordProfileResponse: (fieldName: string, value: string, completed = true) =>
    api.post('/user-learning/profile-response/', { field_name: fieldName, value, completed }),

  // Goals
  getGoalsDashboard: () =>
    api.get('/user-learning/goals/'),
  getGoalDetail: (goalId: string) =>
    api.get(`/user-learning/goals/${goalId}/`),
  recordGoalProgress: (goalId: string, data: GoalProgressRequest) =>
    api.post(`/user-learning/goals/${goalId}/progress/`, data),

  // Skills
  getSkillsSummary: () =>
    api.get('/user-learning/skills/'),
  getSkillGrowthChart: (months = 6) =>
    api.get('/user-learning/skills/growth/', { params: { months } }),
  recordSkillDemonstration: (data: SkillDemonstrationRequest) =>
    api.post('/user-learning/skills/demonstrate/', data),
  getSkillRecommendations: () =>
    api.get('/user-learning/skills/recommendations/'),

  // Combined summary
  getSummary: () =>
    api.get('/user-learning/summary/'),

  // Session 1000C: Learning velocity + preferences (used by Command Center learning tab)
  getVelocity: () =>
    api.get('/learning/velocity/'),
  getAllPreferences: () =>
    api.get('/preferences/'),
}

// Session 745: Research API for network graph
export const researchApi = {
  networkGraph: () => api.get('/v1/research/network-graph/'),
  liveFeed: () => api.get('/v1/research/live-feed/'),
  systemInsights: () => api.get('/v1/research/system-insights/'),
}

// Session 745: Distribution API for monetization
export const distributionApi = {
  // Platforms
  platforms: () => api.get('/distribution/platforms/'),
  platformDetail: (id: string) => api.get(`/distribution/platforms/${id}/`),
  createPlatform: (data: Record<string, unknown>) => api.post('/distribution/platforms/create/', data),

  // User Accounts (OAuth connections)
  accounts: () => api.get('/distribution/accounts/'),
  connectPlatform: (platform: string, data: Record<string, unknown>) => api.post('/distribution/accounts/connect/', { platform, ...data }),
  disconnectPlatform: (platform: string) => api.post(`/distribution/oauth/${platform}/disconnect/`),

  // Content Distribution
  content: () => api.get('/distribution/content/'),
  createDistribution: (data: Record<string, unknown>) => api.post('/distribution/content/create/', data),
  submitDistribution: (id: string) => api.post(`/distribution/content/${id}/submit/`),
  publishDistribution: (id: string) => api.post(`/distribution/content/${id}/publish/`),
  recordSale: (id: string, data: Record<string, unknown>) => api.post(`/distribution/content/${id}/sale/`, data),

  // Analytics & Stats
  stats: () => api.get('/distribution/stats/'),
  recommendations: () => api.get('/distribution/recommendations/'),
  platformAnalytics: (id: string) => api.get(`/distribution/analytics/${id}/`),
  integrations: () => api.get('/distribution/integrations/'),

  // Revenue
  revenueDashboard: () => api.get('/distribution/revenue/dashboard/'),
  platformRevenue: (platform: string) => api.get(`/distribution/revenue/platform/${platform}/`),
  comparePlatforms: () => api.get('/distribution/revenue/compare/'),
  calculateRoi: () => api.get('/distribution/revenue/roi/'),

  // Scheduling & Batch
  scheduled: () => api.get('/distribution/scheduled/'),
  batchDistribute: (data: Record<string, unknown>) => api.post('/distribution/batch/', data),
  reschedule: (id: string, data: Record<string, unknown>) => api.post(`/distribution/${id}/reschedule/`, data),
  cancelScheduled: (id: string) => api.post(`/distribution/${id}/cancel/`),

  // Templates
  templates: () => api.get('/distribution/templates/'),
  applyTemplate: (data: Record<string, unknown>) => api.post('/distribution/templates/apply/', data),

  // Auto Distribution
  autoSettings: () => api.get('/distribution/auto/settings/'),
  createAutoDistribution: (data: Record<string, unknown>) => api.post('/distribution/auto/create/', data),

  // Platform-specific
  syncRevenue: (platform: string) => api.post(`/distribution/${platform}/sync-revenue/`),
}

export const contentApi = {
  // Gallery
  gallery: () => api.get('/v1/gallery/list/'),
  unifiedGallery: () => api.get('/v1/gallery/all/'),
  videoGallery: () => api.get('/v1/gallery/videos/'),
  toggleFavorite: (itemId: string) => api.post('/v1/gallery/toggle-favorite/', { item_id: itemId }),

  // Image History & Editing
  imageHistory: (params?: Record<string, unknown>) =>
    api.get('/images/history/', { params }),
  upscaleImage: (imageId: string) =>
    api.post('/stability/upscale/', { image_id: imageId }),
  removeBackground: (imageId: string) =>
    api.post('/stability/remove-background/', { image_id: imageId }),
  createVariations: (imageId: string, count = 3) =>
    api.post('/stability/create-variations/', { image_id: imageId, count }),
  deleteImage: (imageId: string) =>
    api.delete(`/images/${imageId}/delete/`),

  // Image Generation
  generateImage: (prompt: string, options?: Record<string, unknown>) =>
    api.post('/v1/gallery/generate/', { prompt, ...options }),
  optimizePrompt: (prompt: string) =>
    api.post('/v1/gallery/optimize-prompt/', { prompt }),

  // Video Generation
  textToVideo: (prompt: string, options?: Record<string, unknown>) =>
    api.post('/v1/video/text-to-video/', { prompt, ...options }),
  imageToVideo: (imageUrl: string, options?: Record<string, unknown>) =>
    api.post('/v1/video/image-to-video/', { image_url: imageUrl, ...options }),

  // Video Upload
  uploadVideo: (file: File, title?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    return api.post('/upload/video/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Video Status & History
  videoStatus: (taskId: string) =>
    api.get(`/v1/video/status/${taskId}/`),
  videoHistory: (params?: Record<string, unknown>) =>
    api.get('/v1/video/history/', { params }),

  // Video Management
  toggleVideoFavorite: (videoId: string) =>
    api.post(`/v1/video/history/${videoId}/favorite/`),
  deleteVideo: (videoId: string) =>
    api.delete(`/v1/video/history/${videoId}/`),
  incrementVideoView: (videoId: string) =>
    api.post(`/v1/video/history/${videoId}/view/`),
  incrementVideoDownload: (videoId: string) =>
    api.post(`/v1/video/history/${videoId}/download/`),

  // Video Editing (async — returns task_id, poll via videoStatus)
  extendVideo: (videoUrl: string, options?: Record<string, unknown>) =>
    api.post('/v1/video/extend/', { video_url: videoUrl, ...options }),
  upscaleVideo: (videoUrl: string, prompt: string) =>
    api.post('/v1/video/upscale/', { video_url: videoUrl, prompt }),

  // Video Editing (DaVinci/ffmpeg)
  davinciStatus: () =>
    api.get('/v1/davinci/status/'),
  chainVideos: (videoClips: string[], options?: { add_transitions?: boolean }) => {
    const formData = new FormData()
    formData.append('video_clips', JSON.stringify(videoClips))
    if (options?.add_transitions !== undefined) formData.append('add_transitions', String(options.add_transitions))
    return api.post('/v1/davinci/chain-videos/', formData)
  },
  addTextOverlay: (videoId: string, text: string, options?: { position?: string; font_size?: number; start_second?: number; duration?: number }) => {
    const formData = new FormData()
    formData.append('video_id', videoId)
    formData.append('text', text)
    if (options?.position) formData.append('position', options.position)
    if (options?.font_size !== undefined) formData.append('font_size', String(options.font_size))
    if (options?.start_second !== undefined) formData.append('start_second', String(options.start_second))
    if (options?.duration !== undefined) formData.append('duration', String(options.duration))
    return api.post('/v1/davinci/add-text-overlay/', formData)
  },
  applyColorGrading: (videoId: string, style: string) => {
    const formData = new FormData()
    formData.append('video_id', videoId)
    formData.append('style', style)
    return api.post('/v1/davinci/apply-color-grading/', formData)
  },
  addAudioToVideo: (videoId: string, audioFile: File, volume?: number) => {
    const formData = new FormData()
    formData.append('video_id', videoId)
    formData.append('audio_file', audioFile)
    if (volume !== undefined) formData.append('audio_volume', String(volume))
    return api.post('/v1/davinci/add-audio-to-video/', formData)
  },

  // Voiceover & SFX (ElevenLabs)
  addVoiceoverToVideo: (videoId: string, text: string, voice: string, volume?: number) =>
    api.post('/tool/add-voiceover/', { video_id: videoId, text, voice, volume: volume ?? 0.8 }),
  addSfxToVideo: (videoId: string, description: string, duration?: number, volume?: number) =>
    api.post('/tool/add-sfx-to-video/', { video_id: videoId, description, duration, volume: volume ?? 0.5 }),

  // Video Agents — transcribe, content packs
  videoTranscribe: (videoId: string, language = 'en') =>
    api.post('/v1/video/transcribe/', { id: videoId, language }),
  videoTranscripts: (videoId: string) =>
    api.get('/v1/video/transcripts/', { params: { video_id: videoId } }),
  videoContentPack: (videoId: string, language = 'en') =>
    api.post('/v1/video/content-pack/', { id: videoId, language }),

  // Content Creation
  create: (data: { type: string; prompt: string; options?: Record<string, unknown> }) =>
    api.post('/v1/content/create/', data),
  list: () => api.get('/v1/content/list/'),
  generateBlog: (topic: string) => api.post('/v1/content/blog/generate/', { topic }),
  generateSocial: (topic: string, platform: string) =>
    api.post('/v1/content/social/generate/', { topic, platform }),
  generateVideoScript: (topic: string) => api.post('/v1/content/video/script/', { topic }),
  templates: () => api.get('/v1/content/templates/'),

  // Content Calendar
  calendar: () => api.get('/content-calendar/'),
  calendarUpcoming: () => api.get('/content-calendar/upcoming/'),

  // Session 741: Content Channels API
  channels: (limit?: number) => api.get('/content-channels/', { params: { limit } }),
  channelDetail: (channelId: string) => api.get(`/content-channels/${channelId}/`),
  episodeDetail: (episodeId: string) => api.get(`/content-channels/episode/${episodeId}/`),

  // Creative Projects
  projects: () => api.get('/creative-projects/'),
  createProject: (name: string, description: string) =>
    api.post('/creative-projects/create/', { name, description }),
}

export const settingsApi = {
  // Profile
  getProfile: () => api.get('/v1/profile/'),
  updateProfile: (data: { username?: string; email?: string; bio?: string; dark_mode?: boolean }) =>
    api.put('/v1/profile/update/', data),
  getProfileStats: () => api.get('/v1/profile/stats/'),
  uploadAvatar: (formData: FormData) =>
    api.post('/v1/profile/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  deleteAvatar: () => api.delete('/v1/profile/avatar/delete/'),
  generateAvatar: () => api.post('/v1/profile/avatar/generate/'),

  // Preferences
  getPreferences: () => api.get('/preferences/'),
  getPreferenceStats: () => api.get('/preferences/stats/'),
  clearPreferences: () => api.post('/preferences/clear/'),

  // Notifications
  getNotifications: () => api.get('/proactive/notifications/'),
  markNotificationRead: (notificationId: string) =>
    api.post(`/proactive/notifications/${notificationId}/read/`),
  markAllRead: () => api.post('/proactive/notifications/read-all/'),
  getNotificationPreferences: () => api.get('/proactive/notifications/preferences/'),
  updateNotificationPreferences: (prefs: Record<string, boolean>) =>
    api.put('/proactive/notifications/preferences/', prefs),

  // Security
  changePassword: (oldPassword: string, newPassword: string) =>
    api.post('/v1/auth/change-password/', { old_password: oldPassword, new_password: newPassword }),

  // Data Export
  exportData: (format: 'json' | 'csv') =>
    api.get(`/distribution/revenue/export/?format=${format}`),
}

// Session 934: Types for UnifiedPA response
export interface ToolRun {
  tool: string
  ok: boolean
  latency_ms: number
  error_code?: string
  error_message?: string
}

export interface UnifiedPAResponse {
  success: boolean
  content: string
  trace_id: string
  tool_runs: ToolRun[]
  audio_url: string | null
  intent: string | null
  routed_to: string | null
  profile_completeness: number
  latency_ms: number
  error?: string
  conversation_id?: string
}

// Session 974b: Async PA chat dispatch response
export interface PAChatAsyncResponse {
  success: boolean
  task_id: string
  status: 'processing'
}

// Session 974b: Async PA chat status polling response
export interface PAChatStatusResponse {
  success: boolean
  status: 'processing' | 'completed' | 'failed'
  content?: string
  trace_id?: string
  tool_runs?: ToolRun[]
  audio_url?: string | null
  intent?: string | null
  routed_to?: string | null
  profile_completeness?: number
  latency_ms?: number
  error?: string
  conversation_id?: string
}

// Session 974: Conversation history types
export interface ConversationSummary {
  conversation_id: string
  title: string
  message_count: number
  last_message_at: string | null
  preview: string
}

export interface ConversationMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  tools_used?: string[]
}

export const assistantApi = {
  // Chat - Session 798: Use /assistant/chat/ endpoint (EnhancedPersonalAIAssistant with workspace awareness)
  // instead of /v1/assistant/chat/ (old hardcoded prompt from views_image.py)
  chat: (message: string, options?: { use_personal_assistant?: boolean }) =>
    api.post('/assistant/chat/', { message, ...options }),

  // Session 934: UnifiedPA chat - dedicated endpoint with full tool_runs visibility
  // Session 974b: Returns task_id for async polling (Celery)
  paChat: (message: string, options?: { context?: Record<string, unknown>; generate_audio?: boolean; conversation_id?: string; source?: string; platform?: string }) =>
    api.post<PAChatAsyncResponse>('/pa/chat/', { message, ...options }),

  // Session 974b: Poll async PA chat task status
  paChatStatus: (taskId: string) =>
    api.get<PAChatStatusResponse>(`/pa/chat/status/${taskId}/`),

  // Session 934: Get PA context info (available tools, system state)
  getPAContext: () => api.get('/pa/context/'),

  // Session 974: Conversation history endpoints
  listConversations: () =>
    api.get<{ success: boolean; conversations: ConversationSummary[]; total: number }>('/pa/conversations/'),

  getConversation: (conversationId: string) =>
    api.get<{ success: boolean; conversation_id: string; title: string; messages: ConversationMessage[] }>(
      `/pa/conversations/${conversationId}/`
    ),

  createConversation: () =>
    api.post<{ success: boolean; conversation_id: string }>('/pa/conversations/new/'),

  // Voice Input (Speech-to-Text via Whisper)
  transcribe: (audioBlob: Blob) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    return api.post('/assistant/transcribe/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  voiceChat: (audioBlob: Blob) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    return api.post('/assistant/voice/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Session 894: Voice Output (Text-to-Speech via ElevenLabs)
  speak: (text: string, options?: { voice_id?: string; skip_summarize?: boolean }) =>
    api.post('/tts/speak/', { text, ...options }),

  // Context & Learning
  getContext: () => api.get('/assistant/context/'),
  getLearning: () => api.get('/assistant/learning/'),
  getPreferences: () => api.get('/assistant/preferences/'),
  getAttentionItems: () => api.get('/assistant/attention-items/'),
  getTaskProgress: () => api.get('/assistant/task-progress/'),

  // Session 933: Unified Attention Aggregator - combines system health + user notifications
  getUnifiedAttention: (params?: {
    include_system?: boolean
    include_human?: boolean
    urgency?: string[]
    limit?: number
  }) => {
    const searchParams = new URLSearchParams()
    if (params?.include_system !== undefined) searchParams.set('include_system', String(params.include_system))
    if (params?.include_human !== undefined) searchParams.set('include_human', String(params.include_human))
    if (params?.urgency) params.urgency.forEach(u => searchParams.append('urgency', u))
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    return api.get(`/assistant/attention/unified/?${searchParams.toString()}`)
  },
  getAttentionStats: () => api.get('/assistant/attention/stats/'),

  // Feedback & Reset
  feedback: (messageId: string, rating: 'positive' | 'negative', comment?: string) =>
    api.post('/assistant/feedback/', { message_id: messageId, rating, comment }),
  reset: () => api.post('/assistant/reset/'),
}

export const bettingApi = {
  // Overview & Stats
  stats: () => api.get('/v1/betting/stats/'),
  recent: (limit = 20) => api.get(`/v1/betting/recent/?limit=${limit}`),
  wagers: () => api.get('/v1/betting/wagers/'),

  // Live Odds
  liveOdds: () => api.get('/v1/sports/live-odds/'),
  liveOddsWithScores: () => api.get('/v1/sports/live-odds-scores/'),
  liveOpportunities: () => api.get('/v1/sports/live-opportunities/'),

  // Arbitrage
  arbitrageScan: () => api.get('/v1/betting/arbitrage/scan/'),
  detectArbitrage: (data: { odds: number[] }) => api.post('/v1/odds/arbitrage/', data),

  // Markets
  markets: () => api.get('/v1/odds/markets/'),
  futures: () => api.get('/v1/betting/futures/'),

  // Bankroll
  bankroll: () => api.get('/v1/odds/bankroll/'),
  bankrollStats: () => api.get('/v1/odds/bankroll/stats/'),

  // Line Movement
  lineMovement: (gameId?: string) => api.get(gameId ? `/v1/betting/line-movement/${gameId}/` : '/v1/betting/line-movement/'),
  movers: () => api.get('/v1/betting/movers/'),

  // Intelligence
  intelligence: () => api.get('/v1/sports/betting-intelligence/'),
  todaysGames: (sport?: string) => api.get(sport ? `/v1/betting/todays-games/?sport=${sport}` : '/v1/betting/todays-games/'),
  bettingBrief: (sport?: string) => api.get(sport ? `/v1/betting/brief/?sport=${sport}` : '/v1/betting/brief/'),
  sharpAction: (sport?: string) => api.get(sport ? `/v1/betting/sharp-action/?sport=${sport}` : '/v1/betting/sharp-action/'),

  // Wager Management
  placeBet: (data: { game_id: string; bet_type: string; pick: string; odds: number; stake: number }) =>
    api.post('/v1/betting/place/', data),
  logWager: (data: Record<string, unknown>) => api.post('/v1/betting/wager/', data),
  settleWager: (wagerId: string, result: string) => api.post(`/v1/betting/wagers/${wagerId}/settle/`, { result }),
  cancelWager: (wagerId: string) => api.post(`/v1/betting/wagers/${wagerId}/cancel/`),
  quickPick: (data: Record<string, unknown>) => api.post('/v1/betting/quick-pick/', data),

  // AI Track Record
  trackRecord: (params?: { sport?: string; days?: number }) =>
    api.get('/v1/betting/track-record/', { params }),
}

// Session 998B: Sports Betting Hub Feed
export const sportsHubApi = {
  getFeed: (category?: string, limit = 20) =>
    api.get('/sports-hub/feed/', { params: { category, limit } }).then(r => r.data),
}

// Stock Intelligence Dashboard
export interface StockDashboard {
  success: boolean
  latest_brief: {
    id: string
    brief_date: string
    executive_summary: string
    total_stocks_analyzed: number
    debate_zone_count: number
    situation_health: string
  } | null
  total_briefs: number
  total_alerts: number
  alert_counts_by_type: Record<string, number>
  prediction_accuracy_7d: number | null
  prediction_accuracy_30d: number | null
  total_predictions: number
  sec_filings_count: number
}

export interface MarketBrief {
  id: string
  brief_date: string
  brief_type: string
  executive_summary: string
  total_stocks_analyzed: number
  debate_zone_count: number
  situation_health: string
  confidence_distribution: Record<string, number>
  generated_at: string | null
}

export interface MarketBriefDetail {
  id: string
  brief_date: string
  brief_type: string
  executive_summary: string
  high_conviction_opportunities: unknown[]
  debate_zone: unknown[]
  bullish_opportunities: unknown[]
  bearish_warnings: unknown[]
  risk_alerts: unknown[]
  changes_from_yesterday: Record<string, unknown>
  is_first_brief: boolean
  total_stocks_analyzed: number
  confidence_distribution: Record<string, number>
  debate_zone_count: number
  situation_health: string
  gpt_success_rate: number
  generated_at: string | null
}

export interface StockAlert {
  id: string
  alert_type: string
  symbol: string
  company_name: string
  sector: string
  title: string
  summary: string
  bull_case: string
  bear_case: string
  disagreement_level: string
  confidence_score: number
  bull_score: number
  bear_score: number
  current_price: number | null
  price_change_24h: number | null
  recommended_action: string
  bookmarked: boolean
  detected_at: string | null
}

export interface PredictionOutcome {
  id: string
  ticker: string
  prediction_type: string
  conviction_level: string
  predicted_move: number
  price_at_prediction: number
  prediction_date: string
  price_after_7_days: number | null
  price_after_30_days: number | null
  actual_move_7_days: number | null
  actual_move_30_days: number | null
  was_correct_7_days: boolean | null
  was_correct_30_days: boolean | null
  accuracy_score_7_days: number | null
  accuracy_score_30_days: number | null
  was_in_debate_zone: boolean
  outcome_calculated: boolean
}

export interface TickerLookupResult {
  success: boolean
  symbol: string
  live_quote: Record<string, unknown> | null
  alerts: { results: StockAlert[]; total: number }
  predictions: { results: PredictionOutcome[]; total: number }
  brief_mentions: Array<{
    brief_id: string
    brief_date: string
    mentions: Array<{
      section: string
      ticker: string
      recommendation: string | null
      confidence: string | null
      reasoning: string | null
    }>
  }>
  sec_filings: { results: Array<{ id: string; spider_name: string; source_url: string; data_type: string; raw_data: Record<string, unknown>; relevance_score: number; created_at: string | null }>; total: number }
  spider_data: { results: Array<{ id: string; spider_name: string; source_url: string; data_type: string; summary: string; relevance_score: number; created_at: string | null }>; total: number }
}

// Session 1015: Government & Legislation Hub
export interface GovernmentBill {
  id: string
  bill_number: string
  title: string
  description: string
  plain_summary: string
  status: string
  state: string
  last_action: string
  last_action_date: string
  sponsors: Array<{ name: string; party: string }>
  sponsor_count: number
  committee: string
  topics: string[]
  url: string
  congress_gov_url: string
  created_at: string | null
}

export interface GovernmentHubData {
  success: boolean
  stats: {
    total_bills: number
    house_count: number
    senate_count: number
    status_breakdown: Record<string, number>
  }
  top_topics: Array<{ topic: string; count: number }>
  bills: GovernmentBill[]
}

export const governmentApi = {
  hub: () => api.get<GovernmentHubData>('/government/hub/'),
}

export const stockApi = {
  hub: () => api.get('/stocks/hub/'),
  dashboard: () => api.get('/stocks/dashboard/'),
  briefs: (params?: { limit?: number; offset?: number }) =>
    api.get('/stocks/briefs/', { params }),
  briefDetail: (id: string) => api.get(`/stocks/briefs/${id}/`),
  alerts: (params?: { limit?: number; offset?: number; type?: string; symbol?: string; bookmarked?: boolean }) =>
    api.get('/stocks/alerts/', { params }),
  predictions: (params?: { limit?: number; offset?: number; ticker?: string }) =>
    api.get('/stocks/predictions/', { params }),
  secFilings: (params?: { limit?: number; offset?: number }) =>
    api.get('/stocks/sec-filings/', { params }),
  tickerLookup: (symbol: string) =>
    api.get<TickerLookupResult>(`/stocks/ticker/${symbol.toUpperCase()}/`),
  marketNews: (params?: { limit?: number; offset?: number; source?: string }) =>
    api.get('/stocks/market-news/', { params }),
}

// Legacy learning API (older endpoints - kept for backwards compatibility)
export const legacyLearningApi = {
  // Dashboard & Profile
  dashboard: () => api.get('/learning/dashboard/'),
  profile: () => api.get('/learning/profile/'),
  updateProfile: (data: Record<string, unknown>) => api.post('/learning/profile/update/', data),

  // Preferences
  getAllPreferences: () => api.get('/preferences/'),
  getPreferenceStats: () => api.get('/preferences/stats/'),
  getImplicitPreferences: () => api.get('/preferences/implicit/'),
  getStyleRecommendations: () => api.get('/preferences/recommendations/'),
  getStyleEvolution: () => api.get('/preferences/evolution/'),
  trackBehavior: (behavior: { action: string; context: Record<string, unknown> }) =>
    api.post('/preferences/track/', behavior),

  // Learning Velocity
  getVelocity: () => api.get('/learning/velocity/'),

  // Insights
  getInsights: () => api.get('/learning/insights/'),
  generateInsights: () => api.post('/learning/insights/generate/'),
}

export const legalApi = {
  // Documents (case files)
  documents: () => api.get('/legal/case-files/'),
  documentDetail: (docId: string) => api.get(`/legal/case-files/${docId}/`),
  uploadDocument: (formData: FormData) =>
    api.post('/legal/case-files/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  analyzeDocument: (docId: string) => api.post(`/legal/case-files/${docId}/analyze/`),
  deleteDocument: (docId: string) => api.delete(`/legal/case-files/${docId}/delete/`),

  // Cases
  cases: () => api.get('/legal/cases/'),
  caseDetail: (caseId: string) => api.get(`/legal/cases/${caseId}/`),
  caseContext: (caseId: string) => api.get(`/legal/cases/${caseId}/context/`),
  activeCase: () => api.get('/legal/active-case/'),

  // Litigation
  litigationDocuments: (caseId: string) => api.get(`/legal/litigation/${caseId}/documents/`),
  uploadLitigationDoc: (caseId: string, formData: FormData) =>
    api.post(`/legal/litigation/${caseId}/documents/upload/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  knowledgeGraph: (caseId: string) => api.get(`/legal/litigation/${caseId}/knowledge-graph/`),
  generateResponse: (docId: string) => api.post(`/legal/litigation/${docId}/generate-response/`),
  listResponses: (caseId: string) => api.get(`/legal/litigation/${caseId}/responses/`),

  // Export
  exportSection: (data: { section: string; format: string }) => api.post('/legal/export-section/', data),
}

export const podcastApi = {
  // Episodes list
  list: () => api.get('/podcasts/list/'),
  create: (data: { topic: string; format_type?: string; generate_audio?: boolean }) =>
    api.post('/podcasts/create/', data),

  // Episode details
  status: (episodeId: string) => api.get(`/podcasts/${episodeId}/status/`),
  script: (episodeId: string) => api.get(`/podcasts/${episodeId}/script/`),
  delete: (episodeId: string) => api.delete(`/podcasts/${episodeId}/`),

  // Session 865: Generate TTS audio for an existing episode
  // Accepts optional voiceProfileId to use a custom voice
  generateAudio: (episodeId: string, voiceProfileId?: string) =>
    api.post(`/podcasts/${episodeId}/generate-audio/`, voiceProfileId ? { voice_profile_id: voiceProfileId } : {}),

  // Generation
  generateScript: (topic: string, style?: string) =>
    api.post('/v1/content/podcast/generate/', { topic, style }),

  // Stats
  stats: () => api.get('/podcasts/stats/'),

  // V1 podcasts list
  v1List: () => api.get('/v1/podcasts/'),
}

export const portfolioApi = {
  // Platforms
  platforms: () => api.get('/distribution/platforms/'),
  platformDetail: (platformId: string) => api.get(`/distribution/platforms/${platformId}/`),
  createPlatform: (data: Record<string, unknown>) => api.post('/distribution/platforms/create/', data),

  // Accounts
  accounts: () => api.get('/distribution/accounts/'),
  connectPlatform: (data: Record<string, unknown>) => api.post('/distribution/accounts/connect/', data),

  // Content
  content: () => api.get('/distribution/content/'),
  createContent: (data: Record<string, unknown>) => api.post('/distribution/content/create/', data),
  submitContent: (distId: string) => api.post(`/distribution/content/${distId}/submit/`),
  publishContent: (distId: string) => api.post(`/distribution/content/${distId}/publish/`),

  // Stats & Analytics
  stats: () => api.get('/distribution/stats/'),
  platformAnalytics: (platformId: string) => api.get(`/distribution/analytics/${platformId}/`),
  recommendations: () => api.get('/distribution/recommendations/'),

  // Revenue
  revenueDashboard: () => api.get('/distribution/revenue/dashboard/'),
  platformRevenue: (platformName: string) => api.get(`/distribution/revenue/platform/${platformName}/`),
  comparePlatforms: () => api.get('/distribution/revenue/compare/'),

  // Integrations
  integrations: () => api.get('/distribution/integrations/'),
}

// Human Interface Layer (Session 686)
// Note: Paths don't include /api/ prefix since baseURL is already '/api'
export const humanApi = {
  // Attention Stream
  attention: (params?: { limit?: number; urgency?: string[]; status?: string[] }) => {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    if (params?.urgency) params.urgency.forEach(u => searchParams.append('urgency', u))
    if (params?.status) params.status.forEach(s => searchParams.append('status', s))
    return api.get(`/human/attention/?${searchParams.toString()}`)
  },
  // Session 796: Alias for consistency with frontend usage
  attentionStream: (params?: { limit?: number; urgency?: string[]; status?: string[] }) => {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    if (params?.urgency) params.urgency.forEach(u => searchParams.append('urgency', u))
    if (params?.status) params.status.forEach(s => searchParams.append('status', s))
    return api.get(`/human/attention/?${searchParams.toString()}`)
  },
  attentionStats: () => api.get('/human/attention/stats/'),
  // Session 843: Get single attention item detail for inline modal viewing
  detail: (itemId: string) => api.get(`/human/attention/${itemId}/`),
  decide: (itemId: string, decision: string, feedback?: string, confidence?: number) =>
    api.post(`/human/attention/${itemId}/decide/`, { decision, feedback, confidence }),
  // Session 796: Batch decision support
  batchDecide: (decision: string, filters?: { urgency?: string; item_type?: string }, feedback?: string) =>
    api.post('/human/attention/batch-decide/', { decision, ...filters, feedback }),
  // Session 942: Bulk decide by specific IDs
  bulkDecide: (decision: string, itemIds: string[]) =>
    api.post('/human/attention/bulk-decide/', { decision, item_ids: itemIds }),
  // Session 796: Get consultations awaiting response
  pendingConsultations: () =>
    api.get('/human/attention/?source_type=assistant&status=pending'),
  defer: (itemId: string, remindAt: string) =>
    api.post(`/human/attention/${itemId}/defer/`, { remind_at: remindAt }),
  verify: (itemId: string, outcome: string, profit?: number, notes?: string) =>
    api.post(`/human/attention/${itemId}/verify/`, { outcome, profit, notes }),
  // Session 763: Mission Control execute action
  executeAction: (itemId: string, action: string, feedback?: string, extraData?: Record<string, unknown>) =>
    api.post(`/human/attention/${itemId}/execute/`, { action, feedback, extra_data: extraData }),
  // Session 988: Record boardroom visit for "NEW" badge tracking
  markBoardroomVisited: () => api.post('/human/attention/', {}),

  // Control Panel
  control: () => api.get('/human/control/'),
  pauseAgent: (agentName: string, reason?: string) =>
    api.post('/human/control/pause/', { agent: agentName, reason }),
  resumeAgent: (agentName: string, reason?: string) =>
    api.post('/human/control/resume/', { agent: agentName, reason }),
  setQuietMode: (enabled: boolean, durationMinutes?: number) =>
    api.post('/human/control/quiet/', { enabled, duration_minutes: durationMinutes }),
  setReviewMode: (enabled: boolean) =>
    api.post('/human/control/review/', { enabled }),
  adjustThreshold: (threshold: number) =>
    api.post('/human/control/threshold/', { threshold }),

  // Preferences
  preferences: () => api.get('/human/preferences/'),
  updatePreferences: (data: Record<string, unknown>) =>
    api.put('/human/preferences/', data),
}

export const adminApi = {
  // System Health
  health: () => api.get('/v1/health/'),
  systemHealth: () => api.get('/system-health/'),
  iccHealth: () => api.get('/icc/health/'),
  dashboardHealth: () => api.get('/dashboard/health/'),

  // Celery
  celeryStatus: () => api.get('/celery/status/'),
  celeryStats: () => api.get('/celery/stats/'),

  // Monitoring
  monitoringHealth: () => api.get('/monitoring/health/'),
  monitoringSchedules: () => api.get('/monitoring/schedules/'),

  // Spider Health
  spiderHealth: () => api.get('/spider-health/summary/'),
  spiderExecutions: () => api.get('/spider-health/executions/'),
  runSpider: (spiderName: string) => api.post(`/spider-health/run/${spiderName}/`),

  // Agent Health
  agentHealth: () => api.get('/v1/agents/health/'),

  // Agent Stats (detailed - includes categories, executions, activity)
  agentStats: () => api.get('/agents/stats/'),
}

// Session 696: SKIN Layer - Workspace Management API
export const workspaceApi = {
  // Workspace CRUD
  list: () => api.get('/workspaces/'),
  create: (data: { path: string; name?: string; description?: string }) =>
    api.post('/workspaces/', data),
  detail: (id: string) => api.get(`/workspaces/${id}/`),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/workspaces/${id}/`, data),
  delete: (id: string) => api.delete(`/workspaces/${id}/`),

  // Workspace Actions
  activate: (id: string) => api.post(`/workspaces/${id}/activate/`),
  scan: (id: string) => api.post(`/workspaces/${id}/scan/`),
  getActive: () => api.get('/workspaces/active/'),
  dashboard: () => api.get('/workspaces/dashboard/'),

  // File Operations
  files: (id: string, pattern?: string) =>
    api.get(`/workspaces/${id}/files/`, { params: { pattern } }),
  readFile: (id: string, path: string) =>
    api.get(`/workspaces/${id}/file/`, { params: { path } }),
  writeFile: (id: string, data: { path: string; content: string; agent?: string; description?: string }) =>
    api.post(`/workspaces/${id}/write/`, data),

  // Git Operations
  gitStatus: (id: string) => api.get(`/workspaces/${id}/git-status/`),
  gitCommit: (id: string, data: { message: string; files?: string[] }) =>
    api.post(`/workspaces/${id}/git-commit/`, data),
  gitBranch: (id: string, data: { branch_name: string; checkout?: boolean }) =>
    api.post(`/workspaces/${id}/git-branch/`, data),

  // Operations & Stats
  operations: (id: string, params?: { type?: string; agent?: string; success?: boolean }) =>
    api.get(`/workspaces/${id}/operations/`, { params }),
  stats: (id: string) => api.get(`/workspaces/${id}/stats/`),

  // Session 776: File History
  fileHistory: (id: string, path: string) =>
    api.get(`/workspaces/${id}/file-history/`, { params: { path } }),
}

// Session 696: Workspace Operations API (Audit Trail)
export const workspaceOperationsApi = {
  list: (params?: { type?: string; agent?: string; success?: boolean; pending_review?: boolean; file_path?: string }) =>
    api.get('/workspace-operations/', { params }),
  detail: (id: string) => api.get(`/workspace-operations/${id}/`),
  rollback: (id: string) => api.post(`/workspace-operations/${id}/rollback/`),
  review: (id: string, data: { approved: boolean; notes?: string }) =>
    api.post(`/workspace-operations/${id}/review/`, data),
  pendingReviews: () => api.get('/workspace-operations/pending-reviews/'),
}

// Session 861B: Workspace Triggers API (Autonomous Work Queue)
export const workspaceTriggersApi = {
  // Triggers CRUD
  list: (params?: {
    status?: string
    trigger_type?: string
    min_priority?: number
    category?: string
    workspace?: string
    show_expired?: boolean
  }) => api.get('/workspace-triggers/', { params }),
  detail: (id: string) => api.get(`/workspace-triggers/${id}/`),
  create: (data: {
    trigger_type: string
    title: string
    description?: string
    workspace?: string
    target_agent?: string
    target_category?: string
    context_data?: Record<string, unknown>
    priority?: number
    ttl_hours?: number
  }) => api.post('/workspace-triggers/', data),

  // Trigger Actions
  cancel: (id: string) => api.post(`/workspace-triggers/${id}/cancel/`),
  retry: (id: string) => api.post(`/workspace-triggers/${id}/retry/`),
  bumpPriority: (id: string) => api.post(`/workspace-triggers/${id}/bump_priority/`),

  // Stats & Meta
  stats: () => api.get('/workspace-triggers/stats/'),
  triggerTypes: () => api.get('/workspace-triggers/trigger_types/'),
  autopilotStatus: () => api.get('/workspace-triggers/autopilot-status/'),
}

// Session 861B: Workspace Trigger Configs API
export const workspaceTriggerConfigsApi = {
  list: (params?: { is_active?: boolean; trigger_type?: string }) =>
    api.get('/workspace-trigger-configs/', { params }),
  detail: (id: string) => api.get(`/workspace-trigger-configs/${id}/`),
  create: (data: {
    name: string
    description?: string
    target_spiders?: string[]
    match_field: string
    match_operator: string
    match_value: string
    trigger_type: string
    trigger_title_template?: string
    priority?: number
    ttl_hours?: number
    target_agent?: string
    target_category?: string
    cooldown_minutes?: number
  }) => api.post('/workspace-trigger-configs/', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/workspace-trigger-configs/${id}/`, data),
  delete: (id: string) => api.delete(`/workspace-trigger-configs/${id}/`),
  toggle: (id: string) => api.post(`/workspace-trigger-configs/${id}/toggle/`),
  test: (id: string, sampleData: Record<string, unknown>) =>
    api.post(`/workspace-trigger-configs/${id}/test/`, { sample_data: sampleData }),
}

// Session 697: Multi-LLM Provider API
export const llmApi = {
  // Provider Management
  providers: () => api.get('/v1/llm/providers/'),

  // Intelligent Model Selection
  selectModel: (data: {
    task_type?: string
    complexity?: 'low' | 'medium' | 'high'
    budget_priority?: 'cost' | 'performance' | 'balanced'
    content_length?: number
  }) => api.post('/v1/llm/intelligent-selection/', data),

  // Multi-Model Comparison
  compareModels: (data: {
    prompt: string
    models?: string[]
    parameters?: { temperature?: number; max_tokens?: number }
  }) => api.post('/v1/llm/multi-model-compare/', data),

  // Analytics
  analytics: (timeRange?: string) =>
    api.post('/v1/llm/analytics/', {}, { params: { time_range: timeRange } }),

  // User Preferences
  getPreferences: () => api.get('/v1/llm/preferences/'),
  setPreferences: (data: {
    default_model?: string
    fallback_model?: string
    budget_limit_daily?: number
    quality_threshold?: number
    speed_priority?: 'speed' | 'quality' | 'cost' | 'balanced'
    auto_optimize?: boolean
    preferred_providers?: string[]
    task_specific_models?: Record<string, string>
  }) => api.post('/v1/llm/preferences/', data),
}

// Session 701: HEART Service API - System Health Monitoring
export const heartApi = {
  // Run full health check on all components
  pulse: () => api.get('/heart/pulse/'),

  // Get cached vitals (fast)
  status: () => api.get('/heart/status/'),

  // Get heartbeat history
  history: (hours = 24, limit = 100) =>
    api.get('/heart/history/', { params: { hours, limit } }),

  // Get specific component status
  component: (name: 'brain' | 'nervous_system' | 'organs' | 'sensory' | 'skin' | 'memory') =>
    api.get(`/heart/component/${name}/`),

  // Quick alive check
  alive: () => api.get('/heart/alive/'),
}

// Session 703: LUNGS Service API - Resource & Capacity Management
export const lungsApi = {
  // Run full breathing check (budget analysis)
  breathe: () => api.get('/lungs/breathe/'),

  // Get cached respiratory status (fast)
  status: () => api.get('/lungs/status/'),

  // Get oxygen levels (budget usage percentages)
  oxygen: () => api.get('/lungs/oxygen/'),

  // List all budgets with their limits and usage
  budgets: () => api.get('/lungs/budgets/'),

  // Get spending forecast
  forecast: () => api.get('/lungs/forecast/'),

  // Check if an API call is allowed (budget not exceeded)
  canBreathe: (provider?: string, estimatedCost?: number) =>
    api.get('/lungs/can-breathe/', { params: { provider, estimated_cost: estimatedCost } }),

  // Quick alive check
  alive: () => api.get('/lungs/alive/'),
}

// Session 703: CIRCULATORY Service API - Data Flow Monitoring
export const circulatoryApi = {
  // Run full circulation check (monitor all data flows)
  circulate: () => api.get('/circulatory/circulate/'),

  // Get cached flow status (fast)
  status: () => api.get('/circulatory/status/'),

  // List all monitored flow routes
  routes: (params?: { type?: string; active?: boolean; critical?: boolean }) =>
    api.get('/circulatory/routes/', { params }),

  // Get specific route details
  routeDetail: (routeId: string) => api.get(`/circulatory/routes/${routeId}/`),

  // Get current bottlenecks in data flow
  bottlenecks: (severity?: 'critical' | 'warning' | 'info') =>
    api.get('/circulatory/bottlenecks/', { params: { severity } }),

  // Get flow velocity metrics
  velocity: (hours = 1) =>
    api.get('/circulatory/velocity/', { params: { hours } }),

  // Get circulation pulse history
  history: (hours = 24, limit = 100, status?: string) =>
    api.get('/circulatory/history/', { params: { hours, limit, status } }),

  // Quick alive check - is data flowing normally?
  isFlowing: () => api.get('/circulatory/is-flowing/'),
}

// Session 704: SPINE Service API - Central API Router
export const spineApi = {
  // Run full alignment check
  align: (force = false) => api.get('/spine/align/', { params: { force } }),

  // Get cached spine status (fast)
  status: () => api.get('/spine/status/'),

  // List all route patterns
  patterns: (category?: string, activeOnly = true) =>
    api.get('/spine/patterns/', { params: { category, active: activeOnly } }),

  // Get specific pattern details
  patternDetail: (patternId: string, hours = 24) =>
    api.get(`/spine/patterns/${patternId}/`, { params: { hours } }),

  // Get metrics for a specific route path
  metrics: (path: string, hours = 24) =>
    api.get('/spine/metrics/', { params: { path, hours } }),

  // Get alignment history
  history: (hours = 24, limit = 100) =>
    api.get('/spine/history/', { params: { hours, limit } }),

  // Check if a path can be routed
  canRoute: (path: string, method = 'GET') =>
    api.get('/spine/can-route/', { params: { path, method } }),

  // Quick health check
  isAligned: () => api.get('/spine/is-aligned/'),

  // Get category breakdown
  categories: () => api.get('/spine/categories/'),
}

// Session 700: LLM Routing API (from Backend Claude Session 699)
// Session 894: Fixed paths - backend uses /api/llm-routing/ not /api/v1/llm-routing/
export const llmRoutingApi = {
  // System status overview
  status: () => api.get('/llm-routing/status/'),

  // List all 6 LLM providers with health info
  providers: () => api.get('/llm-routing/providers/'),

  // List all 16 models with costs
  models: (params?: { provider?: string; capability?: string }) =>
    api.get('/llm-routing/models/', { params }),

  // Get agent-model mappings (75 configs)
  agentConfigs: (params?: { agent?: string; model?: string }) =>
    api.get('/llm-routing/agent-configs/', { params }),

  // Update agent config (requires auth)
  updateAgentConfig: (agentName: string, data: { model_id: string; reason?: string }) =>
    api.post(`/llm-routing/agent-configs/${agentName}/`, data),

  // Call logs with filtering
  logs: (params?: {
    hours?: number
    agent?: string
    provider?: string
    success?: boolean
    limit?: number
    offset?: number
  }) => api.get('/llm-routing/logs/', { params }),

  // Cost analytics dashboard
  costAnalytics: (hours?: number) =>
    api.get('/llm-routing/cost-analytics/', { params: { hours } }),
}

// Session 705: IMMUNE System API - Security & Threat Detection
export const immuneApi = {
  // Run full immune scan
  scan: (force = false) => api.get('/immune/scan/', { params: { force } }),

  // Get cached immune status (fast)
  status: () => api.get('/immune/status/'),

  // List threat patterns
  patterns: (params?: { category?: string; active?: boolean }) =>
    api.get('/immune/patterns/', { params }),

  // Get specific pattern details
  patternDetail: (patternId: string) => api.get(`/immune/patterns/${patternId}/`),

  // Get recent threat events
  threats: (params?: {
    hours?: number
    limit?: number
    severity?: string
    category?: string
  }) => api.get('/immune/threats/', { params }),

  // Get quarantine list
  quarantine: (params?: { entity_type?: string; active?: boolean }) =>
    api.get('/immune/quarantine/', { params }),

  // Add to quarantine
  addToQuarantine: (data: {
    entity_type: 'ip' | 'user' | 'user_agent'
    entity_value: string
    reason?: string
    duration_minutes?: number
    notes?: string
  }) => api.post('/immune/quarantine/', data),

  // Release from quarantine
  releaseFromQuarantine: (entityType: string, entityValue: string) =>
    api.delete(`/immune/quarantine/${entityType}/${entityValue}/`),

  // Quick health check
  isHealthy: () => api.get('/immune/is-healthy/'),

  // Check if request is allowed
  checkRequest: (data: {
    ip?: string
    user_id?: number
    user_agent?: string
    path?: string
  }) => api.post('/immune/check-request/', data),

  // Get threat categories breakdown
  categories: () => api.get('/immune/categories/'),
}

// Session 706: DIGESTIVE System API - Data Ingestion & Processing
export const digestiveApi = {
  // Run full digestion check
  digest: (force = false) => api.get('/digestive/digest/', { params: { force } }),

  // Get cached digestion status (fast)
  status: () => api.get('/digestive/status/'),

  // List all ingestion routes
  routes: (params?: { route_type?: string; stage?: string; active_only?: boolean }) =>
    api.get('/digestive/routes/', { params }),

  // Get specific route details
  routeDetail: (routeId: string) => api.get(`/digestive/routes/${routeId}/`),

  // Get current bottlenecks
  bottlenecks: (severity?: string) =>
    api.get('/digestive/bottlenecks/', { params: { severity } }),

  // Get metabolism metrics (throughput rates)
  metabolism: () => api.get('/digestive/metabolism/'),

  // Get digestion pulse history
  history: (hours = 24, limit = 100) =>
    api.get('/digestive/history/', { params: { hours, limit } }),

  // Quick alive check
  isDigesting: () => api.get('/digestive/is-digesting/'),
}

// Session 707: MUSCULAR System API - Agent Work Execution Monitoring
export const muscularApi = {
  // Run full muscle check (analyze agent execution health)
  flex: (force = false) => api.get('/muscular/flex/', { params: { force } }),

  // Get cached muscle status (fast)
  status: () => api.get('/muscular/status/'),

  // List all muscle groups (agent categories)
  groups: (params?: { category?: string; critical_only?: boolean }) =>
    api.get('/muscular/groups/', { params }),

  // Get specific muscle group details
  groupDetail: (groupId: string) => api.get(`/muscular/groups/${groupId}/`),

  // Get weak agents (low success rate)
  weak: (params?: { threshold?: number; limit?: number }) =>
    api.get('/muscular/weak/', { params }),

  // Get overworked agents (high execution count)
  overworked: (params?: { threshold?: number; limit?: number }) =>
    api.get('/muscular/overworked/', { params }),

  // Get muscular pulse history
  history: (hours = 24, limit = 100) =>
    api.get('/muscular/history/', { params: { hours, limit } }),

  // Quick health check - are agents executing successfully?
  isStrong: () => api.get('/muscular/is-strong/'),
}

// Session 722: BRAIN System API - Cognitive Processing Monitoring
export const brainApi = {
  // Run full cognitive check (analyze LLM calls, conversations, reasoning)
  think: (force = false) => api.get('/brain/think/', { params: { force } }),

  // Get cached brain status (fast)
  status: () => api.get('/brain/status/'),

  // Get current vitals (cognitive score, active conversations, etc.)
  vitals: () => api.get('/brain/vitals/'),

  // Get brain pulse history
  history: (hours = 24, limit = 100) =>
    api.get('/brain/history/', { params: { hours, limit } }),

  // Quick health check - is the brain actively thinking?
  isThinking: () => api.get('/brain/is-thinking/'),
}

// Session 723: SKIN System API - Workspace Output Monitoring
export const skinApi = {
  // Run full skin check (analyze workspace operations)
  feel: (force = false) => api.get('/skin/feel/', { params: { force } }),

  // Get cached skin status (fast)
  status: () => api.get('/skin/status/'),

  // Get current vitals (health score, operations count, etc.)
  vitals: () => api.get('/skin/vitals/'),

  // Get skin pulse history
  history: (hours = 24, limit = 100) =>
    api.get('/skin/history/', { params: { hours, limit } }),

  // Quick health check - is the skin healthy?
  isHealthy: () => api.get('/skin/is-healthy/'),

  // Get workspace summary
  workspaces: () => api.get('/skin/workspaces/'),
}

// Session 724: NERVOUS System API - WebSocket Communication Monitoring
export const nervousApi = {
  // Run full nervous check (analyze WebSocket communication)
  feel: (force = false) => api.get('/nervous/feel/', { params: { force } }),

  // Get cached nervous status (fast)
  status: () => api.get('/nervous/status/'),

  // Get current vitals (health score, connections, etc.)
  vitals: () => api.get('/nervous/vitals/'),

  // Get nervous pulse history
  history: (hours = 24, limit = 100) =>
    api.get('/nervous/history/', { params: { hours, limit } }),

  // Quick health check - is the nervous system responsive?
  isResponsive: () => api.get('/nervous/is-responsive/'),

  // Get WebSocket consumers summary
  consumers: () => api.get('/nervous/consumers/'),
}

// Session 716: Advisors API - Famous figure consultations
export const advisorsApi = {
  // List all active advisors
  list: () => api.get('/v1/advisors/list/'),

  // Get advisor details
  detail: (advisorId: string) => api.get(`/v1/advisors/${advisorId}/`),

  // Consult an advisor
  consult: (data: { advisor_id: string; question: string; context?: string }) =>
    api.post('/v1/advisors/consult/', data),

  // Get advisor network (ecosystem view)
  network: () => api.get('/v1/ecosystem/advisors/'),

  // Dashboard insights from advisors
  insights: () => api.get('/dashboard/advisors/'),
}

// Session 716: Agent Relationships API (Session 871: Alliance/Rivalry endpoints removed)
export const relationshipsApi = {
  // Overview of all relationships
  overview: () => api.get('/agent-relationships/'),

  // Get relationships for specific agent
  agentRelationships: (agentId: string) => api.get(`/agent-relationships/agent/${agentId}/`),

  // Create a new relationship
  create: (data: {
    agent1_id: string
    agent2_id: string
    relationship_type: string
    initial_strength?: number
  }) => api.post('/agent-relationships/create/', data),

  // Record interaction between agents
  recordInteraction: (relationshipId: string, data: {
    interaction_type: string
    outcome?: string
    strength_change?: number
  }) => api.post(`/agent-relationships/relationship/${relationshipId}/interact/`, data),

  // Get relationship events history
  events: (relationshipId: string) => api.get(`/agent-relationships/relationship/${relationshipId}/events/`),

  // Auto-generate relationships based on agent activity
  autoGenerate: () => api.post('/agent-relationships/auto-generate/'),
}

// Session 732: RAG/Document Embedding System API
export const ragApi = {
  // Document upload (raw content)
  uploadDocument: (file: File, options?: { collection_id?: string; embedding_model?: string }) => {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.collection_id) formData.append('collection_id', options.collection_id)
    if (options?.embedding_model) formData.append('embedding_model', options.embedding_model)
    return api.post('/v1/rag/upload-document/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // File upload (PDF, TXT, MD) - Session 402 ingestion system
  ingestFile: (file: File, options?: { generate_embeddings?: boolean }) => {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.generate_embeddings !== undefined) {
      formData.append('generate_embeddings', String(options.generate_embeddings))
    }
    return api.post('/documents/ingest-file/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // URL ingestion (YouTube videos or web pages) - Session 402
  // Session 733: Added multi-page crawling support
  ingestUrl: (url: string, options?: {
    title?: string;
    generate_embeddings?: boolean;
    crawl_site?: boolean;
    max_pages?: number;
    max_depth?: number;
    url_pattern?: string;
  }) => api.post('/documents/ingest-url/', { url, ...options }),

  // Semantic search
  semanticSearch: (query: string, options?: { limit?: number; similarity_threshold?: number }) =>
    api.post('/v1/rag/semantic-search/', { query, ...options }),

  // Generate response with RAG context
  generate: (query: string, options?: { max_context_chunks?: number }) =>
    api.post('/v1/rag/generate/', { query, ...options }),

  // Statistics
  stats: () => api.get('/v1/rag/stats/'),

  // Advanced multi-collection query
  advancedQuery: (query: string, collection_ids?: string[]) =>
    api.post('/v1/rag/advanced-query/', { query, collection_ids }),

  // Optimize embedding storage
  optimize: () => api.post('/v1/rag/optimize/'),

  // Collections management (knowledge collections)
  listCollections: () => api.get('/v1/knowledge/collections/list/'),
  createCollection: (data: { name: string; description?: string; document_ids?: string[]; tags?: string[] }) =>
    api.post('/v1/knowledge/collections/create/', data),
  // Note: Delete collection endpoint not available in backend

  // Documents management (Session 402 ingestion system)
  listDocuments: (params?: { collection_id?: string; limit?: number }) =>
    api.get('/documents/', { params }),
  documentDetail: (id: string) => api.get(`/documents/${id}/`),
  deleteDocument: (id: string) => api.delete(`/documents/${id}/delete/`),
}

// Session 716: Neural Orchestra API - AI consciousness visualization
export const neuralOrchestraApi = {
  // Get real-time ecosystem live feed (consciousness insights, system activity)
  ecosystemFeed: () => api.get('/neural-orchestra/ecosystem/live-feed/'),

  // Get agent statistics (total, active, collaborations, top performers)
  agentStats: () => api.get('/neural-orchestra/agents/stats/'),

  // Get learning status (models active, feedback processed, insights)
  learningStatus: () => api.get('/neural-orchestra/learning/status/'),

  // Get learning feed (real-time learning insights)
  learningFeed: () => api.get('/neural-orchestra/learning/feed/'),

  // Health check
  health: () => api.get('/neural-orchestra/health/'),

  // WebSocket configuration
  websocketConfig: () => api.get('/neural-orchestra/websocket-config/'),

  // Debug info
  debug: () => api.get('/neural-orchestra/debug/'),

  // Trigger reality check (force refresh)
  triggerRealityCheck: () => api.post('/neural-orchestra/reality-check/'),
}

// Session 733: Mythology Lab API - Hallucination detection and review
// Session 872: Fixed paths from /v1/mythology/ to /mythology/ (backend migrated in Session 871)
export const mythologyApi = {
  // Dashboard statistics
  stats: () => api.get('/mythology/stats/'),

  // Flagged content management
  flaggedContent: (params?: { limit?: number; status?: string }) =>
    api.get('/mythology/flagged-content/', { params }),
  flaggedContentDetail: (contentId: string) =>
    api.get(`/mythology/flagged-content/${contentId}/`),
  submitReview: (data: { content_id: string; decision: string; notes?: string }) =>
    api.post('/mythology/review/', data),

  // Recent events for Neural Scan section
  recentEvents: (params?: { limit?: number; severity?: string }) =>
    api.get('/mythology/recent-events/', { params }),

  // User reporting
  reportContent: (data: { content_id: string; reason: string; details?: string }) =>
    api.post('/mythology/report/', data),

  // Notifications
  notifications: (params?: { limit?: number; unread_only?: boolean }) =>
    api.get('/mythology/notifications/', { params }),
  markNotificationRead: (notificationId: string) =>
    api.post(`/mythology/notifications/${notificationId}/read/`),
  markAllNotificationsRead: () =>
    api.post('/mythology/notifications/mark-all-read/'),

  // Quarantine management (Session 541)
  quarantine: (params?: { limit?: number; status?: string }) =>
    api.get('/mythology/quarantine/', { params }),
  quarantineStats: () => api.get('/mythology/quarantine/stats/'),
  quarantineDetail: (quarantineId: string) =>
    api.get(`/mythology/quarantine/${quarantineId}/`),
  quarantineApprove: (quarantineId: string, data?: { notes?: string }) =>
    api.post(`/mythology/quarantine/${quarantineId}/approve/`, data || {}),
  quarantineReject: (quarantineId: string, data?: { reason?: string }) =>
    api.post(`/mythology/quarantine/${quarantineId}/reject/`, data || {}),
}

// Session 745: Collective Intelligence API
export const collectiveApi = {
  // Dashboard & Overview
  insights: () => api.get('/collective/insights/'),
  report: () => api.get('/collective/report/'),
  dashboard: () => api.get('/collective/dashboard/'),
  stats: () => api.get('/collective/stats/'),

  // Knowledge Management
  knowledgeGaps: () => api.get('/collective/knowledge-gaps/'),
  knowledgeQuery: (query: string) => api.get('/collective/knowledge/query/', { params: { q: query } }),
  knowledgeShare: (data: { topic: string; content: string; agents?: string[] }) =>
    api.post('/collective/knowledge/share/', data),
  knowledgeTopics: () => api.get('/collective/knowledge-topics/'),  // Session 782: Fixed endpoint

  // Network & Collaboration
  network: () => api.get('/collective/network/'),
  // Session 782: Use proper collaboration history endpoint
  collaborationHistory: (params?: { limit?: number; agent?: string }) =>
    api.get('/collaboration/history/', { params }),
  collaborationStats: () => api.get('/collective/stats/'),
  collaborationMonitor: () => api.get('/collective/monitor/'),
  findCollaborator: (data: { task: string; skills?: string[] }) =>
    api.post('/collaboration/find-collaborator/', data),

  // Teams
  teams: () => api.get('/teams/'),
  teamDetail: (id: string) => api.get(`/teams/${id}/`),
  createTeam: (data: { name: string; description?: string; agents?: string[] }) =>
    api.post('/teams/', data),
  updateTeam: (id: string, data: Record<string, unknown>) =>
    api.patch(`/teams/${id}/`, data),
  deleteTeam: (id: string) => api.delete(`/teams/${id}/`),
  teamMembers: (id: string) => api.get(`/teams/${id}/members/`),
  addTeamMember: (teamId: string, agentId: string) =>
    api.post(`/teams/${teamId}/members/`, { agent_id: agentId }),
  removeTeamMember: (teamId: string, agentId: string) =>
    api.delete(`/teams/${teamId}/members/${agentId}/`),

  // Consensus & Voting
  requestConsensus: (data: { topic: string; options: string[]; agents: string[] }) =>
    api.post('/agent-collab/consensus/', data),
  consensusStatus: (id: string) => api.get(`/agent-collab/consensus/${id}/`),
  submitVote: (consensusId: string, data: { vote: string; reasoning?: string }) =>
    api.post('/agent-collab/vote/', { consensus_id: consensusId, ...data }),

  // Messaging
  sendMessage: (data: { to_agent: string; content: string; priority?: string }) =>
    api.post('/agent-collab/message/', data),
  messages: (params?: { agent?: string; limit?: number }) =>
    api.get('/agent-collab/messages/', { params }),
}

// Session 745: Reasoning Engine API (expanded)
export const reasoningApi = {
  // Dashboard & Overview
  dashboard: () => api.get('/v1/reasoning/dashboard/'),
  config: () => api.get('/v1/reasoning/config/'),

  // Thoughts (reasoning chains)
  thoughts: (params?: { limit?: number; status?: string }) =>
    api.get('/v1/reasoning/thoughts/', { params }),
  thoughtDetail: (id: string) => api.get(`/v1/reasoning/thoughts/${id}/`),

  // Actions
  actions: (params?: { limit?: number; status?: string }) =>
    api.get('/v1/reasoning/actions/', { params }),
  actionDetail: (id: string) => api.get(`/v1/reasoning/actions/${id}/`),
  pendingActions: () => api.get('/v1/reasoning/actions/pending/'),
  // Session 782: Fix - use /respond/ endpoint with action body
  respondToAction: (id: string, action: string, notes?: string) =>
    api.post(`/v1/reasoning/actions/${id}/respond/`, { action, notes: notes || '' }),
  approveAction: (id: string, notes?: string) =>
    api.post(`/v1/reasoning/actions/${id}/respond/`, { action: 'accept', notes: notes || '' }),
  rejectAction: (id: string, notes?: string) =>
    api.post(`/v1/reasoning/actions/${id}/respond/`, { action: 'reject', notes: notes || '' }),
  deferAction: (id: string, notes?: string) =>
    api.post(`/v1/reasoning/actions/${id}/respond/`, { action: 'defer', notes: notes || '' }),

  // Concerns (issues detected)
  concerns: (params?: { limit?: number; severity?: string }) =>
    api.get('/v1/reasoning/concerns/', { params }),
  concernDetail: (id: string) => api.get(`/v1/reasoning/concerns/${id}/`),
  resolveConcern: (id: string, data?: { resolution?: string }) =>
    api.post(`/v1/reasoning/concerns/${id}/resolve/`, data || {}),

  // Trigger & Tasks
  trigger: (data: { prompt?: string; context?: string }) =>
    api.post('/v1/reasoning/trigger/', data),
  taskStatus: (taskId: string) => api.get(`/v1/reasoning/task/${taskId}/`),
}

// Session 745: Experiment Recommendations API
export const experimentRecommendationsApi = {
  list: () => api.get('/experiment-recommendations/'),
}

// Session 745: Autonomous Systems API
export const autonomousApi = {
  // System Control
  status: () => api.get('/autonomous-system/status'),
  start: () => api.post('/autonomous-system/start'),
  pause: () => api.post('/autonomous-system/pause'),

  // Situations (autonomous behaviors)
  situations: () => api.get('/autonomous/situations/'),
  situationDetail: (type: string) => api.get(`/autonomous/situations/${type}/`),
  toggleSituation: (type: string) => api.post(`/autonomous/situations/${type}/toggle/`),
  runSituationNow: (type: string) => api.post(`/autonomous/situations/${type}/run-now/`),

  // Triggers
  triggers: () => api.get('/autonomous/triggers/'),
  triggerDetail: (id: string) => api.get(`/autonomous/triggers/${id}/`),
  createTrigger: (data: Record<string, unknown>) => api.post('/autonomous/triggers/', data),
  updateTrigger: (id: string, data: Record<string, unknown>) => api.patch(`/autonomous/triggers/${id}/`, data),
  deleteTrigger: (id: string) => api.delete(`/autonomous/triggers/${id}/`),

  // Trigger Events (history)
  triggerEvents: (params?: { limit?: number; trigger_id?: string }) =>
    api.get('/autonomous/trigger-events/', { params }),

  // Analytics
  analyticsSummary: () => api.get('/autonomous/analytics/summary/'),
  analyticsTimeline: (params?: { days?: number }) =>
    api.get('/autonomous/analytics/timeline/', { params }),
}

// Session 745: Analytics Dashboard API
export const analyticsApi = {
  // Dashboard Overview
  overview: () => api.get('/analytics/overview/'),
  summary: (params?: { period?: string }) => api.get('/analytics/summary/', { params }),

  // Chart Data
  charts: {
    agentActivity: (params?: { days?: number }) =>
      api.get('/analytics/charts/agent-activity/', { params }),
    contentProduction: (params?: { days?: number }) =>
      api.get('/analytics/charts/content-production/', { params }),
    revenue: (params?: { days?: number }) =>
      api.get('/analytics/charts/revenue/', { params }),
    userEngagement: (params?: { days?: number }) =>
      api.get('/analytics/charts/user-engagement/', { params }),
    spiderPerformance: (params?: { days?: number }) =>
      api.get('/analytics/charts/spider-performance/', { params }),
    learningProgress: (params?: { days?: number }) =>
      api.get('/analytics/charts/learning-progress/', { params }),
    collaborationMetrics: (params?: { days?: number }) =>
      api.get('/analytics/charts/collaboration/', { params }),
    systemHealth: (params?: { days?: number }) =>
      api.get('/analytics/charts/system-health/', { params }),
  },

  // Analytics v2 (detailed)
  v2: {
    trends: (params?: { metric?: string; period?: string }) =>
      api.get('/analytics/v2/trends/', { params }),
    comparison: (params?: { metrics?: string[]; period?: string }) =>
      api.get('/analytics/v2/comparison/', { params }),
    breakdown: (params?: { dimension?: string }) =>
      api.get('/analytics/v2/breakdown/', { params }),
    topPerformers: (params?: { category?: string; limit?: number }) =>
      api.get('/analytics/v2/top-performers/', { params }),
    anomalies: () => api.get('/analytics/v2/anomalies/'),
    forecast: (params?: { metric?: string; days?: number }) =>
      api.get('/analytics/v2/forecast/', { params }),
    export: (params?: { format?: string; metrics?: string[] }) =>
      api.get('/analytics/v2/export/', { params }),
  },

  // Reports
  reports: {
    list: () => api.get('/analytics/reports/'),
    generate: (data: { type: string; period?: string; format?: string }) =>
      api.post('/analytics/reports/generate/', data),
    schedule: (data: { type: string; frequency: string; recipients?: string[] }) =>
      api.post('/analytics/reports/schedule/', data),
    download: (id: string) => api.get(`/analytics/reports/${id}/download/`),
  },
}

// Session 745: Learning Journey API
export const journeyApi = {
  // Journey Management
  list: () => api.get('/learning/journeys/'),
  active: () => api.get('/learning/journeys/active/'),
  detail: (id: string) => api.get(`/learning/journeys/${id}/`),
  start: (data: { template_id?: string; topic?: string; goals?: string[] }) =>
    api.post('/learning/journeys/start/', data),
  pause: (id: string) => api.post(`/learning/journeys/${id}/pause/`),
  resume: (id: string) => api.post(`/learning/journeys/${id}/resume/`),
  complete: (id: string) => api.post(`/learning/journeys/${id}/complete/`),
  abandon: (id: string) => api.post(`/learning/journeys/${id}/abandon/`),

  // Journey Steps
  status: (id: string) => api.get(`/learning/journeys/${id}/status/`),
  startStep: (journeyId: string, step: number) =>
    api.post(`/learning/journeys/${journeyId}/step/${step}/start/`),
  completeStep: (journeyId: string, step: number, data?: { notes?: string; outcome?: string }) =>
    api.post(`/learning/journeys/${journeyId}/step/${step}/complete/`, data || {}),
  skipStep: (journeyId: string, step: number) =>
    api.post(`/learning/journeys/${journeyId}/step/${step}/skip/`),

  // Templates
  templates: () => api.get('/learning/templates/'),
  templateDetail: (id: string) => api.get(`/learning/templates/${id}/`),

  // Progress & Analytics
  progress: (id: string) => api.get(`/learning/journeys/${id}/progress/`),
  analytics: () => api.get('/learning/journeys/analytics/'),
  achievements: () => api.get('/learning/achievements/'),
}

// Session 745: Billing & Subscription API (Stripe)
export const billingApi = {
  // Subscription Management
  subscriptionStatus: () => api.get('/stripe/subscription-status/'),
  subscriptionPlans: () => api.get('/stripe/plans/'),
  subscribe: (data: { plan_id: string; payment_method_id?: string }) =>
    api.post('/stripe/subscribe/', data),
  cancelSubscription: () => api.post('/stripe/cancel-subscription/'),
  resumeSubscription: () => api.post('/stripe/resume-subscription/'),
  updateSubscription: (data: { plan_id: string }) =>
    api.post('/stripe/update-subscription/', data),

  // Payment Methods
  paymentMethods: () => api.get('/stripe/payment-methods/'),
  addPaymentMethod: (data: { payment_method_id: string }) =>
    api.post('/stripe/payment-methods/', data),
  removePaymentMethod: (id: string) => api.delete(`/stripe/payment-methods/${id}/`),
  setDefaultPaymentMethod: (id: string) =>
    api.post(`/stripe/payment-methods/${id}/default/`),

  // Billing & Invoices
  invoices: (params?: { limit?: number }) => api.get('/stripe/invoices/', { params }),
  invoiceDetail: (id: string) => api.get(`/stripe/invoices/${id}/`),
  upcomingInvoice: () => api.get('/stripe/upcoming-invoice/'),

  // Usage & Billing Portal
  usage: () => api.get('/stripe/usage/'),
  billingPortal: () => api.post('/stripe/billing-portal/'),

  // Session 1009: Removed voiceCheckout methods (orphan cleanup)
}

// Session 745: Voice Marketplace API
export const voiceMarketplaceApi = {
  // Browse & Discovery
  browse: (params?: { category?: string; sort?: string; search?: string }) =>
    api.get('/voice-marketplace/', { params }),
  voiceDetail: (id: string) => api.get(`/voice-marketplace/${id}/`),
  featured: () => api.get('/voice-marketplace/featured/'),
  categories: () => api.get('/voice-marketplace/categories/'),

  // My Voices (creator side)
  myVoices: () => api.get('/voice-marketplace/my-voices/'),
  createVoice: (data: FormData) => api.post('/voice-marketplace/create/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  updateVoice: (id: string, data: Record<string, unknown>) =>
    api.patch(`/voice-marketplace/${id}/`, data),
  deleteVoice: (id: string) => api.delete(`/voice-marketplace/${id}/`),
  publishVoice: (id: string) => api.post(`/voice-marketplace/${id}/publish/`),
  unpublishVoice: (id: string) => api.post(`/voice-marketplace/${id}/unpublish/`),

  // Voice Cloning
  startClone: (data: FormData) => api.post('/voice-marketplace/clone/start/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  cloneStatus: (taskId: string) => api.get(`/voice-marketplace/clone/status/${taskId}/`),

  // Generation & Preview
  generate: (id: string, data: { text: string; settings?: Record<string, unknown> }) =>
    api.post(`/voice-marketplace/${id}/generate/`, data),
  preview: (id: string) => api.get(`/voice-marketplace/${id}/preview/`),

  // Reviews & Ratings
  reviews: (id: string) => api.get(`/voice-marketplace/${id}/reviews/`),
  addReview: (id: string, data: { rating: number; comment?: string }) =>
    api.post(`/voice-marketplace/${id}/reviews/`, data),

  // Purchases & Licensing
  purchase: (id: string, data?: { license_type?: string }) =>
    api.post(`/voice-marketplace/${id}/purchase/`, data || {}),
  myPurchases: () => api.get('/voice-marketplace/purchases/'),

  // Earnings & Transactions (creator analytics)
  earnings: () => api.get('/voice-marketplace/earnings/'),
  transactions: (params?: { limit?: number; type?: string }) =>
    api.get('/voice-marketplace/transactions/', { params }),
  withdraw: (data: { amount: number; method: string }) =>
    api.post('/voice-marketplace/withdraw/', data),

  // Stats
  stats: () => api.get('/voice-marketplace/stats/'),
}

// Session 926: Universal Agent Voice System - TTS API
export const ttsApi = {
  /**
   * Generate TTS audio with caching support.
   * Supports agent voice lookup for automatic voice selection.
   */
  generate: (text: string, agentName?: string, voiceId?: string) =>
    api.post('/tts/generate/', {
      text,
      agent_name: agentName,
      voice_id: voiceId,
    }),

  /**
   * Estimate TTS cost and duration before generation.
   * Use this for long content to show cost warning.
   */
  estimate: (text: string) =>
    api.post('/tts/estimate/', { text }),

  /**
   * List available TTS voices with descriptions.
   */
  voices: () => api.get('/tts/voices/'),

  /**
   * Get user's voice settings (enabled, default voice, cloned voice).
   */
  settings: () => api.get('/tts/settings/'),

  /**
   * Speak text with chunking and summarization support.
   * Used for assistant chat responses.
   */
  speak: (text: string, voiceId?: string, options?: {
    model?: string
    chunk_index?: number
    skip_summarize?: boolean
  }) =>
    api.post('/tts/speak/', {
      text,
      voice_id: voiceId,
      ...options,
    }),
}

// Session 758: Integration Health & Observability API
export const integrationHealthApi = {
  // Health check for all 6 context sources
  health: () => api.get('/integration/health/'),

  // Context injection metrics over time
  metrics: () => api.get('/integration/metrics/'),

  // Alerts for silent failures
  alerts: () => api.get('/integration/alerts/'),

  // Execution quality analysis (with vs without context)
  quality: () => api.get('/integration/quality/'),
}

// Session 764: Orchestration Layer API (Multi-Agent Workflow Execution)
export interface OrchestrationWorkflow {
  id: string
  name: string
  description: string
  execution_mode: 'sequential' | 'parallel' | 'dependency'
  max_retries: number
  timeout_seconds: number
  cost_budget: string | null
  step_count: number
  created_at: string | null
  updated_at: string | null
}

// Session 768: Workflow step with full configuration
export interface OrchestrationWorkflowStep {
  id: string
  order: number
  name: string
  description: string
  agent: string
  prompt_template: string
  input_params: string[]
  config: Record<string, unknown>
  timeout_seconds: number
  requires_approval: boolean
  approval_config: Record<string, unknown>
  depends_on_steps: number[]
  rollback_step: number | null
  cost_limit: string | null
  retry_count: number
  is_required: boolean
}

// Session 768: Full workflow detail with steps
export interface OrchestrationWorkflowDetail {
  id: string
  name: string
  description: string
  execution_mode: 'sequential' | 'parallel' | 'dependency'
  max_retries: number
  timeout_seconds: number
  cost_budget: string | null
  require_approval_on_error: boolean
  created_by: string | null
  is_template: boolean
  created_at: string | null
  updated_at: string | null
}

// Session 768: Available agent for workflow configuration
export interface OrchestrationAgent {
  key: string
  name: string
  description: string
  category: string
  capabilities: string[]
}

// Session 768: Create workflow request
export interface CreateWorkflowRequest {
  name: string
  description?: string
  execution_mode?: 'sequential' | 'parallel' | 'dependency'
  max_retries?: number
  timeout_seconds?: number
  cost_budget?: string
  require_approval_on_error?: boolean
  steps: {
    order?: number
    name: string
    description?: string
    agent: string
    prompt_template: string
    config?: Record<string, unknown>
    timeout_seconds?: number
    requires_approval?: boolean
    approval_config?: Record<string, unknown>
    depends_on_steps?: number[]
    rollback_step?: number
    cost_limit?: string
    retry_count?: number
    is_required?: boolean
  }[]
}

export interface OrchestrationExecution {
  id: string
  workflow_id: string
  workflow_name: string
  status: 'pending' | 'running' | 'waiting_approval' | 'completed' | 'failed' | 'cancelled' | 'paused'
  current_step: number
  total_steps: number
  total_cost: string
  total_tokens: number
  // Session 769: External API cost tracking
  total_external_cost?: string
  external_cost_breakdown?: Record<string, number>
  total_combined_cost?: string
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  triggered_by: string | null
}

export interface OrchestrationStepExecution {
  step_number: number
  agent_name: string
  status: string
  started_at: string | null
  completed_at: string | null
  cost: string
  tokens: number
  // Session 769: External API cost tracking per step
  external_cost?: string
  external_cost_breakdown?: Record<string, number>
  combined_cost?: string
  retry_count: number
  error_message: string | null
  output_preview: string | null
}

export interface OrchestrationExecutionDetail {
  execution: OrchestrationExecution & {
    input_data: Record<string, unknown>
    final_output: Record<string, unknown> | null
  }
  steps: OrchestrationStepExecution[]
  approval_gates: {
    id: string
    step_number: number | null
    status: string
    created_at: string | null
    expires_at: string | null
  }[]
  // Session 770: Podcast TTS cost info if this is a podcast workflow
  podcast_info?: {
    episode_id: string
    title: string
    topic: string
    status: string
    tts_cost: string
    tts_cost_breakdown: Record<string, number>
    audio_url: string
    audio_duration_seconds: number | null
  }
}

// Session 765: Step intelligence data linking to core agent systems
export interface StepIntelligenceMemory {
  id: string
  title: string
  content: string
  memory_type: string
  valence: string
  importance_score: number
  created_at: string | null
}

export interface StepIntelligenceData {
  step_info: {
    step_number: number
    agent_name: string
    status: string
    cost: string
    tokens: number
    duration_seconds: number | null
    started_at: string | null
    completed_at: string | null
    input_data: Record<string, unknown>
    output_data: Record<string, unknown>
    error_message: string | null
    retry_count: number
    // Session 767: Full context from workflow step config (not truncated)
    full_context?: {
      dream_context?: {
        title?: string
        content?: string
        type?: string
      }
      hivemind_context?: {
        question?: string
        synthesis?: string
        mode?: string
      }
    }
  }
  agent_execution: {
    id: string
    task: string
    status: string
    execution_time_ms: number
    tokens_used: number
    cost: string
    output_data: Record<string, unknown>
    error_message: string | null
    created_at: string | null
  } | null
  memories_created: StepIntelligenceMemory[]
  context_injected: {
    spider_data?: boolean
    spider_trends?: number
    spider_discussions?: number
    learning_patterns?: boolean
    advisor_insights?: boolean
    performance_feedback?: boolean
    knowledge_state?: boolean
    scifi_context?: boolean
    // Session 769: Additional context fields can be added dynamically
    [key: string]: unknown
  }
  tool_calls: Array<{
    tool?: string  // Session 769: Primary tool name field
    name?: string
    function?: string
    arguments?: Record<string, unknown>
    result?: {
      success?: boolean
      data?: Record<string, unknown>
    }
  }>
}

export const orchestrationApi = {
  // List available workflows
  listWorkflows: () =>
    api.get<{ success: boolean; workflows: OrchestrationWorkflow[]; count: number }>(
      '/orchestration/workflows/'
    ),

  // Session 768: Get workflow detail with all steps
  getWorkflowDetail: (workflowId: string) =>
    api.get<{
      success: boolean
      workflow: OrchestrationWorkflowDetail
      steps: OrchestrationWorkflowStep[]
      input_parameters: string[]
    }>(`/orchestration/workflows/${workflowId}/`),

  // Session 768: Get available agents for workflow configuration
  getAgents: () =>
    api.get<{ success: boolean; agents: OrchestrationAgent[]; count: number }>(
      '/orchestration/agents/'
    ),

  // Session 768: Create a new workflow
  createWorkflow: (data: CreateWorkflowRequest) =>
    api.post<{ success: boolean; workflow_id: string; message: string }>(
      '/orchestration/workflows/create/',
      data
    ),

  // Execute a workflow
  execute: (workflowId: string, input?: Record<string, unknown>, async = true) =>
    api.post<{ success: boolean; execution_id: string; status: string; message: string }>(
      `/orchestration/workflows/${workflowId}/execute/`,
      { input, async }
    ),

  // List executions
  listExecutions: (params?: { status?: string; workflow_id?: string; limit?: number; all?: boolean }) =>
    api.get<{ success: boolean; executions: OrchestrationExecution[]; count: number }>(
      '/orchestration/executions/',
      { params }
    ),

  // Session 1000C: Combined active work for NowHub
  activeWork: () =>
    api.get<{
      success: boolean
      initiatives: {
        active_count: number
        by_stage: Record<string, number>
        recent: Array<{ id: string; name: string; current_stage: number; completion_percentage: number }>
      }
      agent_executions: {
        last_24h: number
        completed: number
        failed: number
        top_agents: Array<{ name: string; count: number }>
      }
      workflows: { running: number }
    }>('/orchestration/active-work/'),

  // Get execution details
  getExecution: (executionId: string) =>
    api.get<{ success: boolean } & OrchestrationExecutionDetail>(
      `/orchestration/executions/${executionId}/`
    ),

  // Resume a paused/waiting execution
  resume: (executionId: string, modifications?: Record<string, unknown>) =>
    api.post<{ success: boolean; execution_id: string; status: string; message: string }>(
      `/orchestration/executions/${executionId}/resume/`,
      { modifications }
    ),

  // Cancel an execution
  cancel: (executionId: string, reason?: string) =>
    api.post<{ success: boolean; execution_id: string; status: string; message: string }>(
      `/orchestration/executions/${executionId}/cancel/`,
      { reason }
    ),

  // Session 765: Get step intelligence data (agent execution, memories, context, tools)
  getStepIntelligence: (executionId: string, stepNumber: number) =>
    api.get<{ success: boolean; intelligence: StepIntelligenceData }>(
      `/orchestration/executions/${executionId}/steps/${stepNumber}/intelligence/`
    ),
}

// Session 784: Documentation Index API
export interface DocsDocument {
  path: string
  title: string
  status: 'active' | 'superseded' | 'deprecated' | 'draft' | 'unknown'
  type: string
  subsystems: string[]
  lines: number
  has_frontmatter: boolean
  outbound_links: Array<{
    target: string
    occurrences: number
    snippets: string[]
  }>
  inbound_links_count: number
  created_at?: string
  modified_at?: string
}

export interface DocsIndexResponse {
  generated_at: string
  version: string
  total_count: number
  filtered_count: number
  documents: DocsDocument[]
  graph: {
    total_links: number
    most_referenced: Array<{ path: string; count: number }>
    orphan_docs: string[]
    broken_links: Array<{ source: string; target: string }>
  }
  filters: {
    statuses: string[]
    types: string[]
    subsystems: string[]
  }
}

export interface DocsDetailResponse {
  document: DocsDocument
  inbound_links: Array<{
    source: string
    title: string
    occurrences: number
    snippets: string[]
  }>
  inbound_count: number
  is_orphan: boolean
}

export interface DocsStatsResponse {
  total_documents: number
  total_lines: number
  with_frontmatter: number
  by_status: Record<string, number>
  by_type: Record<string, number>
  graph: {
    total_links: number
    broken_links: number
    orphan_docs: number
  }
  generated_at: string
  version: string
}

export const docsIndexApi = {
  // Get full documentation index with filtering
  index: (params?: { status?: string; type?: string; subsystem?: string; search?: string; limit?: number }) =>
    api.get<DocsIndexResponse>('/docs/index/', { params }),

  // Get stats for dashboard widgets
  stats: () => api.get<DocsStatsResponse>('/docs/stats/'),

  // Get cross-reference graph summary
  graph: () => api.get<{
    total_links: number
    most_referenced: Array<{ path: string; count: number }>
    orphan_docs: string[]
    broken_links: Array<{ source: string; target: string }>
    stats: {
      total_documents: number
      by_status: Record<string, number>
      by_type: Record<string, number>
    }
  }>('/docs/graph/'),

  // Get details for a specific document
  detail: (docPath: string) => api.get<DocsDetailResponse>(`/docs/detail/${docPath}/`),
}

// Session 1009: Removed agentCollaborationApi + interfaces (orphan cleanup)

// =============================================================================
// Session 815: Platform Command Center API
// =============================================================================

export interface MissionMetric {
  current: number
  target: number
  progress_pct: number
}

export interface MissionMetricsSummary {
  revenue: MissionMetric
  llm_cost: MissionMetric
  canon: MissionMetric
  playbooks: MissionMetric
}

export interface MissionData {
  status: string
  statement: string
  goal: string
  period: string
  session?: number
  priorities?: Array<{
    rank: number
    name: string
    why: string
  }>
}

export interface SystemOwner {
  name: string
  authority: string
  override_level: string
  contact: string
}

export interface EmergencyStatus {
  skin_lock: boolean
  skin_status: string
  quarantined_agents: string[]
  quarantined_count: number
  system_paused: boolean
  pending_critical_decisions: number
}

export interface PendingDecision {
  id: string
  title: string
  summary: string
  urgency: string
  item_type: string
  source_type: string
  source_agent: string
  created_at: string
  ml_recommendation: string
}

export interface CanonDocument {
  path: string
  name: string
  title: string
  category: string
  size_bytes: number
  modified_at: string
  lines: number
}

export interface Playbook {
  path: string
  name: string
  title: string
  description: string
  category: string
  size_bytes: number
  modified_at: string
}

// Session 832: Enhanced RecentActivity with all fields from backend
export interface RecentActivity {
  id: string
  agent_name: string
  agent_category: string | null
  task: string
  task_full: string
  created_at: string | null
  completed_at: string | null
  success: boolean
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  execution_time_ms: number | null
  tokens_used: number
  cost: number
  error_message: string | null
  output_summary: string | null
  tool_results: Array<string | { name?: string; tool?: string }>
  input_data: Record<string, string> | null
  triggered_by: string
}

// Session 832: System Activity types for dreams, conversations, decisions, pilots
export interface SystemActivityItem {
  id: string
  type: 'dream' | 'conversation' | 'decision' | 'pilot'
  icon: string
  title: string
  full_title?: string
  subtitle: string
  full_subtitle?: string
  timestamp: string
  timestamp_display: string
  agent?: string
  agent_name?: string
  agents?: string[]
  category?: string
  content?: string
  status?: string
  decision_type?: string
  kpi?: string
}

export interface SystemActivity {
  success: boolean
  activities: SystemActivityItem[]
  counts: Record<string, number>
  total: number
  hours_back: number
  timestamp: string
}

export const platformApi = {
  // Get current mission with metrics summary
  mission: () =>
    api.get<{
      mission: MissionData
      metrics_summary: MissionMetricsSummary
    }>('/platform/mission/'),

  // Get detailed metrics
  metrics: () =>
    api.get<{
      revenue: {
        monthly: number
        lifetime: number
        pending: number
      }
      llm_costs: {
        daily: { cost: number; calls: number; tokens: number }
        weekly: { cost: number; calls: number }
        monthly: { cost: number; calls: number }
      }
      canon: {
        total: number
        by_category: Record<string, number>
      }
      playbooks: {
        total: number
        by_category: Record<string, number>
      }
      recent_activity: RecentActivity[]
      // Session 832: System activity from RecentActivityService
      system_activity: SystemActivity
    }>('/platform/metrics/'),

  // Get governance status
  governance: () =>
    api.get<{
      owner: SystemOwner
      emergency_controls: EmergencyStatus
      pending_decisions: PendingDecision[]
      pending_decisions_count: number
      authority_escalation_path: Array<{
        level: number
        entity: string
        scope: string
      }>
    }>('/platform/governance/'),

  // Trigger emergency halt
  emergencyHalt: () =>
    api.post<{
      success: boolean
      message: string
      attention_item_id?: string
      error?: string
    }>('/platform/emergency-halt/'),

  // Get canon documents
  canon: (category?: string) =>
    api.get<{
      documents: CanonDocument[]
      total: number
      by_category: Record<string, number>
      filtered_count: number
    }>('/platform/canon/', { params: category ? { category } : {} }),

  // Get playbooks
  playbooks: (category?: string) =>
    api.get<{
      playbooks: Playbook[]
      total: number
      by_category: Record<string, number>
      filtered_count: number
    }>('/platform/playbooks/', { params: category ? { category } : {} }),

  // Session 816: Get audits
  audits: (type?: string) =>
    api.get<{
      audits: Array<{
        path: string
        name: string
        title: string
        summary: string
        audit_type: string
        size_bytes: number
        modified_at: string
      }>
      total: number
      by_type: Record<string, number>
      filtered_count: number
    }>('/platform/audits/', { params: type ? { type } : {} }),

  // Session 833: Get document content for viewer
  docContent: (path: string) =>
    api.get<{
      content: string
      metadata: {
        path: string
        name: string
        title: string
        lines: number
        size_bytes: number
        modified_at: string
      }
      error?: string
    }>('/platform/doc-content/', { params: { path } }),

  // Session 818: Toggle SKIN lock
  skinLock: (action: 'lock' | 'unlock' | 'toggle' = 'toggle') =>
    api.post<{
      success: boolean
      locked: boolean
      status: string
      message: string
      error?: string
    }>('/platform/skin-lock/', { action }),

  // Session 819: Promote content to Canon
  promoteToCanon: (params: {
    title: string
    content: string
    category: 'creative' | 'technical' | 'operational'
    source_type?: string
    source_id?: string
    tags?: string[]
  }) =>
    api.post<{
      success: boolean
      path: string
      message: string
      metadata?: {
        title: string
        category: string
        filename: string
        promoted_at: string
        promoted_by: string
      }
      error?: string
    }>('/platform/canon/promote/', params),

  // Session 819: Run System Audit
  runAudit: () =>
    api.post<{
      success: boolean
      audit_path: string
      summary: {
        passed: number
        failed: number
        warnings: number
        total_checks: number
        health_score: number
      }
      message: string
      error?: string
    }>('/platform/audits/run/', {}),

  // Session 840: Audit Tracking System
  auditFindingsSummary: () =>
    api.get<{
      success: boolean
      summary: {
        total_reports: number
        total_findings: number
        by_status: Record<string, number>
        by_priority: Record<string, number>
        by_category: Record<string, number>
        open_p0: number
        open_p1: number
      }
    }>('/audit-tracking/findings/summary/'),

  auditFindings: (params?: {
    status?: string
    priority?: string
    category?: string
    limit?: number
  }) =>
    api.get<{
      success: boolean
      count: number
      findings: Array<{
        id: string
        title: string
        description: string
        priority: string
        category: string
        status: string
        impact: string
        audit_report: {
          id: string
          title: string
        }
        recommendation: string
        assigned_agent: string
        fixed_by: string
        created_at: string
        updated_at: string
      }>
    }>('/audit-tracking/findings/', { params }),

  auditFindingUpdateStatus: (findingId: string, data: {
    status: string
    notes?: string
    fixed_by?: string
  }) =>
    api.post<{
      success: boolean
      finding: {
        id: string
        status: string
        updated_at: string
      }
      error?: string
    }>(`/audit-tracking/findings/${findingId}/status/`, data),

  // Session 829: Remediation Status and Control
  remediationStatus: () =>
    api.get<{
      findings: {
        total: number
        by_status: Record<string, number>
        by_priority: Record<string, number>
      }
      tasks: {
        total: number
        by_status: Record<string, number>
        by_agent: Array<{ agent: string; count: number }>
      }
      recent_tasks: Array<{
        id: string
        finding_title: string
        agent: string
        status: string
        created_at: string
        completed_at: string | null
      }>
      progress: {
        completed: number
        total: number
        percentage: number
      }
    }>('/platform/remediation/status/'),

  runRemediation: (params: { agent?: string; limit?: number; write_files?: boolean }) =>
    api.post<{
      success: boolean
      message: string
      limit: number
    }>('/platform/actions/run-remediation/', params),

  runSelfAudit: () =>
    api.post<{
      success: boolean
      message: string
    }>('/platform/actions/run-self-audit/', {}),

  // Session 830: Live self-healing progress for UI polling
  selfHealingProgress: () =>
    api.get<{
      total_tasks: number
      completed_tasks: number
      progress_pct: number
      by_agent: Array<{
        agent: string
        completed: number
        total: number
        pct: number
        status: 'DONE' | 'RUNNING' | 'PENDING' | 'IDLE'
      }>
      recent_activity: {
        completed_last_10m: number
        in_progress: number
        assigned: number
        last_completed_at: string | null
      }
      updated_at: string
    }>('/self-healing/progress/'),

  // Session 845: Decision summary detail for System Activity modal
  decisionSummaryDetail: (decisionId: string) =>
    api.get<{ success: boolean; item: Record<string, unknown> }>(`/platform/decision-summary/${decisionId}/`),

  // Session 852: Create initiative from decision
  createInitiativeFromDecision: (decisionId: string) =>
    api.post<{
      success: boolean
      message?: string
      error?: string
      initiative?: {
        id: string
        name: string
        current_stage: number
        status: string
      }
    }>(`/platform/decision-summary/${decisionId}/create-initiative/`),

  // Session 847: Initiative Pipeline Dashboard
  // Session 872: Fixed paths from /v1/initiatives/ to /initiatives/ (backend migrated in Session 871)
  // Session 902: Increased limit to 500 to ensure all initiatives (including completed) are returned
  initiatives: () =>
    api.get<{
      success: boolean
      count: number
      initiatives: Array<{
        id: string
        name: string
        description: string
        status: string
        current_stage: number
        completion_percentage: number
        stages: Record<number, {
          status: string
          stage_name: string
          document_id: string | null
          approved_at: string | null
        }>
        created_at: string
        updated_at: string
      }>
    }>('/initiatives/?limit=500'),

  // Session 847: Auto-populate initiatives from existing deliverables
  populateInitiatives: () =>
    api.post<{
      success: boolean
      created_count: number
      created_initiatives: Array<{ name: string; stages_linked: number }>
      message: string
    }>('/initiatives/populate/'),

  // Session 898: Get full origin trace for an initiative
  originTrace: (initiativeId: string) =>
    api.get<{
      success: boolean
      trace: {
        initiative: {
          id: string
          name: string
          description: string
          status: string
          current_stage: number
          created_at: string
          updated_at: string
        }
        decision: {
          id: string
          decision_type: string
          artifact_type: string
          topic: string
          key_insights: string[]
          recommended_stance: string
          suggested_feature: string | null
          rationale: string
          participants: string[]
          status: string
          created_at: string
        } | null
        conversation: {
          id: string
          type: string
          topic: string
          conversation_type: string
          trigger_type?: string
          status: string
          message_count?: number
          contribution_count?: number
          quality_score?: number
          conclusion: string | null
          synthesis_summary?: string | null
          started_at: string | null
          ended_at?: string | null
          completed_at?: string | null
          // Session 899: Actual conversation messages
          messages?: Array<{
            id: string
            agent_name: string
            content: string
            message_type: string
            sequence_number: number
          }>
        } | null
        trigger: {
          type: string
          description: string
        } | null
        agents: string[]
        stages: Array<{
          stage: number
          name: string
          status: string
          document_id: string | null
          approved_at: string | null
          approved_by: string | null
        }>
        deliverable: {
          id: string
          title: string
          deliverable_type: string
          status: string
          content_length: number
          created_at: string
        } | null
        trace_completeness: {
          has_decision: boolean
          has_conversation: boolean
          has_trigger: boolean
          has_agents: boolean
          has_stages: boolean
          has_deliverable: boolean
          completeness_score: number
        }
      }
    }>(`/initiatives/${initiativeId}/origin-trace/`),

  // Session 928: Pipeline health monitoring
  pipelineHealth: (staleHours?: number) =>
    api.get<{
      generated_at: string
      stale_threshold_hours: number
      summary: {
        active_count: number
        moved_last_24h: number
        transitions_last_24h: number
        transitions_last_1h: number
        approvals_last_24h: number
        stale_count: number
        blocked_count: number
      }
      recent_transitions: Array<{
        id: string
        initiative_id: string
        initiative_name: string
        stage_number: number
        from_status: string
        to_status: string
        timestamp: string
        time_ago: string
        triggered_by: string
        trigger_type: string
        quality_score: number | null
        had_error: boolean
      }>
      stale_initiatives: Array<{
        id: string
        name: string
        current_stage: number
        last_activity: string
        days_stale: number
        completion_pct: number
      }>
      stage_distribution: Record<string, Record<string, number>>
      hourly_activity: Array<{
        hour: number
        label: string
        transitions: number
      }>
      health_status: 'healthy' | 'moderate' | 'slow' | 'stalled' | 'critical' | 'error' | 'unknown'
      health_message: string
    }>(`/initiatives/pipeline-health/${staleHours ? `?stale_hours=${staleHours}` : ''}`),

  // Session 928: Diagnose stuck initiatives
  diagnoseStuck: (limit?: number) =>
    api.get<{
      generated_at: string
      rate_limit_stats: {
        progressions_today: number
        daily_limit: number
        remaining: number
      }
      summary: {
        total_checked: number
        no_document: number
        quality_failed: number
        founder_intent_missing: number
        ready_to_progress: number
      }
      blocking_reasons: Record<string, number>
      initiatives: Array<{
        id: string
        name: string
        stage: number
        blockers: string[]
        can_progress: boolean
        quality_check?: {
          passes: boolean
          confidence: string
          reason: string
        }
      }>
    }>(`/initiatives/diagnose-stuck/${limit ? `?limit=${limit}` : '?limit=100'}`),

  // Session 928: Start a conversation about an initiative
  startConversation: (
    initiativeId: string,
    params?: {
      topic?: string
      objective?: string
      conversation_type?: 'analytical' | 'creative' | 'debate' | 'planning' | 'critique' | 'general'
      auto_select_agents?: boolean
    }
  ) =>
    api.post<{
      success: boolean
      session_id: string
      session_url: string
      message: string
      participants: number
      conversation_type: string
    }>(`/initiatives/${initiativeId}/start-conversation/`, params || {}),

  // Session 957: RAG Observability Dashboard
  ragDashboard: () =>
    api.get<{
      success: boolean
      timestamp: string
      document_inventory: {
        total_documents: number
        total_active: number
        total_critical: number
        by_risk_level: Record<string, number>
        by_document_class: Record<string, number>
        critical_by_class: Record<string, number>
        high_risk_by_class: Record<string, number>
        avg_age_days: number
        newest_doc_age_days: number
        oldest_critical_age_days: number
      }
      retrieval_channels: {
        total_retrievals: number
        semantic_channel_count: number
        critical_channel_count: number
        incident_channel_count: number
        constraint_channel_count: number
        semantic_pct: number
        critical_pct: number
        incident_pct: number
        constraint_pct: number
      }
      risk_boost: {
        total_results_boosted: number
        total_results_unboosted: number
        avg_boost_applied: number
        max_boost_applied: number
        boost_by_risk_level: Record<string, { count: number; boost: number; total_boost_potential: number }>
        boost_by_document_class: Record<string, { count: number; boost: number; total_boost_potential: number }>
      }
      context_budget: {
        total_budget: number
        total_used: number
        utilization_pct: number
        critical_tier_tokens: number
        reserved_tier_tokens: number
        high_tier_tokens: number
        medium_tier_tokens: number
        low_tier_tokens: number
        critical_docs_tokens: number
        incident_docs_tokens: number
        audit_findings_tokens: number
        section_usage: Record<string, { max_tokens: number; priority: string; status: string }>
        is_over_budget: boolean
        sections_truncated: string[]
        sections_skipped: string[]
      }
      health_indicators: Array<{
        level: 'success' | 'warning' | 'info'
        message: string
        recommendation?: string
      }>
      summary: {
        total_documents: number
        critical_documents: number
        classified_documents: number
        high_risk_documents: number
        budget_utilization: number
        reserved_tier_tokens: number
      }
    }>('/rag/observability/dashboard/'),

  ragCriticalDocs: () =>
    api.get<{
      success: boolean
      critical_docs: Array<{
        id: string
        title: string
        path: string
        document_class: string
        risk_level: string
        updated_at: string
        age_days: number
        retrieval_boost: number
      }>
      count: number
    }>('/rag/observability/critical-docs/'),

  ragRiskDistribution: () =>
    api.get<{
      success: boolean
      distribution: {
        risk_matrix: Record<string, Record<string, number>>
        coverage_gaps: Array<{
          type: string
          message: string
          impact: string
        }>
        recommendations: Array<{
          priority: string
          action: string
          command?: string
          reason?: string
        }>
      }
    }>('/rag/observability/risk-distribution/'),

  ragRunClassification: (params?: { limit?: number; force?: boolean }) =>
    api.post<{
      success: boolean
      classified_count: number
      results: {
        by_class: Record<string, number>
        by_risk: Record<string, number>
      }
    }>('/rag/observability/classify/', params || {}),
}

// Session 833: Blogs API for approval workflow
export interface Blog {
  id: string
  title: string
  category: string
  status: 'draft' | 'approved' | 'published'
  meta_description: string
  intro: string
  sections?: Array<{ title: string; content: string }>
  conclusion?: string
  tags: string[]
  full_text?: string
  tone: string
  word_count: number
  stats_snapshot?: Record<string, unknown>
  created_at: string
}

export interface BlogListResponse {
  success: boolean
  blogs: Blog[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  category_counts: Record<string, number>
  status_counts: Record<string, number>
  needs_enhancement_count?: number
}

export const blogsApi = {
  list: (params?: { page?: number; per_page?: number; search?: string; category?: string; status?: string }) =>
    api.get<BlogListResponse>('/v1/research/self-blog/list/', { params }),

  get: (blogId: string) =>
    api.get<{ success: boolean; blog: Blog }>(`/v1/research/self-blog/${blogId}/`),

  delete: (blogId: string) =>
    api.delete<{ success: boolean; message: string }>(`/v1/research/self-blog/${blogId}/delete/`),

  approve: (blogId: string) =>
    api.post<{ success: boolean; message: string; blog: { id: string; title: string; status: string } }>(
      `/v1/research/self-blog/${blogId}/approve/`
    ),

  publish: (blogId: string, force?: boolean) =>
    api.post<{ success: boolean; message: string; blog: { id: string; title: string; status: string } }>(
      `/v1/research/self-blog/${blogId}/publish/`,
      { force }
    ),

  related: (blogId: string, limit?: number) =>
    api.get<{
      success: boolean
      blog_id: string
      blog_title: string
      related: Array<{
        id: string
        title: string
        category: string
        status: string
        intro: string
        tags: string[]
        word_count: number
        created_at: string
        quality_score: number | null
        relatedness_score: number
        relatedness_reason: string
      }>
      count: number
    }>(`/v1/research/self-blog/${blogId}/related/`, { params: { limit: limit || 6 } }),
}

// =============================================================================
// Session 968: Request Log — circular buffer + logging interceptors
// =============================================================================

export interface RequestLogEntry {
  id: number
  method: string
  url: string
  status: number | null
  ms: number
  ts: number
  scope: string | null
  error: string | null
}

let nextId = 1
const requestLog: RequestLogEntry[] = []
const MAX_LOG = 200
const listeners: Set<(entries: RequestLogEntry[]) => void> = new Set()

function notify() {
  const snapshot = [...requestLog]
  listeners.forEach((fn) => fn(snapshot))
}

// Request interceptor — stamp metadata + read X-UI-Scope header
api.interceptors.request.use((config) => {
  const entry: RequestLogEntry = {
    id: nextId++,
    method: (config.method || 'get').toUpperCase(),
    url: `${config.baseURL || ''}${config.url || ''}`,
    status: null,
    ms: 0,
    ts: Date.now(),
    scope: (config.headers?.['X-UI-Scope'] as string) || null,
    error: null,
  }
  config.metadata = { requestId: entry.id, startTime: entry.ts }
  if (requestLog.length >= MAX_LOG) requestLog.shift()
  requestLog.push(entry)
  notify()
  return config
})

// Response interceptor — update entry with status + duration
api.interceptors.response.use(
  (resp) => {
    const meta = resp.config?.metadata
    if (meta) {
      const entry = requestLog.find((e) => e.id === meta.requestId)
      if (entry) {
        entry.status = resp.status
        entry.ms = Date.now() - meta.startTime
        notify()
      }
    }
    return resp
  },
  (err) => {
    const meta = err.config?.metadata
    if (meta) {
      const entry = requestLog.find((e) => e.id === meta.requestId)
      if (entry) {
        entry.status = err.response?.status ?? null
        entry.ms = Date.now() - meta.startTime
        entry.error = err.message || 'Unknown error'
        notify()
      }
    }
    return Promise.reject(err)
  }
)

export function getRequestLog(): RequestLogEntry[] {
  return [...requestLog]
}

export function subscribeRequestLog(fn: (entries: RequestLogEntry[]) => void): () => void {
  listeners.add(fn)
  return () => {
    listeners.delete(fn)
  }
}

export function clearRequestLog() {
  requestLog.length = 0
  notify()
}

// Session 1008: Campaign Orchestrator API
export const campaignApi = {
  list: (params?: { status?: string; limit?: number; offset?: number }) =>
    api.get('/campaigns/', { params }),
  create: (data: Record<string, unknown>) =>
    api.post('/campaigns/create/', data),
  detail: (id: string) => api.get(`/campaigns/${id}/`),
  start: (id: string) => api.post(`/campaigns/${id}/start/`),
  status: (id: string) => api.get(`/campaigns/${id}/status/`),
  deliverables: (id: string, params?: { type?: string; status?: string; platform?: string }) =>
    api.get(`/campaigns/${id}/deliverables/`, { params }),
  delete: (id: string) => api.delete(`/campaigns/${id}/delete/`),
  budgetTiers: () => api.get('/campaigns/budget-tiers/'),
}

// Session 1008: ToolCall Analytics / Audit API
export const auditApi = {
  toolCallRecords: (params?: { agent_name?: string; tool_name?: string; success?: boolean; page?: number }) =>
    api.get('/v1/tool-call-records/', { params }),
  toolCallAggregates: (params?: { agent_name?: string; tool_name?: string; date?: string; page?: number }) =>
    api.get('/v1/tool-call-aggregates/', { params }),
  decisionRecords: (params?: { agent_name?: string; decision_type?: string; was_successful?: boolean; page?: number }) =>
    api.get('/v1/decision-records/', { params }),
  signalClusters: (params?: { pattern_type?: string; status?: string; page?: number }) =>
    api.get('/v1/signal-clusters/', { params }),
}

// Session 1076: Executor Runs API
export const executorApi = {
  list: () => api.get('/v1/executor/runs/list/'),
  detail: (id: string) => api.get(`/v1/executor/runs/${id}/`),
  logs: (id: string) => api.get(`/v1/executor/runs/${id}/logs/`),
  diff: (id: string) => api.get(`/v1/executor/runs/${id}/diff/`),
  create: (data: { plan: unknown; summary?: string; conversation_id?: string }) =>
    api.post('/v1/executor/runs/', data),
  cancel: (id: string) => api.post(`/v1/executor/runs/${id}/cancel/`),
  approve: (id: string) => api.post(`/v1/executor/runs/${id}/approve/`),
  approveStep: (id: string, stepId: string) =>
    api.post(`/v1/executor/runs/${id}/approve-step/`, { step_id: stepId }),
}

// Session 1009: Deliverables Library API
export const deliverablesApi = {
  list: (params?: { type?: string; category?: string; agent?: string; saved?: boolean; template?: boolean; source?: string; search?: string; page?: number; per_page?: number }) =>
    api.get('/deliverables/', { params }),
  detail: (id: string) => api.get(`/deliverables/${id}/`),
  stats: () => api.get('/deliverables/stats/'),
  types: () => api.get('/deliverables/types/'),
  save: (id: string) => api.post(`/deliverables/${id}/save/`),
  unsave: (id: string) => api.post(`/deliverables/${id}/unsave/`),
  clone: (id: string) => api.post(`/deliverables/${id}/clone/`),
  templateize: (id: string) => api.post(`/deliverables/${id}/templateize/`),
  export: (id: string, format: string) => api.post(`/deliverables/${id}/export/`, { format }),
  recordEvent: (id: string, eventType: string, metadata?: Record<string, unknown>) =>
    api.post(`/deliverables/${id}/event/`, { event_type: eventType, metadata: metadata ?? {} }),
}

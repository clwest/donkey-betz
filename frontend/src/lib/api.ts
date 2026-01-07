import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
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
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
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
}

export const activityApi = {
  recent: (limit = 20, hours = 72) => api.get(`/recent-activity/?limit=${limit}&hours=${hours}`),
  learning: (limit = 20) => api.get(`/agent-learning/activity/?limit=${limit}`),
}

// Session 695: Dreams API for Dream Gallery Modal
export const dreamsApi = {
  list: (limit = 20) => api.get(`/agent-dreams/?limit=${limit}`),
  detail: (dreamId: string) => api.get(`/agent-dreams/${dreamId}/`),
  react: (dreamId: string, reaction: string) => api.post(`/agent-dreams/${dreamId}/react/`, { reaction }),
  markShown: (dreamIds: string[]) => api.post('/agent-dreams/mark-shown/', { dream_ids: dreamIds }),
}

// Session 695: Conversations API for Conversation Thread Viewer
export const conversationsApi = {
  list: (limit = 20) => api.get(`/agent-conversations/?limit=${limit}`),
  detail: (conversationId: string) => api.get(`/agent-conversations/${conversationId}/`),
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

// Session 696: Decisions API for Decision Insights Panel
export const decisionsApi = {
  list: (limit = 50) => api.get(`/boardroom/decisions/?limit=${limit}`),
  detail: (decisionId: string) => api.get(`/boardroom/decisions/${decisionId}/`),
  approve: (decisionId: string) => api.post(`/boardroom/decisions/${decisionId}/approve/`),
  reject: (decisionId: string, reason?: string) => api.post(`/boardroom/decisions/${decisionId}/reject/`, { reason }),
  promote: (decisionId: string) => api.post(`/boardroom/decisions/${decisionId}/promote/`),
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
}

export const spidersApi = {
  status: () => api.get('/v1/intelligence/spider-status/'),
  report: () => api.get('/spider-intelligence/report/'),
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
  stats: () => api.get('/agent-learning/stats/'),
  velocity: () => api.get('/learning/velocity/'),
}

export const contentApi = {
  // Gallery
  gallery: () => api.get('/v1/gallery/list/'),
  unifiedGallery: () => api.get('/v1/gallery/all/'),
  videoGallery: () => api.get('/v1/gallery/videos/'),
  toggleFavorite: (itemId: string) => api.post('/v1/gallery/toggle-favorite/', { item_id: itemId }),

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

export const assistantApi = {
  // Chat
  chat: (message: string, options?: { use_personal_assistant?: boolean }) =>
    api.post('/v1/assistant/chat/', { message, ...options }),

  // Voice
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

  // Context & Learning
  getContext: () => api.get('/assistant/context/'),
  getLearning: () => api.get('/assistant/learning/'),
  getPreferences: () => api.get('/assistant/preferences/'),
  getAttentionItems: () => api.get('/assistant/attention-items/'),
  getTaskProgress: () => api.get('/assistant/task-progress/'),

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

  // Wager Management
  placeBet: (data: { game_id: string; bet_type: string; pick: string; odds: number; stake: number }) =>
    api.post('/v1/betting/place/', data),
  logWager: (data: Record<string, unknown>) => api.post('/v1/betting/wager/', data),
  settleWager: (wagerId: string, result: string) => api.post(`/v1/betting/wagers/${wagerId}/settle/`, { result }),
  cancelWager: (wagerId: string) => api.post(`/v1/betting/wagers/${wagerId}/cancel/`),
}

export const userLearningApi = {
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
  create: (data: { topic: string; style?: string }) => api.post('/podcasts/create/', data),

  // Episode details
  status: (episodeId: string) => api.get(`/podcasts/${episodeId}/status/`),
  script: (episodeId: string) => api.get(`/podcasts/${episodeId}/script/`),
  delete: (episodeId: string) => api.delete(`/podcasts/${episodeId}/`),

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
  attentionStats: () => api.get('/human/attention/stats/'),
  decide: (itemId: string, decision: string, feedback?: string, confidence?: number) =>
    api.post(`/human/attention/${itemId}/decide/`, { decision, feedback, confidence }),
  defer: (itemId: string, remindAt: string) =>
    api.post(`/human/attention/${itemId}/defer/`, { remind_at: remindAt }),

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
export const llmRoutingApi = {
  // System status overview
  status: () => api.get('/v1/llm-routing/status/'),

  // List all 6 LLM providers with health info
  providers: () => api.get('/v1/llm-routing/providers/'),

  // List all 16 models with costs
  models: (params?: { provider?: string; capability?: string }) =>
    api.get('/v1/llm-routing/models/', { params }),

  // Get agent-model mappings (75 configs)
  agentConfigs: (params?: { agent?: string; model?: string }) =>
    api.get('/v1/llm-routing/agent-configs/', { params }),

  // Update agent config (requires auth)
  updateAgentConfig: (agentName: string, data: { model_id: string; reason?: string }) =>
    api.post(`/v1/llm-routing/agent-configs/${agentName}/`, data),

  // Call logs with filtering
  logs: (params?: {
    hours?: number
    agent?: string
    provider?: string
    success?: boolean
    limit?: number
    offset?: number
  }) => api.get('/v1/llm-routing/logs/', { params }),

  // Cost analytics dashboard
  costAnalytics: (hours?: number) =>
    api.get('/v1/llm-routing/cost-analytics/', { params: { hours } }),
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

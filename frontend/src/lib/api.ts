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

export const intelligenceApi = {
  status: () => api.get('/v1/intelligence/skynet/status/'),
  opportunities: () => api.get('/v1/intelligence/opportunities/'),
  predictions: () => api.get('/v1/intelligence/predictions/'),
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
  gates: () => api.get('/pilot-gates/dashboard/'),
  progress: () => api.get('/pilots/progress/'),
  gateDetail: (gateId: string) => api.get(`/pilot-gates/${gateId}/`),
  updateGateStatus: (gateId: string, status: string) =>
    api.patch(`/pilot-gates/${gateId}/status/`, { status }),
  approveAllItems: (gateId: string) =>
    api.post(`/pilot-gates/${gateId}/approve-all/`),
  startPilot: (gateId: string) =>
    api.post(`/pilot-gates/${gateId}/pilot/`),
}

export const experimentsApi = {
  list: () => api.get('/experiments/'),
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

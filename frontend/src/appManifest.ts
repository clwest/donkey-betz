/**
 * App Manifest — single source of truth for routes, studios, and capabilities.
 *
 * Consumed by:
 *  - The React app itself (e.g. nav generation)
 *  - generate-manifest.mjs (postbuild → __manifest.json)
 *  - Backend /api/app/manifest/ (RBAC-filtered)
 */

// ── Route definition ────────────────────────────────────────────────────────

export interface AppRoute {
  path: string;
  label: string;
  authRequired: boolean;
  roles?: string[];
  category: 'command' | 'studio' | 'intelligence' | 'domain' | 'reference' | 'admin' | 'auth';
  studioType?: 'image' | 'video';
}

export const APP_ROUTES: AppRoute[] = [
  // Auth
  { path: '/login', label: 'Login', authRequired: false, category: 'auth' },

  // Command
  { path: '/', label: 'Command Center', authRequired: true, category: 'command' },
  { path: '/dashboard', label: 'Dashboard', authRequired: true, category: 'command' },
  { path: '/workspace', label: 'Workspace', authRequired: true, category: 'command' },
  { path: '/boardroom', label: 'Boardroom', authRequired: true, category: 'command' },
  { path: '/governance', label: 'Governance', authRequired: true, category: 'command' },
  { path: '/platform', label: 'Platform', authRequired: true, category: 'command' },
  { path: '/billing', label: 'Billing', authRequired: true, category: 'command' },
  { path: '/analytics', label: 'Analytics', authRequired: true, category: 'command' },

  // Studio
  { path: '/image-studio', label: 'Image Studio', authRequired: true, category: 'studio', studioType: 'image' },
  { path: '/video-studio', label: 'Video Studio', authRequired: true, category: 'studio', studioType: 'video' },

  // Intelligence
  { path: '/intelligence', label: 'Intelligence', authRequired: true, category: 'intelligence' },
  { path: '/agents', label: 'Agents', authRequired: true, category: 'intelligence' },
  { path: '/advisors', label: 'Advisors', authRequired: true, category: 'intelligence' },
  { path: '/neural-orchestra', label: 'Neural Orchestra', authRequired: true, category: 'intelligence' },
  { path: '/conversation-contract', label: 'Conversation Contract', authRequired: true, category: 'intelligence' },
  { path: '/mythology-lab', label: 'Mythology Lab', authRequired: true, category: 'intelligence' },

  // Domain
  { path: '/content', label: 'Content', authRequired: true, category: 'domain' },
  { path: '/betting', label: 'Betting', authRequired: true, category: 'domain' },
  { path: '/stocks', label: 'Stock Intelligence', authRequired: true, category: 'domain' },
  { path: '/portfolio', label: 'Portfolio', authRequired: true, category: 'domain' },
  { path: '/legal', label: 'Legal', authRequired: true, category: 'domain' },
  { path: '/government', label: 'Government', authRequired: true, category: 'domain' },
  { path: '/documents', label: 'Documents', authRequired: true, category: 'domain' },
  { path: '/blog/:blogId', label: 'Blog Viewer', authRequired: true, category: 'domain' },

  // Reference
  { path: '/docs-index', label: 'Docs Index', authRequired: true, category: 'reference' },
  { path: '/how-it-works', label: 'How It Works', authRequired: true, category: 'reference' },

  // Admin
  { path: '/admin', label: 'Admin', authRequired: true, roles: ['admin'], category: 'admin' },
  { path: '/settings', label: 'Settings', authRequired: true, category: 'admin' },
  { path: '/profile', label: 'Profile', authRequired: true, category: 'admin' },
];

// ── Studio config ───────────────────────────────────────────────────────────

export interface StudioConfig {
  enabled: boolean;
  path: string;
  models: string[];
  endpoint: string;
}

export const STUDIO_CONFIG: Record<string, StudioConfig> = {
  image: {
    enabled: true,
    path: '/image-studio',
    models: ['stability-ai', 'dall-e-3', 'replicate'],
    endpoint: '/api/v1/gallery/',
  },
  video: {
    enabled: true,
    path: '/video-studio',
    models: ['runway-ml', 'ffmpeg-edit'],
    endpoint: '/api/v1/video/',
  },
  audio: {
    enabled: true,
    path: '',  // no dedicated page yet
    models: ['elevenlabs-tts'],
    endpoint: '/api/v1/audio/',
  },
};

// ── Capability flags ────────────────────────────────────────────────────────

export const APP_CAPABILITIES: Record<string, boolean> = {
  pa_chat: true,
  websocket: true,
  media_library: true,
  resolve_node: true,
  deliberation_pipeline: true,
  initiative_pipeline: true,
  spider_network: true,
  body_systems: true,
};

// ── Per-route API dependencies ──────────────────────────────────────────────

export interface ApiDependency {
  method: string;       // GET, POST, PUT, DELETE, PATCH
  path: string;         // e.g. '/api/human/attention/'
  toolSurface?: string; // e.g. 'boardroom_tool.list_attention'
  writes: boolean;      // true = mutation, false = read
}

export const API_DEPENDENCIES: Record<string, ApiDependency[]> = {
  '/boardroom': [
    { method: 'GET', path: '/api/human/attention/', toolSurface: 'boardroom_tool.list_attention', writes: false },
    { method: 'GET', path: '/api/human/attention/stats/', toolSurface: 'boardroom_tool.attention_stats', writes: false },
    { method: 'GET', path: '/api/boardroom/decisions/', toolSurface: 'boardroom_tool.list_decisions', writes: false },
    { method: 'GET', path: '/api/artifacts/needs-classification/', writes: false },
    { method: 'POST', path: '/api/human/attention/{itemId}/decide/', toolSurface: 'boardroom_tool.decide', writes: true },
    { method: 'POST', path: '/api/human/attention/bulk-decide/', toolSurface: 'boardroom_tool.bulk_decide', writes: true },
    { method: 'POST', path: '/api/artifacts/{artifactId}/classify/', writes: true },
    { method: 'POST', path: '/api/boardroom/decisions/{decisionId}/promote/', toolSurface: 'boardroom_tool.promote', writes: true },
    { method: 'POST', path: '/api/boardroom/decisions/{decisionId}/reject/', toolSurface: 'boardroom_tool.reject', writes: true },
    { method: 'POST', path: '/api/boardroom/decisions/bulk-promote/', writes: true },
    { method: 'POST', path: '/api/boardroom/decisions/bulk-reject/', writes: true },
    { method: 'POST', path: '/api/human/attention/', writes: true },
  ],
  '/governance': [
    { method: 'GET', path: '/api/platform/governance/', writes: false },
    { method: 'GET', path: '/api/self-healing/progress/', writes: false },
    { method: 'GET', path: '/api/platform/remediation/status/', writes: false },
    { method: 'GET', path: '/api/boardroom/decisions/', toolSurface: 'boardroom_tool.list_decisions', writes: false },
    { method: 'POST', path: '/api/platform/emergency-halt/', writes: true },
    { method: 'POST', path: '/api/platform/skin-lock/', writes: true },
    { method: 'POST', path: '/api/platform/actions/run-remediation/', writes: true },
  ],
  '/': [
    { method: 'GET', path: '/api/home/boot/', writes: false },
    { method: 'GET', path: '/api/body/vitals/', toolSurface: 'body_systems_tool.vitals', writes: false },
    { method: 'GET', path: '/api/human/attention/', toolSurface: 'boardroom_tool.list_attention', writes: false },
    { method: 'GET', path: '/api/orchestration/workflows/', writes: false },
    { method: 'GET', path: '/api/human/control/', writes: false },
    { method: 'GET', path: '/api/v1/agents/list/', toolSurface: 'agent_registry_tool.list', writes: false },
    { method: 'GET', path: '/api/assistant/learning/', writes: false },
    { method: 'GET', path: '/api/learning/velocity/', writes: false },
    { method: 'GET', path: '/api/preferences/', writes: false },
    { method: 'GET', path: '/api/assistant/attention-items/', writes: false },
    { method: 'GET', path: '/api/home/intelligence-desks/', writes: false },
    { method: 'GET', path: '/api/pa/conversations/', writes: false },
    { method: 'GET', path: '/api/pa/conversations/{conversationId}/', writes: false },
    { method: 'POST', path: '/api/home/trigger-desks/', writes: true },
    { method: 'POST', path: '/api/pa/chat/', toolSurface: 'pa_chat', writes: true },
    { method: 'POST', path: '/api/assistant/transcribe/', writes: true },
    { method: 'POST', path: '/api/assistant/voice/', writes: true },
    { method: 'POST', path: '/api/tts/speak/', writes: true },
    { method: 'POST', path: '/api/assistant/feedback/', writes: true },
  ],
  '/workspace': [
    { method: 'GET', path: '/api/workspaces/', toolSurface: 'initiative_tool.list_workspaces', writes: false },
    { method: 'GET', path: '/api/workspaces/active/', writes: false },
    { method: 'GET', path: '/api/workspaces/{id}/', writes: false },
  ],
  '/content': [
    { method: 'GET', path: '/api/v1/gallery/all/', toolSurface: 'media_tool.list', writes: false },
    { method: 'GET', path: '/api/content-calendar/', writes: false },
    { method: 'GET', path: '/api/creative-projects/', writes: false },
    { method: 'GET', path: '/api/v1/content/templates/', writes: false },
  ],
  '/betting': [
    { method: 'GET', path: '/api/v1/betting/stats/', toolSurface: 'betting_tool.stats', writes: false },
    { method: 'GET', path: '/api/v1/betting/wagers/', toolSurface: 'betting_tool.list_wagers', writes: false },
    { method: 'GET', path: '/api/v1/betting/arbitrage/scan/', toolSurface: 'betting_tool.arbitrage', writes: false },
    { method: 'GET', path: '/api/v1/sports/live-odds-scores/', writes: false },
    { method: 'GET', path: '/api/v1/odds/bankroll/stats/', writes: false },
    { method: 'GET', path: '/api/v1/odds/markets/', writes: false },
    { method: 'GET', path: '/api/v1/betting/line-movement/', writes: false },
    { method: 'GET', path: '/api/v1/betting/todays-games/', writes: false },
    { method: 'GET', path: '/api/v1/betting/brief/', toolSurface: 'betting_tool.brief', writes: false },
    { method: 'GET', path: '/api/v1/betting/sharp-action/', writes: false },
    { method: 'GET', path: '/api/v1/betting/track-record/', writes: false },
    { method: 'POST', path: '/api/v1/betting/quick-pick/', writes: true },
    { method: 'POST', path: '/api/v1/betting/place/', writes: true },
    { method: 'POST', path: '/api/v1/betting/wager/', toolSurface: 'betting_tool.log_wager', writes: true },
  ],
  '/stocks': [
    { method: 'GET', path: '/api/stocks/hub/', toolSurface: 'stock_tool.hub', writes: false },
    { method: 'GET', path: '/api/stocks/dashboard/', toolSurface: 'stock_tool.dashboard', writes: false },
    { method: 'GET', path: '/api/stocks/briefs/', toolSurface: 'stock_tool.briefs', writes: false },
    { method: 'GET', path: '/api/stocks/briefs/{id}/', writes: false },
    { method: 'GET', path: '/api/stocks/alerts/', toolSurface: 'stock_tool.alerts', writes: false },
    { method: 'GET', path: '/api/stocks/predictions/', toolSurface: 'stock_tool.predictions', writes: false },
    { method: 'GET', path: '/api/stocks/sec-filings/', writes: false },
    { method: 'GET', path: '/api/stocks/ticker/{symbol}/', writes: false },
  ],
  // Remaining routes — empty for now; populated incrementally
  '/login': [],
  '/dashboard': [],
  '/platform': [],
  '/billing': [],
  '/analytics': [],
  '/image-studio': [],
  '/video-studio': [],
  '/intelligence': [],
  '/agents': [],
  '/advisors': [],
  '/neural-orchestra': [],
  '/conversation-contract': [],
  '/mythology-lab': [],
  '/portfolio': [],
  '/legal': [],
  '/government': [],
  '/documents': [],
  '/blog/:blogId': [],
  '/docs-index': [],
  '/how-it-works': [],
  '/admin': [],
  '/settings': [],
  '/profile': [],
};

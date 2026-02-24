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

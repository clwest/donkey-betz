import type { ComponentType } from 'react';
import React from 'react';
import { Text, View, StyleSheet } from 'react-native';

// ── Safe import helper ──────────────────────────────────────────────────────
// Wraps a module-level require so that if any screen module fails to load
// (e.g. missing native module, syntax error, broken dependency), the rest
// of the registry is still usable. Failed screens get a placeholder that
// shows the error instead of crashing the entire app.

const _placeholderStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  icon: {
    color: '#ef4444',
    fontSize: 36,
    fontWeight: '800',
    width: 56,
    height: 56,
    lineHeight: 56,
    textAlign: 'center',
    borderWidth: 3,
    borderColor: '#ef4444',
    borderRadius: 28,
    marginBottom: 16,
  },
  title: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 8,
  },
  detail: {
    color: '#9ca3af',
    fontSize: 13,
    textAlign: 'center',
  },
});

function _makePlaceholder(screenPath: string, error: unknown): ComponentType<any> {
  const msg = error instanceof Error ? error.message : String(error);
  const Placeholder = () =>
    React.createElement(View, { style: _placeholderStyles.container },
      React.createElement(Text, { style: _placeholderStyles.icon }, '!'),
      React.createElement(Text, { style: _placeholderStyles.title }, `Failed to load ${screenPath}`),
      React.createElement(Text, { style: _placeholderStyles.detail }, msg),
    );
  Placeholder.displayName = `FailedScreen(${screenPath})`;
  return Placeholder;
}

function safeRequire(importFn: () => ComponentType<any>, screenPath: string): ComponentType<any> {
  try {
    return importFn();
  } catch (e) {
    console.error(`[screenRegistry] Failed to import ${screenPath}:`, e);
    return _makePlaceholder(screenPath, e);
  }
}

// ── Screen imports (each wrapped for safety) ────────────────────────────────

const CommandCenterScreen = safeRequire(() => require('../screens/CommandCenterScreen').default, '/');
const DashboardScreen = safeRequire(() => require('../screens/DashboardScreen').default, '/dashboard');
const BoardroomHomeScreen = safeRequire(() => require('../screens/boardroom/BoardroomHomeScreen').default, '/boardroom');
const GovernanceHomeScreen = safeRequire(() => require('../screens/governance/GovernanceHomeScreen').default, '/governance');
const InitiativesHomeScreen = safeRequire(() => require('../screens/initiatives/InitiativesHomeScreen').default, '/initiatives');
const AgentsScreen = safeRequire(() => require('../screens/AgentsScreen').default, '/agents');
const MediaScreen = safeRequire(() => require('../screens/MediaScreen').default, '/media');
const DiagnosticsScreen = safeRequire(() => require('../screens/DiagnosticsScreen').default, '/diagnostics');
const DeliberationHomeScreen = safeRequire(() => require('../screens/deliberation/DeliberationHomeScreen').default, '/content');
const WorkspaceScreen = safeRequire(() => require('../screens/WorkspaceScreen').default, '/workspace');
const IntelligenceScreen = safeRequire(() => require('../screens/IntelligenceScreen').default, '/intelligence');
const SettingsScreen = safeRequire(() => require('../screens/settings/SettingsScreen').default, '/settings');
const BettingScreen = safeRequire(() => require('../screens/BettingScreen').default, '/betting');
const StocksScreen = safeRequire(() => require('../screens/StocksScreen').default, '/stocks');
const PortfolioScreen = safeRequire(() => require('../screens/PortfolioScreen').default, '/portfolio');
const CodeRunnerScreen = safeRequire(() => require('../screens/CodeRunnerScreen').default, '/code-runner');

// ── Registry ─────────────────────────────────────────────────────────────────
// Maps manifest route paths -> RN screen components.
// A route only appears in navigation if it exists in BOTH the manifest AND
// this registry. This means:
//   - Removing a route from the manifest hides it automatically
//   - Adding a route to the manifest without a registry entry is a no-op
//     (placeholder can be added later)

export interface ScreenEntry {
  component: ComponentType<any>;
  /** Override manifest label for nav display */
  label?: string;
  /** Icon name (for drawer/tab) */
  icon?: string;
}

const SCREEN_REGISTRY: Record<string, ScreenEntry> = {
  '/': {
    component: CommandCenterScreen,
    icon: 'message-square',
  },
  '/dashboard': {
    component: DashboardScreen,
    icon: 'bar-chart-2',
  },
  '/boardroom': {
    component: BoardroomHomeScreen,
    icon: 'shield',
  },
  '/governance': {
    component: GovernanceHomeScreen,
    icon: 'lock',
  },
  '/workspace': {
    component: WorkspaceScreen,
    icon: 'briefcase',
  },
  '/content': {
    component: DeliberationHomeScreen,
    label: 'Deliberation',
    icon: 'file-text',
  },
  '/betting': {
    component: BettingScreen,
    icon: 'trending-up',
  },
  '/stocks': {
    component: StocksScreen,
    icon: 'activity',
  },
  '/initiatives': {
    component: InitiativesHomeScreen,
    icon: 'target',
  },
  '/intelligence': {
    component: IntelligenceScreen,
    icon: 'cpu',
  },
  '/agents': {
    component: AgentsScreen,
    icon: 'users',
  },
  '/media': {
    component: MediaScreen,
    icon: 'image',
  },
  '/portfolio': {
    component: PortfolioScreen,
    icon: 'dollar-sign',
  },
  '/settings': {
    component: SettingsScreen,
    icon: 'settings',
  },
  '/diagnostics': {
    component: DiagnosticsScreen,
    icon: 'info',
  },
  '/code-runner': {
    component: CodeRunnerScreen,
    icon: 'terminal',
  },
};

export default SCREEN_REGISTRY;

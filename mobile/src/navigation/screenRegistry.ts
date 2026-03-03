import type { ComponentType } from 'react';

// Placeholder screens — replaced by real implementations in later PRs
import PlaceholderScreen from '../screens/PlaceholderScreen';
import CommandCenterScreen from '../screens/CommandCenterScreen';
import DashboardScreen from '../screens/DashboardScreen';
import BoardroomHomeScreen from '../screens/boardroom/BoardroomHomeScreen';
import GovernanceHomeScreen from '../screens/governance/GovernanceHomeScreen';
import InitiativesHomeScreen from '../screens/initiatives/InitiativesHomeScreen';
import AgentsScreen from '../screens/AgentsScreen';
import MediaScreen from '../screens/MediaScreen';
import DiagnosticsScreen from '../screens/DiagnosticsScreen';
import DeliberationHomeScreen from '../screens/deliberation/DeliberationHomeScreen';

// ── Registry ─────────────────────────────────────────────────────────────────
// Maps manifest route paths → RN screen components.
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
    component: PlaceholderScreen,
    icon: 'briefcase',
  },
  '/content': {
    component: DeliberationHomeScreen,
    label: 'Deliberation',
    icon: 'file-text',
  },
  '/betting': {
    component: PlaceholderScreen,
    icon: 'trending-up',
  },
  '/stocks': {
    component: PlaceholderScreen,
    icon: 'activity',
  },
  '/initiatives': {
    component: InitiativesHomeScreen,
    icon: 'target',
  },
  '/intelligence': {
    component: PlaceholderScreen,
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
    component: PlaceholderScreen,
    icon: 'dollar-sign',
  },
  '/settings': {
    component: PlaceholderScreen,
    icon: 'settings',
  },
  '/diagnostics': {
    component: DiagnosticsScreen,
    icon: 'info',
  },
};

export default SCREEN_REGISTRY;

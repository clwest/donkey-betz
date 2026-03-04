import type { ComponentType } from 'react';

import CommandCenterScreen from '../screens/CommandCenterScreen';
import DashboardScreen from '../screens/DashboardScreen';
import BoardroomHomeScreen from '../screens/boardroom/BoardroomHomeScreen';
import GovernanceHomeScreen from '../screens/governance/GovernanceHomeScreen';
import InitiativesHomeScreen from '../screens/initiatives/InitiativesHomeScreen';
import AgentsScreen from '../screens/AgentsScreen';
import MediaScreen from '../screens/MediaScreen';
import DiagnosticsScreen from '../screens/DiagnosticsScreen';
import DeliberationHomeScreen from '../screens/deliberation/DeliberationHomeScreen';
import WorkspaceScreen from '../screens/WorkspaceScreen';
import IntelligenceScreen from '../screens/IntelligenceScreen';
import SettingsScreen from '../screens/settings/SettingsScreen';
import BettingScreen from '../screens/BettingScreen';
import StocksScreen from '../screens/StocksScreen';
import PortfolioScreen from '../screens/PortfolioScreen';

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
};

export default SCREEN_REGISTRY;

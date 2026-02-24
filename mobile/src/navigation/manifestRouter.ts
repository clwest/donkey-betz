import type { ManifestRoute } from '../api/manifest';
import SCREEN_REGISTRY, { type ScreenEntry } from './screenRegistry';

// ── Resolved screen entry (manifest route + screen component) ───────────────

export interface ResolvedScreen {
  path: string;
  label: string;
  category: string;
  icon?: string;
  entry: ScreenEntry;
}

// ── Category display order for drawer sections ──────────────────────────────

const CATEGORY_ORDER = [
  'command',
  'domain',
  'intelligence',
  'studio',
  'reference',
  'admin',
];

// ── Resolve manifest routes to screen entries ───────────────────────────────

export function resolveScreens(routes: ManifestRoute[]): ResolvedScreen[] {
  const resolved: ResolvedScreen[] = [];

  for (const route of routes) {
    const entry = SCREEN_REGISTRY[route.path];
    if (!entry) continue; // No screen registered for this route — skip

    resolved.push({
      path: route.path,
      label: entry.label ?? route.label,
      category: route.category,
      icon: entry.icon,
      entry,
    });
  }

  // Sort by category order, then by original manifest order within category
  resolved.sort((a, b) => {
    const ai = CATEGORY_ORDER.indexOf(a.category);
    const bi = CATEGORY_ORDER.indexOf(b.category);
    const aOrder = ai === -1 ? 999 : ai;
    const bOrder = bi === -1 ? 999 : bi;
    return aOrder - bOrder;
  });

  return resolved;
}

// ── Group screens by category for drawer sections ───────────────────────────

export function groupByCategory(
  screens: ResolvedScreen[],
): Map<string, ResolvedScreen[]> {
  const groups = new Map<string, ResolvedScreen[]>();
  for (const screen of screens) {
    const list = groups.get(screen.category) ?? [];
    list.push(screen);
    groups.set(screen.category, list);
  }
  return groups;
}

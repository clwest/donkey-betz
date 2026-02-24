import http from './http';

// ── Types matching backend response ──────────────────────────────────────────

export interface ManifestRoute {
  path: string;
  label: string;
  authRequired: boolean;
  roles?: string[];
  category: string;
  studioType?: string;
}

export interface ApiDependency {
  method: string;
  path: string;
  toolSurface?: string;
  writes: boolean;
}

export interface StudioConfig {
  enabled: boolean;
  path: string;
  models: string[];
  endpoint: string;
}

export interface Manifest {
  build_sha: string;
  build_timestamp: string | null;
  env: string;
  route_count: number;
  routes: ManifestRoute[];
  studios: Record<string, StudioConfig>;
  capabilities: Record<string, boolean>;
  api_dependencies: Record<string, ApiDependency[]>;
  user_role: string;
  user_id: string;
}

// ── Fetch ────────────────────────────────────────────────────────────────────

export async function getManifest(): Promise<Manifest> {
  const { data } = await http.get<Manifest>('/app/manifest/');
  return data;
}

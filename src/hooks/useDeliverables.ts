/**
 * useDeliverables hook
 *
 * Default filter includes BOTH 'ready' and 'completed' statuses so newly
 * created deliverables (status=completed) are visible immediately.
 * Pass `status: ['ready']` to restrict to ready-only (acceptance criteria #3).
 */

import { useState, useCallback } from 'react';

export type DeliverableStatus = 'ready' | 'completed' | 'draft' | 'all';

export interface DeliverableFilters {
  /** Default: ['ready','completed'] — pass ['ready'] for ready-only, or 'all' */
  status?: DeliverableStatus | DeliverableStatus[];
  search?: string;
  category?: string;
}

export interface Deliverable {
  id: string;
  title: string;
  status: DeliverableStatus;
  category: string;
  created_at: string;
}

/** Statuses shown by default — satisfies AC #1 (completed visible on load) */
export const DEFAULT_STATUSES: DeliverableStatus[] = ['ready', 'completed'];

/**
 * Build query-string params for the deliverables API endpoint.
 * Ensures search works across ALL requested statuses (AC #2).
 * Does NOT implicitly exclude any category (AC #4).
 */
export function buildDeliverableParams(filters: DeliverableFilters): Record<string, string> {
  const params: Record<string, string> = {};

  // Resolve statuses
  const statuses: DeliverableStatus[] = (() => {
    if (!filters.status || filters.status === 'all') return [];
    if (Array.isArray(filters.status)) return filters.status;
    return [filters.status];
  })();

  // Send comma-separated list; empty means no status filter (== all)
  if (statuses.length > 0) {
    params['status'] = statuses.join(',');
  }

  if (filters.search && filters.search.trim() !== '') {
    params['search'] = filters.search.trim();
  }

  // category is passed through as-is — no implicit exclusions
  if (filters.category && filters.category.trim() !== '') {
    params['category'] = filters.category.trim();
  }

  return params;
}

/**
 * Fetch deliverables from the API.
 */
export async function fetchDeliverables(
  baseUrl: string,
  filters: DeliverableFilters = {}
): Promise<Deliverable[]> {
  const params = buildDeliverableParams({
    status: DEFAULT_STATUSES,
    ...filters,
  });

  const qs = new URLSearchParams(params).toString();
  const url = qs ? `${baseUrl}?${qs}` : baseUrl;

  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Deliverables API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  // Support both { results: [...] } and plain array shapes
  return Array.isArray(data) ? data : (data.results ?? []);
}

/**
 * React hook for deliverables with default filters.
 * Usage:
 *   const { deliverables, setFilters, load, loading } = useDeliverables('/api/deliverables/');
 */
export function useDeliverables(baseUrl: string, initialFilters: DeliverableFilters = {}) {
  const [filters, setFilters] = useState<DeliverableFilters>({
    status: DEFAULT_STATUSES,
    ...initialFilters,
  });
  const [deliverables, setDeliverables] = useState<Deliverable[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (overrideFilters?: DeliverableFilters) => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchDeliverables(baseUrl, overrideFilters ?? filters);
        setDeliverables(result);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    },
    [baseUrl, filters]
  );

  return { deliverables, filters, setFilters, loading, error, load };
}

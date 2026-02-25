import http from './http';
import type {
  ActionItemsResponse,
  InitiativeActionItem,
  InitiativeListItem,
  InitiativeListResponse,
  InitiativeStatus,
} from './types/initiatives';

// ── List initiatives ────────────────────────────────────────────────────────

export async function listInitiatives(params?: {
  status?: InitiativeStatus | 'all';
  limit?: number;
  sort?: 'priority' | 'updated';
}): Promise<InitiativeListResponse> {
  const { data } = await http.get<InitiativeListResponse>('/initiatives/', { params });
  return data;
}

// ── Initiative details (uses list endpoint with single-item filter) ─────────

export async function getInitiative(id: string): Promise<InitiativeListItem> {
  // Backend doesn't have a dedicated detail endpoint — fetch from list
  // and filter client-side. The list endpoint returns full details per item.
  const { data } = await http.get<InitiativeListResponse>('/initiatives/', {
    params: { limit: 500 },
  });
  const item = data.initiatives.find((i) => i.id === id);
  if (!item) throw new Error('Initiative not found');
  return item;
}

// ── Action items ────────────────────────────────────────────────────────────

export async function getActionItems(
  initiativeId: string,
  params?: { status?: string; priority?: string },
): Promise<ActionItemsResponse> {
  const { data } = await http.get<ActionItemsResponse>(
    `/initiatives/${initiativeId}/action-items/`,
    { params },
  );
  return data;
}

// ── Update action item (start / complete / block) ───────────────────────────

export async function updateActionItem(
  itemId: string,
  updates: Partial<Pick<InitiativeActionItem, 'status' | 'priority' | 'completion_notes' | 'blocked_reason'>>,
): Promise<{ success: boolean; action_item: Partial<InitiativeActionItem> }> {
  const { data } = await http.post(`/action-items/${itemId}/`, updates);
  return data;
}

// ── Stage document ──────────────────────────────────────────────────────────

export async function getStageDocument(
  documentId: string,
): Promise<{ id: string; title: string; content: string; full_text?: string }> {
  const { data } = await http.get(`/blogs/${documentId}/`);
  return data;
}

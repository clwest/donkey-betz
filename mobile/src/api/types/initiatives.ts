// ── Initiative Pipeline Types ────────────────────────────────────────────────
// Matches backend response shapes from core/views_research_demo.py

export type InitiativeStatus = 'TRIAGE' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'ARCHIVED' | 'CANCELLED';

export interface InitiativeStage {
  status: string; // PENDING | DRAFT | IN_REVIEW | APPROVED | REJECTED | SUPERSEDED | BLOCKED
  stage_name: string;
  document_id: string | null;
  approved_at: string | null;
}

export interface InitiativeListItem {
  id: string;
  human_id: string | null;
  name: string;
  description: string;
  status: InitiativeStatus;
  current_stage: number;
  completion_percentage: number;
  approved_percentage: number;
  stages_with_work: number;
  stages: Record<string, InitiativeStage>; // { "1": {...}, "2": {...}, ... }
  health: 'healthy' | 'stale' | 'blocked';
  health_issues: string[];
  days_since_update: number;
  purpose: string;
  purpose_display: string;
  program: string;
  program_display: string;
  priority_score: number;
  priority_level: 'critical' | 'high' | 'medium' | 'low';
  impact_score: number;
  urgency: number;
  confidence: number;
  revenue_potential: number;
  created_at: string;
  updated_at: string;
}

export interface InitiativeListResponse {
  success: boolean;
  count: number;
  total_count: number;
  initiatives: InitiativeListItem[];
  stats: {
    total: number;
    active: number;
    completed: number;
    archived: number;
    on_hold: number;
    by_program: Record<string, number>;
    by_purpose: Record<string, number>;
    by_priority: Record<string, number>;
  };
}

export type ActionItemStatus = 'pending' | 'in_progress' | 'completed' | 'blocked' | 'cancelled';
export type ActionItemPriority = 'critical' | 'high' | 'medium' | 'low';

export interface InitiativeActionItem {
  id: string;
  title: string;
  description: string;
  assigned_agent: string;
  assigned_user_id: string | null;
  timeline_text: string;
  due_date: string | null;
  estimated_hours: number | null;
  status: ActionItemStatus;
  priority: ActionItemPriority;
  started_at: string | null;
  completed_at: string | null;
  completed_by: string;
  completion_notes: string;
  blocked_reason: string;
  is_overdue: boolean;
  days_until_due: number | null;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface ActionItemsResponse {
  success: boolean;
  initiative_id: string;
  initiative_name: string;
  count: number;
  stats: {
    total: number;
    pending: number;
    in_progress: number;
    completed: number;
    blocked: number;
    completion_rate: number;
  };
  action_items: InitiativeActionItem[];
}

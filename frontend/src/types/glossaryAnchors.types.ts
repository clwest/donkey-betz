/**
 * TypeScript types for Glossary Anchors System
 * Semantic anchor management for improved RAG retrieval precision
 */

export interface GlossaryAnchor {
  id: string;
  term: string;
  variants: string[];
  description: string;
  anchor_type: 'technical' | 'domain' | 'process' | 'feature' | 'methodology' | 'system' | 'user_term';
  domain_context: string;
  source_evidence: {
    documents?: string[];
    queries?: string[];
    fallback_triggers?: string[];
    user_feedback?: string[];
  };
  confidence: 'high' | 'medium' | 'low';
  fallback_score: number;
  related_memories: string[]; // Memory IDs
  query_matches: number;
  retrieval_improvements: number;
  last_matched: string | null;
  is_active: boolean;
  user: string | null; // User ID for user-specific anchors
  created_by: string;
  created_at: string;
  updated_at: string;
  effectiveness_score?: number;
}

export interface AnchorCluster {
  id: string;
  name: string;
  description: string;
  anchors: string[]; // Anchor IDs
  domain_focus: string;
  semantic_coherence_score: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AnchorPerformanceLog {
  id: string;
  anchor_id: string;
  query_text: string;
  query_hash: string;
  impact_type: 'improved_recall' | 'reduced_fallback' | 'enhanced_precision' | 'semantic_match' | 'false_positive';
  before_score: number;
  after_score: number;
  improvement_delta: number;
  retrieved_memories: string[];
  user: string;
  created_at: string;
}

export interface AnchorAnalytics {
  total_anchors: number;
  active_anchors: number;
  user_anchors: number;
  global_anchors: number;
  avg_effectiveness_score: number;
  total_query_matches: number;
  total_improvements: number;
  anchor_types_breakdown: Record<string, number>;
  confidence_distribution: Record<'high' | 'medium' | 'low', number>;
  recent_performance: AnchorPerformanceLog[];
  top_performing_anchors: Array<{
    anchor: GlossaryAnchor;
    performance_score: number;
    recent_matches: number;
  }>;
}

export interface AnchorRecommendation {
  suggested_term: string;
  suggested_variants: string[];
  confidence: number;
  reasoning: string;
  source_queries: string[];
  potential_impact: 'high' | 'medium' | 'low';
  domain_context: string;
  anchor_type: GlossaryAnchor['anchor_type'];
}

export interface CreateAnchorRequest {
  term: string;
  variants?: string[];
  description: string;
  anchor_type: GlossaryAnchor['anchor_type'];
  domain_context?: string;
  source_evidence?: GlossaryAnchor['source_evidence'];
  confidence?: 'high' | 'medium' | 'low';
  is_active?: boolean;
}

export interface UpdateAnchorRequest extends Partial<CreateAnchorRequest> {
  id: string;
}

export interface AnchorSearchFilters {
  anchor_type?: string;
  confidence?: string;
  domain_context?: string;
  is_active?: boolean;
  user_only?: boolean;
  search_term?: string;
  min_effectiveness?: number;
  sort_by?: 'effectiveness' | 'matches' | 'recent' | 'alphabetical';
  limit?: number;
  offset?: number;
}

export interface BulkAnchorOperation {
  action: 'activate' | 'deactivate' | 'delete' | 'update_confidence' | 'assign_domain';
  anchor_ids: string[];
  parameters?: {
    confidence?: 'high' | 'medium' | 'low';
    domain_context?: string;
    is_active?: boolean;
  };
}

export interface AnchorValidationResult {
  anchor_id: string;
  is_valid: boolean;
  issues: Array<{
    type: 'duplicate' | 'low_confidence' | 'no_matches' | 'conflicting_variants';
    severity: 'warning' | 'error';
    description: string;
    suggestion?: string;
  }>;
  recommendations: AnchorRecommendation[];
}

export interface MemoryRetrievalTest {
  query: string;
  expected_memories: string[];
  actual_memories: string[];
  matching_anchors: string[];
  precision_score: number;
  recall_score: number;
  f1_score: number;
  improvement_suggestions: string[];
}
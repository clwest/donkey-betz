/**
 * TypeScript types for Prompt Diagnostics System
 * Provides type safety for prompt analysis, optimization, and template management
 */

export interface PromptIssue {
  type: 'redundancy' | 'ambiguity' | 'complexity' | 'length' | 'formatting' | 'clarity';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  location?: string;
  suggestion: string;
  confidence: number;
  token_impact?: number;
}

export interface QuickWin {
  description: string;
  before: string;
  after: string;
  token_savings: number;
  clarity_gain: number;
  confidence: number;
  priority: 'low' | 'medium' | 'high';
}

export interface ReadabilityMetrics {
  flesch_kincaid: number;
  grade_level: number;
  sentence_count: number;
  word_count: number;
  avg_sentence_length: number;
}

export interface DiagnosticMetric {
  type: 'token_count' | 'readability' | 'structure' | 'clarity' | 'consistency';
  name: string;
  value_before: number;
  value_after: number;
  improvement_percentage: number;
  unit: 'score' | 'count' | 'percentage';
  confidence: number;
}

export interface RiskAssessment {
  overall_risk: 'low' | 'medium' | 'high';
  semantic_preservation: number;
  context_retention: number;
  potential_issues: string[];
  mitigation_strategies: string[];
  confidence_level: number;
}

export interface PromptAnalysisResult {
  analysis_id: string;
  status: 'analyzing' | 'completed' | 'failed';
  original_prompt: string;
  optimized_prompt: string;
  metrics: {
    original_tokens: number;
    optimized_tokens: number;
    token_reduction: number;
    token_reduction_percentage: number;
    readability_before: ReadabilityMetrics;
    readability_after: ReadabilityMetrics;
    structure_score: number;
    clarity_score: number;
    consistency_score: number;
    detailed_metrics?: DiagnosticMetric[];
  };
  issues: PromptIssue[];
  quick_wins: QuickWin[];
  risk_assessment: RiskAssessment;
  improvements_summary: string;
  implementation_notes: string;
  testing_recommendations: string[];
  rollback_strategy: string;
}

export interface PromptAnalysisRequest {
  prompt: string;
  title?: string;
  prompt_type?: 'user' | 'system' | 'assistant' | 'function';
  target_model?: string;
  optimization_goals?: Array<'reduce_tokens' | 'improve_clarity' | 'enhance_structure' | 'maintain_context'>;
  force_reanalyze?: boolean;
}

export interface PromptAnalysisSummary {
  id: string;
  title: string;
  prompt_type: string;
  status: 'analyzing' | 'completed' | 'failed';
  original_token_count: number;
  optimized_token_count: number;
  token_reduction_percentage: number;
  clarity_score: number;
  structure_score: number;
  issues_count: number;
  quick_wins_count: number;
  created_at: string;
  analyzed_at: string | null;
}

export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  category: 'general' | 'creative' | 'analytical' | 'technical' | 'conversational' | 'system';
  template_text: string;
  variables: string[];
  token_count: number;
  clarity_score: number;
  effectiveness_rating: number;
  usage_count: number;
  is_public: boolean;
  is_verified: boolean;
  is_mine: boolean;
  created_at: string;
  last_used_at: string | null;
}

export interface OptimizationSession {
  session_id: string;
  session_name: string;
  total_prompts: number;
  completed_prompts: number;
  failed_prompts: number;
  total_token_savings: number;
  average_improvement: number;
  analyses: Array<{
    id: string;
    title: string;
    status: string;
    token_reduction: number;
    issues_count: number;
  }>;
}

export interface DiagnosticsDashboardData {
  period: {
    days: number;
    start_date: string;
    end_date: string;
  };
  overview: {
    total_analyses: number;
    completed_analyses: number;
    success_rate: number;
    total_token_savings: number;
    avg_token_reduction: number;
    avg_clarity_score: number;
    templates_created: number;
  };
  issues_breakdown: Record<string, number>;
  prompt_types: Array<{
    prompt_type: string;
    count: number;
  }>;
  recent_analyses: Array<{
    id: string;
    title: string;
    status: string;
    token_reduction_percentage: number;
    created_at: string;
  }>;
  performance_metrics: {
    cost_savings_estimate: string;
    efficiency_gain: string;
    quality_improvement: 'Low' | 'Medium' | 'High';
  };
}

export interface QuickAnalysisResult {
  token_count: number;
  readability_score: number;
  grade_level: number;
  issues_count: number;
  critical_issues: number;
  recommendations: string[];
  complexity_rating: 'Low' | 'Medium' | 'High';
}

export interface BatchAnalysisRequest {
  prompts: Array<{
    text: string;
    title?: string;
    type?: 'user' | 'system' | 'assistant' | 'function';
  }>;
  session_name?: string;
  optimization_goals?: Array<'reduce_tokens' | 'improve_clarity' | 'enhance_structure' | 'maintain_context'>;
  target_model?: string;
}
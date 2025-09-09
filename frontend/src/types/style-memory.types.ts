// Image Style Memory Agent Types

export type InteractionType = 'love' | 'rate_5' | 'rate_4' | 'rate_3' | 'rate_2' | 'rate_1' | 'save' | 'like' | 'generate_similar';

export type VariationType = 'subtle' | 'moderate' | 'creative';

export type PatternType = 'color_preference' | 'style_combination' | 'parameter_sweet_spot' | 'subject_preference';

export interface StyleMemory {
  id: string;
  user_id: string;
  content_id: string;
  interaction_type: InteractionType;
  interaction_strength: number;
  style_name?: string;
  prompt_text: string;
  prompt_embedding?: number[];
  model_used: string;
  cfg_scale: number;
  steps: number;
  seed?: number;
  size: string;
  dominant_colors: string[];
  style_tags: string[];
  mood_descriptors: string[];
  confidence_score: number;
  usage_count: number;
  success_rate: number;
  notes?: string;
  created_at: Date;
  last_used?: Date;
}

export interface StyleLineage {
  id: string;
  parent_content_id: string;
  child_content_id: string;
  user_id: string;
  relationship_type: 'variation' | 'evolution' | 'remix';
  changes_made: Record<string, any>;
  similarity_score: number;
  improvement_score: number;
  generation_number: number;
  created_at: Date;
}

export interface StylePattern {
  id: string;
  user_id: string;
  pattern_type: PatternType;
  pattern_name: string;
  pattern_description: string;
  pattern_data: Record<string, any>;
  confidence: number;
  occurrence_count: number;
  success_rate: number;
  optimal_parameters: Record<string, any>;
  avoid_parameters: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}

export interface StyleSuggestion {
  id: string;
  user_id: string;
  suggestion_type: 'next_step' | 'parameter_tweak' | 'fusion' | 'creative_exploration';
  title: string;
  description: string;
  reasoning: string;
  suggested_prompt: string;
  suggested_parameters: Record<string, any>;
  confidence: number;
  was_used: boolean;
  based_on_patterns: string[];
  based_on_memories: string[];
  created_at: Date;
}

export interface StyleInsights {
  total_memories: number;
  loved_count: number;
  favorite_styles: Array<{ style: string; count: number }>;
  preferred_cfg: number;
  preferred_steps: number;
  color_preferences: string[];
  top_memories: StyleMemory[];
  patterns: StylePattern[];
  suggestions: StyleSuggestion[];
  evolution: {
    trending_up: string[];
    trending_down: string[];
  };
}

export interface VariationRequest {
  base_content_id: string;
  variation_type: VariationType;
  prompt_override?: string;
  use_suggestions?: boolean;
}

export interface VariationResponse {
  success: boolean;
  content: {
    id: string;
    url: string;
    prompt: string;
    parameters: Record<string, any>;
  };
  variation_params: {
    cfg_scale: number;
    steps: number;
    changes_made: Record<string, any>;
  };
  lineage_id: string;
}

export interface StyleRecipe {
  style: string;
  prompt_template: string;
  cfg_scale: number;
  steps: number;
  model: string;
  size: string;
  negative_prompt?: string;
  style_strength: number;
}

export interface LineageTree {
  content: any;
  ancestors: Array<{
    content_id: string;
    generation: number;
    relationship: string;
    similarity: number;
  }>;
  descendants: Array<{
    content_id: string;
    generation: number;
    relationship: string;
    similarity: number;
    improvement: number;
  }>;
  total_generations: number;
}
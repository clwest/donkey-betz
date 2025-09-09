/**
 * Character Management Types
 */

export interface CharacterProfile {
  id: string;
  name: string;
  description: string;
  features: CharacterFeatures;
  seed: number;
  style?: string;
  model: string;
  cfg_scale: number;
  steps: number;
  negative_prompt?: string;
  thumbnail_url?: string;
  tags: string[];
  category: string;
  is_favorite: boolean;
  usage_count: number;
  variation_count?: number;
  last_used?: string;
  created_at: string;
  updated_at?: string;
}

export interface CharacterFeatures {
  hair?: string;
  eyes?: string;
  skin?: string;
  age?: string;
  gender?: string;
  clothing?: string;
  accessories?: string;
  body?: string;
  expression?: string;
  [key: string]: string | undefined;
}

export interface CharacterVariation {
  id: string;
  character_id: string;
  content_id: string;
  scene_description: string;
  variation_strength: number;
  modifications: Record<string, any>;
  created_at: string;
}

export interface SceneBatch {
  id: string;
  name: string;
  character_id: string;
  character_name: string;
  scenes: SceneConfig[];
  variation_strength: number;
  preserve_outfit: boolean;
  preserve_style: boolean;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  total_scenes: number;
  results?: BatchResult[];
  created_at: string;
  completed_at?: string;
}

export interface SceneConfig {
  description: string;
  action?: string;
  mood?: string;
}

export interface BatchResult {
  content_id: string;
  image_url: string;
  scene: SceneConfig;
  prompt_used: string;
}

export interface CharacterMix {
  id: string;
  name: string;
  mixed_features: CharacterFeatures;
  mixed_description: string;
  mixed_seed: number;
  image_url?: string;
  source_characters: MixSource[];
}

export interface MixSource {
  character_id: string;
  character_name: string;
  weight: number;
  features_used?: string[];
}

export interface CharacterCollection {
  id: string;
  name: string;
  description: string;
  character_count: number;
  characters: CharacterProfile[];
  cover_image?: string;
  color_theme: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface CharacterVariationRequest {
  base_content_id: string;
  new_scene: string;
  preserve_outfit?: boolean;
  preserve_style?: boolean;
}

export interface BatchGenerateRequest {
  character_id: string;
  scenes: SceneConfig[];
  batch_name?: string;
  variation_strength?: number;
  preserve_outfit?: boolean;
  preserve_style?: boolean;
}

export interface CharacterMixRequest {
  name: string;
  method: 'weighted' | 'selective' | 'random';
  characters: Array<{
    character_id: string;
    weight: number;
    features?: string[];
  }>;
}

export interface FineTuneRequest {
  character_id: string;
  scene?: string;
  variation_strength?: number;
  feature_overrides?: Partial<CharacterFeatures>;
  seed_offset?: number;
  cfg_scale_adjustment?: number;
  style_mix?: string;
}

export type CharacterCategory = 'default' | 'fantasy' | 'realistic' | 'cartoon' | 'anime' | 'custom';
export type MixMethod = 'weighted' | 'selective' | 'random';
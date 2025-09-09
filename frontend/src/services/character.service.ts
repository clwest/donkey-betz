/**
 * Character Management Service
 * Handles all character-related API calls
 */

import { apiClient } from './api.config';
import type {
  CharacterProfile,
  CharacterVariation,
  CharacterVariationRequest,
  BatchGenerateRequest,
  CharacterMixRequest,
  FineTuneRequest,
  SceneBatch,
  CharacterMix,
  CharacterCollection,
} from '../types/character.types';

export const characterService = {
  // Character Variations
  async createVariation(request: CharacterVariationRequest) {
    const { data } = await apiClient.post('/character/variation/', request);
    return data;
  },

  async extractLovedCharacters() {
    const { data } = await apiClient.post('/character/extract-loved/');
    return data;
  },

  // Character Library
  async getLibrary(params?: {
    category?: string;
    is_favorite?: boolean;
    search?: string;
    tags?: string[];
    sort_by?: string;
  }) {
    const { data } = await apiClient.get<{
      characters: CharacterProfile[];
      total: number;
      categories: string[];
    }>('/character/library/', { params });
    return data;
  },

  async createCharacter(character: {
    name: string;
    description?: string;
    content_id?: string;
    features?: Record<string, string>;
    tags?: string[];
    category?: string;
    is_favorite?: boolean;
    style?: string;
    model?: string;
    cfg_scale?: number;
    steps?: number;
    seed?: number;
  }) {
    const { data } = await apiClient.post('/character/library/create/', character);
    return data;
  },

  async updateCharacter(id: string, updates: Partial<CharacterProfile>) {
    const { data } = await apiClient.patch(`/character/library/${id}/`, updates);
    return data;
  },

  async deleteCharacter(id: string) {
    const { data } = await apiClient.delete(`/character/library/${id}/`);
    return data;
  },

  async toggleFavorite(id: string) {
    const { data } = await apiClient.post(`/character/library/${id}/toggle-favorite/`);
    return data;
  },

  // Batch Generation
  async batchGenerate(request: BatchGenerateRequest) {
    const { data } = await apiClient.post<{
      success: boolean;
      batch_id: string;
      batch_name: string;
      total_requested: number;
      successful: number;
      failed: number;
      results: Array<{
        content_id: string;
        image_url: string;
        scene: any;
        prompt_used: string;
      }>;
    }>('/character/batch-generate/', request);
    return data;
  },

  async getBatchHistory() {
    const { data } = await apiClient.get<{
      batches: SceneBatch[];
    }>('/character/batch-history/');
    return data;
  },

  async getBatchStatus(batchId: string) {
    const { data } = await apiClient.get<SceneBatch>(`/character/batch/${batchId}/status/`);
    return data;
  },

  // Character Mixing
  async mixCharacters(request: CharacterMixRequest) {
    const { data } = await apiClient.post<CharacterMix>('/character/mix/', request);
    return data;
  },

  async getMixHistory() {
    const { data } = await apiClient.get<{
      mixes: CharacterMix[];
    }>('/character/mix-history/');
    return data;
  },

  // Fine-Tuning
  async fineTuneVariation(request: FineTuneRequest) {
    const { data } = await apiClient.post('/character/fine-tune/', request);
    return data;
  },

  async getCharacterVariations(characterId?: string) {
    const params = characterId ? { character_id: characterId } : {};
    const { data } = await apiClient.get('/character/variations/', { params });
    return data;
  },

  // Collections
  async getCollections() {
    const { data } = await apiClient.get<{
      collections: CharacterCollection[];
      total: number;
    }>('/character/collections/');
    return data;
  },

  async createCollection(collection: {
    name: string;
    description?: string;
    character_ids?: string[];
    color_theme?: string;
    is_public?: boolean;
  }) {
    const { data } = await apiClient.post('/character/collections/create/', collection);
    return data;
  },

  async updateCollection(id: string, updates: Partial<CharacterCollection>) {
    const { data } = await apiClient.patch(`/character/collections/${id}/`, updates);
    return data;
  },

  async deleteCollection(id: string) {
    const { data } = await apiClient.delete(`/character/collections/${id}/`);
    return data;
  },

  async addToCollection(collectionId: string, characterIds: string[]) {
    const { data } = await apiClient.post(`/character/collections/${collectionId}/add/`, {
      character_ids: characterIds,
    });
    return data;
  },

  async removeFromCollection(collectionId: string, characterIds: string[]) {
    const { data } = await apiClient.post(`/character/collections/${collectionId}/remove/`, {
      character_ids: characterIds,
    });
    return data;
  },

  // Character Profiles (Legacy)
  async saveProfile(contentId: string, name: string, tags?: string[]) {
    const { data } = await apiClient.post('/character/save-profile/', {
      content_id: contentId,
      name,
      tags,
    });
    return data;
  },

  async getProfiles() {
    const { data } = await apiClient.get('/character/profiles/');
    return data;
  },

  async generateWithProfile(profileId: string, scene: string, action?: string) {
    const { data } = await apiClient.post('/character/generate/', {
      profile_id: profileId,
      scene,
      action,
    });
    return data;
  },

  // Character Variations History
  async getVariations(characterId: string) {
    const { data } = await apiClient.get<CharacterVariation[]>(`/character/${characterId}/variations/`);
    return data;
  },

  // Character Stats
  async getStats(characterId: string) {
    const { data } = await apiClient.get(`/character/${characterId}/stats/`);
    return data;
  },

  // Export/Import
  async exportCharacter(characterId: string) {
    const { data } = await apiClient.get(`/character/${characterId}/export/`);
    return data;
  },

  async importCharacter(characterData: any) {
    const { data } = await apiClient.post('/character/import/', characterData);
    return data;
  },
};
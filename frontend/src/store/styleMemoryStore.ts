import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import type { StyleMemory, StyleInsights, StyleSuggestion, LineageTree } from '../types/style-memory.types';
import { styleMemoryService } from '../services/style-memory.service';
import { toast } from 'sonner';
import { Logger } from '../utils/logger';

interface StyleMemoryState {
  // Data
  insights: StyleInsights | null;
  memories: StyleMemory[];
  suggestions: StyleSuggestion[];
  currentLineage: LineageTree | null;
  
  // UI State
  isLoading: boolean;
  showInsights: boolean;
  showLineage: boolean;
  selectedMemory: StyleMemory | null;
  
  // Actions
  captureInteraction: (contentId: string, interactionType: string, parentContentId?: string) => Promise<{ success: boolean; style_memory_id: string; recipe: any; patterns_detected: number; new_suggestions: number; }>;
  loadInsights: () => Promise<void>;
  generateSimilar: (baseContentId: string, variationType: string) => Promise<any>;
  viewLineage: (contentId: string) => Promise<void>;
  loadSuggestions: () => Promise<void>;
  useSuggestion: (suggestionId: string) => Promise<void>;
  dismissSuggestion: (suggestionId: string) => Promise<void>;
  toggleInsights: () => void;
  toggleLineage: () => void;
  selectMemory: (memory: StyleMemory | null) => void;
}

export const useStyleMemoryStore = create<StyleMemoryState>()(
  immer((set, get) => ({
    // Initial state
    insights: null,
    memories: [],
    suggestions: [],
    currentLineage: null,
    isLoading: false,
    showInsights: false,
    showLineage: false,
    selectedMemory: null,

    // Capture user interaction with content
    captureInteraction: async (contentId: string, interactionType: string, parentContentId?: string) => {
      Logger.state('StyleMemoryStore', 'Capturing interaction', { contentId, interactionType, parentContentId });
      try {
        const result = await styleMemoryService.captureInteraction(
          contentId, 
          interactionType as any, 
          parentContentId
        );
        Logger.state('StyleMemoryStore', 'Interaction captured', { styleMemoryId: result.style_memory_id, patternsDetected: result.patterns_detected });

        // Show feedback to user
        const interactionLabels = {
          love: '❤️ Loved!',
          rate_5: '⭐⭐⭐⭐⭐ Rated 5 stars!',
          save: '💾 Saved!',
          like: '👍 Liked!',
        };

        toast.success(interactionLabels[interactionType as keyof typeof interactionLabels] || 'Style captured!');

        // Show pattern detection notification
        if (result.patterns_detected > 0) {
          toast.success(`🎯 New pattern detected! Your style is evolving.`);
        }

        // Show suggestion notification
        if (result.new_suggestions > 0) {
          toast.success(`💡 ${result.new_suggestions} new suggestions available`);
          get().loadSuggestions(); // Reload suggestions
        }

        // Reload insights if they're currently shown
        if (get().showInsights) {
          get().loadInsights();
        }

        return result;
      } catch (error: any) {
        Logger.error('StyleMemoryStore.captureInteraction', error);
        toast.error('Failed to capture style preference');
        throw error;
      }
    },

    // Load comprehensive insights
    loadInsights: async () => {
      Logger.state('StyleMemoryStore', 'Loading insights');
      set((state) => {
        state.isLoading = true;
      });

      try {
        const insights = await styleMemoryService.getInsights();
        Logger.state('StyleMemoryStore', 'Insights loaded', { 
          favoriteStyles: insights.favorite_styles?.length || 0,
          memories: insights.top_memories?.length || 0 
        });
        set((state) => {
          state.insights = insights;
          state.memories = insights.top_memories;
          state.isLoading = false;
        });
      } catch (error) {
        Logger.error('StyleMemoryStore.loadInsights', error);
        set((state) => {
          state.isLoading = false;
        });
        toast.error('Failed to load style insights');
      }
    },

    // Generate similar image based on style memory
    generateSimilar: async (baseContentId: string, variationType: string = 'moderate') => {
      Logger.state('StyleMemoryStore', 'Generating similar content', { baseContentId, variationType });
      try {
        const result = await styleMemoryService.generateSimilar({
          base_content_id: baseContentId,
          variation_type: variationType as any,
          use_suggestions: true,
        });

        toast.success('Style variation generated!');
        Logger.state('StyleMemoryStore', 'Similar content generated', { contentId: result.id });
        return result;
      } catch (error) {
        Logger.error('StyleMemoryStore.generateSimilar', error);
        toast.error('Failed to generate style variation');
        throw error;
      }
    },

    // View lineage tree for content
    viewLineage: async (contentId: string) => {
      set((state) => {
        state.isLoading = true;
      });

      try {
        const lineage = await styleMemoryService.getLineage(contentId);
        set((state) => {
          state.currentLineage = lineage;
          state.showLineage = true;
          state.isLoading = false;
        });
      } catch (error) {
        set((state) => {
          state.isLoading = false;
        });
        toast.error('Failed to load style lineage');
        console.error('Lineage error:', error);
      }
    },

    // Load AI suggestions
    loadSuggestions: async () => {
      try {
        const suggestions = await styleMemoryService.getSuggestions();
        set((state) => {
          state.suggestions = suggestions;
        });
      } catch (error) {
        console.error('Suggestions error:', error);
      }
    },

    // Use an AI suggestion
    useSuggestion: async (suggestionId: string) => {
      try {
        await styleMemoryService.respondToSuggestion(suggestionId, 'used');
        toast.success('Suggestion applied!');
        
        // Remove suggestion from list
        set((state) => {
          state.suggestions = state.suggestions.filter(s => s.id !== suggestionId);
        });
      } catch (error) {
        toast.error('Failed to apply suggestion');
        console.error('Use suggestion error:', error);
      }
    },

    // Dismiss an AI suggestion
    dismissSuggestion: async (suggestionId: string) => {
      try {
        await styleMemoryService.respondToSuggestion(suggestionId, 'dismissed');
        
        // Remove suggestion from list
        set((state) => {
          state.suggestions = state.suggestions.filter(s => s.id !== suggestionId);
        });
      } catch (error) {
        toast.error('Failed to dismiss suggestion');
        console.error('Dismiss suggestion error:', error);
      }
    },

    // UI Actions
    toggleInsights: () => set((state) => {
      state.showInsights = !state.showInsights;
      if (state.showInsights && !state.insights) {
        // Load insights when first opened
        get().loadInsights();
      }
    }),

    toggleLineage: () => set((state) => {
      state.showLineage = !state.showLineage;
    }),

    selectMemory: (memory: StyleMemory | null) => set((state) => {
      state.selectedMemory = memory;
    }),
  }))
);
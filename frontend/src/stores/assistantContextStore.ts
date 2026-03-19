/**
 * Session 1078: Assistant Context Store
 *
 * Tracks the "focused entity" that Rigby should know about when the user
 * sends a message. Used by workspace tabs to set focus (e.g. "Ask Rigby
 * about this deliverable") and consumed by GlobalPADock to display
 * context pills and include in the chat payload.
 */

import { create } from 'zustand'

export interface FocusedEntity {
  type: 'deliverable' | 'initiative' | 'action_item' | 'attention' | 'file'
  id: string
  title: string
}

interface AssistantContextStore {
  focusedEntity: FocusedEntity | null
  setFocusedEntity: (entity: FocusedEntity) => void
  clearFocusedEntity: () => void
}

export const useAssistantContextStore = create<AssistantContextStore>((set) => ({
  focusedEntity: null,
  setFocusedEntity: (entity) => set({ focusedEntity: entity }),
  clearFocusedEntity: () => set({ focusedEntity: null }),
}))

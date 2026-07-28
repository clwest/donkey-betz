import { create } from 'zustand'

// ADR-0005 §3.4 step 2 substrate — triggered by queryClientErrorHandler on
// non-auth 401. Consumed by SessionExpiredModal (rendered in App.tsx as
// sibling to Routes). Trigger is idempotent — multiple 401s in quick
// succession collapse to a single modal render.
interface SessionExpiredState {
  expired: boolean
  trigger: () => void
  dismiss: () => void
}

export const useSessionExpiredStore = create<SessionExpiredState>((set) => ({
  expired: false,
  trigger: () => set({ expired: true }),
  dismiss: () => set({ expired: false }),
}))

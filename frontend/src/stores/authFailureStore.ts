import { create } from 'zustand'

// ADR-0005 §3.4 step 2 substrate (§3.5 UX widening — S3004).
//
// Discriminated 401 semantic class. Consumed by SessionExpiredModal
// (rendered in App.tsx as sibling to Routes). Triggered by
// queryClientErrorHandler on non-auth 401. Idempotent — multiple 401s
// in quick succession collapse to a single modal render.
//
// Adding a new class: extend AUTH_FAILURE_KIND + render a new variant in
// SessionExpiredModal. Do NOT create a parallel store. Consumers reference
// AUTH_FAILURE_KIND.* rather than raw string literals to prevent typo drift.
export const AUTH_FAILURE_KIND = {
  SESSION_EXPIRED: 'session_expired',
  VIP_EXPIRED: 'vip_expired',
} as const

export type AuthFailureKind = (typeof AUTH_FAILURE_KIND)[keyof typeof AUTH_FAILURE_KIND]

interface AuthFailureState {
  kind: AuthFailureKind | null
  trigger: (kind: AuthFailureKind) => void
  dismiss: () => void
}

export const useAuthFailureStore = create<AuthFailureState>((set) => ({
  kind: null,
  trigger: (kind) => set({ kind }),
  dismiss: () => set({ kind: null }),
}))

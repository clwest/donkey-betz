import type { AxiosError } from 'axios'
import { useAuthStore } from '../stores/authStore'

// ADR-0005 §3.1 γ Layer 1 default onError handler for QueryClient.
// Shape-agnostic per §3.3 — consumes AxiosError.response.status only,
// does not inspect .response.data (works for all 4 co-existing 401 shape
// families A/B/C/D per 2503 §14.1 F1).
//
// Behavior on 401 (per §3.4 nested UX policy — Cat C β "explicit re-login"):
//   1. Clear client-side auth state via useAuthStore.getState().logout().
//   2. Surface session-expired notice — placeholder console.warn until
//      T-ENVELOPE-3 ships a modal/toast component.
//   3. Do NOT force redirect. The api.ts:63-82 response interceptor already
//      redirects when the failing URL is an auth endpoint (/auth/ or /login);
//      Layer 1 defers to that. For non-auth 401s, redirect is deferred to
//      user acknowledgment of the (future T-ENVELOPE-3) modal.
//
// Anti-pattern gate per §3.5 F-C-VIP-1 scope-tightening: this handler MUST NOT
// surface VIPInvite.account_expires_at copy. Session-expired framing is
// bounded to token/session lifecycle, not account lifecycle.
export function handleQueryClientError(error: unknown): void {
  const axiosError = error as AxiosError | undefined
  const status = axiosError?.response?.status
  if (status !== 401) return

  const url = axiosError?.config?.url || ''
  const isAuthEndpoint = url.includes('/auth/') || url.includes('/login')
  if (isAuthEndpoint) return

  useAuthStore.getState().logout()
  // T-ENVELOPE-3 placeholder — replace console.warn with modal/toast.
  console.warn('[T-ENVELOPE-1] Session expired — please log in. (401 from', url, ')')
}

import type { AxiosError } from 'axios'
import { useAuthStore } from '../stores/authStore'
import { AUTH_FAILURE_KIND, useAuthFailureStore } from '../stores/authFailureStore'

// ADR-0005 §3.1 γ Layer 1 default onError handler for QueryClient.
// Shape-agnostic per §3.3 — consumes AxiosError.response.status and the
// X-VIP-Expired discriminator header only, does not inspect .response.data
// (works for all 4 co-existing 401 shape families A/B/C/D per 2503 §14.1 F1).
//
// Behavior on 401 (per §3.4 nested UX policy — Cat C β "explicit re-login"):
//   1. Clear client-side auth state via useAuthStore.getState().logout().
//   2. Trigger discriminated authFailureStore variant (kind) so
//      SessionExpiredModal renders the correct copy + CTA.
//   3. Do NOT force redirect. The api.ts:63-82 response interceptor already
//      redirects when the failing URL is an auth endpoint (/auth/ or /login);
//      Layer 1 defers to that. For non-auth 401s, redirect is deferred to
//      user acknowledgment via the modal.
//
// §3.5 F-C-VIP-1 discharged (S3003 T-VIP-1 shipped enforcement + S3004 UX
// widening). VIP-expiry 401s carry X-VIP-Expired: true from
// core/vip_middleware.py; other non-auth 401s fall to session-expired.
export function handleQueryClientError(error: unknown): void {
  const axiosError = error as AxiosError | undefined
  const status = axiosError?.response?.status
  if (status !== 401) return

  const url = axiosError?.config?.url || ''
  const isAuthEndpoint = url.includes('/auth/') || url.includes('/login')
  if (isAuthEndpoint) return

  const vipExpiredHeader = axiosError?.response?.headers?.['x-vip-expired']
  const kind = vipExpiredHeader === 'true'
    ? AUTH_FAILURE_KIND.VIP_EXPIRED
    : AUTH_FAILURE_KIND.SESSION_EXPIRED

  useAuthStore.getState().logout()
  useAuthFailureStore.getState().trigger(kind)
}

/**
 * S2984 PR4: Generic UI event telemetry helper.
 *
 * Fire-and-forget POST to /api/v1/telemetry/event/. Mirrors the
 * "never blocks UI" contract of usePageTracking — swallows all errors.
 *
 * Auth-free: telemetry endpoint accepts unauthenticated POSTs on
 * purpose (session drift shouldn't silently break event tracking).
 */

/** Fire-and-forget — never throws, never awaited. */
export function trackEvent(event: string, workspaceId?: string, payload?: Record<string, unknown>): void {
  const body: Record<string, unknown> = { event }
  if (workspaceId) body.workspace_id = workspaceId
  if (payload) body.payload = payload

  try {
    fetch('/api/v1/telemetry/event/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body),
    }).catch(() => {})
  } catch {
    // swallow
  }
}

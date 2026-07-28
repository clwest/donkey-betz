import { LogIn } from 'lucide-react'
import { useSessionExpiredStore } from '@/stores/sessionExpiredStore'

// ADR-0005 §3.4 step 2 UI — session-expired modal shown when
// sessionExpiredStore.expired is true (triggered by
// queryClientErrorHandler on non-auth 401).
//
// Per ADR-0005 §3.4 step 3: redirect is deferred to user acknowledgment.
// The single "Log in again" button is the acknowledgment; no X close
// control by design (user must acknowledge to leave the modal).
//
// Per ADR-0005 §3.5 F-C-VIP-1 scope-tightening: copy is bounded to
// token/session lifecycle framing ("session has expired"). MUST NOT
// surface VIPInvite.account_expires_at ("your VIP account expired on...")
// until T-VIP-1 ships runtime enforcement.
export default function SessionExpiredModal() {
  const expired = useSessionExpiredStore((s) => s.expired)
  const dismiss = useSessionExpiredStore((s) => s.dismiss)

  if (!expired) return null

  const handleLogin = () => {
    dismiss()
    window.location.href = '/login'
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="session-expired-title"
    >
      <div className="max-w-md w-full mx-4 rounded-lg border border-border bg-card p-6 shadow-xl">
        <h2
          id="session-expired-title"
          className="text-lg font-semibold text-foreground mb-2"
        >
          Session expired
        </h2>
        <p className="text-sm text-muted-foreground mb-6">
          Your session has expired. Please log in again to continue.
        </p>
        <button
          type="button"
          onClick={handleLogin}
          className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-card"
          autoFocus
        >
          <LogIn className="w-4 h-4" />
          Log in again
        </button>
      </div>
    </div>
  )
}

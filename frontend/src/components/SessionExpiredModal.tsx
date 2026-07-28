import { LogIn, LogOut } from 'lucide-react'
import { AUTH_FAILURE_KIND, useAuthFailureStore } from '@/stores/authFailureStore'

// ADR-0005 §3.4 step 2 UI — auth-failure modal shown when
// authFailureStore.kind is non-null (triggered by
// queryClientErrorHandler on non-auth 401).
//
// Discriminated variants (§3.5 UX widening — S3004):
//   - 'session_expired': generic session/token lifecycle — user can log in
//     again to recover. CTA: "Log in again" → /login.
//   - 'vip_expired': VIPInvite.account_expires_at reached or invite revoked.
//     Re-login won't fix it (VIP entitlement is the invalid dimension).
//     CTA: "Log out" only; user must contact their host to renew.
//
// Per ADR-0005 §3.4 step 3: redirect is deferred to user acknowledgment.
// The CTA is the acknowledgment; no X close control by design (user must
// acknowledge to leave the modal).
//
// §3.5 F-C-VIP-1 discharged (S3003 T-VIP-1 shipped enforcement + S3004
// UX widening surfaces VIPInvite.account_expires_at framing safely).
export default function SessionExpiredModal() {
  const kind = useAuthFailureStore((s) => s.kind)
  const dismiss = useAuthFailureStore((s) => s.dismiss)

  if (kind === null) return null

  const handleLogin = () => {
    dismiss()
    window.location.href = '/login'
  }

  const handleLogout = () => {
    dismiss()
    window.location.href = '/'
  }

  const isVipExpired = kind === AUTH_FAILURE_KIND.VIP_EXPIRED
  const titleId = 'auth-failure-title'

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
    >
      <div className="max-w-md w-full mx-4 rounded-lg border border-border bg-card p-6 shadow-xl">
        <h2
          id={titleId}
          className="text-lg font-semibold text-foreground mb-2"
        >
          {isVipExpired ? 'VIP demo access expired' : 'Session expired'}
        </h2>
        <p className="text-sm text-muted-foreground mb-6">
          {isVipExpired
            ? 'Your VIP demo access has expired. Contact your host to renew your invite.'
            : 'Your session has expired. Please log in again to continue.'}
        </p>
        <button
          type="button"
          onClick={isVipExpired ? handleLogout : handleLogin}
          className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-card"
          autoFocus
        >
          {isVipExpired ? (
            <>
              <LogOut className="w-4 h-4" />
              Log out
            </>
          ) : (
            <>
              <LogIn className="w-4 h-4" />
              Log in again
            </>
          )}
        </button>
      </div>
    </div>
  )
}

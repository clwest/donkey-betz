import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

type Status = 'missing_token' | 'loading' | 'success' | 'error_invalid' | 'error_expired' | 'error_network'

export default function VipAcceptPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)
  const token = searchParams.get('token')
  const next = searchParams.get('next')

  const [status, setStatus] = useState<Status>(token ? 'loading' : 'missing_token')
  const [expiresAt, setExpiresAt] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return

    const controller = new AbortController()

    fetch('/api/v1/vip-invites/exchange/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ token }),
      signal: controller.signal,
    })
      .then(async (res) => {
        const data = await res.json()
        if (res.ok && data.api_key) {
          login(data.api_key, {
            id: 0,
            username: data.username,
            email: '',
            platform_role: data.role,
          })
          if (data.expires_at) setExpiresAt(data.expires_at)
          setStatus('success')

          const redirectTo = next?.startsWith('/') ? next : '/cockpit'
          setTimeout(() => navigate(redirectTo, { replace: true }), 1200)
        } else if (res.status === 410) {
          setStatus('error_expired')
        } else {
          setStatus('error_invalid')
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') setStatus('error_network')
      })

    return () => controller.abort()
  }, [token, login, navigate, next])

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#0a0a0f',
      color: '#e2e8f0',
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      <div style={{
        maxWidth: 440,
        width: '100%',
        padding: '48px 32px',
        textAlign: 'center',
      }}>
        {status === 'loading' && (
          <>
            <div style={{ fontSize: 40, marginBottom: 16 }}>&#9679;</div>
            <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>Verifying your VIP link</h1>
            <p style={{ color: '#94a3b8' }}>This takes a few seconds. Don't refresh.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div style={{ fontSize: 40, marginBottom: 16, color: '#22c55e' }}>&#10003;</div>
            <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>Access granted</h1>
            <p style={{ color: '#94a3b8' }}>Redirecting you to the platform&hellip;</p>
            {expiresAt && (
              <p style={{ color: '#64748b', fontSize: 13, marginTop: 12 }}>
                Access expires {new Date(expiresAt).toLocaleDateString()}
              </p>
            )}
          </>
        )}

        {status === 'error_invalid' && (
          <>
            <div style={{ fontSize: 40, marginBottom: 16, color: '#ef4444' }}>&#10007;</div>
            <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>This VIP link isn't valid</h1>
            <p style={{ color: '#94a3b8' }}>Ask Chris for a fresh link.</p>
          </>
        )}

        {status === 'error_expired' && (
          <>
            <div style={{ fontSize: 40, marginBottom: 16, color: '#f59e0b' }}>&#9888;</div>
            <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>This VIP link has expired</h1>
            <p style={{ color: '#94a3b8' }}>Ask Chris for a new link.</p>
          </>
        )}

        {status === 'error_network' && (
          <>
            <div style={{ fontSize: 40, marginBottom: 16, color: '#ef4444' }}>&#9888;</div>
            <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>Couldn't verify your link</h1>
            <p style={{ color: '#94a3b8', marginBottom: 16 }}>Please try again in a moment.</p>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '10px 24px',
                background: '#3b82f6',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                cursor: 'pointer',
                fontSize: 14,
                fontWeight: 500,
              }}
            >
              Try again
            </button>
          </>
        )}

        {status === 'missing_token' && (
          <>
            <div style={{ fontSize: 40, marginBottom: 16, color: '#64748b' }}>&#128279;</div>
            <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>VIP link missing</h1>
            <p style={{ color: '#94a3b8' }}>This link is incomplete. Please use the full VIP link Chris sent you.</p>
          </>
        )}
      </div>
    </div>
  )
}

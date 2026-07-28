import { Component, type ErrorInfo, type ReactNode } from 'react'
import { AlertTriangle, RotateCw } from 'lucide-react'

// ADR-0005 §3.1 γ Layer 2 — top-level ErrorBoundary framework establishment
// (T-ENVELOPE-0). Wraps the React tree root at main.tsx to catch render-time
// errors escaping Layer 1 (e.g., render errors triggered by a React Query
// mutation callback) so they surface to the user instead of white-screen.
//
// Dual-ownership per ADR-0005 §4.1 T-ENVELOPE-0:
//   (a) Cat D typed-envelope prerequisite (this ADR).
//   (b) Group 2200 post-arc T-slot global-error-UX framework concern.
// Framework here is minimal + swappable — a Group 2200 successor arc can
// replace with richer fallback UI (per-route boundaries, telemetry, retry)
// without changing the top-level wrapper contract.
//
// T-ENVELOPE-6 (future): componentDidCatch is the observability hook-point
// for γ Layer 1+2 telemetry emit to Group 1700.

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // T-ENVELOPE-6 hook-point — replace console.error with observability
    // emit when Group 1700 telemetry channel lands.
    console.error('[ErrorBoundary]', error, errorInfo.componentStack)
  }

  handleReload = (): void => {
    window.location.reload()
  }

  render(): ReactNode {
    if (!this.state.hasError) return this.props.children
    if (this.props.fallback) return this.props.fallback

    return (
      <div
        className="min-h-screen flex items-center justify-center bg-background p-4"
        role="alert"
        aria-labelledby="error-boundary-title"
      >
        <div className="max-w-md w-full rounded-lg border border-border bg-card p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            <h2
              id="error-boundary-title"
              className="text-lg font-semibold text-foreground"
            >
              Something went wrong
            </h2>
          </div>
          <p className="text-sm text-muted-foreground mb-6">
            The page hit an unexpected error. Reload to try again. If this keeps happening, the error has been logged for investigation.
          </p>
          <button
            type="button"
            onClick={this.handleReload}
            className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-card"
            autoFocus
          >
            <RotateCw className="w-4 h-4" />
            Reload
          </button>
        </div>
      </div>
    )
  }
}

export default ErrorBoundary

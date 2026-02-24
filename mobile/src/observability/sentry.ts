import * as Sentry from '@sentry/react-native';
import Constants from 'expo-constants';

const SENTRY_DSN = process.env.EXPO_PUBLIC_SENTRY_DSN ?? '';

/**
 * Initialize Sentry crash reporting and performance monitoring.
 * Call once at app startup (before any React rendering).
 *
 * Gracefully no-ops if SENTRY_DSN is not configured.
 */
export function initSentry(): void {
  if (!SENTRY_DSN) {
    console.log('[Sentry] No DSN configured, skipping initialization');
    return;
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    debug: __DEV__,
    enabled: !__DEV__, // Only report in production builds
    tracesSampleRate: 0.2, // 20% of transactions for performance
    environment: __DEV__ ? 'development' : 'production',
    release: `com.donkeybetz.app@${Constants.expoConfig?.version ?? '0.0.0'}`,
  });
}

/**
 * Set user context for Sentry events after authentication.
 */
export function setSentryUser(user: { id: string; username: string; email?: string } | null): void {
  if (!SENTRY_DSN) return;

  if (user) {
    Sentry.setUser({
      id: user.id,
      username: user.username,
      email: user.email,
    });
  } else {
    Sentry.setUser(null);
  }
}

/**
 * Wrap the root app component with Sentry error boundary.
 */
export const SentryErrorBoundary = Sentry.wrap;

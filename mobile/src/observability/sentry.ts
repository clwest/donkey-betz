import * as Sentry from '@sentry/react-native';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

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

  const extra = Constants.expoConfig?.extra ?? {};
  const buildSha = extra.buildSha ?? process.env.EXPO_PUBLIC_BUILD_SHA ?? 'dev';
  const buildProfile = extra.eas?.buildProfile ?? 'unknown';
  const apiBaseUrl = extra.apiBaseUrl ?? 'not set';

  Sentry.init({
    dsn: SENTRY_DSN,
    debug: __DEV__,
    enabled: !__DEV__,
    tracesSampleRate: 0.2,
    environment: __DEV__ ? 'development' : 'production',
    release: `com.donkeybetz.app@${Constants.expoConfig?.version ?? '0.0.0'}`,
    dist: buildSha,
  });

  // Global tags for filtering events by build/environment
  Sentry.setTag('build_sha', buildSha);
  Sentry.setTag('build_profile', buildProfile);
  Sentry.setTag('api_base_url', apiBaseUrl);
  Sentry.setTag('device_os', `${Platform.OS} ${Platform.Version}`);
}

/**
 * Set user context for Sentry events after authentication.
 */
export function setSentryUser(user: { id: string; username: string; email?: string; platform_role?: string } | null): void {
  if (!SENTRY_DSN) return;

  if (user) {
    Sentry.setUser({
      id: user.id,
      username: user.username,
      email: user.email,
    });
    Sentry.setTag('platform_role', user.platform_role ?? 'unknown');
  } else {
    Sentry.setUser(null);
    Sentry.setTag('platform_role', 'anonymous');
  }
}

/**
 * Wrap the root app component with Sentry error boundary.
 */
export const SentryErrorBoundary = Sentry.wrap;

import { useEffect } from 'react';
import * as Sentry from '@sentry/react-native';

// ── Screen View ──────────────────────────────────────────────────────────────

/**
 * Hook: logs a screen_view breadcrumb on mount.
 * Call at the top of every screen component.
 */
export function useScreenAnalytics(screenName: string, params?: Record<string, string>) {
  useEffect(() => {
    Sentry.addBreadcrumb({
      category: 'screen_view',
      message: screenName,
      data: params,
      level: 'info',
    });

    if (__DEV__) {
      console.log(`[analytics] screen_view: ${screenName}`, params ?? '');
    }
  }, [screenName]); // eslint-disable-line react-hooks/exhaustive-deps
}

// ── API Error Telemetry ──────────────────────────────────────────────────────

/**
 * Log a failed API request as a Sentry breadcrumb.
 * Called from the axios error interceptor.
 */
export function logApiError(opts: {
  method: string;
  path: string;
  status: number | undefined;
  durationMs: number;
  errorType: string;
}) {
  Sentry.addBreadcrumb({
    category: 'api_request_failed',
    message: `${opts.method} ${opts.path} → ${opts.status ?? 'network_error'}`,
    data: opts,
    level: 'warning',
  });

  if (__DEV__) {
    console.warn(`[analytics] api_error: ${opts.method} ${opts.path} → ${opts.status} (${opts.durationMs}ms)`);
  }
}

// ── Mutation Telemetry ───────────────────────────────────────────────────────

/**
 * Track a mutation attempt and result.
 * Wraps an async action and logs both the attempt and outcome.
 */
export async function trackMutation<T>(opts: {
  action: string;
  entityType: string;
  entityId: string;
  fn: () => Promise<T>;
}): Promise<T> {
  Sentry.addBreadcrumb({
    category: 'mutation_attempt',
    message: `${opts.action} ${opts.entityType}`,
    data: { entityId: opts.entityId },
    level: 'info',
  });

  const start = Date.now();
  try {
    const result = await opts.fn();
    Sentry.addBreadcrumb({
      category: 'mutation_result',
      message: `${opts.action} ${opts.entityType} → success`,
      data: {
        entityId: opts.entityId,
        durationMs: Date.now() - start,
        success: true,
      },
      level: 'info',
    });

    if (__DEV__) {
      console.log(`[analytics] mutation: ${opts.action} ${opts.entityType} ${opts.entityId} → success (${Date.now() - start}ms)`);
    }

    return result;
  } catch (error) {
    Sentry.addBreadcrumb({
      category: 'mutation_result',
      message: `${opts.action} ${opts.entityType} → failed`,
      data: {
        entityId: opts.entityId,
        durationMs: Date.now() - start,
        success: false,
        error: String(error),
      },
      level: 'error',
    });

    if (__DEV__) {
      console.warn(`[analytics] mutation: ${opts.action} ${opts.entityType} ${opts.entityId} → FAILED (${Date.now() - start}ms)`);
    }

    throw error;
  }
}

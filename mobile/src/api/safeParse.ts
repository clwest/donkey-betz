import { z } from 'zod';
import * as Sentry from '@sentry/react-native';

/**
 * Parse API response data against a zod schema.
 * On success: returns parsed data.
 * On failure: logs to Sentry with endpoint context, returns the fallback value.
 * This guarantees shape mismatches become visible error states, never crashes.
 */
export function safeParse<T>(
  schema: z.ZodType<T>,
  data: unknown,
  opts: { endpoint: string; fallback: T },
): T {
  const result = schema.safeParse(data);
  if (result.success) return result.data;

  const issues = result.error.issues.map(
    (i) => `${i.path.join('.')}: ${i.message}`,
  );

  Sentry.captureMessage(`API schema mismatch: ${opts.endpoint}`, {
    level: 'warning',
    extra: {
      endpoint: opts.endpoint,
      issues,
      receivedKeys: data && typeof data === 'object' ? Object.keys(data) : typeof data,
    },
  });

  if (__DEV__) {
    console.warn(
      `[safeParse] ${opts.endpoint} schema mismatch:\n${issues.join('\n')}`,
    );
  }

  return opts.fallback;
}

// Session 968: Derive panel status from React Query result
import type { UseQueryResult } from '@tanstack/react-query'

type PanelStatus = 'ok' | 'empty' | 'error' | 'unwired'

interface UsePanelStatusOptions {
  /** Custom emptiness check. Defaults to: data is null/undefined, or empty array, or has count/total of 0 */
  isEmpty?: (data: unknown) => boolean
  /** Set to false for panels that are explicitly not connected to any endpoint */
  isWired?: boolean
}

const defaultIsEmpty = (data: unknown): boolean => {
  if (data == null) return true
  if (Array.isArray(data) && data.length === 0) return true
  if (typeof data === 'object' && data !== null) {
    const d = data as Record<string, unknown>
    // Common API patterns: { results: [], count: 0 } or { blogs: [], pagination: { total: 0 } }
    if (Array.isArray(d.results) && d.results.length === 0) return true
    if (Array.isArray(d.blogs) && d.blogs.length === 0) return true
    if ('count' in d && d.count === 0) return true
  }
  return false
}

export function usePanelStatus(
  query: Pick<UseQueryResult, 'isError' | 'isSuccess' | 'data' | 'error'>,
  opts?: UsePanelStatusOptions
): { status: PanelStatus; error: Error | null } {
  const { isWired = true, isEmpty = defaultIsEmpty } = opts ?? {}

  if (!isWired) {
    return { status: 'unwired', error: null }
  }

  if (query.isError) {
    return {
      status: 'error',
      error: query.error instanceof Error ? query.error : new Error(String(query.error)),
    }
  }

  if (query.isSuccess && isEmpty(query.data)) {
    return { status: 'empty', error: null }
  }

  if (query.isSuccess) {
    return { status: 'ok', error: null }
  }

  // Still loading — treat as ok (let the loading spinner handle it)
  return { status: 'ok', error: null }
}

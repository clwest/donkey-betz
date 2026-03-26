/**
 * Utilities for determining how a chat message should be rendered.
 *
 * Source of truth: backend `role` field.
 * Legacy fallback: if role is missing/incorrect, check `source` for
 *   known tool sources ('code-worker', 'claude-code').
 */

export type MessageRole = 'user' | 'assistant' | 'tool' | 'system';

const TOOL_SOURCES = new Set(['code-worker', 'claude-code']);

/** Returns the effective role for rendering, applying the legacy fallback. */
export function resolveMessageRole(
  role: string | null | undefined,
  source: string | null | undefined,
): MessageRole {
  if (role === 'tool' || role === 'system') return role as MessageRole;
  // Legacy fallback: source is the truth for known tool sources
  if (TOOL_SOURCES.has(source ?? '')) return 'tool';
  if (role === 'assistant') return 'assistant';
  return 'user';
}

/** True if the message should render as a tool/system bubble (left-aligned, tool avatar). */
export function isToolMessage(
  role: string | null | undefined,
  source: string | null | undefined,
): boolean {
  return resolveMessageRole(role, source) === 'tool' ||
    resolveMessageRole(role, source) === 'system';
}

/** Returns a human-readable label for the message author. */
export function getMessageLabel(
  role: string | null | undefined,
  source: string | null | undefined,
): string {
  const effectiveRole = resolveMessageRole(role, source);
  if (effectiveRole === 'tool' || effectiveRole === 'system') {
    if (source === 'claude-code') return 'Claude Code';
    if (source === 'code-worker') return 'CodeWorker';
    return 'Tool';
  }
  if (effectiveRole === 'assistant') return 'Assistant';
  return 'You';
}

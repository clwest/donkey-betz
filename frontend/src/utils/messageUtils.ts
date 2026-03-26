/**
 * messageUtils.ts
 *
 * Utilities for determining how a conversation message should be rendered.
 *
 * Source-of-truth contract (backend):
 *   - CodeWorker results  -> role='tool', source='code-worker'
 *   - Claude Code status  -> role='tool', source='claude-code'
 *
 * These messages must NEVER be rendered as user-authored bubbles.
 *
 * Temporary fallback: if source is 'code-worker' or 'claude-code' treat
 * the message as a tool bubble even when role is missing/incorrect (handles
 * historical rows written before the backend fix was deployed).
 */

export type MessageRole = 'user' | 'assistant' | 'tool' | 'system' | string;
export type MessageSource = 'code-worker' | 'claude-code' | string | undefined;

export interface ConversationMessage {
  role?: MessageRole;
  source?: MessageSource;
  content?: string;
  [key: string]: unknown;
}

/** Sources that identify a tool/system-generated message. */
const TOOL_SOURCES: ReadonlySet<string> = new Set(['code-worker', 'claude-code']);

/** Roles that should always render as a tool bubble. */
const TOOL_ROLES: ReadonlySet<string> = new Set(['tool', 'system']);

/**
 * Returns true when the message should be rendered as a tool bubble
 * (left-justified, non-user-attributed).
 *
 * Logic:
 *  1. Primary:  role in {'tool', 'system'}            -> tool bubble.
 *  2. Fallback: source in {'code-worker','claude-code'} -> tool bubble
 *     (handles legacy rows where role was incorrectly set to 'user').
 */
export function isToolMessage(message: ConversationMessage): boolean {
  const role = message.role ?? '';
  const source = message.source ?? '';

  if (TOOL_ROLES.has(role)) return true;

  // Temporary legacy fallback — remove once all historical rows are migrated.
  if (source && TOOL_SOURCES.has(source)) return true;

  return false;
}

/**
 * Returns true when the message was authored by the human user.
 *
 * Explicitly guards against tool messages being misattributed as user messages.
 */
export function isUserMessage(message: ConversationMessage): boolean {
  if (isToolMessage(message)) return false;
  return message.role === 'user';
}

/**
 * Returns a display label for the message author.
 */
export function getMessageAuthorLabel(
  message: ConversationMessage,
  assistantName = 'Assistant',
): string {
  if (isToolMessage(message)) {
    const source = message.source;
    if (source === 'code-worker') return 'CodeWorker';
    if (source === 'claude-code') return 'Claude Code';
    return 'System';
  }
  if (isUserMessage(message)) return 'You';
  return assistantName;
}

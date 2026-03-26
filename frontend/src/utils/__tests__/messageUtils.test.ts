/**
 * Tests for messageUtils — verifies tool message attribution logic.
 */
import { isToolMessage, isUserMessage, getMessageAuthorLabel } from '../messageUtils';

describe('isToolMessage', () => {
  it('returns true for role=tool', () => {
    expect(isToolMessage({ role: 'tool' })).toBe(true);
  });

  it('returns true for role=system', () => {
    expect(isToolMessage({ role: 'system' })).toBe(true);
  });

  it('returns false for role=user', () => {
    expect(isToolMessage({ role: 'user' })).toBe(false);
  });

  it('returns false for role=assistant', () => {
    expect(isToolMessage({ role: 'assistant' })).toBe(false);
  });

  // Fallback: source-based detection for legacy rows
  it('returns true for source=code-worker even if role is missing', () => {
    expect(isToolMessage({ source: 'code-worker' })).toBe(true);
  });

  it('returns true for source=claude-code even if role is missing', () => {
    expect(isToolMessage({ source: 'claude-code' })).toBe(true);
  });

  it('returns true for source=code-worker even if role=user (legacy row)', () => {
    expect(isToolMessage({ role: 'user', source: 'code-worker' })).toBe(true);
  });

  it('returns true for source=claude-code even if role=user (legacy row)', () => {
    expect(isToolMessage({ role: 'user', source: 'claude-code' })).toBe(true);
  });
});

describe('isUserMessage', () => {
  it('returns true only for genuine user messages', () => {
    expect(isUserMessage({ role: 'user' })).toBe(true);
  });

  it('returns false for role=tool', () => {
    expect(isUserMessage({ role: 'tool' })).toBe(false);
  });

  it('returns false for role=system', () => {
    expect(isUserMessage({ role: 'system' })).toBe(false);
  });

  it('returns false when source=code-worker even if role=user', () => {
    expect(isUserMessage({ role: 'user', source: 'code-worker' })).toBe(false);
  });

  it('returns false when source=claude-code even if role=user', () => {
    expect(isUserMessage({ role: 'user', source: 'claude-code' })).toBe(false);
  });
});

describe('getMessageAuthorLabel', () => {
  it('returns "CodeWorker" for source=code-worker', () => {
    expect(getMessageAuthorLabel({ role: 'tool', source: 'code-worker' })).toBe('CodeWorker');
  });

  it('returns "Claude Code" for source=claude-code', () => {
    expect(getMessageAuthorLabel({ role: 'tool', source: 'claude-code' })).toBe('Claude Code');
  });

  it('returns "System" for generic tool role', () => {
    expect(getMessageAuthorLabel({ role: 'tool' })).toBe('System');
  });

  it('returns "You" for user messages', () => {
    expect(getMessageAuthorLabel({ role: 'user' })).toBe('You');
  });

  it('returns assistant name for assistant messages', () => {
    expect(getMessageAuthorLabel({ role: 'assistant' }, 'Aria')).toBe('Aria');
  });

  it('never labels a code-worker message as "You"', () => {
    const label = getMessageAuthorLabel({ role: 'user', source: 'code-worker' });
    expect(label).not.toBe('You');
  });
});

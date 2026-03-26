import { resolveMessageRole, isToolMessage, getMessageLabel } from '../messageRoleUtils';

describe('resolveMessageRole', () => {
  it('returns tool when role is tool', () => {
    expect(resolveMessageRole('tool', 'code-worker')).toBe('tool');
  });

  it('returns tool for code-worker source with no role (legacy)', () => {
    expect(resolveMessageRole(null, 'code-worker')).toBe('tool');
    expect(resolveMessageRole(undefined, 'code-worker')).toBe('tool');
  });

  it('returns tool for claude-code source with no role (legacy)', () => {
    expect(resolveMessageRole(null, 'claude-code')).toBe('tool');
  });

  it('uses legacy source fallback even when role=user is persisted incorrectly', () => {
    expect(resolveMessageRole('user', 'code-worker')).toBe('tool');
    expect(resolveMessageRole('user', 'claude-code')).toBe('tool');
  });

  it('returns user for normal user messages', () => {
    expect(resolveMessageRole('user', 'user')).toBe('user');
    expect(resolveMessageRole('user', null)).toBe('user');
  });

  it('returns assistant for assistant messages', () => {
    expect(resolveMessageRole('assistant', 'pa')).toBe('assistant');
  });

  it('returns system when role is system', () => {
    expect(resolveMessageRole('system', null)).toBe('system');
  });
});

describe('isToolMessage', () => {
  it('is true for tool role', () => {
    expect(isToolMessage('tool', null)).toBe(true);
  });

  it('is true for legacy code-worker source', () => {
    expect(isToolMessage(null, 'code-worker')).toBe(true);
  });

  it('is false for user messages', () => {
    expect(isToolMessage('user', 'user')).toBe(false);
  });
});

describe('getMessageLabel', () => {
  it('labels code-worker as CodeWorker', () => {
    expect(getMessageLabel('tool', 'code-worker')).toBe('CodeWorker');
  });

  it('labels claude-code as Claude Code', () => {
    expect(getMessageLabel('tool', 'claude-code')).toBe('Claude Code');
  });

  it('labels user messages as You', () => {
    expect(getMessageLabel('user', 'user')).toBe('You');
  });
});

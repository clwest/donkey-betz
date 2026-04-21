# `.githooks/` — Shared Git Hooks

Tracked copy of the pre-commit hook so every clone gets the same security/quality guards.

## What the pre-commit hook blocks

1. **Hardcoded API keys / secrets** — `api_key='...'`, `secret_key='...'`, `password='...'` patterns (unless wrapped in `os.environ.get`, `settings.VAR`, etc.)
2. **Private keys** — any `BEGIN * PRIVATE KEY` block
3. **Database URLs with credentials** — `postgres://user:pass@host` style (unless wrapped in env-var)
4. **40-char hex auth tokens** — `TOKEN = '...'`, `AUTH_TOKEN = '...'`, `Authorization: Token ...` (unless wrapped in env-var). Added 2026-04-20 per `docs/cleanup/TOKEN_ROTATION_PLAYBOOK.md`.
5. **Direct commits to `main` / `master`** — use a feature branch + PR.

Allowed files (exempt from 40-char hex check):
- `.env*` (globally gitignored anyway)
- `docs/cleanup/TOKEN_ROTATION_PLAYBOOK.md` + `docs/cleanup/PHASE_2_EXECUTION_LOG.md` — these intentionally document the found tokens for audit purposes.

## Installation

### Option 1 — one-liner (recommended)

```bash
git config core.hooksPath .githooks
```

This tells Git to look in `.githooks/` instead of `.git/hooks/`. One-time per clone. Hook changes committed to the repo automatically propagate.

### Option 2 — symlink (if you prefer the default hooks path)

```bash
ln -sf ../../.githooks/pre-commit .git/hooks/pre-commit
```

### Option 3 — manual copy

```bash
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Copy doesn't auto-update when the tracked version changes; you have to re-copy after each `git pull`.

## Verify it's working

```bash
echo 'TOKEN = "abc123def456abc123def456abc123def456abcd"' > /tmp/bad.py
git add /tmp/bad.py    # or stage real file
bash .githooks/pre-commit
# Expected: 🚨 SECURITY VIOLATION: Hardcoded 40-char hex token ...
```

## Bypassing (emergency only)

`git commit --no-verify` — use sparingly. Almost always there's a safer path (env var, settings, config file).

## Maintenance

When adding a new check:
1. Edit `.githooks/pre-commit`
2. Update this README's "What the pre-commit hook blocks" section
3. Commit both
4. Bump the version comment in the hook header

## Related

- `docs/cleanup/TOKEN_ROTATION_PLAYBOOK.md` — the token-rotation operational playbook that motivated check #4
- `docs/docs-pattern/06_dos_and_donts.md` — general repo hygiene rules

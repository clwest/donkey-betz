---
title: "Token Rotation Playbook"
status: active
created: 2026-04-20
related: ROOT_CLEANUP_PLAN.md, PHASE_2_EXECUTION_LOG.md
---

# Token Rotation Playbook

Operational playbook for rotating auth tokens and API keys leaked in the repo. Use when you have Django shell / Railway access to execute the rotation.

## Why this doc exists

During the Phase 2 cleanup audit (2026-04-20), multiple 40-char hex auth tokens and at least one external API key were found hardcoded in tracked files. Some were in active scripts; others were in archived documentation. A follow-up audit pulled 14 candidate tokens from git history; 9 of them appear to still live in current HEAD somewhere.

Prod was taken down by Chris on 2026-04-20 so rotation can happen without breaking live services. This doc captures the exact steps so when prod comes back up (or for local rotation), the process is mechanical.

## Token inventory (as of 2026-04-20)

### Scrubbed from HEAD (complete as of 2026-04-20)

All 15 identified tokens have been replaced in HEAD with placeholders or moved to env-var reads. **Git history still contains the original values** — rotation in the production DB is the only way to actually invalidate them.

| Token (first 8) | Owner / usage | Scrub batch | Rotation priority |
|---|---|---|---|
| `43d46129...` | Production DRF token (Railway) | PR #2033 — Part 1 | **HIGH** (still valid, prod currently offline) |
| `19f3b711...` | Local `donkeyking` DRF token | PR #2033 — Part 1 | LOW (localhost-only) |
| `2e63ae5a...` | `mobile_test` DRF token (Session 115) | PR #2033 — Part 1 | LOW (localhost-only, retired user) |
| `0fb2390d...` | Early API token | Part 2 (this PR) — 31 files | MEDIUM |
| `424a48280...` | `alice_writer` DRF token | Part 2 — 7 files (incl. `.env.example` — big no-no) | MEDIUM |
| `993f8273...` | Generic auth token | Part 2 — 46 files (largest batch) | MEDIUM |
| `c4ba8e9a...` | Auth token in `scripts/api/test_sports_integration.py` | Part 2 — 11 files | MEDIUM |
| `0ef9dd74...` | Admin token | Part 2 — 1 file | LOW |
| `2447578c...` | Django login API response token | Part 2 — 4 files | LOW |
| `504406af...` | `external-project-docs/ai-content-studio/` token | Part 2 — 3 files | LOW |
| `cff3e844...` | `external-project-docs/ai-content-studio/` token | Part 2 — 3 files | LOW |
| `e7d2ae96...` | `tests/unit/test_frontend_auth.py` | Part 2 — 1 file | LOW |
| `4b9facbb...` | Multiple — archive + `tests/api/` | Part 2 — 3 files | LOW |
| `85a7e01f...` | `tests/one-off/test_replicate_*.py` + `test_trained_lora.py` | Part 2 — 2 files | LOW (Replicate API key) |
| `f6355675...` | `external-project-docs/ai-content-studio/` token | Part 2 — 1 file | LOW |

All tracked-file occurrences replaced with `<redacted-<first8>-2026-04-20>` placeholder. Scrub sweep done via `git grep -l <token> | xargs sed -i '' "s/.../placeholder/g"` across tracked files only (gitignored `.env*` untouched).

### External API keys

| Key | Status | Action |
|---|---|---|
| **SERPER_API_KEY** (`ba6bd09c...`) | Only in gitignored `.env` + `generated_projects/*/.env` (not tracked in git) | Rotate at https://serper.dev if still valid, update local `.env`. No repo scrub needed. |

### Pre-commit hook now blocks future leaks

`.githooks/pre-commit` (tracked) adds a check for `TOKEN = 'hex40'` / `AUTH_TOKEN = 'hex40'` / `Authorization: Token hex40` patterns. Enable per-clone:

```bash
git config core.hooksPath .githooks
```

See [`.githooks/README.md`](../../.githooks/README.md) for full docs.

## How to rotate a Django DRF token

All of the `19f3b711...`, `2e63ae5a...`, `424a48280...`-style 40-char hex values are Django REST Framework auth tokens owned by a specific user. Rotation is per-user.

### Step 1 — Identify the owner

```python
# python manage.py shell
from rest_framework.authtoken.models import Token

# Look up the leaked token by its first few chars (the full value is in git history
# or in this playbook's inventory table above)
tokens = Token.objects.filter(key__startswith='43d46129')
for t in tokens:
    print(t.user.username, t.user.email, 'is_staff=', t.user.is_staff)
```

### Step 2 — Delete + regenerate

```python
# python manage.py shell
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
User = get_user_model()

# Delete the old token
old = Token.objects.get(key='<old-token-literal>')
user = old.user
old.delete()

# Create a new one
new_token, created = Token.objects.get_or_create(user=user)
print(f"New token for {user.username}: {new_token.key}")
```

The old token is invalidated the instant `.delete()` runs. Any client still sending it will start getting 401s.

### Step 3 — Update consumers

For the **production token** (`43d46129...`):
- Check `Railway → Service → Variables` for any env vars that reference a PA/auth token
- Update them to the new token value
- Redeploy affected Railway services if needed

For the **local `donkeyking` token** (`19f3b711...`):
- Update local `.env` file: `PA_API_TOKEN=<new-token>`
- Update `.claude/settings.local.json` allowlist entries (local-only, gitignored)
- No Railway change needed (localhost-only)

### Step 4 — Verify new token works

```bash
# Local
curl -H "Authorization: Token <new-token>" http://localhost:8000/api/assistant/chat/ -X GET

# Production (once prod is back up)
curl -H "Authorization: Token <new-token>" https://donkey-betz-platform-production.up.railway.app/api/assistant/chat/ -X GET
```

Expect 200 or a 405 (method not allowed). A 401 means the token wasn't recognized.

### Step 5 — Verify old token is dead

```bash
curl -H "Authorization: Token <old-token>" http://localhost:8000/api/assistant/chat/ -X GET
# Expect: 401 Unauthorized
```

## How to rotate an external API key (Serper, OpenAI, etc.)

Different process — these are issued by the external provider, not by Django.

### Serper (ba6bd09c... if still valid)

1. Log into https://serper.dev/
2. Go to API Keys → Revoke the exposed key → Create a new one
3. Update `SERPER_API_KEY` in local `.env`
4. Update Railway env var: `Railway → Variables → SERPER_API_KEY`
5. Grep the repo for the old key literal and scrub any remaining instances (use the grep at the bottom)

### OpenAI / Anthropic / other LLM providers

Similar pattern. Each provider's dashboard has a revoke + reissue flow. Always rotate via the provider's UI first, then update `.env` + Railway env vars, then scrub from code.

## Where the leaks came from (root-cause)

- **Test scripts with hardcoded tokens** — developers copy-pasted a working token into a new script for speed. Most common pattern.
- **Session handoff docs** — Claude Code sessions documented "the LOCAL token is X" for future-Claude's convenience, with the literal inline. These compounded across sessions.
- **Mobile app .env files committed by mistake** — should have been in `.gitignore` from the start.
- **Archive docs preserved old tokens** — session 115 had the token in the body of the doc, preserved through later archive moves.

**Prevention for the future:**
- Never commit a DRF token literal. Always use `os.environ.get('...')` in code.
- Session handoffs should use `<local-donkeyking-token>` placeholder, not the literal.
- Add a pre-commit hook that greps for 40-char hex strings.

## Pre-commit hook (recommended)

Add to `.git/hooks/pre-commit` (or integrate into the existing hook):

```bash
#!/bin/bash
# Block commits containing 40-char hex tokens in tracked files (not in .env*)
if git diff --cached --name-only | grep -vE "^\.env" | \
   xargs -I {} grep -lE "[a-f0-9]{40}" {} 2>/dev/null | head -1; then
    echo "ERROR: 40-char hex literal detected in staged files."
    echo "If it's a commit SHA, that's fine — bypass with --no-verify."
    echo "If it's a token: move to env var. See docs/cleanup/TOKEN_ROTATION_PLAYBOOK.md"
    exit 1
fi
```

This catches the mistake at commit time rather than discovering it post-hoc in an audit.

## Useful grep commands

Locate all remaining token occurrences after a rotation:

```bash
# Full sweep for any 40-char hex literal (noisy — will catch commit SHAs too)
grep -rE "[a-f0-9]{40}" --include="*.py" --include="*.md" --include="*.sh" \
     --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules . \
     | grep -v _index.json

# Specific token hunt
grep -rl "<token-literal>" --include="*.py" --include="*.md" --include="*.sh" \
     --include="*.env*" --exclude-dir=.git --exclude-dir=.venv . \
     | grep -v _index.json
```

## History rewrite — NOT recommended

Tokens in git history stay there forever unless you rewrite history with `git filter-repo` or `BFG Repo-Cleaner`. Both:
- Force-push to main, breaking every clone
- Invalidate existing commit SHAs (breaks PR references, old session handoffs, commit-linking in docs)
- Require every collaborator to re-clone

**Better answer:** rotate the token. Once a token is invalid, its presence in history is harmless (just a 40-char string with no power).

Only rewrite history if:
1. The token is still valid AND cannot be rotated (e.g., vendor account was lost)
2. The leak is sensitive enough to justify breaking everything

Neither applies to any of the tokens in this repo's current audit.

## Session 115 user accounts referenced in old docs

Two retired users still referenced in historical session docs (the users may or may not exist in the DB anymore):

- `mobile_test` / password `test123` — used for Session 115 mobile app auth testing
- `alice_writer` — referenced with token `424a48280...`

If these accounts still exist, consider deactivating them:

```python
# python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
for uname in ['mobile_test', 'alice_writer']:
    u = User.objects.filter(username=uname).first()
    if u:
        u.is_active = False
        u.save(update_fields=['is_active'])
        print(f"Deactivated {uname}")
```

## Related docs

- [`ROOT_CLEANUP_PLAN.md`](ROOT_CLEANUP_PLAN.md) — the phased repo cleanup plan
- [`PHASE_2_EXECUTION_LOG.md`](PHASE_2_EXECUTION_LOG.md) — where the `43d46129...` finding was first flagged
- [`../docs-pattern/06_dos_and_donts.md`](../docs-pattern/06_dos_and_donts.md) — general framework rules (no fluff / verify truth)

---

*When you execute a rotation, append a row to the "Scrubbed from HEAD" table above with the rotation date. That makes this doc self-auditing over time.*

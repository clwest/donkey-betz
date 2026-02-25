# ADR-0002: Moderate-Dangerous Action Policy

**Status**: Accepted
**Date**: 2026-02-25

## Context

The executor can run arbitrary commands on behalf of the platform. A policy
engine must classify actions into tiers to prevent dangerous operations while
allowing productive work.

## Decision

Three-tier action policy:

### Tier A — Auto-Allowed
Read-only operations, tests, linters, repo edits within the working branch:

- `cat`, `grep`, `find`, `ls`, `head`, `tail`, `wc`
- `python -m pytest`, `npm test`, `npx tsc --noEmit`
- `flake8`, `ruff`, `eslint`, `prettier`
- `git status`, `git diff`, `git log`, `git branch`
- File read/write within repo directory
- `pip install`, `npm install` (within repo)

### Tier B — Requires Approval
Operations that modify shared state or cross trust boundaries:

- `git commit`, `git push`
- PR creation/merge (via `gh`)
- Touching sensitive files: `settings.py`, `core/settings.py`, `.env*`,
  CI/CD configs, Dockerfile, Procfile, infrastructure files
- Enabling network egress
- Database migrations (`python manage.py migrate`)
- Package version changes in requirements/package.json

### Tier C — Blocked
Operations that could compromise the host or system:

- `sudo`, `su`, privilege escalation
- Docker socket access (`/var/run/docker.sock`)
- Host filesystem mounts outside repo
- `rm -rf /`, `rm -rf ~`, `rm -rf ..` (path traversal deletes)
- Writing to `/etc`, `/usr`, `/var` (system directories)
- Writing `.env` files with secrets
- `kill`, `pkill` targeting system processes
- Network listeners (`nc -l`, `python -m http.server`)
- Crypto mining, fork bombs, resource exhaustion patterns

## Alternatives Considered

- **Allow everything**: Unacceptable risk.
- **Block everything except reads**: Too restrictive for productive work.
- **Per-command allowlisting**: Too brittle, hard to maintain.

## Consequences

- **Productive**: Most development commands work without friction (Tier A).
- **Safe**: Destructive commands are blocked deterministically (Tier C).
- **Auditable**: Tier B actions require explicit approval, creating a decision trail.
- **Evolvable**: Tiers can be adjusted by editing patterns without code changes.
- **Not bulletproof**: A sophisticated attacker could bypass pattern matching.
  Future versions should add syscall-level enforcement via Docker seccomp profiles.

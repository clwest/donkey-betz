# Audit Workspace

`docs/audit/` is the current active audit workspace for this repository.

Start here:

- [`docs/audit/AUDIT_V1.md`](AUDIT_V1.md)
- [`docs/audit/CLEANUP_PLAN.md`](CLEANUP_PLAN.md)

Historical audit material lives elsewhere:

- `docs/audits/` is the historical audit workspace.
- `docs/audit-2026/` is a legacy, time-bounded audit dossier set.

Do not delete either historical workspace just because it is older. A file
inside one of those folders can still be authoritative if that file says it is
current, but the default assumption is that `docs/audit/` is the active entry
point for new work.

## Guardrails

Run the non-blocking repository drift check manually with:

```bash
python scripts/verify_repo_guardrails.py
```

It prints the current `context-kit` inspection, the `context-kit verify --json`
summary, and warnings for tracked generated paths. Phase 4B can tighten the
selected warnings into blocking checks once the repo is ready.

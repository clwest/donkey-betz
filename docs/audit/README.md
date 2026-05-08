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

By default the script runs in strict mode and exits non-zero when any of these
rules fail:

- `docs/PLATFORM_INVENTORY.md` is stale relative to the current `git HEAD`
- tracked generated paths are present
- `context-kit verify --json` reports any `CONFLICT` findings

The following remain advisory and do not fail the script:

- `context-kit inspect` warnings
- `DOC_ONLY` findings from `context-kit verify --json`
- large-file warnings surfaced by `context-kit inspect`

If you need the Phase 4A warning-only behavior locally, run:

```bash
python scripts/verify_repo_guardrails.py --no-strict
```

Phase 4B keeps strict mode on by default while leaving the advisory warnings
non-blocking.

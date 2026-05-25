# docs/ops/ — runtime output directory

**Status:** active code-output dir, NOT a docs subdir
**Session 1143 audit clarification:** This directory exists as the default output location for `celery_inspect_report.py` (`core/management/commands/celery_inspect_report.py:37` — `default='docs/ops'`). It is treated as a docs subdir by file-listing tools but is functionally a code artifact directory.

## What lives here

- JSON outputs from `python manage.py celery_inspect_report` (filenames like `integration_inventory_<date>.json`, `celery_inspect_<timestamp>.json`)
- Operator runbooks parked here historically (e.g., `FLY_IO_MIGRATION.md` was planned per Session 1116 but never written)

## Why this README exists

Phase 2B-2 of the Session 1143 corpus audit considered deleting this dir as "empty subdir." Pre-flight scan caught the runtime coupling:
- `core/management/commands/celery_inspect_report.py:37-38` writes here by default
- `docs/INDEX.md` lists the dir even when empty
- Historical handoffs reference `docs/ops/FLY_IO_MIGRATION.md` (a parked-open runbook plan)

Outcome: dir KEPT. This README serves as the dir-level pointer for future audits.

## Conventions

- New ops-output JSONs are auto-written here by code; do not edit by hand.
- New ops-output markdown (runbooks, post-mortems) follows the same path. Use a clear filename: `<TOPIC>_RUNBOOK.md` or `<DATE>_<TOPIC>_NOTES.md`.
- Per the DOC_LIFECYCLE.md §2b runtime-coupled paths inventory, this dir must NOT be moved or deleted without first updating `celery_inspect_report.py`.

# Superseded `docs/current/*` (January 2026 snapshot)

**Archived on:** 2026-04-26 (Session 1100 doc-drift cleanup)
**Original location:** `docs/current/`
**Original timestamp:** Stamped "January 2026 / Session 661+"
**Reason for retirement:** Stats had drifted materially from runtime
reality (verifier flagged 12 distinct claim drifts spanning agents,
tasks, models, views, endpoints, services, Discord cogs).

## What this folder contains

A frozen snapshot of `docs/current/` as it stood on 2026-04-26, before
removal from the active doc tree. Every original file is preserved
byte-for-byte after the prepended `ARCHIVED-DOC-V1` pointer header.

## Why we kept it

Per the project rule (see `MEMORY.md` → `feedback_docs_never_delete.md`),
no doc gets deleted. Beyond that, this corpus is being preserved as
potential source material for a future book about *how Chris learned to
collaborate with Claude to build this platform* — these snapshots
capture the platform's January-2026 self-image, including the
contradictions and gaps that drove later automation work (the doc-claim
verifier, `PLATFORM_INVENTORY.md`, this very cleanup).

## Where authoritative live docs now live

| Topic | Authoritative source |
|---|---|
| Platform overview (narrative) | `docs/PLATFORM_WHAT_IT_IS.md` |
| Platform overview (runtime-derived) | `docs/PLATFORM_INVENTORY.md` |
| Agents | `docs/AGENTS.md`, `docs/topics/agent-system.md` |
| Personal Assistant | `docs/topics/personal-assistant.md` |
| Celery / workers | `docs/topics/celery-workers.md` |
| Spiders | `docs/SPIDERS.md`, `docs/topics/spider-network.md` |
| Models | `docs/DATABASE_MODEL_REFERENCE.md` |
| Frontend | `docs/topics/frontend.md` |
| Infrastructure | `docs/topics/infrastructure.md` |
| Discord | `docs/DISCORD_INTEGRATION.md`, `docs/DISCORD_COMMANDS.md` |

To regenerate live numbers at any time:

```bash
python manage.py generate_platform_inventory
python manage.py verify_doc_claims --only-drift
```

## Files in this archive

- `AGENTS.md` — Agent inventory snapshot
- `API_ENDPOINTS.md` — API endpoint catalog
- `ASSISTANT_SYSTEM.md` — Personal Assistant architecture
- `AUTONOMOUS_SYSTEMS.md` — Autonomous behavior overview
- `CELERY_TASKS.md` — Celery task catalog
- `DISCORD.md` — Discord bot snapshot
- `FRONTEND_DATA_AUDIT.md` — Frontend data-flow audit
- `INDEX.md` — `docs/current/` top-level index
- `INFRASTRUCTURE.md` — Infra snapshot
- `LEARNING_SYSTEM.md` — Agent learning-loop notes
- `MANAGEMENT_COMMANDS.md` — Django management command catalog
- `MODELS.md` — Database model snapshot
- `RICH_DATA_AUDIT.md` — Rich-data presence audit
- `SERVICES.md` — Services inventory snapshot
- `SPECIAL_FEATURES.md` — Special-feature catalog
- `SPIDERS.md` — Spider inventory snapshot
- `SYSTEM_INTEGRATION_GUIDE.md` — System wiring snapshot
- `TROUBLESHOOTING.md` — Troubleshooting playbook
- `VIEWS.md` — Django views catalog
- `WEBSOCKETS.md` — WebSocket consumer catalog

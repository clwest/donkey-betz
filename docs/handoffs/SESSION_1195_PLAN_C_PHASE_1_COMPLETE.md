# Session 1195 — Plan C Phase 1 COMPLETE (Initiatives-First Backbone enforcement layer)

**Status:** Wrapped clean. **6 Plan C PRs merged** + 1 inventory refresh + 3 Session 1194 carryover merges. The no-orphan contract is now real: create-time flagging + update-time auto-clear + daily sweep + regression tests + recon command. §6.2 inference-rule decision is now **data-informed** (and the data says workspace-based inference is mathematically dead — keep "require explicit" for now).
**Date:** 2026-06-22
**Active conversation:** `pa-92bacb0fbcab44fb` (spun fresh at session open per Rigby's Session 1194 close-recommendation).
**Prior session:** [`SESSION_1194_INITIATIVES_FIRST_BACKBONE_PIVOT.md`](./SESSION_1194_INITIATIVES_FIRST_BACKBONE_PIVOT.md).

## TL;DR

Session 1195 opened by merging the 3 Session 1194 carryover PRs (#2397/#2398/#2399 — spec, Plan A, Plan B), refreshing the stale inventory (#2401), then implementing Plan C Phase 1 end-to-end across 6 atomic PRs. Each PR was: smoke-tested against real spine Initiative #1 data, Rigby-reviewed in the active thread, admin-merged after Chris's go-ahead. The full no-orphan loop is now closed: factory creates and tool-mediated updates flag misalignment as `diagnostic` with 7-day TTL, alignment-restoring updates auto-clear, and the daily 3:45 AM Denver sweep archives expired diagnostics non-destructively. The PR #6 recon against real Donkey Betz data delivered the §6.2 unlock: **96 of 96 missing-initiative rows in DBZ are ambiguous under any workspace-based inference rule**, because the 3 spine initiatives all target the same workspace — §6.2 must use a new signal, not a smarter workspace match.

## PRs shipped

| PR | Branch | Theme | Spec |
|---|---|---|---|
| **#2397** | `docs/session-1194-initiatives-first-pivot` | Session 1194 carryover — pivot spec + deferred clustering pointer | foundation |
| **#2398** | `feat/session-1194-initiatives-backbone-a-audit-gap` | Session 1194 carryover — Plan A audit gap | AC1 |
| **#2399** | `feat/session-1194-initiatives-backbone-b-read-api-linkage` | Session 1194 carryover — Plan B read-path linkage | AC2/AC3/AC4 |
| **#2401** | `fix/session-1195-inventory-refresh` | Inventory + autoblocks refresh (5+ sessions stale) | DOC_LIFECYCLE §2c |
| **#2402** | `feat/session-1195-plan-c-phase1-migration` | Plan C PR #1 — 5 diagnostic fields + composite index | §3.C / §6.1 |
| **#2403** | `feat/session-1195-plan-c-phase1-factory-hook` | Plan C PR #2 — factory create-path Initiative-alignment hook | §3.C |
| **#2404** | `feat/session-1195-plan-c-phase1-update-hook` | Plan C PR #3 — update-path hook with auto-clear | §3.C |
| **#2405** | `feat/session-1195-plan-c-phase1-sweep` | Plan C PR #4 — daily sweep beat task + mgmt command | §3.C |
| **#2406** | `feat/session-1195-plan-c-phase1-tests` | Plan C PR #5 — 10-case regression test suite | §3.C |
| **#2407** | `feat/session-1195-plan-c-phase1-backfill-cmd` | Plan C PR #6 — backfill recon → §6.2 input | §6.2 |

10 PRs landed total. All admin-bypass merged on the pre-existing `Agents count claims` CONFLICT, which has been red on main since Session 1192 (`load_all_agents_advisors.py` expected=155 vs DB actual=87 — separate fix, still tracked as a P3 deferred item).

## What's now true post-merge (behavioral invariants)

1. **`deliverable_factory.create_deliverable` marks misalignment.** Missing `initiative_id` (or one validated-and-dropped) lands as `diagnostic_status='diagnostic'`, `diagnostic_code='missing_initiative_id'`. Workspace mismatch (initiative target ≠ deliverable workspace) lands as `diagnostic_code='workspace_mismatch'`. TTL defaults to 7 days via `settings.DELIVERABLE_DIAGNOSTIC_TTL_HOURS=168`. Payload captures expected/actual workspace, agent_name, tool, trace_id, caller fingerprint.
2. **`deliverable_tool.update` re-evaluates alignment after every mutation.** Mismatches introduced via update flag diagnostic. Mismatches resolved via update **auto-clear** all 5 fields back to NULL. Idempotent non-alignment updates (e.g., title-only) leave `diagnostic_marked_at` + payload unchanged (no churn).
3. **Daily 3:45 AM Denver sweep archives expired diagnostics.** Flips canonical `Deliverable.status='archived'`, augments `diagnostic_payload` with `archived_by='diagnostic_sweep'` + `archived_reason='ttl_expired'` + `archived_at`. **Preserves `diagnostic_status='diagnostic'`** so later rollups can distinguish TTL-archived from manually-archived (option-b: no parallel lifecycle enum).
4. **`update_path` supports `initiative_id`** — required for end-to-end auto-clear of `missing_initiative_id` (resolving via re-attachment now works).
5. **`[ORPHAN-DELIVERABLE]` is the grep-friendly prefix.** Two warning shapes (per code) on transitions to diagnostic; one info log on auto-clear (with `prior_code`); one info per row + one summary on sweep.

## Rollback / disable levers per PR

| PR | Soft-disable lever | Revert path |
|---|---|---|
| #2402 | n/a (additive nullable fields + index) | revert migration 0360 |
| #2403 | set `DELIVERABLE_DIAGNOSTIC_TTL_HOURS=0` → diagnostic_expires_at would land in the past → first sweep run archives all new flags | revert PR; helper goes too (used by #2404) |
| #2404 | won't auto-clear if `_evaluate_initiative_alignment` raises — already fail-open | revert PR |
| #2405 | disable PeriodicTask row: `python manage.py shell -c "from django_celery_beat.models import PeriodicTask; PeriodicTask.objects.filter(name='sweep-diagnostic-deliverables').update(enabled=False)"` | revert PR + remove beat row |
| #2406 | tests are CI-only currently (local DB infra blocker) | revert PR |
| #2407 | read-only by default; no lever needed | revert PR |

## Key recon finding (the §6.2 evidence)

Run: `python manage.py backfill_deliverable_initiative_links --workspace-id b4503364-2573-4401-9e28-61a739e0ce50`

**Donkey Betz workspace (scanned 165 deliverables):**
- 1 aligned
- 96 missing_initiative_id
- 0 missing_workspace_id
- 0 workspace_mismatch
- 68 initiative_missing_target_workspace

**Inference simulation over the 96 missing-initiative rows:**

| Rule | Assignable | Ambiguous | Unassignable | % Assignable |
|---|---|---|---|---|
| `rule1_workspace_exact` | 0 | **96** | 0 | 0% |
| `rule2_spine_fallback` | 0 | **96** | 0 | 0% |
| `rule3_require_explicit` | 0 | 0 | 96 | 0% (baseline) |

**Verdict (Rigby-ratified):** workspace-based inference is mathematically incapable of disambiguation because the 3 spine initiatives (`6941372d-…`, `2071a9c6-…`, `7e23d621-…`) all target the same Donkey Betz workspace. §6.2 must introduce a **new signal**, not a smarter workspace match.

**Top orphan creators (DBZ workspace):**

```
Rigby=33  ResearchAgent=24  ClaudeCode=11  ContentWriterAgent=9
ThinkingAgent=5  DevOpsAgent=4  COOAgent=3  NewsletterTool=2
CTOAgent=2  PersonalAssistant=2
```

**Bonus quantitative finding:** 68 deliverables have `initiative_id` set but the linked initiative has **no `target_workspace_id`** — the `initiative_create` write-path side-quest from Session 1194 close becoming visible at scale. That gap blocks alignment evaluation for those 68 rows entirely.

## 7-day watch checklist (start 2026-06-29)

After Phase 1 has been live for 7 days, the Phase 2 hard-reject flip decision (§6.1) is evidence-gated. Run:

```bash
# 1. Re-recon DBZ workspace and compare deltas
python manage.py backfill_deliverable_initiative_links \
    --workspace-id b4503364-2573-4401-9e28-61a739e0ce50 \
    --json-only > /tmp/recon-2026-06-29.json
diff <(jq '.totals' /tmp/recon-2026-06-22.json) \
     <(jq '.totals' /tmp/recon-2026-06-29.json)

# 2. Grep production celery.log for `[ORPHAN-DELIVERABLE]` emission rate
grep '\[ORPHAN-DELIVERABLE\]' celery.log | wc -l   # transitions logged
grep 'code=ttl_auto_archive' celery.log | wc -l    # sweep archives

# 3. Verify sweep is running daily
.venv/bin/python -c "from django_celery_beat.models import PeriodicTaskRunResult; \
    print(PeriodicTaskRunResult.objects.filter(task='core.tasks.sweep_diagnostic_deliverables').order_by('-id')[:7])"
```

**Decision rule for Phase 2 flip:**
- Missing-initiative count trending **down** week-over-week + sweep archive rate matching create rate → safe to flip §6.1 Phase 2 hard-reject (factory raises `OrphanDeliverableError` on `initiative_id=None` instead of marking diagnostic).
- Missing-initiative count **flat or up** → root-cause first (likely a caller that isn't passing `initiative_id`); don't flip yet.

## §6.2 decision (Rigby-ratified, session-close)

**Keep "require explicit `initiative_id`" as default** (Rule 3 from the recon). Reason: workspace-based inference is 0% assignable in DBZ; any forced assignment would be arbitrary. The diagnostic + TTL + sweep stack means the system is stable while we design a richer signal.

**Phase 2 attribution requires a new disambiguation signal. Four candidate directions — no commitment yet:**

| Option | Shape | Notes |
|---|---|---|
| **Projects layer (structural)** | New organizational level between Workspace and Deliverables: `Workspace → Project → Deliverable → Initiative (or as overlay)` | **Chris's exploration direction.** Directly responsive to recon ambiguity: narrows the inference domain from "which initiative in the workspace" to "which initiative in *this project*." Bigger IA change. Not implemented; design phase. |
| Agent → initiative affinity map (config) | Declarative table — e.g., `ResearchAgent` defaults to Initiative X unless overridden | Lower-risk, easy to audit. Rigby's lowest-risk pick if we don't take the structural route. |
| Tool-context propagation | Caller (agents/tools) must pass `initiative_id` explicitly; treat missing as defect, not as inference target | Hardens contract at the cost of more friction at the call sites. |
| Heuristics (title/content/recency) | Fuzzy match on deliverable signals | Last resort — noisy, creates silent mis-attribution. |

Top orphan creators (Rigby=33, ResearchAgent=24, ClaudeCode=11, ContentWriterAgent=9) are the input list for whichever direction we pick.

## Open items / what's next

| Priority | Item | Why |
|---|---|---|
| **P0** | `initiative_create` requires `target_workspace_id` | 68 DBZ deliverables can't have alignment evaluated; blocks full Plan C coverage |
| **P1 (time-gated)** | 7-day watch + Phase 2 hard-reject flip decision | Earliest 2026-06-29; playbook above |
| **P2** | `load_all_agents_advisors` baseline fix (155 → 87) | Pre-existing CONFLICT keeping CI red on main; admin-bypass currently required |
| **P2** | Local test DB infra (pgbouncer transaction pool blocks `CREATE DATABASE`) | Surfaces during Session 1195 PR #5; affects every `core/tests/*` file |
| **P3** | §6.2 Phase 2 attribution design — Projects layer (Chris's exploration) vs affinity map vs propagation vs heuristics | Eventual richer-signal replacement for Rule 3; structural Projects layer is Chris's lean per Rigby's Session 1195 close brief |
| **P3** | Direct ORM `.save()` bypass | Phase 1 hooks only cover factory + update tool path; signal could close the gap |

## Carryover from Session 1194 still relevant

- **PA LLM iteration cap silent failure** — deliverable `c2bac9c0-…`. Untouched this session.
- **Producer reroute regression vector** — deliverable `780a8d15-…`. Untouched.
- **PR-D contract flip** — deliverable `9d9db48a-…`. Untouched.

## Pin updates

- `tools/pa_local.sh` re-pinned to `pa-92bacb0fbcab44fb` (Session 1195 conversation, spun fresh at open per Rigby's Session 1194 close recommendation).
- `docs/PLATFORM_INVENTORY.md` regenerated at HEAD `603f90d0`.
- `docs/INDEX.md` rebuilt (945 active / 3 draft / 1733 superseded — same composition + this handoff).
- `CLAUDE.md` autoblock refreshed.

## Session metrics

- **10 PRs shipped** (#2397 → #2407, excluding none)
- **6 Plan C PRs in one session** — full vertical-slice contract from migration through observability
- **~1,200 lines added** to core (incl. tests + mgmt cmd + handoff)
- **Zero rollbacks**, zero hot-fixes
- **All 6 Plan C PRs admin-merged** (pre-existing CONFLICT)
- **Workers restarted twice** (PR #2 + PR #4 — task-imported code changes per memory rule)

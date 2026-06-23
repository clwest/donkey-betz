# Session 1222 v2 — Audit Revisit Close

**Status:** Supplemental close to [`SESSION_1222_CARRYOVER_QUEUE_CLEAR.md`](./SESSION_1222_CARRYOVER_QUEUE_CLEAR.md). Same session, second arc.
**Date:** 2026-06-23.
**Active conversation:** `pa-58737666f25741dc` (continued from Sessions 1217-1222).
**Prior close (same session):** [`SESSION_1222_CARRYOVER_QUEUE_CLEAR.md`](./SESSION_1222_CARRYOVER_QUEUE_CLEAR.md).
**Next session entry point:** Session 1223 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1223".

## TL;DR

After the carryover queue cleared (4 PRs through #2526), Chris asked us to revisit the original Session 1217 self-directed audit (deliverable `bec077ed-…`, 15 findings) and see what was still unaddressed now that bandwidth was free. Rigby ran a per-finding pass; I cross-checked against the PR ledger and corrected one mis-categorization. The corrected gap list was 8 still-open findings. Chris agree-all'd Rigby's top-3 leverage picks (C1, #3, B2). All three shipped same-session.

## Session Manifest (v2 arc)

### PRs merged

| # | Title | Audit finding |
|---|---|---|
| **#2527** | `feat(session-1222): clarify Opportunity pipeline scope (audit C1 PR A — label-only)` | C1 part 1 |
| **#2528** | `feat(session-1222): add scope='mine'|'all' to opportunity_manager_tool (audit C1 PR B)` | C1 part 2 |
| **#2529** | `chore(session-1222): enforce check-llm-sdk.yml — migrate 2 runtime sites, whitelist 4 operator-only (audit #3)` | #3 |
| **#2530** | `chore(session-1222): apply audit B2 decisions — annotate 4 disabled + re-enable Operator Edge w/ dry-run (P6)` | B2 |
| **(this PR)** | `docs(session-1222-v2): audit-revisit close + Session 1223 start-here` | — |

### Deliverables populated

| ID | Title | Final size | Purpose |
|---|---|---|---|
| `116bb6bd-2935-440b-bf69-1bcd7ee1ac9d` | Session 1222 P6 — B2 disabled beat tasks classification + decision card | (Rigby-created mid-arc) | Captured Chris's per-task picks before the migration shipped |

## Finding-by-finding close

### C1 (PRs #2527 + #2528) — Revenue pipeline metrics mismatch

The original audit framed C1 as "2,631 vs 47 inconsistency." DB verification this session turned that frame on its head:

| Metric | Value | Source |
|---|---|---|
| Total `Opportunity` rows | **2,631** | DB count |
| Owned by `system` user (spider-ingested freelance listings, 2026-06-13 → 2026-06-20, 100% <30d) | **2,584** | `filter(user_id=system)` |
| Owned by `chris` (46 freelance + 1 task, the curated subset he's engaged with) | **47** | `filter(user_id=chris)` |
| Orphans (NULL user_id) | **0** | — |

Both tool surfaces were correctly querying the same table with **different scopes**:
- `opportunity_manager_tool action=stats` → caller-scoped (47 when called as chris)
- `autopilot_tool.dry_run_report → revenue_pipeline.total_active` → platform-wide (2,631)

This is the **lead-discovery-pool pattern** — spiders seed Opportunity rows to the system user; users curate the rows they want into their own pipeline. The "inconsistency" was a *labeling* problem.

**PR #2527 (PR A, label-only)** — three sites updated:
- `pa_tool_schemas.py:91` — `opportunity_manager_tool` description gained explicit SCOPE block
- `td_handlers_ops.py:1721` — `dry_run_report` formatter gained a "Revenue Pipeline (platform-wide)" section
- `td_handlers_agents.py:437` — stats response gained `scope` + `scope_note` fields

**PR #2528 (PR B)** — added `scope='mine'|'all'` param to `opportunity_manager_tool.stats` and `list`:
- Default `'mine'` preserves the pre-Session-1222 caller-scoped contract
- `'all'` opt-in surfaces the platform-wide pool + `owner_breakdown` (top 10 user attributions) so the 2,600+ row spike is immediately interpretable

**Deferred:** Tier 3 retention prune of system-owned opps older than 30d. Not needed today (all 2,584 are <30d); shipping prune before labeling lands risks "lost leads" framing.

### #3 (PR #2529) — Enforce `check-llm-sdk.yml`

The workflow was `--warn-only` since Session 1098 PR #A2 because the repo had ~60 legacy direct-SDK call sites. Verification this session: **only 6 violations remained** (most migrated in intervening sessions).

Triaged:
- **Runtime paths migrated to `llm_call_wrapper.llm_call_span`** (2):
  - `core/agents/campaign_orchestrator_agent.py:660`
  - `core/services/curated_action_card_generator.py:245`
  - Pattern: `with llm_call_span(...)` block + `_span.attach_response(response)` + `# noqa: direct-llm-call — wrapped above` on the SDK line (the checker's indent-tracker pops at the multi-line `with`'s closing `):`).
- **Operator-only paths whitelisted** (4):
  - 3 management commands (`extract_initiatives_from_survey`, `draft_repo_verifier_claims`, `survey_external_repo`)
  - `scripts/one-off/rag_docs.py` (alongside the existing root `rag_docs.py` whitelist)

**Workflow flip:** dropped `--warn-only` from `.github/workflows/check-llm-sdk.yml`. Verified: `python tools/check_direct_llm_calls.py --root . --whitelist .ci/llm_whitelist.txt` returns exit 0.

**Both CI checks are now in enforce mode:** `check-reasoning-contract.yml` (PR #2525, Session 1222 P3 from the carryover arc) AND `check-llm-sdk.yml` (PR #2529, this arc).

### B2 (PR #2530) — Disabled beat task classification

DB query surfaced 5 disabled beat tasks. Chris's per-task picks (deliverable `116bb6bd-…`):

| Name | Decision |
|---|---|
| `backfill-spider-embeddings` | Keep off (backfill complete; resume on demand) |
| `scan-income-spider-orchestrator` | Keep off (superseded) |
| `scan-spider-opportunities` | Keep off — **Mode B (curate now)** per audit C1. Pool stays at ~2,584 until UI catches up; resume via manual trigger |
| `warm-up-spiders` | Keep off (spiders stay warm via normal use) |
| `generate-operator-edge-newsletter` | **ENABLE** with `dry_run=True` for 2-Friday burn-in |

Two changes shipped:
1. **`core/migrations/0364_session_1222_b2_beat_task_decisions.py`** — RunPython migration that sets `PeriodicTask.description` on the 4 keep-disabled rows (so future operators know WHY each is disabled and the resume path) AND re-enables the newsletter with `kwargs='{"dry_run": true}'`. Reversible.
2. **`core/celery.py`** — `beat_schedule` entry for the newsletter gains `'kwargs': {'dry_run': True}` so a fresh environment running `add_critical_celery_tasks --force` materializes the same safe-by-default state.

**Promotion path off dry_run:** after 2 successful Friday runs in preview state, flip kwargs to `{}` or `{'dry_run': false}` via a follow-up migration or the django-celery-beat admin UI.

## Net risk reduction (combined v1 + v2 close)

| Concern | Before Session 1222 | After Session 1222 |
|---|---|---|
| OpenAIProvider stub raising NotImplementedError if any caller routed through it | Real risk (deprecation stub, ABC contract held) | Class gone (verified zero callers all-time) |
| Reasoning-contract violations introduced silently | Warn-only CI | Enforce CI (PR #2525) |
| **Direct LLM SDK bypass introduced silently** | **Warn-only CI** | **Enforce CI (PR #2529)** |
| **Opportunity pipeline metrics confusion** | **2,631 vs 47 unlabeled** | **Both views labeled + opt-in scope param** |
| **Beat task purpose ambiguity ("why is X disabled?")** | **No annotation; some forever-disabled** | **4 annotated; 1 promoted to dry_run; Operator Edge revived** |
| 22 + 22 dormant agent classes adding noise to tool surface | Cluttered enum + dispatcher | Trimmed Session 1218 + 1222 P2 |

## What this session did NOT do (Session 1223 candidates)

The remaining 5 STILL OPEN audit findings (Rigby's deprioritized tail):

| # | Title | Effort | Notes |
|---|---|---|---|
| **#4** | Critical hub markers / gates | M | Reliability work; flag critical-path files so PRs touching them require extra review |
| **#6** | Docs drift: SERVICES counts | S | Reconcile `verify_doc_claims --only-drift` SERVICES count |
| **#7** | Docs drift: management command counts (182 vs 194) | S | Same family as #6 |
| **#8** | Seed baseline drift (155 expected vs 89/83 runtime) | M | `load_all_agents_advisors.py` expectation mismatch |
| **#9/#10** | Core orientation + Atlas positioning staleness | M | `docs/PLATFORM_WHAT_IT_IS.md` + `docs/24_7_GLOBAL_AI_APP_ATLAS.md` haven't been refreshed since Session 1141 |

Per Rigby's recommendation: **#6 + #7 (S+S together) is the natural next quick win** unless Chris wants the reliability work of #4. The Session 1223 start-here documents both paths.

## Memory updates worth carrying forward

No new feedback memories. Three existing rules dogfooded:
- `feedback_triage_decision_card_pattern.md` — three decision cards this arc (audit gap list, C1 root cause, B2 per-task picks). All used the lean + agree-all pattern.
- `feedback_rigby_collaboration.md` — Rigby caught one of her own mis-categorizations on the gap analysis (#1 marked open when it was closed) when I cross-checked against the PR ledger. Worth keeping the verification step.
- `feedback_corpus_walks_surface_mechanism_drift.md` — C1's "metrics mismatch" frame turned out to be a labeling drift, not a real bug. The walk surfaced the mechanism (lead-discovery-pool pattern).

## Files touched this v2 arc

```
core/services/pa_tool_schemas.py                                                (C1 PR A + B + #3 #noqa comments)
core/services/td_handlers_ops.py                                                (C1 PR A — dry_run_report section)
core/services/td_handlers_agents.py                                             (C1 PR A + B — scope/scope_note/owner_breakdown)
core/agents/campaign_orchestrator_agent.py                                      (#3 — llm_call_span migration)
core/services/curated_action_card_generator.py                                  (#3 — llm_call_span migration)
.ci/llm_whitelist.txt                                                           (#3 — 4 operator-only path whitelist additions)
.github/workflows/check-llm-sdk.yml                                             (#3 — enforce flip)
core/celery.py                                                                  (B2 — dry_run kwargs in newsletter beat entry)
core/migrations/0364_session_1222_b2_beat_task_decisions.py                     (B2 — NEW migration, 132 lines)
docs/handoffs/SESSION_1222_V2_AUDIT_REVISIT_CLOSE.md                            (NEW, this file)
00-START-NEXT-SESSION.md                                                        (Session 1223 FIRST THING rewrite)
```

Combined Session 1222 net delta (v1 + v2 arcs): **9 PRs merged** (#2522 → #2530 + #2531 incoming for this close), ~200 lines removed via the v1 carryover-clear arc + ~340 lines added/modified via the v2 audit-revisit arc.

# Session 1198 — §6.2 Phase 2 inference cascade + Repo Guardrails baseline fix

**Status:** Wrapped clean. **6 PRs merged on `main`** — first repo PR series in recent history with clean CI through the entire stack (no `--admin` bypass needed once #2424 cleared the long-standing CONFLICT).
**Date:** 2026-06-22
**Active conversation:** `pa-ea12236c83eb4826` (continued from Sessions 1196 + 1197).
**Prior session:** [`SESSION_1197_INITIATIVE_KIND_CLASSIFICATION.md`](./SESSION_1197_INITIATIVE_KIND_CLASSIFICATION.md).

## TL;DR

Two distinct ships landed on main in one session:

1. **PR #2424 — `Agents count claims` CONFLICT cleared.** The pre-existing `Repo Guardrails` CI red that had been forcing `--admin` bypass on every PR turned out to be a single misclassified line in `00-START-NEXT-SESSION.md`. Fix was a 970-line truncation of stale historical session blocks (already preserved in `docs/handoffs/`). First PR series in this session ran clean CI all the way through as a result.

2. **PRs #2425-#2429 — §6.2 Phase 2 inference cascade.** The Initiatives-First Backbone spec §6.2 had been `OPEN/defer` since Session 1194. Rigby + Chris locked the design via agree-all on `pa-ea12236c83eb4826`. Shipped as a 5-PR atomic series: model + seed cmd + pure cascade function + factory hook + tests/spec/ACs. Inference now runs in front of the Plan C Phase 2 hard-reject gate (2026-06-29), so callers omitting `initiative_id` get deduced attachment instead of `OrphanDeliverableError`.

## PRs shipped

| PR | Commit | Theme |
|---|---|---|
| **#2424** | `239930b6` | Baseline fix — truncate stale historical blocks in `00-START-NEXT-SESSION.md` (1280→312 lines); CONFLICT trigger was line 507 "(in-code, 51 agents)" with "Headline" elsewhere on the line propagating total-dimension classification |
| **#2425** | `a60a2040` | Migration 0363 — `AgentInitiativeAffinity` model + indexes (workspace, agent_name, initiative + composite for inference-time lookup) |
| **#2426** | `d470f82d` | `seed_agent_initiative_affinities` mgmt cmd — 2 conservative static seeds (ResearchAgent + ClaudeCode) |
| **#2427** | `2e9c83c5` | `infer_initiative_id()` pure cascade — 5-step kind-aware policy gates |
| **#2428** | `f2135eb0` | Hook into `deliverable_factory.create_deliverable()` — emits `[INFERENCE-MATCH]` log on attach |
| **#2429** | `996ea828` | 19-case regression suite + §6.2 ratified in `INITIATIVES_FIRST_BACKBONE.md` + AC16-AC19 |

## Behavioral invariants — what's now true post-merge

- **`Agents count claims` CONFLICT no longer fires** on canonical docs. CI's `Repo Guardrails` workflow goes green without `--admin` bypass. Verified end-to-end on PR #2424 itself.
- **`AgentInitiativeAffinity` table exists** with composite `(workspace, agent_name, expires_at)` index. 2 static-seed rows live in local Donkey Betz workspace.
- **`infer_initiative_id()` is callable from any code path** that has `(payload, owner_agent)`. Pure function, read-only, no side effects.
- **`deliverable_factory.create_deliverable()` runs inference BEFORE Plan C Phase 1 diagnostic.** Caller-supplied `initiative_id` always wins; inference only fires when missing.
- **`[INFERENCE-MATCH]` log emits at INFO** with structured fields (`agent`, `workspace`, `initiative`, `step`, `confidence`, `reason`). Separate channel from `diagnostic_payload` so inference observability is decoupled from orphan diagnostics.

## §6.2 cascade — the locked design

```
Step 1 — payload.initiative_id        → confidence 1.00  (authoritative)
Step 2 — tool_context.initiative_id   → confidence 0.95  (propagated)
Step 3 — AgentInitiativeAffinity      → kind-policy-aware
Step 4 — heuristics (topic overlap)   → PR3 follow-up (stub)
Step 5 — fall through                 → caller decides (diagnostic / reject)
```

### Kind-aware policy gates (Step 3 + Step 4)

| Initiative kind | Candidates | Recency | Confidence floor |
|---|---|---|---|
| `project` (STRICT) | exactly 1 | ≤ 7 days | ≥ 0.90 |
| `investigation` (BOUNDED) | exactly 1 | ≤ 30 days | ≥ 0.70 |
| `recurring_artifact` | — | — | **never** auto-attach |
| `spec_backlog` | — | — | **never** auto-attach |

Rationale: investigations are catch-all research buckets, tolerate looser attachment; projects have finish-line semantics, need tight confidence; recurring artifacts and spec backlogs are explicit-only containers (avoid the "junk drawer" failure mode).

### Hard stops (all steps)

- **Cross-workspace** — `initiative.target_workspace_id != payload.workspace_id` → invalid.
- **Multiple valid candidates at Step 3** → fall through (don't auto-pick; ambiguity surfaces via trace).
- **Expired affinity rows** (`expires_at < now`) → ignored.
- **Authoritative sources only** for Step 3: `static_seed` + `manual_pin`. `learned_suggestion` rows surface in operator reports but DON'T auto-attach (Rigby's v1 restriction).

## Static seeds shipped

| Agent | Target Initiative | Confidence | Rationale |
|---|---|---|---|
| ResearchAgent | Spider Context Utilization — Retune & Implementation (3b) | 0.92 | ResearchAgent owned Sessions 1187-1189 recon that produced this Initiative's retune list. Natural follow-on. |
| ClaudeCode | Initiatives-First Wiring + No-Orphan Output (spine 1) | 0.90 | ClaudeCode shipped backbone work Sessions 1194-1198. Default attach target. |

Top orphan creators intentionally NOT seeded:

- **Rigby (33 orphans):** coordinator agent that touches every workstream; no single Initiative is the right default. Falls through to heuristics (PR3) or diagnostic mark.
- **ContentWriterAgent (9 orphans):** natural target is `Business News Tracker — June 2026` (kind=recurring_artifact). recurring_artifact is hard-blocked from auto-attach. Operator-pin via `manual_pin` if needed.

## Local apply outcome on Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)

```
AgentInitiativeAffinity rows seeded:  2
Inference cascade verified:           ResearchAgent → 3b Retune (step=3, conf=0.92)
ClaudeCode affinity:                  → spine Initiative 1 (step=3, conf=0.90)
Unknown agent fall-through:           → step=5 no_inference_match → Plan C Phase 1 diagnostic
Explicit initiative_id (any kind):    → step=1 immediate (caller opted in)
Cross-workspace explicit id:          → cascade continues (never auto-attaches across)
```

End-to-end smoke test on main (post-merge):

```
agent=ResearchAgent + workspace=DBZ + no initiative_id →
  [INFERENCE-MATCH] step=3 confidence=0.92 reason=affinity_match
  initiative=23cf3acb (Spider Context Utilization Retune)
  Deliverable saved with inferred initiative_id ✓
```

## Rollback / disable levers

| Surface | Lever | Effect |
|---|---|---|
| Migration 0363 | `python manage.py migrate core 0362` | Drops `AgentInitiativeAffinity` table. Additive-only — safe rollback. |
| Static seeds | `AgentInitiativeAffinity.objects.filter(source='static_seed').delete()` | Wipes 2 seeded rows. Re-run `seed_agent_initiative_affinities --apply` to restore. |
| Inference cascade entirely | Comment out the `infer_initiative_id` call in `deliverable_factory.create_deliverable()` (line ~684) | Hot-rollback to pre-Session-1198 behavior. Falls back to Plan C Phase 1 diagnostic for orphans. |
| Per-row affinity disable | Set `expires_at = now()` on the row | Skipped at inference time. Non-destructive. |
| `[INFERENCE-MATCH]` log noise | Adjust logger level for `deliverable_factory` to WARNING | Suppresses INFO logs without disabling inference. |

The whole ship is data-layer reversible. Worst case is `migrate core 0362` + the model file drop, which loses 2 seed rows + inference behavior but doesn't damage upstream FK relationships.

## What's deliberately NOT in scope

- **Step 4 heuristics (topic overlap)** — stubbed at "returns None / reason=heuristics_not_yet_implemented". PR3 follow-up after we watch Step 3 behavior for a week.
- **Tool-context propagation** — Step 2 of cascade is wired in `infer_initiative_id()` but `create_deliverable()` doesn't currently pass `tool_context`. Requires touching every caller of `create_deliverable` to plumb `tool_context.initiative_id` through. Filed for Phase 2 follow-up.
- **Learned-suggestion auto-attach** — model supports the source enum value, but inference function ignores it. Promotion path needs a feedback signal we don't yet have (which Initiative did the user actually intend? — no signal exists).
- **Manual pin mgmt cmd** — operator escape hatch documented in the seed cmd docstring; no dedicated cmd shipped this session. Add when actual operator demand surfaces.

## Open items for Session 1199

| Item | Priority | Notes |
|---|---|---|
| **Session 1197 24h watch on `default_only_projects`** | **P1 (time-gated)** | Starts **2026-06-23** (today/tomorrow depending on local TZ). Daily `report_initiative_kinds --workspace-id <DBZ>` re-run. Confirm new project rows aren't filed without classification. |
| **Plan C 7-day watch + Phase 2 hard-reject flip** | **P1 (time-gated)** | Start **2026-06-29**. Inference cascade now sits in front of the reject point — Phase 2 flip is safer than pre-Session-1198. |
| **Session 1196 7-day watch** | **P1 (time-gated)** | Start **2026-06-29**. Re-run `backfill_initiative_workspace_links --json-only` and diff against 2026-06-22 baseline. |
| **PR3 — Step 4 heuristics implementation** | P2 | After Step 3 affinity behavior settles. Topic-overlap embedding + recency + owner_match per Rigby's §6.2 framing. |
| **Manual pin mgmt cmd** | P3 | `affinity_pin --workspace X --agent Y --initiative Z` — when operator demand surfaces. |
| **Rigby + ContentWriterAgent seed call** | P2 | Currently unseeded by design; revisit after watching inference accuracy for 1 week. Rigby is coordinator agent; ContentWriterAgent's natural target is recurring_artifact (blocked). |
| **Tool-context propagation** | P2 | Plumb `tool_context.initiative_id` through `create_deliverable` callers so Step 2 of cascade activates. Requires touching ~10 callsites. |
| **Local test DB infra (pgbouncer blocker)** | P2 | Re-surfaced AGAIN in Session 1198 PR1E. Tests pass CI but blocked locally. Add `DJANGO_TEST_DATABASE_URL` support OR document the docker-compose path. |
| **Migration drift audit (Set A + Set B)** | P2/P3 | Each Session 1196/1197/1198 migration trimmed these by hand. Time to actually fix the drift OR add a `.gitignore`-style exclusion in `makemigrations`. |
| **PA LLM iteration cap silent failure** | P2 | Carryover from Session 1193 (`c2bac9c0-…`). Bit during Session 1197 memory cleanup. Still unfixed. |
| **PR-D contract flip** | P2 | Carryover from Session 1194 (`9d9db48a-…`). 24h WARN-volume gate elapsed 2026-06-22. |

## Memory candidates (saved + indexed this session)

1. **`feedback_context_kit_headline_propagates_total.md`** — context-kit's `Headline` strong-token propagates total-dimension classification to every number on the same line. One bad line in canonical docs = `Agents count claims` CONFLICT. Diagnostic recipe + canonical-doc cleanliness rule included.
2. **`feedback_core_models_py_is_dead_code.md`** — u-d-b has BOTH `core/models.py` AND `core/models/` package. Python prefers the package, so any `from .models_X import *` added to `core/models.py` is silently ignored. Symptom: new model loads via direct import but `makemigrations` doesn't see it. Fix: import in `core/models/__init__.py`. Bit me for 10 min on PR1A.

Both saved + indexed in `MEMORY.md`. Future sessions skip these traps.

## Bug filed forward

**Deliverable `cfc7db23-1f9d-4ba7-9dfa-67034cf25265`** in Donkey Betz workspace, linked to Initiative `20d520c6-…` (Session 1197 umbrella). Title: "Rigby: PA UserMemoryContext importance score is broken — all auto-extracted memories get importance=9". Includes reproduction, root cause hypothesis, 3 impact points, 3 recommended fixes, tooling gap note. P2.

Surfaced during Session 1198 Rigby memory store cleanup (216 noise entries removed via ORM bypass; final count 89). The importance score uniform-at-9 broke our ability to purge by importance — required content-prefix filtering instead.

## Pinned reference (Donkey Betz workspace)

- **Workspace ID:** `b4503364-2573-4401-9e28-61a739e0ce50`
- **Initiative count (Session 1198 close):** 42 total (unchanged from Session 1197 close — no new Initiatives created this session)
- **Affinity rows:** 2 (ResearchAgent + ClaudeCode)
- **Spine Initiatives:** still 3 ACTIVE, all kind=project, all in `default_only_projects` detector flag list (expected, real long-arc projects)

## Collaboration shape

- **Claude owned:** the 5-PR series + the baseline fix PR + the memory store cleanup + the bug filing.
- **Rigby owned:** the locked §6.2 design memo (cascade structure + kind-aware policy gates + storage shape + hard stops + trace shape), QA1/QA2/QA3 design ratification, and the static seed sanity check on the 2 chosen agents.
- **Chris owned:** the agree-all ratifications on (1) Rigby's §6.2 design, (2) the 5-PR scope, (3) the merge sequencing, and the "purge lowest-importance and re-save" call on Rigby's memory store overflow.

The day moved fast because:
- Session 1197's kind enum gave inference a richer signal shape than pre-1197 design assumed (kind-policy gates were the post-1197 add)
- Session 1196's no-orphan contract gave us a clean integration point (`_evaluate_initiative_alignment` already lives in the right place; inference sits cleanly upstream)
- The baseline fix removed the `--admin` crutch so PRs land with clean CI

---

**Conversation thread `pa-ea12236c83eb4826`** is still open at session close. Session 1199 can continue on it or spin fresh.

**No prod actions taken** — local-only per memory rule. The migration + seed + inference cascade all ran against local DB. Production rollout would follow the standard playbook: apply migration + seed cmd + worker restart (no new `@shared_task` in this session, but a doc on the rollout sequence should land before 2026-06-29 to coordinate with the Phase 2 hard-reject flip).

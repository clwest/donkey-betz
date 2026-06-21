# Session 1188 — Spider Context: C-trace #3 PR-1 + PR-2 + vocabulary recon

**Status:** 2 PRs merged (both `--admin` bypass on pre-existing `Agents count claims` CONFLICT, Chris-approved). 1 PR-3 spec filed for Session 1189 pickup. 1 missing-PA-tool spec appended.
**Date:** 2026-06-21
**Pinned conversation:** `pa-6658d90a3e4942b3` (fresh Session 1188 thread spun by Rigby at session open; prior `pa-10df024c0bd8` was at health 60-75/100 at Session 1187 close).
**Prior session:** [`SESSION_1187_UTILIZATION_RECON.md`](./SESSION_1187_UTILIZATION_RECON.md) (7 recon deliverables filed in Local QA, zero code).

## TL;DR

Acted on Session 1187's C-trace remediation #3 (register Hot agents in `SpiderContextBuilder.AGENT_SPIDER_MAPPINGS`). Routed scope through Rigby per scope rule. Her PR-prep recon (deliverable `51062b8c-...`) **inverted part of the framing**: ImageAgent + ResearchAgent already substring-matched their existing patterns; only ThinkingAgent was the actual miss. PR-1 added all three explicit Hot-agent keys for trace clarity; PR-2 ran a SpiderData supply recon and **surfaced a platform-wide vocabulary mismatch** — `'creative'`, `'crypto'`, `'sports'` are dead keys (zero supply), and `ai_ml` (364 actionable / 30d) wasn't referenced by any agent. PR-2 fixed Image+Research specifically; PR-3 spec covers the rest.

## What landed (this session)

| PR | Commit | Theme | Verified |
|---|---|---|---|
| **#2380** (PR-1) | `6691d408` | `feat(session-1188-spider-context)` — explicit `imageagent`/`researchagent`/`thinkingagent` keys in `AGENT_SPIDER_MAPPINGS`. Image/Research mirror substring outcomes (no functional change); Thinking moves off `default` to `['tech','news','science','financial']`. | 5/5 unit tests in new `core/tests/test_spider_context_builder_mappings.py`; CI `--admin` bypass on pre-existing CONFLICT (not caused by PR — didn't touch docs). |
| **#2382** (PR-2) | `ab9274e3` | `feat(session-1188-spider-context)` — retunes `imageagent` → `['design','visual_trends','video','tech','entertainment']` (drops dead `'creative'`); `researchagent` adds `'ai_ml'`+`'business'` (largest research-relevant supply buckets it was missing). | 5/5 unit tests pass after retune; CI `--admin` bypass on same CONFLICT. **Replaces #2381 which auto-closed when its base branch (#2380 feature branch) was deleted on merge.** |

## Key finding — the vocabulary mismatch

PR-2 supply recon (executed via one-off `/tmp/pr2_spider_supply_recon.py`; Rigby's snippet + a defensive discovery pass) ran 30d aggregation of `SpiderData` by `data_type` with `is_actionable=True`. **5,967 total actionable rows across 42 distinct `data_type` values.**

The current `AGENT_SPIDER_MAPPINGS` dict treats values as semantic categories, but the read path queries by `SpiderData.data_type`. Mismatch findings:

| AGENT_SPIDER_MAPPINGS key | actionable_30d | Status |
|---|---:|---|
| `creative` | **0** | Dead — real buckets are `design` (31), `visual_trends` (32), `video` (24) |
| `crypto` | **0** | Dead — real bucket is `blockchain` (79) |
| `sports` | **0** | Dead — real buckets are `sports_odds` (335) + `sports_news` (161) |
| `ai_ml` | n/a | **Not referenced by any agent** — but has 364 actionable / 30d (2nd-largest tech-adjacent supply) |
| `business` | n/a | Not referenced — 92 actionable / 30d |

PR-2 fixes ImageAgent (was getting zero from `creative`) and ResearchAgent (was missing `ai_ml`+`business`). PR-3 covers the rest.

## Deliverables filed

| ID | Title | Purpose |
|---|---|---|
| `51062b8c-0fdf-4ca9-855a-264962e2506c` | Rigby PR-1 spec (Hot-agent mapping recon + AC) | Rigby's recon that found ImageAgent + ResearchAgent already substring-match; drives PR-1 scope. |
| `a48e1164-edc6-49d8-bc70-135bedb614a9` | Rigby PR-3 spec (vocabulary bridge) | Alias layer design (`creative` → design+visual_trends+video, `crypto` → blockchain, `sports` → sports_odds+sports_news), `ai_ml` rollout targets, AC, recommended PR-3A/PR-3B breakdown. Implementation deferred to Session 1189. |
| `13032820-1f36-4a1c-8843-6a9d53653405` | Missing PA tools (appended) | Rigby appended +2491 chars specifying a SpiderData aggregation PA tool: group-by `data_type` with filters `is_actionable` + `created_at >= window`, optional samples per group. Came up twice in two sessions — recurring need. |

## How the collaboration worked (Rigby vs Claude lanes)

Per Chris's session-open reinforcement (*"if Rigby can do it she needs to be able to do it"*), every recon was routed to Rigby first:

- **Rigby owned:** PR-prep mapping audit + 30d telemetry baselines per agent + AC drafting (her tools), tool-gap spec authoring + delivery of missing-tool spec to deliverable, scope-call decisions (split A/B/C, narrow vs wide), direct message to Chris on CI bypass decision.
- **Claude owned:** code edits to `core/services/spider_context_builder.py`, new test file, executing the one-off Django shell script Rigby specced (where her tools hit a real gap), PR opening + commit hygiene + admin merge.
- **Tool gap surfaced and filed**, not silently bridged. Rigby explicitly said "I cannot truthfully produce the aggregation from the PA tool surface right now" and named the missing capability for the build queue.

## Operational notes

### CI `--admin` bypass — pre-existing `Agents count claims` CONFLICT

Both PRs tripped the same pre-existing CONFLICT (`context-kit verify` finds 220+ canonical doc claims, 2914+ supporting matches, 7948+ historical mentions of varying agent counts ranging 1-469). Chris approved blanket `--admin` bypass for this session. Same pattern as Session 1183 PR #2357.

**Recommendation:** at some point a dedicated inventory-refresh PR should reconcile the agents-count drift so future PRs don't need bypass. Not in this session's scope.

### PR stacking footgun — base-branch deletion auto-closes child PRs

`gh pr merge --delete-branch` on PR-1 deleted the feature branch that PR-2 was based on, which **auto-closed PR-2 (#2381) unrecoverably** (`gh pr reopen` failed because base branch is gone). Fix: rebased branch onto fresh main, opened fresh PR #2382 with the same commit.

**Lesson for future stacked PRs:** retarget the child PR's base to `main` BEFORE merging the parent (the `gh pr edit <child> --base main` call only works while both PRs are still open). Memory-worthy pattern.

### Local environment

- Stack confirmed local via `platform_config_tool overview` at session open — `service_context: local`, `railway_environment: local`.
- Disk 106 GiB free, no pressure.
- All 5 celery workers + beat + daphne running cleanly throughout session.
- New conversation `pa-6658d90a3e4942b3` health 100/100 at session close.

## Follow-on for Session 1189

### P1 — PR-3 implementation (vocabulary bridge)

Spec lives in deliverable `a48e1164-edc6-49d8-bc70-135bedb614a9`. Rigby recommended splitting PR-3 into:
- **PR-3A** — alias/normalization layer + drop dead keys
- **PR-3B** — systematic retuning of remaining agents + `ai_ml` rollout

Read Rigby's spec first, then route scope through her before code.

### P2 — 7d AC watches from PRs #2380 + #2382

Starts 2026-06-28. Rigby's measurable AC:
- ImageAgent: `categories_queried` includes `design`/`visual_trends`/`video`; ≥1 dispatch with `has_data=True` against any of those.
- ResearchAgent: `categories_queried` includes `ai_ml`+`business`; ≥1 dispatch with `has_data=True` against `ai_ml`.
- ThinkingAgent: ≥3 dispatches with spider context built, ≥1 with `has_data=True`.

### P3 — Missing PA tool: SpiderData aggregation

Spec in deliverable `13032820-...`. Recurring need (2 sessions in a row). Build order in the deliverable.

### P4 — Carryover from Session 1186

- `48b73b04-373a-4d25-b263-9925c7c1a084` — B.1 unify Initiative-stage deliverables (waiting for bucket 4 paths to settle).
- `9d9db48a-4819-4e2b-9548-998c0fe2f8f5` — PR-D contract flip 24h WARN-volume watch (started 2026-06-21 16:00; check after 2026-06-22 16:00).

## Memory candidates from this session

1. **PR stacking + base-branch deletion footgun** — `gh pr merge --delete-branch` on parent auto-closes child PR unrecoverably. Workaround: retarget child to `main` before merging parent.
2. **Substring-matching dicts hide "missing" entries** — `SpiderContextBuilder._get_agent_categories` uses `if pattern in agent_lower`, so an agent appears mapped when it just happens to substring-match an unrelated key. Always check the matching mechanism before concluding an entry is missing.
3. **Vocabulary mismatch between mapping dicts and runtime data** — the AGENT_SPIDER_MAPPINGS dict uses semantic names (`creative`, `crypto`, `sports`) that don't match actual `SpiderData.data_type` values (`design`/`visual_trends`/`video`, `blockchain`, `sports_odds`/`sports_news`). When wiring/routing dicts have low signal-to-noise, check the runtime values first.

These should be captured in memory at session-end (Claude task before close).

# Session 3036 — Actor field threading through canonical-lifecycle broadcast

**Closed:** 2026-07-29
**HEAD at close:** `8080acee5` (PR #3763 merged) + docs cascade + wrapper pin bump
**Session shape:** Flow B spec→ship (single PR), 22-session zero-hallucination Rigby SIGN streak, 21st consecutive Cycle 1A verify-before-build session.

---

## What shipped

**PR #3763 (`8080acee5`) — `feat(s3036): actor field threading through canonical-lifecycle broadcast`.** 14 files, +498/-24 (+33/-10 A2 fold-revision commit folded in same envelope). NEW `core/tests/test_s3036_actor_threading.py` (12 tests). Full S3026→S3036 canonical-lifecycle regression bundle 50/50 passing.

### 7-value actor taxonomy

Threaded through both `emit_canonical_*_broadcast()` helpers, all 10 production call sites, the `canonical_decisions:recent` Redis ring, the `/api/boardroom/lifecycle-activity/` polling endpoint, and the BoardroomTab lifecycle activity panel:

- `human` — single boardroom endpoint (views 2270, 2328)
- `human-bulk` — bulk boardroom endpoints (views 2435, 2530)
- `human-gate` — gate-decline path (views 3922)
- `pa-tool` — Rigby PA tool handlers (td_handlers 6057, 6106)
- `ai-promoter` — AIDecisionPromoterService (ai_decision_promoter 205)
- `ops-task` — Celery auto-approve boardroom items (tasks_ops 309)
- `rules-service` — S589 rules service (decision_promotion_rules 202)

Centralised in `core/services/canonical_decision_broadcast.py` as `ACTOR_*` constants + `CANONICAL_LIFECYCLE_ACTORS` frozenset. Call sites import the constant rather than pass string literals so typos surface at import time (NameError) rather than as "unknown" pill regressions in the UI.

### Schema handling

`schema_version` bumped 1→2 to signal presence of `actor`. v1 events already in the ring at deploy time round-trip cleanly through the polling endpoint (frontend renders missing/unknown as neutral "unknown" pill). No dual-key back-compat needed since we own the only consumer.

### Frontend BoardroomTab

`ACTOR_PILL_STYLES` map (7 colored pill entries — blue/cyan/orange/purple/amber/teal/green) + `UNKNOWN_ACTOR_STYLE` neutral fallback + `resolveActorStyle()` helper handles both missing key AND unknown-string typo cases (Rigby T1 Fold #1 `same_pr_mitigatable` mitigation).

---

## Discharges S3035 T1 Fold `deferred_2nd_trigger_watch`

Chris's live view of the BoardroomTab lifecycle panel at S3035 close observed: "most of the last 13 lifecycle events are rejections — that's real signal." S3036 answers the natural next question: "who rejected them?" First operator ask would have flipped the fold from 1st→2nd trigger; shipping now closes it.

---

## SIGN cycles (PLAYBOOK-7.7.2)

- **T1 SIGN (spec):** AGREE_WITH_REVISIONS, 5/5 dimensions AGREE, 8+ `repo_tool` runs. Rigby verified 10 call sites, adjacent emit_* helper families, downstream consumers, tests locking old shape, schema_version==1 assumption sweep. Zoom-out folds: #1 same_pr_mitigatable (frontend unknown-string fallback + backend central constant list) — both folded same-envelope; #2 future_trigger (`typing.Literal[...]` enforcement) — deferred.
- **A2 SIGN (implementation):** initial AGREE_WITH_REVISIONS caught (a) docstring↔test drift where the helper docstring claimed "parameterized 10-site test bundle" but only 3 service-layer sites are directly covered, and (b) 3 missing evidence dimensions (BoardroomTab.tsx read, adjacent emit_* re-sweep, canonical_decisions:recent consumer sweep, schema_version==1 residual sweep). Same-envelope revisions: docstring rewritten with accurate 3-direct + 7-transitive split, S3036 test v1 fixture annotated as intentional. A2 verdict flipped to READY-TO-MERGE.

**22 sessions continuous SIGN streak. 21 consecutive verify-before-build.** T1 SIGN drove correct scope-shape early (7 actor kinds, not 6; helper-level central constant list; frontend fallback for unknown-string not just missing-key). A2 SIGN caught real docstring drift that would have shipped as false enforcement claim.

---

## Chris D-verdicts

- **Direction (Option A actor-threading pick):** RATIFIED — "let's go with A since it's a recommendation."
- **Spec (7 actor kinds, defensive default, badge-only UI, schema_version bump 1→2):** RATIFIED — "Ratify — proceed to Phase 6 implementation."

---

## Folds persisted (PLAYBOOK-6.10.8)

Same-envelope RESOLVED:
- T1 Fold #1 `same_pr_mitigatable` — actor taxonomy = silent wire-contract; mitigated via frontend unknown-string fallback + backend central constant list.
- A2 Fold #1 `same_pr_actionable` — docstring↔test drift; mitigated via accurate 3-direct + 7-transitive split language in module docstring + S3036 test module docstring.
- A2 Fold #2 `same_pr_actionable` — v1 fixture at test_s3036_actor_threading.py:316 needed explicit "intentional" annotation; done.

Future_trigger carries forward:
- **T1 Fold #2** — `typing.Literal[...]` type-enforcement on `actor` param to catch typos at import time rather than test time. Too invasive for S3036 envelope; watch for 2nd trigger.
- **A2 Fold (new)** — actor taxonomy registry + frontend palette mapping must evolve together. Fallback prevents UI breakage but silently hides typos as "unknown" until someone notices in ops. Consider generating TS constants from backend or shared schema in future.

---

## Cross-cutting workflow references

- **Constitutional governance:** CLAUDE.md Playbook **v0.11.0** (S3036 is net-new schema extension, not drift/hardening; PLAYBOOK-7.7.5 does not fire; no amendment this session).
- **ADR corpus:** ADR-0001 through ADR-0008 (no new ADR this session).
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (S3036 planned end-to-end from S3035 00-START Option A candidate #1).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **1× substantive T1 SIGN (8+ tool_runs) + 1× substantive A2 SIGN (2 dispatch rounds, 12+ tool_runs total across both). Zero rubber-stamp. 22 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Applied on scope-shape decisions (`human-gate` split + BADGE-ONLY vs filter-dropdown) with "do we lose anything / more work later" framing.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` post-merge (frontend touched); Vite rebuild fired via `HEAD~1..HEAD` path-match on `frontend/src/**`; event recorded in `logs/recycle_events.jsonl` sha=8080acee598a.
- **Fold classification (PLAYBOOK-6.10.8):** 5 folds classified this session (3 same_pr resolved + 2 future_trigger persisted).
- **Verify-before-build (Cycle 1A):** **21st consecutive session** — T1 verify pass (10 call sites confirmed pre-spec via `emit_canonical_*_broadcast(` grep; frontend BoardroomTab structure read before draft; existing helper module read to understand event dict shape); A2 verify pass (docstring drift caught before merge, not after).

---

## Session opens with

**S3036 close smoke test** — Chris to open Workspace → System → Governance → "Recent Lifecycle Activity" (expand), then promote OR reject a draft decision from the BoardroomTab. Within 10s the panel should show a new entry with a colored actor pill next to the timestamp. Pill color should match the source (human = blue for single-click, cyan for bulk).

---

## Twin-pointer

**Repo docs:**
- `docs/handoffs/SESSION_3036_ACTOR_THREADING.md` (this file — current close)
- `docs/handoffs/SESSION_3035_BOARDROOM_LIFECYCLE_ACTIVITY.md` (the panel S3036 extends)
- `core/services/canonical_decision_broadcast.py` (helper + taxonomy authoritative source)

**Workspace UI:**
- Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`
- PR #3763 https://github.com/clwest/donkey-betz-platform/pull/3763
- Chief of Staff Escalation deliverable `de861fe2-17ec-4a4a-a1e3-5a4371335812` (open ask — see next section)

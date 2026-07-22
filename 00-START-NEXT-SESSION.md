# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2887 CLOSE → S2887 side-step arc shipped (GTM audit + repo_tool cross-repo + Character OS EB.4 + Postgres port collision fix + C3 bridge-answer persistence) (2026-07-22; picks up as S2888) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2887 close).** S2887 pivoted at open from the queued Ledger #13 `td_error.py` extraction into a Chris-directed GTM-focused side-step. **4 PRs merged across 2 repos.** All Chris D-verdicts inline in the audit doc; R1a proposal rejected as architectural mis-fit (character-os is not a fleet app); C1 EB.4 + C3 ratified as concrete first + second moves.

- **u-d-b PR #3398** `b929e5be7` — `repo_tool` cross-repo scoping (`repo_id` param + `list_repos` action + security widening + `permission_denied` taxonomy fix + 2 profile `root_path` fixes; 57 tests pass).
- **character-os PR #2** `8cbf181` — EB.4 SPA settings panel for per-workspace `EngineConnection` (476/476 vitest pass; +6 new EB.4 tests).
- **character-os PR #3** `348aed8` — Postgres port collision fix (docker mapping `5433:5432` → `5434:5432`); companion parent-workspace edits to `scripts/start-character.sh` (source `.env` at startup) + `Makefile` (`:5434` wait-loop).
- **character-os PR #4** `dc67d2e` — C3 bridge-answer Asset persistence (new `AssetRole.BRIDGE_ANSWER` + migration `0011_c3_bridge_answer_role` + shared `create_bridge_answer_asset` helper + sync dispatch mirror; 912/912 realtime+compositions pass).

Full session context: `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md`.
Audit doc: `docs/investigations/2026-07-22_RIGBY_SAAS_AND_COS_BRIDGE_GTM_GAP_AUDIT.md`.
Workspace mirror: deliverable `60cc462b-3abf-4cae-a809-cdb3b538f284` in Donkey Betz workspace.

---

## S2888 open sequence

### Step 1 (FIRST THING) — Ledger #13 `td_error.py` extraction

The **original S2887 first-action** pushed one session by the GTM side-step. Still queued; adopter gate MET at S2886 close (6/6). No architectural change, no design SIGN needed.

Adopter files (all in `core/services/`): `td_handlers_govern.py`, `td_handlers_ops.py`, `td_handlers_agents.py`, `td_handlers_content.py`, `td_handlers_newsletter.py`, `td_handlers_core.py` (also `td_handlers_gateway.py` has its own `_tool_error` but Rigby said keep that separate at S2875 Q3=A).

Extraction plan:
1. New file `core/services/td_error.py` — module containing the canonical `_handler_error` helper (byte-identical to what's in the 6 adopter files' file-local copies).
2. Update 6 adopter files' import blocks: `from core.services.td_error import _handler_error`.
3. Remove 6 file-local `_handler_error` copies (~28 lines × 6 files = ~168 lines removed).
4. Verify combined regression suite (S2879 → S2886 + `test_zoom_out_tool_2780`) still passes 100/100.
5. Ensure no circular imports (each adopter file already imports from `core.services.*`; new leaf module should be safe).

**Expected diff:** ~30 lines added (new file + 6 import lines), ~168 lines removed. Net **~-140 lines**. Single PR.

**Rigby SIGN Q1 (routing map):** verify at HEAD that the 6 copies are byte-identical (or differ only in docstring session-number attribution). If they diverge on shape, extraction needs a shape-reconciliation SIGN cycle before proceeding.

**Rigby SIGN Q_zoom_out:** any concerns about naming (`td_error.py` vs `td_handler_error.py` vs `handler_envelope.py`)? Any adopters where the file-local docstring adds meaningful context that would be lost in a shared module?

### Step 2 — Playbook v0.9.0 amendment cycle (2 rules at 2nd trigger from S2886)

1. **Fold 1 (2nd trigger): `TransactionTestCase` discipline for dispatcher-DB tests.** S2885 (1st) + S2886 (2nd). Rule shape: "Handler tests that require `setUp`-created ORM fixtures to be visible to `ToolDispatcher.execute_sync` MUST inherit from `TransactionTestCase`, not `TestCase`." Candidate slot: **PLAYBOOK-6.10.11** or **PLAYBOOK-7.4.5**.
2. **Fold 2 (2nd trigger): Shared-taxonomy branch fortification.** S2885 (1st) + S2886 (2nd). Rule shape: "When multiple return branches within a single handler emit the same `error_code`, the migrated-envelope test MUST assert either the distinguishing `action` field or a message-body substring to prevent false-pass on branch-crossing." Candidate slot: EXTENDS **PLAYBOOK-6.10.9** or fresh sibling rule.

Both are ratifiable in a single MINOR amendment cycle (v0.9.0) — 2-rule slate at 2nd trigger each is within the shape ratified for v0.7.0 (2-rule slate) and v0.8.0 (1-rule slate).

### Step 3 — Live UI dogfood of EB.4 + C3 (Character OS side)

Reference-customer verification loop. Open the running character-os SPA at `http://localhost:5174`:

1. Navigate to `/settings/engine-connections`.
2. Configure a connection: URL = u-d-b's PA endpoint (`http://localhost:8000`), token = a fresh DRF token for Chris's user on u-d-b, label = "Local u-d-b".
3. Hit `test_ping` — expect 200 with real latency.
4. Start a realtime session with a spokesperson.
5. Ask a question that would trigger `consult_engine` (portfolio-level context question).
6. Verify a fresh `Asset(role=BRIDGE_ANSWER)` appears in `/workspace/assets/?role=bridge_answer` with the answer in `inline_content`.

This is the audit's ratified reference customer path. If any step fails, the failure IS the next item to fix.

### Step 4 — Net-new engineering candidates for S2888 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2887 close — Ledger #13 `td_error.py` extraction.** See Step 1.
2. **NEW at S2887 close — Playbook v0.9.0 amendment cycle.** See Step 2.
3. **NEW at S2887 close — EB.4 + C3 live dogfood.** See Step 3.
4. **NEW at S2887 close — Character OS side C4 PD-1 timeout fix.** Sev-1 defect: Django `MediaEngineClient` 60s timeout fires before media-engine's ~63s Runway poll. Blocks reliable realtime session start in real mode. Character OS-side only.
5. **NEW at S2887 close — Character OS side C5 non-realtime bridge invocation + C6 tool catalog.** Follow-on from audit §3.2.
6. **NEW at S2887 close — Rigby Tool Gap Ledger review.** 1 new entry accreted at S2887 open (repo_tool cross-repo, RESOLVED same-session via PR #3398). Consider a slate PR that picks 1-2 open ledger items.
7. **Carried from S2886 — everything from S2886 open Step 4** items 5-47, unchanged.

### What's forbidden at S2888 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC). Rejected at S2887 as architectural mis-fit. See audit §6.5.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution.
- R1 fleet reject-mode flip — deferred; fleet HMAC path dormant per S2887 telemetry finding.
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849.
- `requested_model_id` field split on `LLMCallLog` — migration required.
- `was_policy_reroute` field on `LLMCallLog` — migration required.
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate).

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2887 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2887: no A4 spend this session (side-step to GTM audit + Character OS work). A1 shipping spend was Character OS PR #2/#3/#4 + u-d-b PR #3398.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(tt) as ratified at S2886 close. **(uu) added at S2887: engine-bridge tool answers now persist as durable workspace-scoped `Asset(role=BRIDGE_ANSWER)` rows — the engine-bridge product pattern creates durable value instead of transient panel-text. Character OS operators can configure per-workspace `EngineConnection` via `/settings/engine-connections/` (EB.4 SPA panel).**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2887)

See:
- **S2887 handoff (current):** `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md`
- **S2887 audit:** `docs/investigations/2026-07-22_RIGBY_SAAS_AND_COS_BRIDGE_GTM_GAP_AUDIT.md`
- **S2886 handoff:** `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md`
- **S2885 handoff:** `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`
- **S2884 handoff:** `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.

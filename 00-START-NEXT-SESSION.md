# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2889 CLOSE → Playbook v0.9.0 ratified + Chris pivoted to character-os UI exploration (u-d-b PR #3402 `147dcc9cc`, tag `playbook-v0.9.0` pushed) (2026-07-22; picks up as S2890) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2889 close).** S2889 shipped Playbook v0.9.0 MINOR amendment codifying two handler-test-authoring rules under Chapter 3 §3.2. Rigby T1+T2+T3 SIGN cycles all AGREE (10+5 tool_runs total); Chris D-verdict "yes ship it". Chris then pivoted from originally-scripted Step 2 (character-os EB.4/C3 dogfood) to open exploration mode on character-os UI.

- **u-d-b PR #3402** `147dcc9cc` — Playbook v0.9.0: PLAYBOOK-3.2.3 (dispatcher-DB `TransactionTestCase` scoped to transaction-visibility invariant) + PLAYBOOK-3.2.4 (shared-taxonomy branch fortification via `action` field or error-body substring). Rule count 205 → 207. First Chapter 3 extension since v0.2.0 (8-version gap). Ledger 148 → 154 rows (4 backfilled S2885/S2886 + 2 live S2889 folds).

Full session context: `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`.

Workspace deliverables: ratification envelope `6f8767c7-0ad4-4d3c-ad1d-c57ecb5144a4` (governance, clean) + content mirror `9a9ba3dc-2dc4-423d-acc6-2ccb104ec780` (engineering, diagnostic flags cleared).

---

## S2890 open sequence

### Step 1 (FIRST THING) — Character-os UI → u-d-b endpoint reference sheet

Chris pivoted at S2889 close from scripted EB.4/C3 dogfood to open exploration on character-os UI. Direct quote: *"I don't know what parts are going to need to hit u-d-b or what is only on character os."*

**S2890 first-action for Claude (u-d-b side):** produce a compact terminal reference sheet mapping each character-os UI surface to one of:
- (a) hits u-d-b PA endpoint (`http://localhost:8000`)
- (b) character-os-only
- (c) hybrid (character-os drives; u-d-b returns bridge answer)

Sources to read:
- `docs/investigations/2026-07-22_RIGBY_SAAS_AND_COS_BRIDGE_GTM_GAP_AUDIT.md` (S2887 audit doc)
- `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md`
- character-os `consult_engine.py` integration path
- character-os `/settings/engine-connections` config spec (from S2887 audit)

Deliver as terminal artifact for Chris to reference while exploring the character-os SPA.

### Step 2 — Stand by for Chris's exploration questions

Chris drives the character-os UI in a separate terminal (likely a second Claude in the character-os repo). While he clicks around, he pings u-d-b Claude here for:
- Surface-identification ("did that just hit u-d-b?")
- Endpoint spec lookups
- Cross-repo behavior explanations

Claude (u-d-b side): stand by; answer narrowly.

### Two-Claude concurrency safety envelope (verified clean at S2889 close)

- Each terminal uses its own Rigby conversation pin — no state collision.
- Different repos, different branches — no git collision.
- **Watch:** character-os Docker postgres previously captured u-d-b's `:5433` via IPv6 wildcard (S2885 mitigation `USE_PGBOUNCER=0` still in force in both `.env` files); orphan Redis cwd from `/development/` checkout (resolved S2886 open). If character-os side runs `docker compose up`, verify port ownership before restarting u-d-b.
- Shared u-d-b PA endpoint (`http://localhost:8000`) — both Claudes may drive it; surface handles concurrent conversations.
- `feedback_post_travel_port_collision_triage` remains operative for any port-collision surprise.

### What's forbidden at S2890 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC). Rejected at S2887 as architectural mis-fit.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original Step 2 EB.4/C3 scripted dogfood** — Chris pivoted to open exploration; scripted dogfood deferred.
- **Original Step 3 net-new engineering slate** — deferred until Chris returns to slate work.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution.
- R1 fleet reject-mode flip — deferred; fleet HMAC path dormant per S2887 telemetry finding.
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849.
- `requested_model_id` field split on `LLMCallLog` — migration required.
- `was_policy_reroute` field on `LLMCallLog` — migration required.
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate).
- Testing Discipline chapter candidacy (ledger row 154, `future_trigger`) — trigger: 2 more test-authoring rules under §3.2 before Chapter 3 promotion OR one SIGN cycle blocked by ambiguous test-authoring slot placement.

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2889 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2889: zero A4 spend — pure governance amendment.** A1 shipping spend was u-d-b PR #3402.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2889)

See:
- **S2889 handoff (current):** `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`
- **S2888 handoff:** `docs/handoffs/SESSION_2888_TD_ERROR_EXTRACTION.md`
- **S2887 handoff + audit:** `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md`, `docs/investigations/2026-07-22_RIGBY_SAAS_AND_COS_BRIDGE_GTM_GAP_AUDIT.md`
- **S2886 handoff:** `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md`
- **S2885 handoff:** `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.

# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2972+2973 CLOSED. Workflow reframe walks 4 AND 5 validated in the SAME session (first back-to-back two-arc session in the reframe run). Two code PRs shipped: **#3599 (S2972 fix backfill stats-alignment)** + **#3600 (S2973 NO_ITEMS breakdown + Policy A 2-spider exclusion list)**. Chris flagged "backfill returning skipped/concurrent, UI shows 25% coverage / 12,851 pending." Root cause turned out to be a stats-contract bug, not a broken backfill — every "pending" row was already marked [NO_ITEMS] (real backfill queue = 0). S2972 fixed the stats contract; live-verify surfaced **79.1% of new rows in 24h are marked [NO_ITEMS]** which motivated Chris to ratify the S2973 follow-up mid-session. Rigby drafted the S2973 spec (first Rigby-drafted-per-Chris-ratification origination — fold candidate #9). S2973 added `?include_breakdown=1&window=N` param + conservative 2-spider policy exclusion list. 41/41 backend tests pass; frontend build clean; live-verify at HEAD `fa3213b4c` returned real 24h + 30d + baseline + invalid-window scenarios all correctly. Rigby T1 + A2 SIGN both AGREE on both PRs, no F-BLOCKERS. Full context: `docs/handoffs/SESSION_2972_2973_STATS_ALIGNMENT_AND_NO_ITEMS.md`.

**Session cost this session:** minimal — no v2 subprocess dispatches; ~7 PA turns for T1/A2/verify/ledger across both arcs.

**HEAD at close:** `fa3213b4c` (PRs #3599 + #3600 merged; docs cascade PR TBD). Workers recycled after each merge per PLAYBOOK-7.4.4.

---

## S2974 first-action — WAIT FOR CHRIS (same as S2969-S2973)

The reframe held for the **fifth time** — and for the first time via two variants in a single session (Chris-paste for S2972; Rigby-drafted for S2973). Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2972_2973_STATS_ALIGNMENT_AND_NO_ITEMS.md` in full — especially §"Root cause narrative", §"Ground-truth numbers", §"Classification framework — 3-shape NO_ITEMS model", §"Live-verify results".
4. **Optionally probe the shipped state:** `curl -s -H "Cookie: sessionid=<yours>" 'http://localhost:8000/api/signals/embedding-coverage/?include_breakdown=1&window=24'` or open `/workspace?tab=intelligence&sub=signals` and expand "Top no-items producers (24h)". Confirms both S2972 + S2973 builds are still live.
5. **Report readiness in one short message and wait.** Something like: "Oriented. S2972+S2973 closed — reframe validated for the fourth and fifth walk in one session. Coverage widget live at `/workspace?tab=intelligence&sub=signals`; 79.1%/86.7% no_items rate visible; policy list has 2 spiders. Ready when you have a spec pointer."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:** follow the S2969-S2973 pattern — read spec, targeted "existing implementation analysis" (Cycle 1A verify-before-build), T1 SIGN to Rigby with zoom-out ask, fold, implement, A2 SIGN with file+line evidence, merge with `--admin`, `make recycle-all`, live-verify in-shell (Django `Client().force_login` for auth-gated routes; **`HTTP_HOST='localhost'` required or DisallowedHost fires**), Rigby verifies from her tool surface, report three-part summary to Chris.

---

## S2974 high-value seeds (Chris picks whether to open)

**theodds auth-failure fix.** Top NO_ITEMS producer at 294 rows / 30d, 15 rows / 24h. Rigby's S2973 shape-sampling confirmed the rows are `auth_failure_circuit_breaker` / `error_summary` envelopes, not legitimate empties. Fix requires Chris to rotate `THE_ODDS_API_KEY` (or verify API quota). Post-fix: re-run 24h + 30d breakdown to validate top-producers list re-ranks and rate drops.

**Shape sampling for top NO_ITEMS producers (huggingface / legislation / discord_training / udemy).** Sample ~10 rows each, classify into rollup / empty-run / error-envelope per S2973's 3-shape model. May yield 1-2 additions to Policy A exclusion list, or may surface real extractor misses (Policy B territory). huggingface is top-5 over 30d (193 rows) but not 24h — either fires less often now or the pattern is older; sample decides.

---

## S2971 candidate follow-ups (Chris picks whether to open)

**Rail shortcut for /signals** (~5 min). Legacy alias `signals: { primary: 'intelligence', sub: 'signals' }` already wired in `WorkspacePageNew.tsx`. Only need a `<NavLink to="/workspace?tab=signals">` entry in `frontend/src/components/layout/Sidebar.tsx:55` for one-click discoverability from the primary rail.

**Per-view window selector.** Current build shares one window across Dashboard/Feed/Clusters. Rigby's A2 recommendation: keep shared for v1; iterate only on real complaint.

**URL persistence for filter state (spec §8 nice-to-have).** Feed + Cluster filter state currently in component state; deep-linking requires plumbing every filter to `useSearchParams`.

**"Create Initiative from Cluster" button (spec §8 nice-to-have).** Wires cluster detail drawer to `work_tool.initiative_create` via PA.

**Migrate Feed Explorer to `persistence.SpiderData`.** Would surface `relevance_score`/`opportunity_score`/`quality_score`/`urgency_score` (extended fields absent from `LegacySpiderData`). Separate arc — spec §5.1 field names would need per-view remapping (`raw_data`/`processed_data` → `content`/`structured_data`).

---

## S2970 candidate follow-ups still open (unchanged)

**sports_injuries keyword tuning (small mini-PR).** Adding 2-3 conservative keywords (`cleared for`, `activated`) would push NFL/MLB yield from 1-3 → 3-5 items each. Only worth doing if Chris insists on ≥10 as a hard requirement.

**S2969 candidate arc STILL OPEN:** worker egress validation. S2970 PR-B.1 root-caused the DNS piece (aiohttp/aiodns bug). Broader worker-egress questions (HTTPS access to all spider target hosts, network policy, worker daemon env inheritance) remain uninvestigated.

---

## S2968 PR-B branch decision — STILL OPEN

_(unchanged from S2971 open — no session touched the S2968 PR-B branch)_

**Branch `feat/s2968-pr-b-deliverable-as-spec` remains pushed to origin, no PR opened.** Chris now has THREE data points on how the reframe works (S2969 + S2970 + S2971) — the manual UUID-paste flow works cleanly, no exempt-list / schema plumbing strictly required. Options A/C from S2968 close still apply.

---

## Candidate folds surfaced this session (NOT codified)

**Trigger count building toward Playbook rules — do NOT amend without a second trigger unless otherwise noted:**

Carrying forward from S2969/S2970:

1. **Soft-key-vs-LLM-schema-gate.** **Trigger count: 1** (S2968 PR #3589).
2. **"We're building a duplicate of a thing we already have" pattern.** **Trigger count: 2** (S2968).
3. **"Auditability primitive already exists in a different plane" pattern.** **Trigger count: 1** (S2969).
4. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 3** (S2969 + S2970 + S2971). Three-trigger corpus reached. If S2972 continues the pattern, this promotes to a Playbook rule proposal about spec-driven session shape.
5. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** **Trigger count: 1** (S2970).
6. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** **Trigger count: 1** (S2970).

New at S2971:

7. **"Route-placement is a settable expectation, not a spec constraint."** Spec §3.1 offered `/signals` OR `/intelligence/signals`. Rigby's tool-grounded read of App.tsx pushed to Workspace sub-tab (better matched Chris's directive). Zoom-out ask per `feedback_zoom_out_ask_per_rigby_sign` directly surfaced this. **Trigger count: 1** (S2971). Watch for a second.

8. **"Rigby web_fetch_tool can't authenticate against Django session-cookie endpoints."** Verification of auth-gated new endpoints stayed on Claude's side (Django `Client().force_login`); Rigby's tool-surface probe returns 401 (correct behavior, wrong verification vehicle). Flagged as ledger candidate; not adding yet — waiting for second occurrence. **Trigger count: 1** (S2971).

---

## Universal open sequence (unchanged)

1. `context-kit orient` — source-of-truth chain, latest handoff
2. Absorb `MEMORY.md` + `CLAUDE.md` (both auto-injected)
3. Read this `00-START-NEXT-SESSION.md` in full
4. **Session-open atomic mint check:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2974 pin minted at S2972+S2973 close cascade. If not fresh, run `python manage.py session_lifecycle close --label s2972-s2973-stats-alignment-and-no-items` first (per `feedback_session_open_atomic_mint_before_pa_dispatch`).
5. Verify `claude` CLI availability (if v2 dispatches are on the day's plan): `which claude && claude --version` (should show 2.1.114+ at `~/.local/bin/claude`)
6. Read `docs/handoffs/SESSION_2972_2973_STATS_ALIGNMENT_AND_NO_ITEMS.md` — full context on this session's shipped code + reframe walks 4-5
7. **Wait for Chris to hand you a spec pointer via Rigby.** Do not proactively propose work.

---

## What's forbidden at S2974 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward.

- **Do not automatically merge S2968 PR-B** — its dispatch wiring is architecturally stale under the reframe.
- **Do not proactively dispatch v2 test runs at session open** — each burns ~$0.15-0.20.
- **Do not chase spider parsing bugs for reddit / sports_injuries** — S2969/S2970 verified code path works.
- **Do not flip `SPIDER_USE_THREADED_DNS_RESOLVER` off in this env** — aiodns 3.5.0 is broken here; the flag default is `true` intentionally.
- **NEW at S2973: Do NOT expand the Policy A exclusion list (`core/services/no_items_policy.py`) without shape-sampling target rows first** — false exclusions HIDE real data-quality bugs (theodds auth failure, extractor misses). Sample before adding.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2971 additions:**
- Rail shortcut for /signals (~5 min)
- Per-view window selector (v1 shipped shared; iterate only if Chris asks)
- URL persistence for filter state (spec §8 nice-to-have)
- "Create Initiative from Cluster" button (spec §8 nice-to-have)
- persistence.SpiderData migration (extended scoring fields; separate arc)

**S2970 additions:**
- sports_injuries keyword tuning (~10 min if Chris insists on ≥10)
- Worker egress validation arc (broader, DNS piece fixed S2970)

**S2969 additions (unchanged):**
- Retention task Beat schedule — `cleanup_empty_spider_runs` un-scheduled per Rigby T1.

**S2968 additions (unchanged):**
- PR-C (Deliverable status write-back), PR-D (v2 default flip + v1 deletion), Path A (nightly beat + drift dashboard), Path B (per-slice named predicate graduation), Path C (Ledger #20 + #21 fix arc).

**Long-standing (carry forward):** Docs restructuring arc, Slice 5-hardening executable invariants, Tier 2 lint promotion, Advanced paste-UUID fallback for cluster picker, Server-side search + pagination on `/eligible/`, Z1/Z2/Z4 signal-dispatch UI polish, Rank + cap + paginate follow-ups, Per-pattern-type diversity floors, Ledger candidates backlog, W2 #1 / #2b / #2c pending Chris re-slate, LLMCallLog field splits, Bulk `workspace_budget_tool` operations, C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** S2971 was net-new engineering (Signal Intelligence UI), not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend.
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2971)

See:
- **S2971 handoff (current):** `docs/handoffs/SESSION_2971_SIGNAL_INTELLIGENCE_UI.md`
- **S2971 shipped code:** PR #3597 (`feat(s2971): Signal Intelligence UI — Workspace tab (backend + sub-panel)`)
- **S2971 spec deliverable:** `ade9339f-c41f-48a5-9ce8-fa8beee696cc`
- **S2971 support conversation:** `pa-ab10ffdb0e5f4597`
- **S2970 handoff:** `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md`
- **S2969 handoff:** `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md`
- **S2968 handoff:** `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`
- **S2967 handoff:** `docs/handoffs/SESSION_2967_SLICE_7_TOOL_GAP_FIXES.md`
- **S2966 handoff:** `docs/handoffs/SESSION_2966_GOLDEN_EVALS_HARNESS_PR2B.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89`
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.

# Next Session — Start Here

---

## READ THIS — SESSION 3049 CLOSED. **Phase 1 of RaaS UI overhaul arc DONE — 8-row gap map + 5-PR Phase 2 slice ratified in deliverable `edf69671-…`.**

S3049 shipped the pre-ratified RaaS UI overhaul arc **Phase 1** — a Rigby-authored, Claude-verified, Rigby-A2-tightened gap map living at deliverable `edf69671-2a87-49f1-a8ac-d07086f851d5` (Donkey Betz workspace `b4503364-…`, `engineering_backlog` / `product`, 30,367 chars). Zero code shipped; Phase 1 IS the ship — Phase 2 opens next session.

**HEAD at close:** `ba7ec4ae4` (S3048 wrapper pin bump). Docs-cascade PR for handoff + 00-START + wrapper pin bump follows.

### What shipped

- **Deliverable `edf69671-…` — RaaS UI Gap Map (Phase 1 CLOSE)** — 6 sections, all populated with tool_run citations:
  - **§0** — Command Center operator-shaped signal + post-authoring verification note (Rigby A2 + Claude ORM)
  - **§1** — 62 App.tsx routes classified, WorkspacePageNew 5-tab shape, DeliverablesTab filter surface
  - **§2** — 3 MVP capabilities as given/when/then acceptance criteria with explicit out-of-scope
  - **§3** — 8 numbered delta rows (7 blocking + 1 non-blocking), 3× S + 5× M
  - **§4** — 163 RaaS tools categorized into 3 exposure buckets (customer-safe / operator-only / gated) + handler-file concentration map
  - **§5** — 5-PR dependency-ordered Phase 2 slice (2× S + 2× M + 1× S–M), single-session with 2-session fallback
- **Two big Phase 2 effort reductions** (both eliminate schema work):
  1. `Deliverable.user` FK already exists → Gap 7 wins
  2. `User.platform_role` + `customer_role` + `subscription_tier` + `tenant` all exist → PR 4 wins
- **Rigby A2 verification** caught 3 real concerns during Claude's §4/§5 short-circuit — all incorporated as §0 addendum + §4.1/§4.3/§4.4/§5 amendments
- **35th consecutive Cycle 1A verify-before-build session.** **28th consecutive zero-hallucination Rigby SIGN streak.**

### Phase 1 evidence (from deliverable + ORM checks)

- 62 App.tsx routes: 5 public + ~5 customer-reachable + ~38 operator-only + 14 cockpit redirects
- `deliverablesApi.list()` params: `type/category/agent/saved/template/source/search/page/per_page/workspace` — no `owner`/`user`/`created_by`
- `Deliverable.user` = ForeignKey (Rigby `orm_inspect_tool.describe_model`)
- `User` fields include: `platform_role`, `customer_role`, `subscription_tier`, `tenant`, `api_key`, `subscription_tier` (Claude Django-shell)
- `WORKSPACE_AWARE_AGENTS` at `core/epa_handlers_tools.py:3877` (definition) + `:3913` (allowlist check)
- Cycle 1A verify: RaaS-validated=163 unchanged from S3048 close state ✅

### Substrate ledger changes

**Zero new rows.** S3049 was scoping/discovery — no substrate defects surfaced.

### PLAYBOOK folds

**Zero folds** — no spec→ship shape this session.

### Rigby Tool Gap Ledger observation (candidate, 1st trigger)

Rigby exhausted runway on §4/§5 large-synthesis dispatch — enumerating 163 tools across 3 buckets + authoring 5-PR slice in one dispatch is too much. Two consecutive dispatches ran exploratory reads without landing `deliverable_tool.update`. Claude short-circuited (author + ORM splice + Rigby FYI-verify) — correct workaround but underlying gap is real. Not filing until 2nd trigger per convention.

---

## S3050 first-action — RATIFIED PICK (Chris yes/no's at open)

### Pick: **Open Phase 2 of RaaS UI overhaul arc — 5-PR slice, PR 1 first**

**Provenance:** S3049 close ratified the 5-PR slice as S3050 first-action.

**5-PR slice (dependency order):**
1. **PR 1 (S)** — Backend `owner=me` filter on `/deliverables/` list endpoint (discharges Gaps 2 backend / 4 / 7; wires existing `Deliverable.user` FK; no schema change)
2. **PR 2 (S)** — Frontend `deliverablesApi.list()` typed `owner` param at `frontend/src/lib/api.ts:4260` (discharges Gap 2 frontend)
3. **PR 3 (M)** — `/my` route + `<CustomerLayout>` variant mounting PA chat without operator sidebar/tabs (discharges Gaps 1 + 5)
4. **PR 4 (S–M)** — Role guard: extend `ProtectedRoute` + `CustomerRoute` variant + server-side `IsOperatorRole` DRF permission (discharges Gap 6; wires existing `User.platform_role`; no schema change)
5. **PR 5 (M)** — `CUSTOMER_ALLOWED_TOOLS` set at `core/services/tool_dispatcher.py` + tool-schema filter for customer-mode PA chat + argument auto-inject for gated tools

**Predicted:** single-session S3050 with 2-session fallback (S3050 + S3051) if PR 3 layout variant balloons.

**Explicit deferrals (Phase 3+):** Gap 3 (workspace DeliverablesTab stays operator-only), Gap 8 (cockpit redirects), role management UI, per-tool permission matrices, ACL editor, fine-grained ABAC middleware.

### Concrete opening move (S3050)

1. `context-kit orient` (auto-injected)
2. Absorb this file + `MEMORY.md` + `CLAUDE.md`
3. Read S3049 handoff (`docs/handoffs/SESSION_3049_S3049_PHASE_1_RAAS_UI_GAP_MAP_CLOSED.md`)
4. Cycle 1A verify-before-build FIRST — re-run `build_pa_tool_audit --gap-only --check` to confirm RaaS-validated=163; ORM-verify `Deliverable.user`, `User.platform_role`/`customer_role`/`subscription_tier`/`tenant` still present. **36th consecutive Cycle 1A session.**
5. Read `edf69671-…` §5 in full via `deliverable_tool.get` (or ORM).
6. Open PR 1 (backend `owner=me` filter) — smallest S PR, unblocks PR 2 immediately. Full T1 SIGN + A2 SIGN + tests per PLAYBOOK-7.7.1/7.7.2. **PLAYBOOK-7.7.5 fires** — Gap 4 is drift-closure class → mandatory A2 sweep for other list endpoints without ownership enforcement (name the shape signature: `.filter(user=...)` predicate + adjacent endpoints under `/api/v1/*`).
7. If PR 1 lands early, cascade into PR 2 (frontend param — S).
8. Chris ratifies scope at each PR envelope, not just at session open.

### Rejected candidates (documented for provenance)

- **Pivot away from Phase 2** — reasonable but S3049 pre-ratified Phase 2 as the next step; only pivot if new information changes the picture.
- **PR 5 first** (tool allowlist before ownership) — rejected; PR 1's `owner=me` filter is the load-bearing MVP capability without which customer inbox is unusable regardless of tool exposure.
- **`/docs/` restructuring arc** — still deferred (Chris directive S2800).
- **Provenance test suite 4 failures** — still deferred (unrelated to S3049 scope).

---

## S3050 carry-forward seeds

### New from S3049

- **Deliverable `edf69671-…`** = Phase 1 gap map (source-of-truth for Phase 2 PR authoring)
- **Phase 2 5-PR slice** (Chris re-ratifies at open per shape convention)
- **Rigby Tool Gap Ledger observation** — large-synthesis-dispatch runway gap (candidate row, 1st trigger; file at 2nd trigger)

### Carried from prior arcs — status preserved

- **Odds API operationally degraded** — Chris directive S3045: no active API key; back burner.
- **Skiplist re-validation** (5 media/audio tools) — deferred; dedicated media-batch scope required.
- **`agent_router.py:2131-2132` silent fallback** — 1st `future_trigger` (S3043).
- **T1 Fold future_trigger (`typing.Literal[actor]`)** — 1st trigger (S3036).
- **A2 Fold future_trigger (actor-taxonomy vs frontend-palette drift)** — 1st trigger (S3036).
- **`did_X` semantics** — 2nd trigger (S3034); watch for 3rd.
- **S3033 Fold B** — ledger persistence timing (1st trigger discharged; watch for 3rd).
- **S3030 prod deploy carry** — `backfill_canonical_drift --apply` on Railway prod.
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion.
- **S3031 Fold B** — spy fragility.
- **S3034 A2 Folds** — subscriber wire-contract fragility + adjacent-axis superseded/experiment.
- **S3042 arc Q3/Q4** — Spine Contract v1 §§1+3 (frontend event instrumentation + Workspace UI redo Arc C).
- **`chris-personal` orphan-initiative cleanup pass** — Spine Contract v1 §4.
- **Stem-matcher warn-only lint (Option B)** — S3044 row 1; 3-trigger threshold reached; deferred per Rigby T0 SIGN Q5.
- **`/docs/` restructuring arc** — queued (Chris directive S2800).
- **T2 spec for `agent_router.py:2131-2132` silent fallback** — deferred.
- **Provenance test suite 4 failures** — surfaced S3048; still deferred.
- **S3049 Phase 3+ deferrals** (per §5 of `edf69671-…`) — Gap 3, Gap 8, full role UI, permission matrices, ACL editor, fine-grained ABAC.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0**. No amendments this session.
- **Cycle 1A verify-before-build:** **35th consecutive session.**
- **Claude directs, Rigby executes, Claude verifies:** followed cleanly for §0/§1/§2/§3. Short-circuited §4/§5 after 2 Rigby runway exhaustions per `feedback_loop_rigby_in_when_short_circuiting`; Rigby A2 caught 3 concerns all incorporated.
- **SIGN evidence discipline (PLAYBOOK-7.7.2):** Rigby A2 verification was tool-grounded (`deliverable_tool.detail` chunked reads to inspect authored content).
- **Recycle discipline (PLAYBOOK-7.4.4):** No code shipped → no recycle needed.
- **Local truth (`feedback_local_truth_no_production`):** local ORM verification is the truth.

---

## Wrapper pin note

Active PA conversation pin at S3049 close is `pa-15cb9f33d7ad4034`. `session_lifecycle close` at close time will atomically retire it + mint next-session pin + rewrite `tools/pa_local.sh`. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S3049 was pure scoping/discovery — the deliverable IS the ship. Phase 2 opens next session with the 5-PR slice as the ratified starting point. If S3050 first-action pivots, Phase 2 stays parked as pre-ratified until re-picked. Rigby's A2 verification of the short-circuit is the shape that makes short-circuit safe — always loop her in with an ask after, never after-the-fact narration only.

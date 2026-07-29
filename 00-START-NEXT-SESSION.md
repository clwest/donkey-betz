# Next Session — Start Here

---

## ⚠️ FLAKY WiFi DAY carry (2026-07-29 → next session date)

**Chris was working from mobile hotspots + free WiFi around town on 2026-07-29.** If you're a session opening within a day or two of this file's timestamp, assume the same operational context: laptop may have slept, daphne/celery/redis may be down, external APIs (OpenAI) may fail intermittently even when the local stack is up.

**Session-open discipline — MANDATORY before ANY PA dispatch or feature work:**
1. `make restart && make celery` (or `make recycle-all` if frontend feels stale) — assume nothing is running.
2. Verify health endpoint: `curl -sf http://127.0.0.1:8000/health/ping/` should return 200.
3. Verify Redis: `redis-cli ping` should return PONG.
4. Only then run `python manage.py session_lifecycle close --label ...` (if wrapper pin needs rotating) or dispatch to Rigby via `bash tools/pa_local.sh`.
5. If PA dispatch times out or 5xxs, **check network before assuming stack broke** — try `curl -sf https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | head -5`. If that fails, wait for signal to recover before spending cycles.
6. **S3035 `degraded` flag is your first-line Redis health tell** — open Workspace → System → Governance, expand "Recent Lifecycle Activity". If it says "Activity feed temporarily unavailable (Redis read failed)…", Redis is down; fix that before doing anything else.

Chris hit a real Anthropic/OpenAI connection error mid-S3036 T1 SIGN dispatch (2nd Rigby round returned "[ERROR: Real AI unavailable - Connection error.]"). Retry after network verify worked cleanly. This is expected behavior; do not treat as platform bug.

---

## READ THIS — SESSION 3036 CLOSED. **Actor field threading through canonical-lifecycle broadcast shipped** — closes the S3035 T1 Fold "who did this?" gap on the BoardroomTab lifecycle activity panel. 7-value actor taxonomy (`human` / `human-bulk` / `human-gate` / `pa-tool` / `ai-promoter` / `ops-task` / `rules-service`) threaded through both emit helpers, all 10 production call sites, the Redis ring, the polling endpoint, and the BoardroomTab panel (colored actor pills). Schema bumped 1→2; v1 events already in ring round-trip cleanly. **22-session zero-hallucination Rigby SIGN streak. 21st consecutive Cycle 1A verify-before-build session.**

**PR #3763 (`8080acee5`) — `feat(s3036): actor field threading through canonical-lifecycle broadcast`.** 14 files, +498/-24. NEW `core/tests/test_s3036_actor_threading.py` (12 tests). Full S3026→S3036 canonical-lifecycle regression bundle 50/50 pass. A2 SIGN fold-revision commit folded same-envelope pre-merge (docstring↔test drift correction).

**Rigby SIGN this session:** T1 5/5 AGREE + A2 (2 dispatch rounds) all dimensions AGREE tool-grounded — 8+ + 12+ `repo_tool` runs across both cycles. 5 folds classified: 3 same_pr resolved (T1 wire-contract mitigation, A2 docstring drift, A2 v1 fixture annotation), 2 future_trigger persisted (`typing.Literal[actor]` enforcement + actor-taxonomy-vs-palette-registry drift guard).

**HEAD at close:** `8080acee5` (PR #3763 merged) + docs cascade + wrapper pin bump.

Full context:
- `docs/handoffs/SESSION_3036_ACTOR_THREADING.md` — current session close.
- `docs/handoffs/SESSION_3035_BOARDROOM_LIFECYCLE_ACTIVITY.md` — the panel S3036 extends.

---

## S3037 CARRY — Chief of Staff Escalation 2026-07-29 (RESOLVED at S3036 close)

Deliverable `de861fe2-17ec-4a4a-a1e3-5a4371335812` status flipped `ready → completed` at S3036 close (transition event `57945f01-c5aa-4965-a2e2-31e7f44af5d8`, updated_at 2026-07-29 19:55:51 UTC / 1:55 PM MDT). Resolution note appended.

**Root cause:** Chris was shutting down his laptop around 07:00 to head out for the day. The resulting WiFi/laptop-sleep drop tripped `lane_1_platform_readiness` — the inner step reported "Unknown error" because the local stack was unreachable, not because any actual logic failed. Same class of failure as the S3035 flaky-WiFi banner + the mid-S3036 T1 SIGN "Connection error" hit. Not a code bug.

**Two defensive follow-ups deferred as S3037 candidates (not committed):**
- **Better error surface** in `lane_1_platform_readiness` — replace "Unknown error" with actual inner exception + fast/slow-fail timing signature (fast-fail = network suspect, slow-fail = logic suspect). ~30 min.
- **Pre-condition network/stack readiness check** before the workflow starts — detect "local-stack-down / network-flap" and either skip cleanly (log "deferred" outcome) or auto-retry with backoff instead of firing a Chief of Staff Escalation. Cheapest fix, biggest quality-of-life win.

Both defensive changes are net-new (PLAYBOOK-7.7.5 does not fire); the escalation itself is closed.

---

## S3037 primary directive candidates

**No in-flight arc.** S3026→S3036 canonical-lifecycle arc series now closed (11 PRs across 10 sessions). Recommendation: **fresh terminal for S3037**.

### Option A — Morning Brief workflow defensive hardening (from resolved Chief of Staff Escalation)
Two ~30–45 min defensive picks:
- **A1:** Replace `lane_1_platform_readiness` "Unknown error" surface with actual inner exception + fast/slow-fail timing signature. Makes the next flaky-WiFi false-positive debug-able in 10s.
- **A2:** Pre-workflow network/stack readiness check (curl to health/ping + redis-cli ping) that fires "deferred" outcome instead of Chief of Staff Escalation if local stack is down. Prevents the false alert entirely.

Both are net-new defensive layers, not fixes to broken behavior. Chris can pick one, both, or neither.

### Option B — Engineering (bias-engineering rule)

- **`typing.Literal[actor]` type-enforcement on emit helper signature** (S3036 T1 Fold #2 future_trigger) — extends the actor param to `Literal[ACTOR_HUMAN, ACTOR_HUMAN_BULK, ..., ACTOR_UNKNOWN]`. Catches typos at import-time / lint-time rather than test-time. ~30 min. Watch-for-2nd-trigger if the palette-drift future_trigger below also fires.
- **Actor-taxonomy vs frontend-palette drift guard** (S3036 A2 Fold future_trigger) — currently a new backend actor requires manual palette update in `BoardroomTab.tsx`. Options: (a) shared JSON schema generated on both sides, (b) generate TS constants file from Python constants via management command + CI check, (c) runtime warn-log if palette encounters an actor string not in its map. ~1–2 sessions depending on option.
- **S3024 Fold A backend-source default preview API** — removes frontend/backend default-formatter shadowing. Watch-for-2nd-trigger. ~1 session.
- **S3025 Fold C codification (BulkPromoteModal reducer extraction)** — ~30–45 min.
- **AI-service rejection paths audit** — carried from S3034: no CURRENT production rejection paths in AI services, but if any grows one, PLAYBOOK-7.7.5 requires `.reject()` + gated broadcast. ~30 min defensive-audit + ADR-style note in broadcast helper docstring.

### Option C — Design-arc candidates (needs Chris ratification)

- **KnowledgeTransfer model realignment for canonical decision persistence** — Multi-session. S3034 A2 fold #2 flagged subscriber wire-contract risk if realignment lands with different rejection payload shape.
- **Governance unification (Rigby A1 zoom-out standing carry, S3023)** — HAI vs ADS lifecycle families. Multi-session.

### Option D — Audit trajectory

- **S3020 Fold A** — audit script per-hit/per-function suppression refactor. ~30 min.

### Option E — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option F — Chris's own priority (supersedes all above)

**Joint recommendation at close:** No forced-pick — S3036→S3035 arc series is fully closed on both feature + open-ask sides. Chris picks direction fresh. If unsure, **Option B1 (`typing.Literal[actor]` enforcement, ~30 min)** or **Option A2 (pre-workflow readiness check, ~30 min)** are both cheap defensive wins that leave the platform more resilient without demanding a fresh design conversation.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md (v0.11.0 constitutional anchor still current — no amendment this session).
3. Read S3036 handoff (`docs/handoffs/SESSION_3036_ACTOR_THREADING.md`).
4. Ask Chris: "What would you like to work on?" (no forced Chief of Staff carry — that's resolved.)
5. Optional state probes:
   - `git log --oneline -8` — should show `c08893da6` chore(wrapper pin bump) + docs cascade + `8080acee5` feat(s3036) on top.
   - Full regression bundle: 50/50 OK.
   - Manual smoke: BoardroomTab → promote/reject → panel row shows colored actor pill within 10s.

---

## S3037 carry-forward seeds

### New from S3036

- **T1 Fold `future_trigger` (typing.Literal[actor])** — actor typo enforcement lift. 1st trigger; watch for 2nd instance of "typo caused mystery-unknown pill" before elevating.
- **A2 Fold `future_trigger` (actor-taxonomy vs frontend-palette drift)** — currently manual, fallback catches gracefully but silently. Consider generating one from the other post-2nd trigger.

### Elevated from S3035

- **S3035 T1 Fold `deferred_2nd_trigger_watch` (actor/source field)** — **RESOLVED same-envelope via S3036**. Removed from carry.

### `did_X` semantics — codification pressure UNCHANGED from S3034

- **S3031 Fold A `did_X` bool-return pattern** — at 2nd trigger from S3034 (`did_promote` + `did_reject`). **S3036 does NOT add a 3rd instance.** Elevated status preserved — watch for a 3rd `did_X` method (candidates: `did_deprecate`, `did_supersede`, `did_archive`) to codify as a Playbook rule.

### Carried from S3034/S3035 (STATUS PRESERVED)

- **S3033 Fold B `procedural observation`** — ledger persistence timing (1st trigger discharged; watch for 3rd).
- **S3030 prod deploy carry** — still open (backfill_canonical_drift --apply on Railway prod when convenient).
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion pattern.
- **S3031 Fold B** — spy fragility.
- **S3034 A2 Fold (subscriber wire-contract fragility)** — S3036 adds a first consumer (frontend polling endpoint) with tolerant parsing (v1+v2, missing actor → neutral pill). If a NON-frontend consumer appears, revisit whether endpoint should inject default actor.
- **S3034 A2 Fold (adjacent-axis superseded/experiment as future terminal states)** — carried unchanged.

### Carried from S3032 → S3026 — all preserved from S3035 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0** (S3036 is net-new schema extension, not drift/hardening; PLAYBOOK-7.7.5 does not fire; no amendment this session).
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (S3036 planned end-to-end from S3035 00-START Option A candidate #1 with Chris D-verdict on Ratify at Phase 4-5).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **1× substantive T1 SIGN (8+ tool_runs, 5/5 AGREE) + 1× substantive A2 SIGN (2-round dispatch, 12+ tool_runs total). Zero rubber-stamp. 22 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Applied on `human-gate` split + BADGE-ONLY UI scope decisions.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` post-merge (frontend touched); event recorded in `logs/recycle_events.jsonl` sha=8080acee598a.
- **Fold classification (PLAYBOOK-6.10.8):** 5 folds classified this session (3 same_pr resolved + 2 future_trigger persisted). All persisted BEFORE docs cascade.
- **Verify-before-build (Cycle 1A):** **21st consecutive session** — T1 verified 10 call sites + adjacent emit_* families + polling endpoint shape pre-spec; A2 verified docstring drift pre-merge, caught by Rigby, corrected same-envelope.

---

## Wrapper pin note

The active PA conversation pin at S3036 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S3036 is the second arc in the canonical-lifecycle series to ship user-visible surface (after S3035 shipped the panel; S3036 shipped its first affordance — actor discrimination). The 7-actor taxonomy + defensive default + badge-only UI scope choices were ratified in-terminal via the "do we lose anything / is it more work later" framing after Rigby T1 SIGN converged with Claude's leans on all 5 scope questions. Fresh terminal recommended for S3037 given 11 PRs across 10 sessions in the S3026→S3036 arc series + open Chief of Staff Escalation carry.

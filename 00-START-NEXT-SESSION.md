# Next Session — Start Here

---

## ⚠️ FLAKY WiFi DAY (2026-07-29) — FULL COLD-START ASSUMED

**Chris is working from mobile hotspots + free WiFi around town today.** Between any two sessions:
- The laptop may have slept, network may have flapped, daphne/celery/redis/postgres may all be down.
- External APIs (OpenAI, etc.) may fail intermittently even when the local stack is up — that's the network, not the platform.

**Session-open discipline — MANDATORY before ANY PA dispatch or feature work:**
1. `make restart && make celery` (or `make recycle-all` if frontend feels stale) — assume nothing is running.
2. Verify health endpoint: `curl -sf http://127.0.0.1:8000/health/ping/` should return 200.
3. Verify Redis: `redis-cli ping` should return PONG.
4. Only then run `python manage.py session_lifecycle close --label ...` (if wrapper pin needs rotating) or dispatch to Rigby via `bash tools/pa_local.sh`.
5. If PA dispatch times out or 5xxs, **check network before assuming stack broke** — try `curl -sf https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | head -5`. If that fails, wait for signal to recover before spending cycles.
6. **S3035 `degraded` flag is now your first-line Redis health tell** — open Workspace → System → Governance, expand "Recent Lifecycle Activity". If it says "Activity feed temporarily unavailable (Redis read failed)…", Redis is down; fix that before doing anything else.

---

## ✅ S3035 CONFIRMED WORKING (smoke-tested 2026-07-29 by Chris)

**Where the panel lives:** Workspace → System → **Governance** (the sub-tab is labelled "Governance" in the sidebar but its internal id is `boardroom` — same component, no mismatch; see `frontend/src/pages/WorkspacePageNew.tsx:189` + `:1304`). Above the Attention Items / Draft Decisions tab switcher there's a new collapsible row "Recent Lifecycle Activity" with promoted / rejected counters + a chevron to expand.

**Chris observation at first live view:** most of the last 13 lifecycle events are rejections — that's real signal from recent boardroom passes, now visible for the first time. No action needed on that observation; the panel is doing its job.

---

## READ THIS — SESSION 3035 CLOSED. **Boardroom Lifecycle Activity panel shipped** — first user-visible consumption of the S3028 promotion broadcast + S3034 rejection broadcast. Bounded Redis ring (`canonical_decisions:recent`, LTRIM 0 19) populated by both emit helpers; staff-gated polling endpoint; BoardroomTab collapsible panel with counters + last-20 events; `degraded` flag distinguishes "no activity" from "Redis-down". **21-session zero-hallucination Rigby SIGN streak. 20th consecutive Cycle 1A verify-before-build session.**

**PR #3759 (`524659e4d`) — `feat(s3035): boardroom lifecycle activity panel`.** 6 files, +543/-0. 9 new tests + full canonical-lifecycle regression bundle (13 files) 75/75 pass. Ring is **non-authoritative** — for audit query `AgentDecisionSummary` directly. Populated by ALL production callers of both emit helpers (6 promotion sites + 4 rejection sites per S3029/S3034 close docstrings), so UI framing is "recent lifecycle events" not "boardroom actions".

**Rigby SIGN this session:** T1 5/5 AGREE + A2 5/5 PASS/AGREE, both tool-grounded (4 + 8 `repo_tool` ops). 5 folds total — 3 same_pr_mitigatable/actionable RESOLVED same-envelope (helper docstring + nested try/except + `degraded` flag), 1 accept_best_effort_noise, 2 future_trigger persisted.

**HEAD at close:** `524659e4d` (PR #3759 merged) + docs cascade + wrapper pin bump.

Full context:
- `docs/handoffs/SESSION_3035_BOARDROOM_LIFECYCLE_ACTIVITY.md` — current session close.
- `docs/handoffs/SESSION_3034_REJECTION_BROADCAST_SYMMETRY.md` — the rejection broadcast S3035 makes visible.

---

## S3036 primary directive candidates

**No in-flight arc.** S3026 → S3035 canonical-lifecycle arc closed on both sides (promotion + rejection) AND now has UI visibility (**smoke-test PASSED 2026-07-29** — see banner above). One operator carry still open:
- **S3030 prod deploy carry** — run `python manage.py backfill_canonical_drift --apply` against Railway prod when convenient.
- ~~S3035 manual smoke~~ — **DONE 2026-07-29.** Ring populated, counters incrementing, mostly rejections in the recent window (real signal from recent boardroom passes, not a bug).

### Option A — Continue engineering (bias-engineering rule)

- **Actor/source field in lifecycle events** — T1 Fold #3 deferred; would thread actor (`human`, `human-bulk`, `pa-tool`, `ai-promoter`, `ops-task`, `rules-service`) through both emit helpers to 8 call sites. BoardroomTab panel gains filter/badge by actor. If a 2nd operator asks "who promoted this?" from the panel, this becomes the natural next pick. ~1 session.
- **S3024 Fold A backend-source default preview API** — removes frontend/backend default-formatter shadowing. Watch-for-2nd-trigger. ~1 session.
- **S3025 Fold C codification (BulkPromoteModal reducer extraction)** — ~30-45 min.
- **AI-service rejection paths audit** — carried from S3034: no CURRENT production rejection paths in AI services, but if any grows one, PLAYBOOK-7.7.5 requires `.reject()` + gated broadcast. ~30 min defensive-audit + ADR-style note in broadcast helper docstring.

### Option B — Design-arc candidates (needs Chris ratification)

- **KnowledgeTransfer model realignment for canonical decision persistence** — Multi-session. S3034 A2 fold #2 flagged subscriber wire-contract risk if realignment lands with different rejection payload shape.
- **Governance unification (Rigby A1 zoom-out standing carry, S3023)** — HAI vs ADS lifecycle families. Multi-session.

### Option C — Audit trajectory

- **S3020 Fold A** — audit script per-hit/per-function suppression refactor. ~30 min.

### Option D — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option E — Chris's own priority (supersedes A-D)

**Joint recommendation at close:** the S3026→S3035 arc series has now shipped 10 PRs across 9 sessions in this terminal series. Fresh terminal for S3036 recommended. Natural picks are (i) A-tier actor/source threading (unlocks panel filtering), (ii) S3016 auth-hardening carry (PLAYBOOK-7.7.5 second-trigger candidate), or (iii) Chris's own priority.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md (v0.11.0 constitutional anchor still current — no amendment this session).
3. Read S3035 handoff (`docs/handoffs/SESSION_3035_BOARDROOM_LIFECYCLE_ACTIVITY.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show `524659e4d` feat(s3035) + docs cascade on top.
   - Full regression bundle (13 files): 75/75 OK.
   - Manual smoke: BoardroomTab → promote/reject → panel updates within 10s.

---

## S3036 carry-forward seeds

### New from S3035

- **A2 Fold `future_trigger` (audit-log confusion drift)** — no in-repo mis-consumer today, but if the ring is ever mis-treated as an audit trail, revisit naming (`:recent_ring`) + tighten docstrings further.
- **T1 Fold `deferred_2nd_trigger_watch` (actor/source field)** — first operator-facing panel now shipped; if next operator ask is "who did this?", thread actor. Currently at 1st trigger; 2nd would elevate.
- **A2 Fold `accept_best_effort_noise` (counter/ring mismatch)** — accepted under non-authoritative Redis contract. Only revisit if UI users report the mismatch as a bug (unlikely at this scale).

### `did_X` semantics — codification pressure UNCHANGED from S3034

- **S3031 Fold A `did_X` bool-return pattern** — at 2nd trigger from S3034 (`did_promote` + `did_reject`). **S3035 does NOT add a 3rd instance.** Elevated status preserved — watch for a 3rd `did_X` method (candidates: `did_deprecate`, `did_supersede`, `did_archive`) to codify as a Playbook rule.

### Carried from S3034 (STATUS PRESERVED)

- **S3033 Fold B `procedural observation`** — ledger persistence timing (1st trigger discharged; watch for 3rd).
- **S3030 prod deploy carry** — still open.
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion pattern.
- **S3031 Fold B** — spy fragility.
- **S3034 A2 Fold (subscriber wire-contract fragility)** — no in-repo strict-filter subscriber today. S3035 adds a first consumer (frontend polling endpoint) but it consumes JSON-decoded events tolerant of unknown/missing fields.
- **S3034 A2 Fold (adjacent-axis superseded/experiment as future terminal states)** — carried unchanged.

### Carried from S3032 → S3026 — all preserved from S3034 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0** (S3035 is net-new feature, not drift/hardening; PLAYBOOK-7.7.5 does not fire; no amendment this session).
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (S3035 planned end-to-end from 00-START Option A candidate #2 with scope-shape correction pre-T1).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **1× substantive T1 SIGN (4 tool_runs) + 1× substantive A2 SIGN (8 tool_runs, read + search). Zero rubber-stamp. 21 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Applied at scope-shape finding (Option 1 vs Option 2 decision framing before T1).
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` post-merge; event recorded in `logs/recycle_events.jsonl`.
- **Fold classification (PLAYBOOK-6.10.8):** 5 folds this session (3 same-PR RESOLVED + 1 accept_best_effort_noise + 2 future_trigger). All persisted BEFORE docs cascade.
- **Verify-before-build (Cycle 1A):** **20th consecutive session** — scope-shape finding pre-T1 that reshaped the arc from "just add event type" to "wire polling panel + Redis ring buffer + degraded flag" per the actual runtime evidence.

---

## Wrapper pin note

The active PA conversation pin at S3035 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S3035 is the first arc in the canonical-lifecycle series to ship user-visible surface (previous 9 arcs were substrate). The polling-panel-over-WebSocket choice was ratified in-terminal via the "do we lose anything / is it more work later" framing after the scope-shape finding (BoardroomTab uses polling, no WebSocket subscription, no bridge between Redis PubSub `agent_learning` channel and Channels group `agent_learning_feed`). Fresh terminal recommended for S3036 given 10 PRs across 9 sessions in the S3026→S3035 arc series.

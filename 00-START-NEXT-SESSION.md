# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3020 CLOSED. **A.2 pattern generalization audit shipped + 3 real gaps fixed same-PR.** The 5-session memory-* auth arc is now closed (S3016 audit → S3017 decorator → S3018 invariant → S3019 predicate → S3020 audit+generalization). PR #3725 shipped the audit script, findings doc, and F-1/F-1b/F-2 remediation. Rigby T1 REVISE surfaced a 3rd real gap (cluster ownership) I missed on first pass — folded same-PR. 59/59 tests pass. Live smoke: anon → 401 on both endpoints. **Rigby T1 catches 4 sessions in a row** — the zoom-out ask is validated as a reliable class-adjacent gap detector.

**1 feature PR shipped this session (with in-PR REVISE cycle).**

**PR #3725 (`f5c7823166d0`) — `feat(s3020): audit + fold F-1/F-2 memory-clusters scope guards`.**

- **NEW** `scripts/audit_unscoped_gets_s3020.py` — grep-based candidate generator for unscoped `Model.objects.get(id=)` sites.
- **NEW** `docs/audits/UNSCOPED_GETS_S3020.md` — audit findings + methodology.
- **NEW** `docs/audits/unscoped_gets_s3020.json` — raw per-hit output.
- **MODIFIED** `core/views_memory_clusters.py` — F-1 (add-memory-to-cluster) + F-1b (cluster ownership per Rigby REVISE) + F-2 (find-similar) all fixed. `@token_auth_required` decorator + `scope_queryset_agent_memory` + inline cluster-ownership filter.
- **NEW** `core/tests/test_s3020_memory_clusters_scope.py` — 8 tests.
- **MODIFIED** `tests/security/public_paths_gate_snapshot_gated.json` + `public_paths_gate_snapshot_ungated.json` — snapshot regen (29 → 31 `decorator:token_required`).
- **Test result:** 59/59 pass in 8.494s.
- **Live smoke:** both endpoints anon → 401 confirmed.

**HEAD at close:** docs cascade → `f5c7823166d0` (PR #3725).

Full context:
- `docs/handoffs/SESSION_3020_UNSCOPED_GETS_AUDIT_AND_MEMORY_CLUSTERS_SCOPE.md` — full session close.

---

## S3021 primary directive candidates

**No in-flight arc.** Chris directive-required. **Five consecutive substrate-hardening sessions.** Watch for balance signal from Chris — options span both engineering-forward and continued audit-forward.

### Option A — Fresh engineering (per bias-engineering-over-audit rule)

**Recommended for balance.** 5 audit/hardening sessions in a row is a lot.

- **U5:** post-create auto-link cluster ↔ initiative via `initiative_signal_linker.auto_link_initiative_signals()`. ~30 min.
- **U4:** AgentDecisionSummary bulk-decide. ~1 session.
- **U6:** per-row name editing in bulk cluster confirm modal. ~1 session.

### Option B — Continue audit trajectory

- **S3020 Fold A:** audit script per-hit/per-function suppression refactor. Eliminates the file-level false-negative risk. ~30 min.
- **Audit script multiline regex extension** — catch `.filter(...)\n.get(...)` split across lines.
- **Extend predicate universe** as new predicates land.

### Option C — S3018 Fold extensions

- **Fold B (S3018 REVISE-2):** test-time advisory telemetry for decorator-chain-break. ~1 session.
- **Method-decorator detection extension:** catch `@method_decorator(superuser_required)` on CBV methods. ~1 session.

### Option D — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option E — Housekeeping

- Dedupe `/api/celery/` PUBLIC_PATHS entry.
- 9th test coupling from S3013 non-blocking carry.

### Option F — Chris's own priority (supersedes A/B/C/D/E)

**Joint recommendation at close:** **Option A (U5 — auto-link)** for engineering-vs-audit balance. If Chris wants to keep hardening, Option B Fold A refactor is 30 min.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3020 handoff (`docs/handoffs/SESSION_3020_UNSCOPED_GETS_AUDIT_AND_MEMORY_CLUSTERS_SCOPE.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `f5c7823166d0` (PR #3725) → `95158a509` (S3019 close cascade).
   - `python manage.py test core.tests.test_s3020_memory_clusters_scope --keepdb` — 8/8 OK.
   - `python manage.py refresh_public_paths_gate_snapshot --dry-run` — should return `31 decorator:token_required, 98 drf:IsAuthenticated, 604 none`.

---

## S3021 carry-forward seeds

### New from S3020

- **Fold A** — audit script per-hit / per-function suppression refactor.
- **Fold B** — `scope_queryset_memory_cluster` predicate candidate (watch for 2nd trigger where M2M-through-Agent inline pattern is duplicated).
- **Audit multiline chained `.filter(...).get(...)` regex extension.**
- **Predicate universe expansion** as new predicates land in `object_authz.py`.
- **Rigby T1 REVISE-catches-real-bug pattern** — 4 consecutive sessions (S3017 F-3 sibling, S3018 split-snapshot, S3019 test-helper, S3020 cluster ownership). Zoom-out ask validated.

### Carried from S3019 (STATUS UPDATED)

- **S3019 forward-carry: A.2 pattern generalization** — **CLOSED by S3020 PR #3725**.
- **S3019 Fold B (predicate-shape-table)** — still open.

### Carried from S3018 (STATUS PRESERVED)

- **S3018 Fold B (test-time advisory for decorator-chain-break)** — still open, future arc.
- **S3018 Fold D (Rigby response truncation 1st trigger)** — still at 1st trigger.
- **Method-decorator detection extension** — still open.

### Carried from S3017 / older — all preserved from S3019 close 00-START (see S3019 handoff for full carry list).

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship + 1× in-PR REVISE cycle.**
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **1× substantive Rigby SIGN cycle (T1 with REVISE catching real bug). Zero rubber-stamp. 12 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: initial ratification (Option A audit) + 1× same-PR fold ratification (F-1/F-2 remediation).
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3725 merge.
- **Fold classification (PLAYBOOK-6.10.8):** 3× `same_pr_actionable → resolved` (cluster ownership, test tightening, F-3 hand-review). 1× `future arc` (Fold A script refactor).

---

## Wrapper pin note

The active PA conversation pin at S3020 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3020 shipped 1-PR arc with in-PR Rigby REVISE catching a real bug (cluster ownership) and one hand-reviewed FP (F-3 cockpit VIP). The 5-session memory-* auth trajectory is fully closed. S3021 opens with no in-flight arc; watch for engineering-vs-audit balance signal from Chris (5 substrate-hardening sessions in a row).**

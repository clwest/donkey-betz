# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3033 CLOSED. **Engineering Playbook v0.11.0 RATIFIED.** 1 new [GR] rule PLAYBOOK-7.7.5 (class-scoped mandatory A2 sweep for drift/hardening intents) codifies the 3-cycle in-wild Fold C pattern that accreted across S3029 DISCOVERY + S3030/S3031 CLEAN cycles. Rule count: 211 → 212. Rigby T1 SIGN all 5 dimensions AGREE with 1 `same_pr_mitigatable` refinement folded same-envelope (shape-signature naming + adjacent-class boundary + "at minimum" prefix + clean-sweep-first-class explicit). Chris D-verdict: **"ship it"**. **19-session zero-hallucination Rigby SIGN streak. 18th consecutive Cycle 1A verify-before-build session. 6th consecutive MINOR Playbook amendment shipped in single-session shape.**

**HEAD at close:** `180bd4e65` (PR #3755 — v0.11.0 amendment bundle) + wrapper pin bump cascade.

Full context:
- `docs/handoffs/SESSION_3033_PLAYBOOK_V0_11_0_RATIFIED.md` — current session close.
- `docs/research/implementation/RATIFICATION_2026-07-28_PLAYBOOK_V0_11_0.md` — amendment provenance envelope (8 sections).
- `docs/ENGINEERING_PLAYBOOK.md` §7.7.5 — the ratified rule.

---

## S3034 primary directive candidates

**No in-flight arc.** Playbook v0.11.0 ratified; S3026 → S3032 canonical-promotion arc closed at S3032; S3033 was Fold C 3rd-cycle codification (~30 min planned, ~1 hour actual with proper envelope/handoff/cascade). One operator carry still open:
- Run `python manage.py backfill_canonical_drift --apply` against Railway prod when convenient (S3030 carry).

### Option A — Continue engineering (bias-engineering rule)

- **`bulk_reject_decisions` broadcast symmetry** (~1 session): add `canonical_decision_rejected` broadcast for symmetry with `canonical_decision_promoted`. Natural adjacent play — extends the pattern to the deprecation side of the promotion lifecycle. First real-world exercise of PLAYBOOK-7.7.5 could be this arc if it declares "hardening-class" intent.
- **S3024 Fold A backend-source default preview API** (~1 session): removes frontend/backend default-formatter shadowing. Watch-for-2nd-trigger.
- **S3025 Fold C codification (BulkPromoteModal reducer extraction)** (~30-45 min).

### Option B — Design-arc candidates (needs Chris ratification)

- **KnowledgeTransfer model realignment for canonical decision persistence** — Multi-session.
- **Governance unification (Rigby A1 zoom-out standing carry, S3023):** HAI vs ADS lifecycle families. Multi-session.

### Option C — Audit trajectory

- **S3020 Fold A:** audit script per-hit/per-function suppression refactor. ~30 min.

### Option D — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option E — Chris's own priority (supersedes A-D)

**Joint recommendation at close:** `bulk_reject_decisions` broadcast symmetry is the natural first real-world exercise of PLAYBOOK-7.7.5 — the arc is small, the class-triggering intent ("hardening-class: broadcast side of the promotion lifecycle") is clear, and the sweep dimensions are pre-defined by the existing `canonical_decision_promoted` codebase. Would confirm the rule's usability in-wild on a fresh arc.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md (v0.11.0 constitutional anchor now current).
3. Read S3033 handoff (`docs/handoffs/SESSION_3033_PLAYBOOK_V0_11_0_RATIFIED.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show `180bd4e65` feat(s3033) v0.11.0 amendment at top (or wrapper-pin-bump cascade above it if that shipped separately).
   - `grep -c "^\*\*\[GR\] PLAYBOOK-" docs/ENGINEERING_PLAYBOOK.md` — should show 100+ (actual rule count varies with [GR] density; use frontmatter `rule_count: 212` as authoritative).

---

## S3034 carry-forward seeds

### New from S3033

- **Fold B `procedural observation`** — ledger persistence timing. `record_zoom_out_concern` call ran POST Chris D-verdict rather than BEFORE (PLAYBOOK-6.10.8 requires classify+persist before D-verdict; graceful-degradation permits deferral only for tool failure). Backfilled inside ship bundle per v0.9.0 §4.3 precedent. **Watch for 2nd trigger** to determine whether a PLAYBOOK-6.10.8 sequencing sub-rule is warranted.

### Carried from S3032 (STATUS PRESERVED)

- **S3030 prod deploy carry** — still open.
- **S3032 Fold E `2nd cycle, non-blocking accretion evidence`** — `orm_inspect_tool` allowlist growth pattern. If N+2 more accretion PRs land in short succession, revisit periodic-sweep RFC.
- **S3031 Fold A `2nd trigger` (bool-return semantics discipline)** — carried unchanged.
- **S3031 Fold B `informational` (spy fragility)** — carried unchanged.

### Carried from S3029 → S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — evidence-driven investigation. S3033 T1 SIGN adds additional supporting evidence (6 tool_runs).
- **S3026 Fold B `informational`** — spec-invalidation watch.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment.

### Carried from S3025 / S3024 / older — all preserved from S3032 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0** (this session's amendment — new anchor).
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow A meta-spec→ship** this session (Playbook amendment itself walked the 9-phase contract).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **1× substantive Rigby T1 SIGN with 6 tool_runs inline. Zero rubber-stamp. 25 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Applied at Phase 5 ("do we lose anything?" + "is it more work later?" + ≤1 decision).
- **Class-scoped A2 sweep (NEW):** PLAYBOOK-7.7.5. First activation for future drift/hardening arcs starting S3034.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` post-merge; SHA in `logs/recycle_events.jsonl`.
- **Fold classification (PLAYBOOK-6.10.8):** 1 fold `same_pr_mitigatable` (RESOLVED same-envelope) + 1 fold `procedural observation` (Fold B — carried).
- **Verify-before-build (Cycle 1A):** **18th consecutive session** — 3-handoff read + Playbook §7.7 body + evidence-SHA verify before T1.

---

## Wrapper pin note

The active PA conversation pin at S3033 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. Playbook v0.11.0 is now the active governance version.** S3034 opens with either `bulk_reject_decisions` broadcast symmetry (~1 session, first real-world exercise of the new PLAYBOOK-7.7.5 rule) or Chris's own priority (supersedes). Consider fresh terminal if desired — S3033 was ~1 hour focused work with moderate context density.

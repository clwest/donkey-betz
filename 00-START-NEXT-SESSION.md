# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2000+ Event / Integration Architecture arc pin `pa-dd7e973617da464d` is ACTIVE as of S2000 open 2026-07-04 (preserved through S2001 close 2026-07-04 + S2002 close 2026-07-04). Minted via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2000+ arc (S2000 → S2001 → S2002 → **S2003** → S2004 → S2099) — playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2000+ P2 CAT B LANDED AT S2002; NEXT-SESSION = S2003 P3 CAT C CROSS-SUBSTRATE COMPOSITION DESIGN

**Group 2000+ Event / Integration Architecture arc: S2000 parent shipped + S2001 P1 shipped + S2002 P2 shipped → next is S2003 P3 Cat C Cross-Substrate Composition Design child audit** per parent `2000_event_integration_architecture_domain_scoping.md` §5.3.

- **Active arc pin:** `pa-dd7e973617da464d` — preserved through S2002; no rotation between children per playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.
- **Arc progress:** S2000 parent (shipped) + S2001 P1 Cat A EventBus Producer/Consumer Map + Contract Verification (shipped) + S2002 P2 Cat B HAI Event Contract Design (shipped) → S2003 P3 (next) → S2004 P4 → S2099 xx99 canonical summary. On-track for 6-session arc-completion path per parent §9.3.

## READ THIS THIRD — S2002 P2 CAT B CHILD AUDIT LANDED; SIGN CYCLE 1 PASS ACROSS 4 BATCHES; 12 FOLDS LANDED PRE-COMMIT; CHRIS AGREE-ALL D8N-a/b/c/d

Session 2002 shipped the **Group 2000+ P2 Cat B HAI Event Contract Design child audit** at `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md` (`status: draft`, `category: research`, `session: 2002`, `child_slot: P2_cat_b`, `domain_slug: event_integration_architecture`, `research_group: 2000`, `mission_type: child_audit`; ~2896 lines post-Rigby SIGN cycle 1 12 folds landed pre-commit; FIRST design-contract-shape audit under Research OS in contrast with descriptive-audit shape at S2001).

**S2002 P2 audit ships all 6 parent §5.2 deliverables:**

- **§7 HAI Event Schema Contract for 4 HAI candidate transitions** — per-transition tables §7.1-§7.4 with §7.0 shared 12-field envelope (`schema_version` + `event_type` + `event_id` + `emitted_at` + `producer` + `producer_version` + `source_kind` + `authority_scope` + `idempotency_key` + `mission_id` + `boundary_crossed` + `caller_actor`) + typed payload fields mapped 1:1 to current HAI/HFR/HumanPreference model fields where possible. HAI_AUTO_ESCALATED reduced to v0.x reserved-minimal per SIGN batch 3 Q8 FOLD (pending R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE break-point D resolution); full non-binding draft in §20.14.
- **§10 Event Flows — six-plane learning-surface event schema** — 6 planes × per-plane transition event × source_kind enum binding + subsumption rules for HAI-mediated + verification_outcome planes into §7.1 + §7.2 with single-emission rule + double-emission detector per SIGN batch 2 Q6 STRENGTHEN.
- **§12 Schema Alternatives Rejected (versioning policy pick)** — D1 = adopt S1275 per-event `schema_version` semver top-level envelope field with substrate-split rule per SIGN batch 1 Q1 FOLD (EventBus top-level; OpsRunEvent may use `payload.schema_version` until first-class envelope columns). 4 alternatives rejected §12.2/12.3/12.4/12.5/12.6.
- **§17.3 + §17.4 Two-class retention posture** — D3 (Class-1 governance audit-forever OR bounded-history via HFR/HAI + EventBus mirror; Class-2 learning-surface Redis MAXLEN=10000 bounded) + audit-critical test + Class-2 → Class-1 promotion rule per SIGN batch 1 Q2 STRENGTHEN.
- **§17.2 Consumer registry** — 20 rows across 4 HAI candidates + 4 plane events + 3 F.PER-USER-AUTHORITY events + REQUIRED/OPTIONAL/DEFERRED tags + Exists-today column + activation-mode discipline (§17.5) + teeth clause preventing S2001 F9 recurrence + DEFERRED graduation-trigger + default-owner obligation per SIGN batches 2/3/4 folds. `security_audit_consumer` REQUIRED across 3 governance events per SIGN batch 2 Q5 FOLD.
- **§20.9 F.PER-USER-AUTHORITY-MECHANISM event-emission contract** — 3 events (AUTHORITY_CHECK_EVALUATED + AUTHORITY_DECISION_OVERRIDDEN + AUTHORITY_POLICY_BOUND_TO_USER) as provisional contract surface + audit-log-first classification + volume rationale + storm-audit extension hook per SIGN batch 3 Q7 STRENGTHEN. MECHANISM out-of-scope per parent §5.2.

**5 load-bearing design decisions D1-D5:**

- **D1** — Adopt S1275 per-event `schema_version` (§12.1).
- **D2** — Adopt R.HAI.SOURCE-KIND-ENUM-ADR enum as envelope field (§7.0 + §7.5).
- **D3** — Two-class retention posture (§17.3).
- **D4** — Activation-mode as first-class consumer registry contract obligation (§17.5, reframed from beat-enrollment per SIGN batch 3 Q9 STRENGTHEN).
- **D5** — Hybrid canonical+mirror emission strategy per §7.9 (canonical EventBus + optional OpsRunEvent mirror with same event_id; Class-1 governance events only per SIGN batch 4 Q10b FOLD).

**23 findings F0-F22** covering boundary_violation + dead_code + technical_debt + drift + missing_connection + unclear_owner + mature_primitive + extraction_candidate types. Load-bearing: F19 HIGH (auto_escalate blocked on break-point D) + F21 MEDIUM (OpsRunEvent write-volume risk at platform scale) + F22 MEDIUM (security_audit_consumer ownership gap).

**Rigby SIGN cycle 1 PASS at 0.79-0.82 confidence with 12 folds landed pre-commit across 4 batches** on preserved Group 2000+ arc pin `pa-dd7e973617da464d`:
- Batch 1 (Q1 FOLD substrate-split rule + Q2 STRENGTHEN audit-critical test + Q3 STRENGTHEN idempotency+audit-receipt discipline)
- Batch 2 (Q4 STRENGTHEN canonical+mirror rule §7.9 + Q5 FOLD security_audit_consumer REQUIRED + Exists-today column + Q6 STRENGTHEN single-emission rule + double-emission detector + shared wrapper mandate)
- Batch 3 (Q7 STRENGTHEN §20.9 provisional surface + volume rationale + Q8 FOLD auto_escalate reserved-minimal + §20.14 non-binding appendix + Q9 STRENGTHEN activation-mode reframe)
- Batch 4 (Q10 FOLD cross-section consistency — HAI_AUTO_ESCALATED consumer downgrade + §7.9 Class-1-only scope + §17.5 teeth clause + Q11 STRENGTHEN F21+F22 findings + DEFERRED graduation-trigger obligation + Q12 STRENGTHEN meta-methodology capture via §20.15 for xx99 §10 handoff)

Cycle 2 NOT REQUIRED. **D48 40th arm turn 1 CLEAN across 4 batches → 32-consecutive-fully-clean-arms sub-pattern EXTENDED to 35-consecutive** per multi-batch design-contract SIGN criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 34 → 35 at S2002 close).

**Chris "AGREE ALL" ratification 2026-07-04** on D8N-a schema per transition + D8N-b versioning policy + D8N-c retention posture + D8N-d consumer registry per parent §5.2 Chris-gate.

**§20.15 meta-methodology capture for xx99 §10 handoff** — batched-SIGN validated for large design-contract audits (2896 lines / 4 batches / 12 questions / 12 folds / confidence 0.79-0.82) + playbook §11.2 template update suggestion adding Contract Surface Matrix + Consistency Invariants Checklist for design-contract-shape audits (candidate promotion via two-triggers rule if second design-contract arc confirms).

## S2003 P3 next-session priority

**S2003 P3 Cat C Cross-Substrate Composition Design child audit** per parent §5.3. Runtime target 1 session.

**Scope:** Designs the separation contract across the 6 event-emitting substrates (EventBus + WebSocket + CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord). Answers S1273 §3.31 known-drift questions. Inherits F.SYMBOL-MAPPING-STATUS-VERIFICATION audit + F.PER-USER-AUTHORITY event-emission contract from P2 §20.9.

**Deliverables:**

- **6-substrate separation contract** — canonical rule set: "when does a new emission go to EventBus vs. WebSocket vs. CeleryTaskEvent vs. LLMCallEvent vs. OpsRunEvent vs. ToolCallRecord?" Per-substrate criteria. Explicit "these emit to more than one substrate intentionally" register consuming S2002 §7.9 canonical+mirror rule as one case.
- **Duplicate-emission audit** — grep for existing sites that emit to multiple substrates. Classify intentional vs. drift. Flag drift for post-arc T-slot cleanup.
- **Substrate × HAI-event mapping** — from S2002 P2's HAI event schema (§7 + §10), map each event to its intended substrate(s) per S2002 D5 recommendations. Verify no unintentional duplicate emission per S2002 §14.3 double-emission detector inheritance.
- **Symbol Mapping graduation status verification** — per F.SYMBOL-MAPPING-STATUS-VERIFICATION inheritance from Group 1900 §19. Audit S1274 §11 4-trigger monitoring status (which triggers have fired? which are in warn-mode? which are green?). Recommend graduation timing OR extension.
- **DLQ retention decision** — pair with joint retention ADRs from Groups 1700 + 1800; recommend TTL vs. unbounded. Inherits S2002 §17.3 two-class posture + S2001 F14/F15 handler-failure DLQ gap constraint.
- **WebSocket ↔ EventBus overlap resolution** — S1273 §3.31 drift item; audit specific overlap sites and recommend canonical assignment.

**Deliverable path:** `docs/research/domains/event_integration_architecture/2003_event_integration_architecture_cat_c_cross_substrate_composition_design_child_audit.md` per playbook §11.2 template.

**Prereqs:**

- S2002 P2 shipped (§7 HAI event schema + D5 per-transition substrate recommendations + §7.9 canonical+mirror rule as one arbitration case).
- S2001 P1 shipped (EventBus baseline + F9/F14/F15 constraints).
- S1273 §3.31 EventBus inventory (shipped).
- S1899 §8.1 items 4 + 5 (joint retention + source_kind ADRs — parked T0/Gate; P3 inherits scope hooks but does not execute the ADRs).

**Rigby SIGN cadence:** Cycle 1 pre-commit per parent §5.3.

**Chris-gate:** Multi-verdict at close for (a) separation contract, (b) duplicate-emission cleanup priorities, (c) DLQ retention posture, (d) WebSocket ↔ EventBus canonical assignment.

## Session-open protocol (universal)

1. `context-kit orient` — source-of-truth chain + latest handoff.
2. Absorb this `CLAUDE.md` + `MEMORY.md` (both auto-injected).
3. Read this `00-START-NEXT-SESSION.md` in full.
4. Read Research OS §0–§5 (skim §6–§9 headings).
5. Record repo state (branch + SHA + `git status`).
6. Note request context (change vs explain; explicit constraints; for bugs: repro path).
7. Classify the request via OS §5 router → load the matching §8 startup contract.
8. If PA calls will happen: verify `service_context: local` via `platform_config_tool overview`.
9. Verify arc pin `pa-dd7e973617da464d` still routed via `tools/pa_local.sh:215` (Group 2000+ arc-standard).

## Post-commit docs cascade for S2002 close

Per `feedback_docs_cascade_at_every_close.md` + `feedback_cascade_pr_must_include_embed_step.md` — MUST run all 4 steps after commit merges:

1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py embed_documents --all-unembedded` (state chunk count in PR body as evidence)

Then `python manage.py build_docs_provenance` per §11.4 provenance discipline.

# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2000+ Event / Integration Architecture arc pin `pa-dd7e973617da464d` is ACTIVE as of S2000 open 2026-07-04 (preserved through S2001 close + S2002 close + S2003 close 2026-07-04). Minted via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2000+ arc (S2000 → S2001 → S2002 → S2003 → **S2004** → S2099) — playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2000+ P3 CAT C LANDED AT S2003; NEXT-SESSION = S2004 P4 CAT F ADJACENT / SEPARATION BOUNDARIES CONSOLIDATION

**Group 2000+ Event / Integration Architecture arc: S2000 parent shipped + S2001 P1 shipped + S2002 P2 shipped + S2003 P3 shipped → next is S2004 P4 Cat F Adjacent / Separation Boundaries CONSOLIDATION child audit** per parent `2000_event_integration_architecture_domain_scoping.md` §5.4.

- **Active arc pin:** `pa-dd7e973617da464d` — preserved through S2003; no rotation between children per playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.
- **Arc progress:** S2000 parent (shipped) + S2001 P1 Cat A (shipped) + S2002 P2 Cat B (shipped) + S2003 P3 Cat C (shipped) → S2004 P4 Cat F (next) → S2099 xx99 canonical summary. On-track for 6-session arc-completion path per parent §9.3.

## READ THIS THIRD — S2003 P3 CAT C CHILD AUDIT LANDED; SIGN CYCLE 1 PASS ACROSS 4 BATCHES; 12 FOLDS LANDED PRE-COMMIT; CHRIS AGREE-ALL D-VERDICT a/b/c/d/D5

Session 2003 shipped the **Group 2000+ P3 Cat C Cross-Substrate Composition Design child audit** at `docs/research/domains/event_integration_architecture/2003_event_integration_architecture_cat_c_cross_substrate_composition_design_child_audit.md` (`status: draft`, `category: research`, `session: 2003`, `child_slot: P3_cat_c`, `domain_slug: event_integration_architecture`, `research_group: 2000`, `mission_type: child_audit`; ~1900 lines post-Rigby SIGN cycle 1 12 folds landed pre-commit; SECOND design-contract-shape audit under Research OS after S2002).

**S2003 P3 audit ships all parent §5.3 deliverables:**

- **§10.2 6-substrate separation contract** — three-axis selector (Axis A coordination-vs-telemetry + Axis B canonical audience + Axis C retention class) + per-substrate criteria table with sanctioned use cases + forbidden use cases + dual-emission cases. OpsRunEvent-not-canonical-coordination discipline per SIGN batch 1 Q1 STRENGTHEN.
- **§10.3 intentional-dual-emission register** — 5 sanctioned patterns: §10.3.1 Class-1 canonical + mirror (S2002 §7.9 inheritance) + §10.3.2 audit-table backing + §10.3.3 Class-2 canonical-only + **§10.3.4 NEW WebSocket UI-render fanout** with mandatory `ui.render_hint` envelope + payload MUST NOT clause + code-review anti-pattern per SIGN batch 1 Q2 FOLD + §10.3.5 parallel-telemetry-per-concern with concern-boundary defs + duplicate-emission drift test per SIGN batch 2 Q4 STRENGTHEN.
- **§10.4 substrate × HAI-event mapping** — 12 events (4 HAI candidates + 3 F.PER-USER-AUTHORITY per S2002 §20.9 + 5 plane events per S2002 §10) with canonical + mirror substrate assignments; bound to §14.3 double-emission detector via `mirror_of` tag + scope gate for HAI-adjacent events per SIGN batch 1 Q3 STRENGTHEN.
- **§10.5 WebSocket ↔ EventBus overlap resolution** — audit ~40 `channel_layer.group_send` call sites with per-site canonical assignment recommendation. D4 canonical rule: cross-service backend → EventBus; browser session-scoped UI → WebSocket; both required → EventBus canonical + WebSocket UI-render fanout per §10.3.4. T2 slot split by owning-app T2a-T2g with central rubric per SIGN batch 4 Q10 FOLD.
- **§14.1 F11 T1 slot** — spider-data substrate consolidation with compat-shim discipline for `SpiderAgentConnector` → `SpiderAgentRouter` rename (60-day deprecation window + `DeprecationWarning` + removal criteria) per SIGN batch 2 Q6 FOLD. Rigby verified 6-file name-grep + 45-file `__class__.__name__` grep confirms zero runtime-name-lookup breakage risk.
- **§15.1 D3 conditional DLQ retention posture** — D3.a canonical MAXLEN=1000 post F14+F15 closure; D3.b interim non-binding + correctness via S2002 §17.1 rules 6/7 (at-least-once + idempotency + replay/monitoring + audit-receipt) per SIGN batch 3 Q7 FOLD. F14 owner=Group 2000+ + F15a owner=Group 2000+ + F15b owner=Group 1700 Observability split-by-concern per SIGN batch 3 Q8 STRENGTHEN.
- **§17.1 graduation trigger + F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN §19.10.4** — when ≥3 canonical + mirror producers ship OR any HAI transition emits canonical + mirror → re-run §14.3 detector + §10.3 register re-validation + DLQ flow verification per SIGN batch 3 Q9 STRENGTHEN.
- **§19.1 F.SYMBOL-MAPPING-STATUS-VERIFICATION audit** — against S1274 §10.3.1 four graduation triggers with under-sampling detector (activity floor ≥50/day OR ≥350 rows/7d) per SIGN batch 4 Q11 STRENGTHEN. **Empirical D5 resolution at S2003 close: `authority_action_observed` rows = 0 across all time → triggers 1+2 UNKNOWN/UNDER-SAMPLED per activity-floor precondition; not a policy change, only measured outcome under Chris's ratified conditional shape.** F.SYMBOL-MAPPING-EMISSION-VERIFICATION §19.1.6 T-slot registered.
- **§20.8 meta-methodology capture** — SECOND design-contract-shape application (after S2002) confirms playbook §11.2 v3 promotion recommendation at S2099 xx99 §10.2 with codification bundle (batched-SIGN + Contract Surface Matrix + Consistency Invariants Checklist + concern-boundary defs + under-sampling detector + compat-shim + conditional posture) per SIGN batch 4 Q12 STRENGTHEN.

**5 load-bearing design decisions D1-D5:**

- **D1 (separation contract)** — Three-axis selector + per-substrate criteria table + intentional-dual-emission register + substrate × HAI-event mapping.
- **D2 (duplicate-emission cleanup priorities)** — F11 HIGH T1 slot (spider-data three-substrate drift) + WebSocket overlap MEDIUM T1 slot + no other drift observed.
- **D3 (DLQ retention posture)** — CONDITIONAL: D3.a canonical MAXLEN=1000 post F14+F15 closure; D3.b interim non-binding + correctness via S2002 §17.1 rules 6/7.
- **D4 (WebSocket ↔ EventBus canonical assignment)** — Cross-service backend → EventBus; browser UI → WebSocket; both → EventBus canonical + WebSocket UI-render fanout per §10.3.4 with `ui.render_hint` envelope.
- **D5 (F.SYMBOL-MAPPING graduation status)** — Empirical UNKNOWN/UNDER-SAMPLED at S2003 open pending F.SYMBOL-MAPPING-EMISSION-VERIFICATION T-slot resolution; ratified conditional shape.

**Rigby SIGN cycle 1 PASS at avg 0.80 confidence with 12 folds landed pre-commit across 4 batches** on preserved Group 2000+ arc pin `pa-dd7e973617da464d`:
- Batch 1 (Q1 STRENGTHEN OpsRunEvent-not-canonical + Q2 FOLD ui.render_hint envelope + Q3 STRENGTHEN mirror_of tag binding) at 0.82 avg
- Batch 2 (Q4 STRENGTHEN concern-boundary + drift-test + Q5 STRENGTHEN data-gated promotion + Q6 FOLD compat-shim discipline) at 0.78 avg
- Batch 3 (Q7 FOLD D3 conditional + Q8 STRENGTHEN F14/F15 split-by-concern + Q9 STRENGTHEN adoption-trigger detector-rerun) at 0.81 avg
- Batch 4 (Q10 FOLD T2a-T2g split-by-owning-app + Q11 STRENGTHEN under-sampling detector + Q12 STRENGTHEN two-triggers qualification) at 0.80 avg

Cycle 2 NOT REQUIRED. **D48 41st arm turn 1 CLEAN across 4 batches → 32-consecutive-fully-clean-arms sub-pattern EXTENDED to 36-consecutive** per multi-batch design-contract SIGN criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 35 → 36 at S2003 close).

**Chris "AGREE ALL" ratification 2026-07-04** on 5-verdict decision card: (a) separation contract + (b) duplicate-emission cleanup priorities + (c) DLQ retention conditional posture + (d) WebSocket ↔ EventBus canonical assignment + D5 F.SYMBOL-MAPPING graduation status per parent §5.3 Chris-gate. Empirical D5 resolution landed post-ratification (measured outcome under ratified conditional shape).

## S2004 P4 next-session priority

**S2004 P4 Cat F Adjacent / Separation Boundaries CONSOLIDATION child audit** per parent §5.4. Runtime target 1 session.

**Slot:** Cat F CONSOLIDATION (mirror Group 1700/1800/1900 F pattern; **THIRD-consecutive** F CONSOLIDATION application → MC-6 CODIFICATION-CONFIRMED milestone at S2099 close).

**Scope:** Consolidate the separation-boundary posture between Event / Integration Architecture and every adjacent domain surface.

**Scope precision (inheriting Group 1900 P4 discipline):** This is a **separation-boundary posture audit (interface + seam audit)** — a review of interfaces, seams, emission touchpoints, consumer-registration seams, and cross-substrate composition joins between Event / Integration and each adjacent domain. It is **NOT** an audit of each adjacent domain's internal correctness or implementation quality.

**Deliverables:**

- **Separation-boundary posture audit (interface + seam audit)** for each plane event/integration touches: Memory (Group 1300) / Sports (Group 1500) / Content (Group 1600) / Observability (Group 1700) / HAI (Group 1800) / Authority Enforcement (Group 1900) / Employee OS / Frontend / API / Discord.
- Register "emission touchpoints" — where does an adjacent domain write to a substrate? Are there duplicate emissions? Are there gap points where a domain assumes an event fires but P2's contract doesn't cover it?
- Register "consumer-registration seams" — where does an adjacent domain subscribe to a substrate? Are subscribers registered? Are there orphaned subscribers?
- Register "separation boundary posture" — which emission decisions are owned by Group 2000+ vs. delegated to a domain's own governance/telemetry layer?
- Follow-on queue candidates for post-arc T-slot execution.

**Deliverable path:** `docs/research/domains/event_integration_architecture/2004_event_integration_architecture_cat_f_adjacent_separation_boundaries_child_audit.md` per playbook §11.2 template + §16 CONSOLIDATION shape from S1806 Group 1800 Cat F + S1904 Group 1900 Cat F precedent.

**Prereqs:**

- S2001 P1 shipped (EventBus baseline + F8 dual-mechanism drift + F18 handler decorativeness).
- S2002 P2 shipped (HAI event schema + §7.9 canonical+mirror + §17.2 consumer registry + §17.3 retention posture + §20.9 F.PER-USER-AUTHORITY).
- S2003 P3 shipped (6-substrate separation contract §10.2 + duplicate-emission audit §17 + F.CANONICAL-MIRROR-ADOPTION-DETECTOR-RERUN §19.10.4 + T2a-T2g split-by-owning-app + F.SYMBOL-MAPPING-EMISSION-VERIFICATION §19.1.6 + T-slot chain).

**Rigby SIGN cadence:** Cycle 1 pre-commit per parent §5.4.

**Chris-gate:** Ratification at close.

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

## Post-commit docs cascade for S2003 close

Per `feedback_docs_cascade_at_every_close.md` + `feedback_cascade_pr_must_include_embed_step.md` — MUST run all 4 steps after commit merges:

1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py embed_documents --all-unembedded` (state chunk count in PR body as evidence)

Then `python manage.py build_docs_provenance` per §11.4 provenance discipline.

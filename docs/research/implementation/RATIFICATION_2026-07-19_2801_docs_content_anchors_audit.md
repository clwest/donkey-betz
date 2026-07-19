---
title: "Ratification envelope — S2834 T1 anchor & canonical-doc content audit (child 2801) + schema v1.1"
date: 2026-07-19
session: 2834
ratifier: Chris
verbatim_directive: "ratify T1 as-is + schema v1.1"
target_doc: docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md
research_group: 2800
thread: T1
parent_arc: docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
sign_pin: pa-5fa195547db04260
sign_cycles: 3
category: governance
deliverable_type: ratification_record
---

# S2834 — T1 anchor & canonical-doc content audit RATIFICATION

## 1. Ratification statement

Chris D-verdict at S2834 close (2026-07-19):

> ratify T1 as-is + schema v1.1

**Scope of ratification:**

- Full T1 audit doc (`2801_docs_content_anchors_audit.md`) as authored,
  including all 3 Rigby SIGN cycles' folded refinements.
- **Schema §10.1 → v1.1** — 5 new fields (all optional with defaults;
  backward-compatible under permissive YAML parsing; strict parsers
  opt-in via `schema_version: 1.1` frontmatter key).
- §5.5 migration-arc waiver protocol adopted.
- §10.4 root-stability P0 clarification adopted.
- 33-file classified corpus frozen; migration queue routed to future
  §3 execution arc (opens after 2899 arc-close).

## 2. Joint Claude+Rigby SIGN provenance (3 cycles)

### Cycle 1 — 2026-07-19 (5 pressure-test questions)

**Rigby tool_runs (verified non-empty per `feedback_verify_rigby_tool_runs_before_trusting_sign`):** 6 substantive `repo_tool.read` calls:

1. `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md` (parent scoping)
2. `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md` (T1 draft)
3. `docs/topics/personal-assistant.md` (Q1 pressure-test — topics scope)
4. `docs/topics/agent-system.md` (Q1 pressure-test — topics scope)
5. `docs/ARCHITECTURE.md` (Q2 pressure-test — large ref schema)
6. Parent §10 schema deep re-read

**Verdicts:**

| Q | Verdict | Refinement folded |
|---|---|---|
| Q1 corpus completeness | STRENGTHEN | +2 topics canary files (personal-assistant + agent-system); remaining 9 topics route to T3a/T3b |
| Q2 schema refinements | STRENGTHEN | Split `autogen_ok` off `finding_class` into separate `claim_source` attr; codified `[1, N]` whole-doc convention; retained `claim_density_hint` |
| Q3 severity discipline | **DISAGREE** | Removed 2 spurious "class-P0 status-ok" recordings; added `finding_state: active \| resolved`; histogram counts active only |
| Q4 T1 exit gates | AGREE | Exit criteria stand |
| Q5 zoom-out | STRENGTHEN | Added `coverage: full_claim_walk \| structural_only \| deferred` contract-level field |

### Cycle 2 — 2026-07-19 (5 pressure-test questions)

**Rigby tool_runs:** 5 substantive `repo_tool.read` calls verifying cycle-1
folds landed correctly + DOC_LIFECYCLE §3 root-stability semantics.

**Verdicts:**

| Q | Verdict | Refinement folded |
|---|---|---|
| Q6 schema stability | AGREE (with caveat) | Added `schema_version: 1.1` header requirement |
| Q7 P0 discipline | STRENGTHEN | Added §10.4 root-stability P0 clarification |
| Q8 topics generalizability | STRENGTHEN | Added §4.1a T3a pre-scan hint (count_dense vs narrative tagging) |
| Q9 coverage explicitness | STRENGTHEN | Added §5.5 migration-arc waiver protocol |
| Q10 zoom-out #2 — anti-worship | AGREE (lock v1.1 now) | Ship as-is with schema v1.1 at T1 close; further refinements → 2899 close |

### Cycle 3 — 2026-07-19 (3 verification questions)

**Rigby tool_runs:** 5 substantive `repo_tool` calls verifying cycle-2
folds landed correctly + DOC_LIFECYCLE §3 wording alignment.

**Verdicts:**

| Q | Verdict | Refinement folded |
|---|---|---|
| Q11 schema_version placement | STRENGTHEN | Moved `schema_version: 1.1` to frontmatter (single source of truth; no per-row tag needed) |
| Q12 root-stability wording | AGREE | Wording confirmed against DOC_LIFECYCLE §3 lines 113-126 |
| Q13 Chris D-verdict readiness | AGREE | All refinements safely folded; Rigby's suggested D-verdict framing adopted |

### Convergence

Cycle 3 verdicts: 1 STRENGTHEN + 2 AGREE, 0 DISAGREE. Joint Claude+Rigby
convergence reached per `feedback_claude_rigby_agree_first_chris_yes_no`.
Chris D-verdict routed with a single yes/no framing.

## 3. Schema §10.1 → v1.1 delta

All fields backward-compatible (optional with defaults).

| Field | Values | Default | Rationale |
|---|---|---|---|
| `schema_version` (frontmatter) | `1.1` | (absent = v1.0) | Rigby cycle-2 Q6 + cycle-3 Q11 |
| `claim_source` (per-row) | `manual \| autogen` | `manual` | Rigby cycle-1 Q2 |
| `finding_state` (per-row) | `active \| resolved` | `active` | Rigby cycle-1 Q3 DISAGREE |
| `coverage` (per-row) | `full_claim_walk \| structural_only \| deferred` | `full_claim_walk` | Rigby cycle-1 Q5 + cycle-2 Q9 |
| `claim_density_hint` (per-row) | `dense \| sparse \| large_ref_deferred` | (absent = dense) | Rigby cycle-1 Q2 |

**Conventions:**

- Whole-doc findings: `line_range: [1, <total_lines>]` (Rigby cycle-1 Q2)
- Histograms count `finding_state: active` only (Rigby cycle-1 Q3)
- Coverage waiver protocol: any file being MOVED/SUPERSEDED needs
  `coverage: full_claim_walk` OR `structural_only + escalate_to_chris + rationale`
  (Rigby cycle-2 Q9); in-place-only files (rule/policy/NEVER-MOVE) exempt.

**§10.4 root-stability P0 clarification:**

> P0 blocks: (a) destination-subdir migration for migration-eligible
> files, (b) in-place remediation before arc close for root-stable /
> NEVER-MOVE files.

## 4. Real drifts caught + migration queue routing

| Sev | File | Finding | Migration action |
|---|---|---|---|
| P0 | `CLAUDE.md:262` | "Discord bot: 144 commands across 25 Cogs" — contradicts linked doc's S1115 correction AND CLAUDE.md's own autogen block line 148 (which shows 96) | in-place: 144 → 96 (root-stable; §10.4 (b) gate — blocks arc close remediation) |
| P1 | `docs/KNOWLEDGE_PIPELINE.md:25` | ASCII diagram: `SPIDER NETWORK (64 spiders)` — runtime 80 | in-place: 64 → 80 |
| P1 | `docs/topics/personal-assistant.md:6,12,13` | stale runtime counts (104 schemas → 113; 152/169 handlers → 156) | reinforce V1 banner or update inline |
| P1 | `docs/AGENTS.md` / `docs/SPIDERS.md` | drift-known-per-CLAUDE.md but no V1 banner at file top | retrofit V1 banner |
| P2 | `docs/DISCORD_INTEGRATION.md:321` | "Currently at 112" slash commands — runtime 48 | in-place or guardrail-phrase |
| P2 (×9) | 8 large ref docs (ARCHITECTURE / SERVICES / DATABASE_MODEL_REFERENCE / DREAM_INITIATIVE_WORKFLOW / ADVISOR_AUDIT / DISCORD_AUDIT / ARCHITECTURE_INDEX / governance_redesign) + PLATFORM_WHAT_IT_IS refresh cadence banner candidate | `coverage: structural_only` — full walk deferred | migration-arc `full_claim_walk` OR §5.5 escalation waiver |

**Migration queue frozen post-D-verdict. Routing target:** future §3
execution arc that opens after Group 2800 canonical summary (`2899`)
ratifies. Not this arc's execution job (parent §5 non-goals).

## 5. Arc registration

Group 2800 arc state after S2834 T1 close:

- ✅ Parent scoping RATIFIED at S2833 (D1-D9)
- ✅ **T1 anchor content audit RATIFIED at S2834 (schema v1.1 locked)**
- ⏳ T2 reference-graph audit — opens at S2835 (recommended default)
- ⏳ T3a duplicate audit — pre-scan hint recorded (§4.1a topics count_dense tagging)
- ⏳ T3b orphan audit
- ⏳ T4 handoff citation-integrity + retrieval-harm audit
- ⏳ T5 reports + audits triage
- ⏳ 2899 canonical summary (arc close)

**Arc registered:** `docs/research/OPEN_ARCS.md` Group 2800 row advanced
from "parent scoping RATIFIED" to "T1 RATIFIED; T2 next."

## 6. Twin-pointer artifacts

**Repo:**

- Content: `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`
- Envelope: this file
- Handoff: `docs/handoffs/SESSION_2834_T1_ANCHOR_CONTENT_AUDIT.md`
- Arc manifest: `docs/research/OPEN_ARCS.md` (Group 2800 In-progress row updated)

**Workspace UI (per `feedback_twin_deliverable_at_every_ratification`):**

- Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)
- Twin: content mirror + ratification envelope; ORM-direct create per
  `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`
  (category `governance`, `deliverable_type=ratification_record`,
  `diagnostic_status=None`)

## 7. Provenance

- **Session:** 2834
- **Pin:** `pa-5fa195547db04260` (retired at S2834 close, force=true, sixty-fifth
  consecutive per S2770+ pattern)
- **HEAD at ratification:** filled at close cascade PR merge
- **Playbook version:** v0.8.0 (unchanged)
- **Anti-rubber-stamp:** verified non-empty tool_runs across all 3 SIGN cycles
- **Joint agreement:** reached per `feedback_claude_rigby_agree_first_chris_yes_no`
- **Post-merge recycle:** `make recycle-all` per PLAYBOOK-7.4.4 (eightieth
  consecutive close-cycle)

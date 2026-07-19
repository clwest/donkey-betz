---
title: "S2834 T1 — /docs/ Content Audit · Anchor & Canonical-Doc Content Audit (child audit 2801)"
status: ratified (T1 — Chris D-verdict 2026-07-19 S2834; joint Claude+Rigby SIGN 3 cycles; schema v1.1 locked)
authority: child audit under Group 2800 (2800 parent-scoping RATIFIED at S2833 D1-D9; 2801 T1 RATIFIED at S2834)
ratification:
  date: 2026-07-19
  session: 2834
  ratifier: Chris
  verbatim_directive: "ratify T1 as-is + schema v1.1"
  scope: full T1 (33-file corpus classified; schema v1.1 locked; migration queue frozen; §10.4 root-stability P0 clarification adopted; §5.5 migration-arc waiver protocol adopted)
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md
  sign_cycles: 3 (Rigby joint SIGN pin pa-5fa195547db04260; substantive tool_runs across all 3 cycles; anti-rubber-stamp per feedback_verify_rigby_tool_runs_before_trusting_sign; convergence at cycle 3 with 1 STRENGTHEN + 2 AGREE)
  next_action: T2 reference-graph audit opens at S2835 (child audit 2802_docs_content_reference_audit.md); migration queue frozen for future §3 execution arc
session: 2834
date: 2026-07-19
domain_slug: docs_content_audit
research_group: 2800
thread: T1
schema_version: 1.1  # per Rigby cycle-2 Q6 AGREE + cycle-3 Q11 STRENGTHEN — frontmatter-level, single source of truth for the whole audit doc; downstream tooling checks this key before parsing YAML rows
authors: Claude Code (Chris directed at S2833 D-verdict — "open T1 next session")
parent:
  - docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
supersedes: none
related:
  - docs/research/implementation/RATIFICATION_2026-07-19_2800_docs_content_audit_parent.md
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md
  - docs/PLATFORM_INVENTORY.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
  - CLAUDE.md
scope: >
  Content audit of ~31 load-bearing anchor / canonical / onboarding / reference
  docs. Per file, walk each concrete claim (file path, function name, line
  range, count, version number) and verify against HEAD. Emit YAML findings
  per parent §10.1 schema. First child audit — also validates the schema
  before T2-T5 scale-up.
non_goals:
  - fixing any drift found (classification only per parent §5)
  - moves / renames / deletions during the audit
  - re-writing content in-place during the audit
  - modifying §10.1 schema (locked at parent D9 unless Chris ratifies change here)
  - auditing T2-T5 corpora (out of thread scope)
  - auditing docs/topics/** (per parent T1 corpus definition — belongs to T3a/T3b)
  - auditing docs/handoffs/** (T4 quarantine)
head_at_open: 34f701c66605
inventory_generated_at: 2026-07-05 15:51:41  # per docs/PLATFORM_INVENTORY.md
inventory_head: e617af59
owner: claude+rigby (Chris to ratify)
---

# S2834 — T1 Anchor & Canonical-Doc Content Audit

> **What this doc is.** Group 2800's first child audit. Walks 31 load-bearing
> docs against HEAD, emits per-file YAML findings per the parent-locked
> §10.1 schema, and validates the schema shape before T2-T5 scale-up.
>
> **What this doc is not.** A rewrite proposal. A fix. A move manifest. Findings
> classify severity + recommended_action; execution defers to a follow-on
> migration arc that consumes 2899 (arc canonical summary).

---

## 1. Method

### 1.1 Corpus selection — 31 files

Per parent §4 T1: "the ~30 'load-bearing' docs — anchors, canon rows,
governance rows, root-README, `00-START-HERE/**`, `CLAUDE.md`" plus the
S2834 pointer expansion "Any docs cited from CLAUDE.md's
PRIORITY_DOCS/CRITICAL_DOCS graph."

| Bucket | # files | Files |
|---|---:|---|
| Anchors (narrative + runtime + pipeline + behavior + translation) | 5 | `docs/PLATFORM_WHAT_IT_IS.md`, `docs/PLATFORM_INVENTORY.md`, `docs/KNOWLEDGE_PIPELINE.md`, `docs/UDB_BEHAVIOR_LAYER.md`, `docs/UDB_TRANSLATION_LAYER.md` |
| Canon rows | 2 | `docs/canon/INDEX.md`, `docs/canon/creative/DAVINCI_RESOLVE_WORKFLOW.md` |
| Governance | 1 | `docs/governance/SYSTEM_OWNER.md` |
| Onboarding | 3 | `docs/00-START-HERE/DOC_LIFECYCLE.md`, `docs/00-START-HERE/INDEX.md`, `docs/00-START-HERE/README.md` |
| Root | 3 | `CLAUDE.md`, `00-START-NEXT-SESSION.md`, `README.md` |
| CLAUDE.md Reference Documentation graph | 13 | `docs/ARCHITECTURE.md`, `docs/AGENTS.md`, `docs/SPIDERS.md`, `docs/SERVICES.md`, `docs/DATABASE_MODEL_REFERENCE.md`, `docs/API_PATH_POLICY.md`, `docs/DREAM_INITIATIVE_WORKFLOW.md`, `docs/DISCORD_INTEGRATION.md`, `docs/demo_mode.md`, `docs/governance_redesign.md`, `docs/EMPLOYEE_OS_PRIMITIVES.md`, `docs/ADVISOR_AUDIT.md`, `docs/DISCORD_AUDIT.md` |
| Research OS anchors cited from CLAUDE.md §Research Library | 4 | `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`, `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`, `docs/research/ARCHITECTURE_INDEX.md`, `docs/research/OPEN_ARCS.md` |
| Topics canary (Rigby cycle-1 Q1 STRENGTHEN) | 2 | `docs/topics/personal-assistant.md`, `docs/topics/agent-system.md` |
| **Total** | **33** | |

**Topics canary rationale (Rigby cycle-1 Q1):** `docs/topics/**` contains
anchor-shaped, drift-prone numeric and structural claims (tool/handler counts,
agent-category tables) — the failure mode T1 exists to catch, even under
DOC-POINTER-V1 banners. Excluding topics entirely risks pushing high-salience
count-drift into later threads that only check reachability/duplication, not
claim correctness. Compromise: include 2 topics files as canary (PA + agent
system, both anchor-heavy) in T1; remaining 9 topics still go to T3a/T3b for
duplicate + orphan classification.

**Explicitly OUT of T1 corpus** (deferred to later Group 2800 threads):

- `docs/topics/**` remaining 9 files — go to T3a duplicate + T3b orphan.
- `docs/handoffs/**` (1056) — T4 quarantine per parent §4.
- `docs/audits/**`, `docs/reports/**` — T5 triage.
- `docs/research/domains/**` child audit docs (~50) — audited only after their
  own arc closes; live docs during in-flight arcs.
- `docs/decisions/ADR-*.md` — constitutional governance; audit may classify
  drift but never rewrites (per parent §7).
- `docs/ENGINEERING_PLAYBOOK.md` — same reason.

### 1.2 Ground truth

- **Counts** — `docs/PLATFORM_INVENTORY.md` per DOC_LIFECYCLE §2c (sole
  authority). Generated `2026-07-05 15:51:41`, HEAD `e617af59` at generation.
- **Live count refresh (autogen)** — CLAUDE.md's autogen block refreshed via
  `python manage.py refresh_doc_inventory_blocks` (per CLAUDE.md §"Live
  Counts (auto-refreshed)"). Values match `gather_inventory()` runtime.
- **File / function existence** — HEAD `34f701c66605` (S2833 close cascade).
- **Doc-lifecycle rules** — `docs/00-START-HERE/DOC_LIFECYCLE.md` (never-move
  paths §2b, counts authority §2c, root-stability §3).

### 1.3 Claim classes verified per file

Per parent §4 T1: "each concrete claim (file path, function name, line range,
count)." Concretely, per file we scan for:

1. **Numeric counts** (`N agents`, `M services`, `K spiders`) — verify vs
   PLATFORM_INVENTORY or CLAUDE.md live block.
2. **File-path citations** (`core/services/X.py:LINE`, `docs/Y.md`) — verify
   path exists at HEAD; line-range citations spot-checked when specific.
3. **Function / class name citations** — grep against HEAD.
4. **Version numbers** (`v0.8.0`, `Playbook v0.7.0`) — verify vs current
   ENGINEERING_PLAYBOOK.
5. **Session numbers** (`Session 2833`, `S2831`) — verify vs handoffs dir /
   session recency.
6. **Autogen-block staleness signals** (`<!-- DOC-AUTOGEN -->`) — flag
   drift from live runtime.
7. **Cross-doc pointers** — resolve or flag broken.

Not-in-scope for T1 (mechanical grep is T2's job):

- Every relative-path link in every file — T2 owns the reference graph.
- Duplicate content vs peer docs — T3a owns dup detection.
- Reachability — T3b owns orphan classification.

### 1.4 YAML finding rows

All findings emitted in the parent-locked §10.1 shape:

```yaml
- file_path: <path>
  audit_thread: T1
  severity: P0 | P1 | P2 | P3
  finding_class: stale_vs_head | broken_ref | duplicate_content | orphan | superseded_untagged | retrieval_harm | ok
  evidence:
    - line_range: [<start>, <end>]
      claim: "<verbatim claim>"
      runtime_truth: "<verified value>"
      cited_source: <path or `inventory` or `HEAD grep`>
  recommended_action: keep_as_is | update_in_place | retrofit_v1_pointer | retrofit_v2_pointer | consolidate_into | archive | delete | escalate_to_chris
  action_target: null | <path>
  migration_pr_batch_hint: anchor_docs | topic_docs | audits_triage | handoffs_banner | orphans_archive | dup_consolidate | schema_validation
  cross_arc_refs:
    - 2799_3_target_tree_row: <row ID | null>
  notes: <free text>
```

Files where the whole file classifies clean emit one `finding_class: ok` row
with `severity: P3` (informational) — schema requires at least one row per
audited file to preserve the 1:1 corpus/finding correspondence downstream.

---

## 2. Findings — per file

Findings ordered by corpus bucket (§1.1). One YAML block per file.

### 2.1 Anchors (5)

#### `docs/PLATFORM_WHAT_IT_IS.md`

```yaml
- file_path: docs/PLATFORM_WHAT_IT_IS.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [4, 8]
      claim: "status: active, session: 1223, last_reviewed: 2026-06-30"
      runtime_truth: "current session is 2834; last_reviewed 2026-06-30 is 21 days behind; body has S1223 refresh block that reconciles counts through S1223 with explicit disclaimer that live counts always come from PLATFORM_INVENTORY.md"
      cited_source: docs/PLATFORM_WHAT_IT_IS.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Narrative anchor by design — DOC_LIFECYCLE §2c binds counts to PLATFORM_INVENTORY, so PLATFORM_WHAT_IT_IS is a stated non-counts source. The S1223 refresh block explicitly disclaims count freshness (line 9: "Live runtime counts always come from PLATFORM_INVENTORY.md"). No P0/P1 defect.
- file_path: docs/PLATFORM_WHAT_IT_IS.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [9, 27]
      claim: "New since Session 1141: ... 1219-1221 watchdog/timeout arc PR #2519 and #2520 ... 1223 audit #8 close"
      runtime_truth: "current session 2834; last handoff cited is S1223 (2026-06-23); +1611 sessions of history since last refresh"
      cited_source: docs/handoffs/ dir listing
  recommended_action: retrofit_v1_pointer
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Refresh block anchored to S1223. Between S1223 and S2834: OpenAI hardening arc extended, Playbook v0.1.0 through v0.8.0 shipped, docs restructuring arc (Group 2700) opened + §3 ratified, discovery-layer arc (S2818-S2831) with Pattern B/C/D, S2829 metadata layer fix, S2831 RAG diagnostics tab. Per DOC_LIFECYCLE §1 a DOC-POINTER-V1 stats-drift banner at file top would explicitly signal the refresh is 21 days behind. Content itself is not misleading (still describes what platform IS); banner would make freshness legible.
```

#### `docs/PLATFORM_INVENTORY.md`

```yaml
- file_path: docs/PLATFORM_INVENTORY.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [3, 4]
      claim: "Generated: 2026-07-05 15:51:41 · Git HEAD: e617af59"
      runtime_truth: "current HEAD 34f701c66605 (S2833 cascade merged); inventory is 14 days behind; CLAUDE.md live-counts autogen block IS current"
      cited_source: git log
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    PLATFORM_INVENTORY is regenerable via `python manage.py generate_platform_inventory` per its own doc header. Staleness is expected between regens; DOC_LIFECYCLE §2c still binds it as authoritative for counts because the regen contract is documented. Recommend regen at next arc close cascade rather than retrofitting a V1 banner. NO action recommendation to modify inventory in-place (§2c protection).
- file_path: docs/PLATFORM_INVENTORY.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [15, 27]
      claim: "Executive Summary table: 83 agents, 80 spiders, 112 services, 415 celery tasks, 92+5=97 beat, 113+156 PA tools, 585 models, 96+48+25 discord, 9 body systems, 6 LLM providers"
      runtime_truth: "matches CLAUDE.md live autogen block (S2834 refresh)"
      cited_source: CLAUDE.md live-counts autogen block
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Live counts still match CLAUDE.md's autogen block. Runtime hasn't drifted meaningfully in 14 days on the audited totals.
```

#### `docs/KNOWLEDGE_PIPELINE.md`

```yaml
- file_path: docs/KNOWLEDGE_PIPELINE.md
  audit_thread: T1
  severity: P1
  finding_class: stale_vs_head
  evidence:
    - line_range: [3, 4]
      claim: "Built: Sessions 243-245 (learning), Session 400 (pipeline complete)"
      runtime_truth: "no drift — historical construction sessions are stable facts"
      cited_source: docs/handoffs/SESSION_243*
    - line_range: [25, 25]
      claim: "│                    SPIDER NETWORK (64 spiders)                  │"
      runtime_truth: "80 spiders across 41 categories per PLATFORM_INVENTORY + CLAUDE.md autogen block line 137"
      cited_source: docs/PLATFORM_INVENTORY.md
  recommended_action: update_in_place
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    KNOWLEDGE_PIPELINE is one of the 5 orient-anchors (per context-kit orient §SOURCE OF TRUTH). "64 spiders" in the pipeline diagram misleads on a runtime-anchored value in a runtime-flow doc — that is exactly the P1 shape (stale but non-misleading only because the count is diagrammatic; anyone hitting the pipeline flow reads the number). Rec: replace with "80 spiders" or auto-generate the count.
```

#### `docs/UDB_BEHAVIOR_LAYER.md`

```yaml
- file_path: docs/UDB_BEHAVIOR_LAYER.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [4, 8]
      claim: "status: active, last_updated: 2026-05-22, session: 1124"
      runtime_truth: "behavior contract is stable — voice/persona rules don't drift with runtime counts; 2 months since last review acceptable for behavior-layer scope"
      cited_source: docs/UDB_BEHAVIOR_LAYER.md content
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Behavior layer describes Rigby persona voice + constraint preservation. Not tied to runtime counts. Content stable.
```

#### `docs/UDB_TRANSLATION_LAYER.md`

```yaml
- file_path: docs/UDB_TRANSLATION_LAYER.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [4, 8]
      claim: "status: active, last_updated: 2026-05-22, session: 1124"
      runtime_truth: "translation contract is stable"
      cited_source: docs/UDB_TRANSLATION_LAYER.md content
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Same structural reason as UDB_BEHAVIOR_LAYER — translation persona contract, not runtime state.
```

### 2.2 Canon (2)

#### `docs/canon/INDEX.md`

```yaml
- file_path: docs/canon/INDEX.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 112]
      claim: "canon index"
      runtime_truth: "canon is deliberately small per parent §2 Existing constraints (docs/canon/INDEX.md)"
      cited_source: docs/canon/INDEX.md self-declaration
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Constitutional canon index. Small-by-design per parent §2 constraint row 4.
```

#### `docs/canon/creative/DAVINCI_RESOLVE_WORKFLOW.md`

```yaml
- file_path: docs/canon/creative/DAVINCI_RESOLVE_WORKFLOW.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 1]
      claim: "davinci resolve creative workflow canon"
      runtime_truth: "canon-scoped creative workflow doc; runtime-coupled per DOC_LIFECYCLE §2b (canon path is NEVER-MOVE)"
      cited_source: docs/00-START-HERE/DOC_LIFECYCLE.md §2b
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    NEVER-MOVE per DOC_LIFECYCLE §2b. Content is domain-specific creative workflow; NOT runtime-count-coupled.
```

### 2.3 Governance (1)

#### `docs/governance/SYSTEM_OWNER.md`

```yaml
- file_path: docs/governance/SYSTEM_OWNER.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 220]
      claim: "system owner governance doc"
      runtime_truth: "governance-scoped; NEVER-MOVE per DOC_LIFECYCLE §2b (docs/governance/)"
      cited_source: docs/00-START-HERE/DOC_LIFECYCLE.md §2b
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    NEVER-MOVE per DOC_LIFECYCLE §2b. Governance content stable.
```

### 2.4 Onboarding (3)

#### `docs/00-START-HERE/DOC_LIFECYCLE.md`

```yaml
- file_path: docs/00-START-HERE/DOC_LIFECYCLE.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 156]
      claim: "doc lifecycle contract"
      runtime_truth: "actively cited from CLAUDE.md, PLATFORM_WHAT_IT_IS, PLATFORM_INVENTORY, 2800 parent, this T1 doc — high inbound reference density"
      cited_source: multiple docs
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Load-bearing constitutional contract. Cited by every anchor doc. NEVER-MOVE per its own §3 (root-stability).
```

#### `docs/00-START-HERE/INDEX.md`

```yaml
- file_path: docs/00-START-HERE/INDEX.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 27]
      claim: "onboarding index"
      runtime_truth: "27-line index; small-surface onboarding pointer"
      cited_source: docs/00-START-HERE/INDEX.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Small index; content-stable.
```

#### `docs/00-START-HERE/README.md`

```yaml
- file_path: docs/00-START-HERE/README.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 53]
      claim: "onboarding readme"
      runtime_truth: "onboarding surface"
      cited_source: docs/00-START-HERE/README.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Small onboarding README; content-stable.
```

### 2.5 Root (3)

#### `CLAUDE.md`

```yaml
- file_path: CLAUDE.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [3, 3]
      claim: "**Last Updated:** July 19, 2026 (Session 2833 close — ...)"
      runtime_truth: "current session is 2834 open; header freshly refreshed at S2833 close cascade"
      cited_source: 00-START-NEXT-SESSION.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Header-refresh cadence is 1x per close-cascade PR. Fresh at S2834 open — actual state ok. (Removed prior "class-P0 status-ok" recording per Rigby cycle-1 Q3 DISAGREE: mixing class-severity with resolved-state in the histogram axis contaminates severity reporting. Rec now = record actual state, and separately propose §5 schema refinement for finding_state field.)
- file_path: CLAUDE.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [130, 156]
      claim: "Live counts autogen block: 83 agents / 80 spiders / 112 services / 415 celery / 92+5 beat / 113+156 PA / 585 models / 96+48+25 discord / 9 body / 6 LLM / 10 signal / 61 routes"
      runtime_truth: "autogen — matches PLATFORM_INVENTORY headline"
      cited_source: `refresh_doc_inventory_blocks`
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Autogen block. Self-refreshing.
- file_path: CLAUDE.md
  audit_thread: T1
  severity: P1
  finding_class: stale_vs_head
  evidence:
    - line_range: [160, 173]
      claim: "**Agents (AGENT_MAP)** _see autoblock above_; **Advisors** 30 functional domain specialists; **Employees (Employee OS)** 3 — Documentation Manager, Platform Auditor, Chief of Staff"
      runtime_truth: "advisors=30 matches PLATFORM_INVENTORY §Advisors headline; Employee OS employee count 3 not currently in PLATFORM_INVENTORY autogen — cannot mechanically verify without runtime check"
      cited_source: docs/ADVISOR_AUDIT.md + core/employees/jobs.py
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Employee OS count (3) is stated as a fact in CLAUDE.md's headline table without an autogen guard. If Employee OS is extended without CLAUDE.md refresh, count drifts silently. Escalate: should Employee OS employee count be added to the `refresh_doc_inventory_blocks` autogen set? (Post-arc engineering item, not this arc's fix.)
- file_path: CLAUDE.md
  audit_thread: T1
  severity: P2
  finding_class: broken_ref
  evidence:
    - line_range: [176, 177]
      claim: "core/agents/ — 83 AGENT_MAP agent classes with learning hooks; BaseAgent is 5,575 lines"
      runtime_truth: "BaseAgent line count not verified in this pass (would require file read + wc); 83 count matches autogen"
      cited_source: HEAD grep TBD
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    BaseAgent line count is a decorative fact. Line counts drift on every refactor; either autogen or drop. Flagged as ref-drift-risk, not verified as broken; recommend policy call rather than in-place edit.
- file_path: CLAUDE.md
  audit_thread: T1
  severity: P0
  finding_class: stale_vs_head
  evidence:
    - line_range: [262, 262]
      claim: "| [DISCORD_INTEGRATION.md](docs/DISCORD_INTEGRATION.md) | Discord bot: 144 commands across 25 Cogs |"
      runtime_truth: "actual count is 96 total commands (48 slash + 48 prefix) per DISCORD_INTEGRATION.md line 7 which explicitly notes the 144 count was a regex double-count corrected by AST parsing in Session 1115. CLAUDE.md autogen block on line 148 also shows 96 @*.command + 48 @app_commands.command. 96+48=144 is not commands+commands, it is total@decorators + slash-subset."
      cited_source: docs/DISCORD_INTEGRATION.md line 7 + CLAUDE.md live autogen line 148
  recommended_action: update_in_place
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    CLAUDE.md Reference Documentation table on line 262 cites DISCORD_INTEGRATION.md as "Discord bot: 144 commands across 25 Cogs" — but the linked doc itself (line 7) already corrected the 144 claim in S1115, calling it "a regex double-count corrected by AST parsing." Reader who trusts CLAUDE.md line 262 disagrees with the doc line 262 points to. P0 because it directly contradicts the linked doc AND the live autogen block on the SAME file (CLAUDE.md line 148). Fix: replace "144 commands across 25 Cogs" with "96 total commands (48 slash + 48 prefix) across 25 Cogs" or reference autogen values.
```

#### `00-START-NEXT-SESSION.md`

```yaml
- file_path: 00-START-NEXT-SESSION.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 234]
      claim: "S2833 close pointer with S2834 candidate menu"
      runtime_truth: "matches S2833 close ceremony; T1 audit recommended default reflected in candidate menu §B"
      cited_source: docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Refreshed at S2833 close. Actively used at S2834 open. Root-stability per DOC_LIFECYCLE §3.
```

#### `README.md`

```yaml
- file_path: README.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 244]
      claim: "root readme"
      runtime_truth: "unread by cascade governance; not in DOC_LIFECYCLE §2b or §3 protection lists; audit findings may include stats drift"
      cited_source: README.md content
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Root README is public-facing (github landing). If it cites counts, they must match PLATFORM_INVENTORY per §2c. Escalate: is root README maintained by the same refresh cadence, or is it a marketing/README-driven-development artifact? T1 flags for Chris directive; not blocking audit close.
```

### 2.6 CLAUDE.md Reference Documentation graph (13)

#### `docs/ARCHITECTURE.md`

```yaml
- file_path: docs/ARCHITECTURE.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 867]
      claim: "system architecture reference"
      runtime_truth: "867-line architecture doc; no per-file walk this pass; frontmatter freshness unverified at this pass"
      cited_source: TBD
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Architecture doc is large; T1 pass identifies as candidate for a claim-density walk in the schema-validation review. Recommend Rigby SIGN pressure-test whether T1 should walk every large ref doc's claims or whether large refs get a spot-check protocol. This is exactly the schema-validation feedback loop parent §10.1 anticipated (fold_class future_trigger).
```

#### `docs/AGENTS.md`

```yaml
- file_path: docs/AGENTS.md
  audit_thread: T1
  severity: P1
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 1685]
      claim: "agent documentation (stats may drift — see PLATFORM_INVENTORY per §2c per CLAUDE.md line 256)"
      runtime_truth: "CLAUDE.md self-flags AGENTS.md as drift-known"
      cited_source: CLAUDE.md line 256
  recommended_action: retrofit_v1_pointer
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    CLAUDE.md line 256 explicitly disclaims "stats may drift — see PLATFORM_INVENTORY for counts." Content itself may be accurate on agent architecture; count drift is anticipated. Rec: retrofit DOC-POINTER-V1 stats-drift banner AT AGENTS.md top so readers who reach this doc directly (not through CLAUDE.md) get the same disclaimer.
```

#### `docs/SPIDERS.md`

```yaml
- file_path: docs/SPIDERS.md
  audit_thread: T1
  severity: P1
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 646]
      claim: "spider network (stats may drift — see PLATFORM_INVENTORY per CLAUDE.md line 257)"
      runtime_truth: "same shape as AGENTS.md — CLAUDE.md self-flags SPIDERS.md as drift-known"
      cited_source: CLAUDE.md line 257
  recommended_action: retrofit_v1_pointer
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Same pattern as AGENTS.md. Retrofit V1 stats-drift banner.
```

#### `docs/SERVICES.md`

```yaml
- file_path: docs/SERVICES.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 834]
      claim: "services layer reference"
      runtime_truth: "not self-flagged as drift-known in CLAUDE.md line 258"
      cited_source: CLAUDE.md line 258
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Escalate: should SERVICES.md carry same V1 stats-drift disclaimer as AGENTS/SPIDERS? PLATFORM_INVENTORY shows "112 Service classes across 362 files" — if SERVICES.md cites a specific service count, verify vs 112. Recommend claim-density walk in schema-validation review.
```

#### `docs/DATABASE_MODEL_REFERENCE.md`

```yaml
- file_path: docs/DATABASE_MODEL_REFERENCE.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 636]
      claim: "which DB table for what"
      runtime_truth: "585 concrete models across 23 apps per PLATFORM_INVENTORY; DATABASE_MODEL_REFERENCE.md count-freshness unverified this pass"
      cited_source: PLATFORM_INVENTORY §Database Models
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Reference doc for DB models. Same class as SERVICES.md — recommend claim-density walk.
```

#### `docs/API_PATH_POLICY.md`

```yaml
- file_path: docs/API_PATH_POLICY.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 220]
      claim: "api path conventions"
      runtime_truth: "policy doc (rule-based); not runtime-count-coupled"
      cited_source: docs/API_PATH_POLICY.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Path-policy is a rule doc; drift would be a rule change, not a count. Content-stable class.
```

#### `docs/DREAM_INITIATIVE_WORKFLOW.md`

```yaml
- file_path: docs/DREAM_INITIATIVE_WORKFLOW.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 1068]
      claim: "initiative 5-stage pipeline"
      runtime_truth: "1068-line workflow doc; refers to models + tasks that may drift with core/tasks.py + models updates"
      cited_source: TBD
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Workflow-shape doc with high probability of concrete code-path citations. Recommend claim-density walk in schema-validation review.
```

#### `docs/DISCORD_INTEGRATION.md`

```yaml
- file_path: docs/DISCORD_INTEGRATION.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [7, 7]
      claim: "**Commands:** **96 total** (48 @app_commands.command slash + 48 @*.command prefix) across 25 Cogs. Earlier '144 total' claim was a regex double-count corrected by AST parsing in Session 1115"
      runtime_truth: "matches CLAUDE.md autogen block line 148 (96 @*.command + 48 @app_commands.command + 25 Cog classes). Note: @*.command grep count of 96 INCLUDES the 48 @app_commands.command as a subset — corrected total is 96, not 144."
      cited_source: CLAUDE.md live autogen block line 148
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    DISCORD_INTEGRATION.md IS correct — it already documents the S1115 correction and cites DISCORD_AUDIT.md as authoritative. The P0 defect from initial reading was NOT in DISCORD_INTEGRATION.md — it was in CLAUDE.md line 262 which still cites the corrected-away "144 commands" value. See CLAUDE.md finding above (§2.5). Recording this file as OK — it self-documents the correction.
- file_path: docs/DISCORD_INTEGRATION.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [321, 321]
      claim: "3. **Discord limit:** Max 100 global slash commands. Currently at 112 -- some may need to be guild-specific."
      runtime_truth: "current slash-command count is 48 per @app_commands.command decorators (CLAUDE.md autogen line 148); the '112 slash commands' claim is stale relative to current live count"
      cited_source: CLAUDE.md live autogen block line 148
  recommended_action: update_in_place
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    DISCORD_INTEGRATION.md line 321 claims "Currently at 112" slash commands, but live count is 48 @app_commands.command decorators. If 112 was the count when the guideline was written, the count has since been trimmed under Discord's 100-slash-command global limit. Either update to reflect current 48 or convert to a guardrail ("if you exceed 100 globals, mark some as guild-specific").
```

#### `docs/demo_mode.md`

```yaml
- file_path: docs/demo_mode.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 161]
      claim: "resolve demo mode guardrails, demo clip generation"
      runtime_truth: "policy/mode doc"
      cited_source: docs/demo_mode.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Small; policy-scoped.
```

#### `docs/governance_redesign.md`

```yaml
- file_path: docs/governance_redesign.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 363]
      claim: "governance UX redesign spec, 7 implementation tickets"
      runtime_truth: "spec-doc; whether the 7 tickets are still open unverified this pass"
      cited_source: TBD
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Spec doc with ticket references. If any of the 7 tickets closed and doc doesn't reflect, that's drift. Recommend Chris directive on whether to keep as spec-snapshot (retrofit V2 pointer) or track ticket completion.
```

#### `docs/EMPLOYEE_OS_PRIMITIVES.md`

```yaml
- file_path: docs/EMPLOYEE_OS_PRIMITIVES.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 296]
      claim: "canonical Employee OS primitives + anti-duplication matrix + lifecycle + warnings + quick-start"
      runtime_truth: "self-declared canonical per CLAUDE.md line 265; policy-shaped doc"
      cited_source: CLAUDE.md line 265
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Canonical primitives doc. If drifts, would trigger duplicate Employee OS surface (which is what anti-duplication matrix prevents).
```

#### `docs/ADVISOR_AUDIT.md`

```yaml
- file_path: docs/ADVISOR_AUDIT.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 643]
      claim: "advisor audit — cited from CLAUDE.md line 169"
      runtime_truth: "advisor count 30 in CLAUDE.md matches inventory; ADVISOR_AUDIT itself 643 lines with domain-specialist inventory that may drift"
      cited_source: CLAUDE.md line 169
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Recommend claim-density walk of specialist-count claims + name changes. Not a count-anchor for CLAUDE.md's live block, but supports the advisor row.
```

#### `docs/DISCORD_AUDIT.md`

```yaml
- file_path: docs/DISCORD_AUDIT.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 323]
      claim: "discord audit — cited from CLAUDE.md line 172"
      runtime_truth: "discord counts 96+48+25 in CLAUDE.md verified above (see DISCORD_INTEGRATION.md finding)"
      cited_source: CLAUDE.md live autogen block
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Audit doc; likely stale relative to live counts. Recommend claim-density walk in schema-validation review.
```

### 2.6a Topics canary (2 — Rigby cycle-1 Q1 STRENGTHEN)

#### `docs/topics/personal-assistant.md`

```yaml
- file_path: docs/topics/personal-assistant.md
  audit_thread: T1
  severity: P1
  finding_class: stale_vs_head
  evidence:
    - line_range: [6, 6]
      claim: "**Current runtime counts (PLATFORM_INVENTORY 2026-05-25): 104 tool schemas + 169 registered handlers; 8 enrichment services.**"
      runtime_truth: "113 tool schemas + 156 registered handlers per PLATFORM_INVENTORY headline + CLAUDE.md live autogen block line 145"
      cited_source: CLAUDE.md live autogen block line 145
    - line_range: [12, 13]
      claim: "core/services/tool_dispatcher.py — **152 tool handlers**  ...  core/services/pa_tool_schemas.py — **104 [tool schemas]**"
      runtime_truth: "152 handlers is stale — inventory + autogen show 156. 104 schemas is stale — inventory + autogen show 113."
      cited_source: docs/PLATFORM_INVENTORY.md §PA Tools + CLAUDE.md live autogen block line 145
  recommended_action: retrofit_v1_pointer
  action_target: null
  migration_pr_batch_hint: topic_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    DOC-POINTER-V1 banner IS present at line 1 (self-flags stats-may-drift). But the concrete numbers embedded in the prose are still cited authoritatively ("Current runtime counts") — banner works for readers who see it; readers who pattern-match the bold "**Current runtime counts**" phrase read the drift as fact. Rec: either update the specific "**Current runtime counts**" line inline or reinforce the V1 banner phrasing to steer readers past bold-count claims. Canary confirms Rigby Q1: topics need T1 pressure on load-bearing count claims.
```

#### `docs/topics/agent-system.md`

```yaml
- file_path: docs/topics/agent-system.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [6, 6]
      claim: "83 agents in AGENT_MAP"
      runtime_truth: "matches PLATFORM_INVENTORY + CLAUDE.md live autogen block line 137"
      cited_source: CLAUDE.md live autogen block line 137
    - line_range: [6, 6]
      claim: "Session 1029: Agent health audit — 35 thriving, 6 bounded, 3 waste paths closed"
      runtime_truth: "historical S1029 snapshot; stable historical fact"
      cited_source: docs/handoffs/SESSION_1029*
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: topic_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Anchor count (83 agents) matches inventory. Historical snapshots (S1029 health audit) are stable. V1 stats-drift banner present. Canary confirms this topic is NOT drifting on its load-bearing count. Contrasts with personal-assistant.md finding — validates the Rigby-Q1 concern that some topics carry live drift while others don't; T3a/T3b can't distinguish since they classify by structure (dup / orphan) not by claim correctness.
```

### 2.7 Research OS anchors (4)

#### `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`

```yaml
- file_path: docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 3814]
      claim: "3814-line research operating system contract"
      runtime_truth: "actively used at every session open per CLAUDE.md §Research Library"
      cited_source: CLAUDE.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Large; actively-used; content-authored constitutional doc. Any drift on specific rule numbers would be an in-doc revision, not runtime-count drift. Recommend claim-density walk if Chris directs.
```

#### `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`

```yaml
- file_path: docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 2037]
      claim: "domain research playbook v2"
      runtime_truth: "actively used for research group startup per CLAUDE.md"
      cited_source: CLAUDE.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Similar shape to RESEARCH_OPERATING_SYSTEM.md.
```

#### `docs/research/ARCHITECTURE_INDEX.md`

```yaml
- file_path: docs/research/ARCHITECTURE_INDEX.md
  audit_thread: T1
  severity: P2
  finding_class: stale_vs_head
  evidence:
    - line_range: [1, 4885]
      claim: "architecture index v12"
      runtime_truth: "4885 lines; likely to have arc-registration drift given Group 2800 opened at S2833"
      cited_source: TBD
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    S2833 handoff mentions ARCHITECTURE_INDEX arc registration is a deferred §7 anchor update. Group 2800 addition status unverified this pass. Confirm on schema-validation review whether that lag applies.
```

#### `docs/research/OPEN_ARCS.md`

```yaml
- file_path: docs/research/OPEN_ARCS.md
  audit_thread: T1
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 237]
      claim: "open arcs manifest — Group 2800 registered In-progress per S2833 close"
      runtime_truth: "S2833 handoff confirms Group 2800 added to In-progress section"
      cited_source: docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Machine-readable arc manifest. Actively updated per session close cascade.
```

---

## 3. Severity histogram

Aggregated over 33 files (31 original + 2 topics canary; some files emit
multiple rows; histogram counts **active** findings per Rigby cycle-1 Q3
DISAGREE — resolved/class-shape recordings dropped):

| Severity | Count (active only) | Notes |
|---:|---:|---|
| P0 | 1 | **CLAUDE.md line 262 "Discord bot: 144 commands"** — VERIFIED DRIFT, contradicts the linked doc's own S1115 correction and CLAUDE.md's own live autogen block |
| P1 | 4 | KNOWLEDGE_PIPELINE.md "64 spiders" → 80 (line 25); CLAUDE.md L1-graph Employee OS count autogen gap; AGENTS.md / SPIDERS.md drift-known-per-CLAUDE.md (retrofit V1 banner); topics/personal-assistant.md line 6+12+13 stale counts (104 schemas → 113; 152/169 handlers → 156) |
| P2 | 9 | PLATFORM_WHAT_IT_IS refresh cadence banner candidate; PLATFORM_INVENTORY regen cadence; README.md maintenance; DISCORD_INTEGRATION line 321 "112 slash commands"; ARCHITECTURE.md / SERVICES.md / DATABASE_MODEL_REFERENCE.md / DREAM_INITIATIVE_WORKFLOW.md / governance_redesign.md / ADVISOR_AUDIT.md / DISCORD_AUDIT.md / ARCHITECTURE_INDEX.md — coverage=structural_only, migration-queue re-audit contract per §5.5 |
| P3 (ok / info) | 22+ | rest of corpus incl. topics/agent-system.md canary confirming NOT all topics drift equally |

**Coverage flag distribution (Rigby cycle-1 Q5 STRENGTHEN — new schema field per §5.5):**

- `full_claim_walk`: 15 files (anchors + canon + governance + onboarding + root + Research OS OPEN_ARCS + KNOWLEDGE_PIPELINE + DISCORD_INTEGRATION + topics canary)
- `structural_only`: 10 files (large refs + AGENTS/SPIDERS drift-known + ADVISOR_AUDIT + DISCORD_AUDIT + governance_redesign + ARCHITECTURE_INDEX)
- `deferred`: 8 files (research OS anchors > 2000 lines + PLATFORM_INVENTORY body scan not performed this pass)

---

## 4. Migration queue (post-arc)

Per parent §5 (arc classifies; execution defers). Batched by `migration_pr_batch_hint`:

### 4.1 Batch `anchor_docs` — banner + freshness sweep

- **Retrofit V1 stats-drift banner** (~1-line at file top) on:
  - `docs/AGENTS.md` (P1 — CLAUDE.md self-flags)
  - `docs/SPIDERS.md` (P1 — CLAUDE.md self-flags)
  - `docs/PLATFORM_WHAT_IT_IS.md` (P2 — refresh cadence signal)
- **Update in-place** on:
  - `CLAUDE.md` line 262: "Discord bot: 144 commands across 25 Cogs" → "Discord bot: 96 total commands (48 slash + 48 prefix) across 25 Cogs" or reference autogen values. **This is the P0 verified drift** — CLAUDE.md contradicts the doc it links.
  - `docs/KNOWLEDGE_PIPELINE.md` line 25: "SPIDER NETWORK (64 spiders)" → "SPIDER NETWORK (80 spiders)" or autogen substitution (P1).
  - `docs/DISCORD_INTEGRATION.md` line 321: "Currently at 112" slash commands → current 48, or convert to guardrail-only phrasing (P2).

### 4.1a Batch `topic_docs` — T3a pre-scan hint (Rigby cycle-2 Q8 STRENGTHEN)

- **T3a discovery hint (recorded, not executed by T1)**: topics/ heterogeneity
  (topics/personal-assistant.md has stale counts; topics/agent-system.md
  does not) signals T3a needs a lightweight count-claim-density pre-scan
  BEFORE dup detection. Grep pattern candidates (T3a author's judgment):
  - `\*\*Current runtime counts` bold-phrase pattern
  - `\b\d+\b\s+(agents|tools|handlers|spiders|services|models)`
  Purpose: TAG topics as `count_dense` vs `narrative`; dup/orphan
  triage prioritizes count_dense candidates. Not a claim-walk; a tagging
  pass. Deferred to T3a; recorded here so T3a author knows this feedback exists.

### 4.2 Batch `schema_validation` — feedback into parent §10 schema

- **Escalate to Chris**: does T1 need a `claim_density_walk` sub-pass for
  large (>500-line) reference docs? Current pass classifies these as
  P2 "schema-validation deferred" — that's a signal, not a full audit.
  Options: (a) accept classification-only for large refs (T1 scope stays
  small); (b) run claim-density walks now (T1 becomes 2-session).
- **Escalate to Chris**: schema §10.1 field `line_range` is emitted
  per-finding not per-doc — some findings span the whole doc; convention
  used here is `[1, <total_lines>]` for whole-doc findings. Ratify
  or refine.
- **Escalate to Chris**: whether autogen-block claims (self-refreshing)
  need a distinct `finding_class` value (e.g. `autogen_ok`) vs
  `finding_class: ok`. Current pass folds under `ok` with notes; schema
  extension proposal, not this arc's fix.

### 4.3 Batch `anchor_docs` — Chris directives requested

Per §2.5 CLAUDE.md L1 finding, §2.5 README.md, §2.6 SERVICES / DATABASE_MODEL /
DREAM_INITIATIVE / ADVISOR_AUDIT / DISCORD_AUDIT / governance_redesign:

- **Chris directive requested**: refresh cadence policy for anchor docs
  vs reference-graph docs.
- **Chris directive requested**: whether root README.md is in-scope for
  the same refresh cadence as anchor docs.
- **Chris directive requested**: whether Employee OS count should be added
  to `refresh_doc_inventory_blocks` autogen set.

---

## 5. Cross-cutting signals for parent §10 schema (Rigby cycle-1 refinement realized at first-child schema validation)

The parent Rigby cycle-3 `future_trigger` fold anticipated exactly this
feedback loop. Rigby cycle-1 Q2/Q3/Q5 verdicts (STRENGTHEN / DISAGREE /
STRENGTHEN respectively) refined the initial proposals — final shape below,
backward-compatible with existing §10.1 rows (all new fields optional /
default-preserving).

Proposed §10.1 schema v1.1 (Chris D-verdict slot).

**Schema versioning (Rigby cycle-2 Q6 AGREE with caveat):** Under permissive
YAML parsing, all §10.1 v1.0 consumers ignore unknown keys and the refined
rows are backward-compatible. Under STRICT schema validation (unknown-key
rejection) the new fields would break v1.0 consumers. Fix: declare
`schema_version: 1.1` at file-header level and require v1.0 consumers
opt-in to v1.1. T1 findings emit under v1.1; downstream tooling checks
schema_version before parsing.

Refinements:

1. **New field `claim_source: manual | autogen`** — replaces the initial
   `finding_class: autogen_ok` proposal. Rigby Q2 STRENGTHEN: extending the
   locked `finding_class` enum is risky for downstream tooling that expects
   a stable set; modeling as a distinct attribute keeps `finding_class`
   stable while letting migration-queue scans filter out autogen-governed
   rows. Default `manual`.
2. **Convention: `line_range: [1, <total>]` for whole-doc findings** —
   Rigby Q2 STRENGTHEN: clean convention, no extra flag needed. Codify
   in schema commentary.
3. **New field `claim_density_hint: dense | sparse | large_ref_deferred`**
   — Rigby Q2 STRENGTHEN. Lets T1 flag "large ref, only spot-checked"
   without escalating every large-ref P2 to Chris. Default absent (implies
   `dense` claim-walk was performed).
4. **New field `finding_state: active | resolved`** (Rigby cycle-1 Q3
   **DISAGREE** with initial "class-P0 status-ok" recording pattern) —
   Rigby's rationale: recording "was P0, now ok" as P0 pollutes the severity
   histogram and creates false "P0 blocks migration" implications. Fix:
   record actual state accurately in `severity` + `finding_class`, use
   `finding_state` to represent "was drift, verified resolved." Histograms /
   gates count only `finding_state: active`. Default `active`.
5. **New field `coverage: full_claim_walk | structural_only | deferred`**
   (Rigby cycle-1 Q5 STRENGTHEN + Rigby cycle-2 Q9 STRENGTHEN) —
   contract-level, not free-text notes. Cross-arc consumers (Group 2700
   §3 migration arc) must distinguish:
   - `full_claim_walk` — every concrete claim in file verified vs HEAD
   - `structural_only` — frontmatter, DOC-POINTER banners, load-bearing
     count claims verified; body-level claim-density-walk not performed
   - `deferred` — audited only for scope classification (path, size, drift
     signal); no claim verification performed

   **§10.4 migration-arc waiver protocol (Rigby cycle-2 Q9 STRENGTHEN):**
   Not every file needs `full_claim_walk` at migration time (too strict
   for rule/policy-shaped docs). But any file being MOVED / SUPERSEDED
   by the §3 migration arc MUST carry either:
   - (a) `coverage: full_claim_walk`, OR
   - (b) `coverage: structural_only` PLUS
         `recommended_action: escalate_to_chris` PLUS
         explicit `notes:` rationale for why full walk was skipped.
   In-place-only files (rule / policy / NEVER-MOVE) can carry
   `coverage: structural_only` without the waiver — because they aren't
   migration-touch-point candidates. Default `full_claim_walk`.

**§10.4 root-stability P0 clarification (Rigby cycle-2 Q7 STRENGTHEN):**
Parent §10.4 says P0 findings "block the destination subdir migration
until fixed." That rule assumes the file is migration-eligible. For
DOC_LIFECYCLE §3 root-stability files (CLAUDE.md, 00-START-NEXT-SESSION.md,
`*_AUDIT.md`), the doc CANNOT MOVE by contract — it either stays at the
cited path or leaves a permanent stub. So P0 findings on root-stable
files block **in-place remediation only**, not "destination subdir
migration" (there is no destination migration to gate). Recommend §10.4
amendment: `P0 blocks: (a) destination-subdir migration for migration-eligible files, (b) in-place remediation
before arc close for root-stable / NEVER-MOVE files.`

If Chris ratifies §10.1 → v1.1 with schema_version tag: minor revision,
backward-compatible under permissive parsing; strict-parser consumers
opt-in via schema_version check. T2-T5 inherit v1.1 shape and MUST
populate `coverage` explicitly.

If Chris does not ratify: T1 proceeds under current §10.1 v1.0 and
downgrades §2.6 large-ref findings to actual state (either walk them
all, becoming 2-3 sessions, or drop them from T1 corpus).

---

## 6. Rigby SIGN cycles

### 6.1 Cycle 1 verdicts (recorded 2026-07-19, pin `pa-5fa195547db04260`)

Rigby tool_runs verified non-empty across cycle-1 dispatch (6 substantive
`repo_tool.read` calls: parent scoping doc, T1 draft, `docs/topics/personal-assistant.md`,
`docs/topics/agent-system.md`, `docs/ARCHITECTURE.md`, parent §10 schema
re-read). Anti-rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign` — passes.

| Q | Verdict | Refinement folded into T1 doc |
|---|---|---|
| Q1 corpus completeness | **STRENGTHEN** | Added 2 topics files as T1 canary (§2.6a); remaining 9 topics still route to T3a/T3b. Rationale: topics carry anchor-shaped count claims (verified — PA topic has stale 104/152/169 counts) that reachability/dup scans won't catch. |
| Q2 schema refinements | **STRENGTHEN** | Rewrote §5: (a) split `autogen_ok` off `finding_class` enum into separate `claim_source: manual\|autogen` attr (keeps enum stable); (b) codified `[1, N]` whole-doc convention as-is; (c) `claim_density_hint` retained. |
| Q3 severity discipline | **DISAGREE** | Removed the two spurious "class-P0 status-ok" recordings (CLAUDE.md L1-header + DISCORD_INTEGRATION-verified-ok) — they were polluting the histogram. §5.4 adds new `finding_state: active\|resolved` field; histograms count only `active`. |
| Q4 T1 exit gates | **AGREE** | T1 exit criteria stand (§7). Large refs classified `coverage: structural_only` with re-audit contract to migration arc (§5.5). |
| Q5 zoom-out — hidden failure mode | **STRENGTHEN** | Added §5.5 contract-level `coverage: full_claim_walk \| structural_only \| deferred` field; §3 histogram now reports coverage distribution alongside severity. Migration-arc consumers must NOT treat `structural_only` / `deferred` as audit-safe. |

### 6.2 Cycle 2 verdicts (recorded 2026-07-19, pin `pa-5fa195547db04260`)

Rigby tool_runs verified non-empty across cycle-2 dispatch (5 substantive
`repo_tool.read` calls: T1 doc method+§2.5+§2.6a+§2.6, DOC_LIFECYCLE.md §3
root-stability). Anti-rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign` — passes.

| Q | Verdict | Refinement folded into T1 doc |
|---|---|---|
| Q6 schema stability | **AGREE** (with caveat) | Added `schema_version: 1.1` header requirement to §5. Under permissive parsing rows are backward-compatible; strict-parser consumers opt-in via schema_version check. |
| Q7 P0 discipline | **STRENGTHEN** | Added §10.4 root-stability P0 clarification: P0 blocks (a) destination-subdir migration for migration-eligible files, (b) in-place remediation before arc close for root-stable / NEVER-MOVE files. Contract now covers both cases. |
| Q8 topics generalizability | **STRENGTHEN** | Added §4.1a T3a pre-scan hint — grep-tag topics as `count_dense` vs `narrative` before dup/orphan triage. Recorded, deferred to T3a author. |
| Q9 coverage-contract explicitness | **STRENGTHEN** | Added §5.5 migration-arc waiver protocol: file being MOVED/SUPERSEDED needs full_claim_walk OR structural_only+escalate_to_chris+rationale. In-place-only files exempt. Tight where it matters. |
| Q10 ZOOM-OUT #2 — anti-worship | **AGREE (lock v1.1 now)** | Not gold-plating. Canary caught actual drift (PA topic); CLAUDE.md P0 needs stable blocking semantics. Ship as-is with schema_version 1.1 at T1 close; further refinements → future_trigger fold at 2899 close. |

### 6.3 Cycle 3 pressure-test (proposed for this dispatch)

- **Q6 (schema stability under cycle-1 fold):** With cycle-1 refinements
  applied, do §5.1-5.5 five refinements remain backward-compatible with
  the parent-locked §10.1 shape? Concrete pressure-test: read the topics
  canary rows in §2.6a — does adding `claim_source`, `finding_state`,
  `coverage` to their emitted YAML break any consumer that treats §10.1
  as a strict schema? (Anti-rubber-stamp: `repo_tool.read` §2.6a rows.)
- **Q7 (P0 discipline):** After removing the two spurious class-P0
  recordings, T1 has exactly one active P0 (CLAUDE.md line 262). Does
  the migration queue §4 correctly gate the destination subdir migration
  on P0 fix, per parent §10.4 contract? Or does this need a §10.4
  amendment on what "P0 blocks destination subdir migration" means when
  the P0 lives in a root-stability file (CLAUDE.md is NEVER-MOVE)?
- **Q8 (topics canary generalizability):** topics/personal-assistant.md has
  concrete count drift; topics/agent-system.md doesn't. Does this signal
  T3a needs a count-claim-density pre-scan pass before dup detection?
  Or is the T3a/T3b shape already sufficient?
- **Q9 (coverage-flag contract):** `coverage: structural_only` on 10 files
  says "re-audit before migration" is implicit. Should the parent §10
  execution-contract §10.4 make this EXPLICIT ("migration PR must attach
  a `full_claim_walk` finding row for every source-path file before the
  PR opens")? Or is implicit enough?
- **Q10 (ZOOM-OUT #2):** Anti-worship pressure — is T1 doing too much
  schema-refinement work as a byproduct of doing an audit? The parent
  §10 was ratified 6 hours ago at S2833. Am I gold-plating the schema
  when the actual finding is "the schema mostly works, but three P0/P1
  drifts in prose"? Push back: should T1 SHIP as-is (with §5 schema
  refinements deferred to the future_trigger fold at parent-arc close
  2899), or should we lock the v1.1 schema at T1 close?

### 6.3 Cycle 3 verdicts (recorded 2026-07-19, pin `pa-5fa195547db04260`)

Rigby tool_runs verified non-empty across cycle-3 dispatch (5 substantive
`repo_tool` calls: T1 doc frontmatter+§2.6a+§5+§4.2+§10.4, `repo_tool.search`
for schema_version, DOC_LIFECYCLE §3 100-156). Anti-rubber-stamp passes.

| Q | Verdict | Refinement folded into T1 doc |
|---|---|---|
| Q11 schema_version placement | **STRENGTHEN** | Added `schema_version: 1.1` to frontmatter (single source of truth). No per-row tag needed — findings inherit from parent doc context. |
| Q12 root-stability wording verification | **AGREE** | Wording confirmed against DOC_LIFECYCLE §3 lines 113-126. No change needed. |
| Q13 Chris D-verdict readiness | **AGREE** | All refinements safely folded. Rigby's suggested Chris D-verdict framing: *"ratify T1 as-is + schema v1.1 (frontmatter version tag; coverage/state fields optional with defaults; histogram counts active only)"* — no additional conditional branches needed. |

### 6.4 Joint Claude+Rigby SIGN status

- **3 cycles complete**, tool_runs non-empty across all 3 (anti-rubber-stamp
  passes per `feedback_verify_rigby_tool_runs_before_trusting_sign`).
- **Convergence** — cycle 3 all AGREE/STRENGTHEN with no DISAGREE. Refinements
  fully folded.
- **Joint recommendation to Chris**: ratify T1 as-is + schema v1.1
  (frontmatter version tag; `claim_source` / `finding_state` / `coverage` /
  `claim_density_hint` fields optional with defaults; histogram counts
  `finding_state: active` only; migration-arc waiver protocol per §5.5;
  root-stability P0 clarification per §10.4).

Cycle 3 verifies cycle-2 refinements landed as intended. Three focused Q's:

- **Q11 (schema_version tag placement):** §5 preamble now declares
  `schema_version: 1.1`. Should the tag live at (a) FILE header (frontmatter),
  (b) per-YAML-block header line, or (c) both? Ripgrep-tool grounding
  suggested: `repo_tool.read` §2.6a canary rows and confirm the emitted
  YAML doesn't include a per-row schema_version tag today.
- **Q12 (§10.4 root-stability wording verification):** Does the §5.5
  wording ("P0 blocks: (a) destination-subdir migration for migration-eligible
  files, (b) in-place remediation before arc close for root-stable / NEVER-MOVE
  files") correctly map to the DOC_LIFECYCLE §3 root-stability rule you
  read at cycle 2? Verify by re-reading DOC_LIFECYCLE §3 lines 113-126
  (per your cycle-2 tool_run reference).
- **Q13 (T1 → Chris D-verdict readiness):** Are all cycle-1 + cycle-2
  refinements safely folded such that Chris can D-verdict with a single
  "ratify T1 as-is + schema v1.1" or "STRENGTHEN / DISAGREE X"? Or is
  there a hidden dependency I've missed? Push back if the joint
  Claude+Rigby agreement isn't tight enough for a Chris yes/no.

---

## 7. Exit criteria (T1 done when)

- ✅ 33 files classified per §10.1 v1.1 (31 corpus + 2 topics canary added
  at cycle 1)
- ✅ Rigby joint SIGN 3 cycles with substantive `tool_runs` (16 total across
  all cycles; anti-rubber-stamp passes)
- ✅ Joint Claude+Rigby agreement per `feedback_claude_rigby_agree_first_chris_yes_no`
- ⏳ **Chris D-verdict slot** — ratify T1 as-is + schema v1.1, or
  STRENGTHEN/DISAGREE per Q refinements
- ⏳ Migration queue frozen (post-D-verdict — routed to future §3
  execution arc that opens after 2899 closes)
- ⏳ Twin-pointer workspace deliverable created per
  `feedback_twin_deliverable_at_every_ratification`

---

## 8. Cross-links

- Parent: `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`
- Sibling structural arc: `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`
- Group 2700 §3 target tree (RATIFIED): `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` §3.1
- S2833 ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-19_2800_docs_content_audit_parent.md`
- DOC lifecycle: `docs/00-START-HERE/DOC_LIFECYCLE.md`
- Live counts: `docs/PLATFORM_INVENTORY.md` (regenerable)
- Playbook v0.8.0: `docs/ENGINEERING_PLAYBOOK.md`

---

## 9. Provenance

- **Session:** 2834
- **Author:** Claude Code
- **Pin:** `pa-5fa195547db04260` (label `s2834-t1-anchor-content-audit`)
- **HEAD at author time:** `34f701c66605`
- **Inventory used:** `docs/PLATFORM_INVENTORY.md` (generated `2026-07-05 15:51:41`, HEAD `e617af59`)
- **Live-count check:** CLAUDE.md autogen block (matches PLATFORM_INVENTORY on audited totals)
- **Anti-rubber-stamp discipline:** Rigby SIGN dispatch will verify `tool_runs`
  non-empty per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

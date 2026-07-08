# Platform Constitutional Transition Review

**Session:** 2727
**Date:** 2026-07-08
**Role executed:** Constitutional Reviewer (NOT author, NOT ratifier)
**Repository HEAD at review:** `309f85eee4dae5cedb022a393d06a19882ccf62f` (main, unchanged since SESSION 2707 close-merge)
**Rigby SIGN pin active at v0.1 verification history:** `pa-275e12fb72de4b3e` (Session 2725)

**Mission:** Determine whether the platform is constitutionally ready to transition from the Architecture Research phase into the Engineering Playbook era. Do NOT ratify. Do NOT modify Playbook, Canon, workspace, ADRs, or ratification records. Challenge the assumption that ratification is the right next step.

**Sources reviewed (no new research performed):**
- `playbook_v0_1_ratification_package.md` (Session 2726 — 14-step runbook, Options A-E)
- `constitutional_ecosystem_inventory.md` (Session 2714 — 21-section pre-existing ecosystem inventory)
- `platform_constitutional_architecture.md` (Session 2711 — tiered ratification model, six-layer stack, canonical_authority discussion)
- `engineering_playbook_architecture_specification.md` (Session 2712 — §5.1 frontmatter, §7 semver, §14 ratification envelope, §16.9 stub authorization)
- `engineering_playbook_authoring_protocol.md` (Session 2713 — 10 statement classes, evidence admission matrix, §7.2 convergent-research)
- `playbook_constitutional_correction_session_2725.md` (Session 2725 — CD-47 resolution, CD-48 principle extraction)
- `playbook_final_constitutional_verification.md` (Session 2724 — CD-47 origin)
- `engineering_playbook_evidence_manifest.md` (Session 2715 — frozen manifest §2.1 freeze semantics, §2.3 chain enumeration)
- `docs/governance/SYSTEM_OWNER.md` (L0 authority declaration; runtime-load-bearing)
- `docs/canon/INDEX.md` (Canon Registry; runtime-load-bearing)
- `docs/00-START-HERE/DOC_LIFECYCLE.md` (canonical doc governance)
- `00-START-NEXT-SESSION.md` (Session 2726 close)
- CLAUDE.md, MEMORY.md (session-open contracts)

---

## Executive Verdict

**Status after Rigby SIGN (Session 2727 fresh pin `pa-e78b9f0a31294af4`): CORRECTION-PASS applied — post-correction status reflected in-line.**

This report was originally drafted claiming "READY TO TRANSITION" and "ZERO BLOCKERS." Rigby's independent adversarial SIGN across 6 batches produced 1 conditional blocker and 5 must-address findings. Per System Owner directive, every finding was accepted as valid; the review — not the Playbook — was the correction target. The Playbook body itself was verified to correctly assert only what its rules demonstrate (see §Rigby SIGN Findings Appendix at end of document); the review had overclaimed on Playbook runtime authority. This corrected version narrows every review-side claim to what is demonstrated.

**Post-correction verdict: READY TO TRANSITION conditional on the review's now-explicit narrowed scope.** Specifically:

- The Playbook v0.1 is repo-canonical + workspace-ratified but is **NOT** in the session-open runtime-injection list (PLAYBOOK-1.6.11 names only CLAUDE.md, SYSTEM_OWNER.md, canon/INDEX.md). The Playbook body is RAG-retrievable via the `content.Document` mirror; that is NOT the same as "guaranteed-in-context." Any future session-open injection of the Playbook body is a Cycle 2 hardening decision, not an automatic consequence of ratification.
- The Playbook v0.1 codifies "Chris West" as System Owner (PLAYBOOK-1.5.1) — v0.1 is therefore explicitly a **"single-owner, incumbent-named constitution."** Role/incumbent separation is a Cycle 3+ MAJOR-bump concern, named here as an intentional constraint rather than an incidental simplification.
- CD-48 non-blocking status is conditional on codification landing as v0.1.1 PATCH via the first amendment cycle — NOT permanently deferred. Package Option D (permanent waiver) is not compatible with this posture.
- The v0.1 manifest freeze semantic (§2.1) means **sources, not derived draft text.** The Session 2725 CD-47 corrections modified Playbook draft after the manifest was frozen; this is compatible with the freeze because the manifest froze admissible sources, not authoring products.
- Ratification is bounded in operational scope but **high-leverage in runtime-context surfaces** (docs cascade, Canon Registry mutation, CLAUDE.md anchor refresh, `content.Document` mirror row creation, embed step). Failure modes + reversal channel are enumerated in §8.

**Recommendation:** proceed with **Package Option A** (write `docs/ENGINEERING_PLAYBOOK.md` per §6 Step 1, gated by System Owner directive at each subsequent step) — under the narrowed-claim posture above. **NOT Option D** (permanent CD-48 waiver).

**Reversal channel** (explicit): un-ratification is reachable via (a) System Owner Absolute Override directive per SYSTEM_OWNER.md §1; (b) MAJOR supersession per 2712 §7.3; (c) errata amendment per 2712 §15.3. "Irreversible in intent" from the original draft was overclaiming.

---

## Section 1 — Architectural Completeness

**Question:** Do any architectural questions remain unanswered?

**Approach:** evaluate the architecture that already exists across the six-artifact chain (2708-2714 + evidence manifest 2715). Do not perform new research.

### 1.1 What the architecture answers

The six-layer stack (2711 §18) is complete for v0.1 scope:

| Layer | Documentary constitution | Executable constitution | Status |
|---|---|---|---|
| L1 Fleet | None | Fleet models present, dormant | Deferred to Cycle 4+ per 2711 §14.4 |
| L2 Platform | Canon Registry (5+8), repo ADRs (4), Research OS + IOS, CLAUDE.md, MEMORY.md, 952 handoffs, 21 topic docs, top-level docs, **+ Playbook** | 7 CI workflows, CockpitAutopilotPolicy, AgentControlEntry, Budget, PublishGate, canonical_authority, Beat, cascade rules, docs injection, migrations | Home substrate identified; Playbook lands here |
| L3 Tenant | None | Tenant, ComplianceRule/Check dormant | Deferred to Cycle 3+ per 2711 §12.2 |
| L4 User | None (preferences not constitutional) | User preferences | Non-constitutional |
| L5 Workspace | Cycle 0 + Cycle 1 + Cycle 1A ADRs; 8+ ratification records; MANIFEST_v20260707 | WorkspaceConfig, WorkspaceContext, autonomy gates | Ratification envelope for Playbook lands here |
| L6 Deliverable | Ratified deliverables | PublishGate transitions | Governed by L5 |

The Playbook is L2 documentary constitution, `repo_canonical` per KFI-2 B3 (`content/_canonical_authority_helpers.py:33-60`), ratified via a workspace-canonical ratification record. The two-authority pattern (repo body + workspace envelope) is architecturally decided and pressure-tested through six falsification attacks in 2711 §14.

### 1.2 What the architecture does not answer

The following are named as **explicitly deferred** and are NOT architectural gaps:

- **L1 fleet-scope constitutional artifacts** — deferred; fleet infrastructure dormant (2711 §4, ecosystem §10.1).
- **L3 tenant-scope constitutional artifacts** — deferred; tenant activation is Cycle 3 (2711 §6.4, ecosystem §10.2).
- **`tenant_canonical` / `fleet_canonical` enum expansion** — deferred with a defined expansion path (2711 §12.2).
- **Cycle 2 hardening** (`content_hash` population on all ratification records; ORM-signal immutability; CI validation of `deliverable_type`; automated Canon Registry update; runtime-load-bearing docs registry) — enumerated in 2712 §17 and ecosystem §14.1. Cycle 2 work, not v0.1 blocker.
- **Whether Research OS and IOS eventually get absorbed into Playbook chapters vs stay as peer OSes** — Cycle 3+ decision per ecosystem §14.4. Playbook v0.1 references them; does not absorb them.

The following are **provisionally accepted** and NOT blockers, **conditional on the boundary rule below**:

- **Unenumerated `docs/` subdirectories** (per ecosystem §16.9 self-critique — `docs/playbooks/`, `docs/agents/`, `docs/apis/`, `docs/audit/`, `docs/features/`, `docs/plans/`, etc.). Cycle 2 audit expected. Chapter 1 authoring in the ratified Playbook will carry a "Provisional inventory" acknowledgement per 2714 Amendment B.
- **DAVINCI_RESOLVE_WORKFLOW.md and other transitional artifacts** (ecosystem §12) — housekeeping, not blockers.

**Rigby SIGN F-A1 (accepted):** the acknowledgement is sufficient **only if paired** with (a) a concrete boundary rule and (b) an explicit RAG-ingest risk note. Otherwise the acknowledgement masks accidental canonical drift. Both are recorded here as v0.1 posture:

- **(a) Boundary rule for unlisted subdirectories:** any `docs/` subdirectory not enumerated in §2 of this review, in the Playbook Chapter 1 provisional-inventory list, or promoted individually to Canon Registry, is **non-authoritative for constitutional purposes until enumerated.** Content in such subdirectories may exist and may be referenced descriptively; it does not carry constitutional weight and cannot serve as evidence for a Playbook amendment.
- **(b) RAG-ingest risk note:** the docs cascade (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents --all-unembedded`) will still mirror content from unenumerated subdirectories into `content.Document` with `canonical_authority='derived'` (or `repo_canonical` for `docs/`-prefix files per KFI-2 B3). This means RAG retrieval may surface unenumerated content in Rigby's or agents' context windows at retrieval-time. That is a runtime risk (surface drift into agent context) even though the content is not documentary-canonical. Cycle 2 hardening candidate: explicit registry of runtime-load-bearing docs paired with a retrieval-tier scheme so unenumerated content surfaces are not treated as authoritative during agent decision-making.

Both (a) and (b) are recorded here rather than being carried in the Playbook body because they are review-level posture, not new Playbook rules. If the pattern proves out, a Playbook Chapter 4 (Documentation Cascade — currently STUB) MINOR amendment is the natural home for codification.

### 1.3 What surfaced as an open question but was resolved

- **Is a Playbook needed at all, given IOS + Research OS + DOC_LIFECYCLE + SYSTEM_OWNER + Canon Registry already exist?** Falsified in ecosystem §16.1 — Playbook integrates the informal ecosystem into a ratified, versioned codification; adds PIC-10 provenance discipline; adds semver-tracked rule change accounting. Answer: yes, still needed.
- **Should Playbook be inside the Canon Registry rather than beside it?** Ecosystem §16.2 — compatible. Playbook body lives at `docs/ENGINEERING_PLAYBOOK.md`; Canon Registry gets a pointer row. Not either/or.
- **Should Playbook Chapter 1 be SYSTEM_OWNER.md?** Ecosystem §16.4 — no. Chapter 1 cites SYSTEM_OWNER as the L0 anchor; does not restate it.
- **Should Playbook live under `docs/canon/`?** Ecosystem §16.6 — no. Canon Registry rule: "Canon docs live at their original paths (not under `/canon/`). These are pointers, not copies." Playbook stays at `docs/ENGINEERING_PLAYBOOK.md`; canon pointer added.
- **Is the six-layer model wrong given L2 has two sub-tiers (Canon vs peer OSes)?** Ecosystem §16.8 — no. Canon-vs-OS is *tier of constitutional weight*, not new scope. 10 statement classes carry weight; 6 layers carry scope.

### 1.4 Verdict — Section 1

**No architectural question remains unanswered that blocks v0.1 ratification.** Every open question is either:

- Explicitly scoped out (L1 fleet, L3 tenant, Cycle 2 hardening),
- Deliberately deferred to a later cycle with a documented path (enum expansion, Research OS absorption), or
- Provisional and acknowledged as such in the Playbook body (Chapter 1 "Provisional inventory" note, Amendment B).

The architecture is **complete enough** to ratify v0.1. It is not "complete" in a strong sense — no constitutional architecture ever is — but the incompleteness is named, bounded, and does not compromise v0.1 correctness.

---

## Section 2 — Constitutional Ecosystem Hierarchy

**Question:** For each existing constitutional artifact, what is its relationship to the Playbook?

**Approach:** classify each artifact along five axes — Governs / Governed by / Peer / Transitional / Historical.

### 2.1 Full ecosystem hierarchy

| Artifact | Layer | Relationship to Playbook | Rationale |
|---|---|---|---|
| **SYSTEM_OWNER.md** | L2, L0-authority declaration | **Governs** the Playbook | Chris's Absolute Override Level is the ratification act's authority root. Playbook cannot exist without it. |
| **Runtime docs injection** (`docs_context_builder.py:184,186`) | L2 executable | **Governs** the Playbook's operational reach | Determines what agents see at runtime. If Playbook is not injected here, it does not govern agents. |
| **`canonical_authority` derivation** (`_canonical_authority_helpers.py:33-60`) | L2 executable | **Governs** the Playbook's authority classification | KFI-2 B3 assigns `repo_canonical` to `docs/`-prefix files. Playbook lands as `repo_canonical` by mechanism, not by opinion. |
| **PublishGate + `content_tool.content_complete`** | L2 executable | **Governs** the Playbook's ratification envelope transition | The workspace ratification record transitions to `ratified` via PublishGate — Playbook envelope is subject to this mechanism. |
| **Cycle 0 ADRs (0000/0005/0010/0020)** | L5 hosted, semantically L2 | **Governs** the Playbook | Cycle 0 established RAR methodology + Research OS + platform bootstrap contract that the Playbook codifies further. |
| **Cycle 1 open/close (0100/0199)** | L5 workspace-canonical | **Governs** the Playbook | 0100 opened the cycle within which the Playbook is authored; 0199 named "Engineering Playbook architecture" as remaining Cycle 1 work. |
| **Cycle 1A ADRs (0110-0150)** | L5 workspace-canonical | **Governs** the Playbook | Established `canonical_authority` field (KFI-2), cascade automation, CLAUDE.md bootstrap pointer — the substrate the Playbook cites. |
| **DOC_LIFECYCLE.md** (`authority: canonical`) | L2 repo-canonical | **Peer**, extended by Playbook Chapter 4 | Governs `/docs/` corpus; Playbook Chapter 4 (Documentation Cascade) extends with the 4-step cascade + embed discipline (not duplicates). |
| **Research OS** (`RESEARCH_OPERATING_SYSTEM.md`) | L2 repo-canonical | **Governed-by for methodology / Peer for scope** | *Corrected per Rigby F-A2.* Research OS codifies methodology that the Playbook further codifies. For the specific epistemic rules the Playbook operationalizes (SIGN cycle discipline, arc open/close, evidence gathering), Research OS **governs** the Playbook. For scope of coverage (Playbook is broader; codifies more than research alone), Research OS is peer. Long-term absorption is Cycle 3+. |
| **IOS** (`IMPLEMENTATION_OPERATING_SYSTEM.md`) | L2 repo-canonical | **Governed-by for methodology / Peer for scope** | *Corrected per Rigby F-A2.* Same as Research OS: IOS codifies verify-before-build discipline that Playbook Ch3 codifies further. For the methodological constraint, IOS governs; for Playbook's broader coverage, IOS is peer. |
| **Canon Registry** (`docs/canon/INDEX.md`) | L2 repo-canonical, runtime-load-bearing | **Peer**, receives Playbook as a new entry at ratification | Playbook is added as a Canon Registry row (per package §5.3), not absorbed by it. |
| **Repo ADR corpus (ADR-0001..0004)** | L2 repo-canonical | **Peer** (different artifact class) | Point-in-time design decisions; Playbook is a versioned methodology codification. Both are constitutional; different roles. |
| **Workspace ratification records** (existing 8) | L5 workspace-canonical | **Peer**; Playbook's ratification will create the 9th | Same envelope mechanism; Playbook envelope follows the established pattern (per 2712 §14 + package §4). |
| **CLAUDE.md** | L2 repo-canonical, runtime-load-bearing | **Peer** (session-open contract) | Playbook does not replace CLAUDE.md. CLAUDE.md remains bootstrap; Playbook is methodology. Different scope. |
| **MEMORY.md** | L2 user-level auto-memory | **Peer** (behavioral rules) | MEMORY.md is per-user behavioral guidance; Playbook is platform-scope methodology. Different scope. |
| **Frozen evidence manifest (Session 2715)** | L2 research artifact | **Peer / instrument** — governs Playbook v0.1 citation admissibility | Manifest §2.1 (freeze semantics) + §2.3 (2708-2714 chain enumeration) is the boundary the Playbook citation discipline sits within. CD-48 formally clarifies the manifest is not a chain member. |
| **Constitutional research chain (2708-2714)** | L2 research artifacts | **Governed by** Playbook post-ratification | Once Playbook exists, these become the immutable evidence backing v0.1. Future authoring cites them via the Playbook, not directly. |
| **`docs/docs-pattern/` (context-kit framework)** | Separate constitutional subtree | **Explicitly excluded** (peer with scope carve-out) | DOC_LIFECYCLE §0 excludes it; `_provenance.json._meta.excludes` excludes it. Playbook v1.0 MUST NOT govern this subtree. |
| **CI workflows** (`.github/workflows/*.yml`) | L2 executable | **Peer**, cited by Playbook Chapter 8 | Executable constitution enforced at PR-time; Playbook Chapter 8 categorizes but does not enumerate individual workflows. |
| **Runtime policy tables** (CockpitAutopilotPolicy, AgentControlEntry, Budget) | L2 executable | **Peer**, cited by Playbook Chapter 8 | Executable constitution; Playbook codifies the category, not the individual rows. |
| **Governor / active-priority / autonomy control surface** (`governor_tool` at `pa_tool_schemas.py:2739`; `active_priority_tool` at `pa_tool_schemas.py:2615`; `priority_router.py`; `active_priority_model` migration 0329) | L2 executable | **Peer** — cited by Playbook Chapter 8 as executable-constitution surface | *Added per Rigby F-A3.* Real constitutional artifact: PA tool surfaces + priority-router + autonomy-mode migration + admin controls constitute a mission-alignment governance layer distinct from CockpitAutopilotPolicy/AgentControlEntry/Budget. Ch8 STUB names "executable constitution categories"; this is one of them per Constitutional Ecosystem Inventory §5. |
| **`_provenance.json` + `_index.json`** | L2 executable | **Peer**, integrated by Playbook Chapter 6 | Existing HIGH/MEDIUM/LOW/UNKNOWN confidence classification coexists with PIC-10's 5-class taxonomy per 2714 §17.1 Amendment D. |
| **952 session handoffs** | L2 historical | **Historical**, source of evidence class E6 | Immutable-in-place. Playbook Chapter 6 (PIC-10) classifies handoffs as E6 evidence; Chapter 7 (Session Discipline) codifies their ongoing production. |
| **`docs/audit-2026/`, `docs/audits/`, `docs/archive/`** | L2 historical | **Historical** | DOC-POINTER-V2 discipline governs; Playbook does not touch. |
| **DAVINCI_RESOLVE_WORKFLOW.md (retired)** | L2 transitional | **Transitional / historical** | Sunset Session 1143. Housekeeping, not Playbook concern. |
| **21 topic docs** (`docs/topics/*`) | L2 informal current-state canon | **Peer** (informal) | Referenced by CLAUDE.md; not in Canon Registry today. Not governed by Playbook v0.1; may be promoted individually by Chris directive. |
| **~30-50 top-level docs** (AGENTS.md, API_PATH_POLICY.md, EMPLOYEE_OS_PRIMITIVES.md, etc.) | L2 informal reference | **Peer** (informal) | Follow DOC_LIFECYCLE; not Playbook-governed. |
| **`docs/architecture/*` (24 architecture docs)** | L2 descriptive | **Peer** (informal, descriptive not normative) | Not typically constitutional; Playbook does not govern. |
| **L5-hosted-L2 anomaly** (0000/0005/0010/0020/MANIFEST) | L5 workspace-canonical | **Transitional** | Cycle 2+ cleanup per 2711 §8.9 recommendation. Playbook v0.1 does not migrate; it acknowledges. |

### 2.2 Summary count (post-correction)

- **Governs Playbook:** 8 (SYSTEM_OWNER, runtime injection via `docs_context_builder.py`, `canonical_authority` derivation code, PublishGate, Cycle 0 ADRs, Cycle 1 records, Cycle 1A ADRs, evidence manifest as v0.1 instrument).
- **Governs-methodology / Peer-for-scope** (F-A2 refinement): Research OS, IOS.
- **Peer to Playbook:** ~13 other artifact classes (DOC_LIFECYCLE, Canon Registry, repo ADR corpus, workspace ratification records, CLAUDE.md, MEMORY.md, CI workflows, runtime policy tables, Governor/active-priority/autonomy control surface (F-A3 addition), provenance system, topic docs, top-level docs, architecture docs).
- **Governed by Playbook (post-ratification):** the 2708-2714 constitutional research chain becomes reference-only after v0.1 ratifies.
- **Historical (untouched):** 952 handoffs, audit archives, superseded docs.
- **Transitional:** L5-hosted-L2 artifacts (Cycle 2 cleanup), DAVINCI_RESOLVE, `_provenance.json` HIGH/MEDIUM/LOW convergence with PIC-10 (Chapter 6 handles).
- **Explicitly excluded:** docs-pattern subtree (out-of-scope for platform constitution).

### 2.3 Verdict — Section 2

The Playbook joins an existing, well-populated constitutional ecosystem. It does not compete; it codifies. The Playbook's ownership is L2 documentary; its authority is `repo_canonical`; its ratification envelope is `workspace_canonical` at deliverable-record layer. The ecosystem is architecturally coherent with this addition.

---

## Section 3 — Constitutional Authority Graph (Post-Ratification)

**Question:** After Playbook v0.1 ratifies, which documents become subordinate, which remain peers, which become historical, which become implementation references, which become runtime policy?

### 3.1 Documents that become subordinate to the Playbook

**None fully subordinate.** The Playbook is L2 methodology codification; it does not become a supreme document that governs prior canon. It integrates into the ecosystem at a specific role.

However, **the 2708-2714 research chain becomes "citation-reachable-through-Playbook"** rather than "primary reading":

- 2708 (`engineering_playbook_architecture_proposal.md`)
- 2709 (`workspace_architecture_and_constitution_proposal.md`)
- 2710 (`platform_architecture_workspace_boundary_analysis.md`)
- 2711 (`platform_constitutional_architecture.md`)
- 2712 (`engineering_playbook_architecture_specification.md`)
- 2713 (`engineering_playbook_authoring_protocol.md`)
- 2714 (`constitutional_ecosystem_inventory.md`)
- 2715 (`engineering_playbook_evidence_manifest.md`) — remains authoritative for v0.1 citation admissibility; NOT a chain member per CD-48

Also citation-reachable-through-Playbook:

- The Session 2716-2721 body drafts and Session 2723 corrected body draft.
- The Session 2722/2724/2725 Rigby SIGN audits and correction sessions.
- The Session 2726 ratification package.

These remain evidence for v0.1; they are no longer the "front door" for future readers or authoring sessions. The Playbook body becomes the front door.

### 3.2 Documents that remain peers

- **SYSTEM_OWNER.md** — remains L0-authority anchor; Playbook Chapter 1 cites, does not replace.
- **DOC_LIFECYCLE.md** — remains `authority: canonical` doc governance; Playbook Chapter 4 extends.
- **Research OS** — remains peer methodology doc; Playbook Chapter 2 references. Absorption is Cycle 3+.
- **IOS** — remains peer implementation-discipline doc; Playbook Chapter 3 references. Absorption is Cycle 3+.
- **Canon Registry (`canon/INDEX.md`)** — remains L2 promotion mechanism; gains Playbook as a new entry.
- **Repo ADR corpus** — remains design-decision layer; Playbook does not absorb ADRs.
- **Workspace ADR corpus (Cycle 0/1A)** — remains L5 workspace-canonical governance; Playbook does not absorb workspace ADRs.
- **CLAUDE.md** — remains session-open contract, bootstrap pointer. Playbook is not a bootstrap doc.
- **MEMORY.md** — remains per-user behavioral guidance. Playbook is not a memory system.
- **CI workflows, runtime policy tables, provenance system** — remain executable constitution; Playbook Chapter 8 categorizes without absorbing.
- **21 topic docs, ~30-50 informal top-level docs, ~24 architecture docs** — remain informal reference. Chris directive may promote individually.
- **`docs/docs-pattern/` subtree** — remains explicitly out of scope.

### 3.3 Documents that become historical

- **The 2708-2714 research chain** — historical-in-role, though physically still under `docs/research/platform/`. They shift from "current authoring input" to "immutable v0.1 evidence base."
- **Session 2722-2726 audit / correction / ratification-package artifacts** — historical; the ratification record's audit-history section is the durable ledger.
- **Session 2716-2721 body drafts** — historical; the ratified `docs/ENGINEERING_PLAYBOOK.md` supersedes them.

### 3.4 Documents that become implementation references

- **Frozen evidence manifest (Session 2715)** — remains the authoritative source-of-admissibility for v0.1 citations; becomes an implementation reference for future authoring sessions consulting v0.1 provenance.
- **2712 architecture specification (§5.1 frontmatter schema, §7 semver, §14 ratification envelope)** — the schema behind the Playbook body's frontmatter; future amendment PRs reference these.
- **2713 authoring protocol (§6 statement classes, §7 evidence admission)** — the discipline behind rule authoring; future rule additions reference these.

Note: 2712 and 2713 could ALSO be absorbed as Playbook chapters in a future MAJOR version — currently they are external references. This is a Cycle 3+ question.

### 3.5 What the Playbook is at runtime on ratification day (corrected per Rigby F-B2 + F-C4)

**The prior draft of this subsection overclaimed. Corrected here.** The prior draft implied the Playbook "becomes runtime policy" on ratification. That is not what actually happens. This subsection distinguishes three runtime-visibility mechanisms and places the Playbook precisely.

**Mechanism 1 — Session-open injection into agent context (guaranteed-in-context):**

Per PLAYBOOK-1.6.11 (verbatim: *"The repository MUST host three session-open contract documents that are runtime-injected into agent context at every session start: `CLAUDE.md` at the repository root (injected via `core/services/docs_context_builder.py:177` with maximum 300 lines at line 363); `docs/governance/SYSTEM_OWNER.md`; and `docs/canon/INDEX.md` (injected at line 186)."*), the runtime injection list is **exactly three documents**. On ratification day:

- `docs/ENGINEERING_PLAYBOOK.md` is **NOT** in the injection list.
- The Playbook body is therefore **NOT guaranteed-in-context** at agent session start.
- Adding the Playbook body to the injection list would be a code change to `docs_context_builder.py` — this is a Cycle 2 hardening candidate, NOT an automatic consequence of ratification.

**Mechanism 2 — Mirror into `content.Document` with RAG retrievability (available but not guaranteed):**

Post-ratification, the docs cascade runs `sync_docs_index_to_documents` + `embed_documents --all-unembedded` per package §6 Step 5. Result:

- A `content.Document` row is created for `docs/ENGINEERING_PLAYBOOK.md` with `canonical_authority='repo_canonical'` per KFI-2 B3.
- The row is embedded and RAG-retrievable.
- Agent retrieval that hits the Playbook (e.g., "what does the Playbook say about SIGN discipline?") will surface Playbook content.
- Retrieval is NOT guaranteed. An agent that does not query for Playbook content will not see it.

**Mechanism 3 — Named-in-injected-canon (indirect visibility via `canon/INDEX.md`):**

`canon/INDEX.md` is in the injection list (Mechanism 1). Post-ratification, canon/INDEX.md gains a Constitutional Canon subsection row pointing at the Playbook. That row is guaranteed-in-context. It says "the Playbook exists and is here." It does NOT inject the Playbook body itself. Agents see the pointer, not the substance, unless they follow the pointer via retrieval (Mechanism 2).

**Summary — Playbook's runtime status on ratification day:**

| Property | Status |
|---|---|
| In `docs_context_builder.py` injection list | **NO** (Cycle 2 hardening candidate) |
| Guaranteed-in-context at session start | **NO** |
| Mirrored to `content.Document` with `canonical_authority=repo_canonical` | YES (via package §6 Step 5) |
| RAG-retrievable | YES |
| Named in injected canon via `canon/INDEX.md` | YES (via package §6 Step 10) |
| Available to Rigby via her retrieval tools | YES |
| Session-open contract equivalent to CLAUDE.md / SYSTEM_OWNER.md / canon/INDEX.md | **NO** |

**Adjudication when Playbook claim conflicts with runtime code (F-B1 correction):** Per Rigby F-B1, `_canonical_authority_helpers.py` is not merely peer-executable — it is the **runtime adjudicator** of `canonical_authority`. Playbook rules may assert `canonical_authority` classifications, but the classifier code enforces them at write-time (per KFI-2 B1-B4 decision tree). If Playbook text and classifier code disagree, the code wins, unless System Owner Absolute Override directs otherwise. This is codified in Playbook PLAYBOOK-1.4.3 through PLAYBOOK-1.4.8 which describe the classifier as the runtime discipline; the review here names the adjudication direction explicitly.

**Neither `canon/INDEX.md` nor `CLAUDE.md` becomes newly runtime-authoritative** (they already are). The CLAUDE.md anchor refresh in package §6 Step 12 updates injected text; the injection mechanism itself is unchanged. Per Rigby F-B2, anchor refresh is human-protocol authoritative (subsequent Claude sessions will see the updated pointer) — not a new runtime authority claim.

### 3.6 The complete authority graph

```
                              Chris (L0 Absolute Override)
                                         │
                                         │ authorizes
                                         ▼
                             SYSTEM_OWNER.md (declaration)
                                         │
                                         │ enforced by
                                         ▼
                          docs_context_builder.py (runtime inject)
                                         │
                        ┌────────────────┼────────────────┐
                        ▼                ▼                ▼
                   CLAUDE.md       canon/INDEX.md    Every agent
                (session-open)     (Canon Registry)  execution
                                         │
                          ┌──────────────┼──────────────┐
                          ▼              ▼              ▼
                 PLATFORM_INVENTORY  DOC_LIFECYCLE  [+ Playbook entry
                    (runtime               (doc         post-ratif.]
                    counts)             governance)
                          │              │              │
                          │              │              │
                          └──────────────┴──────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
              ▼                          ▼                          ▼
    docs/ENGINEERING_PLAYBOOK.md    Research OS + IOS      Repo ADRs (0001-0004)
    (L2 repo-canonical; NEW)        (peer methodology)     (peer decisions)
              │
              │ ratification envelope
              ▼
    Workspace deliverable
    RATIFICATION_20260708_PLAYBOOK_v0_1_0
    (L5 workspace-canonical)
              │
              │ evidence chain
              ▼
    2708-2714 research + 2715 manifest + 2716-2721 drafts +
    2722-2725 SIGN + 2726 package (all historical-in-role after ratification)


    Executable constitution (parallel plane):
      CockpitAutopilotPolicy, AgentControlEntry, Budget, PublishGate,
      canonical_authority, Beat, CI workflows, cascade rules, migrations,
      signal handlers → all peer to Playbook; cited by Chapter 8, not absorbed


    Historical constitution (parallel plane):
      952 handoffs, audit archives, superseded docs, _provenance.json (2438
      docs / 7775 commits) → historical; not governed by Playbook, integrated
      by Playbook Chapter 6 (PIC-10 × existing provenance classification)


    Out of scope (explicit carve-out):
      docs/docs-pattern/ (context-kit framework, ships separately)
```

### 3.7 Verdict — Section 3

The Playbook's post-ratification role is **"L2 methodology codification with peer status alongside existing L2 documentary constitution"** — it does not become supreme; it does not absorb; it joins. The one durable directional relationship is: the 2708-2714 chain becomes evidence-for-v0.1 rather than active-research-input.

---

## Section 4 — Transition Readiness

**Question:** Once the Playbook is ratified, what actually changes?

### 4.1 Assumptions from the research phase that disappear

**Assumption:** "The methodology of the platform is discoverable through informal reading of CLAUDE.md + MEMORY.md + handoffs + audit findings + IOS + Research OS."
→ Becomes: "The methodology of the platform is codified in `docs/ENGINEERING_PLAYBOOK.md` at v0.1.0. Related documents are cited within, not competing sources."

**Assumption:** "Future methodology changes are authored as research documents in `docs/research/`."
→ Becomes: "Future methodology changes go through Playbook amendment discipline (PATCH / MINOR / MAJOR) per Chapter 10." (Nuance in §7.)

**Assumption:** "Rigby's SIGN audit is a one-off discipline for research artifacts."
→ Becomes: "SIGN is embedded in Playbook Chapter 2 as the ratifiable research-methodology rule; SIGN discipline is now first-class constitutional."

**Assumption:** "The evidence manifest is the source-of-truth for what evidence exists."
→ Becomes: "For Playbook v0.1, the frozen manifest is the source-of-truth. Future versions freeze their own manifests. CD-48 principle codifies that manifests describe chains, they do not join them."

**Assumption:** "Constitutional debt (CD-1 through CD-48) is tracked ad hoc in session artifacts."
→ Becomes: "Constitutional debt is a first-class category tracked against Playbook version; CD items resolve via PATCH/MINOR/MAJOR amendments per Chapter 10 discipline."

### 4.2 Behaviors that change

- **Session-open reading order shifts.** Today: CLAUDE.md → MEMORY.md → 00-START-NEXT-SESSION → latest handoff → Research OS §0-§5. Post-ratification: same order, but Playbook becomes a first-class reference after CLAUDE.md's anchor refresh (per package §6 Step 12). Not a full replacement — an authoritative supplement.
- **Any new methodology suggestion** — instead of "we should adopt this pattern; add it to MEMORY.md," the question becomes "does this deserve a Playbook amendment, and if so at what semver level?" (§7 nuance applies.)
- **Rule violations become citeable.** Today, a rule violation is "you didn't follow the feedback in MEMORY.md." Post-ratification, a rule violation is "you violated PLAYBOOK-N.M.K"; this is machine-parseable, versioned, and evidence-backed.
- **Rigby's constitutional role becomes structured.** SIGN cycles are Chapter 2 codified; correction discipline is Chapter 2 codified; the fresh-pin discipline (§6-§7 of 2725) is Chapter 2 codified. Rigby operates against Playbook rules, not against ad-hoc precedent.
- **Ratification records point at the Playbook.** Every future ratification record cites the Playbook version under which it was ratified. Ratification becomes a Playbook-versioned act.

### 4.3 Future work that changes

- **Cycle 2 planning becomes Playbook-scoped.** The Cycle 2 hardening items enumerated in 2712 §17 and ecosystem §14.1 (content_hash population, ORM immutability, CI validation, Canon Registry automation, runtime-load-bearing docs registry) all become Playbook amendment work — either PATCH-level (implementation-only) or MINOR-level (add new rules).
- **CD-48 remediation** — the "manifests catalog chains but do not join them" principle — becomes a v0.1.1 PATCH or v0.2 MINOR candidate (package §2.9). CD-48 is now on a known amendment track, not floating debt.
- **Chapter 2/3/4/5/7/8/9 stub-to-full conversion** — the 7 STUB chapters (per 2712 §16.9 minimum viable chapter set) will convert to FULL via MINOR amendments as evidence accumulates. Each conversion is a scoped MINOR bump with SIGN cycle.
- **Research OS absorption** — Cycle 3+ decision (ecosystem §14.4). If pursued, becomes a MAJOR Playbook bump.
- **Multi-tenant activation** — Cycle 3 opens `tenant_canonical` (2711 §12.2); this is a MAJOR Playbook bump when it lands.

### 4.4 Documentation changes

- **`docs/canon/INDEX.md`** — gets a new "Constitutional Canon" section with Playbook + evidence manifest entries (package §5.3). Last-updated bumps to Session 2727.
- **`CLAUDE.md`** — L7 anchor gets updated to reference the ratified Playbook version (Cycle 1A pattern).
- **`docs/INDEX.md`** — autogen refresh picks up the new Playbook file.
- **`docs/ENGINEERING_PLAYBOOK.md`** — created (currently does not exist).
- **`docs/research/platform/*.md`** — all 19 untracked Playbook-arc artifacts get committed at some point per package §6; their disposition to `docs/research/platform/` vs `docs/canon/` vs their own subdirectory is Chris directive. They stop being active research; they become v0.1 evidence.
- **New handoffs** — Session 2727 handoff records the ratification; subsequent handoffs cite Playbook rules by ID.

### 4.5 Engineering workflow changes

- **PR discipline** — Playbook amendments follow the workflow in 2712 §9 + §15 (release checklist). Rule additions require SIGN. Rule removals require MAJOR + Chris directive. Playbook body edits require version-bump justification in every PR.
- **CI integration** — `verify_repo_guardrails.py` becomes the Playbook-frontmatter validator (2712 §5.3). CI enforces `content_hash` post-ratification, `commit_sha` format, `version` semver format.
- **Amendment lifecycle** — Chapter 10 codifies the propose → author → SIGN → correct → ratify → mirror → cascade → tag pipeline (2712 §8 + §15).
- **Session cascade discipline** — the 4-step docs cascade + embed becomes a Playbook Chapter 4 rule (extending DOC_LIFECYCLE). Skipping the embed step becomes a citeable rule violation (currently MEMORY.md only).

### 4.6 Governance changes

- **The ratifier surface stays the same.** Chris remains L0 Absolute Override. What changes is what gets ratified: today, individual ADRs and cycle records; post-Playbook, methodology changes route through Playbook amendment.
- **The reviewer surface stays the same.** Rigby SIGN remains default; Claude verifier-loop remains fallback (2714 §6.3, encoded in PLAYBOOK-5.2.1).
- **The author surface stays the same.** Claude Code drafts; Rigby executes tool-surface calls; Claude verifies. This is codified in Playbook Chapter 5 stub referencing MEMORY.md `feedback_claude_directs_rigby_then_verifies`.
- **The discipline layer becomes rule-first with explicit override** (corrected per Rigby F-B3). Prior draft said "discipline externalized rather than embodied" — that was underspecified. The correct framing: **rule-first, override-explicit.** Post-ratification, default decisions cite Playbook rule IDs; discretionary departures require explicit acknowledgement as override/exception, logged in the session artifact (handoff or ratification-record body). System Owner Absolute Override is preserved; the requirement is that overrides be **named as overrides** rather than executed silently. This distinction closes the tension between "authority root stays with Chris" and "discipline becomes rule-first" — Chris retains discretion; the discipline is the visibility of the exception, not the absence of it.

### 4.7 Verdict — Section 4

The transition changes **workflow, discipline visibility, and evidence classification**. It does NOT change the authority root (still Chris), the review substrate (still Rigby SIGN + Claude verifier-loop), or the executable enforcement layer (still `docs_context_builder.py`, `_canonical_authority_helpers.py`, PublishGate). The transition is real but bounded.

---

## Section 5 — CD-48 Re-examination

**Question:** Does CD-48 belong in constitutional debt, or should it become constitutional law before v0.1?

**Prior conclusion (Sessions 2725 + 2726):** CD-48 is non-blocking; deferred to v0.1.1 PATCH or v0.2 MINOR amendment.

### 5.1 The CD-48 principle stated

> A document that describes or catalogs a constitutional evidence chain is not, by virtue of that catalog role, a member of the chain it describes. The evidence manifest admits sources to the constitutional corpus; it does not admit itself.

### 5.2 Why it was recorded as non-blocking

Per Session 2725 §9.1:

- **Already implicit** in manifest §2.1 (freeze semantics), manifest §2.3 (explicit 2708-2714 range), and 2713 §7.2 (convergent-research definition).
- **Rigby correctly rejected** the crossing in Session 2724 (15 F-BLOCKING [EP] defects) — meaning the boundary is enforceable *by the existing constitution* without codifying CD-48.
- **Session 2725 mission scope** (Chris-authored) explicitly excluded new policy additions; codifying CD-48 was out-of-scope for that session.
- **Suggested remediation:** a small explanatory note in Chapter 6 (PIC-10) or Chapter 10 (Evolution) — a v0.1.1 PATCH or v0.2 MINOR concern.

### 5.3 The falsification attempt

**Attack:** CD-48 is not really "already implicit." It is a boundary Rigby drew by rejecting Session 2723's crossing. Without CD-48 codified in the Playbook body, future authors have no textual anchor to consult before reaching for the manifest as a citation. The "already implicit" defense relies on the *frozen manifest itself* being read carefully — which is exactly the reading a Session 2723-style author under time pressure will skip. CD-48 codifies the reading rule; without codification, the manifest §2.3 range boundary is a text-only guardrail, not a Playbook rule.

**Steelman for elevating to constitutional law before v0.1:** the principle protects the entire evidence-manifest mechanism. If a future author, per the pattern that manifested 15 times in one Session 2723 authoring pass, cites the manifest as convergent E3 — and no Rigby SIGN catches it — the Playbook body silently drifts. The manifest is v0.1-only; v0.2 will freeze its own manifest; the pattern re-surfaces every version. Codifying CD-48 pre-v0.1 protects every future version.

**Counter-attack (why the deferred-to-v0.1.1 conclusion holds):**

1. **Manifest §2.3 is a text guardrail today AND will remain a text guardrail post-CD-48 codification.** Codifying CD-48 in the Playbook body does not change the mechanism by which the boundary is enforced — it still relies on either the author or the reviewer catching the crossing.
2. **Rigby's Session 2724 rejection is the empirical proof the boundary is enforceable in the current substrate.** SIGN + fresh-pin discipline + threshold-checking against manifest §2.2 caught 15/15 defects. CD-48 codification would strengthen documentation, not enforcement.
3. **CD-48 codification requires new-policy authoring.** Session 2725's scope constraint (correct only the 15 rules; add no policy) was Chris-directive. Extending scope pre-v0.1 requires a Chris-directive scope change (Option C in the ratification package). This is Chris's call, not a constitutional necessity.
4. **v0.1.1 PATCH is 1 PR, not a cycle.** The PATCH would add ~2-4 sentences to Chapter 6 or Chapter 10. The debt is small; the deferral cost is small.
5. **The evidence manifest §2.1 + §2.3 combined is already normative text.** Manifest freeze semantics + explicit chain enumeration is a policy statement, just not carried in the Playbook body. The Playbook body citing the manifest is a lawful continuation.

### 5.4 Where CD-48 is genuinely load-bearing

CD-48 IS load-bearing in one narrow sense: **when future Playbook versions freeze their own evidence manifests** (v0.2 freezes its manifest per 2712 §7.2 MINOR semantics), the pattern re-arises. Without CD-48 codified, every version's authoring cycle re-discovers the boundary by hitting it and being corrected. This is inefficient but not incorrect.

**Recommendation:** codify CD-48 in v0.1.1 (PATCH; ~1 week of work) or as the first item in v0.2 MINOR. Do NOT block v0.1 on it.

### 5.5 The falsification's conclusion

CD-48 does **not** become constitutional law before v0.1. It remains debt for v0.1.1 or v0.2. The principle is:

- Enforceable today via manifest §2.3 + SIGN discipline (proven Session 2724).
- Non-blocking per Session 2725 mission scope.
- Small remediation cost when codified (PATCH-sized).

**But** the review flags CD-48 as a **priority queue item for v0.1.1** — not a floating item. If Chris waives it permanently (package Option D), the mechanism relies indefinitely on SIGN vigilance. If Chris routes it as v0.1.1 (recommended), the codification lands within one PR cycle post-ratification.

### 5.6 Verdict — Section 5 (corrected per Rigby F-C1 + F-C2)

CD-48 **conditionally** does not block v0.1 ratification. The Sessions 2725 + 2726 conclusion stands **only when paired** with the following review-level posture:

**Rigby F-C1 (accepted):** codifying CD-48 into the Playbook body adds real enforcement power **only if** it (a) creates an explicit citation rule (e.g., "PLAYBOOK-6.X.X — a document that catalogs an evidence chain MUST NOT be cited as a chain-member evidence source") **and** (b) the rule is guaranteed-in-context for reviewers/agents. If the codification is merely narrative and duplicates manifest §2.3, it adds no enforcement beyond the current text guardrail. Therefore the v0.1.1 PATCH must be **non-expansive clarification of existing manifest semantics** phrased as an explicit citation-admission rule, not narrative repetition.

**Rigby F-C2 (accepted):** the "inefficient but not incorrect" framing does not satisfy the constitutional standard "no known recurring footgun may remain un-codified at ratification." Non-blocking status for CD-48 is acceptable **only if** paired with:

1. A **"known recurring defect" register entry** attached to the Playbook v0.1 constitutional-debt roll-up.
2. An **explicit commitment** that CD-48 lands in the **first amendment cycle** (v0.1.1 PATCH), not "maybe later."
3. The v0.1.1 PATCH must satisfy F-C1(a)+(b): explicit citation-admission rule, guaranteed-in-context via `docs_context_builder.py` injection (or via canon/INDEX.md linkage tightened enough that agents receiving canon see the rule).

**Package Option D (permanent CD-48 waiver) is incompatible with this posture.** The review does not recommend Option D. If Chris directs Option D, the review's non-blocking finding for CD-48 no longer stands — under Option D the v0.2+ manifest freeze at each version predictably re-hits the boundary, which does violate "no known recurring footgun uncodified" for the constitutional standard.

**Recommendation:** proceed with **Package Option A**, embedding a written commitment in the ratification-record body or the Session 2727 handoff that CD-48 codification is the target of the first amendment cycle (v0.1.1 PATCH).

---

## Section 6 — Chris-Dependence and Future Company Evolution

**Question:** If another company adopts Donkey Betz, does any part of the Constitution unnecessarily depend on Chris personally?

**Approach:** review every authority reference for personal vs role-based dependence. Determine if Platform / Organization / Workspace / Runtime authority should eventually become separate constitutional concepts.

### 6.1 Direct references to Chris in the constitutional corpus

**Personal references (name / email):**

- `docs/governance/SYSTEM_OWNER.md` — "Name: Chris West" hard-coded.
- Cycle 0/1 ratification records — `ratifier: chris` (username).
- Cycle 1A ratification records — `ratifier: chris` (username).
- MEMORY.md — many `feedback_*` entries scoped by Chris's preferences.
- CLAUDE.md — "Working with Rigby (PA)" section references Chris explicitly as the router of decisions.
- Package §2.10 — verbatim ratification directive template signed "Chris, chris@donkeybetz.com".

**Role references (System Owner):**

- SYSTEM_OWNER.md — "System Owner: Chris West" is a fusion of role + person.
- Canon Registry — "System Owner approved (Chris says 'yes')" — role + person fused.
- Playbook 2712 §4.1 — Ratifier role definition mentions Chris as current ratifier.

### 6.2 Where Chris-dependence is structural vs incidental

**Structural (would need to change under different owner):**

- **`ratifier` frontmatter field** — currently `chris` username. Under another company, would be a different username. This is per-artifact metadata; changes with each ratification. Not a structural block.
- **PA (Rigby) is currently trained on Chris's collaboration style** — MEMORY.md `feedback_claude_directs_rigby_then_verifies`, `feedback_stop_putting_chris_to_bed`, `feedback_last_mile_ui`, etc. These are behavioral. Rigby has no L0-authority claims. Not a structural block.
- **Cycle 0-1A ratification records' `ratifier: chris`** — historical fact. Immutable. Cannot be changed; would not need to be — historical ratification acts stand.
- **`docs/governance/SYSTEM_OWNER.md`** — declares Chris personally. Would need to be re-authored under different ownership (or extended to declare multiple System Owners, or refactored to declare "role: System Owner; incumbent: <name>").

**Incidental (naming, not architecture):**

- Personal-comfort MEMORY entries (`feedback_stop_putting_chris_to_bed`, PA voice preferences) — these are user-scoped, not platform-scoped. Would live at L4, not L2, in the tiered model.
- CLAUDE.md's "Chris" references — could be templated with a `{system_owner}` variable, currently isn't.

### 6.3 Should Platform / Organization / Workspace / Runtime Authority become separate constitutional concepts?

**Current state (per 2711 §5-§9):**

The six-layer stack already separates:

- **L1 Fleet Authority** — cross-app protocol; dormant.
- **L2 Platform Authority** — repo-canonical; the Playbook's home.
- **L3 Tenant Authority** — subscription/billing/compliance; dormant.
- **L4 User Authority** — preferences; not typically constitutional.
- **L5 Workspace Authority** — workspace-canonical; ratification envelopes live here.
- **L6 Deliverable Authority** — governed by higher layers.

Chris today is the **ratifier at every layer** because he is the only L0 human. The layers are architecturally distinct; the ratifier just doesn't scale to multiple people yet.

**What "Organization Authority" would look like:**

- A layer between L1 Fleet (cross-app) and L2 Platform (one-app-scope): the *company* that owns multiple apps.
- Would have its own canonical_authority value (`org_canonical` or similar).
- Would have its own ratifier role (org-level BDFL or governance board).
- Would house artifacts like company-wide brand guidelines, compliance mandates, HR policies.
- **Today: absent.** Donkey Betz is a single-app-scope L2 platform.

**What "Runtime Authority" would look like as a distinct concept:**

- Today, "runtime authority" is implicit in `docs_context_builder.py` (which docs get injected) + `_AUTHORITY_WEIGHTS` (retrieval ranking) + PublishGate (state transitions).
- Could be codified as a runtime-canonical enum value that names "these executable rules are runtime-authoritative right now" — distinct from documentary authority.
- **Today: implicit rather than absent.** The mechanism exists; the label doesn't.

**Recommendation for Cycle 3+ evolution (NOT for v0.1):**

1. **Refactor SYSTEM_OWNER.md** to separate role (`System Owner`) from incumbent (`Chris West`). Add a `succession` section pointing at how the incumbent changes.
2. **Refactor `ratifier` frontmatter** to accept both `username` and `role` — allowing role-based ratification for delegated cases.
3. **Add `org_canonical` to the canonical_authority enum** if/when Donkey Betz becomes multi-app or multi-org.
4. **Add `tenant_canonical` and `fleet_canonical`** per 2711 §12.2 evolution path (already planned).
5. **Codify Runtime Authority explicitly** in Playbook Chapter 8 — declare which mechanisms carry runtime authority vs documentary authority. Currently implicit.
6. **Consider a Playbook Chapter 11** (reserved slot) for organizational governance — how Chris's role delegates when Chris is unavailable, when the company grows, when the platform is adopted by another entity.

### 6.4 Does Chris-dependence block v0.1? (corrected per Rigby F-C3)

**Conditional NO — acceptable only if v0.1 is explicitly declared as a "single-owner, incumbent-named constitution."** Prior draft claimed the Chris-dependence was "acknowledged simplification, not a new rule." Rigby's F-C3 rejects that framing:

> "Hardcoding 'Chris West' inside a runtime-load-bearing canon doc is structural coupling (identity→authority) because the runtime is explicitly privileging that file; it's not merely narrative. Whether it's blocking depends on your stated v0.1 scope: if v0.1 claims portability/role-based evolution readiness, then this is a contradiction and can be blocking; if v0.1 is explicitly 'single-owner constitution,' it can be accepted but must be stated as an intentional constraint (not hand-waved as simplification)."

**Accepted.** Corrected posture:

- **SYSTEM_OWNER.md** hardcodes "Name: Chris West" (verbatim, doc line 19). The file is runtime-injected via `docs_context_builder.py:184` (priority 100, max 100 lines) and referenced at `:365`.
- **Playbook PLAYBOOK-1.5.1** codifies the same identity: *"The System Owner of the platform is Chris West."* This is a Playbook rule, not an incidental narrative — it lives at repository standard [RS] classification and carries E5 evidence to SYSTEM_OWNER.md + `docs_context_builder.py:184`.
- The Playbook body therefore **explicitly encodes the identity-authority coupling.** This is structural coupling in the constitutional artifact itself.

**v0.1 posture (explicit intentional constraint, not simplification):**

> The Engineering Playbook v0.1.0 is a **single-owner, incumbent-named constitution**. The identity of the System Owner is codified as a specific person (Chris West) rather than as a role that admits substitution. This is a deliberate v0.1 scope decision — not a temporary omission and not a bug — reflecting the platform's current single-owner configuration. Role/incumbent separation is an explicit Cycle 3+ MAJOR-bump concern (see §6.5 codification queue item #1). If ownership transitions (successor, delegate, or multi-owner activation) become live, the v0.1 constitution requires a MAJOR bump to accommodate.

**This posture must be surfaced in one of:**

1. The Session 2727 handoff §Executive Summary.
2. The workspace ratification record body §1 Identity block.
3. Or both (recommended).

**Under this narrowed scope claim, Chris-dependence does not block v0.1.** Under any broader claim (portability, role-based readiness, general-purpose constitution), F-C3 would surface as blocking.

### 6.5 Cycle 3+ codification queue (for the future, not for v0.1)

The review flags these items as **candidate future constitutional evolution** (not blocking, but worth recording):

1. **Separate `role` from `incumbent`** in SYSTEM_OWNER.md.
2. **Multi-ratifier delegation model** — Playbook Chapter 10 extension.
3. **`org_canonical` enum value** if Donkey Betz becomes multi-org.
4. **Explicit Runtime Authority codification** in Playbook Chapter 8.
5. **`succession` protocol** for L0 authority transition.
6. **Company-adoption playbook** — a document describing how another company would fork Donkey Betz's constitution while replacing L0 authority.

These are Cycle 3+ concerns. The v0.1 Playbook does not need to prevent them and does not encode obstacles to them.

### 6.6 Verdict — Section 6 (corrected per Rigby F-C3)

**Chris-dependence does NOT block v0.1 ratification** — **conditional on** the explicit "single-owner, incumbent-named constitution" declaration in §6.4 being surfaced in either the Session 2727 handoff or the workspace ratification record body (recommended: both).

Without that explicit declaration, F-C3 becomes blocking (any implicit portability claim contradicts the runtime-load-bearing identity coupling in SYSTEM_OWNER.md + PLAYBOOK-1.5.1).

With the declaration, the 6 evolution items in §6.5 are tracked as **CD-49 candidate** ("L0 authority role/incumbent separation") — recorded as constitutional debt for Cycle 3+ MAJOR-bump consideration, distinct from CD-48's citation-admission concern.

Playbook Chapter 1 authoring does NOT need to add a new rule for this — the existing PLAYBOOK-1.5.1 already codifies the coupling. What is needed is the **review-level and handoff-level naming** of the coupling as an intentional constraint. That naming is a Session 2727 governance act, not a Playbook amendment.

---

## Section 7 — Constitutional Lifecycle: Where Should Future Change Originate?

**Question:** Once the Playbook exists, should future methodology changes still be created as research? Or should they enter through constitutional amendment?

### 7.1 The tension

Pre-Playbook, the workflow is:

```
Chris directive → open research arc → author docs/research/*.md → SIGN → ratify (workspace deliverable + Cycle records)
```

Post-Playbook, one candidate workflow is:

```
Chris directive → propose Playbook amendment (Chapter 10 PROPOSE stage) → SIGN → ratify (workspace deliverable + version bump + git tag)
```

But there is a genuine question: **do all methodology changes enter through Chapter 10 amendment, or do some still enter as research?**

### 7.2 What Playbook Chapter 10 (Evolution & Amendment) governs

Per 2712 §8-§9 and the ratified Chapter 10 (57 rules in the FULL chapter):

- **PATCH amendments** — clarifications, typos, evidence-index refresh, retroactive citations. No new rules. No rule change. Small SIGN cycle.
- **MINOR amendments** — new rules, new chapters filling reserved slots, new statement classes, new evidence classes, new extension-point subsections. Full SIGN cycle.
- **MAJOR amendments** — rule removal, rule replacement, chapter reorganization, frontmatter schema-MAJOR, evidence-class removal. Full SIGN cycle plus Chris ratification directive with explicit acknowledgment of breaking change.

Chapter 10 governs the **codification path** but does not govern the **discovery path**. Discovery is not amendment — it is research.

### 7.3 What research still originates

- **Empirical discovery** — new patterns observed in the field (e.g., "Rigby SIGN worker instability at turn 2" — Session 1405) still originate as SIGN evidence in session handoffs and MEMORY.md before they codify. Research is where patterns emerge; amendment is where they land.
- **Cross-cutting arcs** — Cycle 2 hardening will involve research arcs (e.g., "how should content_hash population be automated?"). The research arc's *conclusions* land as Chapter 8 amendments; the arc *itself* is not an amendment.
- **New evidence-class proposals** — if E7 (e.g., "external partner attestation") is proposed, it starts as research; the amendment adds it to the schema.
- **New tenant / fleet-scope constitutional concepts** — Cycle 3+ activations will be research arcs before they become Playbook amendments.
- **Recovery patterns** — Chapter 9 recovery playbooks originate from actual incident sessions (E6 evidence); each incident is a research artifact before it becomes an [RC] rule.

### 7.4 What amendment originates

- **Rule additions** where evidence already exists — MINOR amendment.
- **Rule refinements** where clarification is needed — PATCH amendment.
- **Rule retirements** where a pattern is superseded — MAJOR amendment.
- **Frontmatter schema evolution** — MINOR (extension) or MAJOR (breaking).
- **Statement-class introductions** — MINOR amendment.
- **Chapter conversions** (STUB → FULL for Chapters 2, 3, 4, 5, 7, 8, 9) — MINOR amendment per 2712 §16.9.

### 7.5 The synthesis: research feeds amendment

The correct model is:

```
Empirical observation
     ↓
Session handoff / MEMORY.md rule / SIGN finding
     ↓
Research arc (if pattern needs synthesis, or is cross-cutting, or introduces new concepts)
     ↓
Convergent research (≥2 arcs corroborating)
     ↓
Playbook amendment proposal (Chapter 10 PROPOSE)
     ↓
SIGN cycle
     ↓
Ratification directive
     ↓
Ratified Playbook version bump
     ↓
Cascade → runtime injection → agents see the new rule
```

**Research and amendment are not competitors — they are pipeline stages.** Research is discovery + synthesis. Amendment is codification + ratification. The Playbook governs the codification stage; it does not replace the discovery stage.

### 7.6 What CANNOT come through research alone anymore (extended per Rigby F-D2)

Once the Playbook exists, these MUST enter through amendment (not directly to code + docs):

- **Any change to how rules are authored, classified, or evidenced** — governed by Playbook Chapter 6 (PIC-10) and Chapter 10 (Evolution). Bypassing Chapter 10 to change PIC-10 informally = constitutional violation.
- **Any change to statement classes** — Chapter 6 governs.
- **Any change to evidence classes** — Chapter 6 + 2712 §11 govern.
- **Any change to ratification workflow** — Chapter 10 governs.
- **Any change to session-open discipline** — Chapter 7 (STUB in v0.1; becomes FULL via MINOR amendment) governs.
- **CI/tooling changes that effectively change constitutional requirements** (Rigby F-D2). Not every CI change qualifies — pure refactoring, formatting, or non-constitutional guardrail additions can proceed as PR-only. But CI changes that:
  - Alter what evidence is required for a rule to pass admission (Chapter 6 evidence-class enforcement).
  - Alter what frontmatter fields are validated (2712 §5.3 validation).
  - Alter what commits are permitted on `main` (branch protection, tag rules).
  - Add or remove enforcement of any Playbook rule.
  ...effectively change constitutional behavior via tooling. These MUST be accompanied by either (a) a Chapter 10-governed amendment, OR (b) a ratified rationale entry in the workspace explaining why the CI change is a downstream implementation of an existing Playbook rule (not a new rule). Without one of these gates, CI drift produces "silent constitutional change via tooling" — Rigby's F-D2 finding.

Attempting to change any of these via a research arc + Chris directive **without a Chapter 10 amendment cycle** (or, for CI changes, the ratified-rationale gate) would violate the Playbook's own constitutional discipline. The amendment cycle IS the discipline.

### 7.7 Where Chris directive still applies without amendment

- **Chris directive can override any Playbook rule** — SYSTEM_OWNER.md declares Absolute Override. This means Chris can, for a specific session, direct a departure from a Playbook rule. The departure is a data point, not a rule change. If the departure recurs, the pattern eventually earns amendment consideration.
- **Chris directive can accelerate amendment** — Chris can bypass SIGN for emergency amendments (2712 §9.6). This is a documented emergency mechanism; not a bypass of the codification path.
- **Chris directive is required for MAJOR bumps** — no MAJOR amendment ships without explicit Chris ratification directive per 2712 §8.5.

### 7.7a Research output admissibility (added per Rigby F-D1)

Post-ratification, research arcs remain the origination point for methodology change. But **not all research output is amendment-admissible.** Rigby F-D1 identified a hidden trap: without an explicit distinction, an author may produce research believing it is amendment-ready when it is not, and be surprised at SIGN.

**Distinction (recorded here; codification is a Chapter 6 or Chapter 10 concern for v0.1.1 PATCH or v0.2 MINOR):**

- **Amendment-admissible research output** — a research artifact that satisfies at least one of:
  - Convergent-research citation per 2713 §7.2 (synthesis from ≥2 independent research arcs on the same subject).
  - Ratification via workspace deliverable + `content_hash` populated, entering the constitutional evidence corpus.
  - Endorsement by an existing Playbook rule as an evidence source at admission time.
- **Informative-but-non-evidence research output** — a research artifact that describes patterns, proposes ideas, or records observations but does not yet meet an evidence-admission threshold. Such artifacts inform future amendments; they cannot be cited as the sole evidence for a new rule.

This distinction closes the trap Rigby named. Its codification lands in the first amendment cycle (either as a Chapter 6 addition alongside CD-48, or as a Chapter 10 clarification of amendment inputs).

### 7.8 Verdict — Section 7 (corrected)

**Future methodology change originates as research; codifies through Playbook amendment; ratifies via workspace record + git tag.** Research and amendment are pipeline stages, not competing entry points. The Playbook does not eliminate research; it structures where research lands.

**Where Cycle 2+ governance rules originate:** as research arcs, per Cycle 2 planning. Each research arc's output either lands as a Playbook amendment or, if scope-outside-Playbook (e.g., a new ADR governing a specific implementation), lands as an ADR + optional Playbook amendment referencing the ADR.

**Where methodology, engineering discipline, and constitutional policy originate:** through the Playbook amendment cycle (Chapter 10). Direct-to-code + docs bypass is a constitutional violation post-ratification. CI/tooling changes that alter constitutional requirements are subject to the F-D2 gate above.

**Where architectural standards originate:** as research (feasibility, synthesis) → then codify via Playbook amendment (if statement-class-fittable) OR ADR (if implementation-specific).

**Where research output admissibility is adjudicated:** the amendment-admissible vs informative-but-non-evidence distinction (§7.7a) is the review-level answer pending codification via Chapter 6 or Chapter 10 in a first amendment cycle.

---

## Section 8 — What Changes on Ratification Day

**Question:** Describe exactly what changes on the day the Playbook is ratified.

### 8.1 Before ratification (current state)

- No `docs/ENGINEERING_PLAYBOOK.md` file exists.
- 19 untracked research artifacts sit in `docs/research/platform/`.
- Canon Registry has 5 promoted docs + 8 autogen runtime audits + Pending Review for "Stage 2 Governance Plan."
- Constitutional debt: CD-47 RESOLVED, CD-48 non-blocking recorded, earlier CD-1..CD-46 outside 2725 scope.
- Cycle 1A ratified. Cycle 1 open at 0100 (ratified). Cycle 1 closure at 0199 ratified. Cycle 2 not yet opened.
- No `playbook-v0.1.0` git tag.
- No `RATIFICATION_20260708_PLAYBOOK_v0_1_0` workspace deliverable.
- CLAUDE.md L7 anchor references Cycle 1A workspace ADRs and manifest.
- Session 2726 has produced the ratification package. Session 2727 awaits Chris directive on Option A/B/C/D/E.

### 8.2 Ratification (the seam)

Per package §6 runbook (14 steps), ratification is a multi-step act, not a single instant:

- **Step 1-2:** `docs/ENGINEERING_PLAYBOOK.md` written on branch `playbook/v0.1.0-inaugural`.
- **Step 3-4:** PR opened → Chris review → merge to `main`. Merge commit SHA captured.
- **Step 5:** First-round docs cascade — build_docs_index → build_rag_corpus → sync → embed.
- **Step 6:** Workspace ratification record deliverable drafted.
- **Step 7:** Chris ratification directive routed to Rigby; deliverable transitions to `ratified`.
- **Step 8:** Post-ratification frontmatter follow-up commit (fills `content_hash`, `commit_sha`, `git_tag`, `ratified_date`, `ratification_record.deliverable_id`).
- **Step 9:** Mirror verification per KFI-1.
- **Step 10:** Canon Registry update.
- **Step 11:** Final cascade.
- **Step 12:** Handoff + 00-START-NEXT-SESSION.md update.
- **Step 13:** Rigby final verification probe.
- **Step 14:** Session close.

The "ratification moment" — the specific transition from unratified to ratified — is **Step 7 (Chris directive routed to Rigby; PublishGate flips deliverable to `ratified`)**. That is the constitutional seam.

### 8.3 After ratification (target state)

- `docs/ENGINEERING_PLAYBOOK.md` exists at v0.1.0 with 165 rules, 11 chapters, ratified frontmatter.
- `playbook-v0.1.0` git tag created.
- `RATIFICATION_20260708_PLAYBOOK_v0_1_0` (or `_20260709_`) workspace deliverable ratified in `a9a16593-e0a4-44dc-8256-efc65d524b3c`.
- Canon Registry has a "Constitutional Canon" subsection with Playbook + evidence manifest entries. Registry count: 7 promoted (was 5), still under ≤10 cap.
- `CLAUDE.md` L7 anchor references Playbook v0.1.0.
- Constitutional debt: CD-47 RESOLVED (already); CD-48 queued for v0.1.1 or v0.2.
- `content.Document` mirror row for `docs/ENGINEERING_PLAYBOOK.md` with `canonical_authority='repo_canonical'`.
- `content.Document` mirror row for the ratification record with `canonical_authority='workspace_canonical'`.
- Session 2727+ handoffs cite Playbook rules by ID.
- Cycle 2 planning becomes the immediate follow-on work.

### 8.3a Freeze and timing integrity (added per Rigby Q4 item 3 + F-E2 freeze-integrity attack)

Ratification is not an instantaneous atomic event. It is a 14-step runbook (package §6) that spans commits, workspace mutations, cascade runs, and tag creation. This introduces the possibility of intermediate states where the artifact is partially ratified (some steps complete, others pending). Rigby's F-E2 named this as an attack the review had not addressed. Addressing it here.

**What "v0.1 manifest freeze" means (Rigby Q4 item 3):**

The frozen evidence manifest (Session 2715) §2.1 declares: *"Every source enumerated in §3-§14 is admissible for v0.1 authoring without further justification."* This is a freeze on **admissible sources** — the input corpus for v0.1 rule authoring. It is **not** a freeze on derived draft text (the Playbook body itself, which was iteratively edited through Sessions 2716-2721 authoring + 2723 correction + 2725 citation substitution).

The distinction:

- **Frozen (§2.1):** the enumeration of admissible sources in manifest §3-§14. Any citation of a source not in this enumeration requires manifest amendment before it can enter the Playbook body. This is the constitutional guarantee behind the manifest.
- **Not frozen:** the Playbook body itself (drafts, corrections, citation substitutions per Session 2725). Draft edits are the normal authoring workflow; the freeze does not prevent them, because they operate *on the Playbook body*, not *on the source enumeration*.

Under this reading, Session 2725's CD-47 correction pass (citation substitutions per §3 of the correction session) did **not** violate the manifest freeze. The substitutions swapped one already-admissible source (2715, subject to CD-48) for another already-admissible source (2711/2712/2714). The set of admissible sources did not expand or contract. The Playbook body changed; the manifest did not.

CD-48 is the codification concern for future authoring where an author might attempt to cite the manifest itself (not an enumerated source but the enumeration instrument) as evidence — that would attempt to expand the admissible-sources set implicitly, which the manifest freeze prohibits.

**Ratification ordering and intermediate-state coherence:**

Per package §6 runbook (14 steps), the ratification sequence has multiple write-points across git and workspace. An intermediate state where some writes complete and others pend is possible. The relevant transitions:

| Step | Write action | Intermediate-state exposure |
|---|---|---|
| Step 2 | Commit `docs/ENGINEERING_PLAYBOOK.md` on branch `playbook/v0.1.0-inaugural` with placeholder frontmatter fields | Branch-scoped; not visible on `main` |
| Step 4 | Merge to `main`; capture merge SHA | Playbook file visible; `content_hash`/`ratification_record.deliverable_id`/`git_tag`/`ratified_date` still placeholder |
| Step 5 | Cascade + embed | `content.Document` mirror row created; RAG queries return Playbook with placeholder-frontmatter body |
| Step 6-7 | Workspace ratification record created (draft → ratified via `content_tool.content_complete`) | Ratification record exists but Playbook frontmatter still holds placeholders |
| Step 8 | Frontmatter follow-up commit fills placeholders | Playbook frontmatter now shows `version_status: ratified` with concrete values |
| Step 10 | Canon Registry update | canon/INDEX.md gains Constitutional Canon subsection |
| Step 11 | Second cascade | All doc mirrors updated to consistent state |

**Failure modes and reversal:**

- **Step 4-5 merge succeeds, Step 6-7 workspace ratification stalls** — Playbook is on `main` with `version_status: draft` frontmatter and no workspace ratification record. Recovery: complete Step 6-7; frontmatter remains draft until Step 8 completes. Rollback path: `git revert` the Step 4 merge commit; workspace record was never created; no persistent state.
- **Step 6-7 workspace ratification succeeds, Step 8 frontmatter follow-up stalls** — workspace record cites a `commit_sha` in `main` but the frontmatter still shows placeholders. This is the two-commit pattern's known window. Recovery: complete Step 8. Reversal: retire the workspace ratification record via `session_tool.retire`-analog on the workspace deliverable (deliverable state transition to `superseded` or `withdrawn`); reissue Playbook with fresh commit if desired.
- **Step 10-11 Canon Registry update stalls** — Playbook is ratified per Step 6-7 but not surfaced in Canon Registry. Recovery: complete Step 10 as a follow-up PR; ratification stands.
- **Full un-ratification path (post-Step 8, mature ratified state):** per Executive Verdict "Reversal channel." Requires System Owner Absolute Override directive. Executes as (a) new commit setting `version_status: superseded` or `version_status: retracted`; (b) workspace deliverable transition to `superseded`; (c) MAJOR version bump if a replacement Playbook body is issued.

**Coherence guarantee at each step:**

At any step, the following invariants hold or are being restored:
- The workspace ratification record's `commit_sha` field either holds a placeholder OR references a `main`-visible commit.
- The Playbook frontmatter's `ratification_record.deliverable_id` either holds a placeholder OR references an existing workspace deliverable.
- The Canon Registry either does NOT list the Playbook OR lists it via `canon/INDEX.md` at the ratified path.
- The `content.Document` mirror either does NOT exist OR reflects the current `main`-visible frontmatter.

**Attack rebuttal (F-E2 freeze-integrity):** the freeze operates on sources, not on draft text. Session 2725 corrections are compatible.

**Attack rebuttal (F-E2 timing/ordering race):** the 14-step runbook is designed with placeholder sentinels + two-commit pattern to bound the intermediate states. Named recovery paths exist for each stall point. "Ratified but not coherent" states are recoverable, not persistent.

### 8.4 Major transitions

The following are the **irreversible / semantically-significant** transitions on ratification day:

| Transition | Before | After |
|---|---|---|
| **Constitutional codification** | Informal (CLAUDE.md, MEMORY.md, IOS, Research OS, handoffs, ADRs — scattered) | Formal (Playbook v0.1.0 unified codification with 165 rules, evidence-cited, semver-tracked) |
| **Ratification substrate** | Per-artifact (each ADR has its own ratification record) | Per-artifact + version-tracked (Playbook amendments cascade version bumps; ratification records reference versions) |
| **Rule identity** | Anonymous (rules are "the rule from feedback_verifier_loop_pattern.md" or "the rule from IOS §4.3") | Named (rules are PLAYBOOK-N.M.K with stable identifiers across versions) |
| **Constitutional debt tracking** | Ad hoc | First-class category tied to versions (CD-47 resolved-in-v0.1, CD-48 targeted-for-v0.1.1) |
| **Evidence discipline** | Informal per-artifact | PIC-10 provenance classification standard, evidence class E1-E6, per-class admission thresholds |
| **Future amendment path** | Research + Chris directive + doc edit | Chapter 10 amendment cycle (propose → author → SIGN → correct → ratify → mirror → tag → cascade) |
| **Session-open reference** | CLAUDE.md + MEMORY.md + 00-START + handoff + Research OS | Same, plus Playbook v0.1.0 as an authoritative supplement |
| **Rigby's operational grounding** | Precedent + MEMORY.md rules | Precedent + MEMORY.md rules + Playbook rules by ID |
| **The "third-order governance artifact"** | Named in 2707 handoff as remaining Cycle 1 work | Instantiated as v0.1.0 |
| **The Architecture Research phase** | Open (Sessions 2708-2726 producing artifacts) | Closed (declared complete per Section 10 answer #10 below) |

### 8.5 Character of the transition (corrected per Rigby F-B4 + F-D3 + F-D4)

The transition has four character properties worth naming (previously three; the fourth surfaces the namespace shift Rigby F-D3 identified):

1. **It is reversible via named channels** (Rigby F-B4 correction). The prior draft claimed "irreversible in intent" — this was overclaiming. Actual reversal channels:
   - System Owner Absolute Override directive (SYSTEM_OWNER.md §1) can un-ratify v0.1 at any time; execution follows §8.3a "Full un-ratification path."
   - MAJOR supersession per 2712 §7.3 replaces v0.1 with a v1.0.0 or higher body carrying revised rules; the v0.1 body remains ratified-in-history via the immutable git tag `playbook-v0.1.0`.
   - Errata amendment per 2712 §15.3 acknowledges a defect via PATCH without moving the tag.
   - Evidentiary burden for un-ratification: (a) written directive from Chris naming the defect; (b) workspace deliverable transition to `superseded` or `withdrawn`; (c) if replaced, MAJOR version bump. Un-ratification is not costly to reach; it is procedurally structured, not physically prevented.
2. **It is one-way in default workflow.** After ratification, methodology changes route through Chapter 10 amendment as the default path. The pre-Playbook workflow (informal research + Chris directive) becomes an exception (emergency amendments per 2712 §9.6) rather than the default. Rule-first + override-explicit (§4.6) preserves Chris's discretion.
3. **It is bounded in operational scope but high-leverage in runtime-context surfaces** (Rigby F-D4 correction). The prior draft claimed "bounded in scope." That is true for product operations (no product feature migration, no user-facing change, no deployment disruption) but underspecifies the mutation to runtime-context surfaces. Ratification mutates:
   - The docs cascade table (build_docs_index, build_rag_corpus, sync_docs_index_to_documents, embed_documents) — write ops to `Document`, `DocumentEmbedding`, and RAG corpus manifest.
   - Canon Registry (`docs/canon/INDEX.md`) — runtime-load-bearing via `docs_context_builder.py:186`. A new subsection is added.
   - CLAUDE.md L7 anchor (per package §6 Step 12) — runtime-load-bearing via `docs_context_builder.py:177`. Text update to the injected content.
   - `content.Document` mirror row for the Playbook body + workspace ratification record.
   Failure modes and rollback for each are enumerated in §8.3a. "Bounded" is retained but qualified: bounded in *operational scope* (things the platform *does*) while *high-leverage* in *runtime-context surfaces* (things the platform's agents *see*).
4. **A namespace shift occurs on ratification day even with STUB chapters** (added per Rigby F-D3). Prior draft implied ratification day is stationary until Ch2 becomes FULL. That is not accurate. On ratification day:
   - Rigby's SIGN findings default to Playbook rule-IDs (`PLAYBOOK-N.M.K`) as the reference namespace for rule citations. This holds even for STUB chapters whose stubs still carry rule IDs.
   - Handoffs, deliverables, and audit findings post-ratification cite Playbook IDs as the primary way to name rules.
   - The fully load-bearing procedural change (SIGN cadence, acceptance criteria, enforcement hooks per Chapter 2) remains Cycle 2 work — that IS still gated on Ch2 STUB→FULL.
   - But the namespace shift itself is immediate on ratification. Rigby operates against Playbook IDs post-ratification even before Chapter 2 becomes FULL.

### 8.6 Verdict — Section 8 (corrected)

The transition is real, one-way-in-default-workflow, bounded-in-operational-scope-but-high-leverage-in-runtime-surfaces, semantically significant, and reversible via named channels. The specific moment of transition is Step 7 (PublishGate transition to `ratified`). Everything before is preparation; everything after is Cycle 2+ engineering. Intermediate states between Steps 4 and 8 are recoverable per §8.3a. Namespace shift to Playbook rule-IDs is immediate on Step 7 even for STUB chapters.

---

## Section 9 — Falsification: Attempts to Prove the Architecture Should NOT Be Ratified

**Approach:** attack from every plausible direction listed in the mission. Retire attacks that fail.

### 9.1 Attack: Hidden circular authority (corrected per Rigby F-E1)

**Claim:** the Playbook cites SYSTEM_OWNER.md; SYSTEM_OWNER.md declares Chris's Absolute Override; Chris ratifies the Playbook. Isn't this circular?

**Attack:** yes — Chris authorizes the very document that declares him authorized. If ratifying were an act of self-authorization, the Playbook has no epistemic ground.

**Refutation (revised — deeper evidence per Rigby F-E4):** the circularity is **not** structural, but the prior draft's "extrinsic ownership" defense dodged the **bootstrap ceremony problem** that Rigby F-E1 named. Addressing directly:

- **Extrinsic authority (source):** Chris's Absolute Override authority derives from ownership of the platform (git repository ownership, business ownership, service infrastructure ownership). This is extrinsic to the Constitution. SYSTEM_OWNER.md documents that pre-existing authority; ratification of the Playbook is Chris exercising authority that already existed. This is the standard "founding constitution" pattern.
- **Bootstrap ceremony (binding of future actors):** the harder question is how the constitution binds *future actors* (Rigby, Claude Code sessions, downstream contributors) who did not exist at the moment of ratification. The answer is: the constitution binds them via **runtime injection** (per §3.5 Mechanism 1) — future agents receive SYSTEM_OWNER.md + CLAUDE.md + canon/INDEX.md as guaranteed-in-context data at session-open. The Playbook (once in canon) is named by the injected canon/INDEX.md and RAG-retrievable by name. Future actors receive the constitution before they act; consent is by construction, not by explicit assent.
- **Enforcement point:** `docs_context_builder.py:177,184,186` is the concrete substrate binding future actors. This is not narrative; it is executable enforcement. Bootstrap ceremony is completed at every session start, not once at ratification.

**Verdict:** rejected. The apparent circle is documentation-order, not authority-order. The bootstrap ceremony is executed continuously via runtime injection — this is stronger than the original draft's "extrinsic ownership" framing.

### 9.2 Attack: Ownership inversion

**Claim:** the Playbook governs L2 Platform, but is ratified via an L5 Workspace deliverable. Isn't the lower layer governing the upper layer?

**Attack:** in the six-layer hierarchy, L5 Workspace is below L2 Platform. The workspace ratification record is L5; the Playbook is L2. If L5 ratifies L2, the layer directionality is inverted.

**Refutation:** per 2711 §10.2, ratification envelopes can move upward. A workspace ratification record can name a platform-scope artifact (git commit + tag). The envelope lives at L5; the artifact stays at L2. The workspace does not become the owner of the platform artifact — it becomes the *ratification ledger* for the artifact. The authority chain is: Chris (L0) → workspace ratification record (L5 ledger) → Playbook body (L2 substance). Chris's authority operates across layers; the workspace is his ledger of record.

**Verdict:** rejected. Envelope layer ≠ substance layer.

### 9.3 Attack: Missing constitutional layer

**Claim:** the six-layer stack is insufficient. Where is Organization / Company / Corporation? Where is Team? Where is Product?

**Attack:** real-world governance often needs an Org layer between Fleet (cross-app) and Platform (single-app-scope). Donkey Betz today is single-app but the constitution should scale.

**Refutation:** the stack is proven to be sufficient FOR THE CURRENT CONFIGURATION. 2711 §12 pre-plans enum expansion (`tenant_canonical`, `fleet_canonical`) — the mechanism is designed for growth. Adding a layer prematurely creates dead architecture (per 2711 §12.3). If Organization emerges as a real layer, it enters via a MAJOR Playbook bump. The v0.1 architecture does not need to prevent this and does not prevent it.

**Verdict:** rejected as a v0.1 blocker; accepted as a Cycle 3+ evolution vector (see Section 6.5 codification queue).

### 9.4 Attack: Runtime contradiction

**Claim:** the Playbook declares `docs/ENGINEERING_PLAYBOOK.md` `canonical_authority='repo_canonical'` per KFI-2 B3. But B3 requires `source='imported' AND file_path.startswith('docs/')`. What if a future refactor moves the Playbook out of `docs/`?

**Attack:** `_canonical_authority_helpers.py:33-60` is the runtime enforcer. If the file moves, B3 no longer applies; the classifier lands in B4 (`derived`), which is a lower authority. The Playbook's declared classification would drift from the enforced classification.

**Refutation:** per 2712 §5.3 frontmatter validation, the `repository_path` field enforces location. Renames require a MAJOR bump. `verify_repo_guardrails.py` catches this at PR time (2712 §17.3). Runtime and documentary agree because CI holds them in agreement.

**Verdict:** rejected. CI enforcement is the guarantee that runtime and doc do not diverge.

### 9.5 Attack: Canon inconsistency (corrected per Rigby F-E1)

**Claim:** the Canon Registry has a ≤10-doc cap. Playbook + evidence manifest brings it from 5 to 7. Then Chapter 7 (Session Discipline) will want to promote CLAUDE.md, and Chapter 4 will want to promote DOC_LIFECYCLE (already in). What about Chapter 8's runtime tables? The cap breaks fast.

**Attack:** if the Playbook induces Canon Registry inflation, the "intentionally small" property is compromised.

**Refutation (revised per Rigby F-E1 — "flagged for Cycle 2" is not a rejection):** the prior draft claimed "flagged as a Cycle 2 partition question" — Rigby correctly noted that flagging-without-plan is not a rejection. Two v0.1-scope commitments make this rejection valid:

- **v0.1 cap-compliance verification:** DOC_LIFECYCLE, PLATFORM_INVENTORY, 00-START-NEXT-SESSION, AUDIT_INDEX, and INDEX are already in Canon (5 promoted). Playbook + evidence manifest add 2. Post-ratification total: 7 promoted + 8 autogen runtime audits. The ≤10 cap applies to promoted (non-autogen) — still 3 slots headroom.
- **v0.1 freeze rule:** no further Canon Registry additions may be made in v0.1 without either (a) a Cycle 2 partition producing a "Constitutional Canon" sub-registry with its own cap, OR (b) an explicit Chris directive that acknowledges cap pressure and either removes an entry or expands the cap. Any implicit promotion attempt during v0.1 lifetime (e.g., a session that unilaterally adds a Canon Registry row) is a constitutional violation and MUST be reverted at SIGN.

Under these two commitments, the ≤10 cap is respected for v0.1 lifetime, and cap pressure enters a controlled Cycle 2 decision path rather than accumulating silently.

**Verdict:** rejected as a v0.1 blocker under the two v0.1 commitments above. Without them, the rejection reduces to "flagged for later" — not a rejection.

### 9.6 Attack: Workspace inconsistency

**Claim:** Cycle 0-1A workspace ADRs used `deliverable_type='document'` (0110/0120/0130) mixing with `deliverable_type='ratification_record'` (0140/0150/0199). If the Playbook ratification record is `ratification_record` but historical records aren't, is the corpus inconsistent?

**Attack:** yes — different `deliverable_type` values on semantically equivalent artifacts. Playbook ratification cannot pretend the historical inconsistency is resolved.

**Refutation:** per 2711 §13.6 + package §4.2, historical inconsistency is documented in 0199 §6. Playbook v0.1 does NOT retroactively fix it. Cycle 2 hardening (2712 §17 + ecosystem §14.1) addresses via CI check enforcing `deliverable_type='ratification_record'` for new records. Historical drift acknowledged; future drift prevented.

**Verdict:** rejected. Inconsistency is bounded to historical records; forward guarantee established.

### 9.7 Attack: Amendment paradox

**Claim:** Chapter 10 (Evolution & Amendment) governs how the Playbook amends itself. If Chapter 10 has a defect, what mechanism fixes it? Amendment via Chapter 10 = self-reference. Amendment outside Chapter 10 = Chapter 10 violation.

**Attack:** the amendment discipline cannot audit itself.

**Refutation:** the same pattern applies to any self-amending constitution (the U.S. Constitution's Article V amends itself via its own procedure). This is the standard self-reference; it does not paralyze the system. Chapter 10 defects surface via SIGN cycles (Rigby catches them the same way any other rule defect is caught). Emergency amendment (2712 §9.6) provides a Chris-directive bypass for genuine paralysis cases. Cycle 3+ can add a "Chapter 10 recovery" playbook if needed.

**Verdict:** rejected. Self-reference is standard; recovery mechanism exists.

### 9.8 Attack: Ratification paradox

**Claim:** the Playbook v0.1 ratification cites its own frontmatter fields for `commit_sha`, `content_hash`, `ratification_record.deliverable_id` — but these values do not exist until AFTER ratification. Circular reference.

**Attack:** the Playbook cannot cite what does not exist yet.

**Refutation:** the two-commit pattern in 2712 §15.1 + package §3.2 resolves this. The ratification commit writes the Playbook with `version_status: draft` (or `signing`) and placeholder sentinels. The post-ratification frontmatter follow-up commit fills the deferred fields after they become known. This is documented and executable per package §6 Step 8.

**Verdict:** rejected. Two-commit pattern resolves the temporal paradox.

### 9.9 Attack: Historical inconsistency (corrected per Rigby F-E1 — reclassified as controlled exception)

**Claim:** 952 handoffs, 4 repo ADRs, 5+ workspace ADRs, 8+ ratification records, IOS + Research OS + startup-introspection — these are pre-Playbook constitutional artifacts using different conventions (statement-class markers, frontmatter shapes, ratification patterns). Playbook v0.1 does not retroactively conform them. The historical corpus is inconsistent with the Playbook's own discipline.

**Attack:** the Playbook creates a two-tier corpus: post-v0.1 artifacts conform; pre-v0.1 artifacts don't. Readers must know which era an artifact belongs to.

**Refutation (revised per Rigby F-E1 — "grandfathering" is an acceptance-under-conditions, not a flat rejection):** Rigby correctly noted the prior draft mislabeled this. Correcting:

- Pre-v0.1 artifacts are **grandfathered as a controlled exception.** They were ratified under prior norms and remain immutable — the Playbook does not retroactively invalidate them.
- Two-tier corpus is **accepted, not refuted.** Readers must know which era an artifact belongs to; this is a known cost of any inaugural constitutional codification.
- The **conditions on the grandfathering acceptance:**
  - Chapter 1 provisional-inventory acknowledgment MUST name the grandfathering explicitly (per ecosystem Amendment B).
  - Pre-v0.1 artifacts can be cited as E6 (session handoff) or E5 (platform evidence) at their own ratification standard; they cannot be cited as evidence of Playbook-standard discipline.
  - Future ratifications that reference pre-v0.1 artifacts MUST NOT claim Playbook-discipline compliance on their behalf.
  - Reader-orientation aids (frontmatter `authority`, `session_added`, `last_verified` fields) become mandatory for future artifacts to distinguish era.

**Verdict:** classified as **controlled exception** rather than "rejected." The attack succeeds as a description of the corpus reality; the controlled-exception framing makes it acceptable-under-conditions, not a v0.1 blocker.

### 9.10 Attack: Future scalability

**Claim:** the Playbook is designed for single-app, single-ratifier configuration. Multi-tenant, multi-org, multi-app, multi-ratifier futures will require significant rewrite.

**Attack:** if v0.1 encodes assumptions that a Cycle 3 activation will break, ratifying v0.1 creates a load-bearing artifact that must be MAJOR-bumped soon.

**Refutation:** 2711 §12 pre-plans enum expansion. 2712 §16.1 pre-reserves chapter slots 11-19. 2712 §4.1 pre-documents ratifier-delegation extension point. Section 6 above documents the L0 role/incumbent separation as a future evolution vector. The Playbook is designed to grow into these futures via MAJOR bumps — not to prevent them. A future MAJOR bump is not a design flaw; it is the mechanism for evolution.

**Verdict:** rejected. Future MAJOR bumps are the expected evolution mechanism.

### 9.11 Attack: The "one more corner case" attack

**Claim:** somewhere, some artifact was missed. Ecosystem §16.9 self-critiques that `docs/playbooks/`, `docs/agents/`, `docs/apis/`, etc. were not enumerated.

**Attack:** if a constitutional artifact is missed and later discovered, v0.1's Chapter 1 constitutional context is factually incomplete.

**Refutation:** Chapter 1 provisional-inventory acknowledgement (per 2714 Amendment B) explicitly names this incompleteness. Cycle 2 audit is expected to complete the inventory. A missed artifact does NOT invalidate v0.1's ratification — it triggers a PATCH (evidence-index refresh) or MINOR (if the discovery adds a rule).

**Verdict:** rejected. Chapter 1 acknowledges limitations; PATCH mechanism handles discovery.

### 9.12 Attack: The evidence manifest is not a chain member (CD-48 re-attack)

**Claim:** the frozen manifest §2.3 restricts convergent-research to 2708-2714. But the manifest itself synthesizes evidence. What if a rule genuinely needs to cite the manifest?

**Attack:** if a rule genuinely needs to cite the manifest, CD-48 blocks it. The Playbook has an unclosed evidence gap.

**Refutation:** per 2725 §3, all 15 CD-47 defects were resolvable via substitution to a bona fide chain member (2711/2712/2714). No rule genuinely needed the manifest as citation. The gap is theoretical, not observed. Rigby confirmed 15/15 PASS.

**Verdict:** rejected. Empirically, the manifest was not needed as a citation source.

### 9.13 Attack: Timing/ordering race (added per Rigby F-E2)

**Claim:** ratification is a 14-step runbook (package §6) spanning multiple write points: commit → merge → cascade → workspace deliverable → workspace transition to `ratified` → frontmatter follow-up commit → tag → Canon Registry update → second cascade. An intermediate state could exist where some writes complete and others pend, producing a "ratified but not coherent" artifact — e.g., Playbook body on `main` with placeholder frontmatter while workspace ratification record cites a merge SHA that has not yet been tagged.

**Attack:** the constitutional artifact does not commit atomically. If a stall or failure occurs mid-runbook, the platform enters a state where different parts of the constitutional evidence chain disagree about ratification status.

**Refutation (per §8.3a "Freeze and timing integrity"):** the runbook is designed with two mechanisms to bound intermediate states:

- **Placeholder sentinels** (2712 §5.1 + §15.1 two-commit pattern): the ratification commit writes frontmatter fields as placeholders (`content_hash: <PLACEHOLDER>`, `commit_sha: <PLACEHOLDER>`, etc.) with `version_status: draft` (or `signing`). The `status` frontmatter field explicitly signals not-yet-ratified until Step 8 flips it to `ratified`. This is discoverable via `grep version_status` and CI-enforceable via `verify_repo_guardrails.py`.
- **Named recovery paths** for each stall point (per §8.3a table): Step 4-5 stall recoverable via revert or completion; Step 6-7 stall recoverable via workspace-deliverable transition; Step 10-11 stall recoverable via follow-up PR. Full un-ratification per §8.3a "Full un-ratification path" is available at any stage.

Intermediate states are **not persistent** and **not silent** — placeholder sentinels signal draft state; recovery paths are named. The attack succeeds at identifying real intermediate states; the runbook design bounds them.

**Verdict:** rejected as a blocker. Accepted as a known operational surface requiring the placeholder-sentinel discipline + named recovery paths. Both are documented in §8.3a and cross-referenced in the ratification package §6.

### 9.14 Attack: Freeze-integrity (added per Rigby F-E2)

**Claim:** the evidence manifest (Session 2715) §2.1 declares freeze semantics: *"Every source enumerated in §3-§14 is admissible for v0.1 authoring without further justification."* But the Session 2725 CD-47 correction pass modified the Playbook draft (specifically the citation of 15 rules) AFTER the manifest was frozen. Doesn't that violate freeze semantics?

**Attack:** either the manifest freeze is broken (Session 2725 edits post-date it), or the freeze semantic is under-specified (allows body edits but not source-enumeration edits) — in either case, "the manifest is frozen" is a weaker claim than the review presented.

**Refutation (per §8.3a):** the freeze operates on the **admissible-sources enumeration**, not on **derived draft text**. Specifically:

- Frozen: manifest §3-§14 enumeration of admissible sources for v0.1 authoring.
- Not frozen: the Playbook body itself, which is the product of drafting on top of admissible sources.
- Session 2725 substitutions swapped one already-admissible source (2715 subject to CD-48) for another already-admissible source (2711/2712/2714) in specific rule citations. The admissible-sources enumeration did not change. The Playbook body changed.

Under this reading, freeze-integrity is preserved. But Rigby's F-E2 correctly identified that this reading was not made explicit prior to §8.3a. Making it explicit is the correction; the freeze itself was never broken. CD-48 (the follow-on codification concern) captures the future case where an author might attempt to cite the manifest itself as evidence — that would be an implicit expansion of the admissible-sources set, which the freeze prohibits.

**Verdict:** rejected as a blocker. Accepted as a legitimate scope-clarification finding — the "freeze scope = sources, not derived draft" semantics MUST be surfaced explicitly in §8.3a (now done). Without §8.3a's clarification, the attack partially succeeds.

### 9.15 Attack: Runtime authority vs documentary authority mismatch (surfaced from F-B2 per Rigby F-E3)

**Claim:** the review claims the Playbook becomes "runtime policy" post-ratification (originally in §3.5 and §4.4). But the Playbook body is NOT in the `docs_context_builder.py` injection list (only three docs are: CLAUDE.md, SYSTEM_OWNER.md, canon/INDEX.md per PLAYBOOK-1.6.11). CLAUDE.md L7 anchor refresh updates human-protocol-authoritative pointer text, not runtime-authoritative injection scope. The review conflated documentary authority (repo_canonical + workspace-ratified) with runtime authority (guaranteed-in-context via injection).

**Attack:** if the review's runtime-authority claims are false, the transition-readiness verdict rests on an unverified mechanism.

**Refutation:** the attack SUCCEEDS against the original draft. The corrected §3.5 acknowledges: on ratification day, the Playbook is `repo_canonical` + workspace-ratified + RAG-retrievable via `content.Document` mirror + named-in-injected-canon via `canon/INDEX.md` — but NOT session-open-injected. Adding the Playbook body to the injection list is Cycle 2 hardening, not automatic. The v0.1 posture is: documentary authority yes; guaranteed-in-context runtime authority no. Cycle 2 candidate: explicit addition to `docs_context_builder.py` injection list with a corresponding MINOR amendment to PLAYBOOK-1.6.11.

**Verdict:** attack succeeded against the original draft; corrected §3.5 narrows the claim to what is demonstrated. Under the narrowed claim, no runtime-authority overclaim exists.

### 9.16 Attack: SYSTEM_OWNER hardcoding as structural coupling (surfaced from F-C3 per Rigby F-E3)

**Claim:** the review's §6.4 originally claimed Chris-dependence is "acknowledged simplification, not a new rule." But SYSTEM_OWNER.md hardcodes "Chris West" (line 19) as identity, is runtime-load-bearing (`docs_context_builder.py:184`), and Playbook PLAYBOOK-1.5.1 codifies the same identity as a rule. This is structural coupling (identity→authority), not narrative simplification.

**Attack:** if v0.1 implicitly claims portability or role-based-evolution readiness (which the original review §6 could be read as implying), the hardcoded identity coupling contradicts the claim. This qualifies as blocking under an implicit portability claim.

**Refutation:** the attack SUCCEEDS against the original framing. The corrected §6.4 accepts that this is structural coupling and narrows the v0.1 scope claim to **"single-owner, incumbent-named constitution"** — explicitly named as an intentional constraint, not a simplification. Under this narrowed scope, the coupling is consistent with the claim. Role/incumbent separation is a Cycle 3+ MAJOR-bump concern (CD-49 candidate).

**Verdict:** attack succeeded against the original draft; corrected §6.4 narrows the claim. Under the narrowed "single-owner, incumbent-named constitution" scope, no contradiction exists — but this scope MUST be declared explicitly in either the Session 2727 handoff or the workspace ratification record body.

### 9.17 Overall falsification tally (corrected)

- **16 attacks attempted** (12 original + 2 missing per F-E2 + 2 from F-E3).
- **12 rejected as v0.1 blockers** with defenses that hold under the narrowed-scope framing above.
- **2 accepted as controlled exceptions** (historical inconsistency §9.9; runtime authority §9.15 under the narrowed §3.5 posture).
- **2 accepted as blocking-until-explicit-declaration** (runtime authority §9.15 pre-correction; SYSTEM_OWNER hardcoding §9.16 pre-correction). Both are resolved by the corrections in §3.5 and §6.4 respectively — provided the declarations are surfaced in Session 2727 handoff / ratification record body.
- **4 accepted as Cycle 2+ / Cycle 3+ evolution vectors** (missing constitutional layer §9.3; Canon Registry partition §9.5; L0 role/incumbent separation §9.16 / §6.5 item #1; CD-48 codification §9.12 / §5.6).

### 9.18 Defense-quality note (per Rigby F-E4)

Rigby's F-E4 flagged the original §9 defenses as "plausible rebuttals" without deep evidence work. The corrections in §9.1, §9.5, §9.9, §9.13, §9.14, §9.15, §9.16 tighten defenses by:

- Naming concrete enforcement points (`docs_context_builder.py:177,184,186`; `_canonical_authority_helpers.py:33-60`; `verify_repo_guardrails.py`).
- Naming concrete recovery paths (placeholder sentinels, two-commit pattern, un-ratification channel).
- Distinguishing overclaims (original) from narrowed claims (corrected).
- Making conditions on rejections explicit (§9.5 requires two v0.1 commitments; §9.9 requires era-labeling frontmatter).
- Reclassifying non-rejections as controlled exceptions (§9.9).

The falsification defense is now backed by specific mechanisms and recovery paths, not asserted mechanisms.

### 9.19 Why every attack ultimately survives without blocking v0.1

The common defense across attacks (post-correction):

- **The architecture is complete enough for v0.1 scope, provided the scope is stated at the narrowed form.** The original draft claimed broader scope than the artifacts support; the corrections narrow to what is demonstrated.
- **Every accepted future concern has a documented amendment path** — PATCH, MINOR, MAJOR — with clear semver semantics.
- **Historical drift is bounded and acknowledged** as controlled exception with era-labeling requirement.
- **Self-reference paradoxes have empirical resolutions** — SIGN discipline + two-commit pattern + emergency amendments + placeholder sentinels handle the theoretical corners.
- **Runtime authority and documentary authority are distinguished** — the Playbook is documentary v0.1; runtime injection is Cycle 2.

The architecture is a **compact, correctly-scoped, evolvable v0.1**. Not perfect. Not eternal. Correct for its scope as now explicitly declared, with named growth paths.

### 9.21 Verdict — Section 9 (post-correction)

The architecture survives falsification **under the narrowed-scope framing established in the corrections above.** Ratifying v0.1 is defensible against every attack in the review, provided:

- The Playbook's runtime status is described as "documentary + RAG-retrievable + named-in-injected-canon" (§3.5 corrected) rather than "runtime policy."
- v0.1 is explicitly declared "single-owner, incumbent-named constitution" (§6.4 corrected).
- CD-48 is targeted for v0.1.1 PATCH with the F-C1(a)+(b) codification form (§5.6 corrected).
- Historical inconsistency is labeled controlled exception with era-labeling requirement (§9.9 corrected).
- Placeholder-sentinel + two-commit pattern is exercised at ratification (§8.3a + §9.13 corrected).

Under any broader claim, the corresponding attack would surface as blocking. The transition is defensible at the narrowed scope; not at the broader scope originally drafted.

---

## Section 10 — Explicit Answers to the 10 Mission Questions

### Q1. Is the Architecture Research phase complete?

**YES**, in the specific sense that the six-artifact research chain (2708-2714) plus the frozen manifest (2715) plus the 6 authoring sessions (2716-2721) plus the 4 audit/correction sessions (2722-2725) plus the ratification package (2726) constitute a complete evidence base sufficient for v0.1 ratification. No further architectural questions block v0.1.

**Deferred (not "incomplete"):** L1 Fleet activation (Cycle 4+), L3 Tenant activation (Cycle 3+), enum expansion (Cycle 3+), Research OS absorption (Cycle 3+), full `docs/` subdirectory audit (Cycle 2), CD-48 codification (v0.1.1 PATCH).

### Q2. Is the constitutional architecture complete?

**YES**, for L2 Platform scope at the current single-app, single-ratifier configuration. The six-layer stack (L1-L6) is proven sufficient for today; Cycle 3+ activation of L1/L3 is architecturally supported via documented enum expansion and reserved chapter slots.

**"Complete" is meaningful; "eternal" is not.** The architecture is complete for v0.1's ambit — Chapters 0/1/6/10 FULL, Chapters 2/3/4/5/7/8/9 STUB (per 2712 §16.9 minimum viable chapter set). STUBs become FULL through MINOR amendments as evidence accumulates.

### Q3. Is any architectural work still required?

**NOT for v0.1 ratification.** Required future work:

- **Cycle 2 hardening** — content_hash population, ORM immutability signals, CI validation of `deliverable_type`, automated Canon Registry update, runtime-load-bearing docs registry (per 2712 §17 + ecosystem §14.1).
- **Chapter conversions** — STUBs to FULLs via MINOR amendments as evidence accumulates.
- **CD-48 codification** — v0.1.1 PATCH.
- **Cycle 3+ evolution** — enum expansion, delegation model, org-layer.

None blocks v0.1.

### Q4. Is any research still required?

**NOT for v0.1 ratification.** Required future research:

- **Empirical discovery** — new patterns will emerge through session work; they will land as MEMORY.md rules → SIGN evidence → Playbook amendments per the pipeline in Section 7.5.
- **Cycle 2 hardening research arcs** — how to automate content_hash, how to codify ORM immutability, etc.
- **Cycle 3+ activation research arcs** — tenant-scope, fleet-scope activation planning.

Research and amendment are pipeline stages, not competitors. Post-v0.1, research continues; it feeds amendment.

### Q5. What constitutional artifacts should never again be created through research?

**Constitutional artifacts that SHOULD go through Playbook amendment instead of research:**

- **Statement class definitions** (governed by Chapter 6).
- **Evidence class definitions** (governed by Chapter 6 + 2712 §11).
- **Frontmatter schema fields** (governed by 2712 §5.1; MINOR for additions, MAJOR for changes).
- **Rule identifiers** (governed by Chapter 6 identifier discipline).
- **Ratification workflow** (governed by Chapter 10 + 2712 §8).
- **PATCH/MINOR/MAJOR semver semantics** (governed by 2712 §7).
- **Amendment procedures** (governed by Chapter 10).
- **Session-open/session-close discipline** (governed by Chapter 7 once STUB→FULL).

**Constitutional artifacts that STILL originate through research:**

- **Empirical patterns from operational sessions** (originate as MEMORY.md rules → E6 handoff evidence → research synthesis → amendment).
- **Cycle 2+ hardening design** (research arc → amendment).
- **New scope activation** (tenant, fleet, org — research → amendment).
- **Recovery playbooks** (originate as incident sessions → E6 evidence → Chapter 9 [RC] rule via MINOR amendment).

### Q6. What becomes the authoritative path for future constitutional change?

**Chapter 10 amendment cycle**:

1. Propose (research arc if needed; direct proposal if evidence exists).
2. Author (draft rule text + evidence citations).
3. SIGN (Rigby default; Claude verifier-loop fallback).
4. Correct (if BLOCKING findings).
5. Ratify (Chris directive verbatim; PublishGate transition).
6. Mirror (workspace deliverable → `content.Document` mirror per KFI-1).
7. Post-ratification frontmatter follow-up commit.
8. Tag (`playbook-vX.Y.Z`).
9. Cascade (4-step + embed + provenance).
10. Anchor refresh (CLAUDE.md L7; `docs/INDEX.md`; `00-START-NEXT-SESSION.md`).

Emergency amendments bypass steps 3-4 with explicit Chris directive per 2712 §9.6 (rare; documented per-use).

### Q7. Is the Engineering Playbook ready to become the governing constitutional document?

**Conditional YES** — subject to Chris's Option A directive (NOT Option D) AND surfacing of the five explicit posture declarations enumerated in §9.21.

- **165 rules, 11 chapters, 4 FULL + 7 STUB per 2712 §16.9.**
- **0 unresolved F-BLOCKING findings on the Playbook body itself.**
- **CD-47 RESOLVED** (15/15 Rigby PASS on fresh SIGN pin `pa-275e12fb72de4b3e`).
- **CD-48 recorded, non-blocking conditional on v0.1.1 PATCH commitment per §5.6 corrected**.
- **Cumulative 70/70 sampled rules verified PASS across Sessions 2724 + 2725**.
- **Ratification package complete** (Session 2726 output; 14-step runbook).
- **Session 2727 CORRECTION-PASS applied to this transition review** (not to the Playbook). Rigby SIGN produced 1 conditional blocker + 5 must-address findings on the transition review; all resolved via review-side narrowing rather than Playbook change. The Playbook body was verified not to overclaim; the review had overclaimed. Corrections narrow the review to what is demonstrated.

The Playbook is **not** the supreme constitutional document — SYSTEM_OWNER.md remains L0. The Playbook is L2 methodology codification, ratified via workspace envelope, joining the existing constitutional ecosystem. It becomes governing for methodology change; it does not become supreme over Chris's Absolute Override. It becomes documentary-canonical + workspace-ratified + RAG-retrievable on ratification; it does NOT automatically become session-open-injected (that is Cycle 2 hardening).

### Q8. What officially ends when the Playbook is ratified?

- **The Architecture Research phase.** Sessions 2708-2726 formally close as the evidence chain backing v0.1. Future work is Cycle 2+ engineering + amendment cycles.
- **The informal methodology era.** Chapter 10 becomes the authoritative amendment path. "Change the rule by directive" becomes an emergency mechanism rather than the default.
- **The "one more research arc" instinct for methodology changes.** New methodology proposals route to Chapter 10 amendment.
- **The evidence manifest as an active authoring instrument.** The v0.1 manifest freezes as historical evidence. v0.2 will freeze its own manifest.
- **The 19-untracked-research-file state.** Per package §6, these artifacts get committed with the Playbook or cascaded into canon per Chris directive.

### Q9. What officially begins?

- **The Engineering Playbook era.** Methodology codified, versioned, evidence-cited, machine-parseable.
- **Cycle 2 planning.** The first activity of the new era; targets Cycle 2 hardening (per 2712 §17 + ecosystem §14.1).
- **Amendment discipline as first-class governance.** Chapter 10 governs how future methodology changes land.
- **Constitutional debt tracking as first-class category.** CD-48 targeted for v0.1.1; CD-49+ candidates queued from this review's §6.5 codification queue.
- **Rule-by-ID discourse.** Future sessions, PRs, and handoffs cite `PLAYBOOK-N.M.K` when referring to methodology.
- **Playbook-versioned ratification records.** Every future ratification record cites the Playbook version under which it was ratified.

### Q10. Should the platform formally declare the Architecture Research era complete?

**YES.**

The declaration is not ceremonial — it is a load-bearing statement of governance boundary. The declaration should be embedded in:

1. **The workspace ratification record** (`RATIFICATION_20260708_PLAYBOOK_v0_1_0`) §1 Identity block OR §8 Cascade Authorization — a specific sentence: *"With this ratification, the Architecture Research phase (Sessions 2708-2726) is declared complete. The Playbook is the authoritative path for future methodology change."*
2. **The Session 2727 handoff** (`SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md`) §1 Executive Summary — a similar declaration linked to the ratification record.
3. **The 00-START-NEXT-SESSION.md rewrite** — moves the current "READY FOR RATIFICATION" block to a "PLAYBOOK v0.1.0 RATIFIED — CYCLE 2 PLANNING BEGINS" block.
4. **CLAUDE.md L7 anchor refresh** — replaces the Cycle 1A workspace-ADR pointer with a Playbook v0.1.0 pointer.

The declaration is symbolic AND operational: it tells future sessions where to look, and it tells future methodology authors which path to walk.

---

## Final Answer to the Success-Criteria Question (post-CORRECTION-PASS)

> **"Are we merely ready to ratify a document... or are we ready to transition into operating under a constitutional engineering system?"**

**We are ready to transition into operating under a constitutional engineering system — provided the transition is understood at the correctly narrowed scope stated in §9.21.**

The transition review as originally drafted overclaimed on runtime authority, on Chris-dependence framing, on CD-48 disposition, on falsification defense-quality, and on ratification irreversibility. Rigby's independent adversarial SIGN across 6 batches identified 1 conditional blocker + 5 must-address findings. Per System Owner directive, every finding was accepted as valid; the review — not the Playbook — was the correction target. All corrections narrow the review's claims to what the Playbook body actually demonstrates. The Playbook body itself was verified to correctly assert only what it demonstrates; no Playbook change is required.

**Ratifying `docs/ENGINEERING_PLAYBOOK.md` at v0.1.0 is the mechanical act.** The transition is what happens next: **where future methodology change originates, how it lands, who ratifies it, how it cascades to runtime.** Each of those questions has a defensible, evidence-backed answer as of Session 2726 and Session 2727's correction pass.

The Playbook v0.1.0 is a compact, **correctly-scoped**, evolvable constitutional codification with:

- 4 FULL chapters (0, 1, 6, 10) covering the minimum viable constitutional surface.
- 7 STUB chapters (2, 3, 4, 5, 7, 8, 9) with defined MINOR-amendment paths.
- 1 known non-blocking constitutional debt item (CD-48) with defined PATCH-form constraints and required-first-amendment-cycle commitment.
- 1 candidate constitutional debt item (CD-49) named this session: L0 authority role/incumbent separation, Cycle 3+ MAJOR-bump concern.
- 16 falsification attacks (12 original + 2 F-E2 missing + 2 F-E3 surfaced) with defenses backed by concrete enforcement points and recovery paths per §9.18.
- A complete 14-step ratification runbook (package §6) with placeholder-sentinel + two-commit pattern discipline for intermediate-state coherence.
- Integration with the pre-existing constitutional ecosystem (~25+ peer/governs-methodology/executable artifacts named in §2, including Governor/PriorityRouter surface added per F-A3).

**What we are NOT claiming (explicit post-correction):**

- We are NOT claiming the Playbook becomes runtime-injected on ratification day (§3.5 corrected: it is documentary + RAG-retrievable + named-in-injected-canon; runtime injection is Cycle 2 hardening).
- We are NOT claiming the constitution is portable or role-based on v0.1 (§6.4 corrected: v0.1 is explicitly single-owner, incumbent-named).
- We are NOT claiming CD-48 is optional to codify (§5.6 corrected: v0.1.1 PATCH commitment is required; Option D permanent waiver is not compatible with the non-blocking finding).
- We are NOT claiming pre-Playbook artifacts (952 handoffs, 4 repo ADRs, 5+ workspace ADRs, IOS + Research OS) will be retroactively conformed (§9.9 corrected: controlled exception with era-labeling requirement).
- We are NOT claiming ratification is irreversible (§8.5 corrected: reversal via System Owner Override + MAJOR supersession + errata amendment; reversal channel named).
- We are NOT claiming the transition is instantaneous or atomic (§8.3a added: 14-step runbook with placeholder sentinels + named recovery paths for intermediate states).

**What we ARE claiming (post-correction):**

- The architecture is complete for the v0.1 scope **as now explicitly declared** (single-owner, incumbent-named, documentary-canonical + workspace-ratified + RAG-retrievable — not runtime-injected).
- The transition is real, one-way-in-default-workflow, bounded-in-operational-scope-but-high-leverage-in-runtime-context-surfaces, and reversible via named channels.
- The Playbook body itself does not overclaim; the review had overclaimed and is now corrected.
- Every known blocker on the Playbook body (CD-47) is resolved.
- Every known non-blocker (CD-48; CD-49 candidate; L5-hosts-L2 anomaly; Canon Registry staleness; unenumerated `docs/` subdirectories) is documented with a defined resolution path.
- The falsification defense is backed by specific enforcement points and recovery paths (§9.18) — no longer "plausible rebuttals only."

**Required declarations for the ratification to hold at the narrowed scope:**

Per §9.21 (surfaced in the Session 2727 handoff and/or the workspace ratification record body — recommended: both):

1. Playbook v0.1 runtime status = documentary + RAG-retrievable + named-in-injected-canon; NOT session-open-injected. Adding the Playbook body to the injection list is Cycle 2 hardening candidate.
2. Playbook v0.1 is a **single-owner, incumbent-named constitution.** Role/incumbent separation is Cycle 3+ MAJOR-bump concern (CD-49 candidate).
3. CD-48 codification is targeted for the first amendment cycle (v0.1.1 PATCH) as an explicit citation-admission rule of the form named in §5.6.
4. Historical pre-v0.1 artifacts are **controlled exceptions** with era-labeling requirement for future artifacts.
5. Ratification uses the **placeholder-sentinel + two-commit pattern** with named recovery paths for intermediate states (§8.3a).

**Recommendation to the System Owner (post-correction):**

- **Option A** (write `docs/ENGINEERING_PLAYBOOK.md`; proceed with §6 runbook step-by-step with Chris directive at each gate) is the recommended path — under the five posture declarations above.
- **Option D** (waive CD-48 permanently) is **incompatible** with the non-blocking status per §5.6 corrected; not recommended.
- **Option E** (abandon) is not defensible given the audit history.
- **Options B (defer) and C (address CD-48 first)** are valid choices at Chris's discretion; the review does not gate them. Option C would fold CD-48 codification into v0.1 itself, closing the F-C1+F-C2 conditional-blocker path entirely.

**Blocker status (post-correction):** **ZERO Playbook-side blockers.** The review-side blocker (F-C4 runtime authority overclaim) is resolved by the §3.5 correction. Remaining posture declarations are governance acts to be executed in the Session 2727 handoff / ratification record body.

**Awaiting System Owner review of this corrected review and directive on Option A / B / C / D / E.**

---

## Non-Actions Taken by This Review

Per mission constraint, this review performed NONE of the following:

- Did NOT modify `docs/ENGINEERING_PLAYBOOK.md` (does not exist).
- Did NOT modify Canon Registry (`docs/canon/INDEX.md`).
- Did NOT modify workspace artifacts.
- Did NOT modify ADRs.
- Did NOT modify ratification records.
- Did NOT begin ratification.
- Did NOT create workspace deliverables.
- Did NOT create session handoffs.
- Did NOT modify the ratification package or Playbook body drafts.
- Did NOT modify any of the 19 untracked research artifacts in `docs/research/platform/`.
- Did NOT modify CLAUDE.md, MEMORY.md, or `00-START-NEXT-SESSION.md`.
- Did NOT run the docs cascade.

**Only artifact produced this session:** `docs/research/platform/platform_constitutional_transition_review.md` (this document).

**STOP state:** review complete. Awaiting System Owner review of this report.

---

## Rigby SIGN Findings Appendix

**Fresh SIGN pin:** `pa-e78b9f0a31294af4` (title: `session-2727-constitutional-transition-sign`; isolated from all prior Session 2722-2726 Playbook SIGN context).

**Dispatch:** 6 batches (A-F) covering all 10 review sections + Executive Verdict + Final Answer. Each batch presented review claims + specific SIGN questions.

**Verdict:** CORRECTION-PASS.

### Findings inventory (all accepted per System Owner directive)

| ID | Section | Finding | Correction location in this document |
|---|---|---|---|
| F-A1 | §1 | Provisional inventory sufficient only if paired with boundary rule + RAG-ingest risk note | §1.2 (boundary rule + risk note added) |
| F-A2 | §2 | Research OS / IOS should be "Governed-by for methodology / Peer for scope," not flat PEER | §2.1 taxonomy row rewrite + §2.2 summary count |
| F-A3 | §2 | Missing artifact — Governor / active-priority / autonomy control surface (`governor_tool`, `active_priority_tool`, `priority_router.py`, migration 0329) | §2.1 taxonomy row added (verified in code) |
| F-B1 | §3 | KFI canonical-authority code is GOVERNING (runtime adjudicator), not runtime-policy peer | §3.5 corrected + adjudication paragraph added |
| F-B2 | §3 | CLAUDE.md anchor refresh is human-protocol authoritative, NOT runtime authoritative | §3.5 corrected (Mechanism 3 named as pointer, not injection) |
| F-B3 | §4 | Discipline-externalization tension → "rule-first, override-explicit" (discretion preserved but logged) | §4.6 corrected |
| F-B4 | §4 / §8 | "Irreversible in intent" overclaims — name reversal channel + evidentiary burden | §8.5 rewrite (Property 1); Executive Verdict "Reversal channel" |
| F-C1 | §5 | CD-48 PATCH viable only as non-expansive clarification (citation-admission rule + guaranteed-in-context) | §5.6 corrected |
| F-C2 | §5 | Non-blocking status acceptable ONLY IF paired with required-first-amendment commitment | §5.6 corrected (required v0.1.1 PATCH commitment; Option D excluded) |
| F-C3 | §6 | Chris hardcoded in runtime-load-bearing canon = structural coupling, not narrative simplification | §6.4 corrected; §6.6 corrected; §9.16 added as successful attack |
| F-C4 | §3/§8 (BLOCKER) | Runtime-authority claims made while Ch8 is STUB + no guaranteed runtime injection path | §3.5 rewrite (blocker resolved via review-side narrowing) |
| F-D1 | §7 | Pipeline needs "inadmissible research output" vs "informative but non-evidence" distinction | §7.7a added (recorded as v0.1.1 PATCH or v0.2 MINOR candidate) |
| F-D2 | §7 | Missing bypass class — CI/workflow guardrail changes | §7.6 extended with CI/tooling gate |
| F-D3 | §8 | Behavioral change on ratification day = namespace shift to PLAYBOOK-N.M.K IDs (immediate, even for STUB chapters) | §8.5 Property 4 added |
| F-D4 | §8 | "Bounded" underspecified → "bounded but high-leverage" with failure modes + rollback | §8.5 Property 3 corrected + §8.3a added |
| F-E1 | §9 | 3 underpowered rejections (§9.1 bootstrap ceremony; §9.5 not a rejection; §9.9 grandfathering) | §9.1, §9.5, §9.9 rewritten |
| F-E2 | §9 | 2 missing attacks (timing/ordering race; freeze-integrity) | §9.13 + §9.14 added |
| F-E3 | §9 | A-D findings not surfaced as successful attacks | §9.15 (runtime authority) + §9.16 (SYSTEM_OWNER hardcoding) added |
| F-E4 | §9 | Defense-quality is "plausible rebuttal" not "deep evidence work" | §9.18 defense-quality note; concrete enforcement points named throughout §9 |

### Playbook body audit result

Per System Owner directive, the Playbook body was audited to determine whether any Rigby finding required Playbook change rather than review change. Findings:

- **No Rigby finding requires Playbook change.** Every finding resolves as a review-side narrowing of scope claims.
- **PLAYBOOK-1.5.1** codifies "Chris West" as System Owner — this is structural coupling in the Playbook body itself, but the finding (F-C3) asks the review to correctly characterize this as an intentional constraint, not to change the Playbook rule.
- **PLAYBOOK-1.6.11** correctly lists exactly 3 documents as session-open runtime-injected (CLAUDE.md, SYSTEM_OWNER.md, canon/INDEX.md). The Playbook does NOT claim to be in this list. The review overclaimed; the Playbook did not.
- **Chapter 8 STUB** (PLAYBOOK-8.1.1..8.3.1) correctly defers runtime-discipline authoring to a future MINOR amendment; explicitly references the Constitutional Ecosystem Inventory §5 as the authoritative enumeration. The Playbook does NOT overclaim runtime authority. The review overclaimed; the Playbook did not.
- **PLAYBOOK-1.4.3..1.4.8** correctly describe the `canonical_authority` derivation as the runtime discipline enforced by `_canonical_authority_helpers.py`. This is consistent with F-B1's "code adjudicates doc claims" framing.

### Verification pass

A fresh Rigby SIGN pin will be minted for verification-only review of these corrections. Verification pass will confirm each of the 19 findings is resolved by the corrections in this document.

---

**END SESSION 2727 CONSTITUTIONAL TRANSITION REVIEW (POST-CORRECTION).**

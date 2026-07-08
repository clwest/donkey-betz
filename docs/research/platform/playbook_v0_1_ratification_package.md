# Engineering Playbook v0.1 — Ratification Package (Session 2726)

**Session:** 2726
**Date:** 2026-07-08
**Role executed:** Constitutional Custodian / Editor-in-Chief
**Predecessor sessions:** 2708-2714 (research chain) → 2715 (evidence manifest frozen) → 2716-2721 (authoring) → 2722 (Rigby first SIGN) → 2723 (correction pass) → 2724 (final verification, CD-47 recorded) → 2725 (compliance correction, CD-47 RESOLVED, CD-48 recorded)
**Repository HEAD at package authoring:** `309f85eee4dae5cedb022a393d06a19882ccf62f` (main branch, clean tree; 18 untracked Cycle-1A-follow-on research files)
**Rigby SIGN pin currently active for v0.1 verification history:** `pa-275e12fb72de4b3e` (Session 2725, title: `session-2725-correction-verify`)

**Readiness verdict:** **READY FOR RATIFICATION.**

---

## 1. Final Corrected Playbook Body — Assembly Confirmation

### 1.1 Composition source

The final corrected Playbook v0.1 body is the logical composition of:

1. **Session 2723 corrected body** — `docs/research/platform/playbook_v0_1_body_corrected.md` (SHA-256 `7de3c8af158226ed1e26aa9d0cbd18f447cf567d9ee491f940eea6f8e86dc78d`) applied over the raw drafts from Sessions 2716, 2718, 2719, 2720, 2721.
2. **Session 2725 citation corrections** — 15 rules with citations substituted per `docs/research/platform/playbook_constitutional_correction_session_2725.md` §3 (SHA-256 `e1d8f3d06d6bdcfdc7b8d206ee01aa27e5b713048adaedb62d1665d8b72f7232`).

The physical single-file assembly (`docs/ENGINEERING_PLAYBOOK.md`) has NOT yet been written. Its content_hash cannot be computed until it is written. Both hashes above are for the working-composition inputs, not the final ratifiable artifact.

### 1.2 Final rule count

**165 rules** distributed across 11 chapters (Chapters 0-10), verified from Session 2721 §5.1 (rule identifier uniqueness pass):

| Chapter | Title | Rule ID range | Rules | Authoring status |
|---|---|---|---|---|
| 0 | Preamble and How to Read This Playbook | PLAYBOOK-0.3.1 through PLAYBOOK-0.6.1 | 8 | FULL |
| 1 | Constitutional Context | PLAYBOOK-1.1.1 through PLAYBOOK-1.10.3 | 29 | FULL |
| 2 | Research Methodology | PLAYBOOK-2.1.1 through PLAYBOOK-2.3.1 | 3 | STUB |
| 3 | Implementation Discipline | PLAYBOOK-3.1.1 through PLAYBOOK-3.3.1 | 3 | STUB |
| 4 | Documentation Cascade | PLAYBOOK-4.1.1 through PLAYBOOK-4.3.1 | 3 | STUB |
| 5 | PA / Rigby Collaboration | PLAYBOOK-5.1.1 through PLAYBOOK-5.3.1 | 3 | STUB |
| 6 | Provenance Classification Standard (PIC-10) | PLAYBOOK-6.1.1 through PLAYBOOK-6.10.4 | 57 | FULL |
| 7 | Session Discipline | PLAYBOOK-7.1.1 through PLAYBOOK-7.3.1 | 3 | STUB |
| 8 | Runtime Discipline | PLAYBOOK-8.1.1 through PLAYBOOK-8.3.1 | 3 | STUB |
| 9 | Recovery & Incident Playbooks | PLAYBOOK-9.1.1 through PLAYBOOK-9.2.1 | 2 | STUB |
| 10 | Evolution and Amendment | PLAYBOOK-10.1.1 through PLAYBOOK-10.13.4 | 51 | FULL |

Total: 8 + 29 + 3 + 3 + 3 + 3 + 57 + 3 + 3 + 2 + 51 = **165 rules**.

FULL chapters: 4 (0, 1, 6, 10) per manifest §16.9 (2712) minimum viable chapter set.
STUB chapters: 7 (2, 3, 4, 5, 7, 8, 9) per 2712 §16.9 stub-authorization.

### 1.3 No unresolved F-BLOCKING findings remain

- **Session 2722** — 4 F-BLOCKING findings + 1 verdict CORRECTION-PASS → all 4 resolved by Session 2723 (63 corrections applied).
- **Session 2724** — 15 F-BLOCKING findings (CD-47) → all 15 resolved by Session 2725 (targeted citation substitutions; Rigby verified 15/15 PASS).
- **Session 2725** — 0 F-BLOCKING findings observed on the corrected draft. Rigby overall Q3 verbatim: *"No additional issues observed... no further correction pass is required."*

### 1.4 CD-48 confirmed non-blocking

CD-48 records the previously-uncodified constitutional principle *"a document that describes/catalogs a constitutional evidence chain is not automatically a member of that chain."* Per Session 2725 §9.1:

- Principle is already **implicit** in manifest §2.1 (freeze semantics), §2.3 (explicit 2708-2714 range), and 2713 §7.2 (convergent-research definition).
- Suggested remediation is a **v0.1.1 PATCH or v0.2 MINOR amendment** adding an explanatory note in Chapter 6 or Chapter 10.
- CD-48 does **NOT** block v0.1 ratification because Session 2725's mission scope (Chris-authored) explicitly excluded new policy additions.

### 1.5 Assembly-confirmation verdict

**All body-integrity preconditions for ratification are met.** The final corrected Playbook body — as the logical composition of Session 2723 body + Session 2725 citation corrections — carries:

- 165 unique rule identifiers
- 0 unresolved F-BLOCKING findings
- 1 non-blocking constitutional-debt item (CD-48) documented
- Rigby-verified [EP]/[AC]/[GR]/[RS]/[DR]/[IP]/[RP]/[RC]/[OR] threshold satisfaction on all 70 sample-verified rules (55 PASS from Session 2724 + 15 PASS from Session 2725)

---

## 2. Ratification Package

### 2.1 Package identity

| Field | Value |
|-------|-------|
| Artifact | Donkey Betz Engineering Playbook v0.1.0 |
| Scope | platform (L2) |
| Version | 0.1.0 (semver MAJOR.MINOR.PATCH per 2712 §7) |
| version_status target | `ratified` |
| parent_version | `null` (inaugural v0.1) |
| supersedes | `[]` (no prior version) |
| Ratifier | `chris` (UnifiedUser.username) |
| ratified_date | TBD at ratification-directive moment |
| Repository path | `docs/ENGINEERING_PLAYBOOK.md` |
| Canonical authority | `repo_canonical` (per KFI-2 B3 derivation; explicit per 2712 §5.1 field rationale) |
| Ratification workspace | `a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture & Research) |
| Ratification record title | `RATIFICATION_20260708_PLAYBOOK_v0_1_0` (or `_20260709_` if crossing midnight UTC) |

### 2.2 Content hash requirement

Field: `content_hash` in the Playbook frontmatter, SHA-256 of the file body **excluding frontmatter**.

Computation timing per 2712 §5.1 and §15.1: content_hash is populated in the **post-ratification frontmatter follow-up commit**, NOT the ratification commit itself. This is because the ratification commit's own hash is embedded in the frontmatter (`commit_sha`), so `content_hash` is stamped after the file is stable at its ratified commit.

Post-ratification steps (per §6 runbook below):

```bash
awk '/^---$/{c++; next} c>=2{print}' docs/ENGINEERING_PLAYBOOK.md \
  | shasum -a 256 \
  | awk '{print "sha256:" $1}'
```

Working-composition hashes (NOT final content_hash — these are input references only):
- Session 2723 corrected body draft: `sha256:7de3c8af158226ed1e26aa9d0cbd18f447cf567d9ee491f940eea6f8e86dc78d`
- Session 2725 correction session report: `sha256:e1d8f3d06d6bdcfdc7b8d206ee01aa27e5b713048adaedb62d1665d8b72f7232`
- Frozen evidence manifest (2715): `sha256:198a4d87f0410330101402de1c1c3ef513edda5ebd581074f103deaa94c3ca2b`

### 2.3 Rule count

**165 rules** (see §1.2 breakdown).

### 2.4 Chapter list

11 chapters (Chapters 0-10):
- Chapter 0 — Preamble and How to Read This Playbook (FULL)
- Chapter 1 — Constitutional Context (FULL)
- Chapter 2 — Research Methodology (STUB)
- Chapter 3 — Implementation Discipline (STUB)
- Chapter 4 — Documentation Cascade (STUB)
- Chapter 5 — PA / Rigby Collaboration (STUB)
- Chapter 6 — Provenance Classification Standard (PIC-10) (FULL)
- Chapter 7 — Session Discipline (STUB)
- Chapter 8 — Runtime Discipline (STUB)
- Chapter 9 — Recovery & Incident Playbooks (STUB)
- Chapter 10 — Evolution and Amendment (FULL)

### 2.5 Evidence manifest reference

**Frozen manifest:** `docs/research/platform/engineering_playbook_evidence_manifest.md` (Session 2715 output).

Sole authoritative source for admissible v0.1 citation sources per manifest §2.1 (freeze semantics). Any source enumerated in manifest §3-§14 is admissible without further justification; any source not enumerated requires a formal manifest amendment before citation.

Convergent-research exception (manifest §2.3): the 2708-2714 chain constitutes convergent research. Per-class threshold matrix in manifest §2.2 is authoritative for Playbook body evidence-threshold checking.

### 2.6 Rigby audit history

| Session | Pin | Role | Verdict | Findings |
|---------|-----|------|---------|----------|
| 2722 | `pa-668ef2284ab44928` (later retired) | First Constitutional SIGN Audit | CORRECTION-PASS | 4 F-BLOCKING findings (multi-keyword-per-sentence, misclassifications, threshold shortfalls) |
| 2723 | `pa-1faea7e0243c4efd` (later retired) | Correction-pass re-audit (partial excerpt scope) | READY-FOR-RATIFICATION (excerpt scope caveat) | Original 4 F-BLOCKING findings resolved; excerpt scope did not cover all rules |
| 2724 | `pa-87b702a436a849d3` (retired 2026-07-08 Session 2725 open, 16 rows updated, `force=true`) | Final Independent Constitutional Verification | NOT-READY (CD-47) | 15 F-BLOCKING [EP] threshold defects on 55/70 verified PASS baseline |
| 2725 | `pa-275e12fb72de4b3e` (currently active) | Targeted correction-verify pass | READY (verbatim Q1/Q2 YES) | 15/15 corrected rules PASS on fresh pin; Q3 no additional issues |

**Cumulative Rigby-verified PASS on distinct rules across the audit history:** 70/70 sampled rules verified PASS after Session 2725.

### 2.7 Correction history

| Session | Purpose | Scope | Correction count |
|---------|---------|-------|------------------|
| 2723 | Constitutional correction pass responding to Session 2722 F-BLOCKING findings | 63 rules touched | 63 corrections applied (TC-1 through TC-5 taxonomy) |
| 2725 | Constitutional compliance correction responding to Session 2724 CD-47 | 15 rules touched (citations only; no wording changes) | 15 citation corrections applied (2715 → 2711/2712/2714 chain members) |

**Total rules touched by correction discipline across 2723 + 2725: 78** (63 + 15). No overlap — the 15 Session 2725 corrections are on 15 of the 63 rules Session 2723 touched (revised citations only).

### 2.8 CD-47 resolution

- **Origin:** Session 2724 §7.1
- **Nature:** 15 F-BLOCKING [EP] threshold defects
- **Resolution session:** 2725
- **Resolution mechanism:** citation substitution per Session 2725 §3 correction table
- **Verification:** Rigby 15/15 PASS on fresh pin `pa-275e12fb72de4b3e`
- **Status at ratification-package time:** **RESOLVED — non-blocking.**

### 2.9 CD-48 non-blocking debt note

- **Origin:** Session 2725 §9.1
- **Nature:** previously-uncodified constitutional principle
- **Statement:** *A document that describes or catalogs a constitutional evidence chain is not, by virtue of that catalog role, a member of the chain it describes. The evidence manifest admits sources to the constitutional corpus; it does not admit itself.*
- **Blocking for v0.1 ratification:** **NO** — v0.1 mission scope excluded new policy additions; principle is recorded for consideration during v0.1.1 PATCH or v0.2 MINOR amendment.
- **Suggested remediation:** small explanatory note in Chapter 6 (Provenance Classification Standard) or Chapter 10 (Evolution and Amendment) formally stating the boundary. Deferred.

### 2.10 Recommended ratification language (for System Owner directive)

The following verbatim language is recommended for Chris's ratification directive. It is written to satisfy the manifest's `[GR]` ratification requirements (E1|E2 + E6) and to be quotable in the workspace ratification record's `ratification_directive` field:

> **RATIFICATION DIRECTIVE — Donkey Betz Engineering Playbook v0.1.0**
>
> As System Owner, I ratify the Engineering Playbook v0.1.0 at commit `<40-char SHA>`, content_hash `sha256:<hash>`, git tag `playbook-v0.1.0`.
>
> This ratification carries these findings:
> - The Playbook body is repo-canonical at `docs/ENGINEERING_PLAYBOOK.md` per KFI-2 B3 derivation.
> - The ratification envelope is workspace-canonical at deliverable `<ratification-record-deliverable-id>` in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`.
> - The frozen evidence manifest (Session 2715, `docs/research/platform/engineering_playbook_evidence_manifest.md`) is the sole authoritative source for admissible v0.1 citations. Amendments to the manifest require formal manifest-amendment discipline per 2713 §11.
> - Constitutional debt CD-47 (fifteen [EP] threshold defects surfaced in Session 2724) is RESOLVED via the targeted correction pass in Session 2725; Rigby-verified 15/15 PASS on fresh SIGN pin `pa-275e12fb72de4b3e`.
> - Constitutional debt CD-48 (uncodified principle that an evidence-chain catalog is not automatically a member of the chain it describes) is recorded as non-blocking for v0.1; deferred to v0.1.1 or v0.2.
> - 165 rules across 11 chapters (Chapters 0-10); 4 chapters FULL (0, 1, 6, 10); 7 chapters STUB (2, 3, 4, 5, 7, 8, 9) per 2712 §16.9 stub-authorization.
>
> Post-ratification cascade authorized per §DOC_LIFECYCLE.md and the workspace canon-promotion policy.
>
> — Chris, `chris@donkeybetz.com`, 2026-07-XX

---

## 3. Repo Placement Plan

### 3.1 Target file

**Path:** `docs/ENGINEERING_PLAYBOOK.md` (repo-canonical; per Playbook frontmatter `repository_path` field).

### 3.2 Write timing (before/after workspace ratification?)

**Recommendation: WRITE FILE FIRST, RATIFY WORKSPACE SECOND, POST-RATIFICATION FRONTMATTER-FILL COMMIT THIRD.**

Rationale per 2712 §15.1 (ratification workflow steps 6-12):

1. The workspace ratification record must cite a specific git `commit_sha` in its evidence chain. That SHA does not exist until the repo commit is merged.
2. The Playbook frontmatter must cite the workspace `ratification_record.deliverable_id`. That UUID does not exist until the workspace record is created.
3. This mutual dependence is resolved by 2712 §15.1's **two-commit pattern**:
   - **Ratification commit** — writes `docs/ENGINEERING_PLAYBOOK.md` with frontmatter carrying `version_status: draft` (or `signing`), placeholders for `ratification_record.deliverable_id`, `content_hash`, `git_tag`, `commit_sha`.
   - **Post-ratification frontmatter follow-up commit** — updates the frontmatter to `version_status: ratified` and fills the deferred fields with concrete values now available after workspace ratification.

### 3.3 Do NOT write yet

Per mission constraint: *"Target file: docs/ENGINEERING_PLAYBOOK.md — Do NOT write it yet unless explicitly authorized."*

`docs/ENGINEERING_PLAYBOOK.md` is **NOT** written in this session. Session 2726's mission scope is package assembly only.

### 3.4 Write authorization required

The next System Owner Directive must explicitly authorize the write. Suggested directive text:

> *"Authorized: write docs/ENGINEERING_PLAYBOOK.md at Session 2727 open, using the assembly composition documented in Session 2726 §1.1."*

### 3.5 Branch discipline

- Branch name: `playbook/v0.1.0-inaugural` (per 2712 §5.1 `branch_authored` field convention)
- Base: `main` at HEAD `309f85eee4dae5cedb022a393d06a19882ccf62f`
- PR title: `feat(playbook): inaugural Engineering Playbook v0.1.0`
- PR body must include the ratification package pointer (`docs/research/platform/playbook_v0_1_ratification_package.md`) and the Session 2725 correction session pointer.

### 3.6 Pre-merge checks (v0.1)

Per 2712 §5.3 frontmatter validation rules:

- [ ] Frontmatter YAML parses.
- [ ] `version` is a valid semver.
- [ ] `git_tag` matches `playbook-v0.1.0` pattern (populated in post-ratification follow-up commit).
- [ ] `commit_sha` is a valid 40-char hex (populated in post-ratification follow-up commit).
- [ ] `ratification_record.workspace_id` is a valid UUID.
- [ ] `ratification_record.deliverable_id` is a valid UUID (populated after workspace ratification).
- [ ] `content_hash` present (populated in post-ratification follow-up commit).
- [ ] `parent_version` is `null` (inaugural v0.1.0).

Ratification-commit precondition: fields 3, 4, 6, 7 may hold placeholder sentinels; ratification-follow-up-commit precondition: all fields populated with concrete values.

### 3.7 CI expectations at merge

- `verify_repo_guardrails.py` — validates repo-guardrail metadata; expected pass.
- `docs-sync.yml` — regenerates `docs/INDEX.md` after merge; expected auto-cascade (part of §6 execution sequence).

---

## 4. Workspace Ratification Envelope Plan

### 4.1 Target workspace

`a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture & Research) — the workspace-canonical governance workspace per CLAUDE.md §"Workspace-canonical governance (Cycle 0/1)".

### 4.2 Target deliverable (to be created)

| Field | Value |
|-------|-------|
| deliverable_type | `ratification_record` |
| title | `RATIFICATION_20260708_PLAYBOOK_v0_1_0` (or `_20260709_` if crossing midnight UTC at ratification moment) |
| workspace_id | `a9a16593-e0a4-44dc-8256-efc65d524b3c` |
| parent_object_id | `null` (inaugural — no supersession chain) |
| status | starts `draft`, then `content_complete` transition to `ratified` per PublishGate |

### 4.3 Required content structure of the ratification record body

Per 2712 §14.4 and PIC-10 provenance discipline:

1. **§1 Identity block** — Playbook version, scope, ratified_date, ratifier, workspace ID, repository path.
2. **§2 Ratification directive verbatim** — Chris's directive per §2.10 above.
3. **§3 Evidence chain** — full manifest reference; per-chapter authoring status; convergent-chain acknowledgement.
4. **§4 Audit history** — verbatim Rigby verdicts from Sessions 2722, 2723, 2724, 2725.
5. **§5 Correction history** — Session 2723 (63 corrections) + Session 2725 (15 corrections) summarized with pointers.
6. **§6 Constitutional debt disposition** — CD-47 RESOLVED; CD-48 non-blocking, deferred to v0.1.1/v0.2.
7. **§7 Git binding** — commit_sha, git_tag, branch, content_hash.
8. **§8 Cascade authorization** — repo-canonical mirror instruction; Canon Registry inclusion (per §5 below).
9. **§9 Provenance classification** — PIC-10 classification per statement class within the record.

### 4.4 Git commit SHA requirement

The workspace ratification record's `§7 Git binding` must cite:

- **`commit_sha`** — the 40-char merge commit SHA of the `playbook/v0.1.0-inaugural` PR into `main`. This SHA does not exist until PR merge; it is captured immediately after merge and inserted before ratification (envelope drafted with placeholder → placeholder replaced pre-ratification).

### 4.5 Content hash requirement

The workspace ratification record's `§7 Git binding` must cite:

- **`content_hash`** — SHA-256 of the merged `docs/ENGINEERING_PLAYBOOK.md` body excluding frontmatter, computed via §2.2 command. Format: `sha256:<64-hex>`. Populated at the same time as `commit_sha` (both post-merge, pre-ratification).

### 4.6 System Owner directive wording

See §2.10 above for verbatim recommended directive language. The workspace ratification record embeds this directive as §2 of the record body.

### 4.7 Ratification record title

`RATIFICATION_20260708_PLAYBOOK_v0_1_0` (default) or `RATIFICATION_20260709_PLAYBOOK_v0_1_0` if the ratification moment crosses UTC midnight. Convention matches prior Cycle 1A ratification records (e.g., `RATIFICATION_20260707_0120_ADR_CANONICAL_AUTHORITY_ATTRIBUTE` per manifest C1-12).

### 4.8 Expected canonical_authority classification

- **`docs/ENGINEERING_PLAYBOOK.md`** — `canonical_authority = repo_canonical` per KFI-2 B3 derivation and 2711 §3-§4 substrate analysis (the Playbook is repo-source-of-truth L2 constitutional artifact).
- **Workspace ratification record deliverable** — `canonical_authority = workspace_canonical` per KFI-2 B2 derivation (workspace deliverables with ratification governance).

The `_derive_canonical_authority` 4-branch decision tree in `content/_canonical_authority_helpers.py:33-60` will assign these values deterministically once the artifacts are created.

### 4.9 Ratification-envelope drafting responsibility

Per this repo's convention and Session 2725 §2.4 collaboration protocol (author directs, Rigby executes, author verifies):

- **Draft body** — Claude Code prepares as a proposed record body (in the target format above).
- **Deliverable creation** — Rigby via `deliverable_tool` — respecting MEMORY.md `feedback_deliverable_create_defaults_to_completed` and `feedback_deliverable_status_via_content_complete` (create as draft → append body → transition via `content_tool` when ratification directive lands).
- **Ratification directive routing** — Chris via PA chat; Rigby records to `ratification_directive` field verbatim.
- **Verification** — Claude Code confirms via ORM read + manual body-inspection that the record body matches the drafted content and the ratification_directive field carries the verbatim directive.

---

## 5. Canon Registry Inclusion Plan

### 5.1 Recommendation

**YES, v0.1 SHOULD enter Canon immediately upon ratification.**

### 5.2 Rationale

Per `docs/canon/INDEX.md` Promotion Criteria:
1. **Expert-level quality** — 165 rules under multi-session Rigby SIGN audit + correction discipline.
2. **Factually accurate** — 70/70 sample-verified rules across Sessions 2724 + 2725.
3. **Production-tested** — the underlying disciplines (canonical_authority, PIC-10, cascade, session-open, RFC-2119, evidence classes) are all in-force via workspace ADRs, MEMORY rules, and CI enforcement.
4. **Practically useful** — solves the "which methodology do we operate by?" question at L2 platform scope.
5. **System Owner approved** — ratification directive is the "Chris says yes" gate.

The Playbook meets all five criteria at ratification moment.

### 5.3 Exact Canon Registry update (proposed)

Insert a new subsection under `docs/canon/INDEX.md` §Canon Registry, positioned between "Operational Canon" and "Runtime Evidence":

```markdown
### Constitutional Canon — the Engineering Playbook and its evidence

| Document | Topic | Promoted | Session |
|----------|-------|----------|---------|
| [`docs/ENGINEERING_PLAYBOOK.md`](../ENGINEERING_PLAYBOOK.md) | Donkey Betz Engineering Playbook — Layer 2 platform-scope constitutional codification of engineering methodology. 165 rules across 11 chapters (4 FULL, 7 STUB). See v0.1 ratification record `RATIFICATION_20260708_PLAYBOOK_v0_1_0`. | 2026-07-08 | 2726 |
| [`docs/research/platform/engineering_playbook_evidence_manifest.md`](../research/platform/engineering_playbook_evidence_manifest.md) | Frozen evidence manifest for Playbook v0.1 — sole authoritative source-of-admissibility for citations in the Playbook body (per manifest §2.1). | 2026-07-08 | 2726 |
```

### 5.4 Canon Registry section-header update

Per `docs/canon/INDEX.md` "Canon is intentionally small (≤10 docs)" constraint: adding 2 entries brings the Registry from 5 promoted-canon (technical + operational + runtime-evidence family) to 7. Under the ≤10 ceiling.

Update the `**Last Updated:** Session <N>` line to `Session 2726` (or whichever session performs the write).

### 5.5 Canon inclusion timing

Per 2712 §15.1 execution ordering, Canon inclusion happens **after** the workspace ratification record is created and Chris's directive is applied. The exact ordering is codified in §6 runbook below.

### 5.6 canon/INDEX.md cascade side-effect

`docs/canon/INDEX.md` is runtime-load-bearing (`core/services/docs_context_builder.py:186`). Changes to it are immediately visible to every agent that receives context. This is intentional per DOC_LIFECYCLE.md §2b — Canon Registry changes are session-open observable.

The docs cascade (per MEMORY.md `feedback_docs_pipeline_4_step_cascade` and `feedback_docs_cascade_at_every_close`) must run after the Canon Registry update to refresh:

1. `build_docs_index` — updates `docs/INDEX.md` autogen table.
2. `build_rag_corpus` — refreshes RAG corpus manifest.
3. `sync_docs_index_to_documents` — mirrors doc rows into `Document` table.
4. `sync_docs_index_to_documents --embed` (or `embed_documents --all-unembedded`) — embeds new content for Rigby retrieval.

Skipping step 4 leaves Rigby's RAG blind to the Playbook — see MEMORY.md `feedback_cascade_pr_must_include_embed_step` for the S1802 blind-spot precedent.

---

## 6. Final Execution Sequence (Runbook)

This runbook is prepared for Session 2727+ execution AFTER an explicit System Owner directive to proceed. Each step's authorization gate is called out.

### Step 0 — Precondition verification (Session 2726 handoff to next session)

- Confirm this ratification package is in `docs/research/platform/playbook_v0_1_ratification_package.md`.
- Confirm HEAD is still `309f85eee4dae5cedb022a393d06a19882ccf62f` or a descendent thereof with no conflicting Playbook content changes.
- Confirm Rigby SIGN pin `pa-275e12fb72de4b3e` is still available for post-ratification verification (or a fresh pin can be minted; MEMORY.md `feedback_session_tool_retire_works` confirms rotation works).

### Step 1 — Write `docs/ENGINEERING_PLAYBOOK.md`

**Authorization gate:** Chris directive: "Authorized: write docs/ENGINEERING_PLAYBOOK.md."

Actions:
1. Create branch `playbook/v0.1.0-inaugural` from `main` at current HEAD.
2. Write `docs/ENGINEERING_PLAYBOOK.md` composing:
   - YAML frontmatter per 2712 §5.1 with `version_status: draft`, `ratification_record.deliverable_id: <PLACEHOLDER>`, `commit_sha: <PLACEHOLDER>`, `content_hash: <PLACEHOLDER>`, `git_tag: <PLACEHOLDER>`.
   - Chapter 0 through Chapter 10 body per Session 2723 corrected draft + Session 2725 citation corrections.
   - Appendix A (evidence index sidecar reference) + Appendix D (version chain) placeholders per 2712 §14.
3. Verify locally: `grep -c "^\*\*\[.*\] PLAYBOOK-" docs/ENGINEERING_PLAYBOOK.md` returns 165.

### Step 2 — Commit

Actions:
1. `git add docs/ENGINEERING_PLAYBOOK.md`
2. `git commit -m "feat(playbook): inaugural Engineering Playbook v0.1.0 body"` (with author co-attribution per repo convention)
3. Verify commit created; capture temporary commit SHA (will be superseded by squash-merge SHA if applicable).

### Step 3 — PR + human review

Actions:
1. `gh pr create --title "feat(playbook): inaugural Engineering Playbook v0.1.0" --body "$(cat <<'EOF' ... EOF)"`
2. PR body includes: pointers to Session 2725 correction session report, Session 2726 ratification package, Rigby verification history, CD-47/CD-48 disposition.
3. Wait for Chris review and approval.

**Authorization gate:** Chris PR-approval or merge directive.

### Step 4 — Merge

Actions:
1. `gh pr merge <PR#> --squash` (or `--merge` per repo convention).
2. Capture merge commit SHA: `git rev-parse origin/main` after merge.
3. Confirm CI green.

### Step 5 — First-round cascade (post-merge, pre-ratification)

Actions (per MEMORY.md `feedback_docs_pipeline_4_step_cascade`):
1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py embed_documents --all-unembedded`
5. `python manage.py build_docs_provenance` (optional but recommended)

Verify: `Document.objects.filter(file_path='docs/ENGINEERING_PLAYBOOK.md').exists()` returns True.

### Step 6 — Create workspace ratification record (draft)

**Authorization gate:** Chris directive: "Proceed with workspace ratification record draft."

Actions (via Rigby per §4.9 collaboration protocol):
1. `deliverable_tool.create` with fields per §4.2. Result: draft record deliverable UUID.
2. `deliverable_tool.append` the body sections §1-§9 per §4.3 structure.
3. `deliverable_tool.set_status` to `ready` (per MEMORY.md `feedback_deliverable_create_defaults_to_completed`).
4. Fill `§7 Git binding` with actual `commit_sha` (from Step 4) and computed `content_hash` (from Step 2.2 command applied to merged file).

Verify (Claude): read the deliverable via ORM; body matches drafted content; §7 has concrete values.

### Step 7 — Ratification directive (Chris → Rigby)

**Authorization gate:** Chris routes the §2.10 verbatim ratification directive to Rigby via PA chat.

Actions:
1. Rigby records the verbatim directive into `deliverable.ratification_directive` field.
2. Rigby transitions the ratification-record deliverable via `content_tool.content_complete` (per MEMORY.md `feedback_deliverable_status_via_content_complete`) to `status=ratified`.
3. Rigby confirms record is workspace-canonical per B2 derivation.

Verify (Claude): ORM check that `ratification_directive` field carries the verbatim directive.

### Step 8 — Post-ratification frontmatter follow-up commit

**Authorization gate:** Chris directive: "Proceed with frontmatter follow-up commit."

Actions:
1. On branch `playbook/v0.1.0-frontmatter-fill` (or direct-to-main per repo convention):
   - Update `docs/ENGINEERING_PLAYBOOK.md` frontmatter: `version_status: ratified`, `ratification_record.deliverable_id: <UUID>`, `commit_sha: <SHA from Step 4>`, `content_hash: sha256:<HASH>`, `git_tag: playbook-v0.1.0`, `ratified_date: <YYYY-MM-DD>`.
2. Commit + PR + merge (or direct-to-main).
3. Tag: `git tag -a playbook-v0.1.0 -m "Engineering Playbook v0.1.0 ratified per RATIFICATION_20260708_PLAYBOOK_v0_1_0" <merged SHA>`
4. `git push origin playbook-v0.1.0`

### Step 9 — Mirror + verify (per ADR-0110 KFI-1)

Actions:
1. Confirm the workspace deliverable → `Document` mirror ran on the ratification-record deliverable per Cycle 1A KFI-1.
2. Verify: `Document.objects.filter(source='workspace', workspace_id='a9a16593-…', canonical_authority='workspace_canonical').filter(reference__contains='RATIFICATION_20260708_PLAYBOOK_v0_1_0').exists()` returns True.
3. Confirm the repo-canonical `Document` row for `docs/ENGINEERING_PLAYBOOK.md` carries `canonical_authority='repo_canonical'` per KFI-2 B3.

### Step 10 — Canon Registry update

**Authorization gate:** Chris directive: "Proceed with Canon Registry update."

Actions:
1. Edit `docs/canon/INDEX.md` per §5.3 exact-text-shown.
2. Bump `**Last Updated:** Session <N>` line.
3. Commit + PR + merge (small doc PR).

### Step 11 — Final cascade

Actions (per §5.6 same as Step 5, plus rerun after Canon update):
1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py embed_documents --all-unembedded`
5. `python manage.py build_docs_provenance`

Verify: `Document.objects.filter(file_path='docs/canon/INDEX.md').update(updated_at=Now())` reflects Canon Registry refresh; Rigby RAG queries for "Engineering Playbook" return the new document.

### Step 12 — Handoff + 00-START update

Actions:
1. Write `docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md` (or applicable session number) recording:
   - Ratification date + Chris directive verbatim
   - Commit SHA, content_hash, git tag
   - Workspace deliverable UUID
   - Any follow-ups (CD-48 remediation queue)
2. Update `00-START-NEXT-SESSION.md` current-priorities block: remove Playbook v0.1 ratification from open queue; add v0.1.1/v0.2 planning as next-cycle item.
3. Commit + PR + merge.

### Step 13 — Final verification (Rigby)

Actions:
1. Send Rigby (on any active pin) a probe: `"Verify: what is the current version of the Engineering Playbook per canon/INDEX.md + docs/ENGINEERING_PLAYBOOK.md frontmatter?"`
2. Expected response: v0.1.0 ratified, workspace record UUID, cited from RAG.

Success criterion: Rigby's response cites Playbook v0.1 from her retrieval corpus, proving cascade + embed succeeded.

### Step 14 — Session close

Actions:
1. Record final tally in the handoff.
2. Retire the currently-active SIGN pin per rotation discipline (per Session 2725 §5.1 pattern).

**End of runbook.**

---

## 7. Non-actions (per mission constraint)

Per explicit Session 2726 mission directives, this session performed NONE of the following:

- Did **NOT** ratify.
- Did **NOT** create workspace deliverables.
- Did **NOT** update Canon.
- Did **NOT** run cascade.
- Did **NOT** create `docs/ENGINEERING_PLAYBOOK.md`.

---

## 8. Ratification-Readiness Summary

| Precondition | Status |
|--------------|--------|
| Final rule count computed | ✓ 165 rules |
| Chapter list assembled | ✓ 11 chapters (Chapters 0-10) |
| Evidence manifest frozen and referenced | ✓ Session 2715 manifest, SHA-256 `198a4d87…` |
| Rigby audit history complete | ✓ 4 sessions (2722, 2723, 2724, 2725) |
| Correction history complete | ✓ 2 sessions (2723 → 63 corrections; 2725 → 15 corrections) |
| CD-47 resolved | ✓ Session 2725 fixed 15 defects; Rigby 15/15 PASS |
| CD-48 recorded as non-blocking | ✓ Session 2725 §9.1 documented |
| Recommended ratification language drafted | ✓ Package §2.10 |
| Repo placement plan drafted | ✓ Package §3 |
| Workspace ratification envelope plan drafted | ✓ Package §4 |
| Canon Registry inclusion plan drafted | ✓ Package §5 |
| Execution runbook drafted | ✓ Package §6 (14 steps) |

**All package preconditions satisfied.**

---

## 9. STOP state (Session 2726)

Package assembly complete. Session 2726 stops here per mission directive.

The final Playbook body (as a physical single file) has NOT been written. No workspace deliverable has been created. No Canon Registry update has been made. No cascade has been run. No ratification has been performed.

### 9.1 Exact next System Owner decision required

Chris must select one of the following:

- **Option A (recommended):** *"Proceed with Session 2727 — write docs/ENGINEERING_PLAYBOOK.md per Session 2726 §6 Step 1, commit + PR, and await further directives at each subsequent step."*
- **Option B (defer):** *"Hold Session 2727 open. I want to review the ratification package in full before authorizing the write."*
- **Option C (address CD-48 first):** *"Before v0.1 ratification, run a v0.1-scope amendment to codify the CD-48 principle in Chapter 6 or Chapter 10." — this would extend the mission scope beyond Session 2725's constraint.*
- **Option D (waive):** *"Waive CD-48 remediation permanently; proceed to Session 2727 write per §6 Step 1."* — same execution path as Option A; adds explicit CD-48 waiver into the ratification directive.
- **Option E (abandon):** *"Do not ratify v0.1; return to authoring."* — not recommended given the audit history but available.

Recommended: **Option A.**

---

**END SESSION 2726 RATIFICATION PACKAGE.**

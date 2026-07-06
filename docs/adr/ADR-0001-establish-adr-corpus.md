---
title: "ADR-0001 — Establish the ADR corpus"
adr_id: ADR-0001
slug: establish-adr-corpus
status: accepted
authority: design-decision
proposed: 2026-07-06
ratified: 2026-07-06
ratifier: chris
supersedes: (none — this is the first ADR)
superseded_by: (none)
intake_id: IB-Q1-BOOT-01
arc_ref: I-0100
source_refs:
  - docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md §2.5
  - docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md §D3
  - docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md Appendix C
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md §8.3 (P1 gap: "No formal ADR corpus exists")
  - docs/research/implementation/BACKLOG.md IB-Q1-BOOT-01 row
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md §5 P0 row
reversibility: 4
  # 1 = irreversible, 5 = trivially reversible.
  # Rated 4: the corpus can be moved or reformatted later; only the
  # naming scheme and directory location are load-bearing across
  # existing cross-references. Renaming/moving requires a batch edit
  # sweep across IOS + BACKLOG + arc scoping docs — recoverable but
  # not instant.
companion_docs:
  - docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md
  - docs/research/implementation/BACKLOG.md
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md
---

# ADR-0001 — Establish the ADR corpus

## 1. Status

**Accepted** — Chris-ratified 2026-07-06 via §D3 recommendation acceptance ("Default stance: accept the IOS v1.1 recommendations unless there is a concrete reason not to.") at IOS v1.2 ratification. This ADR file itself is the concrete materialization of that ratification.

## 2. Context

Research OS `§8.3` states:

> No formal ADR corpus exists. This is a P1 gap called out in §17.

The Implementation Operating System (IOS) — `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md`, active v1.3 as of 2026-07-06 — depends on a durable Architecture Decision Record (ADR) corpus to record design-decision ratifications for every intake row with `risk_class: NEEDS_ADR`. IOS §2.5 specifies the corpus shape; IOS §D3 puts installation to Chris as an open question; Chris ratified installation on 2026-07-06.

The IOS §4.3 Stage 1 exit gate was further refined at v1.2 to add an **ADR corpus precondition**: any arc admitting a `NEEDS_ADR` intake row must verify `docs/adr/` exists on `main` before Stage 2 opens, or bundle `IB-Q1-BOOT-01` as an in-arc P0 prep PR. Arc I-0100 (Observability Correlation Spine + Mission Evidence Substrate — first production implementation arc under IOS) selected Option (a) — bundle `IB-Q1-BOOT-01` as an in-arc P0 prep PR. **This ADR is the deliverable that discharges `IB-Q1-BOOT-01`.**

The recursive shape is intentional: the first ADR establishes the corpus that contains it. Without this bootstrap, Stage 2 of Arc I-0100 (ADR-B for PA write-shape, ADR-A for MISSION_RUNNER staged enable, ADR-C for D74 correlation-spine posture) cannot open — there would be nowhere to put those ADRs.

## 3. Decision

**Establish `docs/adr/` as the canonical ADR corpus for the Donkey Betz platform.** Every design decision that:

- Has multiple viable implementation options AND
- Would materially change runtime behavior, contracts, or subsystem shape AND
- Is not trivially reversible (reversibility ≤ 3 on the 5-point scale below)

...is recorded as an ADR in this directory, ratified by Chris, and cited by every intake row and PR that depends on it.

### 3.1 Directory layout

- **Location:** `docs/adr/`
- **Naming:** `ADR-NNNN-<slug>.md`
- **Numbering:** Monotonically incremented at ratification time, independent from session numbers, arc numbers, or intake IDs. `NNNN` is a zero-padded 4-digit integer starting at `0001`.
- **Slug:** Lowercase-hyphenated short handle. Not the full title. Examples: `establish-adr-corpus`, `d74-correlation-spine-posture`, `pa-write-shape`.

### 3.2 Numbering discipline

- The next ADR's `NNNN` is `max(existing NNNN) + 1`. Gaps are permitted only in cases of a rejected-in-draft ADR that never ratified but reserved a number (rare — noted in a `retracted:` frontmatter field on the placeholder file).
- ADR numbers are stable once ratified. A superseded ADR keeps its number; the superseding ADR gets the next number and cites the prior via `supersedes:` frontmatter.
- ADR numbering is independent from intake ID numbering (`IB-...`), debt IDs (`IDBT-NNNN`), arc IDs (`I-NNNN`), and session numbers (`SNNNN`).

### 3.3 Frontmatter schema (Yes-required fields on every ADR)

```yaml
---
title: "ADR-NNNN — <short human-readable title>"
adr_id: ADR-NNNN
slug: <slug-matching-filename>
status: proposed | accepted | superseded | retracted
authority: design-decision
proposed: YYYY-MM-DD
ratified: YYYY-MM-DD | (open)
ratifier: chris | (open)
supersedes: ADR-XXXX | (none)
superseded_by: ADR-YYYY | (none)
intake_id: IB-... | (none if pre-intake)
arc_ref: I-NNNN | (none if arc-orthogonal)
source_refs:
  - <file:section>
  - <file:section>
reversibility: 1..5
companion_docs:
  - <file>
  - <file>
---
```

Optional fields:

- `retracted: YYYY-MM-DD` — when `status: retracted`.
- `retraction_reason` — free-text.
- `sign_cycle` — Rigby SIGN cycle metadata if the ADR was routed through SIGN.

### 3.4 Body sections (canonical structure)

Every ADR body follows this shape. Order matters; grep-friendly section headers.

1. **§1 Status** — proposed / accepted / superseded / retracted, with Chris ratification citation.
2. **§2 Context** — the situation forcing the decision; upstream research or intake references; the P1 gap or CX-P pattern being closed.
3. **§3 Decision** — the concrete rule being adopted. Load-bearing prescriptions live here. Sub-sections permitted; each labeled §3.N.
4. **§4 Consequences** — what shipping this ADR enables; what it obligates every consumer to do; observable effects on the codebase, runtime, docs, or governance.
5. **§5 Alternatives considered** — every option rejected in getting to §3. For each: shape + reason for rejection. Empty-alternatives ADRs are permitted (no true alternative existed) but must state so explicitly.
6. **§6 Reversibility** — reversibility rating on the 1..5 scale (1 = irreversible, 5 = trivially reversible) with a paragraph justifying the rating and describing what rollback would entail.
7. **§7 Provenance** — Rigby SIGN record (cycle, folds, pin), Chris ratification quote or timestamp, related PRs, related intake rows.

Optional §8+ appendices are permitted for long ADRs (schemas, migration playbooks, exhibit lists).

### 3.5 Reversibility scale

The `reversibility` frontmatter field uses this scale (aligned with IOS §3.1 scoring dimension):

| Rating | Meaning | Example |
|--------|---------|---------|
| **1** | Irreversible or catastrophic to reverse | Column drop with data loss; contract break with fleet-key consumers |
| **2** | Very hard to reverse; would require dedicated arc | Model schema rename with cross-fleet consumers; posture change with in-flight production traffic |
| **3** | Reversible with focused effort | Feature-flag flip that requires code path removal; ADR revision requiring downstream ADR sweep |
| **4** | Reversible with light effort | Format or naming change with bounded cross-references; single-subsystem refactor |
| **5** | Trivially reversible | Comment-only doc edit; toggle-back of a feature flag; single-line config change |

Reversibility informs — but does not determine — the risk classification. A reversibility-1 ADR is not automatically `NEEDS_CHRIS_PRE_RATIFICATION`; IOS §3.1 six-dimension scoring is the authoritative classifier.

### 3.6 Lifecycle: proposed → accepted → superseded / retracted

- **`proposed`** — ADR drafted, routed to Rigby SIGN if IOS §7.2 requires (Stage 2 SIGN is Yes-required for all NEEDS_ADR intake rows). Chris has not ratified. No PR that depends on this ADR opens.
- **`accepted`** — Chris ratified (via PA chat, workspace ratification card, or session-transcript "agree" statement citing the ADR by ID). `ratified` field populated. Downstream PRs may now cite `adr_ref: ADR-NNNN` and proceed to §8.4 IMPLEMENTATION contract.
- **`superseded`** — A later ADR replaces this decision. Body preserved as truth-history; frontmatter `superseded_by` populated; a §8 "Superseded by" section at the bottom cites the successor and summarizes the change.
- **`retracted`** — The ADR proposed a decision that did not survive first contact (§8.4 IOS retracted findings register semantics). Frontmatter `retracted:` date and `retraction_reason` populated. Body preserved.

Superseded and retracted ADRs are **NEVER deleted** — the corpus is truth-history, not just current state.

### 3.7 Coupling to intake rows

Every backlog row with `risk_class: NEEDS_ADR`:

- Enters `BACKLOG.md` with `adr_ref: (pending)` in its notes column.
- Cannot progress past Stage 2 exit until its `adr_ref` is populated with an accepted ADR ID.
- On ADR acceptance, `adr_ref` flips from `(pending)` to `ADR-NNNN`.
- No PR ships against a `NEEDS_ADR` intake until its ADR is `accepted`.

### 3.8 Coupling to PRs

Every PR that ships against a `NEEDS_ADR` intake:

- Cites its `intake_id` in the PR body (IOS §5.2 rule 5).
- Cites the ratified `ADR-NNNN` in the PR body under a `## ADR ratification` section.
- Cannot merge if the cited ADR is not `accepted`.

Every PR that AUTHORS an ADR (Stage 2 PRs, including this one):

- Ships one ADR per PR by default (bundling permitted per IOS §6.3 rules).
- Runs the full 5-step docs cascade locally before PR open per IOS v1.3 §12.5.a — ADRs are RAG-critical artifacts per §12.5.b.
- Includes the §12.5.d cascade evidence block in the PR body.
- Co-commits `docs/INDEX.md` + `docs/_provenance.json` diffs.

### 3.9 The recursive-bootstrap invariant

This ADR (`ADR-0001`) is the recursive-bootstrap ADR: it establishes the corpus that contains itself. Two invariants must hold across future ADRs:

1. **This ADR cannot be retracted or superseded without a successor that re-establishes the corpus in a different form.** Retracting ADR-0001 would delete the ground under every other ADR. If a future ADR proposes a fundamentally different design-decision recording surface (e.g., "move ADRs to a hosted decision-registry service"), that ADR MUST supersede this one and specify the migration path for every existing ADR before ratification.

2. **This ADR's ratification is what unblocks all other Arc I-0100 ADRs.** ADR-A (MISSION_RUNNER + RIGBY_DELEGATION staged-enable posture), ADR-B (PA write shape + PA↔LLMCallEvent correlation contract), and ADR-C (D74 six-axis correlation-spine posture) cannot open Stage 2 SIGN routing until ADR-0001 lands on `main`. This is the concrete unblocking event.

## 4. Consequences

### 4.1 Enabled

- **Every future `NEEDS_ADR` intake row has a home.** Stage 2 of any implementation arc can now open ADR authoring without a Stage 1 exit-gate block.
- **Arc I-0100 Stage 2 unblocks on this PR's merge.** Once `docs/adr/` and this ADR are on `main`, Arc I-0100 can proceed to ADR-B (per Rigby F4 fold, ratifies first), then ADR-A, then ADR-C.
- **Chris + Rigby have a canonical grep surface for architecture decisions.** `grep -r "status: accepted" docs/adr/` lists every ratified decision; `grep -r "supersedes:" docs/adr/` traces decision evolution.
- **Research OS §8.3 P1 gap is closed.** The upstream research operating system's canonical P1 gap ("No formal ADR corpus exists") is discharged as of this ADR's merge.

### 4.2 Obligated

- **Every future arc's Stage 2 planning must count NEEDS_ADR rows and plan for one ADR per row (or bundle per IOS §6.3).**
- **Every PR against a NEEDS_ADR intake must cite its ADR ID.** The IOS §5.2 pre-merge gate 5 (PR body cites intake_id + xx99 file:line) extends to `adr_ref` when applicable.
- **Every ADR must run the docs cascade locally before PR open** per IOS v1.3 §12.5.a — ADRs are RAG-critical per §12.5.b.
- **Superseded ADRs must remain in-tree** — the corpus is truth-history. Deletion is prohibited.
- **Backfilling `adr_ref` on existing NEEDS_ADR intake rows** — Chris and Claude may choose to retroactively populate `adr_ref: (pending)` on the 32 T0 rows and any T1 rows with `risk_class: NEEDS_ADR` in `BACKLOG.md`. Not required by this ADR; recommended.

### 4.3 Non-goals of this ADR

- **This ADR does NOT specify which ADRs to author or in what order.** Sequencing is per-arc, governed by IOS §4.3 Stage 2 and each arc's scoping doc §9 ADR checkpoint.
- **This ADR does NOT prescribe a specific SIGN cadence for ADR review.** IOS §7.2 governs (Stage 2 SIGN is Yes-required for all NEEDS_ADR intake).
- **This ADR does NOT install automation** — no CI check enforces "PRs against NEEDS_ADR must cite ADR." That is a candidate for D11 Wave 2 (`ios_gate_check`) per IOS §D11.
- **This ADR does NOT migrate existing informal design-decision records** (Rigby SIGN Cycle summaries, arc scoping doc §8 Decisions sections). Those remain in place as arc-scoped decisions; only decisions matching §3 criteria become ADRs.

## 5. Alternatives considered

### 5.1 Option B — Collapse ADR requirements onto arc-scoping doc `§Decisions ratified` sections (rejected)

**Shape.** Do not install `docs/adr/`. Instead, arc parent-scoping docs' `§8 Decisions ratified` section serves as the ratification surface. Each `NEEDS_ADR` intake row cites the arc scoping doc file:line.

**Reason for rejection.** Preserves current de-facto habit but keeps Research OS §8.3 as a P1 gap indefinitely. Arc-scoping docs are per-arc; a decision made in one arc becomes hard for a future unrelated arc to discover without a canonical decision registry. Grep across arc scoping docs is possible but requires knowing which arcs touched the decision. `docs/adr/` gives a single grep surface. Chris rejected this via §D3 ratification ("Option A — install `docs/adr/`.")

### 5.2 Option C — External decision-registry service (rejected as non-goal)

**Shape.** Store ADRs in a hosted decision-registry (e.g., Notion, Linear, a custom Django admin app). Access via UI + API.

**Reason for rejection.** Violates the "canonical is git" principle applied to every other governance surface (RESEARCH OS, IOS, BACKLOG, DEBT, ratifications). Adds an external dependency (hosted service uptime, auth, migration) with no compensating benefit at current volume. Not raised as a live option in §D3; noted here for completeness. Not blocked forever — a future ADR could migrate the corpus if volume or discovery pressure justifies. Retained as a viable long-term option, rejected as a starting point.

### 5.3 No-ADR-corpus (rejected as violating IOS)

**Shape.** Ship without any decision-recording surface. Rely on session transcripts, Rigby SIGN records, and CLAUDE.md updates to preserve architecture decisions.

**Reason for rejection.** Violates IOS §2.5 (which requires the corpus) and blocks Arc I-0100 Stage 2 exit-gate ADR corpus precondition. Not compatible with active IOS v1.3.

## 6. Reversibility

**Rating: 4 (reversible with light effort).**

### 6.1 What "reverse" would mean

Reversing ADR-0001 means either (a) migrating the corpus to a different location or format (e.g., `docs/decisions/` instead of `docs/adr/`), (b) migrating the corpus to an external service (Option C above), or (c) removing the corpus entirely and reverting to arc-scoping doc `§Decisions ratified` sections (Option B above).

### 6.2 Reversal effort

- **Format/location rename (a):** batch-edit sweep across IOS §2.5 + §4.3 + §5.2 + §12.5, every intake row's `adr_ref` field, every arc scoping doc that cites `ADR-NNNN`, and every PR body that cites the corpus location. Recoverable in one focused session per ~10 ADRs.
- **External service migration (b):** heavier — export every ADR, ingest into external tool, replace grep-based discovery with API/UI, update every cross-reference. Multi-session arc.
- **Full removal (c):** requires collapsing every accepted ADR's decisions back into their originating arc scoping doc's `§Decisions` section AND accepting that Research OS §8.3 P1 gap reopens. Not recommended.

Rating 4 reflects (a) as the most likely reversal path.

### 6.3 What is NOT reversible (rating-1 sub-property)

The **content** of every accepted ADR is preserved as truth-history regardless of what happens to the corpus location. Superseded ADRs stay in-tree; retracted ADRs stay in-tree. Deletion of an ADR's body content (as opposed to relocation) IS irreversible in that it destroys governance provenance. This constraint holds regardless of corpus form.

## 7. Provenance

### 7.1 Rigby SIGN record

**Not routed to Rigby SIGN Cycle** for this ADR.

**Reason:** IOS §7.2 Stage 2 SIGN requirement is Yes for `NEEDS_ADR` intake, but IB-Q1-BOOT-01 is IOS bootstrap infrastructure specified in advance by §2.5 + §D3 + Appendix C. This ADR materializes the specified corpus format; no design-decision options remain open at authoring time. Same reasoning as IOS v1.1/v1.2/v1.3 execution-refinement patches (no SIGN cycle when the spec is fully pre-specified by upstream policy). If Chris directs a retroactive SIGN cycle before ratification, it can be routed on the current arc pin `pa-c5b235f7b15f45be` per Arc I-0100 scoping doc frontmatter.

### 7.2 Chris ratification

Ratified 2026-07-06 via §D3 recommendation acceptance at IOS v1.2 status flip: "Default stance: accept the IOS v1.1 recommendations unless there is a concrete reason not to." §D3 recommended Option A (install `docs/adr/`). Chris accepted. This ADR is the concrete implementation of that acceptance and inherits the ratification via the P0 prep PR merge.

### 7.3 Related PRs

- `#2939` (MERGED) IOS v1.2 Chris-ratified — includes §D3 acceptance authorizing `docs/adr/` installation.
- `#2943` (MERGED) IOS v1.2 execution-refinement patch — adds Stage 1 exit-gate ADR corpus precondition (§4.3), naming IB-Q1-BOOT-01 as the discharge path.
- `#2945` (MERGED) Arc I-0100 Stage 1 arc-open bundle — selects Option (a) bundle (this P0 prep PR ships before Stage 2).
- `#2947` (MERGED) IOS v1.3 cascade-discipline refinement — codifies the pre-PR cascade rule this ADR PR dogfoods.
- **This PR** — IB-Q1-BOOT-01 discharge PR (P0 prep for Arc I-0100 Stage 2).

### 7.4 Related intake rows

- `IB-Q1-BOOT-01` (BACKLOG.md T0 §"IOS bootstrap infrastructure") — discharged by this ADR. Row flips `TRIAGED → SHIPPED` at this PR's merge, with `arc_ref: I-0100` and `pr_refs` populated.
- Every future `NEEDS_ADR` intake row inherits ADR-0001 as its ambient dependency.

### 7.5 Related debt rows

- `IDBT-0002` (added by this PR) — RAG-domain-owned finding: `sync_docs_index_to_documents` `Updated` path does not invalidate old embeddings on content-change updates, so `embed_documents --all-unembedded` is a no-op for edits to existing docs. Surfaced during PR #2947 IOS v1.3 dogfood cascade. Classified as RAG-domain debt; `resolution_path` delegates to the future Group 2100 RAG research arc backlog (per MEMORY project_2100_plus_queue_ranking — Chris D-override priority). **Not blocking this PR** — ADR-0001 is a new file with a new `Document` row, so it should embed cleanly on this cascade. If ADR-0001 does NOT become RAG-visible after merge, the IB-Q1-BOOT-01 scope reopens to include a targeted fix; otherwise the debt discharges via Group 2100 when opened.

## 8. Next ADRs blocked on this one

Per Arc I-0100 scoping doc §9.1, Stage 2 opens with three ADRs, all blocked on ADR-0001 acceptance:

| ADR ID (reserved) | Slug (proposed) | Content | SIGN ratification order (per F4 fold) |
|-------------------|-----------------|---------|---------------------------------------|
| `ADR-0002` | `pa-write-shape-and-correlation-contract` | PA write shape (per-turn AgentExecution vs per-message span vs dedicated PAAgentExecution) + PA↔LLMCallEvent correlation contract per F5 fold | **First** (ADR-B) |
| `ADR-0003` | `mission-runner-staged-enable-posture` | `MISSION_RUNNER_ENABLED` + `RIGBY_DELEGATION_ENABLED` staged-enable posture per F8-iii + rollback triggers per §7.2/§7.3 | **Second** (ADR-A) |
| `ADR-0004` | `d74-six-axis-correlation-spine-posture` | D74 six-axis observability correlation-spine posture (Option A execution_id / Option B trace_id / Option C shared view / Option D hybrid) with retention constraints as required input per F2 fold | **Third, optional** (ADR-C) |

ADR numbering is not reserved by this ADR — the next PR author assigns `NNNN = max(existing) + 1` per §3.2. The mapping above is the current best-fit slug + intent; actual numbers assigned at each ADR's proposed date.

---

**END ADR-0001-establish-adr-corpus.md**

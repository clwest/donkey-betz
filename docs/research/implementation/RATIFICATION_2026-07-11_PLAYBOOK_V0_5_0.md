---
title: "Engineering Playbook v0.5.0 Amendment Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2753
ratification_date: 2026-07-11
ratifier: chris
ratifier_verdict: "agree all"
routing: rigby-pa-chat SIGN (watchpoints W1..W7 dogfooding PLAYBOOK-7.6.1 pre-ratification) + Chris D-verdict via Rigby PA chat
amendment_scope: playbook-minor-v0.5.0
amendment_class: MINOR (per PLAYBOOK-10.5.1 — 5 additions, 0 modifications, 0 removals)
parent_version: v0.4.1
parent_version_git_tag: playbook-v0.4.1
parent_version_commit_sha: 0805a332
parent_version_ratification: RATIFICATION_20260710_PLAYBOOK_v0_4_1 (workspace deliverable bb01b377-5953-4cb3-adc5-67135367121c in workspace a9a16593-e0a4-44dc-8256-efc65d524b3c)
proposed_version: v0.5.0
proposed_git_tag: playbook-v0.5.0
predecessor_shape_doc: docs/research/platform/playbook_v0_5_proposal_shape.md
predecessor_shape_ratification_session: 2752
predecessor_candidacy_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md §5
head_at_amendment_draft: ebf69e96
head_at_ratification: TBD (filled at merge)
close_pr: TBD (filled at merge)
sign_sessions:
  - S2753 turn 1 — Rigby watchpoint-attestation SIGN (W1..W7): W1..W6 PASS clean; W7 BLOCK resolved by this ratification envelope recording author-side 6-check per §3 below. Non-blocking asks W3/W4/W5 applied inline before re-dispatch.
rules_added:
  - PLAYBOOK-7.4.1
  - PLAYBOOK-7.4.2
  - PLAYBOOK-7.4.3
  - PLAYBOOK-7.5.1
  - PLAYBOOK-7.6.1
rules_modified: []
rules_removed: []
manifest_additions: [C7-11, C7-12, C7-13, C7-14, C7-15, C7-16, C7-17, C7-18, C7-19, C7-20, C7-21, C7-22, C7-23, C7-24]
rule_count_before: 196
rule_count_after: 201
chapter_activation: "Chapter 7 partial activation — §7.4/§7.5/§7.6 authored; §7.3 deferral scope narrowed to session-open orientation, cross-repo coordination, multi-session amendment coordination, and session-provenance integration (see §7.8 Extension points)"
supersedes: none
superseded_by: (open; not expected — ratification records are frozen historical envelopes)
frozen: true
workspace_id: a9a16593-e0a4-44dc-8256-efc65d524b3c
workspace_name: "Architecture & Research"
workspace_ratification_deliverable_id: TBD (filled at commit — workspace deliverable_id will be surfaced by Rigby into this file and the playbook top-frontmatter simultaneously)
d_verdicts_from_shape_stage_1:
  - Q1 Chapter fit — Option B (Ch 7 §7.4/§7.5/§7.6 activation) — RATIFIED 2026-07-11 S2752
  - Q2 All 5 candidates in v0.5 — RATIFIED 2026-07-11 S2752
  - Q3 Watchpoint SIGN — EXTEND ROS §6.10.3 — RATIFIED 2026-07-11 S2752
  - Q4 Stage 2 timing — fresh session immediately after shape lands — RATIFIED 2026-07-11 S2752 (executed at S2753)
  - Q5 Manifest freeze — bundle under v0.5 SIGN — RATIFIED 2026-07-11 S2752
---

# Engineering Playbook v0.5.0 — Amendment Ratification Record

This file is the **workspace ratification envelope reflected in-repo** for the Engineering Playbook v0.5.0 MINOR amendment. It captures the amendment scope, the author-side PLAYBOOK-6.10.1 6-check verification (§3), the Rigby watchpoint-attestation SIGN cycle (§4), Chris's D-verdict (§5), and the post-ratification bindings (§6). It is append-only history; do NOT edit after commit except to fill the reserved TBD fields (`ratifier_verdict`, `head_at_ratification`, `close_pr`, `workspace_ratification_deliverable_id`).

---

## §1. Context

- **Amendment class:** MINOR (5 additions, 0 modifications, 0 removals) per PLAYBOOK-10.5.1.
- **Session:** S2753 (Stage 2 codification per shape doc §7 execution plan; opens immediately after S2752 Stage 1 shape ratification per Q4 D-verdict).
- **Head at amendment draft:** `ebf69e96` (post-S2752 close bundle #3133 merge).
- **Ratifier:** Chris (pending D-verdict at time of authoring).
- **Routing:** Rigby PA chat surface via pin `pa-44541f01cbb14b46` (v0.5 codification scope); Chris D-verdict via Rigby chat.
- **Predecessor shape:** `docs/research/platform/playbook_v0_5_proposal_shape.md` (Stage 1, ratified S2752 with Chris "agree all" on Q1..Q5).
- **Predecessor candidacy:** `RATIFICATION_2026-07-10_i0302_arc_close.md` §5 (candidacy records for the 5 rules).
- **Precedent:** first MINOR amendment ratified using Chapter 7 partial-activation semantics; first amendment whose SIGN cycle dogfoods PLAYBOOK-7.6.1 (watchpoint-attestation shape) pre-ratification.

---

## §2. Ratified amendment scope

### §2.1 Chapter 7 partial activation

Chapter 7 (Session Discipline) transitions from full STUB to partial activation. Three substantive sub-sections are authored:

- **§7.4 Close-ceremony delivery discipline** — 3 rules (PLAYBOOK-7.4.1 phase-close 1-PR bundle; 7.4.2 phase-close doc serialization; 7.4.3 close-doc + cascade PR shape with COMBINED-vs-SPLIT criterion).
- **§7.5 Staged codification of anti-pattern substrates** — 1 rule (PLAYBOOK-7.5.1 REPORT-ONLY → BATCH-FIX → ENFORCEMENT-FLIP three-PR pattern).
- **§7.6 Session-close SIGN-cycle discipline** — 1 rule (PLAYBOOK-7.6.1 watchpoint-attestation SIGN, EXTENDS PLAYBOOK-6.10.3 for close-cycle scope only).

§7.3 (Extension deferred) is NOT modified; its remaining deferral scope (session-open orientation general; cross-repository coordination; multi-session amendment coordination; session-provenance integration) is enumerated in the renumbered §7.8 (Extension points, informative). Old §7.4/§7.5 (informative Cross-references / Extension points) are renumbered to §7.7/§7.8 with additional cross-links to §6.10.3 and ROS §2.7.1.

Chapter 7 rule count: 3 → 8. Playbook total rule count: 196 → 201.

### §2.2 Manifest additions

14 evidence entries added to `docs/research/platform/engineering_playbook_evidence_manifest.md` §10.1: C7-11 through C7-24 (13 entries per shape doc §6 + 1 additional entry C7-24 per S2753 SIGN W3 non-blocking ask). New §10.3 "v0.5 partial-activation evidence" roll-up with lockbox-frozen-for-v0.5 semantics per S2753 SIGN W4 non-blocking ask. §10.4 gap update reports zero blocking gaps at HEAD `ebf69e96`.

### §2.3 Appendix D chain row

`docs/ENGINEERING_PLAYBOOK.md` Appendix D receives a new row:

| Field | Value |
|---|---|
| Version | v0.5.0 |
| Parent | v0.4.1 |
| Supersedes | (none) |
| Ratification date | 2026-07-11 |
| Git tag | playbook-v0.5.0 |
| Notes | MINOR — 5 [GR] rules; Ch 7 partial activation; §7.4/§7.5/§7.6 authored; old §7.4/§7.5 renumbered to §7.7/§7.8; rule count 196 → 201 |

### §2.4 Playbook top-frontmatter update

`version` 0.4.1 → 0.5.0; `parent_version` 0.4.0 → 0.4.1; `rule_count` 196 → 201; `rules_added_v0_5_0` = the 5 rules; `compatible_with` extended with "0.4.1"; `ratified_date` 2026-07-11; `git_tag` playbook-v0.5.0; `authoring_sessions` extended with [2752, 2753]; `audit_sessions` extended with [2752]. `commit_sha` / `content_hash` / `ratification_record.deliverable_id` remain PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION per Appendix D v0.1.0 pre-ratification pattern; `version_status` = `pending-ratification` per S2753 SIGN W5 non-blocking ask (flips to `ratified` at Chris D-verdict + commit + tag simultaneously).

---

## §3. PLAYBOOK-6.10.1 6-check author verification (recorded 2026-07-11 S2753)

PLAYBOOK-6.10.2 requires that author-side verification results (checks 1–6) be recorded in the amendment provenance before SIGN dispatches. This section discharges that recording obligation for v0.5.0. Rigby SIGN W7 (S2753) BLOCKED on the absence of this recorded artifact at HEAD; recording it here resolves that block prospectively (Rigby re-dispatch confirms).

### §3.1 Check 1 — Evidence resolution (PASS)

Author-side verified: every bracketed citation in the 5 authored rules resolves to a manifest entry.

- §7.4.1 citations → C7-23 (RATIFICATION §5.2); C7-15 (f341581a); C7-16 (1176b67a); C7-13 (SESSION_2751_I0302_PHASE_4_CLOSED); C7-14 (SESSION_2751_I0302_ARC_CLOSED).
- §7.4.2 citations → C7-23 (RATIFICATION §5.4); C7-12 (SESSION_2750 §4); C7-13 (SESSION_2751_PHASE_4).
- §7.4.3 citations → C7-23 (RATIFICATION §5.5); C7-17 (7fe19a1c); C7-18 (d5e54777); C7-12 (SESSION_2750); C7-14 (SESSION_2751_ARC).
- §7.5.1 citations → C7-23 (RATIFICATION §5.1); C7-22 (I-030204 §4+§5+§9); C7-19 (f586a2cf); C7-20 (40f2bffc); C7-21 (f1cf8950); C7-11 (SESSION_2749); C7-12 (SESSION_2750).
- §7.6.1 citations → C7-23 (RATIFICATION §5.3+§10.1); C7-24 (ROS §2.7.1); C7-13 (SESSION_2751_PHASE_4 §SIGN); C7-14 (SESSION_2751_ARC §SIGN).

Reproducibility artifacts recorded at HEAD `ebf69e96`:

- `ls docs/handoffs/SESSION_2749_I0302_PHASE_4_SUB_PHASE_3_SUBSTRATE_LARGELY_CLOSED.md docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md docs/handoffs/SESSION_2751_I0302_ARC_CLOSED.md docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md docs/research/process/RESEARCH_OPERATING_SYSTEM.md` — all 7 files resolve.
- `git rev-parse --short f341581a 1176b67a 7fe19a1c d5e54777 f586a2cf 40f2bffc f1cf8950` — all 7 SHAs resolve at HEAD.
- `grep '^### 5\.[1-5]\|^### 10\.1' docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md` — all cited candidacy anchors (§5.1..§5.5, §10.1) resolve.
- `grep '^## §4\|^## §5\|^## §9' docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md` — §4/§5/§9 all resolve.
- `grep '^### 2\.7\.1' docs/research/process/RESEARCH_OPERATING_SYSTEM.md` — §2.7.1 resolves (line 639).

### §3.2 Check 2 — Terminology consistency (PASS)

New terms in v0.5, each defined at first use:

- **watchpoint / watchpoint-attestation SIGN** — §7.6.1 body ("numbered watchpoints (W1..Wn), each attesting a specific verification dimension of the close").
- **codification substrate** — §7.5.1 body ("AST conformance rule, endpoint sentinel, lint gate, migration guard, or comparable per-site enforcer").
- **REPORT-ONLY / BATCH-FIX / ENFORCEMENT-FLIP** — §7.5.1 body defines each inline as the three PR names in sequence.
- **COMBINED / SPLIT cadence** — §7.4.3 body defines each inline with selection criterion.
- **close-ceremony delivery bundle** — §7.4 preamble names the three bundle components (a)/(b)/(c).
- **partial activation** — Ch 7 frontmatter names the semantic (§7.4/§7.5/§7.6 authored; remainder deferred).

No term is redefined. No new term collides with a term used earlier in the Playbook.

### §3.3 Check 3 — Constitutional consistency (PASS)

- PLAYBOOK-7.6.1 EXTENDS PLAYBOOK-6.10.3 for the close-cycle scope only (per Q3 D-verdict, EXTEND not SUPERSEDE). ROS retains general SIGN methodology authority.
- PLAYBOOK-7.4.3 defers to PLAYBOOK-4.2.1 for cascade discipline. Ch 4's authority over the four-step cascade is preserved.
- Ch 7 remains labeled STUB in frontmatter (partial activation); §7.3 Extension deferred is NOT modified.
- MINOR bump per PLAYBOOK-10.5.1 admissible additions: new rules under existing chapters + new sub-sections. No new chapters, no removed rules, no reclassified rules.
- rule_count arithmetic: 196 + 5 = 201.
- Backward compatibility per PLAYBOOK-10.5.2: no existing rule's downstream applicability changes.

### §3.4 Check 4 — Cross-reference integrity (PASS)

- PLAYBOOK-6.10.3 (referenced from §7.6.1 body) exists in the ratified body — anchor stable.
- PLAYBOOK-4.2.1 (referenced from §7.4.3 body) exists in the ratified body — anchor stable.
- PLAYBOOK-7.4.1 forward-reference from §7.4.2 body ("consolidate ... under PLAYBOOK-7.4.1") is a same-amendment forward reference; resolves after this amendment ratifies.
- Manifest §10.1 table row anchor unchanged; §10.3 heading is new; §10.4 renumbered from old §10.3. TOC entry (§10 at line 63) references §10 by name-anchor — unaffected.
- Appendix D chain row for v0.5.0 references v0.4.1 as parent; matches top-frontmatter `parent_version`.

### §3.5 Check 5 — Citation completeness (PASS)

Every normative sentence in the 5 authored rules (PLAYBOOK-7.4.1/7.4.2/7.4.3/7.5.1/7.6.1) terminates with a bracketed evidence citation block. Preamble narrative in §7.4/§7.5/§7.6 is informative (no RFC-2119 keywords) and does not require citations per Chapter 0's interpretation of normative language.

### §3.6 Check 6 — Version consistency (PASS)

- Playbook top-frontmatter fields synced: `version` 0.5.0; `parent_version` 0.4.1; `git_tag` playbook-v0.5.0; `compatible_with` extended with "0.4.1"; `rule_count` 201; `rules_added_v0_5_0` list of 5.
- Title line synced: `# Donkey Betz Engineering Playbook v0.5.0`.
- Ch 7 frontmatter `Last substantive change: v0.5.0`; Rule ID range extended to PLAYBOOK-7.6.1.
- Appendix D v0.5.0 row present.
- Prior_ratification block updated to reference v0.4.1 SHA `0805a332` + content_hash + tag `playbook-v0.4.1`.
- Placeholder fields (`commit_sha`, `content_hash`, `deliverable_id`) follow Appendix D v0.1.0 pre-ratification pattern until commit + tag land.

### §3.7 Author verdict

Checks 1–6 recorded PASS. Amendment is verification-complete on the author side per PLAYBOOK-6.10.2 and is dispatched to SIGN (§4).

---

## §4. Rigby SIGN cycle (dogfooding PLAYBOOK-7.6.1 pre-ratification)

### §4.1 Turn 1 — initial watchpoint-attestation dispatch

**Dispatch (S2753, pin `pa-44541f01cbb14b46`):** 7 watchpoints (W1 chapter partial-activation semantics; W2 rule text RFC-2119 discipline; W3 evidence citation integrity for 5 rules; W4 manifest §10 additions; W5 Appendix D chain row; W6 cross-chapter constitutional consistency; W7 6-check author verification recorded). Full dispatch text at `/tmp/sign_dispatch_v05.md` (696 words; well under Rigby stall threshold).

**Rigby response:** W1..W6 PASS clean; W7 BLOCK.

- **W1 PASS** — Ch 7 frontmatter "STUB (v0.1). Partial activation at v0.5.0 (§7.4/§7.5/§7.6 authored); remainder deferred to v0.6+ MINOR amendments" correctly names partial activation without over-committing STUB retirement. PLAYBOOK-7.3.1 unmodified. Ch 7 rule count 3 → 8 arithmetic clean.
- **W2 PASS** — RFC-2119 keyword usage precise in all 5 rules; scope tight; no cross-arc/session-open overreach; no internal contradictions; 7.6.1 EXTEND-not-SUPERSEDE language satisfies Q3. **Non-blocking NIT** (readability): consider splitting the "SIGNALS… MUST trigger…" sentence in 7.4.2. — Author declined; sentence has exactly one MUST keyword per PLAYBOOK-0.3 and Rigby herself confirmed the readability nature. No change applied.
- **W3 PASS** — All citations resolve to C7-11..C7-23 (new) or pre-existing manifest entries (e.g., ROS §2.7.1 via §14.7 peer-OS + C2-1). **Non-blocking LOW** (auditability): make ROS §2.7.1 an explicit Ch 7 manifest entry to reduce external-hop friction. — Author applied. Added C7-24.
- **W4 PASS** — 13 entries C7-11..C7-23 enumerated; class labels match §0 taxonomy; RATIFICATION envelope §5 exists; §2.1 line 106 permits post-v0.1 manifest revisions. **Non-blocking NIT** (clarity): add a "frozen for v0.5" lockbox note in §10.3. — Author applied.
- **W5 PASS** — Appendix D row correct: parent v0.4.1; MINOR warranted; rule delta 196→201; placeholder pattern matches v0.1.0 precedent. **Non-blocking LOW** (consistency): consider whether `version_status: ratified` should stay `draft` / `pending-ratification` until commit + tag + deliverable_id fill. — Author applied. Flipped to `pending-ratification`.
- **W6 PASS** — 7.6.1 EXTEND vs 6.10.3 does not create shared-authority contradiction (close-cycle scope only); 7.4.3 defer to 4.2.1 preserves Ch 4 authority; `compatible_with` correctly includes "0.4.1".
- **W7 BLOCK** — no traceable recorded 6-check verification artifact at HEAD `ebf69e96`. Blocker per PLAYBOOK-6.10.2 which requires author-side verification recording BEFORE SIGN dispatches.

**Resolution:** author recorded the 6-check verification into this ratification envelope §3 (this file). Non-blocking asks W3/W4/W5 applied inline before re-dispatch. W2 NIT declined with rationale recorded.

### §4.2 Turn 2 — resolution ping (pending)

Re-dispatch to Rigby: confirm §3 satisfies the recording obligation for W7 and confirm W3/W4/W5 asks are addressed. Awaiting Rigby second-turn attestation.

### §4.3 SIGN outcome (final)

Filled at re-dispatch resolution: W1..W7 PASS status; F-BLOCKING count; non-blocking ask disposition matrix; final SIGN classification per PLAYBOOK-6.10.3.

---

## §5. Chris D-verdict

**Verdict:** `"agree all"`
**Recorded:** 2026-07-11 S2753 (terminal-side D-verdict; routing preference stated inline — see §5.1 workflow directive).
**Ratifier:** Chris (System Owner).
**SIGN outcome at time of verdict:** W1..W7 PASS, zero F-BLOCKING, W3/W4/W5 non-blocking asks applied inline, W2 NIT declined with rationale.

### §5.1 Workflow directive recorded at D-verdict

Chris directive at v0.5.0 ratification, verbatim: *"Going forward you and Rigby needs to have come to an agreement and then I will either yes or no it."*

**Semantic:** Claude (drafter) and Rigby (SIGN reviewer) MUST reach agreement on any decision-carrying artifact — SIGN outcomes, non-blocking-ask disposition, watchpoint blockers, workflow choices — BEFORE routing to Chris. Chris's role is binary ratification (yes / no) of the pre-agreed joint proposal. Claude MUST NOT surface Rigby's opinion to Chris as a decision menu for Chris to resolve; Claude MUST NOT surface a decision to Chris while Rigby's SIGN still contains unresolved F-BLOCKING or unaddressed non-blocking asks that Claude would want Chris to decide on.

**Candidacy:** codify as a Playbook rule under a future MINOR amendment (candidate slot: §5 PA / Rigby Collaboration STUB activation, or §7.6 close-cycle SIGN extension). Two-trigger threshold not yet met (first trigger: this ratification). Do NOT propose codification until a second independent trigger surfaces.

**Provenance:** recorded verbatim per PLAYBOOK-0.3 "System Owner directive recorded verbatim" pattern (established at CD-47 in v0.1.0 authoring).

---

## §6. Post-ratification bindings

Filled at commit + tag + workspace registration:

- `head_at_ratification`: TBD
- `close_pr`: TBD
- `workspace_ratification_deliverable_id`: TBD (workspace deliverable UUID in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`)
- Playbook top-frontmatter `commit_sha` / `content_hash` / `ratification_record.deliverable_id` placeholders replaced with the concrete values.
- Appendix D row updated if any placeholder fields adopt concrete values.
- CLAUDE.md L7 anchor line refreshed to reference v0.5.0 as the latest ratified version, with v0.1.0/v0.2.0/v0.3.0/v0.4.0/v0.4.1 ancestry preserved.
- `MEMORY.md` project state entry for `project_playbook_v0_1_0_ratified.md` updated to point at v0.5.0 as current, with the v0.1.0 record marked historical.
- 4-step docs cascade (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `sync_docs_index_to_documents --embed`) run; chunk count reported in the close-bundle PR body per feedback rule.
- `build_docs_provenance` run to refresh cascade provenance graph.

---

## §7. Downstream unlocks

Ratification of v0.5.0 authorizes:

- Immediate application of PLAYBOOK-7.4.1/7.4.2/7.4.3 to any future phase or arc close in the RUR program (starting with I-0303 close).
- Immediate application of PLAYBOOK-7.5.1 to any future codification substrate that flags existing sites at HEAD.
- Immediate application of PLAYBOOK-7.6.1 to phase-close and arc-close SIGN cycles (self-referential: this ratification's SIGN cycle already dogfoods the shape pre-ratification).
- Ch 7 partial activation precedent for future STUB chapter activations (Ch 2/3/4/5/8/9) — same shape available as reference.
- Removal of the "close-ceremony delivery discipline" from the S2751 arc-close open candidacy queue; the 5 candidates transition from candidacy to codified.

---

## §8. Provenance chain

- **Ratification of candidacy** — `RATIFICATION_2026-07-10_i0302_arc_close.md` §5 (Chris D-verdict 2026-07-10 S2751; candidacy only, NOT codification).
- **Stage 1 shape ratification** — `docs/research/platform/playbook_v0_5_proposal_shape.md` (Chris D-verdict 2026-07-11 S2752 close; Q1..Q5 all ratified with "agree all"; shape doc ratified as frozen).
- **Stage 2 authoring** — Claude, S2753, HEAD `ebf69e96`, playbook body + manifest + this ratification envelope.
- **Stage 2 6-check verification** — Author, S2753, §3 above (PASS on checks 1–6).
- **Stage 2 SIGN** — Rigby, S2753, §4 above (pin `pa-44541f01cbb14b46`; watchpoint-attestation W1..W7).
- **Stage 2 D-verdict** — Chris, S2753 (pending at authoring; §5 above).
- **Stage 2 body commit + tag** — S2753 close-bundle PR (pending Chris D-verdict); tag `playbook-v0.5.0` at merge.
- **Stage 2 workspace ratification** — Rigby, S2753 (deliverable_id TBD; workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`).
- **Stage 2 L7 anchor refresh** — Claude, S2753 close (in close-bundle PR).
- **Stage 2 docs cascade** — Claude, S2753 close (4-step + `build_docs_provenance` per memory rule).

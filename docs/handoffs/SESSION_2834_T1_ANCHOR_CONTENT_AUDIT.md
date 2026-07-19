---
title: "S2834 — T1 anchor content audit RATIFIED (child audit 2801 · schema v1.1 locked)"
session: 2834
date: 2026-07-19
status: shipped
research_group: 2800
thread: T1
sign_pin: pa-5fa195547db04260
sign_cycles: 3
ratifier: Chris
verbatim_directive: "ratify T1 as-is + schema v1.1"
---

# S2834 — /docs/ Content Audit · T1 anchor & canonical-doc audit RATIFIED

## 1. Session opener

Chris opened S2834 with "Please begin" per session brief. Per
`context-kit orient` + S2833 close pointer, this session had a ratified
default direction from Chris's S2833 D-verdict: *"ratify D1-D9, open T1
next session."* Sanity checks all green at open:

- pg15 (donkeyking) started
- HEAD `34f701c66605` (S2833 close cascade merged as PR #3279)
- Backfill: 0 mismatches (13 out-of-scope per Chris D6, unchanged)
- Pattern C top-1: `00-START-NEXT-SESSION.md` → `self_reference` ✅
- Pattern B top-1: `docs/PLATFORM_INVENTORY.md` → `count` ✅
- S2831 diagnostics endpoint: `matched_patterns: ['self_reference']` ✅
- Parity harness + registry + diagnostics: 47 passed in 191.6s ✅

Candidate menu presented per `feedback_engineering_bias_over_audit` —
listed net-new engineering pivots alongside the ratified T1 default.
Chris picked T1.

## 2. Ship

| Focus | Artifact | Location |
|---|---|---|
| T1 child audit (33-file classification + schema v1.1 spec) | New | `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md` (1305 lines, status ratified) |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 1→2 of 6 shipped) |
| S2834 handoff | New | This file |
| S2835 pointer | Updated | `00-START-NEXT-SESSION.md` — recommended default = T2 reference-graph audit |

## 3. What T1 caught

### 3.1 Verified drifts (in migration queue)

| Sev | File | Finding |
|---|---|---|
| **P0** | `CLAUDE.md:262` | *"Discord bot: 144 commands across 25 Cogs"* — contradicts linked `DISCORD_INTEGRATION.md` line 7 which explicitly documents the S1115 correction (144 was regex double-count; correct is 96 total = 48 slash + 48 prefix) AND CLAUDE.md's own live autogen block line 148 (which shows 96). Root-stability P0 per §10.4 (b) — blocks in-place remediation, not migration. |
| P1 | `docs/KNOWLEDGE_PIPELINE.md:25` | ASCII diagram: `SPIDER NETWORK (64 spiders)` — runtime is 80. Diagrammatic count on a runtime-flow anchor is exactly the P1 shape. |
| P1 | `docs/topics/personal-assistant.md:6,12,13` | Stale runtime counts: `104 schemas + 169 handlers` → live 113 + 156; separate line "152 tool handlers" → 156. DOC-POINTER-V1 banner IS present but bold-count prose overrides visually. Catches the topics-heterogeneity concern that motivated Rigby Q1 STRENGTHEN. |
| P1 | `docs/AGENTS.md` + `docs/SPIDERS.md` | CLAUDE.md self-flags them as "stats may drift" but neither carries a DOC-POINTER-V1 banner at file top — direct-visit readers get no disclaimer. Retrofit V1 banner. |
| P2 | `docs/DISCORD_INTEGRATION.md:321` | *"Currently at 112"* global slash commands — actual runtime 48 `@app_commands.command`. Note: this doc was OK-verified on the S1115 correction (line 7); the drift is elsewhere in the doc. |
| P2 (×9) | 8 large refs + refresh cadence banner | `coverage: structural_only` — schema-validation-first-pass classified without deep claim walks (would take 2-3 sessions per §5.5 migration waiver rationale). Includes ARCHITECTURE.md 867L / AGENTS.md 1685L / SERVICES.md 834L / DATABASE_MODEL_REFERENCE.md 636L / DREAM_INITIATIVE_WORKFLOW.md 1068L / ADVISOR_AUDIT.md 643L / DISCORD_AUDIT.md 323L / governance_redesign.md 363L / ARCHITECTURE_INDEX.md 4885L. |

Migration queue routed to future §3 execution arc (opens after 2899).

### 3.2 Schema v1.1 refinements (locked)

All backward-compatible under permissive YAML parsing; strict-parser
consumers opt in via `schema_version: 1.1` frontmatter key.

| Field | Default | Origin |
|---|---|---|
| `schema_version: 1.1` (frontmatter) | absent = v1.0 | Rigby cycle-2 Q6 + cycle-3 Q11 STRENGTHEN — frontmatter-level, single source of truth, no per-row tag |
| `claim_source: manual \| autogen` | `manual` | Rigby cycle-1 Q2 — pulled out of `finding_class` enum (keeps enum stable per cycle-2 Q6 caveat) |
| `finding_state: active \| resolved` | `active` | Rigby cycle-1 Q3 **DISAGREE** — histograms count active only; prevents "was P0, now ok" polluting severity axis |
| `coverage: full_claim_walk \| structural_only \| deferred` | `full_claim_walk` | Rigby cycle-1 Q5 + cycle-2 Q9 STRENGTHEN — contract-level, not free-text notes |
| `claim_density_hint: dense \| sparse \| large_ref_deferred` | absent | Rigby cycle-1 Q2 STRENGTHEN — explains why a pass did/didn't exhaustively claim-walk |
| Whole-doc convention | `line_range: [1, N]` | Rigby cycle-1 Q2 |

**§10.4 root-stability P0 clarification** (Rigby cycle-2 Q7 STRENGTHEN):

> P0 blocks: (a) destination-subdir migration for migration-eligible
> files, (b) in-place remediation before arc close for root-stable /
> NEVER-MOVE files.

**§5.5 migration-arc waiver protocol** (Rigby cycle-2 Q9 STRENGTHEN):

> Any file being MOVED / SUPERSEDED by the §3 migration arc MUST carry
> either (a) `coverage: full_claim_walk`, OR (b)
> `coverage: structural_only` PLUS `recommended_action: escalate_to_chris`
> PLUS explicit `notes:` rationale for why full walk was skipped.
> In-place-only files (rule / policy / NEVER-MOVE) can carry
> `structural_only` without the waiver — because they aren't
> migration-touch-point candidates.

**§4.1a T3a pre-scan hint** (Rigby cycle-2 Q8 STRENGTHEN):

Topics/ heterogeneity signal — some carry live count drift
(personal-assistant), others don't (agent-system). T3a should
lightweight-tag topics as `count_dense` vs `narrative` BEFORE dup
detection. Grep patterns recorded (`\*\*Current runtime counts` bold
pattern; `\b\d+\b\s+(agents|tools|handlers|spiders|services|models)`).
Deferred to T3a author.

## 4. Rigby SIGN provenance (3 cycles)

| Cycle | Q# | Tool_runs verified? | Verdicts |
|---|---|---|---|
| 1 | Q1..Q5 | ✅ 6 substantive `repo_tool.read` | 4 STRENGTHEN + 1 DISAGREE (Q3) + 1 AGREE |
| 2 | Q6..Q10 | ✅ 5 substantive `repo_tool` | 4 STRENGTHEN + 1 AGREE (Q10 lock v1.1) |
| 3 | Q11..Q13 | ✅ 5 substantive `repo_tool` (incl. `search`) | 1 STRENGTHEN + 2 AGREE |

Anti-rubber-stamp discipline verified across all 3 cycles per
`feedback_verify_rigby_tool_runs_before_trusting_sign`. Convergence
reached at cycle 3 (all AGREE/STRENGTHEN, 0 DISAGREE). Joint
Claude+Rigby agreement per `feedback_claude_rigby_agree_first_chris_yes_no`
before Chris D-verdict.

## 5. Arc state at S2834 close

- **Group 2800 /docs/ content audit arc**: 2 of 6 shipped
  (parent + T1). T2 opens at S2835.
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817; §3 target
  tree RATIFIED at S2832; §7 anchor updates + §8 follow-on queue
  DEFERRED. Unchanged.
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D +
  DORMANT registry Step 1 + user-facing diagnostics tab all intact.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

## 6. Follow-up work carried

### 6.1 T2 opens at S2835 (recommended default)

- Author `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`
- Scope: relative-path links, ADR references, session-handoff cross-refs,
  file-path citations across all in-scope files
- Method: mechanical grep + resolver; classify PASS / 404 / renamed /
  ambiguous
- Emit v1.1 findings per §10.1 schema locked at S2834
- Rigby joint SIGN + Chris D-verdict

### 6.2 T3a topics pre-scan hint (recorded, not executed)

Per §4.1a — T3a author picks up the `count_dense` vs `narrative`
tagging pattern.

### 6.3 Migration queue (deferred to future §3 execution arc post-2899)

Per §10.1 v1.1 schema, batched by `migration_pr_batch_hint`:

- `anchor_docs` batch: CLAUDE.md line 262 P0 fix; KNOWLEDGE_PIPELINE
  line 25 P1 fix; DISCORD_INTEGRATION line 321 P2 fix; AGENTS/SPIDERS
  V1 banner retrofit; PLATFORM_WHAT_IT_IS refresh-cadence banner
  candidate; README maintenance policy escalation
- `topic_docs` batch: topics/personal-assistant.md V1 banner reinforcement
- `schema_validation` batch: 3 escalate_to_chris items about future
  schema refinements

### 6.4 Chris directives requested (per §4.3)

- Refresh cadence policy for anchor docs vs reference-graph docs
- Root README.md in-scope for anchor-doc refresh cadence?
- Should Employee OS count be added to `refresh_doc_inventory_blocks`
  autogen set?

## 7. Lessons to carry (also in §5 of the T1 doc)

1. **Verify tool_runs non-empty is not a check-box — it's a gate.** Rigby
   cycle-1 Q3 DISAGREE would not have surfaced under rubber-stamp
   discipline. Class-P0-status-ok recording IS histogram pollution.
2. **Anti-worship discipline (Rigby Q10 AGREE lock v1.1)**: schema
   refinements were justified by observed failure modes surfaced in the
   T1 pass (canary caught real drift; CLAUDE.md P0 needed stable blocking
   semantics). Not gold-plating; not scope creep. Lock at close, defer
   further embellishments to `future_trigger` at 2899.
3. **Small canary corpus catches heterogeneity signals.** 2 topics added
   at cycle-1 Q1 — 1 stale (PA), 1 clean (agent-system) — validated
   the T3a pre-scan hint. Two files did more diagnostic work than 20
   would have.
4. **Backward compat = schema versioning discipline.** Under permissive
   parsing, all v1.1 additions are safe; under strict schema, they'd
   break. Fix = frontmatter `schema_version` key, not per-row tags.
5. **Coverage contract > free-text notes.** `structural_only` as a
   contract-level field is enforceable; "recommend claim-density walk"
   as free-text notes is not.

## 8. DO NOTs to carry to S2835

Per parent §7 anti-scope + child inheritance:

1. **DO NOT execute any /docs/ file operations during Group 2800.** Same
   discipline as S2833. Classification only.
2. **DO NOT modify §10.1 v1.1 schema without fresh SIGN + D-verdict.**
   Locked at S2834.
3. **DO NOT collapse T3a/T3b back into single T3** — S2833 Rigby cycle-1
   Q1 STRENGTHEN evidence stands.
4. **DO NOT expand T4 into per-handoff content review.** Quarantined by
   S2833 D4 refinement.
5. **DO NOT reduce §10 P0..P3 severity or 8-action taxonomy.** Locked at
   S2833 D9.
6. **DO NOT audit in-flight arc children** (per parent §7 anti-scope).
7. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without
   fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary.
8. **DO NOT couple new observability surfaces to log capture** — S2831
   Rigby Q2 substrate rule.
9. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary.
10. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract.
11. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure.
12. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant.
13. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred.
14. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards.
15. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary.
16. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4.

## 9. Twin-pointer artifacts

📁 **Repo — S2834 artifacts:**

- T1 audit doc (RATIFIED): `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`
- Ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md`
- Handoff: this file
- Arc registration: `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 2/6 shipped)
- Rigby SIGN conversation: `pa-5fa195547db04260` (3 cycles preserved before retirement)
- Merge SHA: filled at close-cascade PR merge

🖥️ **Workspace UI — S2834 twin-pointer workspace deliverables:**

- Content mirror + Ratification envelope: mint at close cascade in Donkey
  Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), ORM-direct
  create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`;
  category `governance`; `deliverable_type=ratification_record`;
  `diagnostic_status=None`.

## 10. Provenance

- **Session:** 2834
- **Author:** Claude Code + Rigby (joint SIGN 3 cycles) + Chris D-verdict
- **Pin history (S2834):**
  - `pa-5fa195547db04260` (label `s2834-t1-anchor-content-audit`) minted at S2834 open; served as session pin + arc SIGN pin (3 cycles preserved for future arc reference); retired at S2834 close with `force=true` (sixty-fifth consecutive per S2770+ pattern)
- **HEAD at author time:** `34f701c66605`; HEAD at ratification: filled at cascade merge
- **Playbook version:** v0.8.0 (unchanged; 205 rules)
- **Post-merge recycle:** `make recycle-all` per PLAYBOOK-7.4.4 (eightieth consecutive close-cycle)

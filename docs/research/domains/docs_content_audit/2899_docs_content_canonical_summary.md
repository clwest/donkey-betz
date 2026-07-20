---
title: "S2840 /docs/ Content Audit — Canonical Summary (Group 2800 arc close)"
status: ratified (Chris D-verdict 2026-07-19 S2840; Group 2800 arc RATIFIED at close)
ratification:
  date: 2026-07-19
  session: 2840
  ratifier: Chris
  scope: 206-row Chris judgment queue disposition (D1) + §10.1 v1.2 schema batch (D2/D3) + Playbook v0.9 amendment candidates queue (D4) + post-2899 execution arc scoping + guardrails (D5)
  record: docs/research/implementation/RATIFICATION_2026-07-19_2899_docs_content_canonical_summary.md
  chris_directive_verbatim: "Approved"
  sign_cycles: 3 (AEP v0.1 Stage 2 default mode; cycle 1 F1-F3 folds + cycle 2 F4-F7 folds + cycle 3 fully-clean 5/5 AGREE ARS-VERIFIED)
authority: canonical summary for Group 2800 arc (closes 6-thread child-audit set T1-T5, arc COMPLETE 7/7)
session: 2840
date: 2026-07-19
domain_slug: docs_content_audit
research_group: 2800
child_slot: canonical-summary
authors: Claude Code (Chris directed at S2840 open); Rigby (SIGN cycles + workspace mirror + coherence-check)
supersedes: none
related:
  - docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md   # parent (D1-D9 ratified S2833)
  - docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md          # T1 (S2834)
  - docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md         # T2 (S2835)
  - docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md        # T3a (S2836)
  - docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md          # T3b (S2837)
  - docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md          # T4 (S2838)
  - docs/research/domains/docs_content_audit/2805_docs_content_reports_audits_triage.md   # T5 (S2839)
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md # Group 2700 predecessor arc (§3 target tree ratified S2832)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                              # §11.3 canonical summary template
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                                    # §2b/§2c/§3 constraints respected
  - docs/PLATFORM_INVENTORY.md                                                             # runtime counts anchor (referenced, not restated)
  - docs/PLATFORM_WHAT_IT_IS.md                                                            # narrative anchor
  - docs/ENGINEERING_PLAYBOOK.md                                                          # v0.8.0 (v0.9 amendments enumerated in §10.2)
  - CLAUDE.md                                                                              # repo bootstrap
twin_pointer:
  workspace_deliverable_id: TBD (Rigby-created at close per feedback_rigby_writes_workspace_deliverables)
  workspace_id: b4503364-2573-4401-9e28-61a739e0ce50
  workspace_name: Donkey Betz
  created_via: TBD (Rigby default; ORM fallback only if payload exceeds tool cap per feedback fallback clause)
scope: canonical summary for Group 2800 arc — synthesizes T1-T5 findings into (a) 206-row Chris judgment queue disposition, (b) §10.1 v1.2 schema batch outcomes, (c) Playbook v0.9 amendment candidates, (d) post-2899 execution arc scoping
non_goals:
  - re-authoring T1-T5 findings (canonical summary synthesizes; does not re-audit — per Playbook §10)
  - implementation / migration execution (post-2899 execution arc per §8)
  - Playbook v0.9 amendment authoring (separate arc; §10.2 flags readiness)
  - new taxonomies beyond what T1-T5 established + 5-class unified disposition proposed in §3
  - file moves / deletes / renames / edits during arc-close session (parent §5 non-goals)
delegates_to:
  - post-2899 execution arc (§3 target-tree migration + disposition-class rollout per §8)
  - Playbook v0.9 amendment arc (per §10.2 codification candidates)
owner: claude+rigby (closed as arc-close per parent §5 D6)
---

# Group 2800 /docs/ Content Audit — Canonical Summary

> **What this doc is.** Arc-close canonical summary for Group 2800 /docs/ content audit. Synthesizes T1-T5 findings (2801/2802/2803a/2803b/2804/2805) into (a) ratified 5-class disposition for the 206-row Chris judgment queue, (b) §10.1 v1.2 schema batch outcomes, (c) Playbook v0.9 amendment candidates, (d) post-2899 execution arc scoping. **Twin-pointer:** this repo doc + workspace deliverable in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) per parent §5 D7 + feedback_twin_deliverable_at_every_ratification.
>
> **What this doc is not.** Another audit. New evidence sweep. Migration execution. Playbook amendment authoring. Per-file re-classification.

---

## 1. Executive Summary

Group 2800 arc opened at S2833 to answer: *given the S2832-ratified /docs/ target tree, does the CONTENT of the ~1842 in-scope files survive a move to that tree?* Arc structured as 6-thread package (T1 anchors + T2 refs + T3a duplicates + T3b orphans + T4 handoff-citations+retrieval-harm + T5 reports+audits triage). Arc reached **7/7 shipped** at S2839; canonical summary opens S2840.

**Headline findings:**

| Dimension | Result |
|---|---|
| P0 count (root-stability breaches) | **0** across all 5 children (six null-result observations if T5 P1 counted separately) |
| P1 count (real, action-required) | **8** total (1 T3b + 1 T2/T1 shared + 6 T4 broken path-form citations) |
| P2 count (escalate + non-P0/P1) | **~200** across all children |
| Total escalate queue → 2899 workshop | **206** rows (T3a 2 + T3b 75 + T4 22 + T5 107) |
| Cross-cutting patterns identified | **5** (three at ≥2-trigger codification threshold; two single-arc) |
| §10.1 v1.2 schema candidates | **5** (2 recommended ADOPT + 3 DEFER) |
| Playbook v0.9 amendment candidates | **4** (all at ≥2-trigger threshold; ready for v0.9 arc) |
| Migration-PR batch shapes | **5 disposition classes** unified across all children |

**Chris judgment scope at 2899 workshop:** batch-ratify the 5-class disposition (approving batches N-1, N-2, N-3, N-4) + walk case-by-case exceptions (~30-40 rows) + ratify §10.1 v1.2 batch outcomes + ratify Playbook v0.9 amendment queue.

**Post-2899:** §3 execution arc opens with the 5-class disposition + optional Playbook v0.9 small-fix whitelist authorization enabling deterministic small-fix batching.

### 1.1 Chris decision checklist (Rigby cycle-2 Q5 F5 SPM — workshop ergonomics)

Live workshop decisions Chris ratifies at this session. Sub-justifications live in later sections; this checklist is the *decision surface*.

| # | Decision | What changes | Why | What could go wrong | What would change my mind |
|---|---|---|---|---|---|
| D1 | Ratify 5-class disposition (§3) | 206 rows split into 5 batches; post-2899 execution arc opens with these batches as first-class inputs | Chris judgment on 206 individual rows would take multiple sessions; batching preserves per-child ratified findings while unblocking execution | Class predicate may not hold under execution (a row's true disposition differs from batch classification); mitigated by §8.1 execution-arc preflight + interruptible-execution stop-conditions | Evidence that per-child batch classes don't compose cleanly OR that Class 5 case-by-case count would exceed ~40 rows |
| D2 | Adopt v1.2 candidates 1 (`citation_style`) + 3 (`null_result`) — §Appendix 12.1 | §10.1 schema advances to v1.2; future audit arcs use additive fields | Both meet Playbook §20 threshold (2 + 4 triggers respectively); adoption is additive so v1.1 rows remain valid | Field-name collision with future Playbook v0.9 rules; mitigated by v0.9 arc reviewing field-name space | Field semantics disagreement between T4 and T2 formulations of `citation_style` |
| D3 | Defer v1.2 candidates 2 + 4 + 5 — §Appendix 12.1 | These candidates re-consider at next corroborating arc | Threshold not met (1-trigger + 1-trigger + 2-sub-triggers-within-single-arc); premature codification risk | Deferred candidates may accumulate long enough to lose live signal; mitigated by §8.3 future-arc triggers being crisp | Second-arc corroboration surfaces sooner than expected |
| D4 | Queue 4 Playbook v0.9 amendment candidates — §10.2 | Post-2899, dedicated Playbook v0.9 amendment arc opens; 4 [GR] rules join Playbook | Cross-child pre-clustering (4 triggers) + null_result (4 obs) + ambiguous-as-first-class (3 triggers T5-internal) + small-fix whitelist (1-2 triggers, §20 clarification needed) are the ratified codification-ready candidates | §20 threshold-applicability question (§10.4 candidate 1 clarification) not yet resolved; mitigated by handling in v0.9 arc | Chris disagrees with Rigby's §20 clarification framing OR wants candidate 4 (whitelist) authored differently |
| D5 | Endorse post-2899 execution arc §8.1 sequencing + Rigby cycle-2 STRENGTHENs (execution-arc preflight + interruptible execution + preflight-sample-per-class) | Execution arc opens with Class 4 (6 rows) → preflight → Class 2 → Class 3 → Class 1 → Class 5 | Small-first-mechanical sequencing unblocks fastest; preflight ensures no "archive active output" mishap | Whitelist ratification lag from Playbook v0.9 arc; mitigated by Class 4 being whitelist-independent | Whitelist arc slips; execution arc adopts conventional PRs for Classes 2/3 |

### 1.2 Section-scope labels (Rigby cycle-2 Q5 F4 SPM — scope-coupling mitigation)

To prevent 2899 being cited as precedent in contexts it wasn't designed to govern, sections are labeled:

- **[DESCRIPTIVE]** — what's true / already ratified by this arc's children; not adjudicated in this doc
- **[RATIFIED]** — Chris ratifies at 2899 D-verdict (this session)
- **[ADVISORY]** — queued for future arc (Playbook v0.9, execution arc, or future single-corpus arc); not authoritative at this doc
- **[EXECUTION-GATED]** — requires next-arc validation before authoritative treatment

Section-by-section label map appears at each §-header below.

---

## 2. What This Arc Answered [DESCRIPTIVE]

### 2.1 D1-D9 arc-parent decisions (all ratified S2833)

| D# | Decision | Ratified state at S2839 close |
|---|---|---|
| D1 | Content-audit arc opens at S2833 | ✓ opened |
| D2 | Arc group number = 2800 | ✓ |
| D3 | Folder = `docs/research/domains/docs_content_audit/` | ✓ |
| D4 | 6 threads (T1 anchors / T2 refs / T3a duplicates / T3b orphans / T4 handoffs+retrieval / T5 reports+audits) | ✓ all 6 shipped |
| D5 | Non-goals hard-line defer (no moves / deletes / renames / edits / code changes during arc) | ✓ zero in-arc file operations |
| D6 | Canonical summary at 2899 = ratified content-audit output | ✓ this doc |
| D7 | Twin-pointer discipline for arc close | ✓ pending workspace mirror at close |
| D8 | Session-count ≥ 6 sessions | actual 7 (S2833-S2839) |
| D9 | Output = machine-consumable per-file classification schema (v1.1 locked S2834) | ✓ v1.1 unchanged; 5 v1.2 candidates for §10.1 batch |

### 2.2 Per-child completion state

| Child | Session | Corpus | P0 | P1 | Escalate → 2899 | Method |
|---|---|---|---|---|---|---|
| T1 (2801) | S2834 | 33 (anchors + canon + governance + onboarding + root + CLAUDE.md graph + research-OS + topics canary) | 0 | 1 (SESSION_1099 in refresh-block) | 0 | per-file walk of concrete claims vs HEAD |
| T2 (2802) | S2835 | 793 (docs/** non-handoff + 3 root anchors) | 0 | 1 (shared w/ T1 P1) | 0 | mechanical grep + resolver over 4 ref classes → 26,900 refs |
| T3a (2803a) | S2836 | 792 | 0 | 0 | 2 (canonical-ambiguous SYSTEM_ARCH_MAP + CLAUDE_CONTEXT_SYSTEM_PACK) | token-shingling + Jaccard + containment |
| T3b (2803b) | S2837 | 793 | 0 | 0 (README.md separately handled) | 75 | 3-graph reachability BFS (CLAUDE.md + INDEX + Document corpus) |
| T4 (2804) | S2838 | 1061 (handoffs + persistent-reference) | 0 | 6 (broken path-form citations) | 22 (6 P1 + 13 retrieval-harm banner + 3 fragment) | citation-graph decay curve + fragment resolution + retrieval-harm probes |
| T5 (2805) | S2839 | 169 (audits + audit-2026 + audit + reports + docs/*_AUDIT.md) | 0 | 0 | 107 | 4-axis triage (shape × reachability × staleness × pointer) + 8-action derivation |

**Zero P0 across all 5 children.** Root-stability gate holds; DOC_LIFECYCLE §2b/§2c/§3 constraints preserved throughout arc.

### 2.3 Arc process telemetry (for §10 meta-methodology)

- **Cross-child pre-clustering consumption chain: 4 triggers** (T3a←T2, T3b←T3a+T2, T4←T2+T3b, T5←T3b+T4-informational). Playbook v0.9 codification threshold met.
- **`null_result` finding class: 4 observations** (T3b §2.1 + T4 §2.4 + T5 §2.1 P0 + T5 §2.1 P1). Playbook §11.3 template codification threshold met.
- **Anti-rubber-stamp SIGN verified 6/6 arc-wide** (per feedback_verify_rigby_tool_runs_before_trusting_sign): each child SIGN cycle produced ≥1 real STRENGTHEN or DISAGREE with tool-grounded evidence.
- **AEP v0.1 Stage 1 trial → Stage 2 authorized at T5** (S2839 Chris D-verdict `"Approve, let me know if you have Rigby draft the routing note"`).
- **§10.1 v1.1 schema unchanged across full 6-child arc.** 5 v1.2 candidates accumulated for 2899 batch consideration (this doc).

---

## 3. Consolidated Domain Shape — 5-Class Disposition (206-row Chris Judgment Workshop) [RATIFIED at Chris D-verdict]

**Method proposed:** unify per-child batch classes into a single 5-class disposition taxonomy that covers all 206 escalate rows. Chris ratifies batches at class level; individual rows execute per-batch in post-2899 §3 migration arc. Case-by-case rows (Class 5) get Chris walk-through in this session.

**Per-class standalone framing (Rigby cycle-2 Q5 F7 SPM — future-discoverability):** each of §3.1-§3.5 includes definition + intent + risk paragraphs that stand alone. A future reader (6 months out) should be able to read a single §3.N block and reconstruct why the class exists + what it commits to + what could go wrong.

### 3.1 Class 1 — Series-level pointer propagation (`class_1_pointer_prop`)

**Definition:** files sharing a common historical-subdir or template-family origin, each with an escalate row for pointer absence, resolved via subdir-level or series-level V1/V2 pointer inheritance rather than per-file retrofit.

**Intent:** amortize discovery/pointer work across sibling files; one policy PR per subdir vs N per-file PRs. Preserves per-file identity while reducing execution work.

**Risk:** class assumes series-level inheritance is semantically valid — a subdir-level pointer must actually cover the semantics of every sibling. If any sibling has divergent content requiring individual pointer text, the batch classification is wrong for that row → surface at execution-preflight sample check (§8.1).

**Row scope: ~79 rows** = T5 §3.4 `audits_triage_series_pointer` (49) + T3b subset of orphan candidates matching series pattern (est. ~30 pending v1.2 candidate #5 ratification).

**Executable via:** small-fix whitelist bucket #2 (subdir-level index pointer additions) if Playbook v0.9 whitelist ratified.

**Chris batch decision requested:** ADOPT class-level batch treatment ✓ (Claude+Rigby joint recommendation). Whitelist eligibility follows §10.2 v0.9 arc outcome.

### 3.2 Class 2 — Archive candidates (`class_2_archive`)

**Definition:** pre-S2500 one-shot files with (a) session-tag pre-threshold + (b) `search_only` reachability + (c) zero inbound anchor citations. Historic snapshots that no active surface reads.

**Intent:** move to `docs/archive/2020/` (or equivalent) so search corpus stays lean + newer anchor structure is uncluttered by historical dossiers. Files remain readable at new path; discovery drops out of active navigation.

**Risk:** "no active surface reads" claim depends on reachability graph at 2899 time; if a new anchor gets added later that cites an archived path, that anchor breaks. Mitigation: `git mv` preserves history so retrospective ref-repair is possible. Second risk: active audit-runner (§6.3) still generating files → §8.1 execution-arc preflight verifies before archive.

**Row scope: ~40 rows** = T5 §3.4 `audits_triage_archive` (20) + T3b subset of unreachable candidates (est. ~20 conservative — final count derived at execution).

**Notable sub-cluster: SESSION_819_SYSTEM_AUDIT_* series** (19 files T3a-detected 2026-07-14 through 2026-07-16). T3a→T5 boundary rule invoked — T5 recommends archive; T3a defers to T5 disposition. **Chris exception check:** verify whether an audit-runner (SESSION_819) is still actively generating files; if so, PR should include runner-fix in addition to archive move.

**Executable via:** small-fix whitelist bucket #3 (pure `git mv`) if Playbook v0.9 whitelist ratified.

**Chris batch decision requested:** ADOPT class-level batch treatment ✓ (Claude+Rigby joint recommendation) + explicit note re SESSION_819 runner-fix inclusion.

### 3.3 Class 3 — V2 retrofit / V1 stats-drift banner (`class_3_pointer_retrofit`)

**Definition:** files with anchor citations (still-reachable) but with content that has drifted or is closed-arc terminal — retrofit with V2 pointer (`<!-- DOC-POINTER-V2 -->`) or V1 stats-drift banner rather than archive/edit.

**Intent:** preserve inbound citations (no ref-graph breakage) while telling readers where the current-truth version lives. V1 stats-drift banner is lighter (annotation + retention) vs V2 supersession (annotation + explicit successor).

**Risk:** wrong pointer choice — V1 stats-drift banner used where V2 supersession was appropriate (readers land on stale content thinking it's current) OR vice-versa (readers see V2 pointer + follow away from still-valid content). Mitigation: pointer choice ratified per row in execution-arc; whitelist bucket #1 mechanically inserts, doesn't decide policy.

**Row scope: ~49 rows** = T5 §3.4 `audits_triage_v2_retrofit` (18 = 13 anchor-reachable pre-S2500 in `docs/audits/` + 5 `SESSION_1143_*` in `docs/audit/`) + T4 §2.5 retrieval-harm banner candidates (13 P2 + SESSION_2759 added cycle-2) + T4 §2.6 fragment-form banner (3 P2) + T3b subset of stale-content candidates (est. ~15).

**Executable via:** small-fix whitelist bucket #1 (pointer header retrofit — exactly one `<!-- DOC-POINTER-V* -->` line, ≤15 added lines, 0 removed) if Playbook v0.9 whitelist ratified.

**Chris batch decision requested:** ADOPT class-level batch treatment ✓ (Claude+Rigby joint recommendation).

### 3.4 Class 4 — Ref-graph repair (`class_4_ref_repair`)

**Definition:** T4 P1 broken path-form citations (6 rows) — citing docs reference `docs/handoffs/SESSION_NNNN*.md` that doesn't exist. Requires code-touching edits (fix citing doc, not target) so cannot use whitelist. Post-2899 execution PR fixes per citing doc.

**Intent:** heal the ref-graph before further work is done on it. Smallest + most mechanical batch; unblocks other classes. Ratifies "no broken path-form citations" as post-execution-arc invariant.

**Risk:** three resolution paths exist per row (reconcile-basename / remove-reference / handoff-file-was-renamed) — automated PR cannot pick without per-row judgment. Mitigation: execution-arc PR presents each row with recommended resolution + 1-line reasoning; Chris ratifies inline (batch of 6 is small enough for line-level review).

**Row scope: 6 rows** (all T4 P1).

**Executable via:** conventional PRs (small-fix whitelist does NOT cover ref-source edits per whitelist safeguard #3 "no semantic edits").

**Chris batch decision requested:** ADOPT class-level batch treatment ✓ — assign to post-2899 execution arc as first PR (small, mechanical, unblocking).

### 3.5 Class 5 — Case-by-case (Chris walks)

**Definition:** rows where automated classification cannot resolve — canonical-ambiguous, cross-cutting policy questions, or subject-matter judgment.

**Intent:** preserve Chris judgment authority on decisions that require domain context beyond scanner reach. Sizing (~32 rows = ~16% of queue) is intentional cap: workshop is manageable within one session; if it grew past ~40 rows, batching methodology should re-examine what's escaping automation.

**Risk:** if Class 5 grows during execution (rows reclassify OUT of 1-4 into 5 upon closer inspection), workshop scope expands. Mitigation: execution-arc stop-condition (§8.1) — if >20% of sampled Class 1-4 rows escape to Class 5 during preflight, pause and re-triage.

**Row scope: ~32 rows** total. Explicit callouts:

| Source | Row | Nature | Recommendation shape |
|---|---|---|---|
| T3a §2.5 | `docs/SYSTEM_ARCHITECTURE_MAP.md` vs `docs/SYSTEM_MAP.md` | canonical-ambiguous (2 near-duplicate architecture maps) | Chris picks canonical + supersede sibling with V2 pointer |
| T3a §2.5 | `docs/CLAUDE_CONTEXT_SYSTEM_PACK.md` vs `docs/SYSTEM_FULL_ACTIVATION_PLAN.md` | canonical-ambiguous (2 near-duplicate system packs) | Chris picks canonical + supersede sibling with V2 pointer |
| T3b (subset) | ~10 orphan-candidate edge-cases not fitting Class 1/2/3 | mixed | Chris disposition per-row |
| T5 §3.4 `case_by_case` | 10 rows + 2 SESSION_819 ambiguous subcases | mixed (typically small-team-decision or historical-context) | Chris disposition per-row |
| T3b P1 (separate) | `README.md` cited-but-search-invisible | corpus-invisible root anchor | Chris ratifies corpus-inclusion policy for root README.md (in / out of embedded corpus) |

**Chris batch decision requested:** WALK each row this session ✓ (workshop shape).

### 3.6 Reconciliation

| Class | Row count | Approx pct |
|---|---|---|
| Class 1 pointer propagation | ~79 | 38% |
| Class 2 archive | ~40 | 19% |
| Class 3 pointer retrofit | ~49 | 24% |
| Class 4 ref-graph repair | 6 | 3% |
| Class 5 case-by-case | ~32 | 16% |
| **Total** | **206** | 100% |

Per-child breakdown: 2 T3a + 75 T3b + 22 T4 + 107 T5 = 206 (matches S2839 handoff claim).

---

## 4. Cross-Cutting Patterns

### 4.1 Cross-child pre-clustering consumption (4 triggers)

**Corroboration:** T3a §1.5 consumes T2 citation edges; T3b §1.5 consumes T3a V2-stub map + T2 RENAMED basename map; T4 §1.5 consumes T2 edges + T3b reachability; T5 §1.5 consumes T3b reachability + T4 basename-adjacency (T4 basename intersection was null-triggered per T5 §2.1 — informational only, no data cross-loaded).

**Status:** 4-trigger corroboration meets Playbook §20 two-triggers-across-arc-siblings threshold. Ready for Playbook v0.9 codification (§10.2 candidate 1).

**Design intent:** "each subsequent child MUST declare substrate consumption contract explicitly + report re-derivation vs load-only decision" — prevents redundant scan work + surfaces integration gaps early.

### 4.2 `null_result` finding class (4 observations)

**Corroboration:** T3b §2.1 (zero fully-unreachable files); T4 §2.4 (zero chunk-ID citations); T5 §2.1 P0 (zero P0 across corpus); T5 §2.1 P1 (zero P1 — second child achieving this).

**Status:** 4-observation corroboration meets Playbook §11.3 template amendment threshold. Ready for Playbook v0.9 codification (§10.2 candidate 2).

**Design intent:** "Null-result findings are first-class positive evidence — an audit measuring against a hypothesis and finding ZERO defects is a stronger structural-health finding than one finding many." Requires audit template to reserve explicit space for null-result reporting rather than implicit absence.

### 4.3 Pointer-on-INDEX-for-historical-subdirs convention (2 sub-triggers, 1 arc)

**Corroboration:** T5 §5.1 evidence 1 `docs/audit-2026/00-AUDIT-PLAN.md` V1 pointer for 13-file series; T5 §5.1 evidence 2 `docs/audits/INDEX.md` V1 pointer for historical archive; T5 §5.1 counter `docs/audit/README.md` NO pointer (active workspace — negative control).

**Status:** 2 sub-triggers within single child. Codification threshold **not yet met** per Playbook §20 default two-triggers-across-arcs. Recorded as §10.2 v1.2 schema candidate 5 (series-level inheritance field); DEFER for second-arc corroboration.

**Design intent:** where a subdir is historical, the subdir's own INDEX.md/README.md/00-*.md carries a series-level pointer describing supersession; individual files inherit rather than each requiring per-file retrofit.

### 4.4 Ambiguous-as-first-class (T5 internal 3 sub-triggers)

**Corroboration:** T5 §2.2 (81 of 169 files = 47.9% classified `ambiguous` on shape axis — genuine mixed-shape input); T5 §5.4 acceptance methodology; T5 §6.2 spot-verify (5 hand-checked ambiguous rows all classify correctly per axis-combination rules — not scanner defects).

**Status:** internally consistent (1 arc). Not yet cross-arc corroborated. Recorded for Playbook v0.9 consideration alongside cross-child pre-clustering.

**Design intent:** "Where a boolean-ish classification produces genuinely-mixed input class, emit third `ambiguous` value rather than force-picking. `ambiguous` is not scanner failure; it is honest triage output that routes to human judgment."

### 4.5 Bimodal-distribution shape signal (T5 single trigger)

**Corroboration:** T5 §5.8 — one-shot session-tag distribution bimodal [727, 1143] with zero in [1144, 2499], causing empirical threshold insensitivity when varying `stale_pre_s2500` threshold.

**Status:** single-arc single-child observation. Codification threshold not met. Cross-corpus recurrence *probable* (other u-d-b corpuses share non-uniform session-count velocity) but not yet documented. Recorded for future arc validation.

**Design intent:** "Future triage arcs SHOULD report both threshold sensitivity delta AND underlying tag distribution shape (min / median / max / any gaps) so 'robust threshold' claims can be interpreted correctly."

---

## 5. Resolved Contradictions

### 5.1 T2 raw BROKEN_404 count vs T4 filtered P1 count

**Contradiction:** T2 §2 reported 2,502 raw BROKEN_404 references (9.3% of 26,900); T4 §2.4 filtered handoff-scoped citations to 6 real P1 broken path-form.

**Resolution:** T2 methodology-note explicitly reserved FP-1/FP-2/FP-3 filter application to per-child specialized scans (T4 for handoff scope). T4 filter reduced 23 raw handoff-relevant hits to 6 actionable P1 via prose-mention exclusion. Not a contradiction; layered methodology.

### 5.2 T3a "173 P1 pairs" vs T5 "SESSION_819 archive-recommend"

**Contradiction:** T3a §2.3 P1 counts include SESSION_819 cluster as 171 pairs; T5 §3.4 recommends SESSION_819 archive as batch of 19 files.

**Resolution:** Per T3a→T5 boundary rule declared at T3a §5.4 — T5 recommendation supersedes T3a pair-count for SESSION_819 disposition. T3a's 171-pair signal drove T5 to prioritize SESSION_819 investigation; T5's archive recommendation is the ratified disposition. Not a contradiction; T5 disposition authority per parent §4 T5 workflow.

---

## 6. Unresolved Unknowns

### 6.1 Corpus-inclusion policy for root README.md (T3b P1)

**Status:** T3b P1 finding — `README.md` is CLAUDE.md-cited but NOT in `Document` corpus (search-invisible). Not resolved at T3b child ratification per S2836 policy; escalated to 2899 for Chris judgment.

**Question:** should root README.md be embedded in Document corpus (embedded → searchable via Rigby) OR treated as pure discovery-entry (not embedded, only readable via file open)?

**Recommended: Chris walks in §3.5 Class 5.**

### 6.2 Fragment-citation growth risk (T4)

**Status:** T4 §5.4 recorded fragment-adoption growth as future_trigger. Only 3 fragments currently exist arc-wide (all broken); zero `#K` chunk-ID form. If citation-authoring convention shifts (e.g., agent tool adopts `#L123-L145` line-anchor form), sub-loop (b) should rerun.

**Recommended: DEFER to post-2899. No 2899 decision required.**

### 6.3 SESSION_819 runner still active

**Status:** T3a detected 19 SESSION_819 files spanning 2026-07-14 through 2026-07-16. If the audit-runner is still generating files daily, archive-and-forget will not stem inflow.

**Recommended: bundle runner-fix investigation with Class 2 archive batch execution (per §3.2 explicit note).**

---

## 7. Anchor-Update Recommendations

### 7.1 `docs/PLATFORM_INVENTORY.md` (runtime counts anchor)

Add Group 2800 arc-close entry to inventory-adjacent registry (if inventory carries arc registry) OR note in `docs/research/OPEN_ARCS.md` (Group 2800 already marked 7/7 COMPLETE at S2839 close). **No PLATFORM_INVENTORY.md content changes required.**

### 7.2 `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor)

**No content changes required** — Group 2800 arc did not change platform shape, count, or capability. Narrative anchor last-refresh line remains valid.

### 7.3 `docs/research/ARCHITECTURE_INDEX.md`

Register Group 2800 arc COMPLETE (7/7) + link this canonical summary + update §8 timeline entry. Same v-bump commit pattern as prior arc closes.

### 7.4 `CLAUDE.md`

Fix P0 line 262 discord count in-place per Group 2700 §7 §10.4 (b) gate from S2834 T1 (bucket A auto-actionable). Non-blocking on this arc; still owed from Group 2700.

### 7.5 `docs/research/OPEN_ARCS.md`

Update Group 2800 row from `7 of 7 shipped — arc COMPLETE` to `RATIFIED at S2840 — see 2899_docs_content_canonical_summary.md`. Add post-2899 execution arc row as `pending open`.

---

## 8. Follow-On Research Queue

### 8.1 Post-2899 execution arc — §3 target-tree migration + 5-class disposition rollout

**Scope:** execute the 5 disposition-class batches per §3 above, in this order:

**Execution-arc preflight (Rigby cycle-1 Q4 STRENGTHEN — SPM fold F3):** before Class 2 (archive) begins, execution-arc opens with a small empirical preflight PR that (a) greps `core/management/commands/*.py` + `core/tasks.py` + `core/services/*.py` for `SESSION_819` / `819_SYSTEM_AUDIT` referents + (b) checks `ls -lt docs/audits/SESSION_819_SYSTEM_AUDIT_*` for last-write timestamp. If runner is still active, the first execution-arc PR fixes/disables the runner BEFORE any archive move. This keeps 2899 as classification-only (parent §5 non-goals discipline) while ensuring "archive active output" never happens.

**Interruptible-execution stop-conditions (Rigby cycle-2 Q5 F6 SPM — load-bearing-stability guardrail):** batch operations fail when execution reveals semantics that classification missed. Execution arc enforces:

- **Preflight sample per class (before class-batch begins):** randomly sample 5 rows per Class 1/2/3, hand-verify classification predicate (does this row actually match the class definition?). If ≥1 of 5 fails, pause + re-triage the class.
- **Rolling stop-condition (during class-batch execution):** if >20% of executed rows within a class reveal reclassification-need (per-row exception forcing Class 5 escape), pause + escalate to Chris. Prevents "keep going even though half the batch was wrong."
- **Per-PR max-rows cap:** individual PRs within a class execute ≤25 rows to keep review surface tractable. Whitelist automates the mechanics; per-PR review remains human.
- **Explicit resume gate:** after any pause, execution arc requires fresh Chris ratification of the paused class before resume (do NOT auto-resume from stop condition).

1. **Class 4 ref-graph repair** (6 rows) — smallest, most mechanical, unblocking. Single PR.
2. **Class 3 pointer retrofit** (~49 rows) — if Playbook v0.9 whitelist ratified, execute via bucket #1; else conventional PRs batched by subdir.
3. **Class 2 archive** (~40 rows) — if whitelist ratified, execute via bucket #3 `git mv`; else conventional PRs. **Bundle SESSION_819 runner-fix per §6.3.**
4. **Class 1 pointer propagation** (~79 rows) — dependent on v1.2 candidate 5 (series-level inheritance schema) ratification; either single subdir-index PR per subdir (whitelist bucket #2) or per-file if v1.2 deferred.
5. **Class 5 case-by-case** (~32 rows) — post-2899 conventional PRs per Chris disposition.

**Simultaneously:** execute Group 2700 §3 target-tree migration (was already scoped at Group 2700 close; now unblocked by 2899 file-content dispositions).

**Estimated session count:** ~3-5 sessions (Class 4 = 1 session; Classes 2+3+1 = 2-3 sessions with whitelist, 4-5 without; Class 5 = 1 session).

### 8.2 Playbook v0.9 amendment arc

**Scope:** author Playbook v0.9 amendment envelope with 4 codification-ready [GR] rules (per §10.2 below).

**Estimated session count:** 1 session (per S2786 v0.8.0 precedent — "third consecutive MINOR shipped in single-session shape").

**Sequencing recommendation:** ratify Playbook v0.9 **before** post-2899 execution arc begins Classes 2/3 if whitelist codification is ratified — unblocks whitelist-based execution.

### 8.3 Future single-corpus arcs (candidate)

- **Fragment-citation validation arc** — trigger when fragment adoption grows (T4 §5.4 future_trigger)
- **Bimodal-distribution cross-corpus validation** — trigger when a second triage arc encounters similar shape signal (§4.5)
- **Series-level inheritance cross-arc corroboration** — trigger at first arc encountering historical-subdir with existing series-pointer convention (§4.3 for §10.1 v1.2 candidate 5 ratification)

---

## 9. Cross-Links to Delegated Arcs

- **Post-2899 execution arc** — inherits 5-class disposition + all 206 row dispositions from §3
- **Playbook v0.9 amendment arc** — inherits §10.2 four [GR] rule proposals
- **Group 2700 §3 target-tree migration** — dependency-released by this arc close
- **CLAUDE.md P0 line 262 discord count fix** — inherited from Group 2700 §7 bucket A (auto-actionable)

---

## 10. What This Research Taught Us About How to Do Research

*Per Playbook §11.3 template + `feedback_xx99_meta_methodology_section`.*

### 10.1 What worked (methodology validated across this arc)

1. **Sequential-child discipline with cross-child pre-clustering** — parent §4 T5 workflow directive generalized: each child declared substrate consumption contract; T3a→T3b→T4→T5 chain worked without duplicate scan effort. This is *how* the 4-trigger corroboration happened; sequential + explicit + declared.
2. **§10.1 v1.1 schema locked at first child (T1)** — locking the classification schema at T1 ratification prevented mid-arc schema churn. v1.2 candidates accumulated in each child's `future_trigger` note rather than forcing schema evolution mid-corpus.
3. **Deferred escalate policy (S2836)** — S2836 policy "all `escalate_to_chris` rows defer to arc close in multi-child audit arcs" prevented per-child interruption for Chris judgment. Cross-child context (e.g., T5 disposition supersedes T3a pair-signal for SESSION_819) requires cross-child visibility.
4. **AEP v0.1 Stage 1 trial at T5** — validated compressed AEP format at the arc's final child; PASS on all 5 metrics per Rigby Q6 evaluation. Stage 2 authorized S2839 Chris D-verdict; S2840+ SIGN cycles use AEP by default. Cheaper SIGN cycles unlocked at the point of highest cycle-count need (canonical summary).
5. **Anti-rubber-stamp SIGN held 6/6 arc-wide** — every child cycle produced ≥1 real STRENGTHEN or DISAGREE with tool-grounded evidence per `feedback_verify_rigby_tool_runs_before_trusting_sign`. No child shipped on rubber-stamp acceptance.
6. **Same-PR engineering folds** applied twice arc-wide (S2837 T3b + S2839 T5 PA output-cap raise) — Chris directive `"we can fix like that"` codified the pattern: substrate-limitation folds discovered during SIGN cycles can ship in the same PR when the fix is local + low-risk + tests updated.

### 10.2 What to codify into Playbook v0.9 (per §20 two-triggers rule)

Four amendment candidates ready for v0.9 arc:

1. **[GR] Cross-child pre-clustering substrate contract** — "In multi-child arcs, each subsequent child MUST declare substrate consumption contract explicitly in §1.5 + report re-derivation vs load-only decision per substrate class." Corroboration: 4 triggers across T3a/T3b/T4/T5.
2. **[GR] `null_result` finding class as §11.3 template addition** — "Audit templates MUST reserve explicit space (§2.1 P0 / §2.4 chunk-ID absence / equivalent) for null-result reporting rather than implicit absence. Null-results are first-class positive evidence." Corroboration: 4 observations across T3b/T4/T5.
3. **[GR] Ambiguous-as-first-class classification value** — "Where boolean-ish classification produces genuinely-mixed input, emit third `ambiguous` value rather than force-picking. Route to human judgment." Corroboration: T5 §2.2 + §5.4 + §6.2 (3 internal triggers).
4. **[GR] Small-fix whitelist for triage-heavy child arcs** — extension of PLAYBOOK-7.4.4 (recycle-after-merge) family; explicit categories (pointer header retrofit + subdir index pointer additions + pure archive `git mv`) + safeguards (line-diff cap ≤15 added / 0 removed; file-class gating; no semantic edits; audit trail; stop condition). Corroboration: T4 §5.7a proposal + T5 §5.7a formalization (2 arc-siblings within same arc — arguably 2 triggers; conservative reading: 1 trigger with elaborate scoping. **Chris judgment at 2899: is intra-arc-sibling proposal-then-formalization a 2-trigger event or 1?** Recommendation: treat as 1 trigger with strong specification; ratify at v0.9 anyway per stated need for post-2899 execution unblocking.)

**Also for v0.9 arc consideration but NOT recommended by this doc:**
- Bimodal-distribution reporting requirement (§4.5) — insufficient corroboration (1 trigger).
- Series-level pointer inheritance schema (§4.3) — insufficient corroboration (2 sub-triggers within 1 arc).

### 10.3 What didn't work / anti-patterns to avoid

1. **Chunk-ID citation hypothesis (T4 §2.4)** — pre-arc hypothesis that post-1143 chunk-ID reset caused broken fragment citations. Empirically unfounded (0 chunk-ID citations in corpus). Anti-pattern: treating unverified hypothesis as scan requirement; T4 verified before batch-remediating.
2. **T2 raw BROKEN_404 as actionable count** — T2 §2 reported 2,502 raw BROKEN_404 (9.3%); untriaged interpretation would drive over-remediation. FP-1/FP-2/FP-3 filter reduced to 6 real (T4 P1). Anti-pattern: quoting raw grep counts as findings without FP filtration; child audits must include FP methodology-note.
3. **Fragment-adoption growth speculation (T4 §5.4)** — recorded as future_trigger only. Not treated as current-arc scope. Anti-pattern (avoided): scope creep into speculative future patterns.
4. **T5 §5.7a whitelist scope-creep** — T5 explicitly bounded whitelist to future_trigger observation ONLY; NOT in-arc application. Anti-pattern (avoided): applying whitelist mid-arc when scope was audit-only.
5. **Per-child Chris judgment inline** — pre-S2836 default. Would have created 206-interruption workshop across 6 sessions. S2836 deferred-escalate policy fixed this. Anti-pattern: forcing Chris judgment before cross-child context assembled.

### 10.4 Suggestions for the playbook itself

1. **§20 two-triggers threshold clarification** — is intra-arc-sibling proposal-then-formalization 1 trigger or 2? See §10.2 (4) above. Suggested clarification: "Same-arc sibling refinements of the same underlying proposal are 1 trigger; independent proposals within one arc are 2 triggers." Chris judgment recommended at v0.9 amendment authoring.
2. **§11.3 canonical-summary template — add "Class 5 case-by-case" as first-class field** — where child audits produce ≥5% escalate-to-Chris rows in disposition-class taxonomy, canonical summary MUST reserve explicit §3 subsection for case-by-case walk-through. Prevents Chris workshop from being surprise-heavy.
3. **§9 canonical questions — add "which children's escalate rows override which"** — S2836 policy already codifies deferred escalate; boundary rule (T3a→T5 for SESSION_819) is emergent. Codify: "Where a later child's disposition class supersedes an earlier child's finding, the earlier child MUST explicitly declare the boundary at §5.4."

### 10.5 Suggestions for future canonical summaries

1. **§10.2 codification-candidate table format** — this doc uses inline enumeration. Future canonical summaries: use table with columns (candidate, trigger count, corroboration state, recommendation, v0.9 slot). Improves Chris skim path.
2. **§3 disposition class enumeration** — this doc unified per-child classes into 5-class taxonomy for cross-child batching. Future arcs with heterogeneous per-child class taxonomies SHOULD attempt unification at canonical-summary time (not force each child to pre-align).
3. **Row-count reconciliation** (like §3.6) — explicit "N-total row count = ΣN-per-child row counts" section is worth ~5 minutes of authoring and saves ~30 minutes of downstream confusion.
4. **`null_result` §1-line surfacing in Executive Summary** — this doc surfaces "0 P0 across 5 children" in §1 headline; future canonical summaries should do the same. Positive evidence is skimmed first.

---

## 11. Arc Change Log

| Session | Child | Ship | State delta |
|---|---|---|---|
| S2833 | 2800 parent | scoping ratified (D1-D9) | arc opens; 6-child package + §10.1 v1.1 schema locked |
| S2834 | T1 (2801) | ratified | 33 files, 0 P0 / 1 P1 / 30+ P3; anchors/canon stable; schema v1.1 validated |
| S2835 | T2 (2802) | ratified | 793 files, 26,900 refs, 0 P0 / 1 P1 / ~50-100 P2; FP-methodology-note added; v1.2 candidate 1 (`citation_style`) proposed |
| S2836 | T3a (2803a) | ratified | 792 files pairwise, 0 P0 / ~173 P1 / 2 escalate; S2836 deferred-escalate policy codified; v1.2 candidates 2/3/4 proposed (coverage_content_dup / template_family / judgment_state) |
| S2837 | T3b (2803b) | ratified | 793 files 3-graph reachability, 0 P0 / 1 P1 (README.md) / 75 escalate; **first null-result observation**; v1.2 candidate `coverage_reachability` proposed; same-PR engineering fold applied |
| S2838 | T4 (2804) | ratified | 1061 files citation-graph + retrieval-harm, 0 P0 / 6 P1 / 22 escalate; **second null-result observation** (0 chunk-ID citations); T4 §5.7a whitelist future_trigger proposed |
| S2839 | T5 (2805) | ratified | 169 files 4-axis triage, 0 P0 / 0 P1 / 107 escalate; **third + fourth null-result observations**; §5.1 series-inheritance + §5.7a whitelist formalized + §5.8 bimodal signal; AEP v0.1 Stage 2 authorized; PA output-cap raised same-PR |
| S2840 | 2899 canonical summary | **this doc** | arc RATIFIED at close; 206-row queue disposition + 5 v1.2 candidates ratified/deferred + 4 Playbook v0.9 candidates + post-2899 execution arc scoped |

---

## 12. Appendix — Provenance

### 12.1 §10.1 v1.2 schema candidate detail (5 candidates)

| # | Candidate | Source | Corroboration | Claude+Rigby joint recommendation |
|---|---|---|---|---|
| 1 | `citation_style` field (markdown_link \| backtick_path \| prose_ref) | T2 §5.7 + T4 §2.6 | 2 triggers across sibling children | **ADOPT at v1.2** — reduces T2-style FP over-count; enables T4-style filtered P1 batch across future arcs |
| 2 | Canonical probe-query set | T4 §5.7 | 1 trigger + T5 sub-usage (probe queries re-run in T5 methodology-adjacent) | **DEFER** — 1-trigger threshold not met; will corroborate at next retrieval-adjacent audit arc |
| 3 | `null_result` finding class | T3b §2.1 + T4 §2.4 + T5 §2.1 P0 + T5 §2.1 P1 | 4 observations | **ADOPT at v1.2** — 4-observation corroboration far exceeds threshold; enables consistent positive-evidence surfacing |
| 4 | `coverage_reachability` fourth axis | T3b §5.3 | 1 trigger | **DEFER** — subsumed under T3b's existing 3-graph reachability method; adding formal schema axis is premature |
| 5 | Series-level pointer inheritance policy | T5 §5.1 | 2 sub-triggers within 1 arc | **DEFER** — insufficient cross-arc corroboration; will re-trigger at first future arc encountering historical-subdir with pre-existing pointer convention |

**v1.2 ADOPT batch:** candidates 1 + 3. Schema advances to v1.2 at 2899 close (if Chris ratifies) with fields `citation_style` + `null_result_scope` added; existing v1.1 rows remain valid (additive change).

**v1.2 DEFER batch:** candidates 2 + 4 + 5. Re-consider at future arc corroboration.

### 12.2 Playbook v0.9 amendment candidate detail (§10.2 restated)

| # | [GR] proposal | Trigger count | Ready for v0.9? |
|---|---|---|---|
| 1 | Cross-child pre-clustering substrate contract | 4 (T3a/T3b/T4/T5) | YES |
| 2 | `null_result` finding class as §11.3 template addition | 4 (T3b/T4/T5×2) | YES |
| 3 | Ambiguous-as-first-class classification value | 3 (T5 internal) | YES conditional on §20 threshold applicability |
| 4 | Small-fix whitelist for triage-heavy child arcs | 1-2 (T4 proposal + T5 formalization) | YES conditional on §20 clarification (§10.4 (1)) |

### 12.3 Corpus-size reconciliation

| Child | Corpus | Method-defined N |
|---|---|---|
| T1 | 33 | 5 anchors + 2 canon + 1 governance + 3 onboarding + 3 root + 13 CLAUDE.md graph + 4 research-OS + 2 topics canary |
| T2 | 793 | 790 docs/** non-handoff + 3 root anchors |
| T3a | 792 | same rglob as T2, minus 1 duplicate-path exclusion |
| T3b | 793 | same as T2 |
| T4 | 1061 | 1046 SESSION_NNNN handoffs + 15 non-SESSION_ persistent-reference |
| T5 | 169 | 93 audits + 15 audit-2026 + 10 audit + 33 reports + 18 docs/*_AUDIT.md |

Corpuses overlap intentionally (T2/T3a/T3b share base rglob; T4/T5 carve distinct sub-corpuses). Union of unique in-scope files: ~1842 (per parent §1 estimate).

### 12.4 Session pin + AEP telemetry

| Session | Pin | Retired? | AEP cycles | Chris D-verdict |
|---|---|---|---|---|
| S2833 | (parent — no arc pin) | n/a | n/a | scoping ratified |
| S2834 | (T1) | n/a | prose | ratified |
| S2835 | (T2) | n/a | prose | ratified |
| S2836 | (T3a) | n/a | prose | ratified |
| S2837 | (T3b) | n/a | prose | ratified |
| S2838 | (T4) | n/a | prose | ratified |
| S2839 | `pa-c0dd5180697442ad` | retired at close | 3 AEP v0.1 Stage 1 trial cycles | `"Approve, let me know if you have Rigby draft the routing note."` + Stage 2 authorized |
| S2840 | `pa-f541671e8b564dc7` | (retires at close of this session) | TBD (AEP v0.1 Stage 2 default) | TBD |

---

### 12.5 SIGN fold ledger (append-only per cycle)

| Cycle | Fold | Class | Q source | Target | Body |
|---|---|---|---|---|---|
| 1 | F1 | phrasing-clarification | Q2 | (dispatch-only; no doc change) | Rigby cycle-1 misread Q2 SIGN claim wording ("candidate 4 = coverage_reachability triggered by T3b+T4+T5×2"); actual §Appendix 12.1 correctly attributes T3b+T4+T5×2 evidence to candidate 3 (null_result), not candidate 4. Doc as-written is correct; SIGN dispatch claim wording was ambiguous. No amendment to doc. |
| 1 | F2 | nuance-preserved | Q3 | §10.2 candidate 3 | Rigby cycle-1 STRENGTHEN: candidate 3 (ambiguous-as-first-class) is "3 internal triggers in one child" not "cross-arc-sibling"; doc §Appendix 12.2 already labels this "YES conditional on §20 threshold applicability" — no amendment needed. Fold recorded for cycle-continuity. |
| 1 | F3 | SPM | Q4 | §8.1 execution-arc preflight | Rigby cycle-1 STRENGTHEN: add explicit "execution-arc preflight" PR as step 0 before Class 2 archive begins — grep for runner + timestamp check. If active, fix/disable runner before archive. Applied same-PR at §8.1. |
| 2 | F4 | SPM | Q5 | §1.2 + section headers | Rigby cycle-2 STRENGTHEN: scope-coupling / constitution-creep risk. Added §1.2 section-scope labels ([DESCRIPTIVE] / [RATIFIED] / [ADVISORY] / [EXECUTION-GATED]) so fresh readers cannot cite 2899 as precedent in contexts it wasn't designed to govern. |
| 2 | F5 | SPM | Q5 | §1.1 Chris decision checklist | Rigby cycle-2 STRENGTHEN: recommendation density felt pre-cooked. Added §1.1 Chris decision checklist (5 top decisions with what-changes/why/what-could-go-wrong/what-would-change-my-mind columns). Tightens Chris's decision surface. |
| 2 | F6 | SPM | Q5 | §8.1 stop-conditions | Rigby cycle-2 STRENGTHEN: load-bearing assumption ("class mapping stays stable under execution"). Added interruptible-execution stop-conditions to §8.1 (preflight sample per class + rolling stop-condition + per-PR max-rows cap + explicit resume gate). |
| 2 | F7 | SPM | Q5 | §3.1-3.5 definition/intent/risk paragraphs | Rigby cycle-2 STRENGTHEN: future-discoverability (6-month reader) risk. Added standalone definition + intent + risk paragraphs to each Class §3.1-§3.5 so class rationale is reconstructable without re-reading child audits. |

---

**END OF DOCUMENT** — RATIFIED at Chris D-verdict 2026-07-19 S2840 (`"Approved"`). Group 2800 arc RATIFIED at close.

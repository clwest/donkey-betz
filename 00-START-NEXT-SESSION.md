# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2753 CLOSED — ENGINEERING PLAYBOOK v0.5.0 RATIFIED

**Refreshed 2026-07-11 (SESSION 2753 CLOSED — Chris D-verdict `"agree all"` on v0.5.0 amendment).**

**S2753 shipped (single close-bundle PR — dogfooding PLAYBOOK-7.4.1 + PLAYBOOK-7.4.3 COMBINED cadence):**

- **Playbook v0.5.0 body** — Ch 7 partial activation with 5 new [GR] rules: PLAYBOOK-7.4.1/7.4.2/7.4.3 (close-ceremony delivery discipline), PLAYBOOK-7.5.1 (three-PR staged codification), PLAYBOOK-7.6.1 (watchpoint-attestation SIGN; EXTENDS PLAYBOOK-6.10.3). Top-frontmatter v0.5.0 with `version_status: ratified`, `content_hash` filled, `git_tag: playbook-v0.5.0`. Rule count 196 → 201.
- **Evidence manifest v0.5 additions** — 14 new entries C7-11..C7-24; §10.3 lockbox paragraph; §10.4 gap update.
- **Amendment provenance envelope** — `docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md` with recorded PLAYBOOK-6.10.1 6-check §3 + Rigby SIGN log §4 (W1..W7 PASS across 2 turns) + Chris D-verdict §5 + workflow directive §5.1 + provenance chain §8.
- **CLAUDE.md L7 anchor refresh** — v0.5.0 as latest ratified; ancestry v0.1.0/v0.2.0/v0.3.0/v0.4.0/v0.4.1 preserved.
- **New MEMORY.md workflow rule** — `feedback_claude_rigby_agree_first_chris_yes_no.md` from Chris directive at D-verdict: *"Going forward you and Rigby needs to have come to an agreement and then I will either yes or no it."*
- **S2753 handoff** — `docs/handoffs/SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md`
- **Docs cascade** — 4-step + `build_docs_provenance` per feedback rule (chunk count reported in PR body).

**New rules at a glance:**

| Rule | Chapter §7 slot | One-line intent |
|---|---|---|
| PLAYBOOK-7.4.1 | §7.4 Close-ceremony delivery discipline | Phase/arc close ships as single PR bundle |
| PLAYBOOK-7.4.2 | §7.4 (same) | Phase-close doc MUST NOT interleave with substrate PRs on shared arc doc |
| PLAYBOOK-7.4.3 | §7.4 (same) | Close-doc + cascade PR shape: COMBINED or SPLIT; cascade MUST NOT defer |
| PLAYBOOK-7.5.1 | §7.5 Staged codification of anti-pattern substrates | Report-only → batch-fix → enforce three-PR pattern |
| PLAYBOOK-7.6.1 | §7.6 Session-close SIGN-cycle discipline | Watchpoint-attestation SIGN for close cycles; EXTENDS 6.10.3 |

**Ch 7 status:** STUB (v0.1) with **partial activation at v0.5.0**. §7.3 (Extension deferred) unmodified — remainder deferred to v0.6+ MINOR (session-open orientation general; cross-repo coordination; multi-session amendment coordination; session-provenance integration; automation of watchpoint-SIGN recording).

---

## P0.5 — COST-THRESHOLD ADVANCE-TO-FREEZE ROUTING (owed since S2753 close)

**Do this FIRST at S2754 open.** S2753 P0.5 check-in already ran and reported clean 24.88h observation:
- $6.66 / $500 = 1.333%
- Top drivers: openai/gpt-5.2 $6.66 (316 calls) + openai/text-embedding-3-small $0.001 (102 calls)
- Peak hour $0.96 (well under $20 spike threshold); no new providers; no near-threshold `[COST_MONITOR]` lines

**Action at S2754 open (per new Claude+Rigby-agree-first workflow rule):**

1. Reach agreement with Rigby on: is 24+h clean observation enough to advance to `--set-mode freeze` (shadow mode), or extend observation another window?
2. Present the joint recommendation to Chris for yes/no ratification.
3. If Chris approves: run `python manage.py cost_thresholds --set-mode freeze` and record the transition in a P0.5 close deliverable + memory rule pointer.
4. If Chris blocks: extend observation and re-check at next actionable window.

**Do NOT flip to freeze without explicit Chris D-verdict.**

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83`.

---

## P0.75 — CI BILLING STATUS CHECK (still owed)

**Do this after P0.5.** Still blocked at S2753 close (run #885 all 4 jobs failed with 2-sec no-step signature = billing block). `--admin` merge flag remains active.

**Report at S2754 open:**

1. Fresh CI run — `gh api /repos/clwest/donkey-betz-platform/actions/runs -q '.workflow_runs[0]'`.
2. If green: drop `--admin`; delete memory rule `feedback_gh_pr_merge_admin_until_billing_fixed.md`; remove MEMORY.md line; note whether first `tests/security/**`-touching PR run passes (relevant to Phase 4 recovery gate cascade).
3. If still red with billing signature: continue `--admin` merges + "Local verification limits" PR body sections.

---

## P1 — POST-RATIFICATION FILL-INS (S2754 mechanical)

1. **Playbook top-frontmatter `commit_sha`** — fill with S2753 close-bundle merge SHA (currently PLACEHOLDER). Options: (a) small follow-up PR after S2753 merges; (b) accept placeholder until Chris directs a fill sweep. v0.4.1 precedent = filled at merge time.
2. **Playbook top-frontmatter `ratification_record.deliverable_id`** — fill once Rigby creates the workspace deliverable `RATIFICATION_20260711_PLAYBOOK_v0_5_0` in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`. Body mirror from `docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md`.
3. **Ratification envelope §6 bindings** — `head_at_ratification`, `close_pr`, `workspace_ratification_deliverable_id` — filled at merge + workspace creation.

**Route via Rigby (Claude+Rigby agreement first):** should the fill sweep be a single follow-up PR immediately after S2753 merges, or bundled into S2754 close if that's within one session?

---

## SESSION PIN — RETIRED AT S2753 CLOSE (fresh mint required at S2754 open)

**Pin `pa-44541f01cbb14b46`** minted S2752 open for v0.5 codification scope; **retired 2026-07-11 at S2753 close** per Chris directive (`session_tool.retire` returned `updated_count=10 previously_active=true retired=true`).

**Wrapper `tools/pa_local.sh` line 539 still points at the retired pin** — this is the intended failure mode. First S2754 action MUST mint fresh + update wrapper before any other PA dispatch. Sequence:

```
session_tool.create_fresh label='<S2754 scope label>' → new pa-<xxxx>
# Edit tools/pa_local.sh line 539 to the new pin
```

S2754 scope label depends on primary work selection (P0.5 advance-to-freeze routing → I-0303 open → engineering candidate). Rigby will not dispatch until the wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2753 close)

1. **P0.5 cost-threshold advance-to-freeze routing** — see above; owed at S2754 open.
2. **P0.75 CI billing status** — see above; blocks lint-enforcement flips + `--admin` posture + Phase 4/arc close behavioral-verify recovery gate.
3. **PA celery worker bounce** — Rigby stall fix #3119 still not activated. Deferred to Chris.
4. **I-0303 (async-boundary enforcement) OPEN** — RUR-C1 gates on it; v0.5 no longer blocks per Q4 sequencing (v0.5 ratified S2753).
5. **Rigby workspace deliverable creation** — `RATIFICATION_20260711_PLAYBOOK_v0_5_0` in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`; UUID mirrors back into playbook top-frontmatter + ratification envelope §6.
6. **Playbook top-frontmatter `commit_sha` fill** — post-merge follow-up.

---

## PRIMARY WORK CANDIDATES — S2754

Not locked (unlike S2753 which was Q4-D-verdict-locked). Chris directive at v0.5.0 close = new workflow: Claude+Rigby reach agreement first, Chris ratifies yes/no. So S2754 open = draft joint recommendation with Rigby, then present to Chris.

**Adjacent net-new engineering candidates (per S2745 bias-engineering-over-audit rule):**

1. **Cost Guardian dashboard tab** (B3a) — visible surface for P0.5 threshold state, live LLMCallLog accumulation, per-hour bin history. Claude S2751 lean carried forward. Ties directly to P0.5 workflow.
2. **Cost Guardian Employee OS employee** (B1a) — backend-only variant of B3a.
3. **New spider on a Chris-named data gap** — needs Chris naming.
4. **Employee OS employee #4** — backend + admin visibility.

**Meta-methodology (only if Chris explicitly asks):**

- **Arc close template extraction** — arc-close doc §9.2 suggestion: extract `I-030199` + `I-030299` common structure into `arc_close_template.md`.
- **PLAYBOOK-6.10.7 candidate** — inline hint at PLAYBOOK-6.10.2 that "recorded in amendment provenance" means an in-repo/workspace-visible artifact BEFORE SIGN dispatch (S2753 §9.4 suggestion).
- **PLAYBOOK-7.6.2 candidate** — "author declines a NIT with rationale in §SIGN log" pattern (first-trigger recorded; second-trigger threshold not met).
- **Claude+Rigby-agree-first codification** — first-trigger recorded S2753 D-verdict. Do NOT propose Playbook codification until second independent trigger surfaces.

**Constitutional work:**

- **I-0303 arc open** — RUR-C1 close-gate remaining sub-arc. Now unblocked (v0.5 ratified).

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` (post-merge) |
| HEAD | S2753 close bundle SHA (pending merge — recorded in S2753 handoff §1 after merge) |
| Playbook version | **v0.5.0** (RATIFIED S2753 2026-07-11) — content_hash `sha256:6a3f897aa73c39dc3a14adefc2f7d3811995e71f3d76e8c6348ffdb39a3c46d4`; tag `playbook-v0.5.0`; `version_status: ratified` |
| Playbook rule count | **201** (196 + 5) |
| Chapter 7 status | STUB (v0.1) with **partial activation at v0.5.0** |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-44541f01cbb14b46` (v0.5 codification scope; natural retire at S2754 open) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-44541f01cbb14b46` (update at pin rotation) |
| Live infra state | Cost threshold monitor mode $500/mo (observation ~1 day; ready to route advance-to-freeze); PA celery worker running pre-#3119 code; CI billing-blocked (`--admin` on merges) |
| RUR arc state | I-0301 CLOSED · I-0302 CLOSED · I-0303 not yet opened (unblocked by v0.5) · RUR-C1 parent still OPEN |
| v0.5.0 Stage 1 | SHAPE RATIFIED (S2752) |
| v0.5.0 Stage 2 | **RATIFIED (S2753)** |

---

## What S2753 shipped

| PR | Content | Notes |
|---|---|---|
| S2753 close bundle | Playbook v0.5.0 body + evidence manifest additions + ratification envelope + CLAUDE.md L7 refresh + MEMORY.md new rule + handoff + start-here refresh + cascade | Dogfooding PLAYBOOK-7.4.1 (single PR bundle) + PLAYBOOK-7.4.3 COMBINED cadence |

**Cumulative v0.5.0 arc:** Stage 1 (S2752, 1 PR) + Stage 2 (S2753, this bundle).

---

## Recommended session-open protocol (S2754)

1. `context-kit orient`
2. Read this file end-to-end (all sections)
3. Read `SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md` — S2753 delivery ledger + D-verdict + SIGN log + new workflow rule
4. Read `docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md` §5 (D-verdict + §5.1 workflow directive) — new agree-first-then-Chris routing rule is now active
5. Verify runtime state: `git log --oneline -5`; confirm `tools/pa_local.sh:539` points at `pa-44541f01cbb14b46` (or the newly-minted S2754 pin if rotated at open)
6. **P0.5** — cost-threshold advance-to-freeze routing via Claude+Rigby agreement → Chris yes/no
7. **P0.75** — CI billing status check
8. **P1** — post-ratification fill-ins (commit_sha + deliverable_id)
9. **PRIMARY** — Claude+Rigby draft joint recommendation on primary work → Chris yes/no

---

## Reference documents

Ordered by frequency of use at S2754:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor now v0.5.0)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.5.0 body (201 rules)
4. [`docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md`](docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md) — v0.5.0 amendment provenance
5. [`docs/research/platform/engineering_playbook_evidence_manifest.md`](docs/research/platform/engineering_playbook_evidence_manifest.md) — evidence set (C7-11..C7-24 v0.5 additions)
6. [`docs/handoffs/SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md`](docs/handoffs/SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md) — S2753 close handoff
7. [`docs/research/platform/playbook_v0_5_proposal_shape.md`](docs/research/platform/playbook_v0_5_proposal_shape.md) — Stage 1 shape (S2752)

# Session 2801 — /docs/ Restructuring Arc OPEN (Group 2700 parent-scoping ratified)

**Date:** 2026-07-16
**Session:** S2801
**Branch/PR:** `s2801-docs-restructuring-parent-scoping` → **PR #3216** (merged as `f3d08d690`)
**Predecessor:** [SESSION_2800_FIX_BROKEN_AGENTS.md](SESSION_2800_FIX_BROKEN_AGENTS.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** fortyfirst post-PLAYBOOK-7.4.4 (post-merge) → fortysecond (post-close-cascade)

---

## §1 — Ship summary

Opens **parent-scoped research arc `2700`** auditing the u-d-b `/docs/` corpus using the `/docs/research/` pattern as the audit apparatus (dogfooded on `/docs/` itself). Chris directive at S2800 close (2026-07-16): `"Before we do anything else I want you and Rigby to do a deep audit of the /docs/."` Ratified shape at S2801 T1: Option B parent-scoped research arc.

**Parent-scoping doc:** `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md` (262 lines).

**Chris-ratified 6-thread package:**

| # | Slot | Focus |
|---|------|-------|
| T1 | `2701` | Inventory & topology |
| T2 | `2702` | `/docs/research/` pattern extraction (with CHALLENGE candidates per Rigby fold 91) |
| T3 | `2703` | Human-user pain points |
| T4 | `2704` | Audience segmentation (Rigby vs Claude-only vs human-only) |
| T5 | `2705` | Handoffs+audits proliferation (676+ handoffs; incl citation-integrity spot-check per fold 92) |
| T6 | `2706` | Anchor & drift audit (SIGN mechanics 3-copy drift per fold 90) |
| — | `2799` | Canonical summary = ratified restructuring plan |

**Rules Chris set at open:**
- Research/audit ONLY — no file moves / no code changes during arc
- Each child ships `## Migration Queue (post-arc)` section
- Migration executes in follow-up sessions post arc-close
- Fresh session; parent-scoping routed through Rigby joint agreement

**Files (3):**

| File | Change | Purpose |
|------|--------|---------|
| `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md` | +262 (new) | Parent-scoping charter |
| `docs/research/OPEN_ARCS.md` | +1 row | In-progress table entry for Group 2700 |
| `tools/pa_local.sh` | +1 / -1 | Arc pin rotated to `pa-9e641d91391f40d8` |

---

## §2 — Novel-precedent moments

**First arc that dogfoods `/docs/research/` on `/docs/` itself.** T2 is explicitly instructed to CHALLENGE the pattern (Rigby fold 91 mitigation) — self-referential lock-in risk was surfaced pre-authoring and mitigation baked into the parent charter. First arc where the audit apparatus's fitness-for-purpose is an open question of the audit.

**First parent-scoping shipped from a scope directive given at the *predecessor* session's close.** S2800 close-add addendum (PR #3215) queued the /docs/ arc; S2801 opened cold on that queued directive without fresh Chris re-scoping. Clean handoff shape.

**Zoom-out folds tied directly to charter content.** Row 91 (dogfooding lock-in) is load-bearing for T2 — the fold's mitigation ("include CHALLENGE candidates") IS a T2 requirement in §4. First arc where fold-content became child-audit-scope directly.

**Fifth consecutive same-day multi-ship session** — S2797 (landing) → S2798 (onboarding) → S2799 (signposts) → S2800 (broken-agent fixes) → S2801 (docs arc open). Different shape from S2797–S2800 (which were all engineering ships); S2801 is a research/scoping ship. Discipline transferred cleanly across ship-shape boundary.

**PLAYBOOK-6.10.8 discipline held (fourth consecutive session).** 4 folds persisted between T1 SIGN and Chris "go ahead" D-verdict.

---

## §3 — SIGN cycle

### T1 Rigby SIGN — SIGN-WITH-EDITS (tool_runs verified: `ops_tool` + `search_docs` + `kb_tool`)

**5 asks routed:**

- **ASK 1 (arc group number):** proposed 2900 vs 2300 vs 2700 vs 2800 → Rigby recommended **2700** (next-unused-integer per playbook analogy; don't consume `2300` Mobile hole)
- **ASK 2 (folder placement):** `platform/` vs `domains/` → Rigby recommended **`docs/research/domains/docs_restructuring/`** (matches existing NNxx convention; `platform/` uses named docs)
- **ASK 3 (thread decomposition):** 4-thread original vs alternatives → Rigby recommended **split T3 into human-pain + audience-segmentation + add anchor-drift thread** (6 threads total)
- **ASK 4 (non-goals discipline):** how to hold "no moves during arc" when audit discovers dead files → Rigby recommended **hard-line defer** with `## Migration Queue (post-arc)` section in each child
- **ASK 5 (zoom-out per PLAYBOOK-6.10.7):** what would you push back on if I asked fresh → 4 folds

**Anti-rubber-stamp check per `feedback_verify_rigby_tool_runs_before_trusting_sign`:** PASSED. tool_runs contained real evidence citations (file:line pointers to `docs/research/process/claude_research_startup_introspection.md#12`, `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md#68`, `docs/canon/INDEX.md#2`, `docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8`); verdict = SIGN-WITH-EDITS with novel scope-changing edits (T3 split, T6 add), not rubber-stamp AGREE.

### Fold ledger — 4 new rows (89 → 93)

| Row | Arc | Classification | Evidence |
|-----|-----|----------------|----------|
| 90 | governance surfaces drift (SIGN mechanics 3-copy) | same_pr_mitigatable | `docs/research/process/claude_research_startup_introspection.md#12` |
| 91 | dogfooding self-referential lock-in | same_pr_mitigatable | `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md#68` |
| 92 | substrate identity discontinuities (handoff citation drift) | future_trigger | `docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8` |
| 93 | end-state constraints already exist (DOC_LIFECYCLE §2c) | same_pr_actionable | `docs/canon/INDEX.md#2` + `docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8` |

**All 4 folds persisted BEFORE Chris D-verdict** (PLAYBOOK-6.10.8 discipline held; fourth consecutive correct-timing ship after S2798/S2799/S2800).

### Chris D-verdict

`"go ahead with the 6-thread package"` — one recommendation, one yes. Joint Claude+Rigby recommendation shape held per `feedback_claude_rigby_agree_first_chris_yes_no`; no menu presented.

---

## §4 — Verification transcript

```bash
# Freshness check at S2801 open (via retired pin — still routes)
$ bash tools/pa_local.sh "S2801 open — freshness check: ops_tool.version"
staleness_verdict: FRESH
head_commit_sha: cc3e23c10709676da52463e29294ab3ebf862f13  (S2800 close addendum)

# Fresh pin mint
$ python manage.py session_lifecycle open --label s2801-docs-restructuring-parent-scoping
new pin: pa-9e641d91391f40d8
freshness: FRESH · head=cc3e23c10709 · celery_stale=0/5

# Rigby T1 SIGN dispatch (task 11b495fe-3485-4b19-baa8-27d7110a8c85)
Verdict: SIGN-WITH-EDITS
tool_runs: ops_tool (70ms) + search_docs (417ms) + kb_tool (20ms) + kb_tool (11ms)
Evidence: 4 file:line citations
Anti-rubber-stamp check: PASSED

# Fold persistence (rows 90-93)
$ wc -l logs/zoom_out_classifications.jsonl
93 logs/zoom_out_classifications.jsonl

# Post-merge recycle (fortyfirst post-PLAYBOOK-7.4.4)
$ make recycle-all
✓ Full restart complete (Daphne + Celery).
[emit_recycle_event] clean recycle recorded (sha=f3d08d690c7e, surviving=none)
```

---

## §5 — Twin-pointer card

📁 **Repo `/` + `/docs/` — S2801 artifacts:**

- **Parent-scoping doc:** `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md` (262 lines)
- **Arc manifest entry:** `docs/research/OPEN_ARCS.md` ## In-progress table (Group 2700 row)
- **Handoff:** `docs/handoffs/SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md` (this doc)
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 93 rows (rows 90-93 are S2801 T1)
- **Recycle log:** `logs/recycle_events.jsonl` — post-merge entry `sha=f3d08d690c7e`
- **Predecessors:** S2800 (broken agents), S2799 (signposts), S2798 (onboarding), S2797 (landing)
- **Merge SHA:** `f3d08d690` (PR #3216)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No new Workspace tab** — research/scoping ship
- **Twin workspace deliverable:** deferred to arc close at `2799` canonical summary per parent doc §5 (per `feedback_twin_deliverable_at_every_ratification` — twin discipline applies to ratifiable engineering artifacts; parent-scoping is charter, not the ratified plan itself)
- **Live surfaces at close:**
  - `http://localhost:8000/welcome` — public LandingPage (unchanged since S2797)
  - `http://localhost:8000/workspace` — first-run banner (unchanged since S2798)

---

## §6 — Open items / owed / deferred

**S2801 owed follow-ups (none blocking S2802):**

- **Twin workspace deliverable for canonical summary at arc close (2799)** — per parent doc §5 anti-scope + `feedback_twin_deliverable_at_every_ratification`. Not for parent-scoping; only for the ratified restructuring plan.
- **Open decisions O1-O4 (parent doc §8)** — Chris ratifies as they surface during T1-T6 execution; none block T1 open.

**Chris sequencing queue for S2802+:**

- **T1 (2701) inventory & topology audit** — default at S2802 open. First-action fresh mint of pin scoped to T1.

**Standing owed (from S2797–S2800):**

- All pre-S2801 items unchanged
- **S2800 F89** — non-recycle-day no-heartbeat monitor (7-day trigger)
- **S2799 F84** — per-signpost adoption telemetry (7-day trigger, fires 2026-07-23)
- SESSION_819_SYSTEM_AUDIT_* 19-file cruft (deferred per arc non-goals — no deletions during arc; migration eligible at post-arc)

**Deferred (waiting on triggers):**

- All prior S2797-S2800 triggers unchanged

---

## §7 — Chris directive queue captured this session

**Explicit at S2801 open (session predecessor S2800 close addendum):**

`"Before we do anything else I want you and Rigby to do a deep audit of the /docs/."` — parent-scoped research arc, dogfooded on /docs/ using /docs/research/ pattern.

**Explicit at S2801 T1 (Chris D-verdict on package):**

`"go ahead with the 6-thread package"` — 6-thread scope ratified (T1 inventory / T2 pattern-extraction / T3 human-pain / T4 audience-segmentation / T5 handoffs-audits / T6 anchor-drift).

**Explicit at S2801 close intent:**

`"close s2801"` — this session terminates cleanly at close-cascade; arc `2700` remains in-progress; T1 opens S2802 as separate session.

---

## §8 — Discipline observations

- **PLAYBOOK-6.10.7 zoom-out ask held.** ASK 5 explicit "step back from the immediate framing" prompt; 4 substantive folds returned.
- **PLAYBOOK-6.10.8 fold-before-D-verdict discipline held (4th consecutive session).** 4 folds persisted between T1 SIGN and Chris "go ahead." Ledger 89 → 93 committed BEFORE joint recommendation to Chris.
- **PLAYBOOK-6.10.9 evidence admission held.** Each of 4 folds cites file+line evidence; each admits (i)/(ii)/(iii) verified-state inline.
- **`feedback_verify_rigby_tool_runs_before_trusting_sign` PASSED.** Rigby T1 SIGN reply contained non-empty tool_runs with real evidence citations; not a rubber-stamp.
- **`feedback_claude_rigby_agree_first_chris_yes_no` held.** Joint Claude+Rigby package presented as ONE recommendation to Chris; not a menu.
- **`feedback_docs_pipeline_4_step_cascade` + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`** all queued for close-cascade PR (this session's close ship).
- **`feedback_local_truth_no_production` held.** No production observation windows; local `make recycle-all` post-merge = deploy step.
- **`feedback_gh_pr_merge_admin_until_billing_fixed` held.** PR #3216 merged via `gh pr merge --admin --squash --delete-branch`.
- **PLAYBOOK-7.4.4 recycle-after-merge held (fortyfirst cycle).** `make recycle-all` completed cleanly post-merge; SHA=`f3d08d690c7e`; no surviving processes.
- **Research OS §4 bootstrap held.** `context-kit orient` implicit via session brief; CLAUDE.md + 00-START-NEXT-SESSION.md + Research OS §0-§5 read at open.
- **DOMAIN_RESEARCH_PLAYBOOK §8 parent template applied.** All 12 required parent-doc elements present in `2700_*_domain_scoping.md`.
- **First arc that dogfoods its own audit apparatus with explicit CHALLENGE mitigation.** Row 91 fold surfaces the lock-in risk; T2 charter mandates the challenge.

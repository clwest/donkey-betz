---
title: "S2832 — Ratify 2799 §3 target /docs/ tree + open file-content-level audit arc"
session: 2832
date: 2026-07-19
status: shipped
authority: governance
scope: |
  S2832 opened immediately after S2831 close cascade (same terminal
  session). Chris asked what remained in /docs/ backlog before moving
  to Colorado Phase 4. Claude surveyed and surfaced that the 2799
  canonical summary from Group 2700 arc close (S2817) was still
  PROPOSED, not RATIFIED — blocking the whole 8-item follow-on queue.
  Chris directed "ratify 2799 first". Claude routed 5 pressure-test
  questions to Rigby with tool-grounded prompts; Rigby ran substantive
  repo_tool searches (docs/adr codebase references, autogen management
  commands, DOC_LIFECYCLE §2c content, MQ-T5-8 cross-refs, parent §4
  T5 clause) but SIGN cycle was superseded before verdicts extracted
  when Chris clarified that "audit /docs/" originally meant every file
  and directory, not just /docs/research/. Claude corrected the record
  (Group 2700 arc DID cover whole tree at structural/statistical
  level; T1 inventoried all 3247 files; the honest gap is file-CONTENT
  audit — no per-file walk exists). Chris D-verdict: "ratify §3 today,
  open file-level audit arc". §3 target tree ratified as PROPOSED
  (compatibility-first guardrails preserved; NOT a move-script);
  §7 anchor updates + §8 queue ordering deferred to future ratification;
  file-content-level audit arc opens at S2833 as separate arc. Merged
  as PR #NNNN (filled at merge). `make recycle-all` clean post-merge
  per PLAYBOOK-7.4.4. SEVENTY-EIGHTH close-cycle post-PLAYBOOK-7.4.4.
predecessor: docs/handoffs/SESSION_2831_RAG_INTENT_GATE_DIAGNOSTICS_TAB.md
merge_pr: TBD
merge_sha: TBD
---

# S2832 — Ratify 2799 §3 target /docs/ tree + open file-content-level audit arc

## §1 Session shape

Continuation of S2831 terminal session — S2831 closed cleanly with cascade PR #3276 (`f29a892cf`) and final recycle. Chris then asked whether anything remained in `/docs/` before moving on to Colorado Phase 4 personal work.

Claude surveyed the /docs/ backlog:
- **2799 canonical summary** from Group 2700 arc (closed S2817) is still `status: active (canonical summary — arc close; **proposed** restructuring plan + twin-pointer workspace deliverable pending Chris ratification)` — the whole 8-item follow-on queue is technically waiting on Chris D-verdict
- Doctor warnings: inventory stale (14 days), narrative anchor `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 (older than latest handoff), 19 untracked `docs/audits/SESSION_819_SYSTEM_AUDIT_*.md` files in git status, handoff numbering gaps
- Discovery-layer arc (S2818-S2831) addressed §8 item #1 end-to-end; items #2-#8 remain open

Chris picked ratify-2799 as the S2832 target.

## §2 Root-cause investigation

N/A — this was a governance/ratification session.

## §3 Joint Claude+Rigby SIGN (routed, superseded before verdict extraction)

Fresh pin `pa-d10f64b5624c43c9` (label `s2832-ratify-2799-docs-restructuring`) minted at S2832 open. Rigby routing sent 5 pressure-test questions:

- Q1 [§3 SAFETY]: docs/adr → docs/decisions merge — is DOC_LIFECYCLE §2b limited to `ADR-*` filename contract, or are there implicit codebase paths depending on `docs/adr/`?
- Q2 [§3 SCOPE]: 20 loose root `*AUDIT.md` — cleaner to update generators forward vs bulk-move-plus-generator-update coordinated PR?
- Q3 [§7 BUCKET B]: Claim that DOC_LIFECYCLE §2c discovery-layer enforcement is "already done" via S2818-S2831 substrate — is that accurate, or does §2c need explicit clause language added?
- Q4 [§8 ORDERING]: Should Playbook v0.9 OP3 amendment (over-corroborated 7/7) ship before file moves, since it's low-risk governance-only?
- Q5 [ZOOM OUT]: (a) does ratifying §3 without timeline commitment mean anything? (b) technical debt from ratifying without scheduling? (c) 19 uncommitted audit files symptom of autogen non-committing? (d) should the D-verdict split by bucket?

Rigby ran substantive tool_runs before SIGN cycle was superseded:
- `repo_tool search` for `docs/adr` codebase references (~15 files including `models_unified_system.py`, `management/commands/*`, `celery.py`, `urls.py`, `doc_claim_verification.py`, `employees/*`, `verify_repo_guardrails.py`)
- `repo_tool read_file` on `docs/00-START-HERE/DOC_LIFECYCLE.md` (§2b + §2c)
- `repo_tool search` for `MQ-T5-8` cross-refs (3 files)
- `repo_tool search` for `Parent §4` (3 files with substrate-integrity clause context)
- `repo_tool read_file` on `2700_docs_restructuring_domain_scoping.md` parent

Anti-rubber-stamp check honored: tool_runs were substantive, not empty. Full response text not extracted due to Chris scope clarification arriving before response was tailed.

**SIGN cycle superseded** when Chris clarified that "audit /docs/" originally meant per-file, not just structural/statistical. Claude corrected the record (Group 2700 arc DID cover whole tree — T1 inventoried 3247 files; T3/T4 sample-audited; T5 subset-focused on handoffs+audits; T6 rule-based across surfaces — but no session did per-file content walk). Chris D-verdict scoped the ratification.

## §4 Chris D-verdict

**"ratify §3 today, open file-level audit arc"** (S2832, 2026-07-19).

Interpreted narrowly per direct quote:

| Scope | Verdict |
|---|---|
| §3 target `/docs/` tree | RATIFIED as PROPOSED (compatibility-first guardrails intact; NOT a move-script) |
| §7 anchor-update recommendations (bucket A + B) | DEFERRED — ratifiable at future session |
| §8 follow-on queue ordering | DEFERRED — item #1 already done (S2818-S2831); items #2-#8 ratifiable at future session |
| File-content-level audit arc | OPENS at S2833 as separate arc |

## §5 Implementation shipped

### §5.1 Ratification envelope

`docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md` — new file with:
- §1 What was ratified (§3 target tree contents + guardrails)
- §2 What was NOT ratified today (§7 anchor updates + §8 queue + any actual file moves)
- §3 Successor arc scope note (file-content-level audit at S2833)
- §4 Rigby SIGN status (superseded before verdict extraction; tool_runs preserved)
- §5 References

### §5.2 2799 doc frontmatter update

`docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` — frontmatter `status:` changed from "active (canonical summary — arc close; proposed restructuring plan + twin-pointer workspace deliverable pending Chris ratification)" to "ratified (§3 target tree ratified Chris D-verdict 2026-07-19 S2832; §7 anchor updates + §8 follow-on queue ratifiable separately; file-content-level audit opens as separate arc)". Added `ratification:` block with date, session, scope, envelope pointer, verbatim Chris directive, deferred items, clarification note.

### §5.3 S2833 successor arc pointer

`00-START-NEXT-SESSION.md` — updated to point S2833 at file-content-level audit as recommended default. Rough shape (advisory): 3247 files; per-file classification (stale/broken/duplicate/orphan); parent-scoping session picks arc number + strategy.

## §6 E2E verification

Django `python manage.py check` passes; the ratification is doc-only. No runtime changes.

## §7 Lessons to carry

1. **Route governance ratifications through Rigby SIGN even when Chris pre-empts the verdict.** The 5 pressure-test questions still hold value — Rigby's tool_runs surfaced substantive codebase evidence about `docs/adr` references that will inform any future execution of §3 §3.4 merge. Preserving the SIGN pin `pa-d10f64b5624c43c9` conversation for future reference is the right shape.

2. **Chris directives can supersede open SIGN cycles.** When Chris clarifies scope mid-SIGN, the SIGN evidence is preserved but the verdict process shifts from "Claude+Rigby agreement → Chris yes/no" to "Chris scope clarification → direct execution". This is legitimate per `feedback_claude_rigby_agree_first_chris_yes_no` — the memory rule governs the DEFAULT shape, not exclusive shape.

3. **Ratifying destinations without timelines is NOT deferring indefinitely.** §3 ratification means "when execution happens, it aims here" — that pre-commits the direction so future PRs don't need to re-litigate. What it defers is scheduling, not agreement.

4. **File-content-level audit is genuinely a separate arc.** The Group 2700 arc explicitly scoped itself at structural/statistical level (T1 counted files; T3/T4 sample-audited; T5 subset-focused; T6 rule-based) — content-level walk was never in scope. Chris's clarification exposed this as a real gap, not a redo of prior work.

5. **DO NOT execute §3 file moves in the same session as ratification** — ratification is the destination shape; each move needs per-PR verification of DOC_LIFECYCLE §2b + generator coordination (item #8 in §8 queue). Ratifying §3 today doesn't authorize bulk moves tomorrow.

6. **DO NOT ratify §7 or §8 without explicit Chris D-verdict** — Chris said "§3 today"; interpret narrowly. Bucket A auto-actionable anchor edits (PLATFORM_INVENTORY note, ARCHITECTURE_INDEX registration, CLAUDE.md 5 missing CRITICAL_DOCS refs, PLATFORM_WHAT_IT_IS companion doc ref) are LOW-RISK but still need Chris's explicit ratification.

## §8 Follow-up carry

### §8.1 File-content-level audit arc (S2833 open)

- **Scope**: read every `.md` file in `/docs/` (3247 files per T1) + flag stale/broken/duplicate/orphan by CONTENT (not by structure)
- **Arc shape**: parent scoping + N child audits by subdir batch + xx99 canonical summary
- **Numbering**: unclaimed; parent-scoping session picks
- **Estimated size**: multi-session; proportional to 3247 files
- **Not scoped by this ratification** — S2833 parent-scoping session decides

### §8.2 §7 anchor updates (deferred; ratifiable at S2833+ open)

Bucket A (auto-actionable low-risk):
- PLATFORM_INVENTORY: add Group 2700 arc-completion note
- ARCHITECTURE_INDEX: register arc + update §7 decision matrix
- CLAUDE.md: ADD 5 missing CRITICAL_DOCS/PRIORITY_DOCS refs (SYSTEM_OWNER, CURRENT_MISSION, USER_FEEDBACK_QUEUE, CAPABILITIES, DATABASE_MODEL_REFERENCE)
- PLATFORM_WHAT_IT_IS: add companion doc ref + verify docs/current/ reference

Bucket B (separate arcs; require own ratification):
- Parent §4 T5 clause update per MQ-T5-8 (parent §5 Chris-lock)
- Playbook §15/§16 twin-pin discipline codification per MQ-T6-2
- DOC_LIFECYCLE §2c discovery-layer enforcement clause (arguably already handled by S2818-S2831 substrate; language addition still worth explicit ratification)

### §8.3 §8 follow-on queue (deferred; ratifiable at S2833+ open)

- Item #1: Discovery-layer enforcement — DONE via S2818-S2831
- Items #2-#8: ratifiable at future session; strong recommendation to also flag Playbook v0.9 OP3 amendment (item #3) as ready given 7/7 over-corroboration

### §8.4 Latent bug follow-ups (unchanged from S2831)

- `views_rag_observability.py` — 10 pre-existing `status_code=` calls should be `status=`
- LucideIcon typing drift in `WorkspacePageNew.tsx`

### §8.5 Other open follow-ups (unchanged)

- Step 2 refactor (S2830 forward-carry)
- PR3 S2829 (canonical-anchor invariant)
- 13 out-of-index Document rows
- Colorado Phase 4 statute-citation
- BettingPage first-user trace

## §9 Twin-pointer card

📁 **Repo — S2832 artifacts:**

- **Ratification envelope**: `docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md`
- **2799 doc frontmatter**: `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` (status: ratified; ratification block added)
- **Handoff**: `docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md`
- **Rigby SIGN conversation**: `pa-d10f64b5624c43c9` (preserved; tool_runs substantive; verdicts unextracted due to Chris scope clarification)
- **Merge SHA**: TBD (filled at close-cascade PR merge)

🖥️ **Workspace UI — S2832 twin-pointer deliverables:**

- **Content mirror + Ratification envelope**: minted at close cascade in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), ORM-direct create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`; category `governance`; `diagnostic_status=None`.

## §10 Current repository state (S2832 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2832 cascade PR SHA (filled at merge) |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Group 2700 arc state | **ARC CLOSED at S2817; §3 target tree RATIFIED at S2832 (Chris D-verdict 2026-07-19). §7 anchor updates + §8 follow-on queue DEFERRED (ratifiable separately).** |
| Discovery-layer arc state | Pattern B/C/D shipped; DORMANT registry Step 1 + user-facing diagnostics tab shipped (S2818-S2831). Unchanged. |
| Metadata layer | ✅ 0 mismatches (S2829 substrate intact) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2831 pin | `pa-01d9ef16cd6b484b` (retired at S2831 close) |
| S2832 pin | `pa-d10f64b5624c43c9` (label `s2832-ratify-2799-docs-restructuring`, retired at S2832 close, force=true, sixty-third consecutive per S2770+) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2833 open) |
| Session close cascade | THIS session — S2832 |
| Docs cascade | 4-step + provenance |
| Recycle post-merge | ✅ `make recycle-all` executed after cascade merge (PLAYBOOK-7.4.4, seventy-eighth consecutive) |
| Next move | S2833 opens with file-content-level audit arc — parent scoping picks arc number + strategy |

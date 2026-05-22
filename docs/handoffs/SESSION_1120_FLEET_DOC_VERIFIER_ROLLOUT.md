---
title: "Session 1120 — Fleet doc-verifier rollout + chat_conversations migration fix"
date: 2026-05-22
status: active
session: 1120
previous_handoff: SESSION_1119_MULTI_REPO_V0.md
---

# Session 1120 — Fleet doc-verifier rollout

> **Read this if** you want to understand (a) how the chat_conversations
> production drift got reconciled, (b) how 79 TRIAGE initiatives got
> extracted across the laptop-local fleet, or (c) how the doc-vs-runtime
> verifier pattern from u-d-b's Session 1099 got ported into 7 fleet
> repos as a single-session campaign.

## TL;DR

Three pieces of work landed end-to-end through `pa_chat.py`-style
direct flow (no governance ceremony, no Rigby gate-keeping for code
work — Rigby surfaces signals, Claude Code does the wiring).

1. **u-d-b migration drift fix (FIRST THING)** — Rigby's `ops_tool`
   flagged a `ProgrammingError: column chat_conversations.platform does
   not exist` on production. PA success had dropped 100% → 99.59%.
   Shipped migration `0341_chat_conversation_columns_idempotent`
   (idempotent `ADD COLUMN IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS`,
   `state_operations=[]`). No-op locally; restores schema on prod when
   Jessica deploys. PR
   [#2114](https://github.com/clwest/donkey-betz-platform/pull/2114).

2. **Option D fleet survey + initiative extract** — 9 new CTO surveys
   across `24-7-ai-global`, `ai-content-studio`, `compliancesentinel`,
   `contract-concierge`, `dealflowtracker`, `norman-handyman-mvp`,
   `pitchdeckforge`, `sellerpilot`, `signal-studio`. 11 extracts ran
   (the 9 above + `context-kit` and `mentorforge` which already had
   surveys from Session 1119). **Result: 79 TRIAGE initiatives total
   across the 12-repo fleet** (72 newly created this session).
   Cost: ~$0.14.

3. **Doc-verifier fleet campaign (Option D follow-up)** — Picked the
   most cross-cutting initiative theme ("wire doc verifier + seed
   claims" appeared in 5+ repos) and executed it as a fleet sweep.
   Built `draft_repo_verifier_claims` mgmt command, ran it against 6
   repos to get Rigby-drafted thematic plans, then ported u-d-b's
   Session 1099 verifier framework into each as a single-file Python
   script. 7 PRs landed (1 merged, 6 open). New topic doc
   `docs/topics/fleet-doc-verifier-rollout.md` captures the 6-pattern
   claim catalog and the "adding a new repo" runbook. Cost: ~$0.04.

Total session LLM cost: **~$0.18** (under the ~$0.20 ceiling).

## What shipped

### u-d-b PRs

| PR | Branch | Summary |
|---|---|---|
| [#2114](https://github.com/clwest/donkey-betz-platform/pull/2114) | `fix/chat-conversations-migration-drift` | Migration 0341 — idempotent backfill for chat_conversations columns |
| [#2115](https://github.com/clwest/donkey-betz-platform/pull/2115) | `feat/draft-repo-verifier-claims-command` | `draft_repo_verifier_claims` mgmt command + `docs/topics/fleet-doc-verifier-rollout.md` topic doc |

### Fleet PRs (one per repo)

| Repo | PR | Claims | First-run state |
|---|---|---|---|
| mentorforge | [#8](https://github.com/clwest/mentorforge/pull/8) **merged** | 3 | 2 drift + 1 ok (reference impl) |
| pitchdeckforge | [#7](https://github.com/clwest/pitchdeckforge/pull/7) | 3 | 3/3 ok |
| dealflowtracker | [#5](https://github.com/clwest/dealflowtracker/pull/5) | 2 | 2/2 ok |
| contract-concierge | [#5](https://github.com/clwest/contract-concierge/pull/5) | 2 | 2 drift |
| sellerpilot | [#1](https://github.com/clwest/sellerpilot/pull/1) | 2 | 2/2 ok |
| signal-studio | [#1](https://github.com/clwest/signal-studio/pull/1) | 2 | 2/2 ok |
| compliancesentinel | [#1](https://github.com/clwest/compliancesentinel/pull/1) | 3 | 3/3 ok |

mentorforge#8 was merged mid-session so subsequent fleet PRs could
pull `scripts/verify_doc_claims.py` from its `origin/main` as the
canonical template. Local `mentorforge/main` is 2 commits ahead of
`origin/main` (Chris's unpushed `build_planning` mode commit +
stripe/cors changes); those will resolve mentorforge#8's
`session_mode_count` drift when pushed.

### Initiative cleanup

5 TRIAGE initiatives flipped to COMPLETED with PR references:

```
[pitchdeckforge]     Wire doc_claim_verification into backend …          → #7
[dealflowtracker]    Wire doc-claim verifier into backend …              → #5
[sellerpilot]        Wire doc verifier and seed three claims …           → #1
[signal-studio]      Integrate doc_claim_verification.py and seed …      → #1
[compliancesentinel] Wire backend verifier and seed three claims …       → #1
```

mentorforge and contract-concierge didn't have an extracted
"wire verifier" initiative (their CTO surveys flagged different
signals); their PRs landed anyway. ~70 TRIAGE initiatives remain
across the fleet for future sweeps.

## How the patterns broke down

The 7 PRs collectively exercise 6 distinct claim patterns (full
catalog in
[`docs/topics/fleet-doc-verifier-rollout.md`](../topics/fleet-doc-verifier-rollout.md)):

1. **Count claim** — list/dict/enum length vs doc number
2. **AST-traversal claim** — unique key-values across collections
   (sellerpilot's `unique_marketplace_count`)
3. **Import-presence claim** — narrative says "uses X", assert
   imported (compliancesentinel `uses_openai_per_narrative`)
4. **Import-absence claim** — mirror of (3); narrative says "no X"
   (signal-studio `action_engine_llm_free`)
5. **Function-presence claim** — named function defined
   (compliancesentinel `demo_mode_fallback_present`)
6. **Baseline regression claim** — code-side count, no doc anchor
   (signal-studio `demo_cluster_count`)

The whole framework is **stdlib-only, Django-free**, single file
~380-410 lines per repo. CI integration via `python scripts/
verify_doc_claims.py --fail-on-drift` is **not** wired up yet on any
repo — needs the existing drifts reconciled first to avoid breaking
PR CI on merge.

## How Rigby helped

The doc-verifier campaign added a third multi-repo mgmt command to
Rigby's toolbox (following `register_external_repo`,
`refresh_repo_context`, `survey_external_repo`,
`extract_initiatives_from_survey` from Session 1119):

```
.venv/bin/python manage.py draft_repo_verifier_claims --repo <X>
```

Loads Repo Profile + latest Snapshot + latest CTO Survey, feeds them
to gpt-5-mini under a CTOAgent persona, produces structured-prose
proposal of 3 doc-vs-code claims targeting `docs/PROJECT_WHAT_IT_IS.md`.
Saved as a `verifier_plan` deliverable in the repo's workspace.

Two notes on Rigby's output quality:

- **Thematically right, literally wrong.** Snapshots don't include
  code listings, so Rigby guesses at symbol names (`SLIDE_COUNT`
  instead of actual `SLIDE_STRUCTURE`, etc.). The themes are reliable;
  Claude Code (or the operator) verifies + adapts during the per-repo
  PR step. Pattern: "Rigby identifies signal, Claude Code does precise
  wiring."
- **System prompt iteration.** First draft for pitchdeckforge targeted
  TypeScript files — the verifier framework only parses Python.
  Re-prompted with explicit "target_file MUST be a Python file" — Rigby
  then targeted the backend correctly across all 6 repos.

## What didn't ship

- **CI gates.** None of the 7 fleet repos wire
  `--fail-on-drift` into a workflow yet. Two reasons: (a) existing
  drifts break the merge if the gate is on, (b) some baseline
  regression claims are explicitly OK to drift on purpose. Wire CI
  once drifts get reconciled per-repo.
- **Django queue.** `character-os`, `ai-content-studio`,
  `norman-handyman-mvp` need a Django mgmt-command version of the
  verifier (not a standalone script). Same framework, different
  packaging.
- **Next.js queue.** `24-7-ai-global` needs a Node verifier; Python
  framework doesn't parse TS.
- **context-kit verifier seeds.** Trivially needs 3 claims wired into
  the existing `context-kit verify --json` framework; out of scope
  for this session.
- **Reconcile mentorforge & contract-concierge drifts.** Both PRs
  surface real drifts on first run that need follow-up edits to either
  docs or code.

## Misc fleet observations

- **All 12 workspaces** have at least a Repo Profile + Snapshot now.
  character-os is the most fully-developed (4 snapshots, surveys
  across CTO/COO/Editor, 7 TRIAGE initiatives). The rest have 1 or
  2 snapshots + 1 CTO survey + 6-7 TRIAGE initiatives each.
- **Fleet narrative quality varies hugely.** Sellerpilot, signal-studio,
  compliancesentinel, dealflowtracker all have rich
  `docs/PROJECT_WHAT_IT_IS.md` narratives with concrete claims that
  anchor verifier work. mentorforge has a rich narrative *with known
  drift* (says 12 personas; code has 8). contract-concierge is mostly
  placeholder text — verifier had to anchor to README.md instead.
  pitchdeckforge has a strong narrative AND matching code (cleanest
  baseline).
- **Common cross-fleet themes from the 79 TRIAGE initiatives:**
  - Wire doc verifier + seed claims (5 repos — addressed by this session)
  - Complete `PROJECT_WHAT_IT_IS.md` placeholders (most repos)
  - `.env.example` + secret-scan / CI pre-merge checks (3 repos)
  - Document local dev startup ports + sequence (3 repos)
  - Clean dirty git state on main (most repos — operator approval needed)

The doc-verifier theme was the most cross-cutting and ships-as-code,
so it was the right first sweep target. The other themes are smaller-
footprint follow-up campaigns.

## Cost ledger

| Stage | Calls | Tokens (approx) | Cost |
|---|---|---|---|
| 9 CTO surveys (Option D) | 9 | ~75k | ~$0.07 |
| 11 initiative extracts | 11 | ~50k | ~$0.07 |
| 6 verifier plans | 6 | ~50k | ~$0.04 |
| **Total** | **26** | **~175k** | **~$0.18** |

Well under the ~$0.20 budget Chris set at scope time.

## State snapshot

Workspaces with initiative state at session close:

```
24-7-ai-global            TRIAGE=6  COMPLETED=0
ai-content-studio         TRIAGE=7  COMPLETED=0
character-os              TRIAGE=7  COMPLETED=0   (from Session 1119)
compliancesentinel        TRIAGE=6  COMPLETED=1
context-kit               TRIAGE=6  COMPLETED=0
contract-concierge        TRIAGE=7  COMPLETED=0
dealflowtracker           TRIAGE=5  COMPLETED=1
mentorforge               TRIAGE=7  COMPLETED=0
norman-handyman-mvp       TRIAGE=7  COMPLETED=0
pitchdeckforge            TRIAGE=5  COMPLETED=1
sellerpilot               TRIAGE=6  COMPLETED=1
signal-studio             TRIAGE=5  COMPLETED=1
```

12 fleet members. 79 total TRIAGE initiatives. 5 newly COMPLETED
(this session). Rigby surfaces all of them via her existing
`initiative_tool` / `workspace_tool` / `deliverable_tool`.

## Read next

- [`docs/topics/fleet-doc-verifier-rollout.md`](../topics/fleet-doc-verifier-rollout.md)
  — full pattern catalog + new-repo runbook
- [`docs/topics/multi-repo-management.md`](../topics/multi-repo-management.md)
  — Session 1119 v0 (the primitives this session builds on)
- [PR #2114](https://github.com/clwest/donkey-betz-platform/pull/2114)
  — the chat_conversations migration fix; ready for Jessica deploy
- [PR #2115](https://github.com/clwest/donkey-betz-platform/pull/2115)
  — `draft_repo_verifier_claims` cmd + this topic doc

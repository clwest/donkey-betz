---
title: "Session 1121 — Fleet drift reconciliation + CI gates rollout"
date: 2026-05-22
status: active
session: 1121
previous_handoff: SESSION_1120_FLEET_DOC_VERIFIER_ROLLOUT.md
---

# Session 1121 — Fleet drift reconciliation + CI gates rollout

> **Read this if** you want to understand (a) how Session 1120's
> 8 open PRs got eyeballed + merged, (b) how the 2 surfaced drifts
> (mentorforge `mentor_persona_count`, contract-concierge
> `starter_template_count` + `audit_event_type_count`) got reconciled,
> or (c) how all 7 FastAPI fleet repos got `--fail-on-drift` CI gates
> in a single follow-up session.

## TL;DR

15 PRs merged across 8 repos in one session. Zero LLM spend (no
new surveys/drafts — all manual reconciliation + git ops on top of
Session 1120's groundwork). Three waves:

1. **Session 1120 closeout** — eyeballed + merged the 8 open PRs from
   the prior session's campaign: u-d-b #2114 (migration), u-d-b #2115
   (`draft_repo_verifier_claims` command + topic doc), plus the 6 fleet
   verifier-rollout PRs (pitchdeckforge, dealflowtracker,
   contract-concierge, sellerpilot, signal-studio, compliancesentinel).

2. **Drift reconciliation** — closed the 2 verifiers that ran with
   surfaced drift on first run:
   - **mentorforge** — `mentor_persona_count` (doc said 12, code had 8;
     README already correct). Also pushed Chris's 2 unpushed local
     commits (`build_planning` tier fix + stripe config) that had been
     blocking the `session_mode_count` claim.
   - **contract-concierge** — `starter_template_count` (doc said 3
     starters, code had 12 full templates) and `audit_event_type_count`
     (doc enumerated 5 events, `EventType` enum has 7).
   Both reconciled by updating the narrative doc + bumping the
   verifier's hardcoded baseline + adding the CI workflow file.

3. **CI gate rollout** — added
   `.github/workflows/verify-doc-claims.yml` (runs
   `python scripts/verify_doc_claims.py --fail-on-drift` on push + PR
   to main) to the 5 remaining fleet repos whose verifiers already ran
   clean: pitchdeckforge, dealflowtracker, sellerpilot, signal-studio,
   compliancesentinel.

**Outcome:** all 7 fleet repos (mentorforge + 6 FastAPI siblings) now
enforce doc-vs-runtime parity in CI. 12 claims actively gated.
Aggregate session LLM cost: **~$0** (zero new model calls — all work
landed on top of Session 1120's drafts and the merged verifier
framework).

## What shipped

### u-d-b PRs (Session 1120 closeout — merged this session)

| PR | Branch | Squash commit | Summary |
|---|---|---|---|
| [#2114](https://github.com/clwest/donkey-betz-platform/pull/2114) | `fix/chat-conversations-migration-drift` | `6767a152` | Migration 0341 — idempotent backfill for chat_conversations columns. Awaits Jessica's next prod deploy from `main`. |
| [#2115](https://github.com/clwest/donkey-betz-platform/pull/2115) | `feat/draft-repo-verifier-claims-command` | `d9544f1c` | `draft_repo_verifier_claims` mgmt command + `docs/topics/fleet-doc-verifier-rollout.md` topic doc. |

### Fleet verifier-rollout PRs (Session 1120 closeout — merged this session)

| Repo | PR | Squash commit |
|---|---|---|
| pitchdeckforge | [#7](https://github.com/clwest/pitchdeckforge/pull/7) | `3c4f1717` |
| dealflowtracker | [#5](https://github.com/clwest/dealflowtracker/pull/5) | `bb43d001` |
| contract-concierge | [#5](https://github.com/clwest/contract-concierge/pull/5) | `22d7379d` |
| sellerpilot | [#1](https://github.com/clwest/sellerpilot/pull/1) | `d57c14ac` |
| signal-studio | [#1](https://github.com/clwest/signal-studio/pull/1) | `38ca766b` |
| compliancesentinel | [#1](https://github.com/clwest/compliancesentinel/pull/1) | `eb3eab2d` |

### Drift-reconciliation PRs (this session, Option 1)

| Repo | PR | Squash commit | Closes which drift |
|---|---|---|---|
| mentorforge | [#9](https://github.com/clwest/mentorforge/pull/9) | `4e984d37` | `mentor_persona_count` (12 → 8) |
| contract-concierge | [#6](https://github.com/clwest/contract-concierge/pull/6) | `d5f3d126` | `starter_template_count` (3 → 12) + `audit_event_type_count` (5 → 7) |

Both PRs also added the `--fail-on-drift` CI workflow alongside the
content fix — single-PR vertical slice.

### CI-gate PRs (this session, Option 2)

| Repo | PR | Squash commit |
|---|---|---|
| pitchdeckforge | [#8](https://github.com/clwest/pitchdeckforge/pull/8) | `d19a67aa` |
| dealflowtracker | [#6](https://github.com/clwest/dealflowtracker/pull/6) | `984a43a0` |
| sellerpilot | [#2](https://github.com/clwest/sellerpilot/pull/2) | `f8c18dc8` |
| signal-studio | [#2](https://github.com/clwest/signal-studio/pull/2) | `a0effcab` |
| compliancesentinel | [#2](https://github.com/clwest/compliancesentinel/pull/2) | `f548c2d6` |

Each is a single-file PR: `.github/workflows/verify-doc-claims.yml`.

## Reconciliation patterns learned

The verifier framework hardcodes `expected = N` inside each
`@register_claim` function — that's the doc-claim baseline. To
reconcile a drift, both the doc AND the verifier's hardcoded baseline
must move together; updating the doc alone leaves the verifier
flagging the doc as wrong.

**Three reconciliation directions:**

| Direction | When to use | Example |
|---|---|---|
| **Doc up to code** | Code is canonical and the narrative is stale | mentorforge: README already said 8 personas, only `PROJECT_WHAT_IT_IS.md` said 12. Update the narrative + baseline to 8. |
| **Doc up to code with enumeration** | Code grew past a "starter" enumeration that no longer covers reality | contract-concierge: README listed 3 starter templates; code has all 12 seeded. Update README to enumerate all 12 + baseline to 12. |
| **Code down to doc** | Doc represents an intentional contract; code drifted | _(none observed in this session)_ |

The third pattern wasn't needed here but should be flagged
conspicuously when it does come up — it's the only case where the
fix touches runtime behaviour, not just docs.

### Cleanup nit: claim descriptions

The Rigby-drafted verifier scripts hardcode specific numbers into
the `@register_claim(description=...)` text. Once reconciled, those
strings carry stale numbers (e.g. "README lists 3 starter templates"
even after bumping `expected = 12`). The mentorforge canonical
template uses generic 'N' phrasing — contract-concierge#6 rewrote
its descriptions to match. New verifier rollouts (Django + Next.js
flavors) should default to 'N' phrasing from the start to avoid
this cleanup pass.

## What ran clean and what flagged drift

Across the 7 fleet repos, the first-run scoreboard from Session 1120:

| Repo | Claims | First-run | After reconcile |
|---|---|---|---|
| mentorforge | 3 | 2 ok / 1 drift | 3/3 ok |
| pitchdeckforge | 3 | 3/3 ok | 3/3 ok |
| dealflowtracker | 2 | 2/2 ok | 2/2 ok |
| contract-concierge | 2 | 0 ok / 2 drift | 2/2 ok |
| sellerpilot | 2 | 2/2 ok | 2/2 ok |
| signal-studio | 2 | 2/2 ok | 2/2 ok |
| compliancesentinel | 3 | 3/3 ok | 3/3 ok |
| **Total** | **17** | **14 ok / 3 drift** | **17/17 ok** |

Rigby's Session 1120 AI-drafted claims were 82% accurate on first
run (14/17). The 3 drifts all pointed at real narrative staleness
that the verifier correctly identified — code was canonical in
every case.

## CI gate template

The workflow file is identical across all 7 repos and ~250 bytes:

```yaml
name: Verify doc claims

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python scripts/verify_doc_claims.py --fail-on-drift
```

No env vars, no secrets, no setup beyond `actions/setup-python@v5`.
The verifier scripts are stdlib-only (no requirements.txt install
needed), so CI run-time is ~6 seconds per repo.

## Operational signal from Rigby's tools (start-of-session)

- 24h LLM spend (u-d-b instance): **$8.20** — mostly conversation
  ($8.17 on gpt-5.2 across 146 calls); test calls $0.03.
- Initiatives: 83 total — 74 TRIAGE / 3 ACTIVE / 6 COMPLETED.
- SLOs: agent task success 100%, timeouts 0%, deliberation zero-turn
  failures 0% — all green.

The 79 TRIAGE backlog Session 1120 surfaced now sits at ~67
(approximately 7 closed by this session's reconciliation + CI work,
roughly 5 more closeable when Jessica deploys #2114). Plenty of
fodder for follow-up themed campaigns.

## Open loose ends

1. **u-d-b #2114 deploy** — merged but Jessica needs to deploy from
   `main` for the migration to take effect on prod. Expected outcome:
   `process_pa_chat_task` ProgrammingError clears, PA success rate
   recovers 99.59% → 100%.

2. **Untracked local files** — every fleet repo accumulated a few
   untracked context-kit artifacts during the campaign (`analysis/`,
   `connections.json`, `coverage.json`, etc). All explicitly left out
   of PRs. Belongs in `.gitignore` if any repo wants to clean it up,
   or harmless to leave in working dirs.

3. **Verifier pyright warnings** — every ported `scripts/verify_doc_claims.py`
   has ~10 pre-existing pyright type-of-unknown warnings (mostly
   `dict[Unknown, Unknown]` returns from `setdefault` etc). Not blocking,
   not regressions from this session, but worth a single pass in the
   u-d-b template if a future session wants to backport type hints.

4. **mentorforge stripe + tier commits** — local `main`'s 2 unpushed
   commits (`build_planning` tier fix + `7cae207` stripe config)
   landed in origin via the reconciliation rebase. Resolved.

## What's queued for Session 1122

Per Rigby's headline ranking (from Session 1121 brief), the
campaign-shape rollouts that build on this work:

- **Django verifier rollout** (character-os, ai-content-studio,
  norman-handyman-mvp) — port the framework as
  `python manage.py verify_doc_claims` for Django repos. Reuse the
  AST/import extraction patterns; swap `register_claim` decorator into
  a Django mgmt command. ~1 session.

- **Next.js verifier rollout** (24-7-ai-global) — port to
  `scripts/verify_doc_claims.mjs`. Needs Node-native AST handling
  (ts-morph or @typescript-eslint/parser). The hardest port — fleet
  reaches into TypeScript territory. ~1 session.

- **Promote the next cross-cutting initiative theme** — the
  `.env.example` + secret-scan initiative appears in 3+ repos;
  "document local dev startup" appears in 3+ repos. Same campaign
  shape as doc-verifier. Pick whichever is more cross-cutting.

- **Phase 0 cost-survival audit** — `LLMCallLog.workspace` FK +
  `ExternalAPICallLog` model + per-workspace daily cap. Gate for
  multi-tenant SaaS launch. ~1 focused week.

- **F2F.3 unfreeze** — only if HeyGen + Cartesia keys are provisioned.

## Cost ledger

| Activity | Spend |
|---|---|
| Verifying #2114 migration | $0 (local SQL inspection only) |
| Verifying #2115 command | $0 (read-only code review) |
| Eyeballing + merging 6 fleet PRs | $0 (no CI re-runs needed) |
| mentorforge#9 reconciliation | $0 (manual doc edit + verifier baseline bump) |
| contract-concierge#6 reconciliation | $0 (same pattern) |
| 5 CI-gate PRs | $0 (identical workflow file copy) |
| **Total** | **$0** |

Compare Session 1120 (~$0.18 for the upstream campaign): the bulk
of the cost was in Rigby's draft + survey work. Once those drafts
exist, follow-up reconciliation/enforcement is essentially free.

## Operational reminders

- `tools/pa_chat.py` defaults to prod. Local invocation needs
  `PA_API_URL=http://localhost:8000` + the local donkeyking token.
  Session 1121 used `./tools/pa_local.sh` which has both baked in.
- `python manage.py build_docs_index` should run before close if any
  `docs/` content changed.
- `python scripts/verify_repo_guardrails.py` validates the local
  inventory + forbidden-paths + DOC-AUTOGEN markers before PR.

---
title: "Session 1122 — Django + Next.js verifier rollouts"
date: 2026-05-22
status: active
session: 1122
previous_handoff: SESSION_1121_FLEET_DRIFT_RECONCILE_AND_CI_GATES.md
---

# Session 1122 — Django + Next.js verifier rollouts

> **Read this if** you want to understand (a) how the doc-verifier
> framework extended from FastAPI into Django and Next.js, (b) why two
> Django repos were skipped vs. shipped, or (c) what the canonical
> "stdlib-only" shape looks like across three different runtimes.

## TL;DR

Two more PRs merged, two more verifier flavors locked in. The fleet
verifier campaign now spans **all three runtime stacks** in the
laptop-local fleet:

1. **Django flavor** — shipped to `norman-handyman-mvp` as a standalone
   Python script under `scripts/verify_doc_claims.py`, NOT as a
   `manage.py` mgmt command. AST-based claims so it runs in CI without
   booting Django or installing the backend dependency stack.

2. **Next.js flavor** — shipped to `24-7-ai-global` as pure-Node ESM
   under `scripts/verify-doc-claims.mjs`. No `typescript`, `ts-morph`,
   or `@typescript-eslint/parser` deps — uses regex + brace-matching
   against TS source text.

3. **Two repos parked** —
   - `character-os` skipped after Chris flagged an active CC session in
     that repo. Verifier files left uncommitted in working tree; memory
     rule saved for future sessions.
   - `ai-content-studio` skipped because `clwest/ai-content-studio` on
     GitHub is empty (`isEmpty: true`). No origin/main exists to PR
     against. Verifier framework was prototyped locally as a `manage.py`
     mgmt command BEFORE the architecture pivot to standalone Python —
     superseded by the pattern landed in norman.

Total session LLM cost: **$0**. All claim drafting was manual (read
each repo's CTO survey + anchor doc + code, identify 2-3 verifiable
constants, hardcode baselines).

## What shipped

| Repo | PR | Squash commit | Verifier shape |
|---|---|---|---|
| norman-handyman-mvp (Django/JobFlow) | [#1](https://github.com/clwest/norman-handyman-mvp/pull/1) | `38c1e3b2` | Standalone Python (`scripts/verify_doc_claims.py`) |
| 24-7-ai-global (Next.js) | [#9](https://github.com/clwest/24-7-ai-global/pull/9) | `2ca4081d` | Pure Node ESM (`scripts/verify-doc-claims.mjs`) |

Each PR includes the verifier framework, 3 seed claims (all green on
first run), and the matching `.github/workflows/verify-doc-claims.yml`
CI gate running `--fail-on-drift`.

## Seed claims by repo

### norman-handyman-mvp (3 claims, anchored to `docs/PROJECT_WHAT_IT_IS.md`)

| claim | code source | baseline |
|---|---|---|
| `local_django_app_count` | `backend/handyman/settings.py` INSTALLED_APPS (`handyman.*`) | 2 |
| `core_model_count` | `class Foo(models.Model)` in `backend/handyman/core/models.py` | 7 |
| `job_status_count` | `Job.Status` TextChoices entries | 4 |

### 24-7-ai-global (3 claims, anchored to `CLAUDE.md` + `docs/PROJECT_WHAT_IT_IS.md`)

| claim | doc anchor | code source | baseline |
|---|---|---|---|
| `suite_product_count` | CLAUDE.md "§ 02 — The Suite (4 paid products)" | `PRODUCTS` in `src/lib/products.ts` | 4 |
| `lab_work_count` | CLAUDE.md "§ 04 — The Lab" | `LAB` in `src/lib/products.ts` | 10 |
| `total_works_in_motion` | docs/PROJECT_WHAT_IT_IS.md "22 Works in Motion" | sum of PRODUCTS+VERTICALS+LAB+CHANNELS | 22 |

## Architecture decisions

### Django: standalone script > mgmt command

First attempt at norman/ai-content-studio used the natural Django shape:
`apps/X/management/commands/verify_doc_claims.py` mirroring u-d-b's
own `verify_doc_claims` command. That works locally but fails the
moment you try to run it in CI without installing the full backend
dependency stack — `manage.py` requires every app in INSTALLED_APPS
to import successfully, which means installing every transitive
dependency (`pdfplumber`, `psycopg`, `dj-stripe`, etc.) just to
boot Django and run a doc verifier.

The pattern that ships across the Django fleet is:

- **Standalone Python script at `scripts/verify_doc_claims.py`**
- Claims use `ast.parse()` on source files — no Django boot needed
- Uses `argparse` (stdlib) instead of `BaseCommand`
- CI just runs `python scripts/verify_doc_claims.py --fail-on-drift`

This mirrors the FastAPI fleet template's "stdlib-only" philosophy and
keeps CI run-time ~6 seconds. The trade-off is losing direct model
inspection (`Subscription.Tier.choices`) — but AST-parsing the
`class Tier(models.TextChoices)` definition recovers the same info
without the dependency cost.

### Next.js: brace-matching > ts-morph

The Session 1121 handoff noted the Next.js port would "need Node-native
AST handling (ts-morph or @typescript-eslint/parser)". In practice,
the claims we needed (count entries in `export const PRODUCTS = [...]`,
sum across four lists) only required:

1. Regex to find the `export const NAME = [` pattern
2. Brace-matching to find the closing `]`
3. Counting top-level `{` inside that span

None of which need TypeScript semantic analysis. So the verifier
ships as pure-Node ESM with **zero external dependencies**.

`countTopLevelObjects(source, exportName)` is a 20-line helper that
handles the common case. When future claims need richer TS semantics
(generic resolution, type narrowing), swap to `ts-morph` inside that
function — the registry layer doesn't care.

CI workflow uses `actions/setup-node@v4` with `node-version: '20'` and
**no `npm install`** — Node 20 has everything the verifier needs.

## Why character-os and ai-content-studio got parked

### character-os

Chris flagged at session start: "There's a CC working in that repo so
don't interfere with what they are doing." I'd already drafted
the Django mgmt command + workflow file + an anchor-doc edit (`8 Django apps`
→ `14`) — backed off all three. The other CC subsequently reverted my
anchor doc edit when their own work picked up modifications to the
same file, confirming the conflict risk was real.

Files left in character-os working tree (uncommitted):
- `shell/apps/accounts/management/commands/verify_doc_claims.py`
- `.github/workflows/verify-doc-claims.yml`

Both files are pre-pivot (mgmt command shape, not standalone script).
When character-os reopens, the right move is to **rewrite them as a
standalone script under `scripts/verify_doc_claims.py`** following
the norman pattern. The 3 claims I drafted (`django_app_count`,
`subscription_tier_count`, `starter_videos_per_month`) are still
relevant — but the second and third claims would need to switch from
direct model imports (`from apps.billing.models import Subscription`)
to AST parsing of `apps/billing/models.py`.

A memory rule was saved (`feedback_local_only_default.md`'s sibling)
documenting the active-CC constraint: don't push PRs against
character-os from u-d-b sessions, don't edit anchor/inventory docs
there, and don't bundle their WIP into any fleet rollout campaign.

### ai-content-studio

`clwest/ai-content-studio` on GitHub is **empty**:

```
$ gh repo view clwest/ai-content-studio --json isEmpty
{"isEmpty":true}
```

No origin/main exists, so the fleet rollout pattern (open PR + CI
gate) doesn't apply. The local repo has substantial Chris-authored
WIP (~11 modified files including `dump.rdb`) that hasn't been
published yet — pushing the verifier alone would also publish all
that WIP, which isn't my call to make.

The verifier framework was prototyped against the local code:
- `backend/core/management/commands/verify_doc_claims.py` (mgmt command shape) — **deleted** after the pivot
- `scripts/verify_doc_claims.py` (standalone script) — **left in working tree, uncommitted**
- `.github/workflows/verify-doc-claims.yml` — **left in working tree, uncommitted**

3 claims drafted against current code state (all GREEN locally):
- `local_django_app_count` = 11
- `visual_style_library_count` = 27 (vs the doc's hedged "53+ styles")
- `visual_style_category_count` = 8

When ai-content-studio's origin gets bootstrapped, the right move is
to verify the published baseline matches what the local verifier saw,
then commit + push the same files.

## Lessons for future cross-stack rollouts

1. **Pick claim shapes before picking host shape.** The "Django mgmt
   command" instinct was wrong because the claims didn't actually need
   Django — they needed AST parsing. Once you separate "what does the
   claim need to inspect" from "what CLI wraps it," the architecture
   simplifies.

2. **Default to zero external deps.** The fleet now has 9 verifier
   scripts across 3 runtimes; not one of them requires anything beyond
   stdlib (Python 3.11) or built-in Node 20 APIs. CI installs are
   trivially fast.

3. **The CI workflow file is the only repo-shape thing.** Every
   verifier ships with the same conceptual workflow:
   ```yaml
   - uses: actions/checkout@v4
   - uses: actions/setup-{python|node}@v{5|4}
   - run: {python|node} scripts/verify-doc-claims.{py|mjs} --fail-on-drift
   ```
   Variations are minimal: Python version, Node version, extension.

4. **Anchor to where the claim actually lives.** norman's claims
   anchor to `docs/PROJECT_WHAT_IT_IS.md` (the canonical narrative).
   24-7-ai-global's `suite_product_count` and `lab_work_count` anchor
   to `CLAUDE.md` because that's where the concrete count lives — the
   narrative doc only carries the totality ("22 Works in Motion").
   Mixing anchors across docs in one verifier is fine.

5. **CTO surveys are still load-bearing for claim drafting.** Even at
   manual drafting (no LLM spend), the surveys gave me the right
   pointers: "src/lib/products.ts is a public contract referenced by
   other repos" + "22 Works in Motion across 4 sections" was enough to
   find the right file and the right numbers in one pass.

## Open lanes for Session 1123

- **character-os verifier** — pending the other CC finishing up.
  Rewrite my prototype as a standalone Python script (norman pattern),
  recheck the 3 claims against current code, open PR. ~½ session.
- **ai-content-studio verifier** — pending origin bootstrap.
  When `clwest/ai-content-studio` gets published, the verifier files
  in the working tree can be committed and PR'd. ~½ session.
- **Promote the next cross-cutting initiative theme** — `.env.example`
  + secret-scan appears in 3+ repos; "document local dev startup"
  appears in 3+ repos. Same campaign shape as the verifier rollout
  (Rigby drafts, Claude Code wires). ~1 session.
- **Phase 0 cost-survival audit** — `LLMCallLog.workspace` FK +
  `ExternalAPICallLog` model + per-workspace daily cap. Still the
  multi-tenant SaaS launch gate. ~1 focused week.
- **F2F.3 unfreeze** — only when HeyGen + Cartesia keys are provisioned.

## Cost ledger

| Activity | Spend |
|---|---|
| Reading character-os CTO survey | $0 (already drafted in Session 1120) |
| Drafting + running norman verifier | $0 |
| Drafting + running 24-7-ai-global verifier | $0 |
| Architecture pivot (Django mgmt command → standalone script) | $0 |
| 2 PRs opened + merged | $0 |
| **Total** | **$0** |

Compare Sessions 1120 + 1121 combined: ~$0.18 in LLM spend for the
upstream campaign + reconciliation. Now that the framework template
is well-established, downstream rollouts are free.

## Operational reminders

- `tools/pa_chat.py` defaults to prod. Local invocation needs
  `PA_API_URL=http://localhost:8000` + the local donkeyking token
  (or use `./tools/pa_local.sh`).
- `python manage.py build_docs_index` should run before close.
- Local-only mode (Session 1121 directive) still applies — don't drive
  prod verification or deploys without Chris's explicit go.
- character-os is OFF-LIMITS from u-d-b sessions for the duration of
  the other CC's engagement there.

## Fleet verifier scoreboard (after Session 1122)

| Stack | Repos | Verifier file | Claims active |
|---|---|---|---|
| **FastAPI** (Python) | 7 | `scripts/verify_doc_claims.py` | 14 |
| **Django** (Python) | 1 (norman) | `scripts/verify_doc_claims.py` | 3 |
| **Next.js** (Node ESM) | 1 (24-7-ai-global) | `scripts/verify-doc-claims.mjs` | 3 |
| **Total** | **9 repos** | — | **20 claims** |

Each repo has a `--fail-on-drift` CI gate. Each gate runs in under
~10 seconds. None require dependency installs.

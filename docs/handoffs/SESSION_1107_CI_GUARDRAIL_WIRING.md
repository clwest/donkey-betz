---
title: "Session 1107 — CI guardrail wiring (R1)"
date: 2026-05-08
status: active
session: 1107
previous_handoff: SESSION_1106_MASTER_CONTEXT_UNTRACK.md
---

# Session 1107 — CI guardrail wiring (R1)

## TL;DR

- **Shipped:** `.github/workflows/repo-guardrails.yml` invokes `scripts/verify_repo_guardrails.py --inventory-advisory` on every PR and push to `main`. Strict mode is on for three high-value checks (tracked-paths, DOC-AUTOGEN marker, `context-kit verify` CONFLICT findings); platform-inventory freshness is reported but advisory in CI only.
- **Why advisory there:** `generate_platform_inventory` needs DB access that the GitHub runner doesn't have. Local strict runs (no flag) **still fail on stale inventory** — regenerate before opening a PR when you can.
- **No runtime app code touched.** Surface area: 1 script change (additive flag), 1 unit-test extension, 1 new workflow file, 2 nav doc updates, this handoff.
- **Carryover:** `stash@{0}` (Docker subnet override) still preserved.

---

## What Shipped

### 1. `scripts/verify_repo_guardrails.py` — narrow `--inventory-advisory` flag

New CLI flag (additive; default behavior unchanged):

```
--inventory-advisory   Treat platform-inventory freshness as advisory
                       (never blocks) even in strict mode. Other strict
                       checks continue to block. Intended for PR-time
                       CI where the inventory regenerator
                       (`python manage.py generate_platform_inventory`)
                       needs DB access that the runner does not have.
                       Local strict runs should not need this flag.
```

Implementation: extracted the strict-mode failure-decision into a pure helper `classify_failures(...)` so the carve-out lives in one place and is testable without spinning up `main()`. The decision matrix is:

```
if strict and tracked_blocking:                         → fail
if strict and inventory_blocking and not inventory_advisory: → fail
if strict and autogen_blocking:                         → fail
if strict and conflict_blocking:                        → fail
```

Other behaviors:

- The freshness WARNING line shifts to a more explicit `"WARNING: platform inventory freshness check failed (advisory under --inventory-advisory; will not fail strict mode)."` when the flag is in effect — so the report still surfaces drift loud and clear.
- The summary line shifts from `platform inventory fresh: False` to `platform inventory fresh: False (advisory)` when the flag is in effect.
- `--no-strict` semantics unchanged. `--inventory-advisory` is orthogonal to (not exclusive with) `--strict` / `--no-strict`.

### 2. `tests/test_verify_repo_guardrails.py` — 12 new unit tests

Three new test classes, all driving the pure `classify_failures` function:

- **`ClassifyFailuresStrictModeTests` (6 tests)** — strict alone: each gate fails individually; multiple gates aggregate; no-blocker case returns empty.
- **`ClassifyFailuresInventoryAdvisoryTests` (5 tests)** — `--inventory-advisory` only carves out freshness; tracked-paths, autogen, and CONFLICT all still block; `--no-strict + --inventory-advisory` reverts to "nothing blocks" (advisory doesn't revive disabled strict mode).
- **`ClassifyFailuresNoStrictTests` (1 test)** — explicit baseline: `--no-strict` never blocks regardless of inputs.

Total guardrail tests: **19/19 pass** (7 pre-existing + 12 new).

### 3. `.github/workflows/repo-guardrails.yml` — new dedicated workflow

```yaml
name: Repo Guardrails

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  repo-guardrails:
    name: Repo Guardrails
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          python -m pip install --upgrade pip
          pip install context-kit
      - run: python scripts/verify_repo_guardrails.py --inventory-advisory
```

Design choices:

- **Dedicated, small workflow** — clearer than appending to an existing one (mirrors the pattern set by `check-llm-sdk.yml`).
- **Triggers on `pull_request` AND `push: main`** — gates merges, and also catches accidental drift on `main` (e.g., direct pushes if branch protection lapses).
- **`fetch-depth: 0`** — the freshness check uses `git rev-parse HEAD^` to allow inventory-only commits; shallow clones break that.
- **`pip install context-kit`** — the script shells out to `context-kit inspect` and `context-kit verify --json`. PyPI install rather than a local install because the package is already published and stable.
- **`timeout-minutes: 5`** — the script is fast (under 10s locally); a 5-minute ceiling guards against runner hangs without being aggressive.

### 4. Documentation updates

- `00-START-NEXT-SESSION.md` — added a "CI GUARDRAIL POLICY (Session 1107)" section with the strict-vs-advisory matrix and the explicit reminder that local strict runs still fail on stale inventory.
- `docs/handoffs/CURRENT.md` — re-pointed at this handoff.

---

## Verification

| Check | Result |
|---|---|
| `python -m unittest tests.test_verify_repo_guardrails -v` | ✅ **19/19 pass** (7 pre-existing + 12 new) |
| `python scripts/verify_repo_guardrails.py` (default strict) | ✅ exits **1** with FAIL summary listing "platform inventory is stale" — unchanged from before this PR |
| `python scripts/verify_repo_guardrails.py --inventory-advisory` | ✅ exits **0** with PASS summary; freshness WARNING still printed with "(advisory under --inventory-advisory; will not fail strict mode)" wording |
| Working tree | clean |
| Pre-existing pyright warnings on `summarize_json` (lines 73–93) | unchanged — none introduced by this PR |
| Runtime app code modified | 0 |
| `docker-compose.yml` modified | 0 |
| `stash@{0}` (Docker subnet override) | preserved |

---

## Files Changed

```
M  scripts/verify_repo_guardrails.py     +75 lines (new flag + classify_failures helper + advisory wording)
M  tests/test_verify_repo_guardrails.py  +123 lines (3 new test classes, 12 new tests)
A  .github/workflows/repo-guardrails.yml +43 lines (new workflow)
M  00-START-NEXT-SESSION.md              CI guardrail policy section
M  docs/handoffs/CURRENT.md              re-pointed at SESSION_1107
A  docs/handoffs/SESSION_1107_CI_GUARDRAIL_WIRING.md   this file
```

No backend, frontend, agent, or runtime code modified.

---

## Why this design (and what it deliberately doesn't do)

### Why `--inventory-advisory` instead of `--no-strict` in CI?

`--no-strict` would downgrade **all** strict checks to warnings — defeating the purpose of wiring the guardrail in the first place. The high-value gates (tracked-paths, autogen marker, CONFLICT findings) are exactly the ones we want CI to enforce. The freshness check is the only one that's structurally unsatisfiable from a runner without DB access. `--inventory-advisory` is a narrow carve-out targeted at exactly that one case.

### Why not regenerate the inventory in CI?

That would require a Postgres service container in the workflow + DB credentials + a Django settings shim for CI. Significantly larger lift and adds infra surface. Not in R1's scope. When inventory regen becomes part of CI (separate future PR), the `--inventory-advisory` flag can be dropped from the workflow command (or removed from the script entirely).

### What if a PR genuinely needs the inventory regenerated?

Local workflow: run `python manage.py generate_platform_inventory`, commit the refreshed `docs/PLATFORM_INVENTORY.md`, push. Inventory commits have a special-case in the freshness check — a commit that *only* changes `PLATFORM_INVENTORY.md` passes freshness without needing further work. This was already on `main` from prior cleanup; this PR doesn't change that path.

---

## Runtime Behavior Changes

**None.** The guardrail script and the new workflow are observation/enforcement, not runtime logic. No app, agent, PA, or frontend behavior changed.

---

## Next Session Picks Up With

The remaining queue from PR #2058's deferred items:

1. **`.rag/corpus.jsonl` decision** — investigation already done in Session 1102. Production-dormant; decision is between (A) untrack-only or (B) ship a `build_rag_corpus` command first. Awaiting Chris's preference.
2. **`PLATFORM_INVENTORY.md` regen** — DB-gated; needs Chris's local DB up. Will clear the only outstanding `verify_repo_guardrails` warning.
3. **`BACKEND_INVENTORY.md` hygiene reassessment** — pure cosmetic now that context-kit upstream picks the right anchor via `verify.yaml`. No urgency.
4. **Branch cleanup** — older `chore/docs-index-*` and `chore/cleanup-*` branches are still in the local list; separate hygiene pass when convenient.

---

## Rigby / PA / AI Context

- **Conversation ID:** none for this tooling-only session.
- **State at end of session:** working tree clean, all 19 guardrail unit tests green, strict CI gate ready to land via the new PR. Local strict still catches inventory staleness; advisory carve-out is narrow and well-tested.
- **How to resume:** `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-donkeyking-token> .venv/bin/python tools/pa_chat.py "session 1107 follow-up" --conversation <id>`

---

## Cross-References

- Previous handoff: [`SESSION_1106_MASTER_CONTEXT_UNTRACK.md`](SESSION_1106_MASTER_CONTEXT_UNTRACK.md)
- Phase 2A investigation that motivated R1: SESSION_1107 directly closes gap **G5** ("`verify_repo_guardrails.py` is not wired into CI") from that audit
- Cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
- Verification report: [`docs/verification/VERIFY_REPORT.md`](../verification/VERIFY_REPORT.md)
- Canonical truth docs: [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md), [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)

---

*Written at end of session 2026-05-08. Do not edit after the next session begins. If the next session finds a bug in this handoff's reasoning, add a note at the bottom rather than rewriting — the original reasoning is history.*

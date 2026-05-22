# Fleet Doc-Verifier Rollout — Session 1120

**Session:** 1120
**Status:** v0 shipped 2026-05-22. 7 fleet PRs open (1 merged), pattern catalog established.
**Companion:** [multi-repo-management.md](multi-repo-management.md), u-d-b's `core/services/doc_claim_verification.py` (Session 1099).

> Port u-d-b's doc-vs-runtime verifier framework into each laptop-local
> repo as a single-file script. Each repo gets `scripts/verify_doc_claims.py`
> with 2-3 seed claims that compare what its docs say against what its
> code actually shows. Drift surfaces as a `medium` / `high` severity
> result with a concrete fix suggestion.

---

## TL;DR

Each repo in the fleet that has a FastAPI backend (and reasonably stable
narrative anchor) gets:

```
<repo>/scripts/verify_doc_claims.py   # ~390 lines, stdlib only
```

Run it locally:

```bash
python scripts/verify_doc_claims.py
python scripts/verify_doc_claims.py --only-drift
python scripts/verify_doc_claims.py --format json
python scripts/verify_doc_claims.py --list
python scripts/verify_doc_claims.py --fail-on-drift   # CI gate
```

It reads `@register_claim`-decorated functions in the script and runs
each against the repo's code (via `ast` parse or direct import). Each
result is a `ClaimResult` with severity / expected / actual /
fix_suggestion.

---

## Why this exists

The Session 1119 multi-repo v0 made Rigby aware of each fleet repo as
a managed workspace. Session 1120's Option D sweep added CTO surveys
across 12 repos and extracted 79 TRIAGE initiatives — and the most
frequently surfaced initiative theme was **"wire doc-claim verifier +
seed claims"** in 5+ repos.

Rather than open 5 individual PRs in isolation, the campaign:

1. Built the mentorforge reference impl
2. Built a Rigby-side mgmt command (`draft_repo_verifier_claims`) that
   produces a thematic spec per repo from snapshot + CTO survey
3. Ported the verifier to all 6 remaining FastAPI repos in one session
4. Closed the matching TRIAGE initiatives with PR references

The result: a **fleet-wide guardrail** against narrative drift, plus a
proof point that Rigby + Claude Code can act as a cross-repo build
crew using only existing primitives.

---

## What got shipped (Session 1120)

| Repo | PR | Claims | First-run state |
|---|---|---|---|
| mentorforge | [#8](https://github.com/clwest/mentorforge/pull/8) merged | 3 | 2 drift + 1 ok |
| pitchdeckforge | [#7](https://github.com/clwest/pitchdeckforge/pull/7) | 3 | 3/3 ok |
| dealflowtracker | [#5](https://github.com/clwest/dealflowtracker/pull/5) | 2 | 2/2 ok |
| contract-concierge | [#5](https://github.com/clwest/contract-concierge/pull/5) | 2 | 2 drift |
| sellerpilot | [#1](https://github.com/clwest/sellerpilot/pull/1) | 2 | 2/2 ok |
| signal-studio | [#1](https://github.com/clwest/signal-studio/pull/1) | 2 | 2/2 ok |
| compliancesentinel | [#1](https://github.com/clwest/compliancesentinel/pull/1) | 3 | 3/3 ok |

5 of the 7 had a matching `[<repo>] Wire doc-claim verifier and seed 3
claims — 2026-05-22` initiative; all 5 flipped TRIAGE → COMPLETED with
PR references. mentorforge and contract-concierge didn't have one
extracted (their CTO surveys flagged different signals); the verifier
PR landed anyway.

**Out of scope for v0** — queued for follow-up sweeps:

- **character-os, ai-content-studio** — Django repos. Pattern is the same
  but the verifier wants to live as a `python manage.py verify_doc_claims`
  command instead of a standalone script.
- **24-7-ai-global** — Next.js/TypeScript. Needs a Node verifier; the
  Python-native framework here doesn't parse TS.
- **norman-handyman-mvp** — Django (initially misclassified as FastAPI
  during scoping). Same Django queue.
- **context-kit** — already has its own `context-kit verify --json`;
  just needs claims seeded against it.

---

## Pattern catalog

The 7 PRs collectively exercise 6 distinct claim patterns. Future
repos can copy whichever applies.

### 1. Count claim — list/dict/enum length vs doc number

The basic shape. Doc asserts "N things"; verifier counts the code-side
container.

```python
@register_claim(doc='docs/PROJECT_WHAT_IT_IS.md',
                claim_id='slide_count',
                description="Doc says '10-slide deck'; count SLIDE_STRUCTURE.")
def _slide_count():
    actual = _ast_count_at(REPO_ROOT / "backend/app/main.py", "SLIDE_STRUCTURE")
    expected = 10
    return ClaimResult.build(
        expected=expected, actual=actual,
        severity='ok' if expected == actual else 'medium',
        fix_suggestion=f"Update doc to '{actual}-slide deck' or reconcile constant",
    )
```

Used in: pitchdeckforge (slide/template/bonus counts), mentorforge
(persona/tier counts), dealflowtracker (pipeline_stage_count,
scorecard_dimension_count via enum/BaseModel field counting),
contract-concierge (template/event-type counts), sellerpilot
(seeded_product_count).

### 2. AST-traversal claim — unique key-values across a collection

When the canonical fact lives spread across dict literals in a list
(not in a dedicated constant). The verifier walks each dict, collects
values for a specific key, and dedupes.

```python
@register_claim(...)
def _unique_marketplace_count():
    products = _ast_find_list(seed_path, "PRODUCTS")
    marketplaces = set()
    for elt in products.elts:
        if isinstance(elt, ast.Dict):
            for k, v in zip(elt.keys, elt.values):
                if isinstance(k, ast.Constant) and k.value == "marketplace":
                    if isinstance(v, ast.Constant):
                        marketplaces.add(v.value)
    expected = 3   # narrative: "Amazon, Etsy, and Shopify"
    actual = len(marketplaces)
    ...
```

Used in: sellerpilot (`unique_marketplace_count`).

### 3. Import-presence claim — narrative says "uses X", verifier asserts X imported

Useful when the narrative makes a structural claim about a dependency
(e.g., "GPT-4 drafts memos" → must import openai).

```python
@register_claim(...)
def _uses_openai_per_narrative():
    tree = ast.parse(main_path.read_text())
    openai_imports = [
        ... walk Import / ImportFrom nodes for `openai` ...
    ]
    expected = True
    actual = len(openai_imports) > 0
    return ClaimResult.build(expected=expected, actual=actual,
                             severity='ok' if actual else 'high', ...)
```

Used in: compliancesentinel (`uses_openai_per_narrative`).

### 4. Import-absence claim — narrative says "no X", verifier asserts X not imported

Mirror of (3). Useful when the narrative makes a *structural absence*
claim ("no LLM dependency"). Same AST scan, opposite boolean.

Used in: signal-studio (`action_engine_llm_free`).

### 5. Function-presence claim — named function defined in module

Useful when the narrative claims a behavior tied to a specific function
("Demo-mode fallback returns a structured memo" → `_generate_compliance_memo`
must exist).

```python
@register_claim(...)
def _demo_mode_fallback_present():
    tree = ast.parse(main_path.read_text())
    found = any(
        isinstance(node, ast.FunctionDef)
        and node.name == "_generate_compliance_memo"
        for node in ast.walk(tree)
    )
    return ClaimResult.build(expected=1, actual=1 if found else 0,
                             severity='ok' if found else 'high', ...)
```

Used in: compliancesentinel (`demo_mode_fallback_present`).

### 6. Baseline regression claim — code-side count with no doc anchor

When there's a real code-side count but the narrative doesn't claim a
number. The verifier still tracks it as a "this changed unintentionally"
guard. Bump `expected=` when the change is deliberate.

Used in: signal-studio (`demo_cluster_count` — DEMO_CLUSTERS list).

---

## How Rigby helps

The campaign uses three Rigby-side primitives, in order:

1. `refresh_repo_context --repo <X>` (from Session 1119) — writes the
   Snapshot deliverable.
2. `survey_external_repo --repo <X> --agent cto` (Session 1119) — writes
   a CTO Survey deliverable based on snapshot + Repo Profile.
3. **`draft_repo_verifier_claims --repo <X>`** (Session 1120, this
   rollout) — feeds Profile + Snapshot + CTO Survey to gpt-5-mini and
   produces a structured-prose proposal of 3 doc-vs-code claims.
   Saves as a `verifier_plan` deliverable.

The drafted claims are **thematically right but not literally**:
Rigby doesn't see code listings in the snapshot, so she guesses at
symbol names and file paths. Claude Code (or the operator) verifies
each claim against actual repo state before plugging it into the
verifier file. The pattern is "Rigby identifies signal, Claude Code
does the precise wiring."

Cost: ~$0.005 per draft (gpt-5-mini, ~5.5k prompt + ~2k completion).
Whole-fleet drafts came in around $0.04 for 6 repos.

---

## Adding a new repo

1. **Land the context-kit scaffold** if not already on `main`. Need at
   minimum `docs/PROJECT_WHAT_IT_IS.md` so the verifier has a doc to
   anchor to. If the narrative is `context-kit adopt` placeholder text,
   anchor to `README.md` instead until the narrative gets filled in
   (contract-concierge does this).

2. **Run Rigby's pipeline**:
   ```bash
   .venv/bin/python manage.py refresh_repo_context  --repo <X>
   .venv/bin/python manage.py survey_external_repo  --repo <X> --agent cto
   .venv/bin/python manage.py draft_repo_verifier_claims --repo <X>
   ```
   The `verifier_plan` deliverable surfaces in Rigby's workspace tools.

3. **Copy the verifier template** from mentorforge's `origin/main`:
   ```bash
   git -C ~/development/mentorforge show \
     origin/main:scripts/verify_doc_claims.py \
     > ~/development/<X>/scripts/verify_doc_claims.py
   ```

4. **Verify Rigby's drafted symbols against repo reality**, then plug
   them into the template's "Claims" section. Pick whichever pattern
   from the catalog above fits each claim.

5. **Smoke-test locally**: `python scripts/verify_doc_claims.py` —
   should show your claims with sensible expected/actual values.

6. **Two-commit PR**: scaffold + verifier. Or single-commit if the
   scaffold is already on main. Don't add `--fail-on-drift` to CI
   until the surfaced drifts are reconciled — otherwise the PR breaks
   CI on merge.

7. **Close the matching TRIAGE initiative** with a PR reference:
   ```python
   i = Initiative.objects.get(id='<uuid>')
   i.description += f'\n\n— Closed by Session XXXX. PR: <url>'
   i.status = 'COMPLETED'
   i.save(update_fields=['description','status','updated_at'])
   ```

---

## Why no CI gate yet

The verifier framework supports `--fail-on-drift` (exits 1 on any
non-ok result) but none of the 7 PRs wire it into CI. Two reasons:

1. **Existing drift would break the merge.** mentorforge and
   contract-concierge surface real drifts on first run; flipping the
   gate before those are fixed means the PR fails CI on its own merge.
2. **Operator buy-in is per-claim.** Some baseline regression claims
   (signal-studio `demo_cluster_count`) are explicitly OK to drift if
   the seed changes intentionally. Forcing CI to fail on those creates
   busywork.

Recommended path: once a repo's drift is reconciled, add a CI step:

```yaml
# .github/workflows/verify-doc-claims.yml
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: python scripts/verify_doc_claims.py --fail-on-drift
```

No backend install needed — the verifier is stdlib-only.

---

## Cost ledger (Session 1120)

| Stage | LLM calls | Tokens (approx) | Cost |
|---|---|---|---|
| 9 CTO surveys (Option D) | 9 | ~75k | ~$0.07 |
| 11 initiative extracts (Option D) | 11 | ~50k | ~$0.07 |
| 6 verifier plans (Option D follow-up) | 6 | ~50k | ~$0.04 |
| **Total** | **26** | **~175k** | **~$0.18** |

Well under the ~$0.20 budget Chris set at scope time. Per-repo cost
for adding new fleet members is ~$0.005 (one `draft_repo_verifier_claims`
call) plus Claude Code time.

---

## Open follow-ups

- **Django queue:** character-os, ai-content-studio, norman-handyman-mvp.
  Port the framework as a Django mgmt command (`python manage.py
  verify_doc_claims`) instead of standalone script.
- **Next.js queue:** 24-7-ai-global. Needs a Node verifier with the
  same shape; could live as a `scripts/verify_doc_claims.mjs`.
- **context-kit queue:** trivial — just seed 3 claims into the existing
  `context-kit verify --json` framework.
- **Reconcile mentorforge & contract-concierge drifts** so their
  verifiers can be flipped to `--fail-on-drift` in CI.
- **Promote the next batch of TRIAGE initiatives** — the fleet still
  has ~70 TRIAGE initiatives from the Option D sweep. Doc-verifier
  was one theme; ".env.example + secret scan" and "dev startup
  doc" appear in multiple repos too.

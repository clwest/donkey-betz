<!--
Default PR template. Most fields are optional — fill in what's
relevant for the kind of change you're shipping.

If this PR modifies any file in docs/narratives/, scroll to the
"Narrative-edit checklist" section below and fill it out
explicitly. Session 1159 demonstrated that single-pass narrative
editing can ship guardrails violations even in the PR that
introduces the guardrails — the checklist exists to prevent that.
-->

## Summary

<!-- 1–3 sentences on what changed and why. -->

## Test plan

<!-- Bulleted markdown checklist of how to verify the change.
For docs-only PRs, "Local mirrors clean" + "build_docs_index
regenerated" is usually enough. -->

## CI / bypass

<!-- If GH Actions billing is still down, document the bypass:
- [ ] Both local mirrors run clean (`verify_repo_guardrails.py --inventory-advisory`
      + `check_direct_llm_calls.py --warn-only`)
- [ ] Only failure is the pre-existing celery-beat CONFLICT
- [ ] Scope qualifies for the Session-1150 docs/verifier-baselines bypass protocol
      (production code changes need explicit Chris-authorization per Session 1159 PR #2255 precedent)
-->

---

## Narrative-edit checklist

<!--
Required ONLY if this PR modifies any file in docs/narratives/.
Delete this section if the PR doesn't touch narratives.

For each item, check ONLY the lines you changed, not the whole
file. Source: docs/narratives/EDITING_GUARDRAILS.md §"Pre-PR
checklist".
-->

- [ ] **Rule 1 (numbers):** every numeric value in changed lines has a code pointer or as-of label.
- [ ] **Rule 2 (model names):** no model name phrased as a permanent fact; provider-registry pointer present when literal is needed.
- [ ] **Rule 3 (lists):** enum/allowlist/prefix lists are illustrative-with-pointer, not duplicated-as-canonical.
- [ ] **Rule 4 (UI):** every "click X" / "open Y" instruction is paired with a tool/API/management-command equivalent.
- [ ] **Rule 5 (absolutes):** no "never" / "always" / "cannot happen" for runtime behavior; softened with remediation pointer.
- [ ] **Rule 6 (legacy):** legacy mentions name (1) what it is, (2) trigger, (3) how to tell from logs/data which path ran.
- [ ] **Rule 7 (counts):** inventory counts are date-anchored snapshots or replaced with capability descriptions.

If any item can't be ticked, restructure before merging. If all 7 are ticked but the diff still feels brittle, request Rigby's review before merge.

Full rules + rationale: [`docs/narratives/EDITING_GUARDRAILS.md`](../docs/narratives/EDITING_GUARDRAILS.md).

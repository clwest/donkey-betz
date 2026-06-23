<!--
Default PR template. Most fields are optional — fill in what's
relevant for the kind of change you're shipping.

Two conditional checklists are below — fill out whichever applies:

1. If this PR modifies any file in docs/narratives/, scroll to the
   "Narrative-edit checklist" section. Session 1159 demonstrated
   that single-pass narrative editing can ship guardrails violations
   even in the PR that introduces the guardrails — the checklist
   exists to prevent that.

2. If this PR modifies any of the 4 CRITICAL_PATH_HUB files
   (core/agent_router.py, core/services/openai_client_factory.py,
   core/celery.py, core/services/tool_dispatcher.py), scroll to
   the "Critical-path hub change checklist" section. Session 1217
   audit #4 identified these as load-bearing files whose refactor
   mistakes can break the whole platform; the checklist exists
   to force explicit Chris-review + rollback-lever naming.

Delete whichever section doesn't apply.
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

## Critical-path hub change checklist

<!--
Required ONLY if this PR modifies any of the 4 CRITICAL_PATH_HUB files:
- core/agent_router.py
- core/services/openai_client_factory.py
- core/celery.py
- core/services/tool_dispatcher.py

Delete this section if the PR doesn't touch any of those files.

Source: docs/CRITICAL_PATH_HUBS.md (Session 1223 audit #4 close).
-->

- [ ] **What changed:** named the specific function / method / config block touched (not just "added X" — name where it lives).
- [ ] **Chris-review requested:** explicitly pinged Chris before merging (or PR is from Chris). Hub changes do not auto-merge.
- [ ] **Rollback lever named:** if this breaks prod, what's the smallest revert that restores prior behavior? (commit SHA / env flag / config row).
- [ ] **Post-merge verification:** what should be checked in the first hour after deploy? (specific log signature, beat task firing, tool call returning success, etc.)

If any item can't be filled out, the change isn't ready — restructure or split the PR before merging.

Full convention + lineage: [`docs/CRITICAL_PATH_HUBS.md`](../docs/CRITICAL_PATH_HUBS.md).

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

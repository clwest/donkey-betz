# Session 1223 — Audit #8 Seed Baseline Drift Close

**Status:** First arc of Session 1223. Pinned-first item from `00-START-NEXT-SESSION.md` ("If you only do one thing next session: decide the audit #8 canonical-baseline question").
**Date:** 2026-06-23.
**Active conversation:** `pa-17e0fa71fd25470a` (fresh thread — prior `pa-58737666f25741dc` retired at 44 msgs / `strongly_recommend_fresh` after a 6-session run through Sessions 1217-1222).
**Prior session close:** [`SESSION_1222_V2_AUDIT_REVISIT_CLOSE.md`](./SESSION_1222_V2_AUDIT_REVISIT_CLOSE.md).
**Source audit deliverable:** `bec077ed-…` (Session 1217 self-directed, 15 findings).

## TL;DR

Session 1217's self-directed audit flagged finding #8 (seed baseline drift) as the only unresolved drift decision in the codebase. Pre-flight surfaced that the seed loader's own docstring lies: it claims "149 specialized agents" but `agents_data` actually contains **139 tuples** (Session 1149 audit comment in `doc_claim_verification.py:325` already confirmed this). The historical "155" baseline included 16 non-seed rows from other commands / migrations / runtime `DynamicPersonaAgent` inserts. Re-seeding today reaches 139 — not 155 — so Path A doesn't actually close the drift, it just relocates it.

Rigby and I both landed hard on **Path B** (accept 89 as canonical, single-PR close). Chris agree-all'd. Shipped Path B end-to-end in one PR.

## Session Manifest

### PRs merged

| # | Title |
|---|---|
| **#2534** | `fix(session-1223): close audit #8 — accept Agent.objects=89 as canonical seed baseline (Path B)` |

### Conversation lifecycle

- Session-open: orient + read 00-START-NEXT-SESSION.md
- Verified `service_context: local` via `platform_config_tool overview`
- Verified chris-ownership via `opportunity_manager_tool.stats scope=mine` (47 owned, $138k potential ✅)
- Retired `pa-58737666f25741dc` (44 msgs / 22k tokens / `strongly_recommend_fresh`)
- Created `pa-17e0fa71fd25470a` via `session_tool.create_fresh` titled "Session 1223 — Watchdog burn-in + audit tail (P1-P4)"
- Updated `tools/pa_local.sh` to pin new conversation + add retirement note for old one

## Finding-by-finding close

### #8 (PR #2534) — Seed baseline drift, Path B

**The drift:** `core/services/doc_claim_verification.py` had `persona_agent_count.expected = 155` (Session 1149 re-peg) and `total_agent_count_claim.expected = 238` (= AGENT_MAP(83) + 155). Runtime `Agent.objects.count() = 89` — drift of 66 below baseline, holding for ~80 sessions with zero downstream breakage.

**The decision card** (per `feedback_triage_decision_card_pattern.md`):

| Path | What | Claude lean | Rigby lean |
|---|---|---|---|
| A | Re-run `load_all_agents_advisors` → ~139 (not 155). Still needs baseline updates because docs say 155. | ✗ | ✗ |
| B | Accept 89 as canonical: 1-PR fix. | ✓ strong | ✓ strong |
| C | Kill numeric agent counts entirely → invariant checks. | defer | mentioned as cleaner long-term, NOT this audit close |

**Why B beats A** (Rigby's framing — operational truth wins):
- ~80 sessions with 87-89 and no downstream breakage attributable to "missing" persona rows
- Re-seeding reaches 139, not 155 → A doesn't actually resolve the contradiction, it relocates it
- Seed content is decorative — catalog of persona names/prompts, not LLM-backed implementations; calling them "Specialized Agents" at the same level as real agents is what created the false invariant
- Re-seeding would introduce 50+ stub-persona rows (Income Builder Pro, Warren Buffett, etc.) with no real LLM behind them — pure decorative scaffolding

### PR #2534 scope shipped

**`core/management/commands/load_all_agents_advisors.py`:**
- Module docstring rewritten — reframed as "decorative fallback scaffolding for `DynamicPersonaAgent`," not LLM-backed implementations; explicit Session 1223 audit close note
- `Command.help` corrected — "Seed 139 stub persona prompts + 25 stub advisor prompts (DynamicPersonaAgent fallback scaffolding — not load-bearing)"
- `load_all_agents` method docstring corrected — "Seed 139 stub persona prompts"
- `load_legendary_advisors` method docstring corrected — "Seed 25 stub advisor persona prompts (decorative scaffolding)"
- `stdout.write` "149 Specialized Agents" → "139 stub persona prompts (DynamicPersonaAgent fallback)"
- Final success message corrected — "Stub persona scaffolding loaded (139 agents + 25 advisors). Runtime dispatch lives in AGENT_MAP."

**`core/services/doc_claim_verification.py`:**
- `_persona_agent_count`: `expected = 155 → 89`. Docstring rewritten with explicit "not load-bearing" framing, Session 1223 audit close note, updated `note` + `fix_suggestion` to discourage re-seeding as the default fix.
- `_total_agent_count_claim`: `expected = 238 → 172` (= AGENT_MAP(83) + Agent rows(89)). Docstring updated with Session 1223 re-peg note + load-bearing clarification. `fix_suggestion` updated to point at the persona docstring.

**`tests/unit/core_agents/test_agent_router.py`:**
- New `TestSeedPersonaInvariance` class with 2 tests:
  - `test_agent_map_is_the_dispatch_contract` — AGENT_MAP non-empty (the load-bearing surface)
  - `test_persona_table_count_does_not_gate_dispatch` — AGENT_MAP entries resolve from code, not DB; documents that future re-pegs of `persona_agent_count` are not platform regressions
- Note: 3 pre-existing test failures in `TestAgentRouterIntegration` (BookmakerAgent doesn't inherit BaseAgent / lacks name / lacks system_prompt) verified to exist on `main` pre-PR; unrelated.

**`tools/pa_local.sh`:**
- Pinned conversation: `pa-58737666f25741dc → pa-17e0fa71fd25470a`
- Updated session description block to Session 1223 priorities (P1-P4 from start-here)
- Retired `pa-58737666f25741dc` to the prior-pins list with its full 6-session run context

**`00-START-NEXT-SESSION.md`:**
- Added "SESSION 1223 — IN PROGRESS" subsection noting audit #8 closed early-session
- Audit closure summary: closed 11 → 12 of 15; still-open 4 → 3 (#4, #9, #10)
- Priority 3 section reframed from "Chris picks A vs B" to "CLOSED Session 1223 (Path B)" with shipped scope
- Active conversation reference updated to `pa-17e0fa71fd25470a` with retirement note

## Verification post-merge

```bash
.venv/bin/python manage.py verify_doc_claims --only-drift
# → "No matching claims to run."   (i.e., zero drift across all docs)
```

Spot-check on the two re-pegged claims:
```
✓ [      ok] persona_agent_count
✓ [      ok] total_agent_count_claim
```

Repo-wide doc verifier ran clean across all 30+ doc files. The Session 1222 P7 reconciliation push (PR #2532) plus this Session 1223 close means the codebase now has **zero documented drift on agent counts** for the first time since the audit framework was added.

## Audit deliverable update

Source: `bec077ed-…` (Session 1217 self-directed audit, 15 findings).

- **Closed (12):** items 1A + 1B + 2 + 3 + A1 + C1 + #3 + B2 + #6 + #7 + bonus dispatcher-trim drift + **#8 (Session 1223, Path B)**
- **Still open (3):** #4 (critical hub markers), #9 (orientation doc staleness), #10 (Atlas positioning)

All three remaining items are M-effort docs-track work, not drift decisions. The codebase is drift-clean.

## Watchdog observation window (carryover from P1)

Session 1223 priority menu also included verifying the Tier 1 + Tier 2 watchdog fixes (PR #2519 + #2520) after 24-48h burn-in. Not done this arc — out of scope for the audit #8 close. Recommended next arc.

## Lessons / pattern notes

1. **Pre-flight reveals when "either path" is actually "one path."** Path A looked equivalent on paper (both close drift). Pre-flight (reading the loader, finding the 139 vs 155 vs 89 three-way mismatch) showed A would still require a multi-step fix because the docs claim 155 but re-seeding produces 139. Path B was always the cleaner option; pre-flight made it obvious.

2. **Triage decision card pattern works for "Chris-pick" priorities.** Per `feedback_triage_decision_card_pattern.md`, presenting a tight card (proposed action + Claude lean + Rigby lean + agree-all override) reduced this from a multi-message exchange to a single "agree all" response.

3. **Operational truth as audit-close criterion.** Rigby's framing — "we've run ~80 sessions with 87-89 and no downstream breakage attributable to 'missing' persona rows" — is the right yardstick when an "expected" baseline never had a real consumer. Path A would have canonicalized a number nothing actually needs.

4. **Loader docstring lies have long tails.** The "149 Specialized Agents" string was historical aspiration carried through Sessions 1100 → 1115 → 1149 → 1223. Each session's audit added more reconciliation logic without fixing the source lie. This PR fixes the source.

5. **Fresh conversation early-session matters.** The pre-existing thread had `score=25 / strongly_recommend_fresh` from Day 1 of Session 1223. Spinning the fresh thread before doing real work avoids the context-bleed pattern that bit Sessions 1097-1098.

## Next session entry point

See updated `00-START-NEXT-SESSION.md`. Remaining Session 1223 priorities:

- **P1** Watchdog observation window (5 burn-in checks from PR #2519/#2520)
- **P2** Operator Edge newsletter Friday-1 dry-run check (PR #2530)
- **P4** Audit #4 / #9 / #10 (M-effort docs-track work)

No fresh urgent items.

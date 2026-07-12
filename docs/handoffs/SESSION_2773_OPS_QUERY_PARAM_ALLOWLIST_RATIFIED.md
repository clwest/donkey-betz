---
session: 2773
date: 2026-07-12
title: "Ops-endpoint query-param allowlist + helper refactor + date-validation fix ratified"
status: complete
outcome: shipped
scope: net-new-engineering-N18v2
canonical_authority: repo_canonical
ratification_envelope: docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md
---

# Session 2773 — Ops-endpoint query-param allowlist + refactor ratified

## §1. TL;DR

Chris selected N18 from the S2773 candidate menu → Rigby's zoom-out (per S2771 rule, third consecutive application) raised 5 substantive substrate concerns → Chris D-verdict same-turn expanded N18 to N18v2 (Option B): fold Rigby's #1 (proxy DRY refactor), #2 (allowlist to all endpoints, not just close_ceremony_ledger), and #4 (date-parse correctness fix) into the same PR. Structural #3 (URLConf lambda tech debt) and #5 (health_summary overlap) → forward-carry with explicit triggers.

Shipped in 4 clean commits on a single branch (per Rigby Q4 recommendation): helper extraction → allowlist enforcement across all 6 endpoints → date-parse fix → 22 new tests. Combined test suite (N18v2 + S2772 auth-regression) 37/37 PASS in 0.9s.

**Eighth close-cycle post-PLAYBOOK-7.4.4-codification.** Second consecutive test-shipping session (S2772 auth-regression → S2773 param-contract). The S2771 workflow rule is validated for the third time in a row.

## §2. Timeline

| Time (approx) | Event | Reference |
|---|---|---|
| S2773 open | freshness check via retired S2772 pin: FRESH · SHA `e1e9514ac958` | this session |
| N18 selected | Chris: "N18 approved, route joint SIGN through Rigby" | this session |
| Pin minted | `pa-c15a7532e20b4fee` scoped to `s2773-ccl-query-param-allowlist` | `session_lifecycle open` |
| Design SIGN + zoom-out | Rigby: Q1 MODIFY (code field), Q2 MODIFY (new file), Q3 5 substantive concerns | pin above |
| Scope expansion D-verdict | Chris: "B approved" — fold #1 + #2 + #4 same PR | this session |
| Implementation SIGN | Rigby: Q1/Q2 PASS with nudges, Q3 MODIFY on date behavior claim, Q4 multi-commit recommended | pin above |
| Commit 1 | `_call_ops_tool` extraction (helper). Auth regression suite still green. | git log |
| Commit 2 | Allowlist enforcement across all 6 endpoints. Auth regression still green. | git log |
| Commit 3 | `_parse_date_param` calendar validation via `fromisoformat`. | git log |
| Commit 4 | New test file `test_ops_query_param_allowlist_2773.py` — 22 tests. | git log |
| Combined test run | 37/37 PASS in 0.907s | manage.py test |
| Envelope + handoff | this doc + envelope | filesystem |
| Docs cascade + provenance | 4-step + provenance rebuild | (post-merge below) |
| PR merge | filled at merge | GitHub |
| `make recycle-all` | eighth cycle post-codification | Makefile |

## §3. What shipped

**Files touched (all in one PR, 4 commits on branch):**

- `core/views_ops_console.py` — new `_call_ops_tool` helper (Rigby Q3 #1); 6 `_OPS_ALLOWED_PARAMS__<NAME>` frozenset constants (Rigby Q2 nudge on naming); new `_reject_unknown_query_params` helper (Rigby Q3 #2, Q1 MODIFY body shape); all 6 endpoints call the reject helper; 4 endpoints call the ops-tool helper; module policy docstring §3 refresh; `_parse_date_param` calendar validation via `fromisoformat` (Rigby Q3 #4).
- `core/tests/test_ops_query_param_allowlist_2773.py` (new) — 4 TestCase classes, 22 tests. Rigby Q2 MODIFY: separate charter from S2772 auth-regression file.
- `docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md` — new envelope.
- `docs/handoffs/SESSION_2773_OPS_QUERY_PARAM_ALLOWLIST_RATIFIED.md` — this file.

Net: backend +134 lines / −55 lines; tests +243 lines. Zero frontend edits.

**Endpoint allowlists:**

| Endpoint | Allowed params |
|---|---|
| `slo_status` | (none) |
| `failure_signatures` | `{window, limit}` |
| `blocked_agents` | (none) |
| `health_summary` | (none) |
| `close_ceremony_ledger` | `{limit, session_min, session_max, envelope_only, date_from, date_to, text}` |
| `recent_recycles` | `{limit}` |

**400 response body:**

```json
{
  "error": "Unknown query parameter(s)",
  "code": "unknown_query_params",
  "unknown": ["raw", "include_body"],
  "allowed": ["limit", "session_max", "session_min", ...]
}
```

Machine-stable `code` (Rigby Q1 MODIFY) — downstream tools key off `code == 'unknown_query_params'` not the English string.

**`_parse_date_param` behavior change (correctness fix):**

Invalid calendar strings like `2026-99-99` or `2026-02-30` previously slipped through the digit-only check and downstream `parsed_date < date_from` string comparisons operated on garbage. Now `fromisoformat` rejects them → filter dropped correctly. Rigby caught my "no visible behavior change" framing as wrong (implementation SIGN Q3 MODIFY).

## §4. Rigby SIGN Summary

Joint SIGN via pin `pa-c15a7532e20b4fee`. Three round-trips.

**Freshness:** verdict FRESH · SHA `e1e9514ac958` matches HEAD (S2772 close). Seventh post-codification cycle held.

**Design SIGN + zoom-out:** Q1 MODIFY (code field), Q2 MODIFY (new file). Q3 open-ended zoom-out (S2771 rule, third application): 5 substantive concerns raised — proxy DRY, allowlist uniformity, URLConf lambda tech debt, date parse bug, health_summary conceptual overlap. 3 addressed same-PR, 2 forward-carry with explicit triggers.

**Chris D-verdict on scope expansion:** "B approved" — expand N18 → N18v2 to include #1 + #2 + #4 same PR.

**Implementation SIGN:** Q1 PASS on payload-dict helper signature; Q2 PASS on module-constant location; Q3 MODIFY on "no behavior change" claim → adopted as correctness fix framing; Q4 recommended multi-commit-on-branch + squash-merge → adopted.

## §5. Post-merge browser eyeball (Chris)

1. Hard-refresh `localhost:8000/workspace?tab=system&sub=ops`.
2. Every ops-console section should render normally — you're `is_staff=True`, allowlist enforcement is silent for well-formed requests.
3. If you want to see the new 400 in action:
   ```bash
   curl -s -b "sessionid=<your-sid>" 'http://localhost:8000/api/ops/slo-status/?raw=1' | jq .
   ```
   Should return `{error, code: "unknown_query_params", unknown: ["raw"], allowed: []}` with HTTP 400.
4. Filter row on CCL v2 unchanged — clean type in the date input still works (fromisoformat accepts standard `YYYY-MM-DD`).

## §6. Twin-Pointer Card

📁 **Repo `/docs/` + `/core/` — S2773 artifacts:**

- **Amended backend module:** `core/views_ops_console.py` (`_call_ops_tool` + 6 allowlist constants + `_reject_unknown_query_params` + `_parse_date_param` fix + policy docstring refresh)
- **New test file:** `core/tests/test_ops_query_param_allowlist_2773.py` (22 tests)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-12_ops_query_param_allowlist.md`
- **Handoff:** `docs/handoffs/SESSION_2773_OPS_QUERY_PARAM_ALLOWLIST_RATIFIED.md`
- **Predecessor envelopes:** S2769 (CCL v2 filters), S2771 (text search + meta-critique #4 origin), S2772 (auth-regression + first zoom-out validation)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2773
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** ops-console tab unchanged for staff; 400 on unknown params for anyone probing.

## §7. Current Repository State

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2773 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| RUR-C1 state | S2755→S2772 diagnostic infra + operator surfaces + governance CLOSED · **S2773 ops query-param allowlist + refactor CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-c15a7532e20b4fee` (retired at S2773 close, force=true) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-c15a7532e20b4fee` (retired; forces fresh mint at S2774 open) |
| Live infra state | S2755→S2772 diagnostic infra + Playbook v0.6.0 + CCL v2 hover/drawer/filter/search + N7 recycle emitter + N11 PARTIAL_RECYCLE tile + N16 auth-regression suite + staff gate + **N18v2 allowlist + refactor + date fix** operational |
| Next move | Chris selects at S2774 open |

## §8. What This Session Taught About Doing Sessions

- **Multi-commit-on-branch + squash-merge is the right shape for close-ceremony PRs with legitimate scope expansion.** Rigby's Q4 recommendation was exactly right — reviewers can navigate the 4 commits per-diff (helper / allowlist / date fix / tests), while mainline history stays clean via squash. PLAYBOOK-7.4.1's "one PR per arc close" is about PR granularity, not commit granularity.
- **The S2771 zoom-out rule keeps producing high-signal critique on repeat application.** S2772 → 7 concerns, S2773 → 5 concerns. Neither Rigby nor I are gaming it — the rule works because it explicitly steps outside the current scope, and there's always accreted substrate worth naming. Continue.
- **Scope-expansion escalations to Chris should be a single tight ask, not open-ended.** My "A vs B" framing gave Chris a binary — he answered "B approved" in one line. If I'd routed 5 separate D-verdict asks (one per Rigby concern), we'd have burned five turns. Bundle the escalation.
- **`_parse_date_param` bug had lived from S2769 through S2772.** Four sessions of ops-console iteration didn't catch it because the surface tests never fed invalid calendar dates. Rigby caught it by reading the code, not by running tests. This is why zoom-out asks matter — code review from outside the immediate scope catches drift the incremental tests never trigger.
- **Eighth cycle under PLAYBOOK-7.4.4 continues to hold.** The chain of N7-enriched entries S2768→S2773 is now 6 long. The N11 PARTIAL_RECYCLE branch remains dormant — the substrate keeps demonstrating that clean recycles are the norm.

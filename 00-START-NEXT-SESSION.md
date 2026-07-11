# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2766 CLOSED — ENGINEERING PLAYBOOK v0.6.0 MINOR RATIFIED

**Refreshed 2026-07-11 (SESSION 2766 CLOSED — Playbook v0.6.0 MINOR ratified same day as v0.5.0; PLAYBOOK-7.4.4 codifies recycle-after-merge under existing §7.4 Close-ceremony delivery discipline. Rule count 201 → 202. First amendment where the version-bump class was corrected via SIGN before draft — Chris pre-labeled PATCH; joint Claude+Rigby SIGN caught the PLAYBOOK-10.4.1 constitutional constraint and reclassified to MINOR.).**

**S2766 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **`docs/ENGINEERING_PLAYBOOK.md`** — frontmatter version 0.5.0 → 0.6.0; parent_version 0.4.1 → 0.5.0; compatible_with appends "0.5.0"; rule_count 201 → 202; new `rules_added_v0_6_0: [PLAYBOOK-7.4.4]`; new v0_6_0 authoring/ratification session fields (both 2766); prior_ratification block updated with v0.5.0 metadata; Ch 7 metadata `Last substantive change: v0.6.0`; §7.4 preamble now "codifies four rules" + adds S2758–S2765 corroboration provenance; new PLAYBOOK-7.4.4 rule text inserted after 7.4.3; Appendix D v0.6.0 row appended.
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md`
- **Handoff:** `docs/handoffs/SESSION_2766_PLAYBOOK_V0_6_0_RATIFIED.md`
- **CLAUDE.md L7 anchor:** refreshed to reference v0.6.0 as latest; v0.5.0 preserved in ancestry chain
- **Docs cascade:** 4-step complete (index → corpus → sync → embed) + provenance rebuild
- **Post-merge:** `make recycle-all` invoked (dogfoods PLAYBOOK-7.4.4 — the rule the amendment ratifies)

---

## THE PIVOT — WHY THIS SHIP MATTERS

Recycle-after-merge was operator memory (`feedback_recycle_after_merge.md`) as of S2761 close. Between S2762 and S2765, three consecutive close-cycles corroborated the fix. S2766 promotes the rule from volatile MEMORY.md entry to **constitutional force** under PLAYBOOK-7.4.4.

**Second-order precedent set at v0.6.0:** the SIGN cycle caught a constitutional mismatch (Chris pre-labeled the amendment as PATCH v0.5.1 in START-NEXT; PLAYBOOK-10.4.1 forbids rule introduction as PATCH) before any code landed. Joint Claude+Rigby recommendation reclassified to MINOR v0.6.0. Chris ratified with "yes ship it as MINOR v0.6.0." **The Playbook's own rules override operator pre-labeling of amendment class.**

**Live ledger:** three observability layers now govern stale-process triage (Ops Health tile + Staleness Warnings + Recent Recycles from S2765) + one constitutional rule requiring the recycle timing (PLAYBOOK-7.4.4). The rule is machine-observable via `logs/recycle_events.jsonl` even though the rule text is prose.

---

## S2767 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended first per `feedback_engineering_bias_over_audit`)

- **N4** — Close-Ceremony Ledger v2: hover-preview + docs viewer navigation
- **N6** — Command Center home tile mirror of Ops Health (3-card grid at Workspace Home)
- **N7** — extend `recycle-all` emitter with worker PIDs before/after; use this to detect partial recycles

### Housekeeping

- **Candidate 1** — S2761 smoke test `/api/ops/health-summary/` (~20m)
- **Candidate 2** — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision (needs Rigby joint SIGN)
- **Candidate 3** — S2758 D4 HIGH-RISK task file wiring extension (REPORT-ONLY PR)

### Still owed

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check
- **PA celery worker bounce** — Rigby stall fix #3119 still not activated
- **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1
- **S2758 D1 process_pa_chat_task payload strip** — deferred
- **S2758 D5 local shim retirement** — depends on D2 canonical decision
- **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation

---

## SESSION PIN — S2766 RETIRED (fresh mint required at S2767 open)

**Pin history (S2766):**

- `pa-3811268cfce14a49` (label `s2766-playbook-v0-5-1-recycle-after-merge` — label predates MINOR reclass, retained; the constitutional force lives in the Playbook doc not the pin label) minted S2766 open; **retired at S2766 close**

**Wrapper `tools/pa_local.sh:539` still points at `pa-3811268cfce14a49` (retired)** — intended failure mode forces S2767 first-action fresh mint.

**S2767 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read the S2766 envelope §4 (corroboration ladder) + §5 (Rigby SIGN)
# Skim the new PLAYBOOK-7.4.4 rule text in docs/ENGINEERING_PLAYBOOK.md §7.4

# Freshness check + tile eyeball. Should be FRESH · SHA match at S2766 close SHA — this is the FOURTH close-cycle since the recycle-after-merge convention adopted (first cycle AFTER codification).
bash tools/pa_local.sh "S2767 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2766 close + S2765 close as top two entries)"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops — six sections still there

# Mint fresh pin scoped to selected S2767 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2766 close)

Same as S2766 close open items, with N5 removed (shipped) and one addition:

1. **S2761 smoke test** — Candidate 1
2. **S2758 D2 canonical decision** — Candidate 2
3. **S2758 D4 HIGH-RISK wiring extension** — Candidate 3
4. **P0.5 cost-threshold advance-to-freeze**
5. **P0.75 CI billing**
6. **PA celery worker bounce**
7. **RUR-C2 open eligible**
8. **S2758 D1 process_pa_chat_task payload strip**
9. **S2758 D5 local shim retirement**
10. **HMAC signing of `x-acting-user-id`**
11. **N4 / N6 / N7 net-new engineering** — see Candidates above
12. **NEW (post-S2766) — memory rule promotion audit** — now that recycle-after-merge is constitutional (PLAYBOOK-7.4.4), sweep MEMORY.md for other operator memories that have hit the two-triggers threshold and could be candidates for future MINOR amendments. Not urgent; future arc-close closeout item.

---

## Twin-pointer card

📁 **Repo `/docs/` + `CLAUDE.md` — S2766 artifacts:**

- **Playbook body:** `docs/ENGINEERING_PLAYBOOK.md` (v0.6.0)
- **New rule:** PLAYBOOK-7.4.4 in §7.4 Close-ceremony delivery discipline
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md`
- **Handoff:** `docs/handoffs/SESSION_2766_PLAYBOOK_V0_6_0_RATIFIED.md`
- **L7 anchor:** `CLAUDE.md` line 7 (refreshed to v0.6.0)
- **Prior version anchor:** `docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md` (v0.5.0 envelope)

🖥️ **Workspace UI — `/workspaces` surface:**

- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance mirror of v0.6.0 envelope + v0.6.0 body doc (twin-canonical representation per S2754a rule)
- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — sibling arc governance
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Ops Console (6 sections, unchanged from S2765)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2766 merge) |
| Playbook version | **v0.6.0 (RATIFIED S2766)** |
| Playbook rule count | **202** (201 → 202 at v0.6.0; +1 [GR]: PLAYBOOK-7.4.4) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2765 diagnostic infra + operator surfaces CLOSED · **S2766 Playbook v0.6.0 CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-3811268cfce14a49` (retired at S2766 close) |
| Wrapper default pin | `tools/pa_local.sh:539` — `pa-3811268cfce14a49` (retired; forces fresh mint at S2767 open) |
| Live infra state | Playbook v0.6.0 doc + envelope + handoff + L7 anchor + docs cascade complete; `make recycle-all` invoked at close as dogfood test of PLAYBOOK-7.4.4 |
| Next move | Chris selects at S2767 open — see Candidates above (N4/N6/N7 lean ⭐) |

---

## Recommended session-open protocol (S2767)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2766 envelope `RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md` §4 (corroboration ladder) + §5 (Rigby SIGN watchpoints)
4. Skim PLAYBOOK-7.4.4 rule text in `docs/ENGINEERING_PLAYBOOK.md` §7.4
5. **Freshness + findings + tile eyeball (single-round-trip)** — see S2767 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → **rule violation of PLAYBOOK-7.4.4 the very session after codification; escalate to Chris**
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. Present candidate menu to Chris (highlight N4/N6/N7 net-new leans)
9. Chris directs S2767 P0 selection
10. Mint fresh pin with candidate-scoped label
11. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2767:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor refreshed to v0.6.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — **v0.6.0 (latest ratified)**
3. [`docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md`](docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md) — S2766 envelope (this session)
4. [`docs/handoffs/SESSION_2766_PLAYBOOK_V0_6_0_RATIFIED.md`](docs/handoffs/SESSION_2766_PLAYBOOK_V0_6_0_RATIFIED.md) — S2766 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md`](docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md) — prior-version envelope (context for the same-day pair)
6. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md) — S2765 (empirical basis for PLAYBOOK-7.4.4 via §4.1 corroboration table)
7. `core/services/td_handlers_ops.py` — PA tool handler bank (Ops Console backend)
8. `core/views_ops_console.py` — Ops Console REST endpoints (6 views)
9. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Ops Console page (6 sections)

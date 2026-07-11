# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2763 CLOSED — CLOSE-CEREMONY LEDGER RATIFIED

**Refreshed 2026-07-11 (SESSION 2763 CLOSED — net-new operator surface for fast session-open context re-load. Ninth consecutive phase-close in two days. Second corroboration of the recycle-after-merge rule.).**

**S2763 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Backend** (`core/views_ops_console.py`): new `close_ceremony_ledger` view returning last N handoffs paired with ratification envelopes. Reads `docs/handoffs/SESSION_*.md` + `docs/research/implementation/RATIFICATION_*.md` from fixed roots with resolve-then-relative-to path validation (Rigby SIGN concern addressed pre-code).
- **URL** (`core/urls.py:2396`): `/api/ops/close-ceremony-ledger/` route registered.
- **Frontend** (`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`): new "Recent Close-Ceremonies (last N)" section below Blocked Agents with copy-to-clipboard cards for handoff + envelope paths.
- Ratification envelope: `RATIFICATION_2026-07-11_close_ceremony_ledger.md`
- Docs cascade: 4-step complete (index → corpus → sync → embed) + provenance rebuild
- Handoff: `SESSION_2763_CLOSE_CEREMONY_LEDGER_RATIFIED.md`

---

## THE PIVOT — WHY THIS SHIP MATTERS

Chris explicitly picked **N3** from the S2762 candidate menu: net-new engineering per S2745 engineering-bias directive. Ships a browser-visible operator surface for "what shipped recently?" that had previously required terminal + editor round-trips.

**Combined-round-trip discovery:** S2763 batched freshness check + design SIGN into a single Rigby prompt. Rigby returned the freshness verdict (FRESH · SHA matches HEAD — corroborating the recycle-after-merge rule) alongside the design SIGN (PASS with a legit path-traversal risk called out). Hardening was applied BEFORE the view body was written — cheaper than retrofit.

---

## S2764 CANDIDATES (Chris selects at open)

### Candidate 1 — S2761 smoke test (~20 min)

Smoke test `/api/ops/health-summary/` — assert 200 + all top-level keys present.

### Candidate 2 — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision

Design SIGN required. Three approaches (a/b/c) need Chris directive.

### Candidate 3 — S2758 D4 HIGH-RISK task file wiring extension

REPORT-ONLY-shape PR for `tasks_initiatives.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`.

### Candidate 4 — Net-new engineering

Per S2745 engineering-bias directive. Standing proposals + new:

- **N1** — Ops Health tile v2: add SLO summary panel (now that the SLO query works)
- **N2** — New PA tool `ops_tool.recent_recycles` — surface last N `make recycle-all` events + auth-refresh events
- **N4** *(new S2763)* — Close-Ceremony Ledger v2: render title/date/one-liner previews when a card is hovered/clicked; navigate to a `/docs/*` viewer route
- **N5** *(new S2763)* — Playbook amendment proposal for the recycle-after-merge rule (after one more independent corroboration this rule ships to §7.4.1)

### Housekeeping (still owed)

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check

---

## SESSION PIN — S2763 RETIRED (fresh mint required at S2764 open)

**Pin history (S2763):**

- `pa-2e382508b79d478b` (label `s2763-close-ceremony-ledger`) minted S2763 open; **retired at S2763 close**

**Wrapper `tools/pa_local.sh:539` still points at `pa-2e382508b79d478b` (retired)** — intended failure mode forces S2764 first-action fresh mint.

**S2764 open sequence:**

```
context-kit orient

# Read this file end-to-end

# Freshness check + tile eyeball (single Rigby + browser round-trip). Watch for FRESH — that's the THIRD corroboration point for the recycle-after-merge rule.
bash tools/pa_local.sh "S2764 open — three quick tool invocations: (1) ops_tool.version report staleness_verdict + head_commit_sha (2) ops_tool.tenant_boundary_violations window=24h limit=5 (3) ops_tool.staleness_warnings window=24h limit=5"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops — FIVE sections should render: Health tile + SLO grid + Signatures + Blocked + Recent Close-Ceremonies (should include S2763 at top)

# If verdict != FRESH → run make recycle-all before continuing (would be the negative result for the recycle-after-merge rule; escalate to Chris before codifying).

# Mint fresh pin scoped to selected S2764 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2763 close)

1. **S2761 smoke test** — Candidate 1 above
2. **S2758 D2 canonical decision** — Candidate 2 above
3. **S2758 D4 HIGH-RISK wiring extension** — Candidate 3 above
4. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
5. **P0.75 CI billing** — status check
6. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
7. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1
8. **S2758 D1 process_pa_chat_task payload strip** — deferred (HTTP-side bootstrap refactor)
9. **S2758 D5 local shim retirement** — depends on D2 canonical decision
10. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation
11. **`recycle-all AFTER merge` rule codification watch** — S2762 and S2763 corroborated; **one more independent arc-close → propose Playbook amendment to §7.4.1**

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2763 artifacts:**

- **Backend view:** `core/views_ops_console.py` (`close_ceremony_ledger` + `_safe_relpath` + `_index_envelopes_by_session`)
- **URL:** `core/urls.py:2396`
- **Frontend section:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` (Recent Close-Ceremonies)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md`
- **Handoff:** `docs/handoffs/SESSION_2763_CLOSE_CEREMONY_LEDGER_RATIFIED.md`
- **Precedent envelopes:** S2761 tile (composition pattern), S2762 sibling fix (api.get pattern)
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2763
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Ops Health tile + SLO / Signatures / Blocked cards + Recent Close-Ceremonies list

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2763 close-ceremony ledger merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2762 diagnostic infra + tile + sibling fix CLOSED · **S2763 close-ceremony ledger CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-2e382508b79d478b` (retired at S2763 close) |
| Wrapper default pin | `tools/pa_local.sh:539` — `pa-2e382508b79d478b` (retired; forces fresh mint at S2764 open) |
| Live infra state | S2755→S2762 diagnostic infra + tile + sibling cards + ledger operational; process freshness FRESH at close |
| Next move | Chris selects at S2764 open — see Candidates above |

---

## Recommended session-open protocol (S2764)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2763 envelope `RATIFICATION_2026-07-11_close_ceremony_ledger.md` §2 (ratified deliverables) + §3 (security hardening)
4. **Freshness + findings + tile eyeball (single-round-trip)** — see S2764 open sequence in §SESSION PIN above
5. If `staleness_verdict != FRESH` → `make recycle-all` before continuing (escalate to Chris — would be a negative signal for the recycle-after-merge rule)
6. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
7. Present candidate menu to Chris
8. Chris directs S2764 P0 selection
9. Mint fresh pin with candidate-scoped label
10. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2764:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md`](docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md) — S2763 envelope (this session)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md) — S2762
4. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md) — S2761
5. `core/views_ops_console.py` — Ops Console REST endpoints (5 views now)
6. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Ops Console page (5 sections now)
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0

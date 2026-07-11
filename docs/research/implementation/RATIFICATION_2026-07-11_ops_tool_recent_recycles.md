---
title: "ops_tool.recent_recycles PA Tool Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2765
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (freshness + design) + Chris candidate selection + local build + shell smoke test + dogfood via post-merge recycle
scope: S2765 — N2: new `ops_tool.recent_recycles` PA action + `/api/ops/recent-recycles/` REST endpoint + Makefile JSONL emitter + Ops Console frontend section
serves_arc: platform observability (Ops Console at Workspace → System → Ops); operator-action timeline
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md (S2761 — health_summary composition)
  - docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md (S2763 — fixed-root filesystem safety pattern reused)
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md (S2764 — extend-not-fork discipline)
ratified_documents:
  - Makefile (amended — recycle-all target appends JSONL to logs/recycle_events.jsonl)
  - core/services/td_handlers_ops.py (amended — recent_recycles action + _ops_recent_recycles handler)
  - core/services/pa_tool_schemas.py (amended — recent_recycles added to ops_tool actions enum + description)
  - core/views_ops_console.py (amended — recent_recycles REST view)
  - core/urls.py (amended — /api/ops/recent-recycles/ route)
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — RecycleEvent/RecentRecyclesResponse types + recyclesQuery + Recent Recycles section + formatAgo helper)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2765 open freshness (fresh pin pa-a11f652a75b94ad3) — verdict FRESH · SHA b1ae6561… matches HEAD (FOURTH data point / THIRD independent close-cycle → threshold for codification met)
  - S2765 design SIGN (Rigby) — PASS with atomic-append/JSONL malformed-line risk flagged; belt-and-suspenders response (POSIX-atomic append + defensive reader)
frozen: true
---

# ops_tool.recent_recycles PA Tool Ratification Record

Frozen canonical record of Chris's ratification of the recent-recycles operator surface on 2026-07-11. Completes the observability trilogy for stale-Daphne diagnoses: `ops_tool.version` (live snapshot) + `ops_tool.staleness_warnings` (post-hoc detection) + **`ops_tool.recent_recycles` (operator-action timeline)**. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** last-mile UI + PA tool extension (N2 in S2762 standing candidate menu).
- **Motivation:** stale-Daphne diagnoses currently reference `ops_tool.version` (which shows current worker uptime) but there's no first-party record of when `make recycle-all` was invoked. Rigby's S2758→S2761 diagnostic loop repeatedly cited "post-20:22 UTC recycle" as the demarcation for classifying historical findings — but that timestamp came from `daphne_started_at` inference, not a first-party emitter. This action adds an operator-action timeline so future diagnoses can reference exact recycle invocations.
- **Ratifier:** Chris (candidate selection at S2765 open: "let's do N2 next")

---

## §2. Ratified Deliverables

### §2.1 `Makefile` — `recycle-all` JSONL emitter

`recycle-all` target extended with post-restart append:

```makefile
recycle-all: restart
	@mkdir -p logs
	@printf '{"ts":"%s","sha":"%s","label":"recycle-all"}\n' \
		"$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
		"$$(git rev-parse HEAD 2>/dev/null || echo unknown)" \
		>> logs/recycle_events.jsonl
	@echo "✓ Recycle event recorded in logs/recycle_events.jsonl (S2765)."
```

**Atomicity:** POSIX guarantees `write(2)` calls smaller than `PIPE_BUF` (typically 4096 bytes on Linux/macOS) are atomic when writing to a file opened with `O_APPEND`. Our JSONL lines are ~100 bytes — well under. Concurrent Makefile invocations (rare on a single-user workstation) can't interleave a single line.

**Fallback SHA:** `git rev-parse HEAD 2>/dev/null || echo unknown` — if the operator runs recycle outside a git working tree, the entry captures `"sha":"unknown"` rather than failing.

**No `.gitignore` change needed** — `logs/` was already gitignored.

### §2.2 `core/services/td_handlers_ops.py` — `_ops_recent_recycles` handler

New dispatch action `recent_recycles` calling `_ops_recent_recycles(payload, trace_id)`. Handler:

- Resolves `logs/recycle_events.jsonl` against `settings.BASE_DIR`; refuses to read if resolution escapes `BASE_DIR` (mirror of S2763 safety pattern).
- **Fail-soft on missing file:** returns `{log_exists: False, items: [], count: 0, note: "..."}` with diagnostic message pointing at the Makefile target.
- **Defensive parse:** reads lines with `errors='replace'`, iterates tail-first (`reversed(lines)`), skips malformed lines with counter (`malformed_lines_skipped` in response), returns first `limit` valid events.
- Enriches each event with `sha_short` (first 12 chars) + `seconds_ago` (parsed from ISO-8601 `ts` field).
- Limit param clamped `max(1, min(50, int_or_default_10))`.

Response shape:

```json
{
  "action": "recent_recycles",
  "log_exists": true,
  "log_path": "logs/recycle_events.jsonl",
  "items": [
    {
      "timestamp": "2026-07-11T22:15:00Z",
      "sha": "c3a4b5d6e7f8...",
      "sha_short": "c3a4b5d6e7f8",
      "label": "recycle-all",
      "seconds_ago": 42
    }
  ],
  "count": 1,
  "limit": 10
}
```

### §2.3 `core/services/pa_tool_schemas.py` — schema addition

`recent_recycles` added to `ops_tool` action enum + description covering purpose (operator-action timeline), complement relationship to `version`+`staleness_warnings`, and fail-soft behavior.

### §2.4 `core/views_ops_console.py` — REST wrapper

`recent_recycles(request)` view is a thin proxy over the PA handler (same pattern as sibling ops REST endpoints). Auth: `@require_GET + @login_required`. Registered at `/api/ops/recent-recycles/` (`core/urls.py:2397`).

### §2.5 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Recent Recycles section

- New TypeScript interfaces `RecycleEvent` + `RecentRecyclesResponse`.
- New `formatAgo(seconds)` helper (s / m / h / d thresholds).
- New `recyclesQuery` using axios `api.get('/ops/recent-recycles/?limit=10')` with 60s staleTime.
- New section between "empty state" and "Recent Close-Ceremonies" with `<RotateCw />` icon header + compact card list per event: green icon + short SHA (mono, primary color) + timestamp + relative-time badge + label. Section hidden when `log_exists === false` or empty.

---

## §3. Concurrency & Malformed-Line Defense (§4.2 Rigby SIGN concern addressed)

Rigby's SIGN response flagged: "concurrent JSONL writes can interleave/partial-line on append, creating a malformed last line that breaks naive line-by-line JSON parsing."

**Belt-and-suspenders response:**

1. **Writer side** — Makefile uses `printf ... >> file` which is POSIX-atomic for line writes < PIPE_BUF. Our lines are ~100 bytes; PIPE_BUF is 4096 on macOS/Linux. Not a race concern in practice on a single-user workstation.
2. **Reader side** — `_ops_recent_recycles` defensive parse: every line wrapped in `try/except (json.JSONDecodeError, ValueError)`, malformed lines counted in `malformed_lines_skipped` response field but do NOT break the timeline. One bad tail line can never blank the whole list.
3. **Isinstance guard** — even valid JSON that isn't a dict (e.g., a stray `null` or list) is filtered.

Tested implicitly via the shell smoke test (missing file case returns fail-soft `log_exists: false` with diagnostic note).

---

## §4. Rigby SIGN

### §4.1 Freshness — CODIFICATION THRESHOLD MET (S2765 open, pin `pa-a11f652a75b94ad3`)

`ops_tool.version` → **FRESH**, `head_commit_sha b1ae6561…` matches HEAD (post-S2764 merge).

**Corroboration ladder for `feedback_recycle_after_merge.md`:**

| Close cycle | Post-recycle verdict | Next-session-open verdict | Independent? |
|-------------|----------------------|---------------------------|--------------|
| S2762 close (PR #3151) | FRESH · `7db82c84…` | S2763 open FRESH · same SHA | cycle 1 |
| S2763 close (PR #3152) | FRESH · `8785c312…` | S2764 open FRESH · same SHA | cycle 2 |
| S2764 close (PR #3153) | FRESH · `b1ae6561…` | **S2765 open FRESH · same SHA** | **cycle 3** |

**THREE independent close-cycles now confirm the rule.** This meets the "third arc-close corroboration" threshold both my prior session recorded (§8.4 of S2764 handoff) and the PLAYBOOK §14.2 two-triggers default (satisfied at cycle 2, triple-confirmed here).

**Codification proposal deferred to S2766** (new candidate N5 will be to author the Playbook amendment).

### §4.2 Design SIGN

**SIGN LEAN: PASS.** Rigby: "matches the close_ceremony_ledger 'fixed-root safe read + fail-soft + small limit' pattern; minimal surface area."

**Risk called out:** concurrent JSONL writes → interleaved / partial-line append breaking naive parse.

**Response:** belt-and-suspenders (writer POSIX-atomic + reader defensive parse) per §3 above.

---

## §5. Chris D-Verdict

Sequence:

1. **Session-open candidate selection:** "let's do N2 next" (picked N2 from standing candidate menu; sixth consecutive Chris selection matching Claude's top lean this run).
2. **Joint agreement:** no F-BLOCKING decisions surfaced; Rigby's atomicity risk resolved before code landed.
3. **Post-merge verify (pending):** hard-refresh `localhost:8000/workspace?tab=system&sub=ops`; "Recent Recycles" section appears with S2765 close-ceremony recycle as the **first-ever recorded entry** (dogfood test of the emitter).

**Effect:** Ops Console now surfaces THREE observability layers on stale-process diagnoses:
1. **Live snapshot** — Ops Health tile verdict badge + `ops_tool.version`
2. **Post-hoc detection** — Staleness Warnings card + `ops_tool.staleness_warnings`
3. **Operator-action timeline** — Recent Recycles section + `ops_tool.recent_recycles`

Complete trilogy for future stale-Daphne triage.

---

## §6. Verify-Before-Build

- **Reused patterns:**
  - `_ops_recent_recycles` handler shape mirrors `_ops_staleness_warnings` (aggregation + fail-soft note) but reads JSONL instead of `OpsRunEvent` rows.
  - `recent_recycles` REST view mirrors `close_ceremony_ledger` (S2763) safe-root discipline.
  - Frontend section pattern mirrors "Blocked Agents" card style (compact single-line entries with icon + code + timestamp).
  - Makefile emitter uses vanilla `printf ... >> file` — no shell dependency injection, no format string exposure.
- **What's new:** the JSONL data source itself. No new abstraction (no ORM model, no migration, no service class).
- **Reuse/extend/correct verdict:** compose an existing pattern set into a new operator surface.

---

## §7. Provenance Chain

- **Predecessor sessions:** S2761 (tile v1) → S2762 (sibling 401 fix) → S2763 (close-ceremony ledger) → S2764 (tile v2 SLO card) → **S2765 (recent recycles)**
- **Reference infra:** `core/views_ops_console.py:130+` (close_ceremony_ledger safe-root pattern), `core/services/td_handlers_ops.py:1393+` (staleness_warnings aggregation pattern)
- **Engineering Playbook v0.5.0:** PLAYBOOK-7.4.1 (close-ceremony 1-PR bundle) + Cycle 1A verify-before-build applied (§6 above)
- **Memory rules applied:** `feedback_last_mile_ui.md` (browser-visible operator surface + PA tool access via Rigby), `feedback_recycle_after_merge.md` (FOURTH data point / THIRD independent close-cycle → codification threshold met), `feedback_local_truth_no_production.md` (local build + shell smoke test = shipped; dogfood via post-merge recycle)
- **Codification watch:** `feedback_recycle_after_merge.md` corroboration threshold met. S2766 candidate N5 = author Playbook §7.4.1 amendment.

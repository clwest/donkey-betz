---
title: "Recycle-all Emitter Worker-PIDs Enrichment Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2768
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (design + post-smoke verify) + Chris candidate selection (N7) + Chris D-verdict on final plan + local smoke test
scope: S2768 — N7: extend the `recycle-all` Makefile target to snapshot local worker PIDs BEFORE the bounce and AFTER, then append the diff to `logs/recycle_events.jsonl` as `pids_before / pids_after / partial_recycle / surviving_processes`. Reader handler passes new fields through when present; old rows still parse.
serves_arc: PLAYBOOK-7.4.4 machine-observability (constitutional recycle-after-merge rule); operator visibility on partial-recycle failures
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md (S2765 — original JSONL emitter + read handler)
  - docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md (S2766 — codified PLAYBOOK-7.4.4)
  - docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md (S2767 — second post-codification cycle)
ratified_documents:
  - scripts/emit_recycle_event.py (new — stdlib-only helper, snapshot + emit subcommands)
  - Makefile (amended — `recycle-all` becomes sequential: snapshot → $(MAKE) restart → emit; falls back to legacy printf if script missing)
  - core/services/td_handlers_ops.py (amended — `_ops_recent_recycles` surfaces new PID/partial fields when present)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2768 open freshness (retired-pin dispatch to Rigby) — verdict FRESH · SHA caa98579a matches HEAD (SECOND corroboration cycle after PLAYBOOK-7.4.4 codified; recycle log had 3 entries S2767/S2766/S2765)
  - S2768 design SIGN (Rigby, pin pa-3cb29f52e461401a) — Q1 MODIFY (prefer Python script over shell for robustness/testability); Q2 PASS (any survivor = partial); Q3 PASS (JSONL-only this session, defer UI)
  - S2768 post-smoke verify SIGN (Rigby) — PASS on all three checks (new fields present on new row; partial_recycle=false + surviving_processes=[] correct; backward-compat on pre-N7 row)
frozen: true
---

# Recycle-all Emitter Worker-PIDs Enrichment — Ratification Record

Frozen canonical record of Chris's ratification of the S2768 N7 emitter enrichment on 2026-07-11. Adds machine-observable per-role PID diff to every `recycle-all` invocation so partial recycles — where PLAYBOOK-7.4.4 was formally invoked but one or more worker processes silently survived — become detectable from the same JSONL log that the constitutional rule's enforcement layer already reads. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** operator observability extension of the S2765 JSONL emitter (N7 in S2767 candidate menu; deferred one session for the S2767 UI ship).
- **Motivation:** PLAYBOOK-7.4.4 (ratified S2766, v0.6.0) requires a post-merge recycle so all local workers match HEAD SHA. `ops_tool.version` can detect stale processes per-role live, but the recycle log itself lacked per-role evidence: an operator could `make recycle-all`, one worker could silently fail to restart, the JSONL row would still record "recycle-all happened" — and the next session's freshness check would show a stale worker without a clean explanation. N7 makes partial recycles first-class in the log the constitutional rule already uses as evidence.
- **Ratifier:** Chris (candidate selection at S2768 open: "Lets go with N7"; D-verdict on the final plan: "Approved")
- **Second cycle after PLAYBOOK-7.4.4 codification:** S2768 open verified FRESH · SHA-match at `caa98579a` (S2767 close); recycle log at S2768 open had 3 entries (S2767/S2766/S2765) — the rule continues to hold.

---

## §2. Ratified Deliverables

### §2.1 `scripts/emit_recycle_event.py` — stdlib-only PID-snapshot helper

Two subcommands:

- `python scripts/emit_recycle_event.py snapshot` → prints `{role: pid_or_null}` JSON of the 7 known pidfiles to stdout. Called BEFORE `make restart` runs so the Makefile can pipe the result to a temp file.
- `python scripts/emit_recycle_event.py emit --before <path>` → reads the before-snapshot, snapshots AFTER, computes `partial_recycle` (any role whose before-PID equals its after-PID) + `surviving_processes` (list of role names), appends the enriched JSONL row to `logs/recycle_events.jsonl`.

Role map (canonical 7):

| Role | Pidfile |
|---|---|
| `daphne` | `.daphne.pid` |
| `celery_default` | `.celery.pid` |
| `celery_pa` | `.celery-pa.pid` |
| `celery_long_running` | `.celery-long-running.pid` |
| `celery_broadcast` | `.celery-broadcast.pid` |
| `celery_code_jobs` | `.celery-code-jobs.pid` |
| `celery_beat` | `.celery-beat.pid` |

Partial-recycle semantics (per Q2 PASS): a role is "surviving" iff its before-PID is non-null AND equals its after-PID. If either side is null (pidfile absent at that moment — e.g., beat writes its pidfile milliseconds after workers), the role is NOT flagged. This keeps the signal specific to "process claimed restarted but kept the same PID."

Defensive newline: emit checks whether the log file ends with `\n`; if not, it prepends one before writing. This defends against a prior writer crashing mid-line (or, as observed in this session, an operator's shell metachar leaking into an append). Companion to the reader's existing malformed-line skipping.

No Django dependency — reads pidfiles as plain files. Keeps the recycle path fast.

### §2.2 `Makefile` — `recycle-all` target sequentialized

Before (S2765 shape):

```makefile
recycle-all: restart
    @mkdir -p logs
    @printf '{"ts":"%s","sha":"%s","label":"recycle-all"}\n' ... >> logs/recycle_events.jsonl
    @echo "✓ Recycle event recorded ..."
```

After (S2768 N7):

```makefile
recycle-all:
    @mkdir -p logs
    @python scripts/emit_recycle_event.py snapshot > /tmp/recycle_pids_before.json 2>/dev/null || echo '{}' > /tmp/recycle_pids_before.json
    @$(MAKE) restart
    @python scripts/emit_recycle_event.py emit --before /tmp/recycle_pids_before.json 2>/dev/null || \
        printf '{"ts":"%s","sha":"%s","label":"recycle-all"}\n' ... >> logs/recycle_events.jsonl
    @rm -f /tmp/recycle_pids_before.json
    @echo "✓ Recycle event recorded ... (S2768 N7 enriched)."
```

The `restart` prerequisite drops; the recipe now orders snapshot → restart → emit. If the Python script is missing (e.g., checkout without `scripts/`), the target falls back to the legacy printf shape — keeping `recycle-all` operable in every clone state.

### §2.3 `core/services/td_handlers_ops.py::_ops_recent_recycles` — pass-through of new fields

Adds a small loop that copies `pids_before / pids_after / partial_recycle / surviving_processes` from the parsed JSONL event into the returned per-item dict when the keys are present. Legacy events (pre-N7) lack these keys and pass through unchanged via `.get()` semantics.

### §2.4 New JSONL row shape

```json
{
  "ts": "2026-07-11T23:38:32Z",
  "sha": "caa98579a2ae1811c8fa95e8a24d1571343b8769",
  "label": "recycle-all",
  "pids_before": {"daphne": 94684, "celery_default": 94733, ...},
  "pids_after": {"daphne": 5376, "celery_default": 5440, ..., "celery_beat": null},
  "partial_recycle": false,
  "surviving_processes": []
}
```

`celery_beat: null` in the smoke row is an expected edge — beat starts as a background daemon and may write its pidfile a few hundred ms after the workers. `null` is the semantically-correct value: we don't know beat's after-PID. The detection layer intentionally does NOT flag `null` as surviving (which would be a false-positive), leaving the resulting `partial_recycle: false` correct for a clean recycle where beat is momentarily unmeasurable.

---

## §3. What Was NOT Changed

- No new URL, no new REST endpoint, no new PA tool action. `ops_tool.recent_recycles` continues to be the single read path.
- No frontend edit. The Ops Console tab renders whatever fields the handler returns; the new fields just become available to future UI extensions (deferred per Q3 PASS).
- No breaking change to `_ops_recent_recycles` return shape — new fields are optional, absent for legacy events.
- No change to the PLAYBOOK-7.4.4 mechanical waiver list. Waivers still bypass the recycle entirely; N7 only enriches the log when the recycle DOES run.

---

## §4. Rigby SIGN Summary

Joint SIGN routed via pin `pa-3cb29f52e461401a` (label `s2768-recycle-emitter-worker-pids`).

### §4.1 Q1 — Snapshot location (Makefile shell vs helper)
- **Rigby verdict:** MODIFY.
- **Content:** Rejected inline Makefile shell; requested Python helper (script or mgmt command) for robustness + testability. Ship: standalone Python script (no Django startup cost, no ORM needed, stdlib-only). Adopted.

### §4.2 Q2 — Partial-recycle semantics
- **Rigby verdict:** PASS.
- **Content:** "any surviving PID = partial" is correct for `recycle-all`. Waivers bypass the whole check; they do not redefine the invariant. No modification.

### §4.3 Q3 — Surface exposure this session
- **Rigby verdict:** PASS.
- **Content:** Ship the JSONL emitter + handler pass-through; defer UI badges + `health_summary` extension until real-world entries accumulate. Adopted.

### §4.4 Post-smoke verify SIGN
- **Rigby verdict:** PASS.
- **Content:** After a real `make recycle-all` under the new emitter, Rigby's `ops_tool.recent_recycles limit=2` returned: newest row has all 4 new fields with `partial_recycle:false / surviving_processes:[]`; second-newest (S2767 pre-N7) parses cleanly and lacks the new fields (backward-compat verified end-to-end).

---

## §5. Empirical smoke tests

### §5.1 Unit round-trip (script only)
- Command: `python scripts/emit_recycle_event.py snapshot > /tmp/x.json; python scripts/emit_recycle_event.py emit --before /tmp/x.json --label smoke-test`
- Result: script correctly identified the "no restart happened" case as `partial_recycle: true` with all 7 roles surviving (invariant check works).

### §5.2 Real `make recycle-all`
- Command: `make recycle-all`
- Result: full Daphne + Celery restart; script recorded `partial_recycle: false / surviving_processes: []` with pids_before (7 roles) and pids_after (6 roles + celery_beat=null). Console printed `[emit_recycle_event] clean recycle recorded (sha=caa98579a2ae, surviving=none)`.

### §5.3 Read-side verify via Rigby
- Command: `ops_tool.recent_recycles limit=2`
- Result: newest event returns all 4 new fields; second-newest (S2767 pre-N7 shape) returns legacy fields only. Backward-compat verified.

### §5.4 Log-file hygiene incident
Mid-session I noticed one malformed row in the JSONL log with `{"ts":..,"sha":..,"label":"recycle-all"}` — the `..` literal came from shell metacharacter escapes in an earlier Rigby SIGN prompt string leaking through zsh's `>>` redirection. The reader's defensive `json.loads` correctly skipped it as malformed. I cleaned the row and added a defensive newline-prepend to `emit` so a future truncated line can't glue itself to the next legitimate row. Fine to ship; the reader would have coped either way.

---

## §6. Post-ratification bindings

- **Head at ratification:** filled at merge.
- **Merged PR:** filled at merge.
- **Workspace mirrors (S2754a twin-canonical rule):**
  - Governance envelope mirror → `RUR-C1 Tenant Boundary Lockdown` workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (deliverable_type `ratification_record`, category `governance`).
  - Content mirror → same workspace (deliverable_type `initiative_phase_doc`, category `implementation`).
- **PLAYBOOK-7.4.4 dogfood:** `make recycle-all` invoked post-merge — third consecutive cycle where the constitutional rule fires; first cycle to emit an N7-enriched entry into the log the rule uses as evidence.

---

## §7. Forward carry

- **Partial-recycle badge in Ops Console (deferred N).** Once the log accumulates a partial-recycle event in the wild (bad shutdown, macOS OS-level SIGKILL, kernel panic), extend the Recent Recycles render block in `OpsConsoleTab.tsx` with a 🟡 badge on `partial_recycle=true` rows, plus a hover-tooltip listing `surviving_processes`. Two-trigger threshold — needs one observed partial before promoting to a UI change.
- **`ops_tool.health_summary` cross-reference (deferred N).** If `partial_recycle=true` on the most-recent row AND `ops_tool.version` reports a `started_before_head_commit: true` process, surface that as a distinct verdict (currently maps to `STALE_CELERY` / `STALE_DAPHNE`). One-trigger away from a health-tile red bar meaning "PLAYBOOK-7.4.4 partial-recycle detected."
- **Beat pidfile timing.** `celery_beat: null` on the after-snapshot is expected in this recipe order. If it becomes a nuisance (operator confusion), a small `sleep 0.2` between `$(MAKE) restart` and the emit call would smooth it — but it adds latency to every close. Do NOT ship that unprompted; wait for Chris to say "the beat null is bothering me."

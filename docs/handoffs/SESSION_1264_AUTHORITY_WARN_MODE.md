---
session: 1264
status: closed
date: 2026-06-30
arc: MissionRunner authority warn-mode — emit one authority_contract_observed event per mission right after run_started so contract shape becomes queryable across missions; honest scope correction to S1260 plan (the keys are policy descriptions, not runtime symbols, so violation detection is out of scope without future symbol-mapping work)
prs_merged: [2756]
prs_open: []
companions:
  - docs/handoffs/SESSION_1263_CLAUDE_CODE_AGENT_ROW_CONSOLIDATION.md
deliverables: []
---

# Session 1264 — MissionRunner Authority Warn-Mode

## TL;DR

PR #2756 implements the smallest honest authority observability: one
`authority_contract_observed` info event per mission emitted right
after `run_started`. The event captures contract **shape** (counts +
version hash) — not violation detection. The S1260 P4 plan implied a
preflight hook would detect violations; independent verification this
session showed the `JobContract.authority` keys are policy descriptions
(`"modify_docs_files"`, `"open_pull_request"`) not runtime symbols.
There is no registry mapping these strings to tool names / function
calls / model methods. Violation detection requires future symbol-
mapping work that is intentionally out of scope. 3 production
employees opt in via factory kwarg; Employees #4–#20 inherit warn-mode
automatically. Discovery → Phase 1 SIGN-WITH-EDITS → implementation →
13 new tests + 317 regression tests → Phase 4 SIGN → admin-merge, all
in one session.

## What shipped — PR #2756 (admin-merged 2026-06-30, merge SHA `0fa1b577`)

| File | Net | Purpose |
|---|---|---|
| `core/employees/mission_runner.py` | +93 | Constants + exception + hash helper + new `MissionRunnerConfig.job_contract` field + `_emit_authority_contract_event` method + call site after `run_started` |
| `core/jobs/docs_cascade.py` | +5 | `job_contract=DOCUMENTATION_MANAGER` in factory |
| `core/jobs/platform_audit.py` | +2 | `job_contract=PLATFORM_AUDIT_JOB` |
| `core/jobs/morning_brief.py` | +2 | `job_contract=MORNING_BRIEF_JOB` |
| `core/tests/test_mission_runner_authority_warn_mode_s1264.py` | +383 | 13 contract tests |
| 4 existing lifecycle-sequence tests | +1 line each | Include `authority_contract_observed` in expected event sequence |

Total: 9 files, +583 / -3.

### Discovery correction to S1260 plan

**S1260 P4 implied violation detection was achievable. It isn't, without symbol mapping.**

| Authority key | Today's reality | What violation detection needs |
|---|---|---|
| `authority["modify_docs_files"] = "prohibited"` | A string-keyed policy entry | A mapping from `"modify_docs_files"` to actual code paths (file writes, subprocess calls, ORM operations) |
| `prohibited_actions[0] = "Edit any file under docs/..."` | A prose sentence | Same — prose isn't a runtime predicate |

**Steps don't declare what action_classes they invoke. Tools don't have action_class metadata. There's no registry.** Even a perfect preflight hook reading `JobContract.authority` would have nothing to compare against.

The honest smallest thing is to observe the **contract itself** — every mission emits one event recording authority entry counts by level, prohibited_actions count, contract title, and a 16-char SHA-256 prefix of the contract for cross-mission grouping. Real evidence accumulates across N missions. Future enforce-mode can build on this baseline once symbol-mapping ships.

### Event payload (Rigby SIGN edit #4 — explicit metadata contract)

```python
label = "authority_contract_observed"
event_type = "info"
detail = {
    "schema_version": 1,                       # bumps on shape change
    "employee_handle": "rigby" | "platform_auditor" | "chief_of_staff",
    "contract_title": "Documentation Manager" | "Platform Audit" | "Daily Morning Brief",
    "contract_version_tag": "<16-char sha256 prefix>",
    "authority_entries_total": 11 | 15 | 25,
    "authority_level_counts": {
        "execute": N, "observe": N, "recommend": N, "prohibited": N
    },
    "authority_unknown_level_count": 0,        # rises if a future contract uses a value not in AuthorityLevel
    "prohibited_actions_count": 4 | 7 | 10,
    "mode": "warn",                            # explicit so future enforce-mode rows can use "enforce"
    "note": "Observation of contract shape only; not violation detection. ..."
}
```

Live tags on the 3 production contracts (smoke-verified during implementation):

| Employee | auth_entries | prohibited | contract_version_tag |
|---|---|---|---|
| Documentation Manager | 11 | 4 | `f841537c67a1b18d` |
| Platform Audit | 15 | 7 | `c3c303053ef0bb95` |
| Daily Morning Brief | 25 | 10 | `6b5dcdbba9cba693` |

### Rigby Phase 1 SIGN-WITH-EDITS — all 5 edits + 2 don'ts applied

| # | Edit | How applied |
|---|---|---|
| 1 | Typed `Optional[JobContract]` not `Any` | Direct import — verified `core/employees/jobs.py` has zero imports from mission_runner.py, no circular |
| 2 | Counts + identifiers only, no full contract serialization | Detail payload carries shape fields; contract object never serialized |
| 3 | Stable label; version churn in metadata | `AUTHORITY_CONTRACT_OBSERVED_LABEL` constant; `schema_version=1` lives in `detail.schema_version` |
| 4 | Explicit metadata contract | Documented in payload spec above; locked in by §1 contract tests |
| 5 | Hard-fail only on malformed shape | `_AuthorityContractMalformedError` raised on dict/tuple violations; mission still completes; `summary.degraded_evidence=True` + `summary.authority_contract_error` persisted |
| Don't | No enforcement logic | Zero blocks, zero verdict coupling |
| Don't | No new registry / mapping layer | Out of scope — explicitly deferred to enforce-mode |

## What's preserved unchanged

- **MissionRunner public API** — `__init__` signature, `run()`, all existing hooks
- **JobContract dataclass** — zero new fields
- **Mission lifecycle order** — `run_started` → `authority_contract_observed` (new) → `preflight_fn` → step loop → `postflight_fn` → verdict → escalation. Nothing else moves.
- **3 production employees' behavior** — verdict, escalation, shift-report all unchanged
- **prohibited_actions tuple semantics** — read only at warn-mode emission time, not enforced
- **`claude_code_tool`, Employee OS, tool dispatcher, agent_router, Celery topology** — all untouched

## Memory observations worth keeping

- **The verifier-loop pattern caught the S1260 P4 over-promise.** S1260 audit said "JobContract.authority has zero readers — add a preflight hook." Independent verification at S1264 open showed the deeper issue: the keys are policy descriptions, not symbols. A preflight hook would read `authority["modify_docs_files"]` and have nothing to compare against. **Lesson reinforces S1261's wrong-fix observation**: every audit recommendation gets verified against runtime before implementation.
- **"Observation of shape" is honest evidence; "observation of violations" requires symbol mapping.** Worth distinguishing in any future authority work. The new event payload's `note` field embeds this clarification directly so future readers don't conflate the two.
- **Existing primitives (OpsRunEvent) carry the entire warn-mode** without a new model, table, or persistence surface. The S1252 PR 2 evidence-trail design is reusable for telemetry purposes the original spec didn't anticipate.

## Future enforce-mode prerequisites (documented in discovery)

Switching WARN → ENFORCE requires ALL of:

| # | Prerequisite | Threshold |
|---|---|---|
| 1 | Symbol mapping exists | Steps declare `action_classes_invoked: tuple[str, ...]` OR tool-name → action_class registry lands |
| 2 | Clean warn-mode telemetry on N≥4 employees | ≥14 days of `authority_contract_observed` events across docs_manager + platform_audit + morning_brief + Employee #4, zero unexpected shape variance |
| 3 | False-positive rate quantified | ≤5% across actual mission outcomes after step self-attestation lands, observed ≥30 days |
| 4 | Per-employee trust_ratio remains healthy | ≥0.75 across all opt-in employees throughout warn-mode window |
| 5 | Manual operator review | ≥3 employees reviewed; contract-vs-reality match confirmed |

**None block this PR.** Warn-mode is shipped now; enforce-mode is a future arc.

## What's next (Session 1265 entry point)

Carry-forward from S1263 close minus the now-closed P1. Next priorities:

1. **Pre-existing SLO breaches** — `agent_timeout_rate` 12× over, `celery_task_success_rate` marginally under. Investigation.
2. **Read-only `/api/employees/` + `/api/missions/`** — S1260 P5 recommendation; ~250 LOC over existing model + `core/employees/status.py`.
3. **Hygiene PRs** — orphan `content.*` route in CELERY_TASK_ROUTES, CLAUDE.md autoblock + agent taxonomy drift refresh.
4. **Employee #4** — architecturally ready, awaiting Chris's call. Now inherits warn-mode telemetry automatically.
5. **Future S1263 follow-up** — shrink `_CLAUDE_CODE_AGENT_NAMES` to `('claude-code',)` after 1+ week.
6. **Future S1264 follow-up** — when symbol mapping is ready, wire enforce-mode hook reading `JobContract.prohibited_actions` against declared action_classes. Separate ARC.
7. **Carryover backlog** — `_persist_to_summary` dup, user resolution generalization, `sync_celery_beat` orphan trap code fix, PA tool surface gaps, etc.

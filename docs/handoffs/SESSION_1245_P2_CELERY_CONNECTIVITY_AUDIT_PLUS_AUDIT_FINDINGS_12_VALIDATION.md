# Session 1245 — P2 Celery connectivity audit + S1115 AUDIT_FINDINGS.md #12 framework re-validated

**Session window:** 2026-06-27 Saturday afternoon CDT/MDT (continuous from S1244 close).

**Theme:** Telemetry-based dead-task analysis (S1244 deferred-followup) → connectivity census → verify-before-delete cross-reference. Initial probe surfaced 14 "disconnected" Celery tasks; verify-before-delete sweep against `AUDIT_FINDINGS.md` #12 (S1115 multi-batch audit) showed 11 of 14 were already documented as deferred-by-policy, 1 was a probe false positive (direct Python caller blind spot), and only 2 were net-new (`content/` character-training subsystem dormancy). No deletes shipped. New management command `audit_celery_zero_fire` shipped to harden the probe for future sessions.

---

## TL;DR

- **1 PR shipped** — `core/management/commands/audit_celery_zero_fire.py` (runtime telemetry probe + KNOWN_DEFERRED filter).
- **Audit deliverable `24ade5c4-7562-4905-80a1-bb901d0549d7`** — 6,900 chars, status=ready, Donkey Betz workspace.
- **Beat schedule health: PERFECT (90/90 enabled PeriodicTask rows fired in available 14d window).** S1244 queue-parity canary is working.
- **Verify-before-delete prevented a wrong deletion PR** — Bucket II "wrapper orphan" plan would have deleted intentionally-deferred tasks.
- **S1115 audit framework re-validated** — 11 of 14 apparent-orphans were already enumerated in `AUDIT_FINDINGS.md` #12 deferred-pending-green-light list.
- **2 bonus telemetry findings** filed for S1246+ trace.
- **2 net-new findings** queued for owner triage (content/ character-training subsystem dormancy).
- **1 memory rule added** about cross-referencing #12 before any Celery deletion + zero-fire telemetry horizon caveats.

### Net stats

- **1 PR** — `audit_celery_zero_fire` management command (~210 lines)
- **1 deliverable** advanced (S1245 audit, ready status)
- **0 tasks deleted** (verify-before-delete intervened on initial 3-task plan)
- **1 memory rule** added: `feedback_audit_findings_12_canonical_celery_deferred_list.md`

---

## P2 arc — telemetry-based dead-task analysis

S1244 closed the Celery wiring audit by deferring "dead task analysis" to a telemetry-based approach (static analysis hit >50% false positives due to delegation wrappers). S1245 P2 ran the telemetry version.

### Initial census

```
TOTAL_REGISTERED: 430
TOTAL_SEEN_30D:   112
ZERO_FIRE_COUNT:  321
```

**Caveat surfaced immediately:** `CeleryTaskEvent` telemetry only goes back to 2026-06-13 — ~14 days. The 30d/90d/all-time windows all return identical results. A "never fired" claim from 14d of data is unsafe; edge-case tasks may fire monthly. (`CELERY_TASK_EVENT_RETENTION_DAYS = 30` is correctly set; just haven't accumulated yet.)

### Chris's pivot — "can they fire + are they connected" instead of "did they fire"

The S1244 start-here doc proposed: 30d telemetry filter → zero_fire = dead candidates. Telemetry horizon broke that premise. Chris redirected to a connectivity probe: instead of "did this task fire?", ask "can it fire and is it properly wired?"

### 4-axis connectivity probe (telemetry-horizon-independent)

For each registered task, checked 4 dispatch surfaces:
1. PeriodicTask beat row
2. `.delay()` / `.apply_async()` / `.s(` / `.signature(` method calls (per-task short-name grep)
3. String-literal reference (dotted full name in code)
4. Wrapper-to-`_impl_*` pattern (return delegation)

**Result on 321 zero-fire tasks:**
- multi_surface: 70 (well-wired)
- beat_only: 0 (every beat task also has direct dispatch surface)
- call_only: 29
- string_only: 208
- **DISCONNECTED: 14** (no axis hit)

### The 14 disconnected list — initial classification

🔴 Bucket I (9): claims-scheduled-but-no-beat-row (docstring claims scheduled, no PeriodicTask row)
🔴 Bucket II (3): wrapper-and-impl both orphan (no caller anywhere)
🟡 Bucket III (2): S1031 quarantine (explicit DISABLED comment)

### Verify-before-delete sweep — the audit's actual value

Chris green-lit Plan D: open deliverable for all 14 + ship Bucket II deletes. Before opening the deletion PR, ran the memory-rule-mandated verify-before-delete sweep on Bucket II:

- `post_ops_digest` → grep found 2 hits in `core/celery.py:501` + `:627` — **comment block enumerating tasks deferred per AUDIT_FINDINGS.md #12**
- `send_weekly_kpi_summary` → same comment block (LLM-cost deferred)
- `update_agent_effectiveness_from_learning` → **live direct-Python caller** in `core/management/commands/bootstrap_learning_system.py:383` (probe blind spot — only checked Celery dispatch forms, not direct function calls)

**Read `docs/AUDIT_FINDINGS.md` §12 + line 882-895.** Found that 11 of the 14 "disconnected" tasks were ALREADY explicitly enumerated as:
- **LLM-cost deferred** (deferred until OpenAI credits): `post_ops_digest`, `send_weekly_kpi_summary`, `run_ops_autopilot`
- **Agent-dispatch chain deferred** (deferred for green-light): `check_blocked_research_for_unblock`, `intelligence.tasks.process_pending_action_plans`
- **S1031 quarantine** (explicit DISABLED): `assign_open_findings_to_agents`, `discover_and_import_audits`
- **Should-be-scheduled but never wired** (§12 line 890-895 explicit example list): `post_coo_daily_diagnostic`, `post_cto_daily_diagnostic`, `post_trend_daily_diagnostic`, `update_experiment_kpis`

**The verify-before-delete rule worked exactly as designed** — caught a wrong deletion plan before any commit landed.

### Net-new findings (only 2 of 14)

- `content.tasks.check_single_training` — CharacterModel training, "hourly via Celery Beat" claim, no row
- `content.tasks.cleanup_stale_trainings` — sibling, "hourly", no row

Both are part of a **fully-dormant subsystem**:
- `CharacterModel.objects.count()` = 0
- `poll_pending_trainings` (sibling task) = 0 telemetry events ever
- Subsystem originated Session 175 (Replicate character training poller)

**Disposition:** NOT deleted. Per memory rule, retiring a whole app is an owner decision > audit scope. Filed for S1246 product-Q.

### Bonus findings

- **Telemetry repr bug:** 1 CeleryTaskEvent row has `task_name='<@task: core.tasks.cleanup_stale_agent_executions of unified_donkey_betz_core at 0x10b8d91d0>'` — some writer is doing `task_name=str(task_obj)` instead of `task_name=task.name`. Filed for S1246 trace.
- **Ghost task:** `core.tasks.check_system_health` has telemetry rows but task not in `current_app.tasks` registry. Renamed/deleted upstream with leftover writer. Filed for S1246 trace.

---

## PR shipped — `audit_celery_zero_fire` mgmt cmd

`core/management/commands/audit_celery_zero_fire.py` — runtime telemetry probe complementing `build_celery_audit.py` (static caller analysis).

**Features:**
- Imports 23 task modules (same list as `test_celery_queue_parity.py` setUp)
- Queries `CeleryTaskEvent` for last-N-days window (default 30)
- Cross-references KNOWN_DEFERRED set hardcoded from `AUDIT_FINDINGS.md` §12
- Reports effective window (warns when telemetry retention < requested window)
- Output: human-readable table + `--json` mode + `--include-deferred` flag

**Interpretation guard built into output:**
> "zero_fire" means "no CeleryTaskEvent row in window" — NOT "orphan". A task can be zero-fire because: (a) deferred-by-policy [see #12], (b) fired before retention window started, (c) only fires on rare external triggers, (d) genuinely orphan. To distinguish (c) vs (d), run `build_celery_audit` and check per-task callers.

**Smoke test results (current local state):**
```
window=30d (effective=14d, telemetry from 2026-06-13)
  registered                  : 431
  seen_in_window              : 112
  zero_fire                   : 322
  in AUDIT_FINDINGS #12 set   : 11
  uncategorized (need lookup) : 311
```

The 11 deferred-in-zero matches exactly the 11 of my 14 that turned out to be in #12. Filter is correct.

---

## Audit deliverable

**`24ade5c4-7562-4905-80a1-bb901d0549d7`** — "S1245 Celery connectivity audit — 14 disconnected tasks (Buckets I/II/III)"
- **Workspace:** Donkey Betz (`b4503364-2573-4401-9e28-61a739e0ce50`) — initially mis-assigned to `cf708a2e` (S1231 E2E sandbox), reassigned mid-session
- **Status:** ready (not completed — audit findings remain open for S1246+ disposition)
- **Content length:** 6,900 chars
- **Sections:** Headline + corrected classification + bonus findings + content/ dormancy follow-up + audit close summary

---

## Memory rule added

`feedback_audit_findings_12_canonical_celery_deferred_list.md`:

> Before declaring any Celery task orphan, cross-reference `docs/AUDIT_FINDINGS.md` §12 (S1115 multi-batch audit, 272→10 orphan reduction). Use `python manage.py audit_celery_zero_fire` for runtime probe — its KNOWN_DEFERRED set mirrors #12. Zero-fire telemetry claims bounded by `CELERY_TASK_EVENT_RETENTION_DAYS` (default 30) AND age of earliest CeleryTaskEvent row. Direct Python calls from mgmt commands are a known probe blind spot — `rg "\b<short>\s*\("` separately before deletion.

Indexed in MEMORY.md line after `feedback_verify_before_deleting_dead_code` (extends that rule with the Celery-specific cross-ref protocol).

---

## Audit-method evolution this session

- **S1115 framework re-validated** — the deferred-pending-green-light policy is real and being respected by post-S1115 sessions. 11 of 14 "orphan" findings were already enumerated → no actionable new orphans in the AUDIT_FINDINGS.md #12 catalog.
- **Probe blind spot identified + hardened** — direct Python function calls (e.g. mgmt commands importing + invoking task body) need a 5th axis. Added as TODO in `audit_celery_zero_fire` --help; future session can extend.
- **Telemetry retention horizon documented** — `audit_celery_zero_fire` surfaces effective_days and warns when requested window > actual telemetry depth.

---

## Carryover into Session 1246

**Chris-side:**
- Anthropic credit refill at https://console.anthropic.com/billing — still failing CI billing

**S1246 priority menu (Chris discretion):**
- **Content/ subsystem retirement Q** — should the dormant character-training app be retired? CharacterModel=0 rows, 3 tasks=0 events, sibling tasks also dormant. Product-Q before retirement PR.
- **Bonus telemetry findings trace:**
  - Telemetry repr bug — where is `str(task_obj)` being written instead of `task.name`?
  - Ghost task `core.tasks.check_system_health` — where is the writer? Was the task renamed?
- **Add 5th axis to `audit_celery_zero_fire`** — direct Python call detection via `rg "\b<short>\s*\("` minus def-sites + wrapper sites.
- **Re-run `audit_celery_zero_fire` once 30d telemetry accumulates** (~2026-07-13) — get the first telemetry-valid zero-fire census.
- **Pre-existing carryover tail** (unchanged from S1244):
  - Smoke-harness mode inconsistency (S1231 F5, LOW-MEDIUM)
  - Smoke-probe tagging for AgentExecution (S1231 F1 / R2 REC-2)
  - Promote `scripts/smoke_all_agents.py` → mgmt cmd (S1231 F6)
  - Audit `5318da3e-…` §R2 amendment (S1231 F3, P3)
  - Engineer workspace staleness (S1230 F3, MEDIUM)
  - Meeting-context leak shape watch (S1230 F2, LOW — `cf708a2e` workspace still active)
  - Fleet-smoke wall-clock timeouts (S1231 F2 / R2 REC-3, LOW)
  - 80 spiders audit (last S1205)
  - 30 advisors audit (last S1208)
  - 9 body systems audit
  - 144 Discord commands audit
  - 7 fleet sibling apps at localhost:8002-8008

**TIME-BOUND (S1246 morning, ~07:00 MDT 2026-06-28):**
- 06-28 morning_brief cumulative verification — validates cumulative PRs from S1242 + S1243 + S1244 + S1245 in the production morning_brief generation path. See start-here Priority 1 query block.

**Conversation state at S1245 close:**
- `pa-1cb4915546654c78` — was 100/continue, 7 turns + multiple exchanges during S1245. Re-check at S1246 open.
- Rigby drafted 1 deliverable + 1 reassignment + 1 addendum cleanly. No tool failures.
- Per "Claude directs, Rigby executes, Claude verifies" — this session was a clean execution of the pattern. Rigby's `claude_code_tool` dispatch attempt for the census itself was recursive (Claude IS Claude Code) so Claude ran that directly; everything else routed via PA tool surface as designed.

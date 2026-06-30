---
session: 1263
status: closed
date: 2026-06-30
arc: Duplicate Claude Code Agent row consolidation — close the [CLAUDE_CODE_AGENT_DUP] WARN that started firing on every dispatch after S1262 by re-pointing 12 historical FK refs from ClaudeCode → claude-code and fixing the synthesizer that re-created the row
prs_merged: [2754]
prs_open: []
companions:
  - docs/handoffs/SESSION_1262_CLAUDE_CODE_TASK_RECEIPT_RELIABILITY.md
deliverables: []
---

# Session 1263 — Duplicate Claude Code Agent Row Consolidation

## TL;DR

PR #2754 closes the duplicate-Agent-row hygiene gap that the S1262 canonical-name resolver surfaced. Migration `0374` re-points 12 historical FK references (7 AgentExecution + 1 AgentDream + 4 AgentMemory) from the duplicate `ClaudeCode` row to the canonical `claude-code` row, normalizes 7 `owner_agent` strings, and deletes the duplicate. Root-cause fix: `deliverable_factory._synthesize_pa_execution_receipt` now canonicalizes `agent_name` before `Agent.objects.get_or_create`, so the row can't respawn from `'ClaudeCode'` writes. Two mgmt commands updated belt-and-suspenders to write `'claude-code'` directly. Discovery → Rigby Phase 1 SIGN-WITH-EDITS → implementation → 7 new tests + 79 regression tests → live verification → Rigby Phase 4 SIGN → admin-merge → post-merge prod-verified, all in one session.

## What shipped — PR #2754 (admin-merged 2026-06-30, merge SHA `f1af8c54`)

| File | Net | Purpose |
|---|---|---|
| `core/migrations/0374_session_1263_consolidate_claude_code_agent.py` | +172 | Data migration: repoint FKs, normalize strings, defensive safety gate, delete dup |
| `core/services/deliverable_factory.py` | +6 / -1 | `_synthesize_pa_execution_receipt` canonicalizes before `get_or_create` |
| `core/management/commands/seed_agent_initiative_affinities.py` | +3 / -2 | `'ClaudeCode'` → `'claude-code'` |
| `core/management/commands/import_patent_disclosures.py` | +3 / -1 | Same |
| `core/tests/test_claude_code_agent_consolidation_s1263.py` | +265 | 7 contract tests |

Total: 5 files, +458 / -7.

### Root cause

Five sites contributed:
1. **`deliverable_factory.py:697`** — `Agent.objects.get_or_create(name=agent_name, ...)` bypassed `canonicalize_agent_name`. **Primary bug.**
2. **`seed_agent_initiative_affinities.py:77`** + **`import_patent_disclosures.py:189`** — wrote deliverables with `agent_name='ClaudeCode'` (the alias string). When those ran, the synthesizer spawned a fresh Agent row matching the alias.
3. **S1226 migration 0365** had normalized `Deliverable.agent_name` strings but never touched the `Agent` table — so even though the string was supposed to be canonicalized, the synthesizer was still creating new rows under the legacy spelling.
4. **The S1262 canonical-name resolver** (`_resolve_claude_code_agent`) handled this gracefully (always picked `claude-code` deterministically) but logged `[CLAUDE_CODE_AGENT_DUP]` WARN on every dispatch as long as both rows existed — surfacing the underlying problem.

### Repair (per Rigby Phase 1 SIGN-WITH-EDITS)

**Migration `0374` (data-only, RunPython, reverse=noop):**

1. Resolve canonical (`claude-code`) + duplicate (`ClaudeCode`) by name. Skip if duplicate missing (idempotent).
2. Re-point FK references:
   - `AgentExecution.agent` — **7 rows**
   - `AgentDream.agent` — **1 row**
   - `AgentMemory.agent` — **4 rows**
3. Normalize `AgentExecution.owner_agent='ClaudeCode' → 'claude-code'` on the 7 migrated rows so FK + string stay internally consistent.
4. **Defensive safety gate (Rigby SIGN-WITH-EDITS edit #1):** re-enumerate ALL reverse-FK relations on the `Agent` model via Django introspection (not just the 3 expected), assert each is 0, raise `RuntimeError` on any residual reference. Catches future-model surprises without orphaning history.
5. Delete the duplicate row.
6. **Defensive branch:** if only the duplicate exists (fresh DB before any `claude_code_engineer_task` dispatch), rename it in-place to the canonical name rather than dropping history.

**Code fix in `deliverable_factory.py:697`:**

```python
canonical_name = canonicalize_agent_name(agent_name)
agent_record, _created = Agent.objects.get_or_create(
    name=canonical_name,
    defaults={...},
)
```

**Belt-and-suspenders (Rigby SIGN-WITH-EDITS edit #2):** Two mgmt commands updated to write `'claude-code'` directly. Eliminates the source string from the repo.

## What's preserved unchanged

- MissionRunner, Employee OS, JobContract, `employee_tool`: zero edits
- `claude_code_tool` response shape: unchanged
- `_CLAUDE_CODE_AGENT_NAMES` fallback tuple in `claude_code_engineer.py:63` — **kept** per Rigby SIGN-WITH-EDITS edit #3 ("wait one cycle"). Future hygiene PR can shrink it once we've confirmed no re-creation.
- `deliverable_aliases.AGENT_NAME_ALIASES`: kept — still used by `deliverable_tool.normalize`.
- S1262 receipts pipeline: unchanged (resolver continues to find `claude-code` deterministically; just stops WARNing)

## Live verification

### Migration applied locally (real production rows)

```
[0374] canonical='claude-code' (id=341364bb-…); duplicate='ClaudeCode' (id=c2ff634d-…)
[0374] AgentExecution.agent: 7 rows repointed
[0374] AgentExecution.owner_agent string: 7 rows normalized
[0374] AgentDream.agent: 1 rows repointed
[0374] AgentMemory.agent: 4 rows repointed
[0374] deleted duplicate Agent row id=c2ff634d-…
```

Counts match discovery inventory exactly.

### Post-migration Rigby dispatch (`ddcf4e78`)

- Only 1 active `claude_code` Agent row: `claude-code`
- CeleryTaskEvent SUCCESS, dur 2.9s
- `AgentExecution.agent.name='claude-code'`, status=completed, summary `'S1263 CONSOLIDATION OK'`
- `AgentFollowupSubscription` state=**fired**, post-back landed
- 7 historical S1187 Recon rows still queryable under canonical with intact task titles
- Total `AgentExecution` under canonical = 17 (9 pre + 7 migrated + 1 new)
- Zero `[CLAUDE_CODE_AGENT_DUP]` WARN since worker restart

### Post-merge prod verification (`23b32bc8`)

- 1 active `claude_code` Agent row
- AgentExecution status=completed, summary `'S1263 POST-MERGE OK'`
- Subscription state=**fired** at 16:20:38Z
- Zero `[CLAUDE_CODE_AGENT_DUP]` in active log markers

## Tests

- **7/7 new S1263 contract tests pass:**
  - 3 canonicalization tests (alias routes to canonical; canonical passes through; unknown unchanged)
  - 4 migration behavior tests (FK repoint + owner_agent normalize + delete; idempotent skip; rename-in-place; **safety-gate raises on residual reference**)
- **79/79 broader regression sweep passes** (S1263 + S1262 receipts + engineer suites + S1226 string-canon tests)

## Memory observations worth keeping

- **The S1262 WARN was a feature, not a bug.** The `[CLAUDE_CODE_AGENT_DUP]` WARN that started firing after PR #2752 turned a silent latent problem (duplicate Agent rows since S1187 batch) into a visible one — exactly the design intent. S1263 closes the visible WARN by closing the underlying duplication. Lesson: defensive diagnostic markers pay off when the next session can actually act on them.
- **Migration safety gate via reverse-FK introspection.** The Rigby SIGN-WITH-EDITS edit #1 (enumerate ALL reverse-FK relations, not just the 3 expected, raise on residual refs) was the right call. The test that simulates an unaccounted FK by patching `QuerySet.update` proves the safety net works without requiring us to enumerate future models in the migration itself.
- **Synthesizers must canonicalize at write.** The S1226 migration 0365 normalized Deliverable.agent_name strings, but didn't touch the Agent table — so the synthesizer kept spawning new rows when callers passed aliases. The root-cause fix in `deliverable_factory.py` (canonicalize before `get_or_create`) prevents the next S1263 from happening. Pattern worth applying to any future synthesizer that materializes objects from caller-supplied names.

## What's next (Session 1264 entry point)

S1263 closed the duplicate Agent row hygiene gap. Carry-forward from S1262 close (Priority 0) is also satisfied — `[CLAUDE_CODE_AGENT_DUP]` is silent in current logs.

Next priorities (unchanged from S1262 close minus the now-closed Priority 1):

1. **Pre-existing SLO breaches** — `agent_timeout_rate` 12× over, `celery_task_success_rate` marginally under. Investigation.
2. **MissionRunner `authority_check_fn` preflight hook** (warn-mode) — S1260 P4 recommendation.
3. **Read-only `/api/employees/` + `/api/missions/`** — S1260 P5 recommendation.
4. **Hygiene PRs** — orphan `content.*` route in CELERY_TASK_ROUTES, CLAUDE.md autoblock + agent taxonomy drift refresh.
5. **Employee #4** — architecturally ready, awaiting Chris's call.
6. **Future S1263 follow-up:** shrink `_CLAUDE_CODE_AGENT_NAMES = ('claude-code', 'ClaudeCode')` → `('claude-code',)` after 1+ week of clean operation confirms no re-creation paths. ~3-line PR.

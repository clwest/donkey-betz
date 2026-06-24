# Session 1224 — Outreach Pipeline End-to-End + Cross-Cutting Token Budget Sweep

**Status:** Five-PR session — full vertical slice (backend + REST + UI + tests + browser-smoke) shipped end-to-end, hygiene initiative closed same-session, plus a cross-codebase bug sweep surfaced by live LLM probing.
**Date:** 2026-06-23.
**Active conversation:** `pa-17e0fa71fd25470a` — carried over from Session 1223 (no rotation; healthy across 2 sessions).
**Prior session:** [`SESSION_1223_AUDIT_SWEEP_AND_WATCHDOG_GREEN.md`](./SESSION_1223_AUDIT_SWEEP_AND_WATCHDOG_GREEN.md).
**Next session entry point:** Session 1225 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1225".

## TL;DR

Session opened expecting a quiet maintenance window (1223 cleared the audit, watchdog, and carryover queues). Rigby's session-open brief pivoted to **Option B — outreach drafts automation** (the gap between thousands of Opportunity rows and a silent `outreach_inbox`). Chris ratified, and we shipped the vertical slice end-to-end: backend generator → 5 REST endpoints → Workspace `tab=work&sub=outreach` UI → browser smoke → real LLM emails landing in the inbox.

Three follow-on PRs surfaced naturally:
1. **Hygiene gates** (deliverable factory) — Rigby spawned initiative `d8d6c0b2-…` mid-session after spotting `BINDING DIRECTIVE`-titled ResearchAgent deliverables. Closed same-session.
2. **Metadata field-name fan-out** — browser smoke returned `created: 0, skipped_uncontactable: 200`. Spider-ingested opps use `metadata.url`/`metadata.company`, not `metadata.contact_email`/`metadata.company_name`.
3. **`max_completion_tokens` floor sweep** — live LLM probe caught real gpt-5-mini calls returning empty content with `finish_reason='length'`. Codebase grep found 10 more sites with the same bug class. All bumped to 4000.

Both pre-Session-1224 initiatives Rigby created (`d8d6c0b2` hygiene + outreach tracking deliverable `329165f4-…`) closed as `COMPLETED` end-to-end. GH Actions billing still down — all 5 PRs admin-merged per existing Chris session authorization.

## Session Manifest

### PRs merged (5 total)

| # | Title | What |
|---|---|---|
| **#2539** | `feat(session-1224): deliverables hygiene — template-leak + relevance gates` | Gate 4 (`gate_4_template_leak`) — blocks titles containing `BINDING DIRECTIVE` / `research this topic to advance the initiative` / etc. Gate 5 (`gate_5_no_relevance`) — blocks `ResearchAgent` with `metadata.sources_count == 0`. 12 unit tests. Reason codes flow through `DeliverableGatedError`. |
| **#2540** | `feat(session-1224): opportunity → outreach draft pipeline + Inbox UI (Option B)` | New `OpportunityDraftGenerator` service (~270 lines). 5 REST endpoints under `/api/cockpit/outreach/*`. New `tab=work&sub=outreach` Workspace UI with draft list, inline edit, approve/reject, Generate Now button. Synthetic `SpiderData` seed (Option A — no schema migration). 14 unit tests. Tracking deliverable `329165f4-…`. |
| **#2541** | `fix(session-1224): outreach generator field-name fan-out for spider-ingested opps` | Browser smoke surfaced `created: 0, skipped_uncontactable: 200`. RemoteOK opps store `metadata.url` + `metadata.company`, not `metadata.contact_email` + `metadata.company_name`. Gate fanned out across schemas. +3 tests. 17/17 pass. |
| **#2542** | `fix(session-1224): gpt-5-mini max_completion_tokens floor sweep — 11 sites` | Live LLM probe showed outreach generator's `max_completion_tokens=800` returning empty content (`finish_reason='length'`, `reasoning_tokens=800`, `content=None`). Bumped to 4000 + grep found 10 more sites. New memory rule `feedback_gpt5_max_completion_tokens_floor.md`. |
| **(this PR)** | `docs(session-1224): close — outreach E2E + hygiene initiative + token budget sweep + Session 1225 start-here` | Session close handoff + 00-START-NEXT-SESSION.md rewrite for Session 1225. |

### Initiatives + deliverables closed

| ID | Type | Action |
|---|---|---|
| `d8d6c0b2-e281-4413-aaa0-65eadde7b15a` | Initiative | TRIAGE → **COMPLETED** (Rigby flipped via `work_tool.initiative_update_status`). Acceptance criteria fully met by PR #2539. |
| `329165f4-d5c1-420c-a6ea-d5393ec3e343` | Deliverable | `in_progress` → **completed** via `content_tool.content_complete`. Carries 3 appended sections (Backend complete, Frontend complete, Shipped + verified). |

### Existing-data cleanup (Rigby, pre-#2539-merge)

Rigby archived 3 still-`ready` `BINDING DIRECTIVE`-titled deliverables (including one on the hygiene initiative itself, `e47a5a81-…`, and 2 others). After PR #2539 merged, the factory prevents recurrence. Daily audit query: `deliverable_tool action=search query='BINDING DIRECTIVE' status=ready` should return zero new hits going forward.

## The four arcs

### Arc 1 — Outreach drafts vertical slice (PR #2540)

**Design decisions (Rigby + Claude joint plan):**
- **Selection** — `Opportunity.objects.filter(status='active')` excluding opps with any active touch-1 draft. Order: `match_score desc, potential_revenue desc, created_at desc`.
- **Schema fork:** synthetic `SpiderData` seed row (Option A) chosen over migrating `OutreachDraft.spider_data_id` to nullable. Preserves invariants, no migration risk.
- **Dedupe key:** `(opportunity_id, touch_number=1)` — one draft per opp until they reply. Round-robin offer picked at generate time.
- **Cap:** 5/day, counted by `lead_source='opportunity_outreach_seed'` tag for today.
- **LLM:** `gpt-5-mini` JSON-mode with deterministic fallback skeleton when LLM raises.
- **UI:** new sub-tab `tab=work&sub=outreach` — sibling to Queue/Deliverables/Initiatives. Chose `work` over `system` because the surface is an action queue, not telemetry.

**Vertical-slice scope discipline:** beat task (`generate_outreach_drafts_daily` at 7:30am MT) deferred to a follow-up to keep the slice tight + avoid OpenAI-credit risk for unattended runs. On-demand `autopilot_tool action=outreach_generate` + REST `/cockpit/outreach/generate/` cover the workflow today. Deferred work tracked in the close handoff — see Session 1225 FIRST THING.

### Arc 2 — Deliverables hygiene initiative (PR #2539)

Rigby spotted `BINDING DIRECTIVE`-titled deliverables mid-session. Pre-flight grep at `core/agents/research_agent.py:1103` confirmed: `title=f"Research: {task[:100]}"` — when `task` is the Stage 1 prompt (which starts with `Research this topic to advance the initiative.\n\nBINDING DIRECTIVE: ...`), the title becomes the prompt prefix verbatim.

**Defense-in-depth at factory layer:** two new gates in `deliverable_factory._should_create_deliverable`:
- `gate_4_template_leak` — title-only token match. Content can legitimately quote the directive.
- `gate_5_no_relevance` — `ResearchAgent` + `metadata.sources_count == 0` → block.

**Upstream sanitizer at `research_agent.py:1103` deferred** — the factory `GATE REJECT` log line carries the matched token and reason code, so the leak signal is actionable telemetry while Rigby audits. Will sanitize upstream only if her daily audit shows new leaks after this lands.

### Arc 3 — Field-name fan-out (PR #2541)

Browser smoke result post-#2540-merge: `created: 0, skipped_uncontactable: 200`. DB inspection showed RemoteOK opps store contact data at `metadata.url` + `metadata.company`, while my v1 gate looked for `metadata.contact_email` / `metadata.company_name` / `metadata.domain`. Top-level `opportunity.url` is empty by design for spider-ingested rows.

Gate fanned out to accept both schemas without loosening the spirit (company alone still requires a paired URL). 17/17 tests pass post-fix. Re-smoke produced 3 drafts in-process + 2 via REST = 5/5 cap hit.

### Arc 4 — `max_completion_tokens` floor sweep (PR #2542)

Live LLM probe after Chris confirmed `+$40` of credits showed: outreach generator was producing empty content. Diagnostic:

```
finish_reason: length
usage.reasoning_tokens: 800     # consumed full budget
usage.accepted_prediction_tokens: 0
content: None
```

`gpt-5-mini` is a reasoning model — it consumes 1500-2000 internal reasoning tokens BEFORE producing any visible output. A budget of 800 leaves zero room. Bumping to 4000:

```
finish_reason: stop
usage.reasoning_tokens: 1984
usage.accepted_prediction_tokens: 177
content: "Diagnostic and Roadmap for MHCLG\n\nI saw the RemoteOK listing for..."
```

Codebase grep turned up 10 more sites with the same bug class (all confirmed using `gpt-5-mini`). Notably `core/agents/autonomous_content_studio_coordinator.py:800` had `max_completion_tokens=50` for title generation — 100% empty output across all calls. And `core/tasks_initiatives.py:898` had a pre-existing comment `# Higher for GPT-5 reasoning (Session 317)` with the value still at 500 — **the under-correction had been wrong since Session ~317 and recurred** because the lesson wasn't documented as a memory rule.

All 11 sites bumped to 4000. New memory rule `feedback_gpt5_max_completion_tokens_floor.md` documents the diagnostic checklist (`finish_reason='length'` + `reasoning_tokens >> accepted_prediction_tokens` → budget bug, not prompt or credits).

## Behavioral invariants post-Session-1224

For ops monitoring (Rigby's lane):

1. **`deliverable_tool action=search query='BINDING DIRECTIVE' status=ready` returns zero new hits** going forward. Any future hit = regression signal (probably means a new template-leak phrase the token list doesn't catch — extend `TEMPLATE_LEAK_TITLE_TOKENS` in `deliverable_factory.py`).
2. **`OutreachDraft.objects.filter(lead_source='opportunity_outreach_seed', touch_number=1).count()` ≤ 5 per UTC day** (daily cap enforced by `OpportunityDraftGenerator.generate`). Higher = bug in cap accounting.
3. **`gpt-5-mini` calls produce non-empty content** when `max_completion_tokens >= 4000`. Empty content on a bumped site = different bug, not the budget anymore.
4. **`POST /api/cockpit/outreach/generate/`** is auth-required (existing middleware). REST endpoints work for both UI and curl with `Authorization: Token <chris-local-token>`.

## Rollback levers

| PR | Lever | When to use |
|---|---|---|
| #2539 | Comment out gate 4 / gate 5 in `_should_create_deliverable`. Existing telemetry shows which gate fires per reject. | Only if false-positives surface in legitimate research deliverables. Tokens are conservative; unlikely. |
| #2540 | New sub-tab gracefully degrades — drafts list empty if backend isn't running. `OutreachDraft` schema unchanged from pre-1224. Disable by removing the `case 'outreach'` block in `WorkspacePageNew.tsx`. | If UI breaks for unrelated reasons; backend stays safe. |
| #2541 | Field-name fan-out is additive in `is_contactable`/`build_prompt_payload`. Reverting tightens the gate (more skips, no break). | Unlikely needed. |
| #2542 | Bumping `max_completion_tokens` only adds cost ceiling (model returns earlier if it can). Reverting any individual site brings back empty-content bug. | Don't revert; only reduce a site if it's verified to produce well-formed content with `reasoning_tokens < 500`. |

## 24h watch checklist

1. **Outreach generator firing correctly** — `OutreachDraft.objects.filter(lead_source='opportunity_outreach_seed', created_at__gte=today_start_utc).count()` should equal whatever Chris triggered + Rigby's testing. Cap should hold at 5.
2. **Daily audit for hygiene** — Rigby runs `deliverable_tool search query='BINDING DIRECTIVE' status=ready` daily for 7 days; expect 0 new hits.
3. **Dream pipeline content** — `tasks_initiatives.py` Stage 1 title generation (line 898) + actionability/relevance/planning (lines 1160/1203/1455) should produce non-empty content after the budget bump. Grep worker logs for `[dream]` or initiative-stage debug lines and verify non-empty bodies.
4. **Vision API text verification** (`views_image_helpers.py:2815`) — any image-verification calls should return analysis text, not empty.
5. **Autonomous content studio title generator** — `autonomous_content_studio_coordinator.py:800` was producing empty 100% of the time pre-bump. Confirm titles now populate.

## Memory rules added

| File | Why |
|---|---|
| `feedback_chris_discoverability_visibility.md` | Chris's session-mid rule: builds that need his attention must be reachable from Workspace nav / Command Center / deliverables list. In-flight builds should surface as deliverables NOW because deliverables are his cross-session visibility window. Generalizes the existing last-mile UI rule. |
| `feedback_gpt5_max_completion_tokens_floor.md` | 4000 floor for any `gpt-5*` call. Diagnostic checklist: `finish_reason='length'` + `reasoning_tokens >> accepted_prediction_tokens` → budget bug. Documents the under-correction recurrence loop (Session 317 → Session 1224) that this rule breaks. |

## Lessons / pattern notes

1. **Vertical slice + browser smoke catches data-fit bugs that unit tests can't.** PR #2540's 14 tests passed; the browser smoke caught `metadata.url` vs `metadata.contact_email` (PR #2541) and `max_completion_tokens` under-budgeting (PR #2542) — both real cross-cutting bugs. Two-phase verification (unit + live) earned its keep.

2. **Live LLM probing surfaces silent fallbacks.** The deterministic fallback in `render_email` masked the real bug for the first browser smoke (Chris saw drafts, just generic ones). Without the explicit credit-check + direct probe ("show me the raw response usage"), the budget bug would've stayed hidden until Rigby asked why every draft is identical.

3. **"Under-correction recurrence" pattern.** Session 317 hit the gpt-5 reasoning budget bug, bumped from default to 500, didn't document the lesson as a memory rule. Subsequent authors (Sessions 318–1223) kept making the same under-correction. The fix isn't just the code change — it's the memory rule. This pattern probably applies to other historical fixes that didn't become memory rules.

4. **Initiative + deliverable + tracking complement each other.** Rigby spawned initiative `d8d6c0b2` mid-session for hygiene, distinct from the outreach tracking deliverable `329165f4`. Both got their own lifecycle. Chris saw progress in his deliverables list while the initiative carried the formal acceptance criteria. Each layer had its purpose.

5. **Admin-merge cadence held through 5 PRs.** GH Actions billing still down (carrying over from Session 1223). Pre-merge tests + browser smoke + verifier ran clean throughout; no PR shipped untested.

## Stack state at session close

- **Branches:** all 4 feature branches merged + deleted on origin. `main` at `2fd58b92` after the token-budget sweep.
- **Local environment:** Daphne restarted 3× during session (after PR merges that touched runtime paths). Celery restarted once (start of outreach work for `make celery` env vars). All 4 workers healthy. Frontend `dist/` rebuilt twice (initial outreach UI + post-hotfix).
- **OpenAI credits:** Chris confirmed `+$40` added; live probe verified the path works end-to-end with real personalization.
- **CI billing:** still failing per Session 1223. All 5 PRs admin-merged. Awaiting Chris-side billing fix at https://github.com/settings/billing.

## Open carryover into Session 1225

See 00-START-NEXT-SESSION.md FIRST THING. Highlights:

- **Outreach beat task** (`generate_outreach_drafts_daily` at 7:30am MT) — deferred from this slice. Single `@shared_task` + beat schedule entry; small.
- **Operator Edge newsletter Friday-1 burn-in check** — PR #2530 from Session 1222. First Friday post-merge is 2026-06-26 (3 days from session close). Verify ready/preview state output.
- **Watchdog #5 re-run** (24-48h drift confirmation) — optional from Session 1223.
- **Audit #5** (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail from 1223.
- **CI billing fix** — Chris-side.

## What didn't happen

- **No documentation index regen** — `python manage.py build_docs_index` not run this session. Should run + commit before next session if any docs files changed (no narrative or topic edits this session, so likely no drift).
- **No upstream sanitizer at `research_agent.py:1103`** — deferred per the "factory rejection is useful telemetry" argument. Revisit only if Rigby's daily audit catches new leaks.
- **No fleet sibling apps work** — carryover from Session 1223. Credits now restored so this can resume if Chris re-prioritizes.

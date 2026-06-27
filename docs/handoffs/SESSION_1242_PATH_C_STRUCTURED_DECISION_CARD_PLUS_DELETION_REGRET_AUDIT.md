# Session 1242 — Path C structured decision_card + Cat 5 deletion-regret audit + 3 PRs + 5 audit deliverables advanced

**Session window:** 2026-06-27 Saturday morning + early afternoon CDT/MDT.

**Theme:** Started as the time-bound P1 morning_brief verification window from S1241 close. Verification surfaced two Sub-step D regression candidates (PR #2658 MUSCULAR scope gap + PR #2655 MDT dead-letter), which became PR #2672 shipped and a verify-before-delete triage shipped as PR #2674 (Path C). Chris invoked a new memory rule (`feedback_verify_before_deleting_dead_code.md`) mid-session that turned what looked like a "delete dead code" cleanup into a spec-faithful implementation arc. Same session also opened the platform reality audit's Category 5 (deletion-regret) with 3 findings + Rigby's Lens B + Cat 1 fully catalogued (5 findings) + a new Cat 4 candidate (search_docs provenance filter masks Lens B audit power).

---

## TL;DR

- **3 PRs shipped, all admin-merged** (CI billing still failing — `Repo Guardrails` fails on stale platform inventory, both lints fail on Anthropic billing).
- **5 audit deliverables advanced** — 3 new Cat 5 findings + 1 new Cat 4 finding + Finding 1.1 promoted DUAL-SOURCED → RUNTIME-CHECKED + Findings 1.2-1.5 finalized + Path C deliverable shipped-closed.
- **1 new memory rule logged** (`feedback_verify_before_deleting_dead_code.md`) — Chris's directive mid-session that prevented a clean-looking "delete dead code" cleanup from destroying the on-ramp the spec was waiting on.
- **Cross-finding pattern named:** writers exist but produce 0 rows in production via 3 flavors (no callers / short-circuit before persist / feature-flagged paths). Mirrors Cat 5's silent-fallback pattern across archived modules.

### Net stats

- 3 PRs (#2672 MUSCULAR / #2673 S1241 close handoff / #2674 Path C)
- +1,341 net production LOC across 3 PRs
- 69 tests green in the 3 morning_brief-related test files (25 + 11 + 33 = 69; 33 newly added in PR #2674)
- 5 audit deliverables updated (29,887 + 21,005 + 8,167 + 17,830 + 8,306 = 85,195 chars of audit content)
- 1 new memory rule (`feedback_verify_before_deleting_dead_code.md`)
- 1 active PA conversation: `pa-634b8fef344d4af2` (~16-20 turns added this session, started at 75/continue)

---

## Session arc

### Open: P1 06-27 morning_brief cumulative verification (time-bound)

Saturday morning 9:26 CDT, well past 13:00 UTC fire window. Verified:

- **Celery fire SUCCESS** (13:00:02 UTC, 345s duration, +670 MB RSS, `Chriss-MBP.lan` worker, `default` queue)
- **Deliverable landed correctly** (`7ba30cc0-…` in Morning Brief workspace, NOT cf708a2e leak — PR #2653 holds, 5806 chars, status=ready)
- **Sub-step D invariants check** surfaced **2 regression candidates** in the content:
  - **MUSCULAR jargon leak (PR #2658 scope gap):** 4 bare MUSCULAR mentions in TL;DR / Lane 1 / Where-to-verify / Decision 1 body. The PR #2658 humanizer fired but only matched 1 of 4 escape patterns.
  - **MDT absent (PR #2655 dead-letter):** 0 MDT/MST references anywhere. LLM was emitting relative deadlines ("within 48 hours") instead of absolute ("by 11:00 AM MDT"), so the dynamic TZ inject never bit.

### MUSCULAR arc: PR #2672 (90 min)

- Diagnosed scope gap (humanizer was 2-literal-only; LLM emitted in 3 other shapes).
- Decided: broaden humanizer to tolerant regex pass + apply at `_execute_decision_card_synthesis_step` (which read `lane_1_text` raw, never humanized).
- Branched `fix/session-1242-muscular-jargon-broaden`, edited helper + call site, added 6 new tests covering each of the 4 leak sites + idempotency + already-tagged guard.
- 25 tests green locally (5 legacy + 6 new + 14 adjacent).
- Production verification on the actual 06-27 brief content: 4 bare MUSCULAR → 0 bare + 4 tagged `[MUSCULAR]`, mention count preserved.
- **Shipped as PR #2672.** Admin-merged via `--admin --merge`.

### MDT verify-before-delete arc → Path C (the big one, ~3 hr)

- Started to mark `_denver_tz` as dead code (LLM not following the prompt's absolute-format example).
- **Chris invoked NEW memory rule mid-session:** *"Remember the rule with dead code, it's not delete because it's dead, it's only delete after you verified that it's not supposed to be connected to something."* Logged as `feedback_verify_before_deleting_dead_code.md`.
- Ran 6-step verify-before-delete on `_denver_tz`:
  1. Grep direct callers → only definition site
  2. Deadline parser scan → `DecisionEnforcerAgent` parses `decision_json['deadline']` (different flow, structured dict, not markdown)
  3. **Docs search:** `MORNING_BRIEF_SPEC.md:228` **surfaced as planned consumer** — specs structured `decision_card[{..., next_step_timebox}]` alongside markdown. Implementation deferred since S1233 B.1.
  4. Recent handoff scan: only the spec mentions `next_step_timebox`. Deferred, not abandoned.
  5. Rigby `search_docs`: no ICS / calendar export plan
  6. Originating PR #2655 intent: prompt example for absolute format
- **Routed Path A/B/C triage to Rigby.** She picked (C) Hybrid — markdown stays relative for Chris's audience-fit, structured form ships absolute TZ-aware `next_step_timebox` per spec. Constraint: "present but optional" — always emitted, nullable when LLM can't derive absolute.
- **Chris ratified (C).** Logged Path C as deliverable `19b45ea0-…` in Donkey Betz workspace.
- Rigby weighed in on 4 open design Qs:
  - Q1 JSON shape: top-level `{"decision_cards": [...]}` ordered array
  - Q2 Parse strategy: prefer single-pass JSON mode if available, fallback to 2-pass embedded JSON extraction (I shipped 2-pass as v0)
  - Q3 Inspection surface: in-memory context only + observability log (no DB shape change in v0)
  - Q4 Failure mode: don't fail workflow on JSON parse — keep markdown, set `decision_cards=[]`, warning log
  - Bonus: `next_step_deadline_style` 3-state enum (`relative | absolute | hybrid`) — shipped as-is
- Implementation in `_execute_decision_card_synthesis_step`:
  - Single gpt-5-mini call emits BOTH markdown body + ```json fence
  - NEW helper `_parse_decision_card_response(full_response) -> (md, cards, issue)` with 2-pass fence matching (```json preferred, bare ``` fallback, LAST-fence-wins to dodge code-sample false-pair bug)
  - NEW helper `_validate_decision_cards_structured(cards)` enforcing 6-field contract + style enum + ISO-8601 offset + null-when-relative cross-rule
  - `_update_context` branch mirrors both keys
  - `_denver_tz` repurposed: renamed `_denver_iso_offset`, normalized to `-06:00` ISO form, fed ONLY into structured-form prompt rule
- 33 new tests across 3 classes (parser / validator / integration). 2 initial fails caught real bugs:
  - Regex non-greedy false-pair when markdown contained ```python block
  - Test assertion was too strict on negative-example prompt phrase
- Fixed both. All 69 tests green.
- `MORNING_BRIEF_SPEC.md:228` updated with implementation date + 6-field schema table + "present but optional" contract.
- **Shipped as PR #2674.** Admin-merged via `--admin --merge`.

### Platform Reality Audit deepening (Cat 5 + Cat 1 + Cat 4)

- **Cat 5 kickoff triggered by Chris's question:** *"Did we archive something that wasn't actually dead?"* Excellent instinct — exactly the right Cat 5 lens.
- Ran heuristic scan over 254 `archive/*.py` modules vs live-code importers. 9 candidates → after verifying with live-shadow check + importer-line read:
  - **3 real regret cases** (Findings 5.1 / 5.2 / 5.3)
  - 5 false positives (live shadow copies / third-party packages)
  - 1 commented-out stub (`# from core import views_unified_v2` in core/urls.py)
- Rigby ran Lens B docs-side pass on all 3. Surfaced 2 important things:
  - **5.2 has spec context** — `SESSION_34_HANDOFF.md#25` explicitly says `ml_revenue_pipeline` is "optional, fallback works fine, implement if needed." But that doc PREDATES the implementation. So her initial "drift only" classification was revised to "implementation-archived-without-doc-update" with chronology caveat.
  - **Cat 4 candidate Finding 4.3:** `search_docs` provenance filter excludes ~85% of pre-filter matches across all 13 Lens B queries. Rigby's docs-side audit lens is systemically blind unless she falls back to KB semantic search.
- **Cat 1 fully catalogued (5 findings):**
  - **1.1 promoted DUAL-SOURCED → RUNTIME-CHECKED** via Rigby's endpoint probe (count=0, source_counts=0). Reconnect delta: the upstream `AgentDecisionSummary` writer chain is the actual stillborn surface. 3 writers exist but produce 0 rows.
  - **1.2 DISPROVEN as classified** — `UnifiedAgentTemplate.objects.count() == 23`, NOT stillborn at data layer. Re-opened as CANDIDATE for browser-side rendering inspection if Directory IS empty in UI.
  - **1.3 RUNTIME-CHECKED** — Dreams beat task fires 16+ times SUCCESS, but `AgentDream.objects.count() == 0`. Task body short-circuits before persist (gate / cleanup / filter — unknown which).
  - **1.4 RUNTIME-CHECKED** — Channels has 7 writers (not 5) + 1 signal handler on `AgentChannelMessage`, but 0 rows in both `core.AgentChannel` AND `agents.AgentChannel` (DUPLICATE MODEL bug surfaced).
  - **1.5 RUNTIME-CHECKED** — Learning has 1 writer at `persistent_learning_engine.py:65`, but `PersistentLearningEngine` has 0 callers anywhere + DUPLICATE `AgentLearningSession` model (core vs ai_intelligence apps).
- **Cross-finding pattern named:** "writers exist but produce 0 rows in production via 3 flavors":
  1. Writer chain has no callers (1.5 PersistentLearningEngine)
  2. Writer chain fires but short-circuits before persist (1.3 dream tasks SUCCESS but 0 AgentDream rows)
  3. Writer chain fires only in feature-flagged or environment-specific paths (1.4 Channels gated behind Slack/deployment/integration paths)

### Tail cleanup arc: PR #2673

- S1241 close handoff + start-here update were left uncommitted at S1241 close (3 modified files in working tree).
- Branched `docs/session-1241-close-handoff-and-start-file`, committed cleanly.
- **Shipped as PR #2673.** Admin-merged.

---

## PRs shipped this session

| PR | Subject | Merge | Net | Tests |
|---|---|---|---|---|
| [#2672](https://github.com/clwest/donkey-betz-platform/pull/2672) | fix(session-1242): broaden MUSCULAR humanizer + apply at decision_card_synthesis | `74845aee` | +145 / -10 | 6 new (25 total green) |
| [#2673](https://github.com/clwest/donkey-betz-platform/pull/2673) | docs(session-1241): close handoff + S1242 entry-point | `41fa0d15` | +290 / -69 | (docs) |
| [#2674](https://github.com/clwest/donkey-betz-platform/pull/2674) | feat(session-1242): Path C — structured decision_card with next_step_timebox | `b7252f3c` | +908 / -30 | 33 new (69 total green) |

---

## Audit deliverables advanced this session

All in Donkey Betz workspace (`b4503364-…`):

| Doc | UUID | Δ this session |
|---|---|---|
| MASTER INDEX | `dfd2a073-da10-433e-90fe-1fc69a3c716a` | S1242 log entry + summary table (5,741 → 8,306 chars) |
| Cat 1 — Stillborn Surfaces | `2d7ea39f-3bf0-447c-8c89-33210fc0d18b` | Finding 1.1 RUNTIME-CHECKED + Findings 1.2/1.3/1.4/1.5 finalized + cross-finding pattern named (10,898 → 29,887 chars) |
| Cat 4 — Doc↔Code Drift | `0836042d-3a97-4d60-b9c8-11ea8d7f9884` | NEW Finding 4.3 candidate (search_docs provenance-filter exclusion masks ~85% of matches) (5,269 → 8,167 chars) |
| Cat 5 — Deletion Regret | `7ad80aaf-2025-419d-8590-8897ab2e6ee2` | 3 new findings (5.1 / 5.2 / 5.3) + Lens B classifications + chronology caveat on 5.2 (1,081 → 21,005 chars) |
| Path C deliverable | `19b45ea0-0831-43e8-aa43-038cf9c2e705` | Created mid-session + addendum'd with Rigby Q1-Q4 + SHIPPED note (0 → 17,830 chars) |

---

## New memory rule

### `feedback_verify_before_deleting_dead_code.md`

> Code that looks dead may be staged for an unbuilt connection. Never delete with rationale "I don't see what it's for" — that's a sign of insufficient search. Before any delete: grep direct callers + stringified refs + `docs/` + last 5-10 handoffs + audit deliverables via Rigby. Only after all checks come back clean is the symbol genuinely orphan.

**Why it bit this session:** I proposed deleting PR #2655's `_denver_tz` inject as "dead code" because the LLM wasn't following the absolute-format example. Verify-before-delete surfaced `MORNING_BRIEF_SPEC.md:228` as the planned consumer — the structured `next_step_timebox` field. Without the rule, I would have erased the on-ramp the spec was waiting on. With the rule, the verify-then-route-to-Rigby cycle produced Path C — a spec-faithful implementation instead of a destructive cleanup.

**Generalizes to:** any "X has no callers / no readers / no writers" claim. The codebase has many half-shipped features where one side landed and the consumer was deferred — deleting the surviving half *looks* like cleanup but destroys the on-ramp.

---

## Lessons (S1242 specific)

### Path C is the better shape than Path A whenever a spec calls for X and only ½ of X exists

My lean was (A) — delete the dead inject, mark spec field superseded. Rigby's (C) — implement both halves — was strictly better. Reason: (A) erases the spec's intent; (C) closes the drift in the spec-faithful direction. Apply same lens whenever verify-before-delete surfaces a deferred spec consumer: the spec's intent is usually the right north star.

### Per-finding schema's "Verified by Claude" + "Verified by Rigby" pair is load-bearing

S1241's audit method requires both sign-offs before promoting CANDIDATE → DUAL-SOURCED. S1242 paid for this 3 times:
- Finding 1.1 — Rigby's runtime probe confirmed the AgentDecisionSummary endpoint returns empty AND my ORM count confirmed 0 rows
- Finding 5.2 — Rigby surfaced SESSION_34_HANDOFF.md#25 but my chronology caveat caught that it predates the implementation. Without my second-pass, her classification would have been wrong direction.
- Findings 1.2-1.5 — my grep verified writers exist (against start-here's "0 writers anywhere" claim). Without that grep, all 4 would be mis-classified.

### `head -2` in foreground PA pings truncates Rigby's responses

When dispatching Rigby foreground via `tools/pa_local.sh "..." 2>&1 | head -2`, the head truncates BEFORE the response polls in. SIGPIPE may kill the polling loop early. Use full output OR query ConversationMemory ORM after the fact. Cost me ~10 min of "where did her response go" confusion mid-session.

### Cross-finding patterns from audit > individual findings

The 3-flavor pattern (no callers / short-circuit / feature-flagged) surfaced AFTER Cat 1 + Cat 5 were both populated. Naming patterns once they emerge is more valuable than mechanically completing each finding card. Save room in the audit deliverable's footer for these.

### `search_docs` provenance filter is a real audit limiter

13 Lens B queries, 100% returned `result_count: 0`, ~85% had pre-filter matches excluded by provenance gate. Cat 4 Finding 4.3 captured this — if real, it weakens the "no docs evidence found" verdicts on Findings 1.1 / 5.1 / 5.3. Worth investigating whether to (a) backfill provenance metadata, (b) make search_docs default to non-gated mode, or (c) Rigby switches to KB semantic search as primary docs-side audit tool.

---

## State at session close

- **Active PA conversation:** `pa-634b8fef344d4af2` — started session at 75/continue, added ~16-20 turns covering all 3 PRs + audit work + Lens B + Path C design + shipment summary. Health probably 50-65 range now. **Rotation at S1243 open is a real consideration.**
- **Worker state:** No `@shared_task` changes; no PeriodicTask changes. PR #2672 modifies `_humanize_body_system_jargon` + `_execute_decision_card_synthesis_step` (workflow_orchestration_agent.py); PR #2674 rewrites `_execute_decision_card_synthesis_step` further + adds 2 helpers. Both PRs touch the same agent class. **A worker restart isn't strictly required** (no new @shared_task) but the sys.modules cache memory rule applies — modifying agent module code requires worker restart for the new code to actually fire. Chris should run `pkill -9 -f celery; rm -f .celery*.pid; make celery` before going to bed if he wants tomorrow's 06-28 fire to use the new code. **Without restart, the 06-28 brief uses the OLD pre-merge code paths.**
- **Daphne:** No frontend changes — daphne restart not needed.
- **CI billing:** still failing on all 3 PRs. Both Anthropic-dependent lints + Repo Guardrails (stale platform inventory). All 3 PRs admin-merged via `--admin --merge`. Pattern unchanged from S1239-S1241.
- **06-28 morning_brief 4th-fire (07:00 MDT Sun = 13:00 UTC):** cumulative verification window for BOTH PR #2672 AND PR #2674.
- **No new outstanding action items from Chris's side this session** (Anthropic credit refill + CI billing fix are still carryover).

---

## Next session priorities (S1243)

### Priority 0 — Conversation health + rotation decision

`pa-634b8fef344d4af2` quick `session_tool action=health_check`. Started S1242 at 75/continue with 10 turns; added ~16-20 turns this session. Likely 50-65 range now. If score < 60 OR topic_count > 7, **rotate** with carry-forward summary including: PR #2672/#2673/#2674 merge commits, 5 audit deliverables advanced + their UUIDs, cross-finding pattern (writers exist but 0 rows / 3 flavors), `feedback_verify_before_deleting_dead_code.md` rule, 06-28 verification window pending.

### Priority 1 — 06-28 morning_brief 4th-fire cumulative verification (TIME-BOUND, 07:00 MDT Sun = 13:00 UTC)

**Cumulative verification window for BOTH PR #2672 (MUSCULAR broaden) AND PR #2674 (Path C structured form).** Run this verification block:

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

# 1. Did the brief fire?
ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS', f"Brief did not fire or failed: {ev}"

# 2. Did the deliverable land?
d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d, "No morning brief deliverable for 2026-06-28"
assert str(d.workspace.id) != 'cf708a2e-...', "LEAK: cf708a2e regression"

c = d.content

# 3. MUSCULAR broaden verification (PR #2672)
import re
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0, f"MUSCULAR regression: {bare} bare mentions (expected 0)"

# 4. Path C markdown verification (PR #2674)
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits, f"Absolute clock format in markdown body: {absolute_hits}"
```

**If verify clean:** worker restart was successful + both PRs landed in production behavior. Resume audit-action or other priorities.

**If verify fails:**
- MUSCULAR regression → file Cat 1 finding (different escape pattern not yet plumbed through humanizer); do NOT broaden regex further without identifying the new pipeline path.
- Absolute clock format in markdown → Path C prompt may need stronger negative-instruction OR `gpt-5-mini` is ignoring the rule.
- Brief did not fire OR worker still on old code → Chris should run `pkill -9 -f celery; rm -f .celery*.pid; make celery`.

Also worth pulling `decision_cards` log line from the Celery task logs:
```bash
grep "Session 1242 Path C: decision_cards" /tmp/celery.log | tail -3
```
Expected: `count=X, non_null_timebox=Y, parse_issue=False, structured_issues=0`. If parse_issue=True or structured_issues>0, gpt-5-mini JSON adherence needs the 2-pass repair fallback (Rigby's bonus suggestion deferred for v0).

### Priority 2 — Pick one of: audit-action, deeper audit, or carryover

After P0 + P1 land, options:

**(a) Action one of the Cat 1 / Cat 5 findings.** Cat 1 has 5 findings RUNTIME-CHECKED — each is ready for fix work:
- **1.3 Dreams short-circuit** (HIGHEST USER-FACING IMPACT) — `AgentDream.objects.count() == 0` despite beat tasks firing 16+ times SUCCESS. Read `_impl_maintain_dream_backlog` to find the gate.
- **1.5 PersistentLearningEngine orphan** — module has 0 callers. Easiest "remove" case (latent dead code).
- **1.4 Channels duplicate model bug** — `core.AgentChannel` vs `agents.AgentChannel`; verify which one writers vs readers use.
- **1.2 Directory rendering check** — Quick browser-side inspection: hit `/api/v1/agents/comprehensive` and confirm 23 UnifiedAgentTemplate rows surface in response.

Cat 5 has 3 findings; recommend Cat 5 first only if Chris wants to actually restore archived modules (5.1 ml_intelligence.ml_service is the highest-impact restore — silent ML degradation in agent-advisor bridge).

**(b) Deeper audit scan.** Cat 5 v1 heuristic was module-name-only. Broaden to:
- Class/function-level imports (`from <live_module> import <ClassName>` where ClassName was archived but module shell remained)
- Celery task-name string scan (`app.send_task('archived_name')`)
- Settings.py grep (archived modules in `INSTALLED_APPS`, `MIDDLEWARE`, etc.)
- Dynamic imports via `importlib.import_module(...)`

Plus Cat 2 (Phantom Dependencies) and Cat 3 (Orphan Models & Migrations) and Cat 6 (Works-but-wrong-scope/permissions/flags) all have empty schemas with 0 findings — pick one and seed.

**(c) Rigby docs-side passes for findings still pending Lens B:**
- Finding 1.2 (Directory) — pending
- Finding 1.3 (Dreams) — pending
- Finding 1.4 (Channels) — pending
- Finding 1.5 (Learning) — pending

**(d) Carryover tail** (unchanged):
- Anthropic credit refill (Chris-side)
- CI billing fix (Chris-side)
- Rigby memory store cap (S1239)
- 80 spiders / 30 advisors / 9 body systems / 144 Discord commands audits
- 7 fleet sibling apps
- Smoke-harness mode inconsistency (S1231 F5)
- Smoke-probe tagging for AgentExecution (S1231 F1)
- Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents`
- Audit `5318da3e-…` §R2 amendment (S1231 F3)
- Engineer workspace staleness (S1230 F3)
- Meeting-context leak shape watch (S1230 F2)
- Fleet-smoke wall-clock timeouts (S1231 F2)

### Priority N — Whatever Chris wants

Sessions 1226-1242 totaled ~85 PRs + 2 no-code audit sessions. S1242 alone shipped 3 PRs + 5 audit deliverables + 5 findings advanced. S1243 natural arc is either P1 verify-then-action OR deeper audit.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since S1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`

---

## What this session was NOT

- **Not a no-code session.** S1241 was no-code (audit foundation); S1242 was both code (3 PRs) AND audit deepening (5 deliverables advanced).
- **Not a "fix the regressions" session in isolation.** The MDT thread became Path C (architecture work). The MUSCULAR thread became one tight PR.
- **Not a session that touched the runtime ML-enhanced agent-advisor pipeline.** Findings 5.1 / 5.2 surfaced silent ML degradations but we did NOT restore the archived modules — catalogued only.
- **Not a session that ran the docs-to-Rigby 4-step cascade.** This handoff edits + `MORNING_BRIEF_SPEC.md` edit + start-here edit are pending Rigby visibility. Cascade should run at S1243 open OR on a dedicated docs-batch session.

---

## Key insight (S1242)

> "Code that looks dead may be staged for an unbuilt connection."

Chris's mid-session directive is now `feedback_verify_before_deleting_dead_code.md`. The rule's first real application in the same session demonstrated its value: it converted what I framed as "delete dead code" into Path C — a spec-faithful implementation that closes drift instead of erasing it. Same shape will repeat across many future "X looks unused" calls. The audit's Cat 5 work also showed the inverse: 5.1 / 5.2 / 5.3 were archived under similar "looks dead" reasoning, and we now suspect at least 2 of them (5.1 + 5.2) had silent-fallback consumers that were broken in the process. The rule is bidirectional.

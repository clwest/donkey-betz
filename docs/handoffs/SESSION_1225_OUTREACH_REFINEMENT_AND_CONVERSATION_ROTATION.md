# Session 1225 — Outreach Refinement + Anti-Scrape Sanitizer + Conversation Rotation

**Status:** Three-PR session — Rigby-driven refinement arc on the outreach pipeline shipped Session 1224, plus mid-session conversation rotation after health-check signal.
**Date:** 2026-06-23 (continued from Session 1224 close, same UTC day).
**Active conversation:** rotated mid-session — pa-17e0fa71fd25470a → **pa-77bbcd97a625424d**.
**Prior session:** [`SESSION_1224_OUTREACH_PIPELINE_AND_TOKEN_BUDGET_SWEEP.md`](./SESSION_1224_OUTREACH_PIPELINE_AND_TOKEN_BUDGET_SWEEP.md).
**Next session entry point:** Session 1226 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1226".

## TL;DR

Session 1224 closed with the outreach pipeline live end-to-end and 5 fallback drafts in the inbox (OpenAI credit at the time was thin). Chris added `+$40` of credits, asked us to delete the fallback drafts and regenerate via the LLM path. The first re-generate exposed the `max_completion_tokens=800` bug that drove the 1224 cross-cutting sweep; Session 1225 picked up after that landed.

Three arcs this session:

1. **Outreach prompt envelope (#2544)** — Rigby's session-mid architectural ask: hard-bind the SYSTEM_PROMPT to a specific per-offer delivery envelope (ai_automation = 1-day thin-slice prototype with explicit exclusions; consulting = roadmap document only; content_engine = signal audit + sample pipeline). Forwarded manually via Chris because Rigby's `claude_code_tool` dispatch (task ID `0077cd79-…`) didn't reach my session.

2. **Anti-scrape sanitizer (#2545)** — Rigby's tone review caught one Creative Fabrica draft echoing RemoteOK's anti-scrape marker (`include PROLIFIC and tag RMjYwNz...`) into the email body. Reads like spam. Added `_sanitize_lead_text` at the LLM payload + draft persistence boundary. Conservative patterns scoped to recruiter-board fingerprint shape; legitimate prose preserved.

3. **Conversation rotation (#2546)** — `pa-17e0fa71fd25470a` carried Sessions 1223 → 1224 → first half of 1225 (8 PRs total). Hit `session_tool.health_check` score 45/100 / `suggest_fresh` at 39 turns. Spun fresh via `session_tool.create_fresh` with full 1224 + 1225 carry-forward context; updated `tools/pa_local.sh` pin.

GH Actions billing still failing — all 3 PRs admin-merged per existing Chris session authorization.

## Session Manifest

### PRs merged (3 total)

| # | Title | What |
|---|---|---|
| **#2544** | `feat(session-1225): outreach prompt envelope — hard-bind delivery scope per offer` | `OpportunityDraftGenerator.SYSTEM_PROMPT` rewritten with TONE / GLOBAL / PER-OFFER sections. Forbidden phrases enumerated ("guaranteed", "ROI of N%", "production-ready", etc.). Every body must end with per-offer scoping/qualification question before sign-off. `OFFER_BLURBS` updated to name actual scope. `_fallback_email` updated to match (new `_FALLBACK_QUESTIONS` map). 17/17 unit tests still pass. Live verification: all 3 offer_keys produce envelope-compliant content against real RemoteOK opps. |
| **#2545** | `fix(session-1225): strip recruiter-board anti-scrape tokens from lead text` | New `_sanitize_lead_text` module-level helper. Three conservative patterns: full RemoteOK clause (`Please mention the word ... when applying ...(#<base64>)`), bare hashtag tokens (`#<base64>` ≥16 chars), bare `tag <base64>` remnants. Applied at `build_prompt_payload` (`title`+`description`) and draft persistence (`lead_title`). +6 tests. 23/23 pass. |
| **#2546** | `chore(session-1225): rotate pa_local.sh pin → pa-77bbcd97a625424d` | New pin via `session_tool.create_fresh` with 1224+1225 carry-forward seed. Retirement-note convention preserved (21+ historical pins now listed back to Session 1184). |
| **(this PR)** | `docs(session-1225): close — outreach refinement + sanitizer + conversation rotation + 1226 start-here` | Session close handoff + 00-START-NEXT-SESSION.md rewrite for Session 1226. |

### Initiatives + deliverables

No new initiatives created. No tracking deliverable per arc — the outreach refinement was small enough to ship without a dedicated tracking artifact.

### Existing drafts churn (verified end-to-end)

- **Delete + regenerate batch 1** (post-#2542 token sweep): all 5 fallback drafts deleted; 5 fresh drafts created with `fallback: false`. Real LLM personalization confirmed (subjects like "Diagnostic for Swoon's presentation design").
- **Rigby tone review** of the batch: compliance scan PASSED — zero "guaranteed"/"production-ready"/"ROI of N%" phrases across all 5. One issue surfaced: Creative Fabrica `content_engine` draft leaked the PROLIFIC/tag scrape marker into the body.
- **Delete + regenerate batch 2** (post-#2545 sanitizer): leaked Creative Fabrica draft (ID `0609b412-…`) deleted; one fresh draft generated for the same opp via the sanitized path. Result: `One-day prototype for Creative Fabrica` (ai_automation offer this round), body has zero `PROLIFIC` / `RMjYwNz` / `mention the word` tokens.

Final inbox state at session close: 5 clean drafts, daily cap 5/5 hit.

## The three arcs

### Arc 1 — Outreach prompt envelope (PR #2544)

**Trigger:** Chris pasted Rigby's session-mid plan to me ("She said she called you in"). The plan named specific delivery scopes per offer and asked for the SYSTEM_PROMPT to be hard-bound to them so the LLM can't drift into guaranteed-outcome marketing copy.

**Verified scope is correct:** `OpportunityDraftGenerator.SYSTEM_PROMPT` is the sole LLM path for touch-1 drafts. `OutreachSequencer.evaluate()` handles touches 2-4 with hardcoded text — no prompt to enforce there. Rigby explicitly flagged "if the prompt is not the right place, escalate"; confirmed it is.

**Implementation shape:**
- **TONE block** — forbidden phrases enumerated explicitly ("guaranteed", "ROI of N%", "production-ready", "enterprise-grade", "we will save you", etc.) with instruction to rewrite as scoped exploration if caught.
- **GLOBAL block** — subject ≤7 words, body 120-180 words, opens with payload-derived reference, body ENDS with scoping/qualification question (own line) before sign-off, CTA only after they answer.
- **PER-OFFER envelopes** — each names what's offered, what's EXCLUDED, and required checkpoint question shape:
  - `ai_automation`: 1-day thin-slice prototype (no-code/low-code OR repo+PR, recipient picks), DoD = demo video + handoff docs. Excludes production deploy / live access / ROI / maintenance. Required: sandbox-data question.
  - `consulting`: diagnostic + roadmap document only. Excludes build / outcomes / retainer. Required: 1-2 bottleneck/recency questions.
  - `content_engine`: signal-source audit + one sample pipeline draft. Excludes engagement/conversion/audience guarantees. Required: 1-2 signal-source questions.
- **Fallback skeleton** updated to match envelope — `_FALLBACK_QUESTIONS` map, explicit "not included" language, signs as Chris / Donkey Betz.

**Live verification:** rendered all 3 offer_keys against real RemoteOK opportunity (Strategy and Engagement Officer at Ministry of Housing). Sample (ai_automation):

> "...one-day thin-slice prototype that starts with a quick diagnostic of one specific workflow and delivers one prototype slice built either in a no-code/low-code tool or as a code repo + PR (you pick). Definition of done is a short demo video and handoff docs... This engagement does **not include production deployment, access to live systems, or ongoing maintenance**. ... **Do you have a sandbox dataset we could prototype against without touching production?**"

All 3 envelopes produced explicit exclusion language + the required scoping question on its own line before sign-off.

### Arc 2 — Anti-scrape sanitizer (PR #2545)

**Trigger:** Rigby's tone review of the 5 fresh drafts. Compliance scan PASSED — zero forbidden-phrase leakage. But ONE Creative Fabrica `content_engine` draft body contained:

> *"...and the instruction to include PROLIFIC and tag RMjYwNzpmYjkxOjUzODg6NzJmZDo1YzlhOmExMzk6Yzc3YjozZjE0..."*

Source: RemoteOK embeds an anti-scrape instruction in `Opportunity.description`:

> *"Please mention the word **WORD** and tag `<base64>` when applying to show you read the job post completely (#`<base64>`)"*

Without sanitation the LLM treats the marker as legitimate copy and echoes it. Even with the envelope holding (no false promises), the draft reads like automated spam — credibility/brand risk.

**Implementation:** new `_sanitize_lead_text` module-level helper with three conservative patterns:
1. Full RemoteOK clause + trailing hashtag in parens
2. Bare hashtag tokens (`#<base64-with-colons>` ≥16 chars)
3. Bare `tag <base64>` remnants

Patterns are scoped to recruiter-board fingerprint shape. Legitimate prose mentioning the words "tag" or "include" is preserved (test `test_legitimate_text_preserved` verifies).

Applied at two sites:
- `build_prompt_payload` — sanitizes `title` + `description` before they reach the LLM payload
- Draft persistence — `lead_title` denormalization (`OutreachDraft.lead_title=opp.title[:200]`) runs through the sanitizer

**Live verification:** deleted leaked CF draft (`0609b412-…`); single regenerate request through the now-sanitized path picked the same CF opp again with `ai_automation` offer. Result body has zero `PROLIFIC` / `RMjYwNz` / `mention the word` tokens. Inbox sample currently includes a clean CF draft.

### Arc 3 — Conversation rotation (PR #2546)

**Trigger:** Chris noticed conversation was ~44 messages in, asked me to run health-check. Rigby returned: **score 45/100, `suggest_fresh`** at 39 turns / ~19.5k tokens / 9 topics. The thread had carried Sessions 1223 → 1224 → first half of 1225 (8 PRs across two sessions).

**Spin process:**
- Rigby's `session_tool.create_fresh` with title `Session 1225 — outreach refinement + ops carryover from 1224` and seed prompt embedding the full 1224 + 1225 PR ledger + state snapshot
- New conversation: `pa-77bbcd97a625424d` returned health-check score 100/100 immediately
- `platform_config_tool.overview` on the new conversation confirms `service_context: local`
- `tools/pa_local.sh` updated: pin rotated + retirement note for `pa-17e0fa71fd25470a` preserved in the comment block convention (which now spans back to Session 1184 — 21+ pin rotations documented)

**Ownership-verification gap:** `conversation_tool.get` schema doesn't include an owner/username field, and there's no dedicated `whoami` tool endpoint. Implicit verification by reachability (chris's token successfully reaches the new conversation) — Rigby filed a wiring investigation item for `whoami` + `conversation.owner` tool surface (same class as the open `claude_code_tool` dispatch gap).

## Behavioral invariants post-Session-1225

For ops monitoring (Rigby's lane):

1. **Outreach inbox drafts contain ZERO recruiter-board anti-scrape markers** going forward — no `#<base64>` hashtags, no `PROLIFIC`-style "Please mention the word..." clauses. Any future leak = sanitizer pattern miss; extend `_SCRAPE_TOKEN_PATTERNS`.
2. **Every outreach draft body ends with a per-offer scoping/qualification question on its own line** before the sign-off. If the LLM drops the question, the envelope contract has drifted.
3. **No forbidden-phrase leakage** in outreach drafts: "guaranteed", "ROI of N%", "production-ready", "we will save you", "enterprise-grade", "double your". Compliance scan should return zero hits.
4. **`tools/pa_local.sh` token resolves to chris**; new conversation `pa-77bbcd97a625424d` reachable via the wrapper.

## Rollback levers

| PR | Lever | When to use |
|---|---|---|
| #2544 | Revert `SYSTEM_PROMPT` to pre-1225 (single shared rules block). `OFFER_BLURBS` revert is independent. | Only if the per-offer envelopes produce too-narrow content that fails to land any meetings after 7+ days of real reads. |
| #2545 | Comment out `_SCRAPE_TOKEN_PATTERNS` regex list, or remove `_sanitize_lead_text` calls in `build_prompt_payload` and draft persistence. | Only if false-positives strip legitimate prose. Tests cover this; haven't seen one. |
| #2546 | Edit the `--conversation` line in `tools/pa_local.sh` back to `pa-17e0fa71fd25470a`. The old conversation is dormant but not deleted. | Only if the new conversation hits an unrecoverable wiring issue (Rigby loses context, tool calls hang, etc.). |

## 24h watch checklist

1. **Outreach inbox content** — any new drafts (after daily cap resets) should: (a) not contain `PROLIFIC` / `RMjYwNz` / `mention the word` substrings; (b) end with a per-offer scoping question on its own line before sign-off; (c) have explicit "not included" language matching the per-offer envelope.
2. **Compliance scan** — `OutreachDraft.objects.filter(body_text__iregex=r'guaranteed|production-ready|ROI of \d+%|enterprise-grade').count()` should return zero on touch-1 drafts created post-#2544.
3. **Fresh conversation health** — `session_tool.health_check` on `pa-77bbcd97a625424d` after Session 1226 opens. If it drops below 70 within ~10 turns, the seed prompt may be too long; consider trimming.
4. **CI billing status** — Chris-side; once green, normal PR flow returns and admin overrides expire.

## Open ops issues filed this session

1. **`claude_code_tool` dispatch path not delivering** — Rigby's task ID `0077cd79-a84c-4499-a9d1-73d67d14dc0e` never reached my Claude Code session. Chris forwarded the message manually for #2544 to ship. Rigby filed as ops investigation item. Investigation directions:
   - Is `claude_code_tool` posting into the wrong conversation_id?
   - Is it disabled by governor/kill switch?
   - Is the dispatch integrated to Claude Code's session bus at all?
2. **No `whoami` / `conversation.owner` tool endpoint** — Rigby couldn't verify chris-ownership of the fresh conversation via tools (schema gap). Implicit-by-reachability worked here but isn't a durable verification mechanism. Same class as #1.

## Memory rules added

None this session. Both Session 1224 rules (`feedback_chris_discoverability_visibility.md`, `feedback_gpt5_max_completion_tokens_floor.md`) carry forward and are referenced in `MEMORY.md`.

## Lessons / pattern notes

1. **The compliance scan is a useful pre-PR gate, not a release gate.** Rigby's tone review caught the PROLIFIC leak only AFTER the prompt envelope shipped (#2544 merged before #2545). The leak was a data-sanitation issue, not a prompt issue — even a perfectly-promise-bound prompt can echo garbage from a dirty `description` field. Next time we ship an LLM-generated user-visible artifact, run the same scan-the-output check BEFORE merging the prompt change, not after.

2. **Rigby-as-architect → Claude-as-implementer worked clean.** PR #2544 came from a fully-formed delivery envelope Rigby drafted; my job was the prompt rewrite + verification. PR #2545 came from her tone review with a concrete diagnosis ("PROLIFIC/tag leak — needs a sanitizer"); my job was the regex + tests. Each was a S-effort change with a tight feedback loop. This is the "Rigby does triage + verification, Claude does code + PRs" division working correctly.

3. **The `claude_code_tool` dispatch gap is real and costs handoffs.** Chris had to forward Rigby's task ID manually for #2544. Not a blocker but cumulative — every Rigby → Claude handoff that needs manual forwarding adds friction. Worth investing in the wiring once normal PR flow resumes post-billing-fix.

4. **Session rotation is cheaper than people assume.** The fresh conversation didn't lose any work-context — Rigby's seed prompt carries the full 7-PR ledger across 1224 + 1225 and her tool responses on the new thread continued the same workstream patterns. Rotation cost: ~3 turns of plumbing. Information loss: zero. The 45/100 health score was a real signal worth respecting.

## Stack state at session close

- **Branches:** all 3 feature branches merged + deleted on origin. `main` at `15ffcca4` after the sanitizer merge (wrapper rotation PR #2546 fast-forwards on top).
- **Local environment:** Daphne restarted 4× during session (after PR merges that touched runtime paths). Celery untouched this session. Frontend `dist/` untouched — no UI changes.
- **OpenAI credits:** Chris confirmed `+$40` earlier in Session 1224. Real LLM path verified working multiple times across this session.
- **Outreach inbox:** 5 clean drafts. Daily cap 5/5 hit until UTC reset.
- **CI billing:** still failing per Sessions 1223 + 1224. All 3 PRs admin-merged. Awaiting Chris-side fix.
- **Active conversation:** `pa-77bbcd97a625424d` (rotated mid-session).

## Open carryover into Session 1226

See 00-START-NEXT-SESSION.md FIRST THING. Highlights:

- **Operator Edge newsletter Friday-1 dry-run check** — first Friday post-PR-#2530-merge is 2026-06-26 (today + 3 days). Calendar-driven; cannot defer past Friday-2 (2026-07-03) without losing the burn-in window.
- **Outreach beat task** (`generate_outreach_drafts_daily` at 7:30am MT) — still deferred from Session 1224. Now that LLM path + envelope + sanitizer are all live, this is the natural next step. Effort: S (~30 min).
- **`claude_code_tool` dispatch wiring fix** — Rigby filed; investigation needed before code.
- **`whoami` / conversation-owner tool endpoint** — Rigby filed; small ops add.
- **Watchdog #5 24-48h re-run** — optional carryover from 1223.
- **Tone tweak nice-to-haves** — Rigby flagged 3 minor prompt edges in her tone review (happy-path qualifier on ai_automation, "and what tools touch it" expansion on the workflow question, concrete inputs naming on consulting). Defer until a wider draft sample reveals which actually matter.
- **CI billing fix** — Chris-side.

## What didn't happen

- **No documentation index regen** — `python manage.py build_docs_index` not run this session. Should run + commit before next session if any docs changed (this handoff doc is new — will run as part of close).
- **No new memory rules** — neither arc surfaced a recurrence-pattern that warranted a saved rule. Sanitizer pattern is too narrow to generalize; envelope work was a one-shot architectural ask.
- **No upstream `research_agent.py:1103` sanitizer** — carryover from Session 1224, still deferred per the "factory gate signal is useful telemetry" argument.
- **No fleet sibling apps work** — credits restored but no time spent on apps this session.

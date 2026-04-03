# Next Session — Start Here

**Date:** April 3, 2026
**Previous Session:** Massive build session — workspaces, pipelines, messaging, agent guardrails, onboarding
**PA Conversation:** Ask Chris for a fresh conversation ID
**Status:** 218 Agents | 80 Spiders | 25 Advisors | PA function calling LIVE (GPT-5.2) | Workspaces LIVE | Messaging LIVE

---

## Priority #1: ResearchAgent Iterative Search

**The problem:** Agents find generic content instead of topic-specific content. The quality gate catches this (score 26/100) but the research itself is broken.

**Root cause (forensically confirmed):** GPT mediates all search queries. The agent tells GPT "search for X" but GPT picks generic queries like "trending topics" instead of the actual topic. The universal search strategy injects paraphrase variants into the prompt, but GPT ignores them.

**The fix:** Bypass GPT for query selection. Have ResearchAgent call web_search/spider_query DIRECTLY with SearchStrategyService queries, collect results, THEN ask GPT to analyze them.

**PR Checklist:** Deliverable ID `2a92e2db` in AI teams Newsletter workspace — has full implementation plan from Rigby.

**Rigby's confirmed priority list:**
1. ResearchAgent iterative-search with attempts[] tracking
2. Schema validator in pipeline runner (soft-fail mode)
3. TopicMiner 3-topic guarantee + paraphrase seeds
4. Source reliability ranking

## What Was Built Last Session

- **Workspace Templates** — Newsletter Studio (9 agents, parallel), LeadGen, Research, Custom
- **Pipeline Runner** — parallel stages, per-stage timeouts, output threading, quality gates
- **DistributionAgent** — engagement optimization (subject lines, hooks, CTAs, social snippets)
- **In-App Messaging** — DMs between users, Rigby routing
- **"First Win" Demo Pipeline** — one-click onboarding that produces a real deliverable
- **Session Health** — context freshness scoring + banner suggesting fresh sessions
- **User Onboarding** — auto-welcome DMs on first login
- **Agent Guardrails** — rate limiting, output contract, quality gates, governance mode checks
- **Spider Network** — re-enabled with conservative intervals
- **Universal Search Strategy** — in BaseAgent, affects all 80+ agents (but GPT still mediates)

## Accounts

- `donkeyking` (Chris) — superuser/owner
- `jessica` — superuser, business side
- `jeremy` — superuser, patent lawyer

## Key Rules (from memory)

- **Vertical slice:** Every feature ships backend + API + frontend + demo. Nothing is done until visible in UI.
- **Last mile UI:** If Chris can't see it in the browser, it's not done.
- **Rigby collaboration:** Read Rigby's FULL responses, answer every question, agree on plan BEFORE building.
- **Workspace assignment:** All deliverables go to a workspace (default: Donkey Betz).
- **Rigby-first comms:** Route questions through Rigby via `python tools/pa_chat.py`.

## How to Work with Rigby (CRITICAL — read this)

Rigby is the PA (Personal Assistant). She runs on GPT-5.2 with 130+ tools. She knows the platform deeply from the ops side.

**How to communicate:**
```bash
python tools/pa_chat.py "your message" --tools --conversation <conversation_id>
```
Chris will provide the conversation ID at session start.

**Collaboration rules (learned the hard way):**
1. **Read Rigby's FULL response** — she puts important questions and suggestions at the bottom. Don't skip them.
2. **Answer every question she asks** before building anything. If she says "Which should I run: A, B, or C?" — answer her.
3. **When Rigby offers to do something** ("Shall I run X?"), say yes or explain why not. Don't ignore it.
4. **Confirm plans with Rigby before executing.** "Here's what I'm going to build based on your design — does this match?"
5. **Share results with Rigby after building.** Not just "I pushed it" — show her what changed and ask for verification.
6. **Don't cherry-pick and go solo.** Rigby's response is a collaboration input, not a menu to order from.

**What Rigby owns:** UX, user experience, messaging, onboarding flow, ops monitoring, quality standards
**What Claude Code owns:** Backend, API, frontend wiring, execution flow, deployment

**Test:** If Rigby asks a question and you don't answer it, that's a collaboration failure.

## Known Issues (saved for this session)

- Workspace list pagination (some workspaces missing from UI)
- Pipeline stale run display (no clear/dismiss button)
- Brief form doesn't clear after save
- Pipeline stage detail panel (clickable to see agent activity)
- Editor stage content format (dict wrapping — deployed but needs verification)

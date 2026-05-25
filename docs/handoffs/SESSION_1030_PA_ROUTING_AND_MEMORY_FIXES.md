---
originating_session: 1030
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1030: PA Routing & Memory Fixes

**Date:** February 17, 2026
**PRs:** #1287, #1288, #1289

## Problem

Production PA audit (12 test messages against Railway API) revealed 5 routing/payload failures:

1. **Blog/content routing broken** — "show me the latest blogs" fell to `general` intent (substring "show blogs" didn't match "show me the latest blogs"). When it did match `content_review`, the `details` action fired (requires ID) because "show" matched before "latest".
2. **Agent execution doesn't fire** — "run ResearchAgent" matched `research` intent before `agent_execution` because "research" keyword appeared earlier in the intent chain. Even when routing was fixed, the payload lacked `agent_name` extraction.
3. **Crypto price returns 0** — Keyword search on `embedding_text` returned nothing because CoinGecko stores price data in `processed_data` JSON, not in text embeddings.
4. **No conversation memory** — PA instance's `_conversation_history` stored in-memory was lost on every Celery worker recycle (`max_tasks_per_child=50`).
5. **Sports betting misrouted** — "sports betting opportunities" matched `opportunities` intent before `sports_betting` because "opportunities" keyword checked earlier.

## Root Causes

All 5 issues trace to two systemic problems in `_detect_intent_and_route()`:

1. **Intent priority ordering** — Keywords checked top-to-bottom; generic terms ("research", "opportunities", "show") matched before specific intents.
2. **Missing payload builders** — `agent_execution` and `crypto_price` intents had no payload extraction logic, so handlers received empty/wrong data.

## Fixes

### PR #1287 — Core 5 Fixes

**File: `core/services/unified_pa_entrypoint.py`**

| Fix | Change |
|-----|--------|
| Sports betting before opportunities | Added sports_betting keywords check at ~line 838, before generic "opportunities" check |
| Broader blog patterns | Added 'latest blogs', 'recent blogs', 'my blogs', 'publish-ready' etc. to content_review intent |
| Blog type auto-detection | When message mentions "blog/blogs", auto-set `payload['type'] = 'blog'` so handler queries SelfBlog (not Deliverable) |
| Publish-ready guard | "publish-ready" routes to `recent` action with 30-day filter, not `publish` action (which requires ID) |
| Agent execution before research | Moved agent_execution check (with regex) before research keywords |
| Crypto by_spider | Changed crypto_price payload from keyword search to `by_spider` action with `spider_name='coingecko'` |
| Conversation memory from DB | New `_load_conversation_history_from_db()` loads last 10 `ChatConversation` rows on init |

**File: `core/services/tool_dispatcher.py`**

| Fix | Change |
|-----|--------|
| SelfBlog stats | `stats` action now includes SelfBlog counts (total, published, publish_ready, drafts) |
| processed_data in by_spider | First 3 results include `processed_data` field (crypto prices live there) |

### PR #1288 — Routing Refinements

| Fix | Change |
|-----|--------|
| Agent execution regex | Removed `\b` before "agent" so "researchagent" matches (no word boundary in compound word) |
| Blog "show me" routing | Added "latest/recent/newest/show me" as `recent` action before `details` check |

### PR #1289 — Agent Execution Payload

| Fix | Change |
|-----|--------|
| Agent name extraction | New payload builder for `agent_execution` intent extracts `agent_name` (preserving PascalCase) and `task` from messages like "run ResearchAgent to find AI trends" |

## Production Verification

All 5 tests verified on Railway production API:

| # | Test Message | Expected Intent | Result |
|---|-------------|----------------|--------|
| 1 | "show me the latest blogs" | content_review | PASS — returns 10 recent items |
| 2 | "run ResearchAgent to find AI trends" | agent_execution | PASS — routes correctly, agent runs (30s tool timeout) |
| 3 | "what is the current bitcoin price" | crypto_price | PASS — returns CoinGecko data |
| 4 | "what did I just ask you about?" | general | PASS — recalls previous bitcoin question |
| 5 | "sports betting opportunities" | sports_betting | PASS — returns betting overview |

## Testing Methodology

Used production API with curl:
```bash
# Send
curl -s -X POST "https://donkey-betz-platform-production.up.railway.app/api/pa/chat/" \
  -H "Authorization: Token <redacted-0cdc1c72-2026-04-20>" \
  -H "Content-Type: application/json" \
  -d '{"message":"show me the latest blogs"}'
# Returns: {"task_id": "..."}

# Poll
curl -s "https://donkey-betz-platform-production.up.railway.app/api/pa/chat/status/<task_id>/" \
  -H "Authorization: Token <redacted-0cdc1c72-2026-04-20>"
# Returns: {status, content, intent, latency_ms, ...}
```

## Key Discovery: Intent Detection Order Matters

`_detect_intent_and_route()` checks keywords sequentially. The fix pattern for misrouted intents:

1. **Identify the generic keyword** that matches too early (e.g., "research", "opportunities", "show")
2. **Move the specific intent check** before the generic one
3. **Use compound phrases** or regex for disambiguation

This is a recurring pattern — any future intent additions must consider where they land relative to existing generic keywords.

## Remaining PA Issues (Not Fixed This Session)

- **PA tool timeout**: `universal_agent_tool` has 30s timeout — too short for LLM-based agents like ResearchAgent. Agent runs but times out.
- **PA context awareness**: PA doesn't understand which page the user is on. "I just created an image but it's not displaying" from Image Studio gets generic response.
- **Crypto data formatting**: CoinGecko data returns but the LLM summary shows "Hyperliquid" (top market cap coin) instead of extracting the specific coin the user asked about. Needs better prompt engineering or pre-filtering.

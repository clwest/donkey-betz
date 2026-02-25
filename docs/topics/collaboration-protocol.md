# Three-Way Collaboration Protocol

**Status**: Active
**Version**: 1.0
**Last Updated**: 2026-02-25

## Overview

This document defines the collaboration protocol between three actors in the platform:

| Actor | Role | Identity |
|-------|------|----------|
| **User** | Sets intent, priorities, approvals. Final authority. | `source: 'web'` / `'mobile'` / `'discord'` |
| **PA** | Holds the *why/how*. Plans, decisions, acceptance criteria, platform intelligence. | `source: 'pa'` |
| **Claude Code** | Executes work. Edits code, runs commands, reports results. | `source: 'claude-code'` |

## Design Principles

1. **The "why/how" must be durable** — context survives tool crashes/timeouts
2. **Every message has a known actor** — no anonymous messages in shared conversations
3. **Claude Code reports, PA advises, User decides** — clear authority chain
4. **Structured messages enable automation** — PA can parse Claude Code reports programmatically

## Communication Channel

All three actors communicate through **shared PA conversations** via:

- **Endpoint**: `POST /api/pa/chat/`
- **Conversation targeting**: `conversation_id` field links messages to the same thread
- **Actor identity**: `source` field identifies who sent the message

### Authentication

| Actor | Auth Method |
|-------|-------------|
| User (web) | Session cookie / DRF Token |
| User (mobile) | DRF Token (`Authorization: Token <key>`) |
| Claude Code | DRF Token + `source: 'claude-code'` |
| PA (internal) | Server-side, no external auth needed |

## Structured Message Format

Claude Code posts structured messages using a prefix-based format that PA can parse:

### Message Types

| Type | Prefix | When to Use |
|------|--------|-------------|
| **PLAN** | `[PLAN]` | Before starting work — what will be built and why |
| **STATUS** | `[STATUS]` | Progress update during long-running work |
| **RESULT** | `[RESULT]` | Work completed — summary of what was done |
| **DIFF** | `[DIFF]` | Files changed with brief descriptions |
| **ERROR** | `[ERROR]` | Something failed — what and why |
| **QUESTION** | `[QUESTION]` | Needs input from User or PA before proceeding |

### Message Structure

```
[TYPE] Title

Body text with details.

--- metadata ---
key: value
```

### Examples

#### PLAN message
```
[PLAN] PR-14: Content Pipeline Screen for Mobile

Building the /content screen for the React Native app.
PA designed the spec, verified backend endpoints.

Views: overview, article list, article detail, pipeline status
API endpoints: /v1/content/articles/, /v1/content/pipeline/stats/

--- metadata ---
pr: 14
files_planned: 4
based_on: PA spec from conversation mobile-pr14
```

#### RESULT message
```
[RESULT] PR-14 merged successfully

Created content pipeline screen with 4 views.
TypeScript compiles clean. PR #1470 merged to main.

Files created:
- mobile/src/api/types/content.ts
- mobile/src/api/content.ts
- mobile/src/screens/ContentScreen.tsx

Files modified:
- mobile/src/navigation/screenRegistry.ts

--- metadata ---
pr: 14
pr_number: 1470
pr_url: https://github.com/clwest/donkey-betz-platform/pull/1470
files_changed: 4
insertions: 890
deletions: 1
```

#### ERROR message
```
[ERROR] Agent timeout during content generation

ResearchAgent timed out after 180s calling OpenAI API.
Root cause: gpt-5-mini reasoning took longer than timeout.
Immediate fix: increased llm_timeout to 180s for heavy agents.

--- metadata ---
agent: ResearchAgent
error_type: APITimeoutError
duration_s: 185
fix_applied: true
pr_number: 1465
```

#### QUESTION message
```
[QUESTION] Which backend endpoint for stock briefs?

Found two candidates:
1. GET /v1/stocks/briefs/ — returns paginated briefs
2. GET /v1/intelligence/stock-briefs/ — returns last 50 with scores

Which should the mobile app use?

--- metadata ---
blocking: PR-15
options: 2
```

## Collaboration Workflow

### Standard PR Flow

```
1. User:        "Let's build [feature]"
2. User→PA:     "Design the [feature] spec"
3. PA:          Posts detailed spec (screens, API, types, UX)
4. Claude Code: [PLAN] message — what will be built
5. Claude Code: Verifies backend endpoints (research)
6. Claude Code: Builds implementation
7. Claude Code: [RESULT] message — PR created with summary
8. User:        "merge it"
9. Claude Code: [STATUS] Merged, deploying to Railway
```

### Error Recovery Flow

```
1. Claude Code: [ERROR] message — what failed
2. PA:          Analyzes error, suggests fix
3. Claude Code: [PLAN] message — proposed fix
4. User:        Approves or redirects
5. Claude Code: Implements fix
6. Claude Code: [RESULT] message — fix deployed
```

### Context Preservation

After every significant piece of work, Claude Code should:

1. **Post a [RESULT] to the shared conversation** — so PA has the context
2. **Update memory files** — `~/.claude/projects/.../memory/MEMORY.md`
3. **Commit docs if architectural** — ADR in `docs/decisions/` for major decisions

## ADR (Architecture Decision Record) Format

For significant architectural decisions, create `docs/decisions/ADR-NNNN-title.md`:

```markdown
# ADR-NNNN: Title

**Status**: Accepted | Superseded | Deprecated
**Date**: YYYY-MM-DD
**Context**: What situation prompted this decision?
**Decision**: What was decided?
**Alternatives**: What else was considered?
**Consequences**: What are the trade-offs?
```

## Security Rules

### Source Validation
- `source` field is recorded server-side from the authenticated request
- Claude Code must authenticate with a valid DRF Token
- The `source` value is trusted because it comes with authentication
- Frontend displays source badges but does not trust client-provided source for authorization

### Conversation Access
- Messages can only be posted to conversations owned by the authenticated user
- Claude Code uses the same user token, so it accesses the same conversations
- No cross-user conversation injection is possible

### Action Authorization
- Claude Code messages are **informational** — they report what was done
- PA messages are **advisory** — they suggest what to do
- Only **User** messages trigger sensitive actions (approvals, deployments, money movement)
- PA should never auto-execute destructive actions based solely on Claude Code messages

### Rate Limiting
- Claude Code posts are subject to the same API rate limits as other clients
- Recommended: max 10 messages per minute per conversation
- Bulk status updates should be consolidated into single messages

## Implementation Files

| File | Purpose |
|------|---------|
| `core/services/collaboration_protocol.py` | Python helper for posting structured messages |
| `core/views_personal_assistant.py` | PA chat endpoint with source handling |
| `core/models/conversations/models.py` | ChatConversation with source tracking |
| `frontend/src/pages/CommandCenterPage.tsx` | UI with source badges |
| `frontend/src/stores/paStore.ts` | Message store with source preservation |
| `docs/topics/collaboration-protocol.md` | This document |

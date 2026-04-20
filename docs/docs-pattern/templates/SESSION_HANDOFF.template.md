---
title: "Session <N> — <Headline>"
date: YYYY-MM-DD
status: complete
session: <N>
previous_handoff: ../SESSION_<N-1>_*.md
---

# Session <N> — <Headline>

## TL;DR

- **What shipped:** <PR # + one-line outcome>
- **What's blocking next:** <the one thing that matters tomorrow>
- **What's in a weird state:** <test artifacts, live canaries, half-disabled features>

---

## What Shipped

### <Area 1 — e.g. Backend>

- **PR #<N>:** <title>
  - <1–3 bullets — what changed, blast radius, test coverage>
  - <any relevant context — why this approach, what was rejected>

- **PR #<N+1>:** <title>
  - ...

### <Area 2 — e.g. Docs>

- <Files changed, why>

### <Area 3 — e.g. Infrastructure>

- <Config changes, env var flips, deploys>

---

## What Didn't (and Why)

<Blocked work, reversals, investigations that hit dead ends. This is often
the most valuable section for future sessions — it prevents repeating the
same dead-end.>

### <Dead-end / blocker 1>

- **Attempted:** <what you tried>
- **Why it didn't work:** <the specific reason>
- **Next attempt:** <what would be worth trying, if relevant>

### <Dead-end / blocker 2>

...

---

## Known Issues / Test Artifacts

<Anything intentionally left in a weird state — live canaries, disabled
features, pending cleanups, artifacts that should NOT be deleted yet.>

- **<Artifact ID>** — <why it exists, when it can be cleaned up>
- **<Feature flag>** — `FLAG=value` set until <condition>

---

## Rollback Criteria

<Only if the session shipped risky changes. What to watch for, how to revert.>

- **Trigger:** <error pattern, metric threshold, etc.>
- **Rollback steps:**
  1. <command or commit SHA to revert>
  2. <follow-up cleanup>

---

## Next Session Picks Up With

<1–3 specific items — file paths, PR numbers, commands to run first.>

1. **<Priority 1>** — <what, where, any gotchas>
2. **<Priority 2>** — <what, where>
3. **<Priority 3>** — <what, where>

---

## Rigby / PA / AI Context

- **Conversation ID:** `<conversation-id>` (if applicable)
- **State at end of session:** <what the AI knows, any cross-session threads>
- **How to resume:** `<command to resume conversation>`

---

## Cross-References

- Previous handoff: [`SESSION_<N-1>_*.md`](SESSION_<N-1>_*.md)
- Related topic docs:
  - [`docs/topics/<subsystem>.md`](../topics/<subsystem>.md)
- PRs: #<N>, #<N+1>, #<N+2>
- Relevant commits: `<sha>`, `<sha>`

---

*Written at end of session <date>. Do not edit after the next session begins.
If the next session finds a bug in this handoff's reasoning, add a note at
the bottom rather than rewriting — the original reasoning is history.*

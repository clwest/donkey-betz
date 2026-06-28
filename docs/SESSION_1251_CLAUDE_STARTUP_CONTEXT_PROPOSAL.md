---
title: "Session 1251 — Claude startup-context architecture proposal"
status: proposal
session: 1251
generated: 2026-06-28
companion_docs:
  - SESSION_1251_CAPABILITY_AUDIT.md
  - handoffs/SESSION_1251_CAPABILITY_AUDIT.md
  - CLAUDE.md
  - 00-START-NEXT-SESSION.md
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
---

# Claude Startup Context — Architecture Proposal

> **Status: proposal only.** Recommended but not implemented. The
> evaluation was requested at Session 1251 open in parallel with PR
> 12A (`rigby_shift_brief_tool`). The recommendation builds on PR
> 12A — it's the *next* place Rigby's operator responsibility can
> grow.

## §1 The problem

Every fresh Claude session today consumes ~4,000+ lines of hand-edited
markdown before producing any work output. The `context-kit orient`
flow pulls (in order):

| Doc | Size (lines) | Hand-edited? | Refresh cadence |
|---|---|---|---|
| `00-START-NEXT-SESSION.md` | ~3,970 | Yes | Every session close |
| `docs/PLATFORM_INVENTORY.md` | ~2,100 | Auto-generated | On demand (`generate_platform_inventory`) |
| `docs/PLATFORM_WHAT_IT_IS.md` | ~550 | Yes | Sporadic |
| Latest handoff | 200–500 | Yes | Every session close |
| `CLAUDE.md` | ~140 + live block | Mixed | Live block auto-refreshes; rest hand |
| `docs/KNOWLEDGE_PIPELINE.md` | ~450 | Yes | Rare |
| `docs/UDB_BEHAVIOR_LAYER.md` | ~190 | Yes | Rare |
| `docs/UDB_TRANSLATION_LAYER.md` | ~250 | Yes | Rare |
| `MEMORY.md` index | ~200 | Auto-managed | Per-feedback-add |

Claude must scan all of these before any work prompt becomes
actionable. Empirically (Session 1251 open), the orient + 2-doc read
took 9 tool calls and ~30k tokens of context just to load
"who-am-I-working-with-and-what's-the-priority-today."

## §2 What Claude actually needs every session

Triage of the above against "does Claude touch this in the first 5
minutes of work":

| Information | Needed every session? | Source today |
|---|---|---|
| **Today's priority + acceptance criteria** | ✅ Yes | `00-START-NEXT-SESSION.md` first 200 lines |
| **Pinned conversation_id + session health** | ✅ Yes | `00-START-NEXT-SESSION.md` trap blocks |
| **Live runtime counts (agents, spiders, tasks)** | ⚠️ Sometimes | CLAUDE.md live block (auto-generated) |
| **Operating guardrails (rigby-first, etc)** | ✅ Yes (selected subset) | `MEMORY.md` index → drilldowns |
| **The 3–5 most relevant memories for today's task** | ✅ Yes | `MEMORY.md` (manual scan today) |
| **Latest handoff TL;DR + carry-forward signals** | ✅ Yes | Latest handoff `§0 TL;DR` |
| **Subsystem narratives (PLATFORM_WHAT_IT_IS, KNOWLEDGE_PIPELINE)** | ❌ Rare | Read on demand |
| **Behavior + translation layers** | ❌ Rare | Read when persona switches |
| **Full inventory** | ❌ Rare | Read when asked for a specific count |
| **The 30 trap-reading blocks at the top of start-here** | ⚠️ Inconsistently | All loaded every session — actual use rate is maybe 10% |

**Conclusion:** roughly **80% of the ~4,000 lines is paid for and
never used.** It's loaded as insurance against an unlikely
information need.

## §3 What's duplicated

The orient bundle contains four classes of duplication:

1. **Counts mirrored across docs** — agent / spider / task counts
   appear in `CLAUDE.md` live block, `PLATFORM_INVENTORY.md`,
   `PLATFORM_WHAT_IT_IS.md` narrative body, and various
   per-subsystem topic docs. The live block is authoritative; the
   rest drift.
2. **Trap-reading blocks accreting at the top of start-here** —
   Sessions 1144, 1160, 1161, 1184, 1234, 1247 each added a
   "READ THIS FIRST/SECOND/THIRD" block. Today there are ten such
   blocks before "SESSION 1251 — CURRENT ENTRY POINT". The newest
   bury the oldest, but none are pruned.
3. **TL;DR repetition across handoffs** — every handoff opens with a
   `§0 TL;DR` that summarizes the same shape (PRs shipped, headline
   outcomes, headline tests). Sequentially reading the last three
   handoffs duplicates 60–70% of the framing each time.
4. **Memory index entries** — each memory has a one-line index entry
   plus a separate file. The index entry duplicates the file's
   `description` frontmatter field; total cost ~200 lines of
   loaded-every-session content where the per-task signal is the
   2–3 memories that match today's work.

## §4 What could become generated

Already auto-generated and working:
- `docs/PLATFORM_INVENTORY.md` (regenerable via
  `generate_platform_inventory`)
- `CLAUDE.md` live counts block (`refresh_doc_inventory_blocks`)
- `docs/INDEX.md` (`build_docs_index`)
- `docs/_provenance.json` (`build_docs_provenance`)
- Doc-claim drift (`verify_doc_claims --only-drift`)

Could be generated but is hand-edited today:
- **Today's priority + acceptance criteria** — already lives as
  `## SESSION NNNN — CURRENT ENTRY POINT` in start-here.
  Materializable as a single tight doc by close.
- **Recent activity 1-liner** — `recent_activity_tool` already
  returns the data; PR 12A's shift brief renders it.
- **Live session health** — `session_tool.health_check` already
  returns the data; PR 12A renders it.
- **Top-3 relevant memories for today's task** — RAG over
  `MEMORY.md` indexed memories + an LLM filter against the
  start-here `## FIRST THING` text. ~5s once per session.

Cannot easily be generated:
- Voice / collaboration rules (subjective)
- Architectural intent of past decisions (not in code)
- Carry-forward from previous session (Rigby could draft, human edits)

## §5 The proposed shape: `CLAUDE_SESSION_CONTEXT.md`

A single ~200-line doc, regenerated every morning by a Celery beat
task (or on demand by Rigby), bundling:

```markdown
---
generated: 2026-06-29 12:00:00Z
session_predicted: 1252
generator: rigby_session_context_builder
ttl_hours: 24
---

# Session Context — 2026-06-29

## Today's priority (from open handoff)
{{first_thing from 00-START-NEXT-SESSION.md ## CURRENT ENTRY POINT}}

## Active session
- Pin: pa-{{conversation_id}}
- Health: {{score}}/100 — {{recommendation}}
- Last fresh: {{create_fresh_at}}

## Live counts (auto)
| Component | Count |
|---|---|
{{CLAUDE.md live block, verbatim}}

## What changed yesterday
{{shift_brief.what_changed section, verbatim}}

## Active risks
{{shift_brief.active_risks section, verbatim}}

## Most relevant memories for today's task
{{top 3 memory entries by relevance to "today's priority" string}}

## Operating guardrails (hot subset)
- {{rigby-first comms — memory verbatim}}
- {{Claude-directs-Rigby-executes-Claude-verifies — memory verbatim}}
- {{relevant for today's PR domain — selected via task tags}}

## Pointers (don't load unless needed)
- Full inventory: docs/PLATFORM_INVENTORY.md
- Narrative: docs/PLATFORM_WHAT_IT_IS.md
- Subsystem topic docs: docs/topics/{{matched_topic}}.md
- Full handoff: docs/handoffs/SESSION_{{N-1}}_*.md
```

Claude's `context-kit orient` flow then collapses to:

1. Read `CLAUDE_SESSION_CONTEXT.md` (~200 lines, fully curated).
2. Read `00-START-NEXT-SESSION.md` only if the context doc is stale
   (mtime > 24h) or signals an unfamiliar situation.
3. Drill into any pointer doc only when the active task needs it.

**Cost reduction:** ~4,000 lines of loaded markdown drops to ~200 +
on-demand drilldowns. Roughly 95% of the orient cost.

## §6 Could Rigby become the curator?

Yes — naturally. The data Rigby already has in PR 12A's shift brief
is 70% of what `CLAUDE_SESSION_CONTEXT.md` needs:

| Context doc section | Source in PR 12A shift brief | New work for Rigby |
|---|---|---|
| Today's priority | `top_priority` | Re-render from handoff `## FIRST THING` |
| Active session | `session_health` sub-tool | Read pin from PA conversation table |
| Live counts | Already in `CLAUDE.md` live block | Read directly from inventory generator |
| What changed | `what_changed` section | Re-render |
| Active risks | `active_risks` section | Re-render |
| Top-3 memories | NEW | RAG over MEMORY.md vs `top_priority` string |
| Operating guardrails | Static base + dynamic from MEMORY.md | Static + RAG-filtered |
| Pointers | Static | Static |

**What Rigby would need that doesn't exist today:**

1. A way to read `00-START-NEXT-SESSION.md` and extract the most
   recent `## SESSION NNNN — CURRENT ENTRY POINT` block — string
   slicing of the start-here file.
2. A way to RAG-query `MEMORY.md` against a task-string. Already
   exists: `kb_tool` + `search_docs` can index memory files. Needs a
   ranker on top.
3. A `docs/CLAUDE_SESSION_CONTEXT.md` write target that's safe to
   overwrite each morning — same `<!-- DOC-AUTOGEN -->` convention
   as `docs/INDEX.md`.
4. A beat task `generate_session_context_daily` @ 04:00 Denver
   (between docs cascade refresh at 04:00 and shift brief at ~06:30).

All four are 1–3 hour PRs each. Total scope: roughly the same effort
as PR 12A itself.

## §7 Recommendation

**Adopt this proposal as PR 14** (after PR 12A validates manually
and PR 12B schedules the beat task).

**Defer until after PR 12A is validated in production.** The shift
brief is the operator-capability proof point that motivates this
architecture. If the shift brief doesn't end up being something Chris
actually reads daily, then this whole curated-context layer doesn't
have an audience either. **Don't build the second layer until the
first one proves its read-rate.**

**Phasing if approved:**

- **PR 14A** — Extract "today's priority" from start-here into a
  one-section helper. ~1 hour. Pure string slicing.
- **PR 14B** — Implement `rigby_session_context_builder` service +
  PA tool. ~3 hours. Reuses 60% of PR 12A's helper code.
- **PR 14C** — Add memory RAG ranker (against MEMORY.md entries
  vs today's priority text). ~2 hours.
- **PR 14D** — Beat task scheduling + Claude's `context-kit orient`
  refactor to read the context doc first. ~2 hours.

Total: ~8 hours of work, replaces ~95% of every-session orient cost.

## §8 Anti-recommendations

**Don't** turn `CLAUDE_SESSION_CONTEXT.md` into a Markdown blob that
swallows everything. The whole point is curation — a doc that
contains "everything you might need" is just `00-START-NEXT-SESSION.md`
under a new name. Hard caps:

- ≤ 200 lines total
- ≤ 50 lines per section
- Pointers (not inlined content) for anything that's already a
  searchable doc

**Don't** auto-implement the user's behavioral preferences. Rigby
RAG-filters memories *for relevance*; she does not invent new
operating rules. The curator role is editorial, not authorial.

**Don't** delete the existing orient flow. Keep `context-kit orient`
as the deep-dive entry point. The new context doc is the daily fast
path, not a replacement.

---

*This is a proposal, not a plan. PR 14A–D are sized estimates, not
commitments. The actual go/no-go decision belongs to Chris after PR
12A's shift brief proves it has daily readership.*

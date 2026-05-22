---
title: "Handoff numbering gaps — intentional jumps"
status: active
last_updated: 2026-05-22
---

# Handoff numbering — known gaps

`context-kit doctor` warns when `docs/handoffs/SESSION_*.md` is missing
numbered files in a continuous range. Some of those gaps are real (a
session shipped but no handoff was written); some are intentional
renumbers from earlier in the project's history. This file documents
the **intentional** gaps so the doctor warning can be triaged at a
glance instead of treated as a backlog item.

## Gap: SESSION_198 → SESSION_205 (8 missing)

- **Last filed before gap:** `SESSION_197_UI_CONSOLIDATION_PLAN.md`
- **First filed after gap:** `SESSION_206_DASHBOARDS_SPIDERS_FEATURES.md`
- **Status:** intentional. Numbering jumped after the UI consolidation
  arc closed; the next batch of work was bundled and renumbered to
  start a fresh sub-arc. No work was lost — the build progression
  continues in commit history (`git log --since=...` around the
  renumber boundary). Backfilling would require reconstructing
  retroactive handoffs from commits, which is more noise than signal
  this far back.
- **Action:** none. Treat doctor's continuity warning for this range as
  acknowledged.

## Adding to this file

When a future session writes a handoff that creates a new numbering
discontinuity, add it here with the same three fields (last before,
first after, status + action). If the gap is *unintentional*
(handoff genuinely missing from a session that did ship work),
backfill it from CHANGELOG.md + git log rather than logging it here.

## Why this file exists rather than backfilling

The doctor heuristic is right to flag gaps — they usually indicate
missing handoffs. But this project predates the doctor and accreted
some renumbering decisions before the continuity rule was on. This
file is the escape hatch: a single place to record "yes, we know,
and here's why." It keeps `context-kit doctor` warnings actionable
without erasing project history.

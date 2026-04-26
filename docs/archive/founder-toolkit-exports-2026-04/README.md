# Founder Toolkit Exports (April 2026)

**Archived on:** 2026-04-26
**Original location:** `/_recovered_founder_docs/` (repo root, untracked)
**Date stamp on files:** April 22, 2026
**Purpose:** Filesystem backup of Founder Toolkit `Deliverable` rows from the
**local** PostgreSQL database. Committed to GitHub as a durable safety net
since the local DB is the only canonical store today (no managed backup).

## Why this exists

These markdown files are **byte-for-byte exports** of `Deliverable` rows
created during the Founder Toolkit MVP work (April 6, 2026 — see
`memory/project_founder_toolkit.md` and `project_founder_toolkit_crossapp.md`
for the build context). The files appeared at the repo root with a
`_recovered_` prefix on April 22, 2026, suggesting an export/recovery
operation around that date.

Verification (Session 1100, 2026-04-26):

| File | DB Deliverable ID | Body bytes match? |
|---|---|---|
| `PitchDeckForge/PitchDeckForge — Full Business Plan.md` | `899fefec-0146-43ad-93fa-a770d8936236` | ✓ identical |
| `PitchDeckForge/INIT-PitchDeckForge-Build.md` | `07eacdf5-9788-45c3-9bc7-eb9c9c29c565` | ✓ |
| `DealFlowTracker/DealFlowTracker — Full Business Plan (Investor-Ready).md` | `778c72e8-ac5a-44c5-bc3a-449bcbed54b4` | ✓ |
| `MentorForge/MentorForge — Investor-ready Business Plan.md` | `76421180-37cc-476e-98ac-5a648075e863` | ✓ |
| `MentorForge/Workspace Index — MentorForge.md` | `45b3d67c-a37c-428f-afcc-3e810ba7d9af` | ✓ |
| `MentorForge/MentorForge — Full Business Plan (Investor-Ready).md` | `b3e317d6-a411-45f9-bb65-7ed226bdca3f` | ✓ |
| `PitchDeckForge/Landing Copy — Hero + 3 Benefits.md` | matched by title | ✓ |
| `PitchDeckForge/Pilot One-Pager.md` | matched by title | ✓ |
| `PitchDeckForge/Pricing Tiers — Free-Pro-Enterprise.md` | matched by title | ✓ |
| `PitchDeckForge/README — 2-minute Quick Start.md` | matched by title | ✓ |
| `PitchDeckForge/env.example.md` | matched by title (`.env.example`) | ✓ |

The files include a small workspace-metadata header line (`Workspace: ... ·
ID: ... · Created: ... · Updated: ...`) before the body — that's the only
content difference from the DB rows.

## Apps covered

- **PitchDeckForge** — AI-powered investor-ready pitch decks
- **DealFlowTracker** — Deal pipeline tracking for founders/VCs
- **MentorForge** — Mentor-matching/coaching platform

## How to restore

If the local DB ever loses these rows, the canonical content is here. To
re-import, parse each file (strip the workspace-metadata header) and create
a new `Deliverable` row with the body content. Or just read the markdown —
it's directly usable as-is.

## Provenance for later

Per Chris's never-delete-docs rule and the "how I learned to work with AI"
book framing, these are kept as artifacts of the Founder Toolkit MVP build
session and as a redundant backup against local-DB loss.

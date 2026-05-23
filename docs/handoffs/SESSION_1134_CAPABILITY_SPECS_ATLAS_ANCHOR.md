---
title: "Session 1134 — Fleet Capability spec drafts + Rigby grounding + Atlas anchor"
date: 2026-05-23
status: active
session: 1134
previous_handoff: SESSION_1133_FLEET_PA_SIGNING_BACKPROP.md
next_session_primary: app-by-app discovery + GTM build with Rigby (Session 1135)
---

# Session 1134 — Capability specs drafted, grounded, Atlas-anchored

> **Read this if** you want to know how the "capability bundle"
> idea moved from one-line ask → 2 specs → Rigby grounding pass →
> Atlas reality check → v3 anchored drafts, OR what the next
> session's app-by-app discovery sprint is set up to do.

## TL;DR

Session 1134 was a **spec + grounding** session, not an
implementation session. Three documents shipped to
`docs/specs/`:

| Doc | Purpose | Status |
|---|---|---|
| `FLEET_CAPABILITY_MANIFEST_SPEC.md` (v3) | Engineering spec for per-app authz across agents/spiders/beat tasks/PA tools/spokespersons | Atlas-anchored draft |
| `FLEET_CAPABILITY_BUSINESS_SPEC.md` (v3) | Plain-English GTM framing of the same proposal | Atlas-anchored draft |
| (this handoff) | Session record + Session 1135 primer | — |

**Headline outcome**: the spec went through three reshapes —
v1 (initial draft) → v2 (Rigby's review locks + 5th spokesperson
axis) → v3 (β-anchored to App Atlas reality after Rigby's
grounding pass showed v2 framing was ahead of Atlas Phase 1).

**Critical grounding finding** (from Rigby's pass): of the 7 fleet
apps, only 3 have actively-developed product surfaces
(signal-studio = flagship vertical per Atlas; contract-concierge =
Draft Library demo; Rigby itself emerging as Phase 1 flagship at
`app.247globalai.com`). The other 4 (mentorforge, pitchdeckforge,
sellerpilot, dealflowtracker, compliancesentinel) have HMAC
identity + plumbing but **no documented product intent**. Their
routing allowlists "could be name-extrapolated" — they fit the
slug name but if real intent is different they miss it entirely.

**Next session priority** (Chris's directive): "you and Rigby
begin a new session where you guys go through the apps and you
tell me what we can do with it… research everything, and create
a business that has everything I need to start marketing it and
you guys can build out anything missing."

## What landed (this session)

### Three sequential spec versions

**v1 — Initial drafts** (early session). I sketched
both specs based on the 4 fleet primitives (agents, spiders,
beat tasks, PA tools) extending the existing
`fleet_agent_routing.json` v1 pattern.

**v2 — Rigby's locks + persona axis**. Rigby reviewed and pushed
3 architectural changes plus a new axis:

1. Split top-level into `routing` + `capabilities` blocks (even
   though same file) — prevents routing PRs becoming capability
   PRs.
2. PA tools need verb-level perms (tool + allowed actions), not
   tool-name-only (`content_tool` is too coarse).
3. Beat tasks use explicit verbs `{"read", "run"}`, not separate
   `allow`/`force_run` arrays.

Chris then raised: the design misses Character OS / spokesperson
/ Ads — vital to bringing the Suite together. Rigby's read: **(3)
hybrid** — make "who can request which persona/modality" a 5th
manifest axis (`spokespersons`), keep "what they're allowed to say"
in `UDB_BEHAVIOR_LAYER.md` + Character OS policy templates.
Personas are global IDs owned by CO; per-app axis is selection
rights, not persona definitions. u-d-b authorizes + logs; CO
executes.

v2 absorbed all four changes.

**v3 — Atlas anchor (β option)**. Chris flagged a real risk:
Rigby's spec review might be downstream of app-name-implied
semantics, not actual product intent. Rigby ran a **grounding
pass** against u-d-b artifacts (config, handoffs 1116/1126-1133,
App Atlas v1) and produced per-app Known/Guessing/Need-from-Chris
lists. The grounding surfaced:

- **App Atlas v1** says Phase 1 is **Rigby standalone at
  `app.247globalai.com` for $20-30/mo**. Sibling apps marked
  "Standalone sibling apps — defer."
- **Only Signal Studio is named as flagship vertical** in Atlas.
- **Contract Concierge has the 1129 Draft Library** demo
  end-to-end shipped.
- **The other 5 sibling apps** have identity + plumbing but no
  documented product intent. Routing allowlists for them are
  potentially name-extrapolated.
- **Character OS / spokesperson** is Atlas Phase 4+, **parked**
  until paying customer demand.
- **Compliancesentinel** is effectively disabled (`default=null`,
  `allowlist=[]`).

Both specs reshaped to v3 (Atlas-anchored): kept the 5-axis design
target, but scoped near-term implementation to **signal-studio +
contract-concierge only**; deferred apps re-enter the manifest
when their intent is documented; spokesperson axis stays as
future-state design with no near-term work.

### Files modified

```
docs/specs/FLEET_CAPABILITY_MANIFEST_SPEC.md      # v3 Atlas-anchored
docs/specs/FLEET_CAPABILITY_BUSINESS_SPEC.md      # v3 Atlas-anchored
docs/handoffs/SESSION_1134_CAPABILITY_SPECS_ATLAS_ANCHOR.md  # this file
```

No code changes. No migrations. No PRs.

### PA-chat conversations consumed

All via `pa-d19c1674b936` (donkeyking conversation; LOCAL service
context confirmed). Six round-trips total:

1. Initial v1 review → Rigby's 3 schema locks + sequencing answers
2. v2 review continuation (audit retention + drift policy + tier-axis correction + (B) recommendation)
3. Persona-axis architecture read → Rigby's (3) hybrid recommendation
4. Spec reshape to v2 → confirmation
5. Grounding pass instructions → Rigby pulled handoffs 1116-1133 + Atlas v1 → per-app Known/Guessing/Need
6. (No further PA call — Atlas anchor decision came from Chris directly, v3 reshape executed without re-review)

## What's queued for Session 1135 — Chris's directive

> *"After everything is anchored I want you and Rigby to begin a
> new session where you guys go through the apps and you tell me
> what we can do with it. I know it's crazy but I want to see if
> you and Rigby can research everything, and create a business
> that has everything I need to start marketing it and you guys
> can build out anything missing."*

### Session 1135 primary task — app-by-app discovery sprint

For each of the 7 fleet apps (and Rigby standalone as an 8th
surface), produce:

1. **What it is**: actual product intent, not name-implied —
   Chris fills the gap or confirms current assumption.
2. **Who buys it**: primary user + buyer (often same, sometimes
   different).
3. **What's built**: real shipping evidence (UI, API, workflows,
   artifacts).
4. **What proves it's real**: one screenshot / API path / demo
   step / curl invocation that backs item 3. Forces artifact-
   backed evidence, not narrative. (Rigby's lock from 1134 close
   confirmation pass.)
5. **What's missing**: the gap between "current shipping
   evidence" and "could sell this for real."
6. **Buildable in one sprint?**: small / medium / large / blocked.
7. **GTM sketch**: where customers find it, how they buy, what
   they pay, what they get.
8. **Spokesperson alignment** (future-state): if/when Phase 4+
   activates, which persona + modality fits this app.

### Order of attack (per Atlas precedence)

1. **Rigby standalone** (Atlas Phase 1 flagship — this is the
   one that actually ships next).
2. **Signal Studio** (Atlas flagship vertical — most product
   surface built among siblings).
3. **Contract Concierge** (Suite candidate — Draft Library
   shipped).
4. **MentorForge / PitchDeckForge / SellerPilot / DealFlowTracker
   / ComplianceSentinel** in order of Chris's intent priority
   (he picks).

### Rigby's "Need from Chris" list (from grounding pass)

Per Rigby's Part 4/4 grounding output, the per-app questions to
work through Session 1135:

**Global categories** (answer once, applies to all):
1. Intended user + buyer
2. Core workflow(s) + output artifacts
3. Execution posture (analysis-only vs allowed to execute)
4. Data posture (needs spiders? freshness expectations?)
5. Scope boundaries / cross-app calls
6. Brand voice + spokesperson alignment
7. Tier-cut intuition (which dimension defines upgrades?)
8. Status classification (flagship / core SKU / cross-sell /
   internal / parked)

**Per-app specific questions**: documented in the engineering
spec v3 §7 (Primary blocker — fill in next session).

### Deliverables Session 1135 should produce

- Per-app brief (1 doc per app, `docs/apps/<slug>_BRIEF.md`):
  intent, user, built, missing, build size, GTM sketch.
- Synthesis: which app to push to v1 first (after Rigby
  standalone Phase 1).
- Manifest entries for the 2 active sibling apps (signal-studio,
  contract-concierge) populated in `config/fleet_agent_routing.json`
  to validate the v3 schema works in practice.
- "Build list" of anything missing — small concrete tickets that
  can ship in subsequent sessions.
- Updated 5-year-old assumptions in the business spec's
  illustrative pricing where discovery contradicts them.

### Out-of-scope for Session 1135

- Implementing the capability bundle (Phase 0 of engineering
  spec) — that comes AFTER Session 1135 + 1134 (Y) reject-mode
  flip.
- **No manifest enforcement flips beyond warn-only** during 1135
  unless Chris explicitly asks. Keeps discovery from accidentally
  becoming enforcement work. (Rigby's lock from 1134 close
  confirmation pass.)
- Character OS / spokesperson work — Atlas says Phase 4+, parked.
- New fleet app slugs — work with the 7 + Rigby that exist.
- Marketing copy beyond GTM sketches — that's a follow-on session
  once intent is locked.

## Carryover from 1133 still open

- **1134 (Y) reject-mode flip on `/api/pa/chat/`**. The original
  Session 1134 candidate. Still queued; gated on ≥3 days clean
  audit telemetry. Lives independent of the capability spec
  work. Should ship in parallel with Session 1135 discovery,
  not blocked by it.
- **1134 (A) action-card pre-gen**. The alternative visible-
  progress option from 1133. Still queued.
- Spec drafts await Phase 0 scaffolding implementation — but
  per v3 anchor, Phase 0 waits for Session 1135's discovery to
  populate the 2 active apps' allowlists with real intent.

## Operational notes

- All work this session local-only (per project memory rule).
  No commits to main, no PRs opened.
- PA-chat conversation `pa-d19c1674b936` is the active thread;
  donkeyking-owned per Session 1098 fix.
- `tools/pa_local.sh` worked clean throughout.
- 6 PA call round-trips, ~12k tokens consumed approximately.
  No errors, no rate-limit hits.

## Source-of-truth pointers (for Session 1135 entry)

- **App Atlas**: `docs/24_7_GLOBAL_AI_APP_ATLAS.md` — Phase 1
  defines what's shipping (Rigby standalone); Phase 2-3 defines
  when sibling apps unpark; Phase 4+ defines spokesperson.
- **Capability spec (eng)**: `docs/specs/FLEET_CAPABILITY_MANIFEST_SPEC.md`
  v3.
- **Capability spec (biz)**: `docs/specs/FLEET_CAPABILITY_BUSINESS_SPEC.md`
  v3.
- **Fleet routing config**: `config/fleet_agent_routing.json`
  (current state: v1 schema, agent allowlists per app).
- **Rigby's grounding evidence** (verbatim, this session's PA
  thread): conversation `pa-d19c1674b936`, search "grounding"
  for the 4-part deliverable.

---

**End Session 1134.** Session 1135 entry primed in
`00-START-NEXT-SESSION.md`.

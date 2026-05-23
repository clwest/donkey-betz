---
title: "Fleet Capability Manifest — per-app authz on agents, spiders, beat tasks, PA tools, spokespersons"
status: draft
version: v3 (Atlas-anchored)
session: 1134-pre
generated: 2026-05-23
last_reviewed: 2026-05-23 (β-anchor: scoped to App Atlas v1 reality)
author: claude + rigby (grounding pass)
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md       # strategy anchor — defines what's Phase 1 vs Phase 2-3 vs Phase 4+
  - specs/FLEET_MOVE_1_AND_2_SPEC.md
  - specs/FLEET_MOVE_2_ROUND_2_SPEC.md
  - UDB_BEHAVIOR_LAYER.md             # owns "what the persona says about this app"
  - UDB_TRANSLATION_LAYER.md          # the business spec twin lives in this layer's audience contract
related_runtime:
  - config/fleet_agent_routing.json
  - core/services/fleet_routing.py
  - core/models/fleet.py
external_boundaries:
  - character-os                      # owns persona registry + render execution; per Atlas, Phase 4+ — NEVER edited from u-d-b sessions
---

# Fleet Capability Manifest — Spec (draft v3, β-anchored to Atlas)

> **What changed in v3.** v1-v2 framed this spec as if all 7 fleet
> apps were active SKUs. Rigby's grounding pass (2026-05-23) showed
> that's not what the App Atlas says: Phase 1 is **Rigby standalone
> at `app.247globalai.com` ($20-30/mo)**; only signal-studio (flagship
> vertical) and contract-concierge (Draft Library demo) are
> actively-developed sibling surfaces. The other 4 fleet apps
> (mentorforge, pitchdeckforge, sellerpilot, dealflowtracker,
> compliancesentinel) are explicitly **deferred** per Atlas
> ("Standalone sibling apps — defer"). Character OS / spokesperson
> work is **Phase 4+, parked** until a paying customer demands it.
>
> **v3 keeps the 5-axis design target** but explicitly scopes
> *near-term implementation* to the active surfaces. The spec
> remains the eventual shape; what changes is the rollout footprint.

## 0. TL;DR (v3)

The 5-axis manifest design from v2 is correct — it is the right
shape for *when* u-d-b's per-app authz becomes the load-bearing
control plane for the Suite.

**What's near-term real:**

| Surface | Atlas status | Manifest near-term scope |
|---|---|---|
| **Rigby standalone** (`app.247globalai.com`) | Phase 1 flagship | NOT a fleet app today — emerges from u-d-b's core PA path; manifest applies only if/when "rigby" gets its own `app_slug` identity |
| **signal-studio** | Flagship vertical | Fully scoped — already has pull endpoint + curator agent + SSE refresh + `force_allowed: true` |
| **contract-concierge** | Suite candidate (Draft Library shipped) | Fully scoped — `legal_doc_drafter_agent` allowlist + `force_allowed: true` + artifact pipeline |
| mentorforge | Atlas: defer | Identity provisioned (Session 1133); product intent gap |
| pitchdeckforge | Atlas: defer | Identity provisioned; product intent gap |
| sellerpilot | Atlas: defer | Identity provisioned; product intent gap |
| dealflowtracker | Atlas: defer | Identity provisioned; product intent gap |
| compliancesentinel | Atlas: defer | Identity provisioned; routing `default=null`, `allowlist=[]` — effectively disabled |

**The 4 deferred apps re-enter the manifest** when their product
intent is documented (next session's discovery work will produce
this). Until then, their manifest entries stay empty — manifest
absence = no fleet capability claim, not "denied" or "broken."

**The spokesperson axis stays as a future-state design** with no
near-term implementation. It activates only when (a) a paying
customer demands persona-narrated output AND (b) Character OS
unparks per Atlas Phase 4 trigger.

**Roll-out** continues to mirror the PA-chat audit pattern
(Sessions 1132-1133): warn-only audit → ≥3 days clean → reject
flip per axis. But the *targets* are now signal-studio +
contract-concierge first, not all 7 apps simultaneously.

---

## 1. Why this exists

### 1.1 Problem (Atlas-anchored)

A fleet app today can request *any* AGENT_MAP agent in a routing
block, and `fleet_routing.resolve()` will honor the request only
if it's in that app's `allowlists` entry — good. But:

- **PA tools** have no per-app scope. The full 103-schema set is
  exposed to the GPT-5.2 function-calling loop regardless of the
  originating app. (Rigby's review: tool-name-only is too coarse —
  `content_tool` covers both search and publish; we need
  verb-level perms.)
- **Spiders** have no per-app scope. A PA tool call from any fleet
  app could trigger any of the 80 spiders if the wrapping tool is
  invokable.
- **Beat tasks** have no per-app scope. Any task triggerable via
  PA tool can be invoked by any fleet caller. `read` vs `run`
  need to be distinct verbs.
- **Spokespersons (Character OS personas)** are aspirational — no
  current render path is wired through fleet calls. When that
  changes (Phase 4+), per-app scoping prevents the "any app can
  request any persona" failure mode.

The near-term application of all of the above is **signal-studio
and contract-concierge** — the two sibling apps with documented
product intent and live traffic. The other 4 sibling apps are
deferred per Atlas; their manifest entries stay empty until
their intent is documented.

### 1.2 Why now (re-framed)

Don't do this *before* 1134 (Y) reject-mode flip — that one is
gated on telemetry already collected, costs almost nothing to
ship, and materially tightens the auth surface.

**v3 sequencing per Atlas reality:**

1. **1134 (Y) reject-mode flip** on `/api/pa/chat/` — identity
   truth gate.
2. **Optional: 1134 (A) action-card pre-gen** for visible
   progress while audit telemetry accrues.
3. **App discovery + intent capture** (the *next* session per
   Chris) — fills the per-app gap that blocks manifest scope.
4. **Phase 0 manifest scaffolding** for signal-studio +
   contract-concierge (the apps with documented intent).
5. **Phase 1 warn-only audit** — but only for the 2 active apps.
6. **Phase 2 reject flips per axis** — same 2 apps.
7. **Deferred apps re-enter** as their intent gets documented and
   they unpark per Atlas Phase 2-3 trigger.
8. **Spokespersons axis** activates only at Atlas Phase 4+ trigger.

Per Rigby's lock: "capability bundles only have teeth if fleet
identity is enforced." Step 1 stays the gate.

### 1.3 Why file-based, not admin UI (unchanged from v2)

Two reasons:

1. **Diffability.** `fleet_agent_routing.json` lives in git and
   PRs show readable diffs. A capability change is reviewable as
   code, not a click-trail in `/admin/`.
2. **Boot-time correctness.** A file-based manifest validated at
   process start (or in CI) can fail when the manifest references
   a non-existent agent/spider/task/tool/persona.

The escape hatch (kill-switch override per identity at runtime)
is preserved via `FleetServiceIdentity.capabilities` (line 92 in
`core/models/fleet.py`).

---

## 2. Schema (unchanged from v2 — this is the design target)

### 2.1 File location + shape

Extend the existing `config/fleet_agent_routing.json` rather than
add a parallel file. Top-level structure splits explicitly into
two blocks (Rigby's lock #1): `routing` and `capabilities`. This
prevents "routing PRs" from accidentally becoming "capability
PRs" and vice versa even though they share a file.

```jsonc
{
  "_meta": {
    "purpose": "Fleet app capability manifest — see docs/specs/FLEET_CAPABILITY_MANIFEST_SPEC.md",
    "schema_version": 2
  },

  // 2.1.a — ROUTING (which agent should answer)
  "routing": {
    "defaults":      { /* per-app default agent */ },
    "roles":         { /* role → agent indirection */ },
    "allowlists":    { /* per-app agent allowlist (the existing v1 surface) */ },
    "force_allowed": { /* per-app force-routing flag */ }
  },

  // 2.1.b — CAPABILITIES (what can this app do)
  "capabilities": {

    // Verb-level perms (Rigby lock #2): tool name → allowed actions
    "pa_tools": {
      "<app_slug>": {
        "allow":   {
          "content_tool":    ["content_search", "deliverable_list"],
          "newsletter_tool": ["outline", "validate"]
        },
        "default": "deny"
      }
    },

    "spiders": {
      "<app_slug>": {
        "allow":   ["<spider_name>", ...],
        "default": "deny"
      }
    },

    // Verb-level perms (Rigby lock #3): task name → verbs ⊆ {"read", "run"}
    "beat_tasks": {
      "<app_slug>": {
        "allow":   { "<task_name>": ["read", "run"] },
        "default": "deny"
      }
    },

    // 5th axis (FUTURE — Phase 4+ per Atlas, parked until customer demand)
    "spokespersons": {
      "<app_slug>": {
        "allow":   { "<persona_id>": ["<modality>", ...] },
        // modalities: "tts_video" (HeyGen/D-ID), "talking_head", "conversational" (Runway gwm1)
        "default": "deny"
      }
    }
  }
}
```

**v3 scope clarification:** the schema above is the **eventual
shape**. Phase 0 scaffolding populates only `routing.*` +
`capabilities.pa_tools` + `capabilities.spiders` +
`capabilities.beat_tasks` for the 2 active sibling apps
(signal-studio, contract-concierge). The `capabilities.spokespersons`
block ships as an empty object — schema present, no app entries.

Per-axis design notes (unchanged from v2):

- **`default: "deny"`** is the only supported value at v2 (Rigby's
  lock).
- **PA tools are verb-level.** Tool-name only is too coarse.
- **Beat tasks are verb-level too.** `["read"]` = observe;
  `["run"]` = trigger.
- **Spokespersons require a modality.** Future capability.

### 2.2 Identity-level overrides (runtime kill-switch — unchanged)

`FleetServiceIdentity.capabilities` (already exists, JSON field)
gets a new shape mirroring the manifest:

```jsonc
{
  "capability_overrides": {
    "agents":        { "deny": ["<agent_name>"],                        "allow": ["<agent_name>"] },
    "spiders":       { "deny": ["<spider_name>"],                       "allow": ["<spider_name>"] },
    "pa_tools":      { "deny": { "<tool>": ["<action>"] },              "allow": { "<tool>": ["<action>"] } },
    "beat_tasks":    { "deny": { "<task>": ["read", "run"] },           "allow": { "<task>": ["read", "run"] } },
    "spokespersons": { "deny": { "<persona_id>": ["<modality>"] },      "allow": { "<persona_id>": ["<modality>"] } }
  }
}
```

Precedence: deny > allow > file manifest > `default: "deny"`.

---

## 3. Enforcement points (unchanged structure; near-term scope reduced)

For each axis, *where* in the code the check happens. All five
reuse the same `request.fleet_identity` already populated by
`FleetSignatureAuthentication` (Move 1, Session 1129).

### 3.1 Agents

**Already enforced** in `core/services/fleet_routing.resolve()`.
v3 work: extend the function to read the new
`routing.allowlists` location (with back-compat shim for the
legacy top-level `allowlists`) and to consult
`capability_overrides.agents` from `FleetServiceIdentity`.

### 3.2 PA tools

Filter the function-calling loop's tool schema list by
`pa_tools.<app_slug>.allow[<tool_name>]`. Defense-in-depth:
`tool_dispatcher.dispatch()` re-checks `(tool, action)`.

**Near-term scope**: signal-studio + contract-concierge only.

### 3.3 Spiders

`allow_spider(identity, spider_name) -> bool` in new
`core/services/fleet_capability.py`. PA tool handlers that
invoke spiders consult it first.

**Near-term scope**: signal-studio + contract-concierge only.

### 3.4 Beat tasks

`allow_beat_task(identity, task_name, verb)` where
`verb ∈ {"read", "run"}`.

**Near-term scope**: signal-studio + contract-concierge only.

### 3.5 Spokespersons (FUTURE — Phase 4+ per Atlas)

> **Status:** design recorded; no near-term implementation.
> Activates only when (a) a paying customer demands
> persona-narrated output AND (b) Character OS unparks per
> Atlas Phase 4+ trigger.

When it does activate, the design is unchanged from v2:

- The manifest controls **selection rights** (authz).
- *What the persona says* lives in `UDB_BEHAVIOR_LAYER.md` +
  Character OS policy templates keyed by
  `(app_slug, persona_id, modality)`.
- Personas are **global IDs** owned by Character OS.
- u-d-b emits a render event:
  ```
  render_request{
    app_slug, persona_id, modality,
    script_ref, constraints_ref,
    request_id, fleet_signature
  }
  ```
- Character OS executes; u-d-b authorizes + logs only.
- Modality-specific guardrails for `conversational` (Runway) per
  the saved memory on tool-description-vs-narration.

**Cross-repo coordination note**: per project rule, Character OS
has its own active CC session; this spec records the future-state
design but does NOT prescribe work in the CO repo. When Phase 4+
trigger fires, both repos coordinate on the persona registry
contract (§4.1).

### 3.6 NOT enforced here (unchanged)

"What the persona says about this app" — claim provenance, brand
voice, disclosure rules. Those live in `UDB_BEHAVIOR_LAYER.md` +
CO policy templates. The manifest is the *gate*; behavior+CO
are the *contents*.

---

## 4. Inventory grounding (drift prevention)

Add `python manage.py validate_fleet_capability_manifest` that:

1. Loads `config/fleet_agent_routing.json`.
2. For each app's `routing.allowlists` (agents), confirms every
   entry exists in `AGENT_MAP`.
3. For each app's `capabilities.pa_tools.allow`, confirms every
   `(tool, action)` pair exists in `pa_tool_schemas.py`.
4. For each app's `capabilities.spiders.allow`, confirms every
   entry exists in the spider registry (`ai_core/spiders/`).
5. For each app's `capabilities.beat_tasks.allow`, confirms every
   task exists in `PeriodicTask` rows and every verb is in
   `{"read", "run"}`.
6. For each app's `capabilities.spokespersons.allow` (when
   populated post-Phase-4), confirms every `persona_id` exists in
   Character OS's published persona registry.
7. For each `FleetServiceIdentity.capabilities.capability_overrides.*`,
   same checks.

**Policy ladder** (Rigby's lock on Q7):
- **Fail CI** (always) — invalid manifest blocks merge.
- **Fail-at-startup** when `STRICT_MANIFEST=1`.
- **Warn-at-deploy** as optional sugar.

**v3 implementation note**: the validator runs from the start of
Phase 0. The `spokespersons` axis path is implemented but skips
validation when the section is empty (which is its expected state
until Phase 4+).

### 4.1 Character OS persona registry (deferred to Phase 4+)

The persona-registry mirror contract (§4.1 in v2 — file mirror vs
API lookup) is deferred. It only matters when the spokespersons
axis activates. Recorded here so the design is captured.

---

## 5. Rollout plan (re-anchored to Atlas)

**Hard prereq**: 1134 (Y) reject-mode flip on `/api/pa/chat/`
lands first.

### Phase 0 — Scaffolding (1 PR, near-term)

- `config/fleet_agent_routing.json` v2 with top-level `routing` +
  `capabilities` split (back-compat shim for legacy `allowlists`).
- `capabilities.{pa_tools, spiders, beat_tasks}` sections present
  with **only signal-studio + contract-concierge** entries
  populated (empty for the 5 deferred apps).
- `capabilities.spokespersons: {}` (schema present, empty).
- `core/services/fleet_capability.py` with `allow_*` helpers that
  return `True` when the manifest is empty (backward-compat).
- `validate_fleet_capability_manifest` mgmt command (validates
  what's there; skips empty sections).
- No enforcement, no audit table yet.

### Phase 1 — Warn-only audit (1 PR)

- `FleetCapabilityAuditRow` model + migration.
- `fleet_capability.allow_*()` helpers write audit rows
  always-allow-but-log.
- `python manage.py suggest_fleet_manifest` reads
  `FleetCapabilityAuditRow` and prints a proposed allow block
  per (app, axis).
- Scope: signal-studio + contract-concierge.

### Phase 2 — Per-axis reject flip (3 small PRs, signal-studio + CC only)

For each axis in order [pa_tools, spiders, beat_tasks], after
≥3 days of clean audit telemetry:

1. **`pa_tools`** first (most call volume → fastest learning loop).
2. **`spiders`** second.
3. **`beat_tasks`** third.

Each PR: flip `fleet_capability.allow_<axis>()` from log-only to
enforce. Mismatches log as warnings for one more cycle, then
deny.

### Phase 3 — Deferred apps re-enter (n PRs, as intent fills)

For each of the 5 deferred apps (mentorforge, pitchdeckforge,
sellerpilot, dealflowtracker, compliancesentinel), once the
**next session's discovery work** produces documented product
intent:

- Add the app's `capabilities.*` entries to the manifest.
- Phase 1+2 cycle (warn-only → audit → reject flip per axis) for
  that app.
- Per Atlas trigger: app unparks when it has a defined GTM and a
  candidate first customer.

**Status today**: all 5 apps blocked by undefined product intent.
Rigby's grounding pass (2026-05-23) listed the per-app gaps to
fill; see `docs/handoffs/SESSION_1134_<slug>.md` (this session's
handoff).

### Phase 4+ — Spokespersons (per Atlas trigger)

When (a) a paying customer demands persona-narrated output AND
(b) Character OS unparks:

- Populate `capabilities.spokespersons.<app_slug>` entries.
- Implement CO persona-registry mirror (§4.1 v2).
- Wire `allow_spokesperson()` enforcement at render-request
  construction sites.
- Coordinate with Character OS active session.

### Phase 5 — Operator UI (optional, per Rigby need)

- Rigby tool: `fleet_capability_tool <app_slug>`.
- Admin UI: edit `capability_overrides` on `FleetServiceIdentity`.

---

## 6. Vertical slice definition (re-scoped to active apps)

The demo-able unit of v3's Phase 1 is **warn-only audit landing
for signal-studio (most active call surface), one axis
(`pa_tools`)**:

- **Backend**: `FleetCapabilityAuditRow` model + migration; one
  helper wired into PA tool dispatch.
- **API**: no new endpoint — audit rows queryable via existing
  admin / Rigby tool.
- **UI**: Rigby tool that reads the table and prints "in the last
  24h, signal-studio called `(tool, action)` pairs X, Y, Z —
  manifest says `{}`, proposed allow set: {tool: [actions]}."
- **E2E test**: a signal-studio PA-chat call → audit row → Rigby
  tool output.
- **60s demo**: trigger a signal-studio backend call from
  `localhost:5173`, then run the Rigby tool, see the proposed
  manifest snippet.

Subsequent axes ship the same shape, signal-studio first then
contract-concierge.

---

## 7. Open questions (post-grounding, v3)

Rigby answered most of v2's open questions in her review. v3 adds
the per-app intent gap as the primary blocker.

### Primary blocker — fill in next session

**Per-app product intent for the 5 deferred apps.** Rigby's
grounding pass produced the complete "Need from Chris" list. Until
it's filled, the deferred apps cannot enter the manifest because
allowlists would be name-extrapolations (the exact failure mode
this spec exists to close).

Question list (one per deferred app, summarized):
1. **mentorforge** — Who is the "mentor"? What artifacts? Voice?
2. **pitchdeckforge** — Slides or just narrative? Investor or sales?
3. **sellerpilot** — E-com seller? B2B? Local service? Strategy or execution?
4. **dealflowtracker** — Investor or sales dealflow? CRM or analysis?
5. **compliancesentinel** — Real product or parked? What is "compliance" here?

### Still genuinely open (cross-cutting)

1. **Atlas trigger for Phase 3 (deferred apps unpark)**. Per
   Atlas, sibling apps re-enter after Rigby Phase 1 hits its
   KPIs. Does that gate hold strictly, or can one sibling unpark
   earlier with a strong inbound signal?
2. **Routing → routing.* migration**. One-release back-compat
   shim, then drop the legacy top-level keys?
3. **Audit retention** (Rigby's lock on v2 Q6). Asymmetric:
   ALLOW 14–30d, WARN 30–90d, DENY 90–180d + daily rollups.
   Default values OK?
4. **Cross-app "consult" tier** (Rigby's lock on v2 Q3). Yes-but-
   scoped. Ships as separate spec after v2 manifest is stable —
   confirm not bundled into v2?

### Answered in v2 review (recorded so we don't re-litigate)

- ✅ Sequencing — after 1134 (Y); optional after 1134 (A); then
  Phase 0/1 here.
- ✅ Default policy — `default: "deny"` on every axis.
- ✅ Per-user quotas — out of scope for v1.
- ✅ Manifest authorship — humans via PR review; Rigby may
  *suggest* via `suggest_fleet_manifest`, never auto-merge.
- ✅ Inventory drift consequence — Fail CI (primary) +
  fail-at-startup in strict mode + warn-at-deploy as optional
  sugar.

---

## 8. Explicitly not in scope (v3)

- New transport protocols. Reuses fleet HMAC bridge (Move 1).
- New auth mechanism. Reuses `FleetServiceIdentity` /
  `FleetServiceKey`.
- **Defining product intent for the 5 deferred apps.** That's
  the *next session's* job (app-by-app discovery with Chris),
  not this spec's. Manifest entries for those apps stay empty
  until intent is documented elsewhere.
- **Character OS persona work**. Phase 4+ per Atlas. Spec
  records the design; no near-term implementation in this repo
  or CO's.
- **Claim provenance + brand-voice rules.** Those are
  `UDB_BEHAVIOR_LAYER.md` + CO policy templates.
- Per-user quotas.
- Billing / pricing per call.
- Capability inheritance / hierarchies.
- Time-window scoping.
- Multi-tenant scoping inside one app.

---

## 9. Estimated work (re-scaled to v3 scope)

- **Phase 0** scaffolding (split file + helpers + validator) for
  2 active apps: 1 PR, ~250 LOC.
- **Phase 1** audit table + helpers + suggest command, scoped to
  2 active apps: 1 PR, ~350 LOC.
- **Phase 2** axis enforcement (3 PRs for 3 axes × 2 apps):
  ~500 LOC total.
- **Phase 3** deferred apps re-enter: ~50 LOC per app × 5 apps
  = ~250 LOC, but each gated on intent capture.
- **Phase 4+** spokespersons: ~600 LOC (CO mirror + render-event
  shape + enforcement), but gated on Atlas Phase 4 trigger.
- **Phase 5** UI: 1-2 PRs, sized by surface chosen.

Near-term total (Phases 0-2): ~1100 LOC across 5 PRs, 1-2
sessions.

---

## 10. Decision needed from Chris

Recommended path:

- **(B-anchored) Sequence after 1134 (Y).** Reject-mode flip
  lands first. Then Phase 0/1 of this spec for signal-studio +
  contract-concierge only. Defer the rest until the next
  session's app-by-app discovery produces real product intent.
- Spokespersons axis recorded as future-state; not started.

Alternative pathways:

- **(A) Defer the whole spec.** Park until a customer / partner
  asks for per-app authz directly.
- **(C) Try to ship all 7 apps in one push.** Rigby flagged
  this: allowlists for the 5 deferred apps would be
  name-extrapolations. Don't do this.
- **(D) Reshape further.** Tell me what to change.

If you go with (B-anchored), the immediate next move is **not
this spec's Phase 0** — it's the *app-by-app discovery* with
Rigby that fills the per-app intent gaps. That work feeds back
into this spec's Phase 3 trigger.

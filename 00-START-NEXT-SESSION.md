# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2745 CLOSED — ENGINEERING PIVOT DIRECTIVE FOR S2746

**Refreshed 2026-07-10 (SESSION 2745 CLOSED. No PR — pure config-directive session: Chris exercised the S2744-shipped `cost_thresholds` CLI to open the §17 observation period at `month: $500.00 / mode: monitor`. Rigby workspace deliverable dropped for cross-session visibility. Session-close directive from Chris: "for the next session I want to focus on engineering. Over the last few days the questions being answered have not been what needs to be built instead it's been what's built and not connected." Memory rule `feedback_engineering_bias_over_audit.md` codifies the pivot. S2746 opens with engineering bias.).**

Session anchors (read in order):

1. [`docs/handoffs/SESSION_2745_OBSERVATION_OPENED_ENGINEERING_PIVOT.md`](docs/handoffs/SESSION_2745_OBSERVATION_OPENED_ENGINEERING_PIVOT.md) — S2745 arc: threshold opened + engineering-pivot directive + memory rule + P0 wired
2. [`docs/handoffs/SESSION_2744_COST_THRESHOLDS_COMMAND.md`](docs/handoffs/SESSION_2744_COST_THRESHOLDS_COMMAND.md) — S2744: cost_thresholds CLI shipped (the substrate S2745 exercised)
3. [`docs/handoffs/SESSION_2743_COST_PROTECTION_CAT3.md`](docs/handoffs/SESSION_2743_COST_PROTECTION_CAT3.md) — S2743: Cat 3 startup log ($246/mo baseline visibility hook)
4. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)

---

## P0 — COST THRESHOLD OBSERVATION CHECK-IN (opened 2026-07-10 07:35 America/Denver)

**Do this FIRST before candidate selection.** Chris opened the §17 threshold observation period at S2744 close by exercising the newly-shipped CLI. Requested tomorrow-morning check-in.

**State at open:**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation only)
- Set locally on Chris's dev DB via `python manage.py cost_thresholds --set month 500`

**Report to Chris at session open:**

1. **Current threshold config** — run `python manage.py cost_thresholds`; confirm `month: $500.00` still set and mode still `monitor`. Flag any drift.
2. **Accumulation** — query `LLMCallLog` (or the equivalent cost-accumulation surface used by the beat task) for the ~24h since 2026-07-10 07:35 MDT. Report: total accumulated $, % of $500 ceiling, top 3 cost drivers by model/service.
3. **Anomalies** — any single-hour spike >$20, any new provider showing up, any `[COST_MONITOR]` log lines showing near-threshold behavior. If clean, say so explicitly.
4. **Advance recommendation** — based on 24h data, is one day of clean observation enough to advance to `--set-mode freeze` (shadow mode), or does Chris want to observe longer? Rigby SIGN on the recommendation before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.** Per S2735 P1 gate discipline.

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` ("Rigby: Cost threshold observation period — opened 2026-07-10 (S2744)"). Ask Rigby about the observation and she has full context.

---

## ENGINEERING PIVOT — Chris's directive at S2745 close

**Verbatim:** "for the next session I want to focus on engineering. Over the last few days the questions being answered have not been what needs to be built instead it's been what's built and not connected."

**Signal decomposition:**
- The S2739→S2744 arc streak (6 sessions) was all cost-protection substrate iteration. Real work, but repetitive.
- The S2745 candidate queue was dominated by Class 2 (constitutional-ADR unblocking = "connect what's built") + Class 3 (meta-methodology = "codify what we observed"). Almost nothing was net-new engineering.
- Chris wants the pendulum swung back toward building.

**Codified rule:** [`feedback_engineering_bias_over_audit.md`](../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_engineering_bias_over_audit.md). At S2746+ session open, list net-new engineering candidates FIRST. Gate connect-what-exists / meta-methodology behind engineering options. Actively propose 1-3 net-new candidates every session rather than picking from the connect-queue by default.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `20747b6e` (PR #3070 merged; cost_thresholds command shipped — unchanged from S2744) |
| Playbook version | **v0.4.1** (unchanged since S2742) |
| Playbook rule count | **196** |
| Constitutional Debt | **Zero outstanding CDs from v0.1.0 forward** |
| Session pin | `pa-73f0e2e210574d6d` (minted S2745 close, active in wrapper) |
| Prior pin | `pa-571748d9b6b940ea` — retired 2026-07-10 (5 rows updated) |
| Wrapper default pin | `tools/pa_local.sh:532` — matches new S2746 pin |
| Live infra state | `SystemConfiguration` row: `cost_threshold_month = 500`, mode = `monitor` (accumulating since 2026-07-10 07:35 MDT) |

---

## What S2745 was (not shipped)

**No PR. No code changes.** S2745 was pure config-directive + session-close bookkeeping:

- **Live config change** — `python manage.py cost_thresholds --set month 500` executed on Chris's local DB; verified at both CLI and ORM layers
- **P0 wired** — top-of-file callout in this file + step 4 upgrade
- **Rigby deliverable** — `06f04b41-91e1-4a00-8b8e-0905502e7d83` in Donkey Betz workspace
- **Memory codified** — `feedback_engineering_bias_over_audit.md` captures the engineering-pivot directive
- **Docs cascade** — will run at session-close commit per S1802 cascade-PR rule
- **Pin rotated** — S2744 pin retired, S2746 pin `pa-73f0e2e210574d6d` minted + wrapper updated

Full arc detail: `docs/handoffs/SESSION_2745_OBSERVATION_OPENED_ENGINEERING_PIVOT.md`.

---

## Candidate queue for S2746 — engineering-bias framing

**Per new memory rule, net-new engineering leads. Connect-what-exists is demoted. Ask Chris for direction rather than pattern-matching the connect-queue.**

### CLASS 1 — NET-NEW ENGINEERING (propose 1-3 every session per new memory rule)

These are seed suggestions — Chris knows better than me what he wants to build next. Present these as directional prompts, then let him name the actual candidate.

1. **New Employee OS employee (4th)** — there are 3 (Documentation Manager, Platform Auditor, Chief of Staff). Meaningful expansion candidates: Revenue Ops, Content Strategist, Cost/Ops Sentinel (natural extension of the §17 cost-protection work), Betting Ops. Would ship: new `AIEmployee` + `JobContract` entries, new MissionRunner steps, admin visibility, first mission verdict. Vertical-slice friendly.
2. **Betting dashboard new feature** — 9-tab dashboard is user-visible engineering surface. Could be a new tab, new visualization, new prediction pipeline. Needs Chris to name the gap.
3. **New spider on Chris-named data gap** — 80 spiders live. What data does Chris need that isn't covered? Ships: spider class + fixture + test + registry entry + downstream signal wiring. Small vertical slice.
4. **Cost Ops CLI expansion** — the S2744 `cost_thresholds` pattern was clean; could extend to other config surfaces (rate limits, timeouts, per-provider budgets). Genuinely new capability but same substrate — flag as substrate-adjacent, may not fully satisfy the pivot.
5. **New UI page on Command Center** — 61 routes live; if there's a workflow Chris wants that requires a new page (not a new tab in an existing page), that's real engineering.
6. **Discord bot new command** — 96 commands live. A single Cog + slash-command is a bounded engineering slice.

**Recommended session-open pattern:** propose 2-3 from the above (plus any live signal you catch from Chris's recent work) as directional prompts. Chris picks or names his own.

### CLASS 2 — POLISH with user-visible outcome (small S-M engineering)

Small but real new capability. Different from "connect-what-exists" residuals.

7. **§14 Platform Health autonomic Governance reaction** — new signal-to-freeze mapping; needs Chris ADR on trigger-to-freeze semantics (this one straddles engineering + ADR — may still count as "connect" and be deferred)

### CLASS 3 (DEMOTED) — Connect-what-exists / Constitutional-ADR unblocking

**Per pivot: gate these behind Class 1 unless Chris explicitly picks them.** These are all "connect what's built" work:

- **§4 Content Published** — 4 Chris ADRs D65a-D65e blocking
- **§7 Revenue Opportunity** — 5 Chris ADRs T1-T8 blocking
- **§8 HAI Escalation residuals** — small-scope after all 4 bridge methods shipped
- **§9 Governance Enforcement** — Chris ADR blocking
- **§10 Authority Violation** — STAGE 3 Symbol Mapping blocking
- **§11 Memory Creation** — Chris D-verdict D80 blocking
- **§17 Cat 1 enforcement flip** — waits for observation-period data + Chris approval per S2735 P1
- **§18 Auth full scope** — Chris D-verdict on 4-axis §14.14 blocking
- **§19 Cat C2 session-lifecycle Auth cascade** — Chris D-verdict per §14.14
- **§19 Conversation Lifecycle envelope-shape telemetry** — envelope ABSENT at HEAD per §29

### CLASS 4 (DEMOTED) — Meta-methodology / Codification candidates

**Per pivot: propose only if Chris explicitly asks for methodology work.**

- CDR-002 receiver-driven fanout canonical pattern
- CX-P11 CANDIDATE disambiguation (needs third organic instance)
- §29-style verdict template codification
- PATCH-scope record template (v0.4.1 first instance; awaits second)
- Capability graph refresh cadence formalization
- "Body SIGN pass-on-first-attempt as small-to-mid-scope signal" (3 instances so far)
- "Visibility hook + ops verb pair" arc pattern (first instance S2743+S2744)
- "Public-helper-first cross-arc unlocking" (first instance S2743→S2744)
- "Rigby-authored refinement text folded verbatim" (2 instances; awaits third)
- **NEW candidate:** "Substrate-saturation → engineering-pivot signal" — S2745 close is first instance (6 consecutive §17 arcs → Chris pivot). Awaits second instance on different substrate.
- **NEW candidate:** "Config-directive-only session as post-tool-arc pattern" — S2744 shipped CLI, S2745 exercised it. Single-instance.
- **NEW candidate:** "deliverable_tool.create landing as `ready` vs S1241 `completed` rule" — S2745 create returned `ready` directly. Single data point. Awaits second before updating S1241 memory rule.

### External signal-driven

- **Production observation** — `would_freeze` shadow live from S2739; `[COST_MONITOR] startup:` line live from S2743; CLI live from S2744; observation period live from S2745. The check-in P0 above is the current forward motion here.

---

## Recommended session-open protocol (S2746)

1. `context-kit orient`
2. Read `docs/handoffs/SESSION_2745_OBSERVATION_OPENED_ENGINEERING_PIVOT.md` in full
3. Verify runtime state: `git log --oneline -3`, `celery inspect ping`
4. **P0 check:** run the observation check-in per top-of-file callout; report accumulation, anomalies, advance recommendation to Chris
5. Retire `pa-73f0e2e210574d6d` (S2746 open pin) + mint fresh S2746-in-flight pin when candidate is selected (default: reuse the open pin as the arc pin unless SIGN isolation is needed)
6. **Propose 2-3 Class 1 net-new engineering candidates** per new memory rule; ask Chris to pick or name his own. Do NOT default to Class 3 audit/connect items.
7. **On candidate acceptance:** apply PLAYBOOK-6.10.6 verify-before-build FIRST (30s), THEN Cat A

---

## Reference documents

Ordered by frequency of use:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor v0.4.1)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)
4. [`docs/research/platform/platform_capability_graph.md`](docs/research/platform/platform_capability_graph.md) — capability chains + append-only refreshes
5. [`docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md`](docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md)
6. [`docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md`](docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md)
7. [`docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md`](docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md)

---

## Session close summary (Session 2745 — for archive)

- **Arc shipped:** nothing (no PR, no code); pure config-directive session
- **Live state change:** `SystemConfiguration cost_threshold_month = 500` on Chris's local DB; observation period opened
- **Cross-session visibility:** Rigby deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` in Donkey Betz workspace
- **Memory codified:** engineering-pivot rule (`feedback_engineering_bias_over_audit.md`)
- **Docs edits:** this file (P0 callout + full S2746 refresh) + S2745 handoff (new) + tools/pa_local.sh (pin rotation)
- **Pin lifecycle:** S2744 arc pin `pa-571748d9b6b940ea` retired (5 rows updated); S2746 pin `pa-73f0e2e210574d6d` minted + wrapper rotated
- **Constitutional debt at close:** Zero (unchanged)
- **Notable event:** first-observed substrate-saturation event (6 consecutive §17 arcs → Chris engineering pivot); first-observed config-directive-only session as post-tool-arc pattern (both single-instance codification candidates)

---

**Session 2746 opens fresh. Bias engineering. Ask Chris what to build.**

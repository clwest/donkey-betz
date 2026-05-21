# Merge Prep — Tier 4 (Character OS native integration)

**Date:** 2026-05-12
**Author:** Claude Code, Session 1116 (merge-readiness Tier 4)
**Status:** **DRAFT — final tier, gated on Tiers 1–3 sign-off.** Do not start any Slice 1+ code until § G is signed off.

> **Purpose.** Translate the four merge-specific concerns (per-workspace Runway budget, ≤1024 char CI test, approval gate, synthetic naming) into shippable design specs. No code touched.

---

## A. Per-workspace Runway credit budget

Reference: [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) § I.2 — Chris is credit-conscious and the per-workspace cap **ships with Slice 2, not after**.

### A.1 Why this is Tier-4-now, not Tier-5-later

Slice 2 of the merge gives Rigby a `render_spokesperson_ad` tool. Without a budget gate, a 50-message Rigby session can silently spend $50–$100 in Runway credits. The merge proposal flags this as ship-blocker.

### A.2 Design (depends on Tier 1 § F.1 + Tier 3 § B)

```python
# core/services/budget_gate.py — new file
from decimal import Decimal
from typing import Optional, Literal

BudgetDecision = Literal['allow', 'downgrade', 'deny']

def check_workspace_budget(
    workspace_id: int,
    provider: str,          # 'runway' / 'openai' / 'elevenlabs' / ...
    est_cost_usd: Decimal,
    *,
    trace_id: Optional[str] = None,
) -> tuple[BudgetDecision, dict]:
    """
    Pre-call gate. Returns (decision, context_dict).

    context_dict includes:
      - workspace_daily_cap_usd
      - workspace_daily_spend_usd  (from cost_per_workspace_today)
      - est_cost_usd
      - headroom_usd  (cap - spend - est)
      - reason  (string explaining decision)
    """
    ...
```

**Default policy:**

- Daily cap per workspace: **$5.00** (operator-configurable per workspace)
- Soft (downgrade): 70% of cap → reroute to free model where the provider supports one (OpenAI → Together free tier; Runway has no free model so downgrade = deny)
- Hard (deny): 95% of cap

**Storage:**

```python
# Per-workspace cap lives in Workspace.metadata (existing JSON field) at key 'budget':
{
  'budget': {
    'daily_usd_cap': 5.00,
    'providers': {
      'runway': {'daily_usd_cap': 5.00},
      'elevenlabs': {'daily_usd_cap': 2.00},
      'openai': {'daily_usd_cap': 10.00},
    }
  }
}
```

If `workspace.metadata['budget']` is missing, fall through to system default (`SystemConfiguration['default_workspace_daily_usd_cap']`).

### A.3 Wiring points

| Site | Call shape |
|---|---|
| Runway render task (`render_spokesperson_ad`) | `decision, ctx = check_workspace_budget(workspace.id, 'runway', est_cost)` before `apply_async` |
| ElevenLabs TTS in podcast / talking video | `decision, ctx = check_workspace_budget(workspace.id, 'elevenlabs', est_cost)` |
| Stability image gen | same pattern |
| LLM call wrapper | optional — `BudgetController` already covers global; this adds per-workspace |

On `deny`, the caller raises `WorkspaceBudgetExceeded(ctx)`. PA chat surfaces it as a clean message ("workspace budget exceeded — $X.XX of $Y.YY used today"). No silent failure.

### A.4 Effort

| Step | Effort |
|---|---:|
| `budget_gate.py` + tests | half day |
| Workspace metadata schema doc + UI to set cap | half day |
| Wire into 4 render call sites (Runway + ElevenLabs + Stability + Replicate) | half day |
| Error surface in PA / frontend | half day |
| **Total** | **2 days** |

**Hard dependency:** Tier 1 § F.1 (ExternalAPICallLog with workspace_id) — the query that returns "spent so far today" doesn't exist without it.

---

## B. CI test: realtime tool descriptions ≤1024 chars

Reference: `runway-hackathon/docs/MERGE_HANDOFF_BRIEF.md` § "Three differentiators — 2" and PR EW.

### B.1 Why this matters

Runway's realtime API rejects the entire `tools` array if any tool description exceeds 1024 chars. Once a tool is added through normal development workflow, the description can drift over time as helpers append context. Silent failure = no tools available in realtime sessions.

### B.2 Existing guard

PR EW defensively truncates over-cap descriptions at the last sentence boundary under 1000 chars and logs a warning. **This is the safety net.** A CI test makes the loud failure happen at PR time instead of runtime.

### B.3 Proposed CI test (verbatim port pattern)

```python
# tests/test_realtime_tool_descriptions.py — new file
import pytest
from core.services.runway_realtime_client import REALTIME_TOOLS  # post-Slice 4

REALTIME_TOOL_DESCRIPTION_MAX_CHARS = 1024

@pytest.mark.parametrize('tool', REALTIME_TOOLS)
def test_realtime_tool_description_under_runway_cap(tool):
    """
    Runway's realtime API rejects the entire tools array if any
    tool description exceeds 1024 chars. PR EW (Character OS)
    introduced a defensive truncation guard; this test enforces
    the invariant at PR time instead of relying on runtime fallback.
    """
    desc = tool.get('function', {}).get('description', '')
    assert len(desc) <= REALTIME_TOOL_DESCRIPTION_MAX_CHARS, (
        f"Tool {tool['function']['name']} description is "
        f"{len(desc)} chars (max {REALTIME_TOOL_DESCRIPTION_MAX_CHARS}). "
        f"PR EW's _wire_tool_entries truncates at runtime but this CI "
        f"test exists so we never ship over the cap."
    )

def test_realtime_tool_descriptions_have_content():
    """All realtime tool descriptions are non-empty."""
    for tool in REALTIME_TOOLS:
        desc = tool.get('function', {}).get('description', '')
        assert len(desc) > 0, f"{tool['function']['name']} has empty description"
```

### B.4 Where to install

The realtime tool catalog (`core/services/runway_realtime_client.py:REALTIME_TOOLS`) ships in Slice 4. The CI test must land **in the same PR as Slice 4**, not after — that's the rule.

### B.5 Effort

15 minutes (one file, two tests). Trivial.

### B.6 Drift guard extension

Add to `core/services/doc_claim_verification.py`:

```python
{
    'name': 'realtime_tools_under_runway_cap',
    'check': lambda: all(
        len(t['function']['description']) <= 1024
        for t in REALTIME_TOOLS
    ),
    'severity': 'high',
}
```

Severity `high` — failure is service-down for every realtime session.

---

## C. Approval gate for render tools (through Rigby)

Reference: `docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` § I.6 — "render write-actions require operator confirm in PA chat (existing pattern)."

### C.1 The "existing pattern" — what to copy

The PA chat surface already has confirm-before-fire for high-blast-radius tools (e.g., `deliverable_tool(action='delete')`, `agent_control_tool(action='block')`). The shape:

1. LLM calls a render tool with `dry_run=true` (or default `confirm=false`).
2. Handler returns a structured "propose" response: `{status: 'awaiting_confirmation', cost_estimate: X, params: {...}, confirm_token: uuid}`.
3. Operator says "yes" / "go" / "render it" in chat.
4. LLM re-fires the same tool with `confirm_token=<uuid>`.
5. Handler validates the token (1-hour TTL, single-use), checks `budget_gate.check_workspace_budget(...)`, fires `apply_async`.

### C.2 Tools that need this gate

| Tool | Action | Why |
|---|---|---|
| `studio_tool` | `render_spokesperson_ad` (Slice 2) | $1-3 per fire |
| `studio_tool` | `polish_video` (Slice 3) | $0 (free ffmpeg) — no gate needed |
| `studio_tool` | `add_backdrop` | depends — if backdrop is cinematic_video, free; if new cinematic generation, $1 |
| `studio_tool` | `add_animated_pip` | $1 per fire |
| `studio_tool` | `scene_composite` | $1 per fire |
| `studio_tool` | `dub_video` | $0.30 - $1 per fire |
| `studio_tool` | `remix_video` | $0.30 - $1 per fire |
| Realtime tools (Slice 4) | `render_short_ad`, `render_long_ad` | $1-5 per fire |

**Free ops (Polish, PiP, Co-Host, Music, B-Roll)** — no gate; these are pure ffmpeg.

**Cost-dependent ops** (`add_backdrop` with new cinematic generation) — the handler dynamically computes the cost and decides gate-needed flag.

### C.3 Realtime gate caveat

Slice 4's realtime avatar sessions complicate this. The operator is voice-talking to an advisor; pausing for written confirmation breaks the experience. Two options:

**Option A — Pre-authorized budget envelope:** at session open, operator confirms a session-wide budget (e.g., "this session can spend up to $10"). Realtime renders fire freely until the envelope is exhausted.

**Option B — Voice confirmation:** advisor proposes the render verbally; operator says "go ahead" / "render it." Less precise; harder to log.

Recommendation: **Option A.** Cleaner, more bounded, matches the per-workspace budget model.

### C.4 Effort

| Step | Effort |
|---|---:|
| `confirm_token` middleware in PA dispatcher | 2 hr |
| Cost-estimate dry-run mode on render tools | 2 hr |
| Realtime session pre-auth envelope | 3 hr |
| Tests | 2 hr |
| **Total** | **~1 day** |

Ships with Slice 2 (alongside `render_spokesperson_ad`).

---

## D. Synthetic naming convention (rename now while cheap)

Reference: prompt's Tier 4 §4 — "Since nobody's seen the advisors and there's no real-figure constraint, rename them now while the rename is cheap. Original synthetic names from day one."

### D.1 Current state

Per `CLAUDE.md` and `docs/ADVISOR_AUDIT.md`:
- **16 named figures:** Warren Buffett, Cathie Wood, Ray Dalio, Sam Altman, Elon Musk, Gary Vaynerchuk, MrBeast, Chris Voss, Billy Beane, Haralabos Voulgaris, Dr. Peter Attia, Grant Cardone, Kevin Mitnick, Sal Khan, Tim Cook, Andrew Ng
- **14 domain specialists** (already synthetic — "Crypto Whale Tracker" etc.)

The 16 real names are legally exposed if these advisors ever ship with avatars / synthetic voices generated by the merge. **The rename window closes the moment Slice 1 binds Runway avatar IDs** — at that point the brand identity is baked into Cloudinary URLs, Runway records, and Initiative deliverables.

### D.2 Proposed naming pattern

Each named advisor → synthetic identity built from (domain + archetype + first-name only):

| Original | Domain | Archetype | Proposed synthetic |
|---|---|---|---|
| Warren Buffett | Value investing | Mentor | "Walter the Mentor" or "Walt — Long-Horizon Value" |
| Cathie Wood | Disruptive innovation | Visionary | "Cassie — Disruption Hunter" |
| Ray Dalio | Macro / principles | Codifier | "Rey — Principles Codifier" |
| Sam Altman | AI / startups | Builder | "Sami — AI Frontier" |
| Elon Musk | Engineering / risk | Contrarian | "Elias — First Principles" |
| Gary Vaynerchuk | Marketing / hustle | Operator | "Garin — Brand Operator" |
| MrBeast | Audience / spectacle | Showrunner | "Mr. Spectacle — Audience Maximizer" |
| Chris Voss | Negotiation | Tactician | "Voss — Tactical Negotiator" *(common surname, low risk)* |
| Billy Beane | Sports analytics | Quant | "Beck — Roster Quant" |
| Haralabos Voulgaris | Sports betting | Sharp | "Hari — Sharp Bettor" |
| Dr. Peter Attia | Longevity / medical | Diagnostician | "Dr. Peyton — Longevity Lab" |
| Grant Cardone | Sales / real estate | Closer | "Grant — Closer Mindset" *(or rename to "Cardo")* |
| Kevin Mitnick | Security / hacking | Red-team | "Mitch — Red-Team Sentinel" |
| Sal Khan | Education | Teacher | "Sal-Educate" → "Sage — Personal Tutor" |
| Tim Cook | Operations / leadership | Steward | "Timo — Operations Steward" |
| Andrew Ng | ML / education | Practitioner | "Ang — ML Practitioner" |

**Pattern principles:**
1. Single-token name (no "Warren Buffett-style").
2. Tag with domain archetype after an em-dash.
3. Avoid real-figure visual identity (no Buffett-style cherry Coke + suit cues in portrait prompts).
4. Hold the original-figure *wisdom corpus* (their books, talks, etc.) as the knowledge source — that's reference material, not impersonation.

### D.3 Why hold the wisdom corpus

The 16 named figures aren't valuable because of their faces. They're valuable because their *frameworks* are well-trodden. Buffett's value investing principles are public; Dalio's `Principles` is published. The merge surfaces the framework wrapped in a synthetic identity, with proper attribution in the advisor's `knowledge_sources` metadata ("trained on Ray Dalio's `Principles`" — but synthetic identity is the speaker).

### D.4 Implementation footprint

| Step | Effort |
|---|---:|
| New migration: `Advisor.synthetic_name`, `Advisor.original_figure_reference` (text), `Advisor.archetype` | 30 min |
| Backfill: 16 rows updated with synthetic names (above table) | 1 hr |
| Frontend: `AdvisorCard` displays `synthetic_name` not `name` | 30 min |
| Portrait regen prompts: synthetic identity, not real-figure visual cues | runs during Slice 1 anyway |
| Voice clone selection: synthetic voice (use ElevenLabs preset, not impersonation) | runs during Slice 1 anyway |
| Frontend `Wisdom source: <original>` attribution row | 30 min |
| **Total** | **~3 hours** |

**Ships before Slice 1** so portrait + avatar binds carry synthetic identity from day zero.

### D.5 Legal / brand rationale (for Rigby's gate review)

Per memory `feedback_no_fluff_verify_truth.md`, Chris is in "verify truth, no fluff" mode. The truth here:

- Generating Buffett-likeness portraits + voice clones is a clear right-of-publicity violation in most US jurisdictions.
- The wisdom corpus (their books, public talks) is fair-use reference material when properly attributed.
- The synthetic identity wrapper makes the platform's position defensible: "we're synthesising a coach informed by these public frameworks, not impersonating the figures themselves."

This isn't just a UX choice — it's a legal posture. The rename window closes when avatar IDs bind.

---

## E. Slicing dependencies — what blocks what

Combining Tiers 1–3 plus this tier:

```
Tier 1 § F.1 (ExternalAPICallLog + workspace_id on LLMCallLog)
    ↓
Tier 3 § B (trace_id propagation + CeleryTaskEvent.trace_id)
    ↓
Tier 4 § A (per-workspace budget gate)        Tier 4 § B (1024-char CI test)
    ↓                                          ↓ (independent)
Tier 4 § C (approval gate for renders)
    ↓
Tier 4 § D (synthetic rename) ─────────────────┐
                                                ↓
                                         MERGE SLICE 1 — Advisor gets a face
                                                ↓
                                         MERGE SLICE 2 — SpokespersonAgent
                                                ↓
                                         MERGE SLICE 3 — 10 finishing layers
                                                ↓
                                         MERGE SLICE 4 — Realtime sessions
                                                ↓
                                         MERGE SLICE 5 — Initiative video
```

**Critical path:** Tier 1 § F.1 → Tier 3 § B → Tier 4 § A → Slice 2. Cannot ship Slice 2's `render_spokesperson_ad` tool without the budget gate, which requires the workspace-scoped logging, which requires the schema.

**Parallelisable:** Tier 4 § B (CI test) and § D (rename) are independent of the budget rail and can ship in parallel.

---

## F. Total pre-Slice-1 work

| Item | Tier | Effort |
|---|---|---:|
| Add `workspace` FK to `LLMCallLog` + caller plumbing | 1 § H.1 | half day |
| Create `ExternalAPICallLog` + persist 11 cost-calculator sites | 1 § H.1 | 1 day |
| `cost_per_workspace_today` query + PA tool action | 1 § H.1 | 1 hr |
| `build_cost_audit` mgmt command | 1 § H.1 | 1 day |
| `trace_id` end-to-end propagation | 3 § B + § H | 1.5 days |
| `CeleryTaskEvent.trace_id` migration | 3 § H | 30 min |
| `budget_gate.py` + tests + Workspace metadata UI | 4 § A | 2 days |
| `confirm_token` middleware + render approval gate | 4 § C | 1 day |
| Realtime tool 1024-char CI test | 4 § B | 15 min |
| Synthetic advisor rename + migration + backfill | 4 § D | 3 hr |
| **Total** | | **~7-8 working days** |

That's roughly two work-weeks at one-engineer-equivalent throughput.

**Reality check:** Chris is in cost-conscious mode, low OpenAI credits, doing Donkey Betz as a side project. Two weeks of focused pre-merge work without ANY user-visible feature shipping is a real ask. The alternatives:

- **Defer all but the most critical:** ship Tier 1 § F.1 (workspace FK + ExternalAPICallLog), Tier 3 § H.1 (CeleryTaskEvent.trace_id), Tier 4 § D (rename), Tier 4 § B (CI test). That's ~2 days. Skip the budget gate; rely on global BudgetController + manual operator caution for Slice 2.
- **Ship one slice as proof:** Slice 1 (Advisor gets a face) is mostly free of budget risk — portrait + avatar binds are bounded one-time costs. Could ship Slice 1 + rename without the full budget rail, then build the rail before Slice 2.

**Recommendation:** the **defer-to-minimum** path. Ship the rename + CI test + LLMCallLog workspace FK first (~half day), then ship Slice 1, *then* invest the 2-day budget rail before Slice 2.

---

## G. Gate conclusions — operator + Rigby sign-off

Before any Slice 1+ code starts, the operator must agree to all six:

1. **Tier 1 conclusions accepted.** Cost-blindspot (4 ✗ rows) acknowledged; ExternalAPICallLog is real work, not bikeshedding.

2. **Tier 2 conclusions accepted.** Connection census is a detector-roadmap, not a delete-list. No agent deletions before § K detectors ship.

3. **Tier 3 conclusions accepted.** trace_id propagation is ~1.5 days; CeleryTaskEvent.trace_id is the highest-leverage change.

4. **Per-workspace budget design (§ A) is the right shape.** Daily $5/workspace default; soft 70% / hard 95%; surfaced via `budget_gate.check_workspace_budget()`. Or operator disagrees and proposes alternative.

5. **Realtime tool 1024-char CI test (§ B) ships in the same PR as Slice 4.** Non-negotiable per Character OS PR EW.

6. **Synthetic rename (§ D) ships BEFORE Slice 1 portrait binds.** Operator confirms the synthetic-name pattern is acceptable (or proposes alternative). Real-figure names retained in `Advisor.original_figure_reference` as attribution metadata only.

If any of the six is "no" / "not yet," loop back via Rigby. **Do not start Slice 1 code without all six.**

---

## H. Open questions for Rigby (route via PA chat)

Three questions for Rigby's review before this audit's gate closes:

1. **Default workspace cap.** § A.2 proposes $5/workspace/day. Is that the right number? Too tight will block legitimate creative work; too loose defeats the purpose.

2. **Naming.** § D proposes synthetic names with specific suggestions. Does Rigby want to see all 16 renames in a single PR, or one-by-one with operator review per name?

3. **Slicing priority.** Should we go with the **defer-to-minimum** path (§ F recommendation) or commit to the full 2-week pre-merge investment? Chris's call.

PA-chat-formatted ask:

```
PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-donkeyking-token> \
  python tools/pa_chat.py \
  "Reviewing pre-merge readiness audit Tiers 1-4 (docs/COST_SURVIVAL_AUDIT.md, CONNECTION_CENSUS_2026_05.md, TELEMETRY_PLAN_2026_05.md, MERGE_PREP_TIER_4.md). Three gate questions for you and Chris: (1) per-workspace daily $5 cap — right number? (2) all 16 advisor renames in one PR or one-by-one? (3) defer-to-minimum pre-merge path (Tier-4 §F) vs full 2-week investment — recommendation?" \
  --tools --conversation <id>
```

---

## I. References

- [`docs/COST_SURVIVAL_AUDIT.md`](COST_SURVIVAL_AUDIT.md) — Tier 1 (cost survival)
- [`docs/CONNECTION_CENSUS_2026_05.md`](CONNECTION_CENSUS_2026_05.md) — Tier 2 (connection census)
- [`docs/TELEMETRY_PLAN_2026_05.md`](TELEMETRY_PLAN_2026_05.md) — Tier 3 (telemetry)
- [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) — native-integration counter-proposal
- [`docs/ADVISOR_AUDIT.md`](ADVISOR_AUDIT.md) — current 30-advisor inventory
- `runway-hackathon/docs/MERGE_HANDOFF_BRIEF.md` — Character OS handoff (load-bearing patterns)
- `core/models_unified_system.py:828` — `Advisor` model

---

**End of Tier 4.** Pre-merge audit complete. Operator + Rigby gate review required at § G before any Slice 1+ code begins.

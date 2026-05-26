---
title: "Narrative editing guardrails — v1"
status: active
last_updated: 2026-05-26
session: 1159
audience: future-editor of any `docs/narratives/*.md` file
template_version: v1 (Rigby, Session 1159 review of batches B/C/D)
companion_docs:
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/narratives/SIGNAL_INTELLIGENCE.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/PLATFORM_INVENTORY.md
  - docs/UDB_BEHAVIOR_LAYER.md
  - docs/UDB_TRANSLATION_LAYER.md
provenance_confidence: HIGH (derived from Rigby's Session 1159 review memo against batch B/C/D narratives)
provenance_note: Captured as a persistent editing contract after the Session 1159 narrative review (B/C/D) produced the same drift pattern across all three: brittle numeric thresholds, exact counts, model names, hash formulas, and timeouts treated as prose rather than as as-of snapshots of code. The 7 rules below name the failure modes; the "Why" + "Apply" lines name how to avoid them. Applies to every narrative in `docs/narratives/` plus any future addition.
---

# Narrative editing guardrails — v1

> **What this doc is.** A contract on what to write — and what
> NOT to write — when authoring or editing any narrative in
> `docs/narratives/`. The Session 1158 narrative pilot established
> the per-narrative template (frontmatter → §1 What this is → §2
> Vocabulary → §3 Milestone timeline → §4 What came of it → §5
> Current state snapshot → §6 Open questions → §7 Source index).
> The Session 1159 review of batches B / C / D surfaced a single
> recurring failure mode: precise prose that *looked* canonical
> but was actually a snapshot of a constant. This doc locks in
> the lessons so future editors don't reintroduce the drift.
>
> **Companion to behavior + translation layers.**
> [`UDB_BEHAVIOR_LAYER.md`](../UDB_BEHAVIOR_LAYER.md) governs
> Rigby's voice; [`UDB_TRANSLATION_LAYER.md`](../UDB_TRANSLATION_LAYER.md)
> governs audience framing; this doc governs what counts as a
> *narrative* claim worth committing to the corpus.

---

## The 7 rules

### 1. Do not add new numeric thresholds, timeouts, polling intervals, counts, or ratios
…**unless** you also provide one of:
- the config key, constant name, or code pointer, **OR**
- an explicit "as-of YYYY-MM-DD" label tied to a runtime snapshot.

**Why:** numbers in prose age silently. A future operator reads
"breaker threshold = 50," changes runtime to 80, doesn't update
the doc, and the next reader anchors their debugging on the wrong
number. The fix is not "keep numbers fresh" (that's a losing
race); the fix is "make the number's source legible."

**How to apply:** if you find yourself typing a number in prose,
ask "where does this number live in code?" If you can't point at
a constant/env var, the number probably doesn't belong in the
narrative at all — describe the *behavior* instead.

---

### 2. Do not hardcode model names or providers as permanent truth
…use "current default (configurable)" or "the LLM the registry
selects" instead of literal model strings (`gpt-4o-mini`,
`GPT-5.2`, etc.). When a literal is necessary, label it as a
current default and point to the provider-registry config.

**Why:** the platform is intentionally provider-agnostic for most
work, and the cost / capability / latency profile of any single
model is a moving target. Hardcoding "uses GPT-5.2" reads as a
permanent architectural fact when it's actually a config row.

**How to apply:** "current model" / "default model" framing is
safer than the literal name. If the literal matters (e.g., for a
session handoff or a milestone), keep the literal but pin it
("Session 1036 — adopted `gpt-5-mini`; current default may
differ").

---

### 3. Do not duplicate allowlists, enum values, or prefix lists in prose as if canonical
…name the list and the canonical home; keep a representative
sample at most. Prose lists drift; constants don't.

**Why:** when a future contributor adds an entry to
`PATTERN_TYPE_CHOICES` or extends a bypass-prefix tuple, the
constant gets the new value but five narratives that paraphrased
the old list silently disagree with reality. The drift surfaces
as a "wait, which one is right?" moment during incident response.

**How to apply:** "Pattern types are enumerated in
`PATTERN_TYPE_CHOICES`; as-of 2026-05-25 there are 10. Treat the
enum as canonical." Beats: "Pattern types: demand_spike,
trend_emergence, sentiment_shift, opportunity_window,
knowledge_gap, competitive_signal, market_movement, skill_demand,
content_gap, user_need."

---

### 4. Do not include UI-only instructions without an equivalent tool/API path
The audience contract for `docs/narratives/` is **future-operator
who cannot access UI**. Every actionable step must be reachable
through a tool, an API call, a management command, or a shell
recipe. UI mentions are fine as context ("the Workspace tab
shows X"); UI as the *only* path is a violation.

**Why:** a narrative that says "click Settings → Workflows →
Promote" is unusable by future-Claude, future-hire-doing-remote-
onboarding, or future-Chris-on-mobile-without-laptop. The corpus
is meant to remain executable across those audiences. The PA
exists in large part to provide a tool surface for everything
the UI offers; narratives should privilege the tool surface.

**How to apply:** if a step requires a click, write the equivalent
PA tool call (`work_tool action=advance initiative_id=…`) or the
management command alongside it.

---

### 5. Do not use absolute language ("never", "always", "cannot happen") for runtime behavior
…prefer "should not; if it does, check ___" + one concrete
remediation pointer. Even guarded code paths fail in production
under conditions the original author didn't anticipate; absolute
language masks the failure mode.

**Why:** the strongest signal that a narrative is wrong is the
absolute that turns out to be conditional. "The PA never infers
scope from text" should be "the PA should not infer scope from
text; if you observe text-derived scope, file a regression
against the scope-resolution path."

**How to apply:** when you reach for "never" / "always" /
"cannot," ask "if I'm wrong about this, what would the operator
see?" Write the if-wrong path into the prose. The doc becomes
more useful when it's wrong, not less.

---

### 6. Do not blur legacy vs current paths
…if a legacy code path still exists, name it, scope its
trigger, and state what happens when it runs. A narrative that
mentions "both v1 and v2 exist" without saying which is the
default — and how to tell which path a given request took —
sends future debuggers to the wrong subsystem first.

**Why:** the platform has at least three live legacy-vs-current
pairs (content pipeline v1/v2; PA keyword router vs function
calling; signal-aggregation paths pre/post Session 900). Each one
is a debugging trap. The doc that exists *because* the pair
exists has to be the doc that clarifies the trap.

**How to apply:** every legacy mention gets three sentences. (1)
What is it. (2) What triggers it (env var, endpoint, feature
flag). (3) How to tell from logs/data which path ran. If you
can't write all three, the legacy mention belongs in the open-
questions section, not the milestone narrative.

---

### 7. Do not let inventory numbers masquerade as contracts
…treat counts as snapshots; describe capability classes when
possible; cite `PLATFORM_INVENTORY.md` as the source of any
specific count. "We have 80 spiders covering 41 categories" is
prose; "Spider coverage: news / financial / tech / legal / …"
is contract-stable.

**Why:** counts drift constantly (spiders added, agents disabled,
tools consolidated). A reader who sees "155 agents" in a doc and
"83 in AGENT_MAP" in another isn't reading contradictions —
they're reading two snapshots of two different countable things
taken at two different times. Without explicit "as-of" labels,
the corpus accumulates contradictions and loses credibility.

**How to apply:** numbers that *must* appear in narrative
(usually because a milestone captures a specific snapshot) get a
date-anchored frame: "Post-Session 1033 status: 3 COMPLETED / 0
ACTIVE / 17 TRIAGE." Numbers that describe ongoing reality
either move to a capability description or get a hyperlink to
the inventory.

---

## How a future editor uses this

1. **Before adding a new claim** — check it against the 7 rules.
   If it would violate one, restructure the claim before
   writing.

2. **When opening a narrative for edit** — read the file's §8
   ("Canonical sources") block first. That's where the doc
   already names what's authoritative; don't duplicate that
   information into prose elsewhere in the same file.

3. **When reviewing someone else's narrative edit** — the
   review checklist is the 7 rules in order. If the diff adds
   any violation, the comment is "rule N applies here; restructure."

4. **When the rules and the existing prose disagree** — the
   rules win for new prose; the existing prose stays until a
   later edit refactors it. Migration is opportunistic, not
   batch.

5. **When in doubt** — narrative drafts go through the same
   review template that worked for batch A: Template PASS /
   ITERATE + Voice PASS / ITERATE + Accuracy PASS / ITERATE +
   Other notes per section, then cross-narrative coherence +
   drift list. Rigby is the canonical reviewer.

---

## Source

Derived from Rigby's Session 1159 internal-ops review memo of
batches B (`CONTENT_PIPELINE.md`), C (`SIGNAL_INTELLIGENCE.md`),
and D (`PERSONAL_ASSISTANT.md`). The review surfaced the same
8-category risk pattern across all three narratives; this doc
distills the 7 actionable rules that prevent the pattern from
recurring. See PR #2255 + the Session 1159 handoff for the
review thread.

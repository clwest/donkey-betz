---
title: "Advisors — narrative (batch I)"
status: draft (batch I of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/ADVISOR_AUDIT.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to ADVISOR_AUDIT.md DOC-AUTOGEN output + AGENTS.md context-injection section + MEMORY.md Session 1142 rename note)
provenance_note: Smaller subsystem than A-H. The advisors are dataclasses, not classes — there's no per-advisor behavior file. The narrative covers what advisors are, how they got renamed from named real-people to functional specialists in Session 1142, and how they reach the model via the enrichment pipeline. 30 functional advisors across 26 of 26 declared domains. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f).
---

# Advisors

> A "wisdom layer" of 30 functional domain specialists.
> Dataclasses, not classes — each advisor is a profile
> (background + specializations + decision frameworks +
> achievements + certifications), not a code path. The
> `advisor` enrichment service injects advisor wisdom into the
> PA's response on `opportunities` and `reasoning` intents.
> The most significant operational fact is what happened in
> Session 1142: the original 25 "legendary" advisors (named
> real people — Warren Buffett, Cathie Wood, Sam Altman, etc.)
> were renamed to 30 functional specialists with fictional
> personas. This narrative covers what the advisors are now,
> not what they were.

---

## 1. What this is

The Advisors layer is a static knowledge primitive. Thirty
`AdvisorProfile` dataclasses live in `advisors/registry.py`,
constructed by `_initialize_advisor_network()` and exposed as
the `advisor_registry` singleton. Each profile carries:

- `name` and `title`
- `domain` (one of 26 declared in `AdvisorDomain` enum)
- `expertise` level (`legend` / `master` / `expert`)
- `years` of experience
- `background` (narrative paragraph)
- `specializations` (list of skill tags)
- `consultation_types` (what kinds of advice this advisor
  gives — `strategy`, `technical_review`, `research_guidance`,
  etc.)
- `decision_frameworks` (named frameworks this advisor
  applies — e.g., `power_law_returns`, `network_effects`,
  `platform_thinking`)
- `key_achievements` (one-line credentials)
- `certifications`

There is **no per-advisor behavior code**. The advisor profiles
are read by the `AdvisorContextBuilder` (one of the 8
enrichment services covered in narrative D milestone 2) and
their `background + specializations + decision_frameworks`
fields are joined into prompt-friendly markdown that gets
injected as one of the 12 context layers (narrative A § 2).

Two things make this layer interesting beyond "static data":

1. **The Session 1142 rename.** The original 25 named-figure
   advisors were renamed to 30 functional specialists. The
   change was deliberate — public figures whose voices the
   platform was modeling created ambiguous IP and tone
   questions. Functional personas ("Value Investing
   Strategist" instead of "Warren Buffett") sidestep that.

2. **The expertise distribution is information.** 19 legend /
   8 master / 3 expert is intentional — the platform leans
   into "legendary domain experience" as its consultative
   anchor, not "mid-level expertise". The voice the advisors
   inject is decisive, not hedged.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`AdvisorProfile`** | The dataclass in `advisors/registry.py`. Fields enumerated above. Read-only at runtime; constructed once during module import. |
| **`advisor_registry`** | The singleton built by `_initialize_advisor_network()`. The platform's single source of truth for which advisors exist. |
| **`AdvisorDomain`** | Enum with 26 domains: `ai_ml_strategy`, `investment_strategy`, `business_strategy`, `career_coaching`, `content_strategy`, `crypto_analysis`, `cybersecurity`, `data_strategy`, `education_strategy`, `financial_planning`, `healthcare_strategy`, `intellectual_property`, `leadership_development`, `legal_counsel`, `marketing_strategy`, `negotiation_strategy`, `operations_management`, `options_trading`, `product_development`, `real_estate`, `regulatory_compliance`, `risk_management`, `sales_optimization`, `sports_analytics`, `startup_consulting`, `technical_architecture`. All 26 are covered by at least one advisor. |
| **Expertise levels** | `legend` (deepest experience tier, decisive voice), `master`, `expert`. Currently 19 / 8 / 3. |
| **`AdvisorContextBuilder`** | The enrichment service that turns advisor profiles into prompt text. One of 8 services in the PA's enrichment pipeline (narrative D milestone 2). Fires for `opportunities` and `reasoning` intents. |
| **Functional persona (Session 1142 rename)** | The post-1142 advisor identity model. Each advisor is a functional specialist with a fictional persona ("Value Investing Strategist" with 60 years of experience and `decision_frameworks: ['margin_of_safety', 'circle_of_competence', 'mr_market']`). The persona is intentionally decoupled from any specific real person. |
| **`build_advisor_audit`** | The mgmt command that regenerates `docs/ADVISOR_AUDIT.md` (DOC-AUTOGEN file — do **not** hand-edit). Reads the registry; produces the audit doc verbatim from the dataclasses. |
| **`advisor_count_matches_doc`** | The verifier guard that flags drift between the runtime count and `CLAUDE.md`'s claim. Currently the guard exists because earlier docs claimed `32 (10 named + 22 specialists)`; the registry materializes 30. |
| **Named figures (`(AI Model)` tag)** | Public figures whose voice the platform models. **Current count: 0.** This used to be 10 (Warren Buffett, Cathie Wood, Sam Altman, etc.) pre-Session 1142. |
| **Decision framework** | A named approach an advisor applies to problems. Examples: `margin_of_safety`, `power_law_returns`, `circle_of_competence`, `transformer_architecture_principles`. Used by the advisor's prompt-text generation. |
| **Consultation type** | What kind of advice an advisor gives. Examples: `strategy`, `technical_review`, `research_guidance`, `startup_advice`, `scaling`. Determines when an advisor is selected for context injection. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — original advisor network (named figures)** *(early sessions, Inferred)* | Initial advisor registry built as `AdvisorProfile` dataclasses representing named public figures (Warren Buffett, Cathie Wood, Sam Altman, and others). Approximately 25 named "legendary" advisors. Each carried real-person background, real-firm affiliations, real decision frameworks. `AdvisorContextBuilder` introduced as the enrichment service that injected the advisor's wisdom into PA prompts for `opportunities` and `reasoning` intents. | The platform needed a "wisdom layer" — accumulated domain expertise that agents could be augmented with. Named-figure personas were the fastest way to get specific voice and decisive frameworks into prompts (the model already knows what Warren Buffett would say). The "25 legendary advisors" framing became part of the platform's external narrative. | Wisdom layer in place. Agents on relevant intents got named-figure-shaped advice. The shape of "PA enrichment → advisor injection" became standard. | **Superseded by Session 1142.** The named-figure approach is no longer in the registry; only functional specialists are. | `advisors/registry.py` (pre-1142 commits); MEMORY.md `feedback_no_fluff_verify_truth.md` (the "verify what we actually have" pressure) |
| **Integration with the 12-context-layer model** *(Session 858 / ongoing)* | Advisors became one of the 12 context layers injected into every agent execution (narrative A § 2). The `advisor` enrichment service in the PA pipeline (narrative D § 2) fires on `opportunities` and `reasoning` intents; the `AdvisorContextBuilder` is queried for relevant advisors and their wisdom is prepended to the prompt. | The advisors existed as static data; the question was how they reached the model. Integration via the 12-context layer pattern (a deliberate decision in Session 858 and onwards) made advisor wisdom part of the platform's standard prompt-construction. | Every PA `opportunities` and `reasoning` call now gets advisor context injected. No separate "ask the advisors" code path needed — it's built into the enrichment pipeline. | **Active** — advisor enrichment is part of the standard PA flow. | `docs/topics/agent-system.md` §"Context Injection (12 Layers)" — `advisor_context`; `docs/topics/personal-assistant.md` §"Enrichment Pipeline" — `advisor` service for `opportunities`, `reasoning` intents |
| **Session 1115 — audit finds 30, not 32** | Doc-vs-reality verifier (Session 1099 framework) checked the runtime advisor count against `CLAUDE.md` claims. `CLAUDE.md` claimed `32 (10 named + 22 specialists)` at the start of Session 1115; the registry materialized 30. Verifier guard `advisor_count_matches_doc` introduced to flag drift on either side. The audit doc became DOC-AUTOGEN (regenerated by `python manage.py build_advisor_audit`). | The platform's external narrative drifted from the actual registry contents. The audit revealed both that (a) the count was wrong, and (b) the breakdown (named vs specialist) was wrong. Folded into the broader Session 1115 audit findings sweep. | `docs/ADVISOR_AUDIT.md` is now regenerable; the verifier guard flags drift; counts in narrative docs must trace back to the audit doc (or `PLATFORM_INVENTORY.md`). | **Active** — `build_advisor_audit` is the canonical refresh path. | `docs/ADVISOR_AUDIT.md` (DOC-AUTOGEN header); `docs/handoffs/SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md` |
| **Session 1142 — rename to functional specialists (the IP / tone reframe)** | The 25 named-figure advisors were renamed to 30 functional domain specialists. Identity model changed: no real-person names; each advisor became a functional persona ("Value Investing Strategist" with the same decision frameworks as the former named figure). The expertise levels were preserved (mostly `legend`); the years of experience preserved; the decision frameworks preserved; the background paragraphs rewritten to be functional. Same session also shipped: `search_docs` PA tool, threading.Lock on `get_unified_pa()`, advisor rename, disk audit 18 GB → 8.7 GB, `check_doc_headers` mgmt cmd. Three PRs total: #2178, #2180, #2181. | Named public figures created ambiguous questions around IP, tone, and the platform's positioning. "What would Warren Buffett say about this stock?" is a different question than "What would the platform's value-investing strategist say about this stock?" — the latter avoids the IP overhang and keeps the platform's voice fully its own. The post-1142 advisor identities are wholly the platform's. | 30 functional specialists across 26 of 26 declared domains. 0 named figures remaining. The `(AI Model)` tag count drops from 10 to 0. Domain coverage stays the same (or better — went up from however many domains the original 25 covered to all 26). | **Active** — current registry shape. | MEMORY.md `project_session_1142_docs_hygiene_and_search_docs.md`; cross-ref `docs/narratives/PERSONAL_ASSISTANT.md` milestone 8 (search_docs + threading.Lock + advisor rename were all in the same arc); `docs/ADVISOR_AUDIT.md` |
| **Current shape — 30 / 26 / `legend × 19 + master × 8 + expert × 3`** *(steady-state as of 2026-05-25)* | The registry's current composition. Domains with multiple advisors: `sports_analytics` (3 — Sports Analytics & Betting Expert, Sports Analytics Pioneer, Sports Betting Quant), `ai_ml_strategy` (2), `investment_strategy` (2). All other 23 domains have exactly one advisor. Total experience: ranges from 8 years (Blockchain & Crypto Strategist) to 60 years (Value Investing Strategist). | The shape is intentional — three advisors in sports because the platform's sports vertical (narrative C milestone 7) has the tightest verifiable feedback loop and deserves multiple perspectives; two each in AI/ML and investment because those are recurring intent surfaces; one elsewhere because most domains don't yet warrant multiple expert voices. | The advisor layer is now stable; changes to it would be deliberate rather than accumulation. Adding a new advisor = adding a new `AdvisorProfile` dataclass + regenerating `ADVISOR_AUDIT.md`. | **Active.** Adding a 31st advisor or rebalancing domain coverage are still product decisions worth flagging in start-here docs. | `docs/ADVISOR_AUDIT.md` Headline + Advisors-by-domain section |

---

## 4. What came of it

### Wins

- **Wisdom layer is a single primitive.** 30 dataclasses
  in one file; `advisor_registry` singleton is the read
  path; one enrichment service consumes it; one PA
  pipeline stage injects it.
- **Counts are regenerable.** `build_advisor_audit` mgmt
  command + verifier guard `advisor_count_matches_doc`
  make the count itself a runtime fact, not a narrative
  claim.
- **IP / tone footgun removed.** Session 1142's rename
  cleared the named-public-figure exposure. The platform's
  voice is now its own across the board.
- **26 of 26 declared domains covered.** No advisor-domain
  gaps. If a domain is in the enum, an advisor exists for
  it.
- **Three advisors in sports** reflects the vertical's
  weight — narrative C's tight feedback loop deserves
  multiple perspectives.
- **`legend` × 19 weighting** keeps the platform's voice
  decisive. Advisor wisdom comes from "30+ year
  practitioner" framings, not "mid-level expert" hedging.

### Tradeoffs

- **Advisors are static.** They don't learn; they don't
  evolve. New decision frameworks require a code change to
  the dataclass. The agent-learning narrative (H) does
  not extend to advisors.
- **23 of 26 domains have exactly 1 advisor.** Single
  point of perspective. If that advisor's framework is
  wrong for a specific question, there's no second voice
  in the same domain.
- **The pre-1142 narrative is in archived docs.** Old
  references to "25 legendary advisors" or named-figure
  advisors exist in the historical corpus. Some external
  positioning may still use the old framing.
- **`AdvisorContextBuilder` injection text is generated
  from dataclass fields.** The prompt text quality depends
  on the field text quality. No A/B testing of which
  framings work better.
- **No telemetry on advisor utility.** The enrichment fires
  on `opportunities` and `reasoning` intents but there's
  no measurement of whether the advisor injection
  measurably improves output quality vs not injecting.
- **Adding an advisor is a code change + audit-regen.**
  Two steps; easy to do the first and forget the second
  (audit doc would drift).
- **No domain coverage policy.** The 26 declared domains
  are the ones the registry covers. If a new domain is
  needed (say, `quantum_computing` or `synthetic_biology`),
  it's a registry + enum + advisor addition. No process
  for proposing new domains.

### Follow-on systems enabled

- **PA enrichment pipeline** (narrative D milestone 2)
  consumes advisor context for `opportunities` /
  `reasoning` intents. Without advisors, two of the eight
  enrichment services have no source.
- **Agent context injection** (narrative A § 2) — `advisor`
  is one of the 12 layers. Removing the advisor layer
  would change every agent's prompt shape.
- **`verify_doc_claims` framework** (Session 1099,
  narrative A milestone 7) uses the
  `advisor_count_matches_doc` guard as one of its baseline
  claims.

---

## 5. Current state snapshot

> Source for counts: `docs/ADVISOR_AUDIT.md` (DOC-AUTOGEN
> by `build_advisor_audit`) + `PLATFORM_INVENTORY.md`
> snapshot 2026-05-25. 30 advisors / 26 of 26 domains
> covered / 19 legend + 8 master + 3 expert.

**Headline.** 30 advisors registered. 0 named figures.
30 functional domain specialists. 26 of 26 declared
`AdvisorDomain` enum values covered.

**Domains with > 1 advisor.**
- `sports_analytics` — 3 (Sports Analytics & Betting Expert,
  Sports Analytics Pioneer, Sports Betting Quant)
- `ai_ml_strategy` — 2 (AI & Machine Learning Strategist,
  AI & Startup Strategy Expert)
- `investment_strategy` — 2 (Innovation Investment
  Strategist, Value Investing Strategist)

**Expertise distribution.** legend × 19 / master × 8 /
expert × 3.

**Experience range.** 8 years (Blockchain & Crypto
Strategist) — 60 years (Value Investing Strategist).
Average ~22 years.

**Architecture.**
- File: `advisors/registry.py`
- Singleton: `advisor_registry`
- Constructor: `_initialize_advisor_network()`
- Each entry: `AdvisorProfile` dataclass.

**Audit doc.** `docs/ADVISOR_AUDIT.md` — DOC-AUTOGEN.
Regenerate: `python manage.py build_advisor_audit`. Never
hand-edit.

**Verifier guard.** `advisor_count_matches_doc` —
introduced Session 1115. Flags drift between runtime
count and narrative-doc claims.

**Where advisor wisdom reaches the model.**
- 12 context layers (narrative A § 2) — `advisor_context`
  layer.
- PA enrichment pipeline (narrative D milestone 2) —
  `advisor` service.
- Triggers: `opportunities`, `reasoning` intents.

**Where to look when something stops working.**
- Advisor not appearing in PA output → check the intent;
  advisor enrichment only fires on `opportunities` and
  `reasoning`. Other intents (work, content, ops) don't
  get advisor context.
- Advisor count claim doesn't match registry → the audit
  doc drifted; run `python manage.py build_advisor_audit`
  to regenerate.
- New advisor not appearing → confirm the
  `_initialize_advisor_network()` instantiates the new
  `AdvisorProfile` (the registry is built at import
  time). Restart workers.
- Domain coverage gap → check the `AdvisorDomain` enum;
  every enum value must have at least one advisor or the
  audit will flag it.
- "Warren Buffett" or other named figure in advisor output
  → pre-Session-1142 framing leaked through somewhere
  (prompt template, narrative doc, or stale advisor
  field). Audit the affected file.

---

## 6. Open questions / unknown outcomes

- **Pre-1142 references in the historical corpus.**
  *Known:* Session 1142 renamed the advisors. *Unknown:*
  whether old "25 legendary advisors" or named-figure
  references still appear in public-facing docs, marketing
  text, or `PLATFORM_WHAT_IT_IS.md`. A grep across docs/
  would surface and resolve.
- **Domain coverage policy.** *Known:* 26 of 26 covered.
  *Unknown:* whether new domains have been proposed (e.g.,
  for emerging fields the platform might want to advise
  on) and what the process is for adding them.
- **Advisor utility measurement.** *Known:* the
  enrichment fires for `opportunities` and `reasoning`.
  *Unknown:* whether the advisor injection measurably
  improves output vs not injecting. No A/B test in the
  corpus.
- **Whether `legend` × 19 weighting is calibrated.**
  *Known:* the distribution is heavily legend-weighted.
  *Inferred:* intentional — "decisive voice from deep
  experience" is the platform's framing. *Unknown:*
  whether the expertise field affects the prompt text in
  any measurable way, or whether `legend` vs `master`
  just changes the description string.
- **Sports advisor count = 3 vs other singletons = 1.**
  *Known:* sports is the vertical with the tightest
  verifiable feedback loop. *Inferred:* multiple advisors
  reflect multiple perspectives on a domain with the most
  empirical data. *Unknown:* whether the three sports
  advisors disagree productively in actual consultations,
  or whether they say similar things (in which case the
  count is over-engineered).
- **Adding advisor without code review.** *Known:*
  advisors are dataclasses in a single file. *Unknown:*
  whether any process exists for proposing new advisors
  before code review (e.g., domain owner sign-off, voice
  audit) or whether it's purely a code-review pattern.

---

## 7. Source index

### Primary doc sources

- `docs/ADVISOR_AUDIT.md` — DOC-AUTOGEN. The canonical
  source for advisor counts, domain coverage, expertise
  distribution, per-advisor details.
- `docs/PLATFORM_INVENTORY.md` — inventory anchor.
- `docs/topics/agent-system.md` §"Context Injection (12
  Layers)" — `advisor_context` layer.
- `docs/topics/personal-assistant.md` §"Enrichment Pipeline"
  — `advisor` service for `opportunities`, `reasoning`.

### Named session handoffs cited above

- `docs/handoffs/SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md`
  — audit found 30 not 32; verifier guard introduced.
- Session 1142 — rename to functional specialists.
  Memory file: `project_session_1142_docs_hygiene_and_search_docs.md`.
  PRs: #2178, #2180, #2181.

### Code anchors

- `advisors/registry.py` — `_initialize_advisor_network()`,
  `advisor_registry` singleton, 30 `AdvisorProfile`
  dataclasses.
- `advisors/models.py` (or equivalent) — `AdvisorProfile`
  dataclass definition, `AdvisorDomain` enum.
- `core/services/advisor_context_builder.py` (or named
  similarly) — the enrichment service that renders advisor
  profiles to prompt text.
- `core/management/commands/build_advisor_audit.py` —
  DOC-AUTOGEN regenerator.

### Verification commands

- `python manage.py build_advisor_audit` — regenerate
  `docs/ADVISOR_AUDIT.md`.
- `python manage.py verify_doc_claims --only-drift` —
  flag drift in advisor counts vs registry (uses
  `advisor_count_matches_doc` guard).
- `python manage.py generate_platform_inventory` —
  regenerate inventory.

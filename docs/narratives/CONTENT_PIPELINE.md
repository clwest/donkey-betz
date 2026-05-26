---
title: "Content Pipeline — narrative pilot (batch B)"
status: draft (batch B of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1 (Rigby, Session 1158)
companion_docs:
  - docs/topics/content-pipeline.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/PLATFORM_INVENTORY.md
  - docs/UDB_TRANSLATION_LAYER.md
provenance_confidence: HIGH (anchored to topics doc + named handoff files + agent reference)
provenance_note: Batch B narrative for the Session 1158 corpus-narrative program. Center of gravity is the v2 deliberation pipeline introduced in Session 964. Companion to AGENTS_AND_AUTONOMY narrative — there's deliberate overlap on DecisionEnforcer and ContentWriterAgent, but this doc centers on the pipeline shape, not the agent registry. Session attributions trace to claims in docs/topics/content-pipeline.md and named SESSION_NNNN handoff files. Uncertainty labelled inline.
---

# Content Pipeline

> Companion narrative to `AGENTS_AND_AUTONOMY.md`. Same template,
> same audience contract — future-operator who cannot access the
> UI. The agent doc covered "what runs"; this doc covers "what
> the platform produces, how it judges its own output, and what
> keeps low-quality drafts from being shipped." Counts come from
> `PLATFORM_INVENTORY.md`; everything else cites a session
> handoff or a topic doc. Gaps are flagged.

---

## 1. What this is

The content pipeline is the path a piece of platform-generated
writing takes from raw spider data to a publishable artifact. It
exists because the platform produces a lot of text — blogs,
deliverables, briefs, audits — and naive LLM generation, on its
own, produces text that is fluent but un-cited, repetitive,
sometimes stale, and sometimes simply made up. The pipeline is
the platform's answer to "how do we generate at scale without
shipping garbage".

The canonical shape, introduced wholesale in Session 964, is a
six-step deliberation: **ClaimsPack** assembles citable evidence
with deterministic IDs; **ContentWriterAgent** drafts with
mandatory `[C-xxxxxxxxxx]` citations; a **3-reviewer panel**
(Skeptic + FactCheck + DomainPersona) evaluates the draft;
**DecisionEnforcer** forces a single verdict (PUBLISH / REVISE /
KILL); a single **rewrite pass** is allowed on REVISE; and the
**PublishGate** scores the result on quality, novelty, and
structure before letting it become a `SelfBlog` with status
`approved` or `published`. Scheduled tasks (Session 1000C, 1033)
move blogs through the gate without a human pressing buttons.

The pipeline has two coexisting versions. v1
(`content_review_panel.py`) is the original review path; v2
(`content_review_panel_v2.py` + `ContentDeliberationRunner`) is
the claims-based version with structured validation. Both still
exist; v2 is reached via `POST /api/v1/research/self-blog/generate-v2/`.

This narrative covers the pipeline as a whole — every step, why
each step was added, and what changed when each was added. It is
deliberately written for an operator who needs to know what to
look at when a blog ships in a bad state.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **ClaimsPack** | The bundle of citable evidence assembled before drafting. `ClaimsPackBuilder` pulls items from `SpiderData` and active `SignalCluster` rows, deduplicates by normalized URL, and caps the result at a fixed claim count. Current behavior (as-of 2026-05-25): freshness window 72 h on SpiderData, cap 20 claims. Each claim gets a deterministic ID derived from a SHA-256 hash of the normalized URL + title. **All four constants — window, cap, hash recipe, ID prefix — live in `ClaimsPackBuilder`. Treat code as authoritative, not this prose.** The deterministic ID is the load-bearing primitive — every citation in a published blog traces back to a real source. |
| **Citation `[C-xxxxxxxxxx]`** | The literal in-text citation form. Every factual assertion in a drafted blog is supposed to carry one. FactCheckReviewer verifies each one maps to a real URL with freshness inside the window. |
| **ContentWriterAgent** | The drafting agent. Has its **own** prompt-builder (`_build_intelligent_system_prompt`, `_build_content_prompt`, `generate_flagship_injection`) — it does **not** use `BaseAgent._build_intelligent_prompt()`. Anyone injecting evidence into BaseAgent's pipeline must remember it won't reach ContentWriterAgent unless they wire it through the right path. |
| **3-reviewer panel** | Skeptic / FactCheck / DomainPersona. The first two always run; DomainPersona only runs if a domain-detection confidence threshold is met (current value as-of 2026-05-25: ≥ 0.2; constant lives in the reviewer setup — code wins on drift). Each returns structured JSON `{reviewer, verdict, top_issues, required_changes, suggested_edits, confidence}`. Bad/missing LLM output is converted into a synthetic FAIL so review is not skipped silently; if you observe a published blog with zero reviewer entries in `stats_snapshot['deliberation']`, that is a regression. |
| **DecisionEnforcer** | The "Prefrontal Cortex" agent (carried over from `AGENTS_AND_AUTONOMY.md` milestone 3). Outputs `PUBLISH / REVISE / KILL` plus reason, kill criteria, deadline, rejected paths, acknowledged risks. Banned phrases: "Further analysis recommended", "More research needed". Forces a decision. |
| **Rewrite pass** | Exactly one rewrite is permitted on REVISE. ContentWriterAgent receives the top three `required_changes` per reviewer and writes again with the same ClaimsPack. No infinite loops at this layer. |
| **PublishGate** | Three-dimensional quality gate: **quality**, **novelty**, **structure**. Current thresholds (as-of 2026-05-25): 0.75 / 0.60 / 0.55. The thresholds are constants in the PublishGate module — **constants in code win** over this prose if drift is suspected. Decision is `publish` / `enhance` / `internal_only`. Has an explicit bypass: titles starting `[Research]`, `[Stage N]`, `[Audit]`, `[Internal]` auto-classify as internal-only and skip quality checks. The bypass prefix list is enforced in code; treat the code list as canonical and update this entry if it changes. |
| **SelfBlog** | The published artifact's database row. Carries `quality_score`, `novelty_score`, `structure_score`, `publish_ready`, `gate_notes`, `content_type`, `status`, and a `stats_snapshot` JSON that includes the deliberation session_id, decision, claims_count, reviewers, and review verdicts. |
| **`stats_snapshot['deliberation']`** | The per-blog audit packet. Lets you reconstruct, after the fact, what evidence the writer saw, what verdicts the reviewers gave, what DecisionEnforcer chose, and how many rewrite/enhancement rounds ran. |
| **`stats_snapshot['enhancement_count']`** | Counter for EditorAgent rewrite rounds. After 3 unsuccessful rounds, the blog is skipped to prevent infinite enhancement loops. |
| **`BlogPerformanceContextBuilder`** | The builder that injects past-blog performance into future content generation (Session 886). Average quality/novelty/structure from the last 10 blogs, plus auto-detected strengths/weaknesses and active `PipelineLearningInsight` rules. Closes the loop between "what we published" and "what we generate next". |
| **Domain content context (9 domains)** | Session 891's "builder voice" injection — finance, crypto, sports, AI/tech, legal, career, etc. Up to 2 domains per piece. The platform's own operational data (whale moves, agent counts, job application rates) is injected so the blog can write from direct experience rather than abstraction. |
| **Operational telemetry grounding** | Session 1001's primitive. `_build_operational_context()` in `core/tasks.py` queries `AgentExecution`, `CeleryTaskEvent`, `HeartBeat`, `AgentDecisionSummary` and produces a markdown block injected into both pipelines. Same intent as domain context but for the platform's own runtime metrics. |
| **Evidence-first mode** | Session 1103's correctness control. When evidence is present, three spider-context injection paths are explicitly suppressed (`_evidence_context_override`, `get_domain_content_context()`, `generate_flagship_injection()`). Path 2 (blog performance) can still surface spider URLs. |
| **`publish_intent` enum** | Session 1095 contract on deliverables. Values: `internal_only` / `publish_candidate` / `publish_required`. Distinct from `status` (workflow state). Stops the "should this be public?" question from being inferred from `is_internal` booleans. |
| **`needs_enhancement` / `pending_review` / `approved` / `published`** | The status states a blog passes through after the gate. The content finishing loop (Session 1033) wired these into automated transitions. |
| **EditorAgent (in-pipeline)** | The agent that runs on `needs_enhancement` blogs to push them toward `pending_review`. Each pass takes ~18s via OpenAI. Capped at 3 rounds via `enhancement_count`. |
| **Content type classification** | Internal-vs-public auto-detection (Session 1000C). Signals: "we built", "our system", technical density → internal; "you should", "how to guide" → public. Internal score > 1.5x public → marked internal. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Pre-Session 964 (foundation)** *(Inferred)* | `ContentWriterAgent` exists; blogs are generated from spider context; no claims-based citation; no structured review; no quality gate before publish. v1 review panel (`content_review_panel.py`) existed but didn't gate publishing. | The platform needed to write things at scale. The first cut wired the writer to the spider network and let it produce. | Blogs got produced but had no traceable citations, no review verdicts, and no failure modes — fluent text was sometimes wrong, repetitive, or unsupported. | **Active** (as v1 path) — `content_review_panel.py` is untouched; reachable for A/B testing. v2 is preferred for new work. | `docs/topics/content-pipeline.md` §"v1/v2 Coexistence"; `core/services/content_review_panel.py` |
| **Session 964 — the deliberation pipeline (architectural watershed)** | Introduced the full six-step v2 architecture in one piece: ClaimsPack (deterministic IDs from spider items, capped at 20, deduplicated by normalized URL) → ContentWriterAgent drafts with mandatory `[C-xxxxxxxxxx]` citations → 3-reviewer panel (Skeptic + FactCheck + DomainPersona) → DecisionEnforcer (PUBLISH / REVISE / KILL) → single REVISE rewrite pass → PublishGate scoring. Multi-agent content review folded into `core/agents/decision_enforcer_agent.py` and `core/services/content_deliberation_runner.py`. | The v1 path could not answer "what is this claim grounded in?" or "did anyone push back on this draft?". Adding structured deliberation made both questions answerable per-blog. | Every v2 blog now has a `stats_snapshot['deliberation']` packet you can audit after the fact: session_id, decision, claims_count, reviewers, review verdicts. Reviewers are forced to produce structured output (synthetic FAIL on bad/missing output, never skipped). | **Active** — v2 path is the default for new generation. v1 still reachable. | `docs/handoffs/SESSION_964_CONTENT_DELIBERATION_PIPELINE.md`; `core/services/content_review_panel_v2.py`; `core/services/content_deliberation_runner.py`; `core/agents/decision_enforcer_agent.py` |
| **Sessions 886, 891 — performance feedback + builder voice** | `BlogPerformanceContextBuilder` injects the last 10 blogs' quality / novelty / structure averages, auto-detected strengths/weaknesses, and active `PipelineLearningInsight` rules into future generation. Nine-domain context (finance / crypto / sports / AI / tech / legal / career / etc.) auto-detects by keyword and injects real platform data — whale moves, agent counts, job application rates — capped at two domains per piece. | The pipeline had structure but no learning loop: it didn't get better from its own outputs, and it sounded like a generic LLM rather than a system writing from its own platform's perspective. Both were prompt-shape problems. | Blogs in 2 detected domains get "builder voice" injection ("In our implementation…"). The pipeline now has a feedback signal from its own publishing history. Pipeline learning rules ("PREFER: Long-form content 1200+ words") become active context for the next draft. | **Active** — both injection paths still load. Session 1103 added evidence-first suppression that overrides domain context and flagship-voice injection when real evidence is present. | `docs/topics/content-pipeline.md` §"Content Feedback Loop (Session 886)" and §"Domain Content Context (Session 891)" |
| **Session 988 — LLM Provider Registry migration** | Reviewers and writers moved off direct `core.llm_providers` imports (a module path that doesn't exist) onto `core.services.llm_provider_registry`. Canonical call shape: `get_llm_provider_registry() → registry.complete(provider='openai', model_id='gpt-4.1-mini', request=LLMRequest(...))`. | Reviewer code paths were importing a non-existent module and silently failing on first call. Beyond the bug, there was no single chokepoint for swapping providers or adding observability. The registry gave both. | Reviewers and writers now share the registry; provider swaps are config changes. The companion agent narrative (milestone 4) covers the related `AnthropicClient` / `OpenAIClient` factory work that closed the timeout/footgun class. | **Active** — registry is the canonical call shape. Direct `core.llm_providers` imports are forbidden. | `docs/topics/content-pipeline.md` §"3-Reviewer Panel" → "LLM Provider (Session 988)"; `core/services/llm_provider_registry.py`; MEMORY.md feedback "OpenAI factory required" + "Anthropic factory required" |
| **Sessions 990, 1001, 1002, 1103 — truth controls** | (990) PA decisions on agent-generated content (publish / archive / revise) now record back to the originating agent via `AgentMemory` + `UserAgentLearning` + `FeedbackLoopEngine`, then surface into the next execution's `spider_context`. (1001) Operational telemetry grounding: `_build_operational_context()` injects real `AgentExecution`, `CeleryTaskEvent`, `HeartBeat`, `AgentDecisionSummary` data so writers cite verifiable metrics. (1002) Spider context fabrication fix — writers were inventing spider sources; the path was closed. (1103) Evidence-first mode — when real evidence is present, three spider-context paths are explicitly suppressed so domain hand-waving doesn't displace cited claims. | The pipeline had structure, learning, and a canonical provider — but it could still write things that were untrue (fabricated spider URLs, fabricated operational metrics) and the learning loop was open at the PA end (the PA's review decisions weren't recorded back to agents). These four sessions closed the loop and tightened the truth contract. | The "Ground all claims in the data provided" / "cite these, do not invent" prompt language replaced the older "expand with your perspective" language. ContentWriterAgent's `## IMPORTANT` section now explicitly forbids fabricating operational metrics or incidents. PA review actions are first-class context for every subsequent agent execution. | **Active** — all four are part of the standard generation path. | `docs/topics/content-pipeline.md` §"PA-to-Agent Content Feedback (Session 990)" and §"Operational Telemetry Grounding (Session 1001)"; `docs/handoffs/SESSION_1002_SPIDER_CONTEXT_FABRICATION_FIX.md`; `docs/handoffs/SESSION_1001_BLOG_TELEMETRY_GROUNDING.md` |
| **Sessions 997, 1000C — PublishGate hardening + automation** | (997) PublishGate quality / novelty / structure thresholds tightened ("mythology-tier" gating). (1000C) Five scheduled tasks wired so blogs move through the pipeline without manual intervention: `evaluate_unscored_blogs` (every 2h), `auto_enhance_blogs` (every 4h), `enhance_all_blogs_needing_enhancement` (every 6h), `reevaluate_enhanced_blogs` (every 6h), `auto_publish_approved_blogs` (daily 6 AM). `apply_to_blog()` now sets `blog.status = 'approved'` on `publish` decision (previously only set `publish_ready=True` without changing status). Content-type classification (internal vs public) added. | The pipeline could deliberate but couldn't ship — blogs would land in `needs_enhancement` and sit. Without scheduled automation the gate was theoretical. Without status promotion, "publish-ready" blogs never actually got to `published`. | The full automated path now runs end-to-end: drafts get scored, low-scoring ones get enhanced, enhanced ones get re-scored, approved ones get auto-published at 6 AM. Operational title prefixes (`[Research]`, `[Audit]`, `[Internal]`) bypass the quality gate cleanly. | **Active** — the five scheduled tasks are part of beat schedule on the `content` queue (plus `long_running` for the enhancement-loop variant). Status promotion is the standard behavior. | `docs/handoffs/SESSION_997_MYTHOLOGY_PUBLISHGATE.md`; `docs/handoffs/SESSION_1000C_CONTENT_REVIEW_AUTOMATION.md`; `docs/topics/content-pipeline.md` §"Content Review Automation (Session 1000C, updated Session 1033)" |
| **Session 1033 — content finishing loop + deliverable scoring** | Before this session, 116 blogs were stuck in `needs_enhancement` with no automatic path forward — EditorAgent existed but was never auto-triggered. Wired `auto_enhance_blogs` to call `EditorAgent.execute(save=True)` directly on the oldest 5 blogs per run; status moves to `pending_review` on success. EditorAgent's `_enhance_with_llm()` was importing from a nonexistent `core.services.llm_service` — fixed to use `LLMProviderRegistry` (PR #1308). Added `score_unscored_deliverables` task (every 6h at :15) that runs a heuristic over the 4,380 deliverables that had a hardcoded default `quality_score = 0.7` and replaces it with a real score in the 0.1–1.0 range. | The pipeline's "publish" half was automated but its "enhance" half was a dead end. Deliverables had no quality differentiation at all (everything was 0.7). Both were silent failure modes — looked fine, weren't shipping anything useful. | First-run results: 6 blogs enhanced (status `needs_enhancement → pending_review`), 884 deliverables scored in the first batch (distribution 0.30 – 0.75). Status snapshot at session close: 207 draft / 195 published / 111 needs_enhancement / 18 pending_review. | **Active** — both tasks are still scheduled; the finishing loop is the standard path. EditorAgent still uses `gpt-4o-mini` — flagged in the topic doc as a candidate for upgrade. | `docs/handoffs/SESSION_1003_PIPELINE_COMPLETION.md` and the Session 1033 handoff; `docs/topics/content-pipeline.md` §"Content Finishing Loop (Session 1033)" and §"Deliverable Quality Scoring (Session 1033)" |
| **Sessions 1089, 1095 — Governor + `publish_intent` enum** | (1089) "Governor and grounding" — additional grounding pass over the deliverable surface. (1095) `publish_intent` enum migration: `internal_only` / `publish_candidate` / `publish_required` on the Deliverable model (migration 0333 + backfill of 122 rows). Distinct from `status` (workflow state). Took the "is this meant to be public?" question out of inference-from-`is_internal`-boolean and made it a first-class field. | The platform was producing deliverables (not just blogs) but had no clean way to say "this is internal research, never publish" vs "this is a candidate, run it through review" vs "this must publish". Per memory entry [`feedback_publish_intent_enum.md`], Rigby's Session 1094 architectural call was specifically against `is_internal: bool` in favor of the enum. | The `publish_intent` field is now load-bearing for the canary path and the content review automation — both check intent explicitly rather than inferring from status or booleans. 122 existing deliverables backfilled to the right intent on migration. | **Active** — migration applied; field is part of the deliverable contract. Companion to the agent-narrative milestone 7 governance arc. | `docs/handoffs/SESSION_1089_GOVERNOR_AND_GROUNDING.md`; MEMORY.md `feedback_publish_intent_enum.md`; `project_session_1095_coo_gates_complete.md` |

---

## 4. What came of it

### Wins

- **Every published blog is auditable.** The
  `stats_snapshot['deliberation']` packet on `SelfBlog` lets you
  reconstruct the entire deliberation after the fact: what
  evidence the writer saw, what verdicts each reviewer gave,
  what DecisionEnforcer chose, how many rounds ran.
- **Citations are real.** The deterministic
  `C-{sha256(url+title)[:10]}` ID means every cited claim in a
  published blog points back to a specific spider source. Fact
  drift becomes detectable.
- **Bad output is caught, not patched.** The three reviewers
  produce structured FAIL verdicts that DecisionEnforcer is
  forced to acknowledge. The synthetic-FAIL fallback (Session
  964) means a broken reviewer LLM call doesn't silently bypass
  review.
- **The pipeline learns from itself.**
  `BlogPerformanceContextBuilder` (Session 886) closes the loop
  between past outputs and future generation. The PA-feedback
  closure (Session 990) closes the loop between human review
  decisions and future agent prompts.
- **Operational data replaces fabrication.** Sessions 1001 and
  1002 closed two distinct fabrication paths — operational
  telemetry and spider sources. The prompt contract now
  explicitly forbids invention in both areas.
- **Automation is real.** The Session 1000C scheduled tasks
  plus Session 1033's finishing loop mean blogs move from draft
  → published without manual intervention. The `enhancement_count`
  cap prevents infinite-rewrite loops.

### Tradeoffs

- **Two coexisting pipelines.** v1 and v2 both still exist. v1
  is reachable, untouched, and not gated the same way as v2.
  Anyone publishing via v1 bypasses the deliberation guarantees.
  This is intentional (A/B testing) but easy to forget.
- **ContentWriterAgent's parallel prompt-building.**
  ContentWriterAgent does **not** use
  `BaseAgent._build_intelligent_prompt()`. It has its own three
  methods (`_build_intelligent_system_prompt`,
  `_build_content_prompt`, `generate_flagship_injection`).
  Injecting evidence into BaseAgent's pipeline will not reach
  the content writer. This is documented but is a frequent
  source of "I added X and it's not showing up in the blog"
  confusion.
- **PublishGate thresholds are static.** Quality ≥ 0.75,
  novelty ≥ 0.60, structure ≥ 0.55. These are constants in the
  code. They worked when blogs were the dominant artifact;
  whether they're right for the current artifact mix is not
  re-evaluated session-to-session.
- **`auto_enhance_blogs` runs on `gpt-4o-mini`.** Each pass takes
  ~18s. The topic doc flags this as a candidate for upgrade.
  Whether it should move depends on cost vs quality, which is a
  product decision, not a code decision.
- **The pipeline doesn't enforce its own constants.** Title
  prefixes that bypass the gate (`[Research]`, `[Stage N]`,
  `[Audit]`, `[Internal]`) are matched as strings. A typo in a
  title-generator could route a low-quality public draft past
  the gate. This is the "feature, not bug" of an operational
  bypass — the bypass exists because there are legitimate
  internal artifacts that shouldn't be gated.

### Follow-on systems enabled

- **The canary path (Sessions 1094–1098)** uses `publish_intent`
  to route controlled injections without going through the
  user-visible UI. Without the enum, the canary would have to
  rely on inference.
- **`verify_doc_claims` and the doc-runtime split** lean on the
  pipeline's discipline. The same "evidence-first, ground in
  data, do not invent" contract that the content pipeline
  enforces internally is what `PLATFORM_INVENTORY` enforces
  externally for narrative docs (this one included).
- **PA review-feedback (Session 990)** depends on the agent
  system's `gather_context()` plumbing covered in the agent
  narrative — the two pipelines are tightly coupled.
- **`DeliverableEvent` status_transition signal infrastructure
  (Session 1095)** plugs into governance gates (rework/bounce,
  gate-hang) covered in `AGENTS_AND_AUTONOMY.md` milestone 7.

---

## 5. Current state snapshot

> Source for counts: `docs/PLATFORM_INVENTORY.md` snapshot
> 2026-05-25 (git HEAD `d513cd7f`). Pipeline structure
> reconstructed from `docs/topics/content-pipeline.md` and the
> handoffs cited above.

**Pipelines in code.**
- **v1** — `core/services/content_review_panel.py`. Original
  review path; still reachable; not gated by deliberation
  guarantees.
- **v2** — `core/services/content_review_panel_v2.py` +
  `core/services/content_deliberation_runner.py`. Default for
  new generation. Reachable via `POST
  /api/v1/research/self-blog/generate-v2/`.

**Step-by-step (v2).**
1. **ClaimsPack** assembled from `SpiderData` (72h window,
   description → factual @ 0.7 confidence, title-only →
   speculative @ 0.3) + `SignalCluster` (active, analytical @
   0.4 confidence). Deduplicated by normalized URL. Capped at
   20.
2. **ContentWriterAgent** drafts with mandatory
   `[C-xxxxxxxxxx]` citations. Its own prompt-builder, not
   `BaseAgent._build_intelligent_prompt()`. Four spider-data
   injection paths; three suppressed in evidence-first mode.
3. **3-reviewer panel** runs in parallel: Skeptic, FactCheck,
   DomainPersona (only if domain confidence ≥ 0.2). Each
   produces structured JSON; bad output → synthetic FAIL.
4. **DecisionEnforcer** chooses PUBLISH / REVISE / KILL. Banned
   phrases enforced.
5. **Rewrite pass** allowed exactly once on REVISE; same
   ClaimsPack preserved.
6. **PublishGate** scores quality / novelty / structure.
   Decision: `publish` / `enhance` / `internal_only`. Title
   prefixes bypass for internal artifacts.

**Quality thresholds.** Quality ≥ 0.75, novelty ≥ 0.60,
structure ≥ 0.55.

**Bypass title prefixes.** `[Research]`, `[Stage N]`, `[Audit]`,
`[Internal]` → auto-classified `internal_only`, gate skipped.

**Scheduled tasks (Session 1000C + 1033).**
- `evaluate_unscored_blogs` — every 2h at :10, `content` queue.
- `auto_enhance_blogs` — every 4h at :45, `content` queue,
  EditorAgent w/ `save=True`, limit 5.
- `enhance_all_blogs_needing_enhancement` — every 6h at :40,
  `long_running` queue, EditorAgent, limit 5, max 3 rounds.
- `reevaluate_enhanced_blogs` — every 6h at :10, `content`
  queue.
- `auto_publish_approved_blogs` — daily 6 AM, `content` queue.
- `score_unscored_deliverables` — every 6h at :15, `default`
  queue, heuristic scoring (0.1–1.0).

**Blog statuses.** `draft` → `needs_enhancement` (or
`pending_review`) → `pending_review` → `approved` → `published`.
The status transitions are wired in `apply_to_blog()` (Session
1000C) and `auto_enhance_blogs` (Session 1033).

**Deliverable contract.** `publish_intent` enum on Deliverable
(Session 1095): `internal_only` / `publish_candidate` /
`publish_required`. Distinct from `status` (workflow state). 122
rows backfilled.

**Where to look when something stops working.**
- Blog published with no citations → check
  `stats_snapshot['deliberation']['claims_count']`; if zero,
  the writer ran with an empty ClaimsPack — check SpiderData
  freshness for the topic domain.
- Reviewer never produces a FAIL even when the draft is wrong →
  check whether the v1 path is being hit instead of v2 (the
  endpoint matters).
- "I injected context but it's not in the blog" → almost always
  the `BaseAgent._build_intelligent_prompt()` vs
  ContentWriterAgent's parallel prompt builders confusion. The
  writer uses its own.
- Blogs stuck in `needs_enhancement` for days → check
  `auto_enhance_blogs` beat schedule and the `content` queue.
  Also check `stats_snapshot['enhancement_count']` — past 3, the
  task skips.
- Approved blogs never become `published` → 6 AM
  `auto_publish_approved_blogs` task; check beat schedule and
  whether the daily run completed.
- Deliverables all have `quality_score = 0.7` → the
  `score_unscored_deliverables` heuristic is not running; check
  every-6h-at-:15 beat schedule on the `default` queue.
- Blog cites stale data → check 14-day knowledge-freshness
  window (covered in `AGENTS_AND_AUTONOMY.md` milestone 4) +
  the FactCheckReviewer's freshness check (<48h on citation
  URLs).

---

## 6. Open questions / unknown outcomes

- **What's the v1 vs v2 split in production right now?**
  *Known:* both paths exist; v2 is reached via
  `POST /api/v1/research/self-blog/generate-v2/`. *Unknown:*
  what proportion of generated blogs use v1 vs v2 in the
  current beat schedule, and whether v1 should be sunset. A
  per-blog audit of `stats_snapshot['deliberation']` presence
  would answer this — present = v2, absent = v1.
- **Are PublishGate thresholds (0.75 / 0.60 / 0.55) still right?**
  *Known:* the constants are baked into the gate. *Inferred:*
  they were calibrated when blogs were the dominant artifact
  type. *Unknown:* whether the current blog distribution
  reflects what those thresholds were tuned for, or whether the
  artifact mix has shifted.
- **Should `auto_enhance_blogs` move off `gpt-4o-mini`?**
  *Known:* the topic doc flags it as a candidate for upgrade.
  *Unknown:* cost-vs-quality math is not in the corpus. A few
  enhancement runs at higher-tier models with quality-score
  delta would answer this.
- **The 116-blog backlog from Session 1033 — what shape is it
  in now?** *Known:* first-run cleared 6 blogs and moved 18 to
  `pending_review`. *Unknown:* current backlog count. A simple
  `SelfBlog.objects.filter(status='needs_enhancement').count()`
  would answer this; not currently surfaced.
- **`stats_snapshot['enhancement_count']` skip-after-3 policy.**
  *Known:* the cap prevents infinite loops. *Unknown:* what
  happens to a blog that hits the cap and still isn't
  publishable — is it manually triaged, archived, or just left?
  No automated path forward is documented.
- **Is the v1 path being used as A/B testing as intended, or as
  a fallback when v2 fails?** *Known:* the topic doc says
  "Different entry points for A/B testing". *Inferred:* nothing
  prevents v1 from being used as a silent fallback if v2
  errors. *Unknown:* whether v1 use is tracked and rationale
  is recorded per-call.
- **PA review feedback (Session 990) — is it surfacing in
  practice?** *Known:* the wiring exists end-to-end (`PA action
  → _record_content_feedback() → AgentMemory + UserAgentLearning
  → FeedbackLoopEngine → agent_router.gather_context() →
  spider_context`). *Unknown:* whether ContentWriterAgent's
  prompt is actually surfacing `pa_review_feedback` /
  `pa_review_summary` in its system prompt, or whether the
  feedback context is being silently dropped at the agent's own
  prompt builder layer.
- **`[Research]` / `[Audit]` / `[Internal]` bypass — what's the
  scale of operational-bypass usage?** *Known:* the bypass
  exists for legitimate internal artifacts. *Unknown:* how
  often it's triggered, and whether any "real public blogs"
  have been inadvertently routed through it by an upstream
  title-generator.

---

## 7. Source index

### Primary doc sources

- `docs/topics/content-pipeline.md` — current-state topic doc;
  the closest companion. Most session citations originate
  there.
- `docs/AGENTS.md` — DecisionEnforcerAgent and
  ContentDeliberationRunner detail; relevant to milestone 2
  and to the agent-narrative cross-references.
- `docs/PLATFORM_INVENTORY.md` — runtime-derived inventory; the
  authoritative source for any count.
- `docs/narratives/AGENTS_AND_AUTONOMY.md` — companion narrative.
  Cross-references: DecisionEnforcer (this doc § 2, that doc §
  3 milestone 3); spider context fabrication (this doc § 3
  milestone 5, that doc § 3 milestone 4); governance gates
  (this doc § 3 milestone 8, that doc § 3 milestone 7).

### Named session handoffs cited above

- `docs/handoffs/SESSION_964_CONTENT_DELIBERATION_PIPELINE.md` —
  the v2 architecture introduction (architectural watershed).
- `docs/handoffs/SESSION_997_MYTHOLOGY_PUBLISHGATE.md` — gate
  threshold hardening.
- `docs/handoffs/SESSION_1000C_CONTENT_REVIEW_AUTOMATION.md` —
  scheduled tasks + status promotion.
- `docs/handoffs/SESSION_1001_BLOG_TELEMETRY_GROUNDING.md` —
  operational telemetry grounding.
- `docs/handoffs/SESSION_1002_SPIDER_CONTEXT_FABRICATION_FIX.md`
  — spider URL fabrication path closed.
- `docs/handoffs/SESSION_1003_PIPELINE_COMPLETION.md` and the
  Session 1033 handoff series — content finishing loop +
  deliverable quality scoring.
- `docs/handoffs/SESSION_1089_GOVERNOR_AND_GROUNDING.md` —
  Governor + grounding pass.
- Session 1095 handoff — `publish_intent` enum migration.
  Memory file: `project_session_1095_coo_gates_complete.md`.
  MEMORY.md feedback entry: `feedback_publish_intent_enum.md`.

### Code anchors

- `core/services/content_review_panel.py` — v1 panel
  (untouched, still reachable).
- `core/services/content_review_panel_v2.py` — v2 panel.
- `core/services/content_deliberation_runner.py` — v2 runner.
- `core/agents/content_writer_agent.py` — ContentWriterAgent
  (own prompt builder, not BaseAgent's).
- `core/agents/decision_enforcer_agent.py` — DecisionEnforcer.
- `core/services/content_scoring_service.py` — heuristic /
  rule-based reach/intent/replicability scoring.
- `core/services/llm_provider_registry.py` — canonical LLM
  call shape; reviewers and writers route through this.
- `core/tasks.py` — `_build_operational_context()`,
  `evaluate_unscored_blogs`, `auto_enhance_blogs`,
  `enhance_all_blogs_needing_enhancement`,
  `reevaluate_enhanced_blogs`, `auto_publish_approved_blogs`,
  `score_unscored_deliverables`.
- `core/models_self_blog.py` (or equivalent) — `SelfBlog` model
  with `stats_snapshot`.

### Verification commands

- `python manage.py generate_platform_inventory` — regenerate
  the inventory anchor.
- `python manage.py verify_doc_claims --only-drift` — list
  which claims drift from runtime (Session 1099 verifier).
- `python manage.py build_docs_index` — refresh `docs/INDEX.md`
  + `docs/_index.json` after any doc edit.

---

## 8. Canonical sources (for future editors)

> **Reading this doc for ops decisions?** Treat code and config as
> canonical, not prose. The narrative captures *why* things are
> the shape they are; runtime captures *what they are now*.

| Question | Canonical source (code/config wins over prose) |
|---|---|
| Counts (blogs by status, deliverables, scores) | `docs/PLATFORM_INVENTORY.md` + live DB queries |
| Beat cadence (every 2h / every 4h / 6 AM, etc.) | `PeriodicTask` rows + `core/celery.py` schedule entries |
| PublishGate thresholds (0.75 / 0.60 / 0.55) | Constants inside the PublishGate module |
| Bypass title prefixes (`[Research]` etc.) | Constants/list inside the gate module |
| `publish_intent` enum values | Migration 0333 + the Deliverable model field |
| LLM model used by EditorAgent / writer / reviewers | Provider registry config |

If you spot drift between this doc and code/config, **code wins**
and this doc should be corrected. See
[`docs/narratives/EDITING_GUARDRAILS.md`](EDITING_GUARDRAILS.md)
for the editing contract.


---
title: "Domain Research Playbook — standard process for deep domain audits"
status: active
authority: process
session_added: 1274
last_verified: 2026-07-01
companion_anchors:
  - docs/research/platform_architecture_inventory.md   # 32-domain map (S1273)
  - docs/research/platform/cross_domain_integration_audit.md  # integration gaps (S1274)
  - docs/research/ARCHITECTURE_INDEX.md                # library navigation (v5)
  - docs/PLATFORM_INVENTORY.md                          # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                         # narrative anchor
  - docs/EMPLOYEE_OS_PRIMITIVES.md                     # anti-duplication matrix
  - docs/00-START-HERE/DOC_LIFECYCLE.md                # doc governance
verifier_loop: |
  v1 (2026-07-01, S1274): playbook drafted to codify the research
  methodology developed across S1268-S1274 (comms substrate, comms
  protocol sketch, collaboration patterns, governance/authority
  evolution, symbol mapping, actor identity, authority enforcement
  design space, whole-platform inventory, cross-domain integration
  audit). No new methodology invented; playbook standardizes what
  worked. Not routed to Rigby — this is process documentation, not
  a research finding.
owner: claude (drafted S1274)
---

# Domain Research Playbook

> **What this is.** A reusable process document that lets any future
> Claude Code session start a deep domain audit with a short
> request like "Start research group 1300: Memory." The playbook
> codifies the methodology developed across Sessions 1268–1274 so
> Chris does not have to write a massive prompt every time.
>
> **What this is not.** A domain audit itself. A rewrite proposal.
> A methodology innovation. Everything here is what already worked
> in S1268–S1274; the playbook just makes it repeatable.
>
> **How to use.** When Chris says "Start research group NNNN: X"
> (see §11), Claude reads this playbook first, then executes the
> standard mission shape without further prompting.

---

## 1. Purpose

This playbook standardizes deep domain audits across Donkey Betz.
The platform has 32 documented domains (per
`docs/research/platform_architecture_inventory.md` §2). Most are
under-researched. Every domain deserves at least one focused audit
before decisions get made about it — before extraction is
proposed, before enforcement is added, before wiring is changed.

The methodology proven across S1268–S1274:

1. **Read first.** Load the domain's existing docs + research
   library + parent inventory row before touching code.
2. **Sweep with parallel Explore sub-agents.** Six parallel
   sub-agents per audit (see §7).
3. **Synthesize into one document.** Follow the 20-section
   structure in §5.
4. **Verifier loop.** Every claim gets a file:line cite or an
   explicit UNKNOWN.
5. **Rigby SIGN review.** Independent pressure-test on a fresh
   isolation pin (see §9).
6. **Fold edits.** SIGN-with-edits verdicts fold into the doc
   before it's considered publishable.
7. **Chris gates commits.** Nothing lands in `main` without
   Chris's explicit "commit it" instruction.

The playbook exists because this loop is expensive to re-derive
from scratch each session. Chris typed ~4,000 words for S1273 and
S1274 combined. This playbook lets a future session start with 8
words.

---

## 2. Research Group Numbering

Session IDs are grouped into planning ranges. **The ranges are
labels for what the research is about — not runtime identifiers,
not code enforcement, not project keys.** They exist so the
research library's timeline (`ARCHITECTURE_INDEX.md` §8) reads as
a coherent narrative.

| Range | Theme | Rationale |
|---|---|---|
| **1200s** | Employee OS / Authority / Platform inventory foundation | Sessions 1268–1274 already shipped: 8 research docs + integration audit. Foundation is set. |
| **1300s** | Memory / Knowledge / Embeddings | Next queue slot. Domain has DEEP inventory coverage (S1273 §3.13) but LIGHT integration analysis. |
| **1400s** | Revenue / Outreach / Engagement | Rigby-caught missed domain in S1273; LIGHT coverage. Highest business-value under-researched domain. |
| **1500s** | Sports / DBAO / Intelligence | Structural question: island vs integrated (S1274 §12.3). Cannot be resolved without dedicated domain audit. |
| **1600s** | Content / Deliverables / Publishing | Well-inventoried but integration analysis needed (S1274 §5.3 flagged intentional split; §7.4 flagged intentional orchestrators). |
| **1700s** | Observability / Telemetry / SLOs | 5-layer execution telemetry + 14+ event models; dedup audit named by S1273 §5.13 + S1274 §12.6. |
| **1800s** | HumanAttention / Feedback / Learning | Only round-trip learning loop today (S1274 §2.5); ripe for scope expansion research. |
| **1900s** | Event / Integration / Runtime Architecture | Downstream of S1274 §12.1 EventBus Adoption + Contract Verification. |

**Rules for the numbering:**

- A "research group" is a set of related audits, not a single
  session. Group 1300 might span S1300–S1319 depending on how
  deep Memory needs to go.
- The first session in a group is the group's parent audit. Any
  spin-off sessions (e.g., "Memory Freshness SLO Design") come
  after and cite the parent.
- If the domain is bigger than expected, splitting into
  sub-groups is fine. Do not force a single session to cover a
  multi-subsystem domain.
- Ranges are targets, not caps. Group 1300 could bleed into
  S1320s if warranted.

---

## 3. Standard Domain Audit Output

Every domain audit produces exactly one canonical file:

```
docs/research/domains/<domain_slug>/<session_id>_<domain_slug>_architecture_audit.md
```

**Examples:**

- `docs/research/domains/memory/1300_memory_architecture_audit.md`
- `docs/research/domains/revenue/1400_revenue_architecture_audit.md`
- `docs/research/domains/sports/1500_sports_architecture_audit.md`

**Directory creation.** If `docs/research/domains/<domain_slug>/`
does not exist, create it as part of the mission. Do not batch
directory creation into a separate PR.

**Domain slug rules:**

- Lower-case, single word or hyphenated.
- Match the S1273 domain name where possible.
- Preferred slugs for the planned queue: `memory`, `revenue`,
  `sports`, `content`, `observability`, `human-attention`,
  `event-architecture`.

**File-name numeric prefix.** The prefix is the parent-audit
session_id, not a version. If a follow-up session extends the
audit, it creates a **new file** with its own session_id, and the
new file adds a `## 0. Supersedes` header referencing the parent.
Do not overwrite the parent.

---

## 4. Standard Domain Audit Questions

Every domain audit must answer these 27 questions. Some questions
may be answered "UNKNOWN" or "not applicable" — that is acceptable
per §8.

1. What is this domain for? *(one-sentence purpose)*
2. What problem does it solve? *(the business or platform
   problem, distinct from #1)*
3. What are the canonical entry points? *(files, URLs, PA tools,
   management commands)*
4. What are the major models? *(with file:line)*
5. What are the major services? *(with file:line)*
6. What are the major APIs? *(REST, WebSocket, PA tools)*
7. What are the major Celery tasks? *(with beat schedule if
   applicable)*
8. What are the major management commands? *(with file:line)*
9. What are the major runtime flows? *(sequence diagrams or
   step-by-step)*
10. What existing documentation exists? *(topic docs, handoffs,
    narratives)*
11. What research already exists? *(research library entries in
    ARCHITECTURE_INDEX §1)*
12. What is the architecture maturity? *(§6 classification)*
13. What is the research coverage? *(§6 classification)*
14. What integrations does it have? *(with which of the 32
    domains — reference S1273 §2)*
15. What integrations are missing? *(reference S1274 §3 gaps)*
16. What data does it own? *(models exclusive to this domain)*
17. What data does it consume? *(from other domains)*
18. What data does it produce? *(for other domains)*
19. What events does it emit? *(with file:line producers)*
20. What events should it emit? *(gaps — reference S1274 §6)*
21. What other domains depend on it? *(inbound consumers)*
22. What domains does it depend on? *(outbound dependencies)*
23. What models overlap with other domains? *(reference S1274 §5
    duplicate/overlap analysis)*
24. What services violate boundaries? *(reference S1274 §7
    boundary violations)*
25. What ownership is unclear? *(reference S1274 §10)*
26. What is technical debt? *(with severity per §6)*
27. What is drift? *(with evidence)*
28. What should be researched next? *(recommended follow-on
    missions, not implementation plans)*

**Ordering rationale.** Questions 1–2 set frame. 3–9 inventory
what exists. 10–13 assess research state. 14–22 handle
integration lens (the S1274 discipline). 23–27 identify problems.
28 opens the next mission.

---

## 5. Standard Document Structure

Every domain audit uses this 20-section skeleton. Section
headings are exact — do not rename. Section order is fixed. If a
section has no findings, keep the heading and note the reason
(e.g., "No known circular dependencies; searched patterns X, Y,
Z").

```markdown
# <Domain Name> Architecture Audit

## 1. Executive Summary
## 2. Domain Purpose
## 3. Canonical Entry Points
## 4. Major Models
## 5. Major Services
## 6. Major APIs and Interfaces
## 7. Runtime Flows
## 8. Data Ownership and Lifecycle
## 9. Integrations With Other Domains
## 10. Event Flows
## 11. Existing Documentation
## 12. Research Coverage
## 13. Architecture Maturity
## 14. Known Drift
## 15. Known Technical Debt
## 16. Boundary Violations
## 17. Duplicate or Overlapping Systems
## 18. Ownership Gaps
## 19. Recommended Future Research
## 20. Appendix
```

**Frontmatter template** (place at the top of every audit):

```yaml
---
title: "<Domain Name> Architecture Audit"
status: draft
authority: research
session_added: <session_id>
last_verified: <YYYY-MM-DD>
companion_anchors:
  - docs/research/platform_architecture_inventory.md   # parent inventory
  - docs/research/platform/cross_domain_integration_audit.md  # cross-domain lens
  - docs/research/ARCHITECTURE_INDEX.md                # library navigation
  - docs/PLATFORM_INVENTORY.md                          # runtime anchor
  - <any domain-specific docs>
verifier_loop: |
  v1 draft (<YYYY-MM-DD>, S<session_id>): six parallel Explore sub-agents
  produced independent sweeps (see §20 Appendix). Parent (Claude)
  synthesized into 20-section audit. Every claim grounded in
  file:line cites OR flagged UNKNOWN per playbook §8. Rigby SIGN
  review pending.
owner: claude (drafted S<session_id>)
---
```

**Section requirements:**

- **§1 Executive Summary** — Answer: what is this domain, what
  are the biggest gaps, what should be researched next. 300–500
  words maximum.
- **§2 Domain Purpose** — Question #1 + #2 from §4.
- **§3 Canonical Entry Points** — Question #3 with file:line.
- **§4–§8** — Questions #4–#9.
- **§9 Integrations With Other Domains** — Questions #14 + #17 +
  #18 + #21 + #22. Table format preferred.
- **§10 Event Flows** — Questions #19 + #20.
- **§11–§13** — Questions #10–#13.
- **§14–§18** — Questions #23–#27.
- **§19 Recommended Future Research** — Question #28. Rank by
  architectural uncertainty × risk × unblocked flows.
- **§20 Appendix** — Files inspected, docs inspected, grep
  patterns used, unresolved unknowns, conflicts between sources,
  verifier-loop corrections (Rigby SIGN fold notes go here).

---

## 6. Classification Rules

Reuse the classifications developed across the S1268–S1274
research library. Do not invent new classifications per audit.

### Research Coverage

- **NONE** — no meaningful docs beyond code/comments.
- **LIGHT** — some docs or handoffs exist, but no dedicated
  architecture research.
- **MODERATE** — at least one focused doc or meaningful canonical
  documentation exists.
- **DEEP** — multiple focused docs, audits, or research docs
  exist.
- **CANONICAL** — clear source-of-truth docs exist and are
  actively maintained.

### Architecture Maturity

- **EXPERIMENTAL** — prototype, unstable, unclear ownership.
- **PARTIAL** — works in places but not cohesive or fully wired.
- **WORKING** — operational, used, but with gaps or drift.
- **STABLE** — operational, tested, documented, few known gaps.
- **CANONICAL** — stable, documented, verified, treated as
  source of truth.

### Risk

- **LOW**
- **MEDIUM**
- **HIGH**
- **CRITICAL**
- **UNKNOWN**

### Finding Type

Use the exact strings from S1274 §11 for cross-audit
consistency:

- `missing_connection`
- `overcoupling`
- `duplicate_model`
- `event_gap`
- `boundary_violation`
- `circular_dependency`
- `unclear_owner`
- `drift`
- `technical_debt`
- `extraction_candidate`
- `mature_primitive`
- `dead_code`
- `unknown`

---

## 7. Standard Explore-Agent Sweeps

Every domain audit spawns exactly six parallel Explore sub-agents.
Sequential sweeps waste context and slow the mission down;
parallel sweeps have been the proven S1268–S1274 pattern.

Send all 6 in a single message with 6 tool-use blocks (parallel
tool calls). Do not batch sequentially.

### Agent 1 — Models and Persistence

**Focus:** Django models owned by this domain, foreign-key graph
to models outside the domain, migration lineage,
retention/lifecycle policies, unique constraints, indexes.

**Deliverable:** Model inventory with file:line, ownership
classification (this-domain vs shared vs foreign), overlap flags
that cross-reference S1273 §5 (duplicate/overlapping systems).

### Agent 2 — Services and Runtime Flows

**Focus:** Service layer (`core/services/*`, `core/agents/*` if
domain has agents, `core/employees/*` if domain has employees),
runtime flow diagrams, lazy imports, dependency chains,
god-service checks (line count + cross-domain imports).

**Deliverable:** Service inventory with file:line, runtime flow
step-by-step, god-service ranking if any exceed 3000 lines.

### Agent 3 — APIs, Tools, Tasks, Commands

**Focus:** REST endpoints, WebSocket consumers, PA tools
(td_handlers), Celery tasks (with beat schedule if applicable),
management commands. Cross-reference `docs/PLATFORM_INVENTORY.md`
autoblock for counts.

**Deliverable:** External-facing surface inventory with file:line,
beat-schedule cadence, tool schemas if applicable.

### Agent 4 — Integrations and Cross-Domain Dependencies

**Focus:** Which of the 32 domains this domain talks to or should
talk to. Reference `docs/research/platform/cross_domain_integration_audit.md`
§2 (integration map) as starting point. Verify current wiring vs
what's documented.

**Deliverable:** Inbound + outbound integration map, missing
connections, overcoupled surfaces, event flow analysis.

### Agent 5 — Documentation and Prior Research

**Focus:** Existing docs about this domain — topic docs
(`docs/topics/`), handoffs (`docs/handoffs/`), narratives
(`docs/narratives/`), any prior research library entries
(`docs/research/`). Explicit gap analysis: what does existing
documentation NOT cover?

**Deliverable:** Documentation inventory, research coverage
classification, explicit "already covered by X" pointers to avoid
duplication in the new audit.

### Agent 6 — Drift, Debt, Ownership, and Maturity

**Focus:** Known drift (docs say X, runtime says Y), technical
debt (with severity), ownership gaps, maturity assessment
(EXPERIMENTAL/PARTIAL/WORKING/STABLE/CANONICAL).

**Deliverable:** Drift matrix, debt matrix with severity,
ownership row per §4 question #25, maturity verdict with evidence.

### Parent Agent (Claude) Synthesis

After all 6 sub-agents return:

1. Merge duplicate findings.
2. Resolve conflicts by direct file:line reads (verifier loop —
   trust but verify).
3. Spot-check load-bearing claims with independent grep/read.
4. Mark UNKNOWNs honestly (§8).
5. Write the 20-section audit per §5.
6. Route to Rigby per §9.

---

## 8. Standard Evidence Rules

- **File:line citations for load-bearing claims.** Every claim
  that could affect a downstream decision must cite the source.
  Do not paraphrase code without a cite.
- **Direct source verification for important findings.** If a
  sub-agent asserts something load-bearing, the parent agent
  verifies by reading the cited file:line before including it.
  This is the "trust but verify" rule from the S1273 Rigby
  reviews.
- **Unknowns marked honestly.** "UNKNOWN" is a valid finding.
  Guessing is not. When you infer intent from code without a
  documented rationale, flag as **SPECULATIVE**.
- **No speculation presented as fact.** If Rigby will grep and
  catch a wrong claim, better to flag it as SPECULATIVE now.
  (S1274 v1 mis-classified EventBus as "dormant"; Rigby caught
  it by direct grep. That's the failure mode this rule prevents.)
- **Count conflicts resolved against runtime/canonical
  inventory.** When two sources disagree on a count (agent count
  83 vs 90, PA tools 104 vs 113), `PLATFORM_INVENTORY.md`
  autoblock wins per `DOC_LIFECYCLE.md` §2c. Cite the winner;
  flag the drift.
- **No implementation during research.** Research is research.
  Do not open PRs, do not modify runtime code, do not create
  migrations, do not "fix while you're in there." The whole
  point of the research library is that PRs come later and
  reference research.

---

## 9. Standard Rigby Review

Every domain audit routes to Rigby for a human-style architecture
review. Rigby is not a rubber stamp — she independently greps the
codebase and catches factual errors (S1274 lesson).

### Fresh isolation pin

Per S1273/S1274 practice, use a **fresh isolation pin** if the
current arc pin might be shared with another Claude Code
session. Generate via:

```bash
python3 -c "import secrets; print(f'pa-{secrets.token_hex(8)}')"
```

Invoke `pa_chat.py` with explicit `--conversation` override; do
**not** modify `tools/pa_local.sh` if other Claude Code sessions
depend on the shared pin. Retire the isolation pin at session
close.

### Ask Rigby to pressure-test

```
1. Did Claude miss any major parts of this domain?
2. Did Claude overstate maturity?
3. Did Claude understate maturity?
4. Did Claude confuse intentional separation with missing
   integration?
5. Did Claude identify the right technical debt?
6. What is the riskiest finding?
7. What is the most important future research?
8. What did Claude get wrong?
9. What must change before canonical?
```

### Response format Rigby uses

```
Overall confidence: High / Medium / Low

Most accurate part:

Weakest part:

Missing area:

Overstated maturity:

Understated maturity:

Biggest architectural risk:

Most important next research:

What Claude got wrong:

What must change before canonical:

Final verdict: SIGN-clean / SIGN-with-edits / NEEDS-MORE
```

### Folding edits

- **SIGN-clean** — no changes needed. Update frontmatter
  `verifier_loop` with "Rigby SIGN-clean" note. Move on.
- **SIGN-with-edits** — fold every substantive edit into the doc
  before it's considered publishable. Update frontmatter
  `verifier_loop` field with fold summary (what was changed +
  why). Preserve the v1 note.
- **NEEDS-MORE** — Rigby thinks the audit isn't ready. Do not
  publish. Address her concerns, re-audit if needed, re-route.

### Rigby's grep-verification pattern

Rigby regularly verifies claims by direct `repo_tool.search` +
`repo_tool.read_file`. If your audit contains a factual claim
that will fail a 3-second grep, expect her to catch it. Front-run
this by grepping your own claims before shipping to her.
Especially: **binary "X is dormant/absent/missing" claims**. The
S1274 EventBus lesson: "wiring dormant" was wrong; "partially
adopted" was right. Rigby found 5 publisher wrappers + 3
consumer tasks by direct grep in under a minute.

---

## 10. Commit Rules

**Default: do not commit.** Every research audit lands as a
`status: draft` document in an uncommitted state. Chris reviews,
then explicitly says "commit it" (or similar). Only then does the
commit happen.

**When Chris says commit:**

1. Update `docs/research/ARCHITECTURE_INDEX.md`:
   - Add a new §1.N row for the audit (see the S1273 §1.9 or
     S1274 addition pattern).
   - Update §8 timeline with a new row.
   - Update §3 domain map row if this audit changes the maturity
     or coverage rating for the domain.
   - Update §5 gap entries if this audit closes any prior gap or
     opens new ones.
   - Update §7 decision matrix if this audit adds a new class of
     work worth flagging.
   - Update §9 roadmap lateral research list if this audit
     changes what's queued next.
   - Bump frontmatter `last_verified` and `owner` fields.
   - Add Appendix pass notes for the version bump.
2. Register the audit's file in a new commit.
3. Stage **only** `docs/research/` files unless Chris explicitly
   approves other changes.
4. Commit message format:

   ```
   docs(research): add <domain> architecture audit (S<session_id>)

   <one-paragraph summary of biggest findings + Rigby SIGN status>

   Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
   ```

**Never commit without:**

- Explicit Chris instruction.
- Rigby SIGN status resolved (SIGN-clean or SIGN-with-edits
  folded — not NEEDS-MORE).
- All frontmatter fields populated.
- `verifier_loop` note current.

**Never modify:**

- Runtime code (`core/*.py` outside `core/services/pa_tool_schemas.py`
  as a docs edge case).
- Migrations.
- Generated inventories (`docs/PLATFORM_INVENTORY.md`,
  `docs/INDEX.md`) — those come from `manage.py generate_platform_inventory`
  or `manage.py build_docs_index`, not hand edits.
- Anything in `tools/` unless it's a research-only tool.

---

## 11. Short Start Commands

Chris uses these to open a research session:

```
Start research group 1300: Memory
Start research group 1400: Revenue
Start research group 1500: Sports Intelligence
Start research group 1600: Content and Publishing
Start research group 1700: Observability
Start research group 1800: HumanAttention and Learning
Start research group 1900: Event Architecture
```

### How Claude infers the mission shape

Given a command like `Start research group 1300: Memory`, Claude
extracts:

- **`session_id`** — the numeric prefix (e.g., `1300`). If Chris
  wants to number differently within the range, he'll specify.
  Otherwise default to the range's first slot.
- **`domain_slug`** — lowercase single-word or hyphenated form of
  the domain name (e.g., `memory`, `revenue`, `sports`,
  `content`, `observability`, `human-attention`,
  `event-architecture`).
- **`output_path`** —
  `docs/research/domains/<domain_slug>/<session_id>_<domain_slug>_architecture_audit.md`.
- **Standard audit structure** — the 20 sections from §5, with
  frontmatter template from §5.
- **Sub-agent sweeps** — 6 parallel Explore agents per §7.
- **Rigby review** — per §9. Generate a fresh isolation pin.

### Standard opening sequence

1. Read the parent inventory row: `docs/research/platform_architecture_inventory.md`
   §3.N for this domain.
2. Read the cross-domain audit row(s): `docs/research/platform/cross_domain_integration_audit.md`
   §2.N (integration map) + any relevant §3 / §4 / §5 findings
   for this domain.
3. Read the ARCHITECTURE_INDEX row: `docs/research/ARCHITECTURE_INDEX.md`
   §3 (domain map) + §5 (gaps) entries for this domain.
4. Read existing docs for the domain (topic docs, handoffs,
   narratives). Do not duplicate their content in the audit;
   cite them.
5. Create the output directory + file per §3.
6. Launch 6 parallel Explore sub-agents per §7.
7. Synthesize per §5.
8. Route to Rigby per §9.
9. Fold SIGN-with-edits into the doc.
10. Return summary to Chris per §14. **Do not commit** unless
    Chris asks (§10).

---

## 12. Initial Domain Queue

The following research groups are planned. Order is a
recommendation; Chris can pick any of them next.

| Range | Domain | S1273 §3 Row | Coverage | Priority Rationale |
|---|---|---|---|---|
| 1300 | Memory / Knowledge / Embeddings | §3.13 | DEEP inventory / LIGHT integration | Foundation for cross-domain feedback loops; two RAG lanes need call-time selector research |
| 1400 | Revenue / Outreach / Engagement | §3.32 | LIGHT | Rigby-caught missed domain (S1273 v2); business-value highest under-researched domain |
| 1500 | Sports / DBAO / Intelligence | §3.10 | LIGHT | Resolves platform's biggest structural question (island vs integrated per S1274 §12.3) |
| 1600 | Content / Deliverables / Publishing | §3.11 | MODERATE | Well-inventoried; integration analysis needed (S1274 §5.3, §7.4) |
| 1700 | Observability / Telemetry / SLOs | §3.25 | DEEP | 5-layer telemetry dedup audit named by S1273 §5.13 + S1274 §12.6 |
| 1800 | HumanAttention / Feedback / Learning | §3.16 | MODERATE | Only round-trip learning loop today; scope expansion research |
| 1900 | Event / Integration / Runtime Architecture | §3.31 | LIGHT | Downstream of S1274 §12.1 EventBus Adoption + Contract Verification |

**Note on ordering.** The queue above is default; Chris can pick
any of them next. If Chris opens `Start research group 1500`
before `1300`, Claude executes the sports mission without
requiring the memory mission to land first. The ranges are
labels, not dependencies.

**Cross-references to existing research.** Each group inherits
the findings from S1268–S1274 relevant to its domain. See §13.

---

## 13. Relationship to Existing Research

This playbook does not create new methodology — it standardizes
what already worked across S1268–S1274. Reference these prior
missions when starting any new domain audit:

- **S1268 — Employee OS Communication Substrate Audit + Protocol
  Sketch + Collaboration Patterns.** Established the reuse-first
  discipline (do not build a new model when a wrapper suffices)
  + the 64-row primitives inventory pattern + the failure-modes
  inventory pattern.
- **S1269 — Governance / Authority Evolution.** Established the
  4-plane inventory pattern (per-plane inventory + composition
  gap analysis) + the "35 gates" enumeration style.
- **S1270 — Symbol Mapping Architecture.** Established the
  design-space enumeration style (5 options with tradeoffs, no
  selection) + the "F-finding" numbering.
- **S1271 — Actor Identity & Attribution Architecture.**
  Established the multi-role vocabulary pattern (executor_actor /
  sponsor_actor / principal_user) + the "22 attribution
  surfaces" grid.
- **S1272 — Authority Enforcement Design Space.** Established
  the design-space-only maintenance note + the 6-options-A-F
  pattern + the DAG-of-prerequisites style.
- **S1273 — Whole-Platform Architecture Inventory.** Established
  the 32-domain map + 9 cross-domain flows + Maturity Matrix +
  Coverage Map + 11-mission roadmap pattern. Rigby-caught missed
  domain (Revenue) taught the lesson: "if a real domain is
  missing, sub-agent sweeps didn't cover it — trust Rigby's
  independent grep."
- **S1274 — Cross-Domain Integration Audit.** Established the
  integration-lens shape (not another inventory) + the
  "producer/consumer registry" style + the "STRONG/WEAK/MISSING/
  OVERCOUPLED/UNKNOWN" pair classification. Rigby-caught
  binary-classification error ("EventBus dormant" → "partially
  adopted") taught: **do not use binary language for continuous
  reality**.

**The library's shape** (per `ARCHITECTURE_INDEX.md` v5):

- Employee OS deep arc: `§1.1 → §1.2/§1.3 → §1.4 → §1.6 → §1.7 →
  §1.8`.
- Whole-platform sibling arc: `§1.9` (inventory) →
  `docs/research/platform/cross_domain_integration_audit.md`
  (integration audit).
- Domain research group (this playbook drives): `docs/research/domains/<slug>/`
  entries will populate as each research group runs. Each new
  audit becomes a new `§1.N` row in ARCHITECTURE_INDEX §1.

**Anchor discipline** (from S1268 onward): every audit lists
`companion_anchors` in frontmatter. The load-bearing anchors are:

- `docs/PLATFORM_INVENTORY.md` — runtime counts (autoblock wins
  on conflict).
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor (glossary).
- `docs/EMPLOYEE_OS_PRIMITIVES.md` — canonical primitives +
  anti-duplication matrix (always cite before proposing any
  new model).
- `docs/00-START-HERE/DOC_LIFECYCLE.md` — doc governance rules
  including the inventory-wins-on-conflict rule (§2c).
- `docs/research/ARCHITECTURE_INDEX.md` — library navigation.
- `docs/research/platform_architecture_inventory.md` — 32-domain
  map.
- `docs/research/platform/cross_domain_integration_audit.md` —
  integration gap map.

Any audit that misses these anchors is broken at the root.

---

## 14. Final Self-Check

Before returning a mission summary, verify:

- [ ] The playbook or audit does **not** start a domain audit
      unless Chris said "Start research group NNNN: X" (this
      playbook is process documentation; it does not audit).
- [ ] The playbook or audit does **not** make runtime changes.
      Zero touches to `core/*.py` (runtime), migrations, or
      generated inventories.
- [ ] The playbook gives Chris short commands he can reuse
      without a fresh 4,000-word prompt (§11).
- [ ] The playbook is clear enough for a fresh Claude Code with
      no extra prompt. Test: could an agent that has never
      opened this repo before, but has read this playbook,
      execute "Start research group 1300: Memory" end-to-end?
      (§4–§10 must cover this.)
- [ ] The playbook references
      `docs/research/ARCHITECTURE_INDEX.md` and
      `docs/research/platform_architecture_inventory.md` as
      required starting points (§13 does).
- [ ] The playbook references
      `docs/research/platform/cross_domain_integration_audit.md`
      for cross-domain integration context (§9 + §13 do).
- [ ] All frontmatter fields populated: `title`, `status`,
      `authority`, `session_added`, `last_verified`,
      `companion_anchors`, `verifier_loop`, `owner`.
- [ ] Isolation-pin pattern documented (§9) so future sessions
      don't cross context with parallel Claude Code sessions.
- [ ] Commit rules explicit (§10) so nothing lands in `main`
      without Chris's approval.

Return summary to Chris including:

- File created (`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`).
- Summary of the 14 sections.
- Whether `docs/research/ARCHITECTURE_INDEX.md` should be
  updated **now** (to register the playbook as a discoverable
  process document) or **only after first domain audit** (to
  keep the index focused on research findings, not process
  docs). This is a judgment call Chris should make.
- Any questions before Chris commits.

---

**Status.** Playbook active. No routing to Rigby (this is
process documentation, not a research finding). Do not commit
unless Chris explicitly asks.

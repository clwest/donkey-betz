---
title: "Claude Code Startup + Research Execution Introspection — S1276 meta-research"
status: draft
authority: process-audit
session_added: 1276
last_verified: 2026-07-01
companion_anchors:
  - CLAUDE.md
  - 00-START-NEXT-SESSION.md
  - docs/00-START-HERE/README.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/platform_architecture_inventory.md
  - .claude/skills/context-kit/SKILL.md
verifier_loop: |
  v1 (2026-07-01, S1276): drafted after the S1276 playbook v2 commit
  landed. Introspection is against Claude Code's *actual* startup
  behavior on the current session, cross-checked against grep of
  what CLAUDE.md, 00-START-NEXT-SESSION.md, the START-HERE index,
  and the S1276-current playbook actually say. Rigby SIGN pending.
owner: claude (drafted S1276)
---

# Claude Code Startup + Research Execution Introspection

> **What this is.** A meta-research audit of how Claude Code
> actually starts a session in `unified-donkey-betz` and how it
> starts a research mission. Written after the S1276
> `DOMAIN_RESEARCH_PLAYBOOK` v2 commit to check whether the new
> methodology docs match Claude Code's real startup behavior.
>
> **What this is not.** A domain audit. A new research group. An
> implementation plan. Everything here is process observation
> and doc-recommendation.
>
> **Constraint.** No runtime changes. No PRs. No migrations. Report
> only.

---

## Part 1 — Actual Startup Sequence

The observed sequence at S1276 open (this session), step by step.

### Step 1 — `context-kit orient` (Skill: `context-kit`)

- **Do I do it automatically?** **Yes**, per the memory rule
  `feedback_session_open_with_orient` (auto-loaded from
  `MEMORY.md`). Also reinforced by the `context-kit` Skill
  frontmatter which is injected via `<system-reminder>` at
  session open.
- **Mandated by docs?** **Partially.** CLAUDE.md does not
  mention `context-kit orient`. The Skill definition mandates
  it; the memory rule mandates it. Fresh Claude without the
  auto-memory would not know to run it unless the Skill
  triggers.
- **Learned from prior sessions?** **Yes** — the memory rule
  was surfaced across S1200s.
- **Manual / prompt-dependent?** No — this session invoked the
  Skill as the first tool call.
- **What triggers it?** The `context-kit` Skill availability
  banner in the `<system-reminder>` list at session open.
- **What info does it give?** Source-of-truth order,
  `00-START-NEXT-SESSION.md` contents, narrative + runtime
  anchor previews, latest handoff. Very load-bearing.
- **Still missing.** Orient output does NOT surface the
  `research/` library, does NOT tell me `DOMAIN_RESEARCH_PLAYBOOK`
  exists, does NOT reveal any research group's status. It is
  Employee OS-agnostic — treats research as generic docs.

### Step 2 — `CLAUDE.md` (auto-injected via `<system-reminder>`)

- **Do I do it automatically?** **Yes** — CLAUDE.md is injected
  in every session's opening context block.
- **Mandated by docs?** Yes, this is the project instruction
  channel per Claude Code convention.
- **Info I get.** Rigby-first comms, `pa_chat.py` usage,
  system stats, subsystem doc pointers, reference doc pointers.
- **Still missing.** CLAUDE.md does NOT reference
  `DOMAIN_RESEARCH_PLAYBOOK.md`, does NOT reference
  `ARCHITECTURE_INDEX.md`, does NOT reference
  `docs/research/*` at all. Grep confirms zero mentions. A
  fresh Claude reading only CLAUDE.md would not know the
  research library exists.

### Step 3 — `00-START-NEXT-SESSION.md` (via orient)

- **Do I do it automatically?** **Yes** — orient surfaces it
  as the "Start Here" block.
- **Info I get.** Current session priorities, RIGBY prod-vs-
  local trap warning, active PA conversation pin, current
  research arc status (e.g. S1300 → S1301 planning), FIRST
  THING checklist.
- **Still missing.** The FIRST THING checklist in S1300 handoff
  lists: (1) `context-kit orient`, (2) confirm
  `service_context: local` via `platform_config_tool overview`,
  (3) ask Chris to resolve open decisions, (4) begin playbook
  §11 opening sequence, (5) launch sub-agent sweep. **Note:**
  I did NOT execute step 2 (service_context check) at S1276
  open — I went straight from orient into reading the playbook.
  This is a **discipline gap**, not a doc gap.

### Step 4 — `ARCHITECTURE_INDEX.md` usage

- **Automatic?** **No.** I opened it because I needed it for
  the S1276 mission (extending §1.11). Nothing in orient or
  CLAUDE.md prompted me to read it at session start.
- **Mandated?** The playbook §21 opening sequence lists it as
  step 2 for research sessions. Not mandated for other
  sessions.
- **Info I get.** Library navigation, dependency graph, §7
  decision matrix ("about to work on X? read Y first"),
  timeline, roadmap.
- **Still missing.** The §7 decision matrix is arguably the
  single most useful early-read surface — it directly maps
  work intent to prior research. It is buried at ~line 1725
  of a 2100+ line doc; new readers rarely see it. And it is
  **not linked from CLAUDE.md**.

### Step 5 — `DOMAIN_RESEARCH_PLAYBOOK.md` usage

- **Automatic?** **No** — I opened it because S1276 was about
  extending it. For a plain domain-research start, the S1300
  handoff points to it, but nothing else does.
- **Mandated?** Playbook §11 declares itself as *first-read*
  for research sessions. Circular: you have to know the
  playbook exists to read the playbook.
- **Info I get.** Everything about how to run a research group.
- **Still missing.** Discoverability from CLAUDE.md and from
  the START-HERE INDEX. **A fresh Claude who opens CLAUDE.md
  and runs orient would not learn the playbook exists unless
  the current `00-START-NEXT-SESSION.md` happens to mention
  it.**

### Step 6 — `PLATFORM_INVENTORY.md` / `PLATFORM_WHAT_IT_IS.md` usage

- **Automatic?** **Partially** — orient surfaces the anchor
  previews (first ~50 lines each). Full read is manual.
- **Mandated?** DOC_LIFECYCLE.md §2c makes the inventory the
  authoritative counts source. CLAUDE.md points to both.
  Playbook §14 mandates citing them for counts.
- **Info I get.** Regenerable runtime counts (agents, tools,
  models, etc.) and the narrative anchor for platform shape.
- **Still missing.** For most sessions I do not fully read
  either — I use them as *lookup surfaces*. That is
  intentional. Discoverability is not the problem here.

### Step 7 — `git status` / branch detection

- **Automatic?** **Yes** — injected by the Claude Code harness
  in the Environment block.
- **Mandated?** Environmental — the harness prints it.
- **Info I get.** Current branch, uncommitted changes, recent
  commits.
- **Still missing.** No visibility into whether *another*
  Claude Code session is working the same branch or same PA
  pin. This is the biggest multi-Claude risk (see §4).

### Step 8 — Conversation pin / Rigby / `pa_local.sh` setup

- **Automatic?** **No** — I read the pin from
  `00-START-NEXT-SESSION.md` and trust it. I did not verify
  ownership at S1276 open.
- **Mandated?** Yes: memory rule
  `feedback_pa_local_verify_ownership` says verify hardcoded
  token → `donkeyking` on first use per session. Playbook §15
  says use fresh isolation pin if arc pin might be shared.
- **Info I get.** Which PA conversation to use, which token,
  which URL.
- **Still missing.** No pre-flight command to verify the pin's
  owner or check for other active sessions on it. Manual
  verification is prone to skip.

### Step 9 — `service_context: local` check

- **Automatic?** **No** — I did NOT do this at S1276 open.
  `00-START-NEXT-SESSION.md` mandates it as FIRST THING step
  2. Discipline gap.
- **Mandated?** Yes, `00-START-NEXT-SESSION.md` says do it
  before any `pa_chat.py` call.
- **Info I get.** Confirmation that Rigby is talking to local,
  not prod.
- **Still missing.** Should be part of orient output, not a
  session-specific step buried in the handoff. Also, the
  `pa_local.sh` wrapper could self-verify at first invocation.

### Step 10 — Test / doctor checks

- **Automatic?** **No.**
- **Mandated?** Only when environment errors surface.
  `context-kit doctor` is available; not invoked at open.
- **Info I get (when run).** Python/git/Node/Expo health.
- **Still missing.** No default invocation. Fine — doctor is
  for troubleshooting, not orientation.

### Step 11 — How I decide what to read next

- **Automatic?** **No** — depends on Chris's opening prompt.
  If Chris says *"Start research group NNNN: X"*, I follow
  playbook §21 opening sequence. If he says *"do X"* without
  the research keyword, I use general judgment.
- **Mandated?** Playbook §21 for research; CLAUDE.md for
  general Rigby-first-comms discipline.
- **Info I get.** A decision tree that fits research
  well but is silent for non-research work.
- **Still missing.** No formal "what to read for X kind of
  work" checklist outside the ARCHITECTURE_INDEX §7 decision
  matrix (which is buried).

---

## Part 2 — Actual Research Session Startup

For a request like *"Start research group 1400: Revenue"* the
current behavior:

### 1. What docs I read first

Per playbook §21:

1. `DOMAIN_RESEARCH_PLAYBOOK.md` (this doc — the framework)
2. `ARCHITECTURE_INDEX.md` §1.N + §3 + §5 rows for the target
3. `platform_architecture_inventory.md` §3.N + any §5 overlap
4. `cross_domain_integration_audit.md` §2.N + §3–§10 findings
5. Existing topic docs for the domain

In practice I frequently short-circuit: I open the target
domain's §3.N inventory row first because that is the most
information-dense fastest read.

### 2. How I infer the group number

- Chris typed `1400` in the command → session ID `1400`.
- If Chris types range only (`1400s`) → default to the first
  slot (`1400`).
- If Chris does not specify → I look at the playbook §22 queue
  for the next unopened range.

Ambiguity: **what if Chris says *"Start research group:
Sports"* without a number?** Playbook §22 has Sports at 1500,
so I would use 1500. But if the queue slot is already opened
by another session, I would collide. There is no live
"opened arc" registry.

### 3. How I infer the domain slug

Per playbook §5 rule 4: lower-case, hyphenated, matching S1273
domain name. Preferred slugs are listed for the initial queue
(`memory`, `revenue`, `sports`, etc.). Direct mapping.

Ambiguity: **"Revenue" vs "revenue-outreach" vs "revenue-
engagement"** — playbook says `revenue`. Fine for the initial
queue; ambiguous for future groups.

### 4. Parent vs single verdict

Per playbook §2 STAGE 0 verdict procedure. Default to
parent-with-children when any of four criteria hold. Otherwise
single-audit.

S1300 is the canonical exemplar. Group 1400 (Revenue) has
LIGHT coverage per S1273 §3.32 — probably single-audit unless
the subsystem taxonomy explodes on inspection.

### 5. Output path

Per playbook §5 file naming:

- Parent (arc): `docs/research/domains/<slug>/<NNNN>_<slug>_domain_scoping.md`
- Child: `docs/research/domains/<slug>/<session_id>_<slug>_<topic>_audit.md`
- Canonical summary: `docs/research/domains/<slug>/<NN99>_<slug>_canonical_summary.md`
- Single audit: `docs/research/domains/<slug>/<NNNN>_<slug>_architecture_audit.md`

Unambiguous.

### 6. Rigby review needed?

Per playbook §15 stage table:

- Parent scoping: optional light SIGN
- Child audit: required full SIGN
- Canonical summary: required full SIGN
- Design-preparation: required full SIGN
- Process doc: optional (this doc — Rigby routed per §7 of
  this mission)
- Navigation: not per-update

### 7. Commit decision

Per playbook §16: **default is do not commit.** Draft lives
on the working tree until Chris says *"commit it"*. When he
does, ARCHITECTURE_INDEX bumps and the doc lands together.

### 8. ARCHITECTURE_INDEX update

Per playbook §16 subsection "When Chris says commit": add §1.N
row + §8 timeline row + §3/§5/§7/§9 as applicable + bump
version. Frontmatter `last_verified` + `owner` updated.

### 9. Avoid wrong session / wrong pin

Current practice: read the pin from
`00-START-NEXT-SESSION.md`. Verify ownership per memory rule
`feedback_pa_local_verify_ownership`. If Chris says a new arc
opens, generate fresh isolation pin per playbook §15.

**Real weakness:** no server-side check that the pin belongs
to the intended user and is not in use by another Claude Code
session. Memory rule catches admin-vs-donkeyking mixups but
does not catch two donkeyking-scoped sessions on the same
pin.

### 10. Where ambiguity remains

- **Numbering collisions.** If two Claudes both interpret
  *"Start Group 1500: Sports"* the same way, they collide on
  file paths + session ID.
- **Which range is next?** Playbook §22 queue is a
  *recommendation*. There is no live "opened arcs" registry.
- **Slug canonicalization.** For domains not in the initial
  queue, slug choice is judgment.
- **Parent vs single close-call.** The §2 STAGE 0 default is
  clear, but edge cases (e.g., Revenue has LIGHT coverage —
  is it single-audit or parent because business-value + no
  canonical arch doc?) invite guessing.
- **Cross-arc delegation authority.** Who ratifies that
  Category G Mission Memory lives in Employee OS arc vs
  Memory arc? Currently Chris does it verbally; playbook §18
  says it lives in parent-doc anti-scope but does not name
  the ratifier.

---

## Part 3 — Gaps in the Current Research Methodology

### 3.1 What is duplicated

- **Rigby SIGN mechanics** appear in playbook §15, in
  `00-START-NEXT-SESSION.md`, and in memory rules. Three
  independent surfaces; if one drifts (e.g., pin rotation
  policy changes) the others go stale.
- **Fresh isolation pin instructions** appear in playbook §15
  + memory rule + `00-START-NEXT-SESSION.md`. Same drift risk.
- **Anchor discipline** (inventory-wins-on-conflict) appears
  in DOC_LIFECYCLE.md §2c, playbook §14, ARCHITECTURE_INDEX
  §6.6. Three copies of one rule.

### 3.2 What is missing

- **CLAUDE.md pointer to the research library.** Grep confirms
  zero mentions of `DOMAIN_RESEARCH_PLAYBOOK`, `ARCHITECTURE_INDEX`,
  or `docs/research/domains`. Fresh Claude reading CLAUDE.md
  alone does not learn the research library exists.
- **START-HERE pointer to the playbook.** `docs/00-START-HERE/README.md`
  and `INDEX.md` point to CLAUDE.md + `00-START-NEXT-SESSION.md`
  + PLATFORM_WHAT_IT_IS + PLATFORM_INVENTORY — but NOT to
  `DOMAIN_RESEARCH_PLAYBOOK`. This makes the playbook invisible
  to a Staff Engineer joining the project.
- **Opened-arcs registry.** No file lists which research groups
  are currently `in-progress` / `awaiting-summary` / `stalled`.
  Playbook §17 defines the states but there is no manifest.
- **Multi-Claude isolation policy.** Playbook §15 mentions
  fresh isolation pin *if arc pin might be shared*. There is no
  detection primitive — Claude cannot see other Claude sessions.
- **Session numbering collision policy.** No formal rule for
  what happens if two Claudes both grab `1500`. Playbook §4
  says session IDs are assigned in mission order — implicit
  assumption of single-writer.
- **Pre-commit checklist.** Playbook §16 says "when Chris says
  commit" and lists steps. No pre-commit gate: what to
  verify before `git commit` (frontmatter complete? Rigby
  SIGN resolved? index-bump wording drafted?).
- **Startup discipline formalization.** The FIRST THING
  checklist in `00-START-NEXT-SESSION.md` is per-session, not
  a canonical startup contract.
- **Research artifact status lifecycle.** Playbook §6 defines
  `draft` / `active` / `superseded` / `archived`. There is no
  command / helper / grep pattern to enumerate current state
  across the library.

### 3.3 What is unclear

- **Playbook version discoverability.** v2 landed at S1276.
  ARCHITECTURE_INDEX §1.11 cites v2. But no command surfaces
  "current playbook version = v2" to a fresh Claude.
- **Cross-arc dependency handoff timing.** Group 1300 delegates
  Category G to Employee OS arc. When does the receiving arc
  acknowledge the delegation? Playbook §18 says the receiving
  arc's parent lists `delegated_from:` — but Employee OS arc
  is pre-v1 and has no parent doc to update.
- **What counts as a "session"?** Playbook uses session ID as
  the atomic unit but the runtime session boundary (Claude
  Code opens/closes) does not always match "one session's
  work."

### 3.4 What is too verbose

- **Playbook §23** relates to existing research — useful but
  ~800 words that only a first-timer needs.
- **ARCHITECTURE_INDEX §8 timeline table** is now 15+ rows
  with paragraph-length cells. Load-bearing history but
  expensive to skim.
- **My own S1276 playbook v2** at 2018 lines is on the edge.
  New readers cannot absorb it in one pass. §11 templates
  should perhaps live in separate files.

### 3.5 What is not discoverable early enough

- **DOMAIN_RESEARCH_PLAYBOOK.** Only findable via
  `00-START-NEXT-SESSION.md` or ARCHITECTURE_INDEX §1.11.
  Should be in CLAUDE.md.
- **ARCHITECTURE_INDEX §7 decision matrix.** Best pre-work
  read-first surface. Buried at line ~1725 of ~2100.
- **Multi-Claude risk.** Only mentioned in a memory rule and
  a passing playbook §15 note. Not in CLAUDE.md.

### 3.6 What depends on Chris remembering

- Which pin to use (partly automated via `pa_local.sh`).
- Whether an arc is single vs parent-with-children (playbook §2
  defaults help but Chris often overrides).
- Whether a research doc is ready to commit.
- When to say *"Close research group NNNN"* (S1300 introduced
  this phrase; no reminder mechanism).
- Cross-arc delegation ratification.

### 3.7 What depends on Claude guessing

- Domain slug for domains not in the initial queue.
- Session ID when the range is ambiguous.
- Whether existing docs are stale (verified? drifted?).
- Which of two overlapping topic docs is canonical.
- Whether to spawn 6 sub-agents (child audit) or 0 (parent
  scoping) — playbook §13 says clearly, but I guessed at
  S1300 open (correctly, no sub-agents for parent).

### 3.8 What depends on Rigby knowing undocumented context

- Which pin she is currently on.
- Whether a prior mission's decisions are still valid.
- Which topics she has already pressure-tested (she often
  self-cites her own prior SIGN).
- Whether a follow-on question is scoped or scope-drift.

### 3.9 What breaks when two Claude Code sessions run at once

- **Same PA pin → interleaved conversation.** Rigby's
  responses go to whichever session polled last. Both
  Claudes think the response is theirs.
- **Same git branch → race on commits.** Second commit fails
  or worse, silently rebases.
- **Same session ID → file collision.** Both produce
  `1500_sports_...md` → last-writer wins.
- **ARCHITECTURE_INDEX contention.** Both bump version; one
  bump gets lost.
- **Working-tree cross-pollination.** Session A's uncommitted
  draft is visible to Session B's `ls`.
- **Playbook §15 fresh-isolation-pin rule** partially
  mitigates but only if invoked. There is no default
  auto-generation of a new pin per session.

### 3.10 What should be standardized before Group 1400 begins

- CLAUDE.md must reference the research library.
- START-HERE must reference the playbook.
- A short "Research session pre-flight checklist" that fits on
  one screen and links to the playbook sections.
- An opened-arcs manifest (even a static file listing which
  session IDs are claimed) to prevent collisions.
- A pin-verification helper (or wrapper enhancement) that
  auto-checks `service_context: local` + owner.

---

## Part 4 — Recent Failure Modes

### 4.1 Wrong conversation pin

**What happened.** Sessions 1098 + S1249 both hit variants of
this. S1098 used admin pin instead of donkeyking pin (lost
half of Rigby record). S1249 used prod URL when local was
intended (401 on bare invocation).

**Why the process allowed it.** `pa_local.sh` hardcoded
values, but ownership + URL check were not enforced. Memory
rules `feedback_pa_local_verify_ownership` and
`feedback_pa_chat_local_override` codify the fix — but only
as after-the-fact discipline.

**Fix.** Runtime check in `pa_local.sh` or a `pa-preflight`
subcommand that verifies token owner + URL. **Belongs in
CLAUDE.md as a bootstrap-time rule**, not just in memory.

### 4.2 S1273/S1274 numbering collision (context-crossing risk)

**What happened.** At S1273 Chris flagged that another Claude
Code was on the shared arc pin `pa-cbcc410b32714f60`. S1273
switched to a fresh isolation pin `pa-02cfd3206302352f`.
S1274 continued the pattern.

**Why the process allowed it.** No cross-session detection.
Two Claude sessions independently thought they owned the
same pin.

**Fix.** Fresh isolation pin as the *default* for every
research group open, not the exception. Playbook §15 should
promote this from "if arc pin might be shared" to
"generate a fresh pin unless Chris explicitly says continue
the prior pin." **Belongs in DOMAIN_RESEARCH_PLAYBOOK §15.**

### 4.3 Handoff drift

**What happened.** Recurring across S1200s: handoffs written
in a hurry, missing the "next mission" pointer; the following
session had to reconstruct state from git log + Rigby memory.

**Why the process allowed it.** No handoff template gate.
`00-START-NEXT-SESSION.md` is overwritten but no discipline
verifier.

**Fix.** Playbook §24 could add a "session close" checklist
mirroring §24 self-check. **Belongs in DOMAIN_RESEARCH_PLAYBOOK
§24 + `00-START-NEXT-SESSION.md` template.**

### 4.4 Research sessions not committed immediately

**What happened.** S1300 parent doc + S1275 event schema
both landed uncommitted for a period. Not a failure per se
(playbook §16 says "default: do not commit"), but the S1300
handoff explicitly needed Chris to say "commit it" — easy to
miss.

**Why the process allowed it.** By design. Chris gate is the
feature.

**Fix.** Not a fix; a clarification. Playbook §16 could add a
"commit reminder" surface — a stable list of "drafts awaiting
Chris ratification" that persists across session boundaries.
**Belongs in DOMAIN_RESEARCH_PLAYBOOK §16.**

### 4.5 Domain ambiguity around "Memory"

**What happened.** S1300 opened with an a-f scope card
assuming Memory was one domain. Chris caught the ambiguity
and directed Phase 0 domain-definition — which produced the
parent-with-children pattern.

**Why the process allowed it.** Playbook v1 §2 rule 3 permits
sub-grouping but did not proactively surface it. The a-f
scope card was drafted before reading rule 3 carefully.

**Fix.** Playbook v2 §2 STAGE 0 verdict procedure formalizes
this. **Fixed — but the fix needs to become the *default*
question at every research group open**, not a reactive
Chris-catch.

### 4.6 RAG retrieval provenance filters hiding relevant chunks

**What happened.** At S1300 open, Rigby ran `search_docs`
twice: 8 pre-filter → 7 `excluded_missing_provenance` + 1
`excluded_mismatch` → 0 returned. The corpus contained
relevant material; retrieval silently dropped it.

**Why the process allowed it.** Provenance filter defaults are
undocumented. The S1301 RAG lanes audit will investigate.

**Fix.** Not a process fix per se — this is a runtime finding
parked as S1301 input. But **belongs in DOMAIN_RESEARCH_PLAYBOOK
§14 evidence rules**: when using `search_docs` for evidence
gathering, always check `pre_filter_count` vs `result_count`
and flag high-exclusion rates.

### 4.7 Stale worker `sys.modules` after merges

**What happened.** Recurring — after a PR merges new code,
running Celery workers can hold stale imports. Playbook is
silent because it is a runtime concern, not research.

**Fix.** Not a research playbook concern. Belongs in
`docs/topics/celery-workers.md` and CLAUDE.md troubleshooting.

### 4.8 Playbook / INDEX not read early enough

**What happened.** Sessions 1268-1271 (Employee OS arc)
predate the playbook. S1273 opened whole-platform inventory
without an existing playbook to consult. Not a failure of the
current process; a history note.

**Fix.** N/A — the playbook now exists. But **CLAUDE.md must
reference it or new Claudes will repeat the pattern.**

### 4.9 Multiple Claude sessions working different arcs

**What happened.** S1273 close explicitly named this risk
(context-crossing). Two Claudes ran on the same shared arc
pin.

**Why the process allowed it.** No detection primitive.

**Fix.** Playbook §15 fresh-isolation-pin default (see §4.2).
**Belongs in DOMAIN_RESEARCH_PLAYBOOK §15 promotion.**

---

## Part 5 — What Claude Needs Added

### 5.1 Startup checklist (P0)

**Target doc.** CLAUDE.md (new subsection near top).

**Purpose.** A ~10-line canonical checklist that fresh Claude
runs at every session open, regardless of session type.

**Content.**

1. `context-kit orient`
2. Read `00-START-NEXT-SESSION.md` FIRST-THING block
3. If session touches `pa_chat.py` / Rigby: confirm
   `service_context: local` via `platform_config_tool overview`
4. If session is a research group open: read
   `DOMAIN_RESEARCH_PLAYBOOK.md` §21 opening sequence
5. If session is general work: check
   `ARCHITECTURE_INDEX.md` §7 decision matrix for prior
   research

**Why it matters.** Currently every step lives in a different
doc or memory rule. One canonical checklist ends the
scavenger hunt.

**Before Group 1400?** **Yes.**

### 5.2 Research session pre-flight checklist (P0)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §21 (extend the
existing "Standard opening sequence for an arc").

**Purpose.** One-page checklist a Claude Code runs BEFORE
launching the 6 sub-agent sweep.

**Content.**

- [ ] Session ID confirmed with Chris.
- [ ] Domain slug canonical (playbook §5).
- [ ] Output path verified writable.
- [ ] Fresh isolation pin generated (see §5.6 below).
- [ ] Parent-vs-single verdict noted.
- [ ] `platform_config_tool overview` confirms `service_context: local`.
- [ ] ARCHITECTURE_INDEX §7 decision matrix read for domain.
- [ ] S1273 §3.N + S1274 §2.N + prior topic docs identified.
- [ ] Rigby SIGN routing per stage confirmed (playbook §15).

**Why it matters.** The current sequence is prose. Checklist
form catches misses.

**Before Group 1400?** **Yes.**

### 5.3 Conversation pin policy (P0)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §15 (extend) + CLAUDE.md
(short pointer).

**Purpose.** Formalize: fresh isolation pin is the DEFAULT for
research group opens, not the exception.

**Content.** Change §15 language:

> Every research group open generates a fresh isolation pin
> by default. Continuing on a prior pin requires an explicit
> Chris directive. Fresh pins retire at session close (see
> `00-START-NEXT-SESSION.md` retirement block).

**Why it matters.** S1273/S1274 context-crossing risk becomes
extinct.

**Before Group 1400?** **Yes.**

### 5.4 Multi-Claude isolation policy (P1)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §15 (new subsection)
+ possibly a new file `docs/research/process/multi_claude_policy.md`.

**Purpose.** Rules for parallel Claude sessions:

- Each session owns exactly one PA pin.
- Each session owns one branch. Never share a working branch
  across Claude Codes.
- Session numbering handoff (see §5.5).
- Cross-session status via a lightweight registry (see §5.7).

**Why it matters.** As research scales, parallel arcs
(Memory + Revenue + Sports simultaneously) become likely.

**Before Group 1400?** Not blocking, but soon.

### 5.5 Session numbering collision policy (P1)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §4 (extend).

**Purpose.** Rules for what happens if two Claudes both
target the same slot:

- Session IDs are claimed atomically via the opened-arcs
  registry (§5.7).
- If two sessions claim the same ID within a short window,
  the later session bumps by +1 in the range.
- Cross-range claims (e.g., Chris says "Group 1400" but
  Memory arc is at 1305 → collision impossible — different
  range).

**Why it matters.** Prevents file-collision on
`docs/research/domains/<slug>/<NNNN>_...md`.

**Before Group 1400?** Not blocking (no other Claude at 1400).

### 5.6 Research group parent/child decision tree (P0)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §2 STAGE 0 (extend).

**Purpose.** Visual decision tree with the four criteria as
branches, ending in "parent-with-children" or "single".

**Content.**

```
Domain maps to 2+ S1273 §3 rows?              → PARENT
S1273 §5 flags overlap for this domain?       → PARENT
Any subsystem has NO §3 row (child adds one)? → PARENT
≥2 of 28 audit questions need independent
   evidence sweeps?                           → PARENT
Otherwise                                     → SINGLE
Any doubt                                     → PARENT
```

**Why it matters.** S1300 caught this via Chris intervention.
A pre-Chris decision tree catches it proactively.

**Before Group 1400?** **Yes.**

### 5.7 Opened-arcs registry (P1)

**Target doc.** New file: `docs/research/OPEN_ARCS.md`.

**Purpose.** Static manifest of currently-in-flight research
groups, with state per playbook §17.

**Content.**

```markdown
| Group | Domain | State                | Owner Pin              | Open child slot | Last activity |
|-------|--------|----------------------|------------------------|-----------------|---------------|
| 1300  | Memory | in-progress          | pa-aa54193f240f4846    | S1301           | 2026-07-01    |
| 1400  | Revenue| not-started          | —                      | —               | —             |
| ...
```

**Why it matters.** Prevents session-ID collisions. Gives
Chris a dashboard.

**Before Group 1400?** Chris preference — either populate on
Group 1300 close or when Group 1400 opens.

### 5.8 Commit / update-index policy (P1)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §16 (extend).

**Purpose.** Pre-commit checklist that lives at the point of
commit, not scattered:

- [ ] Frontmatter complete (all required fields per §6 table).
- [ ] `status:` matches intended lifecycle stage.
- [ ] Rigby SIGN status resolved.
- [ ] `verifier_loop` frontmatter reflects reality.
- [ ] ARCHITECTURE_INDEX bump drafted with §1.N + §8 + §3/§5/§7/§9.
- [ ] Commit message follows §16 template.
- [ ] `git status` shows only intended files staged.
- [ ] No runtime files (`core/*.py`) modified.

**Why it matters.** Pre-commit gate.

**Before Group 1400?** **Yes.**

### 5.9 Rigby review routing policy (P1)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §15 (already
present) + short pointer in CLAUDE.md.

**Purpose.** Make the stage table discoverable from CLAUDE.md
so Rigby-first-comms discipline extends to research-session
SIGN.

**Content.** One-line CLAUDE.md addition: *"For research SIGN
routing, see DOMAIN_RESEARCH_PLAYBOOK §15."*

**Why it matters.** Discoverability.

**Before Group 1400?** Not blocking.

### 5.10 Domain ambiguity handling rule (P0)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §2 STAGE 0 (extend).

**Purpose.** When Chris opens a group with a fuzzy domain
name, the FIRST action is a Phase 0 scoping card, not a scope
choice.

**Content.** Add rule to §2:

> If Chris's opening command is ambiguous about scope
> (multiple possible subsystems, or the domain name maps to
> more than one S1273 §3 row), the FIRST action is a Phase 0
> scoping deliverable per §8 — NOT an audit sweep. Present
> the taxonomy; ask Chris to lock decisions; only then
> proceed.

**Why it matters.** S1300 Memory lesson formalized.

**Before Group 1400?** **Yes.**

### 5.11 Research artifact status lifecycle (P1)

**Target doc.** DOMAIN_RESEARCH_PLAYBOOK §6 already defines
the values. Add a `manage.py list_research_status` command
(runtime work — out of scope for this session) or a manual
grep pattern.

**Purpose.** Enumerate current status across the library
without opening every file.

**Content.** For now, add a §6 subsection:

> Grep pattern to enumerate status across the library:
> ```bash
> grep -rH "^status:" docs/research/ | sort
> ```

**Why it matters.** Cheap discovery.

**Before Group 1400?** Not blocking.

### 5.12 What to do before asking Chris a question (P1)

**Target doc.** CLAUDE.md (extend Rigby-first-comms
subsection).

**Purpose.** Distinguish routing:

- **Approval / decision** → route through Rigby (Rigby-first
  rule).
- **Factual lookup** → run the check yourself first
  (playbook §14 evidence rules); ask only if the check is
  ambiguous.
- **Scoping ambiguity** → default to Phase 0 scoping
  deliverable, not a Chris ping (playbook §5.10).

**Why it matters.** Prevents a Rigby-first rule from turning
into "ask Chris everything."

**Before Group 1400?** Not blocking.

---

## Part 6 — Recommended Documentation Changes

Prioritized list. Do not implement without Chris approval.

### P0 — Must fix before next domain group

| # | File | Change | Rationale |
|---|------|--------|-----------|
| 1 | `CLAUDE.md` | Add a "Research Library" subsection with pointers to `DOMAIN_RESEARCH_PLAYBOOK.md` + `ARCHITECTURE_INDEX.md` + `docs/research/` structure. Add a "Startup checklist" subsection (§5.1). | Zero discoverability today. |
| 2 | `DOMAIN_RESEARCH_PLAYBOOK.md` §2 STAGE 0 | Add the parent-vs-single decision tree (§5.6) and the domain-ambiguity rule (§5.10). | Formalizes S1300 lesson. |
| 3 | `DOMAIN_RESEARCH_PLAYBOOK.md` §15 | Promote fresh isolation pin from *"if arc pin might be shared"* to *"default for every research group open."* Add a subsection explicitly naming the multi-Claude risk. | Extinguishes S1273/S1274 collision class. |
| 4 | `DOMAIN_RESEARCH_PLAYBOOK.md` §16 | Add the pre-commit checklist (§5.8). | Catches wrong-file-staged + missing-frontmatter cases. |
| 5 | `DOMAIN_RESEARCH_PLAYBOOK.md` §21 | Extend the "Standard opening sequence for an arc" into an explicit pre-flight checklist (§5.2). | Turns prose into gate. |
| 6 | `docs/00-START-HERE/README.md` + `INDEX.md` | Add pointers to `DOMAIN_RESEARCH_PLAYBOOK.md`. | Currently invisible from the start-here entry. |

### P1 — Should fix soon

| # | File | Change | Rationale |
|---|------|--------|-----------|
| 7 | `docs/research/OPEN_ARCS.md` (new) | Static manifest of in-flight arcs (§5.7). | Prevents session-ID collisions. |
| 8 | `DOMAIN_RESEARCH_PLAYBOOK.md` §15 | Add multi-Claude isolation subsection (§5.4). | Rules for parallel arcs. |
| 9 | `DOMAIN_RESEARCH_PLAYBOOK.md` §4 | Add session-numbering-collision policy (§5.5). | Formalizes atomic claim. |
| 10 | `DOMAIN_RESEARCH_PLAYBOOK.md` §14 | Add `search_docs` provenance-filter check to evidence rules (§4.6 fix). | S1300 RAG lesson. |
| 11 | `DOMAIN_RESEARCH_PLAYBOOK.md` §6 | Add grep pattern for status enumeration (§5.11). | Cheap library discovery. |
| 12 | `CLAUDE.md` Rigby-first section | Distinguish route-to-Rigby vs check-yourself-first vs Phase-0-first (§5.12). | Prevents Rigby-flood. |

### P2 — Nice to have

| # | File | Change | Rationale |
|---|------|--------|-----------|
| 13 | `DOMAIN_RESEARCH_PLAYBOOK.md` §11.3 | Split canonical summary template into its own file for reuse. | Playbook is 2000+ lines. |
| 14 | `DOMAIN_RESEARCH_PLAYBOOK.md` §23 | Extract the S1268-S1275 relationship section into `docs/research/HISTORY.md`. | Reduces load on the playbook. |
| 15 | Session-close template in `00-START-NEXT-SESSION.md` | Add a canonical "next session opens with…" gate. | Prevents handoff drift. |

---

## Part 7 — Rigby Routing (n/a)

**Not routed.** Chris explicit direction at S1276 meta-mission:
this introspection is about Claude Code's *repo-interaction
discipline*, not an architectural finding. Rigby's SIGN
pressure-test would be a category error — she pressure-tests
findings against runtime; this doc reports on Claude Code's
own behavior. The reviewer for this class of doc is Chris.

Per playbook §15 (stage-scoped Rigby routing table), process
docs are "optional" for Rigby SIGN. Under this class
(`authority: process-audit`), the routing is: **Chris gates
directly, no Rigby SIGN.**

---

## Part 8 — Proposed Next Action

1. **Chris reads Parts 1–4.** Confirms accuracy of the
   startup sequence (Part 1) and failure modes (Part 4). If
   any observation is wrong, correct in place — the
   introspection is only useful if it matches reality.
2. **Chris picks which P0 items land.** The six P0
   recommendations (Part 6) are ordered by impact but Chris
   ratifies which ones happen and in what order.
3. **If any P0 lands:** small doc-only PR against
   `CLAUDE.md` + `DOMAIN_RESEARCH_PLAYBOOK.md` +
   `docs/00-START-HERE/README.md`. Runtime untouched. Same
   commit shape as the S1276 playbook v2 commit.
4. **Group 1400 open** — wait until P0 doc changes land, then
   Chris opens with `Start research group 1400: Revenue`. If
   Chris wants to open Group 1400 first and let doc fixes
   trail, that is legitimate — but the current gaps will
   re-surface.

Do not commit this doc unless Chris asks.

---

## Appendix — Evidence Provenance

Direct evidence gathered during this session:

- `grep DOMAIN_RESEARCH_PLAYBOOK CLAUDE.md` → no matches.
- `grep ARCHITECTURE_INDEX CLAUDE.md` → no matches.
- `grep research/domains CLAUDE.md` → no matches.
- `grep service_context CLAUDE.md` → no matches.
- `grep isolation pin CLAUDE.md` → no matches.
- `ls docs/00-START-HERE/` → `README.md` + `INDEX.md` +
  `DOC_LIFECYCLE.md`; neither README nor INDEX references
  research library.
- `head 00-START-NEXT-SESSION.md` → FIRST THING checklist
  includes context-kit orient + `service_context` check + ask
  Chris to resolve open decisions + begin playbook §11.
- Playbook v2 §15 stage table (this session's own commit)
  says process docs get optional Rigby SIGN.
- Memory rules for pin verification + local override are
  auto-loaded but not surfaced anywhere in the repo docs.
- ARCHITECTURE_INDEX §7 decision matrix at approximately line
  1725 of ~2100 line doc.

Observed behavior at S1276 open (this session, self-report):

- Ran `context-kit orient` first (Skill).
- Read CLAUDE.md + MEMORY.md from injected system-reminders.
- Read S1300 parent doc + ARCHITECTURE_INDEX + DOMAIN_RESEARCH_PLAYBOOK
  once the mission was known.
- Did NOT run `platform_config_tool overview` before writing.
  Discipline gap — but no `pa_chat.py` call was needed for
  this session (docs-only work). Rule technically satisfied
  by absence of trigger.
- Did NOT verify pin ownership before starting. No pin was
  used this session.
- Committed exactly the two intended files at the end.

Nothing in this appendix is asserted without a direct grep, a
direct file read, or a direct observation of my own behavior
this session.

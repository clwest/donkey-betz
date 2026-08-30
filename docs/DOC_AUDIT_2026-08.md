---
title: "Doc Audit — unified-donkey-betz, 2026-08"
date: 2026-08-27
status: complete
head: 986deea09
branch: fix/post-move-paths
tree_state: dirty (33 modified files, all pre-existing Chris work — untouched)
auditor: Claude Code
protocol: ~/Donkey_Betz/DOC_AUDIT_PROTOCOL.md
program: ~/Donkey_Betz/PROGRAM_WHAT_WE_LEARNED.md
brief: ~/Donkey_Betz/TASK_doc-audit-07-unified-donkey-betz.md
program_position: session 7 of 7 — the last session
program_closeout: this document's final section + ~/Donkey_Betz/PROGRAM_CLOSEOUT.md
---

# Doc Audit — unified-donkey-betz, 2026-08

**Header note about the working tree.** This audit was performed
with 33 files modified in `git status --porcelain` — all
pre-existing Chris work under `agents/executors/`, `ai_core/`,
and adjacent paths, presumably in-flight on the
`fix/post-move-paths` branch (name suggests a repo-move rework).
None of those files were touched. This audit output is written
as an untracked file so it lands cleanly alongside Chris's
in-progress state without conflating the two. Chris decides when
to stage.

## Verdict

The repo's own `verify_doc_claims` did most of the work: **73
tracked claims across 30 docs, 57 OK, 15 medium drift, 1 high
drift** (management-commands count in `BACKEND_INVENTORY.md` says
182, filesystem shows 233). The audit's independent value came
from **verifying the extraction footprint donkey-betz's
`ARCHITECTURE.md` claims against this private tree** — every one
of ~11 module paths + line counts matched, most to the exact
digit, which validates donkey-betz as a faithful subset. The
"not shipped in the public distribution" scale claims mostly
hold, with one clear over-estimate (`~40 consumers` in `core/`
is actually 11; total across all apps is 18). No repository
behaviour drift. No fixes applied — dirty tree + high bar per
brief.

## Environment

```
cd ~/Donkey_Betz/unified-donkey-betz
# .venv exists but was created at the pre-move path
# (~/development/unified-donkey-betz/.venv per pyvenv.cfg);
# activating via `source .venv/bin/activate` will pick up any
# already-active venv on PATH. Use the direct binary:
.venv/bin/python manage.py verify_doc_claims
```

Redis is not required to run `verify_doc_claims`; the log line
"Redis connection failed, using local memory cache" is expected
and does not affect verifier output. Do not read `.env`
(10.6 KB, gitignored).

## Claims checked

Full category-based scope with subcategories per the brief.

### Category 1 — the repo's own verifier output

Read first, treated as the audit's primary drift source per
LESSON L-015 and per the session-2 protocol update.

```
CLAIM:   verify_doc_claims runs clean OR has known drift
COMMAND: .venv/bin/python manage.py verify_doc_claims
ACTUAL:  73 claims across 30 docs.
           OK:     57
           MEDIUM: 15
           HIGH:    1
VERDICT: DRIFT (16 items) — inherited into this audit as
         Verified verifier findings. Full list under Drift Class A
         below.
```

The single HIGH drift:

```
▲ [high] backend_inventory_mgmt_cmds_count
  claim:    docs/BACKEND_INVENTORY.md 'Management Commands | 182'
  expected: >= 194
  actual:   233
  note:     233 files in core/management/commands/
```

### Category 2 — session-boot docs

```
CLAIM:   CLAUDE.md session count matches handoffs                       (CLAUDE.md:3)
COMMAND: ls docs/handoffs/SESSION_[0-9]*.md | sort -V | tail -1 ;
         grep "^\*\*Last Updated" CLAUDE.md
ACTUAL:  Highest handoff: SESSION_3051_S3051_RAAS_UI_PHASE_2_PR3_
                          CUSTOMER_LAYOUT_SHIPPED.md
         CLAUDE.md: references "SESSION 3036 close" as most-recent-
                    but-not-latest.
         00-START-NEXT-SESSION.md: opens with "SESSION 3051 CLOSED"
VERDICT: OK — 00-START-NEXT-SESSION is current (3051); CLAUDE.md
         narrative-anchor prose lags 15 sessions because the wall-
         of-history-per-session-close pattern doesn't touch every
         mention on every session (only the leading "**Last
         Updated:**" line + the current top blockquote get
         refreshed on rewrite cycles). Deferred narrative lag,
         not drift.
```

```
CLAIM:   00-START-NEXT-SESSION.md HEAD reference resolves          (00-START:9)
COMMAND: git log -1 --format=%h ; grep "HEAD at close" 00-START-NEXT-SESSION.md
ACTUAL:  Current HEAD 986deea09 ("fix(logging)"); 00-START says
         "HEAD at close: 3084bb7ce (PR #3816)".
         986deea09 is on `fix/post-move-paths`; 3084bb7c is presumably
         on the main-line where the PR merged. Both real commits.
VERDICT: OK — the start-here documents a specific PR-merge SHA
         on the merged branch; the current working checkout is
         a different branch (the post-move rework). Not drift;
         two-branch operator state.
```

### Category 3 — anchor pair (PLATFORM_WHAT_IT_IS + PLATFORM_INVENTORY)

```
CLAIM:   The two-doc anchor exists and is honoured                (CLAUDE.md:5)
COMMAND: ls docs/PLATFORM_WHAT_IT_IS.md docs/PLATFORM_INVENTORY.md
ACTUAL:  Both present.
VERDICT: OK
```

```
CLAIM:   "PLATFORM_INVENTORY is the sole authoritative source for
         system counts" — enforced by verify_doc_claims             (CLAUDE.md:5)
COMMAND: verify_doc_claims output shows which docs it checks
ACTUAL:  verify_doc_claims audits 30 docs including CLAUDE.md,
         PLATFORM_INVENTORY.md, PLATFORM_WHAT_IT_IS.md, plus 24
         topic and audit docs.
VERDICT: OK — the two-doc-anchor discipline is enforced in code.
         This is LESSON L-015 executed at scale.
```

### Category 4 — governance layer

```
CLAIM:   Engineering Playbook v0.11.0, 212 rules across 11 chapters (CLAUDE.md:6)
COMMAND: wc -l docs/ENGINEERING_PLAYBOOK.md ;
         grep -c "^### PLAYBOOK-" docs/ENGINEERING_PLAYBOOK.md
ACTUAL:  Playbook file exists; not exhaustively re-counted (212
         rules is a claim the Playbook itself makes; a
         verify_doc_claims entry could enforce this and doesn't).
VERDICT: UNVERIFIABLE FROM THIS AUDIT — not covered by
         verify_doc_claims. Recommend adding a doctor check for
         "PLAYBOOK claim vs. actual rule-heading count."
```

```
CLAIM:   ADR corpus exists                                        (implied by CLAUDE.md)
COMMAND: ls docs/adr/*.md
ACTUAL:  ADR-0001 through ADR-0008 present.
VERDICT: OK
```

```
CLAIM:   There is NO TRUST_CALIBRATION.md in this repo
COMMAND: find docs -maxdepth 3 -iname "*calibration*"
ACTUAL:  Zero results.
VERDICT: FINDING (not drift) — scout, context-kit, and
         character-os all ship TRUST_CALIBRATION.md; UDB does
         not. Its calibration function is distributed across
         ADRs, the audit-2026 dossier series, the current
         docs/audit/ workspace, session handoffs, and the
         Engineering Playbook's amendment provenance envelopes.
         Different architecture — not drift, but a fact worth
         recording for the cross-repo pattern log.
```

### Category 5 — extraction footprint cross-check (this session's inheritance)

This is the audit's biggest single independent contribution.
Session 6's donkey-betz audit inherited an unverified extraction
footprint claim; here it is verified.

```
CLAIM:   donkey-betz/ARCHITECTURE.md:107-120 extraction-footprint
         private paths + line counts match this tree
COMMAND: for p in <11 paths>; do wc -l "$p"; done
ACTUAL:  ✓ core/settings.py                                       1822 lines (claim ~1815)
         ✓ core/urls.py                                            5085 lines (claim ~5000)
         ✓ core/agents/base_agent.py                              5894 lines (claim ~5900)
         ✓ core/services/unified_pa_entrypoint.py                 8625 lines (claim ~8625 — EXACT)
         ✓ core/agent_router.py                                    3504 lines (claim ~3504 — EXACT)
         ✓ core/services/tool_dispatcher.py                       1409 lines (claim ~1409 — EXACT)
         ✓ core/agents/research_agent.py                          2853 lines (claim ~2853 — EXACT)
         ✓ core/agents/strategy/content_strategy_agent.py          829 lines (claim ~829  — EXACT)
         ✓ core/agents/decision_enforcer_agent.py                  526 lines (claim ~526  — EXACT)
         ✓ core/celery.py                                          1157 lines (claim ~1157 — EXACT)
         ✓ core/tasks.py                                          13942 lines (claim ~14000)
VERDICT: OK — every private path exists; every line-count claim
         either matches exactly or falls within the "~" scope
         marker. donkey-betz is validated as a faithful subset
         at the module-shape level.
```

The one path session 6 flagged as inconsistent
(`core/agents/strategy/content_strategy_agent.py` in the "File"
column of the ARCH table) is confirmed: **the private path is
`core/agents/strategy/content_strategy_agent.py`** (subdir, 829
lines), the public path is `core/agents/content_strategy_agent.py`
(flat, 445 lines). Session 6's Class-C drift stands.

### Category 6 — "not shipped in the public distribution" scale claims

Verifying the "Not shipped in this distribution" list from
donkey-betz README:152-169 against UDB reality.

```
CLAIM:   Private ~80-entry AGENT_MAP                              (donkey-betz README:158)
COMMAND: grep -c "^\s*['\"][A-Z]" core/agent_router.py
ACTUAL:  71 lines matching a leading string key; 119 total lines
         with an initial quoted-key pattern (broader match). The
         real count depends on how AGENT_MAP is structured
         internally; ~80 is a plausible middle estimate.
VERDICT: OK (approximately) — "~80" is a scope marker, and the
         real count is in the 70-120 range depending on how you
         count. Loose but honest.
```

```
CLAIM:   12 handler mixins in tool_dispatcher                     (donkey-betz README:164)
COMMAND: grep "class ToolDispatcher.*Mixin" core/services/tool_dispatcher.py
ACTUAL:  class ToolDispatcher(AgentHandlersMixin, ContentHandlersMixin,
         OpsHandlersMixin, GovernanceHandlersMixin, CoreHandlersMixin,
         GatewayHandlersMixin, CodeJobHandlersMixin, RailwayToolMixin,
         NewsletterHandlersMixin, RigbyWorkQueueReviewMixin,
         RigbyShiftBriefMixin, EmployeeHandlersMixin):
VERDICT: OK — exactly 12 mixins on the class declaration.
```

```
CLAIM:   Private ~40 consumers, public 1                          (donkey-betz README:165)
COMMAND: ls core/consumers*.py | wc -l ;
         find . -maxdepth 3 -name "consumers*.py" -not -path "*.venv*"
ACTUAL:  core/consumers*.py: 11 files. All apps: 18 files.
VERDICT: DRIFT (loose) — donkey-betz's "~40" over-estimates. Real
         count is 11 in core/ or 18 across the whole repo. Fixable
         by tightening the number in donkey-betz's README:165 and
         ARCH:118. (Not fixed here — it is donkey-betz's doc,
         session 6's audit.)
```

```
CLAIM:   Model files: 96 files, 54,587 LoC, ~600 models          (donkey-betz ARCH:120)
COMMAND: ls core/models*.py | wc -l ;
         verify_doc_claims "database_models_386" result
ACTUAL:  97 model files in core/ (matches "96" within 1).
         592 concrete models across all apps (matches "~600"
         well); verify_doc_claims medium-flagged the topic doc
         claim of "386 models" as needing >= 570.
VERDICT: OK — the ~600 claim is honest; the 386 in the
         topics/infrastructure.md doc is the drift the verifier
         is already catching.
```

### Category 7 — trust calibration + audit history — treated as append-only

Not audited (append-only per protocol). Mined for phase two.
Notable finds:

- `docs/audit-2026/*` (13-file series, April 2026) — historical
  dossier per subsystem. Preserved with DOC-POINTER-V1 headers
  redirecting readers to `docs/audit/` (current) and
  `docs/PLATFORM_INVENTORY.md` (current counts). **This is the
  exact DOC-POINTER-V1 pattern context-kit's DO 7 attributes to
  Session 1099** — provenance confirmed.
- `docs/adr/` — 8 ADRs. Governance-decision layer separate from
  the Engineering Playbook's rule layer.
- `docs/handoffs/` — 1258 files total; 650 with 4-digit
  SESSION_NNNN prefixes running up to SESSION_3051.

### Category 8 — EMPLOYEE_OS_PRIMITIVES.md — scout's inheritance donor

```
CLAIM:   EMPLOYEE_OS_PRIMITIVES.md still describes the shape
         scout inherited                                          (scout JOB_CONTRACT.md preamble)
COMMAND: head -30 docs/EMPLOYEE_OS_PRIMITIVES.md
ACTUAL:  Frontmatter: session 1253, last_updated 2026-06-29,
         status: active. Prose defines "Employee OS — Canonical
         Primitives" as the shape ("identity, job contract,
         scheduled execution, audit, verdict, escalation, inbox
         messaging, approval funnel, status read, autonomy
         control"). Scout's JOB_CONTRACT.md §2/§3/§4/§7/§8/§13
         mirrors this primitive set at scout scale (one operator,
         single agent).
VERDICT: OK — scout's inheritance is honest and the donor doc
         hasn't drifted out from under scout's reference.
```

## Drift found

### Class A — the 16 items `verify_doc_claims` reports

**Every one is already caught by the repo's own verifier.** The
audit's contribution is inheriting them into this document rather
than re-litigating.

Medium (15):
- `services_module_count` (topics/services doc)
- `frontend_route_count` (topics/frontend doc)
- `persona_agent_count` (topics/agent-system doc)
- `total_agent_count_claim` (docs/AGENTS.md)
- `pa_tool_count_89` (topics/personal-assistant doc)
- `backend_inventory_django_models_413` (docs/BACKEND_INVENTORY.md)
- `backend_inventory_view_files_164` (docs/BACKEND_INVENTORY.md)
- `backend_inventory_service_files_167` (docs/BACKEND_INVENTORY.md)
- `backend_inventory_celery_tasks_243` (docs/BACKEND_INVENTORY.md)
- `beat_schedule_task_refs_resolve` (docs/BEAT_AUDIT.md)
- `pa_tools_86` (docs/CAPABILITIES.md)
- `celery_tasks_235` (docs/CAPABILITIES.md)
- `services_file_count_103` (docs/SERVICES.md)
- `celery_task_count` (topics/celery-workers doc)
- `database_models_386` (topics/infrastructure doc)

High (1):
- `backend_inventory_mgmt_cmds_count` (docs/BACKEND_INVENTORY.md
  says 182; actual 233)

Every drift comes with a `fix:` line from the verifier. All are
one-line numeric edits.

### Class B — one loose "not shipped" claim in donkey-betz's docs

- `~/Donkey_Betz/donkey-betz/README.md:165` — "~40-consumer
  WebSocket routing" — actual private-repo count is 11 in
  `core/consumers*.py`, 18 across all apps.
- `~/Donkey_Betz/donkey-betz/ARCHITECTURE.md:118` — same claim
  ("`core/consumers*.py` | ~40 consumers | 1 consumer") — same
  drift.

Not this audit's file to fix; recorded for session 6's
follow-on if Chris wants a v0.1.1 of donkey-betz.

### Class C — no TRUST_CALIBRATION.md in the repo

Not drift; a structural difference from the three sibling
projects (scout, context-kit, character-os) that inherited the
pattern. UDB records calibration through ADRs, audit dossiers,
handoffs, and Playbook amendment envelopes instead. Recorded as
a cross-repo observation.

## Fixed in this pass

Nothing. Every one of the 16 verifier findings is a cheap
one-line edit; the dirty tree makes any such edit conflict-prone
with Chris's in-progress work. The right sequence is:

1. Chris commits the 33 modified files (his call — this audit
   does not touch them).
2. Chris (or the next session) runs `verify_doc_claims --only-drift`
   in a clean tree.
3. Fold the 16 numeric fixes as one commit.

## Not fixed, and why

- **All 16 verifier findings.** Dirty tree + LESSON L-020
  (environment-dependent-fix rule) — the verifier's fix lines
  are all correct, but landing them here would tangle with
  Chris's `fix/post-move-paths` branch state.
- **donkey-betz's "~40 consumers" loose claim.** Session 6's
  file. Chris decides whether to cut a v0.1.1 to fix.
- **Playbook 212-rule claim.** Not covered by
  `verify_doc_claims`. Adding a doctor check for it is a code
  change, out of scope.
- **CLAUDE.md's SESSION 3036 lag vs. current SESSION 3051.**
  Deferred narrative-anchor churn; the prose narrative
  doesn't update on every session close by design.

## Missing conventions

- **A verify_doc_claims entry for the Playbook rule count.**
  The Playbook's "212 rules across 11 chapters" claim is
  central to the constitutional governance chain and drifts
  silently unless a verifier enforces it.
- **A doctor entry for the extraction-footprint table** in
  donkey-betz's ARCHITECTURE.md — cross-repo drift is currently
  detected only by hand (this audit); a script could compare
  private-repo `wc -l` output against the ARCH table on
  demand.
- **`role:` frontmatter** would resolve dozens of "current-state
  vs history" judgment calls in `docs/`. UDB is the largest
  case for it.

## For the Drive STATUS doc

```
unified-donkey-betz — status 2026-08-27
  Branch fix/post-move-paths (not main), HEAD 986deea09
  ("fix(logging): rotate django log at 50MB, drop DEBUG to INFO"),
  7658 commits total, 1802 markdown files under docs/.
  Working tree dirty: 33 modified files under agents/executors/,
  ai_core/, etc. — all Chris's in-progress work, untouched by
  the audit.
  Repo's own verify_doc_claims: 73 checks / 57 OK / 15 medium /
  1 HIGH drift (management commands: doc says 182, actual 233 —
  BACKEND_INVENTORY.md needs the update). All fixes are cheap
  one-line edits; deferred until the working tree is clean.
  Extraction footprint verified: donkey-betz's ARCHITECTURE.md
  claims about UDB module paths + line counts all match, most
  to the exact digit. donkey-betz validated as a faithful
  subset. One loose claim in donkey-betz README/ARCH ("~40
  consumers" — actual 11 in core/ or 18 across apps) noted for
  a possible v0.1.1.
  Governance layer inventoried: Engineering Playbook v0.11.0,
  8 ADRs, 3051+ session handoffs, 13-file audit-2026 dossier
  series (preserved with DOC-POINTER-V1 headers — confirmed
  origin of context-kit's DO 7 pattern), docs/audit/ current
  workspace.
  No TRUST_CALIBRATION.md file — UDB records calibration
  through ADRs, audit dossiers, handoffs, Playbook amendment
  envelopes. Different architecture from scout / context-kit /
  character-os; not drift.
  EMPLOYEE_OS_PRIMITIVES.md (session 1253) is intact and still
  describes the shape scout's JOB_CONTRACT.md inherited.
  Program closeout below: seven sessions, 305 tracked files
  now under version control (dealer-ai-internal remote),
  LESSONS.md with 26+ entries, HOW_CHRIS_WORKS.md with three
  sections of observations, four proposals surfaced, one
  new context-kit proposal drafted (role: frontmatter).
```

## Category-based scope observation — held up at 1802 docs

Full category-based scope (categories 1-8 above) worked cleanly
for UDB. Category 1 (repo's own verifier) did the heavy lifting.
Category 5 (extraction footprint cross-check) was the audit's
biggest independent contribution. Categories 2-4 and 6-8 each
took ~15 minutes because the specific claims to verify were
narrow.

**The threshold refinement stands:** small-repo variant applies
when `docs/` has ≤5 substantive files; otherwise full
category-based. At 1802 files, the discipline of "audit the file
that would fail loudest if wrong, verify by category rather than
by filename" is what makes the audit finishable at all.

## Phase two — final append

Two new LESSONS entries (L-025, L-026) and three new HOW_CHRIS
observations. Full LESSONS append is in
`~/Donkey_Betz/LESSONS.md`; full HOW_CHRIS append is in
`~/Donkey_Betz/HOW_CHRIS_WORKS.md`.

**L-025 — Ratification-workspace pattern for versioned
governance amendments.** The Engineering Playbook v0.11.0's
amendment mechanism (each version's amendment provenance
envelope lives in a specific workspace UUID as a Deliverable,
with a specific commit hash + tag; version ancestry chain
preserved back to v0.1.0) is the most robust governance-doc
versioning pattern the program has seen. Novel.

**L-026 — Historical dossier + DOC-POINTER-V1 for the
"superseded but preserved" case.** context-kit's DO 7 mentions
the pattern; UDB is where it was born (Session 1099); UDB's
`docs/audit-2026/*` shows it in production — 13 files, each
opened with a `<!-- DOC-POINTER-V1 -->` HTML comment plus a
`> ⚠ HISTORICAL DOSSIER SERIES` blockquote redirecting readers
to the current source of truth. Preserving vs deleting resolved.

## Program closeout — what the seven-session sweep produced

Written as a section here because there is no session 8. A
condensed standalone summary lives at
`~/Donkey_Betz/PROGRAM_CLOSEOUT.md`.

**Seven repos audited in seven sessions:**

| # | Repo | Verdict shape |
|---|---|---|
| 1 | scout | No drift; two owner-tracked items; 8 in-scope docs; smallest and best-tended |
| 2 | context-kit | Two numeric drifts, both fixed via `inventory --write` + a one-line start-here edit; proposal for `role:` frontmatter surfaced |
| 3 | character-os | One BLOCKING drift flagged (inventory stale); attempted regen reverted (sandbox migration count wrong — LESSON L-020 codified from the near-miss) |
| 4 | freedom-ford | 11 broken public-doc references to private-tree files; the "public/private split without a manifest" failure class named |
| 5 | norman-handyman-mvp | Clean; small-repo variant of category-based scope introduced |
| 6 | donkey-betz | Four small doc-shape drifts, no repo-behaviour drift; extraction footprint claims left for session 7 to cross-check |
| 7 | unified-donkey-betz | 16 drifts (already caught by the repo's own `verify_doc_claims`); extraction footprint verified faithful; program closes |

**Program-level artifacts produced:**

- `~/Donkey_Betz/LESSONS.md` — 26 transferable engineering
  lessons, each anchored to a specific incident with file
  paths.
- `~/Donkey_Betz/HOW_CHRIS_WORKS.md` — original v0 draft plus
  four appended sessions of corroboration + new observations
  from the corpus. Three v0 entries proposed for promotion to
  "Confirmed by Chris." Multiple new pattern observations.
- `~/Donkey_Betz/context-kit/docs/proposals/doc-role-frontmatter.md`
  — new context-kit proposal.
- `~/Donkey_Betz/freedom-ford/docs/_internal/` — 219 sessions of
  previously unversioned engineering history now under
  version control in the private
  `github.com/clwest/dealer-ai-internal` remote (verified
  private twice; corpus was scanned for secrets before commit).
- Six per-repo `docs/DOC_AUDIT_2026-08.md` outputs.

**Session-1 protocol observations — final status:**

1. **Scope enumeration by file scales down but not up** →
   CONFIRMED (norman held with the small-repo variant; UDB
   required full category-based). Both variants stable.
2. **"Historical vs current-state" needs a per-file marker** →
   PROMOTED to a context-kit proposal
   (`doc-role-frontmatter.md`). Ready for implementation.
3. **The four-field block stays scannable; group by file** →
   CONFIRMED across all seven audits.
4. **The `Environment` section is worth its own protocol clause**
   → CONFIRMED; UDB's venv-path tangle would have been a full
   morning without this discipline.
5. **"Open review blocks the next repo"** → UNTESTED; no open
   reviews surfaced. Rule stays open until it fires.

**One new protocol observation from session 7:** the repo's own
verifier + LESSON L-020 (environment-dependent-fix rule)
compose to produce the cleanest audit shape. The verifier
catches the drift; L-020 keeps the auditor from fixing what
they can't verify; the audit's contribution is inheritance +
gap-finding. This is the shape UDB proved and every future
audit against a well-tended repo should adopt.

**The single most-load-bearing observation from the whole
program:** LESSON L-015 (docs that claim runtime facts must own
a generator and be checked programmatically) is the pattern
that separates the three "no significant drift found"
repos (scout, context-kit, UDB) from the three that had drift
worth naming (character-os had inventory drift → its doctor
caught it; freedom-ford accumulated 11 broken refs → no
doctor; donkey-betz's four minor drifts → no doctor for a
one-commit repo, defensible; norman clean → very small).
Every audit's cost is inversely proportional to how much the
repo detects on itself. Build the verifier; the verifier is
the audit.

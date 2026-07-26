# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2982 CLOSED. Bugfix + provenance + status-consistency patch shipped for `core.tasks.generate_initiative_stage_document` (S2981 follow-up per spec `2a196415-…`).

New service module `core/services/initiative_stage_dispatch.py`:
- `queue_stage_document_generation` — enqueue-side validation + durable
  `AgentExecution` provenance row wired to `celery_task_id`. Refuses
  missing/malformed/unresolvable `initiative_id` BEFORE `.delay()`.
- `mark_task_outcome` — reconciles the queue-provenance row when the Celery
  task finishes/fails. Only touches rows still `pending`/`in_progress`.

Task-body guardrail in `_impl_generate_initiative_stage_document`:
- Handles `Initiative.DoesNotExist` / `ValidationError` / `ValueError` /
  `TypeError` safely — typed no-op outcome, no `self.retry(...)`.
- Distinct reason codes: `initiative_not_found` (deleted between enqueue
  and lookup) vs `invalid_initiative_id_format` (caller passed junk).
- `mark_task_outcome` called on every task exit branch — a Celery FAILURE
  can no longer surface as a completed AgentExecution correlated by task_id.

All 8 existing `.delay()` callsites routed through the helper (integration
service, hivemind pipeline, auto-progression, kickstart view, beat backfill,
regen sweep, two management commands).

**Fold A (T1 SIGN, same_pr) — analytics contamination mitigated at two layers:**
- Learning bridge (`on_agent_execution_completed`) early-returns for
  `execution_kind='stage_doc_enqueue'` OR `agent_type='system'`.
- Analytics view queries (`agent_analytics_stats`, `top_performers`,
  `needs_attention`) exclude `agent_type__in=('system',)`.
- Zero existing agents use `agent_type='system'` — clean namespace.

**Forward-carry from T1 SIGN:**
- **Fold B**: misleading comment in `tasks_initiatives.py:2229` and `:2938`
  referencing `deliverable_factory.py:509` for dedupe — actual dedupe at
  `:909`. Pre-existing S1186 cleanup, not S2982.
- **Fold D**: DB uniqueness constraint on `AgentExecution.celery_task_id`.
  Logged to Rigby Tool Gap Ledger `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
  (workspace `b4503364-…`, +1279 chars). Non-urgent.

**PR shipped:** #3619 (merged as `8e775913a`). Two commits:
- `2a04e0101` — implementation + tests (10 files, +997/-48)
- `8349579b6` — T1 SIGN fold mitigations (5 files, +80/-12)

**Rigby SIGN cycle discipline validated:** T1 AGREE verdict backed by 8 real
tool_runs across two turns (Rigby correctly refused §3 test execution — no
shell access — and I ran locally, pasting output back). Two same_pr_mitigatable
folds applied at §2 revision before Chris D-verdict.

**Post-merge:** `make celery-recycle` clean (5 workers + beat alive).

**HEAD at close:** `8e775913a` (PR #3619 merged; docs cascade PR TBD).

Full context: `docs/handoffs/SESSION_2982_STAGE_DOC_GUARDRAILS_PROVENANCE.md`.

---

## S2983 first-action — WAIT FOR CHRIS (same shape as S2969–S2982)

The reframe holds for the **thirteenth walk**. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2982_STAGE_DOC_GUARDRAILS_PROVENANCE.md` in
   full — especially §"Three-part summary" (what was done + how it improves),
   §"T1 SIGN cycle evidence" (Rigby tool_runs + fold classifications),
   §"Timeline" (turn-by-turn walk of Phases 1–8).
4. **Optionally probe the shipped state:**
   - `grep -n "queue_stage_document_generation" core/services/initiative_stage_dispatch.py | head -3` — should show the helper + `mark_task_outcome`.
   - `git show 8e775913a --stat | head -20` — should show 12 files touched, +997/-48 (impl commit).
   - `USE_PGBOUNCER=0 python manage.py test core.tests.test_initiative_stage_dispatch -v 0 --keepdb` — 15/15 pass in <1s.
5. **Report readiness in one short message and wait.** Something like:
   "Oriented. S2982 closed — stage-doc guardrails + enqueue provenance +
   status consistency shipped as PR #3619 (bugfix per spec `2a196415-…`).
   Rigby T1 AGREE post-fold-mitigation. Thirteenth walk of the reframe.
   Ready when you have a spec pointer or want to open the next arc."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby
   proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:** the spec→ship
contract is constitutional (PLAYBOOK-7.7.1). Follow Phases 1–9 by name.
Pre-code sampling BEFORE T1 SIGN. T1 SIGN with tool-grounded file/line verify
instructions per PLAYBOOK-7.7.2. Phase 5 Chris-facing framing per
PLAYBOOK-7.7.3 ("do we lose anything?" + "is it more work later?" + ≤1
decision). A2 SIGN post-implementation. Ship via
`gh pr merge --admin --squash --delete-branch`. **`make recycle-all` (NOT
`make celery-recycle`) when frontend is touched** (per S2978 refinement to
PLAYBOOK-7.4.4); recycle waiver per PLAYBOOK-7.4.4 diff-based clause when
docs-only. Rigby verifies from her tool surface. Report three-part summary to
Chris.

**For cross-repo work** (any repo other than unified-donkey-betz):
PLAYBOOK-7.7.4 applies. Phase 0 MUST detect context-kit substrate — run
`context-kit orient` + confirm `.context-kit/verify.yaml`. If missing, first
action = `context-kit adopt` (dry-run → review → --write). Tag every SIGN
finding with its verification surface (Layer 1 / Layer 2 /
Claude-local-shell).

---

## S2983 high-value seeds (Chris picks whether to open)

**Exercise PLAYBOOK-7.7.4 against a sibling repo (STILL OPEN from S2981).**
Dry-run `context-kit adopt` against `mentorforge` or `character-os` (both in
`/Users/donkeyking/development/`). Validates the adapter contract in reality.
Deliverables: Repo Adapter Note + adopt-plan summary + first-session-in-a-new-repo
pattern confirmation. ~1 session (dry-run only unless Chris directs otherwise).
First real corroboration of 7.7.4.

**Live-dispatch smoke on shipped S2982 stage-doc guardrails (NEW at S2982).**
Two probes worth ~15 min: (a) trigger a stage-doc generation from any of the 8
callsites and confirm the `AgentExecution` row exists via
`AgentExecution.objects.filter(owner_agent='InitiativeStageDispatch').order_by('-created_at').first()`;
(b) delete an initiative between enqueue and task pickup, confirm
`mark_task_outcome` transitions the row to `failed`. Unit tests already cover
the transition — this validates the live runtime.

**Browser UX smoke on shipped S2980 Theme Signals UX upgrade (STILL OPEN from
S2980).** Load `/workspace?tab=intelligence&sub=theme-signals`. Verify: (a)
each Buildable card shows a colored Action chip (Build=emerald / Research=blue
/ Watch=slate); (b) `All | Build-only` toggle only visible on Buildable tab;
(c) clicking Build-only reduces card list from 5 to 1 (only "Chatgpt, Openai
opportunity window" survives); (d) each card's evidence list shows multiple
sources (not 100% single-source as before S2980); (e) `View all N →` toggle
still works from S2979. ~10 min if browser is open.

**Browser UX smoke on shipped S2979 Theme Signals evidence (STILL OPEN from
S2979).** Load `/workspace?tab=intelligence&sub=theme-signals`, click one
Bluesky evidence row (should open `bsky.app/profile/…/post/…` in new tab) +
one Reuters/Google-News row (should open source article). Confirm
`View all N →` toggle expands/collapses without reordering. ~10 min if browser
is open.

**Phase B Theme Signals — "Why now" LLM summarizer (STILL OPEN from S2978).**
Replace the deterministic template with an LLM-generated 1-2 sentence summary
of what changed. Cache per cluster. Drop the `(Phase A template — expanded in
Phase B)` note from card component. ~1 session.

**Phase B Theme Signals — who-benefits/who-loses (STILL OPEN from S2978).**
Sector map + example tickers for Investable cards. Options: keyword→sector
regex map (fast), or LLM classification with ticker DB linkage (higher
quality). ~1-2 sessions.

**Theme Signals — sub-tab persistence via localStorage (STILL OPEN from
S2978).** Currently defaults to Buildable on every mount. Persist last-selected
sub-tab keyed by workspace_id. Trivial (~30 min).

**Rigby memory-store cap investigation (STILL OPEN from S2979).** Cap Rigby
hit at S2979 — investigate value, per-user vs global, failure mode. Rigby
tool gap ledger candidate. ~30 min diagnostic.

**Rigby Tool Gap Ledger — Fold D from S2982 (NEW at S2982).** DB uniqueness
constraint on `AgentExecution.celery_task_id`. Currently `db_index=True`, not
`unique=True`. Two fix options in the ledger entry: (a) `unique=True` +
migration + backfill dedup; (b) defensive log in `_finalize_queue_provenance`
when >0 existing rows share the intended celery_task_id. Option (b) is
smaller-blast-radius. ~30-60 min.

**Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission
helper.** 3-trigger threshold NOT yet met. Wait for signal.

**Post-close housekeeping (LOW priority).** Fill Playbook front-matter
`commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0.
~15 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote
  (post-v0.10.0 refresh). Points at Playbook v0.10.0 + version ancestry +
  workspace ratification records.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause).
  Session-shape contract for spec-originated implementation.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations
  mandatory for T1/A2). If Rigby returns empty tool_runs + generic AGREE,
  RE-ISSUE the routing.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we
  lose anything?" + "is it more work later?" before yes/no; ≤1 decision).
- **Cross-repo application:** PLAYBOOK-7.7.4 (Layer 1 context-kit primitives /
  Layer 2 repo-local surfaces; tag every SIGN finding with verification
  surface).
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Staged codification for enforcement:** PLAYBOOK-7.5.1.

---

## Wrapper pin note

The active PA conversation pin at S2982 close was `pa-f9e61e81a2514104`.
`session_lifecycle close` at S2982 close retires that pin and mints a fresh
one for S2983; wrapper `tools/pa_local.sh` is rewritten atomically. Commit
the wrapper diff in the S2982 close cascade PR per
`feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session
in S2983+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7
(A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal but MUST
be recorded in a handoff. Phase-skipping is NOT legal once the session enters
Phase 6 implement.

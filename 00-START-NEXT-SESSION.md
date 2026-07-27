# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2990 CLOSED. Findings-surface first real-use loop shipped 3-for-3.

**Four feature PRs merged this session — Flow A (real-use loop of the Audit Findings surface shipped at S2989 Phase B).**

**Finding #1 — `4b92f6f0-b84b-47d1-976a-30246f3dbd3d` (Half-wired drf-spectacular, executable).** Chris picked Path A (enable). PR #3642 (`8bf4e3c2a`) added `drf_spectacular` to `INSTALLED_APPS` + `REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'` at `core/settings.py:222,742` + 3 URL routes at `core/urls.py:5051-5062`. Chris then hit 401 in browser — `UnifiedTokenAuthenticationMiddleware` gates `/api/` before views. PR #3643 (`ec34f772a`) added `/api/schema/` to `PUBLIC_PATHS` at `core/auth_middleware.py:513` + explicit `permission_classes=[AllowAny]` on the three view instances (defense-in-depth). Live at `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/` — 918-path OpenAPI 3.0.3 doc, 16 `@extend_schema` decorators (all `sports/views.py`) now producing real metadata. Chris live-verified in browser.

**Finding #2 — `023d3301-df86-4879-893f-8fd5b0c460c8` (~1,857 undeclared endpoints, decision-evidence).** Different shape from #1 — source audit explicitly says *"Cat A boundary observation; enforcement decision belongs to Cat D S2504."* I initially framed X/Y/Z directly to Chris; Chris caught me: *"Don't forget to loop in Rigby if you need to."* Routed to Rigby → joint agreement on X (evidence report) + MODIFY (pinned Boundaries section) → single yes/no to Chris. PR #3644 (`808c50603`) shipped `docs/research/domains/api/2990_backend_contract_undeclared_endpoints_evidence_report.md` (185 lines) with pinned `## Boundaries (non-prescriptive)` section, per-module breakdown of the 121 distinct top-level API modules, state-changing (438) vs read-only (480) bucketing for Path C axis, and verbatim Path A/B/C quotes with line citations. Zero prescriptive verbs.

**Finding #3 — `3a89fddc-7b62-4093-afaa-1a9896c540f8` (permission_classes implicit inheritance, decision-evidence + STALE).** Verified state upfront (learned from #2). Caught **three staleness issues**: line refs drifted (`652-653` → `737-738`), `LeagueViewSet` example inverted (now DECLARES `permission_classes = [permissions.AllowAny]` at `sports/views.py:48`), and audit's 80-90% implicit-inheritance rate estimate was actually **2.3% via runtime URL-resolver walk** (19 of 818 DRF class-based views). Routed X/Y/Z + zoom-out to Rigby BEFORE framing to Chris (loop-first this time) → joint agreement on X + MODIFY (pinned Staleness section FIRST + forward-pointing audit addendum vs history rewrite). PR #3645 (`6f78b285a`) shipped two-file scope: new evidence report at `docs/research/domains/api/2990_permission_classes_implicit_inheritance_evidence_report.md` (161 lines) with full enumeration of the 18 in-repo implicit views clustered by module (8 sports betting + 5 intelligence income + 5 preview infra), plus small forward-pointing addendum at `2501_...audit.md:1335-1342` (11 lines).

**All 3 findings marked `status='fixed'` via ORM** with truthful `resolution_note` capturing the actual close state (`executable-fixed` / `evidence-delivered (decision pending)` / `evidence-delivered + STALE-CORRECTED`) even though the surface's only public status enum is `fixed`. Rigby tried but couldn't do the marking herself — `DocResearchFinding` not in `orm_inspect_tool` allowlist, `web_fetch_tool` has no session cookies. She honestly reported the blocker with 2 real `tool_runs` proving the attempt (textbook PLAYBOOK-7.7.2 SIGN behavior, not rubber-stamping).

**HEAD at close:** `6f78b285a` (docs cascade PR TBD, wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=6f78b285a550` post-PR-#3645.

Full context:
- `docs/handoffs/SESSION_2990_FINDINGS_SURFACE_FIRST_REAL_USE_LOOP.md`
- `docs/handoffs/SESSION_2989_SEND_TO_RIGBY_SPEC_SHAPE_AND_AUDIT_FINDINGS_SURFACE.md` (prior)

---

## S2991 primary directive — Findings-surface v2 fix/add/remove

**Chris ratified at S2990 close: S2991 focuses on the concrete fix/add/remove list surfaced by the 3-finding real-use retrospective.**

Two highest-leverage adds (shift ~2/3 of future flow from "improvise → Rigby rescue" to "template-fit → straight-through"):

1. **Close-mode taxonomy migration** — extend `DocResearchFinding.status` beyond `open`/`fixed` to `open` / `fixed_via_pr` / `evidence_delivered` / `deferred_to_arc` / `stale_reverify_required` / `informational`. Backfill existing `fixed` rows using `resolution_note` heuristics — start with the 3 S2990 rows as canonical examples. **Unblocks proper close state for the 3 findings marked this session.** ~1 session.

2. **Finding-type classifier at ingest** (`index_doc_research_findings`) — regex signals like `Cat A boundary observation` + `Chris-D-verdict at S<NNNN> xx99` → tag `type=decision_evidence`; signals like `blocks downstream X` + error-at-file-line → `type=executable`. Default `type=unknown`. Migration adds `finding_type` column + batch-classifies existing 900 findings. ~1-2 sessions.

**Ordered follow-on priorities** (dependency-aware, gated behind #1 and #2):

3. **Fix spec-generator prompt** — branch on `finding_type=decision_evidence` to swap in the `evidence_capture` template (Boundaries pinned by default, non-recommendation block, quote-only Path references). Removes the round-peg-square-hole rework Chris and Rigby did on findings #2 and #3. ~30-60 min.

4. **Add staleness detector at ingest** — walk `file:line` + identifier references in each finding text; verify still-matches at HEAD; tag `staleness=suspected` on mismatch. Batch pass over existing 900 findings after landing. Prevents silent surface degradation. ~1 session.

5. **Add Rigby tool allowlist entry** — add `DocResearchFinding` to `orm_inspect_tool` allowlist + wire session cookies into `web_fetch_tool` for authenticated GET/POST. Unblocks Rigby closing her own findings loop end-to-end. (Sharper form of S2989 carry-forward — real-use hit this session.) ~30-60 min.

6. **Add Rigby-SIGN nudge in UI** for `type=decision_evidence` findings at Send-to-Rigby time — soft hint before spec generation. ~30 min.

7. **Add F-A2-equivalent for downstream consumers** — when spec generator's ACs reference downstream artifacts (e.g., finding #1's "frontend api.ts type-generation" AC referenced a non-existent codegen consumer), verify existence and tag `_consumer inferred — verify_` the same way file paths are tagged. ~30-60 min.

8. **Add wire-through smoke-check AC** for half-wired findings — auto-add "verify from Chris's browser session, not just Django test client" to prevent 401-middleware-style landmines (as happened at finding #1 → PR #3643 follow-up). ~30 min.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2990 handoff in full — especially §"v2 gaps surfaced" and §"Open follow-ups for S2991+".
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `6f78b285a` → `808c50603` → `ec34f772a` → `8bf4e3c2a` → `137b21438`.
   - `USE_PGBOUNCER=0 python manage.py shell -c "from django.apps import apps; D=apps.get_model('core','DocResearchFinding'); print('open:', D.objects.filter(status='open').count(), 'fixed:', D.objects.filter(status='fixed').count())"` — should show `open` count reduced by 3 vs S2989 close, `fixed` count = 3.
   - `curl -sS http://localhost:8000/api/schema/ | head -c 200` — schema endpoint should return OpenAPI JSON without auth.

**Suggested first PR shape for S2991:** #1 (close-mode taxonomy migration) is the least-risk highest-leverage opener — it's a schema migration + enum swap + backfill script + optional UI dropdown. Landing #1 first means #2's classifier can immediately map `type=decision_evidence` findings to the new `evidence_delivered` / `deferred_to_arc` close modes.

---

## S2991 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### Carry-forward from S2989 (STILL OPEN)

- **F-D3-tracker-scope wire-up** — activate OpsRun tracker for PA turns. ~1 session. Highest-leverage backend seed.
- **F-D2-broad LLM-bypass audit spec** — evaluate user-facing personalization impact of each `enforce_real_ai` / `chat.completions` / `responses.create` non-PA callsite. Est ~1 session for the audit doc; each preflight wire-up is a small follow-up PR.
- **Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply`.** ~30 min diagnostic + apply. Recommended: `--stale-days 30 --stale-importance-lt 10 --apply`.
- **Canonical Briefing v2 scope toggle.** Arc-Folder / All-Docs + default exclude-globs. Additive UI + one migration (`Document.file_path` index). ~1-2 hr.
- **Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.** S2988 added `briefing_action_item`; systemic fix (default `deliverable_type` from `category` + skip missing_initiative_id marker for governance-scoped categories) still open. ~1 session.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN)** — per-section "Send all", workspace routing inference from arc slug, LLM-mediated deliverable creation via Rigby's actual turn loop. Any of these need Chris explicit ask.

### Older carry-forward (STILL OPEN)

- **Chris browser visual check on S2985 Canonical Briefing tab strip / Refresh behavior.** ~5 min.
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Chris browser visual check on S2984 arcs section.** ~5 min.
- **Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold).** JSON-401-on-XHR middleware pattern. Not blocking; open when 2nd independent trigger surfaces.
- **Live-dispatch smoke on S2982 stage-doc guardrails.** ~15 min.
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.** Dry-run `context-kit adopt` against `mentorforge` or `character-os`.
- **Browser UX smoke on S2980 Theme Signals UX upgrade.** ~5 min.
- **Phase B Theme Signals — "Why now" LLM summarizer.** ~1 session.
- **Phase B Theme Signals — who-benefits/who-loses.** ~1-2 sessions.
- **Theme Signals — sub-tab persistence via localStorage.** ~30 min.
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.
- **Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met. Wait for signal.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0. ~15 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). S2990 was Flow A (real-use loop from S2989's shipped feature), NOT spec-originated; straight-through Claude direct → verify at HEAD → Rigby SIGN → Chris yes/no → execute → verify → mark was legitimate.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). Rigby returned real tool_runs on both SIGN cycles + on the failed marking dispatch. Zero rubber-stamping — she also honestly flagged her own tool-surface blocker on marking.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?"; ≤1 decision). Findings #2 and #3 each surfaced as a single yes/no to Chris after Claude+Rigby joint agreement, per `feedback_claude_rigby_agree_first_chris_yes_no`.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised this session.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` (NOT `make celery-recycle`) for any PR touching `frontend/**`. All S2990 changes backend-only, so HEAD-range path-diff detection correctly skipped frontend rebuild on all 4 merges + close cascade.

---

## Wrapper pin note

The active PA conversation pin at S2990 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2990 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session in S2991+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7 (A2 SIGN), that is a PLAYBOOK-7.7.1 violation. S2990 was Flow A (real-use loop), which is not spec-originated. Rigby-SIGN was applied at joint framing (findings #2 + #3) which was the right shape for the decision-evidence-class findings, per this session's key finding-shape learning.

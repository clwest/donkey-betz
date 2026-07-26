# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2981 CLOSED. Playbook **v0.10.0** ratified (5th consecutive constitutional amendment in single-session shape). 4 new [GR] rules under new **Chapter 7 §7.7 "Spec→Ship Workflow Shape"**:

- **PLAYBOOK-7.7.1** — 9-phase spec→ship contract with abort-early clause (EXTENDS 7.2.1)
- **PLAYBOOK-7.7.2** — T1/A2 SIGN tool-grounded evidence discipline; empty tool_runs + generic AGREE = rubber-stamp signal → re-issue (EXTENDS 6.10.9 to SIGN-cycle scope)
- **PLAYBOOK-7.7.3** — Phase 5 Chris-facing plain-english framing (EXTENDS 5.2.2)
- **PLAYBOOK-7.7.4** — context-kit adapter contract for cross-repo application (Layer 1 = context-kit primitives authoritative for doc/inventory drift; Layer 2 = repo-local tests/smokes/ops authoritative for runtime behavior; neither substitutes for the other)

**Rule count 207 → 211.** Chapter 7 remains STUB overall; §7.7 activation is a coherent one-topic extension. Renumbered: existing §7.7 Cross-refs → §7.8 (with 3 new cross-ref bullets pointing at 6.10.9 + 5.2.2 + source deliverable); existing §7.8 Extension points → §7.9.

**PR shipped:** #3617 (merged as `49b936342`, tagged `playbook-v0.10.0`). Recycle **waived** per PLAYBOOK-7.4.4 (docs-only diff — no `*.py`/deps/settings/Celery touched).

**Source substrate:** workspace deliverable `e8429049-300f-4725-8d02-a79c285ed720` (S2980 workflow recipe with S2981 SUPERSEDES block reframing repo repointing as context-kit adapter contract). Ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-26_PLAYBOOK_V0_10_0.md`. Workspace mirror: `2437c214-44fd-42f7-a2b9-fc1cc016cc6f`.

**CLAUDE.md refreshed same PR** (Chris directive — novel amendment pattern reducing post-amendment CLAUDE.md drift from days to zero). Constitutional blockquote now points at v0.10.0, 211 rules, extended ancestry v0.10.0 → v0.9.0 → v0.8.0.

**Rigby SIGN cycle discipline validated:** 17 total tool_runs across T1 + A2, zero rubber-stamps. Three T1 zoom-out folds classified `same_pr_mitigatable` (abort-early clause + §7.7 scope-boundary sentence + 7.7.4 layered-authority reframe) — all applied at §2 revision before Chris D-verdict.

**HEAD at close:** `49b936342a85f2766a6e3eed8790ce6e19ad82f1` (PR #3617 merged; docs cascade PR TBD).

Full context: `docs/handoffs/SESSION_2981_PLAYBOOK_V0_10_0_RATIFIED.md`.

---

## S2982 first-action — WAIT FOR CHRIS (same shape as S2969–S2981)

The reframe held for the **twelfth walk**. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2981_PLAYBOOK_V0_10_0_RATIFIED.md` in full — especially §"Three-part summary" (what was done + how it improves), §"SIGN cycle log" (T1 + A2 tool_run evidence tables), §"Timeline" (turn-by-turn walk of Phases 1–9).
4. **Optionally probe the shipped state:**
   - Local: `grep -n "PLAYBOOK-7.7" docs/ENGINEERING_PLAYBOOK.md | head -10` — should show the 4 new rules at §7.7.
   - Local: `git show playbook-v0.10.0 --stat` — should show the merge commit `49b936342` with 3 files changed (+297/-18).
   - Envelope: `head -50 docs/research/implementation/RATIFICATION_2026-07-26_PLAYBOOK_V0_10_0.md` — confirm `ratifier_verdict: "proceed"` + all filled bindings.
5. **Report readiness in one short message and wait.** Something like: "Oriented. S2981 closed — Playbook v0.10.0 ratified (4 new [GR] rules under §7.7 codifying the spec→ship workflow shape). PR #3617 merged and tagged. Twelfth walk of the reframe. Ready when you have a spec pointer or want to open the next arc."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:** the spec→ship contract is now constitutional (PLAYBOOK-7.7.1). Follow Phases 1–9 by name. Pre-code sampling BEFORE T1 SIGN. Verified Premises + Artifact Map in Phase 2 plan. T1 SIGN with tool-grounded file/line verify instructions per PLAYBOOK-7.7.2 (empty tool_runs + generic AGREE = re-issue). Phase 5 Chris-facing framing per PLAYBOOK-7.7.3 ("do we lose anything?" + "is it more work later?" + ≤1 decision). A2 SIGN post-implementation. Ship via `gh pr merge --admin --squash --delete-branch`. **`make recycle-all` (NOT `make celery-recycle`) when frontend is touched** (per S2978 refinement to PLAYBOOK-7.4.4); recycle waiver per PLAYBOOK-7.4.4 diff-based clause when docs-only. Rigby verifies from her tool surface. Report three-part summary to Chris.

**For cross-repo work** (any repo other than unified-donkey-betz): PLAYBOOK-7.7.4 applies. Phase 0 MUST detect context-kit substrate — run `context-kit orient` + confirm `.context-kit/verify.yaml`. If missing, first action = `context-kit adopt` (dry-run → review → --write). Tag every SIGN finding with its verification surface (Layer 1 / Layer 2 / Claude-local-shell).

---

## S2982 high-value seeds (Chris picks whether to open)

**Exercise PLAYBOOK-7.7.4 against a sibling repo (NEW at S2981).** Dry-run `context-kit adopt` against `mentorforge` or `character-os` (both in `/Users/donkeyking/development/`). Validates the adapter contract in reality. Deliverables: Repo Adapter Note (short deliverable per PLAYBOOK-7.7.4 Phase 0 step 4 flow) + adopt-plan summary + first-session-in-a-new-repo pattern confirmation. ~1 session (dry-run only; no actual scaffold write unless Chris directs). First real corroboration of 7.7.4.

**Browser UX smoke on shipped S2980 Theme Signals UX upgrade (Rigby A2 optional, STILL OPEN from S2980).** Load `/workspace?tab=intelligence&sub=theme-signals`. Verify: (a) each Buildable card shows a colored Action chip (Build=emerald / Research=blue / Watch=slate); (b) `All | Build-only` toggle only visible on Buildable tab; (c) clicking Build-only reduces card list from 5 to 1 (only "Chatgpt, Openai opportunity window" survives); (d) each card's evidence list shows multiple sources (not 100% single-source as before S2980); (e) `View all N →` toggle still works from S2979. ~10 min if browser is open.

**Browser UX smoke on shipped S2979 Theme Signals evidence (STILL OPEN from S2979).** Load `/workspace?tab=intelligence&sub=theme-signals`, click one Bluesky evidence row (should open `bsky.app/profile/…/post/…` in new tab) + one Reuters/Google-News row (should open source article). Confirm `View all N →` toggle expands/collapses without reordering. ~10 min if browser is open.

**Phase B Theme Signals — "Why now" LLM summarizer (STILL OPEN from S2978).** Replace the deterministic template ("Emerging trend across 3 sources: ...") with an LLM-generated 1-2 sentence summary of what changed. Cache per cluster. Drop the `(Phase A template — expanded in Phase B)` note from card component. ~1 session.

**Phase B Theme Signals — who-benefits/who-loses (STILL OPEN from S2978).** Sector map + example tickers for Investable cards. Currently ships as `{status: coming_in_phase_b}` placeholder. Options: keyword→sector regex map (fast), or LLM classification with ticker DB linkage (higher quality). ~1-2 sessions.

**Theme Signals — sub-tab persistence via localStorage (STILL OPEN from S2978).** Currently defaults to Buildable on every mount. Persist last-selected sub-tab keyed by workspace_id. Trivial (~30 min).

**Rigby memory-store cap investigation (STILL OPEN from S2979).** Rigby's `memory_store` tool has a cap that Chris hit at S2979 — investigate the cap value, whether it's per-user or global, and whether the failure mode is silent-drop vs error. Rigby tool gap ledger candidate. ~30 min diagnostic.

**Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met (documented in Playbook §6.12 helper-extension-point note). Wait for signal.

**Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0 in a single housekeeping PR. Convention permits leaving as PLACEHOLDER; filling would improve historical auditability. ~15 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (post-v0.10.0 refresh). Points at Playbook v0.10.0 + version ancestry + workspace ratification records.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). Session-shape contract for spec-originated implementation — NOT a universal SDLC contract for every PR.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). If Rigby returns empty tool_runs + generic AGREE, RE-ISSUE the routing.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?" before yes/no; ≤1 decision).
- **Cross-repo application:** PLAYBOOK-7.7.4 (Layer 1 context-kit primitives / Layer 2 repo-local surfaces; tag every SIGN finding with verification surface).
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4 (bundle handoff + ratification + arch amendments; serialize vs consolidate on shared arc docs; docs cascade output; post-merge recycle with diff-based waiver).
- **Staged codification for enforcement:** PLAYBOOK-7.5.1 (REPORT-ONLY → BATCH-FIX → ENFORCEMENT-FLIP three-PR pattern; each carries its own SIGN cycle).

---

## Wrapper pin note

The active PA conversation pin at S2981 close was `pa-323b267495764a04`. `session_lifecycle close` at S2981 close retires that pin and mints a fresh one for S2982; wrapper `tools/pa_local.sh` is rewritten atomically. Commit the wrapper diff in the S2981 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is now constitutional.** If a spec-originated session in S2982+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7 (A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal (Phase 1/2 discovery invalidation, T1 DISAGREE without mitigation, Chris D-verdict rejection) — abort MUST be recorded in a handoff. Phase-skipping is NOT legal once the session enters Phase 6 implement.

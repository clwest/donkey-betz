# Current Handoff Pointer

> Stable pointer so future sessions don't have to lex-sort 600+ files to find the latest handoff.

**Latest strategy docs (Session 1116 — read for current state):**
- [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) (v1) — brand pivot Donkey Betz → 24/7 Global AI, soft-cut architecture
- [`docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`](../247_LIVE_INTELLIGENCE_PANEL_SKETCH.md) — first u-d-b → 247globalai.com integration; **shipped** this session
- [`docs/COST_SURVIVAL_AUDIT.md`](../COST_SURVIVAL_AUDIT.md) — Phase 0 gating constraints (still pending)

**Character OS merge — parked:**
- [`docs/MERGE_PROPOSAL_CHARACTER_OS.md`](../MERGE_PROPOSAL_CHARACTER_OS.md) (sidecar) and [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](../MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) (native) stay in tree as v2 backlog. Unpark only if a paying customer asks for an avatar.

**Latest handoff:** [`SESSION_1144_DOCS_CLEANUP_PROVENANCE_AND_LEAK_FIX.md`](SESSION_1144_DOCS_CLEANUP_PROVENANCE_AND_LEAK_FIX.md)
(**10 PRs open**, session closed clean. Rigby-driven docs cleanup wave + socket-leak fix + provenance tooling. **#2201** Postgres `CONN_MAX_AGE=60` + `CONN_HEALTH_CHECKS=True` + per-process caching in OpenAI/Anthropic factories — stops 33K TIME_WAIT leak (72% to :5432) caused by Session 142's `CONN_MAX_AGE=0`. **#2202** `DOC_LIFECYCLE §0` scope boundary — u-d-b `/docs/` vs `docs/docs-pattern/` (context-kit framework) separability. **#2203** `CLAUDE.md` + `CAPABILITIES.md` reframe — strip "source of truth for numbers" from PWII, enforce §2c. **#2204** 17-doc V1 banner sweep — flip PWII → PLATFORM_INVENTORY. **#2205** `python manage.py session_provenance --session N` — clusters docs+code by session of origin (Plan A, Rigby specced + reviewed). **#2207** `build_docs_index` fixes: "Current Session" was 6 stale + INDEX itself published hardcoded stale counts (meta-§2c violation). **#2208** Canon rebase — removed deprecated DaVinci entry, seeded 5 real anchors (PLATFORM_INVENTORY + DOC_LIFECYCLE + INDEX + 00-START-NEXT-SESSION + AUDIT_INDEX), "canon ≤10 docs" operating principle. **#2209** Spec status cleanup — 2 FLEET_MOVE specs `spec` → `implemented`. **#2210** Plans labeled historical — 13 files, INDEX rewrite + 11 V1 banners + B-full status corrected (git-verified shipped via #2016/#2017/#2018). **#2206** This handoff. Also: socket leak locked Chris out of login → `sudo sysctl -w net.inet.ip.portrange.first=32768` + password reset. Process update: commit-message hygiene rule — every session-NNNN commit subject should include `session-NNNN`. Session 1145 starts with `docs/architecture/` sweep (Rigby pre-specced rules in handoff).)

**Previous:** [`SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md`](SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md)

## How to update

When a new session writes a handoff, update **only** the "Latest" line above and shift the prior entry into "Previous." Keep this file at exactly two pointer entries — the full history lives in the lex-sorted handoffs directory.

## Source-of-truth reminders

- **Counts:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) is canonical.
- **Narrative:** [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md).
- **Audit workspace:** [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md).
- **PA route:** `POST /api/pa/chat/` (canonical). `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.

---

*Established: Session 1101 (2026-05-07) under `docs/audit/CLEANUP_PLAN.md` Phase 5.*

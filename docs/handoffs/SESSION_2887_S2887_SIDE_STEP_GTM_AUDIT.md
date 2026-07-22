# Session 2887 — S2887 side-step: GTM gap audit + repo_tool cross-repo + Character OS EB.4 + port collision fix + C3 bridge-answer persistence

**Date:** 2026-07-22
**Session pin (retired at close):** `pa-5af4deadc357415c` (labeled `s2887-open`; minted at S2886 close)
**Prior pin retired at S2886 close (not this session):** `pa-35b93928b15f4a9c`
**Slate label:** S2887 side-step — Chris directive at session open pivoted from the queued Ledger #13 `td_error.py` extraction to a GTM-focused audit + implementation arc.
**PRs shipped (5 total, 4 merged to origin):**
- u-d-b PR #3398 `b929e5be7` — repo_tool cross-repo scoping
- character-os PR #2 `8cbf181` — EB.4 SPA settings panel for EngineConnection
- character-os PR #3 `348aed8` — Postgres port collision fix (5433 → 5434)
- character-os PR #4 `dc67d2e` — C3 bridge-answer Asset persistence

---

## What Chris asked for at session open

"Please begin."

Then, before the ratified S2887 first-action (Ledger #13 `td_error.py` extraction) could start, Chris pivoted:

> "Before we begin can we do one small side step please? We did a massive system audit and you and Rigby did research on what Donkey Betz has become and a couple of the things for user facing was to use Rigby as a service and to connect to Character OS to Donkey Betz. If possible can you and Rigby create an audit on exactly what we would need to focus on to achieve those two things so we can start working towards going to market."

That directive drove the entire session. The Ledger #13 extraction remains queued for S2888.

---

## What shipped (in order)

### 1. GTM gap audit — `docs/investigations/2026-07-22_RIGBY_SAAS_AND_COS_BRIDGE_GTM_GAP_AUDIT.md`

Engineering-scoped audit against two ratified S2841 opportunities (Rigby-as-a-Service + Character OS ↔ DBZ bridge). Read-only survey of all three sibling repos (`unified-donkey-betz`, `character-os`, `context-kit`). Not a strategic discovery arc — the D6 moratorium was respected throughout.

Key findings:
- **Rigby-as-a-Service auth spine already exists.** `FleetSignatureAuthentication` at `core/services/fleet_auth_drf.py` + `fleet_pa_chat_audit` warn-mode + 12 registered external_repos + `provision_fleet_identity` mgmt command. Gap is the last 20%: reject-mode flip, per-tenant billing/metering, customer-facing key-issuance UI, published API contract docs, SDK.
- **Character OS ↔ DBZ bridge already 80% shipped.** Backend `EngineConnection` model + DRF viewset + `test_ping` shipped at Char-OS SESSION 217 (EB.0-EB.3). Gap on Character OS side: EB.4 SPA panel (this session), C3 bridge-answer persistence (this session), C4 PD-1 timeout fix, C6 tool catalog, C5 non-realtime bridge invocation.

Two workspace mirrors created by Rigby (per `feedback_rigby_writes_workspace_deliverables`):
- Deliverable `60cc462b-3abf-4cae-a809-cdb3b538f284` — content mirror of the audit, in DBZ workspace `b4503364-2573-4401-9e28-61a739e0ce50`.

### 2. `repo_tool` cross-repo scoping — u-d-b PR #3398 (`b929e5be7`)

Tool-gap surfaced during Rigby's first SIGN pass: her `repo_tool` was hard-scoped to u-d-b root and couldn't read sibling repos. Chris ratified fixing it immediately. Shipped in the same session:

- Optional `repo_id` param routes reads to sibling repos via `config/external_repos/<slug>.json` profile `root_path`.
- New `list_repos` action enumerates registered profiles with on-disk existence per row.
- Cross-repo security widening (Rigby's Q6 zoom-out fold):
  - BLOCKED_FILE_SUFFIXES: `.pem`, `.key`, `.pfx`, `.p12`, `.keystore`, `.jks`.
  - BLOCKED_FILE_PREFIXES: `.env.*`.
  - BLOCKED_DIRS expanded with `.aws`, `.ssh`, `.gnupg`, `secrets`, `.terraform`, `.docker`.
  - Per-repo `protected_paths` from JSON profile layered as additional denylist.
- Taxonomy fix: `_safe_path`-raised ValueErrors now emit `permission_denied` (5-code taxonomy) instead of the out-of-taxonomy `value_error` code. Extends the S2876→S2886 error-envelope migration arc.
- Strict slug validator (`[a-zA-Z0-9][a-zA-Z0-9._-]*`) — rejects `../evil`, `char/os`, `char\os`, etc.
- Fixed two stale profile `root_path` values (character-os + context-kit → `/Donkey_Betz/`).
- 12 new tests + 1 updated for the taxonomy fix. Regression: 26/26 pass on `test_repo_tool_validation_2728` + 22/22 on `test_s2875_cross_tool_error_envelope`.

Post-merge Rigby verified end-to-end: read `character-os/docs/CHARACTER_OS_WHAT_IT_IS.md` via `repo_id='character-os'`, enumerated the 3 bridge tools via tree, and confirmed all 5 sanity checks passed. This unblocked her ability to independently verify Character OS side claims in the audit.

### 3. R1a proposal rejected; C1 (EB.4) ratified as concrete first move

Rigby's SIGN pass 2 caught a material finding: 100% of `FleetPAChatAuditRow` for the last 7 days are `auth_mode='bearer_only'`. Zero fleet-signature rows. Root cause (tool-grounded via her cross-repo read): character-os `consult_engine.py:87-92` uses `Authorization: Token`, not fleet HMAC.

The audit initially recommended R1a (upgrade character-os bridge tools to fleet HMAC). Chris corrected mid-session: **character-os is not part of the original fleet.** The fleet HMAC path was designed for the 7 sibling apps (mentorforge, sellerpilot, etc.); retrofitting it onto character-os would stretch a mechanism to serve a purpose it wasn't designed for.

R1a formally rejected in audit §6.5 (recorded as an architectural-fit mistake so future sessions don't retry). C1 (EB.4 SPA settings panel) ratified as the concrete first move.

### 4. Character OS EB.4 — SPA settings panel — char-os PR #2 (`8cbf181`)

Pure SPA work; the DRF `EngineConnection` viewset was already shipped at char-os SESSION 217. Narrow scope per Chris directive:
- Workspace-specific engine URL + token config
- Existing auth + workspace boundaries preserved (viewset uses `IsAuthenticated` + `IsWorkspaceMember`; workspace inferred from user)
- `engine_token` write-only end-to-end; UI displays only `****last4` preview after save (contract rule 4)
- Pro+ tier gate mirrored on client (Starter workspaces see upgrade nudge)
- `test_ping` button surfaces backend result inline (status_code + latency + response preview)
- Env-var fallback preserved in the resolver — this UI does not remove `UDB_PA_API_URL` / `UDB_PA_API_TOKEN`
- No fleet HMAC changes; no new tenant API-key architecture

New files:
- `web/src/lib/api/engine-connections.ts` (180 lines) — TanStack Query hooks + zod schemas + CRUD helpers
- `web/src/routes/settings/engine-connections.tsx` (614 lines) — settings page with tier gate / create form / read-only card / edit form / delete confirmation / test_ping UX
- `web/src/routes/settings/engine-connections.test.tsx` (275 lines) — 6 vitest cases covering tier gate, Rule 4 token invariant, schema drift signal
- `web/src/App.tsx` — route registration at `/settings/engine-connections`

Regression: 476/476 SPA vitest pass (was 470; +6 new EB.4). TypeScript build clean. ESLint clean on touched files.

### 5. Character OS workspace reconciliation

Post-EB.4 merge, local `Donkey_Betz/character-os/main` diverged from origin — 5 local-only EB.0-EB.3 commits were superseded by squash-merges on origin. Chris directed a systematic reconciliation before `git reset --hard`:

- Every local-only commit verified byte-identical or superseded on origin (14/14 code files identical, 3/3 living docs newer on origin — SESSION 218 P0 revisions).
- Untracked `docs/production-readiness/dogfood-2.4/` (23 SESSION 221 evidence files) confirmed unaffected by reset.
- Both Claude and Rigby independently returned SAFE verdict per Chris's dual-SIGN rule. Rigby's first pass returned CONDITIONAL because her `repo_tool` reads working tree (local state), not origin; Claude provided git-verified origin content inline, Rigby revised to SAFE.
- Reset executed. HEAD `8cbf181` = `origin/main`. All EB backend + SPA + provider-status + production-readiness artifacts verified present.

### 6. Postgres port collision — proper fix — char-os PR #3 (`348aed8`)

Chris's clarification: "there was one port that Donkey Betz and Character OS are both using but for different reasons that we just put a bandage on yesterday but needs to be fixed properly."

Root cause: `:5433` shared by u-d-b PgBouncer (IPv4 `127.0.0.1:5433`) and character-os docker Postgres (IPv6 `[::]:5433`). psycopg2 was falling through IPv4 rejection to IPv6 success on every character-os connect. The S221 bandage (`.env DB_PORT=5434`) was correct client-side intent but the docker-compose was never updated to expose on 5434, AND the workspace `start-character.sh` script wasn't sourcing `.env`, so Django was silently defaulting to `settings.py`'s 5433.

Proper fix — 4 edits across 2 repos + parent workspace:
- **character-os PR #3** — `infra/docker-compose.yml` maps `5434:5432`. Data volume `character_os_postgres_data` preserved.
- **`Donkey_Betz/scripts/start-character.sh`** (parent, not a git repo) — `shell` and `media` startup branches now `set -a; . "$COS_DIR/.env"; set +a` so Python processes actually see `DB_PORT=5434`, `OPENAI_API_KEY`, etc.
- **`Donkey_Betz/Makefile`** — `infra-up` wait-loop + help text bumped `:5433` → `:5434`.
- **character-os `.env` comment** — corrected to reflect the actual docker-compose mapping.

Verified live end-to-end:
- Fresh character-os Django (PID `38385` then `40226`) on `:8010`, ORM query returns `configured PORT=5434`, connects to `character_os` DB.
- Fresh media-engine (PID `38540` then `40247`) on `:8001`.
- SPA (PID `41458`) on `:5174` unchanged.
- **u-d-b Daphne `/health/ping/`**: 200 in ~3ms — completely unaffected.
- Port map now clean: `:5432` postgres · `:5433` pgbouncer · `:5434` character-os postgres · `:6381` character-os redis.

### 7. C3 bridge-answer Asset persistence — char-os PR #4 (`dc67d2e`)

Ratified per audit §6.4 as follow-on to EB.4. Engine-bridge tool answers now persist as workspace-scoped `Asset(role=BRIDGE_ANSWER)` rows instead of evaporating at session end.

- New `AssetRole.BRIDGE_ANSWER` (12th role) + migration `0011_c3_bridge_answer_role` (single AlterField).
- Shared `create_bridge_answer_asset(session, *, tool_name, question, answer, engine_url, cost_micros, conversation_id?, latency_ms?, intent?)` helper in `apps/realtime/engine_bridge.py`. Co-located because the 3 bridge tools already import `resolve_engine_connection` from there.
- Asset shape: `workspace=session.workspace`, `asset_type=TRANSCRIPT`, `role=BRIDGE_ANSWER`, `title=[<tool>] <question[:96]>` (fits 120 char cap), `file_path=""`, `inline_content=`full answer, `source_spec={tool_name, engine_url, question, conversation_id?, latency_ms?, intent?}`, `cost_micros=`tool cost, `composition=None` (library asset).
- Each of the 3 bridge tools calls the helper on success + returns `asset_id`. Empty answer OR failure path → skip creation.
- `agent_consult` populates `source_spec.intent=agent_name` so the library is filterable by producing agent.
- `_execute_inline` (sync dispatch) now harvests `asset_id` + `composition_id` from executor return dict, mirroring the async wrapper at `tasks.py:373-397`. Closes the pre-C3 foot-gun where `attach_memory` (async) linked its Asset but the 3 bridge tools (sync) could not.
- 11 new tests in `test_engine_bridge.py`; updated 2 existing tests (enum count + isolation allowlist). **912/912 realtime+compositions pass**.

Cross-workspace isolation preserved: helper sets `Asset.workspace=session.workspace`; `pre_save` signal still fires.

---

## Rigby SIGN provenance across the session (all tool-grounded)

- **Audit pass 1 (pre-repo_tool-fix):** DBZ-side claims verified; Q3 R1 telemetry PARTIAL/too-soon; Q4 customer framing PARTIAL (favor mentorforge/sellerpilot); Q_zoom_out AGREE with D6-moratorium + Playbook rule cross-checks. Logged repo_tool tool-gap to Rigby Tool Gap Ledger (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`).
- **Audit pass 2 (post-repo_tool-fix):** Q_A verdict Option 3 → Option 2 (drove §6 revision, R1a proposal). Q_B Character OS §3.1 claims verified via 8 tool_runs. Chris then corrected R1a as architectural mis-fit.
- **Reconciliation SIGN:** initial CONDITIONAL (working-tree-only visibility); revised SAFE after git-verified origin content pasted inline.
- **EB.4 design SIGN:** Q1-Q5 AGREE, Q6 PARTIAL (no `useWorkspaceTier` hook exists → use existing `useSubscription` from `workspaces.ts`). All folds baked in.
- **C3 design SIGN:** Q1-Q6 AGREE with minor field-value corrections (lowercase enum strings, tool_name prefix in title). Q_zoom_out PARTIAL — flagged no v1 length cap, tool_name prefix, sync-vs-async parity as important. All baked in.

Zero rubber-stamp SIGN cycles detected; per-question tool_runs verified throughout.

---

## Deferred / carried forward from S2887

Everything below survives into S2888's queue:

1. **Ledger #13 `td_error.py` extraction** — original S2887 first-action, queued behind this side-step. Adopter gate MET at S2886 close (6/6). No architectural change; simple mechanical extraction of the file-local `_handler_error` helper into `core/services/td_error.py`, updating 6 adopter files' imports. Expected diff ~+30/-168, single PR.
2. **Playbook v0.9.0 amendment cycle (2 rules at 2nd trigger)** — Fold 1 `TransactionTestCase` for dispatcher-DB tests + Fold 2 shared-taxonomy branch fortification. From S2886.
3. **R1 (fleet reject-mode flip)** — DEFERRED. Fleet HMAC path is dormant per Rigby's telemetry finding; revisit only if fleet apps resume calling `/api/pa/chat/`.
4. **C4 PD-1 timeout coordination defect** (Sev-1) — Character OS-side, blocks reliable realtime session start in real mode. Not touched this session.
5. **C5 non-realtime bridge invocation + C6 tool catalog** — Character OS-side follow-ons.
6. **Live UI dogfood of EB.4 + C3** — configure per-workspace connection via `/settings/engine-connections/`, hit `test_ping`, then trigger a bridge tool in a realtime session, verify Asset(BRIDGE_ANSWER) shows up in the workspace library. This is the reference-customer verification loop the audit set up.
7. **Rigby Tool Gap Ledger review** — 1 new entry (repo_tool cross-repo gap, RESOLVED same-session via PR #3398).

---

## Cross-repo docs cascade at this close

**Repo canonical (Claude-authored, this file):**
- u-d-b: `docs/investigations/2026-07-22_RIGBY_SAAS_AND_COS_BRIDGE_GTM_GAP_AUDIT.md` — the audit itself.
- u-d-b: `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md` — this handoff.
- u-d-b: `00-START-NEXT-SESSION.md` refresh for S2888.
- u-d-b: `tools/pa_local.sh` wrapper pin bump `pa-5af4deadc357415c` → S2888 mint.

**Workspace canonical (Rigby-authored):**
- Content mirror of the audit — deliverable `60cc462b-3abf-4cae-a809-cdb3b538f284`, workspace `b4503364-2573-4401-9e28-61a739e0ce50`, category `research_finding`, `deliverable_type='audit_report'`.

**Note on ratification records:** unlike playbook-amendment sessions, this session shipped no methodology change and no ratification envelope is required. The audit itself IS the ratifiable artifact; Chris's D-verdict on R1a rejection + C1 EB.4 + C3 all land inline in the audit's §6 sections.

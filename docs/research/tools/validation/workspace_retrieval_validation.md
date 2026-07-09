# Workspace Retrieval — Validation Report

**Tool:** workspace retrieval surface — three related but divergent entry points into `ProjectWorkspace` resolution.
**Files traced:**
- `core/services/workspace_manager.py:1570-1852` — `WorkspaceManager` class + `get_active_workspace` (line 1697-1729) + `_ensure_system_workspace` + `_ensure_personal_workspace` + `get_codebase_workspace`.
- `core/services/workspace_resolver.py:1-50` — standalone module with `get_active_workspace(user)` + `get_active_workspace_id(user)`.
- `core/agents/base_agent.py:5355-5552` — `BaseAgent.execute_with_workspace` file-writing wrapper.

**Downstream consumers (traced in prior tools):**
- PA entrypoint auto-injects `workspace_id` into every tool call (`unified_pa_entrypoint.py:2101-2113`).
- `deliverable_tool` workspace scoping (Batch A tool 1).
- `run_agent` context promotion of `workspace_id` (Batch A tool 5).
- `_impl_process_url_async` user-owned Document creation (Batch B tool 3 F-KI-2 patch context).

**Session validated:** S2728 → S2729 (Batch B tool 5 of 5).
**HEAD at validation:** `5ce56b5f` + Batch B tools 1-3 uncommitted patches.
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (regression tests suffice).
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch B tool 5 of 5 — Batch B CLOSED). Trace + 2 patches (F-WS-4 narrow-except, F-WS-1 log-only visibility) + 11 regression tests complete; 122 total pass across all Batch A + Batch B validation-2728 files.

---

## 1. Intended purpose

Resolve which `ProjectWorkspace` a caller should operate against. Three surfaces:
- **`WorkspaceManager.get_active_workspace()`** — full 4-tier fallback with SIDE EFFECTS (auto-creates workspaces). Used by agent execution paths.
- **`workspace_resolver.get_active_workspace(user)`** — thin 2-tier lookup, NO side effects, broad-except returns None. Used by media / DeliverableFactory paths.
- **`BaseAgent.execute_with_workspace()`** — post-execute wrapper that extracts files from agent output + writes to workspace + surfaces write status in result.data.

## 2. Rigby's belief (per MEMORY + prior tool context)

Rigby uses workspace resolution indirectly. She dispatches tools that carry `workspace_id` in payload (auto-injected by PA entrypoint); downstream handlers reach for the workspace via one of these three surfaces. Load-bearing MEMORY rules:
- **`feedback_pa_local_verify_ownership`** — Rigby must confirm token resolves to `donkeyking` and conversation belongs to her user before scope-sensitive work. Applies to workspace-scoped tools.
- **F-B-HIGH-3 workspace-membership implicit permission gate** (S2600 PA arc) — `execute_with_workspace` at line 5355 IS the identified surface; `WORKSPACE_AWARE_AGENTS` (20 agents in `core/epa_handlers_tools.py:3873-3922`) dispatch through this path.

## 3. Function signatures (verbatim capture)

### 3.1 `WorkspaceManager.get_active_workspace() -> Optional[ProjectWorkspace]`

4-tier fallback (line 1697-1729):
- **T1:** `ProjectWorkspace.objects.filter(user=self.user, is_active=True).order_by('-total_operations', '-created_at').first()` — user's own most-active workspace (S907).
- **T2:** if `self.user.is_superuser` AND T1 empty → same query without user filter (**cross-user fallback**, S1085).
- **T3:** if `self.user.username == 'system_autonomous'` AND T1-T2 empty → `_ensure_system_workspace()` (S855).
- **T4:** if T1-T3 empty AND `self.user` truthy → `_ensure_personal_workspace()` (S858 — creates workspace under `generated_content/users/{username}/`).

### 3.2 `workspace_resolver.get_active_workspace(user) -> Optional[ProjectWorkspace]`

Thin 2-tier lookup (line 19-41):
- Return None if `user` falsy.
- T1: `ProjectWorkspace.objects.filter(user=user, is_active=True).first()`.
- T2: `ProjectWorkspace.objects.filter(user=user).first()` — any workspace owned by user.
- Broad `except Exception` → return None with WARNING log.

### 3.3 `BaseAgent.execute_with_workspace(task, context, user=None, write_to_workspace=True, base_path='') -> AgentResult`

Wrapper (line 5355-5552):
- Calls `self.execute(...)`.
- If failure or `write_to_workspace=False` → return as-is (silent skip).
- Extracts files from `result.data['results'][i]['data']['files']` OR `code` OR `structured_report` OR `message` (heuristic ladder).
- Writes via `_write_files_to_workspace(...)`.
- Injects `workspace_write`, `partial_failure`, `file_write_failures`, `file_write_errors` into `result.data`.

## 4. Handler behavior (traced)

### 4.1 `WorkspaceManager.get_active_workspace` (line 1697-1729)

- Line 1710-1713: **T1 primary lookup** ordered by `-total_operations, -created_at` (S907 tie-break rationale).
- Line 1716-1719: **T2 superuser cross-user fallback** — if no user-owned workspace, superuser inherits ANY active workspace (regardless of owner). Ordered by same criteria. **F-WS-1** — SECURITY visibility gap.
- Line 1722-1723: T3 system-user fallback.
- Line 1726-1727: T4 personal-workspace auto-creation.
- **`get_*` method with SIDE EFFECTS** (T4 creates a workspace + T3 may create one via `_ensure_system_workspace`). Documented in S855/S858 comments. **F-WS-2** — REST-shape convention violation (documented but surprising).
- **No response signal indicating which tier fired.** Callers can't distinguish "my own workspace" from "cross-user superuser fallback" from "auto-created personal workspace." **F-WS-3.**

### 4.2 `workspace_resolver.get_active_workspace` (line 19-41)

- Line 24-25: fail-loud on falsy user (return None).
- Line 26-35: 2-tier lookup with silent broad `except Exception` at line 36-41. **F-WS-4** — same class as F-RG-1 (S1234 D17-D21 narrow-except discipline).
- Function IS pure-lookup with NO auto-creation side effects. Cleaner semantics than `WorkspaceManager.get_active_workspace`.

### 4.3 `execute_with_workspace` (line 5355-5552)

- Line 5382: `target_user = user or self.user` — defaults to agent's user.
- Line 5385-5390: delegates to `self.execute(...)`.
- Line 5393-5394: **silent skip if `not result.success` OR `not write_to_workspace`.** Returns as-is. No signal in `result.data` about the skip.
- Line 5401-5424: file extraction ladder (results.data.files → results.data.code → result.message code blocks).
- Line 5426-5504: **heuristic report-file creation** — if no files extracted AND `structured_report > 200 chars` OR (`result.message > 500 chars` AND (has formatting markers OR is a report-producing agent by class-name match)) → auto-create markdown file with class-name-derived category path. **F-WS-6** silent heuristics; hardcoded thresholds (500, 200) undocumented; category_map duplicated at 5440-5449 and 5482-5491.
- Line 5506-5551: writes files, injects `workspace_write` metadata, updates message.
- **F-B-HIGH-3 workspace-membership implicit permission gate** (from S2600 PA arc): `_write_files_to_workspace` doesn't verify `target_user` has membership on the workspace they're writing to — it relies on prior `get_active_workspace` scoping.

## 5. Defaults inventory

| Function | Param | Default | Notes |
|---|---|---|---|
| `WorkspaceManager.get_active_workspace` | (self) | — | Reads `self.user` from constructor |
| `WorkspaceManager._ensure_personal_workspace` | (self) | — | Auto-created workspace name: `{username}-personal`; root: `generated_content/users/{username}/`; `allow_file_write=True`, `allow_file_delete=False`, `allow_git_operations=False`; `protected_paths=['.env', '.env.local', 'secrets/', 'credentials/']` |
| `workspace_resolver.get_active_workspace` | user | required | Returns None on falsy user |
| `execute_with_workspace` | user | None → `self.user` | |
| `execute_with_workspace` | write_to_workspace | True | Silent skip when False |
| `execute_with_workspace` | base_path | '' | Directory prefix for written files |

## 6. Hidden filters

- **`WorkspaceManager.get_active_workspace` T2 superuser fallback** — cross-user workspace returns are the primary hidden semantic. Not surfaced.
- **`execute_with_workspace` heuristic report-file creation** — `structured_report > 200 chars`, `message > 500 chars` + formatting markers list, class-name-based category assignment. Silent.

## 7. Limits inventory

- No batch_size / limit on any of the retrieval functions.
- `execute_with_workspace` heuristic thresholds: 500 chars (message), 200 chars (structured_report).

## 8. Silent-truncation test

N/A.

## 9. Silent-filter test

- **F-WS-1**: superuser without own active workspace gets cross-user fallback silently. VERIFIED via code trace.

## 10. Silent-fallback test

- **F-WS-4**: `workspace_resolver.get_active_workspace` broad-except returns None on any error — indistinguishable from "user has no workspace" or "wrong DB state." VERIFIED via code trace.
- **execute_with_workspace** silent skip on failure or `write_to_workspace=False`. No signal in result.data.

## 11. Staleness test

- `is_active` flag drives selection. Reactivation (line 1819-1820) via `.save(update_fields=['is_active'])` — bypasses cache.

## 12. Freshness signal

- Response `ProjectWorkspace` includes `created_at`, `updated_at`, `total_operations` implicitly. No separate "resolution timestamp."

## 13. Provenance signal

- `execute_with_workspace` result.data receives `workspace_write` block with `workspace` (name), `total_written`, `total_failed`, `partial_failure`, `file_write_errors[]`. Good provenance surface for writes.
- **`WorkspaceManager.get_active_workspace` return has NO resolution_tier signal.** Rigby / operators can't tell WHICH tier fired. **F-WS-3.**

## 14. Authority / workspace assumptions

- `WorkspaceManager.get_active_workspace` T2 = **explicit cross-user access** for superusers. Documented in S1085; Chris ratified.
- `workspace_resolver.get_active_workspace` is STRICTLY user-scoped — no cross-user fallback.
- `execute_with_workspace` inherits scoping from `get_active_workspace` call chain; no independent authority check.

## 15. Runtime dependencies

- Django ORM (`ProjectWorkspace`, `User`).
- `subprocess` for git branch/remote detection (workspace registration only, not in the get path).
- Filesystem for `_ensure_personal_workspace` (creates `user_dir`).

## 16. Recoverable failure modes

- `workspace_resolver.get_active_workspace`: DB error → warn log + return None (F-WS-4 currently too broad).
- `WorkspaceManager._ensure_personal_workspace`: line 1849-1851 broad `except Exception` → warn log + return None.
- `execute_with_workspace._write_files_to_workspace`: returns partial_failure metadata.

## 17. STOP-and-report failure modes

- `WorkspaceManager.get_active_workspace` T1: uncaught DB error propagates (no try/except).
- Similar for the register/scan paths.

## 18. Operator-action failure modes

- User with no workspaces triggers auto-creation (T4). Not a failure; but silent.
- Superuser without own workspace inherits another user's (T2). Not a failure at HEAD; SECURITY visibility gap (F-WS-1).

## 19. Existing test coverage

**Modest existing coverage:**

- `test_base_agent_workspace_write_visibility.py` — 3 tests (S1230 F1 partial-write metadata visibility; get_active_workspace mocked).
- `test_workspace_resolution.py` — 4 tests (deliverable-workspace routing).
- `test_workspace_pa_modes.py` — PA-mode workspace binding.
- `test_diagnostic_workspace_resolver.py` — diagnostic-specific resolver.
- `test_deliverable_tool_workspace_parity.py` — parity checks.
- `test_initiative_workspace_diagnostics.py` — initiative + workspace diagnostics.

**Coverage gaps identified:**
- No test for `WorkspaceManager.get_active_workspace` T2 superuser cross-user fallback (F-WS-1).
- No test for `workspace_resolver.get_active_workspace` narrow-except discipline (F-WS-4 target).
- No test for `execute_with_workspace` silent-skip behavior when `write_to_workspace=False` or `result.success=False`.

## 20. Change list

**Code patches (one commit per defect per campaign plan §12.1):**

| File | Lines (post-patch) | Defect | Change |
|---|---|---|---|
| `core/services/workspace_resolver.py` | 20-38 | F-WS-4 | Added module-level `_WORKSPACE_RESOLVER_ENV_ERRORS = (DatabaseError, ConnectionError, OSError)` allowlist mirroring `_PERSONAL_MEMORY_ENV_ERRORS` from the S1234 D21 baseline. Same lazy-Django-import shape used across the D17-D21 allowlists. Extends the invariant tracked by `test_d20_views_rag_embeddings_narrow_except.py::test_all_four_allowlists_have_same_shape`. |
| `core/services/workspace_resolver.py` | 60-83 | F-WS-4 | Narrowed the broad `except Exception as _e:` to `except _WORKSPACE_RESOLVER_ENV_ERRORS as _e:`. Log level upgraded from WARNING to ERROR to match environmental-error severity. Return contract unchanged (None on env errors); logic errors now propagate. |
| `core/services/workspace_manager.py` | 1725-1758 | F-WS-1 | Added `logger.warning(...)` when S1085 superuser cross-user fallback fires. Log names requesting_user + fallback workspace + fallback owner. Zero behavior change; log-only. Preserves the intentional S1085 semantics while enabling operator diagnosis. |

**Test files added:**

- `core/tests/test_workspace_retrieval_validation_2728.py` — 11 regression tests across 4 test classes: F-WS-4 allowlist shape + membership + D17-D21 invariant extension to 6-way (3 tests); source-level broad-except discipline check (1 test); logic-error propagation + env-error safety valve for DatabaseError / ConnectionError / OSError + falsy-user short-circuit (5 tests); F-WS-1 superuser cross-user fallback log verification + no-log-when-superuser-has-own-workspace regression guard (2 tests).

**Docs updated:**

- Validation report (this file) records the trace + findings + patches + tests.

**Docs NOT updated (per campaign plan §2 anti-scope):**

- No schema description changes (workspace retrieval is a substrate module + agent-level wrapper, not a PA-schema-declared tool).
- `docs/topics/personal-assistant.md` — pending Batch B close.

**MEMORY.md:**

- No new rules added. `feedback_pa_local_verify_ownership` (workspace + conversation ownership discipline) remains VALID at HEAD.

**Test verification:**

- `python manage.py test core.tests.test_workspace_retrieval_validation_2728` → **11/11 pass** (0.274s).
- Full Batch A + Batch B cross-tool regression sweep (10 validation-2728 files + adjacent canonical_authority tests): **122/122 substantive pass** (16.8s) with 1 pre-existing skip. Zero cross-tool interference.

---

## Findings

### F-WS-4 — `workspace_resolver.get_active_workspace` broad-except returns None silently (MEDIUM)
- **Class:** DEFECT-CLASS-D2 (silent behavioral consequence).
- **Evidence:** `core/services/workspace_resolver.py:36-41`. Same class as F-RG-1 — the S1234 D17-D21 narrow-except discipline already applied to sibling retrieval helpers.
- **Severity:** MEDIUM. When DB errors occur, callers get None indistinguishable from "user has no workspace." Downstream `DeliverableFactory` + media creation paths get "no workspace" and take the orphan-Deliverable path silently.
- **Action:** PATCH — extend the D17-D21 discipline. Add module-level `_WORKSPACE_RESOLVER_ENV_ERRORS = (DatabaseError, ConnectionError, OSError)` mirroring `_PERSONAL_MEMORY_ENV_ERRORS` shape. Narrow the except so logic errors propagate.

### F-WS-1 — `WorkspaceManager.get_active_workspace` T2 superuser cross-user fallback silent (LOW-MEDIUM; visibility)
- **Class:** UNDER-DOCUMENTED / SECURITY visibility gap.
- **Evidence:** `core/services/workspace_manager.py:1716-1719`. Superuser without own active workspace silently inherits ANY user's most-active workspace.
- **Severity:** LOW-MEDIUM. This behavior is **intentional** (S1085 Chris ratified) — but the CALL SITE has no log entry indicating cross-user fallback fired. If Rigby dispatches and lands in someone else's workspace, no diagnostic trail exists.
- **Action:** PATCH (log-only, no behavior change) — `logger.warning(...)` when T2 fires naming the fallback workspace's owner. Existing S1085 behavior preserved.

### F-WS-2 — `get_active_workspace` has SIDE EFFECTS (T3 + T4 auto-creation) (LOW; batch-close)
- **Class:** REST-shape convention violation.
- **Evidence:** `WorkspaceManager.get_active_workspace` lines 1722-1727 delegate to auto-creation methods.
- **Severity:** LOW. Documented in S855/S858 comments. Convention: `get_*` should be idempotent; this method mutates DB.
- **Action:** BATCH-CLOSE observation. Renaming would break every downstream caller.

### F-WS-3 — No `resolution_tier` signal on retrieval return (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED diagnostic gap.
- **Evidence:** `WorkspaceManager.get_active_workspace` returns `ProjectWorkspace` without indicating which of the 4 tiers fired.
- **Severity:** LOW. Would require attaching metadata to the return (breaking change) OR wrapping in a container tuple.
- **Action:** BATCH-CLOSE observation.

### F-WS-5 — Two divergent `get_active_workspace` functions with different semantics (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED divergence.
- **Evidence:** `WorkspaceManager.get_active_workspace` vs `workspace_resolver.get_active_workspace(user)`.
- **Severity:** LOW. Callers may pick the wrong one.
- **Action:** BATCH-CLOSE — doc-only cross-reference.

### F-WS-6 — `execute_with_workspace` heuristic report-file creation (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED silent heuristics.
- **Evidence:** `core/agents/base_agent.py:5426-5504`. Hardcoded thresholds (500, 200 chars) + hardcoded formatting-marker list + class-name-based category assignment.
- **Severity:** LOW. Documented in S943 commentary; behavior is intentional. Category_map duplicated (F-WS-7).
- **Action:** BATCH-CLOSE observation.

### F-WS-BC-* — batch-close observations
- **F-WS-7:** `category_map` dict duplicated at lines 5440-5449 and 5482-5491.
- **F-WS-8:** No test for `write_to_workspace=False` silent-skip path.
- **F-WS-9:** No `_write_files_to_workspace` workspace-membership permission check (F-B-HIGH-3 territory from S2600).

---

## Rigby-safe assessment (post-patch)

- **R1 (no dangerous defaults):** CLEARED. F-WS-1 patched — log-only visibility on the intentional S1085 cross-user fallback preserves the behavior while enabling operator diagnosis.
- **R2 (no silent action substitution):** N/A.
- **R3 (no silent truncation):** N/A.
- **R4 (hidden filters surfaced):** PARTIAL — F-WS-2 (auto-creation side effect) and F-WS-3 (no resolution_tier signal) deferred to batch-close.
- **R5 (workspace/authority carriage):** CLEARED. F-WS-4 patched — env errors no longer masquerade as "no workspace"; logic errors propagate.
- **R6 (freshness surface):** CLEARED.
- **R7 (provenance surface):** PARTIAL — `execute_with_workspace` write metadata good; F-WS-3 deferred.
- **R8 (worker/env preconditions):** CLEARED.

---

## Verdict

Tool status: **DEFECT-PATCHED-VERIFIED** at HEAD post-Session 2728 patches.

**Code trace coverage:** three surfaces fully traced — `WorkspaceManager.get_active_workspace` + `_ensure_system_workspace` + `_ensure_personal_workspace` (workspace_manager.py:1570-1852); `workspace_resolver.get_active_workspace` + `get_active_workspace_id` (workspace_resolver.py:1-50); `BaseAgent.execute_with_workspace` (base_agent.py:5355-5552) including the file-extraction ladder (results.data.files → code → structured_report → message) + `_write_files_to_workspace` result-injection.

**Findings summary:**

- **Valid at HEAD → patched:** F-WS-4 (broad-except silent-degrade), F-WS-1 (superuser cross-user fallback silent).
- **Batch-close cleanup observations (deferred per Chris):** F-WS-2 (auto-creation side effects — documented but surprising), F-WS-3 (no resolution_tier signal — breaking change to fix), F-WS-5 (two divergent get_active_workspace functions — doc-only), F-WS-6/7 (execute_with_workspace heuristics + duplicated category_map), F-WS-8 (missing test coverage for write_to_workspace=False silent-skip), F-WS-9 (missing workspace-membership check in `_write_files_to_workspace` — F-B-HIGH-3 territory from S2600 PA arc).

**Coverage improvement:**

- Adds 11 targeted regression tests for two surfaces that previously lacked coverage:
  - F-WS-4 discipline (allowlist shape + logic-error propagation + env-error safety valve).
  - F-WS-1 log visibility (cross-user fallback + regression guard for same-user path).
- Extends the D17-D21 narrow-except cross-file allowlist invariant from 5-way (F-RG-1 tool 1 extension) to 6-way at Batch B tool 5.

**Regression sweep at HEAD:**

- 11 new regression tests in `test_workspace_retrieval_validation_2728.py`: **11/11 pass** (0.274s).
- Full Batch A + Batch B cross-tool sweep (10 validation-2728 files + adjacent canonical_authority tests, 122 substantive tests + 1 pre-existing skip): **122/122 pass** (16.8s). Zero cross-tool interference.

**Follow-ups filed:**

- Batch-close observations for cross-tool consistency (F-WS-2/3/5/6/7/8/9).
- Test-file mock refresh observation from Batch B tool 1 (`test_rag_integration_search_embeddings.py` stale post-D16 mocks) remains queued.

**Tool closure statement:** the workspace retrieval surface is VERIFIED at HEAD + 2 patches. Environmental errors in `workspace_resolver.get_active_workspace` no longer silently produce `None` results indistinguishable from "user has no workspace" — the D17-D21 narrow-except discipline is now applied uniformly across 6 retrieval-adjacent helpers. The intentional S1085 superuser cross-user fallback in `WorkspaceManager.get_active_workspace` remains behaviorally unchanged but now emits a WARNING log naming the fallback workspace's owner, closing the diagnostic gap that would have made cross-user attribution invisible in operator logs. Rigby's workspace-scoped tool dispatches inherit these fixes transparently.

---

## Batch B closure statement

**Batch B of the Rigby Tool Validation Engineering Campaign is CLOSED.** Five tools validated:

| Tool | Report | Patches | Coverage |
|---|---|---|---|
| B1 RAG retrieval path | `rag_retrieval_path_validation.md` | 1 (F-RG-1) | 9 new tests + D17-D21 invariant to 5-way |
| B2 `repo_tool` | `repo_tool_validation.md` | 3 (F-RT-2/5/11) | 15 new tests + first coverage at HEAD |
| B3 `kb_ingest` | `kb_ingest_validation.md` | 4 (F-KI-1/2/3/4/5(a)) | 16 new tests + first coverage at HEAD + 2 SECURITY fixes |
| B4 canonical_authority_helpers | `canonical_authority_helpers_validation.md` | 0 (verify-only) | 10 existing tests pass; ratified constitutional artifact |
| B5 workspace retrieval | `workspace_retrieval_validation.md` | 2 (F-WS-4/1) | 11 new tests + D17-D21 invariant to 6-way |

**Batch B totals:** 5 tools verified; **10 defects patched**; 51 new regression tests; 4 MEMORY rules touched (0 new, `feedback_llm_autofills_boolean_params_with_false` reinforced by F-SD-1-style guard extensions across Batch B, `feedback_procfile_makefile_queue_parity` implicitly verified at Batch B tool 3, `feedback_pa_local_verify_ownership` reinforced at tool 5). Zero regressions across the full 122-test cross-tool sweep. First-coverage-at-HEAD established for 2 substrate modules (repo_tool, kb_ingest).

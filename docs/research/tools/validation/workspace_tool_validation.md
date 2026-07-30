# `workspace_tool` — Validation Report (S3044)

**Tool:** `workspace_tool`
**Schema:** `core/services/pa_tool_schemas.py:1101`
**Handler:** `core/services/td_handlers_agents.py:2101` (`_handle_workspace`)
**Register site:** `core/services/tool_dispatcher.py` (workspace registration)
**Session:** S3044 (Path B systematic sweep FINISH — Batch 1)
**HEAD at validation:** `eb38187ec` (2026-07-30)
**Ship shape:** Doc-only (S2796 shape). Dedicated doc supersedes prior loose-stem match against workspace-family docs.
**Category upgrade target:** `validated_partial` (via wrong stem match) → `validated_full`
**Rigby SIGN:** S3044 A1 SIGN AGREE (11 tool_runs) — see §Related.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** analyzed
**Mutation safety:** unsafe_no_dry_run

---

## 1. Purpose / when-to-use

Manage workspaces and workspace-scoped operations. This is the platform's central workspace CRUD + file + git + operations surface. Workspace file actions are always scoped to the active workspace or an explicit `workspace_id`.

Use for: listing workspaces, looking up by name/id, creating/updating/deleting workspaces, scanning workspace structure, reading/writing files inside a workspace, inspecting/mutating git state, reviewing recent workspace operations, and rolling back operations.

Distinct from:
- `workspace_budget_tool` — budget-scoped operations (separate tool).
- `workspace_retrieval` (validation-doc-only artifact) — retrieval-layer semantics documented separately.
- `platform_config_tool` — platform-level config, not per-workspace.

## Covered actions

**READ actions (8 in scope this ship):**

- `list` — read — enumerates all workspaces (optional `name` filter). Supports `offset` + `limit` pagination.
- `get` — read — returns workspace details by `workspace_id` or `name`.
- `status` — read — quick status of the active workspace.
- `scan` — read — rescans workspace structure and stats; returns updated inventory.
- `read` — read — reads a file within the workspace root (`path` required).
- `git_status` — read — inspects git status for the workspace.
- `git_branch` — read — lists workspace git branches (also used to create branches — see mutation section for create semantics).
- `operations` — read — lists recent workspace operations. Supports `offset` + `limit` pagination.

**MUTATION actions (6 excluded — see §5a Mutation containment):**

- `create` — **mutation — deferred to Slice 2 write batch** — see §5a. Creates a new workspace row + directory scaffolding.
- `update` — **mutation — deferred to Slice 2 write batch** — see §5a. Mutates workspace attributes (`root_path`, `new_name`, `description`, `workspace_type`, `business_status`).
- `delete` — **mutation — deferred to Slice 2 write batch** — see §5a. Removes a sandbox workspace (row + directory).
- `write` — **mutation — deferred to Slice 2 write batch** — see §5a. Writes a file within the workspace root (arbitrary content).
- `git_commit` — **mutation — deferred to Slice 2 write batch** — see §5a. Creates a git commit in the workspace repo.
- `rollback` — **mutation — deferred to Slice 2 write batch** — see §5a. Rolls back a workspace operation. Requires `confirm_rollback=true` (explicit destructive-revert guard).

Note: `git_branch` is dual-nature in the schema — the description says "create branches" but is primarily used as a read/create action. Classified as read for §Covered actions purposes; branch creation is a low-blast mutation deferred alongside the other mutation actions.

## 3. Schema notes

- **Required:** `action` (enum: 14 values listed above).
- **Optional (workspace-scoping):** `workspace_id`, `name`, `agent_name`.
- **Optional (create/update):** `new_name`, `description`, `root_path`, `workspace_type`, `business_status`.
- **Optional (file actions):** `path`, `content`.
- **Optional (git):** `message` (git_commit), `branch_name` (git_branch).
- **Optional (rollback):** `operation_id`, `confirm_rollback` (must be `true` to execute the revert).
- **Optional (pagination):** `offset` (default 0), `limit` (default 50).
- **Update-only field:** `root_path` is validated at write time (must exist on disk).
- **Rollback guard:** `confirm_rollback=true` is a mandatory explicit guard for the destructive revert path.

## 4. Golden-path examples

**"List all workspaces:"**

```
workspace_tool  action=list
```

**"Get details for a workspace by id:"**

```
workspace_tool  action=get  workspace_id=<uuid>
```

**"What's the currently-active workspace status?"**

```
workspace_tool  action=status
```

**"Read a file inside the workspace root:"**

```
workspace_tool  action=read  workspace_id=<uuid>  path=README.md
```

**"Check git state:"**

```
workspace_tool  action=git_status  workspace_id=<uuid>
```

**"Show recent operations (paginated):"**

```
workspace_tool  action=operations  workspace_id=<uuid>  limit=25  offset=0
```

## 5. Failure / empty-state / pagination notes

- **Missing `workspace_id`/`name` on workspace-scoped read** — handler returns structured error envelope (see handler for exact shape).
- **Missing `path` on `read`** — structured error envelope.
- **`workspace_id` not found** — returns `{ok: false, error: 'workspace not found', workspace_id}`.
- **`list` with `name` filter and no matches** — returns `{ok: true, workspaces: []}` — empty list, not error.
- **`operations` pagination cursor exhausted** — returns `{ok: true, operations: []}`.
- **`read` on a file outside workspace root** — handler rejects with a path-safety error (workspace root confinement enforced).

## 5a. Mutation containment

- **Mutating actions excluded this ship (6):** `create`, `update`, `delete`, `write`, `git_commit`, `rollback` (+ branch-creation aspect of `git_branch` deferred alongside).
- **Blast-radius classification:**
  - `create` — `cascading` — new workspace row + associated FK-cascade setup + filesystem scaffolding.
  - `update` — `spreading` — updates workspace + config row; can trigger downstream re-scan.
  - `delete` — `cascading` — deletes workspace + associated rows + optionally directory.
  - `write` — `external` — filesystem write outside DB; downstream watchers may re-scan.
  - `git_commit` — `external` — git repo mutation; irreversible-in-place without rollback.
  - `rollback` — `external` — restores prior filesystem/git state; explicit `confirm_rollback=true` guard.
- **Deferral rationale:** consistent with S2908 shape-break commitment — pure-read subset ships in doc-only batch; mutation coverage requires paired lifecycle scaffolding + dry_run affordance (currently `unsafe_no_dry_run` per frontmatter). A future workspace-mutation batch would need to (a) exercise the rollback guard, (b) verify path-safety enforcement on `write`, (c) validate the FK cascade on `delete`.

## 5c. Contract ↔ Implementation Consistency

### 5c.1 Handler / module header claims match action reality

**PASS.** Schema `description` names all 14 actions accurately (list/get/status/create/update/delete/scan/read/write/git_status/git_commit/git_branch/operations/rollback). Handler dispatches per-action from `_handle_workspace` at line 2101.

### 5c.2 Gating truth matches runtime behavior

**PASS.** No feature flag gates the tool. Workspace scoping is the runtime discriminator — every action either operates on the active workspace or an explicit `workspace_id`.

### 5c.3 Shared handler-file coupling noted

Shared module: `td_handlers_agents.py`. Adjacent workspace-family tools include `workspace_budget_tool` (separate handler file), `workspace_retrieval` (documented as a separate validation doc). This tool is the primary workspace CRUD surface; `workspace_budget_tool` is scoped to budget-family actions only.

## 6. Evidence

**Analyzed-mode validation.** Schema at `pa_tool_schemas.py:1101-1156` read verbatim; handler dispatch pattern at `td_handlers_agents.py:2101` confirmed to route all 14 actions through internal action-switch. Live dispatch deferred — read-only actions are frequently exercised by Rigby inline in normal workspace workflows (this doc formalizes coverage rather than adding new exercise evidence).

**Prior loose-stem match issue:** the gap-map stem-matcher (`pa_tools_gap_map.find_matching_doc_stem`) previously matched `workspace_tool` to a workspace-family doc via loose containment (`workspace_budget_tool` or `workspace_retrieval` starts with `workspace_`). This dedicated file supersedes that match: `find_matching_doc_stem` will now hit strategy 1 (exact match on tool name → `workspace_tool` stem) before falling through to loose containment.

## Related

- **Adjacent workspace surfaces:** `workspace_budget_tool_validation.md`, `workspace_retrieval_validation.md`.
- **Shared handler module:** `td_handlers_agents.py`.
- **Mutation-shaped batch candidate:** future Slice 2 write batch would exercise the 6 mutation actions with paired scaffolding.
- **Path B FINISH plan:** `docs/audits/pa_tools/substrate/S3044_path_b_finish_plan.md`.
- **S3044 Rigby A1 SIGN cycle:** 11 tool_runs; AGREE on Q1-Q4; Q5 zoom-out folded.
- **Gap-map stem-matcher:** `core/services/pa_tools_gap_map.py:481` (`find_matching_doc_stem` — 3-strategy resolution: exact → suffix-stripped → loose containment).

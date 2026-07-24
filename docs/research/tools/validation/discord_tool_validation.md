# `discord_tool` — Validation Report (S2919)

**Tool:** `discord_tool`
**Schema:** `core/services/pa_tool_schemas.py:4486`
**Handler:** `core/services/td_handlers_gateway.py:723` (`_handle_discord`)
**Register site:** `core/services/tool_dispatcher.py:598`
**Session:** S2919 (Slice 4 batch 2 — gateway small-tier read-only quartet: discord + distribution + ats + narrative)
**HEAD at validation:** `12d3114b9` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2919 T0 SIGN AGREE — batch-1 pure-read template preserved; span 91 lines; 0/3 Appendix A/N first-hop literals in span 723-814; 0/4 mutation verbs (filesystem read + regex parse only).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`discord_tool` introspects the Discord bot module (`core/services/discord_bot.py`) as source text and returns structured summaries of its slot usage, registered slash commands / groups / subcommands, and cog classes. Use it when the operator asks "how many Discord commands are registered?" / "which cogs are loaded?" / "how many slot slots do we have left?" / "what's the bot's guild binding?".

Distinct from `cockpit_tool` (Celery ops introspection, not Discord surface), from `railway_tool` (infrastructure control, not source-file parse), and from actually running Discord commands (this tool is read-only introspection of the source, not a live gateway session).

## Covered actions

- `status` — **in scope this ship** — default action; returns `{action, file, file_lines, slots_used, slots_limit=100, slots_remaining, sync_mode='guild_only', guild_id, cog_count, top_level_commands, command_groups, subcommands}`. Slot usage parsed from `\d+\s*slots?\s*used` comment regex; nil-safe (returns `None` if no comment matches).
- `commands` — **in scope this ship** — returns `{action, top_level: [{name, description}], top_level_count, groups: [{group, description, subcommands: [str]}], groups_count, total_subcommands}`. Regex-derived from `@app_commands.command` and `app_commands.Group` declarations.
- `cogs` — **in scope this ship** — returns `{action, cogs: [str], count}`. Regex-derived from `class \w+(commands.Cog)` declarations.

Default action = `status` (per `payload.get('action', 'status')` at handler line 728).

## 3. Schema notes

- **Required:** `action` (enum: `status` / `commands` / `cogs`).
- **Optional:** none — this tool takes no other parameters.
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4483-4503`.
- **Envelope shape:** consistent `{action, ...}` prefix across all 3 actions. Each action has its own payload keys (slots data on `status`, command lists on `commands`, cog list on `cogs`) — no shared "results" key.

## 4. Golden-path examples

**Example 1 — quick bot health check (most operator-common):**
```json
{"action": "status"}
```
Expected envelope: `{"action": "status", "file": "core/services/discord_bot.py", "file_lines": <int>, "slots_used": <int|null>, "slots_limit": 100, "slots_remaining": <int|null>, "sync_mode": "guild_only", "guild_id": "<str|null>", "cog_count": <int>, "top_level_commands": <int>, "command_groups": <int>, "subcommands": <int>}`.

**Example 2 — full command inventory:**
```json
{"action": "commands"}
```
Expected envelope: `{"action": "commands", "top_level": [{"name": "/help", "description": "..."}, ...], "top_level_count": <int>, "groups": [{"group": "/bet", "description": "...", "subcommands": ["place", "list", ...]}, ...], "groups_count": <int>, "total_subcommands": <int>}`.

**Example 3 — cog census:**
```json
{"action": "cogs"}
```
Expected envelope: `{"action": "cogs", "cogs": ["BettingCog", "HealthCog", ...], "count": <int>}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown discord_tool action: <action>"}` at handler line 807. Not raised — in-envelope.
- **Handler exception:** any exception is caught at line 809, returns `{"error": "discord_tool error: <str>"}`. No `error_code` field — **legacy-error envelope** (9th corroborating instance post-S2918's 8-instance count; batch-2 first different-tool-block instance since previous instances clustered in analytics/audit/campaign/experiment quartet + studio/workflow_run duo + signal_studio quartet). Per 00-START forbidden-list, substrate arc still gated on explicit Chris directive.
- **Missing `discord_bot.py`:** returns `{"error": "discord_bot.py not found"}` at handler line 736. Uses `os.path.isfile` preflight check.
- **Empty regex matches:** all `re.findall` returns handle empty results as 0-length lists; nil-safe via `if slot_match else None` and `if guild_match else None`. `slots_remaining` is `None` if `slots_used` is `None` (short-circuit at line 764).
- **`slots_limit` hard-coded:** 100 — not derived from live Discord API, purely a manifest constant. Operator relying on this for capacity planning should know it's a repo-defined ceiling, not a dynamic ceiling.
- **No pagination:** all 3 actions return full result sets. No `limit` param; `commands` and `cogs` return the entire parsed inventory.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `os.path.isfile(bot_file)` | `read` | `td_handlers_gateway.py:735` | Filesystem stat; documented |
| `open(bot_file, 'r').read()` | `read` | `td_handlers_gateway.py:738-739` | Filesystem read; source file inside repo |
| `re.search(...)` / `re.findall(...)` | `read` | `td_handlers_gateway.py:743-756, 775-780, 804` | In-process regex on string; no I/O |

**Appendix N (Network-Preflight) — N/A.** No network first-hop. `open()` reads a repo-controlled file; `bot_file` path is derived from `os.path.abspath(__file__)` (line 730) — not user-controllable, no SSRF surface.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop. Handler is entirely synchronous.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with `apply_async` / `httpx|requests|urllib.request` / `openai|anthropic|litellm` literals). S2919 T0 SIGN Q2 per-tool confirmation: discord span 723-814 contains none of these literals — grep receipts in Rigby T0 SIGN turn 3.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2919 handoff. Expected shapes documented in §4 golden-path examples.

## Related

- **Adjacent tools:** `cockpit_tool` (Celery infra, not Discord); `railway_tool` (deploy control); `mobile_tool` (React Native introspection — same shape as discord_tool: file-read + parse) — same batch this ship.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); source file at `core/services/discord_bot.py`.
- **Prior ratifications:** S2892 Path B open, S2918 Slice 4 batch 1 (analytics/audit/campaign/experiment quartet — same gateway ORM-direct shape).
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 9th instance** — first different-tool-block instance since analytics/audit/campaign/experiment quartet (batch 1) + studio/workflow_run duo (S2917) + signal_studio (S2916). Meets Rigby Q4 recommendation criteria for post-D6 substrate arc evaluation, still gated on explicit Chris directive per 00-START forbidden-list.
  - Filesystem-read handler shape (open+regex) new to Slice 4 sweep — mobile_tool is the second such candidate (same file-read pattern; documented separately when scanned).

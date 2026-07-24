# `mobile_tool` — Validation Report (S2920)

**Tool:** `mobile_tool`
**Schema:** `core/services/pa_tool_schemas.py:4508`
**Handler:** `core/services/td_handlers_gateway.py:814` (`_handle_mobile`)
**Register site:** `core/services/tool_dispatcher.py:599`
**Session:** S2920 (Slice 4 batch 3 — gateway medium-tier read-only trio: mobile + calendar + conceptforge; template-preservation swap dropped proactive + self_awareness + profile because verb-scan flagged mutations)
**HEAD at validation:** `9561a1932` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2920 T0 SIGN AGREE-with-edits — span 126 lines (00-START claimed 127); 0/4 mutation verbs; 0/3 Appendix A/N first-hop literals in span 814-939; second filesystem-read gateway tool after `discord_tool`.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`mobile_tool` introspects the React Native / Expo mobile app that sits alongside the Django backend (`mobile/` directory at project root). It reads static config (`package.json` / `app.config.ts` / `eas.json`), screen implementations under `src/screens/`, API client modules under `src/api/`, and returns structured summaries. Use it when the operator asks "what's the mobile app status?" / "which screens exist and which are placeholders?" / "what API modules ship with the mobile app?" / "which Expo / RN version are we on?".

Distinct from `discord_tool` (same file-read + parse shape but targets `discord_bot.py`), from `railway_tool` (infrastructure control, not source-file parse), and from `podcast_tool` (production content surface).

## Covered actions

- `project_status` — **in scope this ship** — default action; reads `package.json` + `app.config.ts|js|json` + `eas.json`. Returns `{action, path='mobile/', name, version, expo_version, react_native_version, navigation, total_dependencies, config_file, eas_profiles}`. Nil-safe: missing files return partial-envelope (e.g., no `eas_profiles` key if `eas.json` absent).
- `screens` — **in scope this ship** — lists `.tsx`/`.ts` files under `mobile/src/screens/`. Each screen carries `{file, name, size_bytes, status: 'placeholder'|'implemented'}` (heuristic: first 500 bytes contain "Placeholder" or "coming soon" → placeholder). Also parses `mobile/src/navigation/screenRegistry.ts` for route ↔ component bindings.
- `api_modules` — **in scope this ship** — lists `.ts`/`.tsx` files under `mobile/src/api/`. Returns `{action, modules: [{file, size_bytes}], count}`.
- `dependencies` — **in scope this ship** — reads `package.json`, returns totals + a fixed key-package roster (`expo`, `react-native`, `react`, `@react-navigation/native`, `@react-navigation/drawer`, `expo-router`, `zustand`, `axios`, `@sentry/react-native`, `expo-notifications`, `expo-secure-store`, `@react-native-async-storage/async-storage`).

Default action = `project_status` (per `payload.get('action', 'project_status')` at handler line 819).

## 3. Schema notes

- **Required:** `action` (enum: `project_status` / `screens` / `api_modules` / `dependencies`).
- **Optional:** none — this tool takes no other parameters.
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4506-4526`.
- **Envelope shape:** consistent `{action, ...}` prefix across all 4 actions. `screens` returns a `count` (+ `implemented` / `placeholders` split); `api_modules` returns a `count`; `project_status` and `dependencies` return flat field rollups (no `count`). Same envelope-key asymmetry-across-actions pattern already at 3/3 triggered post-S2919 batch 2.

## 4. Golden-path examples

**Example 1 — quick mobile app health check (most operator-common):**
```json
{"action": "project_status"}
```
Expected envelope: `{"action": "project_status", "path": "mobile/", "name": "<str>", "version": "<str>", "expo_version": "<str>", "react_native_version": "<str>", "navigation": "react-navigation|expo-router|unknown", "total_dependencies": <int>, "config_file": "app.config.ts|app.config.js|app.json", "eas_profiles": [<str>, ...]}`.

**Example 2 — screen census (implemented vs placeholder):**
```json
{"action": "screens"}
```
Expected envelope: `{"action": "screens", "screens": [{"file": "HomeScreen.tsx", "name": "HomeScreen", "size_bytes": <int>, "status": "implemented|placeholder"}, ...], "count": <int>, "implemented": <int>, "placeholders": <int>, "routes": [{"route": "/home", "component": "HomeScreen"}, ...]}`.

**Example 3 — key-package dependency snapshot:**
```json
{"action": "dependencies"}
```
Expected envelope: `{"action": "dependencies", "total_deps": <int>, "total_dev_deps": <int>, "key_packages": {"expo": "<version|not installed>", "react-native": "<version|not installed>", ...}}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown mobile_tool action: <action>"}` at handler line 936. Not raised — in-envelope.
- **Handler exception:** any exception is caught at line 938, returns `{"error": "mobile_tool error: <str>"}`. No `error_code` field — **legacy-error envelope** (13th corroborating instance post-S2919 batch 2's 12-instance count). Substrate arc still gated on explicit Chris directive per 00-START forbidden-list.
- **Missing `mobile/` directory:** returns `{"error": "No mobile/ directory found in project root"}` at handler line 825 (before try/except body).
- **Missing `mobile/src/screens/` or `mobile/src/api/`:** returns `{"error": "No src/screens/ directory found"}` (line 862) or `{"error": "No src/api/ directory found"}` (line 902) — per-action distinct messages.
- **Missing `package.json` on `dependencies`:** returns `{"error": "No package.json found"}` (line 916). Distinct from `project_status`, which silently omits `name`/`version` fields if `package.json` absent (does NOT error).
- **Placeholder heuristic is 500-byte-window:** if a screen file has real code in the first 500 bytes but also a `Placeholder` comment somewhere later, it may register as `implemented`; conversely, a real-content screen file whose first 500 bytes accidentally contain the literal string `Placeholder` (e.g., in a TypeScript type name) will be mis-flagged. Documented sharp edge.
- **`screenRegistry.ts` regex:** `r"'(/[^']*)'.*?:\s*(\w+)"` — assumes single-quoted route strings + `route: Component` binding. Files using double-quoted routes or object-literal alternates will not populate `routes`.
- **No pagination:** all 4 actions return full result sets. No `limit` param.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `os.path.isdir(mobile_root)` / `os.path.isfile(...)` | `read` | `td_handlers_gateway.py:824, 832, 846, 852, 861, 883, 901, 915` | Filesystem stat; documented |
| `open(<file>, 'r')` + `json_mod.load(...)` | `read` | `td_handlers_gateway.py:833-834, 853-854, 870-871, 883-886, 917-918` | Filesystem read of repo-controlled paths |
| `os.listdir(<dir>)` | `read` | `td_handlers_gateway.py:865, 905` | Filesystem enumerate; documented |
| `re.findall(...)` on `screenRegistry.ts` content | `read` | `td_handlers_gateway.py:887` | In-process regex on string; no I/O |

**Appendix N (Network-Preflight) — N/A.** No network first-hop. `open()` reads repo-controlled paths derived from `os.path.abspath(__file__)` (line 820); not user-controllable, no SSRF surface.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop. Handler is entirely synchronous.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with `apply_async` / `httpx|requests|urllib.request` / `openai|anthropic|litellm` literals). S2920 T0 SIGN Q2 per-tool confirmation: mobile span 814-939 contains none of these literals — grep receipts in Rigby T0 SIGN turn 1.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2920 handoff. Expected shapes documented in §4 golden-path examples.

## Related

- **Adjacent tools:** `discord_tool` (batch 2 — same file-read + regex parse shape targeting `discord_bot.py`); `podcast_tool` (production surface, upstream of mobile-app content); `railway_tool` (infrastructure).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); mobile app source under `mobile/` at project root.
- **Prior ratifications:** S2892 Path B open, S2918 Slice 4 batch 1, S2919 Slice 4 batch 2 (discord/distribution/ats/narrative — same gateway-tier shape).
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 13th instance** — continued corroboration; still gated on explicit Chris directive per 00-START forbidden-list.
  - **Filesystem-read handler shape (open + regex)** — 2nd instance of this pattern in Slice 4 (after `discord_tool`). Two-tool corroboration; not a Fold yet.

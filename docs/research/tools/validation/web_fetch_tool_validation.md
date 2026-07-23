# `web_fetch_tool` — Validation Report (S2910)

**Tool:** `web_fetch_tool`
**Schema:** `core/services/pa_tool_schemas.py:327`
**Handler:** `core/services/td_handlers_agents.py:426` (`_handle_web_fetch`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2910 (Path B systematic sweep — Slice 2 batch 5 of `td_handlers_agents`)
**HEAD at validation:** `e642c7aa8` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (actionless — no schema `action` enum to iterate; single-verb GET/POST surface).
**Rigby SIGN:** S2910 T0 SIGN AGREE-with-edits (batch 5 composition); S2910 T1 SIGN pending — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Raw HTTP GET/POST verification tool (Rigby Tool Gap Ledger #15, shipped S2865). Answers "what does this specific URL actually return?" — health-check a local `/api/...` endpoint, inspect a JSON response, confirm a service is reachable, or verify a bridge / worker liveness path. Handler-side clamps: scheme allowlist (`http://`, `https://`), method allowlist (`GET`, `POST`), timeout capped at 60s (default 15), body capped at 2 MB (default 500 KB), max 5 redirects.

Distinct from `web_search` (Serper-backed keyword search over the public internet) and from `orm_inspect_tool` (read-only Django ORM row inspection — the S2845 false-negative-gap-closer counterpart). `web_fetch_tool` is the *external HTTP verify* surface; `orm_inspect_tool` is the *internal DB verify* surface. Not a browser: no JavaScript execution, no cookies, no bot-protection bypass.

## Covered actions

**This tool is actionless by schema design** — `schema_action_count=0` per T1a harness artifact (`docs/audits/pa_tools/harness_output/web_fetch_tool.json`), no `action` enum declared at `pa_tool_schemas.py:338-393`. The dispatch surface is a single implicit `fetch` call parameterized by `url` (+ optional method / headers / params / body / timeout / max_bytes / allow_private_networks).

Therefore `## Covered actions` is intentionally empty. S2910 batch 5 validates actionless-shape via `TOOL_DEFAULTS` seed (`READ_ONLY` — HTTP fetch is read-only in the platform-mutation sense; there is no ORM write). Same precedent as `web_search` (S2906 batch 2).

## 3. Schema notes

- **Required:** `url` (string; `http://` or `https://` only — handler-enforced at line 463).
- **Optional (declared):**
  - `method` (enum: `GET|POST`, default `GET` — handler-clamped at line 470-476).
  - `headers` (object; `{name: value}`; auth values not logged).
  - `params` (object; querystring merged into URL).
  - `json_body` (object; POST only, ignored for GET at line 498).
  - `timeout_seconds` (number; clamped to `[1, 60]` at handler line 483; default 15).
  - `max_bytes` (integer; clamped to `[1024, 2_000_000]` at handler line 490; default 500000).
  - `allow_private_networks` (boolean; default `true` for current single-tenant pre-prod — see project single-user pre-prod operating context).
- **Content-type handling:** the handler classifies responses as `text-like` when content-type prefix matches `text/`, `application/json`, `application/javascript`, or `application/xml` (constant `_TEXT_LIKE_PREFIXES` at handler line 451). Text-like bodies decode UTF-8 with `errors='replace'`; JSON is parsed only if content-type says JSON AND body was NOT truncated (line 566).

## 4. Golden-path examples

**"What does the local health endpoint return?"**

```
web_fetch_tool  url="http://localhost:8000/api/health"
```

**"Fetch a JSON API with a custom header:"**

```
web_fetch_tool  url="https://api.example.com/v1/status"  headers={"Authorization": "Bearer …"}
```

**"POST to an internal endpoint with a small body:"**

```
web_fetch_tool  url="http://localhost:8000/api/debug/echo"  method=POST  json_body={"ping": true}
```

**"Fetch a large-ish page, capped at 1 MB:"**

```
web_fetch_tool  url="https://example.org/report.html"  max_bytes=1000000
```

## 5. Failure / empty-state / pagination notes

- **Missing `url`** — returns `{ok: false, error: 'url is required'}` at handler line 460. Inline envelope (not a raised exception).
- **Bad scheme** — returns `{ok: false, error: "disallowed scheme 'file' (only http/https allowed)", url}` at line 464.
- **Bad method** — returns `{ok: false, error: "unsupported method 'PUT' (only GET/POST allowed)", url}` at line 472.
- **Timeout** — returns `{ok: false, error: 'timeout after 15.0s: <exc>', url, latency_ms}` at line 536.
- **HTTP-transport error** — returns `{ok: false, error: 'http error (ConnectError): ...', url, latency_ms}` at line 543.
- **HTTP 4xx/5xx from server** — `ok: true`, `status_code=<4xx|5xx>`. Transport-level success + application-layer error is NOT collapsed into `ok: false` — the caller inspects `status_code`.
- **Body larger than `max_bytes`** — returned with `truncated: true`, `body_bytes` reflects the *total* not the truncated slice, `body_text` contains only the truncated slice, and JSON parse is skipped when truncated (line 566).
- **Non-text content-type** — `body_text: ''` + `body_text_note: 'omitted_non_text_content_type'`. Prevents leaking non-text binary blobs (images, PDFs) as garbage-decoded strings.
- **No content-type header** — `body_text: ''` + `body_text_note: 'omitted_unknown_content_type'`.
- **Redirects** — `follow_redirects=True`, `max_redirects=5`. `final_url` in the response captures the terminal URL after any redirect chain.
- **No pagination** — single request/response. Callers that need paginated fetches manage cursors themselves.

**Inline envelope pattern:** unlike `brainstorm_tool` (this batch), `web_fetch_tool` returns validation failures as `{ok: false, error, ...}` envelopes at HTTP 200 rather than raising exceptions. Under the S2909 T1 harness classifier this pattern would classify as `soft_error` — but the tool is actionless so the harness emits 0 rows, and this shape only affects real-caller behavior. Consumers should check `ok` first.

## 5a. Mutation containment

- **Mutating actions:** none. Read-only external HTTP fetch — no ORM writes, no persisted platform state.
- **Safety metadata:** seeded in `TOOL_DEFAULTS` at S2910 with `default_safety_class='READ_ONLY'`, `applicability='always'`. Notes: `env: external:network deps: httpx GET/POST; scheme/method allowlist; caps timeout+max_bytes; no ORM write; actionless schema`.
- **Multi-tenant note:** `allow_private_networks` default `true` is safe for current single-tenant pre-prod context. Rigby Tool Gap Ledger S2865 zoom-out flagged: if platform ever goes multi-tenant, flip the default to `false` + add cloud-metadata blocklist to close the SSRF vector. Not in scope for this validation ship.

## 6. Evidence

### 6.1 T1a harness artifact — this ship

`docs/audits/pa_tools/harness_output/web_fetch_tool.json` at HEAD `e642c7aa8` (harness run 2026-07-23):

```json
{
  "actions": [],
  "harness_version": "v2",
  "schema_action_count": 0,
  "tool_name": "web_fetch_tool"
}
```

Expected shape for actionless tools — zero rows. `## Covered actions` authoring in this doc depends on schema + handler-trace evidence, not harness rows (same discipline as `web_search_validation.md` at S2906).

### 6.2 Handler-trace evidence — this ship

Handler at `td_handlers_agents.py:426-597`:

- Line 458: `url = (payload.get('url') or '').strip()` — required-per-schema; empty check at 459.
- Line 462: `urlparse(url); parsed.scheme not in ('http', 'https')` — scheme allowlist.
- Line 470: `method = (payload.get('method') or 'GET').upper(); method not in ('GET', 'POST')` — method allowlist.
- Line 479-483: timeout clamp to `[1.0, 60.0]`.
- Line 486-490: max_bytes clamp to `[1024, 2_000_000]`.
- Line 503-513: log with header NAMES (never values) — auth header names visible in logs, values hidden.
- Line 517-535: `httpx.Client(timeout=Timeout(connect=min(5, t), read=t, write=min(5, t), pool=min(5, t)), follow_redirects=True, max_redirects=5)`.
- Line 552: `raw_bytes = resp.content or b''; body_bytes_total = len(raw_bytes)`.
- Line 554-555: `truncated = body_bytes_total > max_bytes; body_slice = raw_bytes[:max_bytes] if truncated else raw_bytes`.
- Line 557-558: content-type + `is_text_like` classification via `_TEXT_LIKE_PREFIXES` prefix match.
- Line 560-574: decode + optional JSON parse (only if content-type JSON + not truncated).

### 6.3 Runtime-not-executed — this ship

- **Actual GET against localhost / external URL** — not exercised in the harness (actionless; requires payload). Documented shape via handler trace; consumers exercise routinely via PA dispatch (well-worn since S2865).
- **`allow_private_networks=false` path** — not exercised (private-network blocking is not yet wired in the handler; the flag is captured but the `httpx` client does not gate on it).
- **`max_bytes` truncation edge case** — not exercised at cap boundary.
- **Redirect chain** — not exercised; `max_redirects=5` cap not stress-tested.
- **Timeout path** — not exercised.

---

## Related

- **Ledger candidates surfaced this ship:** none new. `allow_private_networks` gating is a known deferred item from Rigby S2865 zoom-out (not this ship's scope).
- **Adjacent tools:**
  - `web_search` — Serper keyword search; the "what's happening about X?" surface. Also actionless. See S2906 validation doc.
  - `orm_inspect_tool` — read-only Django ORM row inspection; the internal-DB counterpart to `web_fetch_tool`'s external-HTTP verify. See S2907 validation doc + S2909 close FT-5 candidate substrate finding.
  - `intelligence_tool` — multi-source routing (web/spider/agent); does NOT back-route through this handler.
- **Substrate context:** part of S2910 batch 5. Uniform-safety actionless tool sits alongside `schedule_followup` (WRITE_GATED actionless) + `legal_doc_drafter_agent` (MUTATION actionless) + `brainstorm_tool` (mixed 6+1 per-action). Rigby T0 SIGN Q4 named `web_fetch_tool` "raw HTTP; different from typical read-only list/stats" — flagged as heterogeneous risk surface bundled in one batch. `web_fetch_tool` is the safest of the 4 (no platform-state mutation) but its external-network dependency puts it in a different substrate class than pure ORM readers.
- **Prior work:** shipped S2865 (Rigby Tool Gap Ledger #15). No prior validation doc. First entry into the validated corpus this session.
- **Metadata seed:** `TOOL_DEFAULTS` entry at `core/services/tool_action_metadata.py` this ship (Pattern A — uniform safety class + actionless).

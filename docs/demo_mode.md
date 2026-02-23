# Demo Mode

Prevents accidental exposure of real footage, sensitive data, or unfinished features during demos.

## Resolve Node Demo Mode

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `RESOLVE_DEMO_MODE` | `false` | When `true`, restricts renders to `demo_assets/` only |
| `RESOLVE_DEMO_ALLOWED_URL_PREFIXES` | (empty) | Comma-separated URL prefixes allowed in demo mode |

### Enforcement

When `RESOLVE_DEMO_MODE=true`:

1. **Local paths**: Every `clip_paths` entry must resolve inside `resolve_node/demo_assets/`. Path traversal (`../`) is resolved before the check.
2. **Remote URLs**: Blocked unless the URL starts with one of the `RESOLVE_DEMO_ALLOWED_URL_PREFIXES` values.
3. **Violation response**: HTTP 403 with error codes `DEMO_001` (URL blocked) or `DEMO_002` (path outside demo_assets).
4. **Health endpoint**: `/health` includes `"demo_mode": true|false` so UIs can show a badge.

### Setup

```bash
# Generate demo clip
bash resolve_node/demo_assets/setup_demo_env.sh

# Enable demo mode
export RESOLVE_DEMO_MODE=true

# Verify guardrails
python resolve_node/demo_assets/verify_demo_mode.py
```

### Files

| File | Purpose |
|------|---------|
| `resolve_node/demo_assets/generate_demo_clip.sh` | Generates SMPTE color bar test clip with args |
| `resolve_node/demo_assets/setup_demo_env.sh` | One-command setup: checks ffmpeg, generates clip, prints payload |
| `resolve_node/demo_assets/verify_demo_mode.py` | Prints whether guardrails are active |
| `resolve_node/demo_assets/demo_test_clip.mp4` | Generated demo clip (not committed — regenerate locally) |
| `resolve_node/config.py` | `DEMO_MODE`, `DEMO_ASSETS_DIR`, `DEMO_ALLOWED_URL_PREFIXES` |
| `resolve_node/app.py` | `_enforce_demo_mode()` called before every render start |

---

## Governance Demo Mode (Design)

For showing the governance page in demos without exposing real system data.

### Approach: Query Parameter Toggle

Add `?demo=true` to the governance tab URL. When active:

1. **API layer** (`views_platform_command.py`): `governance_view()` checks for `?demo=true` and returns synthetic data instead of real DB queries.
2. **Synthetic data includes**:
   - 3 pending decisions (one critical, one high, one medium) with realistic but fake titles
   - Self-healing progress at 73% with 5 agents showing varied states
   - Emergency controls in nominal state
   - Fake owner name ("Demo Operator")
3. **Frontend**: Badge in the top-right shows "DEMO MODE" when synthetic data is detected (response includes `"demo_mode": true`).
4. **No real data flows**: No DB queries, no Celery dispatch, no mutations.

### Implementation Tickets

**Backend: `views_platform_command.py`**
- Add `_get_demo_governance_data()` helper returning static JSON
- In `governance_view()`: if `request.GET.get('demo') == 'true'`, return demo data
- In `self_healing_progress_view()`: same check, return demo progress
- Disable mutation endpoints (emergency halt, remediation, audit) when demo=true

**Frontend: `GovernanceTab.tsx`**
- Read `demo` query param from URL
- Pass to API calls as query param
- Render "DEMO MODE" badge when `governanceData?.demo_mode === true`
- Disable mutation buttons (gray out + tooltip "Disabled in demo mode")

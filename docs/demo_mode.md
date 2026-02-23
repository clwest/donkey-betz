# Demo Mode

Prevents accidental exposure of real footage, sensitive data, or unfinished features during demos.

## Quick Start

```bash
# One command — checks ffmpeg, generates demo clip, prints render payload:
bash resolve_node/demo_assets/setup_demo_env.sh
```

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

## Demo Clip Generation

### Default (4s, 1280x720, with audio)

```bash
bash resolve_node/demo_assets/generate_demo_clip.sh
```

### All Options

```bash
bash resolve_node/demo_assets/generate_demo_clip.sh \
  --size 1920x1080 \
  --duration 5 \
  --text "CLIENT DEMO" \
  --no-audio \
  --output /tmp/custom_clip.mp4
```

| Flag | Default | Description |
|------|---------|-------------|
| `--output`, `-o` | `demo_test_clip.mp4` in demo_assets/ | Output file path |
| `--duration`, `-d` | `4` | Clip length in seconds |
| `--size`, `-s` | `1280x720` | Video dimensions (WxH) |
| `--text`, `-t` | `DONKEY BETZ DEMO` | Title overlay text |
| `--no-audio` | (audio on) | Omit 440 Hz test tone |

### Verify

```bash
ffprobe -hide_banner resolve_node/demo_assets/demo_test_clip.mp4
```

Expected: H.264 video, AAC audio (if enabled), ~100-150KB.

---

## Example Render Request

### curl

```bash
curl -X POST http://localhost:5001/render/start \
  -H 'Content-Type: application/json' \
  -H 'X-Render-Token: dev-token-change-in-production' \
  -d '{
    "clip_paths": ["/absolute/path/to/resolve_node/demo_assets/demo_test_clip.mp4"],
    "template": "default_mp4",
    "timeline_name": "demo_timeline"
  }'
```

### PA Chat

> "Use the davinci tool to render the demo clip at /path/to/demo_test_clip.mp4"

### PA Tool Call (direct)

```
davinci_tool(action="render", clip_paths=["<absolute_path>"], template="default_mp4", timeline_name="demo_timeline")
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ffmpeg not found` | `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux) |
| Font rendering missing | ffmpeg needs fontconfig. On Alpine: `apk add fontconfig ttf-dejavu` |
| Colon escaping in drawtext | ffmpeg's `drawtext` filter uses `:` as option separator. Colons in text values must be escaped as `\:`. The script handles this automatically. |
| Clip won't render in Resolve | Ensure the path is absolute and the file exists. The script prints the absolute path. |
| Demo mode blocks my render | Either move clips into `demo_assets/` or set `RESOLVE_DEMO_MODE=false` |

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

# Resolve Node Demo Assets

Zero-risk demo assets for DaVinci render testing. These clips contain only SMPTE color bars with text overlays — never real footage.

## Quick Start

```bash
# One command — checks ffmpeg, generates clip, prints render payload:
bash resolve_node/demo_assets/setup_demo_env.sh
```

## Generate Demo Clip

```bash
# Default: 4s 1280x720 with audio
bash resolve_node/demo_assets/generate_demo_clip.sh

# Full HD, no audio, custom title
bash resolve_node/demo_assets/generate_demo_clip.sh \
  --size 1920x1080 --no-audio --text "CLIENT DEMO"

# All options:
#   --output, -o    Output path (default: demo_test_clip.mp4)
#   --duration, -d  Seconds (default: 4)
#   --size, -s      WxH (default: 1280x720)
#   --text, -t      Title text (default: DONKEY BETZ DEMO)
#   --no-audio      Omit 440 Hz test tone
```

## Verify

```bash
ffprobe -hide_banner resolve_node/demo_assets/demo_test_clip.mp4
```

Expected: H.264 video, AAC audio (if enabled), ~100-150KB.

## Demo Mode Guardrails

Set `RESOLVE_DEMO_MODE=true` to prevent renders from using real footage:

```bash
export RESOLVE_DEMO_MODE=true
python resolve_node/demo_assets/verify_demo_mode.py
```

When active:
- Only clip paths inside `resolve_node/demo_assets/` are allowed
- Remote URLs are blocked unless in `RESOLVE_DEMO_ALLOWED_URL_PREFIXES`
- Violations return HTTP 403 with a clear error message

## Example Render Request

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

Via PA chat:
> "Use the davinci tool to render the demo clip at /path/to/demo_test_clip.mp4"

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ffmpeg not found` | `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux) |
| Font rendering missing | ffmpeg needs fontconfig. On Alpine: `apk add fontconfig ttf-dejavu` |
| Colon escaping in drawtext | ffmpeg's `drawtext` filter uses `:` as option separator. Colons in text values must be escaped as `\:`. The script handles this automatically. |
| Clip won't render in Resolve | Ensure the path is absolute and the file exists. The script prints the absolute path. |
| Demo mode blocks my render | Either move clips into `demo_assets/` or set `RESOLVE_DEMO_MODE=false` |

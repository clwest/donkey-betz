#!/usr/bin/env bash
# setup_demo_env.sh — One-command demo environment preparation.
#
# Ensures ffmpeg exists, generates the demo clip if missing, and prints
# a ready-to-copy JSON payload for the DaVinci render API.
#
# Usage:
#   bash resolve_node/demo_assets/setup_demo_env.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEMO_CLIP="$SCRIPT_DIR/demo_test_clip.mp4"

echo "=== Resolve Node Demo Environment Setup ==="
echo ""

# 1. Check ffmpeg
if command -v ffmpeg &>/dev/null; then
  echo "[OK] ffmpeg found: $(which ffmpeg)"
else
  echo "[FAIL] ffmpeg not found."
  echo "  macOS:  brew install ffmpeg"
  echo "  Ubuntu: sudo apt install ffmpeg"
  echo "  Alpine: apk add ffmpeg"
  exit 1
fi

# 2. Generate demo clip if missing
if [[ -f "$DEMO_CLIP" ]]; then
  echo "[OK] Demo clip exists: $DEMO_CLIP ($(du -h "$DEMO_CLIP" | cut -f1))"
else
  echo "[...] Generating demo clip..."
  bash "$SCRIPT_DIR/generate_demo_clip.sh"
fi

# 3. Verify
if ! ffprobe -hide_banner "$DEMO_CLIP" &>/dev/null 2>&1; then
  echo "[FAIL] Demo clip failed verification"
  exit 1
fi
echo "[OK] Demo clip verified"

# 4. Print absolute path
ABS_PATH="$(cd "$(dirname "$DEMO_CLIP")" && pwd)/$(basename "$DEMO_CLIP")"
echo ""
echo "Absolute path (for render calls):"
echo "  $ABS_PATH"

# 5. Print ready-to-copy render payload
TOKEN="${RENDER_NODE_TOKEN:-dev-token-change-in-production}"
BASE_URL="${RESOLVE_NODE_URL:-http://localhost:5001}"

echo ""
echo "=== Ready-to-copy render request ==="
echo ""
echo "curl -X POST ${BASE_URL}/render/start \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'X-Render-Token: ${TOKEN}' \\"
echo "  -d '$(cat <<ENDJSON
{"clip_paths": ["${ABS_PATH}"], "template": "default_mp4", "timeline_name": "demo_timeline"}
ENDJSON
)'"

echo ""
echo "=== PA chat equivalent ==="
echo ""
cat <<EOF
Tell the PA:
  "Use the davinci tool to render the demo clip at ${ABS_PATH} with template default_mp4"

Or directly:
  davinci_tool(action="render", clip_paths=["${ABS_PATH}"], template="default_mp4", timeline_name="demo_timeline")
EOF

echo ""
echo "=== Demo mode check ==="
python3 "$SCRIPT_DIR/verify_demo_mode.py" || true
echo ""
echo "Setup complete."

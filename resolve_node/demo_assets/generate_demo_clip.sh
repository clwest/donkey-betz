#!/usr/bin/env bash
# generate_demo_clip.sh — Create a permanent, zero-risk demo video for DaVinci render testing.
#
# Produces a short clip with SMPTE color bars, optional tone, and burned-in text overlay.
# Safe for public demos — never exposes real footage.
#
# Usage:
#   bash generate_demo_clip.sh                          # defaults
#   bash generate_demo_clip.sh --size 1920x1080         # full HD
#   bash generate_demo_clip.sh --no-audio --duration 2  # silent 2s clip
#   bash generate_demo_clip.sh --text "MY PROJECT"      # custom title
#   bash generate_demo_clip.sh --output /tmp/test.mp4   # custom output path
#
# Requirements: ffmpeg (any recent version)
set -euo pipefail

# --- Defaults ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT=""
DURATION=4
SIZE="1280x720"
TEXT="DONKEY BETZ DEMO"
AUDIO=true

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output|-o)    OUTPUT="$2"; shift 2 ;;
    --duration|-d)  DURATION="$2"; shift 2 ;;
    --size|-s)      SIZE="$2"; shift 2 ;;
    --text|-t)      TEXT="$2"; shift 2 ;;
    --no-audio)     AUDIO=false; shift ;;
    --help|-h)
      echo "Usage: $0 [--output PATH] [--duration SEC] [--size WxH] [--text TITLE] [--no-audio]"
      echo ""
      echo "Options:"
      echo "  --output, -o    Output file path (default: demo_test_clip.mp4 in this dir)"
      echo "  --duration, -d  Clip duration in seconds (default: 4)"
      echo "  --size, -s      Video dimensions as WxH (default: 1280x720)"
      echo "  --text, -t      Title overlay text (default: DONKEY BETZ DEMO)"
      echo "  --no-audio      Omit the 440 Hz test tone"
      exit 0
      ;;
    *) echo "Unknown option: $1 (try --help)"; exit 1 ;;
  esac
done

# Default output path
if [[ -z "$OUTPUT" ]]; then
  OUTPUT="$SCRIPT_DIR/demo_test_clip.mp4"
fi

# Validate ffmpeg
if ! command -v ffmpeg &>/dev/null; then
  echo "ERROR: ffmpeg not found."
  echo "Install: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
  exit 1
fi

# ffmpeg drawtext uses : as option separator — escape colons in values
TIMESTAMP="$(date -u '+%Y-%m-%dT%H\:%M\:%SZ')"
# Also escape colons in user-provided text
SAFE_TEXT="${TEXT//:/\\:}"

echo "Generating demo clip:"
echo "  Output:   $OUTPUT"
echo "  Size:     $SIZE"
echo "  Duration: ${DURATION}s"
echo "  Title:    $TEXT"
echo "  Audio:    $AUDIO"

# Build input sources
INPUTS=(
  -f lavfi -i "smptebars=size=${SIZE}:rate=30:duration=${DURATION}"
)
if [[ "$AUDIO" == "true" ]]; then
  INPUTS+=(-f lavfi -i "sine=frequency=440:sample_rate=48000:duration=${DURATION}")
fi

# Build filter
FILTER="[0:v]drawtext=text='${SAFE_TEXT}':fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h/4"
FILTER+=",drawtext=text='TEST ASSET - NOT REAL FOOTAGE':fontsize=28:fontcolor=yellow:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h/2"
FILTER+=",drawtext=text='Generated ${TIMESTAMP}':fontsize=20:fontcolor=white:borderw=1:bordercolor=black:x=(w-text_w)/2:y=3*h/4[out]"

# Build mapping
MAPS=(-map "[out]")
AUDIO_CODEC=()
if [[ "$AUDIO" == "true" ]]; then
  MAPS+=(-map 1:a)
  AUDIO_CODEC=(-c:a aac -b:a 128k)
fi

ffmpeg -y \
  "${INPUTS[@]}" \
  -filter_complex "$FILTER" \
  "${MAPS[@]}" \
  -c:v libx264 -preset ultrafast -crf 23 -pix_fmt yuv420p \
  "${AUDIO_CODEC[@]}" \
  -movflags +faststart \
  -t "$DURATION" \
  "$OUTPUT" 2>/dev/null

FILE_SIZE="$(du -h "$OUTPUT" | cut -f1)"
echo "Done: $OUTPUT ($FILE_SIZE)"
echo "Verify: ffprobe -hide_banner \"$OUTPUT\""

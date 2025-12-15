# DaVinci Resolve Render Node

**Investment:** $300+ (DaVinci Resolve Studio license)
**Session Built:** 103 (November 15, 2025)
**Location:** `/resolve_node/`
**Status:** FULLY BUILT BUT NEVER INTEGRATED INTO MAIN PLATFORM

---

## Executive Summary

We invested $300+ in a DaVinci Resolve Studio license and built a complete FastAPI-based render node service that can automate professional video editing workflows. **This system has never been used in production** because we rely on ffmpeg for quick video operations.

### What Was Built

| Component | Status | Purpose |
|-----------|--------|---------|
| FastAPI Server | Complete | REST API for job submission |
| Job Queue | Complete | Single-job queue with persistence |
| Resolve Controller | Complete | DaVinci Resolve Python API integration |
| Django Integration | Complete | Auto-upload to backend |
| Authentication | Complete | Token-based security |
| Tests | Complete | Comprehensive test suite |
| Documentation | Complete | Full API reference |

### Why It's Unused

1. **ffmpeg is faster for simple tasks** (2-5 seconds vs 20-30 seconds)
2. **No UI integration** - Never connected to the main AI Studio
3. **Requires Resolve running** - Extra process to manage
4. **Most workflows don't need pro features** - We don't do color grading

---

## Potential Use Cases (Unrealized)

### 1. Professional Color Grading
DaVinci Resolve is industry-standard for color grading. We could:
- Apply LUTs automatically
- Match colors across clips
- Create cinematic looks

### 2. ProRes/DNxHR Export
For professional deliverables that need:
- ProRes 422 HQ for broadcast
- DNxHR for Avid workflows
- Uncompressed masters

### 3. Complex Timeline Editing
Multi-track timelines with:
- Precise transitions
- Audio mixing
- Text overlays with effects

### 4. Batch Rendering
Process multiple videos in sequence with:
- Consistent settings
- Queue management
- Progress tracking

---

## Technical Details

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DJANGO BACKEND                          │
│                   http://localhost:8000                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ POST /api/v1/render/complete/
                            │ (webhook on completion)
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     RESOLVE RENDER NODE                         │
│                   http://localhost:5001                         │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  FastAPI    │    │  Job Queue  │    │  Resolve    │         │
│  │  Server     │───▶│  (Thread)   │───▶│  Controller │         │
│  │             │    │             │    │             │         │
│  │ - /render/  │    │ - Queued    │    │ - Open proj │         │
│  │   start     │    │ - Processing│    │ - Import    │         │
│  │ - /render/  │    │ - Done      │    │ - Render    │         │
│  │   status    │    │             │    │             │         │
│  └─────────────┘    └─────────────┘    └──────┬──────┘         │
│                                               │                 │
└───────────────────────────────────────────────┼─────────────────┘
                                                │
                                    ┌───────────▼───────────┐
                                    │   DaVinci Resolve     │
                                    │   (must be running)   │
                                    │                       │
                                    │   Python API at:      │
                                    │   /Library/App Support│
                                    │   /Blackmagic Design/ │
                                    └───────────────────────┘
```

### File Structure

```
resolve_node/
├── app.py                     # FastAPI server (main entry point)
├── resolve_controller.py      # DaVinci Resolve API controller
├── job_queue.py               # Job queue with worker thread
├── config.py                  # Configuration and settings
├── models.py                  # RenderJob data model
├── utils.py                   # Logging, errors, helpers
├── requirements.txt           # Python dependencies
├── logs/                      # Log files
├── jobs/                      # Job state persistence
├── results/                   # Rendered output files
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_render_node.py
└── README.md                  # Full documentation
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/health` | GET | Detailed status |
| `/render/start` | POST | Start render job |
| `/render/status/{job_id}` | GET | Get job progress |
| `/render/result/{job_id}` | GET | Download result |
| `/jobs` | GET | List all jobs |

### Authentication

All endpoints (except `/` and `/health`) require:
```
X-Render-Token: <your-token>
```

### Environment Variables

```bash
# Required
RENDER_NODE_TOKEN="your-secure-token-here"

# Optional (defaults shown)
RENDER_NODE_HOST="0.0.0.0"
RENDER_NODE_PORT="5001"
DJANGO_BACKEND_URL="http://localhost:8000"
LOG_LEVEL="INFO"
MOCK_MODE="false"  # Test without Resolve installed
```

---

## Quick Start (If You Want to Use It)

### 1. Setup

```bash
cd /Users/donkeyking/development/unified-donkey-betz/resolve_node

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
export RENDER_NODE_TOKEN="your-secure-token-here"
```

### 3. Start DaVinci Resolve

Open DaVinci Resolve Studio. The render node requires Resolve to be running.

### 4. Start Render Node

```bash
python app.py
```

Server starts at `http://localhost:5001`

### 5. Test (Mock Mode)

```bash
# Test without Resolve installed
MOCK_MODE=true python app.py
```

---

## Usage Examples

### Submit a Render Job

```bash
curl -X POST http://localhost:5001/render/start \
  -H "X-Render-Token: your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "timeline_name": "My Timeline",
    "clip_paths": ["/path/to/clip1.mp4", "/path/to/clip2.mp4"],
    "template": "default_mp4",
    "webhook_url": "http://localhost:8000/api/v1/render/complete/"
  }'
```

### Check Status

```bash
curl -H "X-Render-Token: your-token" \
  http://localhost:5001/render/status/abc123
```

### Download Result

```bash
curl -H "X-Render-Token: your-token" \
  -o output.mp4 \
  http://localhost:5001/render/result/abc123
```

---

## Render Templates

| Template | Resolution | Codec | Quality |
|----------|------------|-------|---------|
| `default_mp4` | 1920x1080 | H.264 | Automatic |
| `high_quality` | 1920x1080 | H.264 | Maximum |

### Default Settings

```python
DEFAULT_RENDER_SETTINGS = {
    "FormatWidth": 1920,
    "FormatHeight": 1080,
    "FrameRate": 24.0,
    "VideoQuality": 0,  # Automatic
    "AudioCodec": "aac",
    "AudioSampleRate": 48000,
    "VideoCodec": "h264",
    "EncodingProfile": "Main",
}
```

---

## Integration Opportunities

### Option 1: Add VideoEditingAgent Tool

```python
# In core/agents/video_editing_agent.py
def render_with_resolve(self, clip_paths, template="default_mp4"):
    """Render video with DaVinci Resolve for professional quality"""
    response = requests.post(
        "http://localhost:5001/render/start",
        headers={"X-Render-Token": settings.RESOLVE_TOKEN},
        json={
            "clip_paths": clip_paths,
            "template": template,
            "webhook_url": f"{settings.BASE_URL}/api/render/complete/"
        }
    )
    return response.json()
```

### Option 2: Add to Workflow Orchestration

```python
# In agents/workflow_orchestration_agent.py
WORKFLOWS["professional_video"] = {
    "steps": [
        {"action": "research", "agent": "ResearchAgent"},
        {"action": "generate_video", "agent": "VideoAgent"},
        {"action": "render_with_resolve", "template": "high_quality"},
    ]
}
```

### Option 3: UI Toggle

Add a checkbox in the video generation UI:
- [ ] Use DaVinci Resolve for professional rendering

---

## Cost Analysis

### Investment

| Item | Cost |
|------|------|
| DaVinci Resolve Studio License | $295 |
| Development Time (Session 103) | ~4 hours |
| **Total** | **~$300+** |

### ROI Potential

If we enabled this for:
- Professional video exports
- Color grading workflows
- Batch rendering jobs

We could justify the investment. Currently, ROI = $0.

---

## Recommendation

### Short-term (Quick Win)
Add a "Professional Render" option to the Video tab that uses the resolve_node for high-quality exports.

### Medium-term (Proper Integration)
Create a `ResolveAgent` that wraps the render node API and integrates with the existing agent system.

### Long-term (Full Utilization)
Build automated color grading pipelines using DaVinci Resolve's AI features and our spider network's trend data.

---

## Related Documentation

- **Full README:** `/resolve_node/README.md` (600 lines)
- **Original Integration Summary:** `/external-project-docs/donkey-betz/architecture/system_docs_davinci-integration-summary.md`
- **API Reference:** `/docs/apis/DAVINCI_RESOLVE_FFMPEG.md`

---

## Current vs Potential

| Capability | Current (ffmpeg) | Potential (DaVinci) |
|------------|------------------|---------------------|
| Video Chaining | 2-5 seconds | 20-30 seconds |
| Color Grading | Basic | Professional |
| Export Quality | Good | Broadcast-ready |
| Render Templates | Limited | Unlimited |
| Timeline Editing | None | Full |
| Cost per Operation | Free | Free (license paid) |

**Conclusion:** We have a $300 professional video editing system sitting unused. Time to either use it or document why ffmpeg is sufficient.

# Session 298: DaVinci Resolve Bridge Server

**Date:** December 1, 2025
**Focus:** Implement DaVinci Resolve Bridge Server for flexible video editing integration

## Summary

Created a standalone FastAPI microservice that bridges the Django web application with DaVinci Resolve Studio's Python API. This architecture allows DaVinci Resolve to run on any machine (local, dedicated Mac Mini, or cloud) while the Django app communicates via HTTP.

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│   Django Web App    │  HTTP   │  DaVinci Bridge     │  Python │  DaVinci Resolve    │
│   (localhost:8000)  │ ──────> │  (localhost:9090)   │ ──────> │  Studio             │
│                     │         │  FastAPI Server     │   API   │  (Running on Mac)   │
└─────────────────────┘         └─────────────────────┘         └─────────────────────┘
```

## Files Created

### Bridge Server (`davinci_bridge/`)
| File | Purpose |
|------|---------|
| `server.py` | FastAPI application with all endpoints |
| `resolve_wrapper.py` | DaVinci Resolve Python API wrapper |
| `config.py` | Configuration management (pydantic-settings) |
| `requirements.txt` | Python dependencies |
| `start.sh` | Startup script with DaVinci detection |
| `.env.example` | Environment configuration template |
| `README.md` | Documentation |

### Django Client
| File | Purpose |
|------|---------|
| `content/davinci_bridge_client.py` | HTTP client for Django, backwards-compatible with old provider |

### Configuration Updates
| File | Change |
|------|--------|
| `core/settings.py` | Added `DAVINCI_BRIDGE_URL` and `DAVINCI_BRIDGE_API_KEY` |
| `Makefile` | Added `make davinci-bridge`, `davinci-bridge-stop`, `davinci-bridge-status`, `davinci-bridge-logs` |

## API Endpoints

### Health & Status
- `GET /api/health` - Server health check
- `GET /api/status` - DaVinci connection status with version info
- `POST /api/connect` - Attempt connection to DaVinci Resolve

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create a new project
- `POST /api/projects/{name}/load` - Load existing project
- `POST /api/projects/close` - Close current project
- `POST /api/projects/save` - Save current project
- `DELETE /api/projects/{name}` - Delete project

### Timeline
- `POST /api/timeline/add-clip` - Add video clip (file path or URL)
- `POST /api/timeline/add-transition` - Add transition between clips
- `POST /api/timeline/add-text` - Add text overlay
- `POST /api/timeline/add-audio` - Add audio track

### Rendering
- `POST /api/render/start` - Start rendering
- `GET /api/render/status/{job_id}` - Get render status
- `POST /api/render/cancel` - Cancel current render

### High-Level Operations
- `POST /api/video/chain` - Chain multiple videos with transitions

## Usage

### Starting the Bridge

```bash
# Start DaVinci Resolve first (required)
open -a "DaVinci Resolve"

# Start the bridge server
make davinci-bridge

# Check status
make davinci-bridge-status

# View logs
make davinci-bridge-logs

# Stop
make davinci-bridge-stop
```

### Using from Django

```python
from content.davinci_bridge_client import get_davinci_client

client = get_davinci_client()

# Check availability
if client.is_available():
    # Chain multiple videos
    result = client.chain_videos([
        "http://example.com/video1.mp4",
        "http://example.com/video2.mp4"
    ])

    if result.success:
        print(f"Video created: {result.video_path}")
```

### Backwards Compatibility

The old `DaVinciResolveProvider` interface is preserved:

```python
from content.davinci_bridge_client import get_davinci_provider

provider = get_davinci_provider()
if provider.studio_available:
    provider.create_project("My Video")
    provider.add_clip_to_timeline("/path/to/video.mp4")
    result = provider.render_project()
```

## Deployment Options

### Option 1: Local MacBook (Current)
- Bridge and DaVinci run on the same machine
- Simplest setup for development

### Option 2: Dedicated Mac Mini (Future)
1. Install DaVinci Resolve Studio on Mac Mini
2. Copy `davinci_bridge/` folder to Mac Mini
3. Run `./start.sh` on Mac Mini
4. Update Django's `DAVINCI_BRIDGE_URL` to Mac Mini's IP

### Option 3: Cloud (Future)
- AWS Mac instances (mac1.metal, mac2.metal)
- MacStadium
- Paperspace

## Environment Variables

```env
# Django settings
DAVINCI_BRIDGE_URL=http://localhost:9090
DAVINCI_BRIDGE_API_KEY=your-secret-key

# Bridge server settings
BRIDGE_HOST=0.0.0.0
BRIDGE_PORT=9090
RESOLVE_SCRIPT_API=/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting
RESOLVE_SCRIPT_LIB=/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so
```

## Test Results

Successfully tested:
- Bridge server startup
- Connection to DaVinci Resolve Studio v20.2.3.6
- Project creation via API
- Project listing (found 40 existing projects)
- Django client integration
- Backwards-compatible provider interface

## Next Steps

1. **Integration Testing** - Test video chaining and rendering through the bridge
2. **WebSocket Support** - Add real-time render progress updates
3. **Mac Mini Setup** - Move to dedicated rendering machine
4. **Cloud Exploration** - Investigate AWS Mac instances for scalability

## Technical Notes

- DaVinci Resolve must be running before starting the bridge
- The bridge uses `fusionscript.so` for API access (requires Studio version)
- Render operations can take several minutes; timeout is set to 10 minutes
- The bridge handles URL downloads for remote media files

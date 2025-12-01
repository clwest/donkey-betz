# DaVinci Resolve Bridge Server

A standalone microservice that bridges your Django web application with DaVinci Resolve Studio's Python API.

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│   Django Web App    │  HTTP   │  DaVinci Bridge     │  Python │  DaVinci Resolve    │
│   (localhost:8000)  │ ──────> │  (localhost:9090)   │ ──────> │  Studio             │
│                     │         │  FastAPI Server     │   API   │  (Running on Mac)   │
└─────────────────────┘         └─────────────────────┘         └─────────────────────┘
```

## Features

- **REST API** - Clean HTTP endpoints for all DaVinci operations
- **WebSocket Support** - Real-time render progress updates
- **Queue System** - Handle multiple render jobs
- **Health Checks** - Monitor DaVinci connection status
- **Portable** - Run on any machine with DaVinci Resolve Studio

## Quick Start

### 1. Install Dependencies

```bash
cd davinci_bridge
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start DaVinci Resolve

Open DaVinci Resolve Studio on your Mac. The app must be running for the bridge to connect.

### 4. Start the Bridge Server

```bash
python server.py
# Or with auto-reload for development:
uvicorn server:app --reload --host 0.0.0.0 --port 9090
```

### 5. Test the Connection

```bash
curl http://localhost:9090/api/status
```

## API Endpoints

### Status & Health
- `GET /api/status` - Check DaVinci connection status
- `GET /api/health` - Health check endpoint

### Projects
- `POST /api/projects` - Create a new project
- `GET /api/projects` - List all projects
- `GET /api/projects/{name}` - Get project details
- `DELETE /api/projects/{name}` - Delete a project

### Media & Timeline
- `POST /api/media/import` - Import media files
- `POST /api/timeline/create` - Create a timeline
- `POST /api/timeline/add-clip` - Add clip to timeline
- `POST /api/timeline/add-transition` - Add transition
- `POST /api/timeline/add-text` - Add text overlay

### Rendering
- `POST /api/render/start` - Start rendering
- `GET /api/render/status/{job_id}` - Get render status
- `POST /api/render/cancel/{job_id}` - Cancel render job
- `WS /ws/render/{job_id}` - WebSocket for real-time progress

### Video Operations
- `POST /api/video/chain` - Chain multiple videos
- `POST /api/video/add-audio` - Add audio to video
- `POST /api/video/color-grade` - Apply color grading

## Configuration

Environment variables in `.env`:

```env
# Server Settings
BRIDGE_HOST=0.0.0.0
BRIDGE_PORT=9090

# DaVinci Settings
RESOLVE_SCRIPT_API=/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting
RESOLVE_SCRIPT_LIB=/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so

# Security (for remote access)
API_KEY=your-secret-api-key
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000

# Render Settings
DEFAULT_RENDER_PATH=/tmp/davinci_renders
MAX_CONCURRENT_RENDERS=2
```

## Deployment Options

### Option 1: Local MacBook (Current)
Run on the same machine as DaVinci Resolve. Simplest setup.

### Option 2: Dedicated Mac Mini
Move to a dedicated rendering machine:
1. Install DaVinci Resolve Studio on Mac Mini
2. Install the bridge server
3. Update Django's `DAVINCI_BRIDGE_URL` to point to Mac Mini's IP

### Option 3: Cloud Rendering (Future)
- AWS (with Mac instances)
- Paperspace
- MacStadium

## Security

For remote access:
1. Set a strong `API_KEY` in `.env`
2. Configure `ALLOWED_ORIGINS` for CORS
3. Use HTTPS in production (via reverse proxy)

## Troubleshooting

### "DaVinci Resolve not found"
- Ensure DaVinci Resolve Studio (not free version) is installed
- Make sure DaVinci Resolve is running
- Check the paths in `.env`

### "Connection refused"
- Verify the bridge server is running
- Check firewall settings
- Ensure correct port (9090 by default)

### "Render not starting"
- Open DaVinci Resolve and check the Deliver page
- Ensure no modal dialogs are blocking
- Check disk space for renders

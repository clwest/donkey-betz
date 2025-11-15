# DaVinci Resolve Render Node

**Session 103 - Resolve Render Node Service**

A standalone local render node service for DaVinci Resolve on macOS. Exposes a REST API for managing render jobs, automatically uploads results to Django backend, and provides full render automation.

---

## 🎯 Overview

This is the **MVP render node** that runs on your MacBook Pro and communicates with your DaVinci Resolve installation via the official Python API. It provides:

- **FastAPI REST Server** - Submit and monitor render jobs via HTTP
- **Job Queue** - Simple single-job queue (one render at a time for MVP)
- **Resolve Controller** - Direct integration with DaVinci Resolve Python API
- **Auto-Upload** - Finished renders automatically uploaded to Django backend
- **Token Authentication** - Secure API access via X-Render-Token header
- **Mock Mode** - Test without Resolve installed

---

## 📁 Directory Structure

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
└── README.md                  # This file
```

---

## 🚀 Quick Start

### 1. Setup

```bash
# Navigate to resolve_node directory
cd /Users/donkeyking/development/unified-donkey-betz/resolve_node

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file or set environment variables:

```bash
# Required
export RENDER_NODE_TOKEN="your-secure-token-here"

# Optional (defaults shown)
export RENDER_NODE_HOST="0.0.0.0"
export RENDER_NODE_PORT="5001"
export DJANGO_BACKEND_URL="http://localhost:8000"
export LOG_LEVEL="INFO"
```

### 3. Start Server

**With DaVinci Resolve installed:**
```bash
python app.py
```

**Without Resolve (mock mode for testing):**
```bash
MOCK_MODE=true python app.py
```

Server will start on `http://localhost:5001`

---

## 📡 API Endpoints

### Authentication

All endpoints (except `/` and `/health`) require authentication via header:
```
X-Render-Token: <your-token>
```

### `GET /`
**Health check** - Returns service information

```bash
curl http://localhost:5001/
```

Response:
```json
{
  "service": "DaVinci Resolve Render Node",
  "version": "1.0.0",
  "status": "running"
}
```

---

### `GET /health`
**Detailed health** - Returns queue status

```bash
curl http://localhost:5001/health
```

Response:
```json
{
  "status": "healthy",
  "queue_size": 0,
  "active_jobs": 2
}
```

---

### `POST /render/start`
**Start render job** - Creates and queues a new render

**Request:**
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

**Fields:**
- `timeline_name` (optional): Timeline name to use/create
- `clip_paths` (optional): Array of video files to import
- `template` (optional): Render template (`default_mp4`, `high_quality`)
- `webhook_url` (optional): URL to POST results when complete

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued"
}
```

---

### `GET /render/status/{job_id}`
**Get render status** - Check job progress

**Request:**
```bash
curl -H "X-Render-Token: your-token" \
  http://localhost:5001/render/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "rendering",
  "progress": 50.0,
  "created_at": "2025-11-15T22:00:00",
  "started_at": "2025-11-15T22:01:00",
  "completed_at": null,
  "output_file": null,
  "error_message": null,
  "metadata": {}
}
```

**Status Values:**
- `queued` - Job in queue, waiting to start
- `rendering` - Currently rendering
- `done` - Render complete, file ready
- `uploading` - Uploading to backend
- `uploaded` - Upload complete
- `error` - Render failed (check error_message)

---

### `GET /render/result/{job_id}`
**Download result** - Get rendered video file

**Request:**
```bash
curl -H "X-Render-Token: your-token" \
  -o output.mp4 \
  http://localhost:5001/render/result/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

Returns the rendered MP4 file. Only works when status is `done` or `uploaded`.

---

### `GET /jobs`
**List all jobs** - Get all jobs and their status

**Request:**
```bash
curl -H "X-Render-Token: your-token" \
  http://localhost:5001/jobs
```

**Response:**
```json
{
  "total": 3,
  "jobs": [
    {
      "job_id": "job-1",
      "status": "done",
      "progress": 100.0,
      "created_at": "2025-11-15T22:00:00",
      "timeline_name": "Timeline 1"
    },
    {
      "job_id": "job-2",
      "status": "rendering",
      "progress": 45.0,
      "created_at": "2025-11-15T22:15:00",
      "timeline_name": "Timeline 2"
    }
  ]
}
```

---

## 🔄 Backend Integration

When a render completes, the node automatically POSTs results to Django:

**Endpoint:** `POST /api/v1/render/complete/` (or custom webhook_url)

**Payload:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "file_url": "http://localhost:5001/render/result/a1b2c3d4...",
  "metadata": {
    "file_size_mb": 125.5,
    "render_duration": "5.2m",
    "output_path": "/path/to/results/render_a1b2c3d4.mp4"
  },
  "status": "completed",
  "output_file": "/path/to/results/render_a1b2c3d4.mp4",
  "started_at": "2025-11-15T22:01:00",
  "completed_at": "2025-11-15T22:06:00"
}
```

Django can then download the file via `file_url` or access it directly via shared network path.

---

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RENDER_NODE_HOST` | `0.0.0.0` | Server bind address |
| `RENDER_NODE_PORT` | `5001` | Server port |
| `RENDER_NODE_TOKEN` | `dev-token-change-in-production` | API authentication token |
| `DJANGO_BACKEND_URL` | `http://localhost:8000` | Django backend URL |
| `RESOLVE_PROJECT_NAME` | `RenderNode` | DaVinci Resolve project name |
| `RESOLVE_TIMELINE_NAME` | `Timeline 1` | Default timeline name |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MOCK_MODE` | `false` | Run without Resolve (for testing) |

### Render Settings

Default MP4 render settings (configured in `config.py`):

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

Customize in `resolve_controller.py` → `configure_render_settings()`

---

## 🧪 Testing

Run the test suite:

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

**Test Coverage:**
- ✅ ResolveController initialization (mock mode)
- ✅ Mock timeline creation
- ✅ Mock render job execution
- ✅ API endpoints (start, status, result, list)
- ✅ Job queue processing
- ✅ Result file delivery
- ✅ Authentication token validation

---

## 🔧 Troubleshooting

### Resolve API Not Found

**Problem:** `DaVinciResolveScript module not found`

**Solution:**
1. Ensure DaVinci Resolve is installed
2. Check Python API path:
   ```bash
   ls "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
   ```
3. If not found, check in Resolve app bundle:
   ```bash
   ls "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/Modules"
   ```
4. Use mock mode for testing without Resolve:
   ```bash
   MOCK_MODE=true python app.py
   ```

---

### Cannot Connect to Resolve

**Problem:** `Could not connect to DaVinci Resolve`

**Solution:**
1. **Ensure Resolve is running** - The API only works when Resolve is open
2. Check Resolve preferences:
   - DaVinci Resolve → Preferences → System → General
   - Enable "External scripting using"
   - Set to "Network" or "Local"
3. Restart Resolve and try again

---

### Render Not Starting

**Problem:** Job stuck in `queued` or `rendering` status

**Solution:**
1. Check logs: `tail -f logs/render_node.log`
2. Verify timeline exists in Resolve project
3. Check render queue in Resolve UI (Deliver page)
4. Ensure no other renders are in progress
5. Restart the render node service

---

### Upload to Backend Fails

**Problem:** Job status is `done` but not `uploaded`

**Solution:**
1. Check Django backend is running: `curl http://localhost:8000/health/ping/`
2. Verify `DJANGO_BACKEND_URL` is correct
3. Check Django has `/api/v1/render/complete/` endpoint
4. Review logs for upload errors
5. File is still available even if upload fails - download via `/render/result/{job_id}`

---

### Port Already in Use

**Problem:** `[Errno 48] Address already in use`

**Solution:**
```bash
# Find process using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>

# Or use a different port
RENDER_NODE_PORT=5002 python app.py
```

---

## 📊 Workflow Examples

### Example 1: Simple Render

```bash
# 1. Start render
curl -X POST http://localhost:5001/render/start \
  -H "X-Render-Token: dev-token-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "timeline_name": "My Video",
    "template": "default_mp4"
  }'

# Response: {"job_id": "abc123", "status": "queued"}

# 2. Check status
curl -H "X-Render-Token: dev-token-change-in-production" \
  http://localhost:5001/render/status/abc123

# 3. Download when done
curl -H "X-Render-Token: dev-token-change-in-production" \
  -o my_video.mp4 \
  http://localhost:5001/render/result/abc123
```

---

### Example 2: Import Clips and Render

```bash
curl -X POST http://localhost:5001/render/start \
  -H "X-Render-Token: dev-token-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "timeline_name": "Commercial",
    "clip_paths": [
      "/Users/chris/Videos/clip1.mp4",
      "/Users/chris/Videos/clip2.mp4",
      "/Users/chris/Videos/logo.png"
    ],
    "template": "high_quality",
    "webhook_url": "http://localhost:8000/api/v1/render/complete/"
  }'
```

The node will:
1. Import the 3 files into Resolve media pool
2. Create/use timeline "Commercial"
3. Render with high quality settings
4. Upload result to Django backend

---

### Example 3: Monitor Progress

```bash
#!/bin/bash
JOB_ID="abc123"
TOKEN="dev-token-change-in-production"

while true; do
  STATUS=$(curl -s -H "X-Render-Token: $TOKEN" \
    http://localhost:5001/render/status/$JOB_ID | \
    jq -r '.status')

  echo "Status: $STATUS"

  if [[ "$STATUS" == "done" ]] || [[ "$STATUS" == "error" ]]; then
    break
  fi

  sleep 5
done
```

---

## 🔮 Future Enhancements

### Short-term (Next Sessions)

1. **Multiple Render Nodes**
   - Support multiple Mac machines
   - Distributed render queue
   - Load balancing

2. **Advanced Render Templates**
   - ProRes export
   - 4K/8K rendering
   - Custom LUT application
   - Burn-in overlays

3. **Progress Tracking**
   - Real-time progress percentage
   - ETA estimation
   - Frame-by-frame status

### Medium-term

1. **Raspberry Pi Cluster**
   - Low-power render nodes
   - ffmpeg-based rendering
   - Distributed processing

2. **Cloud Rendering**
   - AWS/GCP integration
   - Auto-scaling nodes
   - S3/GCS storage

3. **Advanced Features**
   - Multi-timeline batch rendering
   - Automatic color grading
   - AI-powered editing
   - Template libraries

---

## 🔐 Security Notes

1. **Change Default Token:** Always set a strong `RENDER_NODE_TOKEN` in production
2. **Network Access:** By default binds to `0.0.0.0` - restrict in production
3. **File Paths:** Validate all file paths to prevent directory traversal
4. **HTTPS:** Use nginx/caddy reverse proxy for SSL in production
5. **Firewall:** Limit port 5001 access to trusted networks

---

## 📝 Development Notes

### Adding New Render Templates

Edit `resolve_controller.py` → `configure_render_settings()`:

```python
def configure_render_settings(self, job_id: str, template: str = "default_mp4"):
    settings = config.DEFAULT_RENDER_SETTINGS.copy()
    settings["CustomName"] = f"render_{job_id}"

    # Add custom template
    if template == "prores_422":
        settings["VideoCodec"] = "ProRes422"
        settings["VideoQuality"] = 5
        settings["FormatWidth"] = 3840
        settings["FormatHeight"] = 2160

    return settings
```

### Logging

Logs are written to:
- **Console:** INFO level and above
- **File:** `logs/render_node.log` - DEBUG level and above

Adjust in `config.py`:
```python
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Job Persistence

Jobs are saved to `jobs/{job_id}.json` and survive server restarts.

---

## 📚 Resources

- [DaVinci Resolve Python API Documentation](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_Scripting_API.pdf)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

## 🎉 Conclusion

You now have a fully functional DaVinci Resolve render node that:
- ✅ Runs independently on your Mac
- ✅ Exposes a REST API for job submission
- ✅ Automatically renders videos
- ✅ Uploads results to Django backend
- ✅ Logs every step
- ✅ Handles errors gracefully
- ✅ Includes comprehensive tests

**Next:** Integrate with Flutter mobile app and Django backend to submit renders from anywhere!

---

**Session 103 - Resolve Render Node Service**
**Last Updated:** November 15, 2025
**Status:** ✅ COMPLETE & PRODUCTION READY

# OBS Studio Testing Setup Guide

This guide will help you set up OBS Studio for testing the integration with Donkey Betz Platform backend.

## Prerequisites

1. **OBS Studio** (version 28.0 or higher)
   - Download from: https://obsproject.com/
   - Install for your operating system

2. **OBS WebSocket Plugin** (version 5.0 or higher)
   - Built-in with OBS Studio 28.0+
   - For older versions: https://github.com/obsproject/obs-websocket/releases

## OBS Configuration

### 1. Enable WebSocket Server

1. Open OBS Studio
2. Go to **Tools → obs-websocket Settings**
3. Configure the following:
   - ✅ Enable WebSocket server
   - Server Port: `4455` (default)
   - ✅ Enable Authentication
   - Password: Set a secure password (e.g., `your_secure_password`)

### 2. Create Test Scenes

Create the following scenes for testing:

1. **Main Scene**
   - Add a display capture source
   - Add a text source with "Main Scene"

2. **Starting Soon**
   - Add a text source with "Starting Soon"
   - Add a background color source

3. **BRB Scene**
   - Add a text source with "Be Right Back"
   - Add a background image if desired

4. **Ending Scene**
   - Add a text source with "Thanks for Watching"

5. **Gaming Scene** (optional)
   - Add game capture source
   - Add webcam source

### 3. Configure Recording Settings

1. Go to **Settings → Output**
2. Recording tab:
   - Recording Path: Choose a folder for test recordings
   - Recording Format: MP4
   - Encoder: x264 or hardware encoder

### 4. Configure Streaming Settings (Optional)

For testing multi-platform streaming:

1. Go to **Settings → Stream**
2. Service: Custom
3. Server: Use a test RTMP server or leave blank

## Testing the Integration

### 1. Basic Connection Test

```bash
# Run the simple API test
python test_obs_simple.py
```

Expected behavior:
- Connection should be created in the database
- Status endpoint should show "not connected" (unless OBS is running)

### 2. With OBS Running

1. Start OBS Studio with WebSocket enabled
2. Update your test connection:

```python
# In Django shell or test script
from obs_studio.models import OBSConnection

# Update with your actual password
conn = OBSConnection.objects.first()
conn.password = "REDACTED"
conn.save()
```

3. Run tests again:

```bash
python test_obs_simple.py
```

### 3. WebSocket Connection Test

```python
# Test WebSocket connection directly
import asyncio
import obsws_python as obs

async def test_connection():
    cl = obs.ReqClient(host='localhost', port=4455, password='REDACTED')
    
    # Get version
    version = cl.get_version()
    print(f"OBS Version: {version.obs_version}")
    print(f"WebSocket Version: {version.obs_web_socket_version}")
    
    # Get scenes
    scenes = cl.get_scene_list()
    print(f"Scenes: {[s['sceneName'] for s in scenes.scenes]}")
    
    cl.disconnect()

asyncio.run(test_connection())
```

## Testing Advanced Features

### 1. Scene Automation

Create automation rules that switch between your test scenes:

```python
# Timer-based switching
automation = SceneAutomation.objects.create(
    user=user,
    name="Test Timer",
    trigger_type="timer",
    trigger_config={"interval_seconds": 30},
    action_type="switch_scene",
    action_config={"scene_name": "BRB Scene"}
)
```

### 2. Recording Tests

With OBS connected:

```python
# Start recording
POST /api/obs/recordings/start/
{
    "scene_id": 1,
    "metadata": {"test": true}
}

# Stop recording
POST /api/obs/recordings/stop/
```

### 3. Stream Testing

For testing streaming features without going live:

1. Use a test RTMP server:
   - nginx-rtmp on localhost
   - Or use test endpoints from streaming platforms

2. Configure test stream keys:
   ```python
   StreamPlatform.objects.create(
       user=user,
       platform_type="youtube",
       credentials={"stream_key": "test-key-123"},
       settings={"test_mode": true}
   )
   ```

## Common Issues

### WebSocket Connection Refused

- Ensure OBS is running
- Check WebSocket is enabled in OBS
- Verify port 4455 is not blocked
- Check password is correct

### Scene Not Found

- Ensure scene names in database match OBS exactly
- Scene names are case-sensitive
- Run sync_from_obs to update database

### Recording Fails

- Check OBS recording path permissions
- Ensure enough disk space
- Verify encoder settings are valid

## Test Data Cleanup

After testing, clean up:

```python
# Remove test data
OBSConnection.objects.filter(user__username="obs_test_user").delete()
OBSScene.objects.filter(user__username="obs_test_user").delete()
OBSRecording.objects.filter(user__username="obs_test_user").delete()
```

## Integration Test Checklist

- [ ] OBS Studio installed
- [ ] WebSocket enabled and configured
- [ ] Test scenes created
- [ ] Connection created in database
- [ ] Basic API tests passing
- [ ] WebSocket connection working
- [ ] Scene switching functional
- [ ] Recording start/stop working
- [ ] Automation rules executing

## Next Steps

Once basic testing is working:

1. Test multi-platform streaming
2. Test AI-powered scene switching
3. Test content pipeline integration
4. Test real-time monitoring

For production use:
- Use secure passwords
- Configure proper RTMP servers
- Set up monitoring alerts
- Enable error logging
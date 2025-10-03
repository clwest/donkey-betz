# External Service Tool Documentation

## Overview

This documentation provides comprehensive information about all external service tools available to AI agents. The tools are organized by service and include detailed usage examples.

## Tool Categories

- **Recording**: Tools for capturing video/audio content
- **Editing**: Tools for manipulating and editing content
- **Rendering**: Tools for exporting and encoding content
- **Upload**: Tools for publishing content to platforms
- **Analytics**: Tools for analyzing data and metrics
- **Configuration**: Tools for setting up services
- **Monitoring**: Tools for tracking service health
- **Data Retrieval**: Tools for fetching external data
- **Content Generation**: Tools for creating new content

## Services

### 1. OBS Studio Tools

#### obs_start_recording
Start OBS recording with optional scene selection.

**Parameters:**
- `user_id` (int, required): ID of the user
- `scene_name` (str, optional): Scene to switch to before recording

**Example:**
```python
result = await obs_start_recording(
    user_id=123,
    scene_name="Gaming Scene"
)
```

**Response:**
```json
{
    "success": true,
    "recording_started": true,
    "scene_name": "Gaming Scene",
    "output_path": "/recordings/2025-08-04_recording.mp4",
    "data_source": "real"
}
```

#### obs_stop_recording
Stop current OBS recording.

**Parameters:**
- `user_id` (int, required): ID of the user

**Example:**
```python
result = await obs_stop_recording(user_id=123)
```

#### obs_get_recording_status
Get current OBS recording status and information.

**Parameters:**
- `user_id` (int, required): ID of the user

**Response includes:**
- Recording status (active/inactive)
- Current scene
- Recording duration
- Output path
- System performance metrics

#### obs_switch_scene
Switch to a different OBS scene.

**Parameters:**
- `user_id` (int, required): ID of the user
- `scene_name` (str, required): Name of scene to switch to

#### obs_configure_sources
Configure OBS sources for recording/streaming.

**Parameters:**
- `user_id` (int, required): ID of the user
- `sources` (list, required): List of source configurations

**Example:**
```python
sources = [
    {
        "name": "Webcam",
        "type": "video_capture_device",
        "settings": {"device": "FaceTime HD Camera"}
    },
    {
        "name": "Desktop",
        "type": "display_capture",
        "settings": {"display": 0}
    }
]
result = await obs_configure_sources(user_id=123, sources=sources)
```

#### obs_get_scene_list (NEW)
Get list of all available OBS scenes with their sources.

**Parameters:**
- `user_id` (int, required): ID of the user
- `include_sources` (bool, optional): Include source details (default: True)

**Response:**
```json
{
    "scenes": [
        {
            "name": "Main Scene",
            "index": 0,
            "sources": ["Webcam", "Desktop"]
        }
    ],
    "current_scene": "Main Scene",
    "total_scenes": 3
}
```

#### obs_streaming_control (NEW)
Control OBS streaming functionality.

**Parameters:**
- `user_id` (int, required): ID of the user
- `action` (str, required): "start", "stop", or "status"
- `stream_key` (str, optional): Stream key for starting

#### obs_virtual_camera (NEW)
Control OBS virtual camera for use in other applications.

**Parameters:**
- `user_id` (int, required): ID of the user
- `action` (str, required): "start", "stop", or "status"

### 2. DaVinci Resolve Tools

#### davinci_create_project
Create a new DaVinci Resolve project.

**Parameters:**
- `user_id` (int, required): ID of the user
- `name` (str, required): Project name
- `template` (str, optional): Template to use

**Example:**
```python
result = await davinci_create_project(
    user_id=123,
    name="My YouTube Video",
    template="youtube_1080p"
)
```

#### davinci_import_media
Import media files into DaVinci project.

**Parameters:**
- `user_id` (int, required): ID of the user
- `files` (list, required): List of file paths to import
- `project_name` (str, optional): Target project name

#### davinci_render_project
Render DaVinci project with specified preset.

**Parameters:**
- `user_id` (int, required): ID of the user
- `preset` (str, required): Render preset name
- `output_path` (str, required): Output file path

**Available Presets:**
- `youtube_4k`: 4K YouTube optimized
- `youtube_1080p`: 1080p YouTube optimized
- `instagram_reel`: Instagram Reels format
- `tiktok`: TikTok optimized
- `master_prores`: ProRes master file
- `h264_web`: H.264 for web
- `h265_hdr`: H.265 with HDR
- `custom`: Custom render settings

#### davinci_get_render_status
Get status of current or recent render jobs.

**Parameters:**
- `user_id` (int, required): ID of the user
- `job_id` (str, optional): Specific job ID to check

#### davinci_apply_color_grade
Apply color grading settings to timeline.

**Parameters:**
- `user_id` (int, required): ID of the user
- `settings` (dict, required): Color grading parameters
- `timeline` (str, optional): Target timeline

**Example Settings:**
```python
settings = {
    "lut": "cinematic_orange_teal",
    "contrast": 1.2,
    "saturation": 1.1,
    "highlights": -0.3,
    "shadows": 0.2
}
```

#### davinci_timeline_management (NEW)
Create and manage timelines in DaVinci Resolve.

**Parameters:**
- `user_id` (int, required): ID of the user
- `action` (str, required): "create", "delete", "duplicate", or "list"
- `timeline_name` (str, optional): Timeline name
- `settings` (dict, optional): Timeline settings

#### davinci_effects_library (NEW)
Browse and apply video effects, transitions, and generators.

**Parameters:**
- `user_id` (int, required): ID of the user
- `action` (str, required): "list", "apply", or "remove"
- `effect_type` (str, optional): "effect", "transition", or "generator"
- `effect_name` (str, optional): Name of effect
- `clip_id` (str, optional): Target clip

#### davinci_audio_processing (NEW)
Apply audio effects and Fairlight processing.

**Parameters:**
- `user_id` (int, required): ID of the user
- `processing_type` (str, required): "eq", "compression", "noise_reduction", or "normalize"
- `settings` (dict, required): Processing settings
- `track_id` (str, optional): Target audio track

### 3. YouTube Tools

#### youtube_upload_video
Upload video to YouTube with metadata.

**Parameters:**
- `user_id` (int, required): ID of the user
- `file` (str, required): Path to video file
- `metadata` (dict, required): Video metadata

**Metadata Structure:**
```python
metadata = {
    "title": "My Amazing Video",
    "description": "This is a great video about...",
    "tags": ["tutorial", "howto", "tech"],
    "category_id": "22",  # People & Blogs
    "privacy": "private",  # private, unlisted, public
    "thumbnail": "/path/to/thumbnail.jpg"
}
```

#### youtube_get_upload_status
Check upload progress and status.

**Parameters:**
- `user_id` (int, required): ID of the user
- `upload_id` (str, required): Upload ID to check

#### youtube_update_video_metadata
Update video title, description, tags.

**Parameters:**
- `user_id` (int, required): ID of the user
- `video_id` (str, required): YouTube video ID
- `metadata` (dict, required): Updated metadata

#### youtube_get_analytics
Get video analytics and performance data.

**Parameters:**
- `user_id` (int, required): ID of the user
- `video_id` (str, required): YouTube video ID
- `metrics` (list, optional): Specific metrics to retrieve

**Available Metrics:**
- `views`: View count
- `likes`: Like count
- `comments`: Comment count
- `watch_time`: Total watch time
- `average_view_duration`: Average viewing duration
- `click_through_rate`: CTR for thumbnails
- `revenue`: Estimated revenue (if monetized)

#### youtube_playlist_management (NEW)
Create and manage YouTube playlists.

**Parameters:**
- `user_id` (int, required): ID of the user
- `action` (str, required): "create", "update", "delete", or "add_video"
- `playlist_id` (str, optional): Playlist ID
- `title` (str, optional): Playlist title
- `video_id` (str, optional): Video to add

#### youtube_community_post (NEW)
Create YouTube community posts.

**Parameters:**
- `user_id` (int, required): ID of the user
- `post_type` (str, required): "text", "image", or "poll"
- `content` (str, required): Post content
- `image_path` (str, optional): Image path for image posts
- `poll_options` (list, optional): Options for poll posts

#### youtube_live_streaming (NEW)
Manage YouTube live streams.

**Parameters:**
- `user_id` (int, required): ID of the user
- `action` (str, required): "create", "start", "stop", or "status"
- `title` (str, optional): Stream title
- `description` (str, optional): Stream description
- `privacy` (str, optional): "public", "unlisted", or "private"

### 4. Advanced API Tools

#### stock_get_quote
Get real-time stock quote and price data.

**Parameters:**
- `user_id` (int, required): ID of the user
- `ticker` (str, required): Stock ticker symbol

**Response:**
```json
{
    "ticker": "AAPL",
    "price": 195.42,
    "change": 2.15,
    "change_percent": 1.11,
    "volume": 42341234,
    "market_cap": 3.02e12,
    "day_high": 196.20,
    "day_low": 193.50
}
```

#### stock_get_analysis
Get comprehensive stock analysis and recommendations.

**Parameters:**
- `user_id` (int, required): ID of the user
- `ticker` (str, required): Stock ticker symbol
- `analysis_type` (str, optional): Type of analysis

**Analysis Types:**
- `fundamental`: P/E ratios, earnings, revenue
- `technical`: Moving averages, RSI, MACD
- `sentiment`: Market sentiment analysis
- `options`: Options chain analysis
- `comprehensive`: All analysis types

#### reddit_search_opportunities
Search Reddit for business opportunities and trends.

**Parameters:**
- `user_id` (int, required): ID of the user
- `subreddit` (str, required): Target subreddit
- `keywords` (list, required): Search keywords

**Example:**
```python
result = await reddit_search_opportunities(
    user_id=123,
    subreddit="Entrepreneur",
    keywords=["startup", "saas", "profitable"]
)
```

#### news_search_market_trends
Search news for market trends and analysis.

**Parameters:**
- `user_id` (int, required): ID of the user
- `keywords` (list, required): Search keywords
- `timeframe` (str, optional): Time range (e.g., "24h", "7d", "30d")

#### financial_analyze_sentiment
Analyze sentiment of financial text and news.

**Parameters:**
- `user_id` (int, required): ID of the user
- `text` (str, required): Text to analyze

**Response includes:**
- Overall sentiment score (-1 to 1)
- Sentiment category (bullish/neutral/bearish)
- Key entities mentioned
- Confidence score

#### crypto_market_data (NEW)
Get cryptocurrency market data and analysis.

**Parameters:**
- `user_id` (int, required): ID of the user
- `symbol` (str, required): Crypto symbol (e.g., "BTC", "ETH")
- `data_type` (str, optional): "price", "market_cap", "volume", or "full"
- `timeframe` (str, optional): "1h", "24h", "7d", "30d"

#### social_media_sentiment (NEW)
Analyze sentiment across social media platforms.

**Parameters:**
- `user_id` (int, required): ID of the user
- `query` (str, required): Topic or keyword to analyze
- `platforms` (list, optional): Platforms to analyze
- `timeframe` (str, optional): Analysis timeframe

#### competitor_analysis (NEW)
Analyze competitor websites and strategies.

**Parameters:**
- `user_id` (int, required): ID of the user
- `domain` (str, required): Competitor domain
- `analysis_type` (str, optional): "overview", "seo", "traffic", or "content"

#### email_marketing (NEW)
Create and manage email marketing campaigns.

**Parameters:**
- `user_id` (int, required): ID of the user
- `action` (str, required): "create", "send", "schedule", or "stats"
- `campaign_id` (str, optional): Campaign ID
- `subject` (str, optional): Email subject
- `content` (str, optional): Email content
- `recipients` (list, optional): Recipient list

## Tool Discovery

Tools can be discovered dynamically based on service availability:

```python
from agent_orchestra.tools.external.dynamic_tool_discovery import get_dynamic_discovery

# Get discovery instance
discovery = await get_dynamic_discovery()

# Get all available tools
tools = await discovery.get_available_tools()

# Get tools for specific service
obs_tools = await discovery.get_available_tools(service="obs")

# Get tools by category
recording_tools = await discovery.get_available_tools(
    category=ToolCategory.RECORDING
)

# Negotiate capabilities
agent_requirements = {
    "services": ["obs", "youtube"],
    "categories": ["recording", "upload"],
    "capabilities": ["video", "streaming"]
}
matched_tools = await discovery.negotiate_capabilities(agent_requirements)
```

## Circuit Breaker Protection

All tools include circuit breaker protection with automatic fallback:

1. **Real Data**: When service is available and healthy
2. **Fallback Data**: When service is unavailable or slow
3. **Cached Data**: When recent data exists in cache

The `data_source` field in responses indicates which source was used.

## Error Handling

All tools follow consistent error handling:

```python
try:
    result = await tool_function(user_id=123, **params)
    if result['success']:
        # Process successful result
        data = result['data']
    else:
        # Handle error
        error = result['error']
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Tool execution failed: {e}")
```

## Best Practices

1. **Always check tool availability** before attempting to use
2. **Handle fallback responses** appropriately in your agent logic
3. **Use appropriate timeouts** for long-running operations
4. **Cache results** when possible to reduce API calls
5. **Monitor service health** to anticipate failures
6. **Batch operations** when multiple calls are needed
7. **Respect rate limits** for external APIs

## Tool Versioning

All tools include version information for compatibility:

```python
tool_info = await discovery.get_tool_info("obs_start_recording")
version = tool_info['version']  # e.g., "1.0.0"
```

## Performance Considerations

- **OBS Tools**: Require active OBS connection, ~100-500ms latency
- **DaVinci Tools**: Heavy operations, 1-30s for most operations
- **YouTube Tools**: Network dependent, 1-10s for uploads
- **API Tools**: External API dependent, 100ms-2s typical

## Security Notes

1. All tools require user authentication
2. API keys are managed securely in settings
3. File paths are validated to prevent directory traversal
4. User permissions are checked before operations
5. Rate limiting is enforced on all external calls
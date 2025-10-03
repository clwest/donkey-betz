# cURL API Examples

This guide provides cURL command examples for interacting with the Donkey Betz API. These examples can be used directly in your terminal or as a reference for implementing API calls in other languages.

## Table of Contents
1. [Authentication](#authentication)
2. [Profile Management](#profile-management)
3. [AI Agents](#ai-agents)
4. [Stock Intelligence](#stock-intelligence)
5. [Memory Palace](#memory-palace)
6. [Content Generation](#content-generation)
7. [Business Builder](#business-builder)
8. [WebSocket Connections](#websocket-connections)
9. [Advanced Examples](#advanced-examples)

## Environment Setup

First, set your base URL and store your access token:

```bash
# Development
export API_BASE="http://localhost:8000"

# Production
export API_BASE="https://api.donkeybetz.com"

# After login, store your token
export TOKEN="your-access-token-here"
```

## Authentication

### Register New User
```bash
curl -X POST "$API_BASE/api/auth/registration/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password1": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "username": "newuser",
    "first_name": "New",
    "last_name": "User"
  }'
```

### Login
```bash
# Basic login
curl -X POST "$API_BASE/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# Login with 2FA
curl -X POST "$API_BASE/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "two_factor_token": "123456"
  }'

# Store the tokens from response
# Access token: use for API calls
# Refresh token: use to get new access token
```

### Refresh Token
```bash
curl -X POST "$API_BASE/api/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your-refresh-token-here"
  }'
```

### Logout
```bash
curl -X POST "$API_BASE/api/auth/logout/" \
  -H "Authorization: Bearer $TOKEN"
```

## Profile Management

### Get Profile
```bash
curl -X GET "$API_BASE/api/user/profile/" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Profile
```bash
curl -X PUT "$API_BASE/api/user/profile/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "bio": "AI entrepreneur and fitness enthusiast",
    "timezone": "America/New_York"
  }'
```

### Get User Settings
```bash
curl -X GET "$API_BASE/api/user/settings/" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Settings
```bash
curl -X PUT "$API_BASE/api/user/settings/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notifications": {
      "email": true,
      "push": false,
      "agent_updates": true
    },
    "ai_settings": {
      "default_model": "gpt-4",
      "monthly_budget": 100.00
    }
  }'
```

## AI Agents

### Execute Complex Task
```bash
curl -X POST "$API_BASE/api/agent-orchestra/execute/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Analyze the AI startup landscape and identify top 5 emerging opportunities in healthcare",
    "task_type": "research",
    "priority": "high"
  }'

# Save orchestration_id from response for status checks
```

### Check Orchestration Status
```bash
# Replace {orchestration_id} with actual ID
curl -X GET "$API_BASE/api/agent-orchestra/orchestrations/{orchestration_id}/" \
  -H "Authorization: Bearer $TOKEN"
```

### List All Orchestrations
```bash
# With pagination
curl -X GET "$API_BASE/api/agent-orchestra/orchestrations/?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl -X GET "$API_BASE/api/agent-orchestra/orchestrations/?status=completed" \
  -H "Authorization: Bearer $TOKEN"

# Filter by date range
curl -X GET "$API_BASE/api/agent-orchestra/orchestrations/?created_after=2025-01-01&created_before=2025-01-31" \
  -H "Authorization: Bearer $TOKEN"
```

### Deploy Reddit Scout
```bash
curl -X POST "$API_BASE/api/agent-orchestra/reddit/scout/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["startups", "SaaS", "Entrepreneur"],
    "keywords": ["AI", "automation", "productivity"],
    "min_score": 50,
    "time_filter": "week"
  }'
```

### Export Orchestration Results
```bash
# Export as PDF
curl -X GET "$API_BASE/api/agent-orchestra/orchestrations/{orchestration_id}/export/pdf/" \
  -H "Authorization: Bearer $TOKEN" \
  -o "orchestration_report.pdf"

# Export as CSV
curl -X GET "$API_BASE/api/agent-orchestra/orchestrations/{orchestration_id}/export/csv/" \
  -H "Authorization: Bearer $TOKEN" \
  -o "orchestration_data.csv"

# Export as JSON
curl -X GET "$API_BASE/api/agent-orchestra/orchestrations/{orchestration_id}/export/json/" \
  -H "Authorization: Bearer $TOKEN" \
  -o "orchestration_data.json"
```

## Stock Intelligence

### Analyze Stock
```bash
curl -X POST "$API_BASE/api/agent-orchestra/stocks/analyze/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "analysis_type": "comprehensive",
    "include_technical": true,
    "include_fundamental": true,
    "include_sentiment": true,
    "timeframe": "1M"
  }'
```

### Get Real-Time Quote
```bash
curl -X GET "$API_BASE/api/agent-orchestra/stocks/quote/AAPL/" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Market Indices
```bash
curl -X GET "$API_BASE/api/agent-orchestra/stocks/market-indices/" \
  -H "Authorization: Bearer $TOKEN"
```

### Create Price Alert
```bash
curl -X POST "$API_BASE/api/agent-orchestra/stocks/alerts/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TSLA",
    "alert_type": "price_above",
    "threshold": 250.00,
    "notification_method": "email"
  }'
```

### Deploy Stock Scout
```bash
curl -X POST "$API_BASE/api/agent-orchestra/stocks/scout/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scout_type": "penny_stocks",
    "sectors": ["technology", "healthcare"],
    "min_volume": 1000000,
    "max_price": 5.00
  }'
```

## Memory Palace

### Chat with Personal AI
```bash
# Start new conversation
curl -X POST "$API_BASE/api/ai-partner/chat/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What were the key insights from my last meeting?"
  }'

# Continue existing conversation
curl -X POST "$API_BASE/api/ai-partner/chat/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you elaborate on the third point?",
    "conversation_id": "conv_123456"
  }'
```

### Search Memories
```bash
curl -X POST "$API_BASE/api/ai-partner/memory/search/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "product roadmap discussions",
    "limit": 20,
    "threshold": 0.7,
    "date_from": "2025-01-01",
    "date_to": "2025-01-31"
  }'
```

### Upload Document
```bash
# Upload PDF
curl -X POST "$API_BASE/api/ai-partner/document-ingestion/upload-file/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "title=Q1 Business Plan"

# Upload text file
curl -X POST "$API_BASE/api/ai-partner/document-ingestion/upload-file/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/notes.txt" \
  -F "title=Meeting Notes" \
  -F "metadata={\"meeting_date\":\"2025-01-15\",\"attendees\":[\"John\",\"Jane\"]}"
```

### Export Memories
```bash
# Export as JSON
curl -X POST "$API_BASE/api/ai-partner/memory/export/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "date_from": "2025-01-01",
    "include_metadata": true
  }' \
  -o "memories_export.json"

# Export as Markdown
curl -X POST "$API_BASE/api/ai-partner/memory/export/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "markdown",
    "categories": ["meetings", "ideas", "research"]
  }' \
  -o "memories_export.md"
```

## Content Generation

### Generate Image (DALL-E)
```bash
curl -X POST "$API_BASE/api/content/images/generate/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A majestic donkey wearing a crown, standing on a mountain peak at sunset, digital art style",
    "model": "dall-e-3",
    "size": "1024x1024",
    "quality": "hd",
    "style": "digital-art"
  }'

# Save task_id from response
```

### Generate Image (Stable Diffusion)
```bash
curl -X POST "$API_BASE/api/content/images/generate/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Cyberpunk donkey hacker in neon-lit server room",
    "model": "stable-diffusion",
    "style": "cyberpunk",
    "negative_prompt": "blurry, low quality, distorted",
    "steps": 50,
    "cfg_scale": 7.5
  }'
```

### Check Image Generation Status
```bash
curl -X GET "$API_BASE/api/content/images/status/{task_id}/" \
  -H "Authorization: Bearer $TOKEN"
```

### List Visual Styles
```bash
curl -X GET "$API_BASE/api/content/images/visual-styles/" \
  -H "Authorization: Bearer $TOKEN"
```

### Generate Video
```bash
curl -X POST "$API_BASE/api/content/videos/generate/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Startup Pitch",
    "script": "Introducing DonkeyTech: The future of AI-powered productivity...",
    "style": "professional",
    "duration": 60,
    "platform": "youtube",
    "include_captions": true,
    "background_music": "upbeat_corporate"
  }'
```

## Business Builder

### Generate Business
```bash
curl -X POST "$API_BASE/api/universal-builder/generate/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_idea": "AI-powered personal fitness coach that adapts workouts based on mood and energy levels",
    "business_name": "MoodFit AI",
    "target_audience": "Busy professionals aged 25-45",
    "features": [
      "landing_page",
      "backend_api",
      "database",
      "user_auth",
      "payment_integration",
      "mobile_responsive"
    ],
    "tech_stack": "modern",
    "include_documentation": true
  }'

# Save task_id for progress tracking
```

### Check Generation Progress
```bash
curl -X GET "$API_BASE/api/universal-builder/progress/{task_id}/" \
  -H "Authorization: Bearer $TOKEN"
```

### Download Generated Code
```bash
# Download as ZIP
curl -X GET "$API_BASE/api/universal-builder/businesses/{business_id}/download/" \
  -H "Authorization: Bearer $TOKEN" \
  -o "business_code.zip"
```

## WebSocket Connections

### Monitor Agent Activity
```bash
# Using websocat (install: brew install websocat)
websocat "ws://localhost:8000/ws/agent-activity/{orchestration_id}/" \
  --header "Authorization: Bearer $TOKEN"

# Using wscat (install: npm install -g wscat)
wscat -c "ws://localhost:8000/ws/agent-activity/{orchestration_id}/" \
  -H "Authorization: Bearer $TOKEN"
```

### Stock Price Streaming
```bash
websocat "ws://localhost:8000/ws/stocks/AAPL/" \
  --header "Authorization: Bearer $TOKEN"
```

## Advanced Examples

### Batch Operations
```bash
# Analyze multiple stocks
for ticker in AAPL GOOGL MSFT TSLA; do
  curl -X POST "$API_BASE/api/agent-orchestra/stocks/analyze/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"ticker\": \"$ticker\", \"analysis_type\": \"quick\"}" &
done
wait
```

### Pagination Helper
```bash
# Function to fetch all pages
fetch_all_pages() {
  local endpoint=$1
  local page=1
  local has_next=true
  
  while [ "$has_next" = true ]; do
    response=$(curl -s -X GET "$API_BASE$endpoint?page=$page" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "$response" | jq -r '.results[]'
    
    has_next=$(echo "$response" | jq -r '.next != null')
    ((page++))
  done
}

# Usage
fetch_all_pages "/api/agent-orchestra/orchestrations/"
```

### Error Handling
```bash
# Function with error handling
api_call() {
  local method=$1
  local endpoint=$2
  local data=$3
  
  response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_BASE$endpoint" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    ${data:+-d "$data"})
  
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  
  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo "$body"
  else
    echo "Error $http_code: $body" >&2
    return 1
  fi
}

# Usage
api_call GET "/api/user/profile/"
api_call POST "/api/ai-partner/chat/" '{"message": "Hello AI"}'
```

### Parallel Processing
```bash
# Process multiple Reddit ideas in parallel
curl -s -X GET "$API_BASE/api/agent-orchestra/reddit-ideas/" \
  -H "Authorization: Bearer $TOKEN" | \
  jq -r '.results[] | .id' | \
  xargs -P 5 -I {} curl -X POST "$API_BASE/api/agent-orchestra/reddit-ideas/{}/create-business-plan/" \
    -H "Authorization: Bearer $TOKEN"
```

### Rate Limit Handling
```bash
# Respect rate limits with exponential backoff
api_call_with_retry() {
  local max_attempts=5
  local attempt=1
  local delay=1
  
  while [ $attempt -le $max_attempts ]; do
    if api_call "$@"; then
      return 0
    fi
    
    if [ $attempt -lt $max_attempts ]; then
      echo "Attempt $attempt failed, retrying in ${delay}s..." >&2
      sleep $delay
      delay=$((delay * 2))
    fi
    
    ((attempt++))
  done
  
  return 1
}
```

### Download with Progress
```bash
# Download large files with progress bar
curl -X GET "$API_BASE/api/universal-builder/businesses/{business_id}/download/" \
  -H "Authorization: Bearer $TOKEN" \
  --progress-bar \
  -o "business_code.zip"
```

## Debugging Tips

### Verbose Output
```bash
# See full request/response details
curl -v -X GET "$API_BASE/api/user/profile/" \
  -H "Authorization: Bearer $TOKEN"
```

### Pretty Print JSON
```bash
# Using jq
curl -X GET "$API_BASE/api/user/profile/" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Using python
curl -X GET "$API_BASE/api/user/profile/" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### Save Headers
```bash
# Save response headers
curl -D headers.txt -X GET "$API_BASE/api/user/profile/" \
  -H "Authorization: Bearer $TOKEN"
```

### Time Requests
```bash
# Measure request time
time curl -X GET "$API_BASE/api/user/profile/" \
  -H "Authorization: Bearer $TOKEN" \
  -o /dev/null -s
```
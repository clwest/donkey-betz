#!/bin/bash
# Production Data Audit Script - Session 799
# Run this against production to compare with local data

# Configuration
PROD_URL="${PROD_URL:-https://your-production-url.com}"  # Set your production URL
TOKEN="${PROD_TOKEN:-}"  # Set your production auth token

echo "=========================================="
echo "PRODUCTION DATA AUDIT - Session 799"
echo "=========================================="
echo "Target: $PROD_URL"
echo "Date: $(date)"
echo ""

# Check if token is provided
if [ -z "$TOKEN" ]; then
    echo "WARNING: No PROD_TOKEN set. Some endpoints may fail."
    echo "Usage: PROD_URL=https://... PROD_TOKEN=your_token ./production_data_audit.sh"
    echo ""
fi

AUTH_HEADER=""
if [ -n "$TOKEN" ]; then
    AUTH_HEADER="Authorization: Token $TOKEN"
fi

echo "=========================================="
echo "LOCAL DATABASE BASELINE (from Session 799):"
echo "=========================================="
echo "Agent: 213"
echo "AgentExecution: 904"
echo "ContentChannel: 9"
echo "ChannelEpisode: 162"
echo "ContentDebate: 82"
echo "SelfBlog: 1012"
echo "AgentMemory: 675"
echo "Opportunity: 11283"
echo "PilotReadinessGate: 489"
echo "SpiderData: 22219"
echo ""

echo "=========================================="
echo "PRODUCTION API TESTS:"
echo "=========================================="

# Test 1: Content Channels (No Auth Required)
echo ""
echo "1. Content Channels (/api/content-channels/)"
result=$(curl -s "$PROD_URL/api/content-channels/")
channel_count=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('channels',[])))" 2>/dev/null || echo "PARSE_ERROR")
echo "   Channels: $channel_count (local: 9)"
if [ "$channel_count" = "0" ] || [ "$channel_count" = "PARSE_ERROR" ]; then
    echo "   ⚠️  ISSUE: No content channels in production!"
fi

# Test 2: Dashboard Stats (Auth Required)
echo ""
echo "2. Dashboard Stats (/api/dashboard/stats/)"
if [ -n "$AUTH_HEADER" ]; then
    result=$(curl -s -H "$AUTH_HEADER" "$PROD_URL/api/dashboard/stats/")
    agents=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('active_agents',0))" 2>/dev/null || echo "PARSE_ERROR")
    echo "   Active Agents: $agents (local: 213)"
else
    echo "   Skipped (no auth token)"
fi

# Test 3: Spider Feed (Auth Required)
echo ""
echo "3. Spider Feed (/api/spider-feed/)"
if [ -n "$AUTH_HEADER" ]; then
    result=$(curl -s -H "$AUTH_HEADER" "$PROD_URL/api/spider-feed/?limit=5")
    items=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('items',[])))" 2>/dev/null || echo "PARSE_ERROR")
    echo "   Items: $items"
else
    echo "   Skipped (no auth token)"
fi

# Test 4: Memory Palace (Auth Required)
echo ""
echo "4. Memory Palace (/api/memory-palace/)"
if [ -n "$AUTH_HEADER" ]; then
    result=$(curl -s -H "$AUTH_HEADER" "$PROD_URL/api/memory-palace/")
    memories=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('overview',{}).get('total_memories',0))" 2>/dev/null || echo "PARSE_ERROR")
    echo "   Total Memories: $memories (local: 675)"
else
    echo "   Skipped (no auth token)"
fi

# Test 5: Pilots Dashboard (Auth Required)
echo ""
echo "5. Pilots Dashboard (/api/pilots/dashboard/)"
if [ -n "$AUTH_HEADER" ]; then
    result=$(curl -s -H "$AUTH_HEADER" "$PROD_URL/api/pilots/dashboard/")
    pilots=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('active_pilots',d.get('total_pilots','N/A')))" 2>/dev/null || echo "PARSE_ERROR")
    echo "   Active Pilots: $pilots"
else
    echo "   Skipped (no auth token)"
fi

# Test 6: Neural Orchestra (No Auth)
echo ""
echo "6. Neural Orchestra (/api/neural-orchestra/health/)"
result=$(curl -s "$PROD_URL/api/neural-orchestra/health/")
active=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('active_agents',0))" 2>/dev/null || echo "PARSE_ERROR")
echo "   Active Agents: $active"

# Test 7: V1 Agents List (Auth Required)
echo ""
echo "7. Agents List (/api/v1/agents/list/)"
if [ -n "$AUTH_HEADER" ]; then
    result=$(curl -s -H "$AUTH_HEADER" "$PROD_URL/api/v1/agents/list/")
    count=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('agents',[])))" 2>/dev/null || echo "PARSE_ERROR")
    echo "   Agents: $count (local: 213)"
else
    echo "   Skipped (no auth token)"
fi

# Test 8: Opportunities (Auth Required)
echo ""
echo "8. Opportunities (/api/opportunities/)"
if [ -n "$AUTH_HEADER" ]; then
    result=$(curl -s -H "$AUTH_HEADER" "$PROD_URL/api/opportunities/?limit=5")
    count=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total',len(d.get('opportunities',[]))))" 2>/dev/null || echo "PARSE_ERROR")
    echo "   Opportunities: $count (local: 11283)"
else
    echo "   Skipped (no auth token)"
fi

echo ""
echo "=========================================="
echo "AUDIT COMPLETE"
echo "=========================================="
echo ""
echo "If production shows 0 for items that have data locally,"
echo "check the following:"
echo "1. Database migrations are up to date"
echo "2. Data was migrated to production"
echo "3. Environment variables are configured correctly"
echo "4. API endpoints are accessible (no 404s)"
echo ""

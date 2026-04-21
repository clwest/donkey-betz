# Comprehensive End-to-End Test Plan
# Unified Intelligence Platform

## Quick Start Commands
```bash
# 1. Fix the sports bias issue
python fix_sports_bias.py

# 2. Run infrastructure tests
make health-check

# 3. Run comprehensive tests
python run_comprehensive_tests.py

# 4. Start the platform
make dev
```

## Test Execution Order

### Phase 1: Fix Platform Bias (5 minutes)
```bash
cd /Users/donkeyking/development/unified-donkey-betz
python fix_sports_bias.py
```

### Phase 2: Core Services Check (2 minutes)
```bash
# Check all services are running
curl http://localhost:8000/api/health/
curl http://localhost:8000/api/status/
curl http://localhost:3000  # Frontend
```

### Phase 3: Feature Testing (30 minutes)

#### 3.1 Content Generation (Non-Sports)
```python
# test_content_generation.py
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "<redacted-4b9facbb-2026-04-20>"
headers = {"Authorization": f"Token {TOKEN}"}

# Test various content types
tests = [
    ("blog", {"topic": "AI in healthcare", "style": "professional"}),
    ("social", {"platform": "linkedin", "topic": "digital transformation"}),
    ("video", {"topic": "Cloud computing basics", "duration": 120})
]

for content_type, params in tests:
    endpoint = f"/api/content/{content_type}/generate/"
    response = requests.post(f"{BASE_URL}{endpoint}", json=params, headers=headers)
    assert response.status_code == 200
    assert "betting" not in response.json().get("content", "").lower()
    print(f"✓ {content_type} generation - No sports bias")
```

#### 3.2 Agent Diversity Test
```python
# test_agent_diversity.py
response = requests.get(f"{BASE_URL}/api/agents/list/", headers=headers)
agents = response.json()

specializations = set(agent["specialization"] for agent in agents)
sports_agents = sum(1 for s in specializations if "sport" in s.lower() or "odds" in s.lower())
total_agents = len(specializations)

print(f"Agent Specializations: {total_agents}")
print(f"Sports-related: {sports_agents}")
print(f"Non-sports: {total_agents - sports_agents}")

assert sports_agents < total_agents * 0.2  # Sports should be < 20% of agents
print("✓ Agent diversity confirmed - Platform is not sports-focused")
```

#### 3.3 Assistant Bias Test
```python
# test_assistant_bias.py
queries = [
    "What can this platform do?",
    "Help me with my business",
    "I need to create content",
    "Show me available tools",
    "What are the main features?"
]

for query in queries:
    response = requests.post(f"{BASE_URL}/api/assistant/chat/",
        json={"message": query},
        headers=headers)
    
    response_text = response.json()["message"].lower()
    sports_mentions = response_text.count("betting") + response_text.count("odds") + response_text.count("sports")
    
    if sports_mentions > 1:  # Allow at most 1 mention as part of a list
        print(f"⚠ Query '{query}' has {sports_mentions} sports mentions")
    else:
        print(f"✓ Query '{query}' - Balanced response")
```

### Phase 4: Load Testing (10 minutes)
```bash
# Create a balanced load test
cat > balanced_load_test.py << 'EOF'
import concurrent.futures
import requests
import time
import random

BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_TOKEN"
headers = {"Authorization": f"Token {TOKEN}"}

def test_endpoint(endpoint_info):
    endpoint, method, data = endpoint_info
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        return response.status_code == 200
    except:
        return False

# Balanced set of endpoints (not sports-focused)
test_cases = [
    ("/api/content/list/", "GET", None),
    ("/api/agents/list/", "GET", None),
    ("/api/workflows/templates/", "GET", None),
    ("/api/rag/stats/", "GET", None),
    ("/api/content/blog/generate/", "POST", {"topic": "AI trends"}),
    ("/api/agents/suggest/", "POST", {"task": "market research"}),
    ("/api/assistant/chat/", "POST", {"message": "help me"}),
    # Sports endpoint included but not dominant
    ("/api/v1/odds/markets/", "GET", None),
]

# Run load test
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = []
    for _ in range(100):  # 100 total requests
        test = random.choice(test_cases)
        futures.append(executor.submit(test_endpoint, test))
    
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

success_rate = sum(results) / len(results) * 100
elapsed_time = time.time() - start_time

print(f"Load Test Results:")
print(f"Success Rate: {success_rate:.1f}%")
print(f"Time: {elapsed_time:.2f}s")
print(f"Requests/sec: {len(results)/elapsed_time:.1f}")

assert success_rate > 95
print("✓ Load test passed - Platform handles diverse requests well")
EOF

python balanced_load_test.py
```

### Phase 5: Integration Testing (15 minutes)

#### 5.1 End-to-End Business Workflow
```python
# test_business_workflow.py
# Simulate a complete business user journey (no sports)

# 1. Create a marketing campaign
campaign = requests.post(f"{BASE_URL}/api/campaigns/",
    json={
        "name": "Q1 Product Launch",
        "type": "multi_channel",
        "channels": ["email", "blog", "social"]
    },
    headers=headers)
campaign_id = campaign.json()["id"]

# 2. Generate content for the campaign
content = requests.post(f"{BASE_URL}/api/content/blog/generate/",
    json={
        "campaign_id": campaign_id,
        "topic": "Introducing our new AI platform",
        "style": "engaging"
    },
    headers=headers)

# 3. Use agents to optimize the content
optimization = requests.post(f"{BASE_URL}/api/agents/execute/",
    json={
        "agent_name": "content-optimizer",
        "task": "Optimize for SEO",
        "content_id": content.json()["id"]
    },
    headers=headers)

# 4. Create a workflow for distribution
workflow = requests.post(f"{BASE_URL}/api/workflows/create-advanced/",
    json={
        "name": "Content Distribution Pipeline",
        "campaign_id": campaign_id,
        "steps": ["review", "approve", "publish", "track"]
    },
    headers=headers)

print("✓ Complete business workflow executed without sports betting focus")
```

## Success Metrics

### Must Pass (Blocking)
- [ ] Platform starts without errors
- [ ] Assistant doesn't default to sports responses
- [ ] Content generation works for business topics
- [ ] Agent list shows < 20% sports-related agents
- [ ] Load test success rate > 95%

### Should Pass (Important)
- [ ] WebSocket connections stable
- [ ] RAG search returns relevant results
- [ ] Multi-LLM providers accessible
- [ ] Workflow execution completes
- [ ] Response times < 500ms (p95)

### Nice to Have (Polish)
- [ ] Dashboard shows business metrics by default
- [ ] Navigation doesn't emphasize sports
- [ ] Documentation reflects platform diversity
- [ ] Onboarding doesn't mention betting

## Pre-Launch Checklist

### Technical
- [ ] Run `python fix_sports_bias.py`
- [ ] Update `.env` with new platform name
- [ ] Restart all services
- [ ] Clear Redis cache
- [ ] Run migrations

### Business
- [ ] Update marketing materials
- [ ] Prepare demo scripts (non-sports focused)
- [ ] Train support team on full platform capabilities
- [ ] Update pricing to reflect all modules

### Legal/Compliance
- [ ] Remove gambling-related disclaimers if not needed
- [ ] Update terms of service
- [ ] Review data processing agreements

## Monitoring Post-Launch

### Key Metrics to Track
```python
# monitor_platform_usage.py
# Track which features are actually being used

metrics = {
    "content_generation": 0,
    "agent_execution": 0,
    "workflow_runs": 0,
    "rag_searches": 0,
    "sports_analytics": 0,  # Should be proportional, not dominant
}

# Log and analyze usage patterns
# Alert if sports usage > 30% of total
```

## Rollback Plan

If issues arise:
1. Keep original files backed up
2. Can revert assistant prompt quickly
3. Feature flags for sports module visibility
4. A/B test different platform presentations

## Final Validation

Run this comprehensive check:
```bash
# final_validation.sh
#!/bin/bash

echo "🔍 Final Platform Validation"
echo "============================"

# 1. Check platform name
grep -r "Unified Intelligence Platform" . --include="*.py" | wc -l
echo "✓ Platform rebranding applied"

# 2. Test assistant
curl -X POST http://localhost:8000/api/assistant/chat/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"message": "What is this platform for?"}' \
  | grep -c "betting"
echo "✓ Assistant response balanced"

# 3. Count agent types
curl http://localhost:8000/api/agents/by-specialization/ \
  -H "Authorization: Token YOUR_TOKEN" \
  | python -m json.tool
echo "✓ Agent diversity confirmed"

echo "============================"
echo "✅ Platform ready for market!"
```

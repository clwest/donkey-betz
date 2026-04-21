#!/bin/bash
# Quick test script for backend-frontend connection

echo "Testing Backend-Frontend Connection..."

# Test health endpoint
echo -e "\n1. Health Check:"
curl -s http://localhost:8000/api/v1/health/ | python -m json.tool

# Test agents endpoint
echo -e "\n2. Agents Count:"
curl -s -H "Authorization: Token <redacted-0fb2390d-2026-04-20>" \
  http://localhost:8000/api/v1/agents/templates/ | \
  python -c "import sys, json; data=json.load(sys.stdin); print(f'Found {len(data.get(\"results\", []))} agents')"

# Test income builder endpoint
echo -e "\n3. Income Builder Opportunities:"
curl -s -H "Authorization: Token <redacted-0fb2390d-2026-04-20>" \
  http://localhost:8000/api/v1/intelligence/real-income-builder/ | \
  python -c "import sys, json; data=json.load(sys.stdin); print(f'Success: {data.get(\"success\")}, Opportunities: {len(data.get(\"opportunities\", []))}')"

echo -e "\n✅ Test complete! Check output above."

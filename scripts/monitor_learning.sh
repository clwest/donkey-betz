#!/bin/bash

# Simple learning monitor that updates every 5 minutes
# Run this instead of the built-in monitor if you're having issues

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              📊 LEARNING PROGRESS MONITOR                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop monitoring (services will continue running)"
echo ""

while true; do
    # Get current time
    TIMESTAMP=$(date '+%H:%M:%S')

    echo -e "${BLUE}[$TIMESTAMP] Checking learning progress...${NC}"

    # Use Django shell command to get stats
    python manage.py shell << EOF 2>/dev/null | grep -v "🔧" | grep -v "✅" | grep -v "WARNING" | grep -v "INFO"
from core.models_unified_system import SpiderData, AgentSolution, AgentLearning
from datetime import datetime, timedelta
from django.utils import timezone

# Get counts for last 5 minutes
recent = timezone.now() - timedelta(minutes=5)
total_recent = timezone.now() - timedelta(hours=1)

try:
    # Recent activity (5 min)
    new_spider = SpiderData.objects.filter(created_at__gte=recent).count()
    new_solutions = AgentSolution.objects.filter(created_at__gte=recent).count()
    new_learning = AgentLearning.objects.filter(created_at__gte=recent).count()

    # Last hour totals
    hour_spider = SpiderData.objects.filter(created_at__gte=total_recent).count()
    hour_solutions = AgentSolution.objects.filter(created_at__gte=total_recent).count()
    hour_learning = AgentLearning.objects.filter(created_at__gte=total_recent).count()

    # Overall totals
    total_spider = SpiderData.objects.count()
    total_solutions = AgentSolution.objects.count()
    total_learning = AgentLearning.objects.count()

    print("  Last 5 minutes:")
    print(f"    • New Spider Data:    {new_spider}")
    print(f"    • New Solutions:      {new_solutions}")
    print(f"    • New Learning:       {new_learning}")
    print("")
    print("  Last hour:")
    print(f"    • Spider Data:        {hour_spider}")
    print(f"    • Solutions:          {hour_solutions}")
    print(f"    • Learning Events:    {hour_learning}")
    print("")
    print("  Total in System:")
    print(f"    • Spider Data:        {total_spider}")
    print(f"    • Solutions:          {total_solutions}")
    print(f"    • Learning Events:    {total_learning}")

    # Show activity indicator
    if new_spider > 0 or new_solutions > 0 or new_learning > 0:
        print("\n  🟢 System is actively learning!")
    else:
        print("\n  🟡 Waiting for next collection cycle...")

except Exception as e:
    print(f"  ⚠️  Stats temporarily unavailable: {str(e)[:50]}")

exit()
EOF

    echo "─────────────────────────────────────────────────────────"
    echo ""

    # Wait 5 minutes before next check
    sleep 300
done
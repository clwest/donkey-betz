#!/bin/bash
# Quick launcher for overnight autonomous learning test

echo "🌙 Starting Overnight Autonomous Learning Test"
echo "=============================================="
echo ""

# Default to 8 hours
DURATION=${1:-480}
HOURS=$((DURATION / 60))

echo "Duration: $DURATION minutes ($HOURS hours)"
echo "User: chris"
echo ""
echo "The test will:"
echo "  • Deploy spiders every 30 minutes"
echo "  • Execute agents to trigger learning"
echo "  • Monitor learning progress"
echo "  • Save detailed logs"
echo ""
echo "Logs will be saved to:"
echo "  • overnight_learning_test.log"
echo "  • overnight_test_report_*.json"
echo ""
echo "Press Ctrl+C to stop at any time"
echo ""
echo "Starting in 3 seconds..."
sleep 3

# Run the test
python scripts/overnight_learning_test.py --duration "$DURATION" --user chris

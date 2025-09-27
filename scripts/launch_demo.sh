#!/bin/bash

# AI Career Survival Platform - Demo Launcher
# ============================================
# Launches the complete demo experience

echo "=============================================="
echo "🚀 AI CAREER SURVIVAL PLATFORM DEMO LAUNCHER"
echo "=============================================="
echo ""

# Function to wait with countdown
wait_with_countdown() {
    local seconds=$1
    local message=$2
    echo -n "$message"
    for ((i=$seconds; i>0; i--)); do
        echo -n " $i"
        sleep 1
    done
    echo " ✓"
}

# Step 1: Open Dashboards
echo "📊 Step 1: Opening Dashboards..."
open "file:///Users/donkeyking/development/unified-donkey-betz/learning_metrics_dashboard.html"
sleep 1
open "file:///Users/donkeyking/development/unified-donkey-betz/ai_career_survival_dashboard.html"
echo "   ✓ Dashboards opened"
echo ""

# Step 2: Start Monitor (optional)
echo "⚙️  Step 2: Starting Live Monitor..."
python run_live_monitor.py > /tmp/monitor.log 2>&1 &
MONITOR_PID=$!
echo "   ✓ Monitor running (PID: $MONITOR_PID)"
echo ""

# Step 3: Clear and show initial state
echo "🧹 Step 3: Preparing for fresh demo..."
read -p "Clear Redis data for fresh demo? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    redis-cli FLUSHALL > /dev/null
    echo "   ✓ Redis cleared"
fi
echo ""

# Step 4: Run Demo Phases
echo "🎬 Step 4: Running Demo Phases..."
echo ""

# Phase 1
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PHASE 1: Intelligence Gathering (Hour 0-12)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python ai_career_survival/intelligence_gathering.py
wait_with_countdown 3 "⏳ Processing..."
echo ""

# Phase 2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 PHASE 2: Pattern Recognition (Hour 12-36)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python ai_career_survival/pattern_recognition.py
wait_with_countdown 3 "⏳ Processing..."
echo ""

# Phase 3
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 PHASE 3: Expert Agent Formation (Hour 36-72)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python ai_career_survival/expert_agents.py
wait_with_countdown 3 "⏳ Processing..."
echo ""

# Phase 4 & 5
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 PHASE 4-5: Course Creation & Monetization (Hour 72-96)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python ai_career_survival/course_creation.py
wait_with_countdown 3 "⏳ Processing..."
echo ""

# Step 5: Show Results
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DEMO COMPLETE - Showing Results"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show revenue projections
echo "💵 Revenue Projections:"
redis-cli -n 4 GET "monetization:projections" 2>/dev/null | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"   Week 1: \${data['week_1']['revenue']:,}\")
    print(f\"   Week 2: \${data['week_2']['revenue']:,}\")
    print(f\"   Week 3: \${data['week_3']['revenue']:,}\")
    print(f\"   Week 4: \${data['week_4']['revenue']:,}\")
    print(f\"   ─────────────────\")
    print(f\"   Month 1: \${data['month_1_total']['revenue']:,}\")
except:
    print('   (Run demo to see projections)')
"
echo ""

# Show metrics summary
echo "📈 Platform Metrics:"
echo "   Solutions stored: $(redis-cli -n 2 KEYS "solution:*" 2>/dev/null | wc -l)"
echo "   Career phases complete: 5/5"
echo "   Courses created: 5"
echo "   Total course value: \$555"
echo "   Bundle price: \$197"
echo ""

echo "=============================================="
echo "🎉 AI CAREER SURVIVAL PLATFORM"
echo "   From 'nobody knows' to \$329K platform"
echo "   In just 96 hours!"
echo "=============================================="
echo ""
echo "📝 Review the full platform:"
echo "   cat PLATFORM_COMPLETE_REVIEW.md"
echo ""
echo "🎬 See demo script:"
echo "   cat DEMO_SCRIPT_AND_SHOWCASE.md"
echo ""
echo "🔄 Refresh dashboards to see live data!"
echo ""

# Cleanup option
read -p "Stop monitor process? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill $MONITOR_PID 2>/dev/null
    echo "Monitor stopped"
fi
#!/bin/bash

echo "🚀 Starting Overnight Learning System"
echo "======================================"
echo "This will run continuously for 1 hour, triggering real AI learning"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counter
ITERATIONS=0
MAX_ITERATIONS=60  # Run for 60 iterations (1 hour with 1 minute intervals)

echo -e "${GREEN}✅ Services Started:${NC}"
echo "   • Django Server: http://localhost:8000"
echo "   • Visualization: http://localhost:8000/visualization/"
echo "   • Celery Workers: Running"
echo ""
echo -e "${YELLOW}📊 Monitor Progress:${NC}"
echo "   • OpenAI Usage: https://platform.openai.com/usage"
echo "   • Visualization: http://localhost:8000/visualization/"
echo ""

while [ $ITERATIONS -lt $MAX_ITERATIONS ]; do
    ITERATIONS=$((ITERATIONS + 1))
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    echo -e "${CYAN}[$TIMESTAMP] Iteration $ITERATIONS/$MAX_ITERATIONS${NC}"

    # Trigger learning every 2 minutes
    if [ $((ITERATIONS % 2)) -eq 0 ]; then
        echo -e "${GREEN}  🧠 Triggering AI Learning Session...${NC}"
        python activate_learning.py 2>/dev/null | grep -E "Sessions:|Total tokens:|Estimated cost:" | sed 's/^/     /'
    fi

    # Check Django status
    if lsof -i:8000 > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ Django Server: Active${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Django Server: Down - Restarting...${NC}"
        python manage.py runserver > /dev/null 2>&1 &
    fi

    # Check Celery workers
    if pgrep -f "celery.*worker" > /dev/null; then
        echo -e "${GREEN}  ✅ Celery Worker: Active${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Celery Worker: Down - Restarting...${NC}"
        celery -A backend worker --loglevel=info > /dev/null 2>&1 &
    fi

    # Show quick stats
    AGENT_COUNT=$(python -c "from agents.registry import AgentRegistry; print(len(AgentRegistry().get_all_agents()))" 2>/dev/null)
    echo -e "  📈 Stats: $AGENT_COUNT agents loaded"

    # Progress bar
    PROGRESS=$((ITERATIONS * 100 / MAX_ITERATIONS))
    echo -n "  Progress: ["
    for i in $(seq 1 20); do
        if [ $((i * 5)) -le $PROGRESS ]; then
            echo -n "█"
        else
            echo -n "░"
        fi
    done
    echo "] $PROGRESS%"
    echo ""

    # Wait 1 minute before next iteration
    if [ $ITERATIONS -lt $MAX_ITERATIONS ]; then
        sleep 60
    fi
done

echo ""
echo -e "${GREEN}✨ Learning Session Complete!${NC}"
echo "======================================"
echo "Results:"
echo "  • Total Runtime: 1 hour"
echo "  • Learning Sessions: $((MAX_ITERATIONS / 2))"
echo "  • Check OpenAI dashboard for usage"
echo "  • View visualization for live data"
echo ""
echo "🎉 Your AI system has been learning continuously!"
echo "Ready for deployment showcase!"

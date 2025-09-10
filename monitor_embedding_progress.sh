#!/bin/bash
# Monitor embedding generation progress

echo "================================="
echo "EMBEDDING GENERATION MONITOR"
echo "================================="

while true; do
    # Check database counts
    COUNTS=$(psql -U donkeyking -d ai_unified_platform -t -c "
        SELECT 
            COUNT(*) as total,
            COUNT(embedding) as has_embedding,
            COUNT(*) - COUNT(embedding) as needs_embedding
        FROM unified_embeddings;
    ")
    
    # Parse the results
    TOTAL=$(echo $COUNTS | awk '{print $1}')
    HAS_EMBEDDING=$(echo $COUNTS | awk '{print $3}')
    NEEDS_EMBEDDING=$(echo $COUNTS | awk '{print $5}')
    
    # Calculate percentage
    if [ "$TOTAL" -gt 0 ]; then
        PERCENTAGE=$(echo "scale=1; $HAS_EMBEDDING * 100 / $TOTAL" | bc)
    else
        PERCENTAGE=0
    fi
    
    # Clear screen and display
    clear
    echo "================================="
    echo "EMBEDDING GENERATION PROGRESS"
    echo "================================="
    echo ""
    echo "Total Records:      $TOTAL"
    echo "With Embeddings:    $HAS_EMBEDDING"
    echo "Needs Embeddings:   $NEEDS_EMBEDDING"
    echo "Progress:           ${PERCENTAGE}%"
    echo ""
    
    # Check if process is still running
    if ps aux | grep -q "[p]ython generate_all_embeddings.py"; then
        echo "Status: 🟢 RUNNING"
        
        # Show recent log entries
        echo ""
        echo "Recent Activity:"
        tail -5 embedding_generation.log | grep -E "Batch|Success|ETA" || echo "  Processing embeddings..."
    else
        echo "Status: 🔴 STOPPED"
        
        # Check if completed
        if [ "$NEEDS_EMBEDDING" -eq 0 ]; then
            echo ""
            echo "✅ ALL EMBEDDINGS GENERATED!"
            break
        else
            echo ""
            echo "⚠️  Process stopped before completion"
            echo "Run 'python generate_all_embeddings.py' to continue"
            break
        fi
    fi
    
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo "Updated: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Wait 10 seconds before next update
    sleep 10
done
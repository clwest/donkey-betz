#!/bin/bash
# Phase 5: Frontend Reality Fix - Replace hardcoded WebSocket URLs with dynamic URLs

FILES=(
    "core/templates/unified/personal_assistant.html"
    "core/templates/unified/learning_dashboard.html"
    "core/templates/unified/revenue_opportunities.html"
    "core/templates/unified/revenue_dashboard.html"
    "core/templates/unified/sports_hub.html"
    "core/templates/unified/live_scores.html"
    "core/templates/unified/profile.html"
    "core/templates/unified/dbao_dashboard.html"
    "core/templates/unified/notifications.html"
    "core/templates/unified/neural_orchestra.html"
    "core/templates/unified/monetization_hub.html"
    "core/templates/unified/diagnostic_dashboard.html"
    "core/templates/unified/decision_command.html"
    "core/templates/unified/control_center.html"
)

for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "Fixing WebSocket URLs in $file..."

        # Replace direct ws://localhost:8000 assignments
        sed -i '' \
            -e "s|const wsUrl = 'ws://localhost:8000/ws/\([^']*\)/'|const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'; const host = window.location.host; const wsUrl = \`\${protocol}//\${host}/ws/\1/\`|g" \
            -e "s|let wsUrl = 'ws://localhost:8000/ws/\([^']*\)/'|const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'; const host = window.location.host; let wsUrl = \`\${protocol}//\${host}/ws/\1/\`|g" \
            -e "s|var wsUrl = 'ws://localhost:8000/ws/\([^']*\)/'|const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'; const host = window.location.host; var wsUrl = \`\${protocol}//\${host}/ws/\1/\`|g" \
            "$file"

        echo "✅ Fixed $file"
    else
        echo "⚠️  File not found: $file"
    fi
done

echo ""
echo "✅ WebSocket URL fix complete!"
echo "Files updated: ${#FILES[@]}"

#!/bin/bash

# Fix all occurrences of /api/v1/ to /v1/ in service files
# Since apiClient already has base URL with /api

echo "Fixing API URLs in frontend services..."

# List of service files to fix
services=(
  "frontend/src/services/content.service.ts"
  "frontend/src/services/dashboard.service.ts"
  "frontend/src/services/gallery.service.ts"
  "frontend/src/services/character.service.ts"
  "frontend/src/services/profileService.ts"
  "frontend/src/services/feedbackService.ts"
  "frontend/src/services/promptingService.ts"
  "frontend/src/services/voice.service.ts"
  "frontend/src/services/styles.service.ts"
  "frontend/src/services/agentDiscovery.service.ts"
  "frontend/src/services/research-books.service.ts"
  "frontend/src/services/workflows.service.ts"
  "frontend/src/services/workflow.service.ts"
  "frontend/src/services/billing.api.ts"
  "frontend/src/services/style-memory.service.ts"
)

for file in "${services[@]}"; do
  if [ -f "$file" ]; then
    echo "Processing $file..."
    # Replace /api/v1/ with /v1/ for apiClient calls
    sed -i '' "s|apiClient\.\(get\|post\|put\|delete\|patch\)('/api/v1/|apiClient.\1('/v1/|g" "$file"
    sed -i '' 's|apiClient\.request({[^}]*url: '\''/api/v1/|apiClient.request({url: '\''/v1/|g' "$file"
  else
    echo "File not found: $file"
  fi
done

echo "Done! All API URLs have been fixed."
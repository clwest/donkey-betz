#!/bin/bash

echo "Clearing ALL stale Redis data..."

# Clear all freelance-related keys
redis-cli --scan --pattern "freelance:*" | xargs -r redis-cli del
redis-cli --scan --pattern "task:active:*" | xargs -r redis-cli del
redis-cli --scan --pattern "agent:task:*" | xargs -r redis-cli del
redis-cli --scan --pattern "project_updates:*" | xargs -r redis-cli del
redis-cli --scan --pattern "agent:stats:*" | xargs -r redis-cli del
redis-cli --scan --pattern "agent:updates:*" | xargs -r redis-cli del
redis-cli --scan --pattern "project_execution:*" | xargs -r redis-cli del
redis-cli --scan --pattern "agent:queue:*" | xargs -r redis-cli del

# Count remaining keys
REMAINING=$(redis-cli keys "*" | wc -l)
echo "Redis data cleared. $REMAINING keys remaining."
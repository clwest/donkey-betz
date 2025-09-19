#!/bin/bash
# Build and push Docker image
echo "Building Docker image..."
docker build -t ai-project:latest .
docker tag ai-project:latest registry.digitalocean.com/donkeybetz/ai-project:latest
docker push registry.digitalocean.com/donkeybetz/ai-project:latest

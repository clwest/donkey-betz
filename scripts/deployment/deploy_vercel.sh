#!/bin/bash
# Auto-deploy to Vercel
echo "Deploying to Vercel..."
vercel --prod --token $VERCEL_TOKEN

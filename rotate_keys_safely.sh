#!/bin/bash
# Script to safely rotate API keys

echo "🔄 API Key Rotation Guide"
echo "========================="
echo ""
echo "Step 1: Rotate your keys at these URLs:"
echo "----------------------------------------"
echo "1. OpenAI: https://platform.openai.com/api-keys"
echo "2. Anthropic: https://console.anthropic.com/settings/keys"
echo "3. Google: https://console.cloud.google.com/apis/credentials"
echo "4. Groq: https://console.groq.com/keys"
echo ""
echo "Step 2: Back up your current .env (just in case):"
echo "---------------------------------------------------"
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"
echo ""
echo "Step 3: Create a new .env with placeholders:"
echo "---------------------------------------------"
cat > .env.new << 'EOF'
# IMPORTANT: Replace these with your NEW API keys
# NEVER commit real keys to version control

# Core Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys - REPLACE WITH NEW KEYS
OPENAI_API_KEY=sk-...your-new-openai-key-here
ANTHROPIC_API_KEY=sk-ant-...your-new-anthropic-key-here
GOOGLE_API_KEY=AIza...your-new-google-key-here
GROQ_API_KEY=gsk_...your-new-groq-key-here

# Add other configuration as needed from .env.example
EOF

echo "✅ New .env template created as .env.new"
echo ""
echo "Step 4: Clean git history (if keys were ever committed):"
echo "---------------------------------------------------------"
echo "Run this command to check if .env was ever in git:"
echo "  git log --all --full-history -- .env"
echo ""
echo "If it shows results, clean the history with:"
echo "  git filter-branch --index-filter 'git rm --cached --ignore-unmatch .env' HEAD"
echo ""
echo "Step 5: Set up secure key management:"
echo "--------------------------------------"
echo "Consider using one of these for production:"
echo "  - macOS Keychain (for local dev)"
echo "  - AWS Secrets Manager"
echo "  - HashiCorp Vault"
echo "  - 1Password CLI"
echo "  - Doppler"
echo ""
echo "Step 6: Update your .env file:"
echo "-------------------------------"
echo "  mv .env.new .env"
echo "  # Then edit .env and add your NEW keys"
echo ""
echo "⚠️  IMPORTANT: Never use the old keys again!"
echo "⚠️  They should be considered permanently compromised."
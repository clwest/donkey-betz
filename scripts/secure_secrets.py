#!/usr/bin/env python3
"""
Unified Donkey Betz Platform - Secure Secrets Management
This script sets up proper secrets management for production deployment.
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from pathlib import Path
import subprocess

class SecureSecretsManager:
    """Manages API keys and secrets securely for the platform."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.secrets_dir = self.project_root / 'secrets'
        self.backup_env_file = None

    def setup_directories(self):
        """Create secure directories for secrets management."""
        self.secrets_dir.mkdir(exist_ok=True, mode=0o700)

        # Create secure subdirectories
        (self.secrets_dir / 'vault').mkdir(exist_ok=True, mode=0o700)
        (self.secrets_dir / 'backup').mkdir(exist_ok=True, mode=0o700)
        (self.secrets_dir / 'production').mkdir(exist_ok=True, mode=0o700)

        print(f"✅ Created secure secrets directories in {self.secrets_dir}")

    def generate_encryption_key(self):
        """Generate a new encryption key for secrets."""
        key = Fernet.generate_key()
        key_file = self.secrets_dir / 'vault' / 'master.key'

        with open(key_file, 'wb') as f:
            f.write(key)

        # Secure the key file
        os.chmod(key_file, 0o600)

        print(f"✅ Generated master encryption key: {key_file}")
        return key

    def extract_secrets_from_backup(self):
        """Extract API keys from backup .env files."""
        secrets = {}

        # Find backup .env files
        for env_file in self.project_root.glob('.env.backup.*'):
            if 'security' in str(env_file):
                print(f"📖 Reading secrets from {env_file}")
                with open(env_file, 'r') as f:
                    content = f.read()

                # Extract actual API keys (not placeholder text)
                for line in content.split('\n'):
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        value = value.strip().strip('"').strip("'")

                        # Only store real API keys (not placeholders)
                        if (value and
                            value not in ['', 'your-key-here', 'example-key'] and
                            not value.startswith('example-') and
                            not value.startswith('your-') and
                            len(value) > 10):
                            secrets[key.strip()] = value

                self.backup_env_file = env_file
                break

        print(f"✅ Extracted {len(secrets)} API keys from backup")
        return secrets

    def encrypt_secrets(self, secrets, encryption_key):
        """Encrypt secrets using Fernet encryption."""
        fernet = Fernet(encryption_key)
        encrypted_secrets = {}

        for key, value in secrets.items():
            encrypted_value = fernet.encrypt(value.encode()).decode()
            encrypted_secrets[key] = encrypted_value

        return encrypted_secrets

    def save_encrypted_secrets(self, encrypted_secrets):
        """Save encrypted secrets to secure vault."""
        vault_file = self.secrets_dir / 'vault' / 'secrets.json'

        with open(vault_file, 'w') as f:
            json.dump(encrypted_secrets, f, indent=2)

        # Secure the vault file
        os.chmod(vault_file, 0o600)

        print(f"✅ Saved {len(encrypted_secrets)} encrypted secrets to vault")

    def create_production_env_template(self):
        """Create production environment template."""
        template = """# UNIFIED DONKEY BETZ PLATFORM - PRODUCTION CONFIGURATION
# This file references encrypted secrets from the secure vault
# Real API keys are loaded at runtime from encrypted storage

# Core Django Settings
SECRET_KEY=${VAULT_SECRET_KEY}
DEBUG=False
DJANGO_ENV=production
ALLOWED_HOSTS=${PRODUCTION_DOMAIN}

# Database Configuration
DATABASE_URL=${VAULT_DATABASE_URL}
DB_HOST=${PRODUCTION_DB_HOST}
DB_PORT=5432
DATABASE_USE_POSTGRES=True

# Redis Configuration
REDIS_URL=${VAULT_REDIS_URL}
CELERY_BROKER_URL=${VAULT_CELERY_BROKER_URL}
CELERY_RESULT_BACKEND=${VAULT_CELERY_RESULT_BACKEND}

# AI Provider API Keys (Loaded from vault)
OPENAI_API_KEY=${VAULT_OPENAI_API_KEY}
ANTHROPIC_API_KEY=${VAULT_ANTHROPIC_API_KEY}
GROQ_API_KEY=${VAULT_GROQ_API_KEY}
GOOGLE_API_KEY=${VAULT_GOOGLE_API_KEY}
STABILITY_API_KEY=${VAULT_STABILITY_API_KEY}
ELEVENLABS_API_KEY=${VAULT_ELEVENLABS_API_KEY}

# Sports & Financial APIs (Loaded from vault)
THE_ODDS_API_KEY=${VAULT_THE_ODDS_API_KEY}
SPORTRADAR_API_KEY=${VAULT_SPORTRADAR_API_KEY}
POLYGON_API_KEY=${VAULT_POLYGON_API_KEY}
SEC_API_KEY=${VAULT_SEC_API_KEY}

# Platform Configuration
PLATFORM_NAME=Unified Donkey Betz
FRONTEND_URL=${PRODUCTION_FRONTEND_URL}
BACKEND_URL=${PRODUCTION_BACKEND_URL}

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Performance & Monitoring
ENABLE_PERFORMANCE_MONITORING=True
ENABLE_DETAILED_LOGGING=True
LOG_LEVEL=INFO
"""

        prod_env_file = self.secrets_dir / 'production' / '.env.production'
        with open(prod_env_file, 'w') as f:
            f.write(template)

        print(f"✅ Created production environment template")

    def create_secrets_loader(self):
        """Create Python script to load secrets at runtime."""
        loader_script = '''#!/usr/bin/env python3
"""
Runtime secrets loader for Unified Donkey Betz Platform
Loads encrypted secrets from vault and injects into environment
"""

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet

class SecretsLoader:
    """Loads encrypted secrets at runtime."""

    def __init__(self):
        self.secrets_dir = Path(__file__).parent.parent / 'secrets'

    def load_secrets(self):
        """Load and decrypt secrets from vault."""
        # Load encryption key
        key_file = self.secrets_dir / 'vault' / 'master.key'
        if not key_file.exists():
            raise FileNotFoundError("Master encryption key not found!")

        with open(key_file, 'rb') as f:
            encryption_key = f.read()

        # Load encrypted secrets
        vault_file = self.secrets_dir / 'vault' / 'secrets.json'
        if not vault_file.exists():
            raise FileNotFoundError("Encrypted secrets vault not found!")

        with open(vault_file, 'r') as f:
            encrypted_secrets = json.load(f)

        # Decrypt and inject into environment
        fernet = Fernet(encryption_key)

        for key, encrypted_value in encrypted_secrets.items():
            try:
                decrypted_value = fernet.decrypt(encrypted_value.encode()).decode()
                os.environ[key] = decrypted_value
            except Exception as e:
                print(f"Warning: Could not decrypt {key}: {e}")

        print(f"✅ Loaded {len(encrypted_secrets)} secrets from vault")

    def get_secret(self, key, default=None):
        """Get a specific secret value."""
        return os.environ.get(key, default)

# Auto-load secrets when imported
if __name__ != "__main__":
    loader = SecretsLoader()
    loader.load_secrets()
'''

        loader_file = self.secrets_dir / 'loader.py'
        with open(loader_file, 'w') as f:
            f.write(loader_script)

        print(f"✅ Created secrets loader script")

    def create_docker_secrets_integration(self):
        """Create Docker secrets integration."""
        docker_compose_secrets = '''# Docker Compose Secrets Configuration
# Add this to your docker-compose.yml file

services:
  backend:
    # ... other configuration ...
    secrets:
      - openai_api_key
      - anthropic_api_key
      - vault_master_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_api_key
      - VAULT_MASTER_KEY_FILE=/run/secrets/vault_master_key

secrets:
  openai_api_key:
    file: ./secrets/production/openai_api_key.txt
  anthropic_api_key:
    file: ./secrets/production/anthropic_api_key.txt
  vault_master_key:
    file: ./secrets/vault/master.key
'''

        docker_file = self.secrets_dir / 'docker-compose.secrets.yml'
        with open(docker_file, 'w') as f:
            f.write(docker_compose_secrets)

        print(f"✅ Created Docker secrets configuration")

    def update_gitignore_security(self):
        """Ensure .gitignore has proper security exclusions."""
        gitignore_file = self.project_root / '.gitignore'

        security_rules = [
            "# Secrets Management - NEVER COMMIT THESE",
            "secrets/",
            "*.key",
            "*.pem",
            "*.crt",
            "vault/",
            ".env.backup.*",
            "credentials.json",
            "secrets.json",
            "master.key",
            "# API Key Files",
            "*_api_key.txt",
            "*_secret.txt",
            "*_token.txt"
        ]

        with open(gitignore_file, 'r') as f:
            content = f.read()

        # Add security rules if not present
        new_rules = []
        for rule in security_rules:
            if rule not in content:
                new_rules.append(rule)

        if new_rules:
            with open(gitignore_file, 'a') as f:
                f.write('\n\n# Enhanced Security Rules\n')
                f.write('\n'.join(new_rules))
                f.write('\n')

            print(f"✅ Added {len(new_rules)} security rules to .gitignore")
        else:
            print("✅ .gitignore already has proper security rules")

    def run_security_setup(self):
        """Run complete security setup."""
        print("🔒 Starting Unified Donkey Betz Platform Security Setup...")
        print("=" * 60)

        # Step 1: Setup directories
        self.setup_directories()

        # Step 2: Generate encryption key
        encryption_key = self.generate_encryption_key()

        # Step 3: Extract secrets from backup
        secrets = self.extract_secrets_from_backup()

        if not secrets:
            print("⚠️  No API keys found in backup files")
            print("    Please ensure you have a backup .env file with real API keys")
            return False

        # Step 4: Encrypt secrets
        encrypted_secrets = self.encrypt_secrets(secrets, encryption_key)

        # Step 5: Save encrypted secrets
        self.save_encrypted_secrets(encrypted_secrets)

        # Step 6: Create production templates
        self.create_production_env_template()

        # Step 7: Create secrets loader
        self.create_secrets_loader()

        # Step 8: Create Docker integration
        self.create_docker_secrets_integration()

        # Step 9: Update .gitignore
        self.update_gitignore_security()

        print("=" * 60)
        print("🎉 Security setup completed successfully!")
        print(f"📁 Secrets vault: {self.secrets_dir}")
        print("📋 Next steps:")
        print("   1. Test the secrets loader with: python secrets/loader.py")
        print("   2. Update Django settings to use secrets loader")
        print("   3. Deploy using production environment template")
        print("   4. Secure the master.key file in production (HSM/KMS)")

        return True

if __name__ == "__main__":
    manager = SecureSecretsManager()
    manager.run_security_setup()
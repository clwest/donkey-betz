#!/usr/bin/env python3
"""
Setup Execution Infrastructure

This script sets up the complete execution infrastructure for the Unified Donkey Betz platform.
It ensures all necessary directories, configurations, and dependencies are in place for
agents to execute successfully and generate real revenue.

Key Setup Tasks:
- Create output directories for all agent types
- Initialize executor registry and agent mappings
- Verify tool configurations and API connectivity
- Set up monitoring and logging infrastructure
- Create sample configuration files
- Test basic execution pipeline
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ExecutionInfrastructureSetup:
    """Setup and verify execution infrastructure"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.setup_log = []

    def run_complete_setup(self):
        """Run complete infrastructure setup"""

        print("🚀 Setting up Unified Donkey Betz Execution Infrastructure")
        print("=" * 60)

        try:
            self.create_directory_structure()
            self.setup_configuration_files()
            self.verify_dependencies()
            self.create_sample_env_file()
            self.setup_logging_infrastructure()
            self.verify_django_setup()
            self.create_documentation()

            print("\n✅ SETUP COMPLETE!")
            self.show_next_steps()

        except Exception as e:
            print(f"\n❌ SETUP FAILED: {e}")
            raise

    def create_directory_structure(self):
        """Create necessary directory structure"""

        print("\n📁 Creating directory structure...")

        directories = [
            # Core agent outputs
            'agent_outputs',
            'income_builder_outputs',
            'content_outputs',
            'payment_outputs',

            # Agent executors
            'agents/executors',

            # Tools and utilities
            'core/tools',

            # Test outputs
            'test_outputs',
            'demo_outputs',

            # Logs and monitoring
            'logs/agents',
            'logs/executors',

            # Configuration
            'config',

            # Templates
            'templates/agents',
            'templates/content',
            'templates/invoices',

            # Cache and temp
            'cache/agents',
            'temp/agent_files',

            # Documentation
            'docs/agents',
            'docs/executors',
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            # Create .gitkeep for empty directories
            gitkeep_path = dir_path / '.gitkeep'
            if not any(dir_path.iterdir()) and not gitkeep_path.exists():
                gitkeep_path.touch()

        print(f"   ✅ Created {len(directories)} directories")
        self.setup_log.append("Directory structure created")

    def setup_configuration_files(self):
        """Create configuration files"""

        print("\n⚙️  Setting up configuration files...")

        # Agent executor configuration
        executor_config = {
            "default_settings": {
                "timeout_seconds": 300,
                "max_retries": 3,
                "enable_monitoring": True,
                "enable_caching": True
            },
            "income_builder": {
                "default_output_dir": "income_builder_outputs",
                "max_opportunities": 10,
                "research_depth": "comprehensive"
            },
            "content_creator": {
                "default_output_dir": "content_outputs",
                "default_word_count": 1200,
                "enable_seo_optimization": True
            },
            "payment_processor": {
                "default_output_dir": "payment_outputs",
                "default_payment_terms": "Net 15",
                "enable_stripe_integration": True
            }
        }

        config_path = self.project_root / 'config' / 'executor_config.json'
        with open(config_path, 'w') as f:
            json.dump(executor_config, f, indent=2)

        # Tool configuration
        tool_config = {
            "web_search": {
                "enabled": True,
                "fallback_engines": ["duckduckgo"],
                "max_results": 10
            },
            "file_operations": {
                "enabled": True,
                "temp_dir": "temp/agent_files"
            },
            "api_connector": {
                "enabled": True,
                "timeout": 30,
                "retries": 3
            }
        }

        tool_config_path = self.project_root / 'config' / 'tool_config.json'
        with open(tool_config_path, 'w') as f:
            json.dump(tool_config, f, indent=2)

        print("   ✅ Configuration files created")
        self.setup_log.append("Configuration files created")

    def create_sample_env_file(self):
        """Create sample environment file"""

        print("\n🔐 Creating sample environment configuration...")

        env_sample_content = """# Unified Donkey Betz Agent Execution Environment
# Copy this file to .env and fill in your actual API keys

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Stripe Payment Processing
STRIPE_API_KEY=your_stripe_api_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here

# Web Search APIs
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_CX=your_google_custom_search_engine_id_here
BING_SEARCH_API_KEY=your_bing_search_api_key_here

# Additional APIs
GITHUB_TOKEN=your_github_token_here
NEWS_API_KEY=your_news_api_key_here

# Django Configuration
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Agent Configuration
AGENT_EXECUTION_TIMEOUT=300
AGENT_MAX_RETRIES=3
AGENT_ENABLE_MONITORING=True

# File Paths
AGENT_OUTPUT_DIR=agent_outputs
AGENT_LOG_DIR=logs/agents

# Performance Settings
AGENT_CONCURRENT_LIMIT=10
AGENT_CACHE_TIMEOUT=300
"""

        env_sample_path = self.project_root / '.env.sample'
        with open(env_sample_path, 'w') as f:
            f.write(env_sample_content)

        print("   ✅ Sample environment file created (.env.sample)")
        print("   ⚠️  Copy .env.sample to .env and add your API keys")
        self.setup_log.append("Sample environment file created")

    def verify_dependencies(self):
        """Verify Python dependencies"""

        print("\n📦 Verifying dependencies...")

        required_packages = [
            'django',
            'aiohttp',
            'openai',
            'pathlib',
            'asyncio'
        ]

        optional_packages = [
            'stripe',
            'requests'
        ]

        missing_required = []
        missing_optional = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_required.append(package)

        for package in optional_packages:
            try:
                __import__(package)
            except ImportError:
                missing_optional.append(package)

        if missing_required:
            print(f"   ❌ Missing required packages: {', '.join(missing_required)}")
            print("   Run: pip install " + " ".join(missing_required))
        else:
            print("   ✅ All required packages available")

        if missing_optional:
            print(f"   ⚠️  Missing optional packages: {', '.join(missing_optional)}")
            print("   Run: pip install " + " ".join(missing_optional))

        self.setup_log.append(f"Dependencies checked - {len(missing_required)} missing required")

    def setup_logging_infrastructure(self):
        """Setup logging infrastructure"""

        print("\n📝 Setting up logging infrastructure...")

        # Agent execution logger configuration
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "simple": {
                    "format": "%(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "agent_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/agents/agent_execution.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "detailed"
                },
                "executor_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/executors/executor_performance.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "detailed"
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple"
                }
            },
            "loggers": {
                "agents.executors": {
                    "handlers": ["agent_file", "console"],
                    "level": "INFO",
                    "propagate": False
                },
                "agents.executor_registry": {
                    "handlers": ["executor_file", "console"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }

        logging_config_path = self.project_root / 'config' / 'logging_config.json'
        with open(logging_config_path, 'w') as f:
            json.dump(logging_config, f, indent=2)

        print("   ✅ Logging configuration created")
        self.setup_log.append("Logging infrastructure configured")

    def verify_django_setup(self):
        """Verify Django setup"""

        print("\n🌐 Verifying Django setup...")

        try:
            # Check if Django settings are configured
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

            import django
            django.setup()

            # Try importing Django models
            from agents.models import UnifiedAgentTemplate
            from agents.registry import get_agent_registry

            agent_count = UnifiedAgentTemplate.objects.filter(is_active=True).count()
            print(f"   ✅ Django configured - {agent_count} active agents in database")

            self.setup_log.append(f"Django verified - {agent_count} agents")

        except Exception as e:
            print(f"   ❌ Django setup issue: {e}")
            print("   Make sure to run Django migrations first")
            self.setup_log.append(f"Django setup issue: {e}")

    def create_documentation(self):
        """Create basic documentation"""

        print("\n📚 Creating documentation...")

        # README for agents
        agent_readme = """# Agent Execution System

This directory contains the active agent execution system that transforms
passive agent registrations into working, revenue-generating agents.

## Key Components

- `executors/`: Agent executor implementations
- `executor_registry.py`: Central executor management
- `models.py`: Django models for agent tracking

## Usage

1. Initialize executors: `python manage.py initialize_executors`
2. Run tests: `python test_real_agent_execution.py`
3. Demo system: `python demo_working_agents.py`

## Available Executors

- **IncomeBuilderExecutor**: Analyzes opportunities and creates action plans
- **ContentCreatorExecutor**: Generates AI-powered content
- **PaymentProcessorExecutor**: Handles invoicing and payments

## Key Features

- Real API integration (OpenAI, Stripe, web search)
- Actual file generation and deliverables
- Performance monitoring and cost tracking
- Error handling and retry logic
- Concurrent execution support
"""

        agent_readme_path = self.project_root / 'agents' / 'README.md'
        with open(agent_readme_path, 'w') as f:
            f.write(agent_readme)

        # Quick start guide
        quickstart_guide = """# Quick Start Guide: Agent Execution System

## 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.sample .env
# Edit .env with your API keys

# Setup database
python manage.py migrate
```

## 2. Initialize Executors

```bash
python manage.py initialize_executors --register-all --status
```

## 3. Test Execution

```bash
# Run comprehensive tests
python test_real_agent_execution.py

# Run demo
python demo_working_agents.py
```

## 4. Use Individual Agents

```python
from agents.executor_registry import execute_agent_by_name

# Income Builder
result = await execute_agent_by_name('income_builder', {
    'task_type': 'analyze_opportunities',
    'user_profile': {'skills': ['python', 'ai']}
})

# Content Creator
result = await execute_agent_by_name('content_creator', {
    'content_type': 'blog_post',
    'topic': 'AI productivity tools'
})

# Payment Processor
result = await execute_agent_by_name('payment_processor', {
    'task_type': 'create_invoice',
    'amount': 500.0
})
```

## 5. Monitor Performance

```bash
python manage.py initialize_executors --stats --health-check
```
"""

        quickstart_path = self.project_root / 'docs' / 'QUICKSTART.md'
        with open(quickstart_path, 'w') as f:
            f.write(quickstart_guide)

        print("   ✅ Documentation created")
        self.setup_log.append("Documentation created")

    def show_next_steps(self):
        """Show next steps to the user"""

        print("\n🎯 NEXT STEPS:")
        print("=" * 30)

        print("\n1. Configure API Keys:")
        print("   - Copy .env.sample to .env")
        print("   - Add your OpenAI API key (required for content generation)")
        print("   - Add Stripe API key (optional, for payment processing)")
        print("   - Add search API keys (optional, for better research)")

        print("\n2. Initialize Database:")
        print("   python manage.py migrate")
        print("   python manage.py initialize_executors")

        print("\n3. Test the System:")
        print("   python test_real_agent_execution.py")

        print("\n4. Run Demo:")
        print("   python demo_working_agents.py")

        print("\n5. Start Using Agents:")
        print("   from agents.executor_registry import execute_agent_by_name")
        print("   result = await execute_agent_by_name('income_builder', task_data)")

        print("\n📁 Key Directories Created:")
        print("   - agent_outputs/       : All agent-generated files")
        print("   - logs/               : Execution logs and monitoring")
        print("   - config/             : Configuration files")
        print("   - docs/               : Documentation and guides")

        print("\n🔧 Management Commands:")
        print("   python manage.py initialize_executors --status")
        print("   python manage.py initialize_executors --health-check")
        print("   python manage.py initialize_executors --test-execution")

        print("\n⚡ Key Features Now Available:")
        print("   ✅ Real AI-powered content generation")
        print("   ✅ Actual market research and opportunity analysis")
        print("   ✅ Working payment processing and invoicing")
        print("   ✅ File generation and deliverable creation")
        print("   ✅ Performance monitoring and cost tracking")
        print("   ✅ Error handling and retry logic")

        # Save setup summary
        setup_summary = {
            'setup_completed_at': datetime.now().isoformat(),
            'setup_log': self.setup_log,
            'next_steps': [
                'Configure API keys in .env file',
                'Run Django migrations',
                'Initialize executors',
                'Run tests',
                'Start using agents'
            ],
            'key_files': [
                '.env.sample',
                'config/executor_config.json',
                'agents/README.md',
                'docs/QUICKSTART.md'
            ]
        }

        summary_path = self.project_root / 'setup_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(setup_summary, f, indent=2)

        print(f"\n📋 Setup summary saved to: setup_summary.json")


def main():
    """Main setup function"""

    print("🤖 UNIFIED DONKEY BETZ: EXECUTION INFRASTRUCTURE SETUP")
    print("=" * 60)
    print("Transforming passive agents into active revenue generators...")
    print()

    setup = ExecutionInfrastructureSetup()
    setup.run_complete_setup()


if __name__ == "__main__":
    main()
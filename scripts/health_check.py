#!/usr/bin/env python
"""
System Health Check for Claude Sessions
========================================

Run at the start of any session to verify system state:
    python scripts/health_check.py

Or via make:
    make health-check

Created: Session 391 (Technical Debt Remediation Planning)
"""
import os
import sys
from pathlib import Path

# Add project root to path (for running from scripts/ directory)
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

# Setup Django before imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

def setup_django():
    """Initialize Django."""
    import django
    django.setup()


def check_agents():
    """Verify agent system is healthy."""
    try:
        from core.agent_router import AgentRouter
        router = AgentRouter()
        count = len(router.AGENT_MAP)
        print(f"  ✓ AgentRouter: {count} agents registered")

        # List agent categories
        categories = {
            'Creation': ['ImageAgent', 'VideoAgent', 'AudioAgent', 'ThreeDAgent'],
            'Editing': ['ImageEditingAgent', 'VideoEditingAgent'],
            'Research': ['ResearchAgent'],
            'Strategy': ['ContentStrategyAgent', 'BrandIdentityAgent', 'SEOOptimizerAgent', 'SocialMediaAgent'],
            'Executive': ['CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'MeetingCoordinatorAgent'],
            'Business': ['CompetitorAnalysisAgent', 'CustomerResearchAgent'],
        }

        missing = []
        for category, agents in categories.items():
            for agent in agents:
                if agent not in router.AGENT_MAP:
                    missing.append(agent)

        if missing:
            print(f"  ⚠ Missing agents: {', '.join(missing)}")
            return False

        return count >= 20
    except Exception as e:
        print(f"  ✗ AgentRouter: {e}")
        return False


def check_spiders():
    """Verify spider registry."""
    try:
        from ai_core.spiders.spider_registry import SpiderRegistry
        registry = SpiderRegistry()
        stats = registry.get_spider_count()
        total = stats.get('total', 0)
        print(f"  ✓ SpiderRegistry: {total} spiders across {stats.get('categories', 0)} categories")
        return total >= 100
    except Exception as e:
        print(f"  ✗ SpiderRegistry: {e}")
        return False


def check_database():
    """Verify database connection and key tables."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Check key tables exist
        from core.models_unified_system import Agent, SpiderData
        from content.models import ImageHistory

        agent_count = Agent.objects.filter(is_active=True).count()
        spider_data_count = SpiderData.objects.count()
        image_count = ImageHistory.objects.count()

        print(f"  ✓ Database: Connected")
        print(f"    - {agent_count} active agents")
        print(f"    - {spider_data_count} spider data entries")
        print(f"    - {image_count} images in history")
        return True
    except Exception as e:
        print(f"  ✗ Database: {e}")
        return False


def check_redis():
    """Verify Redis connection."""
    try:
        import redis
        from django.conf import settings

        redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        print(f"  ✓ Redis: Connected")
        return True
    except Exception as e:
        print(f"  ⚠ Redis: {e} (non-critical)")
        return True  # Non-critical for basic operation


def check_api_keys():
    """Verify API keys are configured (not their validity)."""
    from django.conf import settings

    keys = {
        'OPENAI_API_KEY': getattr(settings, 'OPENAI_API_KEY', ''),
        'STABILITY_API_KEY': getattr(settings, 'STABILITY_API_KEY', ''),
    }

    configured = []
    missing = []

    for name, value in keys.items():
        if value and len(value) > 10:
            configured.append(name)
        else:
            missing.append(name)

    print(f"  ✓ API Keys: {len(configured)} configured")
    if missing:
        print(f"    - Missing: {', '.join(missing)}")

    return len(configured) >= 1  # At least OpenAI should be configured


def check_file_sizes():
    """Check for concerning file sizes."""
    import pathlib

    large_files = []
    thresholds = {
        'ai_core/templates/ai_image_studio.html': 70000,
        'core/views_image.py': 15000,
        'core/views_video.py': 10000,
        'core/models_unified_system.py': 15000,
    }

    base = pathlib.Path('.')
    for filepath, max_lines in thresholds.items():
        full_path = base / filepath
        if full_path.exists():
            lines = len(full_path.read_text().splitlines())
            if lines > max_lines:
                large_files.append((filepath, lines))

    if large_files:
        print(f"  ⚠ Large files detected (technical debt):")
        for filepath, lines in large_files:
            print(f"    - {filepath}: {lines:,} lines")
    else:
        print(f"  ✓ File sizes: All within thresholds")

    return True  # Informational only


def check_agent_migration():
    """Check if legacy agents/ still exists."""
    import pathlib

    legacy_path = pathlib.Path('agents')
    clean_path = pathlib.Path('core/agents')

    if legacy_path.exists() and clean_path.exists():
        legacy_files = len(list(legacy_path.glob('*.py')))
        clean_files = len(list(clean_path.glob('*.py'))) + len(list(clean_path.glob('**/*.py')))
        print(f"  ⚠ Two agent systems exist (migration incomplete):")
        print(f"    - agents/ (legacy): {legacy_files} files")
        print(f"    - core/agents/ (clean): {clean_files} files")
        return True  # Informational
    elif clean_path.exists():
        print(f"  ✓ Agent system: Unified in core/agents/")

    return True


def main():
    """Run all health checks."""
    print("=" * 50)
    print("  SYSTEM HEALTH CHECK")
    print("  Session 391+ Technical Debt Monitoring")
    print("=" * 50)
    print()

    setup_django()

    checks = [
        ("Agent System", check_agents),
        ("Spider Network", check_spiders),
        ("Database", check_database),
        ("Redis", check_redis),
        ("API Keys", check_api_keys),
        ("Agent Migration", check_agent_migration),
        ("File Sizes", check_file_sizes),
    ]

    results = []
    for name, check_fn in checks:
        print(f"\n[{name}]")
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    passed = sum(1 for _, r in results if r)
    total = len(results)

    if passed == total:
        print(f"  ✓ ALL CHECKS PASSED ({passed}/{total})")
    else:
        print(f"  ⚠ {passed}/{total} checks passed")
        failed = [name for name, r in results if not r]
        print(f"  Failed: {', '.join(failed)}")

    print("=" * 50)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

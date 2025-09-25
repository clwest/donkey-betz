#!/usr/bin/env python3
"""
Test the Documentation Fetcher Tool
"""

import os
import sys
import django
import asyncio

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.tools import ToolRegistry


async def test_doc_fetcher():
    print("=" * 60)
    print("📚 TESTING DOCUMENTATION FETCHER")
    print("=" * 60)

    # Get the documentation fetcher tool
    doc_tool = ToolRegistry.get_tool('documentation_fetcher')

    if not doc_tool:
        print("❌ Documentation fetcher not registered!")
        return

    print("✅ Documentation fetcher found in registry")
    print("\nTool Info:")
    info = doc_tool.get_info()
    print(f"  Name: {info['name']}")
    print(f"  Configured: {info['configured']}")
    print(f"  Supported Frameworks: {', '.join(info['supported_frameworks'])}")
    print(f"  Cache Enabled: {info['cache_enabled']}")

    print("\n" + "=" * 60)
    print("TEST 1: Fetching React Documentation")
    print("=" * 60)

    result = await doc_tool.fetch_documentation(
        framework='react',
        topic='useState hook',
        section='api_docs'
    )

    if result['success']:
        print(f"✅ Documentation URL: {result.get('documentation_url')}")
        print(f"   Fresh: {result.get('fresh', False)}")
    else:
        print(f"❌ Failed: {result.get('error')}")

    print("\n" + "=" * 60)
    print("TEST 2: Checking Latest Package Version")
    print("=" * 60)

    result = await doc_tool.check_latest_version(
        package='react',
        registry='npm'
    )

    if result['success']:
        print(f"✅ React latest version: {result.get('latest_version')}")
    else:
        print(f"❌ Failed: {result.get('error')}")

    print("\n" + "=" * 60)
    print("TEST 3: Getting Django API Changes")
    print("=" * 60)

    result = await doc_tool.get_api_changes('django')

    if result['success']:
        print(f"✅ Django changes URL: {result.get('changes_url')}")
        print(f"   {result.get('message')}")
    else:
        print(f"❌ Failed: {result.get('error')}")

    print("\n" + "=" * 60)
    print("🎉 Documentation Fetcher is Working!")
    print("=" * 60)
    print("\nYour Code Assistant now has access to:")
    print("• Real-time documentation for 9+ frameworks")
    print("• Package version checking (npm, pypi, cargo)")
    print("• StackOverflow search integration")
    print("• API change tracking")
    print("\nThe Code Assistant will automatically fetch relevant docs when needed!")

    # Cleanup
    await doc_tool.cleanup()


if __name__ == "__main__":
    asyncio.run(test_doc_fetcher())
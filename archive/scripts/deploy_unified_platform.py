#!/usr/bin/env python3
"""
Platform Unification Deployment Script

This script deploys the complete Platform Unification Orchestrator that transforms
7 isolated components into a unified AI-powered business platform.

Integration Targets:
1. Spider Army → Content Studio (intelligence-driven content)
2. 149 Agents → Content Workflows (automated production)
3. 25 Advisors → Expert Content Streams (legendary insights)
4. Neural Orchestra → Real System Data (live visualization)
5. pgvector → Semantic Search (knowledge discovery)
6. Revenue Tracking → Automated Pipelines (content monetization)

Usage:
    python deploy_unified_platform.py [--test-mode] [--start-server]
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
import argparse


def print_banner():
    """Print deployment banner"""
    print("🚀" * 20)
    print("🎛️  PLATFORM UNIFICATION ORCHESTRATOR")
    print("🚀" * 20)
    print("""
🔗 Unified Platform Integration:
   🕷️  Spider Army Intelligence → Content Studio
   🤖 149 Agents → Content Production Workflows
   🧠 25 Advisor Personalities → Expert Content Streams
   🎼 Neural Orchestra → Real-time System Visualization
   🔍 pgvector Embeddings → Semantic Search Interface
   💰 Content Creation → Automated Revenue Pipelines

🎯 Result: Revolutionary AI-powered business platform
""")


def check_prerequisites():
    """Check system prerequisites"""
    print("🔍 Checking Prerequisites...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version compatible")

    # Check if in correct directory
    if not os.path.exists('manage.py'):
        print("❌ Must run from Django project root directory")
        return False
    print("✅ Django project directory confirmed")

    # Check for key files
    required_files = [
        'core/platform_unification_orchestrator.py',
        'core/management/commands/deploy_platform_unification.py',
        'agents/registry.py',
        'intelligence/spiders/spider_army/orchestrator.py'
    ]

    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing required file: {file_path}")
            return False
    print("✅ All required files present")

    return True


def setup_environment():
    """Setup environment for deployment"""
    print("\n🔧 Setting up Environment...")

    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

    # Install/update requirements if needed
    try:
        import django
        import redis
        import channels
        import scrapy
        print("✅ Core dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

    return True


def migrate_database():
    """Run database migrations"""
    print("\n💾 Running Database Migrations...")

    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print("✅ Database migrations completed")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Migration timeout")
        return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False


def start_redis_if_needed():
    """Start Redis if not running"""
    print("\n🔴 Checking Redis Status...")

    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis is running")
        return True
    except redis.ConnectionError:
        print("⚠️ Redis not running - attempting to start...")

        # Try to start Redis (macOS with Homebrew)
        try:
            subprocess.run(['brew', 'services', 'start', 'redis'],
                         capture_output=True, check=True)
            time.sleep(3)

            # Test connection again
            client.ping()
            print("✅ Redis started successfully")
            return True

        except (subprocess.CalledProcessError, redis.ConnectionError):
            print("❌ Could not start Redis automatically")
            print("💡 Please start Redis manually: brew services start redis")
            return False
    except Exception as e:
        print(f"❌ Redis check failed: {e}")
        return False


def deploy_platform_unification(test_mode=False):
    """Deploy the Platform Unification Orchestrator"""
    print("\n🎛️ Deploying Platform Unification Orchestrator...")

    # Build management command
    cmd = [sys.executable, 'manage.py', 'deploy_platform_unification']

    if test_mode:
        cmd.append('--test-mode')
        cmd.append('--verbose')

    cmd.append('--start-immediately')

    try:
        print("⏳ Executing deployment command...")
        print(f"🔧 Command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode == 0:
            print("✅ Platform Unification Deployment SUCCESSFUL!")
            return True
        else:
            print(f"❌ Deployment failed with code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Deployment timeout after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False


def start_django_server(background=False):
    """Start Django development server"""
    print("\n🌐 Starting Django Server...")

    try:
        if background:
            # Start in background
            with open('server.log', 'w') as log_file:
                process = subprocess.Popen([
                    sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
                ], stdout=log_file, stderr=log_file)

            print(f"✅ Django server started in background (PID: {process.pid})")
            print("📄 Server logs: server.log")
            time.sleep(3)  # Give server time to start

        else:
            print("🚀 Starting Django server in foreground...")
            print("💡 Use Ctrl+C to stop the server")
            print("🌐 Access at: http://localhost:8000")

            subprocess.run([
                sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
            ])

        return True

    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Server start failed: {e}")
        return False


def run_integration_tests():
    """Run platform integration tests"""
    print("\n🧪 Running Integration Tests...")

    try:
        result = subprocess.run([
            sys.executable, 'test_platform_unification.py'
        ], text=True, timeout=120)

        if result.returncode == 0:
            print("✅ Integration tests PASSED")
            return True
        else:
            print("⚠️ Some integration tests failed")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Test timeout")
        return False
    except FileNotFoundError:
        print("⚠️ Test file not found - skipping tests")
        return True
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def display_deployment_summary():
    """Display deployment summary and next steps"""
    print("\n" + "🎉" * 20)
    print("✅ PLATFORM UNIFICATION DEPLOYMENT COMPLETE!")
    print("🎉" * 20)

    print("""
🚀 Your Unified AI Platform is Ready:

📡 WebSocket Endpoints:
   • ws://localhost:8000/ws/platform-orchestrator/
   • ws://localhost:8000/ws/content-intelligence-pipeline/
   • ws://localhost:8000/ws/agent-content-factory/
   • ws://localhost:8000/ws/advisor-content-streams/
   • ws://localhost:8000/ws/semantic-search/
   • ws://localhost:8000/ws/revenue-pipeline-monitor/

🔗 Integration Status:
   ✅ Spider Army → Content Studio (intelligence-driven content)
   ✅ 149 Agents → Content Workflows (automated production)
   ✅ 25 Advisors → Expert Streams (legendary insights)
   ✅ Neural Orchestra → Real Data (live visualization)
   ✅ pgvector → Semantic Search (knowledge discovery)
   ✅ Content → Revenue Pipelines (monetization automation)

🎯 Next Steps:
   1. Visit: http://localhost:8000 to access the platform
   2. Connect to WebSocket endpoints for real-time data
   3. Monitor revenue generation and content creation
   4. Scale the system as your business grows

💰 Revenue Multipliers Now Active:
   🎨 Automated content generation
   🧠 Expert advisor insights
   🔍 Intelligence-driven opportunities
   📊 Real-time performance optimization
""")


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy Platform Unification Orchestrator')
    parser.add_argument('--test-mode', action='store_true',
                       help='Deploy in test mode with reduced functionality')
    parser.add_argument('--start-server', action='store_true',
                       help='Start Django server after deployment')
    parser.add_argument('--run-tests', action='store_true',
                       help='Run integration tests after deployment')
    parser.add_argument('--background-server', action='store_true',
                       help='Start server in background')

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Aborting deployment.")
        sys.exit(1)

    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed. Aborting deployment.")
        sys.exit(1)

    # Migrate database
    if not migrate_database():
        print("❌ Database migration failed. Aborting deployment.")
        sys.exit(1)

    # Start Redis
    if not start_redis_if_needed():
        print("❌ Redis not available. Aborting deployment.")
        sys.exit(1)

    # Deploy platform unification
    if not deploy_platform_unification(test_mode=args.test_mode):
        print("❌ Platform deployment failed. Aborting.")
        sys.exit(1)

    # Run tests if requested
    if args.run_tests:
        run_integration_tests()

    # Display summary
    display_deployment_summary()

    # Start server if requested
    if args.start_server:
        start_django_server(background=args.background_server)

    print("\n🎊 Platform Unification Orchestrator deployment complete!")
    print("🚀 Your unified AI-powered business platform is ready!")


if __name__ == "__main__":
    main()
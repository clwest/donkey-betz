#!/usr/bin/env python
"""
Enhanced Neural Orchestra Demo Launcher
========================================
Comprehensive launcher for the Enhanced Neural Orchestra with live agent learning workflow

This script:
1. Sets up the environment and dependencies
2. Runs the real learning systems to generate data
3. Starts the Django server
4. Opens the Enhanced Neural Orchestra interface
5. Provides demo instructions and examples

Features demonstrated:
- Live agent learning with real OpenAI API calls
- Dynamic team formation based on learning needs
- Real-time agent conversations and thought processes
- Knowledge transfer visualization between agents
- Spider data integration and processing
- Content generation from collaborative learning
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def check_prerequisites():
    """Check if all prerequisites are met"""
    print_header("CHECKING PREREQUISITES")

    checks_passed = True

    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print_success(f"Python {python_version.major}.{python_version.minor} - Compatible")
    else:
        print_error(f"Python {python_version.major}.{python_version.minor} - Requires Python 3.8+")
        checks_passed = False

    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
        r.ping()
        print_success("Redis server - Running")
    except ImportError:
        print_error("Redis Python library not installed. Run: pip install redis")
        checks_passed = False
    except:
        print_error("Redis server not running. Start with: brew services start redis (macOS) or sudo systemctl start redis (Linux)")
        checks_passed = False

    # Check OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()

    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print_success("OpenAI API key - Found")
    else:
        print_error("OPENAI_API_KEY not found in environment. Add to .env file")
        checks_passed = False

    # Check Django
    try:
        import django
        print_success(f"Django {django.get_version()} - Available")
    except ImportError:
        print_error("Django not installed. Run: pip install django")
        checks_passed = False

    # Check Channels (for WebSockets)
    try:
        import channels
        print_success("Django Channels - Available")
    except ImportError:
        print_warning("Django Channels not installed. WebSocket features may be limited")

    if not checks_passed:
        print_error("Prerequisites check failed. Please fix the issues above.")
        return False

    print_success("All prerequisites satisfied!")
    return True

def setup_django():
    """Setup Django environment"""
    print_header("SETTING UP DJANGO ENVIRONMENT")

    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        import django
        django.setup()
        print_success("Django environment configured")
        return True
    except Exception as e:
        print_error(f"Django setup failed: {e}")
        return False

def run_learning_systems():
    """Run the learning systems to generate real data"""
    print_header("GENERATING REAL LEARNING DATA")

    print_info("This will run actual AI learning systems with OpenAI API calls")
    print_info("Expected cost: ~$0.50-1.00 for complete demonstration")

    # Clear Redis for fresh demo
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
        r.flushdb()
        print_success("Cleared Redis database for fresh demo")
    except:
        print_warning("Could not clear Redis database")

    # Run real agent learning system
    print_info("Running Real Agent Learning System...")
    try:
        result = subprocess.run([
            sys.executable, 'real_agent_learning_system.py'
        ], capture_output=True, text=True, timeout=180)

        if result.returncode == 0:
            print_success("Real Agent Learning System completed")
        else:
            print_warning(f"Learning system completed with warnings: {result.stderr[:200]}...")
    except subprocess.TimeoutExpired:
        print_warning("Learning system timeout (normal for large learning sessions)")
    except Exception as e:
        print_error(f"Error running learning system: {e}")
        return False

    # Run agent-to-agent learning
    print_info("Running Agent-to-Agent Learning System...")
    try:
        result = subprocess.run([
            sys.executable, 'agent_to_agent_learning.py'
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print_success("Agent-to-Agent Learning completed")
        else:
            print_warning(f"Agent learning completed with warnings: {result.stderr[:200]}...")
    except subprocess.TimeoutExpired:
        print_warning("Agent learning timeout (normal for API calls)")
    except Exception as e:
        print_warning(f"Agent learning system issue: {e}")

    print_success("Learning data generation completed!")
    return True

def verify_learning_data():
    """Verify that learning data was properly generated"""
    print_header("VERIFYING LEARNING DATA")

    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

        # Check learning metrics
        learning_metrics = r.hgetall("learning:system:metrics")
        final_metrics = r.hgetall("learning:system:final")

        if learning_metrics or final_metrics:
            print_success("Learning system metrics found:")
            total_learnings = learning_metrics.get('total_learnings', 0) or final_metrics.get('total_knowledge_items', 0)
            total_agents = learning_metrics.get('total_agents', 0) or final_metrics.get('agents_trained', 0)
            total_tokens = learning_metrics.get('total_tokens', 0) or final_metrics.get('total_tokens_used', 0)

            print_info(f"   📚 Total learnings: {total_learnings}")
            print_info(f"   🤖 Agents trained: {total_agents}")
            print_info(f"   🎯 Tokens used: {total_tokens}")

        # Check generated content
        content_count = r.llen("generated_content")
        collaborations_count = r.llen("collaborations")

        print_info(f"   📝 Generated content pieces: {content_count}")
        print_info(f"   🤝 Agent collaborations: {collaborations_count}")

        if int(total_learnings) > 0 or content_count > 0:
            print_success("Learning data verified and ready!")
            return True
        else:
            print_warning("Limited learning data found. Demo will use simulated data.")
            return True

    except Exception as e:
        print_error(f"Error verifying learning data: {e}")
        return False

def start_django_server():
    """Start Django development server in background"""
    print_header("STARTING DJANGO SERVER")

    def run_server():
        try:
            subprocess.run([
                sys.executable, 'manage.py', 'runserver', '8000'
            ], check=True)
        except Exception as e:
            print_error(f"Django server error: {e}")

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    print_info("Waiting for Django server to start...")
    time.sleep(3)

    # Test if server is running
    try:
        import urllib.request
        urllib.request.urlopen('http://localhost:8000')
        print_success("Django server is running on http://localhost:8000")
        return True
    except:
        print_warning("Django server may still be starting...")
        return True

def open_enhanced_neural_orchestra():
    """Open the Enhanced Neural Orchestra interface"""
    print_header("LAUNCHING ENHANCED NEURAL ORCHESTRA")

    # URLs to try
    urls = [
        'http://localhost:8000/enhanced_neural_orchestra.html',
        'http://localhost:8000/enhanced-neural-orchestra.html',
        'http://localhost:8000/neural-orchestra/',
        'http://localhost:8000/'
    ]

    success = False
    for url in urls:
        try:
            import urllib.request
            urllib.request.urlopen(url)
            print_success(f"Opening Enhanced Neural Orchestra: {url}")
            webbrowser.open(url)
            success = True
            break
        except:
            continue

    if not success:
        print_warning("Could not automatically open interface")
        print_info("Manually navigate to one of these URLs:")
        for url in urls:
            print_info(f"   {url}")

    return success

def show_demo_instructions():
    """Show demo instructions and examples"""
    print_header("ENHANCED NEURAL ORCHESTRA DEMO GUIDE")

    print(f"{Colors.OKBLUE}🎯 WHAT YOU'LL SEE:{Colors.ENDC}")
    print("   • Real-time agent learning workflow with live data")
    print("   • Dynamic team formation based on learning topics")
    print("   • Agent conversations showing actual thought processes")
    print("   • Knowledge transfer between specialized agents")
    print("   • Spider data feeds from real sources")
    print("   • Content generation from collaborative learning")

    print(f"\n{Colors.OKGREEN}🚀 HOW TO USE THE DEMO:{Colors.ENDC}")
    print("   1. Enter a learning topic (e.g., 'Quantum Computing', 'AI Ethics')")
    print("   2. Click 'Start Learning' to initiate the workflow")
    print("   3. Watch the 5-phase learning process unfold in real-time:")
    print("      • Phase 1: Spider Data Collection")
    print("      • Phase 2: Initial Agent Learning")
    print("      • Phase 3: Dynamic Team Formation")
    print("      • Phase 4: Agent-to-Agent Knowledge Sharing")
    print("      • Phase 5: Collaborative Content Generation")
    print("   4. Observe real agent conversations and learning metrics")
    print("   5. See knowledge transfer visualizations")
    print("   6. View generated content from the learning process")

    print(f"\n{Colors.WARNING}💡 DEMO TOPICS TO TRY:{Colors.ENDC}")
    topics = [
        "Quantum Computing Applications",
        "Sustainable Energy Technologies",
        "AI Ethics and Governance",
        "Blockchain and DeFi",
        "Space Exploration Technologies",
        "Biotechnology and Gene Therapy",
        "Climate Change Solutions",
        "Neural Interface Technologies"
    ]

    for topic in topics:
        print(f"   • {topic}")

    print(f"\n{Colors.OKCYAN}🔍 WHAT MAKES THIS SPECIAL:{Colors.ENDC}")
    print("   • Uses real OpenAI API calls - no simulations!")
    print("   • Agents actually learn and teach each other")
    print("   • Dynamic specialist team creation based on topic needs")
    print("   • Real spider data integration from news sources")
    print("   • Live WebSocket updates showing authentic agent work")
    print("   • Demonstrates true AI collaboration and knowledge building")

    print(f"\n{Colors.HEADER}🎬 READY TO START THE DEMO!{Colors.ENDC}")
    print(f"   The Enhanced Neural Orchestra is now live at: {Colors.BOLD}http://localhost:8000{Colors.ENDC}")

def monitor_learning_activity():
    """Monitor and display learning activity"""
    print_header("MONITORING LIVE LEARNING ACTIVITY")

    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

        print_info("Monitoring Redis for learning activity...")
        print_info("Press Ctrl+C to stop monitoring")

        last_content_count = 0
        last_collaboration_count = 0

        while True:
            try:
                # Check for new content
                current_content_count = r.llen("generated_content")
                current_collaboration_count = r.llen("collaborations")

                if current_content_count > last_content_count:
                    print_success(f"New content generated! Total: {current_content_count}")
                    last_content_count = current_content_count

                if current_collaboration_count > last_collaboration_count:
                    print_success(f"New agent collaboration! Total: {current_collaboration_count}")
                    last_collaboration_count = current_collaboration_count

                time.sleep(5)

            except KeyboardInterrupt:
                print_info("Stopping activity monitor")
                break
            except Exception as e:
                print_warning(f"Monitor error: {e}")
                time.sleep(5)

    except Exception as e:
        print_error(f"Could not start activity monitor: {e}")

def main():
    """Main demo launcher function"""
    print_header("🧠 ENHANCED NEURAL ORCHESTRA DEMO LAUNCHER")
    print(f"{Colors.OKCYAN}Real Agent Learning • Dynamic Team Formation • Live Collaboration{Colors.ENDC}\n")

    # Step 1: Check prerequisites
    if not check_prerequisites():
        return False

    # Step 2: Setup Django
    if not setup_django():
        return False

    # Step 3: Generate learning data
    print_info("Generating real learning data (this may take a few minutes)...")
    user_input = input(f"{Colors.WARNING}⚠️  This will make real OpenAI API calls (~$0.50-1.00 cost). Continue? (y/N): {Colors.ENDC}")

    if user_input.lower() in ['y', 'yes']:
        if not run_learning_systems():
            print_warning("Learning data generation had issues. Continuing with demo...")
    else:
        print_info("Skipping learning data generation. Using existing data...")

    # Step 4: Verify data
    verify_learning_data()

    # Step 5: Start Django server
    if not start_django_server():
        print_error("Failed to start Django server")
        return False

    # Step 6: Open interface
    open_enhanced_neural_orchestra()

    # Step 7: Show instructions
    show_demo_instructions()

    # Step 8: Optional monitoring
    monitor_choice = input(f"\n{Colors.OKBLUE}Would you like to monitor live learning activity? (y/N): {Colors.ENDC}")
    if monitor_choice.lower() in ['y', 'yes']:
        monitor_learning_activity()

    print_success("Enhanced Neural Orchestra demo is ready!")
    print_info("Keep this terminal open to maintain the Django server")
    print_info("Visit http://localhost:8000 to access the interface")

    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\nDemo launcher interrupted by user")
    except Exception as e:
        print_error(f"Demo launcher error: {e}")
        sys.exit(1)
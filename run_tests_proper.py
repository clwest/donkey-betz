#!/usr/bin/env python3
"""
Proper Test Suite Runner
Executes tests in correct order with proper Django async handling
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()


def run_test_file(test_file, description):
    """Run a single test file and capture results"""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {description}")
    print(f"📁 File: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Run the test file as a subprocess to avoid async/sync conflicts
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print("Output:", result.stdout[-500:])  # Last 500 chars
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("Error:", result.stderr[-500:])
            if result.stdout:
                print("Output:", result.stdout[-500:])
                
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (5 minutes)")
        return False, "", "Test timed out after 5 minutes"
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {str(e)}")
        return False, "", str(e)


def main():
    """Run tests in optimal order"""
    print("🚀 Starting Unified Donkey Betz Test Suite")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test execution order - from simple to complex
    test_suite = [
        # 1. Basic connectivity tests (fastest)
        ("test_ws_connection.py", "WebSocket Connection Test"),
        ("test_websocket.py", "Basic WebSocket Test"),
        
        # 2. API endpoint tests (medium speed)
        ("test_api_endpoints.py", "API Endpoints Test"),
        ("test_assistant.py", "Assistant API Test"),
        
        # 3. Individual component tests
        ("test_agent_execution.py", "Agent Execution Test"),
        ("test_embeddings_working.py", "Working Embeddings Test"),
        ("test_rag_quick.py", "Quick RAG Test"),
        
        # 4. Integration tests (slower)
        ("test_sports_integration.py", "Sports Integration Test"),
        ("test_odds_api.py", "Odds API Test"),
        
        # 5. Workflow tests (slowest, most complex)
        ("test_working_workflows.py", "Working Workflows Test"),
        ("test_workflow_scenarios.py", "Workflow Scenarios Test"),
        ("test_websocket_agent_integration.py", "WebSocket Agent Integration Test"),
        ("test_cross_system_workflows.py", "Cross-System Workflows Test"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_file, description in test_suite:
        if os.path.exists(test_file):
            success, stdout, stderr = run_test_file(test_file, description)
            results.append({
                'file': test_file,
                'description': description,
                'success': success,
                'stdout': stdout,
                'stderr': stderr
            })
            
            if success:
                passed += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Skipping {test_file} - file not found")
            failed += 1
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("📊 TEST SUITE SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
    print(f"⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"  {status} - {result['description']}")
        if not result['success'] and result['stderr']:
            print(f"    Error: {result['stderr'][:200]}...")
    
    print(f"\n{'='*80}")
    
    return passed, failed


if __name__ == "__main__":
    try:
        passed, failed = main()
        sys.exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Test Progressive Results Delivery
Tests that Income Builder provides progressive updates during execution
"""

import requests
import json
import time
from datetime import datetime


def test_progressive_results():
    """Test that Income Builder provides progressive results during execution"""
    print("🔄 Testing Progressive Results Delivery...")
    print("="*60)

    # Step 1: Create an action plan
    api_url = "http://localhost:8000/api/v1/intelligence/income-builder/execute/"

    test_data = {
        "plan": {
            "steps": [
                "Research AI-powered social media management market trends",
                "Create comprehensive service package with pricing",
                "Develop 3 portfolio samples with real case studies",
                "Set up profiles on major freelance platforms"
            ],
            "timeline": "2 weeks",
            "expected_outcome": "Established freelance social media management business"
        },
        "opportunity": {
            "id": "social_media_management",
            "title": "AI-Powered Social Media Management",
            "description": "Start a social media management business using AI tools"
        }
    }

    print("📋 Creating action plan...")
    response = requests.post(api_url, json=test_data, timeout=30)

    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create action plan: {response.status_code}")
        return

    plan_data = response.json()
    plan_id = plan_data.get('plan_id')
    celery_task_id = plan_data.get('celery_task_id')

    print(f"✅ Action plan created: {plan_id}")
    print(f"🔄 Celery task started: {celery_task_id}")
    print()

    # Step 2: Poll for progressive updates
    print("📊 Polling for progressive results...")
    print("-" * 40)

    max_polls = 30  # Poll for up to 5 minutes (30 * 10 seconds)
    poll_count = 0
    last_progress = -1
    results_history = []

    while poll_count < max_polls:
        poll_count += 1
        print(f"Poll #{poll_count:2d} ({datetime.now().strftime('%H:%M:%S')})", end=" - ")

        try:
            polling_response = requests.get(api_url, timeout=10)

            if polling_response.status_code == 200:
                polling_data = polling_response.json()
                plans = polling_data.get('plans', [])

                # Find our plan
                our_plan = None
                for plan in plans:
                    if plan.get('id') == plan_id:
                        our_plan = plan
                        break

                if our_plan:
                    status = our_plan.get('status', 'unknown')
                    progress = our_plan.get('progress', 0)
                    current_step = our_plan.get('current_step', 0)
                    total_steps = our_plan.get('total_steps', 0)
                    results = our_plan.get('results', {})

                    # Track results progression
                    results_size = len(str(results))
                    results_keys = list(results.keys()) if results else []

                    results_history.append({
                        'poll': poll_count,
                        'time': datetime.now().isoformat(),
                        'status': status,
                        'progress': progress,
                        'current_step': current_step,
                        'results_size': results_size,
                        'results_keys': results_keys,
                        'files_created': len(results.get('files_created', [])) if results else 0
                    })

                    # Display progress
                    if progress != last_progress or status == 'completed':
                        print(f"Progress: {progress}% | Step: {current_step}/{total_steps} | Status: {status}")

                        if results:
                            print(f"     📁 Results: {results_size} chars, {len(results_keys)} keys")
                            if results.get('files_created'):
                                print(f"     📄 Files: {len(results['files_created'])} created")
                            if results_keys:
                                print(f"     🔑 Keys: {', '.join(results_keys[:5])}")
                        else:
                            print("     ⚠️  No results yet")

                        last_progress = progress
                    else:
                        print(f"Progress: {progress}% (no change)")

                    # Check if completed
                    if status == 'completed':
                        print()
                        print("🎉 Execution completed!")
                        break

                    # Check if failed
                    if status == 'failed':
                        print()
                        print("❌ Execution failed!")
                        break

                else:
                    print("❓ Plan not found in response")

            else:
                print(f"❌ Polling failed: {polling_response.status_code}")

        except Exception as e:
            print(f"❌ Polling error: {e}")

        # Wait before next poll
        if poll_count < max_polls:
            time.sleep(10)  # Wait 10 seconds between polls

    print()
    print("="*60)
    print("📈 PROGRESSIVE RESULTS ANALYSIS")
    print("="*60)

    # Analyze results progression
    if results_history:
        print(f"Total polls: {len(results_history)}")
        print(f"Execution time: ~{len(results_history) * 10} seconds")
        print()

        # Check for progressive results
        non_empty_results = [r for r in results_history if r['results_size'] > 2]  # More than just "{}"
        progressive_updates = len(non_empty_results)

        print(f"Progressive updates: {progressive_updates}/{len(results_history)}")
        print(f"Progressive ratio: {(progressive_updates/len(results_history)*100):.1f}%")
        print()

        # Show progression timeline
        print("📊 Results Progression Timeline:")
        for i, result in enumerate(results_history[::3]):  # Show every 3rd poll
            timestamp = datetime.fromisoformat(result['time']).strftime('%H:%M:%S')
            print(f"  {timestamp} | Progress: {result['progress']:3d}% | Results: {result['results_size']:4d} chars | Files: {result['files_created']}")

        print()

        # Final assessment
        final_result = results_history[-1]
        if final_result['results_size'] > 100:
            print("✅ ASSESSMENT: Progressive results are working!")
            print(f"   Final results size: {final_result['results_size']} characters")
            print(f"   Files created: {final_result['files_created']}")
            print(f"   Results keys: {len(final_result['results_keys'])}")
        else:
            print("❌ ASSESSMENT: Progressive results may not be working")
            print("   Results are empty or minimal throughout execution")

        # Save detailed analysis
        analysis_file = f"income_builder_outputs/progressive_results_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_file, 'w') as f:
            json.dump({
                'test_timestamp': datetime.now().isoformat(),
                'plan_id': plan_id,
                'celery_task_id': celery_task_id,
                'total_polls': len(results_history),
                'progressive_updates': progressive_updates,
                'progressive_ratio': (progressive_updates/len(results_history)*100) if results_history else 0,
                'final_status': final_result.get('status'),
                'final_progress': final_result.get('progress'),
                'final_results_size': final_result.get('results_size'),
                'final_files_count': final_result.get('files_created'),
                'polling_history': results_history
            }, f, indent=2)

        print(f"📄 Detailed analysis saved to: {analysis_file}")

    else:
        print("❌ No polling data collected")


if __name__ == "__main__":
    test_progressive_results()
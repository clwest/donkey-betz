#!/usr/bin/env python
"""
Demo Script - Deploy Agents and Show Learning
==============================================
"""

import requests
import json
import time

def run_demo():
    """
    Deploy agents and show learning in action
    """
    print("🚀 AGENT DEPLOYMENT & LEARNING DEMO")
    print("=" * 50)

    # API endpoint
    base_url = "http://localhost:8000"

    # 1. Deploy agents
    print("\n📦 Deploying AI Agents...")

    agents_to_deploy = [
        "Business Agent",
        "ML Recommendation Engine",
        "Database Architect"
    ]

    payload = {
        "project_type": "ecommerce",
        "agents": agents_to_deploy,
        "ml_features": ["personalization", "recommendations", "dynamic_pricing"],
        "strategy": "parallel"
    }

    try:
        response = requests.post(
            f"{base_url}/api/agent-deployment/execute/",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                print(f"✅ Successfully deployed {len(data.get('outputs', []))} agents!")

                # Show outputs
                for output in data.get('outputs', []):
                    agent = output.get('agent')
                    status = output.get('status')
                    result = output.get('output')

                    if status == 'success':
                        print(f"   ✓ {agent}: {result}")
                    else:
                        print(f"   ✗ {agent}: {status}")

                # Show files generated
                files = data.get('files', [])
                if files:
                    print(f"\n📁 Generated {len(files)} files:")
                    total_lines = 0
                    for file_info in files:
                        size = file_info.get('size', 0)
                        lines = size // 50  # Approximate lines
                        total_lines += lines
                        print(f"   - {file_info['filename']}: ~{lines} lines")

                    print(f"\n📊 Total code generated: ~{total_lines} lines")

                # Check learning stats
                print("\n🧠 Checking Learning Metrics...")
                time.sleep(2)

                stats_response = requests.get(f"{base_url}/api/learning/stats/")
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print(f"   • Active sessions: {stats.get('active_sessions', 0)}")
                    print(f"   • Code generated today: {stats.get('code_generated_today', 0)}")
                    print(f"   • Total lines: {stats.get('total_lines', 0)}")

                    # Show agent-specific stats
                    agents_data = stats.get('agents', [])
                    if agents_data:
                        print(f"\n📈 Agent Performance:")
                        for agent in agents_data[:5]:  # Show top 5
                            print(f"   {agent['name']}:")
                            print(f"      - Lines: {agent.get('total_lines', 0)}")
                            print(f"      - Quality: {agent.get('quality', 0)}%")
                            print(f"      - Complexity: {agent.get('complexity', 0)}")

            else:
                print(f"❌ Deployment failed: {data.get('message', 'Unknown error')}")

        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except requests.exceptions.Timeout:
        print("⏱️ Request timed out (this is normal for long-running tasks)")
        print("   Check the dashboard for progress!")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)
    print("✨ Demo Complete!")
    print("\n📍 View the live dashboard at:")
    print(f"   {base_url}/master-demo/")
    print("\n💡 The dashboard shows:")
    print("   - Real-time code generation")
    print("   - Learning metrics updating live")
    print("   - Agent collaboration events")
    print("   - Quality improvements over time")

if __name__ == "__main__":
    run_demo()
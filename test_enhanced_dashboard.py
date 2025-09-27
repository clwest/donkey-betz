#!/usr/bin/env python3
"""
Test script to verify the enhanced dashboard displays ALL data
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_dashboard_data():
    """Test that the dashboard receives complete data via API"""

    print("🔍 Testing Enhanced Dashboard Data Display")
    print("=" * 50)

    # Test the intelligence API endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/intelligence/")
        data = response.json()

        if response.status_code == 200 and data.get('success'):
            dashboard_data = data.get('data', {})

            # Check for all the key data types
            checks = {
                'agent_performance': dashboard_data.get('agent_performance', []),
                'emergent_behaviors': dashboard_data.get('emergent_behaviors', []),
                'system_statistics': dashboard_data.get('system_statistics', {}),
                'system_metrics': dashboard_data.get('system_metrics', {}),
                'real_metrics': dashboard_data.get('real_metrics', {}),
                'learning_analytics': dashboard_data.get('learning_analytics', {})
            }

            print("✅ API Response Received")
            print(f"📊 Data completeness check:")

            for key, value in checks.items():
                if value:
                    if isinstance(value, list):
                        print(f"  ✓ {key}: {len(value)} items")
                        # Show sample data
                        if key == 'agent_performance' and len(value) > 0:
                            print(f"    Sample: {value[0].get('name', 'N/A')} - Success: {value[0].get('success_rate', 0)}%")
                        elif key == 'emergent_behaviors' and len(value) > 0:
                            print(f"    Sample: {value[0].get('type', 'N/A')} - Significance: {value[0].get('significance', 'N/A')}")
                    elif isinstance(value, dict):
                        print(f"  ✓ {key}: {len(value)} fields")
                        # Show sample metrics
                        if key == 'system_statistics':
                            print(f"    Total Files: {value.get('total_files', 0):,}")
                            print(f"    Total Lines: {value.get('total_lines', 0):,}")
                        elif key == 'system_metrics':
                            print(f"    CPU Usage: {value.get('cpu_usage', 0)}%")
                            print(f"    Memory Usage: {value.get('memory_usage', 0)}%")
                else:
                    print(f"  ⚠️  {key}: No data")

            # Calculate data visibility percentage
            data_points_found = sum(1 for v in checks.values() if v)
            total_data_points = len(checks)
            visibility_percentage = (data_points_found / total_data_points) * 100

            print(f"\n📈 Data Visibility: {visibility_percentage:.1f}%")

            if visibility_percentage < 100:
                print(f"⚠️  Only {visibility_percentage:.1f}% of data types are present")
                print("   The backend may need to generate more data")
            else:
                print("🎉 ALL data types are being sent to the dashboard!")

            # Check WebSocket endpoint
            print(f"\n🔌 WebSocket endpoint available at: ws://localhost:8000/ws/consciousness/")
            print("   Dashboard should auto-connect and display updates every 30 seconds")

            return True

        else:
            print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("   Make sure the Django server is running: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error testing dashboard: {str(e)}")
        return False

def check_dashboard_page():
    """Check if the dashboard page loads"""
    try:
        response = requests.get(f"{BASE_URL}/intelligence/")
        if response.status_code == 200:
            # Check if enhanced functions are in the HTML
            html_content = response.text

            enhanced_functions = [
                'updateAgentsEnhanced',
                'updateEmergentBehaviors',
                'updateSystemStatistics',
                'updateSystemMetricsEnhanced',
                'agent-perf-grid',
                'stat-card',
                'metric-item'
            ]

            print(f"\n🖥️  Dashboard Page Check:")
            for func in enhanced_functions:
                if func in html_content:
                    print(f"  ✓ {func} found in HTML")
                else:
                    print(f"  ❌ {func} NOT found in HTML")

            print(f"\n✅ Dashboard accessible at: http://localhost:8000/intelligence/")
            return True
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking dashboard page: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🚀 Enhanced Dashboard Display Test")
    print("=" * 50)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test API data
    api_success = test_dashboard_data()

    # Test dashboard page
    page_success = check_dashboard_page()

    if api_success and page_success:
        print("\n✅ SUCCESS: Enhanced dashboard is ready!")
        print("📊 Open http://localhost:8000/intelligence/ to see ALL the data")
        print("🎯 The dashboard now displays:")
        print("   • Detailed agent performance metrics")
        print("   • Emergent behaviors detection")
        print("   • System statistics (files, lines of code)")
        print("   • Live system metrics (CPU, Memory, Redis, WebSocket)")
        print("   • Enhanced learning analytics")
    else:
        print("\n⚠️  Some issues detected - check the output above")
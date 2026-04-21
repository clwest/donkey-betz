#!/usr/bin/env python3
"""
Backend-Frontend Connection Diagnostic & Fix Script
This script will:
1. Test all backend API endpoints
2. Verify what data they return
3. Map them to frontend expectations
4. Create a connection report
5. Generate fixes for any broken connections
"""

import json
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Configuration
API_BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "<redacted-0fb2390d-2026-04-20>"  # Default token from your env

class BackendFrontendBridge:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = {
            "Authorization": f"Token {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "endpoints": {},
            "agents": {},
            "issues": [],
            "fixes": []
        }

    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

    def test_endpoint(self, path: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=5)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=5)
            else:
                return {"error": f"Unsupported method: {method}"}

            return {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else response.text
            }
        except requests.exceptions.ConnectionError:
            return {"status": 0, "success": False, "error": "Connection refused - is the backend running?"}
        except requests.exceptions.Timeout:
            return {"status": 0, "success": False, "error": "Request timeout"}
        except Exception as e:
            return {"status": 0, "success": False, "error": str(e)}

    def test_critical_endpoints(self):
        """Test all critical endpoints that the frontend expects"""
        self.print_header("Testing Critical API Endpoints")

        # Map of endpoints the frontend is trying to use
        critical_endpoints = {
            # Agent endpoints
            "/api/v1/agents/": "List all agents",
            "/api/v1/agents/templates/": "Agent templates",
            "/api/v1/agents/executions/": "Agent executions",
            "/api/v1/agents/discover/": "Discover agents",

            # Intelligence/Income Builder endpoints
            "/api/v1/intelligence/income-builder/": "Income Builder main",
            "/api/v1/intelligence/real-income-builder/": "Real Income Builder",
            "/api/v1/intelligence/opportunities/": "Opportunities",
            "/api/v1/intelligence/revenue/": "Revenue data",
            "/api/v1/intelligence/action-plan/": "Action plans",

            # Sports/Betting endpoints
            "/api/v1/sports/leagues/": "Sports leagues",
            "/api/v1/sports/games/": "Sports games",
            "/api/v1/odds/": "Odds data",

            # Content endpoints
            "/api/v1/content/generate/": "Content generation",
            "/api/v1/content/images/": "Image generation",

            # Health check
            "/api/v1/health/": "Health check",
        }

        for endpoint, description in critical_endpoints.items():
            print(f"\n{Fore.CYAN}Testing: {description}{Style.RESET_ALL}")
            print(f"  Endpoint: {endpoint}")

            result = self.test_endpoint(endpoint)
            self.results["endpoints"][endpoint] = result

            if result["success"]:
                self.print_success(f"Status: {result['status']} - Working")
                if result["data"]:
                    # Check if data is meaningful
                    if isinstance(result["data"], dict):
                        if "results" in result["data"] and result["data"]["results"]:
                            count = len(result["data"]["results"])
                            self.print_info(f"Returns {count} items")
                        elif "agents" in result["data"]:
                            count = len(result["data"]["agents"])
                            self.print_info(f"Returns {count} agents")
                        elif "opportunities" in result["data"]:
                            count = len(result["data"]["opportunities"])
                            self.print_info(f"Returns {count} opportunities")
                        elif result["data"]:
                            self.print_info(f"Returns data: {list(result['data'].keys())[:5]}")
            else:
                self.print_error(f"Status: {result['status']} - {result['error'][:100]}")
                self.results["issues"].append({
                    "endpoint": endpoint,
                    "issue": result["error"],
                    "impact": f"Frontend cannot load {description}"
                })

    def test_agent_system(self):
        """Test the agent system specifically"""
        self.print_header("Testing Agent System")

        # Try to get agent count
        result = self.test_endpoint("/api/v1/agents/templates/?page_size=200")

        if result["success"] and result["data"]:
            if "results" in result["data"]:
                agents = result["data"]["results"]
                self.results["agents"]["count"] = len(agents)
                self.results["agents"]["list"] = [
                    {"name": a.get("name"), "description": a.get("description", "")[:50]}
                    for a in agents[:10]  # First 10 agents
                ]

                self.print_success(f"Found {len(agents)} agents in the system!")

                # Show first few agents
                print(f"\n{Fore.GREEN}Sample Agents:{Style.RESET_ALL}")
                for agent in agents[:5]:
                    print(f"  • {agent.get('name')}: {agent.get('description', '')[:50]}...")
            else:
                self.print_warning("Agent endpoint returns data but no 'results' field")
                self.results["issues"].append({
                    "endpoint": "/api/v1/agents/templates/",
                    "issue": "Unexpected data structure",
                    "fix": "Check serializer output format"
                })
        else:
            self.print_error("Cannot retrieve agents from backend")
            self.results["agents"]["count"] = 0

    def test_websocket_endpoints(self):
        """Check if WebSocket endpoints are configured"""
        self.print_header("Checking WebSocket Configuration")

        ws_endpoints = [
            "/ws/assistant/",
            "/ws/agents/",
            "/ws/income-builder/",
            "/ws/command-center/",
            "/ws/opportunity-scanner/",
            "/ws/neural-orchestra/"
        ]

        print(f"{Fore.YELLOW}Note: WebSocket testing requires a different approach.{Style.RESET_ALL}")
        print("WebSocket endpoints that should be configured:")

        for endpoint in ws_endpoints:
            print(f"  • ws://localhost:8000{endpoint}")

        print(f"\n{Fore.BLUE}To test WebSockets, run: python simple_ws_test.py{Style.RESET_ALL}")

    def generate_fixes(self):
        """Generate fix recommendations based on issues found"""
        self.print_header("Generating Fix Recommendations")

        if not self.results["issues"]:
            self.print_success("No critical issues found!")
            return

        for issue in self.results["issues"]:
            endpoint = issue["endpoint"]

            if "Connection refused" in issue["issue"]:
                fix = {
                    "issue": "Backend not running",
                    "fix": "Start the backend with: ./start_ws_quick.sh",
                    "verify": f"curl -H 'Authorization: Token {AUTH_TOKEN}' {self.base_url}{endpoint}"
                }
            elif "404" in issue["issue"] or "Not Found" in issue["issue"]:
                fix = {
                    "issue": f"Endpoint {endpoint} not found",
                    "fix": """
1. Check if URL pattern is registered in ai_core/core/urls.py:
   - Should have: path('api/v1/intelligence/', include('intelligence.urls'))

2. Check if view exists in the app's urls.py and views.py

3. Create the missing endpoint:
   # In intelligence/urls.py
   path('real-income-builder/', views.RealIncomeBuilderView.as_view(), name='real-income-builder'),

   # In intelligence/views.py
   class RealIncomeBuilderView(APIView):
       def get(self, request):
           # Return real opportunities from database
           opportunities = Opportunity.objects.all()
           return Response({'success': True, 'opportunities': [...]})
""",
                    "verify": f"python manage.py show_urls | grep {endpoint.split('/')[-2]}"
                }
            elif "500" in str(issue.get("status", "")):
                fix = {
                    "issue": f"Server error on {endpoint}",
                    "fix": """
1. Check Django logs: tail -f django_server.log
2. Check for missing imports or database issues
3. Run: python manage.py check
4. Ensure migrations are up to date: python manage.py migrate
""",
                    "verify": "python manage.py shell -c 'from intelligence.models import *; print(Opportunity.objects.count())'"
                }
            else:
                fix = {
                    "issue": issue["issue"],
                    "fix": "Check backend implementation for this endpoint",
                    "verify": f"python manage.py shell -c 'from django.urls import resolve; print(resolve(\"{endpoint}\"))'"
                }

            self.results["fixes"].append(fix)

            print(f"\n{Fore.RED}Issue: {fix['issue']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Fix:{Style.RESET_ALL} {fix['fix']}")
            print(f"{Fore.BLUE}Verify:{Style.RESET_ALL} {fix['verify']}")

    def create_connection_test_file(self):
        """Create a test file that the frontend can use to verify connections"""
        self.print_header("Creating Frontend Connection Test")

        test_code = '''
// Save this as: frontend/src/utils/testBackendConnection.ts

export async function testBackendConnection() {
  const API_BASE = 'http://localhost:8000';
  const TOKEN = localStorage.getItem('authToken') || '<redacted-0fb2390d-2026-04-20>';

  const endpoints = [
    '/api/v1/agents/templates/',
    '/api/v1/intelligence/opportunities/',
    '/api/v1/intelligence/revenue/',
  ];

  const results = {};

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Authorization': `Token ${TOKEN}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      results[endpoint] = {
        success: response.ok,
        status: response.status,
        hasData: !!data,
        dataKeys: Object.keys(data || {})
      };

      console.log(`✅ ${endpoint}:`, results[endpoint]);
    } catch (error) {
      results[endpoint] = { success: false, error: error.message };
      console.error(`❌ ${endpoint}:`, error);
    }
  }

  return results;
}

// Call this from browser console:
// await testBackendConnection()
'''

        print(test_code)

        # Save to file
        with open("test_backend_connection.js", "w") as f:
            f.write(test_code)

        self.print_success("Test file created: test_backend_connection.js")
        print(f"{Fore.BLUE}Copy this to frontend/src/utils/ and run in browser console{Style.RESET_ALL}")

    def save_report(self):
        """Save the diagnostic report"""
        filename = f"backend_frontend_connection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        self.print_success(f"Report saved to: {filename}")

    def run_diagnostic(self):
        """Run the complete diagnostic"""
        self.print_header("BACKEND-FRONTEND CONNECTION DIAGNOSTIC")
        print(f"Testing backend at: {self.base_url}")
        print(f"Using auth token: {AUTH_TOKEN[:10]}...")

        # Run tests
        self.test_critical_endpoints()
        self.test_agent_system()
        self.test_websocket_endpoints()
        self.generate_fixes()
        self.create_connection_test_file()

        # Summary
        self.print_header("DIAGNOSTIC SUMMARY")

        working_endpoints = sum(1 for e in self.results["endpoints"].values() if e.get("success"))
        total_endpoints = len(self.results["endpoints"])

        print(f"Endpoints tested: {total_endpoints}")
        print(f"Working endpoints: {working_endpoints}")
        print(f"Failed endpoints: {total_endpoints - working_endpoints}")
        print(f"Agents found: {self.results['agents'].get('count', 0)}")
        print(f"Issues found: {len(self.results['issues'])}")
        print(f"Fixes generated: {len(self.results['fixes'])}")

        # Save report
        self.save_report()

        # Final recommendation
        if working_endpoints < total_endpoints / 2:
            self.print_error("\n⚠️  CRITICAL: Most endpoints are not working!")
            self.print_warning("Recommended action: Check if backend is running and migrations are complete")
            print(f"\n{Fore.YELLOW}Quick fix commands:{Style.RESET_ALL}")
            print("  1. cd /Users/donkeyking/development/unified-donkey-betz")
            print("  2. source .venv/bin/activate")
            print("  3. python manage.py migrate")
            print("  4. python manage.py runserver")
        elif self.results["agents"].get("count", 0) == 0:
            self.print_warning("\n⚠️  No agents found in the system!")
            print(f"\n{Fore.YELLOW}To populate agents:{Style.RESET_ALL}")
            print("  python activate_all_agents.py")
        else:
            self.print_success("\n✅ Backend is mostly functional!")
            self.print_info("Now let's connect it to the frontend properly")


if __name__ == "__main__":
    bridge = BackendFrontendBridge()
    bridge.run_diagnostic()
#!/usr/bin/env python3
"""
Test all frontend pages and their corresponding API endpoints
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Security fix: Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000/api"
AUTH_TOKEN = os.getenv("TEST_AUTH_TOKEN", "")
if not TOKEN:
    print("WARNING: No TEST_AUTH_TOKEN found. Please set it in .env file.")
    import sys
    sys.exit(1)  # chris token

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log(message: str, status: str = "INFO"):
    """Pretty print log messages"""
    colors = {"SUCCESS": GREEN, "ERROR": RED, "WARNING": YELLOW, "INFO": BLUE}
    color = colors.get(status, RESET)
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {message}{RESET}")


def test_endpoint(endpoint: str, method: str = "GET", data: Dict = None) -> Tuple[bool, str]:
    """Test a single API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code in [200, 201]:
            return True, f"Status {response.status_code}"
        else:
            return False, f"Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)


def main():
    """Test all pages and their API dependencies"""
    
    # Define pages and their required API endpoints
    pages = {
        "Dashboard (/dashboard)": [
            ("/status/", "GET", None),
            ("/analytics/dashboard/", "GET", None),
            ("/agents/discovery/stats/", "GET", None),
        ],
        "Studio (/studio)": [
            ("/content/templates/", "GET", None),
            ("/prompting/settings/", "GET", None),
            ("/content/library/", "GET", None),
        ],
        "Gallery (/gallery)": [
            ("/gallery/videos/", "GET", None),
            ("/content/list/", "GET", None),
        ],
        "Campaigns (/campaigns)": [
            ("/campaigns/", "GET", None),
            ("/campaigns/templates/", "GET", None),
        ],
        "Workflows (/workflows)": [
            ("/campaigns/templates/", "GET", None),  # Workflows uses campaign templates
            ("/workflows/templates/", "GET", None),
        ],
        "Agents (/agents)": [
            ("/agents/list/", "GET", None),
            ("/agents/health/", "GET", None),
            ("/agents/by-specialization/", "GET", None),
        ],
        "Research (/research)": [
            ("/research/books/", "GET", None),
            ("/research/documents/", "GET", None),
        ],
        "E-books (/ebooks)": [
            ("/ebooks/", "GET", None),
        ],
        "Voice (/voice)": [
            ("/voice/history/", "GET", None),
        ],
        "Orchestrations (/orchestrations)": [
            ("/orchestrations/", "GET", None),
            ("/instances/", "GET", None),
        ],
        "Profile (/profile)": [
            ("/profile/", "GET", None),
            ("/profile/stats/", "GET", None),
            ("/auth/user/", "GET", None),
        ],
        "Feedback (/feedback)": [
            ("/feedback/analytics/", "GET", None),
            ("/feedback/history/", "GET", None),
        ],
        "AI Settings (/ai-settings)": [
            ("/prompting/settings/", "GET", None),
            ("/llm/providers/", "GET", None),
        ],
        "Sports Board (/sports)": [
            ("/v1/sports/live-opportunities/", "GET", None),
            ("/v1/odds/markets/", "GET", None),
        ],
        "Odds (/odds)": [
            ("/v1/odds/markets/", "GET", None),
            ("/v1/odds/bankroll/stats/", "GET", None),
        ],
        "Agent Orchestra (/agent-orchestra)": [
            ("/agents/list/", "GET", None),
            ("/agents/health/", "GET", None),
        ],
    }
    
    log("=" * 60, "INFO")
    log("TESTING ALL FRONTEND PAGES AND API ENDPOINTS", "INFO")
    log("=" * 60, "INFO")
    
    total_pages = len(pages)
    working_pages = 0
    failed_endpoints = []
    
    for page_name, endpoints in pages.items():
        log(f"\n📄 {page_name}", "INFO")
        page_working = True
        
        for endpoint, method, data in endpoints:
            success, message = test_endpoint(endpoint, method, data)
            
            if success:
                log(f"  ✓ {endpoint}: {message}", "SUCCESS")
            else:
                log(f"  ✗ {endpoint}: {message}", "ERROR")
                failed_endpoints.append((page_name, endpoint, message))
                page_working = False
        
        if page_working:
            working_pages += 1
            log(f"  → Page APIs: ALL WORKING", "SUCCESS")
        else:
            log(f"  → Page APIs: SOME FAILURES", "WARNING")
    
    # Summary
    log("\n" + "=" * 60, "INFO")
    log("SUMMARY", "INFO")
    log("=" * 60, "INFO")
    
    success_rate = (working_pages / total_pages * 100) if total_pages > 0 else 0
    log(f"Pages with all APIs working: {working_pages}/{total_pages} ({success_rate:.1f}%)", "INFO")
    
    if failed_endpoints:
        log(f"\n⚠️  Failed endpoints ({len(failed_endpoints)}):", "WARNING")
        for page, endpoint, error in failed_endpoints[:10]:  # Show first 10
            log(f"  • {page}: {endpoint}", "ERROR")
            log(f"    Error: {error[:100]}", "ERROR")
    
    if success_rate == 100:
        log("\n✅ ALL PAGES FULLY FUNCTIONAL!", "SUCCESS")
    elif success_rate >= 70:
        log(f"\n⚠️  {100-success_rate:.0f}% of pages have issues", "WARNING")
    else:
        log(f"\n❌ {100-success_rate:.0f}% of pages need fixing", "ERROR")
    
    return working_pages == total_pages


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
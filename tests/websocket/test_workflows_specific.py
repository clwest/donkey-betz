#!/usr/bin/env python3
"""
Specific test for workflows page functionality
"""

import requests
import json
from datetime import datetime

# Security fix: Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "http://localhost:8000/api"
AUTH_TOKEN = os.getenv("TEST_AUTH_TOKEN", "")
if not TOKEN:
    print("WARNING: No TEST_AUTH_TOKEN found. Please set it in .env file.")
    import sys
    sys.exit(1)

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log(message: str, status: str = "INFO"):
    colors = {"SUCCESS": GREEN, "ERROR": RED, "WARNING": YELLOW, "INFO": BLUE}
    color = colors.get(status, RESET)
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {message}{RESET}")


def test_workflows_api():
    """Test all APIs used by workflows page"""
    
    log("=" * 60, "INFO")
    log("TESTING WORKFLOWS PAGE APIS", "INFO")
    log("=" * 60, "INFO")
    
    headers = {
        "Authorization": f"Token {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1. Test campaigns/templates endpoint (primary)
    log("\n1. Testing GET /campaigns/templates/", "INFO")
    try:
        response = requests.get(f"{API_URL}/campaigns/templates/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            log(f"✅ Success! Found {len(templates)} templates", "SUCCESS")
            for template in templates[:3]:
                log(f"   - {template.get('name', 'Unknown')}: {template.get('description', '')}", "INFO")
        else:
            log(f"❌ Failed with status {response.status_code}", "ERROR")
            log(f"   Response: {response.text}", "ERROR")
    except Exception as e:
        log(f"❌ Exception: {str(e)}", "ERROR")
    
    # 2. Test workflows/templates endpoint (secondary)
    log("\n2. Testing GET /workflows/templates/", "INFO")
    try:
        response = requests.get(f"{API_URL}/workflows/templates/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Success! Response: {str(data)[:100]}...", "SUCCESS")
        else:
            log(f"❌ Failed with status {response.status_code}", "ERROR")
            log(f"   Response: {response.text}", "ERROR")
    except Exception as e:
        log(f"❌ Exception: {str(e)}", "ERROR")
    
    # 3. Test creating campaign from template
    log("\n3. Testing POST /campaigns/from-template/", "INFO")
    try:
        payload = {
            "template_name": "Email Campaign",
            "customizations": {
                "name": "Test Campaign",
                "target_audience": {
                    "description": "Test audience"
                },
                "budget": 1000
            }
        }
        response = requests.post(f"{API_URL}/campaigns/from-template/", 
                                headers=headers, 
                                json=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            log(f"✅ Success! Created campaign: {data.get('id', 'unknown')}", "SUCCESS")
        else:
            log(f"❌ Failed with status {response.status_code}", "ERROR")
            log(f"   Response: {response.text}", "ERROR")
    except Exception as e:
        log(f"❌ Exception: {str(e)}", "ERROR")
    
    # 4. Test creating blank campaign
    log("\n4. Testing POST /campaigns/ (blank campaign)", "INFO")
    try:
        payload = {
            "title": "Test Custom Campaign",
            "description": "AI-powered custom workflow",
            "campaign_type": "multi",
            "target_audience": "Define your audience"
        }
        response = requests.post(f"{API_URL}/campaigns/", 
                                headers=headers, 
                                json=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            campaign_id = data.get('id') or data.get('campaign', {}).get('id')
            log(f"✅ Success! Created campaign: {campaign_id}", "SUCCESS")
            
            # Try to delete the test campaign
            if campaign_id:
                try:
                    del_response = requests.delete(f"{API_URL}/campaigns/{campaign_id}/", 
                                                  headers=headers)
                    if del_response.status_code in [200, 204]:
                        log(f"   Cleanup: Deleted test campaign", "INFO")
                except:
                    pass
        else:
            log(f"❌ Failed with status {response.status_code}", "ERROR")
            log(f"   Response: {response.text[:200]}", "ERROR")
    except Exception as e:
        log(f"❌ Exception: {str(e)}", "ERROR")
    
    # 5. Test CORS headers
    log("\n5. Testing CORS headers", "INFO")
    try:
        # Simulate browser preflight request
        response = requests.options(f"{API_URL}/campaigns/templates/", 
                                   headers={
                                       "Origin": "http://localhost:3000",
                                       "Access-Control-Request-Method": "GET",
                                       "Access-Control-Request-Headers": "authorization,content-type"
                                   })
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        log("CORS Headers:", "INFO")
        for header, value in cors_headers.items():
            if value:
                log(f"   {header}: {value}", "SUCCESS")
            else:
                log(f"   {header}: Not set", "WARNING")
    except Exception as e:
        log(f"❌ Exception: {str(e)}", "ERROR")
    
    log("\n" + "=" * 60, "INFO")
    log("RECOMMENDATIONS", "INFO")
    log("=" * 60, "INFO")
    
    log("If you're still seeing errors:", "INFO")
    log("1. Check browser console (F12) for specific error messages", "INFO")
    log("2. Check Network tab to see failed requests", "INFO")
    log("3. Verify localStorage has authToken set", "INFO")
    log("4. Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)", "INFO")
    log("5. Clear browser cache and cookies for localhost:3000", "INFO")


if __name__ == "__main__":
    test_workflows_api()
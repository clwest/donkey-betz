#!/usr/bin/env python3
"""
Quick UI verification script to check if the fixes are working
"""
import requests
from bs4 import BeautifulSoup
import sys

def check_ui():
    try:
        # Check if frontend is running
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code != 200:
            print("❌ Frontend not accessible")
            return False

        print("✅ Frontend is running on port 3000")

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if the app div exists
        app_div = soup.find('div', {'id': 'root'})
        if app_div:
            print("✅ React root element found")
        else:
            print("⚠️  React root element not found")

        # Check if Tailwind CSS is loaded (looking for tailwind classes in the HTML)
        html_content = response.text
        if 'tailwind' in html_content.lower() or 'vite' in html_content:
            print("✅ Build system is active (Vite detected)")

        # Check backend
        try:
            api_response = requests.get('http://localhost:8000/api/v1/agents/',
                                       headers={'Authorization': 'Token <redacted-0fb2390d-2026-04-20>'},
                                       timeout=5)
            if api_response.status_code == 200:
                agents = api_response.json()
                print(f"✅ Backend API is running - {len(agents)} agents available")
            else:
                print(f"⚠️  Backend API returned status {api_response.status_code}")
        except:
            print("❌ Backend API not accessible")

        print("\n🎯 NEXT STEPS:")
        print("1. Open http://localhost:3000/dashboard in your browser")
        print("2. Do a hard refresh (Cmd+Shift+R on Mac)")
        print("3. Check for:")
        print("   - No gray overlays blocking the UI")
        print("   - CommandPalette works with Cmd+K")
        print("   - AI Assistant button in bottom-right corner")
        print("   - Dashboard content is fully visible and interactive")
        print("\nℹ️  If you still see old UI:")
        print("   - Clear browser cache")
        print("   - Open in Incognito/Private mode")
        print("   - Check browser console for errors (F12)")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to frontend on port 3000")
        print("   Run: ./start_ws_quick.sh")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verifying UI Fix Status...\n")
    success = check_ui()
    sys.exit(0 if success else 1)
#!/usr/bin/env python
"""
Test the file viewer API endpoint
"""

import requests
import json

def test_file_viewer():
    """Test viewing a generated file"""

    print("\n" + "="*80)
    print("📁 TESTING FILE VIEWER API")
    print("="*80 + "\n")

    # Test file from AI Social Media Management
    test_file = "AI Social Media Management/AI-Powered_Social_Media_Management_Complete_Plan.md"

    print(f"📄 Testing file: {test_file}\n")

    # URL encode the filename
    import urllib.parse
    encoded_filename = urllib.parse.quote(test_file)

    # Make the API request
    url = f"http://localhost:8000/api/v1/intelligence/income-builder/file/{encoded_filename}/"
    print(f"🌐 URL: {url}\n")

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get('success'):
            print("✅ File loaded successfully!")
            print(f"   Content length: {len(data.get('content', ''))} characters")

            # Show first 500 characters
            content = data.get('content', '')
            if content:
                print("\n📝 First 500 characters of content:")
                print("-" * 40)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-" * 40)
        else:
            print(f"❌ Failed to load file: {data.get('error', 'Unknown error')}")
            print(f"   Status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Error making request: {e}")

    # Test with a non-existent file
    print("\n\n🧪 Testing with non-existent file...")
    bad_file = "NonExistent/file.md"
    encoded_bad = urllib.parse.quote(bad_file)
    bad_url = f"http://localhost:8000/api/v1/intelligence/income-builder/file/{encoded_bad}/"

    try:
        response = requests.get(bad_url)
        data = response.json()

        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent file")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*80)
    print("✅ FILE VIEWER API TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_file_viewer()
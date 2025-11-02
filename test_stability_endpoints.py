#!/usr/bin/env python3
"""
Comprehensive Stability AI API Endpoint Testing
Tests all available Stability AI endpoints to verify functionality
"""

import os
import requests
import base64
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

class StabilityAPITester:
    """Test all Stability AI API endpoints"""

    def __init__(self):
        self.api_key = os.getenv('STABILITY_API_KEY')
        if not self.api_key:
            raise ValueError("STABILITY_API_KEY not found in environment")

        self.base_url = "https://api.stability.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.results = []

    def test_sdxl_text_to_image(self):
        """Test SDXL 1.0 text-to-image (our current endpoint)"""
        print("\n" + "="*80)
        print("1. Testing SDXL 1.0 Text-to-Image (Current Endpoint)")
        print("="*80)

        url = f"{self.base_url}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        body = {
            "text_prompts": [{"text": "a cute robot, simple test", "weight": 1}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }

        try:
            print(f"📍 Endpoint: {url}")
            print(f"📝 Prompt: 'a cute robot, simple test'")
            print("⏳ Generating...")

            start = datetime.now()
            response = requests.post(url, headers=self.headers, json=body, timeout=60)
            elapsed = (datetime.now() - start).total_seconds()

            if response.status_code == 200:
                data = response.json()
                artifacts = data.get("artifacts", [])

                print(f"✅ SUCCESS")
                print(f"   Status: {response.status_code}")
                print(f"   Time: {elapsed:.2f}s")
                print(f"   Images: {len(artifacts)}")
                print(f"   Cost: ~$0.002")

                # Save first image
                if artifacts:
                    img_data = artifacts[0].get("base64")
                    if img_data:
                        filename = f"test_sdxl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        with open(filename, 'wb') as f:
                            f.write(base64.b64decode(img_data))
                        print(f"   Saved: {filename}")

                self.results.append({
                    "endpoint": "SDXL 1.0 Text-to-Image",
                    "status": "✅ Working",
                    "time": f"{elapsed:.2f}s",
                    "notes": "Legacy but functional"
                })
                return True
            else:
                print(f"❌ FAILED")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

                self.results.append({
                    "endpoint": "SDXL 1.0 Text-to-Image",
                    "status": "❌ Failed",
                    "error": f"HTTP {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.results.append({
                "endpoint": "SDXL 1.0 Text-to-Image",
                "status": "❌ Error",
                "error": str(e)
            })
            return False

    def test_sd3_text_to_image(self):
        """Test SD3 text-to-image (newer model)"""
        print("\n" + "="*80)
        print("2. Testing Stable Diffusion 3 Text-to-Image")
        print("="*80)

        # Try common SD3 endpoint patterns
        possible_endpoints = [
            f"{self.base_url}/v1/generation/stable-diffusion-3/text-to-image",
            f"{self.base_url}/v2beta/stable-image/generate/sd3",
            f"{self.base_url}/v2beta/stable-image/generate/core",
        ]

        body = {
            "text_prompts": [{"text": "a cute robot, simple test", "weight": 1}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }

        for url in possible_endpoints:
            try:
                print(f"\n📍 Testing: {url}")
                response = requests.post(url, headers=self.headers, json=body, timeout=60)

                if response.status_code == 200:
                    print(f"✅ SUCCESS - Found working SD3 endpoint!")
                    print(f"   URL: {url}")

                    self.results.append({
                        "endpoint": f"SD3: {url}",
                        "status": "✅ Working",
                        "notes": "Newer model available"
                    })
                    return True
                elif response.status_code == 404:
                    print(f"⚠️  Not found (404) - trying next...")
                else:
                    print(f"❌ Error {response.status_code}: {response.text[:100]}")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

        print(f"\n❌ No working SD3 endpoint found")
        self.results.append({
            "endpoint": "SD3 Text-to-Image",
            "status": "❌ Not Found",
            "notes": "Tried multiple endpoints"
        })
        return False

    def test_list_engines(self):
        """Test listing available engines/models"""
        print("\n" + "="*80)
        print("3. Testing List Available Engines")
        print("="*80)

        url = f"{self.base_url}/v1/engines/list"

        try:
            print(f"📍 Endpoint: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS")
                print(f"   Available engines/models:")

                engines = data if isinstance(data, list) else data.get('engines', [])
                for engine in engines:
                    engine_id = engine.get('id', 'unknown')
                    engine_name = engine.get('name', 'unknown')
                    print(f"   - {engine_id}: {engine_name}")

                self.results.append({
                    "endpoint": "List Engines",
                    "status": "✅ Working",
                    "count": len(engines)
                })
                return True
            else:
                print(f"❌ FAILED")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

                self.results.append({
                    "endpoint": "List Engines",
                    "status": "❌ Failed",
                    "error": f"HTTP {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.results.append({
                "endpoint": "List Engines",
                "status": "❌ Error",
                "error": str(e)
            })
            return False

    def test_account_balance(self):
        """Test account balance/credits endpoint"""
        print("\n" + "="*80)
        print("4. Testing Account Balance/Credits")
        print("="*80)

        url = f"{self.base_url}/v1/user/balance"

        try:
            print(f"📍 Endpoint: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS")
                print(f"   Account info:")
                print(f"   {json.dumps(data, indent=2)}")

                self.results.append({
                    "endpoint": "Account Balance",
                    "status": "✅ Working",
                    "data": data
                })
                return True
            else:
                print(f"❌ FAILED")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

                self.results.append({
                    "endpoint": "Account Balance",
                    "status": "❌ Failed",
                    "error": f"HTTP {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.results.append({
                "endpoint": "Account Balance",
                "status": "❌ Error",
                "error": str(e)
            })
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("STABILITY AI API ENDPOINT TEST SUMMARY")
        print("="*80 + "\n")

        working = sum(1 for r in self.results if "✅" in r['status'])
        total = len(self.results)

        print(f"📊 Results: {working}/{total} endpoints working\n")

        for result in self.results:
            status = result['status']
            endpoint = result['endpoint']
            print(f"{status} {endpoint}")

            if 'time' in result:
                print(f"     Time: {result['time']}")
            if 'notes' in result:
                print(f"     Notes: {result['notes']}")
            if 'error' in result:
                print(f"     Error: {result['error']}")
            print()

        print("="*80)
        print(f"✅ Working Endpoints: {working}")
        print(f"❌ Failed Endpoints: {total - working}")
        print("="*80 + "\n")


def main():
    print("\n🧪 COMPREHENSIVE STABILITY AI API TESTING")
    print("Testing all available endpoints to verify functionality\n")

    try:
        tester = StabilityAPITester()

        # Run all tests
        tester.test_sdxl_text_to_image()
        tester.test_sd3_text_to_image()
        tester.test_list_engines()
        tester.test_account_balance()

        # Print summary
        tester.print_summary()

        print("💡 RECOMMENDATIONS:")
        print("   1. If SDXL 1.0 works, we can continue using it (it's 'legacy' but functional)")
        print("   2. If SD3/SD3.5 is available, consider migrating for better quality")
        print("   3. Check account balance to understand usage limits")
        print("   4. Review available engines to see what models you have access to\n")

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("   Make sure STABILITY_API_KEY is set in your .env file\n")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}\n")


if __name__ == '__main__':
    main()

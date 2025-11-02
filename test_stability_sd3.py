#!/usr/bin/env python3
"""
Test Stability AI SD3 endpoints with correct multipart/form-data format
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_sd3_multipart():
    """Test SD3 with multipart/form-data (correct format)"""

    api_key = os.getenv('STABILITY_API_KEY')
    if not api_key:
        print("❌ STABILITY_API_KEY not found")
        return

    print("\n" + "="*80)
    print("Testing SD3 with Multipart/Form-Data Format")
    print("="*80 + "\n")

    # Try SD3, Ultra, and Core endpoints
    endpoints = [
        ("SD3", "https://api.stability.ai/v2beta/stable-image/generate/sd3"),
        ("Stable Image Ultra", "https://api.stability.ai/v2beta/stable-image/generate/ultra"),
        ("Stable Image Core", "https://api.stability.ai/v2beta/stable-image/generate/core"),
    ]

    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*"  # Accept image response
    }

    # Use form-data format
    payload = {
        "prompt": "a cute robot, simple test",
        "output_format": "png",
        "aspect_ratio": "1:1"  # SD3 uses aspect ratio instead of width/height
    }

    for name, url in endpoints:
        try:
            print(f"📍 Testing {name}")
            print(f"   URL: {url}")
            print(f"   Format: multipart/form-data")
            print("   ⏳ Generating...")

            start = datetime.now()
            response = requests.post(
                url,
                headers=headers,
                files={"none": ''},  # Dummy file to make it multipart
                data=payload,
                timeout=60
            )
            elapsed = (datetime.now() - start).total_seconds()

            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                print(f"      Status: {response.status_code}")
                print(f"      Time: {elapsed:.2f}s")
                print(f"      Content-Type: {response.headers.get('content-type')}")
                print(f"      Image Size: {len(response.content)} bytes")

                # Save image
                filename = f"test_{name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"      Saved: {filename}\n")

            elif response.status_code == 403:
                print(f"   ⚠️  FORBIDDEN (403)")
                print(f"      Message: {response.text[:200]}")
                print(f"      Note: Your API key plan may not include this model\n")

            elif response.status_code == 402:
                print(f"   ⚠️  PAYMENT REQUIRED (402)")
                print(f"      Message: {response.text[:200]}")
                print(f"      Note: Insufficient credits or plan upgrade needed\n")

            else:
                print(f"   ❌ FAILED")
                print(f"      Status: {response.status_code}")
                print(f"      Response: {response.text[:200]}\n")

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}\n")


def test_sd3_parameters():
    """Test SD3 with all available parameters"""

    api_key = os.getenv('STABILITY_API_KEY')

    print("\n" + "="*80)
    print("Testing SD3 Advanced Parameters")
    print("="*80 + "\n")

    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*"
    }

    # Try with more parameters
    payload = {
        "prompt": "a friendly robot in pixar style, helping a child with homework",
        "negative_prompt": "blurry, low quality, distorted",
        "aspect_ratio": "1:1",
        "seed": 42,
        "output_format": "png",
        "model": "sd3-large"  # Try specifying model
    }

    try:
        print(f"📍 Testing SD3 with advanced parameters")
        print(f"   Prompt: {payload['prompt']}")
        print(f"   Negative: {payload['negative_prompt']}")
        print(f"   Model: {payload.get('model', 'default')}")
        print("   ⏳ Generating...")

        response = requests.post(
            url,
            headers=headers,
            files={"none": ''},
            data=payload,
            timeout=60
        )

        if response.status_code == 200:
            print(f"   ✅ SUCCESS with advanced parameters!")
            filename = f"test_sd3_advanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"   Saved: {filename}\n")
        else:
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}\n")

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}\n")


def main():
    print("\n🎨 STABILITY AI SD3/ULTRA/CORE TESTING")
    print("Testing newer models with correct API format\n")

    test_sd3_multipart()
    test_sd3_parameters()

    print("="*80)
    print("Summary:")
    print("- If SD3/Ultra/Core work: You have access to newer, better models!")
    print("- If 403 Forbidden: Your plan only includes SDXL 1.0")
    print("- If 402 Payment Required: Need credits or plan upgrade")
    print("- SDXL 1.0 still works great with 6,990 credits!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()

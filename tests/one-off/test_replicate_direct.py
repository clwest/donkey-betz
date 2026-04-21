#!/usr/bin/env python3
"""
Direct test of Replicate API with LoRA weights - Session 134
"""

import requests
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

# Get Replicate API key from settings
REPLICATE_API_KEY = settings.EXTERNAL_API_KEYS.get('REPLICATE_API_KEY')

headers = {
    "Authorization": f"Token {REPLICATE_API_KEY}",
    "Content-Type": "application/json"
}

# Payload for FLUX with LoRA
payload = {
    "version": "<redacted-85a7e01f-2026-04-20>",
    "input": {
        "prompt": "test robot image",
        "lora_weights": "clwest/ai-content-generation-company-style:bae61384a7977e46ca0e5172c89d17f851009b8ae539a84b02b637f752fa05f7",
        "lora_scale": 0.8,
        "width": 1024,
        "height": 1024,
        "num_outputs": 1,
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "output_format": "png",
        "output_quality": 100
    }
}

print("🔍 Testing Replicate API with LoRA weights...")
print(f"   Version: {payload['version']}")
print(f"   LoRA weights: {payload['input']['lora_weights']}")
print(f"   LoRA scale: {payload['input']['lora_scale']}")

response = requests.post(
    "https://api.replicate.com/v1/predictions",
    headers=headers,
    json=payload
)

print(f"\n📊 Response:")
print(f"   Status code: {response.status_code}")
print(f"   Response body: {response.text}")

#!/usr/bin/env python3
"""
Test script to verify FLUX LoRA training completion and test the model.

Training ID: 4xxb3efx91rm80ctkh6sag1mem
"""

import os
import sys
import django
import requests
from pathlib import Path

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from content.models import CharacterModel

def check_training_status():
    """Check the training status via Replicate API."""
    training_id = "4xxb3efx91rm80ctkh6sag1mem"

    print(f"🔍 Checking training status for: {training_id}")
    print("=" * 60)

    # Get training from database
    try:
        training = CharacterModel.objects.get(training_id=training_id)
        print(f"\n📊 Database Record:")
        print(f"   Status: {training.training_status}")
        print(f"   Model Name: {training.name}")
        print(f"   Description: {training.description[:100] if training.description else 'None'}")
        print(f"   Training Progress: {training.training_progress}%")
        print(f"   Created: {training.created_at}")
        print(f"   Updated: {training.updated_at}")

        if training.replicate_model_name:
            print(f"   Replicate Model: {training.replicate_model_name}")
        if training.replicate_version_id:
            print(f"   Version ID: {training.replicate_version_id}")
        if training.error_message:
            print(f"   Error: {training.error_message}")

    except CharacterModel.DoesNotExist:
        print(f"❌ Training {training_id} not found in database")
        return None

    # Check via Replicate API
    print(f"\n🌐 Checking Replicate API...")

    api_token = settings.EXTERNAL_API_KEYS.get('REPLICATE_API_KEY') or os.environ.get('REPLICATE_API_TOKEN')
    headers = {
        "Authorization": f"Token {api_token}",
        "Content-Type": "application/json"
    }

    url = f"https://api.replicate.com/v1/trainings/{training_id}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        print(f"\n✅ Replicate API Response:")
        print(f"   Status: {data.get('status')}")
        print(f"   Model: {data.get('model')}")

        if data.get('output'):
            print(f"\n🎨 Training Output:")
            output = data['output']
            if isinstance(output, dict):
                if 'version' in output:
                    print(f"   Version: {output['version']}")
                if 'weights' in output:
                    print(f"   Weights: {output['weights']}")
            else:
                print(f"   {output}")

        if data.get('logs'):
            print(f"\n📝 Recent logs:")
            logs = data['logs'].split('\n')[-10:]  # Last 10 lines
            for log in logs:
                if log.strip():
                    print(f"   {log}")

        return data

    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None


def test_generate_with_lora():
    """Generate a test image using the trained LoRA model."""
    training_id = "4xxb3efx91rm80ctkh6sag1mem"

    print("\n" + "=" * 60)
    print("🎨 Testing Image Generation with Trained LoRA")
    print("=" * 60)

    # Get training record
    try:
        training = CharacterModel.objects.get(training_id=training_id)

        if training.training_status != 'completed':
            print(f"⚠️  Training status is '{training.training_status}', not 'completed'")
            print("   Cannot generate images yet!")
            return

        if not training.replicate_version_id:
            print("⚠️  No version ID found for training")
            return

        print(f"\n✅ Training succeeded!")
        print(f"   Model Version: {training.replicate_version_id}")

        print("\n📋 To generate images using this LoRA model:")
        print("\n   Option 1: Via AI Assistant")
        print("   - Open your project modal")
        print("   - In the AI Assistant, say:")
        print('     "Generate an image using my trained style"')

        print("\n   Option 2: Via API")
        print("   - Use the FLUX model with the LoRA weights")
        print(f"   - Model version: {training.replicate_version_id}")

        print("\n   Option 3: Direct Replicate Call")
        print("   - Model: black-forest-labs/flux-1.1-pro")
        print(f"   - LoRA Version: {training.replicate_version_id}")

        # Try a test generation
        print("\n🚀 Attempting test generation...")

        api_token = settings.EXTERNAL_API_KEYS.get('REPLICATE_API_KEY') or os.environ.get('REPLICATE_API_TOKEN')
        headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }

        # Use FLUX with the trained LoRA
        payload = {
            "version": "85a7e01f60cf31fbb0d22c48f9719fa7f9f6ab8d",  # FLUX dev
            "input": {
                "prompt": "a professional logo design, modern and clean style",
                "lora_weights": training.replicate_version_id,
                "lora_scale": 0.8,
                "width": 1024,
                "height": 1024,
                "num_outputs": 1
            }
        }

        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 201:
            result = response.json()
            prediction_id = result.get('id')
            print(f"\n✅ Test generation started!")
            print(f"   Prediction ID: {prediction_id}")
            print(f"   Status: {result.get('status')}")
            print(f"\n   Check status at:")
            print(f"   https://replicate.com/p/{prediction_id}")

            return result
        else:
            print(f"\n❌ Generation failed: {response.status_code}")
            print(f"   {response.text}")

    except CharacterModel.DoesNotExist:
        print(f"❌ Training {training_id} not found in database")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check training status
    data = check_training_status()

    # If training succeeded, try generating
    if data and data.get('status') == 'succeeded':
        test_generate_with_lora()
    else:
        print("\n⏳ Training not yet complete or failed")

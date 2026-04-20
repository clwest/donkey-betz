#!/usr/bin/env python3
"""
Register Trained Creation Agent in UnifiedAgentTemplate - Session 135

This script creates the missing UnifiedAgentTemplate entry for 'trained-creation-agent'
so that agent contributions can be properly tracked.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate, AgentSpecialization

def register_trained_creation_agent():
    """Register the Trained Creation Agent in the unified agent registry."""

    print("=" * 80)
    print("🤖 Registering Trained Creation Agent - Session 135")
    print("=" * 80)
    print()

    # Check if agent already exists
    existing = UnifiedAgentTemplate.objects.filter(name='trained-creation-agent').first()
    if existing:
        print(f"⚠️  Agent already exists:")
        print(f"   Name: {existing.name}")
        print(f"   Display Name: {existing.display_name}")
        print(f"   Active: {existing.is_active}")
        print()

        # Ask if we should update
        response = input("Update existing agent? (y/n): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            return

        agent = existing
        print("📝 Updating existing agent...")
    else:
        print("✨ Creating new agent...")
        agent = UnifiedAgentTemplate(name='trained-creation-agent')

    # Set agent properties
    agent.display_name = 'Trained Creation Agent'
    agent.description = (
        'Generates images using trained FLUX LoRA models for consistent character and style generation. '
        'Supports custom character models trained through Replicate API, enabling brand-consistent imagery '
        'and character-driven content creation. Works with trigger words for voice-friendly model selection.'
    )
    agent.specialization = AgentSpecialization.CONTENT

    # Capabilities
    agent.capabilities = [
        'trained-image-generation',
        'lora-generation',
        'character-generation',
        'style-transfer',
        'brand-consistent-imagery',
        'trigger-word-matching'
    ]

    # Required tools
    agent.required_tools = [
        'replicate-api',
        'flux-lora',
        'image-storage'
    ]

    # Optional tools
    agent.optional_tools = [
        'upscaling',
        'background-removal',
        'image-editing'
    ]

    # System prompt
    agent.system_prompt = (
        "You are the Trained Creation Agent, specialized in generating images using trained FLUX LoRA models. "
        "Your expertise includes:\n"
        "- Generating consistent character images using custom LoRA weights\n"
        "- Matching user requests to trained models via trigger words\n"
        "- Creating brand-consistent imagery with style transfer\n"
        "- Managing generation parameters for optimal results\n"
        "\n"
        "You work closely with the Character Training Agent and Creation Agent to provide a complete "
        "image generation pipeline."
    )

    # Personality traits
    agent.personality_traits = {
        'style': 'precise',
        'tone': 'professional',
        'detail_level': 'high',
        'creativity': 'medium'
    }

    # LLM configuration
    agent.llm_provider = 'openai'
    agent.llm_model = 'gpt-5-mini'
    agent.llm_config = {
        'temperature': 0.7,
        'max_tokens': 1000
    }

    # Routing keywords
    agent.routing_keywords = [
        'trained model',
        'character model',
        'lora',
        'custom style',
        'brand style',
        'trained character',
        'trigger word',
        'consistent character'
    ]

    # Routing patterns (regex)
    agent.routing_patterns = [
        r'trained.*model',
        r'character.*model',
        r'lora.*generation',
        r'custom.*style',
        r'brand.*style'
    ]

    # Domain tags
    agent.domain_tags = [
        'content-creation',
        'image-generation',
        'character-design',
        'brand-identity',
        'ai-art'
    ]

    # Performance metrics (initial estimates)
    agent.confidence_score = 0.85
    agent.avg_completion_time = 60  # ~60 seconds average
    agent.success_rate = 0.95
    agent.estimated_cost_per_execution = 0.038  # ~$0.038 per generation

    # Advanced features
    agent.supports_streaming = False
    agent.supports_interruption = True
    agent.supports_collaboration = True
    agent.max_concurrent_executions = 3

    # Learning and self-improvement
    agent.learning_enabled = True
    agent.self_improvement_enabled = False

    # Public and verified
    agent.is_public = True
    agent.is_verified = True
    agent.is_active = True

    # Version
    agent.agent_version = '1.0.0'

    # Save to database
    try:
        agent.save()
        print()
        print("✅ Agent registered successfully!")
        print()
        print(f"   Name: {agent.name}")
        print(f"   Display Name: {agent.display_name}")
        print(f"   Specialization: {agent.specialization}")
        print(f"   Capabilities: {len(agent.capabilities)} capabilities")
        print(f"   Routing Keywords: {len(agent.routing_keywords)} keywords")
        print(f"   Active: {agent.is_active}")
        print()
        print("📊 Agent Contributions can now be tracked for Trained Creation Agent!")
        print("=" * 80)

    except Exception as e:
        print()
        print(f"❌ Error saving agent: {e}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    register_trained_creation_agent()

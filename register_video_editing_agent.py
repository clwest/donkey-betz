#!/usr/bin/env python3
"""
Register Video Editing Agent in UnifiedAgentTemplate database.

This agent handles video enhancement operations using ffmpeg.
Includes Session 154 features: upscaling (2x/4x), color grading effects.
Includes Session 155 features: agent metadata, UI status indicators, contribution tracking.
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate, AgentSpecialization

# Check if already exists
existing = UnifiedAgentTemplate.objects.filter(name='video-editing-agent').first()
if existing:
    print(f"⚠️  Agent already exists: {existing.name}")
    print(f"   Display Name: {existing.display_name}")
    print(f"   Specialization: {existing.specialization}")
    print(f"   Status: {'Active' if existing.is_active else 'Inactive'}")
    sys.exit(0)

# Create Video Editing Agent
agent = UnifiedAgentTemplate.objects.create(
    name='video-editing-agent',
    display_name='Video Editing Agent',
    description=(
        'Handles video enhancement and editing operations using ffmpeg. '
        'Session 154: Upscaling (2x/4x with lanczos), color grading (6 effects: '
        'cinematic, vibrant, vintage, noir, warm, cool). '
        'Session 155: Agent metadata for UI status indicators, contribution tracking. '
        'Supports batch operations for processing multiple videos at once. '
        'Cost-effective: Uses ffmpeg (free) instead of API calls.'
    ),
    system_prompt=(
        'You are a specialized Video Editing Agent that enhances videos using ffmpeg. '
        'You can upscale videos (2x or 4x resolution), apply professional color grading effects, '
        'and process multiple videos in batches. You use ffmpeg lanczos scaling for upscaling '
        'and advanced filter chains for color grading. All operations are free (no API costs).'
    ),
    specialization=AgentSpecialization.CONTENT,
    capabilities=[
        'video-upscaling',
        'color-grading',
        'ffmpeg-processing',
        'batch-operations',
        'lanczos-scaling',
        'cinematic-effects',
        'vintage-effects',
        'noir-effects',
        'temperature-adjustment'
    ],
    required_tools=[
        'ffmpeg',
        'video-storage'
    ],
    optional_tools=[
        'progress-indicator',
        'batch-processor'
    ],
    llm_provider='openai',
    llm_model='gpt-5-mini',
    is_active=True
)

print("✅ Successfully created Video Editing Agent!")
print(f"   Name: {agent.name}")
print(f"   Display Name: {agent.display_name}")
print(f"   Specialization: {agent.specialization}")
print(f"   Capabilities: {len(agent.capabilities)} total")
print(f"   Required Tools: {len(agent.required_tools)} total")
print(f"   LLM: {agent.llm_provider}/{agent.llm_model}")
print(f"   Status: {'Active' if agent.is_active else 'Inactive'}")

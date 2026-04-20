#!/usr/bin/env python3
"""
Session 131: Replace individual tools with agent orchestrators
"""

# Read the original file
with open('core/personal_ai_assistant_enhanced.py', 'r') as f:
    lines = f.readlines()

# Find the line numbers
start_line = None
end_line = None

for i, line in enumerate(lines):
    if '"name": "remove_background",' in line and start_line is None:
        # Go back to find the opening brace
        for j in range(i-1, -1, -1):
            if lines[j].strip() == '{':
                start_line = j
                break
    if '"name": "apply_color_grading",' in line:
        # Find the closing brace for this tool
        for j in range(i, len(lines)):
            if lines[j].strip() == '}' and lines[j+1].strip() == ']':
                end_line = j + 1  # Include the closing brace
                break
        break

print(f"Replacing lines {start_line} to {end_line}")
print(f"Old tools start: {lines[start_line]}")
print(f"Old tools end: {lines[end_line]}")

# The new agent tools (4 additional agents, since image_editing_agent is already done)
new_agents = '''
            # Session 131: Video Generation Agent (replaces 4 tools)
            {
                "type": "function",
                "name": "video_generation_agent",
                "description": "Handle all video generation operations: generate (create video from text), animate (transform image to moving video), extend (make video longer), chain (combine multiple videos). Use this agent for ANY video generation request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation: 'generate' | 'animate' | 'extend' | 'chain'",
                            "enum": ["generate", "animate", "extend", "chain"]
                        },
                        "params": {
                            "type": "object",
                            "description": "Operation-specific parameters. For generate: {prompt, duration}. For animate: {image_id, motion_prompt, duration}. For extend: {video_id, extension_seconds, prompt}. For chain: {video_ids, add_transitions}.",
                            "properties": {
                                "prompt": {"type": "string"},
                                "duration": {"type": "integer", "default": 5},
                                "image_id": {"type": "string"},
                                "motion_prompt": {"type": "string", "default": "natural motion"},
                                "video_id": {"type": "string"},
                                "extension_seconds": {"type": "integer", "default": 10},
                                "video_ids": {"type": "array", "items": {"type": "string"}},
                                "add_transitions": {"type": "boolean", "default": True}
                            }
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID"
                        }
                    },
                    "required": ["operation", "params"]
                }
            },

            # Session 131: Audio Generation Agent (replaces 2 tools)
            {
                "type": "function",
                "name": "audio_generation_agent",
                "description": "Handle all audio generation: generate_voice (text-to-speech), add_voiceover (add narration to video). Use this agent for ANY audio generation request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation: 'generate_voice' | 'add_voiceover'",
                            "enum": ["generate_voice", "add_voiceover"]
                        },
                        "params": {
                            "type": "object",
                            "description": "For generate_voice: {text, voice}. For add_voiceover: {video_id, text, voice}.",
                            "properties": {
                                "text": {"type": "string"},
                                "voice": {"type": "string", "default": "Rachel"},
                                "video_id": {"type": "string"}
                            }
                        },
                        "project_id": {"type": "string"}
                    },
                    "required": ["operation", "params"]
                }
            },

            # Session 131: 3D Generation Agent (replaces 1 tool)
            {
                "type": "function",
                "name": "three_d_generation_agent",
                "description": "Convert images to 3D models using Replicate TRELLIS. Creates downloadable GLB files for 3D printing. Use when users want: 'convert to 3D', 'make 3D model', '3D print', 'create 3D object'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation (currently only 'convert')",
                            "enum": ["convert"]
                        },
                        "image_id": {
                            "type": "string",
                            "description": "Image identifier: sequential number OR full UUID"
                        },
                        "project_id": {"type": "string"}
                    },
                    "required": ["operation", "image_id"]
                }
            },

            # Session 131: Video Editing Agent (replaces 2 tools)
            {
                "type": "function",
                "name": "video_editing_agent",
                "description": "Handle all video editing: add_text_overlay (captions/titles with timing), apply_color_grading (cinematic color effects). Use this agent for ANY video editing request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation: 'add_text_overlay' | 'apply_color_grading'",
                            "enum": ["add_text_overlay", "apply_color_grading"]
                        },
                        "video_id": {
                            "type": "string",
                            "description": "Video identifier: sequential number OR full UUID"
                        },
                        "params": {
                            "type": "object",
                            "description": "For add_text_overlay: {text, position, start_second, duration, font_size}. For apply_color_grading: {style}.",
                            "properties": {
                                "text": {"type": "string"},
                                "position": {"type": "string", "default": "center"},
                                "start_second": {"type": "number", "default": 0},
                                "duration": {"type": "number", "default": 3},
                                "font_size": {"type": "integer", "default": 72},
                                "style": {"type": "string", "default": "cinematic_warm"}
                            }
                        },
                        "project_id": {"type": "string"}
                    },
                    "required": ["operation", "video_id"]
                }
            }
'''

# Replace the section
new_lines = lines[:start_line] + [new_agents] + lines[end_line:]

# Write back
with open('core/personal_ai_assistant_enhanced.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Replacement complete!")
print(f"Removed {end_line - start_line} lines of old tools")
print(f"Added {len(new_agents.split(chr(10)))} lines of new agent tools")

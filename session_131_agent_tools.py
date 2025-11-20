"""
Session 131: Agent-Based Tool Definitions
This file contains the new agent orchestrator tool definitions that will replace the 14+ individual tools.
"""

AGENT_TOOLS = [
    # 1. Image Editing Agent (replaces 6 tools: upscale, remove_background, create_variations, erase_object, recolor, refine)
    {
        "type": "function",
        "name": "image_editing_agent",
        "description": "Handle all image editing operations: upscale (4x resolution), remove_background (transparent PNG), create_variations (multiple styles), erase_object (remove specific items), recolor (change colors), refine (enhance/modify). Use this agent for ANY image editing request.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform: 'upscale' | 'remove_background' | 'create_variations' | 'erase_object' | 'recolor' | 'refine'",
                    "enum": ["upscale", "remove_background", "create_variations", "erase_object", "recolor", "refine"]
                },
                "image_id": {
                    "type": "string",
                    "description": "Image identifier: use sequential number (e.g., '2' for Image #2) OR full UUID"
                },
                "params": {
                    "type": "object",
                    "description": "Operation-specific parameters. For erase_object: {object_description}. For recolor: {prompt}. For refine: {refinement_request}. For create_variations: {count}.",
                    "properties": {
                        "object_description": {"type": "string"},
                        "prompt": {"type": "string"},
                        "refinement_request": {"type": "string"},
                        "count": {"type": "integer", "default": 3}
                    }
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID to associate result with"
                }
            },
            "required": ["operation", "image_id"]
        }
    },

    # 2. Video Generation Agent (replaces 4 tools: generate_video, animate_image, extend_video, chain_videos)
    {
        "type": "function",
        "name": "video_generation_agent",
        "description": "Handle all video generation operations: generate (create video from text), animate (transform image to moving video), extend (make video longer), chain (combine multiple videos). Use this agent for ANY video generation request.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform: 'generate' | 'animate' | 'extend' | 'chain'",
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
                    "description": "Optional project ID to associate result with"
                }
            },
            "required": ["operation", "params"]
        }
    },

    # 3. Audio Generation Agent (replaces 2 tools: generate_voice, add_voiceover)
    {
        "type": "function",
        "name": "audio_generation_agent",
        "description": "Handle all audio generation operations: generate_voice (text-to-speech), add_voiceover (add narration to video). Use this agent for ANY audio generation request.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform: 'generate_voice' | 'add_voiceover'",
                    "enum": ["generate_voice", "add_voiceover"]
                },
                "params": {
                    "type": "object",
                    "description": "Operation-specific parameters. For generate_voice: {text, voice}. For add_voiceover: {video_id, text, voice}.",
                    "properties": {
                        "text": {"type": "string"},
                        "voice": {"type": "string", "default": "Rachel", "description": "Rachel, Drew, Clyde, Paul, Aria, Domi, Dave, Antoni, Sarah, Josh, Bella, Charlotte"},
                        "video_id": {"type": "string"}
                    }
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID to associate result with"
                }
            },
            "required": ["operation", "params"]
        }
    },

    # 4. 3D Generation Agent (replaces 1 tool: convert_to_3d)
    {
        "type": "function",
        "name": "three_d_generation_agent",
        "description": "Convert images to 3D models using Replicate TRELLIS. Creates downloadable GLB 3D model files perfect for 3D printing. Use this when users want to: 'convert to 3D', 'make 3D model', '3D print', 'create 3D object'.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform (currently only 'convert')",
                    "enum": ["convert"]
                },
                "image_id": {
                    "type": "string",
                    "description": "Image identifier: use sequential number (e.g., '2' for Image #2) OR full UUID"
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID to associate result with"
                }
            },
            "required": ["operation", "image_id"]
        }
    },

    # 5. Video Editing Agent (replaces 2 tools: add_text_overlay, apply_color_grading)
    {
        "type": "function",
        "name": "video_editing_agent",
        "description": "Handle all video editing operations: add_text_overlay (captions/titles with timing), apply_color_grading (cinematic color effects). Use this agent for ANY video editing request.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform: 'add_text_overlay' | 'apply_color_grading'",
                    "enum": ["add_text_overlay", "apply_color_grading"]
                },
                "video_id": {
                    "type": "string",
                    "description": "Video identifier: use sequential number OR full UUID"
                },
                "params": {
                    "type": "object",
                    "description": "Operation-specific parameters. For add_text_overlay: {text, position, start_second, duration, font_size}. For apply_color_grading: {style}.",
                    "properties": {
                        "text": {"type": "string"},
                        "position": {"type": "string", "default": "center", "enum": ["center", "lower_third", "upper_third"]},
                        "start_second": {"type": "number", "default": 0},
                        "duration": {"type": "number", "default": 3},
                        "font_size": {"type": "integer", "default": 72},
                        "style": {"type": "string", "default": "cinematic_warm", "enum": ["cinematic_warm", "cinematic_cool", "vintage", "modern", "high_contrast", "soft", "vibrant"]}
                    }
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID to associate result with"
                }
            },
            "required": ["operation", "video_id"]
        }
    }
]

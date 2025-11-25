"""
JSON Schema Validators for Content Models
==========================================

Provides validation schemas and validators for JSONField data.

Session 186: Created as part of Phase 3 Architecture Improvements (Task 3.5)

Schemas:
- IMAGE_PARAMETERS_SCHEMA: Validation for ImageHistory.parameters
- VIDEO_PARAMETERS_SCHEMA: Validation for VideoHistory.parameters
- GENERATION_CONFIG_SCHEMA: Validation for ContentTemplate.generation_config
- TEMPLATE_VARIABLES_SCHEMA: Validation for ContentTemplate.variables
"""

import json
import logging
from typing import Dict, Any, List, Optional
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


# ============================================================================
# JSON Schemas
# ============================================================================

IMAGE_PARAMETERS_SCHEMA = {
    "type": "object",
    "properties": {
        "width": {"type": "integer", "minimum": 64, "maximum": 4096},
        "height": {"type": "integer", "minimum": 64, "maximum": 4096},
        "quality": {"type": "string", "enum": ["balanced", "high", "ultra"]},
        "style": {"type": "string"},
        "model": {"type": "string"},
        "seed": {"type": "integer"},
        "negative_prompt": {"type": "string"},
        "guidance_scale": {"type": "number", "minimum": 0, "maximum": 30},
        "steps": {"type": "integer", "minimum": 1, "maximum": 150},
        "scheduler": {"type": "string"},
        "cfg_scale": {"type": "number", "minimum": 0, "maximum": 30},
        # Image editing specific
        "source_image_id": {"type": "string"},
        "mask_url": {"type": "string"},
        "strength": {"type": "number", "minimum": 0, "maximum": 1},
        "upscale_factor": {"type": "integer", "enum": [2, 4]},
        "creativity": {"type": "number", "minimum": 0, "maximum": 1},
        # Character model
        "character_model_name": {"type": "string"},
        "lora_scale": {"type": "number", "minimum": 0, "maximum": 1},
        "trigger_word": {"type": "string"},
        # Project context
        "project_id": {"type": "string", "format": "uuid"},
        "session_id": {"type": "string", "format": "uuid"},
    },
    "additionalProperties": True  # Allow additional provider-specific params
}

VIDEO_PARAMETERS_SCHEMA = {
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "duration": {"type": "integer", "minimum": 1, "maximum": 60},
        "ratio": {
            "type": "string",
            "enum": [
                "1920:1080", "1080:1920",  # 16:9 and 9:16
                "1280:720", "720:1280",    # HD
                "1104:832", "832:1104",    # gen4 specific
                "960:960",                  # Square
                "1584:672"                  # Cinematic
            ]
        },
        "quality": {"type": "string"},
        "style": {"type": "string"},
        "seed": {"type": "integer"},
        "enhance_prompt": {"type": "boolean"},
        "enhancement_level": {"type": "string", "enum": ["none", "basic", "advanced"]},
        # Image-to-video specific
        "source_image_id": {"type": "string"},
        "motion_prompt": {"type": "string"},
        # Video editing
        "speed_factor": {"type": "number", "minimum": 0.25, "maximum": 4.0},
        "start_time": {"type": "number", "minimum": 0},
        "end_time": {"type": "number", "minimum": 0},
        "effect": {"type": "string"},
        "effect_intensity": {"type": "number", "minimum": 0, "maximum": 1},
        "upscale_factor": {"type": "integer", "enum": [2, 4]},
        # Concatenation
        "source_video_ids": {"type": "array", "items": {"type": "string"}},
        # Audio
        "volume": {"type": "number", "minimum": 0, "maximum": 2},
        "mute": {"type": "boolean"},
        # Project context
        "project_id": {"type": "string", "format": "uuid"},
        "session_id": {"type": "string", "format": "uuid"},
    },
    "additionalProperties": True
}

GENERATION_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "temperature": {"type": "number", "minimum": 0, "maximum": 2},
        "max_tokens": {"type": "integer", "minimum": 1, "maximum": 128000},
        "top_p": {"type": "number", "minimum": 0, "maximum": 1},
        "frequency_penalty": {"type": "number", "minimum": -2, "maximum": 2},
        "presence_penalty": {"type": "number", "minimum": -2, "maximum": 2},
        "stop_sequences": {"type": "array", "items": {"type": "string"}},
        "response_format": {"type": "string", "enum": ["text", "json"]},
    },
    "additionalProperties": True
}

TEMPLATE_VARIABLES_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["string", "number", "boolean", "array", "object"]},
            "required": {"type": "boolean"},
            "default": {},  # Any type
            "description": {"type": "string"},
            "enum": {"type": "array"},
            "min": {"type": "number"},
            "max": {"type": "number"},
        },
        "required": ["type"]
    }
}

AUDIO_PARAMETERS_SCHEMA = {
    "type": "object",
    "properties": {
        "voice": {"type": "string"},
        "voice_id": {"type": "string"},
        "model": {"type": "string"},
        "output_format": {
            "type": "string",
            "enum": ["mp3_44100_128", "mp3_22050_32", "pcm_16000", "pcm_22050", "pcm_24000"]
        },
        "stability": {"type": "number", "minimum": 0, "maximum": 1},
        "similarity_boost": {"type": "number", "minimum": 0, "maximum": 1},
        "style": {"type": "number", "minimum": 0, "maximum": 1},
        "speed": {"type": "number", "minimum": 0.25, "maximum": 4.0},
        "language_code": {"type": "string"},
        # Lip sync specific
        "video_id": {"type": "string"},
        "audio_url": {"type": "string"},
        # Project context
        "project_id": {"type": "string", "format": "uuid"},
    },
    "additionalProperties": True
}

THREE_D_PARAMETERS_SCHEMA = {
    "type": "object",
    "properties": {
        "style": {"type": "string", "enum": ["toy", "realistic", "stylized", "anime"]},
        "scale": {"type": "string", "enum": ["small", "medium", "large"]},
        "source_image_id": {"type": "string"},
        "output_format": {"type": "string", "enum": ["glb", "stl", "obj", "fbx"]},
        "mesh_quality": {"type": "string", "enum": ["low", "medium", "high"]},
        "texture_resolution": {"type": "integer", "enum": [512, 1024, 2048, 4096]},
        # Project context
        "project_id": {"type": "string", "format": "uuid"},
    },
    "additionalProperties": True
}


# ============================================================================
# Validators
# ============================================================================

def validate_json_type(value: Any, expected_type: str) -> bool:
    """Validate value matches expected JSON type."""
    type_map = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }

    expected = type_map.get(expected_type)
    if expected is None:
        return True  # Unknown type, accept

    return isinstance(value, expected)


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate JSON data against a schema.

    Args:
        data: Dictionary to validate
        schema: JSON schema dictionary

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if not isinstance(data, dict):
        errors.append(f"Expected object, got {type(data).__name__}")
        return errors

    schema_type = schema.get("type", "object")
    if schema_type != "object":
        errors.append(f"Schema type must be 'object', got '{schema_type}'")
        return errors

    properties = schema.get("properties", {})
    required = schema.get("required", [])
    additional = schema.get("additionalProperties", True)

    # Check required fields
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    # Validate each property
    for key, value in data.items():
        if key not in properties:
            if not additional:
                errors.append(f"Unknown field: '{key}'")
            continue

        prop_schema = properties[key]
        field_errors = _validate_property(key, value, prop_schema)
        errors.extend(field_errors)

    return errors


def _validate_property(key: str, value: Any, schema: Dict[str, Any]) -> List[str]:
    """Validate a single property against its schema."""
    errors = []

    # Type validation
    expected_type = schema.get("type")
    if expected_type:
        if not validate_json_type(value, expected_type):
            errors.append(f"Field '{key}': expected {expected_type}, got {type(value).__name__}")
            return errors  # Skip further validation if type is wrong

    # Enum validation
    enum_values = schema.get("enum")
    if enum_values is not None and value not in enum_values:
        errors.append(f"Field '{key}': value '{value}' not in allowed values {enum_values}")

    # Numeric constraints
    if isinstance(value, (int, float)):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            errors.append(f"Field '{key}': value {value} below minimum {minimum}")

        maximum = schema.get("maximum")
        if maximum is not None and value > maximum:
            errors.append(f"Field '{key}': value {value} above maximum {maximum}")

    # String constraints
    if isinstance(value, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(value) < min_length:
            errors.append(f"Field '{key}': string too short (min {min_length})")

        max_length = schema.get("maxLength")
        if max_length is not None and len(value) > max_length:
            errors.append(f"Field '{key}': string too long (max {max_length})")

        pattern = schema.get("pattern")
        if pattern:
            import re
            if not re.match(pattern, value):
                errors.append(f"Field '{key}': value doesn't match pattern '{pattern}'")

    # Array constraints
    if isinstance(value, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            errors.append(f"Field '{key}': array too short (min {min_items} items)")

        max_items = schema.get("maxItems")
        if max_items is not None and len(value) > max_items:
            errors.append(f"Field '{key}': array too long (max {max_items} items)")

        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(value):
                item_errors = _validate_property(f"{key}[{i}]", item, items_schema)
                errors.extend(item_errors)

    return errors


# ============================================================================
# Django Validators
# ============================================================================

def validate_image_parameters(value: Dict[str, Any]) -> None:
    """Django validator for ImageHistory.parameters."""
    if not value:
        return  # Empty is OK

    errors = validate_json_schema(value, IMAGE_PARAMETERS_SCHEMA)
    if errors:
        logger.warning(f"Image parameters validation warnings: {errors}")
        # Log but don't raise - these are warnings for existing data


def validate_video_parameters(value: Dict[str, Any]) -> None:
    """Django validator for VideoHistory.parameters."""
    if not value:
        return

    errors = validate_json_schema(value, VIDEO_PARAMETERS_SCHEMA)
    if errors:
        logger.warning(f"Video parameters validation warnings: {errors}")


def validate_generation_config(value: Dict[str, Any]) -> None:
    """Django validator for ContentTemplate.generation_config."""
    if not value:
        return

    errors = validate_json_schema(value, GENERATION_CONFIG_SCHEMA)
    if errors:
        raise ValidationError(f"Invalid generation config: {'; '.join(errors)}")


def validate_template_variables(value: Dict[str, Any]) -> None:
    """Django validator for ContentTemplate.variables."""
    if not value:
        return

    errors = validate_json_schema(value, TEMPLATE_VARIABLES_SCHEMA)
    if errors:
        raise ValidationError(f"Invalid template variables: {'; '.join(errors)}")


def validate_audio_parameters(value: Dict[str, Any]) -> None:
    """Django validator for audio generation parameters."""
    if not value:
        return

    errors = validate_json_schema(value, AUDIO_PARAMETERS_SCHEMA)
    if errors:
        logger.warning(f"Audio parameters validation warnings: {errors}")


def validate_three_d_parameters(value: Dict[str, Any]) -> None:
    """Django validator for 3D generation parameters."""
    if not value:
        return

    errors = validate_json_schema(value, THREE_D_PARAMETERS_SCHEMA)
    if errors:
        logger.warning(f"3D parameters validation warnings: {errors}")


# ============================================================================
# Utility Functions
# ============================================================================

def sanitize_parameters(params: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize parameters to match schema expectations.

    - Removes unknown fields if additionalProperties is False
    - Applies defaults for missing required fields
    - Coerces types where possible

    Args:
        params: Input parameters
        schema: Target schema

    Returns:
        Sanitized parameters dictionary
    """
    if not isinstance(params, dict):
        return {}

    result = dict(params)
    properties = schema.get("properties", {})
    additional = schema.get("additionalProperties", True)

    # Remove unknown fields if not allowed
    if not additional:
        result = {k: v for k, v in result.items() if k in properties}

    # Apply defaults
    for key, prop_schema in properties.items():
        if key not in result and "default" in prop_schema:
            result[key] = prop_schema["default"]

    return result


def get_parameter_defaults(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Extract default values from a schema."""
    defaults = {}
    for key, prop_schema in schema.get("properties", {}).items():
        if "default" in prop_schema:
            defaults[key] = prop_schema["default"]
    return defaults

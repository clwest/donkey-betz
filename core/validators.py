"""
Centralized input validation utilities.
Phase 2 High Priority - Task 2.4

Provides validation functions for:
- Prompts and text input
- File paths and security
- URLs
- IDs (UUID and numeric)
- Numeric ranges
- Filename sanitization
"""

import re
import os
from typing import Optional, Tuple, Union, List
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Maximum lengths
MAX_PROMPT_LENGTH = 10000
MAX_FILENAME_LENGTH = 255
MAX_PATH_LENGTH = 4096
MAX_URL_LENGTH = 2048


# =============================================================================
# PROMPT VALIDATION
# =============================================================================

# Dangerous patterns that could indicate injection attempts (XSS prevention)
DANGEROUS_PATTERNS = [
    r'<script',                    # Script tags
    r'</script',                   # Closing script tags
    r'javascript:',                # JavaScript protocol
    r'on\w+\s*=',                  # Event handlers (onclick=, onerror=, etc.)
    r'data:\s*text/html',          # Data URI with HTML
    r'vbscript:',                  # VBScript protocol
    r'<iframe',                    # iframes
    r'<object',                    # object tags
    r'<embed',                     # embed tags
    r'<form',                      # form tags
    r'<input',                     # input tags
    r'<svg.*onload',               # SVG with onload
    r'<img.*onerror',              # IMG with onerror
    r'expression\s*\(',            # CSS expression
    r'url\s*\(\s*javascript',      # CSS with JavaScript
    r'&#x?[0-9a-fA-F]+;',         # HTML encoded characters
    r'%3C',                        # URL encoded <
    r'%3E',                        # URL encoded >
]


def validate_prompt(prompt: str, min_length: int = 1, max_length: int = MAX_PROMPT_LENGTH) -> Tuple[bool, Optional[str]]:
    """
    Validate AI prompt input.

    Args:
        prompt: User-provided prompt text
        min_length: Minimum required length (default 1)
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if prompt is None:
        return False, "Prompt cannot be None"

    if not isinstance(prompt, str):
        return False, "Prompt must be a string"

    prompt = prompt.strip()

    if not prompt:
        return False, "Prompt cannot be empty"

    if len(prompt) < min_length:
        return False, f"Prompt must be at least {min_length} characters"

    if len(prompt) > max_length:
        return False, f"Prompt exceeds maximum length of {max_length} characters"

    # Check for potential injection patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            logger.warning(f"Potentially dangerous pattern detected in prompt: {pattern}")
            return False, "Prompt contains potentially dangerous content"

    return True, None


def sanitize_prompt(prompt: str, max_length: int = MAX_PROMPT_LENGTH) -> str:
    """
    Sanitize a prompt by removing dangerous patterns and trimming.

    Args:
        prompt: User-provided prompt text
        max_length: Maximum allowed length

    Returns:
        Sanitized prompt string
    """
    if not prompt:
        return ""

    prompt = str(prompt).strip()

    # Remove dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        prompt = re.sub(pattern, '', prompt, flags=re.IGNORECASE)

    # Trim to max length
    if len(prompt) > max_length:
        prompt = prompt[:max_length]

    return prompt


def escape_html(text: str) -> str:
    """
    Escape HTML special characters to prevent XSS.

    Phase 2 P1: Use this when rendering user content in HTML contexts.

    Args:
        text: User-provided text that may contain HTML

    Returns:
        HTML-escaped text safe for rendering
    """
    if not text:
        return ""

    import html
    return html.escape(str(text), quote=True)


def sanitize_for_display(text: str, max_length: int = 1000) -> str:
    """
    Fully sanitize text for safe display to users.

    Phase 2 P1: Combines pattern removal and HTML escaping.

    Args:
        text: User-provided text
        max_length: Maximum length to return

    Returns:
        Sanitized and escaped text safe for display
    """
    if not text:
        return ""

    # First sanitize (remove dangerous patterns)
    text = sanitize_prompt(text, max_length)

    # Then HTML escape
    text = escape_html(text)

    return text


# =============================================================================
# FILE PATH VALIDATION
# =============================================================================

# Allowed image extensions
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']
ALLOWED_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.aac', '.ogg', '.m4a', '.flac']
ALLOWED_3D_EXTENSIONS = ['.glb', '.gltf', '.stl', '.obj', '.fbx']


def validate_file_path(
    path: str,
    must_exist: bool = False,
    allowed_extensions: List[str] = None,
    base_dir: str = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate file path for safety.

    Args:
        path: File path to validate
        must_exist: Whether the file must exist
        allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.png'])
        base_dir: Base directory path must be within (prevents traversal)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Path cannot be empty"

    if not isinstance(path, str):
        return False, "Path must be a string"

    if len(path) > MAX_PATH_LENGTH:
        return False, f"Path exceeds maximum length of {MAX_PATH_LENGTH}"

    # Normalize the path
    normalized = os.path.normpath(path)

    # Prevent path traversal attacks
    if '..' in path or '..' in normalized:
        return False, "Path traversal (..) not allowed"

    # Check if path stays within base directory
    if base_dir:
        base_dir = os.path.normpath(base_dir)
        if not normalized.startswith(base_dir):
            return False, "Path must be within allowed directory"

    # Check extension if specified
    if allowed_extensions:
        ext = os.path.splitext(path)[1].lower()
        if ext not in allowed_extensions:
            return False, f"File extension '{ext}' not allowed. Allowed: {allowed_extensions}"

    # Check existence if required
    if must_exist and not os.path.exists(path):
        return False, "File does not exist"

    return True, None


def validate_image_path(path: str, must_exist: bool = False, base_dir: str = None) -> Tuple[bool, Optional[str]]:
    """Validate path as an image file."""
    return validate_file_path(path, must_exist, ALLOWED_IMAGE_EXTENSIONS, base_dir)


def validate_video_path(path: str, must_exist: bool = False, base_dir: str = None) -> Tuple[bool, Optional[str]]:
    """Validate path as a video file."""
    return validate_file_path(path, must_exist, ALLOWED_VIDEO_EXTENSIONS, base_dir)


def validate_audio_path(path: str, must_exist: bool = False, base_dir: str = None) -> Tuple[bool, Optional[str]]:
    """Validate path as an audio file."""
    return validate_file_path(path, must_exist, ALLOWED_AUDIO_EXTENSIONS, base_dir)


# =============================================================================
# URL VALIDATION
# =============================================================================

ALLOWED_URL_SCHEMES = ['http', 'https']
DANGEROUS_URL_PATTERNS = [
    r'javascript:',
    r'data:',
    r'vbscript:',
    r'file:',
]


def validate_url(url: str, require_https: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate URL for safety.

    Args:
        url: URL to validate
        require_https: Whether to require HTTPS scheme

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"

    if not isinstance(url, str):
        return False, "URL must be a string"

    if len(url) > MAX_URL_LENGTH:
        return False, f"URL exceeds maximum length of {MAX_URL_LENGTH}"

    # Check for dangerous patterns
    for pattern in DANGEROUS_URL_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return False, f"URL contains disallowed scheme or pattern"

    try:
        parsed = urlparse(url)

        if not parsed.scheme:
            return False, "URL must have a scheme (http/https)"

        if parsed.scheme.lower() not in ALLOWED_URL_SCHEMES:
            return False, f"URL scheme must be http or https, got: {parsed.scheme}"

        if require_https and parsed.scheme.lower() != 'https':
            return False, "URL must use HTTPS"

        if not parsed.netloc:
            return False, "URL must have a host"

        return True, None

    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


# =============================================================================
# ID VALIDATION
# =============================================================================

UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)


def validate_uuid(value: str) -> Tuple[bool, Optional[str]]:
    """
    Validate UUID format.

    Args:
        value: String to validate as UUID

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value:
        return False, "UUID cannot be empty"

    if not isinstance(value, str):
        value = str(value)

    value = value.strip()

    if UUID_PATTERN.match(value):
        return True, None

    return False, "Invalid UUID format"


def validate_numeric_id(value: Union[str, int]) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate and convert numeric ID.

    Args:
        value: Value to validate as numeric ID

    Returns:
        Tuple of (is_valid, parsed_value, error_message)
    """
    try:
        if isinstance(value, int):
            num = value
        else:
            num = int(str(value).strip())

        if num < 1:
            return False, None, "ID must be a positive integer"

        return True, num, None

    except (ValueError, TypeError):
        return False, None, "Invalid numeric ID"


def validate_hybrid_id(value: Union[str, int]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate hybrid ID (UUID or numeric).

    Args:
        value: Value to validate

    Returns:
        Tuple of (is_valid, id_type ('uuid' or 'numeric'), error_message)
    """
    if not value:
        return False, None, "ID cannot be empty"

    value_str = str(value).strip()

    # Try UUID first
    if UUID_PATTERN.match(value_str):
        return True, 'uuid', None

    # Try numeric
    try:
        num = int(value_str)
        if num < 1:
            return False, None, "Numeric ID must be positive"
        return True, 'numeric', None
    except ValueError:
        pass

    return False, None, "ID must be a valid UUID or positive integer"


# =============================================================================
# NUMERIC RANGE VALIDATION
# =============================================================================

def validate_numeric_range(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    param_name: str = "Value"
) -> Tuple[bool, Optional[str]]:
    """
    Validate numeric value is within range.

    Args:
        value: Numeric value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        param_name: Name of parameter for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return False, f"{param_name} must be a number"

    if min_val is not None and value < min_val:
        return False, f"{param_name} must be at least {min_val}"

    if max_val is not None and value > max_val:
        return False, f"{param_name} must be at most {max_val}"

    return True, None


def validate_integer_range(
    value: Union[int, str],
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
    param_name: str = "Value"
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate and convert integer value within range.

    Args:
        value: Value to validate as integer
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        param_name: Name of parameter for error messages

    Returns:
        Tuple of (is_valid, parsed_value, error_message)
    """
    try:
        parsed = int(value)
    except (ValueError, TypeError):
        return False, None, f"{param_name} must be an integer"

    if min_val is not None and parsed < min_val:
        return False, None, f"{param_name} must be at least {min_val}"

    if max_val is not None and parsed > max_val:
        return False, None, f"{param_name} must be at most {max_val}"

    return True, parsed, None


# =============================================================================
# FILENAME SANITIZATION
# =============================================================================

# Characters not allowed in filenames
UNSAFE_FILENAME_CHARS = r'[<>:"/\\|?*\x00-\x1f]'


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"

    # Remove path components
    filename = os.path.basename(filename)

    # Remove dangerous characters
    filename = re.sub(UNSAFE_FILENAME_CHARS, '', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # If filename is empty after sanitization, provide default
    if not filename:
        filename = "unnamed"

    # Limit length
    if len(filename) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(filename)
        filename = name[:MAX_FILENAME_LENGTH - len(ext)] + ext

    return filename


# =============================================================================
# BATCH VALIDATION HELPERS
# =============================================================================

def validate_list_of_ids(
    ids: List[Union[str, int]],
    min_count: int = 1,
    max_count: int = 100
) -> Tuple[bool, Optional[List[str]], Optional[str]]:
    """
    Validate a list of IDs.

    Args:
        ids: List of IDs to validate
        min_count: Minimum number of IDs required
        max_count: Maximum number of IDs allowed

    Returns:
        Tuple of (is_valid, normalized_ids, error_message)
    """
    if not ids:
        return False, None, f"At least {min_count} ID(s) required"

    if not isinstance(ids, list):
        return False, None, "IDs must be provided as a list"

    if len(ids) < min_count:
        return False, None, f"At least {min_count} ID(s) required"

    if len(ids) > max_count:
        return False, None, f"Maximum {max_count} IDs allowed"

    normalized = []
    for i, id_val in enumerate(ids):
        is_valid, id_type, error = validate_hybrid_id(id_val)
        if not is_valid:
            return False, None, f"Invalid ID at position {i + 1}: {error}"
        normalized.append(str(id_val).strip())

    return True, normalized, None


# =============================================================================
# REQUEST DATA EXTRACTION WITH VALIDATION
# =============================================================================

def get_validated_string(
    data: dict,
    key: str,
    default: Optional[str] = None,
    required: bool = False,
    max_length: int = 1000
) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract and validate a string from request data.

    Args:
        data: Dictionary containing request data
        key: Key to extract
        default: Default value if not present
        required: Whether the field is required
        max_length: Maximum allowed length

    Returns:
        Tuple of (value, error_message)
    """
    value = data.get(key)

    if value is None:
        if required:
            return None, f"'{key}' is required"
        return default, None

    if not isinstance(value, str):
        value = str(value)

    value = value.strip()

    if required and not value:
        return None, f"'{key}' cannot be empty"

    if len(value) > max_length:
        return None, f"'{key}' exceeds maximum length of {max_length}"

    return value, None


def get_validated_int(
    data: dict,
    key: str,
    default: Optional[int] = None,
    required: bool = False,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None
) -> Tuple[Optional[int], Optional[str]]:
    """
    Extract and validate an integer from request data.

    Args:
        data: Dictionary containing request data
        key: Key to extract
        default: Default value if not present
        required: Whether the field is required
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Tuple of (value, error_message)
    """
    value = data.get(key)

    if value is None:
        if required:
            return None, f"'{key}' is required"
        return default, None

    try:
        value = int(value)
    except (ValueError, TypeError):
        return None, f"'{key}' must be an integer"

    if min_val is not None and value < min_val:
        return None, f"'{key}' must be at least {min_val}"

    if max_val is not None and value > max_val:
        return None, f"'{key}' must be at most {max_val}"

    return value, None


def get_validated_float(
    data: dict,
    key: str,
    default: Optional[float] = None,
    required: bool = False,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> Tuple[Optional[float], Optional[str]]:
    """
    Extract and validate a float from request data.

    Args:
        data: Dictionary containing request data
        key: Key to extract
        default: Default value if not present
        required: Whether the field is required
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Tuple of (value, error_message)
    """
    value = data.get(key)

    if value is None:
        if required:
            return None, f"'{key}' is required"
        return default, None

    try:
        value = float(value)
    except (ValueError, TypeError):
        return None, f"'{key}' must be a number"

    if min_val is not None and value < min_val:
        return None, f"'{key}' must be at least {min_val}"

    if max_val is not None and value > max_val:
        return None, f"'{key}' must be at most {max_val}"

    return value, None

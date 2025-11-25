# Core utilities package
#
# Session 186: Consolidated exports for Task 3.8 Utility Consolidation
#
# Temporary file management
from .temp_files import temp_file, temp_directory, temp_file_from_content, TempFileManager

# ID resolution and parsing
from .id_resolver import (
    resolve_content_id,
    resolve_image_id,
    resolve_video_id,
    resolve_project_id,
    parse_identifier,
    parse_id_range,
    extract_ids_from_text
)

# URL validation and SSRF protection
from .url_validator import (
    validate_url,
    validate_url_for_download,
    validate_url_permissive,
    is_private_ip,
    get_allowed_domains,
)

__all__ = [
    # Temp files
    'temp_file',
    'temp_directory',
    'temp_file_from_content',
    'TempFileManager',
    # ID resolution
    'resolve_content_id',
    'resolve_image_id',
    'resolve_video_id',
    'resolve_project_id',
    'parse_identifier',
    'parse_id_range',
    'extract_ids_from_text',
    # URL validation
    'validate_url',
    'validate_url_for_download',
    'validate_url_permissive',
    'is_private_ip',
    'get_allowed_domains',
]

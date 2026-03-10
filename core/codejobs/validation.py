"""Code Job change validation logic.

Extracted from core/tasks.py to keep that file manageable.
All original behaviour and return values are preserved.
"""

from __future__ import annotations

import logging
from typing import Any

from core.codejobs.errors import (
    CODEJOB_ANCHOR_NOT_FOUND,
    CODEJOB_FILE_TOO_LARGE,
    CodeJobValidationError,
)

logger = logging.getLogger(__name__)

# Maximum file size (in bytes) permitted for code-job patch operations.
MAX_CODEJOB_FILE_SIZE = 1_700_000  # ~1.65 MB guard-rail


def validate_file_size(content: "str | bytes", filename: str = "<unknown>") -> None:
    """Raise CodeJobValidationError(CODEJOB_FILE_TOO_LARGE) when *content* exceeds
    MAX_CODEJOB_FILE_SIZE.

    Parameters
    ----------
    content:
        The raw file content (str or bytes).
    filename:
        Used only for the error detail message.
    """
    size = len(content) if isinstance(content, (str, bytes)) else 0
    if size > MAX_CODEJOB_FILE_SIZE:
        raise CodeJobValidationError(
            failure_code=CODEJOB_FILE_TOO_LARGE,
            message=(
                f"File '{filename}' is {size} bytes which exceeds the "
                f"maximum allowed size of {MAX_CODEJOB_FILE_SIZE} bytes."
            ),
            details={"filename": filename, "size": size, "max_size": MAX_CODEJOB_FILE_SIZE},
        )


def validate_anchor_present(content: str, anchor: str, filename: str = "<unknown>") -> None:
    """Raise CodeJobValidationError(CODEJOB_ANCHOR_NOT_FOUND) when *anchor* is not
    found inside *content*.

    Parameters
    ----------
    content:
        Current file content as a string.
    anchor:
        The exact text that must be present before the change can be applied.
    filename:
        Used only for the error detail message.
    """
    if anchor not in content:
        raise CodeJobValidationError(
            failure_code=CODEJOB_ANCHOR_NOT_FOUND,
            message=(
                f"Anchor text not found in '{filename}'. "
                f"The file may have changed since the patch was generated."
            ),
            details={"filename": filename, "anchor_preview": anchor[:120]},
        )


def validate_codejob_change(
    filename: str,
    current_content: str,
    anchor: "str | None" = None,
    *,
    check_size: bool = True,
) -> "dict[str, Any]":
    """High-level convenience validator combining size and anchor checks.

    Returns a result dict ``{"valid": True}`` on success, or
    ``{"valid": False, "failure_code": ..., "message": ...}`` on failure.

    This never raises; callers that want exceptions should call the
    individual validators directly.
    """
    try:
        if check_size:
            validate_file_size(current_content, filename)
        if anchor is not None:
            validate_anchor_present(current_content, anchor, filename)
    except CodeJobValidationError as exc:
        logger.warning(
            "CodeJob validation failed for '%s': %s (%s)",
            filename,
            exc.message,
            exc.failure_code,
        )
        return {"valid": False, **exc.to_dict()}

    return {"valid": True}

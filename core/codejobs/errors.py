"""Centralized error types and failure codes for Code Job validation."""

# Guardrail failure codes
CODEJOB_FILE_TOO_LARGE = "CODEJOB_FILE_TOO_LARGE"
CODEJOB_ANCHOR_NOT_FOUND = "CODEJOB_ANCHOR_NOT_FOUND"
CODEJOB_INVALID_CHANGE = "CODEJOB_INVALID_CHANGE"
CODEJOB_PATCH_CONFLICT = "CODEJOB_PATCH_CONFLICT"

# Human-readable messages for each failure code
FAILURE_MESSAGES = {
    CODEJOB_FILE_TOO_LARGE: "File exceeds maximum allowed size for code job changes.",
    CODEJOB_ANCHOR_NOT_FOUND: "Anchor text not found in the target file.",
    CODEJOB_INVALID_CHANGE: "The proposed change is invalid or malformed.",
    CODEJOB_PATCH_CONFLICT: "The patch conflicts with the current file state.",
}


class CodeJobValidationError(Exception):
    """Raised when a code job change fails validation."""

    def __init__(self, failure_code: str, message: str = None, details: dict = None):
        self.failure_code = failure_code
        self.message = message or FAILURE_MESSAGES.get(failure_code, "Validation failed.")
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "failure_code": self.failure_code,
            "message": self.message,
            "details": self.details,
        }


class CodeJobError(RuntimeError):
    """Base exception for CodeJob pipeline failures with structured error codes.

    Used by the execute_code_job task to map exceptions to failure reason codes.
    The .code attribute is read by the except handler in the task's outer try/except.
    """
    code: str = 'CODEJOB_ERROR'

    def __init__(self, message: str, **context):
        self.context = context
        super().__init__(f'{self.code}: {message}')


class CodeJobAnchorNotFoundError(CodeJobError):
    """Raised when a patch search string is not found in the target file."""
    code = CODEJOB_ANCHOR_NOT_FOUND


class CodeJobFileTooLargeError(CodeJobError):
    """Raised when a target file exceeds the size limit for safe editing."""
    code = CODEJOB_FILE_TOO_LARGE

"""
User-Friendly Error Messages

Provides clear, actionable error messages for common API and system errors.
Created in Session 89 to improve user experience.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ErrorMessageBuilder:
    """Build user-friendly error messages with actionable guidance"""

    @staticmethod
    def api_key_error(service_name: str, key_var_name: str) -> Dict[str, str]:
        """
        Generate user-friendly API key error message

        Args:
            service_name: Name of the service (e.g., "Stability AI", "Runway ML")
            key_var_name: Environment variable name (e.g., "STABILITY_API_KEY")

        Returns:
            Dict with title, message, and action
        """
        return {
            "title": f"🔑 {service_name} API Key Invalid",
            "message": f"Your {service_name} API key is missing, invalid, or expired.",
            "action": f"Please check your {key_var_name} in settings and ensure it's valid.",
            "help_url": "/docs/setup#api-keys",
            "user_message": f"API key issue: Please verify your {service_name} API key in settings."
        }

    @staticmethod
    def insufficient_credits_error(
        service_name: str,
        credits_needed: Optional[int] = None,
        credits_remaining: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Generate user-friendly insufficient credits error

        Args:
            service_name: Name of the service
            credits_needed: Credits required for operation
            credits_remaining: Credits currently available

        Returns:
            Dict with title, message, and action
        """
        if credits_needed and credits_remaining is not None:
            detail = f"You need {credits_needed} credits but have {credits_remaining} remaining."
        else:
            detail = "You don't have enough credits for this operation."

        return {
            "title": f"💳 Insufficient {service_name} Credits",
            "message": detail,
            "action": f"Add more credits to your {service_name} account to continue.",
            "help_url": f"/docs/{service_name.lower().replace(' ', '-')}/pricing",
            "user_message": f"Insufficient credits: {detail} Please add credits to your {service_name} account."
        }

    @staticmethod
    def rate_limit_error(
        service_name: str,
        limit: Optional[str] = None,
        retry_after: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Generate user-friendly rate limit error

        Args:
            service_name: Name of the service
            limit: Rate limit description (e.g., "5 requests/minute")
            retry_after: Seconds to wait before retrying

        Returns:
            Dict with title, message, and action
        """
        if retry_after:
            wait_msg = f"Please wait {retry_after} seconds and try again."
        elif limit:
            wait_msg = f"You've hit the rate limit ({limit}). Please wait a moment and try again."
        else:
            wait_msg = "You've made too many requests. Please wait a moment and try again."

        return {
            "title": f"⏱️ {service_name} Rate Limit Reached",
            "message": wait_msg,
            "action": "Wait a moment before making another request, or upgrade your plan for higher limits.",
            "retry_after": retry_after,
            "user_message": f"Rate limit: {wait_msg}"
        }

    @staticmethod
    def timeout_error(
        operation: str,
        timeout_seconds: int,
        will_continue: bool = True
    ) -> Dict[str, str]:
        """
        Generate user-friendly timeout error

        Args:
            operation: Name of operation (e.g., "Video generation", "Character training")
            timeout_seconds: Timeout duration in seconds
            will_continue: Whether operation will continue in background

        Returns:
            Dict with title, message, and action
        """
        if will_continue:
            action = "We'll continue processing and notify you when complete. Check back in a few minutes."
        else:
            action = "Please try again. If the issue persists, try reducing complexity or contact support."

        return {
            "title": f"⏰ {operation} Taking Longer Than Expected",
            "message": f"{operation} is taking longer than {timeout_seconds}s.",
            "action": action,
            "will_continue": will_continue,
            "user_message": f"Timeout: {operation} is taking longer than expected. " +
                           ("We'll notify you when complete." if will_continue else "Please try again.")
        }

    @staticmethod
    def content_policy_error(
        service_name: str,
        flagged_terms: Optional[list] = None,
        reason: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate user-friendly content policy error

        Args:
            service_name: Name of the service
            flagged_terms: List of terms that triggered policy
            reason: Specific reason for rejection

        Returns:
            Dict with title, message, and action
        """
        if flagged_terms:
            detail = f"Your prompt contains potentially sensitive terms: {', '.join(flagged_terms)}"
            action = f"Try removing these words: {', '.join(flagged_terms)}"
        elif reason:
            detail = f"Your request was rejected: {reason}"
            action = "Please modify your prompt and try again."
        else:
            detail = "Your prompt was rejected by content policy filters."
            action = "Please use appropriate language and try again."

        return {
            "title": f"🚫 {service_name} Content Policy Violation",
            "message": detail,
            "action": action,
            "help_url": "/docs/content-policy",
            "user_message": f"Content policy: {detail} {action}"
        }

    @staticmethod
    def network_error(service_name: str, status_code: Optional[int] = None) -> Dict[str, str]:
        """
        Generate user-friendly network error

        Args:
            service_name: Name of the service
            status_code: HTTP status code if available

        Returns:
            Dict with title, message, and action
        """
        if status_code:
            if status_code >= 500:
                detail = f"{service_name} is experiencing technical difficulties (error {status_code})."
                action = "This is a temporary issue. Please try again in a few moments."
            elif status_code == 404:
                detail = "The requested resource was not found."
                action = "Please check your request and try again, or contact support."
            else:
                detail = f"Request failed with error {status_code}."
                action = "Please try again. If the issue persists, contact support."
        else:
            detail = f"Unable to connect to {service_name}."
            action = "Please check your internet connection and try again."

        return {
            "title": f"🌐 {service_name} Connection Error",
            "message": detail,
            "action": action,
            "status_code": status_code,
            "user_message": f"Connection error: {detail} {action}"
        }

    @staticmethod
    def validation_error(field_name: str, issue: str, suggestion: str) -> Dict[str, str]:
        """
        Generate user-friendly validation error

        Args:
            field_name: Name of the field with validation issue
            issue: Description of the validation issue
            suggestion: Suggestion for fixing the issue

        Returns:
            Dict with title, message, and action
        """
        return {
            "title": f"⚠️ Invalid {field_name}",
            "message": f"{field_name}: {issue}",
            "action": suggestion,
            "user_message": f"Validation error in {field_name}: {issue}. {suggestion}"
        }

    @staticmethod
    def parse_api_error(
        service_name: str,
        status_code: int,
        response_text: str
    ) -> Dict[str, str]:
        """
        Parse API error response and generate user-friendly message

        Args:
            service_name: Name of the service
            status_code: HTTP status code
            response_text: Raw response text from API

        Returns:
            Dict with title, message, and action
        """
        # Check for common error patterns
        response_lower = response_text.lower()

        # Authentication errors
        if status_code == 401 or status_code == 403:
            if 'key' in response_lower or 'token' in response_lower:
                return ErrorMessageBuilder.api_key_error(service_name, f"{service_name.upper().replace(' ', '_')}_API_KEY")

        # Credit/payment errors
        if status_code == 402 or 'credit' in response_lower or 'payment' in response_lower:
            return ErrorMessageBuilder.insufficient_credits_error(service_name)

        # Rate limit errors
        if status_code == 429 or 'rate limit' in response_lower or 'too many' in response_lower:
            return ErrorMessageBuilder.rate_limit_error(service_name)

        # Content policy errors
        if 'content' in response_lower and ('policy' in response_lower or 'filter' in response_lower):
            return ErrorMessageBuilder.content_policy_error(service_name)

        # Server errors
        if status_code >= 500:
            return ErrorMessageBuilder.network_error(service_name, status_code)

        # Generic error
        return ErrorMessageBuilder.network_error(service_name, status_code)

    @staticmethod
    def format_for_api(error_dict: Dict[str, str]) -> Dict[str, str]:
        """
        Format error dictionary for API response

        Args:
            error_dict: Error dictionary from builder methods

        Returns:
            Dict formatted for JSON API response
        """
        return {
            "success": False,
            "error": error_dict.get("user_message", error_dict.get("message", "An error occurred")),
            "error_title": error_dict.get("title"),
            "error_action": error_dict.get("action"),
            "error_help_url": error_dict.get("help_url"),
            "retry_after": error_dict.get("retry_after")
        }


# Convenience functions for common errors
def api_key_error(service: str, key_var: str) -> Dict[str, str]:
    """Generate API key error"""
    return ErrorMessageBuilder.format_for_api(
        ErrorMessageBuilder.api_key_error(service, key_var)
    )


def insufficient_credits(service: str, needed: int = None, remaining: int = None) -> Dict[str, str]:
    """Generate insufficient credits error"""
    return ErrorMessageBuilder.format_for_api(
        ErrorMessageBuilder.insufficient_credits_error(service, needed, remaining)
    )


def rate_limit_error(service: str, limit: str = None, retry_after: int = None) -> Dict[str, str]:
    """Generate rate limit error"""
    return ErrorMessageBuilder.format_for_api(
        ErrorMessageBuilder.rate_limit_error(service, limit, retry_after)
    )


def timeout_error(operation: str, timeout: int, continues: bool = True) -> Dict[str, str]:
    """Generate timeout error"""
    return ErrorMessageBuilder.format_for_api(
        ErrorMessageBuilder.timeout_error(operation, timeout, continues)
    )


def content_policy_error(service: str, terms: list = None, reason: str = None) -> Dict[str, str]:
    """Generate content policy error"""
    return ErrorMessageBuilder.format_for_api(
        ErrorMessageBuilder.content_policy_error(service, terms, reason)
    )


def parse_api_error(service: str, status_code: int, response: str) -> Dict[str, str]:
    """Parse API error and generate user-friendly message"""
    return ErrorMessageBuilder.format_for_api(
        ErrorMessageBuilder.parse_api_error(service, status_code, response)
    )

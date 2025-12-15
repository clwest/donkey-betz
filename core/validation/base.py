# core/validation/base.py
"""
Base Validation Agent

Provides common functionality for all section validators.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from django.utils import timezone
from django.test import Client

logger = logging.getLogger(__name__)


@dataclass
class ValidationCheck:
    """Result of a single validation check."""
    name: str
    passed: bool
    message: str
    duration_ms: float = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'pass': self.passed,
            'message': self.message,
            'duration_ms': self.duration_ms,
            'details': self.details,
        }


class BaseValidationAgent(ABC):
    """
    Base class for all section validation agents.

    Subclasses must implement:
    - section_name: Name of the section being validated
    - run_checks(): Run all validation checks for the section
    """

    section_name: str = "base"

    def __init__(self, user=None):
        """
        Initialize the validator.

        Args:
            user: Optional user for authenticated requests. If None, creates test user.
        """
        self.user = user
        # Use SERVER_NAME=localhost to avoid DisallowedHost errors
        self.client = Client(SERVER_NAME='localhost')
        self.results: List[ValidationCheck] = []

        # Setup authenticated client if user provided
        if self.user:
            self.client.force_login(self.user)

    def validate_all(self) -> dict:
        """
        Run all validation checks and return results.

        Returns:
            dict with status, checks list, and timestamp
        """
        self.results = []
        start_time = datetime.now()

        try:
            self.run_checks()
        except Exception as e:
            logger.error(f"Validation error in {self.section_name}: {e}")
            self.results.append(ValidationCheck(
                name="validation_execution",
                passed=False,
                message=f"Validation failed: {str(e)}"
            ))

        # Determine overall status
        all_passed = all(r.passed for r in self.results)
        any_passed = any(r.passed for r in self.results)

        if all_passed:
            status = "healthy"
        elif any_passed:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            'section': self.section_name,
            'status': status,
            'checks': [r.to_dict() for r in self.results],
            'summary': {
                'total': len(self.results),
                'passed': sum(1 for r in self.results if r.passed),
                'failed': sum(1 for r in self.results if not r.passed),
            },
            'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
            'timestamp': timezone.now().isoformat(),
        }

    @abstractmethod
    def run_checks(self):
        """
        Run all validation checks for this section.

        Subclasses must implement this method and call self.add_check()
        for each validation check performed.
        """
        pass

    def add_check(self, name: str, passed: bool, message: str,
                  duration_ms: float = 0, details: Dict = None):
        """Add a validation check result."""
        self.results.append(ValidationCheck(
            name=name,
            passed=passed,
            message=message,
            duration_ms=duration_ms,
            details=details or {}
        ))

    def check_endpoint(self, path: str, method: str = 'GET',
                       expected_status: int = 200, data: dict = None,
                       name: str = None) -> bool:
        """
        Check if an endpoint responds correctly.

        Args:
            path: URL path to check
            method: HTTP method (GET, POST, etc.)
            expected_status: Expected HTTP status code
            data: Optional data for POST requests
            name: Optional name for the check

        Returns:
            True if endpoint responded with expected status
        """
        check_name = name or f"endpoint_{path.replace('/', '_')}"
        start = datetime.now()

        try:
            if method.upper() == 'GET':
                response = self.client.get(path)
            elif method.upper() == 'POST':
                response = self.client.post(path, data or {})
            else:
                response = getattr(self.client, method.lower())(path, data or {})

            duration = (datetime.now() - start).total_seconds() * 1000
            passed = response.status_code == expected_status

            self.add_check(
                name=check_name,
                passed=passed,
                message=f"{method} {path} -> {response.status_code}",
                duration_ms=duration,
                details={
                    'method': method,
                    'path': path,
                    'expected': expected_status,
                    'actual': response.status_code,
                }
            )
            return passed

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            self.add_check(
                name=check_name,
                passed=False,
                message=f"Error: {str(e)}",
                duration_ms=duration,
                details={'error': str(e)}
            )
            return False

    def check_model_count(self, model_class, min_count: int = 0,
                          name: str = None, filters: dict = None) -> bool:
        """
        Check if a model has expected minimum records.

        Args:
            model_class: Django model class
            min_count: Minimum expected record count
            name: Optional name for the check
            filters: Optional queryset filters

        Returns:
            True if count meets minimum
        """
        check_name = name or f"model_{model_class.__name__}_count"

        try:
            queryset = model_class.objects.all()
            if filters:
                queryset = queryset.filter(**filters)
            count = queryset.count()

            passed = count >= min_count

            self.add_check(
                name=check_name,
                passed=passed,
                message=f"{model_class.__name__}: {count} records (min: {min_count})",
                details={
                    'model': model_class.__name__,
                    'count': count,
                    'min_required': min_count,
                }
            )
            return passed

        except Exception as e:
            self.add_check(
                name=check_name,
                passed=False,
                message=f"Error: {str(e)}",
                details={'error': str(e)}
            )
            return False

    def check_import(self, module_path: str, class_name: str = None,
                     name: str = None) -> bool:
        """
        Check if a module/class can be imported.

        Args:
            module_path: Python module path (e.g., 'core.agents')
            class_name: Optional class name to import from module
            name: Optional name for the check

        Returns:
            True if import succeeds
        """
        check_name = name or f"import_{module_path.replace('.', '_')}"

        try:
            import importlib
            module = importlib.import_module(module_path)

            if class_name:
                obj = getattr(module, class_name)
                self.add_check(
                    name=check_name,
                    passed=True,
                    message=f"Successfully imported {module_path}.{class_name}",
                )
            else:
                self.add_check(
                    name=check_name,
                    passed=True,
                    message=f"Successfully imported {module_path}",
                )
            return True

        except Exception as e:
            self.add_check(
                name=check_name,
                passed=False,
                message=f"Import failed: {str(e)}",
                details={'error': str(e)}
            )
            return False

    def check_api_key(self, key_name: str, name: str = None) -> bool:
        """
        Check if an API key is configured.

        Args:
            key_name: Name of the setting (e.g., 'OPENAI_API_KEY')
            name: Optional name for the check

        Returns:
            True if key is set and non-empty
        """
        from django.conf import settings

        check_name = name or f"api_key_{key_name}"

        try:
            # Check in settings directly
            value = getattr(settings, key_name, None)

            # Also check EXTERNAL_API_KEYS dict
            if not value and hasattr(settings, 'EXTERNAL_API_KEYS'):
                value = settings.EXTERNAL_API_KEYS.get(key_name)

            passed = bool(value)

            self.add_check(
                name=check_name,
                passed=passed,
                message=f"{key_name}: {'configured' if passed else 'NOT SET'}",
                details={'key_name': key_name, 'is_set': passed}
            )
            return passed

        except Exception as e:
            self.add_check(
                name=check_name,
                passed=False,
                message=f"Error checking key: {str(e)}",
                details={'error': str(e)}
            )
            return False

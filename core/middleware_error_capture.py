"""
Session 1069: HTTP error capture middleware.
Pipes Django 500 errors into FailureDetection/FailureSignature so they
appear in the PA's error_summary_tool automatically.
"""
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
import logging

logger = logging.getLogger(__name__)


class RequestErrorCaptureMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        try:
            from core.models_diagnostic_pipeline import FailureSignature, FailureDetection

            path = request.path
            exc_type = type(exception).__name__
            sig_str = f"HTTP_500_{exc_type}_{path}"
            sig_hash = FailureSignature.generate_hash(sig_str)

            signature, _ = FailureSignature.objects.get_or_create(
                signature_hash=sig_hash,
                defaults={
                    'signature': sig_str[:255],
                    'category': FailureSignature.Category.EXECUTION_ERROR,
                    'error_code': '500',
                    'description': f"{exc_type} in {request.method} {path}",
                }
            )
            signature.increment_occurrence()

            FailureDetection.objects.create(
                signature=signature,
                source_type='http_request',
                error_type=exc_type,
                error_message=str(exception)[:1000],
                metadata={
                    'method': request.method,
                    'path': path,
                    'user_id': getattr(request.user, 'id', None),
                    'view': _resolve_view_name(request),
                },
            )
        except Exception:
            logger.warning("RequestErrorCaptureMiddleware failed", exc_info=True)
        return None


def _resolve_view_name(request):
    try:
        match = resolve(request.path)
        return f"{match.func.__module__}.{match.func.__name__}"
    except Exception:
        return 'unknown'

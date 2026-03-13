"""
Preview System — Celery Tasks

TTL enforcement for preview environments and periodic cleanup.
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    name="cleanup_expired_preview_environments",
    queue="default",
    ignore_result=True,
    max_retries=1,
)
def cleanup_expired_preview_environments():
    """
    Find expired preview environments and mark them as destroyed.
    Expires their magic links and logs the cleanup.
    Runs on default queue (lightweight DB work only).
    """
    from core.models_preview_system import MagicLink, PreviewEnvironment

    expired = PreviewEnvironment.objects.filter(
        ttl_expires_at__lt=timezone.now(),
        status__in=[
            PreviewEnvironment.Status.PROVISIONING,
            PreviewEnvironment.Status.READY,
        ],
    )

    count = 0
    for env in expired:
        # Expire all magic links
        env.magic_links.filter(expires_at__gt=timezone.now()).update(
            expires_at=timezone.now()
        )

        # Mark as destroyed
        env.status = PreviewEnvironment.Status.DESTROYED
        env.save(update_fields=["status", "updated_at"])

        logger.info(
            "Preview env '%s' (project: %s) auto-destroyed (TTL expired at %s)",
            env.name,
            env.project.name,
            env.ttl_expires_at,
        )
        count += 1

    if count > 0:
        logger.info("Cleaned up %d expired preview environments", count)

    return {"destroyed": count}


@shared_task(
    name="destroy_preview_provider_resources",
    queue="long_running",
    ignore_result=True,
    max_retries=3,
    default_retry_delay=30,
)
def destroy_preview_provider_resources(preview_env_id: str):
    """
    Tear down provider resources (Vercel deployments, Railway services)
    for a destroyed preview environment.
    Runs on long_running queue (external API calls).
    """
    from core.models_preview_system import PreviewEnvironment, PreviewService
    from core.services.preview_deploy_service import get_provider

    try:
        env = PreviewEnvironment.objects.get(id=preview_env_id)
    except PreviewEnvironment.DoesNotExist:
        logger.warning("Preview env %s not found for resource cleanup", preview_env_id)
        return

    for service in env.services.all():
        if not service.provider_metadata or service.provider_metadata.get("stub"):
            continue

        try:
            repo = service.repo
            provider = get_provider(repo.build_system)
            provider.destroy(service.provider_metadata)
            logger.info(
                "Destroyed provider resources for %s (%s)",
                service.service_type, repo.name,
            )
        except Exception as e:
            logger.error(
                "Failed to destroy provider resources for %s: %s",
                service.service_type, e,
            )

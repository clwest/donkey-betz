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


@shared_task(
    name="vip_exchange_smoke_test",
    queue="default",
    ignore_result=True,
    max_retries=0,
)
def vip_exchange_smoke_test():
    """
    Prod smoke sentinel: verify VIP magic link exchange is publicly accessible.

    Creates a test invite, exchanges it unauthenticated, validates the response,
    then cleans up. Alerts via logging if the exchange fails.

    Runs every 6 hours to catch auth middleware regressions early.
    """
    import requests
    import os

    base_url = os.environ.get(
        "VIP_SMOKE_BASE_URL",
        os.environ.get("RAILWAY_PUBLIC_DOMAIN", ""),
    )

    if not base_url:
        logger.info("[VIP Smoke] No base URL configured, skipping")
        return {"skipped": True, "reason": "no_base_url"}

    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"

    # Step 1: Create a test invite (using model directly, not API)
    from core.models_vip_invite import VIPInvite
    from django.contrib.auth import get_user_model
    User = get_user_model()

    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        logger.warning("[VIP Smoke] No admin user found, skipping")
        return {"skipped": True, "reason": "no_admin"}

    invite = VIPInvite.objects.create(
        created_by=admin,
        label="[smoke-test] Auto-generated — safe to delete",
    )

    # Step 2: Exchange unauthenticated
    try:
        resp = requests.post(
            f"{base_url}/api/v1/vip-invites/exchange/",
            json={"token": invite.token},
            timeout=15,
        )
    except requests.RequestException as e:
        logger.error("[VIP Smoke] FAIL — exchange request failed: %s", e)
        # Clean up
        invite.delete()
        return {"success": False, "error": f"request_failed: {e}"}

    # Step 3: Validate response
    if resp.status_code == 200:
        data = resp.json()
        has_key = "api_key" in data and len(data.get("api_key", "")) == 40
        has_role = data.get("role") == "vip_demo_viewer"

        if has_key and has_role:
            logger.info("[VIP Smoke] PASS — exchange returned valid api_key")

            # Clean up: deactivate the smoke test user
            try:
                vip_user = User.objects.get(username=data["username"])
                vip_user.is_active = False
                vip_user.save(update_fields=["is_active"])
            except User.DoesNotExist:
                pass

            return {"success": True, "username": data["username"]}
        else:
            logger.error(
                "[VIP Smoke] FAIL — response missing api_key or wrong role: %s",
                data,
            )
            return {"success": False, "error": "invalid_response_shape", "data": data}
    else:
        body = resp.text[:500]
        logger.error(
            "[VIP Smoke] FAIL — exchange returned %d: %s", resp.status_code, body,
        )
        # Clean up unused invite
        invite.delete()
        return {"success": False, "error": f"status_{resp.status_code}", "body": body}

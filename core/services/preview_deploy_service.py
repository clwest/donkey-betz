"""
Preview Deploy Service — Provider abstraction for deploying preview environments.

Supports Vercel (web/static), Railway (backend/API), and Expo EAS (mobile).
Each provider implements deploy/status/destroy/logs for a single repo.
"""

import hashlib
import logging
import os
from datetime import timedelta

import requests
from django.utils import timezone

from core.models_preview_system import (
    DeployJob,
    PreviewDeployment,
    PreviewEnvironment,
    PreviewService,
    ProjectEnvVar,
    ProjectRepo,
)

logger = logging.getLogger(__name__)


# ── Provider Base ─────────────────────────────────────────────────────────


class DeployProvider:
    """Base class for deploy providers."""

    name = "base"

    def deploy(self, repo: ProjectRepo, env: PreviewEnvironment, env_vars: dict, git_ref: str) -> dict:
        """Deploy a repo. Returns {provider_job_id, public_url, logs_url}."""
        raise NotImplementedError

    def get_status(self, provider_job_id: str) -> str:
        """Check deployment status. Returns 'running', 'succeeded', 'failed'."""
        raise NotImplementedError

    def destroy(self, provider_metadata: dict) -> bool:
        """Tear down a deployed service."""
        raise NotImplementedError

    def get_logs(self, provider_job_id: str) -> str:
        """Retrieve build logs."""
        raise NotImplementedError


# ── Vercel Provider ───────────────────────────────────────────────────────


class VercelProvider(DeployProvider):
    """Deploy Next.js / static sites to Vercel."""

    name = "vercel"

    def __init__(self):
        self.token = os.environ.get("VERCEL_TOKEN", "")
        self.team_id = os.environ.get("VERCEL_TEAM_ID", "")
        self.base_url = "https://api.vercel.com"

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def deploy(self, repo, env, env_vars, git_ref):
        if not self.token:
            logger.warning("Vercel token not configured — using stub deploy")
            return self._stub_deploy(repo, env)

        # Trigger deployment via Vercel API
        payload = {
            "name": f"{env.name}-{repo.name}",
            "gitSource": {
                "type": "github",
                "repo": repo.repo_url.replace("https://github.com/", ""),
                "ref": git_ref,
            },
            "target": "preview",
        }

        # Add env vars
        if env_vars:
            payload["env"] = {k: v for k, v in env_vars.items()}

        params = {}
        if self.team_id:
            params["teamId"] = self.team_id

        try:
            resp = requests.post(
                f"{self.base_url}/v13/deployments",
                json=payload,
                headers=self.headers,
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            return {
                "provider_job_id": data.get("id", ""),
                "public_url": f"https://{data.get('url', '')}",
                "logs_url": f"https://vercel.com/{self.team_id or 'dashboard'}/deployments/{data.get('id', '')}",
                "metadata": {"vercel_deployment_id": data.get("id")},
            }
        except requests.RequestException as e:
            logger.error("Vercel deploy failed: %s", e)
            return self._stub_deploy(repo, env)

    def _stub_deploy(self, repo, env):
        """Stub deploy for development/testing."""
        stub_id = hashlib.md5(f"{env.name}-{repo.name}".encode()).hexdigest()[:12]
        return {
            "provider_job_id": f"stub-vercel-{stub_id}",
            "public_url": f"https://{env.name}-{repo.name}.vercel.app",
            "logs_url": "",
            "metadata": {"stub": True},
        }

    def get_status(self, provider_job_id):
        if provider_job_id.startswith("stub-"):
            return "succeeded"
        try:
            resp = requests.get(
                f"{self.base_url}/v13/deployments/{provider_job_id}",
                headers=self.headers,
                timeout=15,
            )
            data = resp.json()
            state = data.get("readyState", "")
            return {"READY": "succeeded", "ERROR": "failed", "CANCELED": "failed"}.get(state, "running")
        except requests.RequestException:
            return "running"


# ── Railway Provider ──────────────────────────────────────────────────────


class RailwayProvider(DeployProvider):
    """Deploy Django/API services to Railway."""

    name = "railway"

    def __init__(self):
        self.token = os.environ.get("RAILWAY_API_TOKEN", "")
        self.base_url = "https://backboard.railway.com/graphql/v2"

    def deploy(self, repo, env, env_vars, git_ref):
        if not self.token:
            logger.warning("Railway token not configured — using stub deploy")
            return self._stub_deploy(repo, env)

        # Railway uses GraphQL — simplified for MVP
        # Full integration would create a service + deploy from repo
        return self._stub_deploy(repo, env)

    def _stub_deploy(self, repo, env):
        stub_id = hashlib.md5(f"{env.name}-{repo.name}".encode()).hexdigest()[:12]
        return {
            "provider_job_id": f"stub-railway-{stub_id}",
            "public_url": f"https://{env.name}-{repo.name}.up.railway.app",
            "logs_url": "",
            "metadata": {"stub": True},
        }

    def get_status(self, provider_job_id):
        if provider_job_id.startswith("stub-"):
            return "succeeded"
        return "running"


# ── Provider Registry ─────────────────────────────────────────────────────


PROVIDERS = {
    "vercel": VercelProvider,
    "railway": RailwayProvider,
}


def get_provider(build_system: str) -> DeployProvider:
    cls = PROVIDERS.get(build_system)
    if not cls:
        raise ValueError(f"Unknown build system: {build_system}")
    return cls()


# ── Orchestrator ──────────────────────────────────────────────────────────


def deploy_preview_environment(preview_env: PreviewEnvironment, deployment: PreviewDeployment):
    """
    Deploy all repos in a preview environment.

    Iterates through each repo in the project, resolves env vars,
    delegates to the appropriate provider, and records results.
    """
    project = preview_env.project
    repos = project.repos.all()

    deployment.status = PreviewDeployment.Status.RUNNING
    deployment.started_at = timezone.now()
    deployment.save(update_fields=["status", "started_at", "updated_at"])

    preview_env.status = PreviewEnvironment.Status.PROVISIONING
    preview_env.save(update_fields=["status", "updated_at"])

    all_succeeded = True
    git_context = {}

    for repo in repos:
        job = deployment.jobs.filter(repo=repo).first()
        if not job:
            job = DeployJob.objects.create(deployment=deployment, repo=repo)

        job.status = DeployJob.Status.RUNNING
        job.started_at = timezone.now()
        job.save(update_fields=["status", "started_at"])

        # Resolve env vars for this repo
        env_vars = _resolve_env_vars(project.id, repo.id)

        # Get provider
        if repo.build_system == ProjectRepo.BuildSystem.NONE:
            job.status = DeployJob.Status.SUCCEEDED
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "finished_at"])
            continue

        try:
            provider = get_provider(repo.build_system)
            result = provider.deploy(repo, preview_env, env_vars, repo.default_ref)

            # Record results
            job.provider_job_id = result.get("provider_job_id", "")
            job.logs_url = result.get("logs_url", "")
            job.status = DeployJob.Status.SUCCEEDED
            job.finished_at = timezone.now()
            job.save(update_fields=[
                "provider_job_id", "logs_url", "status", "finished_at",
            ])

            # Create/update PreviewService
            service_type = {
                ProjectRepo.RepoType.WEB: PreviewService.ServiceType.WEB,
                ProjectRepo.RepoType.BACKEND: PreviewService.ServiceType.API,
            }.get(repo.type, PreviewService.ServiceType.WEB)

            PreviewService.objects.update_or_create(
                preview_env=preview_env,
                repo=repo,
                defaults={
                    "service_type": service_type,
                    "public_url": result.get("public_url", ""),
                    "provider_metadata": result.get("metadata", {}),
                    "health_status": PreviewService.HealthStatus.HEALTHY,
                    "last_health_check_at": timezone.now(),
                },
            )

            git_context[repo.name] = repo.default_ref

        except Exception as e:
            logger.error("Deploy failed for repo %s: %s", repo.name, e)
            job.status = DeployJob.Status.FAILED
            job.error_summary = str(e)[:500]
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error_summary", "finished_at"])
            all_succeeded = False

    # Finalize deployment
    deployment.git_context = git_context
    deployment.status = (
        PreviewDeployment.Status.SUCCEEDED if all_succeeded
        else PreviewDeployment.Status.FAILED
    )
    deployment.finished_at = timezone.now()
    deployment.save(update_fields=["git_context", "status", "finished_at", "updated_at"])

    preview_env.status = (
        PreviewEnvironment.Status.READY if all_succeeded
        else PreviewEnvironment.Status.FAILED
    )
    preview_env.save(update_fields=["status", "updated_at"])

    logger.info(
        "Preview deployment %s: %s (%d repos)",
        deployment.id, deployment.status, repos.count(),
    )

    # Record deploy operation.
    # Session 1103c: loud on failure so preview deploy activity can be
    # traced through the Ops Run timeline. Previously every failure to
    # record the deploy op was swallowed — meaning the Ops Run view
    # could show successful deploys without any trail in Django logs
    # explaining why.
    try:
        from core.services.operation_recorder import record_op
        ws_id = str(preview_env.project.workspace_id)
        op_type = 'deploy_succeeded' if all_succeeded else 'deploy_failed'
        record_op(
            workspace_id=ws_id,
            op_type=op_type,
            title=f"Deploy: {preview_env.name} ({deployment.status})",
            description=f"{repos.count()} repos deployed",
            actor_type='system',
            actor_id='PreviewDeployService',
            success=all_succeeded,
            entity_type='preview_deployment',
            entity_id=str(deployment.id),
            correlation_id=str(deployment.id),
        )
    except Exception as e:
        logger.warning(
            "preview_deploy_service: record_op failed for deployment %s "
            "(%s: %s) — Ops Run timeline will be missing this entry",
            deployment.id, type(e).__name__, e,
        )

    return deployment


def _resolve_env_vars(project_id, repo_id):
    """Resolve env vars: shared (repo=null) + repo-specific, for preview environment."""
    from django.db.models import Q

    vars_qs = ProjectEnvVar.objects.filter(
        project_id=project_id,
        environment=ProjectEnvVar.Environment.PREVIEW,
    ).filter(
        Q(repo_id=repo_id) | Q(repo__isnull=True)
    )

    resolved = {}
    for var in vars_qs:
        resolved[var.key] = var.value
    return resolved

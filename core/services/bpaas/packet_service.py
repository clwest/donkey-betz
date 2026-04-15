"""
BPaaS Packet Service — Orchestrates the build packet → project pipeline.

Takes a validated build packet and:
1. Creates a WorkspaceProject with repos
2. Sets up default env vars
3. Creates initial preview environment + magic link
4. Generates the close pack (SOW, delivery checklist)
"""

import logging
import uuid
from datetime import timedelta

from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)


def create_project_from_packet(workspace, packet: dict, created_by=None) -> dict:
    """
    Create a full BPaaS project from a build packet spec.

    Returns dict with project, repos, preview_env, magic_link details.
    """
    from core.models_preview_system import (
        MagicLink,
        PreviewEnvironment,
        ProjectEnvVar,
        ProjectRepo,
        WorkspaceProject,
    )

    project_spec = packet.get("project", {})
    name = project_spec.get("name", "Untitled Project")
    slug = project_spec.get("slug") or slugify(name)

    # 1. Create WorkspaceProject
    project = WorkspaceProject.objects.create(
        workspace=workspace,
        name=name,
        slug=slug,
        description=project_spec.get("problem_statement", ""),
    )
    logger.info("BPaaS: Created project '%s' (id=%s)", name, project.id)

    # 2. Create repos based on tech stack + users
    tech = packet.get("tech_stack", {})
    repos_created = []

    # Determine which surfaces are needed
    users = packet.get("users", [])
    needs_web = any(u.get("platform") in ("web", "both") for u in users)
    needs_mobile = any(u.get("platform") in ("mobile", "both") for u in users)
    needs_backend = True  # Always need a backend

    if needs_backend:
        backend_repo = ProjectRepo.objects.create(
            project=project,
            name=f"{slug}-backend",
            repo_url=f"https://github.com/clwest/{slug}",
            type=ProjectRepo.RepoType.BACKEND,
            build_system=_map_hosting(tech.get("hosting", ""), "backend"),
            output_kind=ProjectRepo.OutputKind.SERVICE,
        )
        repos_created.append(backend_repo)

    if needs_web:
        web_repo = ProjectRepo.objects.create(
            project=project,
            name=f"{slug}-web",
            repo_url=f"https://github.com/clwest/{slug}",
            type=ProjectRepo.RepoType.WEB,
            build_system=_map_hosting(tech.get("hosting", ""), "web"),
            output_kind=ProjectRepo.OutputKind.STATIC_SITE,
        )
        repos_created.append(web_repo)

    if needs_mobile:
        mobile_repo = ProjectRepo.objects.create(
            project=project,
            name=f"{slug}-mobile",
            repo_url=f"https://github.com/clwest/{slug}",
            type=ProjectRepo.RepoType.MOBILE,
            build_system=ProjectRepo.BuildSystem.EAS,
            output_kind=ProjectRepo.OutputKind.MOBILE_ARTIFACT,
        )
        repos_created.append(mobile_repo)

    # 3. Set up default env vars from integrations
    integrations = packet.get("integrations", [])
    for integration in integrations:
        service = integration.get("service", "").upper().replace(" ", "_")
        if service == "STRIPE":
            ProjectEnvVar.objects.create(
                project=project, key="STRIPE_SECRET_KEY", value="sk_test_...",
                environment="preview", is_secret=True,
            )
            ProjectEnvVar.objects.create(
                project=project, key="STRIPE_WEBHOOK_SECRET", value="whsec_...",
                environment="preview", is_secret=True,
            )

    # Brand info as shared env vars
    brand = packet.get("brand", {})
    if brand.get("business_name"):
        ProjectEnvVar.objects.create(
            project=project, key="BUSINESS_NAME",
            value=brand["business_name"], environment="preview",
        )

    # 4. Create initial preview environment
    preview_env = PreviewEnvironment.objects.create(
        project=project,
        name=f"preview-{slug}-initial",
        status=PreviewEnvironment.Status.PROVISIONING,
        ttl_expires_at=timezone.now() + timedelta(hours=72),
        created_by=created_by,
    )

    # 5. Create initial magic link for client review
    raw_token, token_hash = MagicLink.generate_token()
    magic_link = MagicLink.objects.create(
        preview_env=preview_env,
        token_hash=token_hash,
        label=f"{name} — Client Review",
        scope=MagicLink.Scope.REVIEW,
        expires_at=timezone.now() + timedelta(hours=72),
        created_by=created_by,
    )

    result = {
        "project": {
            "id": str(project.id),
            "name": project.name,
            "slug": project.slug,
        },
        "repos": [
            {"id": str(r.id), "name": r.name, "type": r.type}
            for r in repos_created
        ],
        "preview_env": {
            "id": str(preview_env.id),
            "name": preview_env.name,
        },
        "magic_link": {
            "id": str(magic_link.id),
            "label": magic_link.label,
            "raw_token": raw_token,
            "review_url": f"/r/{raw_token}",
            "expires_at": magic_link.expires_at.isoformat(),
        },
        "acceptance_criteria": packet.get("acceptance_criteria", []),
        "screens_count": len(packet.get("screens", [])),
        "flows_count": len(packet.get("flows", [])),
        "integrations": [i.get("service") for i in integrations],
    }

    logger.info(
        "BPaaS: Project '%s' fully provisioned — %d repos, preview env, magic link ready",
        name, len(repos_created),
    )

    # Record operations for each BPaaS step
    try:
        from core.services.operation_recorder import record_op
        ws_id = str(workspace.id)
        record_op(
            workspace_id=ws_id, op_type='bpaas_project_create',
            title=f"BPaaS: Created project '{name}'",
            description=f"{len(repos_created)} repos, preview env, magic link",
            actor_type='system', actor_id='BPaaS',
            entity_type='workspace_project', entity_id=str(project.id),
        )
        for repo in repos_created:
            record_op(
                workspace_id=ws_id, op_type='bpaas_project_create',
                title=f"BPaaS: Created repo '{repo.name}' ({repo.type})",
                actor_type='system', actor_id='BPaaS',
                entity_type='project_repo', entity_id=str(repo.id),
            )
        record_op(
            workspace_id=ws_id, op_type='preview_env_create',
            title=f"Preview: Created '{preview_env.name}'",
            actor_type='system', actor_id='BPaaS',
            entity_type='preview_environment', entity_id=str(preview_env.id),
        )
        record_op(
            workspace_id=ws_id, op_type='magic_link_create',
            title=f"Magic link: '{magic_link.label}'",
            actor_type='system', actor_id='BPaaS',
            entity_type='magic_link', entity_id=str(magic_link.id),
        )
    except Exception as e:
        # Session 1103c: loud on failure so BPaaS packet creation
        # activity is traceable through the Ops Run timeline.
        logger.warning(
            "bpaas.packet_service: record_op chain failed for "
            "preview_env=%s (%s: %s) — Ops Run timeline entries "
            "for repo/env/magic_link may be incomplete",
            getattr(preview_env, 'id', '<unknown>'),
            type(e).__name__, e,
        )

    return result


def generate_close_pack(packet: dict) -> dict:
    """
    Generate close pack documents from a build packet.

    Returns structured content for SOW, delivery checklist, and proposal.
    """
    project = packet.get("project", {})
    name = project.get("name", "Project")
    criteria = packet.get("acceptance_criteria", [])
    flows = packet.get("flows", [])
    screens = packet.get("screens", [])
    integrations = packet.get("integrations", [])
    timeline = packet.get("timeline", {})
    out_of_scope = packet.get("out_of_scope", [])

    # SOW
    sow = {
        "title": f"Statement of Work — {name}",
        "sections": {
            "project_overview": project.get("problem_statement", ""),
            "deliverables": [
                f"Backend API ({_count_by(screens, 'platform', 'mobile') + _count_by(screens, 'platform', 'web')} endpoints)",
                *[f"Web: {s['name']}" for s in screens if s.get("platform") in ("web", "both")],
                *[f"Mobile: {s['name']}" for s in screens if s.get("platform") in ("mobile", "both")],
                *[f"Integration: {i['service']}" for i in integrations if i.get("mvp_required")],
                "Preview environment with client review portal",
                "Seed demo data for testing",
            ],
            "acceptance_criteria": criteria,
            "timeline": timeline.get("target_delivery", "2 weeks"),
            "out_of_scope": out_of_scope,
            "revision_policy": "2 rounds of feedback included. Additional revisions billed at hourly rate.",
            "payment_terms": "50% deposit to start, 50% on delivery acceptance.",
        },
    }

    # Delivery checklist
    checklist = {
        "title": f"Delivery Checklist — {name}",
        "items": [
            {"category": "Setup", "items": [
                "GitHub repo created",
                "Local dev environment documented",
                "Docker Compose / DB setup",
                "CI/CD pipeline configured",
            ]},
            {"category": "Backend", "items": [
                "Data models implemented",
                "API endpoints functional",
                *[f"Integration: {i['service']} wired" for i in integrations if i.get("mvp_required")],
                "Admin panel configured",
                "Email notifications working",
            ]},
            {"category": "Frontend", "items": [
                *[f"Screen: {s['name']}" for s in screens],
                "Responsive design verified",
                "Error states handled",
            ]},
            {"category": "Acceptance", "items": [
                *[f"✓ {c}" for c in criteria],
            ]},
            {"category": "Delivery", "items": [
                "Preview environment deployed",
                "Magic link generated for client",
                "Demo data seeded",
                "Client feedback round completed",
                "Final fixes applied",
                "Handoff documentation delivered",
            ]},
        ],
    }

    # Proposal summary
    proposal = {
        "title": f"Proposal — {name}",
        "problem": project.get("problem_statement", ""),
        "solution_summary": f"Full-stack {project.get('business_type', 'application')} with {len(screens)} screens across {_platforms(screens)}, {len(flows)} core workflows, and {len(integrations)} integrations.",
        "key_flows": [f.get("name") for f in flows],
        "timeline": timeline.get("target_delivery", "2 weeks"),
        "includes": [
            "Full-stack development (backend + web + mobile as needed)",
            "Hosted preview environment with live URL",
            "Client review portal with feedback capture",
            "2 rounds of revision based on feedback",
            "Seed demo data for testing",
            "Deployment-ready codebase with documentation",
        ],
        "excludes": out_of_scope,
    }

    return {
        "sow": sow,
        "checklist": checklist,
        "proposal": proposal,
    }


def _map_hosting(hosting: str, surface: str) -> str:
    """Map hosting preference to build system."""
    if "vercel" in hosting and surface == "web":
        return "vercel"
    if "railway" in hosting and surface == "backend":
        return "railway"
    if "fly" in hosting:
        return "flyio"
    return "none"


def _count_by(items: list, key: str, value: str) -> int:
    return sum(1 for i in items if i.get(key) == value)


def _platforms(screens: list) -> str:
    platforms = set()
    for s in screens:
        p = s.get("platform", "")
        if p == "both":
            platforms.update(["web", "mobile"])
        elif p:
            platforms.add(p)
    return " + ".join(sorted(platforms))

"""Manual dispatcher for `start_resolve_render` — Session 1115 batch-7.

The DaVinci Resolve render task (`core.tasks.start_resolve_render`,
Session 478) is invoked from this management command. It had no
schedulable cadence (renders are user-initiated) but also no caller
path inside the codebase, leaving it flagged as orphan. Wrapping in
a same-name management command (1) gives operators a real way to
kick a render off without writing Python and (2) lets the audit's
"same-name CLI" caller detector attribute the task correctly.

Usage::

    python manage.py start_resolve_render \\
        --job-id <uuid> --video-ids id1,id2 \\
        --template default --color-grade neutral \\
        [--user-id <int>]
"""

from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Manually dispatch start_resolve_render for a DaVinci Resolve job."

    def add_arguments(self, parser):
        parser.add_argument(
            "--job-id",
            required=True,
            help="UUID/string identifier of the resolve render job.",
        )
        parser.add_argument(
            "--video-ids",
            required=True,
            help="Comma-separated list of video IDs to render.",
        )
        parser.add_argument(
            "--template",
            required=True,
            help="Render template (e.g. 'default', 'short_form').",
        )
        parser.add_argument(
            "--color-grade",
            required=True,
            help="Color grade preset name (see resolve_node/color_grades.py).",
        )
        parser.add_argument(
            "--spider-trends",
            default="",
            help="Optional JSON string of spider trend context.",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            default=None,
            help="Optional user id for ownership/attribution.",
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Run synchronously instead of dispatching to Celery.",
        )

    def handle(self, *args, **opts):
        from core.tasks import start_resolve_render

        job_id: str = opts["job_id"]
        video_ids = [v.strip() for v in opts["video_ids"].split(",") if v.strip()]
        template: str = opts["template"]
        color_grade: str = opts["color_grade"]
        spider_trends: dict[str, Any] = {}
        if opts.get("spider_trends"):
            spider_trends = json.loads(opts["spider_trends"])
        user_id: int | None = opts.get("user_id")

        if opts.get("sync"):
            self.stdout.write(self.style.WARNING(
                f"Running start_resolve_render synchronously for job {job_id}"
            ))
            result = start_resolve_render(
                job_id, video_ids, template, color_grade,
                spider_trends, user_id,
            )
            self.stdout.write(self.style.SUCCESS(f"Result: {result}"))
            return

        async_result = start_resolve_render.delay(
            job_id, video_ids, template, color_grade,
            spider_trends, user_id,
        )
        self.stdout.write(self.style.SUCCESS(
            f"Dispatched start_resolve_render task_id={async_result.id} "
            f"for job_id={job_id} template={template} grade={color_grade}"
        ))

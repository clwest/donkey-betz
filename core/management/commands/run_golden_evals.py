"""``run_golden_evals`` — Golden Evals validator harness entrypoint.

Session 2964 PR-1 (foundation scope): discovers ``evals/tier1/*.yaml``,
parses + validates each slice, resolves the substrate adapter via
:data:`~core.services.golden_evals.adapters.ADAPTER_REGISTRY`, and prints
one row per prompt in ``--dry-run`` mode (default). No agent dispatch,
no acceptance-criteria evaluation, no substrate row creation — those land
in PR-2.

The dry-run flow is deliberately shippable on its own so Rigby can dogfood
the two-substrate abstraction (canon_v2 Item 6) + the source-stratification
filter (canon_v2 Item 2) + the receipt-contamination filter (canon_v2
Item 4) end-to-end without waiting for executor logic to stabilize.

Usage:

    # Discover + dry-run every Tier-1 slice.
    python manage.py run_golden_evals

    # Filter to one slice by filename stem.
    python manage.py run_golden_evals --slice rigby_agent

    # Point at a custom YAML root (e.g., for local experimentation).
    python manage.py run_golden_evals --yaml-root evals/tier1
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from core.models_golden_evals import GoldenEvalRun
from core.services.golden_evals.adapters import ADAPTER_REGISTRY
from core.services.golden_evals.loader import (
    LoadedSlice,
    SliceLoadError,
    TIER1_ROOT,
    discover_slices,
    load_slice,
)


class Command(BaseCommand):
    help = "Run Golden Evals Tier-1 slices (S2964 foundation — dry-run only)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--yaml-root",
            default=str(TIER1_ROOT),
            help="Directory containing Tier-1 YAML slices (default: evals/tier1).",
        )
        parser.add_argument(
            "--slice",
            dest="slice_name",
            default=None,
            help=(
                "Filter to a single slice by filename stem "
                "(e.g., 'rigby_agent' for evals/tier1/rigby_agent.yaml)."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=True,
            help=(
                "Skip agent dispatch + acceptance-criteria evaluation "
                "(S2964 PR-1 foundation default). PR-2 will add "
                "``--execute`` to flip this off."
            ),
        )
        parser.add_argument(
            "--no-persist",
            action="store_true",
            default=False,
            help=(
                "Skip writing GoldenEvalRun rows even in dry-run. Useful "
                "for local inspection when the DB migration hasn't been "
                "applied to the target environment."
            ),
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        root = Path(opts["yaml_root"])
        slice_filter = opts.get("slice_name")
        persist = not opts.get("no_persist")

        paths = discover_slices(root)
        if not paths:
            raise CommandError(f"No YAML slices found under {root}")

        if slice_filter:
            paths = [p for p in paths if p.stem == slice_filter]
            if not paths:
                raise CommandError(
                    f"No slice matched --slice={slice_filter!r} under {root}"
                )

        run_id = uuid.uuid4()
        self.stdout.write(f"run_id={run_id}")
        self.stdout.write(f"yaml_root={root}")
        self.stdout.write(f"slices_discovered={len(paths)}")
        self.stdout.write("")

        total_prompts = 0
        rows_written = 0

        for path in paths:
            try:
                loaded = load_slice(path)
            except SliceLoadError as exc:
                self.stderr.write(self.style.ERROR(f"[LOAD-FAIL] {exc}"))
                continue

            adapter_cls = ADAPTER_REGISTRY.get(loaded.substrate_type)
            if adapter_cls is None:
                self.stderr.write(
                    self.style.ERROR(
                        f"[NO-ADAPTER] {path.name} declares substrate_type="
                        f"{loaded.substrate_type!r} but no adapter is "
                        "registered. Add one under core/services/golden_evals/"
                        "adapters/ + register in ADAPTER_REGISTRY."
                    )
                )
                continue

            adapter = adapter_cls()
            self._report_slice(loaded, adapter_cls.__name__)

            for prompt_id in loaded.prompt_ids:
                total_prompts += 1
                if persist:
                    GoldenEvalRun.objects.create(
                        run_id=run_id,
                        yaml_path=str(path),
                        prompt_id=prompt_id,
                        substrate_type=loaded.substrate_type,
                        primary_row_id="",
                        evidence_ledger_refs=[],
                        passed=None,
                        failure_reasons=[],
                        finalized_at=None,
                        latency_ms=None,
                    )
                    rows_written += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"[DONE] slices={len(paths)} prompts={total_prompts} "
                f"rows_written={rows_written} run_id={run_id}"
            )
        )

    def _report_slice(self, loaded: LoadedSlice, adapter_name: str) -> None:
        self.stdout.write(
            f"[SLICE] {loaded.path.name}  agent={loaded.agent}  "
            f"canon={loaded.canon_version}  schema={loaded.schema_version}  "
            f"substrate={loaded.substrate_type}  adapter={adapter_name}  "
            f"prompts={len(loaded.prompt_ids)}"
        )

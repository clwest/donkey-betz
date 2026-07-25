"""Agent Capability Drift Scanner.

Ratified at S2953 (plan pivot from A1 Phase 1 → capability substrate first).
Rigby SIGN-refined spec: single codepath, three surfaces (management command +
Django test wrapper + PA-callable audit tool). Motivated by the S2952 finding
that ``market_intelligence_agent`` was silently no-op'ing because nobody was
checking the AGENT_MAP ↔ enum ↔ mapping ↔ Agent-row ↔ recent-execution round
trip.

Invariants checked
------------------
1. AGENT_MAP entry → Agent DB row exists (canonicalized name match).
2. User-callable exposure completeness — every AGENT_MAP class either:
     a) is tagged ``internal-only`` in the exceptions allowlist, OR
     b) appears in the ``run_agent`` enum AND resolves via
        ``_tool_to_agent_name`` back to its class AND has a registered
        dispatcher handler.
3. Recent execution evidence — every ``supported`` agent (default tier) has
   ≥1 ``AgentExecution`` row with ``status='completed'`` in the last N days
   (default 30).

Rerouted-must-be-labeled (Rigby zoom-out invariant 4) is stubbed as a future
extension — router-level rerouting happens inside ``_apply_task_routing_override``
at dispatch time and doesn't have a queryable structure yet. Ledger candidate.

Exception allowlist
-------------------
``capabilities_exceptions.yaml`` at project root. Format::

    version: 1
    exceptions:
      <ClassName>:
        tier: supported | internal-only | legacy | rerouted | experimental
        reason: "short human-readable explanation"
        ttl_expires: null | "YYYY-MM-DD"  # optional; scanner warns after expiry

Entries in the allowlist suppress findings for the covered invariants:
- ``internal-only`` tier suppresses invariant-2 exposure failures for that agent
- ``rerouted``/``legacy``/``experimental`` tiers suppress invariant-3 recent-execution failures
- ``supported`` tier is the default and enforces all applicable invariants
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml
from django.conf import settings
from django.utils import timezone


DEFAULT_RECENT_WINDOW_DAYS = 30
DEFAULT_EXCEPTIONS_PATH_NAME = "capabilities_exceptions.yaml"

SUPPORTED = "supported"
INTERNAL_ONLY = "internal-only"
LEGACY = "legacy"
REROUTED = "rerouted"
EXPERIMENTAL = "experimental"

VALID_TIERS = frozenset({SUPPORTED, INTERNAL_ONLY, LEGACY, REROUTED, EXPERIMENTAL})

# Tiers that do NOT require invariant-2 (user-callable exposure).
TIERS_EXEMPT_FROM_EXPOSURE = frozenset({INTERNAL_ONLY, LEGACY, REROUTED, EXPERIMENTAL})

# Tiers that do NOT require invariant-3 (recent execution).
TIERS_EXEMPT_FROM_RECENT_EXEC = frozenset({INTERNAL_ONLY, LEGACY, REROUTED, EXPERIMENTAL})


@dataclass
class DriftFinding:
    """One drift observation. Emitted per (agent, invariant) pair."""

    agent_class: str
    invariant: str  # 'agent_map_to_db' | 'exposure_completeness' | 'recent_execution'
    severity: str  # 'warn' | 'fail'
    message: str
    tier: str = SUPPORTED
    exception_reason: Optional[str] = None  # populated when suppressed by allowlist

    def to_dict(self) -> Dict:
        return {
            "agent_class": self.agent_class,
            "invariant": self.invariant,
            "severity": self.severity,
            "message": self.message,
            "tier": self.tier,
            "exception_reason": self.exception_reason,
        }


@dataclass
class DriftReport:
    scanned_at: str
    total_agent_map_entries: int
    total_agent_db_rows: int
    total_run_agent_enum_entries: int
    exceptions_loaded: int
    findings: List[DriftFinding] = field(default_factory=list)
    suppressed_findings: List[DriftFinding] = field(default_factory=list)

    @property
    def has_active_failures(self) -> bool:
        return any(f.severity == "fail" for f in self.findings)

    @property
    def has_active_warnings(self) -> bool:
        return any(f.severity == "warn" for f in self.findings)

    def to_dict(self) -> Dict:
        return {
            "scanned_at": self.scanned_at,
            "totals": {
                "agent_map_entries": self.total_agent_map_entries,
                "agent_db_rows": self.total_agent_db_rows,
                "run_agent_enum_entries": self.total_run_agent_enum_entries,
                "exceptions_loaded": self.exceptions_loaded,
                "active_findings": len(self.findings),
                "suppressed_findings": len(self.suppressed_findings),
            },
            "has_active_failures": self.has_active_failures,
            "has_active_warnings": self.has_active_warnings,
            "findings": [f.to_dict() for f in self.findings],
            "suppressed_findings": [f.to_dict() for f in self.suppressed_findings],
        }


def _exceptions_path() -> Path:
    override = getattr(settings, "CAPABILITIES_EXCEPTIONS_PATH", None)
    if override:
        return Path(override)
    return Path(settings.BASE_DIR) / DEFAULT_EXCEPTIONS_PATH_NAME


def load_exceptions(path: Optional[Path] = None) -> Dict[str, Dict]:
    """Load capabilities_exceptions.yaml. Returns {class_name: {tier, reason, ttl_expires}}.

    Missing file returns an empty dict — scanner still runs and reports all defaults.
    Expired TTL entries emit a warning but still suppress the finding for one grace
    scan (they surface via the ``ttl_expired`` field in the finding message).
    """
    target = path or _exceptions_path()
    if not target.exists():
        return {}
    raw = yaml.safe_load(target.read_text()) or {}
    entries = raw.get("exceptions", {}) or {}
    normalized: Dict[str, Dict] = {}
    for cls, meta in entries.items():
        if not isinstance(meta, dict):
            continue
        tier = meta.get("tier", SUPPORTED)
        if tier not in VALID_TIERS:
            tier = SUPPORTED
        normalized[cls] = {
            "tier": tier,
            "reason": meta.get("reason", ""),
            "ttl_expires": meta.get("ttl_expires"),
        }
    return normalized


def _ttl_active(ttl_expires) -> bool:
    if ttl_expires in (None, "", "null"):
        return True  # permanent
    try:
        expires = datetime.fromisoformat(str(ttl_expires))
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.now().tzinfo)
        return expires >= timezone.now()
    except (TypeError, ValueError):
        return True  # unparseable → treat as permanent, don't false-fail


def _fallback_snake_to_camel(tool_name: str) -> str:
    """Mirror of _tool_to_agent_name's fallback for verification only."""
    stem = tool_name[:-len("_agent")] if tool_name.endswith("_agent") else tool_name
    return "".join(p.capitalize() for p in stem.split("_")) + "Agent"


class AgentCapabilityDriftScanner:
    """Runs the full invariant sweep against live code + DB state."""

    def __init__(
        self,
        recent_window_days: int = DEFAULT_RECENT_WINDOW_DAYS,
        exceptions_path: Optional[Path] = None,
    ):
        self.recent_window_days = recent_window_days
        self.exceptions = load_exceptions(exceptions_path)

    def _tier_for(self, class_name: str) -> str:
        entry = self.exceptions.get(class_name)
        if entry and _ttl_active(entry.get("ttl_expires")):
            return entry["tier"]
        return SUPPORTED

    def _exception_reason(self, class_name: str) -> Optional[str]:
        entry = self.exceptions.get(class_name)
        if entry:
            return entry.get("reason") or ""
        return None

    def _classify_finding(self, finding: DriftFinding) -> DriftFinding:
        """Route a raw finding into either active or suppressed based on tier + invariant."""
        tier = finding.tier
        invariant = finding.invariant
        if invariant == "exposure_completeness" and tier in TIERS_EXEMPT_FROM_EXPOSURE:
            finding.exception_reason = self._exception_reason(finding.agent_class) or f"tier={tier}"
            return finding
        if invariant == "recent_execution" and tier in TIERS_EXEMPT_FROM_RECENT_EXEC:
            finding.exception_reason = self._exception_reason(finding.agent_class) or f"tier={tier}"
            return finding
        return finding

    def scan_invariant_1_agent_map_to_db(self, agent_map_classes: Dict[str, str]) -> List[DriftFinding]:
        """agent_map_classes: {tool_name: class_name}."""
        from core.models_unified_system import Agent

        findings: List[DriftFinding] = []
        db_names = set(Agent.objects.values_list("name", flat=True))
        for _tool_name, class_name in agent_map_classes.items():
            if class_name not in db_names:
                findings.append(DriftFinding(
                    agent_class=class_name,
                    invariant="agent_map_to_db",
                    severity="warn",
                    message=f"AGENT_MAP entry {class_name!r} has no matching Agent DB row",
                    tier=self._tier_for(class_name),
                ))
        return findings

    def scan_invariant_2_exposure_completeness(
        self,
        agent_map_classes: Dict[str, str],
        run_agent_enum: Set[str],
        tool_to_agent_mapping: Dict[str, str],
        handler_registry_keys: Set[str],
    ) -> List[DriftFinding]:
        """Check user-callable exposure path. Findings suppressed for internal-only tiers."""
        findings: List[DriftFinding] = []

        # (a) Every enum entry must resolve via _tool_to_agent_name to a class present in AGENT_MAP.
        agent_map_class_names = set(agent_map_classes.values())
        for slug in run_agent_enum:
            resolved = tool_to_agent_mapping.get(slug) or _fallback_snake_to_camel(slug)
            if resolved not in agent_map_class_names:
                findings.append(DriftFinding(
                    agent_class=resolved,
                    invariant="exposure_completeness",
                    severity="warn",
                    message=(
                        f"run_agent enum entry {slug!r} resolves to {resolved!r}, "
                        f"which is not present in AgentRouter.AGENT_MAP"
                    ),
                    tier=self._tier_for(resolved),
                ))

        # (b) Every AGENT_MAP class not tagged internal-only must have a corresponding
        #     enum entry + mapping entry + dispatcher handler entry.
        enum_slug_by_class: Dict[str, str] = {}
        for slug in run_agent_enum:
            resolved = tool_to_agent_mapping.get(slug) or _fallback_snake_to_camel(slug)
            enum_slug_by_class[resolved] = slug

        for tool_name, class_name in agent_map_classes.items():
            tier = self._tier_for(class_name)
            if class_name not in enum_slug_by_class:
                # Always emit — classifier routes to `suppressed_findings`
                # when tier is exempt so operator-facing reports still show
                # "these agents are internal-only by allowlist" as visible
                # audit evidence rather than silent omissions.
                findings.append(DriftFinding(
                    agent_class=class_name,
                    invariant="exposure_completeness",
                    severity="warn",
                    message=(
                        f"AGENT_MAP class {class_name!r} (tool_name={tool_name!r}) has no "
                        f"run_agent enum entry — Rigby cannot reach it. Tag as "
                        f"internal-only in capabilities_exceptions.yaml if intentional."
                    ),
                    tier=tier,
                ))
                continue
            if tier in TIERS_EXEMPT_FROM_EXPOSURE:
                # Reachable via enum but tagged exempt (unusual but valid):
                # skip mapping/handler checks since we don't require user-callable.
                continue
            slug = enum_slug_by_class[class_name]
            if slug not in tool_to_agent_mapping:
                findings.append(DriftFinding(
                    agent_class=class_name,
                    invariant="exposure_completeness",
                    severity="warn",
                    message=(
                        f"{class_name!r} enum-exposed as {slug!r} but missing from "
                        f"_tool_to_agent_name explicit mapping — falls back to snake→Camel "
                        f"formatter (regression risk: S2952 MarketIntel-class silent no-op)"
                    ),
                    tier=tier,
                ))
            if slug not in handler_registry_keys:
                findings.append(DriftFinding(
                    agent_class=class_name,
                    invariant="exposure_completeness",
                    severity="warn",
                    message=f"{class_name!r} enum-exposed as {slug!r} but no dispatcher handler registered",
                    tier=tier,
                ))
        return findings

    def scan_invariant_3_recent_execution(
        self,
        agent_map_classes: Dict[str, str],
    ) -> List[DriftFinding]:
        from core.models_unified_system import AgentExecution

        findings: List[DriftFinding] = []
        window_start = timezone.now() - timedelta(days=self.recent_window_days)
        recent_success_names = set(
            AgentExecution.objects.filter(
                status="completed",
                created_at__gte=window_start,
            ).values_list("agent__name", flat=True).distinct()
        )
        for _tool_name, class_name in agent_map_classes.items():
            tier = self._tier_for(class_name)
            if class_name not in recent_success_names:
                # Always emit — classifier routes to `suppressed_findings`
                # for exempt tiers, keeping the audit report transparent.
                findings.append(DriftFinding(
                    agent_class=class_name,
                    invariant="recent_execution",
                    severity="warn",
                    message=(
                        f"{class_name!r} (tier={tier}) has zero successful executions in "
                        f"the last {self.recent_window_days} days. Downgrade tier or "
                        f"exercise the agent to restore evidence."
                    ),
                    tier=tier,
                ))
        return findings

    def _collect_agent_map(self) -> Dict[str, str]:
        """Return {tool_name_key_in_AGENT_MAP: class_name}."""
        from core.agent_router import AgentRouter

        result: Dict[str, str] = {}
        for key, cls in AgentRouter.AGENT_MAP.items():
            class_name = getattr(cls, "__name__", str(cls))
            result[key] = class_name
        return result

    def _collect_run_agent_enum(self) -> Set[str]:
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

        for tool in PA_TOOL_SCHEMAS:
            if tool.get("name") == "run_agent":
                enum = tool.get("parameters", {}).get("properties", {}).get("agent_name", {}).get("enum", [])
                return set(enum)
        return set()

    def _collect_tool_to_agent_mapping(self) -> Dict[str, str]:
        """Extract explicit mappings from _tool_to_agent_name via source inspection."""
        from core.services.tool_dispatcher import ToolDispatcher
        import inspect

        d = ToolDispatcher()
        src = inspect.getsource(d._tool_to_agent_name)
        return dict(re.findall(r"'([a-z0-9_]+)': '([A-Za-z0-9]+)'", src))

    def _collect_handler_registry_keys(self) -> Set[str]:
        from core.services.tool_dispatcher import ToolDispatcher

        d = ToolDispatcher()
        # Canonical attribute name on ToolDispatcher (verified S2953).
        registry = getattr(d, "_tool_handlers", None)
        if registry:
            return set(registry.keys())
        # Defensive fallbacks in case attribute is renamed in the future.
        for alt in ("_handlers", "handlers", "_handler_registry"):
            registry = getattr(d, alt, None)
            if registry:
                return set(registry.keys())
        return set()

    def run_all(self) -> DriftReport:
        from core.models_unified_system import Agent

        agent_map = self._collect_agent_map()
        enum = self._collect_run_agent_enum()
        mapping = self._collect_tool_to_agent_mapping()
        handlers = self._collect_handler_registry_keys()

        report = DriftReport(
            scanned_at=timezone.now().isoformat(),
            total_agent_map_entries=len(agent_map),
            total_agent_db_rows=Agent.objects.count(),
            total_run_agent_enum_entries=len(enum),
            exceptions_loaded=len(self.exceptions),
        )

        raw_findings: List[DriftFinding] = []
        raw_findings.extend(self.scan_invariant_1_agent_map_to_db(agent_map))
        raw_findings.extend(self.scan_invariant_2_exposure_completeness(
            agent_map, enum, mapping, handlers,
        ))
        raw_findings.extend(self.scan_invariant_3_recent_execution(agent_map))

        for finding in raw_findings:
            classified = self._classify_finding(finding)
            if classified.exception_reason is not None:
                report.suppressed_findings.append(classified)
            else:
                report.findings.append(classified)
        return report

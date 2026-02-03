"""
Report Schemas and Provenance Tracking
======================================

Session 918: Structured output schemas for agent reports.

Based on feedback to add data provenance, validation gates, and structured
JSON output alongside markdown reports.

Key Components:
1. ReportProvenance - Tracks data sources, timestamps, and validation status
2. SportsReportSchema - Structured output for sports betting analysis
3. FinanceReportSchema - Structured output for stock/finance analysis
4. ValidationGate - Determines if report is publishable

Philosophy:
- Be honest about what we know and don't know
- Track WHERE data came from and WHEN
- Don't pretend to have precision we don't have
- Clear disclaimers on limitations
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Report validation status levels."""
    VERIFIED = "verified"           # All data sources confirmed fresh
    PARTIALLY_VERIFIED = "partially_verified"  # Some data may be stale
    UNVERIFIED = "unverified"       # Data freshness unknown
    STALE = "stale"                 # Data known to be outdated


class ReportType(Enum):
    """Types of reports we generate."""
    SPORTS_ODDS = "sports_odds"
    STOCK_ANALYSIS = "stock_analysis"
    MARKET_REPORT = "market_report"
    BLOCKCHAIN_AUDIT = "blockchain_audit"


@dataclass
class SourceInfo:
    """
    Information about a data source used in the report.

    Tracks the spider/API that provided data and when it was retrieved.
    """
    name: str                       # e.g., "TheOddsSpider", "YahooFinanceSpider"
    endpoint: str = ""              # API endpoint or data path
    retrieved_at: Optional[str] = None  # ISO timestamp when data was pulled
    data_timestamp: Optional[str] = None  # Timestamp of the data itself (if different)
    record_count: int = 0           # Number of records from this source
    freshness_hours: float = 0.0    # Hours since data was retrieved

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReportProvenance:
    """
    Session 918: Provenance tracking for agent reports.

    Every report should include this block to establish:
    - When the report was generated
    - What data sources were used
    - How fresh the underlying data is
    - Whether the report is safe to publish/act on

    This enables auditing, trust calibration, and publishing gates.
    """
    # Generation metadata
    report_type: str = ""
    generated_at_utc: str = ""
    generated_at_local: str = ""
    agent_name: str = ""
    agent_version: str = "1.0"

    # Data window
    data_window_start: Optional[str] = None  # Earliest data timestamp used
    data_window_end: Optional[str] = None    # Latest data timestamp used

    # Sources
    sources: List[SourceInfo] = field(default_factory=list)
    total_records_analyzed: int = 0

    # Freshness & Validation
    max_data_age_hours: float = 0.0
    avg_data_age_hours: float = 0.0
    validation_status: str = "unverified"  # verified/partially_verified/unverified/stale
    validation_notes: List[str] = field(default_factory=list)

    # Publishing gate
    publishable: bool = False
    publish_blockers: List[str] = field(default_factory=list)

    # Disclaimer
    disclaimer: str = "Informational only. Verify data before acting. Not financial advice."

    def to_dict(self) -> dict:
        result = {
            'report_type': self.report_type,
            'generated_at_utc': self.generated_at_utc,
            'generated_at_local': self.generated_at_local,
            'agent_name': self.agent_name,
            'agent_version': self.agent_version,
            'data_window_start': self.data_window_start,
            'data_window_end': self.data_window_end,
            'sources': [s.to_dict() for s in self.sources],
            'total_records_analyzed': self.total_records_analyzed,
            'max_data_age_hours': round(self.max_data_age_hours, 2),
            'avg_data_age_hours': round(self.avg_data_age_hours, 2),
            'validation_status': self.validation_status,
            'validation_notes': self.validation_notes,
            'publishable': self.publishable,
            'publish_blockers': self.publish_blockers,
            'disclaimer': self.disclaimer,
        }
        return result

    def to_markdown_block(self) -> str:
        """Generate markdown provenance block for report header."""
        lines = [
            "---",
            "## Report Provenance",
            "",
            f"**Generated:** {self.generated_at_local} (UTC: {self.generated_at_utc})",
            f"**Agent:** {self.agent_name} v{self.agent_version}",
            f"**Data Window:** {self.data_window_start or 'N/A'} → {self.data_window_end or 'N/A'}",
            "",
            "### Data Sources",
        ]

        if self.sources:
            for src in self.sources:
                freshness = f"{src.freshness_hours:.1f}h ago" if src.freshness_hours else "unknown age"
                lines.append(f"- **{src.name}**: {src.record_count} records ({freshness})")
        else:
            lines.append("- No data sources tracked")

        lines.extend([
            "",
            f"**Total Records:** {self.total_records_analyzed}",
            f"**Max Data Age:** {self.max_data_age_hours:.1f} hours",
            f"**Validation:** {self.validation_status.upper()}",
        ])

        if self.validation_notes:
            lines.append("")
            lines.append("### Validation Notes")
            for note in self.validation_notes:
                lines.append(f"- {note}")

        # Publishing status
        lines.extend([
            "",
            f"**Publishable:** {'✅ Yes' if self.publishable else '❌ No'}",
        ])

        if self.publish_blockers:
            lines.append("**Blockers:**")
            for blocker in self.publish_blockers:
                lines.append(f"- ⚠️ {blocker}")

        lines.extend([
            "",
            f"*{self.disclaimer}*",
            "",
            "---",
        ])

        return "\n".join(lines)


@dataclass
class Claim:
    """
    A specific claim made in the report.

    Tracking claims enables:
    - Confidence calibration over time
    - Accountability for predictions
    - Clear evidence linking
    """
    claim: str
    confidence: float = 0.5  # 0.0-1.0
    evidence_source: str = ""  # Which source supports this claim
    claim_type: str = "observation"  # observation, prediction, recommendation

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Recommendation:
    """
    An actionable recommendation from the report.
    """
    action: str
    rationale: str
    confidence: float = 0.5
    risk_level: str = "medium"  # low, medium, high
    blockers: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskFlag:
    """
    A risk or warning identified in the analysis.
    """
    severity: str  # low, medium, high, critical
    description: str
    mitigation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# =============================================================================
# SPORTS REPORT SCHEMA
# =============================================================================

@dataclass
class GameAnalysis:
    """
    Analysis of a single game/matchup for sports betting.

    NOTE: We do NOT claim to have a "model line" - we aggregate market data.
    The "edge" here is between different bookmakers, not vs our prediction.
    """
    game_id: str = ""
    sport: str = ""
    matchup: str = ""
    home_team: str = ""
    away_team: str = ""

    # Market data (from bookmakers)
    home_moneyline: Optional[int] = None
    away_moneyline: Optional[int] = None
    home_implied_prob: Optional[float] = None
    away_implied_prob: Optional[float] = None
    spread: Optional[float] = None
    total: Optional[float] = None

    # Cross-book analysis (NOT model vs market)
    bookmaker_count: int = 0
    line_consensus: str = ""  # "tight" or "wide" based on book agreement
    best_home_odds: Optional[int] = None
    best_away_odds: Optional[int] = None
    best_home_book: str = ""
    best_away_book: str = ""

    # Game timing
    start_time_utc: str = ""
    start_time_local: str = ""
    hours_until_start: float = 0.0

    # Status flags
    injury_data_available: bool = False
    injury_check_time: Optional[str] = None
    injury_impacts: List[str] = field(default_factory=list)

    # Signal type
    signal_type: str = ""  # TOSS_UP, SHARP_MARKET, FAVORITE_ANALYSIS, etc.
    signal_reasoning: str = ""

    def to_dict(self) -> dict:
        return {
            'game_id': self.game_id,
            'sport': self.sport,
            'matchup': self.matchup,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_moneyline': self.home_moneyline,
            'away_moneyline': self.away_moneyline,
            'home_implied_prob': self.home_implied_prob,
            'away_implied_prob': self.away_implied_prob,
            'spread': self.spread,
            'total': self.total,
            'bookmaker_count': self.bookmaker_count,
            'line_consensus': self.line_consensus,
            'best_home_odds': self.best_home_odds,
            'best_away_odds': self.best_away_odds,
            'best_home_book': self.best_home_book,
            'best_away_book': self.best_away_book,
            'start_time_utc': self.start_time_utc,
            'start_time_local': self.start_time_local,
            'hours_until_start': round(self.hours_until_start, 1),
            'injury_data_available': self.injury_data_available,
            'injury_check_time': self.injury_check_time,
            'injury_impacts': self.injury_impacts,
            'signal_type': self.signal_type,
            'signal_reasoning': self.signal_reasoning,
        }


@dataclass
class SportsReportSchema:
    """
    Session 918: Structured output schema for sports betting reports.

    Stored as JSON alongside the markdown report for downstream processing.
    """
    # Provenance
    provenance: ReportProvenance = field(default_factory=ReportProvenance)

    # Summary stats
    total_games_analyzed: int = 0
    sports_covered: List[str] = field(default_factory=list)
    games_in_next_24h: int = 0

    # Game analyses by sport
    nfl_games: List[GameAnalysis] = field(default_factory=list)
    nba_games: List[GameAnalysis] = field(default_factory=list)
    mlb_games: List[GameAnalysis] = field(default_factory=list)
    nhl_games: List[GameAnalysis] = field(default_factory=list)
    other_games: List[GameAnalysis] = field(default_factory=list)

    # Signals (what stood out)
    toss_up_games: List[str] = field(default_factory=list)  # Game IDs
    sharp_market_games: List[str] = field(default_factory=list)
    heavy_favorites: List[str] = field(default_factory=list)

    # Key claims and recommendations
    key_claims: List[Claim] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    risk_flags: List[RiskFlag] = field(default_factory=list)

    # Confidence
    overall_confidence: float = 0.5
    confidence_rationale: str = ""

    # Rejection tracking (games removed due to data quality)
    rejected_games: List[Dict[str, str]] = field(default_factory=list)  # {game_id, reason}

    def to_dict(self) -> dict:
        return {
            'provenance': self.provenance.to_dict(),
            'total_games_analyzed': self.total_games_analyzed,
            'sports_covered': self.sports_covered,
            'games_in_next_24h': self.games_in_next_24h,
            'nfl_games': [g.to_dict() for g in self.nfl_games],
            'nba_games': [g.to_dict() for g in self.nba_games],
            'mlb_games': [g.to_dict() for g in self.mlb_games],
            'nhl_games': [g.to_dict() for g in self.nhl_games],
            'other_games': [g.to_dict() for g in self.other_games],
            'toss_up_games': self.toss_up_games,
            'sharp_market_games': self.sharp_market_games,
            'heavy_favorites': self.heavy_favorites,
            'key_claims': [c.to_dict() for c in self.key_claims],
            'recommendations': [r.to_dict() for r in self.recommendations],
            'risk_flags': [r.to_dict() for r in self.risk_flags],
            'overall_confidence': self.overall_confidence,
            'confidence_rationale': self.confidence_rationale,
            'rejected_games': self.rejected_games,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# =============================================================================
# FINANCE REPORT SCHEMA
# =============================================================================

@dataclass
class ScenarioAnalysis:
    """
    A scenario in the scenario tree (Bull/Base/Bear).

    NOTE: We use qualitative descriptions, not fake probabilities.
    """
    scenario_name: str  # "Bull", "Base", "Bear"
    description: str
    key_assumptions: List[str] = field(default_factory=list)
    potential_impact: str = ""  # Qualitative impact description
    risk_triggers: List[str] = field(default_factory=list)  # What would make this happen

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FinanceReportSchema:
    """
    Session 918: Structured output schema for stock/finance reports.

    Stored as JSON alongside the markdown report for downstream processing.
    """
    # Provenance
    provenance: ReportProvenance = field(default_factory=ReportProvenance)

    # Target
    ticker: str = ""
    company_name: str = ""
    sector: str = ""

    # Analysis summary
    severity: str = "LOW"  # CRITICAL, HIGH, MEDIUM, LOW
    analysis_type: str = ""  # fundamental, technical, filing_review, etc.

    # Scenarios (qualitative, not fake probabilities)
    scenarios: List[ScenarioAnalysis] = field(default_factory=list)

    # Time horizons considered
    horizons: List[str] = field(default_factory=list)  # ["3M", "12M", "36M"]

    # Key claims and recommendations
    key_claims: List[Claim] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    risk_flags: List[RiskFlag] = field(default_factory=list)

    # Decision drivers (what mainly drove the conclusions)
    decision_drivers: List[str] = field(default_factory=list)

    # Blockers (what prevents full analysis)
    blockers: List[Dict[str, Any]] = field(default_factory=list)  # {blocker, owner, data_needed}

    # Tools used
    tools_executed: List[str] = field(default_factory=list)

    # ML analysis (if available)
    ml_analysis: Dict[str, Any] = field(default_factory=dict)

    # Confidence
    overall_confidence: float = 0.5
    confidence_rationale: str = ""

    def to_dict(self) -> dict:
        return {
            'provenance': self.provenance.to_dict(),
            'ticker': self.ticker,
            'company_name': self.company_name,
            'sector': self.sector,
            'severity': self.severity,
            'analysis_type': self.analysis_type,
            'scenarios': [s.to_dict() for s in self.scenarios],
            'horizons': self.horizons,
            'key_claims': [c.to_dict() for c in self.key_claims],
            'recommendations': [r.to_dict() for r in self.recommendations],
            'risk_flags': [r.to_dict() for r in self.risk_flags],
            'decision_drivers': self.decision_drivers,
            'blockers': self.blockers,
            'tools_executed': self.tools_executed,
            'ml_analysis': self.ml_analysis,
            'overall_confidence': self.overall_confidence,
            'confidence_rationale': self.confidence_rationale,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# =============================================================================
# PROVENANCE BUILDER HELPERS
# =============================================================================

def build_provenance(
    report_type: str,
    agent_name: str,
    sources: List[Dict[str, Any]],
    stale_threshold_hours: float = 4.0,
) -> ReportProvenance:
    """
    Session 918: Build a provenance block from source data.

    Args:
        report_type: Type of report (sports_odds, stock_analysis, etc.)
        agent_name: Name of the agent generating the report
        sources: List of source dicts with name, retrieved_at, record_count
        stale_threshold_hours: Hours after which data is considered stale

    Returns:
        ReportProvenance with validation status calculated
    """
    now = datetime.now(timezone.utc)

    provenance = ReportProvenance(
        report_type=report_type,
        generated_at_utc=now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        generated_at_local=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        agent_name=agent_name,
    )

    # Process sources
    source_infos = []
    ages = []
    total_records = 0
    earliest_data = None
    latest_data = None

    for src in sources:
        retrieved_at = src.get('retrieved_at')
        if retrieved_at:
            if isinstance(retrieved_at, str):
                try:
                    dt = datetime.fromisoformat(retrieved_at.replace('Z', '+00:00'))
                except ValueError:
                    dt = now
            elif isinstance(retrieved_at, datetime):
                dt = retrieved_at if retrieved_at.tzinfo else dt.replace(tzinfo=timezone.utc)
            else:
                dt = now

            age_hours = (now - dt).total_seconds() / 3600
            ages.append(age_hours)

            # Track data window
            if earliest_data is None or dt < earliest_data:
                earliest_data = dt
            if latest_data is None or dt > latest_data:
                latest_data = dt
        else:
            age_hours = 0.0

        record_count = src.get('record_count', 0)
        total_records += record_count

        source_infos.append(SourceInfo(
            name=src.get('name', 'Unknown'),
            endpoint=src.get('endpoint', ''),
            retrieved_at=src.get('retrieved_at', ''),
            data_timestamp=src.get('data_timestamp', ''),
            record_count=record_count,
            freshness_hours=round(age_hours, 2),
        ))

    provenance.sources = source_infos
    provenance.total_records_analyzed = total_records

    if ages:
        provenance.max_data_age_hours = max(ages)
        provenance.avg_data_age_hours = sum(ages) / len(ages)

    if earliest_data:
        provenance.data_window_start = earliest_data.strftime("%Y-%m-%d %H:%M UTC")
    if latest_data:
        provenance.data_window_end = latest_data.strftime("%Y-%m-%d %H:%M UTC")

    # Determine validation status
    if not source_infos:
        provenance.validation_status = "unverified"
        provenance.validation_notes.append("No data sources tracked")
        provenance.publishable = False
        provenance.publish_blockers.append("No data source provenance")
    elif provenance.max_data_age_hours > stale_threshold_hours:
        provenance.validation_status = "stale"
        provenance.validation_notes.append(
            f"Data is {provenance.max_data_age_hours:.1f}h old (threshold: {stale_threshold_hours}h)"
        )
        provenance.publishable = False
        provenance.publish_blockers.append(f"Data exceeds {stale_threshold_hours}h freshness threshold")
    elif provenance.max_data_age_hours > stale_threshold_hours / 2:
        provenance.validation_status = "partially_verified"
        provenance.validation_notes.append(
            f"Data is {provenance.max_data_age_hours:.1f}h old - approaching staleness"
        )
        provenance.publishable = True
    else:
        provenance.validation_status = "verified"
        provenance.validation_notes.append(
            f"All data within {stale_threshold_hours}h freshness window"
        )
        provenance.publishable = True

    # Check for minimum data
    if total_records == 0:
        provenance.publishable = False
        provenance.publish_blockers.append("No data records to analyze")

    return provenance


def format_disclaimer(report_type: str) -> str:
    """Get appropriate disclaimer for report type."""
    disclaimers = {
        'sports_odds': (
            "Informational only. Odds must be verified with bookmakers before placing any bets. "
            "This is not gambling advice. Past performance does not guarantee future results."
        ),
        'stock_analysis': (
            "Informational only. Not financial advice. Verify all data with official sources. "
            "Consult a qualified financial advisor before making investment decisions."
        ),
        'market_report': (
            "Informational only. Market conditions change rapidly. "
            "Verify current data before acting on this analysis."
        ),
        'blockchain_audit': (
            "Informational only. This analysis does not constitute a security audit. "
            "Smart contract interactions carry risk of loss."
        ),
    }
    return disclaimers.get(report_type, "Informational only. Verify data before acting.")

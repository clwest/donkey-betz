"""
Session 960 Phase 0: Agent Output Envelope
==========================================

Lightweight schema for publishable artifacts (blogs, reports).
Wraps agent output with provenance, claims, internal_refs, and
paragraph-level citation metadata. Validates via CitationGateService
without requiring new Django models.

Usage:
    envelope = build_envelope(
        agent_name="ContentWriterAgent",
        content="...",
        claims=[...],
        internal_refs=[...],
    )
    result = validate_envelope(envelope)
    if result['valid']:
        # safe to publish
"""

import hashlib
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ParagraphCitation:
    """Citation metadata for a single paragraph or content section."""
    paragraph_index: int
    source_ids: List[str] = field(default_factory=list)
    has_citation: bool = False
    citation_type: str = "none"  # none | url | data_ref | internal_doc | agent_memory


@dataclass
class AgentOutputEnvelope:
    """
    Envelope wrapping a publishable artifact with provenance metadata.

    This does NOT replace ReportProvenance; it augments it with
    paragraph-level citation tracking and internal doc references.
    """
    # Identity
    envelope_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    # Content
    content_hash: str = ""  # SHA-256 of the artifact content
    content_type: str = "blog"  # blog | report | dossier | analysis

    # Provenance links
    internal_refs: List[Dict[str, str]] = field(default_factory=list)
    # Each: {'path': 'docs/...', 'content_hash': '...', 'source_type': 'internal_doc'}

    # Claims from report_schemas.Claim
    claims: List[Dict[str, Any]] = field(default_factory=list)
    # Each: {'claim_id': '...', 'claim': '...', 'confidence': 0.x, 'source_ids': [...], 'status': '...'}

    # Paragraph-level citations
    paragraph_citations: List[Dict[str, Any]] = field(default_factory=list)

    # Validation results (populated by validate_envelope)
    citation_score: float = 0.0  # 0.0-1.0 ratio of cited paragraphs
    validation_passed: bool = False
    validation_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentOutputEnvelope':
        """Reconstruct an envelope from a dict (round-trip support)."""
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)


def build_envelope(
    agent_name: str,
    content: str,
    claims: Optional[List[Dict[str, Any]]] = None,
    internal_refs: Optional[List[Dict[str, str]]] = None,
    content_type: str = "blog",
    paragraph_citations: Optional[List[Dict[str, Any]]] = None,
) -> AgentOutputEnvelope:
    """
    Build an envelope for a publishable artifact.

    Args:
        agent_name: Name of the producing agent
        content: The full text content
        claims: List of claim dicts (from Claim.to_dict())
        internal_refs: List of internal doc references (from get_docs_consumed())
        content_type: Type of artifact
        paragraph_citations: Optional pre-computed paragraph citations

    Returns:
        AgentOutputEnvelope ready for validation
    """
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

    # Auto-generate claim IDs if missing
    if claims:
        for claim in claims:
            if not claim.get('claim_id'):
                claim['claim_id'] = str(uuid.uuid4())

    return AgentOutputEnvelope(
        agent_name=agent_name,
        content_hash=content_hash,
        content_type=content_type,
        internal_refs=internal_refs or [],
        claims=claims or [],
        paragraph_citations=paragraph_citations or [],
    )


def validate_envelope(
    envelope: AgentOutputEnvelope,
    min_citation_ratio: float = 0.0,
    require_claims: bool = False,
) -> Dict[str, Any]:
    """
    Validate an envelope against citation requirements.

    Uses CitationGateService if available, falls back to basic validation.

    Args:
        envelope: The envelope to validate
        min_citation_ratio: Minimum ratio of paragraphs with citations (0.0-1.0)
        require_claims: Whether at least one claim is required

    Returns:
        Dict with 'valid', 'citation_score', 'notes', 'violations'
    """
    notes = []
    violations = []

    # Check claims
    if require_claims and not envelope.claims:
        violations.append({
            'type': 'no_claims',
            'message': 'Envelope has no claims but claims are required',
        })

    # Calculate citation score from paragraph_citations
    total_paragraphs = len(envelope.paragraph_citations) if envelope.paragraph_citations else 0
    cited_paragraphs = 0
    if total_paragraphs > 0:
        cited_paragraphs = sum(
            1 for p in envelope.paragraph_citations
            if p.get('has_citation', False)
        )
        citation_score = cited_paragraphs / total_paragraphs
    else:
        citation_score = 0.0

    envelope.citation_score = citation_score

    if citation_score < min_citation_ratio:
        violations.append({
            'type': 'low_citation_ratio',
            'message': f'Citation ratio {citation_score:.0%} below minimum {min_citation_ratio:.0%}',
            'found': citation_score,
            'required': min_citation_ratio,
        })

    # Check internal refs have content hashes
    refs_with_hash = sum(1 for r in envelope.internal_refs if r.get('content_hash'))
    if envelope.internal_refs and refs_with_hash < len(envelope.internal_refs):
        notes.append(
            f"{len(envelope.internal_refs) - refs_with_hash} internal ref(s) missing content_hash"
        )

    # Check claim statuses
    refuted_claims = [c for c in envelope.claims if c.get('status') == 'refuted']
    if refuted_claims:
        violations.append({
            'type': 'refuted_claims',
            'message': f'{len(refuted_claims)} claim(s) have been refuted',
            'claim_ids': [c.get('claim_id') for c in refuted_claims],
        })

    # Wire to CitationGateService if available
    try:
        from core.services.citation_gate_service import CitationGateService
        gate = CitationGateService()
        if gate.requires_citations(envelope.agent_name):
            # Build a minimal result dict for the gate
            gate_result = {
                'content': '',  # Content is hashed, not passed
                'sources': [
                    {'name': ref.get('path', ref.get('name', '')), 'url': ''}
                    for ref in envelope.internal_refs
                ],
                'claims': envelope.claims,
            }
            is_valid, gate_violations = gate.validate(
                agent_name=envelope.agent_name,
                result=gate_result,
            )
            if not is_valid:
                violations.extend(gate_violations)
                notes.append(f"CitationGate: {len(gate_violations)} violation(s)")
            else:
                notes.append("CitationGate: passed")
    except ImportError:
        notes.append("CitationGateService not available")
    except Exception as e:
        notes.append(f"CitationGate error: {e}")

    is_valid = len(violations) == 0
    envelope.validation_passed = is_valid
    envelope.validation_notes = notes

    return {
        'valid': is_valid,
        'citation_score': citation_score,
        'notes': notes,
        'violations': violations,
        'cited_paragraphs': cited_paragraphs,
        'total_paragraphs': total_paragraphs,
    }

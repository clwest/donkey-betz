"""
Session 963 Phase 3: Evidence Pack Builder

Incrementally assembles an evidence-pack-v1 JSON on DeliberationSession.evidence_pack.
Sources, claims, contradictions, internal refs, and memory retrievals are appended
as the conversation progresses. Never blocks conversations — all operations are
try/except safe.
"""

import logging
import uuid
from django.utils import timezone

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 'evidence-pack-v1'


class EvidencePackBuilder:
    """Builds evidence packs incrementally on DeliberationSession.evidence_pack."""

    def init_pack(self, session) -> dict:
        """Initialize an empty evidence pack on the session."""
        pack = {
            '$schema': SCHEMA_VERSION,
            'session_id': str(session.id),
            'assembled_at': None,
            'sources': [],
            'claims': [],
            'contradictions': [],
            'internal_refs': [],
            'memory_retrievals': [],
        }
        session.evidence_pack = pack
        session.save(update_fields=['evidence_pack', 'updated_at'])
        return pack

    def _get_pack(self, session) -> dict:
        """Get existing pack or initialize."""
        pack = session.evidence_pack
        if not isinstance(pack, dict) or pack.get('$schema') != SCHEMA_VERSION:
            return self.init_pack(session)
        return pack

    def _save_pack(self, session, pack: dict):
        """Save updated pack to DB."""
        session.evidence_pack = pack
        session.save(update_fields=['evidence_pack', 'updated_at'])

    def append_source(self, session, source_dict: dict):
        """
        Append a source to the evidence pack. Dedupes by source_id or content_hash.

        source_dict should include:
            source_type, name, endpoint_or_path (optional),
            retrieved_at, content_hash (optional), record_count (optional)
        """
        try:
            pack = self._get_pack(session)
            source = {
                'source_id': source_dict.get('source_id', str(uuid.uuid4())),
                'source_type': source_dict.get('source_type', 'unknown'),
                'name': source_dict.get('name', ''),
                'endpoint_or_path': source_dict.get('endpoint_or_path', ''),
                'retrieved_at': source_dict.get('retrieved_at', timezone.now().isoformat()),
                'content_hash': source_dict.get('content_hash'),
                'freshness_hours': source_dict.get('freshness_hours'),
                'record_count': source_dict.get('record_count'),
            }

            # Dedupe by source_id
            existing_ids = {s.get('source_id') for s in pack['sources']}
            if source['source_id'] not in existing_ids:
                pack['sources'].append(source)
                self._save_pack(session, pack)
        except Exception as e:
            logger.warning(f"[Phase 3] append_source failed: {e}")

    def append_claims(self, session, claims_list: list, source_ids: list = None):
        """
        Append claims extracted from agent output.

        Each claim should be a dict with: claim_text, claim_type, confidence, status.
        source_ids links claims to evidence sources.
        """
        try:
            pack = self._get_pack(session)
            for claim_data in claims_list:
                claim = {
                    'claim_id': claim_data.get('claim_id', str(uuid.uuid4())),
                    'claim_text': claim_data.get('claim_text', claim_data.get('claim', '')),
                    'claim_type': claim_data.get('claim_type', 'analytical'),
                    'confidence': claim_data.get('confidence', 0.5),
                    'source_ids': claim_data.get('source_ids', source_ids or []),
                    'status': claim_data.get('status', 'uncontested'),
                }
                # Dedupe by claim_id
                existing_ids = {c.get('claim_id') for c in pack['claims']}
                if claim['claim_id'] not in existing_ids:
                    pack['claims'].append(claim)

            self._save_pack(session, pack)
        except Exception as e:
            logger.warning(f"[Phase 3] append_claims failed: {e}")

    def append_contradiction(self, session, contradiction_dict: dict):
        """
        Append a contradiction record when tension is detected.

        contradiction_dict: nature, claim_a_text, claim_b_text, resolution (optional)
        """
        try:
            pack = self._get_pack(session)
            contradiction = {
                'contradiction_id': contradiction_dict.get('contradiction_id', str(uuid.uuid4())),
                'nature': contradiction_dict.get('nature', 'disagreement'),
                'claim_a_text': contradiction_dict.get('claim_a_text', ''),
                'claim_b_text': contradiction_dict.get('claim_b_text', ''),
                'resolution': contradiction_dict.get('resolution', 'unresolved'),
                'resolved_by': contradiction_dict.get('resolved_by'),
            }
            pack['contradictions'].append(contradiction)
            self._save_pack(session, pack)
        except Exception as e:
            logger.warning(f"[Phase 3] append_contradiction failed: {e}")

    def append_internal_refs(self, session, refs: list):
        """
        Append internal document references.

        Each ref: {doc_path, accessed_at, version_hash (optional)}
        """
        try:
            pack = self._get_pack(session)
            existing_paths = {r.get('doc_path') for r in pack['internal_refs']}
            for ref in refs:
                doc_path = ref.get('doc_path', '')
                if doc_path and doc_path not in existing_paths:
                    pack['internal_refs'].append({
                        'doc_path': doc_path,
                        'accessed_at': ref.get('accessed_at', timezone.now().isoformat()),
                        'version_hash': ref.get('version_hash'),
                    })
                    existing_paths.add(doc_path)
            self._save_pack(session, pack)
        except Exception as e:
            logger.warning(f"[Phase 3] append_internal_refs failed: {e}")

    def append_memory_retrievals(self, session, retrievals: list):
        """
        Append strategic memory retrievals (best effort).

        Each retrieval: {source_type, title, score, ref}
        """
        try:
            pack = self._get_pack(session)
            for ret in retrievals[:5]:  # Cap at 5
                pack['memory_retrievals'].append({
                    'source_type': ret.get('source_type', ''),
                    'title': ret.get('title', ''),
                    'score': ret.get('score', 0),
                    'ref': ret.get('ref', ''),
                    'retrieved_at': timezone.now().isoformat(),
                })
            self._save_pack(session, pack)
        except Exception as e:
            logger.warning(f"[Phase 3] append_memory_retrievals failed: {e}")

    def finalize(self, session):
        """Mark the evidence pack as assembled."""
        try:
            pack = self._get_pack(session)
            pack['assembled_at'] = timezone.now().isoformat()
            self._save_pack(session, pack)
        except Exception as e:
            logger.warning(f"[Phase 3] finalize evidence pack failed: {e}")


# Singleton
_builder_instance = None


def get_evidence_pack_builder() -> EvidencePackBuilder:
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = EvidencePackBuilder()
    return _builder_instance

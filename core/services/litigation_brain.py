"""
Session 408: Legal Document Brain - Multi-Document Litigation Management

This module implements the core intelligence for the litigation management system:
1. LegalDocumentIngestor - Processes uploaded documents
2. LegalContextBuilder - Builds the case knowledge graph
3. LegalResponseWriter - Generates responses to filings
4. LegalFilingPackager - Bundles documents for filing

IMPORTANT DISCLAIMERS:
- This provides GENERAL LEGAL INFORMATION, NOT legal advice
- This does NOT create an attorney-client relationship
- Users should consult a licensed attorney for specific legal matters
"""

import logging
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, Any, List, Optional, Tuple
from uuid import UUID

from django.utils import timezone

if TYPE_CHECKING:
    from core.models_legal import GeneratedResponse, LitigationDocument

logger = logging.getLogger(__name__)


# =============================================================================
# Document Type Detection
# =============================================================================

DOCUMENT_TYPE_PATTERNS = {
    # Court Orders
    'temporary_orders': [
        r'temporary\s+orders?',
        r'interim\s+orders?',
        r'temporary\s+parenting',
    ],
    'prior_parenting': [
        r'parenting\s+plan',
        r'allocation\s+of\s+parental',
        r'custody\s+order',
        r'parenting\s+time\s+order',
    ],
    'status_quo': [
        r'status\s+quo',
        r'maintain.*current',
    ],
    'restriction': [
        r'restrict.*parenting',
        r'supervised\s+parenting',
        r'protective\s+order',
    ],
    'emergency_ruling': [
        r'emergency\s+order',
        r'emergency\s+motion.*granted',
        r'ex\s+parte',
    ],
    # Motions
    'my_motion': [
        r'motion\s+to\s+modify',
        r'motion\s+for\s+contempt',
        r'verified\s+motion',
    ],
    'opposing_motion': [
        r'respondent.s?\s+motion',
        r'response\s+to.*motion',
    ],
    # Responses
    'response': [
        r'response\s+to\s+motion',
        r'opposition\s+to',
        r'objection\s+to',
    ],
    'reply': [
        r'reply\s+(to|in)',
        r'petitioner.s?\s+reply',
    ],
    'affidavit': [
        r'affidavit',
        r'sworn\s+statement',
        r'declaration',
    ],
    # Evidence types
    'messages': [
        r'text\s+message',
        r'sms',
        r'imessage',
        r'screenshot.*message',
    ],
    'transcript': [
        r'transcript',
        r'deposition',
        r'hearing\s+transcript',
    ],
}

PARTY_ROLE_PATTERNS = {
    'petitioner': [
        r'petitioner',
        r'father',
        r'mother',
        r'plaintiff',
        r'applicant',
    ],
    'respondent': [
        r'respondent',
        r'defendant',
        r'opposing\s+party',
    ],
    'court': [
        r'court\s+order',
        r'the\s+court\s+finds',
        r'it\s+is\s+ordered',
        r'judge\s+\w+',
    ],
}


class LegalDocumentIngestor:
    """
    Processes uploaded legal documents - extracts text, normalizes formatting,
    classifies document type, and stores in the case file.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.LegalDocumentIngestor")

    def process_document(
        self,
        case_profile_id: UUID,
        file_content: bytes,
        filename: str,
        user_category: Optional[str] = None,
        user_document_type: Optional[str] = None,
        filing_party: Optional[str] = None,
        litigation_role: Optional[str] = None,  # Session 410: Added litigation role
        document_date: Optional[str] = None,
        filed_date: Optional[str] = None,
        responds_to_id: Optional[UUID] = None,
        notes: str = '',
    ) -> Dict[str, Any]:
        """
        Process an uploaded document and add it to the case.

        Args:
            case_profile_id: UUID of the CaseProfile
            file_content: Raw bytes of the uploaded file
            filename: Original filename
            user_category: User-specified category (court_order, motion, etc.)
            user_document_type: User-specified type (temporary_orders, etc.)
            filing_party: Who filed this (petitioner, respondent, court)
            litigation_role: Role in thread (motion, response, reply, order) - Session 410
            document_date: Date on the document
            filed_date: Date filed with court
            responds_to_id: UUID of document this responds to
            notes: User notes

        Returns:
            Dict with document info and processing results
        """
        from core.models_legal import CaseProfile, LitigationDocument

        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id)
        except CaseProfile.DoesNotExist:
            return {'success': False, 'error': 'Case profile not found'}

        # Extract text from file
        extracted_text = self._extract_text(file_content, filename)
        if not extracted_text:
            return {'success': False, 'error': 'Could not extract text from file'}

        # Auto-detect category and type if not provided
        detected_category, detected_type = self._detect_document_type(extracted_text)
        category = user_category or detected_category or 'evidence'
        document_type = user_document_type or detected_type or 'notes'

        # Detect filing party if not provided
        if not filing_party:
            filing_party = self._detect_filing_party(extracted_text)

        # Session 410: Auto-detect litigation role if not provided
        if not litigation_role:
            litigation_role = self._detect_litigation_role(extracted_text, document_type, category)

        # Parse dates
        doc_date = None
        file_date = None
        if document_date:
            try:
                doc_date = datetime.strptime(document_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        if filed_date:
            try:
                file_date = datetime.strptime(filed_date, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Extract metadata
        extracted_metadata = self._extract_metadata(extracted_text, category)

        # Create the document record
        doc = LitigationDocument.objects.create(
            case_profile=case_profile,
            category=category,
            document_type=document_type,
            filing_party=filing_party or 'petitioner',
            litigation_role=litigation_role or 'other',  # Session 410
            title=self._generate_title(filename, document_type),
            original_filename=filename,
            file_size=len(file_content),
            extracted_text=extracted_text,
            status='analyzed',
            document_date=doc_date,
            filed_date=file_date,
            responds_to_id=responds_to_id,
            extracted_metadata=extracted_metadata,
            notes=notes,
        )

        # Trigger knowledge graph rebuild
        self._trigger_rebuild(case_profile)

        return {
            'success': True,
            'document_id': str(doc.id),
            'title': doc.title,
            'category': category,
            'document_type': document_type,
            'filing_party': filing_party,
            'word_count': len(extracted_text.split()),
            'metadata_extracted': bool(extracted_metadata),
            'detected_category': detected_category,
            'detected_type': detected_type,
        }

    def _extract_text(self, content: bytes, filename: str) -> str:
        """Extract text from various file formats."""
        filename_lower = filename.lower()
        self.logger.info(f"[Session 409] _extract_text called: filename='{filename}', size={len(content)} bytes")

        if filename_lower.endswith('.txt'):
            self.logger.info("[Session 409] Detected TXT file")
            return content.decode('utf-8', errors='ignore')

        elif filename_lower.endswith('.pdf'):
            self.logger.info("[Session 409] Detected PDF file")
            return self._extract_pdf_text(content)

        elif filename_lower.endswith('.docx') or filename_lower.endswith('.doc'):
            self.logger.info("[Session 409] Detected DOCX/DOC file")
            return self._extract_docx_text(content)

        self.logger.warning(f"[Session 409] Unknown file extension for '{filename}', returning empty")
        return ''

    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF using PyMuPDF, with OCR fallback for scanned PDFs."""
        try:
            import fitz  # PyMuPDF
            import io
            self.logger.info(f"[Session 409] Extracting PDF text, content size: {len(content)} bytes")
            doc = fitz.open(stream=io.BytesIO(content), filetype="pdf")
            text = ""
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                text += page_text
                self.logger.debug(f"[Session 409] Page {page_num + 1}: {len(page_text)} chars")

            # If no text found, try OCR (scanned PDF)
            if not text.strip():
                self.logger.info(f"[Session 409] No text found in PDF, attempting OCR...")
                text = self._extract_pdf_text_ocr(content)

            self.logger.info(f"[Session 409] PDF extraction complete: {len(text)} total chars from {len(doc)} pages")
            return text
        except ImportError as e:
            self.logger.error(f"[Session 409] PyMuPDF not installed: {e}")
            import traceback
            traceback.print_exc()
            return ''
        except Exception as e:
            self.logger.error(f"[Session 409] PDF extraction error: {e}")
            import traceback
            traceback.print_exc()
            return ''

    def _extract_pdf_text_ocr(self, content: bytes) -> str:
        """Extract text from scanned PDF using OCR (PyMuPDF + pytesseract)."""
        try:
            import fitz  # PyMuPDF
            import pytesseract
            from PIL import Image
            import io

            self.logger.info("[Session 409] Running OCR on scanned PDF using PyMuPDF...")

            # Open PDF with PyMuPDF
            doc = fitz.open(stream=io.BytesIO(content), filetype="pdf")

            text_parts = []
            for page_num, page in enumerate(doc):
                # Render page to image at high resolution
                mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Run OCR
                page_text = pytesseract.image_to_string(img)
                text_parts.append(page_text)
                self.logger.debug(f"[Session 409] OCR Page {page_num + 1}: {len(page_text)} chars")

            full_text = '\n\n'.join(text_parts)
            self.logger.info(f"[Session 409] OCR complete: {len(full_text)} chars from {len(doc)} pages")
            return full_text
        except ImportError as e:
            self.logger.warning(f"[Session 409] OCR dependencies not available: {e}")
            return ''
        except Exception as e:
            self.logger.error(f"[Session 409] OCR extraction error: {e}")
            import traceback
            traceback.print_exc()
            return ''

    def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX."""
        try:
            from docx import Document
            import io
            doc = Document(io.BytesIO(content))
            return '\n'.join([p.text for p in doc.paragraphs])
        except Exception as e:
            self.logger.error(f"DOCX extraction error: {e}")
            return ''

    def _detect_document_type(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Auto-detect document category and type from content."""
        text_lower = text.lower()

        # Map document types to categories
        type_to_category = {
            'temporary_orders': 'court_order',
            'prior_parenting': 'court_order',
            'status_quo': 'court_order',
            'restriction': 'court_order',
            'emergency_ruling': 'court_order',
            'my_motion': 'motion',
            'opposing_motion': 'motion',
            'response': 'response',
            'reply': 'response',
            'affidavit': 'response',
            'messages': 'evidence',
            'transcript': 'evidence',
        }

        for doc_type, patterns in DOCUMENT_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    category = type_to_category.get(doc_type, 'evidence')
                    return category, doc_type

        return None, None

    def _detect_filing_party(self, text: str) -> str:
        """Detect who filed/authored the document."""
        text_lower = text.lower()

        # Check for court orders first
        for pattern in PARTY_ROLE_PATTERNS['court']:
            if re.search(pattern, text_lower):
                return 'court'

        # Count petitioner vs respondent mentions in context
        petitioner_score = 0
        respondent_score = 0

        for pattern in PARTY_ROLE_PATTERNS['petitioner']:
            petitioner_score += len(re.findall(f'{pattern}.*submits|{pattern}.*requests|{pattern}.*alleges', text_lower))

        for pattern in PARTY_ROLE_PATTERNS['respondent']:
            respondent_score += len(re.findall(f'{pattern}.*submits|{pattern}.*requests|{pattern}.*alleges', text_lower))

        if petitioner_score > respondent_score:
            return 'petitioner'
        elif respondent_score > petitioner_score:
            return 'respondent'

        return 'petitioner'  # Default

    def _detect_litigation_role(self, text: str, document_type: str, category: str) -> str:
        """
        Session 410: Detect litigation role (motion, response, reply, order).
        Used for document threading.
        """
        text_lower = text.lower()

        # Court orders are easy
        if category == 'court_order':
            return 'order'

        # Check document type for hints
        motion_types = ['my_motion', 'opposing_motion', 'pending_motion', 'emergency_motion']
        response_types = ['response', 'objection', 'opposition']
        reply_types = ['reply', 'rebuttal']

        if document_type in motion_types:
            return 'motion'
        if document_type in response_types:
            return 'response'
        if document_type in reply_types:
            return 'reply'

        # Text pattern matching
        reply_patterns = [
            r'reply\s+(to|in\s+support)',
            r'petitioner.s?\s+reply',
            r'respondent.s?\s+reply',
            r'rebuttal',
        ]
        for pattern in reply_patterns:
            if re.search(pattern, text_lower):
                return 'reply'

        response_patterns = [
            r'response\s+to.*motion',
            r'opposition\s+to',
            r'objection\s+to',
            r'answer\s+to.*petition',
        ]
        for pattern in response_patterns:
            if re.search(pattern, text_lower):
                return 'response'

        motion_patterns = [
            r'motion\s+(to|for)',
            r'verified\s+motion',
            r'emergency\s+motion',
            r'petitioner.*moves',
            r'respondent.*moves',
        ]
        for pattern in motion_patterns:
            if re.search(pattern, text_lower):
                return 'motion'

        order_patterns = [
            r'it\s+is\s+ordered',
            r'the\s+court\s+orders',
            r'hereby\s+ordered',
            r'court\s+order',
        ]
        for pattern in order_patterns:
            if re.search(pattern, text_lower):
                return 'order'

        # Default based on category
        if category == 'motion':
            return 'motion'
        if category == 'response':
            return 'response'

        return 'other'

    def _extract_metadata(self, text: str, category: str) -> Dict[str, Any]:
        """Extract structured metadata from document text."""
        metadata = {
            'parties_mentioned': [],
            'dates_mentioned': [],
            'allegations': [],
            'claims': [],
            'relief_requested': [],
            'case_numbers': [],
            'exhibits_referenced': [],
        }

        # Extract dates (various formats)
        date_patterns = [
            r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',
            r'\b(\w+ \d{1,2}, \d{4})\b',
            r'\b(\d{4}-\d{2}-\d{2})\b',
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            metadata['dates_mentioned'].extend(matches[:10])  # Limit

        # Extract case numbers
        case_pattern = r'\b(\d{4}[A-Z]{2}\d+)\b'
        metadata['case_numbers'] = re.findall(case_pattern, text)[:5]

        # Extract exhibit references
        exhibit_pattern = r'[Ee]xhibit\s+([A-Z]|\d+)'
        metadata['exhibits_referenced'] = re.findall(exhibit_pattern, text)

        # Extract relief requested (if motion)
        if category == 'motion':
            relief_patterns = [
                r'(?:requests?|asks?|seeks?)(?:\s+that)?\s+(?:the\s+)?[Cc]ourt\s+(.{20,200}?)(?:\.|;|$)',
                r'[Rr]elief\s+[Rr]equested[:.]?\s*(.{20,300}?)(?:\n\n|$)',
                r'[Pp]rayer\s+for\s+[Rr]elief[:.]?\s*(.{20,300}?)(?:\n\n|$)',
            ]
            for pattern in relief_patterns:
                matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
                if matches:
                    metadata['relief_requested'] = [m.strip() for m in matches[:5]]
                    break

        # Extract allegations
        allegation_patterns = [
            r'[Pp]etitioner\s+alleges\s+that\s+(.{20,200}?)(?:\.|;|$)',
            r'[Rr]espondent\s+has\s+(.{20,200}?)(?:\.|;|$)',
            r'[Ff]ailed\s+to\s+(.{20,150}?)(?:\.|;|$)',
            r'[Vv]iolated\s+(.{20,150}?)(?:\.|;|$)',
        ]
        for pattern in allegation_patterns:
            matches = re.findall(pattern, text)
            metadata['allegations'].extend([m.strip() for m in matches[:3]])

        return metadata

    def _generate_title(self, filename: str, document_type: str) -> str:
        """Generate a clean title from filename and type."""
        # Remove extension and clean up
        base = filename.rsplit('.', 1)[0]
        base = re.sub(r'[_-]+', ' ', base)
        base = base.title()

        # Add type prefix if not already in name
        type_display = document_type.replace('_', ' ').title()
        if type_display.lower() not in base.lower():
            return f"{type_display}: {base}"

        return base

    def _trigger_rebuild(self, case_profile) -> None:
        """Mark knowledge graph for rebuild."""
        try:
            from core.models_legal import CaseKnowledgeGraph
            kg, created = CaseKnowledgeGraph.objects.get_or_create(
                case_profile=case_profile
            )
            kg.rebuild_needed = True
            kg.save(update_fields=['rebuild_needed'])
        except Exception as e:
            self.logger.error(f"Could not trigger rebuild: {e}")


class LegalContextBuilder:
    """
    Builds and maintains the Case Knowledge Graph.
    Extracts and links information across all documents.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.LegalContextBuilder")

    def rebuild_knowledge_graph(self, case_profile_id: UUID) -> Dict[str, Any]:
        """
        Rebuild the complete knowledge graph for a case.

        Extracts:
        - Parties and their roles
        - Timeline of events
        - Allegations from all documents
        - Legal issues
        - Claims and counterclaims
        - Relief requested
        - Evidence references
        - Contradictions between documents
        - Procedural posture
        - Deadlines
        - Unaddressed issues
        """
        from core.models_legal import CaseProfile, CaseKnowledgeGraph, LitigationDocument

        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id)
        except CaseProfile.DoesNotExist:
            return {'success': False, 'error': 'Case profile not found'}

        documents = LitigationDocument.objects.filter(
            case_profile=case_profile
        ).order_by('filed_date', 'document_date', 'uploaded_at')

        # Initialize data structures
        parties = {}
        timeline = []
        allegations = {'petitioner': [], 'respondent': []}
        legal_issues = []
        claims = {'petitioner': [], 'respondent': []}
        relief_requested = {}
        evidence_referenced = {}
        contradictions = []
        procedural_posture = {'pending_motions': [], 'deadlines': [], 'next_hearing': None}
        deadlines = []
        unaddressed_issues = []
        misinformation = []

        # Process each document
        for doc in documents:
            self._process_document_for_graph(
                doc, parties, timeline, allegations, legal_issues,
                claims, relief_requested, evidence_referenced,
                contradictions, procedural_posture, deadlines,
                unaddressed_issues, misinformation
            )

        # Detect contradictions across documents
        self._find_contradictions(documents, contradictions)

        # Find unaddressed issues (claims without responses)
        self._find_unaddressed_issues(documents, claims, allegations, unaddressed_issues)

        # Calculate statistics
        stats = {
            'total_documents': documents.count(),
            'court_orders': documents.filter(category='court_order').count(),
            'motions': documents.filter(category='motion').count(),
            'responses': documents.filter(category='response').count(),
            'evidence': documents.filter(category='evidence').count(),
            'pending_responses': len([d for d in deadlines if d.get('type') == 'response']),
            'contradictions_found': len(contradictions),
            'unaddressed_issues': len(unaddressed_issues),
        }

        # Update or create knowledge graph
        kg, created = CaseKnowledgeGraph.objects.update_or_create(
            case_profile=case_profile,
            defaults={
                'parties': parties,
                'timeline': timeline,
                'allegations': allegations,
                'legal_issues': legal_issues,
                'claims': claims,
                'relief_requested': relief_requested,
                'evidence_referenced': evidence_referenced,
                'contradictions': contradictions,
                'procedural_posture': procedural_posture,
                'deadlines': deadlines,
                'unaddressed_issues': unaddressed_issues,
                'misinformation': misinformation,
                'stats': stats,
                'rebuild_needed': False,
            }
        )

        return {
            'success': True,
            'case_number': case_profile.case_number,
            'stats': stats,
            'parties_count': len(parties),
            'timeline_events': len(timeline),
            'contradictions_found': len(contradictions),
        }

    def _process_document_for_graph(
        self, doc, parties, timeline, allegations, legal_issues,
        claims, relief_requested, evidence_referenced,
        contradictions, procedural_posture, deadlines,
        unaddressed_issues, misinformation
    ):
        """Process a single document to extract information for the graph."""

        text = doc.extracted_text or ''
        metadata = doc.extracted_metadata or {}
        doc_id = str(doc.id)

        # Extract parties from text
        self._extract_parties(text, parties, doc_id)

        # Build timeline
        if doc.filed_date or doc.document_date:
            event_date = doc.filed_date or doc.document_date
            timeline.append({
                'date': str(event_date),
                'event': f"{doc.get_document_type_display()}: {doc.title}",
                'source_document': doc_id,
                'category': doc.category,
            })

        # Extract allegations
        filing_party = doc.filing_party
        if metadata.get('allegations'):
            for allegation in metadata['allegations']:
                allegations[filing_party].append({
                    'allegation': allegation,
                    'document': doc_id,
                    'date': str(doc.filed_date) if doc.filed_date else None,
                })

        # Extract relief requested
        if metadata.get('relief_requested'):
            relief_requested[doc_id] = [
                {'relief_type': 'requested', 'specifics': r}
                for r in metadata['relief_requested']
            ]

        # Extract evidence references
        if metadata.get('exhibits_referenced'):
            for exhibit in metadata['exhibits_referenced']:
                evidence_referenced[f"Exhibit {exhibit}"] = {
                    'type': 'exhibit',
                    'description': f"Exhibit {exhibit} referenced in {doc.title}",
                    'documents': [doc_id],
                }

        # Track pending motions
        if doc.category == 'motion' and doc.status not in ['responded', 'archived']:
            procedural_posture['pending_motions'].append({
                'motion_id': doc_id,
                'title': doc.title,
                'type': doc.document_type,
                'filed_date': str(doc.filed_date) if doc.filed_date else None,
            })

            # Calculate response deadline (21 days in Colorado)
            if doc.filed_date and doc.filing_party == 'respondent':
                deadline_date = doc.filed_date + timedelta(days=21)
                deadlines.append({
                    'date': str(deadline_date),
                    'motion_id': doc_id,
                    'motion_title': doc.title,
                    'type': 'response',
                    'days_remaining': (deadline_date - timezone.now().date()).days,
                })

    def _extract_parties(self, text: str, parties: dict, doc_id: str):
        """Extract party names and roles from text."""
        # Simple pattern matching for common party indicators
        name_patterns = [
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+),?\s+(?:Petitioner|as\s+Petitioner)', 'petitioner'),
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+),?\s+(?:Respondent|as\s+Respondent)', 'respondent'),
            (r'(?:Petitioner|Petitioner\'s name:?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', 'petitioner'),
            (r'(?:Respondent|Respondent\'s name:?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', 'respondent'),
        ]

        for pattern, role in name_patterns:
            matches = re.findall(pattern, text)
            for name in matches:
                name = name.strip()
                if name and len(name) > 3:
                    if name not in parties:
                        parties[name] = {
                            'role': role,
                            'mentions': 0,
                            'documents': [],
                        }
                    parties[name]['mentions'] += 1
                    if doc_id not in parties[name]['documents']:
                        parties[name]['documents'].append(doc_id)

    def _find_contradictions(self, documents, contradictions: list):
        """Find contradictions between documents."""
        # Group claims by topic for comparison
        doc_claims = {}
        for doc in documents:
            metadata = doc.extracted_metadata or {}
            if metadata.get('allegations'):
                doc_claims[str(doc.id)] = {
                    'doc': doc,
                    'claims': metadata['allegations'],
                }

        # Compare claims between opposing parties
        for doc_id1, data1 in doc_claims.items():
            for doc_id2, data2 in doc_claims.items():
                if doc_id1 >= doc_id2:
                    continue
                if data1['doc'].filing_party == data2['doc'].filing_party:
                    continue

                # Check for contradicting claims (simplified check)
                for claim1 in data1['claims']:
                    for claim2 in data2['claims']:
                        # Very basic contradiction check
                        if self._claims_contradict(claim1, claim2):
                            contradictions.append({
                                'doc1': doc_id1,
                                'claim1': claim1,
                                'doc2': doc_id2,
                                'claim2': claim2,
                                'analysis': 'Potentially contradicting claims detected',
                            })

    def _claims_contradict(self, claim1: str, claim2: str) -> bool:
        """Check if two claims potentially contradict."""
        # Simple heuristic: look for negation patterns
        negation_words = ['not', 'never', 'did not', 'failed', 'refused']
        claim1_lower = claim1.lower()
        claim2_lower = claim2.lower()

        # Check if claims are about similar topics but with opposite assertions
        for word in negation_words:
            if word in claim1_lower and word not in claim2_lower:
                # Check for word overlap (same topic)
                words1 = set(claim1_lower.split())
                words2 = set(claim2_lower.split())
                overlap = len(words1 & words2)
                if overlap >= 3:  # At least 3 common words
                    return True

        return False

    def _find_unaddressed_issues(self, documents, claims: dict, allegations: dict, unaddressed: list):
        """Find claims/allegations that haven't been responded to."""
        # Get all responded documents
        responded_docs = set()
        for doc in documents:
            if doc.responds_to:
                responded_docs.add(str(doc.responds_to.id))

        # Find motions without responses
        for doc in documents:
            if doc.category == 'motion' and doc.filing_party == 'respondent':
                if str(doc.id) not in responded_docs:
                    for allegation in (doc.extracted_metadata or {}).get('allegations', []):
                        unaddressed.append({
                            'issue': allegation,
                            'source_document': str(doc.id),
                            'type': 'unresponded_allegation',
                        })

    def get_case_context_json(self, case_profile_id: UUID) -> Dict[str, Any]:
        """Export case context as JSON (for API/frontend)."""
        from core.models_legal import CaseKnowledgeGraph

        try:
            kg = CaseKnowledgeGraph.objects.get(case_profile_id=case_profile_id)
            return kg.to_json()
        except CaseKnowledgeGraph.DoesNotExist:
            # Try to build it
            result = self.rebuild_knowledge_graph(case_profile_id)
            if result['success']:
                kg = CaseKnowledgeGraph.objects.get(case_profile_id=case_profile_id)
                return kg.to_json()
            return {}


class LegalResponseWriter:
    """
    Generates responses to opposing party filings.
    Structures responses in legal format with Admit/Deny/Insufficient Knowledge.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.LegalResponseWriter")

    def generate_response(
        self,
        doc: "LitigationDocument",
        case_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response to a filing.

        `doc` MUST be scoped to the requesting user by the caller — this
        service performs no authorization check. Pass a raw ID lookup and
        you have an IDOR vector.

        Returns a structured response with:
        - Admit/Deny/Insufficient Knowledge for each allegation
        - Factual corrections
        - Legal standard
        - Argument
        - Relief requested
        - Proposed order
        - Exhibit list
        """
        from core.models_legal import GeneratedResponse

        case_profile = doc.case_profile

        # Get case context if not provided
        if not case_context:
            builder = LegalContextBuilder()
            case_context = builder.get_case_context_json(case_profile.id)

        # Extract allegations from the document to respond to
        metadata = doc.extracted_metadata or {}
        allegations = metadata.get('allegations', [])
        relief_requested = metadata.get('relief_requested', [])

        # Generate response components using GPT
        response_content = self._generate_admit_deny_responses(
            allegations, case_context, doc
        )
        factual_corrections = self._generate_factual_corrections(
            doc.extracted_text, case_context
        )
        legal_standard = self._generate_legal_standard(doc.document_type)
        argument = self._generate_argument(
            allegations, relief_requested, case_context
        )
        our_relief = self._generate_relief_requested(doc, case_context)

        # Generate proposed order
        proposed_order = self._generate_proposed_order(
            doc, case_profile, our_relief
        )

        # Build exhibit list from evidence in case
        exhibits = self._build_exhibit_list(case_profile, allegations)

        # Assemble full document
        full_document = self._assemble_response_document(
            case_profile, doc, response_content, factual_corrections,
            legal_standard, argument, our_relief
        )

        # Create GeneratedResponse record
        generated = GeneratedResponse.objects.create(
            case_profile=case_profile,
            responds_to=doc,
            response_content=response_content,
            factual_corrections=factual_corrections,
            legal_standard=legal_standard,
            argument=argument,
            relief_requested=our_relief,
            full_document=full_document,
            proposed_order=proposed_order,
            exhibits=exhibits,
            generation_context={
                'allegations_count': len(allegations),
                'evidence_count': len(exhibits),
                'generated_at': timezone.now().isoformat(),
            }
        )

        # Mark the original document as responded
        doc.status = 'responded'
        doc.save(update_fields=['status', 'updated_at'])

        return {
            'success': True,
            'response_id': str(generated.id),
            'full_document': full_document,
            'proposed_order': proposed_order,
            'exhibits_count': len(exhibits),
        }

    def _generate_admit_deny_responses(
        self, allegations: list, case_context: dict, doc
    ) -> str:
        """Generate Admit/Deny/Insufficient Knowledge responses."""
        if not allegations:
            return "No specific allegations to respond to."

        responses = []
        for i, allegation in enumerate(allegations, 1):
            # For now, generate placeholder - will integrate with GPT
            responses.append(f"{i}. **Allegation:** {allegation}")
            responses.append(f"   **Response:** Denied. [Specific denial or explanation required]")
            responses.append("")

        return "\n".join(responses)

    def _generate_factual_corrections(self, text: str, case_context: dict) -> str:
        """Generate factual corrections based on evidence."""
        return "The Respondent's filing contains the following factual inaccuracies:\n\n[Based on evidence review, specific corrections will be listed here]"

    def _generate_legal_standard(self, document_type: str) -> str:
        """Generate the applicable legal standard."""
        standards = {
            'opposing_motion': """**Applicable Legal Standard**

In Colorado family law matters, the party seeking modification of parenting time must demonstrate:

1. A substantial and continuing change in circumstances
2. That the modification serves the child's best interests

The court considers the factors set forth in C.R.S. § 14-10-124 when determining best interests.""",

            'response': """**Legal Standard for Response**

The responding party has 21 days to respond to a motion under C.R.C.P. 121, Section 1-15.""",
        }

        return standards.get(document_type, standards['response'])

    def _generate_argument(
        self, allegations: list, relief_requested: list, case_context: dict
    ) -> str:
        """Generate the argument section."""
        return """**ARGUMENT**

I. THE MOTION SHOULD BE DENIED

[Detailed argument addressing each allegation and requested relief]

II. THE EVIDENCE DOES NOT SUPPORT THE REQUESTED RELIEF

[Evidence-based rebuttal]

III. THE REQUESTED RELIEF IS NOT IN THE CHILD'S BEST INTERESTS

[Best interests analysis]"""

    def _generate_relief_requested(self, doc, case_context: dict) -> str:
        """Generate our relief requested."""
        return """**RELIEF REQUESTED**

WHEREFORE, Petitioner respectfully requests that this Court:

1. DENY Respondent's Motion in its entirety;
2. Award Petitioner attorney's fees and costs incurred in responding to this Motion;
3. Grant such other and further relief as the Court deems just and proper."""

    def _generate_proposed_order(
        self, doc, case_profile, relief: str
    ) -> str:
        """Generate proposed order."""
        return f"""DISTRICT COURT, {case_profile.county.upper()} COUNTY, COLORADO
Court Address: {case_profile.court_address or '[Court Address]'}

In re: The Marriage/Parental Responsibilities of:

Petitioner: {case_profile.petitioner.full_name if case_profile.petitioner else '[Petitioner Name]'}
And
Respondent: {case_profile.respondent.full_name if case_profile.respondent else '[Respondent Name]'}

Case Number: {case_profile.case_number}
Division: {case_profile.division or '[Division]'}

**PROPOSED ORDER DENYING RESPONDENT'S MOTION**

THIS MATTER comes before the Court on Respondent's {doc.title}. Having reviewed the Motion, Petitioner's Response, and being fully advised in the premises:

THE COURT FINDS AND ORDERS:

1. Respondent's Motion is DENIED.

2. [Additional orders as appropriate]

DATED this _____ day of _____________, 20____.

_________________________________
DISTRICT COURT JUDGE"""

    def _build_exhibit_list(self, case_profile, allegations: list) -> list:
        """Build exhibit list from case evidence."""
        from core.models_legal import LitigationDocument

        evidence_docs = LitigationDocument.objects.filter(
            case_profile=case_profile,
            category='evidence'
        ).order_by('uploaded_at')

        exhibits = []
        for i, doc in enumerate(evidence_docs, 1):
            letter = chr(64 + i) if i <= 26 else str(i)  # A-Z then numbers
            exhibits.append({
                'number': i,
                'letter': letter,
                'title': doc.title,
                'document_id': str(doc.id),
                'description': doc.description or doc.get_document_type_display(),
                'date': str(doc.document_date) if doc.document_date else None,
            })

        return exhibits

    def _assemble_response_document(
        self, case_profile, doc, response_content, factual_corrections,
        legal_standard, argument, relief
    ) -> str:
        """Assemble the complete response document."""
        return f"""DISTRICT COURT, {case_profile.county.upper()} COUNTY, COLORADO
Court Address: {case_profile.court_address or '[Court Address]'}

In re: The Marriage/Parental Responsibilities of:

Petitioner: {case_profile.petitioner.full_name if case_profile.petitioner else '[Petitioner Name]'}
And
Respondent: {case_profile.respondent.full_name if case_profile.respondent else '[Respondent Name]'}

Case Number: {case_profile.case_number}
Division: {case_profile.division or '[Division]'}

**PETITIONER'S RESPONSE TO {doc.title.upper()}**

Petitioner, {case_profile.petitioner.full_name if case_profile.petitioner else '[Petitioner Name]'}, pro se, respectfully submits this Response to Respondent's {doc.title} and states as follows:

**INTRODUCTION**

Petitioner responds to Respondent's filing and denies the allegations contained therein except as specifically admitted below.

**RESPONSE TO ALLEGATIONS**

{response_content}

**FACTUAL CORRECTIONS**

{factual_corrections}

{legal_standard}

{argument}

{relief}

RESPECTFULLY SUBMITTED this _____ day of _____________, 20____.

_________________________________
{case_profile.petitioner.full_name if case_profile.petitioner else '[Petitioner Name]'}
Pro Se Petitioner
[Address]
[Phone]
[Email]

**CERTIFICATE OF SERVICE**

I certify that on the _____ day of _____________, 20____, a true and correct copy of the foregoing was served upon:

{case_profile.respondent.full_name if case_profile.respondent else '[Respondent Name]'}
[or Respondent's Attorney]
[Address]

via [  ] U.S. Mail, first-class postage prepaid
    [  ] Hand Delivery
    [  ] Email to: ____________________


_________________________________
{case_profile.petitioner.full_name if case_profile.petitioner else '[Petitioner Name]'}"""


class LegalFilingPackager:
    """
    Bundles generated documents for filing.
    Creates DOCX, PDF, and ZIP packages with all required documents.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.LegalFilingPackager")

    def create_filing_package(
        self,
        response: "GeneratedResponse",
        formats: List[str] = ['docx', 'txt'],
    ) -> Dict[str, Any]:
        """
        Create a complete filing package.

        `response` MUST be scoped to the requesting user by the caller —
        this service performs no authorization check. Pass a raw ID lookup
        and you have an IDOR vector.

        Includes:
        - Response document
        - Proposed Order
        - Evidence Checklist
        - Exhibit List
        - Conferral Email (if needed)
        """

        package = {
            'documents': [],
            'response_id': str(response.id),
        }

        # Main response
        package['documents'].append({
            'name': 'Response',
            'content': response.full_document,
            'filename': f"Response_to_{response.responds_to.title.replace(' ', '_')[:30]}",
        })

        # Proposed order
        if response.proposed_order:
            package['documents'].append({
                'name': 'Proposed Order',
                'content': response.proposed_order,
                'filename': 'Proposed_Order',
            })

        # Exhibit list
        if response.exhibits:
            exhibit_list = self._format_exhibit_list(response.exhibits, response.case_profile)
            package['documents'].append({
                'name': 'Exhibit List',
                'content': exhibit_list,
                'filename': 'Exhibit_List',
            })

        # Evidence checklist
        checklist = self._create_evidence_checklist(response)
        package['documents'].append({
            'name': 'Evidence Checklist',
            'content': checklist,
            'filename': 'Evidence_Checklist',
        })

        # Generate file data for each format
        files = []
        for doc in package['documents']:
            for fmt in formats:
                if fmt == 'docx':
                    file_data = self._create_docx(doc['content'], doc['filename'])
                elif fmt == 'txt':
                    file_data = doc['content'].encode('utf-8')
                else:
                    continue

                files.append({
                    'name': f"{doc['filename']}.{fmt}",
                    'content': file_data,
                    'document_type': doc['name'],
                })

        package['files'] = files
        package['success'] = True

        return package

    def _format_exhibit_list(self, exhibits: list, case_profile) -> str:
        """Format exhibit list for filing."""
        lines = [
            f"EXHIBIT LIST",
            f"Case Number: {case_profile.case_number}",
            "",
            "Exhibit | Description | Date",
            "--------|-------------|-----",
        ]

        for exhibit in exhibits:
            lines.append(
                f"{exhibit['letter']} | {exhibit['title']} | {exhibit.get('date', 'N/A')}"
            )

        return "\n".join(lines)

    def _create_evidence_checklist(self, response) -> str:
        """Create evidence checklist for preparation."""
        return f"""EVIDENCE CHECKLIST FOR FILING

Case: {response.case_profile.case_number}
Response to: {response.responds_to.title}

[ ] Response document (signed and dated)
[ ] Proposed Order (attached)
[ ] Exhibit List (attached)
[ ] All Exhibits labeled and organized
[ ] Certificate of Service completed
[ ] Copy for Court
[ ] Copy for Respondent/Opposing Counsel
[ ] Copy for your records

FILING INFORMATION:
- File by: [Calculate deadline - typically 21 days from service]
- Filing fee: [Check current fee schedule]
- File at: {response.case_profile.county} County District Court

IMPORTANT REMINDERS:
- Sign all documents before filing
- Keep copies of everything
- Note the file-stamp date and time
- Serve opposing party same day if possible"""

    def _create_docx(self, content: str, filename: str) -> bytes:
        """Create a DOCX file from content."""
        try:
            from docx import Document
            from docx.shared import Inches
            import io

            doc = Document()

            # Set margins
            sections = doc.sections
            for section in sections:
                section.left_margin = Inches(1)
                section.right_margin = Inches(1)
                section.top_margin = Inches(1)
                section.bottom_margin = Inches(1)

            # Add content paragraph by paragraph
            for para in content.split('\n'):
                p = doc.add_paragraph()
                if para.startswith('**') and para.endswith('**'):
                    # Bold header
                    run = p.add_run(para.replace('**', ''))
                    run.bold = True
                else:
                    p.add_run(para)

            # Save to bytes
            buffer = io.BytesIO()
            doc.save(buffer)
            return buffer.getvalue()

        except Exception as e:
            self.logger.error(f"DOCX creation error: {e}")
            return content.encode('utf-8')


# =============================================================================
# Service Instance Getters
# =============================================================================

def get_document_ingestor() -> LegalDocumentIngestor:
    """Get or create the document ingestor instance."""
    return LegalDocumentIngestor()


def get_context_builder() -> LegalContextBuilder:
    """Get or create the context builder instance."""
    return LegalContextBuilder()


def get_response_writer() -> LegalResponseWriter:
    """Get or create the response writer instance."""
    return LegalResponseWriter()


def get_filing_packager() -> LegalFilingPackager:
    """Get or create the filing packager instance."""
    return LegalFilingPackager()

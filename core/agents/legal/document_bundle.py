"""
Session 407: Document Bundle Parser for Legal Document Downloads

This module parses the motion rewriter output into downloadable sections.
Each section can be exported as .docx, .md, or .txt files.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class DocumentSection:
    """A single downloadable section of a legal document bundle."""
    id: str
    label: str
    role: str  # filing_motion, proposed_order, optional_exhibit, checklist, communication_template, analysis
    format: str  # markdown
    content: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LegalDocumentBundle:
    """
    A structured bundle of all sections from a motion rewrite pipeline.

    This allows the frontend to display download buttons for each section:
    - Verified Motion (.docx)
    - Proposed Order (.docx)
    - Appendix A (.docx)
    - Evidence Checklist (.md)
    - Conferral Email (.txt)
    """
    case_number: str
    jurisdiction: str
    pipeline: str
    sections: List[DocumentSection] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'case_number': self.case_number,
            'jurisdiction': self.jurisdiction,
            'pipeline': self.pipeline,
            'sections': [s.to_dict() for s in self.sections]
        }

    def get_section(self, section_id: str) -> Optional[DocumentSection]:
        """Get a section by ID."""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None


def parse_motion_output_to_bundle(
    full_output: str,
    case_number: str = '',
    county: str = '',
    state: str = 'CO'
) -> LegalDocumentBundle:
    """
    Parse the motion rewriter's full output into a structured bundle.

    The output has these sections (separated by `---`):
    - PART 1: PROCEDURAL DEFECTS IDENTIFIED
    - PART 2: NON-PARTY RULE CHECK
    - PART 3: CORRECTED MOTION (contains the gold standard motion)
    - PART 4: EVIDENCE CHECKLIST
    - PART 5: LIKELIHOOD OF SUCCESS
    - PART 6: CONFERRAL EMAIL

    PART 3 internally contains (separated by `------------------------------------------------------------`):
    - Motion body (caption through Certificate of Service)
    - APPENDIX A (optional exhibit)

    We extract:
    1. motion_core - The verified motion (everything in PART 3 up to APPENDIX A)
    2. proposed_order - Just the PROPOSED ORDER section from within the motion
    3. appendix_a - The factual narrative exhibit
    4. evidence_checklist - PART 4 content
    5. conferral_email - PART 6 content (if present)
    """
    bundle = LegalDocumentBundle(
        case_number=case_number or 'Unknown',
        jurisdiction=f"{state}_{county}".upper() if county else state.upper(),
        pipeline='denied_motion_rewrite'
    )

    # Split by main PART headers
    parts = re.split(r'\n---\n', full_output)

    part3_content = ''
    part4_content = ''
    part5_content = ''
    part6_content = ''

    for part in parts:
        if '## PART 3:' in part or 'CORRECTED MOTION' in part:
            # Extract everything after the header
            match = re.search(r'## PART 3:[^\n]*\n(?:\*[^\n]*\*\n\n)?(.+)', part, re.DOTALL)
            if match:
                part3_content = match.group(1).strip()
        elif '## PART 4:' in part or 'EVIDENCE CHECKLIST' in part:
            match = re.search(r'## PART 4:[^\n]*\n(?:\*[^\n]*\*\n\n)?(.+)', part, re.DOTALL)
            if match:
                part4_content = match.group(1).strip()
        elif '## PART 5:' in part or 'LIKELIHOOD OF SUCCESS' in part:
            match = re.search(r'## PART 5:[^\n]*\n(.+)', part, re.DOTALL)
            if match:
                part5_content = match.group(1).strip()
        elif '## PART 6:' in part or 'CONFERRAL EMAIL' in part:
            match = re.search(r'## PART 6:[^\n]*\n(?:\*[^\n]*\*\n\n)?(.+)', part, re.DOTALL)
            if match:
                part6_content = match.group(1).strip()

    # Parse PART 3 into sub-sections
    if part3_content:
        # Split on APPENDIX A if present
        appendix_split = re.split(
            r'\n*={10,}\nAPPENDIX A:',
            part3_content,
            maxsplit=1
        )

        motion_body = appendix_split[0].strip()
        appendix_content = ''
        if len(appendix_split) > 1:
            appendix_content = 'APPENDIX A:' + appendix_split[1].strip()

        # Extract PROPOSED ORDER section from motion body
        proposed_order = _extract_proposed_order(motion_body)

        # The motion_core is the full motion body (including proposed order)
        # because that's what you file with the court
        bundle.sections.append(DocumentSection(
            id='motion_core',
            label='Verified Motion (Full Filing)',
            role='filing_motion',
            format='markdown',
            content=motion_body
        ))

        # Also provide just the proposed order as a separate document
        # (some courts want it on a separate page)
        if proposed_order:
            bundle.sections.append(DocumentSection(
                id='proposed_order',
                label='Proposed Order (Separate)',
                role='proposed_order',
                format='markdown',
                content=proposed_order
            ))

        # Appendix A (optional exhibit)
        if appendix_content:
            bundle.sections.append(DocumentSection(
                id='appendix_a',
                label='Appendix A - Factual Narrative',
                role='optional_exhibit',
                format='markdown',
                content=appendix_content
            ))

    # Evidence Checklist
    if part4_content:
        bundle.sections.append(DocumentSection(
            id='evidence_checklist',
            label='Evidence Checklist',
            role='checklist',
            format='markdown',
            content=part4_content
        ))

    # Likelihood of Success (analysis - typically not downloaded but could be useful)
    if part5_content:
        bundle.sections.append(DocumentSection(
            id='success_analysis',
            label='Success Analysis',
            role='analysis',
            format='markdown',
            content=part5_content
        ))

    # Conferral Email
    if part6_content:
        # Extract just the email body from the markdown code block
        email_body = _extract_email_body(part6_content)
        bundle.sections.append(DocumentSection(
            id='conferral_email',
            label='Conferral Email Template',
            role='communication_template',
            format='markdown',
            content=email_body if email_body else part6_content
        ))

    logger.info(f"[Session 407] Parsed {len(bundle.sections)} sections from motion output")
    return bundle


def _extract_proposed_order(motion_body: str) -> str:
    """
    Extract just the PROPOSED ORDER section from the motion body.

    The proposed order starts with the PROPOSED ORDER header and ends
    at CERTIFICATE OF SERVICE or end of document.
    """
    # Find PROPOSED ORDER section
    match = re.search(
        r'(-{20,}\nPROPOSED ORDER[^\n]*\n-{20,}\n)(.*?)(?=-{20,}\nCERTIFICATE OF SERVICE|$)',
        motion_body,
        re.DOTALL
    )

    if match:
        # Include the header
        return match.group(1) + match.group(2).strip()

    return ''


def _extract_email_body(part6_content: str) -> str:
    """
    Extract the email body from within markdown code blocks.

    The conferral email is wrapped in ```...``` in the output.
    """
    # Try to extract from code block
    match = re.search(r'```\n?(.*?)\n?```', part6_content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no code block, look for Subject: line and take everything after
    match = re.search(r'(Subject:.*)', part6_content, re.DOTALL)
    if match:
        return match.group(1).strip()

    return ''


def generate_docx_from_section(section: DocumentSection) -> bytes:
    """
    Generate a Word document from a section's content.

    This applies basic court document formatting:
    - Times New Roman 12pt
    - 1" margins
    - Double-spaced
    """
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from io import BytesIO

    doc = Document()

    # Set margins
    for section_obj in doc.sections:
        section_obj.top_margin = Inches(1)
        section_obj.bottom_margin = Inches(1)
        section_obj.left_margin = Inches(1)
        section_obj.right_margin = Inches(1)

    # Split content into lines and add as paragraphs
    lines = section.content.split('\n')

    for line in lines:
        # Skip empty lines by adding empty paragraph
        if not line.strip():
            doc.add_paragraph()
            continue

        # Check if this is a header line (dashes or section markers)
        if re.match(r'^-{10,}$', line.strip()):
            # Skip pure separator lines, they'll be implied by formatting
            continue

        if re.match(r'^={10,}$', line.strip()):
            # Add a page break before APPENDIX sections
            doc.add_page_break()
            continue

        # Add the paragraph
        para = doc.add_paragraph()

        # Check if this is a centered header
        is_header = (
            line.strip().startswith('DISTRICT COURT') or
            line.strip().startswith('ORDER ON') or
            line.strip().startswith('VERIFIED MOTION') or
            line.strip().startswith('APPENDIX') or
            'PROPOSED ORDER' in line.upper() or
            'CERTIFICATE OF' in line.upper() or
            'RELIEF REQUESTED' in line.upper() or
            'FACTS' in line.upper() and 'VERIFIED' in line.upper()
        )

        # Style the paragraph
        run = para.add_run(line)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)

        if is_header:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run.font.bold = True

    # Save to bytes
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def generate_txt_from_section(section: DocumentSection) -> bytes:
    """Generate a plain text file from section content."""
    # Strip markdown formatting
    content = section.content
    # Remove bold markers
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
    # Remove italic markers
    content = re.sub(r'\*([^*]+)\*', r'\1', content)
    # Remove header markers
    content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)

    return content.encode('utf-8')


def generate_md_from_section(section: DocumentSection) -> bytes:
    """Generate a markdown file from section content."""
    return section.content.encode('utf-8')


def generate_pdf_from_section(section: DocumentSection) -> bytes:
    """
    Generate a PDF document from a section's content using reportlab.

    This applies court document formatting:
    - Times New Roman 12pt
    - 1" margins
    - Proper headers centered and bold
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from io import BytesIO

    buf = BytesIO()

    # Create document with 1" margins
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=1*inch,
        rightMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )

    # Create styles
    styles = getSampleStyleSheet()

    # Normal body text - Times New Roman 12pt, justified
    body_style = ParagraphStyle(
        'CourtBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6
    )

    # Centered header style (for DISTRICT COURT, etc.)
    header_style = ParagraphStyle(
        'CourtHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=6
    )

    # Section header style (for FACTS, RELIEF REQUESTED, etc.)
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=6
    )

    # Build the document content
    story = []
    lines = section.content.split('\n')

    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines - add spacer instead
        if not line_stripped:
            story.append(Spacer(1, 6))
            continue

        # Skip separator lines (dashes)
        if re.match(r'^-{10,}$', line_stripped):
            story.append(Spacer(1, 3))
            continue

        # Page break for APPENDIX sections
        if re.match(r'^={10,}$', line_stripped):
            story.append(PageBreak())
            continue

        # Escape special characters for reportlab
        safe_line = line_stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Check if this is a centered header
        is_court_header = (
            line_stripped.startswith('DISTRICT COURT') or
            line_stripped.startswith('Court Address:') or
            line_stripped.startswith('Petitioner:') or
            line_stripped.startswith('Respondent:') or
            line_stripped.startswith('Case Number:') or
            line_stripped.startswith('Division:')
        )

        is_section_header = (
            line_stripped.startswith('ORDER ON') or
            line_stripped.startswith('VERIFIED MOTION') or
            line_stripped.startswith('APPENDIX') or
            'PROPOSED ORDER' in line_stripped.upper() or
            'CERTIFICATE OF' in line_stripped.upper() or
            'RELIEF REQUESTED' in line_stripped.upper() or
            'VERIFICATION' in line_stripped.upper() or
            'EXISTING COURT ORDERS' in line_stripped.upper() or
            ('FACTS' in line_stripped.upper() and 'VERIFIED' in line_stripped.upper())
        )

        # Apply appropriate style
        if is_court_header:
            story.append(Paragraph(safe_line, header_style))
        elif is_section_header:
            story.append(Paragraph(f'<b>{safe_line}</b>', section_header_style))
        else:
            story.append(Paragraph(safe_line, body_style))

    # Build PDF
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

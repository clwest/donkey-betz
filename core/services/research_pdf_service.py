"""
Research PDF Export Service
============================

Session 325: Export research analysis to professional PDFs

This service generates downloadable PDF reports from business research
(Customer Research, Competitor Analysis) for offline use and sharing.

Features:
- Professional formatting
- Executive summary
- Key findings sections
- Source citations
- Platform branding

Usage:
    from core.services.research_pdf_service import ResearchPDFService

    service = ResearchPDFService()
    pdf_bytes = service.generate_research_pdf(project_id, research_index)
"""

import io
import logging
import textwrap
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass

from django.conf import settings

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

logger = logging.getLogger(__name__)

# Platform branding
PLATFORM_NAME = "Donkey AI Studio"
REPORT_VERSION = "1.0"

# Colors
PRIMARY_COLOR = HexColor("#4F46E5")  # Indigo
SECONDARY_COLOR = HexColor("#6366F1")
ACCENT_COLOR = HexColor("#10B981")  # Emerald
DARK_COLOR = HexColor("#1F2937")
LIGHT_COLOR = HexColor("#F3F4F6")
PURPLE_COLOR = HexColor("#A855F7")


@dataclass
class PDFResult:
    """Result from PDF generation."""
    success: bool
    pdf_bytes: Optional[bytes] = None
    filename: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'filename': self.filename,
            'error': self.error,
        }


class ResearchPDFService:
    """
    Service for generating PDF research reports.

    Creates professional, formatted reports from business research
    stored in project metadata.
    """

    def __init__(self):
        self.platform_name = PLATFORM_NAME
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=PRIMARY_COLOR,
            spaceAfter=20,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=SECONDARY_COLOR,
            spaceBefore=15,
            spaceAfter=10
        ))

        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=DARK_COLOR,
            spaceBefore=10,
            spaceAfter=5
        ))

        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=DARK_COLOR,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        ))

        self.styles.add(ParagraphStyle(
            name='Quote',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor("#4B5563"),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            leading=12,
            fontName='Helvetica-Oblique'
        ))

        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=HexColor("#9CA3AF"),
            alignment=TA_CENTER
        ))

    def generate_research_pdf(
        self,
        project_id: str,
        research_index: int = -1
    ) -> PDFResult:
        """
        Generate a PDF report for research in a project.

        Args:
            project_id: UUID of the project
            research_index: Index of research summary (-1 for latest)

        Returns:
            PDFResult with PDF bytes
        """
        try:
            from core.models_partnership import PartnershipProject

            project = PartnershipProject.objects.get(id=project_id)
            metadata = project.metadata or {}

            research_summaries = metadata.get('research_summaries', [])
            if not research_summaries:
                return PDFResult(
                    success=False,
                    error='No research found in this project'
                )

            # Get the requested research (default to latest)
            if research_index == -1:
                research = research_summaries[-1]
            else:
                research = research_summaries[research_index]

            # Generate PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )

            story = []

            # Build the document
            self._add_header(story, project, research)
            self._add_executive_summary(story, research)
            self._add_analysis_content(story, research)
            self._add_sources_section(story, research, metadata)
            self._add_footer(story, project)

            # Build PDF
            doc.build(story)

            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            # Generate filename
            research_type = research.get('type', 'research').replace('_', '-')
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"{project.project_name[:30]}-{research_type}-{date_str}.pdf"
            filename = filename.replace(' ', '-').replace('/', '-')

            logger.info(f"Research PDF generated for project {project_id}")

            return PDFResult(
                success=True,
                pdf_bytes=pdf_bytes,
                filename=filename
            )

        except PartnershipProject.DoesNotExist:
            return PDFResult(success=False, error='Project not found')
        except Exception as e:
            logger.error(f"Error generating research PDF: {e}")
            import traceback
            traceback.print_exc()
            return PDFResult(success=False, error=str(e))

    def _add_header(self, story: List, project, research: Dict):
        """Add report header."""
        # Title based on research type
        research_type = research.get('type', 'business_research')
        if research_type == 'customer_research':
            title = "Customer Research Report"
            icon = "👥"
        elif research_type == 'competitor_analysis':
            title = "Competitive Analysis Report"
            icon = "🎯"
        else:
            title = "Business Research Report"
            icon = "📊"

        story.append(Paragraph(f"{title}", self.styles['ReportTitle']))
        story.append(Spacer(1, 10))

        # Project info
        story.append(Paragraph(
            f"<b>Project:</b> {project.project_name}",
            self.styles['BodyText']
        ))

        # Date
        timestamp = research.get('timestamp', datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            date_str = timestamp

        story.append(Paragraph(
            f"<b>Generated:</b> {date_str}",
            self.styles['BodyText']
        ))

        # Data points and sources
        data_points = research.get('data_points', 0)
        sources = research.get('sources', [])
        story.append(Paragraph(
            f"<b>Analysis:</b> {data_points} data points from {len(sources)} sources",
            self.styles['BodyText']
        ))

        story.append(Spacer(1, 20))

        # Horizontal line
        story.append(Paragraph("—" * 80, self.styles['BodyText']))
        story.append(Spacer(1, 10))

    def _add_executive_summary(self, story: List, research: Dict):
        """Add executive summary section."""
        summary = research.get('summary', '')
        if not summary:
            return

        story.append(Paragraph("Executive Summary", self.styles['SectionTitle']))

        # Extract first paragraph or first 500 chars as executive summary
        paragraphs = summary.split('\n\n')
        exec_summary = paragraphs[0] if paragraphs else summary[:500]

        # Clean up markdown
        exec_summary = self._clean_markdown(exec_summary)

        story.append(Paragraph(exec_summary, self.styles['BodyText']))
        story.append(Spacer(1, 15))

    def _add_analysis_content(self, story: List, research: Dict):
        """Add the main analysis content."""
        summary = research.get('summary', '')
        if not summary:
            return

        story.append(Paragraph("Detailed Analysis", self.styles['SectionTitle']))

        # Split into sections based on markdown headers
        sections = self._parse_sections(summary)

        for section in sections:
            if section.get('title'):
                story.append(Paragraph(
                    section['title'],
                    self.styles['SubSection']
                ))

            content = self._clean_markdown(section.get('content', ''))

            # Split into paragraphs
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # Check for bullet points
                if para.startswith('- ') or para.startswith('• '):
                    lines = para.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('- ') or line.startswith('• '):
                            line = '• ' + line[2:]
                        story.append(Paragraph(line, self.styles['BodyText']))
                else:
                    story.append(Paragraph(para, self.styles['BodyText']))

            story.append(Spacer(1, 5))

        story.append(Spacer(1, 15))

    def _add_sources_section(self, story: List, research: Dict, metadata: Dict):
        """Add sources section."""
        sources = research.get('sources', [])
        articles = metadata.get('research_articles', [])

        if sources or articles:
            story.append(Paragraph("Sources", self.styles['SectionTitle']))

        if sources:
            sources_text = ", ".join(sources)
            story.append(Paragraph(
                f"<b>Data Sources:</b> {sources_text}",
                self.styles['BodyText']
            ))

        if articles:
            story.append(Spacer(1, 10))
            story.append(Paragraph("Referenced Articles:", self.styles['SubSection']))

            for i, article in enumerate(articles[:10], 1):
                title = article.get('title', 'Untitled')
                url = article.get('url', article.get('link', ''))
                source = article.get('source', 'Unknown')

                article_text = f"{i}. <b>{title}</b> ({source})"
                if url:
                    article_text = f"{i}. <link href='{url}'><b>{title}</b></link> ({source})"

                story.append(Paragraph(article_text, self.styles['BodyText']))

    def _add_footer(self, story: List, project):
        """Add report footer."""
        story.append(Spacer(1, 30))
        story.append(Paragraph("—" * 80, self.styles['BodyText']))
        story.append(Spacer(1, 10))

        story.append(Paragraph(
            f"Generated by {self.platform_name}",
            self.styles['Footer']
        ))
        story.append(Paragraph(
            f"Report Version {REPORT_VERSION} • {datetime.now().strftime('%Y-%m-%d')}",
            self.styles['Footer']
        ))

    def _clean_markdown(self, text: str) -> str:
        """Clean markdown formatting for PDF."""
        if not text:
            return ""

        # Remove markdown headers (we handle them separately)
        import re
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Convert bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__([^_]+)__', r'<b>\1</b>', text)

        # Convert italic
        text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
        text = re.sub(r'_([^_]+)_', r'<i>\1</i>', text)

        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def _parse_sections(self, text: str) -> List[Dict]:
        """Parse markdown text into sections."""
        import re

        sections = []
        current_section = {'title': None, 'content': ''}

        lines = text.split('\n')
        for line in lines:
            # Check for headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_section['content'].strip():
                    sections.append(current_section)

                current_section = {
                    'title': header_match.group(2),
                    'content': ''
                }
            else:
                current_section['content'] += line + '\n'

        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)

        return sections


# Convenience function
def generate_research_pdf(project_id: str, research_index: int = -1) -> PDFResult:
    """Generate a research PDF for a project."""
    service = ResearchPDFService()
    return service.generate_research_pdf(project_id, research_index)

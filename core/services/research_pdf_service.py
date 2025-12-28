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
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass


# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

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
            name='ReportBody',
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
            self.styles['ReportBody']
        ))

        # Date
        timestamp = research.get('timestamp', datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime('%B %d, %Y at %I:%M %p')
        except Exception:
            date_str = timestamp

        story.append(Paragraph(
            f"<b>Generated:</b> {date_str}",
            self.styles['ReportBody']
        ))

        # Data points and sources
        data_points = research.get('data_points', 0)
        sources = research.get('sources', [])
        story.append(Paragraph(
            f"<b>Analysis:</b> {data_points} data points from {len(sources)} sources",
            self.styles['ReportBody']
        ))

        story.append(Spacer(1, 20))

        # Horizontal line
        story.append(Paragraph("—" * 80, self.styles['ReportBody']))
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

        story.append(Paragraph(exec_summary, self.styles['ReportBody']))
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
                        story.append(Paragraph(line, self.styles['ReportBody']))
                else:
                    story.append(Paragraph(para, self.styles['ReportBody']))

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
                self.styles['ReportBody']
            ))

        if articles:
            story.append(Spacer(1, 10))
            story.append(Paragraph("Referenced Articles:", self.styles['SubSection']))

            for i, article in enumerate(articles[:10], 1):
                title = article.get('title', 'Untitled')
                url = article.get('url', article.get('link', ''))
                source = article.get('source', 'Unknown')

                # Session 349: Sanitize title - remove HTML and special characters
                title = self._clean_markdown(title)
                title = title[:100]  # Limit length

                article_text = f"{i}. \"{title}\" ({source})"
                story.append(Paragraph(article_text, self.styles['ReportBody']))

    def _add_footer(self, story: List, project):
        """Add report footer."""
        story.append(Spacer(1, 30))
        story.append(Paragraph("—" * 80, self.styles['ReportBody']))
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

        import re

        # Session 349: Strip ALL HTML tags that break ReportLab PDF generation
        # Spider data from Medium RSS feeds contains raw/malformed HTML
        # ReportLab's Paragraph parser only supports: b, i, u, link, br, para

        # First, strip ALL HTML tags aggressively (including malformed ones)
        # This catches <a href="..., <div class="..., etc.
        text = re.sub(r'<[^>]*>', '', text)  # Remove all HTML tags
        text = re.sub(r'<[^>]*$', '', text)  # Remove incomplete tags at end
        text = re.sub(r'^[^<]*>', '', text)  # Remove incomplete tags at start

        # Remove HTML entities
        text = re.sub(r'&#x[0-9a-fA-F]+;', '', text)  # Hex entities
        text = re.sub(r'&#\d+;', '', text)  # Decimal entities
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)  # Named entities like &nbsp;

        # Remove any remaining angle brackets that might cause issues
        text = text.replace('<', '').replace('>', '')

        # Remove markdown headers (we handle them separately)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Convert bold (only if we're sure there's no HTML contamination)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Just remove ** markers
        text = re.sub(r'__([^_]+)__', r'\1', text)

        # Convert italic
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)

        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

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


    def generate_comprehensive_pdf(self, project_id: str) -> PDFResult:
        """
        Session 352: Generate a comprehensive PDF with ALL research summaries.

        Combines all research (Trend Analysis, Competitor Analysis, Customer Research)
        into one complete document.

        Args:
            project_id: UUID of the project

        Returns:
            PDFResult with PDF bytes containing all research
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

            # Add comprehensive header
            self._add_comprehensive_header(story, project, research_summaries)

            # Add table of contents
            self._add_table_of_contents(story, research_summaries)

            # Add each research section
            for idx, research in enumerate(research_summaries):
                self._add_research_section(story, research, idx + 1)

            # Add combined sources section
            self._add_combined_sources(story, research_summaries, metadata)

            # Add footer
            self._add_footer(story, project)

            # Build PDF
            doc.build(story)

            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            # Generate filename
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"{project.project_name[:30]}-complete-research-{date_str}.pdf"
            filename = filename.replace(' ', '-').replace('/', '-')

            logger.info(f"Comprehensive research PDF generated for project {project_id} with {len(research_summaries)} sections")

            return PDFResult(
                success=True,
                pdf_bytes=pdf_bytes,
                filename=filename
            )

        except PartnershipProject.DoesNotExist:
            return PDFResult(success=False, error='Project not found')
        except Exception as e:
            logger.error(f"Error generating comprehensive research PDF: {e}")
            import traceback
            traceback.print_exc()
            return PDFResult(success=False, error=str(e))

    def _add_comprehensive_header(self, story: List, project, research_summaries: List[Dict]):
        """Add header for comprehensive report."""
        story.append(Paragraph("Complete Business Research Report", self.styles['ReportTitle']))
        story.append(Spacer(1, 10))

        # Project info
        story.append(Paragraph(
            f"<b>Project:</b> {project.project_name}",
            self.styles['ReportBody']
        ))

        # Project description if available
        if project.description:
            story.append(Paragraph(
                f"<b>Description:</b> {project.description[:200]}",
                self.styles['ReportBody']
            ))

        # Summary stats
        total_data_points = sum(r.get('data_points', 0) for r in research_summaries)
        all_sources = set()
        for r in research_summaries:
            all_sources.update(r.get('sources', []))

        story.append(Paragraph(
            f"<b>Total Analysis:</b> {len(research_summaries)} research sections, {total_data_points} data points, {len(all_sources)} unique sources",
            self.styles['ReportBody']
        ))

        story.append(Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['ReportBody']
        ))

        story.append(Spacer(1, 20))
        story.append(Paragraph("—" * 80, self.styles['ReportBody']))
        story.append(Spacer(1, 10))

    def _add_table_of_contents(self, story: List, research_summaries: List[Dict]):
        """Add table of contents."""
        story.append(Paragraph("Table of Contents", self.styles['SectionTitle']))
        story.append(Spacer(1, 10))

        for idx, research in enumerate(research_summaries, 1):
            research_type = research.get('type', 'business_research')
            type_labels = {
                'trend_analysis': 'Trend Analysis',
                'competitor_analysis': 'Competitive Analysis',
                'customer_research': 'Customer Research',
                'business_research': 'Business Research'
            }
            label = type_labels.get(research_type, research_type.replace('_', ' ').title())
            data_points = research.get('data_points', 0)

            story.append(Paragraph(
                f"{idx}. {label} ({data_points} data points)",
                self.styles['ReportBody']
            ))

        story.append(Spacer(1, 20))
        story.append(Paragraph("—" * 80, self.styles['ReportBody']))
        story.append(Spacer(1, 15))

    def _add_research_section(self, story: List, research: Dict, section_num: int):
        """Add a single research section to the comprehensive report."""
        research_type = research.get('type', 'business_research')

        # Section header with icon
        type_config = {
            'trend_analysis': ('Trend Analysis', '📈'),
            'competitor_analysis': ('Competitive Analysis', '🎯'),
            'customer_research': ('Customer Research', '👥'),
            'business_research': ('Business Research', '📊')
        }
        label, icon = type_config.get(research_type, ('Research', '📋'))

        # Add section title
        story.append(Paragraph(
            f"Section {section_num}: {label}",
            self.styles['SectionTitle']
        ))

        # Metadata line
        data_points = research.get('data_points', 0)
        sources = research.get('sources', [])
        timestamp = research.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime('%B %d, %Y')
        except Exception:
            date_str = 'Unknown'

        story.append(Paragraph(
            f"<i>{data_points} data points from {len(sources)} sources • {date_str}</i>",
            self.styles['ReportBody']
        ))
        story.append(Spacer(1, 10))

        # Add the analysis content
        summary = research.get('summary', '')
        if summary:
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
                            story.append(Paragraph(line, self.styles['ReportBody']))
                    else:
                        story.append(Paragraph(para, self.styles['ReportBody']))

                story.append(Spacer(1, 5))

        # Section divider
        story.append(Spacer(1, 15))
        story.append(Paragraph("—" * 80, self.styles['ReportBody']))
        story.append(Spacer(1, 15))

    def _add_combined_sources(self, story: List, research_summaries: List[Dict], metadata: Dict):
        """Add combined sources section."""
        story.append(Paragraph("All Sources", self.styles['SectionTitle']))

        # Collect all unique sources
        all_sources = set()
        for research in research_summaries:
            all_sources.update(research.get('sources', []))

        if all_sources:
            sources_text = ", ".join(sorted(all_sources))
            story.append(Paragraph(
                f"<b>Data Sources:</b> {sources_text}",
                self.styles['ReportBody']
            ))

        # Add research articles
        articles = metadata.get('research_articles', [])
        if articles:
            story.append(Spacer(1, 10))
            story.append(Paragraph("Referenced Articles:", self.styles['SubSection']))

            for i, article in enumerate(articles[:15], 1):  # Show up to 15 articles
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')

                title = self._clean_markdown(title)
                title = title[:100]

                article_text = f"{i}. \"{title}\" ({source})"
                story.append(Paragraph(article_text, self.styles['ReportBody']))


# Convenience functions
def generate_research_pdf(project_id: str, research_index: int = -1) -> PDFResult:
    """Generate a research PDF for a project."""
    service = ResearchPDFService()
    return service.generate_research_pdf(project_id, research_index)


def generate_comprehensive_pdf(project_id: str) -> PDFResult:
    """Session 352: Generate a comprehensive PDF with all research for a project."""
    service = ResearchPDFService()
    return service.generate_comprehensive_pdf(project_id)

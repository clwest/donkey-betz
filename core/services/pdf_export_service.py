"""
PDF Export Service
==================

Session 918: Generates downloadable PDF reports from agent output.

Supports all report types:
- Sports: Odds analysis, arbitrage reports
- Financial: Stock analysis, bull/bear cases, market intelligence
- Blockchain: Smart contract audits, whale alerts, exploit detection
- Narrative: Cultural analysis, trend reports
- Strategy: Brand, content, SEO strategies
- Research: General research reports

Uses WeasyPrint for HTML/CSS to PDF conversion.
"""

import io
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# Report category styling
CATEGORY_STYLES = {
    'sports': {
        'primary_color': '#16a34a',  # Green
        'secondary_color': '#166534',
        'icon': '🏈',
        'header_bg': 'linear-gradient(135deg, #16a34a 0%, #166534 100%)',
    },
    'financial': {
        'primary_color': '#2563eb',  # Blue
        'secondary_color': '#1d4ed8',
        'icon': '📈',
        'header_bg': 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
    },
    'blockchain': {
        'primary_color': '#7c3aed',  # Purple
        'secondary_color': '#6d28d9',
        'icon': '⛓️',
        'header_bg': 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
    },
    'narrative': {
        'primary_color': '#ea580c',  # Orange
        'secondary_color': '#c2410c',
        'icon': '📖',
        'header_bg': 'linear-gradient(135deg, #ea580c 0%, #c2410c 100%)',
    },
    'strategy': {
        'primary_color': '#0891b2',  # Cyan
        'secondary_color': '#0e7490',
        'icon': '🎯',
        'header_bg': 'linear-gradient(135deg, #0891b2 0%, #0e7490 100%)',
    },
    'research': {
        'primary_color': '#4f46e5',  # Indigo
        'secondary_color': '#4338ca',
        'icon': '🔬',
        'header_bg': 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)',
    },
    'default': {
        'primary_color': '#374151',  # Gray
        'secondary_color': '#1f2937',
        'icon': '📄',
        'header_bg': 'linear-gradient(135deg, #374151 0%, #1f2937 100%)',
    },
}


@dataclass
class PDFExportConfig:
    """Configuration for PDF export."""
    include_provenance: bool = True
    include_disclaimer: bool = True
    include_timestamp: bool = True
    page_size: str = 'letter'  # letter, A4
    margin: str = '1in'
    font_family: str = 'system-ui, -apple-system, sans-serif'


def get_base_css(category: str = 'default', config: PDFExportConfig = None) -> str:
    """Generate base CSS for PDF reports."""
    config = config or PDFExportConfig()
    style = CATEGORY_STYLES.get(category, CATEGORY_STYLES['default'])

    return f"""
    @page {{
        size: {config.page_size};
        margin: {config.margin};
        @bottom-center {{
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10px;
            color: #666;
        }}
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        font-family: {config.font_family};
        font-size: 11pt;
        line-height: 1.6;
        color: #1f2937;
        margin: 0;
        padding: 0;
    }}

    .report-header {{
        background: {style['header_bg']};
        color: white;
        padding: 24px;
        margin: -1in -1in 24px -1in;
        width: calc(100% + 2in);
    }}

    .report-header h1 {{
        margin: 0 0 8px 0;
        font-size: 24pt;
        font-weight: 700;
    }}

    .report-header .subtitle {{
        font-size: 12pt;
        opacity: 0.9;
    }}

    .report-header .meta {{
        margin-top: 16px;
        font-size: 10pt;
        opacity: 0.8;
    }}

    .provenance-block {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 24px;
        font-size: 10pt;
    }}

    .provenance-block h3 {{
        margin: 0 0 12px 0;
        color: {style['primary_color']};
        font-size: 12pt;
    }}

    .provenance-block .sources {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
    }}

    .provenance-block .source-tag {{
        background: #e2e8f0;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 9pt;
    }}

    .validation-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 9pt;
        font-weight: 600;
        text-transform: uppercase;
    }}

    .validation-verified {{
        background: #dcfce7;
        color: #166534;
    }}

    .validation-partially {{
        background: #fef9c3;
        color: #854d0e;
    }}

    .validation-unverified {{
        background: #fee2e2;
        color: #991b1b;
    }}

    .content {{
        margin-bottom: 24px;
    }}

    h2 {{
        color: {style['primary_color']};
        border-bottom: 2px solid {style['primary_color']};
        padding-bottom: 8px;
        margin-top: 32px;
        margin-bottom: 16px;
        font-size: 16pt;
    }}

    h3 {{
        color: {style['secondary_color']};
        margin-top: 24px;
        margin-bottom: 12px;
        font-size: 13pt;
    }}

    h4 {{
        color: #4b5563;
        margin-top: 20px;
        margin-bottom: 8px;
        font-size: 11pt;
    }}

    p {{
        margin: 0 0 12px 0;
    }}

    ul, ol {{
        margin: 0 0 16px 0;
        padding-left: 24px;
    }}

    li {{
        margin-bottom: 6px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 10pt;
    }}

    th {{
        background: {style['primary_color']};
        color: white;
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
    }}

    td {{
        padding: 10px 12px;
        border-bottom: 1px solid #e2e8f0;
    }}

    tr:nth-child(even) {{
        background: #f8fafc;
    }}

    code {{
        background: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'SF Mono', Monaco, Consolas, monospace;
        font-size: 9pt;
    }}

    pre {{
        background: #1f2937;
        color: #e5e7eb;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        font-size: 9pt;
        line-height: 1.4;
    }}

    pre code {{
        background: none;
        padding: 0;
        color: inherit;
    }}

    blockquote {{
        border-left: 4px solid {style['primary_color']};
        margin: 16px 0;
        padding: 12px 16px;
        background: #f8fafc;
        font-style: italic;
    }}

    .risk-flag {{
        border-left: 4px solid;
        padding: 12px 16px;
        margin: 16px 0;
        border-radius: 0 8px 8px 0;
    }}

    .risk-critical {{
        border-color: #dc2626;
        background: #fef2f2;
    }}

    .risk-high {{
        border-color: #ea580c;
        background: #fff7ed;
    }}

    .risk-medium {{
        border-color: #ca8a04;
        background: #fefce8;
    }}

    .risk-low {{
        border-color: #16a34a;
        background: #f0fdf4;
    }}

    .disclaimer {{
        margin-top: 32px;
        padding: 16px;
        background: #f1f5f9;
        border-radius: 8px;
        font-size: 9pt;
        color: #64748b;
        text-align: center;
    }}

    .footer {{
        margin-top: 48px;
        padding-top: 16px;
        border-top: 1px solid #e2e8f0;
        font-size: 9pt;
        color: #9ca3af;
        text-align: center;
    }}

    /* Signal/Recommendation boxes */
    .signal-box {{
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
    }}

    .signal-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}

    .signal-type {{
        font-weight: 600;
        color: {style['primary_color']};
    }}

    .confidence-bar {{
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        margin-top: 8px;
    }}

    .confidence-fill {{
        height: 100%;
        background: {style['primary_color']};
        border-radius: 4px;
    }}

    /* Scenario cards for finance */
    .scenario-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 16px 0;
    }}

    .scenario-card {{
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
    }}

    .scenario-bull {{
        border-top: 4px solid #16a34a;
    }}

    .scenario-base {{
        border-top: 4px solid #2563eb;
    }}

    .scenario-bear {{
        border-top: 4px solid #dc2626;
    }}
    """


def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown content to HTML."""
    try:
        import markdown
        from markdown.extensions.tables import TableExtension
        from markdown.extensions.fenced_code import FencedCodeExtension

        md = markdown.Markdown(extensions=[
            TableExtension(),
            FencedCodeExtension(),
            'nl2br',
        ])
        return md.convert(markdown_content)
    except ImportError:
        # Fallback: basic conversion
        import re
        html = markdown_content

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Code blocks
        html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # Lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'

        return html


def build_provenance_html(provenance: Dict[str, Any]) -> str:
    """Build HTML for the provenance block."""
    if not provenance:
        return ""

    validation_status = provenance.get('validation_status', 'unverified')
    validation_class = {
        'verified': 'validation-verified',
        'partially_verified': 'validation-partially',
        'unverified': 'validation-unverified',
        'stale': 'validation-unverified',
    }.get(validation_status, 'validation-unverified')

    sources_html = ""
    for src in provenance.get('sources', []):
        freshness = f"{src.get('freshness_hours', 0):.1f}h ago" if src.get('freshness_hours') else "unknown"
        sources_html += f'<span class="source-tag">{src.get("name", "Unknown")} ({src.get("record_count", 0)} records, {freshness})</span>'

    publishable = '✅ Yes' if provenance.get('publishable') else '❌ No'

    return f"""
    <div class="provenance-block">
        <h3>📋 Report Provenance</h3>
        <p>
            <strong>Generated:</strong> {provenance.get('generated_at_local', 'Unknown')}<br>
            <strong>Agent:</strong> {provenance.get('agent_name', 'Unknown')} v{provenance.get('agent_version', '1.0')}<br>
            <strong>Data Window:</strong> {provenance.get('data_window_start', 'N/A')} → {provenance.get('data_window_end', 'N/A')}
        </p>
        <p>
            <strong>Data Sources:</strong>
            <div class="sources">{sources_html or '<span class="source-tag">No sources tracked</span>'}</div>
        </p>
        <p>
            <strong>Total Records:</strong> {provenance.get('total_records_analyzed', 0)} |
            <strong>Max Age:</strong> {provenance.get('max_data_age_hours', 0):.1f}h |
            <strong>Validation:</strong> <span class="{validation_class}">{validation_status.upper().replace('_', ' ')}</span> |
            <strong>Publishable:</strong> {publishable}
        </p>
    </div>
    """


def build_report_html(
    title: str,
    content: str,
    category: str = 'default',
    agent_name: str = '',
    provenance: Dict[str, Any] = None,
    structured_data: Dict[str, Any] = None,
    config: PDFExportConfig = None,
) -> str:
    """Build complete HTML document for PDF conversion."""
    config = config or PDFExportConfig()
    style = CATEGORY_STYLES.get(category, CATEGORY_STYLES['default'])

    # Convert markdown to HTML
    content_html = markdown_to_html(content)

    # Build provenance section
    provenance_html = ""
    if config.include_provenance and provenance:
        provenance_html = build_provenance_html(provenance)

    # Build disclaimer
    disclaimer_html = ""
    if config.include_disclaimer:
        disclaimer = provenance.get('disclaimer', '') if provenance else ''
        if not disclaimer:
            disclaimers = {
                'sports': "Informational only. Odds must be verified with bookmakers before placing any bets. Not gambling advice.",
                'financial': "Informational only. Not financial advice. Consult a qualified advisor before investing.",
                'blockchain': "Informational only. This is not a security audit. Smart contract interactions carry risk.",
                'default': "Informational only. Verify all data before acting on this analysis.",
            }
            disclaimer = disclaimers.get(category, disclaimers['default'])

        disclaimer_html = f'<div class="disclaimer">{disclaimer}</div>'

    # Timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            {get_base_css(category, config)}
        </style>
    </head>
    <body>
        <div class="report-header">
            <h1>{style['icon']} {title}</h1>
            <div class="subtitle">{agent_name or 'AI-Generated Report'}</div>
            <div class="meta">Generated: {timestamp}</div>
        </div>

        {provenance_html}

        <div class="content">
            {content_html}
        </div>

        {disclaimer_html}

        <div class="footer">
            Generated by Donkey Betz AI Platform | {timestamp}
        </div>
    </body>
    </html>
    """


def generate_pdf(
    title: str,
    content: str,
    category: str = 'default',
    agent_name: str = '',
    provenance: Dict[str, Any] = None,
    structured_data: Dict[str, Any] = None,
    config: PDFExportConfig = None,
) -> bytes:
    """
    Generate PDF from report content.

    Args:
        title: Report title
        content: Markdown content
        category: Report category (sports, financial, blockchain, etc.)
        agent_name: Name of the agent that generated the report
        provenance: Provenance data dict
        structured_data: Structured report schema data
        config: PDF export configuration

    Returns:
        PDF file as bytes
    """
    try:
        from weasyprint import HTML, CSS

        # Build HTML document
        html_content = build_report_html(
            title=title,
            content=content,
            category=category,
            agent_name=agent_name,
            provenance=provenance,
            structured_data=structured_data,
            config=config,
        )

        # Generate PDF
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()

        logger.info(f"Generated PDF for '{title}' ({category}) - {len(pdf_bytes)} bytes")
        return pdf_bytes

    except ImportError:
        logger.error("WeasyPrint not installed. Install with: pip install weasyprint")
        raise ImportError("WeasyPrint is required for PDF generation")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise


def generate_pdf_from_workspace_operation(operation_id: str) -> bytes:
    """
    Generate PDF from a WorkspaceOperation record.

    Args:
        operation_id: UUID of the WorkspaceOperation

    Returns:
        PDF file as bytes
    """
    try:
        from core.models_skin_layer import WorkspaceOperation

        operation = WorkspaceOperation.objects.get(id=operation_id)

        # Determine category from file path
        file_path = operation.file_path or ''
        category = 'default'
        if 'financial' in file_path or 'stocks' in file_path:
            category = 'financial'
        elif 'sports' in file_path:
            category = 'sports'
        elif 'blockchain' in file_path:
            category = 'blockchain'
        elif 'narrative' in file_path:
            category = 'narrative'
        elif 'strategy' in file_path:
            category = 'strategy'
        elif 'research' in file_path:
            category = 'research'

        # Get content
        content = operation.file_content_after or operation.description or ''

        # Try to extract provenance from content or metadata
        provenance = None
        # If the content has a provenance block, it will be rendered as part of markdown

        return generate_pdf(
            title=operation.agent_task or f"Report from {operation.agent_name}",
            content=content,
            category=category,
            agent_name=operation.agent_name,
            provenance=provenance,
        )

    except Exception as e:
        logger.error(f"Failed to generate PDF from operation {operation_id}: {e}")
        raise


def generate_pdf_from_agent_result(
    result_data: Dict[str, Any],
    title: str = None,
) -> bytes:
    """
    Generate PDF from an AgentResult data dict.

    Args:
        result_data: The .data dict from an AgentResult
        title: Optional title override

    Returns:
        PDF file as bytes
    """
    # Extract provenance
    provenance = result_data.get('provenance', {})
    structured_report = result_data.get('structured_report', {})

    # Determine category
    report_type = provenance.get('report_type', '')
    category_map = {
        'sports_odds': 'sports',
        'stock_analysis': 'financial',
        'market_report': 'financial',
        'blockchain_audit': 'blockchain',
    }
    category = category_map.get(report_type, 'default')

    # Get content
    content = result_data.get('analysis', '') or result_data.get('message', '')

    # Get title
    if not title:
        agent_name = provenance.get('agent_name', 'Report')
        ticker = result_data.get('ticker', '')
        if ticker:
            title = f"{agent_name}: {ticker}"
        else:
            title = agent_name

    return generate_pdf(
        title=title,
        content=content,
        category=category,
        agent_name=provenance.get('agent_name', ''),
        provenance=provenance,
        structured_data=structured_report,
    )


# ── Deliverable PDF Export (reportlab-based, no WeasyPrint needed) ────────────

def generate_deliverable_pdf_bytes(title: str, content: str, content_format: str = 'markdown') -> bytes:
    """Convert markdown/text deliverable content to PDF bytes using reportlab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=1 * inch, rightMargin=1 * inch,
        topMargin=1 * inch, bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Title'], fontName='Helvetica-Bold',
        fontSize=18, leading=22, spaceAfter=4, alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'], fontName='Helvetica',
        fontSize=10, leading=12, spaceAfter=16, alignment=TA_CENTER,
        textColor='#666666',
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=16, leading=20, spaceBefore=16, spaceAfter=8,
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'], fontName='Helvetica-Bold',
        fontSize=14, leading=17, spaceBefore=12, spaceAfter=6,
    )
    h3_style = ParagraphStyle(
        'H3', parent=styles['Heading3'], fontName='Helvetica-Bold',
        fontSize=12, leading=15, spaceBefore=10, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'], fontName='Helvetica',
        fontSize=11, leading=14, spaceAfter=6, alignment=TA_LEFT,
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=body_style, leftIndent=24, bulletIndent=12,
        spaceAfter=3,
    )
    code_style = ParagraphStyle(
        'Code', parent=styles['Normal'], fontName='Courier',
        fontSize=9, leading=11, spaceAfter=6, leftIndent=18,
        backColor='#f5f5f5',
    )

    def _escape(text: str) -> str:
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def _apply_inline(text: str) -> str:
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        text = re.sub(r'`(.+?)`', r'<font face="Courier" size="9">\1</font>', text)
        return text

    story = []
    story.append(Paragraph(_escape(title), title_style))
    story.append(Paragraph(
        _escape(f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"),
        subtitle_style,
    ))
    story.append(Spacer(1, 8))

    in_code_block = False
    code_lines: list = []

    for line in content.split('\n'):
        stripped = line.strip()

        if stripped.startswith('```'):
            if in_code_block:
                if code_lines:
                    code_text = '<br/>'.join(_escape(cl) for cl in code_lines)
                    story.append(Paragraph(code_text, code_style))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped:
            story.append(Spacer(1, 6))
            continue

        if stripped.startswith('### '):
            story.append(Paragraph(_escape(stripped[4:]), h3_style))
        elif stripped.startswith('## '):
            story.append(Paragraph(_escape(stripped[3:]), h2_style))
        elif stripped.startswith('# '):
            story.append(Paragraph(_escape(stripped[2:]), h1_style))
        elif stripped.startswith('- ') or stripped.startswith('* '):
            text = _apply_inline(_escape(stripped[2:]))
            story.append(Paragraph(f'\u2022 {text}', bullet_style))
        elif re.match(r'^\d+\.\s', stripped):
            text = _apply_inline(_escape(stripped))
            story.append(Paragraph(text, bullet_style))
        elif re.match(r'^-{3,}$|^\*{3,}$|^_{3,}$', stripped):
            story.append(Spacer(1, 12))
        else:
            text = _apply_inline(_escape(stripped))
            story.append(Paragraph(text, body_style))

    # Flush unclosed code block
    if code_lines:
        code_text = '<br/>'.join(_escape(cl) for cl in code_lines)
        story.append(Paragraph(code_text, code_style))

    def _add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawCentredString(letter[0] / 2, 0.5 * inch,
                                 f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    buf.seek(0)
    return buf.getvalue()


def export_deliverable_to_pdf(deliverable_id: str, user_id) -> dict:
    """
    Full pipeline: load deliverable -> generate PDF -> upload to storage -> record export.

    Returns dict with export_id, file_url, file_size_bytes, title.
    """
    import uuid as _uuid
    from django.contrib.auth import get_user_model
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage
    from django.utils.text import slugify
    from core.models_deliverables import Deliverable, DeliverableExport, DeliverableEvent

    User = get_user_model()
    deliverable = Deliverable.objects.get(id=deliverable_id)

    user = None
    if user_id:
        user = User.objects.filter(id=user_id).first()

    pdf_bytes = generate_deliverable_pdf_bytes(
        title=deliverable.title,
        content=deliverable.content or '',
        content_format=deliverable.content_format or 'markdown',
    )

    slug = slugify(deliverable.title)[:60]
    short_id = _uuid.uuid4().hex[:8]
    storage_path = f'exports/pdf/{slug}-{short_id}.pdf'
    saved_path = default_storage.save(storage_path, ContentFile(pdf_bytes))
    file_url = default_storage.url(saved_path)

    export = DeliverableExport.objects.create(
        deliverable=deliverable,
        user=user,
        export_format='pdf',
        file_path=saved_path,
        file_url=file_url,
        file_size_bytes=len(pdf_bytes),
    )

    DeliverableEvent.objects.create(
        deliverable=deliverable,
        event_type='deliverable_exported',
        user=user,
        source='pa_tool',
        metadata={'export_id': str(export.id), 'format': 'pdf', 'file_size_bytes': len(pdf_bytes)},
    )

    logger.info("PDF export created: %s (%d bytes) -> %s", deliverable.title, len(pdf_bytes), file_url)

    return {
        'export_id': str(export.id),
        'file_url': file_url,
        'file_size_bytes': len(pdf_bytes),
        'title': deliverable.title,
        'message': f'PDF exported: "{deliverable.title}" ({len(pdf_bytes):,} bytes). Download: {file_url}',
    }


# Singleton accessor
_pdf_service = None


def get_pdf_export_service():
    """Get the PDF export service singleton."""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFExportService()
    return _pdf_service


class PDFExportService:
    """Service class for PDF export operations."""

    def generate_pdf(self, *args, **kwargs) -> bytes:
        return generate_pdf(*args, **kwargs)

    def generate_from_operation(self, operation_id: str) -> bytes:
        return generate_pdf_from_workspace_operation(operation_id)

    def generate_from_result(self, result_data: Dict[str, Any], title: str = None) -> bytes:
        return generate_pdf_from_agent_result(result_data, title)

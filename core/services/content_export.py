"""
Session 521: Content Export Service

Export written content (blog posts, scripts, newsletters, etc.) to various formats.
Supports: .md (Markdown), .docx (Word), .txt (Plain text), .pdf (PDF)
"""
import re
import logging
from typing import Dict, Any, Optional
from io import BytesIO

logger = logging.getLogger(__name__)

# Content type display names
CONTENT_TYPE_NAMES = {
    'blog_post': 'Blog Post',
    'podcast_script': 'Podcast Script',
    'video_script': 'Video Script',
    'article': 'Article',
    'social_thread': 'Social Thread',
    'newsletter': 'Newsletter',
}


def export_content_to_markdown(content_data: Dict[str, Any], content_type: str) -> bytes:
    """
    Export written content to Markdown format.

    Args:
        content_data: The content data dict (with full_text, sections, etc.)
        content_type: Type of content (blog_post, podcast_script, etc.)

    Returns:
        UTF-8 encoded markdown bytes
    """
    parts = []

    # Add title/headline
    title = content_data.get('title') or content_data.get('headline') or content_data.get('subject_line', '')
    if title:
        parts.append(f"# {title}\n")

    # Add subtitle/subheadline if present
    subtitle = content_data.get('subheadline') or content_data.get('meta_description', '')
    if subtitle:
        parts.append(f"*{subtitle}*\n")

    # Add intro/lead
    intro = content_data.get('intro') or content_data.get('lead') or content_data.get('preview_text', '')
    if intro:
        parts.append(f"\n{intro}\n")

    # Add sections based on content type
    if content_type == 'blog_post':
        _add_blog_sections(parts, content_data)
    elif content_type == 'podcast_script':
        _add_podcast_sections(parts, content_data)
    elif content_type == 'video_script':
        _add_video_sections(parts, content_data)
    elif content_type == 'article':
        _add_article_sections(parts, content_data)
    elif content_type == 'social_thread':
        _add_social_sections(parts, content_data)
    elif content_type == 'newsletter':
        _add_newsletter_sections(parts, content_data)
    else:
        # Fallback: use full_text if available
        if content_data.get('full_text'):
            parts.append(f"\n{content_data['full_text']}\n")

    # Add conclusion if present
    conclusion = content_data.get('conclusion')
    if conclusion:
        parts.append(f"\n## Conclusion\n\n{conclusion}\n")

    # Add CTA if present
    cta = content_data.get('cta')
    if cta:
        parts.append(f"\n---\n\n**{cta}**\n")

    # Add tags if present
    tags = content_data.get('tags', [])
    if tags:
        tag_str = ', '.join([f"#{tag}" if not tag.startswith('#') else tag for tag in tags])
        parts.append(f"\n---\n\n*Tags: {tag_str}*\n")

    return '\n'.join(parts).encode('utf-8')


def _add_blog_sections(parts: list, content_data: Dict[str, Any]):
    """Add blog post sections to markdown."""
    sections = content_data.get('sections', [])
    for section in sections:
        if isinstance(section, dict):
            header = section.get('header', section.get('title', ''))
            content = section.get('content', section.get('body', ''))
            if header:
                parts.append(f"\n## {header}\n")
            if content:
                parts.append(f"{content}\n")
        elif isinstance(section, str):
            parts.append(f"\n{section}\n")


def _add_podcast_sections(parts: list, content_data: Dict[str, Any]):
    """Add podcast script sections to markdown."""
    # Intro hook
    intro_hook = content_data.get('intro_hook')
    if intro_hook:
        parts.append(f"\n## Intro Hook\n\n{intro_hook}\n")

    # Segments
    segments = content_data.get('segments', [])
    for i, segment in enumerate(segments, 1):
        if isinstance(segment, dict):
            topic = segment.get('topic', f'Segment {i}')
            talking_points = segment.get('talking_points', [])
            parts.append(f"\n## {topic}\n")
            for point in talking_points:
                parts.append(f"- {point}\n")
        elif isinstance(segment, str):
            parts.append(f"\n### Segment {i}\n\n{segment}\n")

    # Outro
    outro = content_data.get('outro')
    if outro:
        parts.append(f"\n## Outro\n\n{outro}\n")


def _add_video_sections(parts: list, content_data: Dict[str, Any]):
    """Add video script sections to markdown."""
    scenes = content_data.get('scenes', content_data.get('segments', []))
    for i, scene in enumerate(scenes, 1):
        if isinstance(scene, dict):
            scene_name = scene.get('scene', scene.get('title', f'Scene {i}'))
            narration = scene.get('narration', scene.get('content', ''))
            visual = scene.get('visual', scene.get('b_roll', ''))
            timing = scene.get('timing', '')

            parts.append(f"\n### {scene_name}")
            if timing:
                parts.append(f" ({timing})")
            parts.append("\n")

            if visual:
                parts.append(f"**Visual:** {visual}\n\n")
            if narration:
                parts.append(f"**Narration:** {narration}\n")
        elif isinstance(scene, str):
            parts.append(f"\n### Scene {i}\n\n{scene}\n")


def _add_article_sections(parts: list, content_data: Dict[str, Any]):
    """Add article sections to markdown."""
    body_sections = content_data.get('body_sections', content_data.get('sections', []))
    for section in body_sections:
        if isinstance(section, dict):
            header = section.get('header', section.get('title', ''))
            content = section.get('content', section.get('body', ''))
            if header:
                parts.append(f"\n## {header}\n")
            if content:
                parts.append(f"{content}\n")
        elif isinstance(section, str):
            parts.append(f"\n{section}\n")


def _add_social_sections(parts: list, content_data: Dict[str, Any]):
    """Add social thread posts to markdown."""
    # Hook post
    hook = content_data.get('hook_post', content_data.get('hook', ''))
    if hook:
        parts.append(f"\n## Thread\n\n**1.** {hook}\n")

    # Thread posts
    thread_posts = content_data.get('thread_posts', [])
    for i, post in enumerate(thread_posts, 2):
        if isinstance(post, dict):
            text = post.get('text', post.get('content', ''))
            parts.append(f"\n**{i}.** {text}\n")
        elif isinstance(post, str):
            parts.append(f"\n**{i}.** {post}\n")

    # CTA post
    cta_post = content_data.get('cta_post')
    if cta_post:
        parts.append(f"\n**Final.** {cta_post}\n")

    # Hashtags
    hashtags = content_data.get('hashtags', [])
    if hashtags:
        parts.append(f"\n---\n\n{' '.join(hashtags)}\n")


def _add_newsletter_sections(parts: list, content_data: Dict[str, Any]):
    """Add newsletter sections to markdown."""
    # Greeting
    greeting = content_data.get('greeting')
    if greeting:
        parts.append(f"\n{greeting}\n")

    # Sections
    sections = content_data.get('sections', [])
    for section in sections:
        if isinstance(section, dict):
            header = section.get('header', section.get('title', ''))
            content = section.get('content', section.get('body', ''))
            if header:
                parts.append(f"\n## {header}\n")
            if content:
                parts.append(f"{content}\n")
        elif isinstance(section, str):
            parts.append(f"\n{section}\n")

    # Sign off
    sign_off = content_data.get('sign_off')
    if sign_off:
        parts.append(f"\n---\n\n{sign_off}\n")


def export_content_to_text(content_data: Dict[str, Any], content_type: str) -> bytes:
    """
    Export written content to plain text format.
    Strips markdown formatting.
    """
    # Get markdown first
    md_bytes = export_content_to_markdown(content_data, content_type)
    md_text = md_bytes.decode('utf-8')

    # Strip markdown formatting
    text = md_text
    # Remove headers
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Remove bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    # Remove italic
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'^---\s*$', '\n', text, flags=re.MULTILINE)
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip().encode('utf-8')


def export_content_to_docx(content_data: Dict[str, Any], content_type: str) -> bytes:
    """
    Export written content to Word document format.
    """
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Set margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Get markdown content and parse it
    md_bytes = export_content_to_markdown(content_data, content_type)
    md_text = md_bytes.decode('utf-8')

    lines = md_text.split('\n')

    for line in lines:
        line_stripped = line.strip()

        if not line_stripped:
            doc.add_paragraph()
            continue

        # Skip horizontal rules
        if line_stripped == '---':
            doc.add_paragraph('_' * 50)
            continue

        # Check for headers
        if line_stripped.startswith('# '):
            para = doc.add_heading(line_stripped[2:], level=1)
        elif line_stripped.startswith('## '):
            para = doc.add_heading(line_stripped[3:], level=2)
        elif line_stripped.startswith('### '):
            para = doc.add_heading(line_stripped[4:], level=3)
        else:
            # Regular paragraph - strip markdown formatting
            text = line_stripped
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
            text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic

            para = doc.add_paragraph()

            # Handle bullet points
            if text.startswith('- '):
                para.style = 'List Bullet'
                text = text[2:]
            elif re.match(r'^\d+\.\s', text):
                para.style = 'List Number'
                text = re.sub(r'^\d+\.\s', '', text)

            run = para.add_run(text)
            run.font.name = 'Calibri'
            run.font.size = Pt(11)

    # Save to bytes
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def export_content_to_pdf(content_data: Dict[str, Any], content_type: str) -> bytes:
    """
    Export written content to PDF format using reportlab.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    buf = BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=1*inch,
        rightMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'ContentTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        'ContentHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'ContentBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=6
    )

    # Get markdown content
    md_bytes = export_content_to_markdown(content_data, content_type)
    md_text = md_bytes.decode('utf-8')

    story = []
    lines = md_text.split('\n')

    for line in lines:
        line_stripped = line.strip()

        if not line_stripped:
            story.append(Spacer(1, 6))
            continue

        if line_stripped == '---':
            story.append(Spacer(1, 12))
            continue

        # Escape special characters
        safe_line = line_stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Remove markdown formatting for display
        safe_line = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', safe_line)
        safe_line = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', safe_line)

        if line_stripped.startswith('# '):
            story.append(Paragraph(safe_line[2:], title_style))
        elif line_stripped.startswith('## '):
            story.append(Paragraph(safe_line[3:], heading_style))
        elif line_stripped.startswith('### '):
            story.append(Paragraph(safe_line[4:], heading_style))
        else:
            story.append(Paragraph(safe_line, body_style))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def get_export_filename(content_data: Dict[str, Any], content_type: str, format: str) -> str:
    """Generate a safe filename for export."""
    title = content_data.get('title') or content_data.get('headline') or content_data.get('subject_line', '')

    if not title:
        title = CONTENT_TYPE_NAMES.get(content_type, 'content')

    # Sanitize filename
    safe_title = "".join(c for c in title if c.isalnum() or c in ' -_').strip()
    safe_title = safe_title.replace(' ', '_')[:50]

    if not safe_title:
        safe_title = content_type or 'content'

    return f"{safe_title}.{format}"


def export_written_content(
    content_data: Dict[str, Any],
    content_type: str,
    format: str = 'md'
) -> tuple[bytes, str, str]:
    """
    Export written content to the specified format.

    Args:
        content_data: The content data dict
        content_type: Type of content (blog_post, podcast_script, etc.)
        format: Export format (md, txt, docx, pdf)

    Returns:
        Tuple of (file_bytes, filename, content_type_header)
    """
    format = format.lower()

    if format == 'md':
        file_bytes = export_content_to_markdown(content_data, content_type)
        content_type_header = 'text/markdown'
    elif format == 'txt':
        file_bytes = export_content_to_text(content_data, content_type)
        content_type_header = 'text/plain'
    elif format == 'docx':
        file_bytes = export_content_to_docx(content_data, content_type)
        content_type_header = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif format == 'pdf':
        file_bytes = export_content_to_pdf(content_data, content_type)
        content_type_header = 'application/pdf'
    else:
        raise ValueError(f"Unsupported format: {format}")

    filename = get_export_filename(content_data, content_type, format)

    return file_bytes, filename, content_type_header

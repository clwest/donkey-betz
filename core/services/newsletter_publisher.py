"""
Newsletter Publisher — Provider-based publishing adapter.

Session 1077+: POC 1 — Autopilot Ops Newsletter

Transforms issue deliverables into platform-ready artifacts (markdown/HTML)
with subject lines, preview text, CTA blocks, and publish checklists.

Architecture:
  PublisherProvider (ABC)
    ├── SubstackManualProvider  (copy/paste workflow — active)
    ├── BeehiivProvider         (future — real API)
    └── ButtondownProvider      (future — real API)

Usage:
    from core.services.newsletter_publisher import get_publisher

    publisher = get_publisher()  # Returns configured provider
    result = publisher.prepare_issue(deliverable_id, user_id=1)
    # → dict with substack_html, subject, preview_text, checklist, etc.
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


# ── Template v1 Sections ────────────────────────────────────────────────────

TEMPLATE_V1_SECTIONS = [
    {'key': 'top_signal', 'label': 'Top Signal', 'required': True, 'min_words': 50},
    {'key': 'what_broke', 'label': 'What Broke', 'required': True, 'min_words': 80},
    {'key': 'autopilot_move', 'label': 'Autopilot Move', 'required': True, 'min_words': 100},
    {'key': 'cost_watch', 'label': 'Cost Watch', 'required': True, 'min_words': 30},
    {'key': 'what_changed', 'label': 'What Changed', 'required': True, 'min_words': 50},
    {'key': 'tool_of_week', 'label': 'Tool / Repo of the Week', 'required': False, 'min_words': 20},
    {'key': 'sponsor', 'label': 'Sponsor', 'required': False, 'min_words': 0},
    {'key': 'cta', 'label': 'Forward + Subscribe CTA', 'required': True, 'min_words': 10},
]

# Section heading patterns for parsing issue content
SECTION_PATTERNS = {
    'top_signal': re.compile(r'^#{1,3}\s+Top Signal', re.IGNORECASE | re.MULTILINE),
    'what_broke': re.compile(r'^#{1,3}\s+What Broke', re.IGNORECASE | re.MULTILINE),
    'autopilot_move': re.compile(r'^#{1,3}\s+Autopilot Move', re.IGNORECASE | re.MULTILINE),
    'cost_watch': re.compile(r'^#{1,3}\s+Cost Watch', re.IGNORECASE | re.MULTILINE),
    'what_changed': re.compile(r'^#{1,3}\s+What Changed', re.IGNORECASE | re.MULTILINE),
    'tool_of_week': re.compile(r'^#{1,3}\s+Tool\b.*(?:Repo|Week)', re.IGNORECASE | re.MULTILINE),
    'sponsor': re.compile(r'^#{1,3}\s+Sponsor', re.IGNORECASE | re.MULTILINE),
    'cta': re.compile(r'^#{1,3}\s+(?:Forward|Subscribe|CTA)', re.IGNORECASE | re.MULTILINE),
}

# Default CTA block (appended if missing)
DEFAULT_CTA = """
---

**Enjoyed this?** Forward to a teammate who hates being paged at 3 AM.

**New here?** [Subscribe to Autopilot Ops]({{subscribe_url}}) — free, weekly, no spam.

*Have a sponsorship inquiry?* Reply to this email.
"""

# Default sponsor slot placeholder
SPONSOR_PLACEHOLDER = """
---

*This spot is reserved for a relevant DevOps/SRE sponsor. [Reach out](mailto:{{sponsor_email}}) for our media kit.*

---
"""


def _word_count(text: str) -> int:
    return len(text.split())


def _extract_sections(content: str) -> Dict[str, str]:
    """Parse markdown content into Template v1 sections."""
    sections = {}
    # Find all section positions
    positions = []
    for key, pattern in SECTION_PATTERNS.items():
        match = pattern.search(content)
        if match:
            positions.append((match.start(), key, match.end()))

    # Sort by position
    positions.sort(key=lambda x: x[0])

    # Extract text between sections
    for i, (start, key, header_end) in enumerate(positions):
        if i + 1 < len(positions):
            section_text = content[header_end:positions[i + 1][0]].strip()
        else:
            section_text = content[header_end:].strip()
        sections[key] = section_text

    return sections


def _validate_sections(sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """Check Template v1 section completeness and length."""
    issues = []
    for spec in TEMPLATE_V1_SECTIONS:
        key = spec['key']
        text = sections.get(key, '')
        wc = _word_count(text) if text else 0

        if spec['required'] and not text:
            issues.append({
                'section': spec['label'],
                'severity': 'error',
                'message': f"Missing required section: {spec['label']}",
            })
        elif text and wc < spec['min_words']:
            issues.append({
                'section': spec['label'],
                'severity': 'warning',
                'message': f"{spec['label']}: {wc} words (target: {spec['min_words']}+)",
            })
    return issues


def _count_links(text: str) -> int:
    return len(re.findall(r'https?://\S+|\[.+?\]\(.+?\)', text))


def _markdown_to_substack_html(md: str) -> str:
    """Convert markdown to clean HTML suitable for Substack paste.

    Substack's editor accepts HTML paste well. We do a lightweight
    conversion — no external dependencies needed.
    """
    html = md

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

    # Horizontal rules
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)

    # Unordered list items
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # Wrap consecutive <li> in <ul>
    html = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', html)

    # Paragraphs — wrap non-tag lines
    lines = html.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            result.append(f'<p>{stripped}</p>')
        else:
            result.append(line)

    return '\n'.join(result)


# ── Publisher Provider Interface ────────────────────────────────────────────

class PublisherProvider(ABC):
    """Base class for newsletter publishing providers."""

    provider_name: str = 'base'

    @abstractmethod
    def prepare_issue(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Transform issue content into platform-ready artifact.

        Args:
            content: Markdown content of the issue
            metadata: title, issue_number, subscribe_url, sponsor_email, etc.

        Returns:
            dict with: formatted_content, subject, preview_text, checklist, etc.
        """
        pass

    @abstractmethod
    def get_publish_checklist(self, metadata: Dict[str, Any]) -> List[str]:
        """Return platform-specific publish checklist steps."""
        pass


class SubstackManualProvider(PublisherProvider):
    """Manual Substack publishing — generates copy/paste-ready artifacts."""

    provider_name = 'substack_manual'

    def prepare_issue(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        title = metadata.get('title', 'Autopilot Ops')
        issue_number = metadata.get('issue_number', '?')
        subscribe_url = (metadata.get('subscribe_url') or '').strip() or 'https://autopilotops.substack.com'
        sponsor_email = (metadata.get('sponsor_email') or '').strip() or 'sponsor@autopilotops.com'

        # Parse and validate sections
        sections = _extract_sections(content)
        issues = _validate_sections(sections)

        # Build subject line options
        subjects = self._generate_subjects(title, issue_number, sections)

        # Generate preview text (first ~140 chars of Top Signal)
        top_signal = sections.get('top_signal', '')
        preview_text = top_signal[:140].rsplit(' ', 1)[0] + '…' if len(top_signal) > 140 else top_signal

        # Ensure CTA exists
        full_content = content
        if not sections.get('cta'):
            cta = DEFAULT_CTA.replace('{{subscribe_url}}', subscribe_url)
            full_content = content.rstrip() + '\n\n' + cta

        # Replace subscribe URL placeholders in existing content
        # subscribe_url is guaranteed non-empty (falls back to default above)
        full_content = full_content.replace('{{subscribe_url}}', subscribe_url)
        full_content = full_content.replace('(Substack link)', f'({subscribe_url})')
        full_content = full_content.replace('{{sponsor_email}}', sponsor_email)

        # Ensure sponsor slot exists (placeholder if no sponsor)
        if not sections.get('sponsor'):
            sponsor_block = SPONSOR_PLACEHOLDER.replace('{{sponsor_email}}', sponsor_email)
            # Insert before CTA
            cta_match = SECTION_PATTERNS['cta'].search(full_content)
            if cta_match:
                full_content = (
                    full_content[:cta_match.start()].rstrip()
                    + '\n\n' + sponsor_block + '\n\n'
                    + full_content[cta_match.start():]
                )

        # Generate HTML version
        html_content = _markdown_to_substack_html(full_content)

        # Stats
        total_words = _word_count(full_content)
        link_count = _count_links(full_content)
        reading_time = max(1, round(total_words / 250))

        checklist = self.get_publish_checklist(metadata)

        return {
            'provider': self.provider_name,
            'markdown': full_content,
            'html': html_content,
            'subjects': subjects,
            'preview_text': preview_text,
            'sections_found': list(sections.keys()),
            'sections_missing': [
                s['key'] for s in TEMPLATE_V1_SECTIONS
                if s['required'] and s['key'] not in sections
            ],
            'validation_issues': issues,
            'stats': {
                'word_count': total_words,
                'link_count': link_count,
                'reading_time_min': reading_time,
                'section_count': len(sections),
                'has_sponsor': bool(sections.get('sponsor')),
            },
            'checklist': checklist,
        }

    def _generate_subjects(self, title: str, issue_number, sections: Dict) -> List[str]:
        """Generate 3 subject line options."""
        top_signal = sections.get('top_signal', '')
        # Clean up: remove time markers like "(1 minute)", strip leading whitespace/newlines
        import re
        cleaned = re.sub(r'\(\d+\s*minutes?\)', '', top_signal).strip()
        # Skip lines that are just formatting artifacts
        lines = [l.strip() for l in cleaned.split('\n') if l.strip() and not l.strip().startswith('*')]
        first_sentence = lines[0].split('.')[0].strip()[:60] if lines else ''

        return [
            f"Ops Autopilot #{issue_number}: {first_sentence}" if first_sentence else f"Ops Autopilot #{issue_number}",
            f"Autopilot Ops #{issue_number} — What broke + what to automate",
            f"#{issue_number}: Reliability signals, condensed",
        ]

    def get_publish_checklist(self, metadata: Dict[str, Any]) -> List[str]:
        return [
            "1. Log in to Substack → New Post",
            "2. Paste the HTML content (or import markdown)",
            f"3. Set subject line (pick from suggested options)",
            f"4. Set preview text: first ~140 chars of Top Signal",
            "5. Add hero image (recommended: 1200x630, ops/infra themed)",
            "6. Set section: 'Newsletter' (or your default)",
            "7. Tag: ops, sre, devops, automation, reliability",
            "8. Review sponsor slot — insert sponsor copy or keep placeholder",
            "9. Send test email to yourself",
            "10. Schedule or send to all subscribers",
            "11. After send: record metrics (opens, clicks) when available",
        ]


class BeehiivProvider(PublisherProvider):
    """Beehiiv API provider — future implementation."""

    provider_name = 'beehiiv'

    def prepare_issue(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Beehiiv provider not yet implemented. Set up API key first.")

    def get_publish_checklist(self, metadata: Dict[str, Any]) -> List[str]:
        return ["Beehiiv provider not yet configured."]


class ButtondownProvider(PublisherProvider):
    """Buttondown API provider — future implementation."""

    provider_name = 'buttondown'

    def prepare_issue(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Buttondown provider not yet implemented. Set up API key first.")

    def get_publish_checklist(self, metadata: Dict[str, Any]) -> List[str]:
        return ["Buttondown provider not yet configured."]


# ── Provider Registry ───────────────────────────────────────────────────────

_PROVIDERS = {
    'substack_manual': SubstackManualProvider,
    'beehiiv': BeehiivProvider,
    'buttondown': ButtondownProvider,
}


def get_publisher(provider_name: str = 'substack_manual') -> PublisherProvider:
    """Get a configured publisher provider instance."""
    cls = _PROVIDERS.get(provider_name)
    if not cls:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(_PROVIDERS.keys())}")
    return cls()


# ── Issue Generation ────────────────────────────────────────────────────────

def generate_issue_outline(issue_number: int, sources: Optional[List[Dict]] = None) -> str:
    """Generate a Template v1 issue outline with section headers and guidance.

    Args:
        issue_number: The issue number
        sources: Optional list of source items (from source pack)

    Returns:
        Markdown outline ready for content generation
    """
    source_block = ""
    if sources:
        source_lines = []
        for s in sources[:20]:
            source_lines.append(f"- [{s.get('title', 'Untitled')}]({s.get('url', '#')}) — {s.get('category', 'general')}")
        source_block = f"\n**Available Sources:**\n" + '\n'.join(source_lines) + '\n'

    return f"""# Autopilot Ops — Issue #{issue_number}

**Subject:** [TBD — pick after writing Top Signal]
**Preheader:** [TBD — first 140 chars of Top Signal]

---
{source_block}
## Top Signal
<!-- 5-7 sentences on the highest-leverage theme of the week. What's the meta-pattern? -->

---

## What Broke
<!-- 3-5 incidents/outages. Each: what happened + 1 takeaway. Link primary sources. -->

- **[Incident 1]:** ...
- **[Incident 2]:** ...
- **[Incident 3]:** ...

---

## Autopilot Move
<!-- 1 concrete automation pattern. Include: what it does, inputs, outputs, why it works. -->
### [Pattern Name]

**Inputs:**
-

**Outputs:**
-

**Why it works:**

**Definition of Done:**
-

---

## Cost Watch
<!-- 1-2 FinOps/capacity items. What cost surprised someone? What to monitor. -->

---

## What Changed
<!-- 3-7 vendor changes, releases, CVEs, pricing updates. Quick-hit format. -->

- **[Vendor/Tool]:** ...
- **[CVE/Security]:** ...
- **[Platform Update]:** ...

---

## Tool / Repo of the Week
<!-- 1 tool or repo worth checking out. What it does, why now. -->

---

## Forward + Subscribe CTA
Enjoyed this? Forward to a teammate who hates being paged at 3 AM.

New here? [Subscribe to Autopilot Ops]({{{{subscribe_url}}}}) — free, weekly, no spam.
"""


def compute_issue_metrics(content: str, issue_number: int, title: str = '') -> Dict[str, Any]:
    """Compute metrics for a published issue."""
    sections = _extract_sections(content)
    return {
        'issue_number': issue_number,
        'title': title,
        'send_date': None,  # Set manually when sent
        'word_count': _word_count(content),
        'link_count': _count_links(content),
        'sections_present': list(sections.keys()),
        'section_count': len(sections),
        'has_sponsor': bool(sections.get('sponsor')),
        'reading_time_min': max(1, round(_word_count(content) / 250)),
        # Manual entry fields (populated after send)
        'opens': None,
        'clicks': None,
        'unsubscribes': None,
        'new_subscribers': None,
    }

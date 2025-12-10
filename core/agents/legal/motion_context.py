"""
Motion Context - Centralized Data Structure for Legal Document Pipeline

Session 406 PATCH-5: Created to eliminate placeholder binding issues and provide
a single source of truth for all motion-related data.

All templates in the denied_motion_rewrite pipeline should depend on this
MotionContext dataclass rather than ad-hoc dictionary lookups.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
import re


@dataclass
class ReferencedOrder:
    """Court order referenced in the motion."""
    date: str
    order_type: str
    label: str  # e.g., "Exhibit A"
    key_provisions: List[str] = field(default_factory=list)


@dataclass
class MotionContext:
    """
    Central structure for all case + motion data needed by templates.

    This eliminates the need for ad-hoc {placeholder} replacements by
    providing a typed, validated context object.
    """
    # Court/Case Information
    state: str = "COLORADO"
    county: str = ""
    court_address: str = ""
    case_number: str = ""
    division: str = ""
    courtroom: str = ""

    # Parties
    petitioner_name: str = ""
    petitioner_first_name: str = ""
    respondent_name: str = ""
    respondent_first_name: str = ""

    # Child Information (family law)
    child_name: str = ""
    child_first_name: str = ""
    child_age: Optional[int] = None
    children: List[Dict[str, Any]] = field(default_factory=list)

    # Respondent's Counsel (if represented)
    respondent_counsel_name: str = ""
    respondent_counsel_first_name: str = ""
    respondent_counsel_firm: str = ""
    respondent_counsel_address: str = ""
    respondent_counsel_email: str = ""
    is_respondent_represented: bool = False

    # Respondent Address (for service if pro se)
    respondent_address: str = ""

    # Motion Details
    motion_title: str = ""
    relief_type: str = ""
    is_emergency: bool = False
    relief_items: List[str] = field(default_factory=list)

    # Referenced Orders
    referenced_orders: List[ReferencedOrder] = field(default_factory=list)
    has_non_disparagement: bool = False

    # Conferral Information
    conferral_email_deadline: Optional[date] = None
    conferral_date_sent: Optional[date] = None
    conferral_status: str = "pending"  # pending, no_response, refused, partial, agreed

    # Original motion content (for narrative extraction)
    original_motion_content: str = ""

    @classmethod
    def from_case_details(cls, case_details: Dict[str, Any]) -> 'MotionContext':
        """
        Factory method to create MotionContext from existing case_details dict.

        This provides backward compatibility with existing code while
        transitioning to the typed MotionContext.
        """
        # Extract child info
        children = case_details.get('children', [])
        child_name = ""
        child_first_name = ""
        child_age = None

        if children:
            first_child = children[0]
            child_name = first_child.get('name', '') or first_child.get('full_name', '')
            child_first_name = first_child.get('first_name', '')
            child_age = first_child.get('age')

        # Fallback to legacy child_name field
        if not child_name:
            child_name = case_details.get('child_name', 'the minor child')

        # Determine if respondent is represented
        is_represented = case_details.get('conferral_recipient_is_attorney', False)

        # Get counsel info
        counsel_name = case_details.get('respondent_counsel') or case_details.get('conferral_recipient_name', '')
        counsel_firm = case_details.get('respondent_counsel_firm', '')
        counsel_address = case_details.get('respondent_counsel_address', '')
        counsel_email = case_details.get('respondent_counsel_email', '')

        # If we have conferral_recipient info and it's an attorney, use that
        if case_details.get('conferral_recipient_is_attorney'):
            counsel_name = case_details.get('conferral_recipient_name', counsel_name)

        # Calculate conferral deadline (default 2 business days)
        conferral_deadline = datetime.now().date() + timedelta(days=2)

        return cls(
            state=case_details.get('state', 'COLORADO') or 'COLORADO',
            county=case_details.get('county', '') or '',
            court_address=case_details.get('court_address', '') or '',
            case_number=case_details.get('case_number', '') or '',
            division=case_details.get('division', '') or '',
            courtroom=case_details.get('courtroom', '') or '',

            petitioner_name=case_details.get('petitioner_name', '') or '',
            petitioner_first_name=case_details.get('petitioner_first_name', '') or cls._extract_first_name(case_details.get('petitioner_name', '')),
            respondent_name=case_details.get('respondent_name', '') or '',
            respondent_first_name=case_details.get('respondent_first_name', '') or cls._extract_first_name(case_details.get('respondent_name', '')),

            child_name=child_name,
            child_first_name=child_first_name or cls._extract_first_name(child_name),
            child_age=child_age,
            children=children,

            respondent_counsel_name=counsel_name,
            respondent_counsel_first_name=cls._extract_first_name(counsel_name),
            respondent_counsel_firm=counsel_firm,
            respondent_counsel_address=counsel_address,
            respondent_counsel_email=counsel_email,
            is_respondent_represented=is_represented or bool(counsel_name),

            respondent_address=case_details.get('respondent_address', '') or '',

            conferral_email_deadline=conferral_deadline,
        )

    @staticmethod
    def _extract_first_name(full_name: str) -> str:
        """Extract first name from full name."""
        if not full_name:
            return ""
        parts = full_name.split()
        return parts[0] if parts else ""

    def validate(self) -> List[str]:
        """
        Validate that all required fields are populated.

        Returns list of validation errors, empty if valid.
        """
        errors = []

        # Required fields for a valid motion
        if not self.state:
            errors.append("Missing state")
        if not self.county:
            errors.append("Missing county")
        if not self.petitioner_name:
            errors.append("Missing petitioner name")
        if not self.respondent_name:
            errors.append("Missing respondent name")
        if not self.case_number:
            errors.append("Missing case number")

        return errors

    def get_service_recipient(self) -> str:
        """
        Get the formatted service recipient for Certificate of Service.

        Returns counsel if represented, otherwise respondent.
        """
        if self.is_respondent_represented and self.respondent_counsel_name:
            lines = [self.respondent_counsel_name]
            if self.respondent_counsel_firm:
                lines.append(self.respondent_counsel_firm)
            lines.append("Attorney for Respondent")
            return "\n".join(lines)
        return self.respondent_name

    def get_service_address(self) -> str:
        """Get the service address for Certificate of Service."""
        if self.is_respondent_represented and self.respondent_counsel_address:
            return self.respondent_counsel_address
        return self.respondent_address or "_____________________________________"

    def get_conferral_salutation(self) -> str:
        """
        Get the appropriate salutation for conferral email.

        Returns counsel's first name if represented, otherwise respondent's.
        """
        if self.is_respondent_represented and self.respondent_counsel_first_name:
            return self.respondent_counsel_first_name
        return self.respondent_first_name or "Respondent"

    def get_conferral_target(self) -> str:
        """Get the formal conferral target description."""
        if self.is_respondent_represented:
            return "Respondent's counsel"
        return "Respondent"

    def get_conferral_target_short(self) -> str:
        """Get the short conferral target description."""
        if self.is_respondent_represented:
            return "Counsel"
        return "Respondent"

    def get_child_description(self) -> str:
        """
        Get a properly formatted child description.

        Returns "Nicolas West, age 8" or "the minor child" if unknown.
        """
        if self.child_name and self.child_name != "the minor child":
            if self.child_age is not None:
                return f"{self.child_name}, age {self.child_age}"
            return self.child_name
        return "the minor child"

    def get_children_description(self) -> str:
        """
        Get description of all children for motions involving multiple children.
        """
        if not self.children:
            return self.get_child_description()

        if len(self.children) == 1:
            child = self.children[0]
            name = child.get('name', '') or child.get('full_name', 'the minor child')
            age = child.get('age')
            if age is not None:
                return f"{name}, age {age}"
            return name

        # Multiple children
        descriptions = []
        for child in self.children:
            name = child.get('name', '') or child.get('full_name', '')
            age = child.get('age')
            if name:
                if age is not None:
                    descriptions.append(f"{name}, age {age}")
                else:
                    descriptions.append(name)

        if descriptions:
            return "; ".join(descriptions)
        return "the minor children"


def clean_motion_text(text: str) -> str:
    """
    Post-processing cleaner to fix common narrative glitches.

    Session 406 PATCH-5: Applies normalization to collapse double spaces,
    fix comma spacing, remove orphaned periods, and clean up wording glitches.
    """
    if not text:
        return text

    # Fix "occurred:." pattern
    text = text.replace("occurred:.", "occurred:")
    text = text.replace("occurred: .", "occurred:")

    # Fix "pattern of escalating, harmful, and constitutes" wording
    text = re.sub(
        r'escalating pattern of\s+escalating[,\s]+',
        'escalating pattern of ',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'pattern of\s+harmful[,\s]+and',
        'pattern of conduct that',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'pattern of\s+escalating,?\s*harmful,?\s*and\s+constitutes',
        'pattern that is escalating, harmful, and constitutes',
        text,
        flags=re.IGNORECASE
    )

    # Fix double spaces
    text = re.sub(r'  +', ' ', text)

    # Fix " ," spacing
    text = text.replace(" ,", ",")

    # Session 406 PATCH-5.1: Fix stray space before periods
    text = re.sub(r'\s+\.(?=\s|$)', '.', text)
    text = re.sub(r'\s+;(?=\s|$)', ';', text)

    # Session 406 PATCH-5.1: Fix "( date )" pattern - remove spaces inside parens
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)

    # Fix orphaned periods
    text = re.sub(r':\s*\.', ':', text)
    text = re.sub(r'\.\s*\.', '.', text)

    # Session 406 PATCH-5.1: Fix semicolon followed by period
    text = text.replace(";.", ";")

    # Session 406 PATCH-5.1: Clean up "repeat" text that may have slipped through
    text = text.replace("repeat .", "")
    text = text.replace(" repeat .", "")

    # Session 406 PATCH-5.2: Format incident lists with bullets
    # Pattern: "These incidents occurred:\nDuring..." should become "These incidents occurred:\n- During..."
    text = re.sub(
        r'(incidents occurred:)\s*\n\s*([A-Z])',
        r'\1\n- \2',
        text
    )
    # Add bullets to subsequent lines that look like incident items
    text = re.sub(
        r'\n([A-Z][a-z]+ \d{1,2}, \d{4},)',  # Lines starting with "August 29, 2025,"
        r'\n- \1',
        text
    )
    text = re.sub(
        r'\n(The following week,)',
        r'\n- \1',
        text
    )
    text = re.sub(
        r'\n(On [A-Z][a-z]+ \d{1,2}, \d{4})',
        r'\n- \1',
        text
    )
    text = re.sub(
        r'\n(During )',
        r'\n- \1',
        text
    )

    # Fix multiple newlines (more than 2)
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    return text


def render_relief_block(relief_items: List[str]) -> str:
    """
    Render relief items as a numbered list for the RELIEF REQUESTED section.
    """
    if not relief_items:
        return "1. [Specific relief requested]"

    lines = []
    for idx, item in enumerate(relief_items, start=1):
        # Ensure item starts properly
        item = item.strip()
        if item:
            lines.append(f"{idx}. {item}")

    return "\n".join(lines) if lines else "1. [Specific relief requested]"


def render_proposed_order_relief(relief_items: List[str]) -> str:
    """
    Render relief items for the Proposed Order section.

    Similar to relief block but formatted for judge's signature.
    """
    if not relief_items:
        return "IT IS ORDERED that the requested relief be granted."

    lines = []
    for idx, item in enumerate(relief_items, start=1):
        item = item.strip()
        if item:
            # Ensure proper sentence structure
            if not item.endswith('.'):
                item += '.'
            lines.append(f"{idx}. {item}")

    return "\n".join(lines) if lines else "IT IS ORDERED that the requested relief be granted."


def count_relief_items(relief_items: List[str]) -> int:
    """
    Count the number of substantive relief items.

    This is the single source of truth for relief counting.
    """
    return len([item for item in relief_items if item and len(item.strip()) > 10])


def score_relief_scope(num_items: int) -> tuple:
    """
    Score relief scope based on number of items.

    Returns (score, explanation) tuple.

    Scoring:
    - 1-3 items: 20-25 points (court likes narrow, clear requests)
    - 4-5 items: 10-19 points (ok but a bit heavy)
    - 6+ items: 0-9 points (likely perceived as overbroad)
    """
    if num_items == 0:
        return (15, "No specific relief items identified")
    elif num_items <= 2:
        return (25, f"Highly focused relief ({num_items} item{'s' if num_items > 1 else ''})")
    elif num_items <= 3:
        return (22, f"Focused relief requests ({num_items} items)")
    elif num_items <= 5:
        return (15, f"Several relief requests ({num_items} items); consider narrowing if possible")
    else:
        return (7, f"Many relief items ({num_items}); court may prefer a narrower motion")

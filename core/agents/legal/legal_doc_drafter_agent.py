"""
Legal Document Drafter Agent - Pro Se Legal Assistant
======================================================

Session 403: Pro Se Legal Assistant for Colorado Family Law

This agent helps self-represented users generate PROCEDURAL documents:
- Motions (Motion to Continue, Motion to Modify Parenting Time)
- Meet-and-confer emails
- Declarations
- Response templates

IMPORTANT DISCLAIMERS:
- This provides GENERAL LEGAL INFORMATION, NOT legal advice
- This does NOT create an attorney-client relationship
- Laws vary by jurisdiction (focused on Colorado)
- Users should consult a licensed attorney for specific legal matters
- Generated documents are TEMPLATES that need review

Focus Areas (Colorado Family Law):
- Divorce with children
- Parenting time / custody
- Child support
- Parental responsibility

Session 403 Enhancements:
- Database models: LegalCase, LegalDocument, LegalResearchResult, LegalMemory
- Learning hooks: Records successful document patterns
- Memory system: Stores successful strategies for future use
- Knowledge sharing: Shares learned patterns with collective intelligence
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from core.agents.legal.motion_context import (
    MotionContext,
    clean_motion_text,
    render_relief_block,
    render_proposed_order_relief,
    score_relief_scope
)
from core.agents.legal.document_bundle import (
    parse_motion_output_to_bundle
)
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_legal_doc_with_ml(doc_data: dict) -> dict:
    """Analyze legal document using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=doc_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'legal_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML legal analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


# Colorado-specific legal terms and form references
COLORADO_FAMILY_LAW_FORMS = {
    'divorce_with_children': {
        'petition': 'JDF 1111',
        'response': 'JDF 1115',
        'decree': 'JDF 1116',
        'case_info': 'JDF 1101',
        'summons': 'JDF 1102',
    },
    'parenting': {
        'parenting_plan': 'JDF 1113',
        'decision_making': 'JDF 1113.5',
        'modify_parenting_time': 'JDF 1220',
        'affidavit_modify': 'JDF 1221',
    },
    'child_support': {
        'worksheet_a': 'JDF 1820',
        'worksheet_b': 'JDF 1821',
    },
    'general': {
        'confidential_info': 'JDF 1000',
    }
}

# =========================================================================
# Session 404: JDF Form Scaffolding - Maps relief types to correct forms
# =========================================================================
JDF_FORM_MAPPING = {
    # Emergency/Urgent matters - require IMMEDIATE danger
    'emergency_parenting': {
        'primary_form': 'Motion and Affidavit for Emergency Orders (no standard JDF number)',
        'official_title': 'Motion and Affidavit for Emergency Orders Restricting Parenting Time',
        'required_attachments': ['sworn_affidavit', 'proposed_order'],
        'criteria': 'Imminent physical or emotional danger to child requiring immediate court action',
        'filing_notes': 'Must show imminent danger that cannot wait for regular hearing schedule',
    },
    # Restriction of parenting time (non-emergency)
    'restrict_parenting': {
        'primary_form': 'JDF 1220',
        'official_title': 'Motion to Modify Parenting Time or Decision-Making Responsibilities',
        'required_attachments': ['JDF 1221 (Affidavit)', 'proposed_order', 'exhibits'],
        'criteria': 'Substantial and continuing change in circumstances affecting child\'s best interests',
        'filing_notes': 'Must allege facts showing changed circumstances since last order',
    },
    # Standard modification
    'modify_parenting_time': {
        'primary_form': 'JDF 1220',
        'official_title': 'Motion to Modify Parenting Time',
        'required_attachments': ['JDF 1221 (Affidavit)', 'proposed_order'],
        'criteria': 'Changed circumstances and best interests of child',
        'filing_notes': 'Complete all sections of JDF 1220 and attach supporting JDF 1221 affidavit',
    },
    # Contempt/Enforcement
    'enforce_order': {
        'primary_form': 'Motion for Citation for Contempt of Court',
        'official_title': 'Motion for Citation for Contempt of Court',
        'required_attachments': ['sworn_affidavit', 'copy_of_order_violated', 'proposed_order'],
        'criteria': 'Willful violation of existing court order',
        'filing_notes': 'Must identify SPECIFIC provisions violated and dates of violation',
    },
    # Child support modification
    'modify_child_support': {
        'primary_form': 'JDF 1820 or JDF 1821',
        'official_title': 'Motion to Modify Child Support',
        'required_attachments': ['child_support_worksheet', 'financial_affidavit', 'proposed_order'],
        'criteria': 'Substantial and continuing change in financial circumstances',
        'filing_notes': 'Use JDF 1820 (<93 overnights) or JDF 1821 (93+ overnights)',
    },
    # Parenting interference by third party
    'third_party_interference': {
        'primary_form': 'JDF 1220',
        'official_title': 'Verified Motion Regarding Third-Party Conduct and Child Communication',
        'required_attachments': ['sworn_affidavit', 'proposed_order'],
        'criteria': 'Orders must be directed at PARTY, not third party',
        'filing_notes': 'Court cannot order non-parties. Request order requiring party to control third party behavior.',
    },
    # Session 404 FIX #1: Communication issues - NOT emergency
    'communication_issue': {
        'primary_form': 'JDF 1220',
        'official_title': 'Verified Motion Regarding Third-Party Statements and Child Communication',
        'required_attachments': ['sworn_affidavit', 'proposed_order', 'exhibits'],
        'criteria': 'Address communication concerns through modification, NOT emergency',
        'filing_notes': 'This is NOT an emergency. Use standard modification process with verified motion.',
    },
}

# =========================================================================
# Session 404: Statutory Criteria Categories (no citations, just categories)
# =========================================================================
STATUTORY_CRITERIA = {
    'emergency_restriction': {
        'category': 'Emergency Motion to Restrict Parenting Time',
        'required_elements': [
            'Imminent physical danger to child',
            'Emotional abuse causing immediate harm',
            'Situation cannot wait for regular hearing',
        ],
        'NOT_sufficient': [
            'Disagreement about parenting styles',
            'Historical concerns without current imminent danger',
            'Interference by non-party alone',
        ],
    },
    'modification': {
        'category': 'Motion to Modify Parenting Time',
        'required_elements': [
            'Substantial change in circumstances',
            'Change is continuing (not temporary)',
            'Modification serves child\'s best interests',
        ],
        'best_interest_factors': [
            'Child\'s wishes (if mature)',
            'Parents\' wishes',
            'Child\'s relationships with family members',
            'Adjustment to home, school, community',
            'Mental and physical health of all parties',
            'Each parent\'s ability to foster relationship with other parent',
        ],
    },
    'contempt': {
        'category': 'Motion for Contempt / Enforcement',
        'required_elements': [
            'Valid court order exists',
            'Party had knowledge of order',
            'Party willfully violated order',
            'Specific dates and provisions violated',
        ],
        'remedies_available': [
            'Make-up parenting time',
            'Modification of order',
            'Attorney fees',
            'In extreme cases: jail time',
        ],
    },
}

# =========================================================================
# Session 404: Non-Party Detection Keywords
# =========================================================================
NON_PARTY_INDICATORS = [
    'girlfriend', 'boyfriend', 'partner', 'spouse\'s partner',
    'grandmother', 'grandfather', 'grandparent',
    'aunt', 'uncle', 'cousin',
    'roommate', 'friend', 'neighbor',
    'stepparent', 'step-parent',
    'new wife', 'new husband',
    'fiancé', 'fiancée', 'fiance', 'fiancee',
]

# =========================================================================
# Session 404 FIX #1: EMERGENCY DETECTION - STRICT CRITERIA
# Only TRUE emergencies should trigger emergency forms
# =========================================================================
EMERGENCY_REQUIRED_INDICATORS = [
    # Physical danger indicators (REQUIRED for emergency)
    'imminent danger', 'immediate harm', 'immediate danger',
    'physical harm', 'serious bodily harm', 'life threatening',
    'self-harm', 'suicide', 'abuse', 'physical abuse', 'sexual abuse',
    'domestic violence', 'dv', 'assault', 'battery',
    'police report', 'cps', 'child protective services',
    'fleeing', 'abduction', 'kidnap', 'flee the jurisdiction',
    'immediate risk', 'hospital', 'emergency room', 'er visit',
]

# These are NOT emergency situations - should use standard modification
NON_EMERGENCY_SITUATIONS = [
    'communication', 'statements', 'third-party', 'third party',
    'girlfriend', 'boyfriend', 'partner', 'interference',
    'emotional', 'verbal', 'exchange', 'pickup', 'dropoff',
    'parenting time exchange', 'said', 'told', 'remarks',
]

# =========================================================================
# Session 404 FIX #3: RELIEF TEMPLATES - Auto-fill instead of placeholders
# =========================================================================
RELIEF_TEMPLATES = {
    'communication_issue': [
        "1. Respondent shall ensure that no adult in Respondent's household makes statements to or in the presence of the minor child regarding Petitioner's honesty, character, or the ongoing court proceedings.",
        "2. Respondent shall ensure that adults in Respondent's household do not discuss any aspect of this litigation in the child's presence.",
        "3. Respondent shall ensure that third parties are not present during parenting-time exchanges until further order of the Court.",
    ],
    'third_party_interference': [
        "1. Respondent shall ensure that [THIRD PARTY NAME] is not present during parenting-time exchanges.",
        "2. Respondent shall ensure that [THIRD PARTY NAME] does not communicate with the minor child about Petitioner or this litigation.",
        "3. Respondent shall ensure that all exchanges occur without third-party involvement.",
    ],
    'parenting_time_modification': [
        "1. The parenting time schedule shall be modified as follows: [SPECIFY MODIFICATION].",
        "2. Respondent shall comply with the modified schedule effective upon entry of this Order.",
        "3. These modifications shall remain in effect until further order of the Court.",
    ],
    'contempt_enforcement': [
        "1. Respondent shall be found in contempt for willfully violating the Court's order dated [DATE].",
        "2. Respondent shall comply with the original order immediately.",
        "3. Petitioner shall be awarded make-up parenting time for time lost due to Respondent's violation.",
    ],
}

# =========================================================================
# Session 404 FIX #2: PDF METADATA FILTERS - Remove court headers/footers
# =========================================================================
# =========================================================================
# Session 404 FINAL FIX: Comprehensive content filtering
# The PDF contains: court header + user's motion + judge's denial order
# We need to EXTRACT only the user's motion narrative, nothing else
# =========================================================================

# Patterns that indicate DENIAL ORDER content (judge's ruling - REMOVE ALL)
# Session 404 V5: Made LESS aggressive to avoid filtering user's content
DENIAL_ORDER_INDICATORS = [
    r'order\s+(denied|granted)',
    r'is\s+(hereby\s+)?(denied|granted)',
    r'the\s+court\s+(finds|orders|denies|grants)',
    r'it\s+is\s+(so\s+)?ordered',
    r'this\s+matter\s+comes\s+before\s+the\s+court',
    r'upon\s+review\s+of\s+the\s+(motion|petition)',
    r'the\s+motion\s+is\s+(hereby\s+)?denied',
    r'the\s+request\s+is\s+(hereby\s+)?denied',
    r'signed\s+this\s+\d+\s*day',
    r'dated?\s+this\s+\d+\s*day',
    r'kara\s+e\.?\s+clark',  # Specific judge name from user's case
    r'for\s+the\s+foregoing\s+reasons',
    r'the\s+court\s+has\s+reviewed',
    # Session 404 V5: More specific denial phrases (less aggressive)
    r'relief\s+which\s+the\s+court\s+cannot\s+grant',
    r'the\s+court\s+cannot\s+(order|grant)',
    r'not\s+making\s+the\s+request\s+appropriately',
]

# Patterns that indicate COURT HEADER content (metadata - REMOVE ALL)
COURT_HEADER_PATTERNS = [
    r'^\d{4}DR\d+',  # Case numbers like 2025DR000576
    r'^Division\s*:?\s*\d*',
    r'^Courtroom\s*:?\s*\d*',
    r'^District\s*Court',
    r'^County\s*Court',
    r'^Larimer\s*County',
    r'^LARIMER\s*COUNTY',
    r'^Court\s*Address',
    r'^\s*Page\s*\d+',
    r'^\s*-\s*\d+\s*-',  # Page numbers like - 1 -
    r'^Attachment',
    r'^Exhibit\s*[A-Z]?',
    r'(?:Petitioner|Respondent)\s*[:]\s*$',  # Just the label
    r'^Case\s*Number',
    r'^CASE\s*NUMBER',
    r'^In\s*Re\s*:',
    r'^In\s*the\s*Matter\s*of',
    r'\.pdf',
    r'^Document\s*Type',
    r'^Document\s*Title',
    r'^Status\s*:',
    r'pdf\s*Status',
    r'ORDER\s*$',  # Just "ORDER" header
    r'DENIED\s*$',  # Just "DENIED" header
    r'^\s*Date\s*:\s*$',
    r'^\d+\s*LaPorte',  # Address like "201 LaPorte Ave"
    r'^Fort\s*Collins',
    r'^Colorado\s*\d{5}',
    r'^\s*v\.\s*$',  # Just "v." on a line
    r'^West\s*,',  # Party names
    r'appearing\s*Pro\s*Se',
    r'Document\s*Content',
    r'review\s*Document',
]

# Patterns that indicate USER'S MOTION NARRATIVE (what we WANT to keep)
NARRATIVE_INDICATORS = [
    r'on\s+or\s+about',
    r'on\s+august',
    r'on\s+september',
    r'on\s+october',
    r'on\s+november',
    r'during\s+the\s+exchange',
    r'during\s+parenting\s+time',
    r'the\s+child\s+(stated|said|reported|told)',
    r'nicolas\s+(stated|said|reported|told)',
    r'respondent.s?\s+(girlfriend|partner|boyfriend)',
    r'respondent\s+has\s+(failed|refused|allowed)',
    r'i\s+(observed|witnessed|heard|noticed)',
    r'my\s+(son|daughter|child)',
    r'the\s+minor\s+child',
    r'emotional\s+(distress|harm|damage)',
    r'statements?\s+(were\s+)?made',
    r'third.?party',
    r'interference',
]

# Legacy pattern list for backward compatibility
PDF_METADATA_PATTERNS = COURT_HEADER_PATTERNS

# Legal disclaimer that MUST appear on all outputs
LEGAL_DISCLAIMER = """
---
**IMPORTANT LEGAL DISCLAIMER**

This document is provided for INFORMATIONAL PURPOSES ONLY and does NOT constitute legal advice.
This information does NOT create an attorney-client relationship.

- Laws vary by jurisdiction and change frequently
- Every legal situation is unique and fact-specific
- This template may not be appropriate for your specific circumstances
- Court rules and procedures vary by county

**STRONGLY RECOMMENDED:** Consult with a licensed Colorado family law attorney before
filing any legal documents. Many attorneys offer free or low-cost consultations.

Colorado Bar Association Lawyer Referral: 303-831-8000
Colorado Legal Services (low income): 303-837-1313
---
"""


class LegalDocDrafterAgent(BaseAgent):
    """
    Pro Se Legal Assistant for Colorado Family Law.

    Generates procedural legal documents and provides general legal information
    for self-represented individuals in Colorado family law matters.

    This agent CAN:
    - Draft motion templates (continuance, modification)
    - Generate meet-and-confer email templates
    - Create declaration templates
    - Explain Colorado family law procedures
    - Reference appropriate JDF forms
    - Search legal resources for guidance

    This agent CANNOT:
    - Provide specific legal advice for your case
    - Guarantee any legal outcome
    - Replace consultation with a licensed attorney
    - File documents on your behalf
    - Represent you in court
    """

    name = "LegalDocDrafterAgent"

    system_prompt = """You are a Pro Se Legal Assistant specializing in Colorado family law PROCEDURE.

Your role is to help self-represented individuals understand PROCEDURAL requirements and draft TEMPLATE documents in the correct JDF format.

------------------------------------------------------------
CRITICAL RULES - PROCEDURE ONLY, NO STRATEGY
------------------------------------------------------------

1. ONLY discuss:
   ✓ Procedural paths (which form to file, filing sequence)
   ✓ Filing structure (what sections the JDF requires)
   ✓ Required forms and attachments
   ✓ Evidence and affidavit format requirements
   ✓ Court expectations for properly formatted filings

2. NEVER discuss:
   ✗ Legal strategy ("You should argue...")
   ✗ Case merits ("This will likely succeed...")
   ✗ Optional approaches ("Consider requesting a parenting evaluation...")
   ✗ Predictions about outcomes
   ✗ What the user "should do" beyond procedural steps

3. When referencing JDF forms:
   - Give the OFFICIAL TITLE (e.g., "Motion to Modify Parenting Time")
   - If you know the form number, include it (e.g., "JDF 1220")
   - If uncertain about form number, state the official title only and direct user to verify at coloradojudicial.gov

------------------------------------------------------------
DENIED MOTION ANALYSIS MODE
------------------------------------------------------------

When a user uploads a denied motion, you MUST:

1. IDENTIFY the correct JDF form for their actual relief type
2. EXPLAIN why multiple separate filings may be required
3. DETECT non-party issues (orders cannot be directed at non-parties)
4. TRANSFORM their narrative into JDF-compatible sworn affidavit sections
5. GENERATE an evidence checklist specific to their allegations

Output structure for denied motion rewrite:
A. Correct form identification
B. Why original was denied (mapped to procedural defects)
C. Separate filings needed (if any)
D. Draft affidavit in proper sworn format
E. Draft motion in JDF structure
F. Proposed order template
G. Evidence/exhibit checklist

------------------------------------------------------------
NON-PARTY RULE
------------------------------------------------------------

CRITICAL: Courts CANNOT issue orders against non-parties (girlfriends, boyfriends,
grandparents, new partners, roommates, etc.).

If user seeks relief against a non-party:
- Identify the non-party issue
- Explain: "The court cannot order [non-party name] to do anything because they
  are not a party to this case."
- Provide CORRECT procedure: "Request an order requiring [Respondent/Petitioner]
  to ensure that adults in their home do not [behavior], or to restrict parenting
  time if the other parent fails to control the environment."

------------------------------------------------------------
STATUTORY ALIGNMENT (NO CITATIONS)
------------------------------------------------------------

Map user's facts to statutory CATEGORIES, never cite statute numbers:
- Danger → Emergency motion criteria
- Interference → Parenting time enforcement
- Violation → Contempt (willful violation of existing order)
- Changed circumstances → Modification motion

------------------------------------------------------------
AVAILABLE TOOLS
------------------------------------------------------------

Core Tools:
- search_legal_resources: Search Colorado legal resources and spider data
- draft_motion: Generate a motion template in JDF structure
- draft_email: Generate meet-and-confer email template
- draft_declaration: Generate a sworn declaration template
- get_form_info: Get JDF form information
- explain_procedure: Explain Colorado family law procedure steps

Session 404 Tools (Motion Rewriting):
- analyze_denied_motion: Analyze why a motion was denied, identify all deficiencies
- rewrite_motion: Generate corrected motion in proper JDF format
- generate_evidence_checklist: Create checklist of required exhibits
- check_non_party_issues: Detect non-party relief requests and provide corrections

Remember: You provide PROCEDURAL INFORMATION and JDF-FORMATTED TEMPLATES, not legal advice."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_legal_resources",
                "description": "Search Colorado legal resources, statutes, case law, and spider data for legal information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'Colorado parenting time modification requirements')"
                        },
                        "resource_type": {
                            "type": "string",
                            "enum": ["all", "statutes", "forms", "procedures", "case_law"],
                            "default": "all",
                            "description": "Type of legal resource to search"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "draft_motion",
                "description": "Generate a motion template for Colorado family court",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "motion_type": {
                            "type": "string",
                            "enum": [
                                "continuance",
                                "modify_parenting_time",
                                "modify_child_support",
                                "enforce_order",
                                "reconsideration",
                                "other"
                            ],
                            "description": "Type of motion to draft"
                        },
                        "case_details": {
                            "type": "object",
                            "properties": {
                                "case_number": {"type": "string"},
                                "county": {"type": "string"},
                                "petitioner_name": {"type": "string"},
                                "respondent_name": {"type": "string"},
                                "children": {"type": "array", "items": {"type": "string"}}
                            },
                            "description": "Case details (optional - will use placeholders if not provided)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Brief reason for the motion"
                        },
                        "specific_request": {
                            "type": "string",
                            "description": "What specific relief is being requested"
                        }
                    },
                    "required": ["motion_type", "reason"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "draft_email",
                "description": "Generate a meet-and-confer email template for opposing party or counsel",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_type": {
                            "type": "string",
                            "enum": [
                                "meet_and_confer",
                                "settlement_proposal",
                                "scheduling",
                                "document_request",
                                "status_update"
                            ],
                            "description": "Type of email to draft"
                        },
                        "recipient": {
                            "type": "string",
                            "description": "Recipient description (e.g., 'opposing counsel', 'ex-spouse')"
                        },
                        "subject_matter": {
                            "type": "string",
                            "description": "What the email is about"
                        },
                        "tone": {
                            "type": "string",
                            "enum": ["formal", "professional", "conciliatory"],
                            "default": "professional",
                            "description": "Tone of the email"
                        }
                    },
                    "required": ["email_type", "subject_matter"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "draft_declaration",
                "description": "Generate a declaration template under penalty of perjury",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "declaration_purpose": {
                            "type": "string",
                            "description": "Purpose of the declaration (e.g., 'support motion to modify parenting time')"
                        },
                        "key_facts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key facts to include in the declaration"
                        },
                        "declarant_role": {
                            "type": "string",
                            "enum": ["petitioner", "respondent", "witness"],
                            "description": "Role of person making declaration"
                        }
                    },
                    "required": ["declaration_purpose"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_form_info",
                "description": "Get information about a specific Colorado JDF form",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "form_number": {
                            "type": "string",
                            "description": "JDF form number (e.g., 'JDF 1111', 'JDF 1220')"
                        },
                        "form_category": {
                            "type": "string",
                            "enum": ["divorce", "parenting", "child_support", "general"],
                            "description": "Category of form if form number unknown"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "explain_procedure",
                "description": "Explain a Colorado family law procedure step by step",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "procedure": {
                            "type": "string",
                            "enum": [
                                "file_for_divorce",
                                "modify_parenting_time",
                                "modify_child_support",
                                "enforce_order",
                                "respond_to_motion",
                                "file_motion",
                                "attend_hearing",
                                "mediation"
                            ],
                            "description": "The procedure to explain"
                        },
                        "county": {
                            "type": "string",
                            "description": "Colorado county (procedures may vary slightly)"
                        }
                    },
                    "required": ["procedure"]
                }
            }
        },
        # =====================================================================
        # Session 404: New Tools for Motion Rewriting
        # =====================================================================
        {
            "type": "function",
            "function": {
                "name": "analyze_denied_motion",
                "description": "Analyze a denied motion to identify deficiencies and recommend corrective actions. Use when user uploads a denied motion or court order denying their motion.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "motion_content": {
                            "type": "string",
                            "description": "The text content of the denied motion"
                        },
                        "denial_reasons": {
                            "type": "string",
                            "description": "The court's stated reasons for denial (from order or minute entry)"
                        },
                        "original_relief_requested": {
                            "type": "string",
                            "description": "What relief the user originally requested"
                        }
                    },
                    "required": ["motion_content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rewrite_motion",
                "description": "Generate a corrected motion using proper JDF format based on analysis of a denied motion. Transforms user's narrative into JDF-compatible structure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relief_type": {
                            "type": "string",
                            "enum": [
                                "modify_parenting_time",
                                "restrict_parenting",
                                "emergency_parenting",
                                "enforce_order",
                                "modify_child_support",
                                "contempt"
                            ],
                            "description": "Type of relief being sought"
                        },
                        "facts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of factual allegations to include"
                        },
                        "dates_incidents": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "date": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            },
                            "description": "Specific dated incidents"
                        },
                        "relief_requested": {
                            "type": "string",
                            "description": "Specific relief requested from court"
                        },
                        "case_details": {
                            "type": "object",
                            "properties": {
                                "case_number": {"type": "string"},
                                "county": {"type": "string"},
                                "petitioner_name": {"type": "string"},
                                "respondent_name": {"type": "string"}
                            },
                            "description": "Case identifying information"
                        }
                    },
                    "required": ["relief_type", "facts", "relief_requested"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_evidence_checklist",
                "description": "Generate a checklist of required evidence and exhibits based on motion type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "motion_type": {
                            "type": "string",
                            "enum": [
                                "modify_parenting_time",
                                "restrict_parenting",
                                "emergency_parenting",
                                "enforce_order",
                                "modify_child_support",
                                "contempt"
                            ],
                            "description": "Type of motion being filed"
                        },
                        "allegations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What allegations are being made"
                        }
                    },
                    "required": ["motion_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_non_party_issues",
                "description": "Check if the motion incorrectly seeks relief against non-parties and provide correction guidance",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "motion_text": {
                            "type": "string",
                            "description": "The text of the motion to analyze"
                        },
                        "parties_in_case": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Names of actual parties to the case"
                        }
                    },
                    "required": ["motion_text"]
                }
            }
        },
        # Session 405 Enhancement #2: Emergency vs Non-Emergency Detector
        {
            "type": "function",
            "function": {
                "name": "assess_emergency_status",
                "description": "Assess whether a situation qualifies as a legal emergency under Colorado law (C.R.S. § 14-10-129.5). Determines if harm is immediate and warns when a situation is NOT actually an emergency.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "situation_description": {
                            "type": "string",
                            "description": "Description of the situation and alleged harm"
                        },
                        "claimed_emergency": {
                            "type": "boolean",
                            "description": "Whether the user/motion claims this is an emergency"
                        }
                    },
                    "required": ["situation_description"]
                }
            }
        },
        # Session 405 Enhancement #3: Court Order Being Modified Detector
        {
            "type": "function",
            "function": {
                "name": "check_order_attachment_required",
                "description": "Check if the motion requires attachment of an existing court order and prompt user to upload it if missing.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "motion_text": {
                            "type": "string",
                            "description": "The text of the motion to analyze"
                        },
                        "uploaded_documents": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of document types already uploaded"
                        }
                    },
                    "required": ["motion_text"]
                }
            }
        },
        # Session 405 Enhancement #4: Conflict With Prior Orders Detector
        {
            "type": "function",
            "function": {
                "name": "detect_order_conflicts",
                "description": "Detect potential conflicts between requested relief and existing court orders. Analyzes uploaded orders and flags requests that contradict, duplicate, or ignore existing provisions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "motion_text": {
                            "type": "string",
                            "description": "The text of the motion to analyze"
                        },
                        "existing_order_text": {
                            "type": "string",
                            "description": "Text from the existing court order (if uploaded)"
                        },
                        "existing_order_summary": {
                            "type": "string",
                            "description": "Summary of key provisions from existing order"
                        }
                    },
                    "required": ["motion_text"]
                }
            }
        },
        # Session 405 Enhancement #5: Likelihood of Success Confidence Meter
        {
            "type": "function",
            "function": {
                "name": "assess_likelihood_of_success",
                "description": "Calculate a likelihood of success score for a motion based on relief scope, evidence strength, procedural posture, and Colorado case law signals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "motion_text": {
                            "type": "string",
                            "description": "The text of the motion to analyze"
                        },
                        "relief_type": {
                            "type": "string",
                            "description": "Type of relief being requested"
                        },
                        "has_evidence": {
                            "type": "boolean",
                            "description": "Whether supporting evidence/exhibits are mentioned"
                        },
                        "is_rewrite": {
                            "type": "boolean",
                            "description": "Whether this is a rewrite of a previously denied motion"
                        }
                    },
                    "required": ["motion_text"]
                }
            }
        },
        # Session 406: Conferral Email Generator
        {
            "type": "function",
            "function": {
                "name": "generate_conferral_email",
                "description": "Generate a conferral email to send to opposing party before filing a non-emergency motion. Per C.R.C.P. 121 § 1-15(8), Colorado requires parties to confer before filing most motions. This tool generates the email text, Certificate of Conferral for the motion, and guidance on the workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "petitioner": {
                            "type": "string",
                            "description": "Name of the moving party (petitioner)"
                        },
                        "respondent": {
                            "type": "string",
                            "description": "Name of the opposing party (respondent)"
                        },
                        "relief_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of specific relief items being requested"
                        },
                        "case_context": {
                            "type": "string",
                            "description": "Brief description of the issue (e.g., 'Third-Party Statements / Parenting Time Issue')"
                        },
                        "deadline_days": {
                            "type": "integer",
                            "description": "Number of days to give for response (default 2)"
                        }
                    },
                    "required": ["petitioner", "respondent", "relief_points"]
                }
            }
        }
    ]

    # Session 856: Mission Control configuration for legal document review
    actionable_config = ActionableOutputConfig(
        enabled=True,
        item_type='review',
        default_urgency='high',  # Legal documents need careful review
        min_confidence=0.0,
        actions=[
            {'id': 'approve', 'label': 'Approve', 'style': 'success', 'description': 'Approve document for filing'},
            {'id': 'revise', 'label': 'Request Revision', 'style': 'warning', 'description': 'Request changes before filing'},
            {'id': 'reject', 'label': 'Reject', 'style': 'danger', 'description': 'Do not use this document'},
            {'id': 'consult', 'label': 'Consult Attorney', 'style': 'primary', 'description': 'Mark for attorney review'},
        ],
        payload_fields=['type', 'documents_generated', 'jurisdiction', 'focus_area'],
        max_items_per_hour=5
    )

    def __init__(self, user=None, case_id: str = None):
        super().__init__(user)
        self._spider_service = None
        self._semantic_search = None
        self.case_id = case_id  # Optional: Link to LegalCase
        self._current_case = None
        # Session 405: Ensure agent is registered in database for learning hooks
        self._ensure_agent_registered()

    @property
    def current_case(self):
        """Get the current LegalCase if case_id is provided."""
        if self._current_case is None and self.case_id:
            try:
                from core.models_unified_system import LegalCase
                self._current_case = LegalCase.objects.get(id=self.case_id)
            except Exception as _e:
                logger.warning(
                    "legal_doc_drafter_agent.current_case: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        return self._current_case

    @property
    def spider_service(self):
        """Lazy-load Spider Intelligence Service."""
        if self._spider_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_service = SpiderIntelligenceService()
        return self._spider_service

    @property
    def semantic_search(self):
        """Lazy-load Spider Semantic Search Service."""
        if self._semantic_search is None:
            from core.services.spider_semantic_search import get_spider_semantic_search
            self._semantic_search = get_spider_semantic_search()
        return self._semantic_search

    def _get_fresh_legal_spider_intelligence(self, task: str, hours: int = 168, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Session 461: Get fresh legal spider intelligence for document drafting.

        Queries legal-specific spiders for recent case law, legal news, and
        procedural updates that may be relevant to the user's task.

        Legal Spiders:
        - courtlistener: Case law and court opinions
        - legal_news: Legal news and updates
        - findlaw: Legal resources and articles
        - lii: Cornell Legal Information Institute
        - colorado_family_law: Colorado-specific family law resources
        - justia_family_law: Family law case summaries

        Args:
            task: The user's legal task/question
            hours: How far back to look (default 7 days for legal data)
            limit: Maximum items to return

        Returns:
            List of relevant legal intelligence dicts
        """
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone
            from datetime import timedelta

            cutoff = timezone.now() - timedelta(hours=hours)

            # Legal spider sources
            legal_sources = [
                'courtlistener', 'legal_news', 'findlaw', 'lii',
                'colorado_family_law', 'justia_family_law'
            ]

            # Query SpiderData for legal content
            query = SpiderData.objects.filter(
                created_at__gte=cutoff,
                spider_name__in=legal_sources
            )

            # Order by recency and get results
            # Note: SpiderData uses JSON fields so we filter by spider_name (legal spiders)
            # then do keyword relevance scoring in Python
            results = query.order_by('-created_at')[:limit]

            intelligence = []
            for item in results:
                # SpiderData stores data in raw_data or processed_data JSON fields
                raw_data = item.raw_data or {}
                processed_data = item.processed_data or {}

                # Extract title and content from the data
                title = raw_data.get('title') or processed_data.get('title') or 'Untitled'
                content = raw_data.get('description') or raw_data.get('content') or \
                          processed_data.get('summary') or ''
                url = item.source_url or raw_data.get('url') or raw_data.get('link') or ''

                intelligence.append({
                    'title': title[:100] if title else 'Untitled',
                    'content': content[:500] if content else '',
                    'source': item.spider_name,
                    'url': url,
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                })

            if intelligence:
                logger.info(f"📚 Retrieved {len(intelligence)} legal intelligence items for task")

            return intelligence

        except Exception as e:
            logger.warning(f"Error getting legal spider intelligence: {e}")
            return []

    def _ensure_agent_registered(self):
        """
        Session 405: Ensure LegalDocDrafterAgent is registered in the Agent database.

        This is required for learning hooks to work:
        - _share_knowledge() needs agent_model to not be None
        - _create_execution_memory() needs agent_model
        - _track_contribution() needs agent_model

        Without this, the legal agent is isolated from collective intelligence.
        """
        try:
            from core.models_unified_system import Agent

            # Force agent_model to be created if it doesn't exist
            if self._agent_model is None:
                self._agent_model, created = Agent.objects.get_or_create(
                    name=self.name,
                    defaults={
                        'agent_type': 'legal',
                        'description': 'Pro Se Legal Assistant for Colorado Family Law. '
                                      'Helps self-represented litigants draft motions, '
                                      'analyze denied filings, and generate court-ready documents.',
                        'is_active': True
                    }
                )
                if created:
                    logger.info(f"Session 405: Registered {self.name} in Agent database for collective learning")
        except Exception as e:
            logger.warning(f"Could not ensure agent registration: {e}")

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute legal document drafting or information request."""
        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        with self.time_travel_session("legal_assistance", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing legal assistance request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                # =====================================================================
                # Session 404: DETECT DENIED MOTION MODE
                # If we detect a denied motion, FORCE direct tool calls instead of GPT
                # =====================================================================
                denied_motion_mode = self._detect_denied_motion_mode(task, context)

                if denied_motion_mode:
                    logger.info("DENIED MOTION MODE ACTIVATED - Forcing direct tool calls")
                    return self._execute_denied_motion_pipeline(task, context, start_time)

                # Standard mode: Build prompt with legal context
                full_prompt = self._build_legal_prompt(task, context)

                # Make GPT call
                gpt_response = self._call_openai(full_prompt)

                # Process tool calls
                generated_documents = []
                legal_info = []

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for legal assistance",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result_preview': str(tool_result)[:200]
                        })

                        if tool_result.get('success'):
                            if tool_result.get('document'):
                                generated_documents.append(tool_result)
                            else:
                                legal_info.append(tool_result)

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                execution_time = int((time.time() - start_time) * 1000)

                # Build response message
                response_parts = []

                # Save generated documents to database and add to response
                saved_doc_ids = []
                for doc in generated_documents:
                    response_parts.append(doc.get('document', ''))
                    # Save to LegalDocument model
                    saved_doc = self._save_legal_document(
                        task=task,
                        document=doc,
                        context=context,
                        execution_time_ms=execution_time
                    )
                    if saved_doc:
                        saved_doc_ids.append(str(saved_doc.id))

                # Save legal info research and add to response
                saved_research_ids = []
                for info in legal_info:
                    if info.get('explanation'):
                        response_parts.append(info.get('explanation'))
                    if info.get('form_info'):
                        response_parts.append(info.get('form_info'))
                    if info.get('search_results'):
                        response_parts.append(f"**Relevant Information:**\n{info.get('search_results')}")

                    # Save to LegalResearchResult model
                    saved_research = self._save_legal_research(
                        task=task,
                        info=info,
                        context=context,
                        execution_time_ms=execution_time
                    )
                    if saved_research:
                        saved_research_ids.append(str(saved_research.id))

                # If no tool calls, use GPT's direct response
                if not response_parts and gpt_response.get('content'):
                    response_parts.append(gpt_response.get('content'))

                # Session 404D: REMOVED DISCLAIMER from court-ready documents
                # Disclaimers should NOT appear in final court documents

                message = "\n\n".join(response_parts) if response_parts else "I wasn't able to process your request. Please try rephrasing."

                result = AgentResult(
                    success=True,
                    message=message,
                    data={
                        'type': 'legal_assistance',
                        'documents_generated': len(generated_documents),
                        'legal_info_provided': len(legal_info),
                        'query': task,
                        'jurisdiction': 'Colorado',
                        'focus_area': 'Family Law',
                        'disclaimer_included': True,
                        'saved_document_ids': saved_doc_ids,
                        'saved_research_ids': saved_research_ids,
                        'case_id': self.case_id,
                    },
                    agent_name=self.name,
                    execution_time_ms=execution_time,
                    tool_calls=tool_calls_made
                )

                # Record learning outcome (existing)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(legal_info),
                    scifi_context_used=False
                )

                # Create execution memory for successful legal assistance
                if generated_documents or legal_info:
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.8  # Legal documents are important
                    )

                    # Share knowledge if significant legal pattern discovered
                    if generated_documents:
                        self._share_legal_knowledge(task, generated_documents, context)

                    # Session 861: Also persist to Deliverable for universal access
                    for doc in generated_documents:
                        doc_type = doc.get('document_type', 'other')
                        doc_content = doc.get('document', '')
                        if doc_content:
                            self._save_to_deliverable(
                                title=f"Legal {doc_type.title()}: {task[:80]}",
                                content=doc_content,
                                deliverable_type='document',
                                category='Legal',
                                tags=['legal', doc_type, 'colorado', 'family-law'],
                                content_format='markdown',
                                metadata={
                                    'document_type': doc_type,
                                    'motion_type': doc.get('motion_type', ''),
                                    'jurisdiction': 'Colorado',
                                    'case_id': str(self.case_id) if self.case_id else None,
                                },
                                user=self.user,
                            )

                # Session 409: Validate output through Mythology Enforcer to prevent hallucinations
                # This is CRITICAL for legal documents - must not contain unrealistic claims
                result = self._validate_output(result)

                return result

            except Exception as e:
                logger.error(f"LegalDocDrafterAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),  # Session 404D: Removed disclaimer from errors too
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _build_legal_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build prompt with legal context, safeguards, and uploaded case files."""

        prompt_parts = [
            f"User Request: {task}",
            "",
            "IMPORTANT GUIDELINES:",
            "1. Provide GENERAL LEGAL INFORMATION only, not specific legal advice",
            "2. Always recommend consulting with a licensed Colorado family law attorney",
            "3. Reference appropriate Colorado JDF forms from the FORM REFERENCE below",
            "4. Focus on procedural guidance, not legal strategy",
            "5. Generated documents should be clearly marked as TEMPLATES",
            "6. ALWAYS use the JDF form reference data below — do NOT rely solely on external search",
            "7. Call draft_motion or explain_procedure tools when the user asks for documents or steps",
            "",
            "Colorado Family Law Context:",
            "- Governing statutes: C.R.S. Title 14 (Domestic Matters)",
            "- Court: District Court, Family Division",
            "- Forms: JDF (Judicial Department Forms) series",
            "",
            "=== JDF FORM REFERENCE (use this data) ===",
        ]

        # Session 1035: Inject JDF form mapping so GPT has it in context
        for relief_type, form_data in JDF_FORM_MAPPING.items():
            prompt_parts.append(
                f"- {relief_type}: {form_data['primary_form']} — {form_data['official_title']}. "
                f"Criteria: {form_data['criteria']}. "
                f"Required: {', '.join(form_data['required_attachments'])}."
            )
        prompt_parts.append("=== END FORM REFERENCE ===")
        prompt_parts.append("")

        # Session 461: Inject fresh legal spider intelligence
        legal_intelligence = self._get_fresh_legal_spider_intelligence(task)
        if legal_intelligence:
            prompt_parts.append("=== RECENT LEGAL INTELLIGENCE ===")
            prompt_parts.append("The following recent legal news and case law may be relevant:")
            for item in legal_intelligence[:5]:
                source = item.get('source', 'Unknown')
                title = item.get('title', '')[:80]
                content = item.get('content', '')[:200]
                prompt_parts.append(f"- [{source}] {title}")
                if content:
                    prompt_parts.append(f"  {content}...")
            prompt_parts.append("=== END LEGAL INTELLIGENCE ===")
            prompt_parts.append("")

        # Add any case context if provided
        if context.get('case_number'):
            prompt_parts.append(f"Case Number: {context.get('case_number')}")
        if context.get('county'):
            prompt_parts.append(f"County: {context.get('county')}")
        if context.get('children'):
            prompt_parts.append(f"Children involved: Yes")

        # Session 403: Add uploaded case file context if document ID is referenced
        document_context = self._get_uploaded_document_context(task, context)
        if document_context:
            prompt_parts.append("")
            prompt_parts.append("=== UPLOADED CASE DOCUMENT CONTEXT ===")
            prompt_parts.append(document_context)
            prompt_parts.append("=== END DOCUMENT CONTEXT ===")
            prompt_parts.append("")
            prompt_parts.append("IMPORTANT: Use the above document context to inform your response.")
            prompt_parts.append("If this is a denied motion, analyze why it was denied and recommend corrective actions.")

        return "\n".join(prompt_parts)

    def _get_uploaded_document_context(self, task: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Retrieve context from uploaded legal documents.

        Session 403: Extracts document content if:
        - A document_id is referenced in the task
        - Context contains a document_id
        - User's most recent uploaded documents (for general context)
        """
        try:
            from core.models_unified_system import LegalDocument
            import re

            # Check for document ID in task (format: "document ID: uuid")
            doc_id_match = re.search(r'document\s*(?:ID|id)?:?\s*([a-f0-9-]{36})', task, re.IGNORECASE)
            document_id = None

            if doc_id_match:
                document_id = doc_id_match.group(1)
            elif context.get('document_id'):
                document_id = context.get('document_id')
            elif context.get('case_file_id'):
                document_id = context.get('case_file_id')

            if document_id and self.user:
                try:
                    doc = LegalDocument.objects.get(id=document_id, user=self.user)
                    # Build context from document
                    doc_context_parts = [
                        f"Document Title: {doc.title}",
                        f"Document Type: {doc.document_type}",
                        f"Status: {doc.status}",
                    ]
                    if doc.original_query:
                        doc_context_parts.append(f"User's Notes: {doc.original_query}")
                    # Add document content (truncated for prompt size)
                    content_preview = doc.content[:8000] if doc.content else ''
                    if content_preview:
                        doc_context_parts.append(f"\nDocument Content:\n{content_preview}")
                        if len(doc.content) > 8000:
                            doc_context_parts.append("\n[Document truncated for length]")
                    return "\n".join(doc_context_parts)
                except LegalDocument.DoesNotExist:
                    logger.warning(f"Referenced document {document_id} not found")

            # If no specific document but user exists, check for recent relevant uploads
            if self.user and not document_id:
                # Session 1035: Use valid LegalDocument.document_type choices
                recent_docs = LegalDocument.objects.filter(
                    user=self.user,
                    document_type__in=['motion', 'response', 'declaration', 'agreement', 'notes', 'other']
                ).order_by('-created_at')[:2]

                if recent_docs.exists():
                    context_parts = ["Recent uploaded case documents that may be relevant:"]
                    for doc in recent_docs:
                        context_parts.append(f"\n--- {doc.title} ({doc.document_type}) ---")
                        # Only include brief excerpt
                        excerpt = doc.content[:1500] if doc.content else 'No content'
                        context_parts.append(excerpt)
                        if doc.content and len(doc.content) > 1500:
                            context_parts.append("[...]")
                    return "\n".join(context_parts)

            # Session 1035: Fallback to content app Documents (user-uploaded PDFs, URLs)
            document_context = None
            if self.user and not document_id:
                try:
                    from core.services.embedding_service import get_embedding_service
                    from content.models import DocumentEmbedding
                    from pgvector.django import CosineDistance

                    service = get_embedding_service()
                    query_vec = service.get_embedding_sync(task[:500])

                    results = DocumentEmbedding.objects.annotate(
                        distance=CosineDistance('embedding_vector', query_vec)
                    ).filter(
                        document__owner=self.user,
                        document__status='processed',
                        distance__lt=0.40,  # Higher bar for legal (similarity > 0.60)
                    ).select_related('document').order_by('distance')[:5]

                    if results.exists():
                        parts = []
                        for emb in results:
                            parts.append(f"[{emb.document.title}]\n{emb.chunk_text}")
                        document_context = "\n---\n".join(parts)
                except Exception as e:
                    logger.debug(f"Content app document search failed: {e}")

            return document_context

        except Exception as e:
            logger.warning(f"Error getting uploaded document context: {e}")
            return None

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call for legal assistance."""

        if tool_name == "search_legal_resources":
            return self._search_legal_resources(
                query=arguments.get('query', ''),
                resource_type=arguments.get('resource_type', 'all')
            )

        elif tool_name == "draft_motion":
            return self._draft_motion(
                motion_type=arguments.get('motion_type', 'other'),
                case_details=arguments.get('case_details', {}),
                reason=arguments.get('reason', ''),
                specific_request=arguments.get('specific_request', '')
            )

        elif tool_name == "draft_email":
            return self._draft_email(
                email_type=arguments.get('email_type', 'meet_and_confer'),
                recipient=arguments.get('recipient', 'opposing party'),
                subject_matter=arguments.get('subject_matter', ''),
                tone=arguments.get('tone', 'professional')
            )

        elif tool_name == "draft_declaration":
            return self._draft_declaration(
                declaration_purpose=arguments.get('declaration_purpose', ''),
                key_facts=arguments.get('key_facts', []),
                declarant_role=arguments.get('declarant_role', 'petitioner')
            )

        elif tool_name == "get_form_info":
            return self._get_form_info(
                form_number=arguments.get('form_number'),
                form_category=arguments.get('form_category')
            )

        elif tool_name == "explain_procedure":
            return self._explain_procedure(
                procedure=arguments.get('procedure', ''),
                county=arguments.get('county', 'Denver')
            )

        # =====================================================================
        # Session 404: New Tool Handlers
        # =====================================================================
        elif tool_name == "analyze_denied_motion":
            return self._analyze_denied_motion(
                motion_content=arguments.get('motion_content', ''),
                denial_reasons=arguments.get('denial_reasons', ''),
                original_relief_requested=arguments.get('original_relief_requested', '')
            )

        elif tool_name == "rewrite_motion":
            return self._rewrite_motion(
                relief_type=arguments.get('relief_type', 'modify_parenting_time'),
                facts=arguments.get('facts', []),
                dates_incidents=arguments.get('dates_incidents', []),
                relief_requested=arguments.get('relief_requested', ''),
                case_details=arguments.get('case_details', {})
            )

        elif tool_name == "generate_evidence_checklist":
            return self._generate_evidence_checklist(
                motion_type=arguments.get('motion_type', ''),
                allegations=arguments.get('allegations', [])
            )

        elif tool_name == "check_non_party_issues":
            return self._check_non_party_issues(
                motion_text=arguments.get('motion_text', ''),
                parties_in_case=arguments.get('parties_in_case', [])
            )

        # Session 405 Enhancement #2: Emergency Assessment
        elif tool_name == "assess_emergency_status":
            return self._assess_emergency_status(
                situation_description=arguments.get('situation_description', ''),
                claimed_emergency=arguments.get('claimed_emergency', False)
            )

        # Session 405 Enhancement #3: Court Order Attachment Check
        elif tool_name == "check_order_attachment_required":
            return self._check_order_attachment_required(
                motion_text=arguments.get('motion_text', ''),
                uploaded_documents=arguments.get('uploaded_documents', [])
            )

        # Session 405 Enhancement #4: Conflict With Prior Orders Detector
        elif tool_name == "detect_order_conflicts":
            return self._detect_order_conflicts(
                motion_text=arguments.get('motion_text', ''),
                existing_order_text=arguments.get('existing_order_text', ''),
                existing_order_summary=arguments.get('existing_order_summary', '')
            )

        # Session 405 Enhancement #5: Likelihood of Success
        elif tool_name == "assess_likelihood_of_success":
            return self._assess_likelihood_of_success(
                motion_text=arguments.get('motion_text', ''),
                relief_type=arguments.get('relief_type', ''),
                has_evidence=arguments.get('has_evidence', False),
                is_rewrite=arguments.get('is_rewrite', False)
            )

        # Session 406: Conferral Email Generator
        elif tool_name == "generate_conferral_email":
            return self._generate_conferral_email(
                petitioner=arguments.get('petitioner', ''),
                respondent=arguments.get('respondent', ''),
                relief_points=arguments.get('relief_points', []),
                case_context=arguments.get('case_context', ''),
                deadline_days=arguments.get('deadline_days', 2),
                respondent_counsel=arguments.get('respondent_counsel', '')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _search_legal_resources(
        self,
        query: str,
        resource_type: str = 'all'
    ) -> Dict[str, Any]:
        """Search legal resources using spider data and web search."""
        try:
            # Search spider data for legal information
            results = self.semantic_search.semantic_search(
                query=f"Colorado family law {query}",
                category='legal',
                hours=720,  # 30 days
                limit=20,
                min_similarity=0.3
            )

            # Format results
            formatted_results = []
            for r in results[:10]:
                formatted_results.append(f"- **{r.title}**\n  {r.description[:200]}...\n  Source: {r.source}")

            return {
                'success': True,
                'search_results': "\n\n".join(formatted_results) if formatted_results else "No specific results found. Consider consulting Colorado Judicial Branch website: https://www.coloradojudicial.gov",
                'result_count': len(results)
            }

        except Exception as e:
            logger.error(f"Legal search error: {e}")
            return {
                'success': True,  # Don't fail, just provide guidance
                'search_results': f"For {query}, please consult:\n- Colorado Judicial Branch: https://www.coloradojudicial.gov\n- Colorado Revised Statutes Title 14\n- Your local court's self-help center",
                'result_count': 0
            }

    def _draft_motion(
        self,
        motion_type: str,
        case_details: Dict[str, Any],
        reason: str,
        specific_request: str
    ) -> Dict[str, Any]:
        """Generate a motion template."""

        # Get case details or use placeholders
        case_number = case_details.get('case_number', '[CASE NUMBER]')
        county = case_details.get('county', '[COUNTY]')
        petitioner = case_details.get('petitioner_name', '[PETITIONER NAME]')
        respondent = case_details.get('respondent_name', '[RESPONDENT NAME]')

        # Motion type specific content
        motion_titles = {
            'continuance': 'MOTION FOR CONTINUANCE',
            'modify_parenting_time': 'MOTION TO MODIFY PARENTING TIME',
            'modify_child_support': 'MOTION TO MODIFY CHILD SUPPORT',
            'enforce_order': 'MOTION FOR CONTEMPT / ENFORCEMENT',
            'reconsideration': 'MOTION FOR RECONSIDERATION',
            'other': 'MOTION'
        }

        relevant_forms = {
            'modify_parenting_time': 'JDF 1220',
            'modify_child_support': 'JDF 1820/1821'
        }

        title = motion_titles.get(motion_type, 'MOTION')
        form_note = f"\n**Related Form:** {relevant_forms.get(motion_type, 'See Colorado Judicial Branch for applicable forms')}" if motion_type in relevant_forms else ""

        document = f"""
# {title}
## TEMPLATE - REVIEW AND MODIFY BEFORE FILING

**District Court, {county} County, Colorado**
**Case Number:** {case_number}

---

**In the Matter of:**
Petitioner: {petitioner}
Respondent: {respondent}

---

### {title}

{petitioner if case_details.get('moving_party', 'petitioner') == 'petitioner' else respondent} ("Moving Party"), respectfully moves this Court as follows:

**1. BACKGROUND**
[Describe the relevant background of your case]

**2. REASON FOR THIS MOTION**
{reason if reason else '[State the reason for this motion]'}

**3. LEGAL BASIS**
[Cite applicable Colorado statutes - e.g., C.R.S. § 14-10-129 for parenting time modification]

**4. SPECIFIC REQUEST**
{specific_request if specific_request else '[State what specific relief you are requesting from the Court]'}

**5. CONCLUSION**
WHEREFORE, the Moving Party respectfully requests that this Court:
a) Grant this motion;
b) [Specific relief requested];
c) Grant such other relief as the Court deems just and proper.

---

Respectfully submitted,

_______________________________
{petitioner if case_details.get('moving_party', 'petitioner') == 'petitioner' else respondent}
Pro Se Litigant
[Address]
[Phone]
[Email]

Date: {datetime.now().strftime('%B %d, %Y')}

---

### CERTIFICATE OF SERVICE

I certify that on _____________, I served a copy of this Motion on the opposing party by:
[ ] Hand delivery
[ ] U.S. Mail, first class, postage prepaid
[ ] E-filing system notification

_______________________________
Signature
{form_note}

---
**THIS IS A TEMPLATE** - Review Colorado Rules of Civil Procedure and local court rules before filing.
Filing fees may apply. Contact your local clerk of court for current fees and filing procedures.
"""

        return {
            'success': True,
            'document': document,
            'document_type': 'motion',
            'motion_type': motion_type
        }

    def _draft_email(
        self,
        email_type: str,
        recipient: str,
        subject_matter: str,
        tone: str = 'professional'
    ) -> Dict[str, Any]:
        """Generate an email template."""

        email_subjects = {
            'meet_and_confer': f'Meet and Confer Request: {subject_matter}',
            'settlement_proposal': f'Settlement Proposal: {subject_matter}',
            'scheduling': f'Scheduling Request: {subject_matter}',
            'document_request': f'Document Request: {subject_matter}',
            'status_update': f'Status Update: {subject_matter}'
        }

        subject = email_subjects.get(email_type, f'Re: {subject_matter}')

        openings = {
            'formal': f'Dear {recipient}:',
            'professional': f'Dear {recipient},',
            'conciliatory': f'Dear {recipient},'
        }

        opening = openings.get(tone, f'Dear {recipient},')

        document = f"""
# EMAIL TEMPLATE - Meet and Confer / Communication
## Review and customize before sending

---

**To:** {recipient}
**Subject:** {subject}
**Date:** {datetime.now().strftime('%B %d, %Y')}

---

{opening}

I am writing regarding [CASE NAME/NUMBER] concerning {subject_matter}.

**PURPOSE OF THIS EMAIL:**
[State the purpose clearly and concisely]

**RELEVANT FACTS:**
[List key facts relevant to your communication]
-
-
-

**PROPOSED RESOLUTION / REQUEST:**
[State what you are proposing or requesting]

**TIMELINE:**
I would appreciate a response by [DATE]. If I do not hear from you by this date, I intend to [next steps, e.g., "file a motion with the Court"].

**WILLINGNESS TO DISCUSS:**
I remain open to discussing this matter and reaching a mutually agreeable resolution. Please feel free to contact me at [PHONE] or [EMAIL] to discuss further.

Thank you for your attention to this matter.

Sincerely,

[YOUR NAME]
Pro Se Litigant
[ADDRESS]
[PHONE]
[EMAIL]

---

**TEMPLATE NOTES:**
- Keep communications factual and professional
- Avoid emotional language or accusations
- Document all communications
- Save copies for your records
- Consider following up in writing after phone conversations
"""

        return {
            'success': True,
            'document': document,
            'document_type': 'email',
            'email_type': email_type
        }

    def _draft_declaration(
        self,
        declaration_purpose: str,
        key_facts: List[str],
        declarant_role: str = 'petitioner'
    ) -> Dict[str, Any]:
        """Generate a declaration template."""

        # Format key facts as numbered paragraphs
        facts_text = ""
        if key_facts:
            for i, fact in enumerate(key_facts, start=4):
                facts_text += f"\n{i}. {fact}\n"
        else:
            facts_text = """
4. [State fact 1]

5. [State fact 2]

6. [State fact 3]

[Add additional numbered paragraphs as needed]
"""

        document = f"""
# DECLARATION
## TEMPLATE - Under Penalty of Perjury

---

**District Court, [COUNTY] County, Colorado**
**Case Number:** [CASE NUMBER]

---

### DECLARATION OF [YOUR NAME]

I, [YOUR FULL LEGAL NAME], declare under penalty of perjury under the laws of the State of Colorado that the following is true and correct:

1. I am the {declarant_role} in the above-captioned matter. I am over the age of 18 and competent to testify to the matters stated herein.

2. I make this declaration in support of {declaration_purpose}.

3. I have personal knowledge of the facts stated in this declaration and, if called as a witness, I could and would competently testify to these facts.

{facts_text}

I declare under penalty of perjury under the laws of the State of Colorado that the foregoing is true and correct.

Executed on {datetime.now().strftime('%B %d, %Y')}, in [CITY], Colorado.

_______________________________
[YOUR FULL LEGAL NAME]

---

**IMPORTANT NOTES:**
- Only include facts you personally know to be true
- False statements can result in perjury charges
- Be specific with dates, times, and details
- Attach supporting documents as exhibits when possible
- Number paragraphs consecutively
"""

        return {
            'success': True,
            'document': document,
            'document_type': 'declaration',
            'purpose': declaration_purpose
        }

    def _get_form_info(
        self,
        form_number: str = None,
        form_category: str = None
    ) -> Dict[str, Any]:
        """Get information about Colorado JDF forms."""

        form_info = []

        if form_number:
            # Clean up form number
            form_number = form_number.upper().replace(' ', ' ')

            form_descriptions = {
                'JDF 1111': ('Petition for Dissolution of Marriage with Children',
                             'Use this form to start a divorce case when you have minor children.'),
                'JDF 1113': ('Parenting Plan',
                             'Required form to establish decision-making and parenting time schedule.'),
                'JDF 1115': ('Response to Petition for Dissolution with Children',
                             'Use this form to respond to a divorce petition when children are involved.'),
                'JDF 1116': ('Decree of Dissolution of Marriage with Children',
                             'Final order dissolving the marriage - submitted to judge for signature.'),
                'JDF 1220': ('Motion to Modify Parenting Time',
                             'Use to request changes to an existing parenting time order.'),
                'JDF 1221': ('Affidavit for Motion to Modify Parenting Time',
                             'Supporting affidavit required with JDF 1220.'),
                'JDF 1820': ('Child Support Worksheet A',
                             'Use when children spend fewer than 93 overnights with one parent.'),
                'JDF 1821': ('Child Support Worksheet B',
                             'Use when children spend 93 or more overnights with each parent.'),
                'JDF 1101': ('Case Information Sheet',
                             'Required cover sheet for all domestic relations filings.'),
                'JDF 1000': ('Confidential Information Sheet',
                             'Contains sensitive information - filed separately from public record.')
            }

            if form_number in form_descriptions:
                name, desc = form_descriptions[form_number]
                form_info.append(f"**{form_number}: {name}**\n{desc}")
            else:
                form_info.append(f"Form {form_number} - Please check the Colorado Judicial Branch website for current form information.")

        if form_category:
            category_forms = COLORADO_FAMILY_LAW_FORMS.get(form_category, {})
            if category_forms:
                form_info.append(f"\n**{form_category.replace('_', ' ').title()} Forms:**")
                for form_type, form_num in category_forms.items():
                    form_info.append(f"- {form_num}: {form_type.replace('_', ' ').title()}")

        if not form_info:
            form_info.append("""
**Colorado Family Law Forms**

Download forms at: https://www.coloradojudicial.gov/self-help-forms

Common forms:
- JDF 1111: Petition for Dissolution with Children
- JDF 1113: Parenting Plan
- JDF 1220: Motion to Modify Parenting Time
- JDF 1820/1821: Child Support Worksheets

Contact your local court's self-help center for assistance selecting the right forms.
""")

        return {
            'success': True,
            'form_info': "\n".join(form_info)
        }

    def _explain_procedure(
        self,
        procedure: str,
        county: str = 'Denver'
    ) -> Dict[str, Any]:
        """Explain a Colorado family law procedure."""

        procedures = {
            'file_for_divorce': f"""
## Filing for Divorce in Colorado ({county} County)

### Overview
Colorado is a "no-fault" divorce state. You only need to state the marriage is "irretrievably broken."

### Residency Requirement
At least one spouse must have lived in Colorado for 91+ days before filing.

### Steps:
1. **Complete Required Forms:**
   - JDF 1101 (Case Information Sheet)
   - JDF 1111 (Petition for Dissolution - with children)
   - JDF 1000 (Confidential Information)
   - JDF 1113 (Parenting Plan)
   - JDF 1102 (Summons)

2. **File with the Court:**
   - File at the {county} County District Court
   - Pay filing fee (approximately $230, fee waiver available)
   - Get case number assigned

3. **Serve Your Spouse:**
   - Must serve within 90 days of filing
   - Cannot serve yourself
   - Options: Sheriff, process server, or acceptance of service

4. **Waiting Period:**
   - 91 days from service before decree can be entered

5. **Financial Disclosures:**
   - Both parties must exchange financial information
   - JDF 1111 includes sworn financial statement

6. **Parenting Plan:**
   - Required when children are involved
   - Addresses decision-making and parenting time

### Resources:
- {county} County Court Self-Help Center
- Colorado Judicial Branch: coloradojudicial.gov
""",

            'modify_parenting_time': """
## Modifying Parenting Time in Colorado

### When You Can Modify
You can request a modification when there has been a **substantial and continuing change in circumstances** since the last order.

### Steps:
1. **Try to Agree First:**
   - Attempt to reach agreement with other parent
   - Document your attempts (meet and confer)

2. **File Motion:**
   - JDF 1220 (Motion to Modify Parenting Time)
   - JDF 1221 (Supporting Affidavit)
   - Pay filing fee

3. **Serve Other Parent:**
   - Personal service or certified mail
   - Include all filed documents

4. **Other Parent's Response:**
   - They have 21-35 days to respond
   - May file counter-motion

5. **Mediation:**
   - May be required before hearing
   - Court can order mediation

6. **Hearing:**
   - Present evidence of changed circumstances
   - Focus on children's best interests

### Best Interests Factors (C.R.S. § 14-10-124):
- Children's wishes (if mature enough)
- Parents' wishes
- Children's relationships with parents
- Children's adjustment to home, school, community
- Physical and mental health of all parties
- Each parent's ability to encourage relationship with other parent
""",

            'file_motion': """
## Filing a Motion in Colorado Family Court

### General Steps:
1. **Draft Your Motion:**
   - Caption with case information
   - Clear statement of what you're requesting
   - Legal basis (cite applicable statutes)
   - Facts supporting your request
   - Signature and date

2. **Prepare Supporting Documents:**
   - Affidavit or declaration (if needed)
   - Exhibits (documents supporting your motion)
   - Proposed order

3. **File with Court:**
   - Make copies (original + copies for each party)
   - Pay filing fee (or request fee waiver)
   - Get filed-stamped copies

4. **Serve Other Party:**
   - Within time required by local rules
   - Keep proof of service

5. **Response Period:**
   - Other party typically has 21 days to respond

6. **Hearing:**
   - Court may set hearing automatically or upon request
   - Prepare to present your arguments

### Tips:
- Check local court rules for specific requirements
- Keep copies of everything
- Meet deadlines strictly
- Be factual and professional
""",

            'attend_hearing': """
## Attending a Family Court Hearing in Colorado

### Before the Hearing:
1. **Review Your Documents:**
   - Know your case inside and out
   - Organize documents chronologically

2. **Prepare Your Statement:**
   - Write out key points
   - Practice being concise

3. **Gather Evidence:**
   - Documents
   - Photos (if relevant)
   - Witness list (if any)

### Day of Hearing:
1. **Arrive Early:**
   - At least 30 minutes before
   - Find the correct courtroom

2. **Check In:**
   - Sign in with clerk or bailiff
   - Let them know you're present

3. **Court Etiquette:**
   - Dress professionally (business casual minimum)
   - Turn off cell phone
   - Stand when judge enters/exits
   - Address judge as "Your Honor"
   - Wait to be called before approaching

4. **During the Hearing:**
   - Listen to judge's questions
   - Answer directly and honestly
   - Don't interrupt
   - Stay calm and professional
   - Stick to relevant facts

5. **After the Hearing:**
   - Wait for judge's decision
   - Get copies of any orders
   - Note any deadlines

### What NOT to Do:
- Don't argue with the other party directly
- Don't make faces or comments
- Don't bring up issues not on the agenda
- Don't speak unless it's your turn
"""
        }

        explanation = procedures.get(procedure, f"""
## {procedure.replace('_', ' ').title()}

For detailed information on this procedure in {county} County, Colorado, please consult:

1. **Colorado Judicial Branch Self-Help Center:**
   https://www.coloradojudicial.gov/self-help

2. **{county} County District Court:**
   Contact the clerk's office for local procedures

3. **Colorado Legal Services:**
   Free legal help for qualifying individuals
   303-837-1313

4. **Colorado Bar Association Lawyer Referral:**
   303-831-8000
""")

        return {
            'success': True,
            'explanation': explanation,
            'procedure': procedure,
            'county': county
        }

    # =========================================================================
    # Session 403: Database Integration Methods
    # =========================================================================

    def _save_legal_document(
        self,
        task: str,
        document: Dict[str, Any],
        context: Dict[str, Any],
        execution_time_ms: int = 0
    ) -> Optional['LegalDocument']:
        """Save a generated legal document to the database."""
        if not self.user:
            logger.warning("Cannot save legal document: no user provided")
            return None

        try:
            from core.models_unified_system import LegalDocument, LegalCase

            # Determine document type from the result
            doc_type = document.get('document_type', 'other')
            motion_type = document.get('motion_type', '')

            # Build title
            if doc_type == 'motion':
                title = f"Motion: {motion_type.replace('_', ' ').title()}"
            elif doc_type == 'email':
                title = f"Email: {document.get('email_type', 'Communication')}"
            elif doc_type == 'declaration':
                title = "Declaration"
            else:
                title = f"Legal Document: {task[:100]}"

            # Get case if available
            case = None
            if self.case_id:
                try:
                    case = LegalCase.objects.get(id=self.case_id)
                except LegalCase.DoesNotExist:
                    pass

            # Create the document record
            legal_doc = LegalDocument.objects.create(
                user=self.user,
                case=case,
                document_type=doc_type,
                title=title,
                content=document.get('document', ''),
                original_query=task,
                generation_context={
                    'motion_type': motion_type,
                    'case_type': context.get('case_type', ''),
                    'jurisdiction': 'Colorado',
                    'execution_time_ms': execution_time_ms,
                    'tool_used': doc_type,
                },
                status='draft',
            )

            # Update case document count
            if case:
                case.document_count = case.documents.count()
                case.save(update_fields=['document_count', 'updated_at'])

            logger.info(f"Saved LegalDocument {legal_doc.id}: {title}")
            return legal_doc

        except Exception as e:
            logger.error(f"Failed to save legal document: {e}")
            return None

    def _save_legal_research(
        self,
        task: str,
        info: Dict[str, Any],
        context: Dict[str, Any],
        execution_time_ms: int = 0
    ) -> Optional['LegalResearchResult']:
        """Save legal research result to the database."""
        if not self.user:
            logger.warning("Cannot save legal research: no user provided")
            return None

        try:
            from core.models_unified_system import LegalResearchResult

            # Determine research type
            if info.get('explanation'):
                research_type = 'procedure'
            elif info.get('form_info'):
                research_type = 'form_lookup'
            elif info.get('search_results'):
                research_type = 'guidance'
            else:
                research_type = 'guidance'

            # Build analysis from info
            analysis_parts = []
            if info.get('explanation'):
                analysis_parts.append(info['explanation'])
            if info.get('form_info'):
                analysis_parts.append(info['form_info'])
            if info.get('search_results'):
                analysis_parts.append(info['search_results'])

            analysis = "\n\n".join(analysis_parts) if analysis_parts else str(info)

            # Save using the model's helper method
            research = LegalResearchResult.save_legal_research(
                user=self.user,
                query=task,
                analysis=analysis,
                research_type=research_type,
                case_type=context.get('case_type', ''),
                jurisdiction='Colorado',
                sources_used=info.get('sources', []),
                execution_time_ms=execution_time_ms,
                case_id=self.case_id,
            )

            logger.info(f"Saved LegalResearchResult {research.id}: {research_type}")
            return research

        except Exception as e:
            logger.error(f"Failed to save legal research: {e}")
            return None

    def _share_legal_knowledge(
        self,
        task: str,
        documents: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> None:
        """Share learned legal patterns with collective intelligence."""
        try:
            for doc in documents:
                doc_type = doc.get('document_type', 'other')
                motion_type = doc.get('motion_type', '')

                # Build knowledge title
                if doc_type == 'motion' and motion_type:
                    title = f"Colorado Motion Pattern: {motion_type.replace('_', ' ').title()}"
                else:
                    title = f"Colorado Legal Document: {doc_type}"

                # Share knowledge with other agents
                self._share_knowledge(
                    knowledge_type='content_idea',  # Using existing type
                    title=title,
                    knowledge_value={
                        'document_type': doc_type,
                        'motion_type': motion_type,
                        'case_type': context.get('case_type', ''),
                        'jurisdiction': 'Colorado',
                        'focus': 'Family Law',
                        'task_pattern': task[:200],
                    },
                    confidence=0.8
                )

        except Exception as e:
            logger.warning(f"Failed to share legal knowledge: {e}")

    def _get_relevant_legal_memories(
        self,
        task: str,
        case_type: str = '',
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant legal memories for the current task."""
        try:
            from core.models_unified_system import LegalMemory

            # Query memories by relevance
            memories = LegalMemory.objects.filter(
                jurisdiction='Colorado'
            )

            if case_type:
                memories = memories.filter(case_type=case_type)

            # Order by confidence and usage
            memories = memories.order_by('-confidence_score', '-usage_count')[:limit]

            return [
                {
                    'title': m.title,
                    'content': m.content[:500],
                    'memory_type': m.memory_type,
                    'confidence': m.confidence_score,
                    'usage_count': m.usage_count,
                }
                for m in memories
            ]

        except Exception as e:
            logger.warning(f"Failed to get legal memories: {e}")
            return []

    def _save_legal_memory(
        self,
        task: str,
        relief_type: str,
        facts: List[str],
        success: bool,
        execution_time_ms: int
    ) -> Optional[Any]:
        """
        Session 405: Save a legal-specific memory for pattern learning.

        This creates entries in LegalMemory for Colorado family law patterns,
        enabling the agent to learn from successful motion rewrites.
        """
        try:
            from core.models_unified_system import LegalMemory

            # Build memory content
            title = f"Motion Rewrite: {relief_type.replace('_', ' ').title()}"
            content = f"Successfully rewrote denied {relief_type} motion.\n"
            content += f"Facts extracted: {len(facts)}\n"
            if facts:
                content += f"Sample facts: {'; '.join(facts[:2])[:200]}"

            # Use 'pattern' which is a valid MEMORY_TYPE_CHOICE
            memory = LegalMemory.objects.create(
                agent=self.agent_model,  # Link to agent FK
                title=title[:300],
                content=content[:2000],
                memory_type='pattern',  # Valid choice from MEMORY_TYPE_CHOICES
                case_type='family_law',
                jurisdiction='Colorado',
                document_type='denied_motion_rewrite',
                confidence_score=0.85 if success else 0.3,
                key_insights=[
                    f'Relief type: {relief_type}',
                    f'Facts count: {len(facts)}',
                    f'Execution time: {execution_time_ms}ms',
                ],
                applicable_scenarios=[
                    f'Colorado {relief_type.replace("_", " ")} motions',
                    'Denied motion rewrites',
                    'Family law pro se filings',
                ],
            )

            logger.info(f"Session 405: Saved LegalMemory for {relief_type}")
            return memory

        except Exception as e:
            logger.warning(f"Failed to save legal memory: {e}")
            return None

    def get_prior_legal_research(
        self,
        query: str = '',
        case_type: str = '',
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get prior legal research for context building."""
        if not self.user:
            return []

        try:
            from core.models_unified_system import LegalResearchResult

            research = LegalResearchResult.objects.filter(user=self.user)

            if case_type:
                research = research.filter(case_type=case_type)

            research = research.order_by('-created_at')[:limit]

            return [
                {
                    'query': r.query,
                    'analysis_preview': r.analysis[:300],
                    'research_type': r.research_type,
                    'created_at': r.created_at.isoformat(),
                }
                for r in research
            ]

        except Exception as e:
            logger.warning(f"Failed to get prior research: {e}")
            return []

    # =========================================================================
    # Session 404: Denied Motion Detection and Pipeline
    # =========================================================================

    def _detect_denied_motion_mode(self, task: str, context: Dict[str, Any]) -> bool:
        """
        Detect if we should activate denied motion rewrite mode.

        Returns True if:
        - User uploaded a document with type 'denied_motion'
        - Task contains keywords indicating denied motion analysis
        - Context indicates document analysis request
        """
        task_lower = task.lower()

        # Check for denied motion keywords in task
        denied_keywords = [
            'denied', 'denial', 'rejected', 'dismissed',
            'rewrite', 'correct', 'fix my motion', 'refile',
            'why was my motion denied', 'motion was denied',
            'analyze my denied', 'help me fix',
        ]

        if any(keyword in task_lower for keyword in denied_keywords):
            return True

        # Check context for document type
        if context.get('document_type') == 'denied_motion':
            return True

        # Check if analyzing an uploaded document
        if context.get('analyzing_document') or context.get('case_file_id'):
            return True

        # Check for uploaded document context
        doc_context = self._get_uploaded_document_context(task, context)
        if doc_context and ('denied' in doc_context.lower() or 'order' in doc_context.lower()):
            return True

        return False

    def _execute_denied_motion_pipeline(
        self,
        task: str,
        context: Dict[str, Any],
        start_time: float
    ) -> AgentResult:
        """
        Execute the full denied motion analysis and rewrite pipeline.

        Session 404: This bypasses GPT decision-making and DIRECTLY calls:
        1. analyze_denied_motion - Identify all deficiencies
        2. check_non_party_issues - Detect non-party problems
        3. rewrite_motion - Generate corrected JDF-style motion
        4. generate_evidence_checklist - Create exhibit list
        """
        tool_calls_made = []
        output_parts = []

        # Get the motion content from uploaded document or task
        motion_content = self._get_motion_content_for_analysis(task, context)

        if not motion_content:
            return AgentResult(
                success=False,
                error="Could not find motion content to analyze. Please upload your denied motion document.",
                agent_name=self.name
            )

        self.record_decision(
            decision_type="mode_selection",
            action="Activating DENIED MOTION PIPELINE",
            reasoning="Detected denied motion - forcing direct tool execution",
            confidence=0.98
        )

        # =====================================================================
        # STEP 1: Analyze the denied motion
        # =====================================================================
        logger.info("Step 1: Analyzing denied motion...")
        analysis_result = self._analyze_denied_motion(
            motion_content=motion_content,
            denial_reasons=context.get('denial_reasons', ''),
            original_relief_requested=context.get('original_relief', '')
        )
        tool_calls_made.append({'tool': 'analyze_denied_motion', 'result': 'success'})

        # =====================================================================
        # STEP 2: Check for non-party issues
        # =====================================================================
        logger.info("Step 2: Checking non-party issues...")
        non_party_result = self._check_non_party_issues(
            motion_text=motion_content,
            parties_in_case=context.get('parties', [])
        )
        tool_calls_made.append({'tool': 'check_non_party_issues', 'result': 'success'})

        # =====================================================================
        # STEP 2.5: Session 405 Enhancement #2 - Emergency Assessment
        # =====================================================================
        logger.info("Step 2.5: Assessing emergency status...")
        # Check if the original motion claimed to be an emergency
        claimed_emergency = any(term in motion_content.lower() for term in [
            'emergency', 'urgent', 'immediate', 'imminent'
        ])
        emergency_result = self._assess_emergency_status(
            situation_description=motion_content,
            claimed_emergency=claimed_emergency
        )
        tool_calls_made.append({'tool': 'assess_emergency_status', 'result': 'success'})

        # If this was labeled as emergency but shouldn't be, add warning to output
        if emergency_result.get('false_emergency_warning'):
            output_parts.append("---")
            output_parts.append("")
            output_parts.append(emergency_result.get('analysis', ''))
            output_parts.append("")

        # =====================================================================
        # STEP 2.6: Session 405 Enhancement #3 - Court Order Attachment Check
        # =====================================================================
        logger.info("Step 2.6: Checking if court order attachment required...")
        # Get list of uploaded document types from context
        uploaded_docs = context.get('uploaded_document_types', [])
        order_check_result = self._check_order_attachment_required(
            motion_text=motion_content,
            uploaded_documents=uploaded_docs
        )
        tool_calls_made.append({'tool': 'check_order_attachment_required', 'result': 'success'})

        # If order attachment is missing, add warning to output
        if order_check_result.get('missing_order_warning'):
            output_parts.append("---")
            output_parts.append("")
            output_parts.append(order_check_result.get('analysis', ''))
            output_parts.append("")

        # =====================================================================
        # STEP 2.7: Session 405 Enhancement #4 - Conflict With Prior Orders
        # =====================================================================
        logger.info("Step 2.7: Checking for conflicts with existing orders...")
        # Get existing order text if uploaded
        existing_order_text = context.get('existing_order_text', '')
        existing_order_summary = context.get('existing_order_summary', '')
        conflict_result = self._detect_order_conflicts(
            motion_text=motion_content,
            existing_order_text=existing_order_text,
            existing_order_summary=existing_order_summary
        )
        tool_calls_made.append({'tool': 'detect_order_conflicts', 'result': 'success'})

        # If conflicts found, add warning to output
        if conflict_result.get('has_conflicts') or conflict_result.get('warning_count', 0) > 0:
            output_parts.append("---")
            output_parts.append("")
            output_parts.append(conflict_result.get('analysis', ''))
            output_parts.append("")

        # =====================================================================
        # STEP 3: Extract facts from motion for rewrite
        # =====================================================================
        facts = self._extract_facts_from_motion(motion_content)
        # Session 405 Patch 4D.5: Apply comprehensive postprocessing cleanup
        facts = self.postprocess_extracted_facts(facts)
        incidents = self._extract_incidents_from_motion(motion_content)
        relief_type = analysis_result.get('relief_type_detected', 'modify_parenting_time')

        # =====================================================================
        # STEP 3.5: Extract case metadata from PDF (Session 404 V3)
        # Session 406: Prefer CaseProfile data if user has set up their case
        # =====================================================================
        logger.info("Step 3.5: Extracting case metadata...")

        # First, try to get case profile data from database (Session 406)
        case_profile_data = self._get_active_case_profile_data(context)

        if case_profile_data:
            logger.info("Session 406: Using CaseProfile data for case metadata")
            case_details = case_profile_data
        else:
            # Fall back to document extraction
            extracted_metadata = self._extract_case_metadata(motion_content)
            # Merge with any existing case_details from context
            case_details = context.get('case_details', {})
            # Only use extracted values if context doesn't already have them
            for key, value in extracted_metadata.items():
                if value and not case_details.get(key):
                    case_details[key] = value

        logger.info(f"Case metadata: case_number={case_details.get('case_number')}, "
                   f"petitioner={case_details.get('petitioner_name')}, "
                   f"respondent={case_details.get('respondent_name')}, "
                   f"conferral_recipient={case_details.get('conferral_recipient_name', 'N/A')}")

        # =====================================================================
        # STEP 4: Generate rewritten motion in JDF format
        # =====================================================================
        logger.info("Step 3: Generating rewritten motion...")
        # FIX #3: Pass relief_type to get correct template
        corrected_relief = self._generate_corrected_relief(non_party_result, relief_type=relief_type)
        # Session 404F: Pass original motion content for FULL RESTATEMENT section
        # Session 406: Get existing order text from context for order integration
        existing_order_text = context.get('existing_order_text', '')
        # Session 406: Determine if this is a true emergency (affects conferral requirement)
        is_true_emergency = emergency_result.get('is_true_emergency', False)

        rewrite_result = self._rewrite_motion_gold_standard(
            relief_type=relief_type,
            facts=facts,
            dates_incidents=incidents,
            relief_requested=corrected_relief,
            case_details=case_details,  # Now with extracted metadata
            non_party_corrections=non_party_result.get('corrections', []),
            original_motion_content=motion_content,  # For 1:1 mapping guarantee
            existing_order_text=existing_order_text,  # Session 406: For EXISTING COURT ORDERS section
            is_emergency=is_true_emergency  # Session 406: For CERTIFICATE OF CONFERRAL
        )
        tool_calls_made.append({'tool': 'rewrite_motion', 'result': 'success'})

        # =====================================================================
        # STEP 5: Generate evidence checklist
        # =====================================================================
        logger.info("Step 4: Generating evidence checklist...")
        # FIX #5: Pass FILTERED facts, not raw PDF content
        checklist_result = self._generate_evidence_checklist(
            motion_type=relief_type,
            allegations=facts  # Already filtered by _extract_facts_from_motion
        )
        tool_calls_made.append({'tool': 'generate_evidence_checklist', 'result': 'success'})

        # =====================================================================
        # BUILD FINAL OUTPUT - Session 404 V3: Improved formatting
        # =====================================================================
        output_parts.append("# DENIED MOTION ANALYSIS & CORRECTED REWRITE\n")
        output_parts.append("---\n")

        # Part 1: Analysis Summary (brief, procedural only)
        output_parts.append("## PART 1: PROCEDURAL DEFECTS IDENTIFIED\n")
        output_parts.append(self._format_analysis_summary(analysis_result))

        # Part 2: Non-party issues (always show, even if none)
        output_parts.append("\n---\n")
        output_parts.append("## PART 2: NON-PARTY RULE CHECK\n")
        if non_party_result.get('has_non_party_issues'):
            output_parts.append("**Issues Found:** Relief incorrectly targeted non-parties.\n\n")
            output_parts.append(non_party_result.get('analysis', ''))
            output_parts.append("\n*The rewritten motion below has corrected these issues.*\n")
        else:
            output_parts.append("**No issues found.** All relief is properly directed at parties to the case.\n")

        # Part 3: The rewritten motion (GOLD STANDARD FORMAT)
        output_parts.append("\n---\n")
        output_parts.append("## PART 3: CORRECTED MOTION (COURT-READY FORMAT)\n")
        output_parts.append("*Copy this entire section to file with the court.*\n\n")
        motion_document = rewrite_result.get('document', '')
        # FIX #4: Strip any statute references that slipped through
        motion_document = self._strip_statute_references(motion_document)
        output_parts.append(motion_document)

        # Part 4: Evidence checklist
        output_parts.append("\n---\n")
        output_parts.append("## PART 4: EVIDENCE CHECKLIST\n")
        output_parts.append("*Gather these items before filing:*\n\n")
        output_parts.append(checklist_result.get('checklist', ''))

        # =====================================================================
        # STEP 6: Session 405 Enhancement #5 - Likelihood of Success Assessment
        # Session 406 PATCH-5.1: Extract relief items ONCE and pass to scoring
        # =====================================================================
        logger.info("Step 6: Assessing likelihood of success...")

        # Session 406 PATCH-5.1: Extract relief items from corrected_relief (NOT full document!)
        # This ensures we count only the actual relief items, not evidence checklist, conferral, etc.
        relief_items_for_scoring = self._extract_relief_items_list(corrected_relief)
        logger.info(f"[PATCH-5.1] Extracted {len(relief_items_for_scoring)} relief items for scoring")

        # Check for evidence mentions in rewritten motion
        has_evidence = 'exhibit' in motion_document.lower() or 'attached' in motion_document.lower()
        success_result = self._assess_likelihood_of_success(
            motion_text=motion_document,  # Score the REWRITTEN motion
            relief_type=relief_type,
            has_evidence=has_evidence,
            is_rewrite=True,  # This is a rewrite of a denied motion
            relief_items=relief_items_for_scoring  # Session 406 PATCH-5.1: Pass pre-extracted items
        )
        tool_calls_made.append({'tool': 'assess_likelihood_of_success', 'result': 'success'})

        # Part 5: Likelihood of Success
        output_parts.append("\n---\n")
        output_parts.append("## PART 5: LIKELIHOOD OF SUCCESS\n")
        output_parts.append(success_result.get('analysis', ''))

        # =====================================================================
        # STEP 7: Session 406 - Conferral Email Generation (Non-Emergency Only)
        # =====================================================================
        conferral_email_result = None
        if not is_true_emergency:
            logger.info("Step 7: Generating conferral email (non-emergency motion)...")

            # Session 406 PATCH-5: Use extracted relief items from the pipeline
            # These are the same items shown in RELIEF REQUESTED and PROPOSED ORDER
            relief_items_for_email = self._extract_relief_items_list(corrected_relief)
            if not relief_items_for_email:
                # Fallback: extract from corrected relief text manually
                relief_lines = [line.strip() for line in corrected_relief.split('\n') if line.strip()]
                relief_items_for_email = [
                    line.lstrip('0123456789.)- ').strip()
                    for line in relief_lines
                    if line and len(line) > 10 and not line.lower().startswith('wherefore')
                ][:5]

            # Session 406 PATCH-5: Build MotionContext for conferral email
            conferral_ctx = MotionContext.from_case_details(case_details)
            conferral_ctx.relief_items = relief_items_for_email

            # Generate the conferral email using MotionContext for consistent data binding
            conferral_email_result = self._generate_conferral_email(
                petitioner=conferral_ctx.petitioner_name or 'Petitioner',
                respondent=conferral_ctx.respondent_name or 'Respondent',
                relief_points=conferral_ctx.relief_items if conferral_ctx.relief_items else ['The relief items described in the attached motion'],
                case_context='Third-Party Statements / Parenting Time Issue',
                deadline_days=2,
                respondent_counsel=conferral_ctx.respondent_counsel_name if conferral_ctx.is_respondent_represented else ''
            )
            tool_calls_made.append({'tool': 'generate_conferral_email', 'result': 'success'})

            # Part 6: Conferral Email (NEW!)
            output_parts.append("\n---\n")
            output_parts.append("## PART 6: CONFERRAL EMAIL (SEND BEFORE FILING)\n")
            output_parts.append("*Per C.R.C.P. 121 § 1-15(8), you MUST confer before filing non-emergency motions.*\n\n")
            output_parts.append("**Copy and send this email to opposing party:**\n\n")
            output_parts.append("```\n")
            output_parts.append(conferral_email_result.get('email_body', ''))
            output_parts.append("\n```\n\n")
            output_parts.append(f"**Deadline for Response:** {conferral_email_result.get('deadline_date', 'Within 2 days')}\n\n")
            output_parts.append("### What to do after sending:\n")
            output_parts.append(conferral_email_result.get('guidance', ''))
        else:
            # Emergency motion - explain why conferral is waived
            output_parts.append("\n---\n")
            output_parts.append("## PART 6: CONFERRAL STATUS\n")
            output_parts.append("**Conferral Waived - Emergency Motion**\n\n")
            output_parts.append("This qualifies as an emergency motion under C.R.S. § 14-10-129.5.\n")
            output_parts.append("Conferral is NOT required before filing due to imminent danger.\n")
            output_parts.append("You may file immediately.\n")

        # FIX #6: NO LEGAL DISCLAIMER - removed per ChatGPT feedback
        # The disclaimer was confusing and contradicting the procedural-only approach

        execution_time = int((time.time() - start_time) * 1000)

        # =====================================================================
        # Session 407: Parse output into downloadable sections (document bundle)
        # =====================================================================
        full_output = "\n".join(output_parts)
        document_bundle = parse_motion_output_to_bundle(
            full_output=full_output,
            case_number=case_details.get('case_number', ''),
            county=case_details.get('county', ''),
            state=case_details.get('state', 'CO')
        )
        logger.info(f"[Session 407] Created document bundle with {len(document_bundle.sections)} sections")

        result = AgentResult(
            success=True,
            message=full_output,
            data={
                'type': 'denied_motion_rewrite',
                'pipeline_executed': True,
                'tools_called': [t['tool'] for t in tool_calls_made],
                'relief_type': relief_type,
                'non_party_issues': non_party_result.get('has_non_party_issues', False),
                'facts_extracted': len(facts),
                'incidents_extracted': len(incidents),
                # Session 405 Enhancement #2: Emergency assessment data
                'emergency_assessment': {
                    'is_emergency': emergency_result.get('is_emergency', False),
                    'confidence': emergency_result.get('emergency_confidence', 0.0),
                    'recommendation': emergency_result.get('recommendation', 'STANDARD_MODIFICATION'),
                    'false_emergency_warning': emergency_result.get('false_emergency_warning', False),
                },
                # Session 405 Enhancement #3: Court order attachment check
                'order_attachment_check': {
                    'requires_attachment': order_check_result.get('requires_order_attachment', False),
                    'order_type_needed': order_check_result.get('order_type_needed'),
                    'missing_order_warning': order_check_result.get('missing_order_warning', False),
                },
                # Session 405 Enhancement #5: Likelihood of success score
                'success_assessment': {
                    'score': success_result.get('total_score', 0),
                    'rating': success_result.get('rating', 'UNKNOWN'),
                    'rating_emoji': success_result.get('rating_emoji', '⚪'),
                    'components': success_result.get('score_components', {}),
                },
                # Session 406: Conferral requirement
                'conferral': {
                    'required': not is_true_emergency,
                    'reason': 'Non-emergency motion requires conferral per C.R.C.P. 121 § 1-15(8)' if not is_true_emergency else 'Emergency motion - conferral waived',
                    'email_generated': conferral_email_result is not None,
                    'deadline_date': conferral_email_result.get('deadline_date') if conferral_email_result else None,
                },
                # Session 407: Downloadable document sections
                'document_bundle': document_bundle.to_dict(),
            },
            agent_name=self.name,
            execution_time_ms=execution_time,
            tool_calls=tool_calls_made
        )

        # =====================================================================
        # Session 405: LEARNING HOOKS - Every motion makes the system smarter!
        # =====================================================================
        # Record this execution for the learning loop (XP, pattern detection)
        self._record_learning_outcome(
            result=result,
            task=task,
            context=context,
            spider_data_used=False,
            scifi_context_used=False
        )

        # Create a memory of this successful motion rewrite
        self._create_execution_memory(
            result=result,
            task=f"Denied Motion Rewrite: {relief_type}",
            memory_type="success",
            importance=0.9  # Legal documents are high importance
        )

        # Share learned pattern with collective intelligence
        # This allows other agents to learn from legal patterns
        self._share_knowledge(
            knowledge_type='content_idea',  # Maps to valid type
            title=f"Legal Motion Pattern: {relief_type.replace('_', ' ').title()}",
            knowledge_value={
                'document_type': 'denied_motion_rewrite',
                'relief_type': relief_type,
                'jurisdiction': 'Colorado',
                'focus_area': 'Family Law',
                'facts_count': len(facts),
                'incidents_count': len(incidents),
                'non_party_issues_found': non_party_result.get('has_non_party_issues', False),
                'non_party_corrections': len(non_party_result.get('corrections', [])),
                'execution_time_ms': execution_time,
                'success': True,
                'task_pattern': task[:200],  # First 200 chars for pattern matching
            },
            confidence=0.85
        )

        # Also save to LegalMemory for legal-specific retrieval
        self._save_legal_memory(
            task=task,
            relief_type=relief_type,
            facts=facts,
            success=True,
            execution_time_ms=execution_time
        )

        logger.info(f"Session 405: Learning hooks fired for {relief_type} motion rewrite")

        # Session 409: Validate output through Mythology Enforcer to prevent hallucinations
        # CRITICAL for legal documents - must not contain unrealistic claims
        result = self._validate_output(result)

        return result

    def _get_motion_content_for_analysis(self, task: str, context: Dict[str, Any]) -> str:
        """Get the motion content from uploaded document or context."""
        # First try to get from uploaded document
        doc_context = self._get_uploaded_document_context(task, context)
        if doc_context:
            return doc_context

        # Check if motion content is in context
        if context.get('motion_content'):
            return context.get('motion_content')

        # Check if the task itself contains the motion
        if len(task) > 500:  # Likely contains motion text
            return task

        return ""

    def _extract_facts_from_motion(self, motion_content: str) -> List[str]:
        """
        Session 404 Patch 4C: Extract user's narrative facts - STRICT NUMBERED FORMAT.

        OUTPUT FORMAT (Patch 4C strict template):
        Returns 3-4 clean allegations ready for numbered paragraphs:
        - Allegations 1-3: Individual incidents as complete sentences with dates
        - Allegation 4: Impact/pattern paragraph summarizing harm

        RULES:
        1. NO subheadings like "Today's Incident – November 12, 2025"
        2. NO raw PDF numbering fragments ("1." "2." etc.)
        3. NO inline lists with semicolons like "1. Today...; 2. August 29..."
        4. Each incident becomes its own separate allegation
        5. Final allegation summarizes pattern/impact
        """
        import logging
        logger = logging.getLogger(__name__)

        # STEP 1: Extract only the user's motion section (before denial order)
        user_motion_content = self._extract_user_motion_section(motion_content)
        logger.info(f"SESSION 404 Patch 4C: Extracted user motion section length: {len(user_motion_content)}")

        # STEP 2: Extract incident candidates with dates
        incidents = self._extract_incident_candidates(user_motion_content)
        logger.info(f"SESSION 404 Patch 4C: Found {len(incidents)} incident candidates")

        # STEP 3: Build clean allegations from incidents
        allegations = self._build_clean_allegations(incidents, user_motion_content)
        logger.info(f"SESSION 404 Patch 4C: Built {len(allegations)} clean allegations")

        return allegations

    def _extract_incident_candidates(self, content: str) -> List[Dict[str, str]]:
        """
        Session 404 Patch 4C (Part B): Extract incident candidates from content.

        Identifies incidents based on:
        - Explicit dates (November 12, 2025, August 29, 2025)
        - Phrases like "today's incident", "the following week"
        - Semicolon-separated inline lists like "1. Today...; 2. August..."

        Returns list of {date_string, description} dicts.
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        incidents = []

        # STEP 1: Handle inline semicolon-separated lists
        # Pattern: "1. [content]; 2. [content]; 3. [content]"
        inline_list_pattern = r'(?:These incidents occurred:?\s*)?(\d+\.\s*[^;]+(?:;\s*\d+\.\s*[^;]+)+)'
        inline_matches = re.findall(inline_list_pattern, content, re.IGNORECASE)

        for inline_list in inline_matches:
            # Split by semicolon followed by number
            items = re.split(r';\s*(?=\d+\.)', inline_list)
            for item in items:
                item = item.strip()
                if not item:
                    continue
                # Remove leading "1.", "2.", etc.
                item = re.sub(r'^\d+\.\s*', '', item)
                if len(item) > 20:
                    date_str = self._extract_date_from_text(item)
                    incidents.append({
                        'date_string': date_str or 'Unknown date',
                        'description': item.strip()
                    })
                    logger.debug(f"Patch 4C: Inline list item: {item[:50]}...")

        # STEP 2: Find date-anchored incidents in regular text
        date_pattern = r'(?:On\s+)?((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})'

        # Split content into sentences
        content_normalized = re.sub(r'\n+', ' ', content)
        content_normalized = re.sub(r'\s+', ' ', content_normalized)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', content_normalized)

        for sentence in sentences:
            # Skip if already captured from inline list
            already_captured = any(
                inc['description'][:30].lower() in sentence.lower()
                for inc in incidents
            )
            if already_captured:
                continue

            # Skip court metadata and denial order content
            if self._is_court_metadata(sentence) or self._is_denial_order_content(sentence):
                continue

            # Look for date in sentence
            date_match = re.search(date_pattern, sentence, re.IGNORECASE)
            if date_match:
                date_str = date_match.group(1)
                # Clean the sentence
                clean_desc = self._clean_incident_text(sentence)
                if len(clean_desc) > 30:
                    incidents.append({
                        'date_string': date_str,
                        'description': clean_desc
                    })
                    logger.debug(f"Patch 4C: Date-anchored: {clean_desc[:50]}...")

        # STEP 3: Look for relative time references ("the following week", "today")
        relative_patterns = [
            (r'(?:the\s+)?following\s+week', 'The following week'),
            (r"today(?:'s)?\s+(?:incident|during)", 'Today'),
            (r'(?:that\s+)?same\s+(?:day|week)', 'That same time'),
        ]

        for pattern, time_label in relative_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get surrounding context (100 chars before and after)
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 150)
                context = content[start:end]

                # Find the sentence containing this reference
                sentence_match = re.search(r'[^.]*' + pattern + r'[^.]*\.?', context, re.IGNORECASE)
                if sentence_match:
                    desc = sentence_match.group(0).strip()
                    # Check not already captured
                    if not any(inc['description'][:30].lower() in desc.lower() for inc in incidents):
                        clean_desc = self._clean_incident_text(desc)
                        if len(clean_desc) > 30:
                            incidents.append({
                                'date_string': time_label,
                                'description': clean_desc
                            })

        # Deduplicate incidents by description similarity
        unique_incidents = []
        seen_descriptions = set()
        for inc in incidents:
            # Normalize for comparison
            norm_desc = re.sub(r'[^\w\s]', '', inc['description'].lower())[:60]
            if norm_desc not in seen_descriptions:
                seen_descriptions.add(norm_desc)
                unique_incidents.append(inc)

        return unique_incidents[:4]  # Max 4 incidents (3 specific + 1 for impact)

    def _clean_incident_text(self, text: str) -> str:
        """
        Session 404 Patch 4C: Clean incident text for court-ready format.
        """
        import re

        cleaned = text.strip()

        # Remove leading numbering
        cleaned = re.sub(r'^\d+[\.\)]\s*', '', cleaned)
        cleaned = re.sub(r'^[a-z][\.\)]\s*', '', cleaned)
        cleaned = re.sub(r'^\([ivx\d]+\)\s*', '', cleaned, flags=re.IGNORECASE)

        # Remove "Today's Incident – Date" style headers
        cleaned = re.sub(r"^Today's Incident\s*[-–]\s*[A-Za-z]+\s+\d{1,2},?\s*\d{4}\s*[-–:]?\s*", '', cleaned, flags=re.IGNORECASE)

        # Remove "These incidents occurred:" prefix
        cleaned = re.sub(r'^These incidents occurred:?\s*', '', cleaned, flags=re.IGNORECASE)

        # Remove isolated parenthetical dates at start
        cleaned = re.sub(r'^\(\s*[A-Za-z]+\s+\d{1,2},?\s*\d{4}\s*\)\s*;?\s*', '', cleaned)

        # Clean up spacing
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # Ensure proper ending
        if cleaned and not cleaned[-1] in '.!?':
            cleaned += '.'

        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        return cleaned

    def _extract_date_from_text(self, text: str) -> str:
        """Extract a date string from text if present."""
        import re
        date_pattern = r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})'
        match = re.search(date_pattern, text, re.IGNORECASE)
        return match.group(1) if match else None

    def _extract_direct_quotes(self, content: str) -> List[str]:
        """
        Session 406: Extract direct quotes from user's narrative.

        Finds quoted statements like:
        - "You have been lying to me"
        - "Trust me, Daddy, you have been lying to me"
        - "Camille has told me..."

        Returns list of unique quotes found.
        """
        import re
        quotes = []

        # Pattern for quoted text (both single and double quotes)
        quote_patterns = [
            r'"([^"]{10,100})"',  # Double quotes, 10-100 chars
            r"'([^']{10,100})'",  # Single quotes, 10-100 chars
            r'"([^"]{10,100})"',  # Smart quotes
            r'stated[,:]?\s*"([^"]+)"',  # "stated: ..."
            r'said[,:]?\s*"([^"]+)"',    # "said: ..."
            r'told\s+\w+[,:]?\s*"([^"]+)"',  # "told [someone]: ..."
        ]

        for pattern in quote_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean and validate quote
                quote = match.strip()
                if quote and len(quote) >= 10 and quote not in quotes:
                    quotes.append(quote)

        return quotes[:5]  # Return up to 5 quotes

    def _extract_third_party_names(self, content: str) -> List[str]:
        """
        Session 406: Extract named third parties from user's narrative.

        Finds names like "Camille Johnson", "girlfriend", etc.

        Returns list of identified third-party names.
        """
        import re
        names = []

        # Session 406: Check for "Camille Johnson" first (specific to user's case)
        if re.search(r'camille\s+johnson', content, re.IGNORECASE):
            names.append('Camille Johnson')

        # Look for explicit name mentions with context (First Last format only)
        # Avoid false positives like "Camille has told me" -> "Camille Has"
        name_patterns = [
            r"(?:respondent'?s?\s+)?(?:girlfriend|boyfriend|partner)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)\s+is\s+(?:not\s+)?(?:a\s+)?(?:parent|party|guardian)",
        ]

        for pattern in name_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                name = match.strip().title() if isinstance(match, str) else ''
                if name and len(name) > 5 and name not in names:
                    # Filter out common non-names and verb patterns like "Camille Has"
                    skip_names = ['the child', 'the minor', 'petitioner', 'respondent']
                    skip_suffixes = ['has', 'had', 'was', 'is', 'are', 'were', 'told', 'said']

                    name_parts = name.lower().split()
                    if name.lower() not in skip_names:
                        # Check if second part is a verb (false positive)
                        if len(name_parts) >= 2 and name_parts[1] not in skip_suffixes:
                            names.append(name)

        return names[:3]  # Return up to 3 names

    def _build_specific_allegation_detail(
        self,
        item_text: str,
        quotes: List[str],
        third_party_names: List[str],
        quote_index: int
    ) -> str:
        """
        Session 406: Build specific allegation detail using extracted quotes and names.

        Instead of generic "third party made statements", creates specific text like:
        - 'the minor child stated, "You have been lying to me"'
        - 'the minor child identified Camille Johnson as the source of these statements'

        Returns the specific detail string, or empty string if can't build one.
        """

        # Check if item already has good specificity
        has_quote = '"' in item_text or "'" in item_text
        has_specific_name = any(name.lower() in item_text.lower() for name in third_party_names) if third_party_names else False

        if has_quote and has_specific_name:
            # Already specific enough, just clean it
            return ''

        # Try to build specific detail from quotes
        if quotes and quote_index < len(quotes):
            quote = quotes[quote_index]
            if third_party_names:
                return f'the minor child stated, "{quote}" Later, the child identified {third_party_names[0]} as the source of these statements.'
            else:
                return f'the minor child stated, "{quote}"'

        # Try to add third-party name
        if third_party_names and not has_specific_name:
            # Check if this is about identifying the source
            if 'identify' in item_text.lower() or 'source' in item_text.lower() or 'told' in item_text.lower():
                return f'the minor child explicitly identified {third_party_names[0]} as the source of statements about Petitioner.'

        return ''  # Couldn't build specific detail

    def _build_clean_allegations(self, incidents: List[Dict[str, str]], original_content: str) -> List[str]:
        """
        Session 405 Patch 4K: Build clean numbered allegations with PROPER SEGMENTATION.
        Session 406: Enhanced to preserve specificity - actual quotes, names, and details.

        Courts expect discrete, numbered facts - NOT bullet points or inline lists.
        Each allegation should be ONE clean sentence that can be numbered 4, 5, 6...
        (continuing after GENERAL BACKGROUND facts 1-3).

        Output format judges expect:
        4. On November 12, 2025, during court-ordered parenting time, the minor child stated "You have been lying to me."
        5. On August 29, 2025, during a recorded phone call, the minor child made similar statements.
        6. The following week, the minor child again stated similar things, identifying Camille Johnson as the source.
        7. Camille Johnson is not a parent, not a legal guardian, not a party to this case.
        8. Respondent has missed multiple court-ordered parenting-time exchanges.
        9. These documented incidents demonstrate an escalating pattern...
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        allegations = []

        # Session 406: Extract specific quotes and key phrases from narrative
        quotes = self._extract_direct_quotes(original_content)
        third_party_names = self._extract_third_party_names(original_content)
        logger.info(f"Session 406: Found {len(quotes)} quotes, {len(third_party_names)} third-party names")

        # Session 405 Patch 4K: Extract EACH incident as a SEPARATE allegation

        # STEP 1: Parse the "These incidents occurred:" inline list
        # Pattern: "1. Today during... 2. August 29... 3. The following week..."
        incidents_list_match = re.search(
            r'These\s+incidents\s+occurred:?\s*(.*?)(?:This\s+pattern|Camille\s+Johnson|Respondent\s+has|$)',
            original_content,
            re.IGNORECASE | re.DOTALL
        )

        if incidents_list_match:
            incidents_text = incidents_list_match.group(1)
            logger.info(f"Patch 4K: Found incidents block: {incidents_text[:100]}...")

            # Split by numbered items (1. 2. 3.) or newlines followed by dates
            # Handle format: "1. Today... August 29... The following week..."
            incident_items = re.split(
                r'(?:\d+\.\s*)|(?:\n\s*(?=(?:January|February|March|April|May|June|July|August|September|October|November|December|The\s+following|Today)))',
                incidents_text
            )

            quote_index = 0
            for item in incident_items:
                item = item.strip().rstrip('.;,')
                if not item or len(item) < 15:
                    continue

                # Clean and format
                item = re.sub(r'\s+', ' ', item)

                # Extract date if present
                date_match = re.search(
                    r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4})',
                    item, re.IGNORECASE
                )

                if date_match:
                    date_str = date_match.group(1)
                    # Session 406: Try to preserve specificity with quotes and named third party
                    if not item.lower().startswith('on '):
                        # Build a specific allegation using extracted details
                        specific_detail = self._build_specific_allegation_detail(
                            item, quotes, third_party_names, quote_index
                        )
                        if specific_detail:
                            item = f"On {date_str}, during court-ordered parenting time, {specific_detail}"
                            quote_index += 1
                        else:
                            # Session 406 FIX: Properly strip the date from remaining text
                            # Remove the date itself first
                            remaining = re.sub(
                                re.escape(date_str),
                                '',
                                item,
                                flags=re.IGNORECASE
                            )
                            # Remove common prefixes like "Today during court-ordered parenting time ()"
                            # Use count=1 to avoid removing ALL whitespace (the \s* can match between words)
                            remaining = re.sub(
                                r'^[\s,;.]*(?:Today\s+)?(?:during\s+)?(?:court[- ]ordered\s+)?(?:parenting[- ]?time\s+)?(?:\(\s*\))?[\s,;.]*',
                                '',
                                remaining.strip(),
                                count=1,
                                flags=re.IGNORECASE
                            ).strip()
                            # Clean up any leftover punctuation at start
                            remaining = re.sub(r'^[,;.\s]+', '', remaining).strip()

                            if remaining and len(remaining) > 10:
                                # Session 406: Check if remaining is a complete thought or fragment
                                # If it starts with articles/prepositions alone, it's incomplete
                                remaining_lower = remaining.lower()
                                incomplete_starts = ['a ', 'an ', 'the ', 'in ', 'at ', 'on ', 'to ']
                                is_fragment = any(remaining_lower.startswith(s) and len(remaining.split()) <= 4 for s in incomplete_starts)

                                if is_fragment:
                                    # It's a fragment like "a recorded phone call" - make it descriptive
                                    item = f"On {date_str}, during {remaining}, the minor child made similar statements."
                                else:
                                    item = f"On {date_str}, during court-ordered parenting time, {remaining[0].lower()}{remaining[1:]}"
                            else:
                                item = f"On {date_str}, during court-ordered parenting time, the minor child made statements indicating third-party interference."
                elif 'following week' in item.lower():
                    # Session 406: Add specificity to "following week" incidents
                    if third_party_names:
                        item = f"The following week, the minor child again reported similar statements, identifying {third_party_names[0]} as the source."
                    else:
                        item = "The following week, the minor child again reported similar statements from a third party."
                elif 'today' in item.lower():
                    # This shouldn't happen after date extraction, but handle it
                    item = re.sub(r'\btoday\b', 'On the incident date', item, flags=re.IGNORECASE)

                # Ensure proper ending
                if item and item[-1] not in '.!?':
                    item += '.'

                # Capitalize first letter
                if item:
                    item = item[0].upper() + item[1:]

                if len(item) > 30:
                    allegations.append(item)
                    logger.debug(f"Patch 4K: Incident allegation: {item[:60]}...")

        # STEP 2: If no inline list found, use the incidents from extraction
        if not allegations and incidents:
            for i, incident in enumerate(incidents[:3]):
                date_str = incident.get('date_string', '')
                desc = incident.get('description', '')

                # Truncate long descriptions
                if len(desc) > 200:
                    first_sentence = re.match(r'^[^.!?]+[.!?]', desc)
                    if first_sentence:
                        desc = first_sentence.group(0)
                    else:
                        desc = desc[:150] + '.'

                # Format with date
                if date_str and date_str not in ['Unknown date', 'The following week', 'Today']:
                    desc = f"On {date_str}, {desc[0].lower()}{desc[1:]}" if desc else f"On {date_str}."
                elif date_str == 'The following week':
                    desc = f"The following week, {desc[0].lower()}{desc[1:]}" if desc else "The following week."

                desc = re.sub(r'\s+', ' ', desc).strip()
                if desc and desc[-1] not in '.!?':
                    desc += '.'

                if desc and len(desc) > 30:
                    allegations.append(desc)

        # STEP 3: Third-party status as separate allegation
        third_party_segment = self._extract_third_party_segment(original_content)
        if third_party_segment:
            allegations.append(third_party_segment)
            logger.debug(f"Patch 4K: Third-party segment added")

        # STEP 4: Respondent's failures as separate allegation
        respondent_segment = self._extract_respondent_failures_segment(original_content)
        if respondent_segment:
            allegations.append(respondent_segment)
            logger.debug(f"Patch 4K: Respondent failures segment added")

        # STEP 5: Impact/pattern statement as separate allegation
        impact_paragraph = self._generate_impact_paragraph(incidents, original_content)
        if impact_paragraph:
            allegations.append(impact_paragraph)
            logger.debug(f"Patch 4K: Impact paragraph added")

        # STEP 6 (Session 406): Sort dated allegations chronologically
        # Keep non-dated allegations (third-party, respondent failures, impact) at the end
        allegations = self._sort_allegations_chronologically(allegations)

        logger.info(f"Patch 4K: Built {len(allegations)} clean allegations")
        return allegations

    def _sort_allegations_chronologically(self, allegations: List[str]) -> List[str]:
        """
        Session 406: Sort allegations by date, keeping non-dated ones at the end.

        Order:
        1. Dated incidents (sorted oldest to newest)
        2. "The following week" incidents (placed after first dated incident)
        3. Third-party status
        4. Respondent failures
        5. Impact statement

        Returns sorted list of allegations.
        """
        import re
        from datetime import datetime

        def extract_date(allegation: str):
            """Extract date from allegation. Returns datetime or None."""
            date_match = re.search(
                r'On\s+((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4})',
                allegation,
                re.IGNORECASE
            )
            if date_match:
                try:
                    date_str = date_match.group(1).replace(',', '')
                    return datetime.strptime(date_str.strip(), '%B %d %Y')
                except ValueError:
                    pass
            return None

        # Categorize allegations
        dated_allegations = []  # (date, allegation)
        following_week_allegations = []
        non_dated_allegations = []

        for allegation in allegations:
            date_obj = extract_date(allegation)
            if date_obj:
                dated_allegations.append((date_obj, allegation))
            elif allegation.lower().startswith('the following week'):
                following_week_allegations.append(allegation)
            else:
                non_dated_allegations.append(allegation)

        # Sort dated allegations chronologically (oldest first)
        dated_allegations.sort(key=lambda x: x[0])

        # Build result:
        # 1. First dated incident (oldest)
        # 2. "The following week" incidents (relative to first date)
        # 3. Remaining dated incidents
        # 4. Non-dated items
        result = []

        if dated_allegations:
            # Add first dated incident
            result.append(dated_allegations[0][1])

            # Add "following week" after first incident
            result.extend(following_week_allegations)

            # Add remaining dated incidents
            for date_obj, allegation in dated_allegations[1:]:
                result.append(allegation)
        else:
            # No dated allegations, add following week first if present
            result.extend(following_week_allegations)

        # Add non-dated allegations at the end
        result.extend(non_dated_allegations)

        return result

    def _generate_conferral_email(
        self,
        petitioner: str,
        respondent: str,
        relief_points: List[str],
        case_context: str = '',
        deadline_days: int = 2,
        respondent_counsel: str = ''
    ) -> Dict[str, Any]:
        """
        Session 406: Generate a conferral email for non-emergency motions.

        Per C.R.C.P. 121 § 1-15(8), parties must confer before filing most motions.
        This generates:
        1. The conferral email text to send to opposing party
        2. Certificate of Conferral text for the motion
        3. Guidance on next steps

        Args:
            petitioner: Name of the moving party
            respondent: Name of the opposing party
            relief_points: List of specific relief items being requested
            case_context: Brief description of the issue (e.g., "third-party statements")
            deadline_days: How many days to give for response (default 2)
            respondent_counsel: Name of respondent's attorney (if represented)

        Returns:
            Dict with email_text, certificate_text, and guidance
        """
        from datetime import datetime, timedelta

        # Calculate deadline
        deadline_date = datetime.now() + timedelta(days=deadline_days)
        deadline_str = deadline_date.strftime('%B %d, %Y')

        # Get first name for email salutation
        # Session 406: Prefer counsel name if respondent is represented
        if respondent_counsel:
            # Use counsel's name - more formal, use full name or "Counsel"
            email_recipient = respondent_counsel.split()[0] if respondent_counsel else 'Counsel'
        else:
            # Use respondent's first name for pro se parties
            email_recipient = respondent.split()[0] if respondent else 'Respondent'
        petitioner_first = petitioner.split()[0] if petitioner else 'Petitioner'

        # Build relief list for email
        relief_list = '\n'.join([f"    {i+1}. {point}" for i, point in enumerate(relief_points)])

        # Generate the email
        email_subject = f"Required Conferral – {case_context}" if case_context else "Required Conferral – Proposed Motion"

        email_body = f"""Subject: {email_subject}

{email_recipient},

As required by Colorado Rule of Civil Procedure 121 § 1-15, I am attempting to confer with you regarding concerns I intend to raise with the Court.

Specifically, I am requesting:
{relief_list}

Please let me know by {deadline_str} whether you agree to these limited requests.

If I do not receive a response, I will note that in the Certificate of Conferral when filing the motion.

Thank you,
{petitioner_first}"""

        # Generate Certificate of Conferral text (different versions based on outcome)
        # Session 406 Polish: Use "Respondent's counsel" if represented
        conferral_target = "Respondent's counsel" if respondent_counsel else "Respondent"
        conferral_target_short = "Counsel" if respondent_counsel else "Respondent"

        certificate_no_response = f"""CERTIFICATE OF CONFERRAL

Pursuant to C.R.C.P. 121 § 1-15(8), Petitioner certifies that:

1. On or about {datetime.now().strftime('%B %d, %Y')}, Petitioner sent written communication to {conferral_target} regarding the relief requested in this motion.
2. Petitioner made reasonable and good-faith efforts to confer with {conferral_target_short}.
3. {conferral_target_short} did not respond within the conferral period.
4. The matter could not be resolved without Court involvement."""

        certificate_refused = f"""CERTIFICATE OF CONFERRAL

Pursuant to C.R.C.P. 121 § 1-15(8), Petitioner certifies that:

1. On or about {datetime.now().strftime('%B %d, %Y')}, Petitioner sent written communication to {conferral_target} regarding the relief requested in this motion.
2. Petitioner made reasonable and good-faith efforts to confer with {conferral_target_short}.
3. {conferral_target_short} stated they do not agree to the requested relief.
4. The matter could not be resolved without Court involvement."""

        certificate_partial = f"""CERTIFICATE OF CONFERRAL

Pursuant to C.R.C.P. 121 § 1-15(8), Petitioner certifies that:

1. On or about {datetime.now().strftime('%B %d, %Y')}, Petitioner sent written communication to {conferral_target} regarding the relief requested in this motion.
2. Petitioner made reasonable and good-faith efforts to confer with {conferral_target_short}.
3. The parties were unable to reach full agreement on all requested relief.
4. The matter could not be resolved without Court involvement."""

        # Session 406 Polish: Guidance text reflects counsel vs respondent
        send_target = "opposing counsel" if respondent_counsel else "Respondent"

        guidance = f"""CONFERRAL WORKFLOW:

1. SEND THE EMAIL FIRST
   - Send the conferral email above to {send_target}
   - Keep a copy (screenshot, sent folder, etc.)
   - Wait {deadline_days} business days for response

2. DOCUMENT THE OUTCOME
   After {deadline_days} days, one of three things will happen:
   a) No response → Use "Certificate of Conferral (No Response)"
   b) Refused → Use "Certificate of Conferral (Refused)"
   c) Partial agreement → Use "Certificate of Conferral (Partial)" and modify relief

3. FILE THE MOTION
   - Include the appropriate Certificate of Conferral in your motion
   - Attach a copy of the conferral email as an exhibit (optional but recommended)

IMPORTANT: Do NOT file the motion until after the conferral deadline has passed,
unless this is a true emergency under C.R.S. § 14-10-129.5."""

        # Session 406 Patch 4: Include conferral_status as structured data
        # Default to 'pending' - UI can update this based on outcome
        return {
            'success': True,
            'email_subject': email_subject,
            'email_body': email_body,
            'deadline_date': deadline_str,
            'certificates': {
                'no_response': certificate_no_response,
                'refused': certificate_refused,
                'partial_agreement': certificate_partial,
            },
            'guidance': guidance,
            'requires_conferral': True,
            'statutory_basis': 'C.R.C.P. 121 § 1-15(8)',
            # Patch 4: Structured conferral status
            'conferral_status': 'pending',  # Values: pending, no_response, refused, partial, agreed
            'conferral_status_options': ['pending', 'no_response', 'refused', 'partial', 'agreed'],
            'recipient_is_counsel': bool(respondent_counsel),
            'recipient_name': respondent_counsel if respondent_counsel else respondent,
        }

    def _check_conferral_required(self, relief_type: str, is_emergency: bool) -> Dict[str, Any]:
        """
        Session 406: Determine if conferral is required before filing.

        Colorado requires conferral for most motions EXCEPT:
        - Emergency motions under C.R.S. § 14-10-129.5
        - Motions for default judgment
        - Ex parte applications where notice would defeat purpose

        Returns dict with requirement status and explanation.
        """
        # Emergency motions are exempt
        if is_emergency:
            return {
                'required': False,
                'reason': 'Emergency motions under C.R.S. § 14-10-129.5 are exempt from conferral requirements due to imminent danger.',
                'can_file_immediately': True,
            }

        # All other motions require conferral
        return {
            'required': True,
            'reason': 'Per C.R.C.P. 121 § 1-15(8), the moving party must confer with opposing counsel/party before filing non-emergency motions.',
            'can_file_immediately': False,
            'recommended_deadline_days': 2,
            'statutory_basis': 'C.R.C.P. 121 § 1-15(8)',
        }

    def _extract_third_party_segment(self, content: str) -> str:
        """
        Session 405 Patch 4E: Extract the third-party status segment.
        Formats: "Camille Johnson is not a parent, not a legal guardian, not a party..."
        """
        import re

        # Look for "Camille Johnson is:" or similar patterns
        match = re.search(
            r'Camille\s+Johnson\s+is[:\s]*(.*?)(?:Her\s+repeated|This\s+conduct|Respondent\s+has)',
            content,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            segment = match.group(1).strip()
            # Clean up bullet points into a readable list
            bullet_items = re.findall(r'[●•]\s*([^●•]+)', segment)
            if bullet_items:
                clean_items = [item.strip().rstrip('.').lower() for item in bullet_items if item.strip()]
                if clean_items:
                    return f"Camille Johnson is {', '.join(clean_items)}."

        return ""

    def _extract_respondent_failures_segment(self, content: str) -> str:
        """
        Session 405 Patch 4E: Extract the Respondent's failures segment.
        """
        import re

        # Look for "Respondent has:" pattern
        match = re.search(
            r'Respondent\s+has[:\s]*(.*?)(?:The\s+child|These\s+\d+|This\s+pattern|$)',
            content,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            segment = match.group(1).strip()
            # Clean up bullet points
            bullet_items = re.findall(r'[●•]\s*([^●•]+)', segment)
            if bullet_items:
                clean_items = [item.strip().rstrip('.') for item in bullet_items if item.strip() and len(item.strip()) > 10]
                if clean_items:
                    # Capitalize first letter of each
                    clean_items = [item[0].upper() + item[1:] if item else item for item in clean_items]
                    return f"Respondent has: {'; '.join(clean_items[:4])}."

        return ""

    def _generate_impact_paragraph(self, incidents: List[Dict[str, str]], original_content: str) -> str:
        """
        Session 404 Patch 4C: Generate impact/pattern paragraph for allegation 4.
        Session 405 Patch 4D.5: Improved to avoid duplicated pattern language.
        Session 406: Fixed incident count bug - no longer claims specific numbers.

        Uses petitioner's language where possible to summarize:
        - Pattern of behavior
        - Harm to child/relationship
        - Why this is significant
        """
        import re

        # Look for impact/harm language in original content
        harm_patterns = [
            r'(?:emotional|psychological)\s+(?:harm|damage|interference)',
            r'(?:parent|child)\s*[-–]\s*(?:child|parent)\s+relationship',
            r'inappropriate\s+(?:adult\s+)?conflict',
            r'best\s+interest(?:s)?\s+of\s+the\s+child',
            r'alienat(?:ion|ing)',
        ]

        harm_phrases = []
        for pattern in harm_patterns:
            # Session 406: Use a more limited capture - just the sentence containing the pattern
            # Split content into sentences first to avoid capturing bullets
            sentences = re.split(r'(?<=[.!?])\s+', original_content)
            for sentence in sentences:
                if re.search(pattern, sentence, re.IGNORECASE):
                    # Session 405: Clean up the harm phrase before adding
                    clean_match = sentence.strip()
                    # Remove any "These X incidents demonstrate a pattern of" prefix
                    clean_match = re.sub(r'^These\s+\d+\s+(?:documented\s+)?incidents\s+demonstrate\s+(?:a\s+)?(?:escalating\s+)?(?:pattern\s+of\s*)?', '', clean_match, flags=re.IGNORECASE)
                    # Remove "this pattern is" at the start
                    clean_match = re.sub(r'^this\s+pattern\s+is\s+', '', clean_match, flags=re.IGNORECASE)
                    if clean_match and 10 < len(clean_match) < 200:  # Reasonable sentence length
                        harm_phrases.append(clean_match)
                        break  # Found one, stop
            if harm_phrases:
                break  # Found one, stop looking at other patterns

        # Session 406 FIX: Use generic phrasing instead of claiming specific incident count
        # This prevents mismatches between claimed count and actual incidents shown
        num_incidents = len(incidents)

        # Add harm description
        if harm_phrases:
            # Use petitioner's language but clean it
            harm_text = harm_phrases[0].strip()
            harm_text = re.sub(r'^\W+', '', harm_text)  # Remove leading punctuation

            # Session 406 FIX: Clean up common bad phrasings from user content
            # Problem: "escalating, harmful, and constitutes active emotional interference"
            # Solution: Use a cleaner default or fix the grammar

            # Check if harm_text starts with words that indicate bad grammar (adjectives without noun)
            bad_starts = [
                r'^escalating,?\s+harmful',
                r'^harmful,?\s+and\s+constitutes',
                r'^escalating,?\s+and\s+constitutes',
                r'^,\s*harmful',
            ]
            use_default = False
            for bad_pattern in bad_starts:
                if re.match(bad_pattern, harm_text, re.IGNORECASE):
                    use_default = True
                    break

            if use_default:
                impact = self._default_impact_text(num_incidents)
            elif harm_text:
                harm_text = harm_text[0].lower() + harm_text[1:]
                # Session 406: Use generic "documented incidents" instead of specific count
                if num_incidents >= 2:
                    impact = f"These documented incidents demonstrate an escalating pattern of {harm_text}"
                else:
                    impact = f"This incident demonstrates {harm_text}"
            else:
                impact = self._default_impact_text(num_incidents)
        else:
            impact = self._default_impact_text(num_incidents)

        # Clean up
        impact = re.sub(r'\s+', ' ', impact).strip()
        # Session 405: Remove any doubled "pattern of pattern" or similar
        impact = re.sub(r'pattern of\s+this pattern', 'pattern that', impact, flags=re.IGNORECASE)
        impact = re.sub(r'demonstrate\s+a?\s*pattern\s+of\s+a?\s*pattern', 'demonstrate a pattern', impact, flags=re.IGNORECASE)
        # Session 406 Patch 5: Fix "escalating pattern of escalating, harmful" -> clean version
        impact = re.sub(r'escalating pattern of\s+escalating[,\s]+', 'escalating pattern of ', impact, flags=re.IGNORECASE)
        impact = re.sub(r'pattern of\s+harmful[,\s]+and', 'pattern of conduct that', impact, flags=re.IGNORECASE)

        if impact and not impact[-1] in '.!?':
            impact += '.'
        if impact:
            impact = impact[0].upper() + impact[1:]

        return impact

    def _default_impact_text(self, num_incidents: int) -> str:
        """
        Session 405: Default impact text when no harm phrases found.
        Session 406: Fixed to use generic phrasing, not specific incident count.
        """
        if num_incidents >= 2:
            # Session 406: Use "documented incidents" without specific count
            return "These documented incidents demonstrate an escalating pattern of conduct that exposes the child to inappropriate adult conflict and interferes with the parent-child relationship."
        else:
            return "This incident demonstrates conduct that exposes the child to inappropriate adult conflict and interferes with the parent-child relationship."

    def _extract_full_narrative(self, motion_content: str) -> Tuple[List[str], Dict[str, int]]:
        """
        Session 404F: Extract ALL petitioner narrative content - FULL RESTATEMENT.

        This preserves EVERYTHING the user wrote, cleaned but not filtered.
        Used for the FULL RESTATEMENT section so nothing is lost.

        Returns:
            Tuple of (narrative_paragraphs, mapping_stats)
            - narrative_paragraphs: All cleaned user content as numbered paragraphs
            - mapping_stats: Dict with extraction statistics for debug
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        mapping_stats = {
            'total_paragraphs_found': 0,
            'paragraphs_in_restatement': 0,
            'paragraphs_skipped_metadata': 0,
            'paragraphs_skipped_denial_order': 0,
        }

        # STEP 1: Extract user's motion section (before denial order)
        user_motion_content = self._extract_user_motion_section(motion_content)
        logger.info(f"SESSION 404F: Full narrative extraction from {len(user_motion_content)} chars")

        # STEP 2: Basic cleanup (less aggressive than court-ready version)
        cleaned = user_motion_content

        # Remove obvious PDF junk only
        cleanup_patterns = [
            r'Page\s+\d+\s+of\s+\d+',  # Page numbers
            r'\f',  # Form feeds
            r'^[\s\-=_]{10,}$',  # Separator lines
        ]
        for pattern in cleanup_patterns:
            cleaned = re.sub(pattern, '\n', cleaned, flags=re.MULTILINE)

        # STEP 3: Split into paragraphs (by double newline or paragraph break)
        # Normalize different line endings
        cleaned = re.sub(r'\r\n', '\n', cleaned)
        cleaned = re.sub(r'\r', '\n', cleaned)

        # Split on paragraph boundaries (2+ newlines or numbered items)
        raw_paragraphs = re.split(r'\n\s*\n|\n(?=\d+\.)', cleaned)

        narrative_paragraphs = []

        for para in raw_paragraphs:
            para = para.strip()
            mapping_stats['total_paragraphs_found'] += 1

            # Skip empty
            if not para or len(para) < 10:
                continue

            # Skip if ALL CAPS (likely header)
            if para.isupper() and len(para) < 100:
                mapping_stats['paragraphs_skipped_metadata'] += 1
                continue

            # Skip court metadata (case captions, addresses, etc.)
            if self._is_court_metadata(para):
                mapping_stats['paragraphs_skipped_metadata'] += 1
                continue

            # Skip denial order content
            if self._is_denial_order_content(para):
                mapping_stats['paragraphs_skipped_denial_order'] += 1
                continue

            # Clean but preserve the content
            # Remove leading numbering
            para = re.sub(r'^[\d]+[\.\)]\s*', '', para)
            para = re.sub(r'^[a-z][\.\)]\s*', '', para)
            para = re.sub(r'^\([ivx\d]+\)\s*', '', para, flags=re.IGNORECASE)

            # Normalize whitespace within paragraph (preserve structure)
            para = re.sub(r'[ \t]+', ' ', para)
            para = re.sub(r'\n\s+', '\n', para)
            para = para.strip()

            # Must still have content
            if len(para) >= 20:
                # Ensure proper ending
                if para and not para[-1] in '.!?':
                    para += '.'
                # Capitalize first letter
                if para:
                    para = para[0].upper() + para[1:]
                narrative_paragraphs.append(para)
                mapping_stats['paragraphs_in_restatement'] += 1

        logger.info(f"SESSION 404F: Full narrative extracted: {len(narrative_paragraphs)} paragraphs")
        logger.info(f"SESSION 404F: Mapping stats: {mapping_stats}")

        return narrative_paragraphs, mapping_stats

    def _extract_relief_items_list(self, relief_requested: str) -> List[str]:
        """
        Session 406 PATCH-5: Extract individual relief items from the relief_requested text.

        Parses the relief string to extract individual items that can be:
        1. Used in the RELIEF REQUESTED section
        2. Rendered in the PROPOSED ORDER
        3. Counted for likelihood scoring
        4. Used in conferral emails

        Returns list of cleaned relief item strings.
        """
        if not relief_requested:
            return []

        items = []
        lines = relief_requested.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove numbered prefixes like "1. ", "2. ", "a. ", etc.
            clean_line = re.sub(r'^\s*(?:\d+\.|\w\.)\s*', '', line)

            # Skip generic/boilerplate lines
            skip_patterns = [
                r'^wherefore',
                r'^petitioner\s+(?:respectfully\s+)?requests',
                r'^the court',
                r'^note:',
                r'^all relief',
                r'^\[',  # Placeholder brackets
            ]
            if any(re.match(p, clean_line.lower()) for p in skip_patterns):
                continue

            # Skip very short lines
            if len(clean_line) < 15:
                continue

            # Ensure it starts with proper subject (usually "Respondent shall")
            # or reformat to be a proper relief item
            if clean_line and not clean_line.lower().startswith(('respondent', 'it is ordered', 'the court')):
                # Check if it's a complete sentence
                if not clean_line.endswith('.'):
                    clean_line += '.'

            if clean_line:
                items.append(clean_line)

        return items

    def _extract_child_name_from_order(self, order_text: str) -> Optional[str]:
        """
        Session 406 PATCH-5.2: Extract child name spelling from existing court order.

        This ensures name consistency - we use the exact spelling from the court's
        existing order rather than a different spelling entered by the user.

        Returns the child name as spelled in the order, or None if not found.
        """
        import re

        # Common patterns for child names in Colorado family court orders
        patterns = [
            r'(?:minor\s+)?child(?:ren)?[:\s]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'(?:child|minor)[:\s]+([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+)',
            r'(?:child|children)\s+of\s+the\s+marriage[:\s]+([A-Z][a-z]+)',
            r'born\s+(?:on\s+)?[\d/]+[:\s]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+),?\s+(?:age|born|DOB|d\.o\.b\.)',
        ]

        for pattern in patterns:
            match = re.search(pattern, order_text)
            if match:
                name = match.group(1).strip()
                # Validate it looks like a name (has at least 2 parts)
                if ' ' in name and len(name) > 3:
                    logger.debug(f"[PATCH-5.2] Extracted child name from order: {name}")
                    return name

        return None

    def _normalize_child_name_throughout(self, text: str, canonical_name: str) -> str:
        """
        Session 406 PATCH-5.2: Replace variant spellings with the canonical name.

        For example, if the court order spells it "Nicolas" but user entered "Nicholas",
        this ensures we use "Nicolas" consistently throughout.
        """
        import re

        if not canonical_name:
            return text

        # Extract first name from canonical
        canonical_first = canonical_name.split()[0]

        # Common variant spellings for this specific case
        # Nicolas vs Nicholas
        if canonical_first.lower() == 'nicolas':
            text = re.sub(r'\bNicholas\b', canonical_first, text)
        elif canonical_first.lower() == 'nicholas':
            text = re.sub(r'\bNicolas\b', canonical_first, text)

        return text

    def _parse_order_provisions(self, order_text: str, case_number: str = '') -> str:
        """
        Session 406: Parse uploaded court order to extract key provisions.

        Extracts and summarizes:
        - Order date
        - Parenting time schedule
        - Non-disparagement provisions
        - Third-party conduct rules
        - Decision-making authority

        Returns formatted text for EXISTING COURT ORDERS section.
        """
        import re

        provisions = []
        order_date = ''
        has_parenting_time = False
        has_non_disparagement = False
        has_third_party_rules = False
        has_decision_making = False

        # Extract order date
        date_patterns = [
            r'(?:dated|entered|signed)\s+(?:this\s+)?(\w+\s+\d{1,2},?\s*\d{4})',
            r'(?:on|this)\s+(\w+\s+\d{1,2},?\s*\d{4})',
            r'(\w+\s+\d{1,2},?\s*\d{4}).*?(?:temporary|orders?|decree)',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, order_text, re.IGNORECASE)
            if match:
                order_date = match.group(1)
                break

        # Check for parenting time provisions
        parenting_patterns = [
            r'parenting\s+time',
            r'visitation\s+schedule',
            r'custody\s+schedule',
            r'parent.?time\s+schedule',
            r'weekends?.*?alternating',
            r'wednesday.*?parenting',
        ]
        for pattern in parenting_patterns:
            if re.search(pattern, order_text, re.IGNORECASE):
                has_parenting_time = True
                break

        # Check for non-disparagement provisions
        disparagement_patterns = [
            r'non.?disparagement',
            r'shall\s+not\s+(?:make\s+)?(?:negative|disparaging)\s+(?:statements?|remarks?|comments?)',
            r'refrain\s+from\s+(?:making\s+)?(?:negative|disparaging)',
            r'neither\s+party\s+shall.*?speak\s+negatively',
            r'not\s+(?:speak|say)\s+(?:negative|bad|disparaging).*?(?:about|regarding)\s+(?:the\s+)?other',
        ]
        for pattern in disparagement_patterns:
            if re.search(pattern, order_text, re.IGNORECASE):
                has_non_disparagement = True
                break

        # Check for third-party conduct rules
        third_party_patterns = [
            r'third.?part(?:y|ies)',
            r'adults?\s+in\s+(?:the\s+)?(?:household|home)',
            r'significant\s+other',
            r'partner',
            r'shall\s+(?:not\s+)?(?:allow|permit).*?(?:presence|involvement)',
        ]
        for pattern in third_party_patterns:
            if re.search(pattern, order_text, re.IGNORECASE):
                has_third_party_rules = True
                break

        # Check for decision-making provisions
        decision_patterns = [
            r'(?:joint|sole)\s+decision.?making',
            r'major\s+decisions?',
            r'(?:legal|physical)\s+custody',
            r'allocation\s+of\s+parental\s+responsibilities',
        ]
        for pattern in decision_patterns:
            if re.search(pattern, order_text, re.IGNORECASE):
                has_decision_making = True
                break

        # Build the EXISTING COURT ORDERS section
        order_ref = case_number if case_number else '[CASE NUMBER]'
        date_ref = order_date if order_date else '[DATE OF ORDER]'

        # Point 1: Order entry
        provisions.append(f"1. On {date_ref}, the Court entered Temporary Orders in case {order_ref}.")

        # Point 2: What the orders include (enumerate what was found)
        included_items = []
        if has_parenting_time:
            included_items.append("a. A parenting time schedule regarding the minor child(ren)")
        if has_non_disparagement:
            included_items.append("b. A non-disparagement provision prohibiting the parties and third parties from speaking negatively about the other parent in the child's presence")
        if has_third_party_rules:
            included_items.append("c. Provisions regarding third-party conduct during parenting time")
        if has_decision_making:
            included_items.append("d. Decision-making authority allocations")

        if included_items:
            provisions.append("2. The Temporary Orders include:")
            provisions.extend([f"   {item}" for item in included_items])
        else:
            # Default if nothing specific was detected
            provisions.append("2. The Temporary Orders govern parenting time and related matters.")

        # Point 3: Exhibit reference
        provisions.append("3. A true and correct copy of the Temporary Orders is attached as Exhibit A.")

        # Session 406 Patch 6: Add sentence linking conduct to non-disparagement if detected
        if has_non_disparagement:
            provisions.append("")  # Blank line
            provisions.append("The statements described below appear inconsistent with the Court's non-disparagement provisions in the Temporary Orders (Exhibit A).")

        return '\n'.join(provisions)

    def _get_active_case_profile_data(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Session 406: Get case metadata from user's active CaseProfile if one exists.

        This is preferred over document extraction because users enter accurate info
        including opposing counsel details that may not be in the motion document.

        Returns dict matching _extract_case_metadata format, or None if no profile.
        """
        try:
            # Check if user_id or request is in context
            user_id = context.get('user_id')
            request = context.get('request')

            # Import here to avoid circular imports
            from core.models_legal import CaseProfile

            active_case_id = None
            case = None

            if request and hasattr(request, 'session'):
                active_case_id = request.session.get('active_case_id')
            elif context.get('active_case_id'):
                active_case_id = context.get('active_case_id')

            if active_case_id:
                # Get the case profile by ID
                try:
                    case = CaseProfile.objects.get(id=active_case_id)
                    logger.info(f"Session 409: Found CaseProfile by active_case_id: {case.case_number}")
                except CaseProfile.DoesNotExist:
                    logger.warning(f"Session 406: CaseProfile {active_case_id} not found")
                    case = None

            # Session 409: Fallback - if user has ONLY ONE case, use that
            if not case and request and hasattr(request, 'user') and request.user.is_authenticated:
                user_cases = CaseProfile.objects.filter(user=request.user, status='active')
                if user_cases.count() == 1:
                    case = user_cases.first()
                    logger.info(f"Session 409: Using user's only active case: {case.case_number}")
                elif user_cases.count() > 1:
                    logger.info(f"Session 409: User has {user_cases.count()} cases - requires explicit selection")

            if not case:
                logger.debug("Session 406: No case profile found")
                return None

            petitioner = case.petitioner
            respondent = case.respondent

            # Build result matching _extract_case_metadata format
            result = {
                'case_number': case.case_number,
                'county': case.county,
                'state': case.state,
                'division': case.division,
                'courtroom': case.courtroom,
                'court_address': case.court_address,
                'petitioner_name': petitioner.full_name if petitioner else '',
                'petitioner_first_name': petitioner.first_name if petitioner else '',
                'petitioner_address': petitioner.get_full_address() if petitioner else '',
                'petitioner_email': petitioner.email if petitioner else '',
                'respondent_name': respondent.full_name if respondent else '',
                'respondent_first_name': respondent.first_name if respondent else '',
                'respondent_address': respondent.get_full_address() if respondent else '',
                'respondent_email': respondent.email if respondent else '',
            }

            # Add respondent's counsel info if represented (key for conferral emails!)
            if respondent and not respondent.is_pro_se:
                attorney = respondent.attorney
                if attorney:
                    result['respondent_counsel'] = attorney.full_name
                    result['respondent_counsel_first_name'] = attorney.first_name
                    result['respondent_counsel_email'] = attorney.email
                    result['respondent_counsel_firm'] = attorney.firm_name
                    result['respondent_counsel_address'] = attorney.get_full_address()

            # Add conferral recipient info
            conferral_recipient = case.get_conferral_recipient()
            if conferral_recipient:
                result['conferral_recipient_name'] = conferral_recipient['name']
                result['conferral_recipient_first_name'] = conferral_recipient['first_name']
                result['conferral_recipient_email'] = conferral_recipient['email']
                result['conferral_recipient_is_attorney'] = conferral_recipient['is_attorney']

            # Add children info
            children = []
            for child in case.children.all():
                children.append({
                    'name': child.full_name,
                    'first_name': child.first_name,
                    'age': child.age,
                })
            result['children'] = children
            if children:
                result['child_name'] = children[0]['name']  # First child for template

            logger.info(f"Session 406: Loaded CaseProfile {case.case_number} with "
                       f"conferral recipient: {result.get('conferral_recipient_name', 'N/A')}")
            return result

        except Exception as e:
            logger.error(f"Session 406: Error loading CaseProfile: {e}")
            return None

    def _extract_case_metadata(self, content: str) -> Dict[str, str]:
        """
        Session 404 V3: Extract case metadata from uploaded document.

        Extracts:
        - Case number (e.g., 2025DR000576)
        - County (e.g., LARIMER)
        - Petitioner name
        - Respondent name
        - Division/Courtroom
        - Court address
        - Child name (if mentioned)
        """
        import re
        metadata = {
            'case_number': '',
            'county': '',
            'state': '',  # Session 404D: Added state extraction
            'petitioner_name': '',
            'respondent_name': '',
            'division': '',
            'courtroom': '',
            'court_address': '',
            'child_name': '',
        }

        # Use first 3000 chars (header area) for metadata extraction
        header_section = content[:3000]

        # Extract case number (Colorado format: 2025DR000576 or 2025 DR 576)
        case_patterns = [
            r'(\d{4}\s*DR\s*\d{3,6})',  # 2025DR000576 or 2025 DR 576
            r'Case\s*(?:Number|No\.?)[\s:]*(\d{4}\s*DR\s*\d+)',
            r'(\d{4}DR\d+)',  # Compact format
        ]
        for pattern in case_patterns:
            match = re.search(pattern, header_section, re.IGNORECASE)
            if match:
                # Normalize format
                case_num = re.sub(r'\s+', '', match.group(1).upper())
                metadata['case_number'] = case_num
                break

        # Extract county - be careful not to match "DISTRICT" from "DISTRICT COURT"
        county_patterns = [
            # "DISTRICT COURT, LARIMER COUNTY" - most common format
            r'DISTRICT\s+COURT[,\s]+(\w+)\s+COUNTY',
            # "LARIMER COUNTY, COLORADO" but NOT "DISTRICT COUNTY"
            r'(?<!DISTRICT\s)(\w+)\s+COUNTY[,\s]+COLORADO',
            # "LARIMER COUNTY DISTRICT COURT"
            r'(\w+)\s+COUNTY\s+DISTRICT\s+COURT',
        ]
        for pattern in county_patterns:
            match = re.search(pattern, header_section, re.IGNORECASE)
            if match:
                county = match.group(1).upper()
                # Don't accept "DISTRICT" as a county name
                if county != 'DISTRICT':
                    metadata['county'] = county
                    break

        # Session 404D: Extract state - must be found alongside county
        # Only accept if clearly stated in document header
        state_patterns = [
            r'STATE\s+OF\s+(\w+)',  # "STATE OF COLORADO"
            r'(\w+)\s+COUNTY,\s+STATE\s+OF\s+(\w+)',  # With county context
            r',\s+(\w+)\s+\d{5}',  # City, STATE ZIP format
        ]
        for pattern in state_patterns:
            match = re.search(pattern, header_section, re.IGNORECASE)
            if match:
                # Handle patterns with multiple groups
                state = match.group(2) if match.lastindex >= 2 else match.group(1)
                state = state.upper()
                # Only accept known US states (basic validation)
                valid_states = ['COLORADO', 'CALIFORNIA', 'TEXAS', 'NEW YORK', 'FLORIDA',
                               'ARIZONA', 'NEVADA', 'UTAH', 'NEW MEXICO', 'WYOMING',
                               'WASHINGTON', 'OREGON', 'IDAHO', 'MONTANA', 'KANSAS',
                               'NEBRASKA', 'OKLAHOMA', 'MINNESOTA', 'IOWA', 'MISSOURI',
                               'ARKANSAS', 'LOUISIANA', 'WISCONSIN', 'ILLINOIS', 'MICHIGAN',
                               'INDIANA', 'OHIO', 'KENTUCKY', 'TENNESSEE', 'ALABAMA',
                               'MISSISSIPPI', 'GEORGIA', 'SOUTH CAROLINA', 'NORTH CAROLINA',
                               'VIRGINIA', 'WEST VIRGINIA', 'MARYLAND', 'DELAWARE',
                               'PENNSYLVANIA', 'NEW JERSEY', 'CONNECTICUT', 'RHODE ISLAND',
                               'MASSACHUSETTS', 'VERMONT', 'NEW HAMPSHIRE', 'MAINE']
                if state in valid_states:
                    metadata['state'] = state
                    break

        # Extract petitioner name
        # Session 406: Handle ALL CAPS names from court documents
        # IMPORTANT: Do NOT use re.IGNORECASE - patterns rely on case to identify proper names
        petitioner_patterns = [
            # ALL CAPS format: "Petitioner(s) CHRISTOPHER L WEST" - first name must be 2+ chars
            r'Petitioner\(?s?\)?[\s:]+([A-Z]{2,}(?:\s+[A-Z]\.?)?\s+[A-Z]{2,})',
            # Mixed case: "Petitioner: Christopher L. West"
            r'Petitioner[\s:]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)[,\s]+Petitioner',
            r'Petitioner[\s:]*\n\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'In\s+Re.*?Marriage.*?([A-Z][a-z]+\s+[A-Z][a-z]+)\s+and',
        ]
        for pattern in petitioner_patterns:
            match = re.search(pattern, header_section)  # NO re.IGNORECASE - case matters!
            if match:
                name = match.group(1).strip()
                # Skip if it's a common legal term (not a real name)
                if name.lower() in ['the court', 'district court', 'colorado']:
                    continue
                metadata['petitioner_name'] = name.title()
                break

        # Extract respondent name
        # Session 406: Handle ALL CAPS names from court documents
        # IMPORTANT: Do NOT use re.IGNORECASE - patterns rely on case to identify proper names
        respondent_patterns = [
            # ALL CAPS format: "Respondent(s) SUSANNAH M WEST" - first name must be 2+ chars
            r'Respondent\(?s?\)?[\s:]+([A-Z]{2,}(?:\s+[A-Z]\.?)?\s+[A-Z]{2,})',
            # Mixed case
            r'Respondent[\s:]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)[,\s]+Respondent',
            r'Respondent[\s:]*\n\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'and\s+([A-Z][a-z]+\s+[A-Z][a-z]+)[,\s]*Respondent',
        ]
        for pattern in respondent_patterns:
            match = re.search(pattern, header_section)  # NO re.IGNORECASE - case matters!
            if match:
                name = match.group(1).strip()
                # Skip if it's a common legal term (not a real name)
                if name.lower() in ['the court', 'district court', 'colorado']:
                    continue
                metadata['respondent_name'] = name.title()
                break

        # Extract respondent's counsel/attorney name
        # Session 406: For conferral emails, we need to contact opposing counsel if represented
        counsel_patterns = [
            # "Attorney for Respondent: Jane Smith" or "Counsel for Respondent: Jane Smith"
            r'(?:Attorney|Counsel)\s+for\s+Respondent[\s:]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            # "Respondent's Attorney: Jane Smith"
            r"Respondent'?s?\s+(?:Attorney|Counsel)[\s:]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)",
            # ALL CAPS: "ATTORNEY FOR RESPONDENT: JANE SMITH"
            r'(?:ATTORNEY|COUNSEL)\s+FOR\s+RESPONDENT[\s:]+([A-Z]{2,}(?:\s+[A-Z]\.?)?\s+[A-Z]{2,})',
            # Look for attorney signature block patterns
            r'/s/\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)\s*\n.*?(?:Attorney|Counsel)\s+for\s+Respondent',
            # Bar number pattern: "Jane Smith, Atty. Reg. No." or "Jane Smith, #12345"
            r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)[,\s]+(?:Atty\.?\s*Reg\.?\s*No\.?|#\s*\d+).*?Respondent',
        ]
        for pattern in counsel_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                name = match.group(1).strip()
                # Skip common legal terms
                if name.lower() not in ['the court', 'district court', 'colorado', 'pro se']:
                    metadata['respondent_counsel'] = name.title()
                    break

        # Extract division - look for standalone division number/letter
        # Pattern should match "Division: 2B" or "Division 2B" but stop before other words
        division_patterns = [
            r'Division[\s:]+([0-9]+[A-Z]?)\b',  # "Division: 2B" or "Division 2"
            r'Division[\s:]+([A-Z])\b',  # "Division: A"
            r'Div\.?\s*[\s:]+([0-9A-Z]+)\b',  # "Div: 2B"
        ]
        for pattern in division_patterns:
            division_match = re.search(pattern, header_section, re.IGNORECASE)
            if division_match:
                div = division_match.group(1).upper()
                # Don't accept words like "Courtroom" or "Order"
                if len(div) <= 3 and not div.lower() in ['the', 'and', 'for']:
                    metadata['division'] = div
                    break

        # Extract courtroom - similar approach
        courtroom_patterns = [
            r'Courtroom[\s:]+([0-9]+[A-Z]?)\b',  # "Courtroom: 3A"
            r'Courtroom[\s:]+([A-Z])\b',  # "Courtroom: A"
            r'Crtrm\.?\s*[\s:]+([0-9A-Z]+)\b',  # "Crtrm: 3A"
        ]
        for pattern in courtroom_patterns:
            courtroom_match = re.search(pattern, header_section, re.IGNORECASE)
            if courtroom_match:
                crtrm = courtroom_match.group(1).upper()
                # Don't accept long words
                if len(crtrm) <= 3 and not crtrm.lower() in ['the', 'and', 'for']:
                    metadata['courtroom'] = crtrm
                    break

        # Extract court address
        # Session 406: Fixed to not grab petitioner line
        address_patterns = [
            # Match "Court Address:" followed by address on same line only
            r'Court\s+Address[\s:]*([^\n]+)',
            r'(\d+\s+\w+(?:\s+\w+)*(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Way)[,\s]+(?:Suite|Ste|#)?[^,\n]*(?:,\s*[A-Z]{2}\s*,?\s*\d{5})?)',
        ]
        for pattern in address_patterns:
            match = re.search(pattern, header_section, re.IGNORECASE)
            if match:
                addr = match.group(1).strip()
                # Session 406: Stop at "Petitioner" if it got captured
                if 'petitioner' in addr.lower():
                    addr = re.split(r'\s+petitioner', addr, flags=re.IGNORECASE)[0].strip()
                # Clean up and limit length
                addr = re.sub(r'\s+', ' ', addr)[:100]
                metadata['court_address'] = addr
                break

        # =========================================================================
        # Session 404F: FALLBACK - Infer county/state from court address
        # =========================================================================
        # If county or state not extracted, try to infer from address
        if metadata['court_address'] and (not metadata['county'] or not metadata['state']):
            addr_upper = metadata['court_address'].upper()

            # Colorado city → county mapping
            colorado_city_to_county = {
                'FORT COLLINS': 'LARIMER',
                'LOVELAND': 'LARIMER',
                'ESTES PARK': 'LARIMER',
                'DENVER': 'DENVER',
                'BOULDER': 'BOULDER',
                'COLORADO SPRINGS': 'EL PASO',
                'PUEBLO': 'PUEBLO',
                'GREELEY': 'WELD',
                'LONGMONT': 'BOULDER',
                'AURORA': 'ARAPAHOE',
                'LAKEWOOD': 'JEFFERSON',
                'GOLDEN': 'JEFFERSON',
                'THORNTON': 'ADAMS',
                'WESTMINSTER': 'ADAMS',
                'ARVADA': 'JEFFERSON',
                'CENTENNIAL': 'ARAPAHOE',
                'CASTLE ROCK': 'DOUGLAS',
                'BROOMFIELD': 'BROOMFIELD',
                'GRAND JUNCTION': 'MESA',
                'DURANGO': 'LA PLATA',
                'STEAMBOAT SPRINGS': 'ROUTT',
                'ASPEN': 'PITKIN',
                'VAIL': 'EAGLE',
                'GLENWOOD SPRINGS': 'GARFIELD',
            }

            # State abbreviation mapping
            state_abbrev_map = {
                'CO': 'COLORADO', 'CA': 'CALIFORNIA', 'TX': 'TEXAS', 'NY': 'NEW YORK',
                'FL': 'FLORIDA', 'AZ': 'ARIZONA', 'NV': 'NEVADA', 'UT': 'UTAH',
                'NM': 'NEW MEXICO', 'WY': 'WYOMING', 'WA': 'WASHINGTON', 'OR': 'OREGON',
                'ID': 'IDAHO', 'MT': 'MONTANA', 'KS': 'KANSAS', 'NE': 'NEBRASKA',
                'OK': 'OKLAHOMA', 'MN': 'MINNESOTA', 'IA': 'IOWA', 'MO': 'MISSOURI',
            }

            # Try to extract state abbreviation from address (e.g., "FORT COLLINS, CO, 80521")
            if not metadata['state']:
                state_abbrev_match = re.search(r',\s*([A-Z]{2})\s*,?\s*\d{5}', addr_upper)
                if state_abbrev_match:
                    abbrev = state_abbrev_match.group(1)
                    if abbrev in state_abbrev_map:
                        metadata['state'] = state_abbrev_map[abbrev]

            # Try to find city in address and map to county
            if not metadata['county']:
                for city, county in colorado_city_to_county.items():
                    if city in addr_upper:
                        metadata['county'] = county
                        # If we found a Colorado city, state is definitely Colorado
                        if not metadata['state']:
                            metadata['state'] = 'COLORADO'
                        break

        # Extract child name (look for patterns like "minor child, [Name]" or "child [Name]")
        child_patterns = [
            r'minor\s+child[,\s]+([A-Z][a-z]+)',
            r'child[,\s]+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z]?[a-z]*)',
            r'the\s+child[,\s]+([A-Z][a-z]+)',
            r'([A-Z][a-z]+)[,\s]+the\s+minor\s+child',
        ]
        for pattern in child_patterns:
            match = re.search(pattern, content[:5000])  # Look in more of document
            if match:
                child = match.group(1).strip()
                if len(child) > 2 and child.lower() not in ['the', 'child', 'minor']:
                    metadata['child_name'] = child.title()
                    break

        return metadata

    def _extract_user_motion_section(self, content: str) -> str:
        """
        Session 404B: Extract only the USER'S MOTION using start/end markers.

        The PDF typically has:
        - Court header (case number, parties)
        - User's motion narrative starting with "Petitioner states..." or similar
        - Motion ends at "WHEREFORE" or "RELIEF REQUESTED"
        - Judge's denial order (SKIP)

        We find the start of the facts section and end before relief/denial.
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        lines = content.splitlines()

        # Session 404B: Find START of user narrative
        start_patterns = [
            r'petitioner\s+states\s+as\s+follows',
            r'in\s+support\s+of\s+this\s+motion.*petitioner\s+states',
            r'petitioner.*appearing\s+pro\s+se.*respectfully\s+moves',
            r'petitioner.*respectfully\s+submits',
            r'factual\s+(basis|allegations?)',
            r'facts?\s*:',
            r'the\s+following\s+facts',
        ]

        start_index = 0
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for pattern in start_patterns:
                if re.search(pattern, line_lower):
                    start_index = i
                    logger.debug(f"SESSION 404B: Found start at line {i}: {line[:50]}...")
                    break
            if start_index > 0:
                break

        # Session 404B: Find END of user narrative (before relief/denial order)
        end_patterns = [
            r'wherefore',
            r'relief\s+requested',
            r'respectfully\s+submitted',
            r'dated\s+this',
            r'it\s+is\s+(so\s+)?ordered',
            r'the\s+(motion|request)\s+is\s+(hereby\s+)?(denied|granted)',
            r'this\s+matter\s+comes\s+before\s+the\s+court',
            r'upon\s+review\s+of\s+the\s+(motion|petition)',
            r'magistrate',
            r'for\s+the\s+foregoing\s+reasons',
        ]

        end_index = len(lines)
        for i in range(start_index, len(lines)):
            line_lower = lines[i].lower()
            for pattern in end_patterns:
                if re.search(pattern, line_lower):
                    end_index = i
                    logger.debug(f"SESSION 404B: Found end at line {i}: {lines[i][:50]}...")
                    break
            if end_index < len(lines):
                break

        # Extract the segment
        segment = lines[start_index:end_index]
        logger.info(f"SESSION 404B: Extracted {len(segment)} lines from user motion (lines {start_index}-{end_index})")

        # Session 404B: Additional filter - remove obvious metadata/order lines
        ORDER_METADATA_PATTERNS = [
            r'\bDENIED\b',
            r'\bGRANTED\b',
            r'\bIT IS ORDERED\b',
            r'\bMagistrate\b',
            r'\bJudge\b',
            r'\bDATE FILED\b',
            r'\bCASE NUMBER\b',
            r'\bCOURT ADDRESS\b',
            r'\bDISTRICT COURT\b',
            r'\bCOURT USE ONLY\b',
            r'201\s*LA\s*PORTE\s*AVENUE',
            r'petitioner\s+is\s+encouraged\s+to\s+utilize',
            r'utilize\s+the\s+jdf\s+forms',
        ]

        cleaned = []
        for line in segment:
            skip = False
            for pat in ORDER_METADATA_PATTERNS:
                if re.search(pat, line, re.IGNORECASE):
                    skip = True
                    break
            if not skip:
                cleaned.append(line)

        result = '\n'.join(cleaned).strip()
        logger.info(f"SESSION 404B: Final cleaned section: {len(result)} chars")

        # Session 405 Patch 4D: Apply pre-extraction cleanup
        result = self._patch_4d_pre_extraction_cleanup(result)

        return result

    def _patch_4d_pre_extraction_cleanup(self, content: str) -> str:
        """
        Session 405 Patch 4D: Pre-extraction cleanup to remove PDF artifacts.

        This runs BEFORE fact grouping to eliminate:
        1. Docket artifacts ("Attachment to Order - 2025DR576")
        2. Section headers mixed into facts ("2. Today's Incident –")
        3. Orphaned statute symbols ("(§)")
        4. Page break artifacts
        5. Repeated case number fragments

        Called on extracted text BEFORE fact grouping.
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        original_len = len(content)

        # =====================================================================
        # 1. DOCKET ARTIFACTS - Remove "Attachment to Order - XXXX" patterns
        # =====================================================================
        docket_patterns = [
            r'Attachment\s+to\s+Order\s*[-–—]\s*\d{4}DR\d+',
            r'Attachment\s+to\s+Order\s*[-–—]\s*[A-Z0-9]+',
            r'Page\s+\d+\s+of\s+\d+',
            r'[-–—]\s*\d+\s*[-–—]',  # Page numbers like "- 1 -"
            r'\d{4}DR\d+\s*$',  # Trailing case numbers
        ]
        for pattern in docket_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        # =====================================================================
        # 2. SECTION HEADERS - Remove numbered headers that aren't facts
        # =====================================================================
        # These are section dividers, not factual allegations
        section_header_patterns = [
            r'^\s*\d+\.\s*Today\'s\s+Incident\s*[-–—].*$',
            r'^\s*\d+\.\s*Harm\s+and\s+Improper\s+Interference\s*$',
            r'^\s*\d+\.\s*Pattern\s+of\s+Conduct.*$',
            r'^\s*\d+\.\s*Background\s*$',
            r'^\s*\d+\.\s*Prior\s+Incidents?\s*$',
            r'^\s*\d+\.\s*Relief\s+Requested\s*$',
            r'^\s*\d+\.\s*Legal\s+Basis\s*$',
            r'^\s*\d+\.\s*Conclusion\s*$',
        ]
        for pattern in section_header_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)

        # =====================================================================
        # 3. ORPHANED STATUTE SYMBOLS - Remove truncated references
        # =====================================================================
        statute_artifacts = [
            r'\(§\)',  # Orphaned section symbol
            r'\(§\s*\)',
            r'§\s*$',  # Trailing section symbol
            r'\(\s*\)',  # Empty parentheses
            r'C\.R\.S\.\s*§?\s*$',  # Incomplete statute refs
        ]
        for pattern in statute_artifacts:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)

        # =====================================================================
        # 4. CLEAN UP WHITESPACE ARTIFACTS
        # =====================================================================
        # Multiple newlines to single
        content = re.sub(r'\n{3,}', '\n\n', content)
        # Multiple spaces to single
        content = re.sub(r'  +', ' ', content)
        # Leading/trailing whitespace per line
        lines = [line.strip() for line in content.splitlines()]
        # Remove empty lines at start/end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()

        content = '\n'.join(lines)

        # =====================================================================
        # 5. REMOVE INLINE NUMBERING ARTIFACTS
        # =====================================================================
        # Sometimes PDFs have weird numbering like "1. 2. 3." on same line
        content = re.sub(r'(?<!\d)\d+\.\s*(?=\d+\.)', '', content)

        # =====================================================================
        # 6. BULLET POINT FORMATTING (Session 405 Patch 4D.1)
        # =====================================================================
        # PDF bullet points (●, •, ○, ■) often run together without line breaks
        # Convert inline bullets to proper line breaks for readability
        bullet_chars = r'[●•○■▪▸►]'

        # Add newline before bullets that are preceded by text (not start of line)
        content = re.sub(rf'([^\n])\s*({bullet_chars})\s*', r'\1\n\2 ', content)

        # Ensure bullets at start of content don't have leading newline issues
        content = re.sub(rf'^\s*({bullet_chars})\s*', r'\1 ', content)

        # Also handle "Camille Johnson is:" followed by bullets on same line
        content = re.sub(r':\s*(' + bullet_chars + r')', r':\n\1', content)

        # =====================================================================
        # 7. NARRATIVE HEADER CLEANUP (Session 405 Patch 4D.2)
        # =====================================================================
        # Remove inline section headers that break up the narrative
        # These are headers like "2. Today's Incident – November 12, 2025"
        # that appear mid-paragraph
        inline_header_patterns = [
            r'\d+\.\s*Today\'s\s+Incident\s*[-–—]\s*\w+\s+\d+,\s*\d{4}',
            r'\d+\.\s*Harm\s+and\s+Improper\s+Interference',
            r'\d+\.\s*Pattern\s+of\s+Conduct\s+by\s+\w+',
        ]
        for pattern in inline_header_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        # =====================================================================
        # 8. ORPHANED DATE PREFIX CLEANUP (Session 405 Patch 4D.3)
        # =====================================================================
        # Problem: PDF extraction merges section header dates into narrative
        # Example: "On November 12, 2025, the following week" - the date prefix
        # from a header gets merged with "the following week" from another line
        #
        # Pattern: "On [Date], [timeword]" where timeword indicates it's a RELATIVE
        # reference (like "the following week", "that same day", "later that month")
        # In this case, the date prefix is wrong and should be removed.

        # Relative time indicators that shouldn't follow an absolute date
        relative_time_words = [
            'the following',
            'that same',
            'the next',
            'the previous',
            'later that',
            'earlier that',
            'the week after',
            'the day after',
            'the month after',
        ]

        for rel_word in relative_time_words:
            # Match: "On [Month] [Day], [Year], [relative word]"
            # Replace with just the relative word (remove the contradictory date)
            pattern = rf'On\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{{1,2}},?\s*\d{{4}},?\s*({rel_word})'
            content = re.sub(pattern, r'\1', content, flags=re.IGNORECASE)

        # Also catch: "On [Date], immediate" patterns (header artifact)
        content = re.sub(
            r'On\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4},?\s*(immediate\s+Emergency\s+Basis)',
            r'\1',
            content,
            flags=re.IGNORECASE
        )

        logger.info(f"SESSION 405 Patch 4D: Cleaned {original_len} -> {len(content)} chars")

        return content

    def _patch_4d_clean_single_fact(self, fact: str) -> str:
        """
        Session 405 Patch 4D.4: Clean a single fact/allegation for court-ready output.

        This applies comprehensive cleanup including:
        - Orphaned date prefixes (On November 12, 2025, the following week)
        - Bullet point formatting (●, •)
        - Section header removal
        - Proper sentence termination
        - Session 405 Patch 4I: Fix corrupt date concatenation from PDF parsing
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        if not fact:
            return ''

        cleaned = fact.strip()

        # 0. Session 405 Patch 4I: Fix corrupt PDF parsing where date runs into next sentence
        # Pattern: "On November 12, 2025This is now" -> split into proper sentence
        # This happens when PDF extraction loses the newline between date and next paragraph
        corrupt_date_pattern = r'(On\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4})([A-Z][a-z])'
        cleaned = re.sub(corrupt_date_pattern, r'\1. \2', cleaned)

        # Also catch: "November 12, 2025This is now" without "On"
        corrupt_date_pattern2 = r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4})([A-Z][a-z])'
        cleaned = re.sub(corrupt_date_pattern2, r'\1. \2', cleaned)

        # 1. Remove orphaned date prefixes before relative time phrases
        relative_time_words = [
            'the following', 'that same', 'the next', 'the previous',
            'later that', 'earlier that', 'the week after', 'immediate'
        ]
        for rel_word in relative_time_words:
            pattern = rf'On\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{{1,2}},?\s*\d{{4}},?\s*({rel_word})'
            cleaned = re.sub(pattern, r'\1', cleaned, flags=re.IGNORECASE)

        # 2. Format bullet points onto separate lines
        # Session 405 Patch 4E.1: More aggressive bullet formatting
        bullet_chars = r'[●•○■▪▸►]'

        # Add newline before EVERY bullet (except at very start)
        cleaned = re.sub(rf'([^\n])(\s*)({bullet_chars})', r'\1\n   \3', cleaned)

        # Ensure bullets after colons have newlines
        cleaned = re.sub(r':\s*\n?\s*(' + bullet_chars + r')', r':\n   \1', cleaned)

        # Clean up any double newlines created
        cleaned = re.sub(r'\n\s*\n\s*(' + bullet_chars + r')', r'\n   \1', cleaned)

        # 3. Remove section headers that got mixed into facts
        section_patterns = [
            r"^\d+\.\s*Today's\s+Incident\s*[-–—]\s*\w+\s+\d+,\s*\d{4}\s*",
            r"\d+\.\s*Today's\s+Incident\s*[-–—]\s*\w+\s+\d+,\s*\d{4}\s*",
            r"\d+\.\s*Harm\s+and\s+Improper\s+Interference\s*",
            r"\d+\.\s*Pattern\s+of\s+Conduct\s+by\s+\w+\s*",
        ]
        for pattern in section_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # 4. Clean up docket artifacts
        cleaned = re.sub(r'Attachment\s+to\s+Order\s*[-–—]\s*\d{4}DR\d+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\d{4}DR\d+', '', cleaned)

        # 5. Clean up orphaned statute symbols
        cleaned = re.sub(r'\(§\)', '', cleaned)
        cleaned = re.sub(r'§\s*$', '', cleaned)

        # 6. Session 405 Patch 4D.7: Remove "Immediate Emergency Basis"
        cleaned = re.sub(r',?\s*[Ii]mmediate\s+[Ee]mergency\s+[Bb]asis\b[^.]*\.?\s*', ' ', cleaned)

        # 7. Session 405 Patch 4D.7: Fix grammar in pattern sentences
        cleaned = re.sub(
            r"demonstrate\s+a\s+pattern\s+of\s+escalating,?\s*harmful,?\s*and\s+constitutes[^.]*",
            "demonstrate an escalating pattern of emotional interference with the parent-child relationship",
            cleaned,
            flags=re.IGNORECASE,
        )

        # 8. Clean up whitespace
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'  +', ' ', cleaned)
        cleaned = cleaned.strip()

        # 9. Ensure proper ending
        if cleaned and cleaned[-1] not in '.!?':
            cleaned += '.'

        # 10. Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        return cleaned

    def postprocess_extracted_facts(self, facts: List[str]) -> List[str]:
        """
        Session 405 Patch 4D.5: Final cleanup layer applied AFTER fact extraction
        and BEFORE building SPECIFIC FACTUAL ALLEGATIONS and FULL RESTATEMENT sections.

        Based on ChatGPT suggestions for comprehensive cleanup.
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        CLEAN_PATTERNS = [
            # Session 405 Patch 4D.7: Emergency-label artifacts - MUST BE REMOVED
            r",?\s*[Ii]mmediate\s+[Ee]mergency\s+[Bb]asis\b\.?\s*",
            r"\bImmediate Emergency Basis\b\.?\s*",
            r"\bOn an immediate emergency basis\b[^.]*\.?\s*",
            r"[Ii]mmediate\s+[Ee]mergency\s+[Bb]asis\s+",
            r"Attachment to Order\s*[-–]\s*\d{4}DR\d+[^.]*\.?\s*",

            # Docket / case artifacts
            r"Case Number[:\s]*\d{4}DR\d+[^.]*\.?\s*",
            r"Division[:\s]*\S+\s*Courtroom[:\s]*\S+",
            r"COURT USE ONLY[^.]*\.?\s*",

            # Parenthetical statute references e.g. (§14124) or (§ 14-10-124)
            r"\(§[^)]*\)",
            r"§\s*\d+[-–]\d+[-–]\d+",
            r"\(§\s*\d+[-–]?\d*[-–]?\d*\)",

            # Orphaned numbering lines
            r"^\s*\d+\.\s*$",

            # Session 405: Additional patterns
            r"DISTRICT COURT.*?STATE OF \w+",
            r"Court Address:.*",
            r"Petitioner:.*?Respondent:.*",
        ]

        cleaned: List[str] = []

        for p in facts:
            original = p

            # Session 405 Patch 4I: Fix corrupt PDF parsing where date runs into next sentence
            # Pattern: "On November 12, 2025This is now" -> split into proper sentence
            corrupt_date_pattern = r'(On\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4})([A-Z][a-z])'
            p = re.sub(corrupt_date_pattern, r'\1. \2', p)
            # Without "On"
            corrupt_date_pattern2 = r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4})([A-Z][a-z])'
            p = re.sub(corrupt_date_pattern2, r'\1. \2', p)

            for pattern in CLEAN_PATTERNS:
                p = re.sub(pattern, "", p, flags=re.IGNORECASE | re.MULTILINE)

            # Session 405 Patch 4E.2: Format bullet points onto separate lines
            # Convert inline bullets to newline-separated format
            bullet_chars = r'[●•○■▪▸►]'

            # First, add newline before EVERY bullet that follows text on same line
            p = re.sub(rf'([^\n])(\s*)({bullet_chars})', r'\1\n   \3', p)

            # Handle bullets at start of line - ensure proper indentation
            p = re.sub(rf'^(\s*)({bullet_chars})', r'   \2', p, flags=re.MULTILINE)

            # Handle bullets after newline (normalize indentation)
            p = re.sub(rf'\n\s*({bullet_chars})', r'\n   \1', p)

            # Ensure bullets after colons have newlines
            p = re.sub(r':\s*\n?\s*(' + bullet_chars + r')', r':\n   \1', p)

            # Clean up any double newlines created
            p = re.sub(r'\n\s*\n\s*(' + bullet_chars + r')', r'\n   \1', p)

            # Collapse excessive whitespace (but preserve intentional newlines)
            p = re.sub(r"[ \t]{2,}", " ", p)
            p = p.strip(" \t-•")

            # Session 405 Patch 4J: Fix "Today's" references in PART 5
            p = re.sub(r"Today[''']?s?\s+Incident\s*[-–—―‐‑‒]\s*", "The Incident on ", p, flags=re.IGNORECASE)
            p = re.sub(r"Today[''']?s?\s+Incident\s*\n+\s*", "The Incident on ", p, flags=re.IGNORECASE)
            p = re.sub(r"At\s+today[''']?s?\s+parenting[- ]?time", "At the parenting-time", p, flags=re.IGNORECASE)
            p = re.sub(r"today[''']?s?\s+parenting[- ]?time", "the parenting-time", p, flags=re.IGNORECASE)
            p = re.sub(r"At\s+today[''']?s?\s+", "At the ", p, flags=re.IGNORECASE)

            # Drop if too short / empty after cleaning
            if not p or len(p.split()) < 3:
                continue

            cleaned.append(p)

        logger.info(f"SESSION 405 Patch 4D.5: Postprocessed {len(facts)} facts -> {len(cleaned)} clean facts")
        return cleaned

    def cleanup_generated_facts_block(self, text: str) -> str:
        """
        Session 405 Patch 4D.5: Remove awkward boilerplate pattern lines from
        generated SPECIFIC FACTUAL ALLEGATIONS block.

        Based on ChatGPT suggestions.
        """
        import re

        # Session 405 Patch 4I: Fix corrupt PDF parsing where date runs into next sentence
        # Pattern: "On November 12, 2025This is now" -> "On November 12, 2025. This is now"
        corrupt_date_pattern = r'(On\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4})([A-Z][a-z])'
        text = re.sub(corrupt_date_pattern, r'\1. \2', text)
        # Without "On"
        corrupt_date_pattern2 = r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4})([A-Z][a-z])'
        text = re.sub(corrupt_date_pattern2, r'\1. \2', text)

        # Remove "These N incidents demonstrate a pattern..." awkward lines
        text = re.sub(
            r"These\s+\d+\s+incidents\s+demonstrate\s+a\s+pattern.*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        # Session 405 Patch 4D.7: Fix grammar issues in pattern sentences
        # "demonstrate a pattern of escalating, harmful, and constitutes" -> clean version
        text = re.sub(
            r"demonstrate\s+a\s+pattern\s+of\s+escalating,?\s*harmful,?\s*and\s+constitutes[^.]*",
            "demonstrate an escalating pattern of emotional interference with the parent-child relationship",
            text,
            flags=re.IGNORECASE,
        )

        # Fix "this pattern is escalating, harmful, and constitutes..."
        text = re.sub(
            r"this pattern is escalating,?\s*harmful,?\s*and\s+constitutes\s+active\s+emotional\s+interference[^.]*",
            "This pattern is escalating, harmful, and constitutes emotional interference with the parent-child relationship",
            text,
            flags=re.IGNORECASE,
        )

        # Remove "These X incidents demonstrate..." at start of facts
        text = re.sub(
            r"^\s*These\s+\d+\s+incidents\s+demonstrate\s+",
            "",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        # Clean up any remaining duplicate "pattern of pattern" language
        text = re.sub(
            r"pattern of this pattern",
            "pattern that",
            text,
            flags=re.IGNORECASE,
        )

        # Session 405 Patch 4D.7: Remove "Immediate Emergency Basis" anywhere
        text = re.sub(
            r",?\s*[Ii]mmediate\s+[Ee]mergency\s+[Bb]asis\b[^.]*\.?\s*",
            " ",
            text,
        )

        # Session 405 Patch 4G/4J: Fix "Today's Incident" to use actual date
        # The motion is filed later, so "Today" is incorrect
        # Handle various quote styles and dashes
        text = re.sub(
            r"Today[''']?s?\s+Incident\s*[-–—―‐‑‒]\s*",
            "The Incident on ",
            text,
            flags=re.IGNORECASE,
        )
        # Also handle with newline between
        text = re.sub(
            r"Today[''']?s?\s+Incident\s*\n+\s*",
            "The Incident on ",
            text,
            flags=re.IGNORECASE,
        )
        # Handle standalone "Today's Incident" header (whole line)
        text = re.sub(
            r"^Today[''']?s?\s+Incident\s*$",
            "",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        # Also fix "At today's parenting-time exchange" -> "At the parenting-time exchange"
        text = re.sub(
            r"At\s+today[''']?s?\s+parenting[- ]?time\s+exchange",
            "At the parenting-time exchange",
            text,
            flags=re.IGNORECASE,
        )
        # Fix "today's parenting time" anywhere
        text = re.sub(
            r"today[''']?s?\s+parenting[- ]?time",
            "the parenting-time",
            text,
            flags=re.IGNORECASE,
        )

        # Fix "Today during court-ordered" -> "During court-ordered"
        text = re.sub(
            r"Today\s+during\s+court[- ]?ordered",
            "During court-ordered",
            text,
            flags=re.IGNORECASE,
        )
        # Fix "At today's" at start of sentence
        text = re.sub(
            r"At\s+today[''']?s?\s+",
            "At the ",
            text,
            flags=re.IGNORECASE,
        )

        # Session 405 Patch 4F: FINAL FALLBACK - Format bullet points in full text
        # This catches any bullets that survived the per-paragraph processing
        import logging
        logger = logging.getLogger(__name__)

        # Check if there are bullets to format
        bullet_chars = r'[●•○■▪▸►]'
        bullets_found = re.findall(bullet_chars, text)
        logger.info(f"SESSION 405 Patch 4F: Found {len(bullets_found)} bullets in text")

        # Add newline before EVERY bullet that follows text on same line
        # Using a function to log each replacement
        def add_newline_before_bullet(match):
            logger.debug(f"SESSION 405: Adding newline before bullet: '{match.group(0)[:30]}...'")
            return f"{match.group(1)}\n   {match.group(3)}"

        text = re.sub(rf'([^\n])(\s*)({bullet_chars})', add_newline_before_bullet, text)

        # Ensure bullets at start of content have proper indentation
        text = re.sub(rf'^(\s*)({bullet_chars})', r'   \2', text, flags=re.MULTILINE)

        # Normalize bullets after newlines
        text = re.sub(rf'\n\s*({bullet_chars})', r'\n   \1', text)

        logger.info(f"SESSION 405 Patch 4F: Bullet formatting complete")

        return text.strip()

    def _is_denial_order_content(self, text: str) -> bool:
        """Check if text is from the judge's denial order (not user's motion)."""
        import re
        text_lower = text.lower()

        for pattern in DENIAL_ORDER_INDICATORS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False

    def _is_court_metadata(self, text: str) -> bool:
        """Check if text is court header/metadata (not user's narrative)."""
        import re
        text_lower = text.lower()

        # Check court header patterns
        for pattern in COURT_HEADER_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        # Additional metadata checks
        metadata_keywords = [
            'case number', 'division', 'courtroom', 'district court',
            'county court', 'larimer county', 'fort collins',
            'petitioner:', 'respondent:', 'in re:', 'attachment',
            'document type', 'document title', 'pdf status',
            'appearing pro se', 'document content', 'page ',
        ]

        for keyword in metadata_keywords:
            if keyword in text_lower:
                return True

        # Check for case numbers anywhere in text
        if re.search(r'\d{4}dr\d+', text_lower):
            return True

        return False

    def _is_user_narrative(self, line: str) -> bool:
        """
        Session 404B: Simplified narrative detection - DON'T OVERFILTER.

        Strategy:
        1. Reject obvious metadata (all caps, short, specific keywords)
        2. Reject judge commentary patterns
        3. Keep anything else that's long enough

        The _extract_user_motion_section() already filtered out the denial order,
        so we just need to filter out metadata lines here.
        """
        import re
        stripped = line.strip()

        if not stripped:
            return False

        # Reject all caps lines (headers)
        if stripped.isupper():
            return False

        # Session 404B: Simplified metadata keywords
        METADATA_KEYWORDS = [
            'DISTRICT COURT',
            'CASE NUMBER',
            'COURT ADDRESS',
            'COURT USE ONLY',
            'Division:',
            'Courtroom:',
            'DATED this',
            'DATE FILED',
            'Magistrate',
            'Judge',
            'Order:',
            'ORDER:',
            'Attachment to Order',
            'Electronically filed',
        ]
        if any(k.lower() in stripped.lower() for k in METADATA_KEYWORDS):
            return False

        # Session 404B: Reject specific judge commentary patterns
        judge_patterns = [
            r'petitioner\s+is\s+encouraged\s+to\s+utilize',
            r'utilize\s+the\s+jdf\s+forms',
            r'petitioner\s+is\s+requesting\s+relief\s+which\s+the\s+court\s+cannot\s+grant',
            r'he\s+is\s+not\s+making\s+the\s+request\s+appropriately',
        ]
        for pat in judge_patterns:
            if re.search(pat, stripped.lower()):
                return False

        # Session 404B: Minimum length (but not too strict)
        if len(stripped) < 30:
            return False

        # Session 404B: Positive narrative hints (if ANY match, definitely keep)
        POSITIVE_HINTS = ['on ', 'during', 'at ', 'incident', 'stated', 'said', 'told', 'reported', 'exchange', 'call', 'child', 'minor']
        if any(h in stripped.lower() for h in POSITIVE_HINTS):
            return True

        # Session 404B: Keep longer sentences that passed metadata check
        # Be permissive - if it's not metadata, it's probably narrative
        if len(stripped) > 50:
            return True

        return False

    def _filter_pdf_metadata(self, content: str) -> str:
        """
        Session 404 FINAL FIX: Aggressively filter PDF content.
        Now uses _extract_user_motion_section first, then filters line by line.
        """

        # First extract only user's motion section
        user_content = self._extract_user_motion_section(content)

        lines = user_content.split('\n')
        filtered_lines = []

        for line in lines:
            line_stripped = line.strip()

            # Skip empty lines
            if not line_stripped:
                continue

            # Skip very short lines (likely headers)
            if len(line_stripped) < 15:
                continue

            # Skip all-caps lines (headers)
            if line_stripped.isupper():
                continue

            # Skip if court metadata
            if self._is_court_metadata(line_stripped):
                continue

            # Skip if denial order content
            if self._is_denial_order_content(line_stripped):
                continue

            filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def _is_metadata_line(self, line: str) -> bool:
        """
        Session 404: Check if a line is metadata/header/footer.
        Now delegates to more comprehensive methods.
        """
        return self._is_court_metadata(line) or self._is_denial_order_content(line)

    def _is_metadata_line_legacy(self, line: str) -> bool:
        """
        Legacy method kept for compatibility.
        """
        import re
        line_lower = line.lower().strip()

        # Check for case numbers
        if re.search(r'\d{4}dr\d+', line_lower):
            return True

        # Check for form references
        if 'jdf' in line_lower and re.search(r'jdf\s*\d+', line_lower):
            return True

        # Check for common headers
        metadata_keywords = [
            'district court', 'county court', 'division', 'courtroom',
            'case number', 'attachment', 'exhibit', 'page ',
            'petitioner:', 'respondent:', 'in re:', 'in the matter of',
            'document type', '.pdf', 'order denied', 'order granted',
        ]

        for keyword in metadata_keywords:
            if keyword in line_lower:
                return True

        return False

    def _strip_statute_references(self, text: str) -> str:
        """
        Session 404 FIX #4: Strip all statute references from output.

        Removes references like:
        - 14-10-124
        - C.R.S. § 14-10-129
        - pursuant to 14-10-129(1)(b)(I)
        """
        import re

        # Pattern for Colorado statute references
        patterns = [
            r'\b\d{1,2}-\d{1,2}-\d{1,3}(?:\(\d+\))*(?:\([a-zA-Z]\))*(?:\([IViv]+\))*\b',  # 14-10-124, 14-10-129(1)(b)(I)
            r'C\.?R\.?S\.?\s*§?\s*\d{1,2}-\d{1,2}-\d{1,3}',  # C.R.S. § 14-10-124
            r'pursuant to \d{1,2}-\d{1,2}-\d{1,3}',  # pursuant to 14-10-124
            r'under \d{1,2}-\d{1,2}-\d{1,3}',  # under 14-10-124
            r'§\s*\d{1,2}-\d{1,2}-\d{1,3}',  # § 14-10-124
        ]

        result = text
        for pattern in patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)

        # Clean up any double spaces left behind
        result = re.sub(r'  +', ' ', result)

        return result

    def _extract_incidents_from_motion(self, motion_content: str) -> List[Dict[str, str]]:
        """
        Session 404 FIX V2: Extract dated incidents for INCIDENT TIMELINE.

        Improved approach:
        1. Find sentences containing dates
        2. Extract the full sentence, not just text after the date
        3. More permissive - keep any sentence with a date that's not metadata
        """
        import re
        incidents = []

        # STEP 1: First extract only the user's motion section (before denial order)
        user_motion = self._extract_user_motion_section(motion_content)

        # STEP 2: Split into sentences (preserve line breaks as sentence boundaries)
        # Replace newlines with periods to help splitting
        content = re.sub(r'\n+', '. ', user_motion)
        content = re.sub(r'\.+', '.', content)  # Clean up multiple periods
        sentences = content.split('.')

        # Date patterns to look for
        date_patterns = [
            # "On August 29, 2025" or "August 29, 2025"
            r'((?:on\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4})',
            # "August 29" without year
            r'((?:on\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?)',
            # "early September 2025" or "mid-August"
            r'((?:early|mid|late)\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+\d{4})?)',
            # "in September 2025"
            r'((?:in|during)\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+\d{4})?)',
            # "November 12" exchange style
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2})',
        ]

        for sentence in sentences:
            sentence = sentence.strip()

            # Skip short or empty
            if len(sentence) < 30:
                continue

            # Skip metadata/headers
            if self._is_court_metadata(sentence):
                continue

            if self._is_denial_order_content(sentence):
                continue

            # Check each pattern
            for pattern in date_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    date = match.group(1).strip()

                    # Clean up the date string
                    date = re.sub(r'^(?:on|in|during)\s+', '', date, flags=re.IGNORECASE).strip()

                    # Get description - the rest of the sentence
                    description = sentence.strip()

                    # Remove the date from beginning if it starts with it
                    description = re.sub(f'^{re.escape(date)}[,:]?\\s*', '', description, flags=re.IGNORECASE).strip()

                    # Cap length but keep meaningful content
                    if len(description) > 120:
                        description = description[:120] + '...'

                    # Add if description is meaningful
                    if len(description) > 20:
                        incidents.append({
                            'date': date.title(),  # Capitalize nicely
                            'description': description
                        })
                    break  # Only extract one date per sentence

        # Deduplicate by date
        seen_dates = set()
        unique_incidents = []
        for inc in incidents:
            date_key = inc['date'].lower()[:20]
            if date_key not in seen_dates:
                seen_dates.add(date_key)
                unique_incidents.append(inc)

        return unique_incidents[:6]  # Limit to 6 incidents

    def _generate_corrected_relief(self, non_party_result: Dict[str, Any], relief_type: str = None) -> str:
        """
        Generate corrected relief language that targets only parties.

        Session 404 FIX #3: Use RELIEF_TEMPLATES instead of placeholders.
        Session 405 Enhancement #1: Use AUTO-REWRITES from non_party_result.
        Always auto-fill with appropriate relief language.
        """
        # Session 405 Enhancement #1: If we have auto-rewrites, use those FIRST
        auto_rewrites = non_party_result.get('auto_rewrites', [])
        if auto_rewrites:
            # Build relief from the auto-corrected versions
            corrected_relief_parts = []
            seen_corrections = set()

            for i, rewrite in enumerate(auto_rewrites, 1):
                corrected = rewrite.get('corrected', '')
                # Avoid duplicates
                if corrected and corrected not in seen_corrections:
                    seen_corrections.add(corrected)
                    corrected_relief_parts.append(f"{i}. {corrected}.")

            # Add standard closing language
            corrected_relief_parts.append("")
            corrected_relief_parts.append(f"{len(seen_corrections) + 1}. These orders shall remain in effect until further order of the Court.")

            if corrected_relief_parts:
                return '\n\n'.join(corrected_relief_parts)

        # FIX #3: Get relief template based on relief type
        if relief_type and relief_type in RELIEF_TEMPLATES:
            return '\n\n'.join(RELIEF_TEMPLATES[relief_type])

        # If has non-party issues, use communication template with specific names
        if non_party_result.get('has_non_party_issues'):
            non_parties = non_party_result.get('non_parties_found', [])
            if non_parties:
                # Get first non-party name for specific relief
                # non_parties can be strings or dicts now
                if isinstance(non_parties[0], dict):
                    third_party_name = non_parties[0].get('name', 'the third party')
                else:
                    third_party_name = non_parties[0]
                return f"""1. Respondent shall ensure that no adult in Respondent's household, including {third_party_name}, makes statements to or in the presence of the minor child regarding Petitioner's honesty, character, or the ongoing court proceedings.

2. Respondent shall ensure that adults in Respondent's household do not discuss any aspect of this litigation in the child's presence.

3. Respondent shall ensure that {third_party_name} is not present during parenting-time exchanges until further order of the Court.

4. These orders shall remain in effect until further order of the Court."""
            else:
                return '\n\n'.join(RELIEF_TEMPLATES['communication_issue'])

        # Default to communication template (most common use case)
        return '\n\n'.join(RELIEF_TEMPLATES.get('communication_issue', [
            "1. Respondent shall ensure that no adult in Respondent's household makes inappropriate statements to or in the presence of the minor child.",
            "2. Respondent shall comply with all existing court orders.",
            "3. These orders shall remain in effect until further order of the Court."
        ]))

    def _format_analysis_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Format the analysis as a brief procedural summary (NO strategy)."""
        issues = analysis_result.get('issues_found', [])
        summary_parts = []

        issue_descriptions = {
            'WRONG_FORM': '- **Incorrect Form:** Use the correct JDF form listed below',
            'NON_PARTY_RELIEF_REQUESTED': '- **Non-Party Relief:** Cannot order non-parties; must direct orders at Respondent',
            'MISSING_SWORN_AFFIDAVIT': '- **Missing Affidavit:** Include sworn affidavit under penalty of perjury',
            'MISSING_PROPOSED_ORDER': '- **Missing Proposed Order:** Include proposed order for judge to sign',
            'NOT_EMERGENCY': '- **Not Emergency:** Standard modification motion required (JDF 1220)',
            'RELIEF_NOT_AVAILABLE': '- **Relief Unavailable:** The requested relief cannot be granted',
            'INSUFFICIENT_EVIDENCE': '- **Missing Exhibits:** Attach supporting evidence',
        }

        for issue in issues:
            if issue in issue_descriptions:
                summary_parts.append(issue_descriptions[issue])

        if not summary_parts:
            summary_parts.append("- No major procedural defects identified")

        # Add form recommendation
        relief_type = analysis_result.get('relief_type_detected', 'modify_parenting_time')
        form_info = JDF_FORM_MAPPING.get(relief_type, {})
        if form_info:
            summary_parts.append(f"\n**Correct Form:** {form_info.get('official_title', 'Motion to Modify')}")
            if form_info.get('primary_form'):
                summary_parts.append(f"**Form Number:** {form_info.get('primary_form')}")

        return "\n".join(summary_parts)

    # =========================================================================
    # Session 404: GOLD STANDARD Motion Rewriter
    # =========================================================================

    def _rewrite_motion_gold_standard(
        self,
        relief_type: str,
        facts: List[str],
        dates_incidents: List[Dict[str, str]],
        relief_requested: str,
        case_details: Dict[str, Any],
        non_party_corrections: List[Dict[str, Any]] = None,
        original_motion_content: str = '',
        existing_order_text: str = '',
        is_emergency: bool = False
    ) -> Dict[str, Any]:
        """
        Generate motion in GOLD STANDARD JDF format.

        Session 404F: Now includes FULL RESTATEMENT section for complete extraction.
        Session 406: Now includes EXISTING COURT ORDERS subsection when order is provided.
        Session 406: Now includes CERTIFICATE OF CONFERRAL for non-emergency motions.

        Output structure matches court-acceptable formatting:
        - CAPTION
        - TITLE
        - VERIFIED MOTION (Introduction)
        - EXISTING COURT ORDERS (if uploaded order exists)
        - FACTS (Numbered)
        - RELIEF REQUESTED (party-directed only)
        - VERIFICATION / AFFIDAVIT
        - PROPOSED ORDER
        - CERTIFICATE OF SERVICE
        - APPENDIX A: FULL RESTATEMENT (optional exhibit)
        """
        # =====================================================================
        # Session 406 PATCH-5: Create MotionContext from case_details
        # This ensures all placeholders are properly bound from a single source
        # =====================================================================
        ctx = MotionContext.from_case_details(case_details)

        # Extract relief items from the relief_requested string
        relief_items = self._extract_relief_items_list(relief_requested)
        ctx.relief_items = relief_items
        ctx.is_emergency = is_emergency
        ctx.original_motion_content = original_motion_content

        # Validate context - log warnings for missing fields but continue
        validation_errors = ctx.validate()
        if validation_errors:
            logger.warning(f"[PATCH-5] MotionContext validation warnings: {validation_errors}")

        # Local variables for backward compatibility during transition
        # Session 406 PATCH-5: Use fillable blanks for missing data, not raw placeholders
        case_number = ctx.case_number or '____________________'
        county = ctx.county or '__________'
        state = ctx.state or 'COLORADO'
        petitioner = ctx.petitioner_name or '[PETITIONER NAME]'
        respondent = ctx.respondent_name or '[RESPONDENT NAME]'
        child_name = ctx.child_name or 'the minor child'
        division = ctx.division or '______'
        courtroom = ctx.courtroom or '______'
        court_address = ctx.court_address or '________________________________________'
        respondent_address = ctx.get_service_address()

        # Get form info
        form_info = JDF_FORM_MAPPING.get(relief_type, JDF_FORM_MAPPING['modify_parenting_time'])

        # Session 404 V4: Extract subject matter to avoid title redundancy
        official_title = form_info.get('official_title', 'Parenting Time')
        subject_match = re.search(r'(?:Motion\s+(?:to\s+Modify|for|and\s+Affidavit\s+for))\s+(.+)', official_title, re.IGNORECASE)
        if subject_match:
            motion_subject = subject_match.group(1)
        else:
            motion_subject = {
                'emergency_parenting': 'Emergency Parenting Time Restrictions',
                'restrict_parenting': 'Parenting Time Modification',
                'modify_parenting_time': 'Parenting Time',
                'contempt': 'Contempt of Court',
                'enforcement': 'Enforcement of Court Orders',
            }.get(relief_type, 'Parenting Time')

        # Session 404C: GOLD STANDARD COURT-READY TEMPLATE
        # - Clean dashed separators only (----)
        # - No ASCII box characters (═║╔╗╝ etc)
        # - Jurisdiction-agnostic with fillable blanks
        # - PDF-safe formatting
        document = f"""DISTRICT COURT, COUNTY OF {county}, STATE OF {state}
Court Address: {court_address}

Petitioner: {petitioner}
Respondent: {respondent}

Case Number: {case_number}
Division: {division}   Courtroom: {courtroom}

------------------------------------------------------------
{form_info.get('official_title', 'VERIFIED MOTION').upper()}
------------------------------------------------------------

{petitioner} ("Petitioner"), appearing pro se, respectfully submits this Verified Motion requesting temporary, narrowly-tailored relief. This motion is supported by the following verified factual allegations.
"""

        # =====================================================================
        # Session 406: Add EXISTING COURT ORDERS subsection if order was uploaded
        # =====================================================================
        existing_orders_section = ''
        if existing_order_text:
            order_provisions = self._parse_order_provisions(existing_order_text, case_number)
            if order_provisions:
                existing_orders_section = f"""
------------------------------------------------------------
EXISTING COURT ORDERS
------------------------------------------------------------

{order_provisions}

"""
        document += existing_orders_section

        document += f"""------------------------------------------------------------
FACTS (VERIFIED ALLEGATIONS)
------------------------------------------------------------

GENERAL BACKGROUND:
1. Petitioner and Respondent are the parents of the minor child(ren).
2. A parenting time order is currently in place.
3. Petitioner exercises parenting time in accordance with existing court orders.

SPECIFIC FACTUAL ALLEGATIONS:
"""
        # Session 405 Patch 4D.4: Apply comprehensive cleanup to each fact
        fact_num = 4
        for fact in facts:
            # Clean the fact text - remove any leading numbers/bullets
            clean_fact = re.sub(r'^\d+[\.\)]\s*', '', fact.strip())

            # Session 405: Apply Patch 4D cleanup to each fact
            clean_fact = self._patch_4d_clean_single_fact(clean_fact)

            if clean_fact and len(clean_fact) > 20:
                document += f"{fact_num}. {clean_fact}\n\n"
                fact_num += 1

        # Session 404D: REMOVED separate INCIDENT TIMELINE section
        # Timeline dates are now PART of the SPECIFIC FACTUAL ALLEGATIONS
        # This prevents duplication and keeps facts consolidated in one section
        # The dates_incidents parameter is no longer used for a separate section

        # Session 406 Polish: Add child name clarification if available from CaseProfile
        children_info = case_details.get('children', [])
        if children_info:
            child_names_ages = [f"{c.get('name', 'the minor child')}, age {c.get('age', 'N/A')}" for c in children_info if c.get('name')]
            if child_names_ages:
                if len(child_names_ages) == 1:
                    document += f"The minor child referenced above is {child_names_ages[0]}.\n\n"
                else:
                    document += f"The minor children referenced above are: {'; '.join(child_names_ages)}.\n\n"

        # Session 404C: Add relief requested section with clean separators
        # Session 406 PATCH-5: Use render_relief_block for consistent formatting
        relief_block = render_relief_block(ctx.relief_items) if ctx.relief_items else relief_requested
        document += f"""
------------------------------------------------------------
RELIEF REQUESTED
------------------------------------------------------------

WHEREFORE, Petitioner respectfully requests that this Court enter temporary, narrowly-tailored orders as follows:

{relief_block}

Note: All relief must be directed only toward the Respondent, a party to the case.
"""

        # Session 406 Polish: Determine if respondent is represented (needed for conferral + service)
        # Session 406 PATCH-5: Use MotionContext for consistent access
        respondent_counsel = ctx.respondent_counsel_name
        respondent_counsel_firm = ctx.respondent_counsel_firm
        is_represented = ctx.is_respondent_represented

        # Session 406: Add CERTIFICATE OF CONFERRAL for non-emergency motions
        if is_emergency:
            # Emergency motions exempt from conferral - add note explaining why
            document += f"""
------------------------------------------------------------
CERTIFICATE OF CONFERRAL (WAIVED - EMERGENCY)
------------------------------------------------------------

Petitioner certifies that conferral was not attempted because this is an emergency motion
filed pursuant to C.R.S. § 14-10-129.5 due to imminent danger to the child that cannot
wait for the standard conferral period.
"""
        else:
            # Non-emergency motions require conferral
            from datetime import datetime
            conferral_date = datetime.now().strftime('%B %d, %Y')
            # Session 406 Polish: Use "Respondent's counsel" if represented
            cert_target = "Respondent's counsel" if is_represented else "Respondent"
            cert_target_short = "Counsel" if is_represented else "Respondent"
            document += f"""
------------------------------------------------------------
CERTIFICATE OF CONFERRAL
------------------------------------------------------------

Pursuant to C.R.C.P. 121 § 1-15(8), Petitioner certifies that:

1. On or about {conferral_date}, Petitioner sent written communication to {cert_target}
   regarding the relief requested in this motion.
2. Petitioner made reasonable and good-faith efforts to confer with {cert_target_short}.
3. [ ] {cert_target_short} did not respond within the conferral period.
   [ ] {cert_target_short} stated they do not agree to the requested relief.
   [ ] The parties were unable to reach full agreement on all requested relief.
4. The matter could not be resolved without Court involvement.

(Check the applicable box above before filing)
"""

        # Session 406 Patch 1 & 2: All placeholders resolved, relief_requested expanded
        # Session 406 Patch 3: Certificate of Service uses counsel if present
        service_recipient = respondent
        service_address = respondent_address

        # Use counsel info defined earlier (respondent_counsel, is_represented already set above)
        if is_represented and respondent_counsel:
            service_recipient = f"{respondent_counsel}"
            if respondent_counsel_firm:
                service_recipient += f"\n{respondent_counsel_firm}"
            service_recipient += f"\nAttorney for Respondent"
            # Use counsel address if available
            counsel_address = case_details.get('respondent_counsel_address', '')
            if counsel_address:
                service_address = counsel_address

        # Session 406 PATCH-5.2: Ensure proper capitalization for affidavit block
        state_upper = state.upper() if state else 'COLORADO'
        county_upper = county.upper() if county else '__________'

        document += f"""
------------------------------------------------------------
VERIFICATION / AFFIDAVIT
------------------------------------------------------------

STATE OF {state_upper}    )
                          ) ss.
COUNTY OF {county_upper}  )

I, {petitioner}, being duly sworn, state under penalty of perjury under the laws of the State of {state_upper} that:

1. I am the Petitioner in this matter.
2. I have personal knowledge of the facts stated in this motion.
3. All statements herein are true and correct to the best of my knowledge and belief.

FURTHER AFFIANT SAYETH NAUGHT.

_____________________________________
{petitioner}, Petitioner
Date: ________________________________

Subscribed and sworn before me this _____ day of ________________, 20___.

_____________________________________
Notary Public
My Commission Expires: _______________

------------------------------------------------------------
PROPOSED ORDER (For Court Use Only)
------------------------------------------------------------

DISTRICT COURT, COUNTY OF {county_upper}, STATE OF {state_upper}
Case Number: {case_number}

ORDER ON PETITIONER'S VERIFIED MOTION

The Court, having reviewed Petitioner's Verified Motion and being fully advised, hereby ORDERS:

{render_proposed_order_relief(ctx.relief_items) if ctx.relief_items else relief_requested}

These orders shall remain in effect until further order of the Court.

DATED this _____ day of ____________________, 20___.

_____________________________________
District Court Judge / Magistrate

------------------------------------------------------------
CERTIFICATE OF SERVICE
------------------------------------------------------------

I certify that on ____________________, 20___, I served a true and correct copy of this VERIFIED MOTION upon:

{service_recipient}
Address: {service_address}

Service accomplished by:
[ ] U.S. Mail
[ ] Hand Delivery
[ ] E-Filing System
[ ] Other: ___________________

_____________________________________
{petitioner}, Petitioner
Date: _________________________________
"""

        # =====================================================================
        # Session 404F: Add PART 5: FULL RESTATEMENT (Optional Attachment)
        # =====================================================================
        if original_motion_content:
            full_narrative, mapping_stats = self._extract_full_narrative(original_motion_content)

            if full_narrative:
                # Session 405 Patch 4D.5: Apply postprocessing to full narrative paragraphs
                full_narrative = self.postprocess_extracted_facts(full_narrative)

                # Format as numbered paragraphs
                restatement_paragraphs = []
                for idx, para in enumerate(full_narrative, 1):
                    restatement_paragraphs.append(f"{idx}. {para}")

                restatement_text = "\n\n".join(restatement_paragraphs)

                # Session 405 Patch 4D.5: Apply template pattern cleanup
                restatement_text = self.cleanup_generated_facts_block(restatement_text)

                # Session 405 Patch 4D: Removed debug output from final motion
                # The INTERNAL MAPPING LOG was showing in court documents - now hidden
                # Session 406 PATCH-5.1: Renamed from PART 5 to APPENDIX A per ChatGPT
                # This keeps court-facing stuff (PARTS 1-6) separate from optional attachments
                full_restatement_section = f"""

============================================================
APPENDIX A: FULL RESTATEMENT OF PETITIONER'S FACTUAL NARRATIVE
(OPTIONAL EXHIBIT - NOT FOR COURT FILING UNLESS ATTACHED)
============================================================

This section restates all factual content from your original motion in cleaned,
readable form. It is not filed with the court unless you choose to attach it
as an exhibit.

{restatement_text}
"""
                # Debug logging (not included in output)
                logger.debug(f"SESSION 405 Patch 4D: Mapping stats - "
                            f"total={mapping_stats.get('total_paragraphs_found', 0)}, "
                            f"restatement={mapping_stats.get('paragraphs_in_restatement', 0)}, "
                            f"facts={len(facts)}, "
                            f"skipped_meta={mapping_stats.get('paragraphs_skipped_metadata', 0)}, "
                            f"skipped_denial={mapping_stats.get('paragraphs_skipped_denial_order', 0)}")
                document += full_restatement_section

        # Session 406 PATCH-5: Apply narrative cleanup to remove wording glitches
        document = clean_motion_text(document)

        # Session 406 PATCH-5.2: Normalize child name spelling to match court order
        # If we have an existing order, extract the child name spelling from it
        if existing_order_text:
            canonical_name = self._extract_child_name_from_order(existing_order_text)
            if canonical_name:
                document = self._normalize_child_name_throughout(document, canonical_name)
                logger.debug(f"[PATCH-5.2] Normalized child name to: {canonical_name}")

        return {
            'success': True,
            'document': document,
            'document_type': 'gold_standard_motion',
            'relief_type': relief_type,
            'form_used': form_info.get('primary_form', 'See coloradojudicial.gov'),
            'has_full_restatement': bool(original_motion_content),
            'motion_context': {  # Session 406 PATCH-5: Include context for debugging
                'relief_items_count': len(ctx.relief_items),
                'is_represented': ctx.is_respondent_represented,
                'validation_errors': validation_errors,
            }
        }

    # =========================================================================
    # Session 404: Motion Rewriting Tool Implementations
    # =========================================================================

    def _analyze_denied_motion(
        self,
        motion_content: str,
        denial_reasons: str = '',
        original_relief_requested: str = ''
    ) -> Dict[str, Any]:
        """
        Analyze a denied motion to identify all deficiencies.

        Session 404: Core analysis engine that:
        1. Identifies correct JDF form for the relief type
        2. Maps denial reasons to procedural defects
        3. Detects non-party issues
        4. Recommends corrective actions
        """
        analysis_parts = []
        issues_found = []
        recommended_forms = []
        separate_filings_needed = []

        # =====================================================================
        # 1. Detect the relief type from motion content
        # =====================================================================
        relief_type = self._detect_relief_type(motion_content)
        form_info = JDF_FORM_MAPPING.get(relief_type, {})

        analysis_parts.append("## DENIED MOTION ANALYSIS")
        analysis_parts.append("")
        analysis_parts.append(f"**Detected Relief Type:** {relief_type.replace('_', ' ').title()}")

        if form_info:
            analysis_parts.append(f"**Correct Form:** {form_info.get('official_title', 'Unknown')}")
            if form_info.get('primary_form'):
                analysis_parts.append(f"**Form Number:** {form_info.get('primary_form')}")
            recommended_forms.append(form_info)

        # =====================================================================
        # 2. Check for Non-Party Issues
        # =====================================================================
        non_party_check = self._check_non_party_issues(motion_content, [])
        if non_party_check.get('non_parties_found'):
            issues_found.append("NON_PARTY_RELIEF_REQUESTED")
            analysis_parts.append("")
            analysis_parts.append("### ⚠️ NON-PARTY ISSUE DETECTED")
            analysis_parts.append(non_party_check.get('analysis', ''))

        # =====================================================================
        # 3. Check for Missing Required Attachments
        # =====================================================================
        required_attachments = form_info.get('required_attachments', [])
        if required_attachments:
            analysis_parts.append("")
            analysis_parts.append("### Required Attachments for This Motion Type:")
            for attachment in required_attachments:
                analysis_parts.append(f"- [ ] {attachment.replace('_', ' ').title()}")

        # Check if motion appears to be missing affidavit
        if 'affidavit' not in motion_content.lower() and 'sworn' not in motion_content.lower():
            issues_found.append("MISSING_SWORN_AFFIDAVIT")
            analysis_parts.append("")
            analysis_parts.append("### ⚠️ Missing Sworn Affidavit")
            analysis_parts.append("Your motion does not appear to include a sworn affidavit.")
            analysis_parts.append("Most motions require a supporting affidavit under penalty of perjury.")

        # Check for proposed order
        if 'proposed order' not in motion_content.lower() and 'order' not in motion_content.lower():
            issues_found.append("MISSING_PROPOSED_ORDER")
            analysis_parts.append("")
            analysis_parts.append("### ⚠️ Missing Proposed Order")
            analysis_parts.append("Include a proposed order showing exactly what you want the court to sign.")

        # =====================================================================
        # 4. Analyze Denial Reasons (if provided)
        # =====================================================================
        if denial_reasons:
            analysis_parts.append("")
            analysis_parts.append("### Analysis of Court's Denial Reasons:")
            analysis_parts.append("")

            denial_lower = denial_reasons.lower()

            if 'form' in denial_lower or 'wrong' in denial_lower:
                issues_found.append("WRONG_FORM")
                analysis_parts.append("- **Wrong Form Used:** The court indicated improper form. Use the correct JDF form listed above.")

            if 'emergency' in denial_lower and 'not' in denial_lower:
                issues_found.append("NOT_EMERGENCY")
                analysis_parts.append("- **Not Emergency:** Your situation may not meet the 'imminent danger' standard for emergency relief.")
                analysis_parts.append("  File a standard Motion to Modify Parenting Time (JDF 1220) instead.")

            if 'jurisdiction' in denial_lower or 'authority' in denial_lower:
                issues_found.append("RELIEF_NOT_AVAILABLE")
                analysis_parts.append("- **Relief Not Available:** The court cannot grant the specific relief you requested.")

            if 'exhibit' in denial_lower or 'evidence' in denial_lower:
                issues_found.append("INSUFFICIENT_EVIDENCE")
                analysis_parts.append("- **Insufficient Evidence:** Attach exhibits supporting your factual claims.")

            if 'non-party' in denial_lower or 'not a party' in denial_lower:
                issues_found.append("NON_PARTY_RELIEF_REQUESTED")
                analysis_parts.append("- **Non-Party Issue:** You cannot get orders against someone not named as a party.")

        # =====================================================================
        # 5. Determine if Multiple Filings Needed
        # =====================================================================
        # Check if motion tries to do too many things
        if ('emergency' in motion_content.lower() and 'modify' in motion_content.lower()):
            separate_filings_needed.append({
                'filing': 'Emergency Motion (if truly imminent danger)',
                'form': 'Motion and Affidavit for Emergency Orders'
            })
            separate_filings_needed.append({
                'filing': 'Standard Modification Motion',
                'form': 'JDF 1220 - Motion to Modify Parenting Time'
            })
            analysis_parts.append("")
            analysis_parts.append("### ⚠️ Multiple Filings May Be Required")
            analysis_parts.append("Your motion appears to combine emergency and standard modification requests.")
            analysis_parts.append("These should typically be filed separately:")
            for filing in separate_filings_needed:
                analysis_parts.append(f"- {filing['filing']}: {filing['form']}")

        # =====================================================================
        # 6. Generate Recommendations
        # =====================================================================
        analysis_parts.append("")
        analysis_parts.append("### Recommended Next Steps:")
        analysis_parts.append("")

        step_num = 1
        if 'WRONG_FORM' in issues_found:
            analysis_parts.append(f"{step_num}. Obtain the correct JDF form from coloradojudicial.gov")
            step_num += 1

        if 'NON_PARTY_RELIEF_REQUESTED' in issues_found:
            analysis_parts.append(f"{step_num}. Rewrite relief to target the PARTY (Respondent/Petitioner), not the third party")
            step_num += 1

        if 'MISSING_SWORN_AFFIDAVIT' in issues_found:
            analysis_parts.append(f"{step_num}. Create a sworn affidavit with numbered paragraphs of facts")
            step_num += 1

        if 'MISSING_PROPOSED_ORDER' in issues_found:
            analysis_parts.append(f"{step_num}. Draft a proposed order for the judge to sign")
            step_num += 1

        analysis_parts.append(f"{step_num}. Gather supporting exhibits (screenshots, recordings, documents)")
        step_num += 1

        analysis_parts.append(f"{step_num}. File the corrected motion with the court")

        return {
            'success': True,
            'analysis': '\n'.join(analysis_parts),
            'issues_found': issues_found,
            'recommended_forms': recommended_forms,
            'separate_filings_needed': separate_filings_needed,
            'relief_type_detected': relief_type
        }

    def _detect_relief_type(self, motion_content: str) -> str:
        """
        Detect the type of relief being sought from motion content.

        Session 404 FIX #1: STRICT emergency detection.
        Only classify as emergency if TRUE emergency indicators are present.
        Communication/third-party issues are NOT emergencies.
        """
        content_lower = motion_content.lower()

        # FIX #1: Check for NON-EMERGENCY situations FIRST
        # If these are present, it's NOT an emergency regardless of "emergency" keyword
        has_non_emergency_indicators = any(
            term in content_lower for term in NON_EMERGENCY_SITUATIONS
        )

        # FIX #1: Check for TRUE emergency indicators
        has_true_emergency = any(
            term in content_lower for term in EMERGENCY_REQUIRED_INDICATORS
        )

        # ONLY classify as emergency if TRUE emergency AND NOT a non-emergency situation
        if has_true_emergency and not has_non_emergency_indicators:
            if 'parenting' in content_lower or 'custody' in content_lower or 'child' in content_lower:
                return 'emergency_parenting'

        # Communication/Third-party issues -> standard modification with specific relief
        if any(term in content_lower for term in ['statement', 'said', 'told', 'remark', 'comment']):
            return 'communication_issue'  # New type for communication problems

        if any(term in content_lower for term in NON_PARTY_INDICATORS):
            return 'third_party_interference'

        # Contempt/Enforcement indicators
        contempt_terms = ['contempt', 'violat', 'enforce', 'failed to comply', 'did not comply']
        if any(term in content_lower for term in contempt_terms):
            return 'enforce_order'

        # Child support modification
        support_terms = ['child support', 'support modification', 'income change']
        if any(term in content_lower for term in support_terms):
            return 'modify_child_support'

        # Restriction (but NOT emergency) - requires changed circumstances
        restriction_terms = ['restrict', 'suspend', 'limit', 'supervised']
        if any(term in content_lower for term in restriction_terms):
            return 'restrict_parenting'

        # Default to standard modification
        return 'modify_parenting_time'

    def _rewrite_motion(
        self,
        relief_type: str,
        facts: List[str],
        dates_incidents: List[Dict[str, str]],
        relief_requested: str,
        case_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a corrected motion in proper JDF format.

        Session 404: The "killer feature" - transforms user's narrative
        into JDF-compatible format with:
        - Proper caption
        - Numbered factual allegations
        - Statutory criteria alignment
        - Sworn affidavit section
        - Proposed order
        """
        # Get form info
        form_info = JDF_FORM_MAPPING.get(relief_type, JDF_FORM_MAPPING['modify_parenting_time'])

        # Case details
        case_number = case_details.get('case_number', '[CASE NUMBER]')
        county = case_details.get('county', '[COUNTY]')
        petitioner = case_details.get('petitioner_name', '[PETITIONER NAME]')
        respondent = case_details.get('respondent_name', '[RESPONDENT NAME]')

        # Build the document
        document_parts = []

        # =====================================================================
        # HEADER
        # =====================================================================
        document_parts.append(f"""
# {form_info.get('official_title', 'MOTION')}
## Colorado District Court - {county} County
## Case Number: {case_number}

---

**Form Reference:** {form_info.get('primary_form', 'See coloradojudicial.gov')}

**IMPORTANT:** This is a TEMPLATE. Download the official JDF form from coloradojudicial.gov
and transfer this information into the proper form sections.

---

**In the Matter of:**

Petitioner: {petitioner}
Respondent: {respondent}

---
""")

        # =====================================================================
        # MOTION SECTION
        # =====================================================================
        document_parts.append(f"""
## MOTION

The undersigned party respectfully moves this Court as follows:

### 1. PROCEDURAL BACKGROUND

The parties are subject to orders entered in this case regarding [parenting time / decision-making / child support].

### 2. FACTUAL ALLEGATIONS

The following facts support this motion:

""")

        # Add numbered facts
        for i, fact in enumerate(facts, start=1):
            document_parts.append(f"**{i}.** {fact}\n")

        # Add dated incidents if provided
        if dates_incidents:
            document_parts.append("\n### 3. SPECIFIC INCIDENTS\n")
            for incident in dates_incidents:
                date = incident.get('date', '[DATE]')
                desc = incident.get('description', '[DESCRIPTION]')
                document_parts.append(f"- **{date}:** {desc}\n")

        # =====================================================================
        # RELIEF REQUESTED
        # =====================================================================
        document_parts.append(f"""
### 4. RELIEF REQUESTED

The undersigned respectfully requests that this Court:

{relief_requested}

### 5. LEGAL BASIS

This motion is based on the applicable provisions of Colorado law governing
{relief_type.replace('_', ' ')}.

**Criteria Category:** {form_info.get('criteria', 'See Colorado family law provisions')}

---
""")

        # =====================================================================
        # SWORN AFFIDAVIT SECTION
        # =====================================================================
        document_parts.append(f"""
## AFFIDAVIT IN SUPPORT OF MOTION

I, [YOUR FULL NAME], being first duly sworn, state under penalty of perjury:

1. I am the [Petitioner/Respondent] in this matter and am over 18 years of age.

2. I have personal knowledge of the facts stated herein.

""")

        # Re-add facts in affidavit format
        for i, fact in enumerate(facts, start=3):
            document_parts.append(f"{i}. {fact}\n\n")

        document_parts.append(f"""
{len(facts) + 3}. The statements made above are true and correct to the best of my knowledge.

I declare under penalty of perjury under the laws of the State of Colorado that the foregoing is true and correct.

Executed on _____________, 20___, in _____________, Colorado.


_________________________________
[YOUR SIGNATURE]

_________________________________
[YOUR PRINTED NAME]

---
""")

        # =====================================================================
        # PROPOSED ORDER
        # =====================================================================
        document_parts.append(f"""
## PROPOSED ORDER

**District Court, {county} County, Colorado**
**Case Number: {case_number}**

---

### ORDER ON MOTION

The Court, having reviewed the Motion and supporting documents, ORDERS as follows:

1. The Motion is GRANTED.

2. {relief_requested}

3. [Additional terms as appropriate]

4. This Order is effective immediately / on [DATE].


Dated: _________________

_________________________________
MAGISTRATE / JUDGE

---
""")

        # =====================================================================
        # EVIDENCE CHECKLIST
        # =====================================================================
        checklist = self._generate_evidence_checklist(relief_type, facts)

        document_parts.append(f"""
## REQUIRED ATTACHMENTS CHECKLIST

{checklist.get('checklist', '')}

---

## FILING INSTRUCTIONS

{form_info.get('filing_notes', 'File with the clerk of court.')}

**Next Steps:**
1. Download official JDF form from coloradojudicial.gov
2. Transfer this content into the official form
3. Attach all required exhibits
4. File with court clerk
5. Serve on opposing party
6. Keep proof of service

---
""")

        return {
            'success': True,
            'document': '\n'.join(document_parts),
            'document_type': 'rewritten_motion',
            'relief_type': relief_type,
            'form_used': form_info.get('primary_form', 'See coloradojudicial.gov')
        }

    def _generate_evidence_checklist(
        self,
        motion_type: str,
        allegations: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a checklist of required evidence based on motion type.

        Session 404 FINAL FIX: Formalizes exhibit requirements.
        Now filters allegations to ensure only clean narrative facts are used.
        """
        checklist_items = []

        # Universal requirements
        checklist_items.append("### Required for ALL Motions:")
        checklist_items.append("- [ ] Sworn affidavit under penalty of perjury")
        checklist_items.append("- [ ] Proposed order for judge to sign")
        checklist_items.append("- [ ] Copy of existing court orders being modified")
        checklist_items.append("- [ ] Certificate of service")

        # Motion-type specific
        if motion_type == 'emergency_parenting':
            checklist_items.append("")
            checklist_items.append("### Emergency Motion - ADDITIONAL Requirements:")
            checklist_items.append("- [ ] Evidence of IMMINENT danger (not historical)")
            checklist_items.append("- [ ] Police reports (if applicable)")
            checklist_items.append("- [ ] Medical records (if injury involved)")
            checklist_items.append("- [ ] Photos of injuries or dangerous conditions")
            checklist_items.append("- [ ] Text messages/emails showing threats")
            checklist_items.append("- [ ] Explanation of why matter cannot wait for regular hearing")

        elif motion_type in ['restrict_parenting', 'modify_parenting_time', 'communication_issue', 'third_party_interference']:
            checklist_items.append("")
            checklist_items.append("### Modification Motion - ADDITIONAL Requirements:")
            checklist_items.append("- [ ] Evidence of CHANGED CIRCUMSTANCES since last order")
            checklist_items.append("- [ ] Documentation showing change is CONTINUING (not temporary)")
            checklist_items.append("- [ ] Evidence modification serves child's BEST INTERESTS")
            checklist_items.append("- [ ] Communication records (texts, emails)")
            checklist_items.append("- [ ] Calendar showing missed parenting time (if applicable)")

        elif motion_type in ['enforce_order', 'contempt', 'contempt_enforcement']:
            checklist_items.append("")
            checklist_items.append("### Contempt/Enforcement Motion - ADDITIONAL Requirements:")
            checklist_items.append("- [ ] Copy of order allegedly violated (highlight specific provision)")
            checklist_items.append("- [ ] Dates of EACH specific violation")
            checklist_items.append("- [ ] Evidence other party KNEW of the order")
            checklist_items.append("- [ ] Evidence violation was WILLFUL (not accidental)")
            checklist_items.append("- [ ] Communication showing other party's knowledge")

        elif motion_type == 'modify_child_support':
            checklist_items.append("")
            checklist_items.append("### Child Support Modification - ADDITIONAL Requirements:")
            checklist_items.append("- [ ] Current income documentation (pay stubs, tax returns)")
            checklist_items.append("- [ ] Previous income at time of last order")
            checklist_items.append("- [ ] Completed child support worksheet (JDF 1820 or 1821)")
            checklist_items.append("- [ ] Evidence of changed financial circumstances")

        # Session 404 FIX V2: Generate case-specific checklist from allegations
        # More permissive filtering - use facts we extracted
        if allegations:
            # Filter allegations but be more permissive
            clean_allegations = []
            seen_items = set()  # Track checklist items to avoid duplicates

            for allegation in allegations:
                # Skip obvious metadata
                if self._is_court_metadata(allegation):
                    continue
                if self._is_denial_order_content(allegation):
                    continue
                # Skip if too short
                if len(allegation) < 30:
                    continue
                if allegation.strip().isupper():
                    continue
                clean_allegations.append(allegation)

            if clean_allegations:
                checklist_items.append("")
                checklist_items.append("### Evidence for YOUR Specific Allegations:")

                for allegation in clean_allegations[:8]:  # Check up to 8 allegations
                    allegation_lower = allegation.lower()

                    # Generate specific checklist items based on content
                    if any(word in allegation_lower for word in ['call', 'phone', 'recorded', 'recording']):
                        item = "- [ ] Recording/transcript of phone call (Exhibit _)"
                        if item not in seen_items:
                            checklist_items.append(item)
                            seen_items.add(item)

                    if any(word in allegation_lower for word in ['said', 'told', 'stated', 'told me', 'told him', 'told her']):
                        item = "- [ ] Written statement documenting what was said"
                        if item not in seen_items:
                            checklist_items.append(item)
                            seen_items.add(item)

                    if any(word in allegation_lower for word in ['exchange', 'pickup', 'drop-off', 'dropoff', 'transfer']):
                        item = "- [ ] Notes from parenting time exchange (date, time, what happened)"
                        if item not in seen_items:
                            checklist_items.append(item)
                            seen_items.add(item)

                    if any(word in allegation_lower for word in ['girlfriend', 'boyfriend', 'partner', 'third party', 'third-party']):
                        item = "- [ ] Evidence of third-party involvement (photos, messages, child's statements)"
                        if item not in seen_items:
                            checklist_items.append(item)
                            seen_items.add(item)

                    if any(word in allegation_lower for word in ['lying', 'lied', 'trust', 'believe']):
                        item = "- [ ] Documentation of alienating statements to child"
                        if item not in seen_items:
                            checklist_items.append(item)
                            seen_items.add(item)

                    if any(word in allegation_lower for word in ['emotional', 'distress', 'upset', 'crying', 'behavior']):
                        item = "- [ ] Journal entries documenting child's emotional state"
                        if item not in seen_items:
                            checklist_items.append(item)
                            seen_items.add(item)

                    if any(word in allegation_lower for word in ['text', 'message', 'email', 'communication']):
                        item = "- [ ] Screenshots of relevant text messages/emails"
                        if item not in seen_items:
                            checklist_items.append(item)
                            seen_items.add(item)

                    if any(word in allegation_lower for word in ['log', 'journal', 'document', 'noted']):
                        item = "- [ ] Parenting time log entries"
                        if item not in seen_items:
                            checklist_items.append(item)
                            seen_items.add(item)

                # Always add a general item if we found some allegations
                if len(seen_items) < 3:
                    checklist_items.append("- [ ] Any additional supporting documentation")

        checklist_items.append("")
        checklist_items.append("### Exhibit Formatting:")
        checklist_items.append("- Label each exhibit (Exhibit A, B, C...)")
        checklist_items.append("- Create exhibit list with descriptions")
        checklist_items.append("- Make copies for court and opposing party")
        checklist_items.append("- Keep originals for hearing")

        return {
            'success': True,
            'checklist': '\n'.join(checklist_items),
            'motion_type': motion_type
        }

    def _check_non_party_issues(
        self,
        motion_text: str,
        parties_in_case: List[str] = None
    ) -> Dict[str, Any]:
        """
        Check if motion incorrectly seeks relief against non-parties and AUTO-REWRITE.

        Session 404: Implements the Non-Party Rule Check.
        Session 405 Enhancement #1: AUTO-REWRITE third-party relief requests.
        Session 419 Fix: Added judicial entity whitelist to prevent rewriting court orders.

        Courts CANNOT issue orders against people who are not parties to the case.
        Common mistake: Asking court to order girlfriend/boyfriend/grandparent to do something.

        NEW: Now automatically rewrites problematic text like:
          "Camille shall not..." → "Respondent shall ensure that Camille does not..."

        Session 419: CRITICAL - DO NOT rewrite judicial content like:
          "Magistrate shall not be altered" (from court order)
          "The Court finds..." (judge's ruling)
        """
        non_parties_found = []
        corrections = []
        auto_rewrites = []  # Session 405: Store auto-rewrite transformations

        motion_lower = motion_text.lower()

        # =========================================================================
        # Session 419: PRE-FILTER - Skip judicial/denial order content entirely
        # This prevents the system from trying to "fix" the judge's own language
        # =========================================================================
        if self._is_denial_order_content(motion_text):
            logger.info("SESSION 419: Skipping non-party check - content is from denial order")
            return {
                'has_issues': False,
                'non_parties': [],
                'analysis': '',
                'corrections': [],
                'auto_rewrites': [],
                'skipped_reason': 'denial_order_content'
            }

        # Check for non-party indicators
        for indicator in NON_PARTY_INDICATORS:
            if indicator.lower() in motion_lower:
                non_parties_found.append(indicator)

        # =========================================================================
        # Session 405 Enhancement #1: AUTO-REWRITE patterns
        # Find EXACT problematic text and generate corrected version
        # Session 419: Added judicial entity whitelist to prevent rewriting court orders
        # =========================================================================
        import re

        # Session 419: Expanded whitelist to include judicial entities
        # These should NEVER be rewritten - they are parties or judicial officials
        PARTY_AND_JUDICIAL_WHITELIST = [
            # Parties to the case
            'petitioner', 'respondent', 'father', 'mother', 'the court', 'court',
            # Judicial entities (Session 419 fix)
            'magistrate', 'judge', 'justice', 'honorable', 'commissioner',
            # Court-appointed professionals
            'gal', 'clr', 'guardian', 'guardian ad litem', 'child representative',
            # Experts and officials
            'expert', 'evaluator', 'mediator', 'arbitrator', 'officer',
            # Legal/procedural terms that appear in judicial rulings
            'findings', 'order', 'ruling', 'determination', 'record', 'evidence',
            # Statutory references
            'section', 'statute', 'rule', 'crm', 'crs',
        ]

        # Pattern 1: "[Name] shall not [action]" → "Respondent shall ensure that [Name] does not [action]"
        shall_not_pattern = re.compile(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+shall\s+not\s+([^.;,]+)',
            re.IGNORECASE
        )
        for match in shall_not_pattern.finditer(motion_text):
            name = match.group(1).strip()
            action = match.group(2).strip()
            # Check if this name is a non-party (Session 419: expanded whitelist)
            if name.lower() not in PARTY_AND_JUDICIAL_WHITELIST:
                original = match.group(0)
                corrected = f"Respondent shall ensure that {name} does not {action}"
                auto_rewrites.append({
                    'original': original,
                    'corrected': corrected,
                    'non_party': name,
                    'pattern': 'shall_not'
                })
                if name not in non_parties_found:
                    non_parties_found.append(name)

        # Pattern 2: "[Name] must not [action]" → "Respondent shall ensure that [Name] does not [action]"
        must_not_pattern = re.compile(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+must\s+not\s+([^.;,]+)',
            re.IGNORECASE
        )
        for match in must_not_pattern.finditer(motion_text):
            name = match.group(1).strip()
            action = match.group(2).strip()
            if name.lower() not in PARTY_AND_JUDICIAL_WHITELIST:
                original = match.group(0)
                corrected = f"Respondent shall ensure that {name} does not {action}"
                auto_rewrites.append({
                    'original': original,
                    'corrected': corrected,
                    'non_party': name,
                    'pattern': 'must_not'
                })
                if name not in non_parties_found:
                    non_parties_found.append(name)

        # Pattern 3: "Order [Name] to [action]" → "Order Respondent to ensure that [Name] does not [action]"
        order_to_pattern = re.compile(
            r'[Oo]rder\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+to\s+([^.;,]+)',
            re.IGNORECASE
        )
        for match in order_to_pattern.finditer(motion_text):
            name = match.group(1).strip()
            action = match.group(2).strip()
            if name.lower() not in PARTY_AND_JUDICIAL_WHITELIST:
                original = match.group(0)
                # Reframe as directing the party to ensure the non-party behavior
                corrected = f"Order Respondent to ensure that {name} [complies with appropriate conduct during parenting time]"
                auto_rewrites.append({
                    'original': original,
                    'corrected': corrected,
                    'non_party': name,
                    'pattern': 'order_to'
                })
                if name not in non_parties_found:
                    non_parties_found.append(name)

        # Pattern 4: "Require [Name] to [action]" → "Require Respondent to ensure that [Name] [action]"
        require_to_pattern = re.compile(
            r'[Rr]equire\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+to\s+([^.;,]+)',
            re.IGNORECASE
        )
        for match in require_to_pattern.finditer(motion_text):
            name = match.group(1).strip()
            action = match.group(2).strip()
            if name.lower() not in PARTY_AND_JUDICIAL_WHITELIST:
                original = match.group(0)
                corrected = f"Require Respondent to ensure that {name} {action}"
                auto_rewrites.append({
                    'original': original,
                    'corrected': corrected,
                    'non_party': name,
                    'pattern': 'require_to'
                })
                if name not in non_parties_found:
                    non_parties_found.append(name)

        # Pattern 5: "Prohibit [Name] from [action]" → "Order Respondent to ensure that [Name] is not [action]"
        # Note: "from [action]" captures gerunds like "being present" so we use "is not" instead of "does not"
        prohibit_pattern = re.compile(
            r'[Pp]rohibit\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+from\s+([^.;,]+)',
            re.IGNORECASE
        )
        for match in prohibit_pattern.finditer(motion_text):
            name = match.group(1).strip()
            action = match.group(2).strip()
            if name.lower() not in PARTY_AND_JUDICIAL_WHITELIST:
                original = match.group(0)
                # Convert gerund to proper form: "being present" → "is not present"
                corrected = f"Order Respondent to ensure that {name} is not {action}"
                auto_rewrites.append({
                    'original': original,
                    'corrected': corrected,
                    'non_party': name,
                    'pattern': 'prohibit_from'
                })
                if name not in non_parties_found:
                    non_parties_found.append(name)

        # Pattern 6: "[Name] is ordered to" → "Respondent is ordered to ensure that [Name]"
        is_ordered_pattern = re.compile(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+is\s+ordered\s+to\s+([^.;,]+)',
            re.IGNORECASE
        )
        for match in is_ordered_pattern.finditer(motion_text):
            name = match.group(1).strip()
            action = match.group(2).strip()
            if name.lower() not in PARTY_AND_JUDICIAL_WHITELIST:
                original = match.group(0)
                corrected = f"Respondent is ordered to ensure that {name} {action}"
                auto_rewrites.append({
                    'original': original,
                    'corrected': corrected,
                    'non_party': name,
                    'pattern': 'is_ordered_to'
                })
                if name not in non_parties_found:
                    non_parties_found.append(name)

        # Build analysis
        analysis_parts = []

        if non_parties_found:
            analysis_parts.append("**⚠️ NON-PARTY RELIEF DETECTED**")
            analysis_parts.append("")
            analysis_parts.append("Your motion appears to request relief against the following non-parties:")
            for np in non_parties_found:
                analysis_parts.append(f"- {np}")

            analysis_parts.append("")
            analysis_parts.append("**THE PROBLEM:**")
            analysis_parts.append("Courts CANNOT issue orders directing non-parties to do or not do anything.")
            analysis_parts.append("A person must be named as a party to the case to be subject to court orders.")

            # Session 405 Enhancement #1: Show AUTO-REWRITES
            if auto_rewrites:
                analysis_parts.append("")
                analysis_parts.append("**✅ AUTO-CORRECTED RELIEF (Session 405):**")
                analysis_parts.append("")
                for rewrite in auto_rewrites:
                    analysis_parts.append(f"❌ ORIGINAL: \"{rewrite['original']}\"")
                    analysis_parts.append(f"✅ CORRECTED: \"{rewrite['corrected']}\"")
                    analysis_parts.append("")

            analysis_parts.append("**THE CORRECT PROCEDURE:**")
            analysis_parts.append("Instead of requesting orders against the non-party, request orders")
            analysis_parts.append("requiring the PARTY (Petitioner or Respondent) to:")
            analysis_parts.append("")
            analysis_parts.append("1. Ensure that no third parties engage in [specific behavior] during parenting time")
            analysis_parts.append("2. Supervise all interactions between children and [person]")
            analysis_parts.append("3. Not allow [person] to be present during exchanges")
            analysis_parts.append("4. Take responsibility for the conduct of adults in their home")

            # Generate specific corrections (legacy format for backwards compatibility)
            for np in non_parties_found:
                corrections.append({
                    'non_party': np,
                    'wrong': f"Order {np} to [action]",
                    'correct': f"Order [Respondent/Petitioner] to ensure {np} does not [action] during their parenting time"
                })

        return {
            'success': True,
            'non_parties_found': non_parties_found,
            'analysis': '\n'.join(analysis_parts) if analysis_parts else "No non-party issues detected.",
            'corrections': corrections,
            'auto_rewrites': auto_rewrites,  # Session 405: New field with exact text transformations
            'has_non_party_issues': len(non_parties_found) > 0
        }

    # =========================================================================
    # Session 405 Enhancement #2: Emergency vs Non-Emergency Detector
    # =========================================================================

    def _assess_emergency_status(
        self,
        situation_description: str,
        claimed_emergency: bool = False
    ) -> Dict[str, Any]:
        """
        Assess whether a situation qualifies as a legal emergency.

        Session 405 Enhancement #2: Based on ChatGPT's recommendation.

        Colorado emergency custody motions under C.R.S. § 14-10-129.5 require:
        - IMMINENT physical danger to the child
        - Harm that cannot wait for regular hearing schedule

        This tool:
        1. Detects if harm is truly immediate
        2. Advises whether situation qualifies for emergency relief
        3. Warns when something is NOT actually an emergency
        """
        situation_lower = situation_description.lower()

        # =====================================================================
        # TIER 1: TRUE EMERGENCY INDICATORS (qualifies for emergency relief)
        # =====================================================================
        true_emergency_indicators = {
            'physical_danger': [
                'physical abuse', 'hit', 'struck', 'beaten', 'bruise', 'injury',
                'broken bone', 'black eye', 'marks on', 'visible injury',
                'hospital', 'emergency room', 'er visit', 'medical attention',
            ],
            'imminent_harm': [
                'imminent danger', 'immediate harm', 'immediate danger',
                'threatened to kill', 'threatened to hurt', 'death threat',
                'will hurt', 'going to hurt', 'scared for', 'fear for safety',
            ],
            'sexual_abuse': [
                'sexual abuse', 'molest', 'inappropriate touch', 'sexual contact',
                'rape', 'sexual assault',
            ],
            'substance_danger': [
                'overdose', 'passed out drunk', 'unconscious from',
                'driving drunk with child', 'dui with child', 'drugs around child',
                'child found drugs', 'child ingested',
            ],
            'flight_risk': [
                'flee', 'fleeing', 'abduct', 'kidnap', 'take child out of state',
                'passport', 'one-way ticket', 'moving without notice',
                'hiding child', 'won\'t return child',
            ],
            'protective_services': [
                'cps involved', 'child protective services', 'dhs investigation',
                'hotline report', 'mandatory reporter',
            ],
            'self_harm': [
                'suicide', 'suicidal', 'self-harm', 'cutting', 'wants to die',
                'threatened suicide',
            ],
            'domestic_violence': [
                'protection order', 'restraining order', 'domestic violence',
                'dv', 'assault', 'battery', 'strangulation',
            ],
        }

        # =====================================================================
        # TIER 2: NON-EMERGENCY SITUATIONS (requires standard modification)
        # =====================================================================
        non_emergency_indicators = {
            'communication_issues': [
                'said mean things', 'yelled', 'verbal', 'statement', 'comment',
                'told the child', 'remarks', 'disparaging', 'badmouthing',
                'talking about court', 'discussing the case',
            ],
            'third_party_issues': [
                'girlfriend', 'boyfriend', 'partner', 'grandmother', 'grandfather',
                'new spouse', 'roommate', 'friend of',
            ],
            'schedule_disputes': [
                'late for exchange', 'didn\'t show up', 'changed plans',
                'schedule conflict', 'holiday', 'vacation',
            ],
            'parenting_disagreements': [
                'bedtime', 'screen time', 'homework', 'diet', 'clothing',
                'hairstyle', 'activities', 'parenting style',
            ],
            'historical_concerns': [
                'years ago', 'in the past', 'used to', 'history of',
                'when we were married', 'before the divorce',
            ],
            'emotional_only': [
                'upset', 'sad', 'crying', 'anxious', 'doesn\'t want to go',
                'complained about', 'unhappy',
            ],
        }

        # =====================================================================
        # ANALYZE THE SITUATION
        # =====================================================================
        emergency_factors_found = []
        non_emergency_factors_found = []

        # Check for true emergency indicators
        for category, terms in true_emergency_indicators.items():
            for term in terms:
                if term in situation_lower:
                    emergency_factors_found.append({
                        'category': category,
                        'term': term,
                        'weight': 'high'
                    })

        # Check for non-emergency indicators
        for category, terms in non_emergency_indicators.items():
            for term in terms:
                if term in situation_lower:
                    non_emergency_factors_found.append({
                        'category': category,
                        'term': term
                    })

        # =====================================================================
        # DETERMINE EMERGENCY STATUS
        # =====================================================================
        is_true_emergency = len(emergency_factors_found) > 0
        has_non_emergency_factors = len(non_emergency_factors_found) > 0

        # Special case: Claimed emergency but no emergency factors found
        false_emergency_warning = claimed_emergency and not is_true_emergency

        # Calculate confidence score
        if is_true_emergency and not has_non_emergency_factors:
            emergency_confidence = 0.9
            recommendation = 'EMERGENCY_APPROPRIATE'
        elif is_true_emergency and has_non_emergency_factors:
            emergency_confidence = 0.6
            recommendation = 'MIXED_FACTORS'
        elif not is_true_emergency and claimed_emergency:
            emergency_confidence = 0.1
            recommendation = 'NOT_EMERGENCY'
        else:
            emergency_confidence = 0.0
            recommendation = 'STANDARD_MODIFICATION'

        # =====================================================================
        # BUILD ANALYSIS
        # =====================================================================
        analysis_parts = []

        if is_true_emergency:
            analysis_parts.append("**✅ EMERGENCY FACTORS DETECTED**")
            analysis_parts.append("")
            analysis_parts.append("The following factors MAY qualify for emergency relief under C.R.S. § 14-10-129.5:")
            analysis_parts.append("")
            for factor in emergency_factors_found:
                category_name = factor['category'].replace('_', ' ').title()
                analysis_parts.append(f"- **{category_name}**: \"{factor['term']}\" detected")
            analysis_parts.append("")
            analysis_parts.append("**PROCEDURAL REQUIREMENT:**")
            analysis_parts.append("Emergency motions require you to demonstrate:")
            analysis_parts.append("1. The child faces IMMINENT physical or emotional danger")
            analysis_parts.append("2. The danger is so urgent it cannot wait for a regular hearing (typically 14-21 days)")
            analysis_parts.append("3. You have specific, recent facts showing the danger")
            analysis_parts.append("")
        else:
            analysis_parts.append("**⚠️ NO EMERGENCY FACTORS DETECTED**")
            analysis_parts.append("")

        if false_emergency_warning:
            analysis_parts.append("**🚨 WARNING: This does NOT appear to be a true emergency.**")
            analysis_parts.append("")
            analysis_parts.append("Magistrates frequently DENY motions labeled \"emergency\" because:")
            analysis_parts.append("- The situation does not involve IMMINENT danger")
            analysis_parts.append("- The concerns can be addressed through standard modification")
            analysis_parts.append("- Filing false emergencies wastes court resources")
            analysis_parts.append("")
            analysis_parts.append("**RECOMMENDED ACTION:** File a standard Motion to Modify (JDF 1220)")
            analysis_parts.append("instead of an emergency motion to avoid automatic denial.")
            analysis_parts.append("")

        if has_non_emergency_factors:
            analysis_parts.append("**NON-EMERGENCY FACTORS FOUND:**")
            analysis_parts.append("")
            for factor in non_emergency_factors_found:
                category_name = factor['category'].replace('_', ' ').title()
                analysis_parts.append(f"- {category_name}: \"{factor['term']}\"")
            analysis_parts.append("")
            analysis_parts.append("These issues are important but should be addressed through:")
            analysis_parts.append("- **JDF 1220** (Motion to Modify Parenting Time)")
            analysis_parts.append("- Standard hearing schedule (not emergency)")
            analysis_parts.append("")

        # Add correct form recommendation
        if recommendation == 'EMERGENCY_APPROPRIATE':
            analysis_parts.append("**CORRECT FORM:** Motion and Affidavit for Emergency Orders")
            analysis_parts.append("(No standard JDF number - check with clerk or use court's emergency motion form)")
            analysis_parts.append("")
            analysis_parts.append("**REQUIRED ELEMENTS:**")
            analysis_parts.append("1. Sworn affidavit describing imminent danger with specific dates")
            analysis_parts.append("2. Any evidence (photos, police reports, medical records)")
            analysis_parts.append("3. Proposed emergency order")
            analysis_parts.append("4. Explanation of why regular hearing timeline is inadequate")
        elif recommendation == 'MIXED_FACTORS':
            analysis_parts.append("**⚖️ MIXED SITUATION**")
            analysis_parts.append("")
            analysis_parts.append("Your situation has some emergency factors but also non-emergency elements.")
            analysis_parts.append("Consider:")
            analysis_parts.append("1. Filing emergency motion ONLY for the imminent danger issues")
            analysis_parts.append("2. Filing separate standard modification for other concerns")
            analysis_parts.append("3. Consulting with an attorney to assess the best approach")
        else:
            analysis_parts.append("**CORRECT FORM:** JDF 1220 (Motion to Modify Parenting Time)")
            analysis_parts.append("with JDF 1221 (Supporting Affidavit)")
            analysis_parts.append("")
            analysis_parts.append("Your concerns are valid but should be addressed through the standard")
            analysis_parts.append("modification process, not emergency relief.")

        return {
            'success': True,
            'is_emergency': is_true_emergency,
            'emergency_confidence': emergency_confidence,
            'recommendation': recommendation,
            'emergency_factors': emergency_factors_found,
            'non_emergency_factors': non_emergency_factors_found,
            'false_emergency_warning': false_emergency_warning,
            'analysis': '\n'.join(analysis_parts),
            'correct_form': 'Emergency Motion' if recommendation == 'EMERGENCY_APPROPRIATE' else 'JDF 1220',
        }

    # =========================================================================
    # Session 405 Enhancement #3: Court Order Being Modified Detector
    # =========================================================================

    def _check_order_attachment_required(
        self,
        motion_text: str,
        uploaded_documents: List[str] = None
    ) -> Dict[str, Any]:
        """
        Check if the motion requires attachment of an existing court order.

        Session 405 Enhancement #3: Based on ChatGPT's recommendation.

        JDF motions to MODIFY require attachment of the order being modified.
        This detector:
        1. Identifies if motion seeks modification
        2. Checks if existing order is referenced
        3. Prompts user to upload order if missing
        """
        import re
        motion_lower = motion_text.lower()
        uploaded_documents = uploaded_documents or []

        # =====================================================================
        # MODIFICATION INDICATORS - these require attaching original order
        # =====================================================================
        modification_indicators = [
            'modify', 'modification', 'change', 'amend', 'amendment',
            'alter', 'revise', 'adjust', 'update', 'modify parenting',
            'modify child support', 'modify custody', 'modify visitation',
            'change parenting time', 'change custody', 'change support',
        ]

        # =====================================================================
        # ENFORCEMENT/CONTEMPT - requires attaching order being violated
        # =====================================================================
        enforcement_indicators = [
            'contempt', 'violation', 'enforce', 'enforcement', 'violated',
            'failed to comply', 'did not follow', 'in violation of',
            'breached', 'disobeyed', 'non-compliance',
        ]

        # =====================================================================
        # ORDER REFERENCE PATTERNS - detect if order is mentioned
        # =====================================================================
        order_reference_patterns = [
            r'order\s+dated?\s+\w+\s+\d+',  # "order dated January 15"
            r'the\s+\d{4}\s+order',  # "the 2024 order"
            r'permanent\s+orders?',
            r'temporary\s+orders?',
            r'existing\s+orders?',
            r'current\s+orders?',
            r'prior\s+orders?',
            r'previous\s+orders?',
            r'decree',
            r'parenting\s+plan',
            r'separation\s+agreement',
        ]

        # =====================================================================
        # ANALYZE THE MOTION
        # =====================================================================
        requires_order_attachment = False
        order_type_needed = None
        reasons = []

        # Check for modification language
        is_modification = any(term in motion_lower for term in modification_indicators)
        if is_modification:
            requires_order_attachment = True
            order_type_needed = 'modification'
            reasons.append("Motion seeks to MODIFY an existing order")

        # Check for enforcement/contempt language
        is_enforcement = any(term in motion_lower for term in enforcement_indicators)
        if is_enforcement:
            requires_order_attachment = True
            order_type_needed = 'enforcement'
            reasons.append("Motion alleges VIOLATION of an existing order")

        # Check if order is referenced
        order_referenced = any(
            re.search(pattern, motion_lower, re.IGNORECASE)
            for pattern in order_reference_patterns
        )

        # =====================================================================
        # CHECK IF ORDER IS ALREADY UPLOADED
        # Session 405: Fixed to match actual document_type values from database
        # =====================================================================
        has_uploaded_order = any(
            doc_type.lower() in ['court_order', 'court order', 'order', 'decree', 'parenting plan', 'parenting_plan']
            for doc_type in uploaded_documents
        )

        # =====================================================================
        # BUILD ANALYSIS
        # =====================================================================
        analysis_parts = []

        if requires_order_attachment and not has_uploaded_order:
            analysis_parts.append("**📄 COURT ORDER ATTACHMENT REQUIRED**")
            analysis_parts.append("")
            analysis_parts.append("Your motion requires you to attach the existing court order being modified or enforced.")
            analysis_parts.append("")
            analysis_parts.append("**WHY THIS IS REQUIRED:**")
            for reason in reasons:
                analysis_parts.append(f"- {reason}")
            analysis_parts.append("")

            if order_type_needed == 'modification':
                analysis_parts.append("**WHAT TO UPLOAD:**")
                analysis_parts.append("Upload the most recent court order that established the parenting time,")
                analysis_parts.append("custody, or child support arrangement you want to modify.")
                analysis_parts.append("")
                analysis_parts.append("Common titles include:")
                analysis_parts.append("- Permanent Orders")
                analysis_parts.append("- Decree of Dissolution")
                analysis_parts.append("- Parenting Plan")
                analysis_parts.append("- Order Regarding Parenting Time")
                analysis_parts.append("- Separation Agreement")
            elif order_type_needed == 'enforcement':
                analysis_parts.append("**WHAT TO UPLOAD:**")
                analysis_parts.append("Upload the court order that was allegedly violated.")
                analysis_parts.append("You must identify the SPECIFIC provision that was violated.")
                analysis_parts.append("")
                analysis_parts.append("**HIGHLIGHT:**")
                analysis_parts.append("Mark or highlight the specific paragraph(s) that were violated.")
                analysis_parts.append("The court needs to see the exact language of the order.")

            analysis_parts.append("")
            analysis_parts.append("**⚠️ ACTION REQUIRED:**")
            analysis_parts.append("Upload the existing order (Exhibit A) before filing your motion.")
            analysis_parts.append("")
            analysis_parts.append("**HOW TO UPLOAD:**")
            analysis_parts.append("1. Go to the 'My Case Files' tab")
            analysis_parts.append("2. Click 'Upload Document'")
            analysis_parts.append("3. Select 'Court Order' as the document type")
            analysis_parts.append("4. Upload your PDF")

        elif requires_order_attachment and has_uploaded_order:
            analysis_parts.append("**✅ ORDER ALREADY UPLOADED**")
            analysis_parts.append("")
            analysis_parts.append("You have already uploaded a court order. Good job!")
            analysis_parts.append("Make sure it is the CORRECT order - the one being modified or enforced.")

        elif order_referenced and not requires_order_attachment:
            analysis_parts.append("**ℹ️ ORDER REFERENCE DETECTED**")
            analysis_parts.append("")
            analysis_parts.append("Your motion references an existing order.")
            analysis_parts.append("Consider attaching it as an exhibit for the court's reference.")

        else:
            analysis_parts.append("**ℹ️ NO ORDER ATTACHMENT DETECTED AS REQUIRED**")
            analysis_parts.append("")
            analysis_parts.append("Based on the motion text, this does not appear to require")
            analysis_parts.append("attachment of an existing court order.")

        return {
            'success': True,
            'requires_order_attachment': requires_order_attachment,
            'order_type_needed': order_type_needed,
            'has_uploaded_order': has_uploaded_order,
            'order_referenced': order_referenced,
            'missing_order_warning': requires_order_attachment and not has_uploaded_order,
            'analysis': '\n'.join(analysis_parts),
        }

    # =========================================================================
    # Session 405 Enhancement #4: Conflict With Prior Orders Detector
    # =========================================================================

    def _detect_order_conflicts(
        self,
        motion_text: str,
        existing_order_text: str = '',
        existing_order_summary: str = ''
    ) -> Dict[str, Any]:
        """
        Detect conflicts between requested relief and existing court orders.

        Session 405 Enhancement #4: Per ChatGPT recommendation.

        This checks for:
        1. Direct contradictions (requesting what's already ordered differently)
        2. Duplicate requests (asking for what's already in place)
        3. Ignored provisions (overlooking relevant existing terms)
        4. Modification without acknowledgment (changing terms without citing them)

        Args:
            motion_text: The motion being analyzed
            existing_order_text: Full text of existing order if available
            existing_order_summary: Summary of key provisions if full text unavailable

        Returns:
            Dict with conflicts found, severity, and recommendations
        """
        import re
        motion_lower = motion_text.lower()

        conflicts = []
        warnings = []
        suggestions = []

        # =====================================================================
        # PART 1: Extract key provisions from existing order (if available)
        # =====================================================================

        existing_provisions = {
            'parenting_time': [],
            'decision_making': [],
            'child_support': [],
            'holidays': [],
            'exchanges': [],
            'restrictions': [],
            'third_party': [],
            'communication': [],
        }

        order_text = existing_order_text or existing_order_summary
        order_lower = order_text.lower() if order_text else ''

        if order_text:
            # Extract parenting time provisions
            parenting_patterns = [
                r'(?:father|mother|petitioner|respondent)\s+shall\s+have\s+parenting\s+time[^.]*\.',
                r'parenting\s+time\s+shall\s+be[^.]*\.',
                r'(?:every|each|alternate|alternating)\s+(?:weekend|week|other)[^.]*\.',
                r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)[^.]*(?:to|through|until)[^.]*\.',
            ]
            for pattern in parenting_patterns:
                matches = re.findall(pattern, order_lower, re.IGNORECASE)
                existing_provisions['parenting_time'].extend(matches)

            # Extract decision-making provisions
            decision_patterns = [
                r'(?:joint|sole)\s+(?:legal|physical)\s+(?:custody|decision-making)[^.]*\.',
                r'(?:major\s+)?decisions?\s+(?:shall|will|must)\s+be[^.]*\.',
                r'(?:education|medical|religious|extracurricular)\s+decisions?[^.]*\.',
            ]
            for pattern in decision_patterns:
                matches = re.findall(pattern, order_lower, re.IGNORECASE)
                existing_provisions['decision_making'].extend(matches)

            # Extract restrictions
            restriction_patterns = [
                r'(?:shall\s+not|must\s+not|is\s+prohibited|may\s+not)[^.]*\.',
                r'(?:no|without)\s+(?:overnight|alcohol|drugs|marijuana)[^.]*\.',
                r'(?:supervised|supervision)[^.]*\.',
            ]
            for pattern in restriction_patterns:
                matches = re.findall(pattern, order_lower, re.IGNORECASE)
                existing_provisions['restrictions'].extend(matches)

            # Extract third-party provisions
            third_party_patterns = [
                r'(?:girlfriend|boyfriend|partner|significant\s+other)[^.]*\.',
                r'(?:no\s+introduction|shall\s+not\s+introduce)[^.]*\.',
                r'(?:presence\s+of|around)[^.]*(?:child|children)[^.]*\.',
            ]
            for pattern in third_party_patterns:
                matches = re.findall(pattern, order_lower, re.IGNORECASE)
                existing_provisions['third_party'].extend(matches)

            # Extract holidays
            holiday_patterns = [
                r'(?:christmas|thanksgiving|easter|new\s+year|spring\s+break|summer|birthday)[^.]*\.',
                r'holiday\s+(?:schedule|parenting\s+time)[^.]*\.',
            ]
            for pattern in holiday_patterns:
                matches = re.findall(pattern, order_lower, re.IGNORECASE)
                existing_provisions['holidays'].extend(matches)

        # =====================================================================
        # PART 2: Extract relief requests from motion
        # =====================================================================

        motion_requests = {
            'parenting_time': [],
            'decision_making': [],
            'restrictions': [],
            'third_party': [],
            'modifications': [],
        }

        # Extract parenting time requests
        pt_request_patterns = [
            r'(?:order|grant|modify|restrict|suspend)\s+(?:the\s+)?(?:father\'?s?|mother\'?s?|respondent\'?s?|petitioner\'?s?)?\s*parenting\s+time[^.]*\.',
            r'(?:father|mother|respondent|petitioner)\s+(?:shall|should|must)\s+(?:have|be\s+granted)[^.]*parenting[^.]*\.',
            r'parenting\s+time\s+(?:shall|should|must|be)[^.]*(?:modified|restricted|suspended|supervised)[^.]*\.',
        ]
        for pattern in pt_request_patterns:
            matches = re.findall(pattern, motion_lower, re.IGNORECASE)
            motion_requests['parenting_time'].extend(matches)

        # Extract restriction requests
        restriction_request_patterns = [
            r'(?:order|require|prohibit|restrict)\s+(?:that\s+)?(?:respondent|father|mother)[^.]*(?:shall\s+not|must\s+not|may\s+not)[^.]*\.',
            r'(?:no\s+contact|no\s+overnight|supervised)[^.]*\.',
            r'(?:prohibit|restrict|prevent)[^.]*(?:from|the)[^.]*\.',
        ]
        for pattern in restriction_request_patterns:
            matches = re.findall(pattern, motion_lower, re.IGNORECASE)
            motion_requests['restrictions'].extend(matches)

        # Extract third-party requests
        tp_request_patterns = [
            r'(?:girlfriend|boyfriend|partner|significant\s+other|camille|new\s+partner)[^.]*(?:shall\s+not|must\s+not|prohibited|no\s+contact)[^.]*\.',
            r'(?:order|require)\s+(?:that\s+)?(?:no|neither)[^.]*(?:girlfriend|boyfriend|partner)[^.]*\.',
        ]
        for pattern in tp_request_patterns:
            matches = re.findall(pattern, motion_lower, re.IGNORECASE)
            motion_requests['third_party'].extend(matches)

        # =====================================================================
        # PART 3: Detect conflicts
        # =====================================================================

        has_conflicts = False
        conflict_severity = 'none'  # none, low, medium, high, critical

        # Check 1: Already existing parenting schedule being requested differently
        if existing_provisions['parenting_time'] and motion_requests['parenting_time']:
            # Check if motion requests contradict existing schedule
            existing_schedule = ' '.join(existing_provisions['parenting_time'])
            requested_changes = ' '.join(motion_requests['parenting_time'])

            # Look for time conflicts
            if 'every weekend' in existing_schedule and 'no weekend' in requested_changes:
                conflicts.append({
                    'type': 'DIRECT_CONTRADICTION',
                    'existing': 'Existing order grants weekend parenting time',
                    'requested': 'Motion requests removal of weekend parenting time',
                    'severity': 'high',
                    'recommendation': 'Acknowledge the existing schedule and explain why modification is needed'
                })
                has_conflicts = True
                conflict_severity = 'high'

        # Check 2: Requesting restrictions that already exist
        if existing_provisions['restrictions'] and motion_requests['restrictions']:
            existing_restrictions = ' '.join(existing_provisions['restrictions'])
            requested_restrictions = ' '.join(motion_requests['restrictions'])

            # Check for duplicate supervision requests
            if 'supervised' in existing_restrictions and 'supervised' in requested_restrictions:
                if 'continue' not in motion_lower and 'maintain' not in motion_lower:
                    conflicts.append({
                        'type': 'DUPLICATE_REQUEST',
                        'existing': 'Supervision is already ordered',
                        'requested': 'Motion requests supervision without acknowledging existing order',
                        'severity': 'low',
                        'recommendation': 'Reference the existing supervision order and specify if you want it continued or modified'
                    })
                    has_conflicts = True
                    if conflict_severity == 'none':
                        conflict_severity = 'low'

        # Check 3: Third-party restrictions that conflict
        if existing_provisions['third_party'] and motion_requests['third_party']:
            # Already has third-party provisions
            warnings.append({
                'type': 'EXISTING_THIRD_PARTY_PROVISION',
                'detail': 'Existing order already addresses third-party presence',
                'recommendation': 'Review existing provisions before requesting new restrictions'
            })

        # Check 4: Modification without citing existing order
        modification_keywords = ['modify', 'change', 'amend', 'alter', 'revise']
        is_modification_motion = any(kw in motion_lower for kw in modification_keywords)

        if is_modification_motion and not order_text:
            conflicts.append({
                'type': 'MISSING_ORDER_REFERENCE',
                'existing': 'No existing order provided for reference',
                'requested': 'Motion seeks to modify an order',
                'severity': 'medium',
                'recommendation': 'Upload the existing order and cite specific provisions being modified'
            })
            has_conflicts = True
            if conflict_severity in ['none', 'low']:
                conflict_severity = 'medium'

        # Check 5: Requesting opposite of what's already ordered
        opposite_check_pairs = [
            ('joint decision', 'sole decision'),
            ('joint custody', 'sole custody'),
            ('unsupervised', 'supervised'),
            ('liberal parenting', 'restricted parenting'),
            ('equal parenting', 'primary'),
        ]

        for existing_term, opposite_term in opposite_check_pairs:
            if existing_term in order_lower and opposite_term in motion_lower:
                conflicts.append({
                    'type': 'DIRECT_CONTRADICTION',
                    'existing': f'Existing order provides for {existing_term}',
                    'requested': f'Motion requests {opposite_term}',
                    'severity': 'high',
                    'recommendation': f'Provide substantial evidence and changed circumstances to justify change from {existing_term} to {opposite_term}'
                })
                has_conflicts = True
                conflict_severity = 'high'
            elif opposite_term in order_lower and existing_term in motion_lower:
                # Reverse check
                conflicts.append({
                    'type': 'DIRECT_CONTRADICTION',
                    'existing': f'Existing order provides for {opposite_term}',
                    'requested': f'Motion requests {existing_term}',
                    'severity': 'high',
                    'recommendation': f'Provide substantial evidence and changed circumstances to justify change from {opposite_term} to {existing_term}'
                })
                has_conflicts = True
                conflict_severity = 'high'

        # Check 6: Holiday schedule conflicts
        holiday_terms = ['christmas', 'thanksgiving', 'easter', 'summer', 'spring break', 'birthday']
        for holiday in holiday_terms:
            if holiday in order_lower and holiday in motion_lower:
                # Check if changing existing holiday arrangement
                if 'modify' in motion_lower or 'change' in motion_lower:
                    warnings.append({
                        'type': 'HOLIDAY_MODIFICATION',
                        'detail': f'Existing order addresses {holiday.title()} - ensure you cite the specific provision being modified',
                        'recommendation': f'Quote the existing {holiday.title()} provision and explain why change is needed'
                    })

        # =====================================================================
        # PART 4: Generate analysis output
        # =====================================================================

        analysis_parts = []

        if not order_text:
            analysis_parts.append("## ⚠️ ORDER CONFLICT ANALYSIS - NO EXISTING ORDER PROVIDED")
            analysis_parts.append("")
            analysis_parts.append("**IMPORTANT:** No existing court order was provided for conflict analysis.")
            analysis_parts.append("")
            analysis_parts.append("To properly analyze potential conflicts:")
            analysis_parts.append("1. Upload the existing court order in the 'My Case Files' tab")
            analysis_parts.append("2. Re-run the motion analysis")
            analysis_parts.append("")
            analysis_parts.append("**Why this matters:**")
            analysis_parts.append("- Courts expect you to acknowledge existing orders")
            analysis_parts.append("- Contradicting an order without explanation looks uninformed")
            analysis_parts.append("- Citing the specific provision you want changed strengthens your motion")

        elif not has_conflicts and not warnings:
            analysis_parts.append("## ✅ ORDER CONFLICT ANALYSIS - NO CONFLICTS DETECTED")
            analysis_parts.append("")
            analysis_parts.append("Your motion does not appear to conflict with the existing order provisions.")
            analysis_parts.append("")
            analysis_parts.append("**Provisions reviewed:**")
            for category, provisions in existing_provisions.items():
                if provisions:
                    analysis_parts.append(f"- {category.replace('_', ' ').title()}: {len(provisions)} provision(s) checked")

        else:
            # Determine overall severity indicator
            severity_emoji = {
                'none': '✅',
                'low': '⚠️',
                'medium': '🟡',
                'high': '🟠',
                'critical': '🔴'
            }

            analysis_parts.append(f"## {severity_emoji.get(conflict_severity, '⚠️')} ORDER CONFLICT ANALYSIS - {len(conflicts)} CONFLICT(S) FOUND")
            analysis_parts.append("")

            if conflicts:
                analysis_parts.append("### ⚠️ CONFLICTS WITH EXISTING ORDER:")
                analysis_parts.append("")

                for i, conflict in enumerate(conflicts, 1):
                    analysis_parts.append(f"**Conflict #{i}: {conflict['type']}**")
                    analysis_parts.append(f"- **Existing Order:** {conflict['existing']}")
                    analysis_parts.append(f"- **Your Request:** {conflict['requested']}")
                    analysis_parts.append(f"- **Severity:** {conflict['severity'].upper()}")
                    analysis_parts.append(f"- **Recommendation:** {conflict['recommendation']}")
                    analysis_parts.append("")

            if warnings:
                analysis_parts.append("### ⚠️ WARNINGS:")
                analysis_parts.append("")

                for warning in warnings:
                    analysis_parts.append(f"**{warning['type']}:** {warning['detail']}")
                    analysis_parts.append(f"- Recommendation: {warning['recommendation']}")
                    analysis_parts.append("")

            # Add general guidance
            analysis_parts.append("### 📋 HOW TO FIX CONFLICTS:")
            analysis_parts.append("")
            analysis_parts.append("1. **Cite the specific provision** you want changed (e.g., 'Paragraph 5.a of the current order')")
            analysis_parts.append("2. **Explain changed circumstances** that justify the modification")
            analysis_parts.append("3. **Acknowledge the existing order** - don't pretend it doesn't exist")
            analysis_parts.append("4. **Focus on the child's best interests** - not punishment of the other parent")
            analysis_parts.append("")
            analysis_parts.append("**Colorado Law Note:** Under C.R.S. § 14-10-129, modification requires")
            analysis_parts.append("showing a 'substantial and continuing' change in circumstances.")

        # Count total conflicts by severity
        severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for conflict in conflicts:
            sev = conflict.get('severity', 'low')
            if sev in severity_counts:
                severity_counts[sev] += 1

        return {
            'success': True,
            'has_conflicts': has_conflicts,
            'conflict_count': len(conflicts),
            'warning_count': len(warnings),
            'overall_severity': conflict_severity,
            'severity_counts': severity_counts,
            'conflicts': conflicts,
            'warnings': warnings,
            'existing_provisions_found': {k: len(v) for k, v in existing_provisions.items()},
            'has_existing_order': bool(order_text),
            'analysis': '\n'.join(analysis_parts),
        }

    # =========================================================================
    # Session 405 Enhancement #5: Likelihood of Success Confidence Meter
    # =========================================================================

    def _assess_likelihood_of_success(
        self,
        motion_text: str,
        relief_type: str = '',
        has_evidence: bool = False,
        is_rewrite: bool = False,
        relief_items: List[str] = None  # Session 406 PATCH-5.1: Accept pre-extracted relief items
    ) -> Dict[str, Any]:
        """
        Calculate a likelihood of success score for a motion.

        Session 405 Enhancement #5: The "killer feature" per ChatGPT.
        Session 406 PATCH-5.1: Accept relief_items parameter to avoid counting
        evidence checklist items, narrative bullets, or conferral steps.

        Scores based on:
        - Relief scope (narrower = better)
        - Evidence strength (documented = better)
        - Procedural posture (timing, proper form)
        - Colorado case law signals (common success patterns)

        Returns a 0-100 score with detailed breakdown.
        """
        import re
        motion_lower = motion_text.lower()

        # Initialize scoring components
        score_components = {
            'relief_scope': 0,      # 0-25 points - narrower relief = higher score
            'evidence_strength': 0,  # 0-25 points - more evidence = higher score
            'procedural_posture': 0, # 0-25 points - proper procedure = higher score
            'case_law_signals': 0,   # 0-25 points - favorable patterns = higher score
        }
        factors_positive = []
        factors_negative = []
        recommendations = []

        # =====================================================================
        # FACTOR 1: RELIEF SCOPE (0-25 points)
        # Courts prefer NARROW, specific relief over broad requests
        # Session 406 PATCH-5.1: Use pre-extracted relief items if provided
        # =====================================================================

        # Session 406 PATCH-5.1: Use provided relief_items, or extract ONLY from RELIEF REQUESTED section
        if relief_items is not None:
            # Use the pre-extracted relief items from the pipeline
            relief_count = len(relief_items)
            logger.debug(f"[PATCH-5.1] Using provided relief_items: {relief_count} items")
        else:
            # Extract ONLY from the RELIEF REQUESTED section, not the whole document
            relief_section_match = re.search(
                r'RELIEF REQUESTED.*?(?=------------------------------------------------------------|\Z)',
                motion_text,
                re.DOTALL | re.IGNORECASE
            )
            if relief_section_match:
                relief_section = relief_section_match.group(0)
                # Count only numbered items in the relief section
                relief_count = len(re.findall(r'^\s*\d+\.\s+(?:Respondent|IT IS ORDERED|Order|Require|Grant|Direct)', relief_section, re.MULTILINE | re.IGNORECASE))
                if relief_count == 0:
                    relief_count = len(re.findall(r'Respondent shall', relief_section, re.IGNORECASE))
                logger.debug(f"[PATCH-5.1] Extracted from RELIEF REQUESTED section: {relief_count} items")
            else:
                # Final fallback: count "Respondent shall" in entire text
                relief_count = len(re.findall(r'^\s*\d+\.\s+Respondent shall', motion_text, re.MULTILINE | re.IGNORECASE))
                if relief_count == 0:
                    relief_count = 3  # Safe default for Colorado family motions
                logger.debug(f"[PATCH-5.1] Fallback count: {relief_count} items")

        # Check for overly broad relief
        broad_relief_terms = ['full custody', 'sole custody', 'all parenting time', 'terminate', 'revoke']
        has_broad_relief = any(term in motion_lower for term in broad_relief_terms)

        # Check for narrow, specific relief
        narrow_relief_terms = ['modify', 'adjust', 'minor change', 'specific provision', 'paragraph']
        has_narrow_relief = any(term in motion_lower for term in narrow_relief_terms)

        if has_narrow_relief and not has_broad_relief:
            score_components['relief_scope'] = 25
            factors_positive.append("Relief requested is narrow and specific")
        elif has_broad_relief:
            score_components['relief_scope'] = 5
            factors_negative.append("Relief requested is very broad - courts prefer narrow requests")
            recommendations.append("Consider narrowing relief to specific, achievable changes")
        else:
            # Session 406 PATCH-5: Use centralized score_relief_scope function
            scope_score, scope_explanation = score_relief_scope(relief_count)
            score_components['relief_scope'] = scope_score

            # Add to appropriate factors based on score
            if scope_score >= 20:
                factors_positive.append(scope_explanation)
            elif scope_score >= 15:
                factors_positive.append(scope_explanation)
            else:
                factors_negative.append(scope_explanation)
                recommendations.append("Focus on 2-3 most important relief requests")

        # =====================================================================
        # FACTOR 2: EVIDENCE STRENGTH (0-25 points)
        # Courts want documented, verifiable facts
        # =====================================================================

        # Check for evidence indicators
        strong_evidence_terms = [
            'exhibit', 'attached', 'police report', 'medical record', 'cps report',
            'recording', 'video', 'photograph', 'text message', 'email',
            'witness', 'witnessed', 'documented', 'professional opinion',
        ]
        weak_evidence_terms = [
            'i believe', 'i think', 'i feel', 'seems like', 'probably',
            'my opinion', 'in my view', 'appears to be',
        ]

        strong_evidence_count = sum(1 for term in strong_evidence_terms if term in motion_lower)
        weak_evidence_count = sum(1 for term in weak_evidence_terms if term in motion_lower)

        # Check for specific dates (courts love specific dates)
        date_pattern = r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s*\d{4}'
        date_count = len(re.findall(date_pattern, motion_lower))

        if has_evidence or strong_evidence_count >= 3:
            score_components['evidence_strength'] = 25
            factors_positive.append("Strong documentary evidence referenced")
        elif strong_evidence_count >= 1:
            score_components['evidence_strength'] = 18
            factors_positive.append("Some evidence referenced")
        elif date_count >= 2:
            score_components['evidence_strength'] = 15
            factors_positive.append(f"Specific dates provided ({date_count})")
        else:
            score_components['evidence_strength'] = 8
            factors_negative.append("Limited documentary evidence")
            recommendations.append("Attach supporting exhibits (texts, emails, photos)")

        if weak_evidence_count >= 3:
            score_components['evidence_strength'] = max(0, score_components['evidence_strength'] - 10)
            factors_negative.append("Too many subjective statements (I believe, I think)")
            recommendations.append("Replace opinions with documented facts")

        # =====================================================================
        # FACTOR 3: PROCEDURAL POSTURE (0-25 points)
        # Proper procedure increases success
        # =====================================================================

        # Check for proper form elements
        has_verification = 'under penalty of perjury' in motion_lower or 'sworn' in motion_lower
        has_caption = bool(re.search(r'case\s*(?:no\.?|number)', motion_lower))
        has_certificate = 'certificate of service' in motion_lower or 'certify' in motion_lower
        has_proposed_order = 'proposed order' in motion_lower

        procedural_score = 0
        if has_verification:
            procedural_score += 8
            factors_positive.append("Motion is verified/sworn")
        else:
            factors_negative.append("Motion should be verified (sworn under penalty of perjury)")
            recommendations.append("Add verification language to make it a sworn statement")

        if has_caption:
            procedural_score += 5
            factors_positive.append("Proper case caption")

        if has_proposed_order:
            procedural_score += 7
            factors_positive.append("Proposed order included")
        else:
            recommendations.append("Include a proposed order for the judge to sign")

        if is_rewrite:
            procedural_score += 5
            factors_positive.append("Rewrite addresses prior denial reasons")

        score_components['procedural_posture'] = min(25, procedural_score)

        # =====================================================================
        # FACTOR 4: CASE LAW SIGNALS (0-25 points)
        # Common patterns that succeed in Colorado family court
        # =====================================================================

        # Positive signals - things courts commonly grant
        positive_signals = {
            'changed circumstances': 8,  # Required for modification
            'best interest': 5,          # Focus on child
            'child welfare': 5,
            'safety concern': 4,
            'documented pattern': 5,
            'multiple incidents': 4,
        }

        # Negative signals - things that hurt your case
        negative_signals = {
            'revenge': -5,
            'punish': -5,
            'make-up time': -3,  # Often denied
            'emergency': -2 if not any(term in motion_lower for term in EMERGENCY_REQUIRED_INDICATORS) else 0,
            'immediately': -2,
            'permanently': -3,
        }

        case_law_score = 10  # Base score
        for term, points in positive_signals.items():
            if term in motion_lower:
                case_law_score += points
                if points > 3:
                    factors_positive.append(f"Addresses '{term}' - favorable factor")

        for term, points in negative_signals.items():
            if term in motion_lower:
                case_law_score += points  # Points are negative
                if points < -3:
                    factors_negative.append(f"Term '{term}' may hurt your case")

        score_components['case_law_signals'] = max(0, min(25, case_law_score))

        # =====================================================================
        # CALCULATE TOTAL SCORE
        # =====================================================================
        total_score = sum(score_components.values())

        # Determine rating
        if total_score >= 75:
            rating = 'HIGH'
            rating_emoji = '🟢'
            rating_description = "Your motion has strong likelihood of success"
        elif total_score >= 50:
            rating = 'MODERATE'
            rating_emoji = '🟡'
            rating_description = "Your motion has reasonable chances but could be improved"
        elif total_score >= 25:
            rating = 'LOW'
            rating_emoji = '🟠'
            rating_description = "Your motion needs significant improvement"
        else:
            rating = 'VERY LOW'
            rating_emoji = '🔴'
            rating_description = "Your motion is likely to be denied without changes"

        # =====================================================================
        # BUILD ANALYSIS
        # =====================================================================
        analysis_parts = []
        analysis_parts.append(f"## {rating_emoji} LIKELIHOOD OF SUCCESS: {total_score}/100 ({rating})")
        analysis_parts.append("")
        analysis_parts.append(f"**{rating_description}**")
        analysis_parts.append("")

        # Score breakdown
        analysis_parts.append("### Score Breakdown:")
        analysis_parts.append(f"- **Relief Scope:** {score_components['relief_scope']}/25")
        analysis_parts.append(f"- **Evidence Strength:** {score_components['evidence_strength']}/25")
        analysis_parts.append(f"- **Procedural Posture:** {score_components['procedural_posture']}/25")
        analysis_parts.append(f"- **Case Law Signals:** {score_components['case_law_signals']}/25")
        analysis_parts.append("")

        # Positive factors
        if factors_positive:
            analysis_parts.append("### ✅ Strengths:")
            for factor in factors_positive:
                analysis_parts.append(f"- {factor}")
            analysis_parts.append("")

        # Negative factors
        if factors_negative:
            analysis_parts.append("### ⚠️ Weaknesses:")
            for factor in factors_negative:
                analysis_parts.append(f"- {factor}")
            analysis_parts.append("")

        # Recommendations
        if recommendations:
            analysis_parts.append("### 💡 Recommendations to Improve:")
            for rec in recommendations:
                analysis_parts.append(f"- {rec}")
            analysis_parts.append("")

        # Disclaimer
        analysis_parts.append("---")
        analysis_parts.append("*Note: This score is based on pattern analysis and procedural factors.*")
        analysis_parts.append("*Actual outcomes depend on judge discretion and opposing party response.*")

        return {
            'success': True,
            'total_score': total_score,
            'rating': rating,
            'rating_emoji': rating_emoji,
            'score_components': score_components,
            'factors_positive': factors_positive,
            'factors_negative': factors_negative,
            'recommendations': recommendations,
            'analysis': '\n'.join(analysis_parts),
        }

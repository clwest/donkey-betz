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
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


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
        }
    ]

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
            except Exception:
                pass
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
            "3. Reference appropriate Colorado JDF forms when applicable",
            "4. Focus on procedural guidance, not legal strategy",
            "5. Generated documents should be clearly marked as TEMPLATES",
            "",
            "Colorado Family Law Context:",
            "- Governing statutes: C.R.S. Title 14 (Domestic Matters)",
            "- Court: District Court, Family Division",
            "- Forms: JDF (Judicial Department Forms) series",
            "",
        ]

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
                # Look for recent denied motions or court orders that might be relevant
                recent_docs = LegalDocument.objects.filter(
                    user=self.user,
                    document_type__in=['denied_motion', 'court_order']
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

            return None

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

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

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
        # STEP 3: Extract facts from motion for rewrite
        # =====================================================================
        facts = self._extract_facts_from_motion(motion_content)
        # Session 405 Patch 4D.5: Apply comprehensive postprocessing cleanup
        facts = self.postprocess_extracted_facts(facts)
        incidents = self._extract_incidents_from_motion(motion_content)
        relief_type = analysis_result.get('relief_type_detected', 'modify_parenting_time')

        # =====================================================================
        # STEP 3.5: Extract case metadata from PDF (Session 404 V3)
        # =====================================================================
        logger.info("Step 3.5: Extracting case metadata...")
        extracted_metadata = self._extract_case_metadata(motion_content)
        # Merge with any existing case_details from context
        case_details = context.get('case_details', {})
        # Only use extracted values if context doesn't already have them
        for key, value in extracted_metadata.items():
            if value and not case_details.get(key):
                case_details[key] = value
        logger.info(f"Case metadata: case_number={case_details.get('case_number')}, "
                   f"petitioner={case_details.get('petitioner_name')}, "
                   f"respondent={case_details.get('respondent_name')}")

        # =====================================================================
        # STEP 4: Generate rewritten motion in JDF format
        # =====================================================================
        logger.info("Step 3: Generating rewritten motion...")
        # FIX #3: Pass relief_type to get correct template
        corrected_relief = self._generate_corrected_relief(non_party_result, relief_type=relief_type)
        # Session 404F: Pass original motion content for FULL RESTATEMENT section
        rewrite_result = self._rewrite_motion_gold_standard(
            relief_type=relief_type,
            facts=facts,
            dates_incidents=incidents,
            relief_requested=corrected_relief,
            case_details=case_details,  # Now with extracted metadata
            non_party_corrections=non_party_result.get('corrections', []),
            original_motion_content=motion_content  # For 1:1 mapping guarantee
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

        # FIX #6: NO LEGAL DISCLAIMER - removed per ChatGPT feedback
        # The disclaimer was confusing and contradicting the procedural-only approach

        execution_time = int((time.time() - start_time) * 1000)

        result = AgentResult(
            success=True,
            message="\n".join(output_parts),
            data={
                'type': 'denied_motion_rewrite',
                'pipeline_executed': True,
                'tools_called': [t['tool'] for t in tool_calls_made],
                'relief_type': relief_type,
                'non_party_issues': non_party_result.get('has_non_party_issues', False),
                'facts_extracted': len(facts),
                'incidents_extracted': len(incidents),
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
        import re
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

    def _build_clean_allegations(self, incidents: List[Dict[str, str]], original_content: str) -> List[str]:
        """
        Session 405 Patch 4E: Build clean numbered allegations with PROPER SEGMENTATION.

        This completely rewrites fact extraction to produce discrete, numbered facts
        that judges expect:
        1. On [date], [incident 1]
        2. On [date], [incident 2]
        3. [Third party status - who Camille Johnson is NOT]
        4. [Respondent's failures]
        5. [Impact statement]
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        allegations = []

        # Session 405 Patch 4E: Build structured allegations from content segments

        # SEGMENT 1-3: Date-based incidents
        for i, incident in enumerate(incidents[:3]):
            date_str = incident.get('date_string', '')
            desc = incident.get('description', '')

            # LIMIT description length - if too long, truncate to first sentence
            if len(desc) > 300:
                # Find first sentence ending
                first_sentence = re.match(r'^[^.!?]+[.!?]', desc)
                if first_sentence:
                    desc = first_sentence.group(0)
                else:
                    desc = desc[:250] + '...'

            # Ensure it starts with "On [date]" if date is available
            if date_str and date_str not in ['Unknown date', 'The following week', 'Today', 'That same time']:
                if not re.match(r'^(?:On\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)', desc, re.IGNORECASE):
                    desc = f"On {date_str}, {desc[0].lower()}{desc[1:]}" if desc else f"On {date_str}."
            elif date_str in ['The following week', 'Today', 'That same time']:
                if not desc.lower().startswith(date_str.lower()):
                    desc = f"{date_str}, {desc[0].lower()}{desc[1:]}" if desc else f"{date_str}."

            desc = re.sub(r'\s+', ' ', desc).strip()
            if desc and desc[-1] not in '.!?':
                desc += '.'

            if desc and len(desc) > 30:
                allegations.append(desc)
                logger.debug(f"Patch 4E: Allegation {i+1}: {desc[:60]}...")

        # SEGMENT 4: Third-party status (Camille Johnson is NOT...)
        third_party_segment = self._extract_third_party_segment(original_content)
        if third_party_segment:
            allegations.append(third_party_segment)
            logger.debug(f"Patch 4E: Third-party segment added")

        # SEGMENT 5: Respondent's failures
        respondent_segment = self._extract_respondent_failures_segment(original_content)
        if respondent_segment:
            allegations.append(respondent_segment)
            logger.debug(f"Patch 4E: Respondent failures segment added")

        # SEGMENT 6: Impact/pattern statement
        impact_paragraph = self._generate_impact_paragraph(incidents, original_content)
        if impact_paragraph:
            allegations.append(impact_paragraph)
            logger.debug(f"Patch 4E: Impact paragraph added")

        return allegations

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
            matches = re.findall(f'[^.]*{pattern}[^.]*\\.?', original_content, re.IGNORECASE)
            for match in matches[:1]:
                # Session 405: Clean up the harm phrase before adding
                clean_match = match.strip()
                # Remove any "These X incidents demonstrate a pattern of" prefix
                clean_match = re.sub(r'^These\s+\d+\s+incidents\s+demonstrate\s+a?\s*pattern\s+of\s*', '', clean_match, flags=re.IGNORECASE)
                # Remove "this pattern is" at the start
                clean_match = re.sub(r'^this\s+pattern\s+is\s+', '', clean_match, flags=re.IGNORECASE)
                if clean_match and len(clean_match) > 10:
                    harm_phrases.append(clean_match)

        # Build impact paragraph - Session 405: Only create ONE pattern statement
        num_incidents = len(incidents)

        # Add harm description
        if harm_phrases:
            # Use petitioner's language but clean it
            harm_text = harm_phrases[0].strip()
            harm_text = re.sub(r'^\W+', '', harm_text)  # Remove leading punctuation
            if harm_text:
                harm_text = harm_text[0].lower() + harm_text[1:]
                # Session 405: Build clean impact statement
                if num_incidents >= 2:
                    impact = f"These {num_incidents} documented incidents demonstrate a pattern of {harm_text}"
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

        if impact and not impact[-1] in '.!?':
            impact += '.'
        if impact:
            impact = impact[0].upper() + impact[1:]

        return impact

    def _default_impact_text(self, num_incidents: int) -> str:
        """Session 405: Default impact text when no harm phrases found."""
        if num_incidents >= 2:
            return f"These {num_incidents} documented incidents demonstrate a pattern of conduct that exposes the child to inappropriate adult conflict and interferes with the parent-child relationship."
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
        petitioner_patterns = [
            r'Petitioner[\s:]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)[,\s]+Petitioner',
            r'Petitioner[\s:]*\n\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'In\s+Re.*?Marriage.*?([A-Z][a-z]+\s+[A-Z][a-z]+)\s+and',
        ]
        for pattern in petitioner_patterns:
            match = re.search(pattern, header_section)
            if match:
                name = match.group(1).strip()
                # Skip if it's a common word
                if name.lower() not in ['the court', 'district court', 'colorado']:
                    metadata['petitioner_name'] = name.title()
                    break

        # Extract respondent name
        respondent_patterns = [
            r'Respondent[\s:]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)[,\s]+Respondent',
            r'Respondent[\s:]*\n\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'and\s+([A-Z][a-z]+\s+[A-Z][a-z]+)[,\s]*Respondent',
        ]
        for pattern in respondent_patterns:
            match = re.search(pattern, header_section)
            if match:
                name = match.group(1).strip()
                if name.lower() not in ['the court', 'district court', 'colorado']:
                    metadata['respondent_name'] = name.title()
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
        address_patterns = [
            r'Court\s+Address[\s:]*([^\n]+(?:\n[^\n]+)?)',
            r'(\d+\s+\w+(?:\s+\w+)*(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Way)[^\n]*)',
        ]
        for pattern in address_patterns:
            match = re.search(pattern, header_section, re.IGNORECASE)
            if match:
                addr = match.group(1).strip()
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
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        if not fact:
            return ''

        cleaned = fact.strip()

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

        # Session 405 Patch 4G: Fix "Today's Incident" to use actual date
        # The motion is filed later, so "Today" is incorrect
        text = re.sub(
            r"Today'?s?\s+Incident\s*[-–—]\s*",
            "The Incident on ",
            text,
            flags=re.IGNORECASE,
        )
        # Also fix "At today's parenting-time exchange" -> "At the parenting-time exchange on [date]"
        text = re.sub(
            r"At\s+today'?s?\s+parenting[- ]time\s+exchange",
            "At the parenting-time exchange",
            text,
            flags=re.IGNORECASE,
        )
        # Fix "Today during court-ordered" -> "On [date] during court-ordered"
        text = re.sub(
            r"Today\s+during\s+court[- ]ordered",
            "During court-ordered",
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
        import re

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
        Always auto-fill with appropriate relief language.
        """
        # FIX #3: Get relief template based on relief type
        if relief_type and relief_type in RELIEF_TEMPLATES:
            return '\n\n'.join(RELIEF_TEMPLATES[relief_type])

        # If has non-party issues, use communication template
        if non_party_result.get('has_non_party_issues'):
            non_parties = non_party_result.get('non_parties_found', [])
            if non_parties:
                # Get first non-party name for specific relief
                third_party_name = non_parties[0].get('name', 'the third party')
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
        original_motion_content: str = ''
    ) -> Dict[str, Any]:
        """
        Generate motion in GOLD STANDARD JDF format.

        Session 404F: Now includes FULL RESTATEMENT section for complete extraction.

        Output structure matches court-acceptable formatting:
        - CAPTION
        - TITLE
        - VERIFIED MOTION (Introduction)
        - FACTS (Numbered)
        - RELIEF REQUESTED (party-directed only)
        - VERIFICATION / AFFIDAVIT
        - PROPOSED ORDER
        - CERTIFICATE OF SERVICE
        - PART 5: FULL RESTATEMENT (all user content, cleaned)
        """
        # Case details with placeholders - Session 404 V3: Use extracted metadata
        case_number = case_details.get('case_number') or '____________________'
        county = case_details.get('county') or '__________'
        petitioner = case_details.get('petitioner_name') or '[PETITIONER NAME]'
        respondent = case_details.get('respondent_name') or '[RESPONDENT NAME]'
        child_name = case_details.get('child_name') or 'the minor child'
        division = case_details.get('division') or '______'
        courtroom = case_details.get('courtroom') or '______'
        court_address = case_details.get('court_address') or '________________________________________'

        # Get form info
        form_info = JDF_FORM_MAPPING.get(relief_type, JDF_FORM_MAPPING['modify_parenting_time'])

        # Session 404 V4: Extract subject matter to avoid title redundancy
        # e.g., "Motion to Modify Parenting Time" -> "Parenting Time"
        import re
        official_title = form_info.get('official_title', 'Parenting Time')
        # Extract just the subject matter (after "Motion to Modify", "Motion for", etc.)
        subject_match = re.search(r'(?:Motion\s+(?:to\s+Modify|for|and\s+Affidavit\s+for))\s+(.+)', official_title, re.IGNORECASE)
        if subject_match:
            motion_subject = subject_match.group(1)
        else:
            # If no match, use a simple default based on relief type
            motion_subject = {
                'emergency_parenting': 'Emergency Parenting Time Restrictions',
                'restrict_parenting': 'Parenting Time Modification',
                'modify_parenting_time': 'Parenting Time',
                'contempt': 'Contempt of Court',
                'enforcement': 'Enforcement of Court Orders',
            }.get(relief_type, 'Parenting Time')

        # Session 404D: County/State Autofill Logic
        # ONLY fill if BOTH are confidently extracted from the user's document
        # Never hardcode - leave blank for universal use
        extracted_county = case_details.get('county')
        extracted_state = case_details.get('state')

        # If both are extracted, use them; otherwise leave both blank
        if extracted_county and extracted_state:
            county = extracted_county
            state = extracted_state
        else:
            county = '__________'
            state = '__________'

        # Session 404C: Get respondent address (fillable blank if not available)
        respondent_address = case_details.get('respondent_address') or '_____________________________________'

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

------------------------------------------------------------
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

        # Session 404C: Add relief requested section with clean separators
        document += f"""
------------------------------------------------------------
RELIEF REQUESTED
------------------------------------------------------------

WHEREFORE, Petitioner respectfully requests that this Court enter temporary, narrowly-tailored orders as follows:

{relief_requested}

Note: All relief must be directed only toward the Respondent, a party to the case.

------------------------------------------------------------
VERIFICATION / AFFIDAVIT
------------------------------------------------------------

STATE OF {state}       )
                       ) ss.
COUNTY OF {county}     )

I, {petitioner}, being duly sworn, state under penalty of perjury under the laws of the State of {state} that:

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

DISTRICT COURT, COUNTY OF {county}, STATE OF {state}
Case Number: {case_number}

ORDER ON PETITIONER'S VERIFIED MOTION

The Court, having reviewed Petitioner's Verified Motion and being fully advised, hereby ORDERS:

{relief_requested}

These orders shall remain in effect until further order of the Court.

DATED this _____ day of ____________________, 20___.

_____________________________________
District Court Judge / Magistrate

------------------------------------------------------------
CERTIFICATE OF SERVICE
------------------------------------------------------------

I certify that on ____________________, 20___, I served a true and correct copy of this VERIFIED MOTION upon:

Respondent: {respondent}
Address: {respondent_address}

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
                full_restatement_section = f"""

============================================================
PART 5: FULL RESTATEMENT OF PETITIONER'S FACTUAL NARRATIVE
(OPTIONAL ATTACHMENT - NOT FOR COURT FILING UNLESS ATTACHED AS EXHIBIT)
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

        return {
            'success': True,
            'document': document,
            'document_type': 'gold_standard_motion',
            'relief_type': relief_type,
            'form_used': form_info.get('primary_form', 'See coloradojudicial.gov'),
            'has_full_restatement': bool(original_motion_content)
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
        Check if motion incorrectly seeks relief against non-parties.

        Session 404: Implements the Non-Party Rule Check.

        Courts CANNOT issue orders against people who are not parties to the case.
        Common mistake: Asking court to order girlfriend/boyfriend/grandparent to do something.
        """
        non_parties_found = []
        corrections = []

        motion_lower = motion_text.lower()

        # Check for non-party indicators
        for indicator in NON_PARTY_INDICATORS:
            if indicator.lower() in motion_lower:
                non_parties_found.append(indicator)

        # Check for "order [person] to" patterns with non-party names
        order_patterns = [
            r'order\s+(\w+)\s+to',
            r'require\s+(\w+)\s+to',
            r'direct\s+(\w+)\s+to',
            r'(\w+)\s+shall\s+not',
            r'(\w+)\s+must\s+not',
            r'prohibit\s+(\w+)',
        ]

        import re
        for pattern in order_patterns:
            matches = re.findall(pattern, motion_lower)
            for match in matches:
                # Check if matched name is a non-party indicator
                for indicator in NON_PARTY_INDICATORS:
                    if indicator.lower() in match.lower():
                        if indicator not in non_parties_found:
                            non_parties_found.append(indicator)

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

            analysis_parts.append("")
            analysis_parts.append("**THE CORRECT PROCEDURE:**")
            analysis_parts.append("Instead of requesting orders against the non-party, request orders")
            analysis_parts.append("requiring the PARTY (Petitioner or Respondent) to:")
            analysis_parts.append("")
            analysis_parts.append("1. Ensure that no third parties engage in [specific behavior] during parenting time")
            analysis_parts.append("2. Supervise all interactions between children and [person]")
            analysis_parts.append("3. Not allow [person] to be present during exchanges")
            analysis_parts.append("4. Take responsibility for the conduct of adults in their home")

            analysis_parts.append("")
            analysis_parts.append("**EXAMPLE CORRECTION:**")
            analysis_parts.append("")
            analysis_parts.append("❌ WRONG: \"Order Camille Johnson to not yell at the children\"")
            analysis_parts.append("")
            analysis_parts.append("✅ CORRECT: \"Order Respondent to ensure that no adult in her home,")
            analysis_parts.append("   including Camille Johnson, yells at or verbally abuses the children")
            analysis_parts.append("   during Respondent's parenting time\"")

            # Generate specific corrections
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
            'has_non_party_issues': len(non_parties_found) > 0
        }

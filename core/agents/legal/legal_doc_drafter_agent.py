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
from typing import Dict, Any, List, Optional
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

    system_prompt = """You are a Pro Se Legal Assistant specializing in Colorado family law.

Your role is to help self-represented individuals understand procedures and draft TEMPLATE documents.

CRITICAL RULES:
1. ALWAYS include the legal disclaimer in your responses
2. NEVER provide specific legal advice - only general legal information
3. ALWAYS recommend consulting a licensed attorney
4. Focus on PROCEDURAL matters, not legal strategy
5. Reference appropriate Colorado JDF forms when relevant
6. Be clear that generated documents are TEMPLATES requiring review

Colorado Family Law Focus Areas:
- Divorce with children (C.R.S. § 14-10-101 et seq.)
- Allocation of Parental Responsibilities (custody)
- Parenting Time schedules
- Child Support calculations
- Modifications of existing orders

Key Colorado JDF Forms:
- JDF 1111: Petition for Dissolution of Marriage with Children
- JDF 1113: Parenting Plan
- JDF 1220: Motion to Modify Parenting Time
- JDF 1820/1821: Child Support Worksheets

You have these tools:
- search_legal_resources: Search Colorado legal resources, statutes, and spider data
- draft_motion: Generate a motion template
- draft_email: Generate a meet-and-confer email template
- draft_declaration: Generate a declaration template
- get_form_info: Get information about specific JDF forms
- explain_procedure: Explain a Colorado family law procedure

Remember: You provide INFORMATION and TEMPLATES, not legal advice."""

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
        }
    ]

    def __init__(self, user=None, case_id: str = None):
        super().__init__(user)
        self._spider_service = None
        self._semantic_search = None
        self.case_id = case_id  # Optional: Link to LegalCase
        self._current_case = None

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

                # Build prompt with legal context
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

                # ALWAYS add disclaimer
                response_parts.append(LEGAL_DISCLAIMER)

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
                    error=str(e) + "\n\n" + LEGAL_DISCLAIMER,
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _build_legal_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build prompt with legal context and safeguards."""

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

        return "\n".join(prompt_parts)

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

"""
Legal Agents Package
====================

Session 403: Pro Se Legal Assistant agents for Colorado family law.

Agents:
- LegalDocDrafterAgent: Generates procedural legal documents (motions, emails, declarations)

IMPORTANT DISCLAIMER:
These agents provide GENERAL LEGAL INFORMATION only, NOT legal advice.
Users should always consult a licensed attorney for their specific situation.
"""

from .legal_doc_drafter_agent import LegalDocDrafterAgent

__all__ = ['LegalDocDrafterAgent']

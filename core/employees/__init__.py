"""
AI Employee framework — v0.

Session 1252 PR 1: defines the AIEmployee + JobContract dataclasses and
the first employee/job constants (Rigby as Documentation Manager).

Frozen-config v0 — no Django models, no migrations. Job definitions
live in version control; runtime state lives in existing OpsRun /
OpsRunEvent / Deliverable tables. See ``jobs.py`` for the contract.
"""

from core.employees.jobs import (
    AIEmployee,
    JobContract,
    AuthorityLevel,
    RIGBY,
    DOCUMENTATION_MANAGER,
    PLATFORM_AUDITOR,
    PLATFORM_AUDIT_JOB,
    CHIEF_OF_STAFF,
    MORNING_BRIEF_JOB,
    BUG_TRIAGE_SPECIALIST,
    BUG_TRIAGE_JOB,
    list_employees,
    get_employee,
    list_jobs_for_employee,
    list_jobs_with_keys,
    list_job_keys_for_employee,
    get_job,
)

__all__ = [
    "AIEmployee",
    "JobContract",
    "AuthorityLevel",
    "RIGBY",
    "DOCUMENTATION_MANAGER",
    "PLATFORM_AUDITOR",
    "PLATFORM_AUDIT_JOB",
    "CHIEF_OF_STAFF",
    "MORNING_BRIEF_JOB",
    "BUG_TRIAGE_SPECIALIST",
    "BUG_TRIAGE_JOB",
    "list_employees",
    "get_employee",
    "list_jobs_for_employee",
    "list_jobs_with_keys",
    "list_job_keys_for_employee",
    "get_job",
]

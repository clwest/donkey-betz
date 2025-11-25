# Code Review Report Template

Use this template for each session's output. Copy and fill in all sections.

---

# Code Review: [DOMAIN NAME]

## Session Info
- **Session Number:** [1-8]
- **Domain:** [Domain being reviewed]
- **Reviewer:** Claude Code
- **Date:** [YYYY-MM-DD]
- **Duration:** [Estimated time spent]

## Files Reviewed
| File | Path | Lines | Purpose |
|------|------|-------|---------|
| | | | |
| | | | |
| | | | |

---

## Executive Summary

[2-3 paragraphs providing a high-level overview of the code quality in this domain. Include:
- Overall impression of the code
- Key strengths identified
- Most critical concerns
- General recommendation]

---

## Scores

| Category | Score | Justification |
|----------|-------|---------------|
| Code Quality | /10 | [Brief explanation] |
| Architecture | /10 | [Brief explanation] |
| Security | /10 | [Brief explanation] |
| Performance | /10 | [Brief explanation] |
| Error Handling | /10 | [Brief explanation] |
| Testing | /10 | [Brief explanation] |
| **Overall** | /10 | [Weighted average or overall assessment] |

### Score Criteria Reference
- **9-10:** Excellent - Production ready, follows best practices
- **7-8:** Good - Minor issues, acceptable for production
- **5-6:** Adequate - Several issues need attention
- **3-4:** Poor - Significant issues, needs refactoring
- **1-2:** Critical - Major rewrites needed

---

## Critical Issues (P0)

Issues that **must be fixed before production deployment**. These represent security vulnerabilities, data loss risks, or functionality that is fundamentally broken.

### P0-1: [Issue Title]
- **File:** `path/to/file.py`
- **Line(s):** XXX-XXX
- **Category:** Security / Data Integrity / Functionality
- **Description:**
  [Detailed description of the issue]
- **Impact:**
  [What happens if this isn't fixed - be specific about risks]
- **Recommendation:**
  [How to fix this issue]
- **Code Example:**
```python
# Current (Problematic)
[code snippet showing the issue]

# Recommended Fix
[code snippet showing the solution]
```

### P0-2: [Issue Title]
[Repeat structure...]

---

## High Priority Issues (P1)

Issues that **should be fixed soon** (within 1-2 weeks). These affect reliability, maintainability, or represent moderate security concerns.

### P1-1: [Issue Title]
- **File:** `path/to/file.py`
- **Line(s):** XXX-XXX
- **Category:** Performance / Reliability / Maintainability
- **Description:**
  [Detailed description]
- **Impact:**
  [What problems this causes]
- **Recommendation:**
  [How to fix]
- **Code Example:**
```python
# Current
[code]

# Recommended
[code]
```

### P1-2: [Issue Title]
[Repeat structure...]

---

## Medium Priority Issues (P2)

Issues to address during **normal development cycles**. These improve code quality but don't pose immediate risks.

### P2-1: [Issue Title]
- **File:** `path/to/file.py`
- **Line(s):** XXX-XXX
- **Category:** Code Quality / Best Practices / Documentation
- **Description:** [Description]
- **Impact:** [Impact]
- **Recommendation:** [Recommendation]

### P2-2: [Issue Title]
[Repeat structure...]

---

## Low Priority Issues (P3)

**Nice-to-have improvements** that can be addressed opportunistically or during refactoring efforts.

### P3-1: [Issue Title]
- **File:** `path/to/file.py`
- **Line(s):** XXX-XXX
- **Category:** Style / Optimization / Enhancement
- **Description:** [Description]
- **Recommendation:** [Recommendation]

### P3-2: [Issue Title]
[Repeat structure...]

---

## Positive Findings

Highlight what's **done well** that should be preserved or used as a model for other code.

### Strength 1: [Title]
- **File(s):** `path/to/file.py`
- **Description:** [What's good about this code]
- **Why It Matters:** [Why this is a positive pattern]

### Strength 2: [Title]
[Repeat structure...]

---

## Code Metrics

### Complexity Analysis
| File | Lines | Functions | Avg Complexity | Max Complexity |
|------|-------|-----------|----------------|----------------|
| | | | | |

### Duplication
| Pattern | Occurrences | Files | Recommendation |
|---------|-------------|-------|----------------|
| | | | |

### Dependencies
| External Dependency | Usage | Risk Level |
|--------------------|-------|------------|
| | | |

---

## Detailed Findings Index

Quick reference to all findings by file:

### `filename1.py`
| Line | Severity | Category | Issue |
|------|----------|----------|-------|
| | | | |

### `filename2.py`
| Line | Severity | Category | Issue |
|------|----------|----------|-------|
| | | | |

---

## Recommendations Summary

### Immediate Actions
1. [Most critical fix]
2. [Second most critical]
3. [Third most critical]

### Short-Term Improvements
1. [Improvement that should happen soon]
2. [Another improvement]

### Long-Term Considerations
1. [Architectural consideration]
2. [Refactoring opportunity]

---

## Appendix

### A. Testing Recommendations
[Specific tests that should be added]

### B. Documentation Gaps
[Documentation that should be added]

### C. Tool Recommendations
[Linters, formatters, or other tools that could help]

---

**Review Complete**

- **Total Issues Found:** [X]
- **P0 Issues:** [X]
- **P1 Issues:** [X]
- **P2 Issues:** [X]
- **P3 Issues:** [X]
- **Positive Findings:** [X]

---

*This report was generated by Claude Code as part of a comprehensive code review.*
*Session [X] of 8 - [Domain Name]*

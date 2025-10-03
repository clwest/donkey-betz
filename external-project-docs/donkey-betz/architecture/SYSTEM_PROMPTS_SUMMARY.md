# Comprehensive System Review - System Prompts Summary

## Overview
This document provides a summary of all 7 detailed system prompts created for the comprehensive system review sessions. Each prompt is designed to be copy/pasted to a new agent to address all identified issues in that session.

## Session Prompts Created

### 📍 Session 01: Core AI Architecture
**File**: `session-01-core-ai-architecture/04-detailed-system-prompt.md`
**Priority Issues**: 
- 🔴 AI-002: Agent performance at 66% (target 95%)
- 🔴 AI-003: Database queries 2066ms (target <100ms)
- 🔴 AI-004: Memory count discrepancy (1,059 vs 6,500+)
**Key Actions**: Performance analysis, query optimization, memory validation

### 📍 Session 02: Memory & Knowledge Systems
**File**: `session-02-memory-knowledge-systems/04-detailed-system-prompt.md`
**Priority Issues**:
- 🚨 MEM-001: Missing HNSW vector indexes (10-20x performance impact)
- 🔴 MEM-002: 92 entries missing embeddings
- 🔴 MEM-003: Memory Palace deprecation needed
**Key Actions**: Create vector index, generate embeddings, service migration

### 📍 Session 03: Content Creation Pipeline
**File**: `session-03-content-creation-pipeline/04-detailed-system-prompt.md`
**Priority Issues**:
- 🚨 CCP-001: Missing DaVinciRenderJob table
- 🚨 CCP-002: Wrong AI asset model references
- 🔴 CCP-003: Async/sync context issues
**Key Actions**: Create tables, fix model references, implement sync wrappers

### 📍 Session 04: Business Intelligence & Research
**File**: `session-04-business-intelligence/04-detailed-system-prompt.md`
**Priority Issues**:
- 🔴 BI-001: Reddit API not configured
- 🔴 BI-002: Deprecated FallbackDataService in use
- 🔴 BI-003: Event loop resource leaks
**Key Actions**: Configure APIs, remove deprecated services, fix async patterns

### 📍 Session 05: Security & Infrastructure
**File**: `session-05-security-infrastructure/04-detailed-system-prompt.md`
**Priority Issues**:
- 🚨 SEC-001: Encryption key in settings file
- 🚨 SEC-002: Debug logs exposing sensitive data
- 🔴 PERF-001: No rate limiting (DoS vulnerability)
**Key Actions**: Move keys to env, sanitize logs, implement rate limiting

### 📍 Session 06: Frontend & User Experience
**File**: `session-06-frontend-user-experience/04-detailed-system-prompt.md`
**Priority Issues**:
- 🚨 FE-001: WCAG accessibility violations (blocks production)
- 🚨 FE-002: Type safety issues with `any` types
- 🔴 FE-003: Not mobile responsive
**Key Actions**: Fix accessibility, add proper types, implement responsive design

### 📍 Session 07: Integration & Testing
**File**: `session-07-integration-testing/04-detailed-system-prompt.md`
**Priority Issues**:
- 🚨 MEM-500: Memory API field error (blocks all operations)
- 🚨 CMD-400: Command parsing validation error
- 🔴 API-404: 5 missing critical endpoints
**Key Actions**: Fix field errors, add endpoints, achieve >90% test pass rate

## Usage Instructions

1. **Select Session**: Choose which session to work on based on priority
2. **Copy Prompt**: Open the `04-detailed-system-prompt.md` file in that session's directory
3. **Paste to Agent**: Copy the entire content and paste to a new Claude agent
4. **Follow Instructions**: The agent will have all context needed to fix the issues
5. **Update Tracker**: After fixes, update the `02-issue-tracker.md` file
6. **Complete Handoff**: Update the `03-session-handoff.md` with results

## Priority Order Recommendation

Based on criticality and dependencies:

1. **Session 05** - Security & Infrastructure (critical vulnerabilities)
2. **Session 07** - Integration & Testing (API blockers)
3. **Session 06** - Frontend & UX (production blockers)
4. **Session 02** - Memory & Knowledge (performance critical)
5. **Session 01** - Core AI Architecture (functionality issues)
6. **Session 03** - Content Pipeline (feature completeness)
7. **Session 04** - Business Intelligence (data quality)

## Total Issues Summary

| Priority | Count | Description |
|----------|-------|-------------|
| P0 (Critical) | 8 | Production blockers, security vulnerabilities |
| P1 (High) | 23 | Major functionality or performance issues |
| P2 (Medium) | 18 | Should be fixed but not blocking |
| P3 (Low) | 12 | Nice-to-have improvements |
| **Total** | **61** | All identified issues across system |

## Success Metrics

Each session has specific success criteria defined in its prompt:
- Session 01: Agent success rate >= 90%, queries < 200ms
- Session 02: Semantic search < 100ms, 100% embedding coverage
- Session 03: All pipeline stages working, tables created
- Session 04: All APIs configured, no mock data
- Session 05: No security vulnerabilities, rate limiting active
- Session 06: WCAG compliant, zero `any` types, responsive
- Session 07: Test pass rate >= 90%, all endpoints working

## Notes

- Each prompt is self-contained with all necessary context
- Prompts include specific code examples and test commands
- All file paths are absolute from the project root
- Database credentials and connection details are included
- Success criteria and checklists ensure completeness

---

**Created**: August 12, 2025
**Total Prompts**: 7 comprehensive system prompts
**Estimated Time**: 3-4 hours per session for experienced developer
**Goal**: Achieve production-ready system with all critical issues resolved
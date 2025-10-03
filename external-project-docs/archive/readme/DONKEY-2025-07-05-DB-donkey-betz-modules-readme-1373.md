# Archived Donkey Betz Modules

**Archived Date**: July 5, 2025

## Overview
These modules were part of the platform split architecture that was planned but not fully implemented. The project has since consolidated into a single backend architecture.

## Archived Modules

### donkey_betz_business
- **Purpose**: Was intended to be the business-focused platform for AI-powered business creation
- **Status**: Partially implemented, superseded by unified backend

### donkey_betz_personal  
- **Purpose**: Was intended to be the personal wellness platform
- **Status**: Exists as a separate app but not actively developed

### donkey_betz_shared
- **Purpose**: Shared code and services between business and personal platforms
- **Status**: Core functionality moved to main backend

### donkey_betz_sso
- **Purpose**: Single Sign-On implementation for cross-platform authentication
- **Status**: Not needed with single backend architecture

### donkey_betz_billing
- **Purpose**: Unified billing system for both platforms
- **Status**: Billing handled within main backend

## Current Architecture
The project now uses:
- **Backend**: Single Django backend at `/backend` (port 8000)
- **Frontend**: React app at `/donkey-betz-frontend` 
- **Mobile**: Flutter app at `/frontend/momentum_flutter`

## References
See `/CURRENT_STATE/platform_split_process.md` for historical context on the platform split attempt.
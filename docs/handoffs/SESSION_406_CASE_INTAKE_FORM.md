# Session 406: Case Intake Form + ChatGPT Patches

**Date:** December 9, 2025
**Status:** COMPLETE
**Branch:** feature/session-52-ai-assistant

---

## Summary

Created a complete Case Intake Form system so the Legal Assistant has full case context before analyzing motions. This solves the problem of inaccurate name extraction from PDFs and allows the system to work for ANY case regardless of document formatting.

---

## What Was Built

### 1. Django Models (`core/models_legal.py`)
- **CaseProfile** - Main case record (UUID pk, user FK, case_number, case_type, county, state, court info)
- **Party** - Petitioner/Respondent with contact info and pro se status
- **Attorney** - Legal counsel for a party (FK to Party)
- **Child** - Minor children in the case (FK to CaseProfile)
- **CaseDocument** - Court orders attached to case profile

Key method: `CaseProfile.get_conferral_recipient()` - Returns counsel info if respondent is represented, else respondent info

### 2. API Endpoints (`core/views_legal_cases.py`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/legal/cases/` | GET | List all user's case profiles |
| `/api/legal/cases/` | POST | Create new case with nested parties/attorneys/children |
| `/api/legal/cases/<uuid>/` | GET | Full case details |
| `/api/legal/cases/<uuid>/` | PUT | Update case |
| `/api/legal/cases/<uuid>/` | DELETE | Delete case |
| `/api/legal/cases/<uuid>/context/` | GET | Get case context for motion analysis |
| `/api/legal/cases/<uuid>/children/` | POST | Add child |
| `/api/legal/cases/<uuid>/children/<uuid>/` | DELETE | Remove child |
| `/api/legal/cases/<uuid>/documents/` | POST | Upload document |
| `/api/legal/cases/<uuid>/documents/<uuid>/` | DELETE | Remove document |
| `/api/legal/active-case/` | GET/POST | Get/Set active case for session |

### 3. Admin Interface (`core/admin.py` lines 160-320)
- CaseProfileAdmin with PartyInline, ChildInline, CaseDocumentInline
- PartyAdmin with AttorneyInline
- Individual admins for Attorney, Child, CaseDocument

### 4. UI Form (`ai_core/templates/components/panels/legal_assistant_panel.html`)
- New "Case Setup" tab in Legal Assistant panel (lines 106-110)
- Multi-step wizard form (lines 660-933):
  - Step 1: Case Information (case number, type, county, court)
  - Step 2: Your Information (petitioner details, pro se status)
  - Step 3: Other Party (respondent details, their attorney)
  - Step 4: Children (add/remove children)
- JavaScript functions (lines 1646-1924):
  - `loadCaseProfiles()` - Load existing cases
  - `showCaseSetupForm()` / `hideCaseSetupForm()` - Form visibility
  - `nextCaseStep()` / `prevCaseStep()` - Step navigation
  - `addChildRow()` / `removeChildRow()` - Dynamic child management
  - `saveCaseProfile()` - Save to API
  - `setActiveCase()` - Mark a case as active

### 5. Pipeline Integration (`core/agents/legal/legal_doc_drafter_agent.py`)
- New method `_get_active_case_profile_data()` (lines 3828-3919)
  - Checks context for active_case_id
  - Loads CaseProfile from database
  - Returns dict matching `_extract_case_metadata()` format
  - Includes `conferral_recipient_name`, `conferral_recipient_first_name`, etc.
- Updated Step 3.5 in pipeline (lines 2452-2477)
  - First tries to get CaseProfile data
  - Falls back to document extraction if no profile
  - Logs conferral recipient for debugging

---

## Files Changed

| File | Changes |
|------|---------|
| `docs/SESSION_406_CASE_INTAKE_FORM.md` | Feature spec |
| `core/models_legal.py` | NEW - 5 Django models |
| `core/migrations/0077_legal_case_intake_form.py` | NEW - Migration |
| `core/admin.py` | Added admin registrations (lines 160-320) |
| `core/views_legal_cases.py` | NEW - API endpoints (~500 lines) |
| `core/urls.py` | Added URL patterns (lines 2618-2644) |
| `ai_core/templates/components/panels/legal_assistant_panel.html` | Added Case Setup tab + form + JS |
| `core/agents/legal/legal_doc_drafter_agent.py` | Added `_get_active_case_profile_data()`, updated Step 3.5 |

---

## How It Works

### User Flow
1. User goes to Legal Assistant → Case Setup tab
2. Clicks "Set Up New Case"
3. Fills out multi-step form:
   - Case number, county, court info
   - Their name and contact (petitioner)
   - Opposing party and their attorney
   - Any children involved
4. Clicks "Save Case Profile"
5. Case is auto-set as active

### Motion Analysis Flow
1. User uploads denied motion for analysis
2. Pipeline Step 3.5 checks for active CaseProfile
3. If found, uses CaseProfile data for:
   - Caption (parties, case number, court)
   - Conferral email recipient (counsel if represented!)
   - Certificate of Service addresses
4. If no profile, falls back to document extraction

### Conferral Email Logic
```python
# In CaseProfile.get_conferral_recipient():
if respondent and not respondent.is_pro_se:
    attorney = respondent.attorneys.first()
    if attorney:
        return {'name': attorney.full_name, 'is_attorney': True, ...}
if respondent:
    return {'name': respondent.full_name, 'is_attorney': False, ...}
```

---

## Testing

### Manual Testing
1. Start server: `make start`
2. Go to http://localhost:8000/ai-studio/
3. Click Legal Assistant tab
4. Click "Case Setup" sub-tab
5. Click "Set Up New Case"
6. Fill in case details with opposing counsel info
7. Save and verify conferral emails use attorney name

### API Testing
```bash
# List cases (requires auth)
curl http://localhost:8000/api/legal/cases/

# Create case (requires CSRF token + auth)
curl -X POST http://localhost:8000/api/legal/cases/ \
  -H "Content-Type: application/json" \
  -d '{"case_number": "2025DR576", "county": "Larimer", ...}'
```

---

## Known Limitations

1. **Edit functionality** - The "Edit" button shows a toast "coming soon" - needs implementation
2. **Document upload** - The CaseDocument upload is basic, could add OCR extraction
3. **Multi-case** - Users can have multiple cases but only one active at a time

---

## Related Sessions

- Session 405: Conferral Email feature (this provides the counsel data for it!)
- Session 404: Motion rewrite pipeline (this integrates with Step 3.5)
- Session 403: Legal Assistant panel setup

---

## ChatGPT Patch Review (Session 406 Part 2)

User received detailed feedback from ChatGPT reviewing the Legal Doc Drafter output. Six patches were implemented:

### Patch 1: Resolve Core Placeholders from CaseMeta
**Location:** `_rewrite_motion_gold_standard()` lines 5262-5265
- Changed logic to always resolve `{state}` to extracted value or default to "COLORADO"
- Removed problematic "both must be extracted" logic that was leaving blanks

### Patch 2: Replace {relief_requested} in Proposed Order
**Location:** `_rewrite_motion_gold_standard()` lines 5384-5403
- Verification/Affidavit and Proposed Order sections now use f-strings properly
- All placeholders resolved from local variables

### Patch 3: Conferral Recipient Uses Counsel if Present
**Location:** `_rewrite_motion_gold_standard()` lines 5384-5402
- Certificate of Service now routes to counsel if respondent is represented:
  ```python
  is_represented = case_details.get('conferral_recipient_is_attorney', False)
  if is_represented and respondent_counsel:
      service_recipient = f"{respondent_counsel}\n{firm}\nAttorney for Respondent"
  ```

### Patch 4: Store conferral_status as Structured Data
**Location:** `_generate_conferral_email()` lines 3413-3433
- Added `conferral_status` field to return dict with values: `pending`, `no_response`, `refused`, `partial`, `agreed`
- Added `conferral_status_options` list for UI dropdowns
- Added `recipient_is_counsel` and `recipient_name` for display

### Patch 5: Fix "Escalating Pattern of Escalating" Wording Glitch
**Location:** `_generate_impact_paragraph()` lines 3594-3596
- Added regex cleanup:
  ```python
  impact = re.sub(r'escalating pattern of\s+escalating[,\s]+', 'escalating pattern of ', impact)
  impact = re.sub(r'pattern of\s+harmful[,\s]+and', 'pattern of conduct that', impact)
  ```

### Patch 6: Link Conduct to Temporary Orders Non-Disparagement
**Location:** `_parse_order_provisions()` lines 3829-3832
- When non-disparagement is detected, adds:
  > "The statements described below appear inconsistent with the Court's non-disparagement provisions in the Temporary Orders (Exhibit A)."

---

## Bug Fix: motion_text is not defined

**Issue:** User got error when analyzing motion: `name 'motion_text' is not defined`
**Location:** `_extract_case_metadata()` line 4069
**Root Cause:** Method parameter is `content` but code referenced `motion_text`
**Fix:** Changed `re.search(pattern, motion_text, ...)` to `re.search(pattern, content, ...)`

---

## Critical Fix: CaseProfile Not Being Loaded

**Issue:** Even with CaseProfile selected, conferral email still addressed respondent (Susannah) instead of counsel
**Root Cause:** `analyze_legal_document()` didn't pass `request` to context, so `_get_active_case_profile_data()` couldn't access `request.session.get('active_case_id')`

**Files Fixed:**
- `core/views_legal.py`:
  - Added `request=None` parameter to `analyze_legal_document()`
  - Added `active_case_id` and `request` to context dict
  - Updated both callers to pass `request=request`

**Result:** CaseProfile data now flows through pipeline → conferral email addresses counsel!

---

## Next Steps

1. **Implement edit functionality** for existing case profiles
2. **Add case profile indicator** in UI showing which case is active
3. **Auto-populate form** from uploaded court orders using OCR
4. **Multiple children** - test with cases having 3+ children
5. **Address formatting** - verify Certificate of Service uses correct format
6. **Test ChatGPT patches** - Run full motion analysis to verify patches work

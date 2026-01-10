# Session 406: Case Intake Form Feature

**Date:** December 9, 2025
**Status:** In Progress
**Goal:** Create a Case Intake Form so the Legal Assistant has full case context before analyzing motions

---

## Problem Statement

The Legal Assistant extracts party names, case numbers, and other metadata from uploaded documents. However:

1. **Opposing counsel info** is often not in the motion being analyzed
2. **Extraction errors** occur when document formatting varies
3. **Conferral emails** need to be addressed to the correct recipient (counsel if represented, party if pro se)
4. **Certificate of Service** needs accurate addresses

**Solution:** A Case Intake Form that users fill out ONCE when setting up their case, providing complete context for all future motion analysis.

---

## Data Model

### CaseProfile
The main case record linking all parties and documents.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user | ForeignKey | Owner of this case profile |
| case_number | CharField | Court case number (e.g., "2025DR576") |
| case_type | CharField | divorce, custody, modification, enforcement, other |
| county | CharField | County name |
| state | CharField | State (default: Colorado) |
| district | CharField | Judicial district |
| division | CharField | Court division |
| court_address | TextField | Full court address |
| filing_date | DateField | When case was filed |
| status | CharField | active, closed, pending |
| notes | TextField | Any additional case notes |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last modification timestamp |

### Party
Represents either Petitioner or Respondent.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| case_profile | ForeignKey | Link to CaseProfile |
| party_type | CharField | petitioner, respondent |
| full_name | CharField | Full legal name |
| first_name | CharField | First name (for salutations) |
| address | TextField | Mailing address |
| city | CharField | City |
| state | CharField | State |
| zip_code | CharField | ZIP code |
| phone | CharField | Phone number |
| email | EmailField | Email address |
| is_pro_se | BooleanField | True if self-represented |

### Attorney
Represents legal counsel for a party.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| party | ForeignKey | Link to Party they represent |
| full_name | CharField | Attorney's full name |
| first_name | CharField | First name (for salutations) |
| firm_name | CharField | Law firm name |
| address | TextField | Office address |
| city | CharField | City |
| state | CharField | State |
| zip_code | CharField | ZIP code |
| phone | CharField | Phone number |
| email | EmailField | Email address |
| bar_number | CharField | Attorney registration number |

### Child
For family law cases involving minor children.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| case_profile | ForeignKey | Link to CaseProfile |
| full_name | CharField | Child's full name |
| first_name | CharField | First name |
| date_of_birth | DateField | DOB |
| age | IntegerField | Computed age |

### CaseDocument
Links uploaded court orders to the case profile.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| case_profile | ForeignKey | Link to CaseProfile |
| document_type | CharField | temporary_orders, permanent_orders, separation_agreement, other |
| title | CharField | Document title |
| file | FileField | Uploaded file |
| entered_date | DateField | Date order was entered |
| extracted_text | TextField | OCR/extracted text content |
| notes | TextField | Any notes about this document |
| uploaded_at | DateTime | Upload timestamp |

---

## UI Design

### Case Setup Page (New)

Located at: `/ai-studio/` → Legal Assistant Panel → "My Cases" tab

**Flow:**
1. User clicks "New Case" button
2. Multi-step form wizard:
   - Step 1: Case Information (case number, county, court, type)
   - Step 2: Your Information (petitioner details, pro se or attorney)
   - Step 3: Opposing Party (respondent details, their attorney if known)
   - Step 4: Children (if applicable)
   - Step 5: Court Orders (upload existing orders)
3. Case saved and available for all future motion analysis

**Form Sections:**

```
┌─────────────────────────────────────────────────────────────┐
│  CASE SETUP                                          [1/5]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Case Number: [__2025DR576__________]                       │
│                                                             │
│  Case Type:   ( ) Divorce                                   │
│               (●) Child Custody                             │
│               ( ) Modification                              │
│               ( ) Enforcement                               │
│               ( ) Other                                     │
│                                                             │
│  County:      [__Larimer_____________] State: [_Colorado_]  │
│                                                             │
│  Court Address:                                             │
│  [__201 LaPorte Avenue, Suite 100_________________________] │
│  [__Fort Collins, CO 80521________________________________] │
│                                                             │
│  Division: [_2B_]  Courtroom: [____]                        │
│                                                             │
│                              [Cancel]  [Next →]             │
└─────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR INFORMATION (PETITIONER)                       [2/5]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Full Name:   [__Christopher L. West____________________]   │
│                                                             │
│  Address:     [__123 Main Street________________________]   │
│  City:        [__Fort Collins___] State: [_CO_] ZIP:[80521] │
│                                                             │
│  Phone:       [__(970) 555-1234_____]                       │
│  Email:       [__chris@email.com____]                       │
│                                                             │
│  ☑ I am representing myself (Pro Se)                        │
│                                                             │
│  ┌─ YOUR ATTORNEY (if represented) ─────────────────────┐   │
│  │  Name:     [______________________________]          │   │
│  │  Firm:     [______________________________]          │   │
│  │  Phone:    [______________]                          │   │
│  │  Email:    [______________________________]          │   │
│  │  Bar #:    [______________]                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│                         [← Back]  [Next →]                  │
└─────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────┐
│  OPPOSING PARTY (RESPONDENT)                         [3/5]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Full Name:   [__Susannah M. West_______________________]   │
│                                                             │
│  Address:     [__456 Oak Avenue_________________________]   │
│  City:        [__Fort Collins___] State: [_CO_] ZIP:[80525] │
│                                                             │
│  Phone:       [__(970) 555-5678_____]                       │
│  Email:       [__susannah@email.com_]                       │
│                                                             │
│  ☐ Respondent is Pro Se (self-represented)                  │
│                                                             │
│  ┌─ RESPONDENT'S ATTORNEY ──────────────────────────────┐   │
│  │  Name:     [__Jane Smith, Esq._______________]       │   │
│  │  Firm:     [__Smith Family Law LLC___________]       │   │
│  │  Phone:    [__(970) 555-9999_]                       │   │
│  │  Email:    [__jane@smithlaw.com______________]       │   │
│  │  Bar #:    [__12345__________]                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│                         [← Back]  [Next →]                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration with Motion Analysis

When user runs "Analyze Denied Motion" or any legal tool:

1. System checks if user has a CaseProfile
2. If yes, auto-populates:
   - Caption information (parties, case number, court)
   - Conferral email recipient (opposing counsel if represented, else respondent)
   - Certificate of Service addresses
   - Relief phrasing (uses correct names)
3. If no CaseProfile, falls back to document extraction (current behavior)

### Code Changes Required

**1. `_extract_case_metadata()` enhancement:**
```python
def _extract_case_metadata(self, motion_text: str, case_profile: Optional[CaseProfile] = None):
    # If case profile provided, use it as authoritative source
    if case_profile:
        return {
            'case_number': case_profile.case_number,
            'county': case_profile.county,
            'state': case_profile.state,
            'petitioner_name': case_profile.petitioner.full_name,
            'respondent_name': case_profile.respondent.full_name,
            'respondent_counsel': case_profile.respondent.attorney.full_name if not case_profile.respondent.is_pro_se else '',
            # ... etc
        }
    # Otherwise, extract from document (current behavior)
    # ...
```

**2. `_generate_conferral_email()` enhancement:**
```python
# Already updated to accept respondent_counsel parameter
# Will use counsel name for greeting if provided, else respondent name
```

**3. Pipeline integration:**
```python
# In _execute_denied_motion_pipeline():
case_profile = self._get_user_case_profile(user_id)  # New method
case_details = self._extract_case_metadata(motion_text, case_profile=case_profile)
```

---

## API Endpoints (New)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/legal/cases/` | List user's case profiles |
| POST | `/api/legal/cases/` | Create new case profile |
| GET | `/api/legal/cases/{id}/` | Get case profile details |
| PUT | `/api/legal/cases/{id}/` | Update case profile |
| DELETE | `/api/legal/cases/{id}/` | Delete case profile |
| POST | `/api/legal/cases/{id}/documents/` | Upload court order |
| GET | `/api/legal/cases/{id}/documents/` | List case documents |

---

## File Locations

| File | Purpose |
|------|---------|
| `core/models_legal.py` | New models (CaseProfile, Party, Attorney, Child, CaseDocument) |
| `core/views_legal.py` | API endpoints for case management |
| `core/serializers_legal.py` | DRF serializers |
| `core/agents/legal/legal_doc_drafter_agent.py` | Integration with pipeline |
| `ai_core/templates/ai_image_studio.html` | UI for case setup form |

---

## Migration Plan

1. Create models in `core/models_legal.py`
2. Run migrations
3. Add API endpoints
4. Add UI form in Legal Assistant panel
5. Integrate with motion analysis pipeline
6. Test end-to-end

---

## Future Enhancements

- **Case Templates:** Pre-fill common case types
- **Document OCR:** Auto-extract info from uploaded orders to pre-fill form
- **Multi-case Support:** Handle users with multiple active cases
- **Case Sharing:** Allow attorneys to share case profiles with clients
- **Court Calendar Integration:** Track hearing dates

---

## Summary

The Case Intake Form transforms the Legal Assistant from a document-by-document tool into a comprehensive case management system. By capturing case context upfront, every motion analysis automatically has:

- Accurate party names and roles
- Correct opposing counsel information
- Proper addresses for service
- Context from existing court orders

This makes the system work for ANY case, not just specific hard-coded scenarios.

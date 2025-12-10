# Session 406: Order Integration + Facts Upgrade + Conferral System

**Date:** December 9, 2025
**Focus:** ChatGPT-recommended enhancements to Legal Assistant motion rewriting

## Summary

Implemented ChatGPT's v5 and v6 patch recommendations to improve the denied motion rewriting pipeline:

1. **Court Order Integration** - Uploaded orders now appear in the rewritten motion
2. **Facts Promotion** - PART 3 now includes specific quotes and named third parties
3. **Incident Count Fix** - No longer claims "4 incidents" when only showing 3
4. **Chronological Sorting** - SPECIFIC FACTUAL ALLEGATIONS now sorted oldest→newest
5. **Conferral Email System** - Auto-generates conferral email + Certificate of Conferral (NEW!)

## Changes Made

### 1. EXISTING COURT ORDERS Section (New Feature)

**File:** `core/agents/legal/legal_doc_drafter_agent.py`

Added `_parse_order_provisions()` method that:
- Extracts order date from uploaded court order
- Detects parenting time provisions
- Detects non-disparagement clauses
- Detects third-party conduct rules
- Detects decision-making authority provisions

Adds new section to motion (before FACTS):
```
------------------------------------------------------------
EXISTING COURT ORDERS
------------------------------------------------------------

1. On November 5, 2025, the Court entered Temporary Orders in case 2025DR000576.
2. The Temporary Orders include:
   a. A parenting time schedule regarding the minor child(ren)
   b. A non-disparagement provision prohibiting the parties and third parties from speaking negatively about the other parent in the child's presence
   c. Provisions regarding third-party conduct during parenting time
   d. Decision-making authority allocations
3. A true and correct copy of the Temporary Orders is attached as Exhibit A.
```

### 2. Facts Promotion (Enhanced Specificity)

**New helper methods:**
- `_extract_direct_quotes()` - Extracts quoted statements from narrative
- `_extract_third_party_names()` - Finds named third parties (e.g., "Camille Johnson")
- `_build_specific_allegation_detail()` - Constructs specific allegations using quotes/names

**Before (generic):**
```
4. On November 12, 2025, during court-ordered parenting time, the minor child reported that a third party made statements about Petitioner.
```

**After (specific):**
```
4. On November 12, 2025, during court-ordered parenting time, the minor child stated, "You have been lying to me." Later, the child identified Camille Johnson as the source of these statements.
```

### 3. Incident Count Fix

**Problem:** Code said "These 4 documented incidents" but only showed 3 incidents.

**Solution:** Changed to generic phrasing "These documented incidents demonstrate an escalating pattern..."

**Updated methods:**
- `_generate_impact_paragraph()` - Now uses "documented incidents" without count
- `_default_impact_text()` - Same fix

Also fixed `_extract_third_party_names()` to avoid false positives like "Camille Has" (from "Camille has told me").

### 4. Chronological Date Sorting (Additional Fix)

**Problem:** SPECIFIC FACTUAL ALLEGATIONS showed dates out of order:
```
1. On November 12, 2025...  (most recent)
2. On August 29, 2025...    (first incident)
3. The following week...     (second incident)
```

**Solution:** Added `_sort_allegations_chronologically()` method that:
- Parses dates from allegations
- Sorts dated items chronologically (oldest first)
- Places "The following week" after the first dated incident
- Keeps non-dated items (third-party status, respondent failures, impact) at the end

**After (chronological order):**
```
1. On August 29, 2025...     (first incident)
2. The following week...      (second incident)
3. On November 12, 2025...   (most recent)
4. Camille Johnson is not... (third-party status)
5. Respondent has...          (failures)
6. These documented...        (impact statement)
```

## Testing

All changes tested with sample motion content:
```python
# Test order parsing
agent._parse_order_provisions(sample_order, '2025DR000576')

# Test quote extraction
agent._extract_direct_quotes(sample_motion)  # Returns: ["You have been lying to me.", ...]

# Test name extraction
agent._extract_third_party_names(sample_motion)  # Returns: ["Camille Johnson"]

# Test allegation building
agent._build_clean_allegations([], sample_motion)  # Returns specific allegations
```

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/legal/legal_doc_drafter_agent.py` | Added 6 new methods, updated 4 existing methods |

**New methods added:**
- `_parse_order_provisions()` - Extracts provisions from uploaded court orders
- `_extract_direct_quotes()` - Extracts quoted statements from narrative
- `_extract_third_party_names()` - Finds named third parties
- `_build_specific_allegation_detail()` - Constructs specific allegations
- `_sort_allegations_chronologically()` - Sorts dated incidents oldest→newest

## How It Works Now

1. User uploads court order (e.g., Temporary Orders.pdf)
2. System saves order and extracts key provisions
3. User uploads denied motion for rewrite
4. Pipeline:
   - Fetches user's uploaded court orders from database
   - Parses provisions from orders
   - Extracts quotes and third-party names from motion
   - Builds motion with:
     - EXISTING COURT ORDERS section (referencing uploaded order)
     - Specific, numbered facts with actual quotes and names
     - Generic "documented incidents" phrasing (no miscount)

## ChatGPT Validation

ChatGPT's assessment of the original system:
> "Your system's rewrite is correct, court-ready, and properly formatted with zero red flags."

These enhancements address the remaining gaps:
- Order integration into motion text
- Fact specificity
- Incident count accuracy

### 5. Conferral Email System (Major New Feature)

**Why This Matters:**
Per C.R.C.P. 121 § 1-15(8), Colorado courts require parties to confer before filing most non-emergency motions. Judges frequently deny motions that lack a Certificate of Conferral.

**What Was Added:**

1. **New Tool:** `generate_conferral_email`
   - Generates ready-to-send email to opposing party
   - Creates 3 versions of Certificate of Conferral (no response, refused, partial)
   - Provides step-by-step workflow guidance

2. **Motion Template Update:**
   - Emergency motions: Shows "CERTIFICATE OF CONFERRAL (WAIVED - EMERGENCY)"
   - Non-emergency motions: Shows fillable Certificate with checkboxes

3. **Pipeline Integration:**
   - New PART 6 in output: "CONFERRAL EMAIL (SEND BEFORE FILING)"
   - Includes copy-paste email text
   - Explains what to do after sending

**Sample Conferral Email Generated:**
```
Subject: Required Conferral – Third-Party Statements / Parenting Time Issue

Susannah,

As required by Colorado Rule of Civil Procedure 121 § 1-15, I am attempting to confer with you regarding concerns I intend to raise with the Court.

Specifically, I am requesting:
    1. That no adults in Respondent's household make statements to or in the presence of Nicolas regarding Petitioner's honesty, character, or this case
    2. That adults in Respondent's household refrain from discussing litigation in Nicolas's presence
    3. That third parties not be present during parenting-time exchanges

Please let me know by December 11, 2025 whether you agree to these limited requests.

If I do not receive a response, I will note that in the Certificate of Conferral when filing the motion.

Thank you,
Christopher
```

**Sample Certificate of Conferral:**
```
CERTIFICATE OF CONFERRAL

Pursuant to C.R.C.P. 121 § 1-15(8), Petitioner certifies that:

1. On or about December 09, 2025, Petitioner sent written communication to Respondent regarding the relief requested in this motion.
2. Petitioner made reasonable and good-faith efforts to confer with Respondent.
3. [ ] Respondent did not respond within the conferral period.
   [ ] Respondent stated they do not agree to the requested relief.
   [ ] The parties were unable to reach full agreement on all requested relief.
4. The matter could not be resolved without Court involvement.
```

## New Methods Added (Session 406)

| Method | Purpose |
|--------|---------|
| `_generate_conferral_email()` | Creates conferral email + certificates |
| `_check_conferral_required()` | Determines if conferral needed (emergency = no) |
| `_sort_allegations_chronologically()` | Sorts incidents oldest→newest |

## New Tools Added

| Tool | Description |
|------|-------------|
| `generate_conferral_email` | Standalone tool to generate conferral emails for any motion |

## Output Structure (Updated)

The denied motion rewrite now produces:
- **PART 1:** Procedural Defects Identified
- **PART 2:** Non-Party Rule Check
- **PART 3:** Corrected Motion (Court-Ready Format)
  - Includes CERTIFICATE OF CONFERRAL section
- **PART 4:** Evidence Checklist
- **PART 5:** Likelihood of Success
- **PART 6:** Conferral Email (NEW!) - Only for non-emergency motions

## Next Steps

Consider:
1. ~~Auto-detect specific order clauses~~ ✅ Done
2. Add explicit conflict detection messages when motion relief contradicts order terms
3. Test with real PDF uploads through the UI
4. Add email tracking to note when conferral was sent

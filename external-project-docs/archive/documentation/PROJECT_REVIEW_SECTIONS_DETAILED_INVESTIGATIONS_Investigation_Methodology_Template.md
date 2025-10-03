# Investigation Methodology Template

## Purpose
This template provides a structured approach for investigating issues in the Donkey Betz codebase. Use this for any new investigation to ensure thoroughness and consistency.

## Investigation Structure

### 1. Problem Definition
```
## Problem Statement
[Clear, concise description of the issue]

## User Impact
[How does this affect users?]

## Technical Symptoms
[What are the observable technical issues?]

## Success Criteria
[How will we know when it's fixed?]
```

### 2. Hypothesis Formation
```
## Initial Hypotheses
1. [Most likely cause]
2. [Second possibility]
3. [Third possibility]

## Evidence Needed
- [ ] Evidence for hypothesis 1
- [ ] Evidence for hypothesis 2
- [ ] Evidence for hypothesis 3
```

### 3. Code Discovery Phase
```
## Entry Points
Starting file: [filename]
Starting method: [method name]
User action that triggers: [description]

## Trace Path
1. User Action → 
2. Frontend Component →
3. API Call →
4. Backend Service →
5. Database/External Service →
6. Response Path Back

## Key Files Identified
- File 1: [path] - [purpose]
- File 2: [path] - [purpose]
- File 3: [path] - [purpose]
```

### 4. Systematic Search Queries
```bash
# Query 1: Find entry points
grep -r "endpoint_name\|function_name" backend/ --include="*.py"

# Query 2: Trace data flow
grep -r "variable_name\|model_name" backend/ --include="*.py"

# Query 3: Find error handling
grep -r "try\|except\|raise" backend/specific_module/ --include="*.py"

# Query 4: Find related tests
find . -path "*/tests/*" -name "*test_*.py" -o -name "*_test.py" | xargs grep -l "TestSubject"
```

### 5. Data Flow Analysis
```
## Data Transformation Points
1. Input Format: [description]
   Location: [file:line]
   
2. First Transformation: [description]
   Location: [file:line]
   
3. Second Transformation: [description]
   Location: [file:line]
   
4. Output Format: [description]
   Location: [file:line]

## Data Loss/Corruption Points
- Point 1: [where/why data might be lost]
- Point 2: [where/why data might be corrupted]
```

### 6. Testing Methodology
```
## Test Case 1: Normal Flow
Input: [specific input]
Expected: [expected output]
Actual: [actual output]
Pass/Fail: [status]

## Test Case 2: Edge Case
Input: [edge case input]
Expected: [expected behavior]
Actual: [actual behavior]
Pass/Fail: [status]

## Test Case 3: Error Case
Input: [error-inducing input]
Expected: [expected error handling]
Actual: [actual behavior]
Pass/Fail: [status]
```

### 7. Debug Instrumentation
```python
# Add strategic logging
import logging
logger = logging.getLogger(__name__)

# At entry point
logger.info(f"[INVESTIGATION] Entry: {variable_name}")

# At transformation point
logger.info(f"[INVESTIGATION] Before transform: {data}")
# ... transformation code ...
logger.info(f"[INVESTIGATION] After transform: {data}")

# At exit point
logger.info(f"[INVESTIGATION] Exit: {result}")
```

### 8. Database Investigation
```sql
-- Check data state
SELECT * FROM table_name WHERE condition LIMIT 10;

-- Check relationships
SELECT t1.*, t2.*
FROM table1 t1
LEFT JOIN table2 t2 ON t1.id = t2.table1_id
WHERE t1.condition = 'value';

-- Check for orphaned data
SELECT * FROM child_table
WHERE parent_id NOT IN (SELECT id FROM parent_table);
```

### 9. Performance Profiling
```python
# If performance-related
import time
import cProfile
import pstats

# Time specific operations
start_time = time.time()
# ... operation ...
print(f"Operation took: {time.time() - start_time} seconds")

# Profile function
cProfile.run('function_to_profile()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

### 10. Root Cause Analysis
```
## Confirmed Root Cause
[Description of the actual problem]

## Why It Happens
1. [Primary reason]
2. [Contributing factor]
3. [System design issue]

## Impact Scope
- Affected Components: [list]
- Affected Users: [description]
- Data Impact: [description]
```

### 11. Solution Design
```
## Proposed Fix
[Description of the fix]

## Implementation Steps
1. [ ] Step 1: [description]
2. [ ] Step 2: [description]
3. [ ] Step 3: [description]

## Potential Side Effects
- [Side effect 1]
- [Side effect 2]

## Testing Plan
- [ ] Unit tests for [component]
- [ ] Integration test for [flow]
- [ ] Manual test for [scenario]
```

### 12. Documentation Updates
```
## Code Comments Needed
- File: [path] - [what to document]
- File: [path] - [what to document]

## README Updates
- Section: [section name] - [update needed]

## API Documentation
- Endpoint: [endpoint] - [change description]
```

## Investigation Checklist

### Pre-Investigation
- [ ] Reproduce the issue locally
- [ ] Check existing issues/tickets
- [ ] Review recent commits in affected area
- [ ] Check test coverage

### During Investigation
- [ ] Keep investigation notes
- [ ] Save important queries/commands
- [ ] Document assumptions
- [ ] Track time spent

### Post-Investigation
- [ ] Create fix implementation plan
- [ ] Estimate effort required
- [ ] Identify risks
- [ ] Plan rollback strategy

## Common Pitfalls to Avoid

1. **Assumption without verification** - Always verify with code/data
2. **Fixing symptoms not causes** - Dig deeper to find root cause
3. **Ignoring edge cases** - Consider all scenarios
4. **Missing related issues** - Check for similar problems
5. **Inadequate testing** - Test the fix thoroughly

## Investigation Tools

### Code Analysis
- grep/ripgrep for searching
- Django shell for live testing
- Python debugger (pdb) for stepping through
- Browser DevTools for frontend

### Database Tools
- psql for PostgreSQL queries
- Django ORM for data exploration
- pgAdmin for visual inspection

### Performance Tools
- Django Debug Toolbar
- cProfile for Python profiling
- Chrome DevTools Performance tab
- Backend logs analysis

### Monitoring
- Application logs
- Error tracking (if configured)
- Performance metrics
- User feedback

## Results Documentation Format
```
# Investigation Results: [Issue Name]
Date: [date]
Investigator: [name]
Time Spent: [hours]

## Summary
[2-3 sentence summary of findings]

## Root Cause
[Detailed explanation]

## Fix Applied/Recommended
[Description of fix]

## Lessons Learned
[What can we learn from this?]

## Follow-up Items
- [ ] Item 1
- [ ] Item 2
```
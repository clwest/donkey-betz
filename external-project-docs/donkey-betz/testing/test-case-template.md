# Test Case Template

## Test Information
- **Test ID**: [TC-XXXX]
- **Test Category**: [Infrastructure/API/Agent/Database/Security/Performance/Frontend/Monitoring]
- **Test Name**: [Descriptive name]
- **Priority**: [Critical/High/Medium/Low]
- **Created Date**: [YYYY-MM-DD]
- **Last Tested**: [YYYY-MM-DD]
- **Tester**: [Name]

## Test Description
[Detailed description of what this test validates]

## Prerequisites
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]
- [ ] [Environment setup required]

## Test Environment
- **Server**: [Development/Staging/Production]
- **Database**: [PostgreSQL version]
- **Redis**: [Version]
- **Load**: [Number of concurrent users/requests]

## Test Steps
1. [Step 1 - Specific action]
   - Expected Result: [What should happen]
   - Actual Result: [What actually happened]
   - Status: [PASS/FAIL]

2. [Step 2 - Specific action]
   - Expected Result: [What should happen]
   - Actual Result: [What actually happened]
   - Status: [PASS/FAIL]

3. [Continue for all steps...]

## Test Data
```
[Any specific test data, commands, or scripts used]
```

## Success Criteria
- [ ] [Criteria 1 - e.g., Response time < 2s]
- [ ] [Criteria 2 - e.g., No errors in logs]
- [ ] [Criteria 3 - e.g., Memory usage < 1GB]

## Results

### Summary
- **Overall Status**: [PASS/FAIL/BLOCKED]
- **Pass Rate**: [X/Y test steps passed]
- **Performance Metrics**:
  - Response Time: [Xms]
  - Memory Usage: [XMB]
  - CPU Usage: [X%]
  - Error Rate: [X%]

### Issues Found
1. **Issue 1**
   - Severity: [Critical/High/Medium/Low]
   - Description: [Detailed description]
   - Steps to Reproduce: [How to reproduce]
   - Screenshot/Logs: [Link or attachment]
   - Bug Ticket: [JIRA/GitHub Issue #]

2. **Issue 2**
   - [Continue for all issues...]

### Logs and Evidence
```
[Paste relevant logs, error messages, or stack traces]
```

### Screenshots
[Attach or link to screenshots if applicable]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]
- [Performance optimization suggestions]
- [Security improvements]

## Follow-up Actions
- [ ] [Action item 1]
- [ ] [Action item 2]
- [ ] [Bug fixes required]
- [ ] [Re-test after fixes]

## Sign-off
- **Tested By**: [Name] - [Date]
- **Reviewed By**: [Name] - [Date]
- **Approved By**: [Name] - [Date]

## Version History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | YYYY-MM-DD | [Name] | Initial test case |
| 1.1 | YYYY-MM-DD | [Name] | [What changed] |
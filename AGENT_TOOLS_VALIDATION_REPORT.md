# Agent Tools Validation Report

**Generated:** 2025-09-19T03:50:08.421283
**Status:** FAIL

## Executive Summary

- **Components Tested:** 3
- **Violations Found:** 2
- **Real Data Confirmations:** 3

## Test Results

### Opportunities Api
- **Status:** Unknown
- **Details:** {
  "http://localhost:8000/api/opportunities/": {
    "status_code": 200,
    "real_indicators": 5,
    "mock_indicators": 2,
    "data_type": "REAL"
  }
}

### File Creation
- **Status:** FILE_CREATION_WORKING
- **Details:** {
  "can_create_files": true,
  "test_file_size": 151,
  "test_file_path": "test_file_creation/agent_test_file.md",
  "status": "FILE_CREATION_WORKING"
}

### Web Search
- **Status:** WEB_SEARCH_AVAILABLE
- **Details:** {
  "available_modules": [
    "requests",
    "aiohttp"
  ],
  "web_connectivity": true,
  "test_response": true,
  "status": "WEB_SEARCH_AVAILABLE"
}

## Violations Found

### live_job_scraper
- **Issue:** Spider execution failed: Cannot run the event loop while another loop is running
- **Severity:** CRITICAL
- **Recommendation:** See recommendations section

### agent_executors
- **Issue:** Agent executor test failed: Apps aren't loaded yet.
- **Severity:** HIGH
- **Recommendation:** See recommendations section

## Real Data Confirmations

### opportunities_api
- **Evidence:** APIs returning real data indicators

### file_creation
- **Evidence:** Successfully created file: test_file_creation/agent_test_file.md

### web_search
- **Evidence:** Web connectivity confirmed for real-time data

## Recommendations


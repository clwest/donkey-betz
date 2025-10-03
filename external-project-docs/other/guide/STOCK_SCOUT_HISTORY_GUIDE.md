# Stock Scout History Guide

> Created: July 6, 2025
> Feature: Complete Stock Scout historical review system

## 📍 Where to Find It

**Location**: Business Hub → Scout Central → Stock Scout History tab

## 🎯 What It Does

The Stock Scout History feature allows users to:
- Review all previous Stock Scout missions
- Filter and search through past scouts
- View detailed results and opportunities
- Export data for further analysis

## 🔧 Key Features

### 1. **Mission Overview**
- Lists all Stock Scout missions with:
  - Scout type (penny_stocks, value_plays, momentum, comprehensive)
  - Status (completed, failed, executing, completed_with_errors)
  - Start date and duration
  - Number of opportunities found
  - Visual status indicators

### 2. **Filtering & Search**
- **Scout Type Filter**: Filter by specific scout strategies
- **Date Range**: Filter missions within specific dates
- **Status Filter**: Show only completed, failed, or executing missions
- **Search**: Find missions by ticker, company name, or opportunity type

### 3. **Detailed Results View**
Click any mission to see:
- **Mission Metadata**:
  - Duration and completion time
  - Number of agents deployed
  - Overall progress percentage
  - Scout type and parameters

- **Discovered Opportunities**:
  - Ticker and company name
  - Current/Entry/Target/Stop prices
  - Investment thesis
  - Key catalysts
  - Risk factors
  - Opportunity scores (Reddit buzz, fundamental, technical, overall)
  - Conviction level and risk rating

- **Agent Reports** (when extraction fails):
  - Raw agent outputs
  - Step-by-step execution details
  - Individual agent results

### 4. **Export Functionality**
- **CSV Export**: 
  - Structured format with metadata section
  - Opportunities table with all fields
  - Ready for Excel analysis

- **JSON Export**:
  - Complete mission data
  - All agent outputs
  - Programmatic access to results

## 🛠️ Technical Implementation

### Frontend Components
```typescript
// Main component
/donkey-betz-frontend/src/features/reddit-scout/components/StockScoutHistory.tsx

// Integration point
/donkey-betz-frontend/src/features/business-hub/components/RedditIdeas.tsx
```

### API Endpoints
```python
# List missions
GET /api/agent-orchestra/stocks/scout/missions/

# Get results
GET /api/agent-orchestra/stocks/scout/{id}/results/

# Export data
GET /api/agent-orchestra/stocks/scout/{id}/export/?format=csv|json
```

### Key Functions
- `loadMissions()`: Fetches and displays scout missions
- `handleViewDetails()`: Opens detailed results modal
- `handleExport()`: Exports mission data in selected format
- `applyFilters()`: Filters missions based on criteria

## 🐛 Known Issues & Workarounds

### 1. **Opportunity Extraction Issues**
- **Problem**: Automatic extraction sometimes fails or extracts incorrect tickers
- **Example**: Extracted "SEC" from text about SEC filings
- **Workaround**: View raw agent reports in detail modal

### 2. **Status Display**
- **Problem**: Missions show "failed" even when completed if any agent has errors
- **Impact**: Visual confusion but data is still available
- **Workaround**: Check completion percentage (100% means finished)

## 📊 Usage Example

1. Navigate to Business Hub → Scout Central → Stock Scout History
2. Filter by "penny_stocks" to see all penny stock scouts
3. Click a mission to view detailed results
4. Export to CSV for further analysis in Excel

## 🚀 Future Enhancements

1. **Manual Opportunity Editing**: Allow users to correct extraction errors
2. **Bulk Export**: Export multiple missions at once
3. **Comparison View**: Compare results across multiple scouts
4. **Performance Metrics**: Track scout accuracy over time
5. **Scheduled Scouts**: Set up recurring scout missions

## 📝 Notes for Tomorrow

User wants to "finish up the Reddit section of the app" which includes:
- Fix automatic opportunity extraction
- Improve parsing logic for agent outputs
- Add manual review/edit capabilities
- Complete any remaining Reddit Scout features

The Stock Scout History foundation is solid and ready for these enhancements!
# Stock Intelligence Feature Guide

## Overview
Stock Intelligence is a comprehensive AI-powered market analysis and portfolio tracking system. It provides real-time market data, portfolio management, watchlists, alerts, AI-driven analysis, and market scanning capabilities.

## Architecture

### Frontend Components
Located in `/donkey-betz-frontend/src/features/stock-intelligence/`

#### Main Pages
- `StockIntelligence.tsx` - Main entry point with tab navigation
- `StockDashboard.tsx` - Dashboard component that renders tab content

#### Tab Components (6 Total)
1. **MarketOverviewTab.tsx** - Market indices and trending stocks
2. **PortfolioTab.tsx** - Portfolio positions and performance tracking
3. **WatchlistsTab.tsx** - Custom watchlists management
4. **AlertsTab.tsx** - Price and news alerts configuration
5. **MarketScannerTab.tsx** - AI-powered market scanning tools
6. **AIAnalysisTab.tsx** - Deep AI analysis of individual stocks

#### Supporting Components
- `ApiHealthStatus.tsx` - Shows API connection status
- `DataQualityIndicator.tsx` - Indicates data quality (real-time vs cached)
- `AlertConfigModal.tsx` - Modal for configuring alerts
- `TabNavigation.tsx` - Reusable tab navigation component
- `StockScoutReport.tsx` - Detailed stock analysis report

#### Hooks
- `useStockPrices.ts` - Real-time price updates
- `useMarketData.ts` - Market overview data
- `usePortfolioData.ts` - Portfolio positions and analytics
- `useWatchlists.ts` - Watchlist management
- `useAlerts.ts` - Alert management
- `useStockAnalysis.ts` - AI analysis functionality
- `useAIAlerts.ts` - AI-generated alerts

### Backend API Endpoints
Base URL: `/api/agent-orchestra/stocks/`

## Tab-by-Tab Functionality

### Tab 1: Market Overview
**Purpose**: Display real-time market indices and trending stocks

**Features**:
- Major indices (S&P 500, NASDAQ, DOW)
- Market status and hours
- Top gainers/losers
- Most active stocks
- Real-time connection indicator
- Data quality indicator

**API Endpoints**:
- `GET /api/agent-orchestra/stocks/market-overview/` - Market summary data
- `GET /api/agent-orchestra/stocks/quote/{ticker}/` - Individual stock quotes

**Status**: ✅ Fully functional with real data

### Tab 2: Portfolio
**Purpose**: Track portfolio positions and performance

**Features**:
- Total portfolio value
- Individual position tracking
- Gain/loss calculations
- Portfolio analytics by timeframe
- Diversification metrics
- Best/worst performers

**API Endpoints**:
- `GET /api/agent-orchestra/stocks/portfolio/` - Portfolio summary
- `GET /api/agent-orchestra/stocks/portfolio/analytics/` - Performance analytics
- `POST /api/agent-orchestra/stocks/portfolio/add-position/` - Add position
- `DELETE /api/agent-orchestra/stocks/portfolio/remove-position/` - Remove position

**Status**: ⚠️ Backend returns empty portfolio (no test data)

### Tab 3: Watchlists
**Purpose**: Create and manage custom stock watchlists

**Features**:
- Multiple watchlist support
- Add/remove stocks
- Quick access to watched stocks
- Real-time price updates for watchlist items
- Default watchlist designation

**API Endpoints**:
- `GET /api/agent-orchestra/stocks/watchlists/` - List all watchlists
- `POST /api/agent-orchestra/stocks/watchlists/` - Create watchlist
- `PATCH /api/agent-orchestra/stocks/watchlists/{id}/` - Update watchlist
- `DELETE /api/agent-orchestra/stocks/watchlists/{id}/` - Delete watchlist
- `POST /api/agent-orchestra/stocks/watchlists/{id}/add-stock/` - Add stock
- `POST /api/agent-orchestra/stocks/watchlists/{id}/remove-stock/` - Remove stock

**Status**: ✅ Functional, currently empty (no watchlists created)

### Tab 4: Alerts
**Purpose**: Configure price and news alerts for stocks

**Features**:
- Price threshold alerts (above/below)
- Volume spike alerts
- News alerts
- Alert history
- Active/inactive toggle
- Alert notifications

**API Endpoints**:
- `GET /api/agent-orchestra/stocks/alerts/list/` - List all alerts
- `POST /api/agent-orchestra/stocks/alerts/create/` - Create alert
- `PATCH /api/agent-orchestra/stocks/alerts/{id}/update/` - Update alert
- `DELETE /api/agent-orchestra/stocks/alerts/{id}/delete/` - Delete alert

**Status**: ✅ Functional, currently empty (no alerts configured)

### Tab 5: Market Scanner (AI Scanner)
**Purpose**: AI-powered market scanning for opportunities

**Scanner Types**:
1. **Breakout Scanner** - Stocks breaking resistance levels
2. **Earnings Play** - Upcoming earnings catalysts
3. **Momentum Scanner** - High momentum with volume
4. **Value Scanner** - Undervalued fundamentals
5. **Dividend Scanner** - High-yield dividend stocks
6. **Custom Scan** - User-defined criteria

**API Endpoints**:
- `POST /api/agent-orchestra/stocks/scan/` - Run market scan
- `GET /api/agent-orchestra/stocks/scan-results/` - Get scan results

**Status**: 🚧 Frontend UI complete, backend implementation TODO

### Tab 6: AI Analysis
**Purpose**: Deep AI-powered analysis of individual stocks

**Features**:
- Comprehensive stock analysis
- Buy/Sell/Hold recommendations
- Confidence scores
- Price targets
- Key insights
- Risk factors
- Opportunities
- Financial highlights
- Multiple analysis types

**API Endpoints**:
- `POST /api/agent-orchestra/stocks/analyze/` - Request AI analysis
- `GET /api/agent-orchestra/stocks/analyses/` - List all analyses
- `GET /api/agent-orchestra/stocks/analyses/{id}/` - Get specific analysis

**Status**: ✅ Functional, awaiting stock selection for analysis

## Data Sources

### Primary APIs
1. **Polygon.io** - Real-time stock quotes and market data
2. **News API** - Stock news and sentiment
3. **Internal AI Agents** - Analysis and recommendations

### Data Quality Indicators
- **Real-time**: Live data from Polygon.io
- **Cached**: Recent data from cache (< 5 minutes old)
- **Fallback**: Static/mock data when APIs unavailable

## WebSocket Support
Real-time price updates via WebSocket connection:
- Endpoint: `ws://localhost:8000/ws/stocks/`
- Events: price updates, alert triggers, analysis completion

## Authentication
All endpoints require Token authentication:
```
Authorization: Token YOUR_TOKEN_HERE
```

## Common Issues and Solutions

### Issue: No data showing in Portfolio tab
**Solution**: Portfolio needs to be populated with positions first. Use the add position endpoint or UI.

### Issue: Market Scanner not returning results
**Solution**: Scanner backend implementation is TODO. Frontend UI is ready.

### Issue: Real-time prices not updating
**Solution**: Check WebSocket connection status indicator. Ensure backend WebSocket service is running.

## Testing the Feature

### Quick Test Script
```bash
# Test all stock endpoints
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/agent-orchestra/stocks/market-overview/

# Create a watchlist
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tech Stocks", "tickers": ["AAPL", "GOOGL", "MSFT"]}' \
  http://localhost:8000/api/agent-orchestra/stocks/watchlists/

# Request AI analysis
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "analysis_type": "comprehensive"}' \
  http://localhost:8000/api/agent-orchestra/stocks/analyze/
```

## Future Enhancements

1. **Portfolio Management**
   - Transaction history
   - Performance attribution
   - Tax lot tracking
   - Rebalancing suggestions

2. **Advanced Analytics**
   - Options chain analysis
   - Technical indicators
   - Backtesting capabilities
   - Risk metrics (Sharpe, Beta, etc.)

3. **Social Features**
   - Share watchlists
   - Follow other traders
   - Community sentiment
   - Discussion forums

4. **Automation**
   - Automated trading rules
   - Alert-based actions
   - Portfolio rebalancing
   - Dollar-cost averaging

## Development Status

| Component | Status | Notes |
|-----------|--------|-------|
| Market Overview | ✅ Complete | Real-time data working |
| Portfolio | ⚠️ Partial | UI complete, needs data |
| Watchlists | ✅ Complete | Fully functional |
| Alerts | ✅ Complete | Fully functional |
| Market Scanner | 🚧 In Progress | UI done, backend TODO |
| AI Analysis | ✅ Complete | Fully functional |
| WebSocket | ⚠️ Partial | Basic implementation |
| API Health | ✅ Complete | Monitoring working |

## Key Files Reference

### Frontend
- Main: `/src/features/stock-intelligence/pages/StockIntelligence.tsx`
- Tabs: `/src/features/stock-intelligence/components/*Tab.tsx`
- Hooks: `/src/features/stock-intelligence/hooks/*.ts`
- Services: `/src/services/api/stocks.service.ts`

### Backend
- Views: `/backend/agent_orchestra/views_stocks.py`
- Models: `/backend/stocks/models.py`
- URLs: `/backend/agent_orchestra/urls.py` (stocks section)
- Services: `/backend/agent_orchestra/services/stock_*.py`
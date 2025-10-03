# Changelog - July 17, 2025

## WebSocket Connection Management Improvements

### Added
- **Connection Throttling System** (`connectionThrottle.ts`)
  - Prevents WebSocket connection flooding
  - Max 3 connection attempts per endpoint within 10 seconds
  - Global limit of 5 concurrent connections
  - Automatic cleanup of old connection attempts

- **WebSocket Debug Tools** (`websocketDebug.ts`)
  - Browser console utilities for debugging
  - Commands: `wsDebug.getStats()`, `wsDebug.monitor()`, `wsDebug.reset()`, `wsDebug.traceConnections()`
  - Real-time connection monitoring
  - Stack trace logging for connection creation

### Fixed
- WebSocket connection loop issue causing hundreds of rapid reconnections
- Updated WebSocketManager to use connection throttling
- Removed duplicate reconnection logic

## Polygon API Service Refactoring

### Added
- **Modular Polygon Services** (`backend/agent_orchestra/services/polygon/`)
  - `base.py` - Base service with common functionality
  - `stocks.py` - Stock quotes, aggregates, technical indicators
  - `indices.py` - Market indices using ETF proxies
  - `options.py` - Options chains and analytics
  - `crypto.py` - Cryptocurrency data
  - `forex.py` - Foreign exchange rates
  - `market.py` - Market-wide data, gainers/losers

- **Unified Service Wrapper** (`polygon_unified.py`)
  - Maintains backward compatibility
  - Wraps all modular services
  - Single import for existing code

- **Market Movers Endpoint**
  - New `get_market_movers()` method in PolygonMarketService
  - Returns top gainers, losers, and most active stocks
  - Proper error handling with mock data fallback

### Fixed
- `NameError: name 'polygon_service' is not defined` errors
- Updated all imports from old `PolygonAPIService` to new modular services
- Fixed trending stocks endpoint to return real data instead of empty results
- Top Gainers/Losers now display properly on Stock Intelligence page

## Other Fixes

### Backend
- Fixed DRF Response object caching error in `cache_decorators.py`
- Updated stock tracking views to use correct service instances
- Added proper service cleanup in finally blocks

### Frontend
- Updated imports to include WebSocket debug tools
- Added conditional loading of debug tools in development mode

## Migration Notes

### For Developers
1. Old `PolygonAPIService` imports should be updated to use specific services:
   ```python
   # Old
   from .services.polygon_api_service import PolygonAPIService
   
   # New
   from .services.polygon.stocks import PolygonStocksService
   from .services.polygon.indices import PolygonIndicesService
   # etc.
   ```

2. Or use the unified service for backward compatibility:
   ```python
   from .services.polygon_unified import PolygonUnifiedService
   polygon = PolygonUnifiedService()
   ```

3. WebSocket debugging available in browser console:
   ```javascript
   wsDebug.getStats()     // View connection statistics
   wsDebug.monitor()      // Start real-time monitoring
   wsDebug.reset()        // Reset all connections
   ```

## Files Changed

### Backend
- `/backend/agent_orchestra/services/polygon/` (new directory)
- `/backend/agent_orchestra/services/polygon_unified.py` (new)
- `/backend/agent_orchestra/services/polygon_migration.py` (new)
- `/backend/agent_orchestra/views_stock_tracking.py` (modified)
- `/backend/core/decorators/cache_decorators.py` (modified)

### Frontend
- `/donkey-betz-frontend/src/services/websocket/connectionThrottle.ts` (new)
- `/donkey-betz-frontend/src/utils/websocketDebug.ts` (new)
- `/donkey-betz-frontend/src/services/websocket/WebSocketManager.ts` (modified)
- `/donkey-betz-frontend/src/App.tsx` (modified)

### Documentation
- `/CLAUDE.md` (updated)
- `/WEBSOCKET_DEBUG_PLAN.md` (new)
- `/CHANGELOG_2025_07_17.md` (this file)
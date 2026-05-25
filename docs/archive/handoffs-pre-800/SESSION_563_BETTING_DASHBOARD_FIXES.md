# Session 563: Betting Dashboard Sub-Tab Fixes

**Date:** December 27, 2025
**Status:** COMPLETE
**Focus:** Fix all Betting Dashboard sub-tabs to load data correctly

---

## Summary

Fixed multiple Betting Dashboard sub-tabs that weren't loading data correctly due to:
1. Incorrect API field mappings
2. Broken event listeners for tab activation
3. Wrong default filter values

---

## Commits

1. `df3f81d` - Bet tracking backend - parlays & wager history
2. `b0eec38` - Bet history UI with comprehensive stats display
3. `0653b3e` - Value Plays now loads correctly from live odds API
4. `f058188` - Futures API now extracts teams from contenders array
5. `20d9e94` - Line Movement tab now functional with Show All option
6. `632a4fc` - Line Movement uses regular fetch for public APIs
7. `a35bbf4` - Line Movement tab now loads data correctly
8. `564c114` - Prediction Markets now displays Kalshi data correctly
9. `ee4f75c` - Arbitrage tab uses authenticatedFetch and robust events

---

## Fixes Applied

### 1. Value Plays Section (Overview Tab)
**Problem:** Showed "use /odds in Discord" instead of actual data
**Root Cause:** Code used `.find()` on markets which was a dictionary, not an array
**Fix:** Changed to `bm.markets?.h2h` and added `&markets=h2h` to API request

### 2. Futures Tab
**Problem:** API returned placeholder data with zero odds
**Root Cause:** Spider returns futures with `contenders` array, view expected individual entries
**Fix:** Updated view to loop through `future.get('contenders', [])` and extract each team

### 3. Line Movement Tab
**Problem:** Nothing displayed, migrations were broken
**Root Cause:**
- Migration 0126 was marked as applied but tables weren't created
- Default threshold (0.5+) filtered out all games (only 1 snapshot, all movements = 0)
- Used `authenticatedFetch` which might fail for some users
**Fix:**
- Re-applied migrations properly
- Changed default threshold to "Show All"
- Added robust event handling (event delegation + click fallback)

### 4. Prediction Markets Tab
**Problem:** Markets not displaying with correct probabilities
**Root Cause:** JS looked for `yes_price`/`probability` but Kalshi API returns `implied_probability`/`last_price`
**Fix:** Updated field mapping to use correct Kalshi API fields

### 5. Arbitrage Tab
**Problem:** Tab not auto-loading when clicked
**Root Cause:** Event listener not attaching correctly
**Fix:** Added robust event handling (event delegation + click fallback)

---

## Pattern Applied to All Tabs

All betting sub-tabs now use this robust event pattern:

```javascript
// Event delegation for tab shown
document.addEventListener('shown.bs.tab', function(event) {
    if (event.target && event.target.id === 'betting-{tab}-tab') {
        console.log('[{Tab}] Tab shown, loading data...');
        loadFunction();
    }
});

// Click fallback
document.getElementById('betting-{tab}-tab')?.addEventListener('click', function() {
    console.log('[{Tab}] Tab clicked, loading data...');
    setTimeout(loadFunction, 100);
});
```

---

## Files Modified

- `ai_core/templates/components/panels/betting/betting_overview.html`
- `ai_core/templates/components/panels/betting/betting_line_movement.html`
- `ai_core/templates/components/panels/betting/betting_markets.html`
- `ai_core/templates/components/panels/betting/betting_arbitrage.html`
- `core/views_odds_sports.py` (Futures API fix)

---

## Remaining Sub-Tabs Status

| Tab | Status | Notes |
|-----|--------|-------|
| Overview | WORKING | Value Plays, Bet History functional |
| Live Odds | WORKING | Already functional |
| Arbitrage | WORKING | Loads when clicked |
| Prediction Markets | WORKING | Shows Kalshi data correctly |
| Bankroll | NOT TESTED | May need similar fixes |
| Futures | WORKING | Teams extracted correctly |
| Line Movement | WORKING | Shows all games, needs more snapshots for movement data |
| Alerts | NOT TESTED | May need similar fixes |

---

## Session 564 Recommendations

1. **Test Bankroll and Alerts tabs** - Apply same event listener pattern if needed
2. **Run more odds snapshots** - Line Movement will show actual movement after multiple snapshots
3. **Consider WebSocket for real-time updates** - Arbitrage and Line Movement could benefit from live updates

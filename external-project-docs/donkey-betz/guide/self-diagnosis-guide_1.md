# Self-Diagnosis System Integration Guide

## Overview
The Main Assistant has a complete self-diagnosis and debugging system that tracks performance, 
identifies patterns, and generates improvement suggestions.

## Available API Endpoints

### 1. Main Self-Diagnosis
```
GET /api/ai-partner/self-diagnosis/?hours=24&include_details=true
```
Returns comprehensive system health analysis including:
- Overall health score and status
- Performance metrics (response times, cache hit rates)
- Error analysis and recovery rates
- Learning progress and active anchors
- Actionable improvement suggestions

### 2. Session Analysis
```
GET /api/ai-partner/self-diagnosis/session/<session_id>/
```
Get detailed analysis of a specific debug session.

### 3. Performance Baselines
```
GET /api/ai-partner/self-diagnosis/baselines/
```
View historical performance baselines for trend analysis.

### 4. System Insights
```
GET /api/ai-partner/self-diagnosis/insights/
```
List of system-generated insights with patterns and recommendations.

### 5. Health History
```
GET /api/ai-partner/self-diagnosis/health-history/
```
Historical health snapshots for trend analysis.

## Integration Steps

### 1. Add to Frontend Routes
```typescript
// In your routes configuration
{
  path: '/self-diagnosis',
  component: SelfDiagnosisDashboard,
  meta: { requiresAuth: true, requiresAdmin: true }
}
```

### 2. Add Navigation Link
```typescript
// In your admin navigation
{
  label: 'Self-Diagnosis',
  icon: Brain,
  path: '/self-diagnosis',
  adminOnly: true
}
```

### 3. Enable Debug Logging
Make sure debug logging is enabled in your Django settings:
```python
DEBUG_FLOW_LOGGING_ENABLED = True
```

## What's Already Working

✅ **Debug Flow Logger** - Tracks every step in the Main Assistant pipeline
✅ **Session Analysis** - Analyzes patterns across debug sessions  
✅ **Performance Baselines** - Tracks performance metrics over time
✅ **System Insights** - Generates actionable improvement suggestions
✅ **Self-Learning Integration** - Tracks learning progress and reinforcement

## Safe Enhancement Ideas

### 1. Real-time Monitoring Widget
Add a small widget to admin dashboard showing current health score.

### 2. Performance Alerts
Set up alerts when performance degrades below thresholds.

### 3. Automated Reports
Schedule weekly self-diagnosis reports via email.

### 4. Trend Visualization
Add charts showing performance trends over time.

## Testing the System

Run a manual self-diagnosis test:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/ai-partner/self-diagnosis/
```

The system is fully functional and just needs better visibility!

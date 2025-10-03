# MEDIUM PRIORITY ISSUE: Universal Styling Not Applied

## Status: ❌ NOT ADDRESSED

## Issue Description
5 major AI Insights components are not using the universal styling system, causing:
- Inconsistent appearance
- Theme switching broken
- Accessibility features missing
- Dark mode not working

## Affected Components
1. **MemoryTimeline** component
2. **AgentPerformance** component  
3. **KnowledgeGraph** component
4. **InsightsDashboard** component
5. **PredictionAccuracy** component

## Current Problem
```typescript
// Components using inline styles (WRONG)
<div style={{ backgroundColor: '#fff', color: '#000' }}>

// Should use universal styling context
import { useUniversalStyles } from '@/contexts/UniversalStyleContext';
const styles = useUniversalStyles();
<div className={styles.container}>
```

## Impact
- **Visual Inconsistency**: Different look from rest of app
- **Theme Support**: Dark mode doesn't work
- **Accessibility**: Missing ARIA attributes and keyboard navigation
- **Maintainability**: Styles scattered across components

## Required Changes

### 1. Import Universal Style Context
```typescript
// Add to each component
import { useUniversalStyles } from '@/contexts/UniversalStyleContext';
import { useTheme } from '@/contexts/ThemeContext';
```

### 2. Replace Inline Styles
```typescript
// Before (WRONG)
<div style={{ 
  backgroundColor: '#ffffff',
  padding: '20px',
  borderRadius: '8px'
}}>

// After (CORRECT)
<div className={cn(
  styles.card,
  styles.padding.lg,
  styles.rounded.md
)}>
```

### 3. Update Chart Themes
```typescript
// Charts need theme-aware colors
const chartColors = theme.isDark ? {
  background: '#1a1a1a',
  text: '#ffffff',
  grid: '#333333'
} : {
  background: '#ffffff',
  text: '#000000',
  grid: '#e0e0e0'
};
```

### 4. Add Accessibility
```typescript
// Add ARIA attributes
<div 
  role="region"
  aria-label="Memory Timeline"
  tabIndex={0}
  onKeyDown={handleKeyboardNavigation}
>
```

### 5. Responsive Design
```typescript
// Use universal breakpoints
<div className={cn(
  styles.grid,
  styles.responsive.sm.cols1,
  styles.responsive.md.cols2,
  styles.responsive.lg.cols3
)}>
```

## Files to Update
- `donkey-betz-frontend/src/features/ai-insights/MemoryTimeline.tsx`
- `donkey-betz-frontend/src/features/ai-insights/AgentPerformance.tsx`
- `donkey-betz-frontend/src/features/ai-insights/KnowledgeGraph.tsx`
- `donkey-betz-frontend/src/features/ai-insights/InsightsDashboard.tsx`
- `donkey-betz-frontend/src/features/ai-insights/PredictionAccuracy.tsx`

## Testing Checklist
- [ ] Dark mode toggles correctly
- [ ] Consistent spacing and typography
- [ ] Responsive on mobile/tablet/desktop
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Charts update with theme

## Universal Style Benefits
- Single source of truth for styles
- Automatic theme switching
- Built-in accessibility
- Consistent spacing system
- Responsive utilities
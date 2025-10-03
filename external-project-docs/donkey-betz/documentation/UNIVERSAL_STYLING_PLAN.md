# Universal Styling Implementation Plan - AI Insights Dashboard

## Overview
This document outlines the plan to update all AI Insights Dashboard components to use the universal styling context, ensuring consistent theming and design across the application.

## Components to Update

### 1. Main Dashboard Component
**File**: `donkey-betz-frontend/src/features/ai-agent/AIInsights.tsx`
- [ ] Import `useUniversalStyling` hook
- [ ] Replace inline styles with universal styles
- [ ] Update card wrappers to use `styles.cards.default`
- [ ] Apply consistent spacing with `styles.spacing`

### 2. Performance Tab
**File**: `donkey-betz-frontend/src/features/ai-agent/tabs/PerformanceTab.tsx`
- [ ] Import universal styling context
- [ ] Update metric cards to use `styles.cards.metric`
- [ ] Apply theme colors to charts
- [ ] Use `styles.colors.success/warning/error` for status indicators

### 3. Active Agents Tab
**File**: `donkey-betz-frontend/src/features/ai-agent/tabs/ActiveAgentsTab.tsx`
- [ ] Import universal styling
- [ ] Update agent cards with `styles.cards.agent`
- [ ] Apply `styles.status` for agent status badges
- [ ] Use theme-aware progress bars

### 4. Knowledge Graph Tab
**File**: `donkey-betz-frontend/src/features/ai-agent/tabs/KnowledgeGraphTab.tsx`
- [ ] Import universal styling
- [ ] Update graph container styling
- [ ] Apply theme colors to nodes and edges
- [ ] Use `styles.cards.visualization` for graph container

### 5. Recent Insights Tab
**File**: `donkey-betz-frontend/src/features/ai-agent/tabs/RecentInsightsTab.tsx`
- [ ] Import universal styling
- [ ] Update insight cards with `styles.cards.insight`
- [ ] Apply confidence indicators with theme colors
- [ ] Use `styles.typography` for text hierarchy

### 6. Analytics Tab
**File**: `donkey-betz-frontend/src/features/ai-agent/tabs/AnalyticsTab.tsx`
- [ ] Import universal styling
- [ ] Update chart containers
- [ ] Apply theme colors to all Recharts components
- [ ] Use `styles.grid` for layout

## Universal Styling Structure

### Import Pattern
```typescript
import { useUniversalStyling } from '@/hooks/useUniversalStyling';

const Component = () => {
  const styles = useUniversalStyling();
  
  return (
    <div style={styles.cards.default}>
      {/* Component content */}
    </div>
  );
};
```

### Common Style Replacements

| Current Style | Universal Style |
|---------------|-----------------|
| `backgroundColor: '#ffffff'` | `styles.cards.default.backgroundColor` |
| `borderRadius: '8px'` | `styles.cards.default.borderRadius` |
| `padding: '16px'` | `styles.spacing.md` |
| `color: '#333'` | `styles.colors.text.primary` |
| `boxShadow: '0 2px 4px rgba(0,0,0,0.1)'` | `styles.shadows.sm` |
| `margin: '8px'` | `styles.spacing.sm` |
| `fontSize: '14px'` | `styles.typography.body.fontSize` |
| `fontWeight: 'bold'` | `styles.typography.heading.fontWeight` |

### Chart Color Updates
Replace hardcoded chart colors with theme-aware colors:

```typescript
// Before
const colors = ['#8884d8', '#82ca9d', '#ffc658'];

// After
const colors = [
  styles.colors.primary,
  styles.colors.success,
  styles.colors.warning
];
```

### Status Indicators
Use semantic colors for status:

```typescript
// Before
const statusColor = status === 'success' ? '#4caf50' : '#f44336';

// After
const statusColor = status === 'success' 
  ? styles.colors.success 
  : styles.colors.error;
```

## Implementation Steps

### Phase 1: Core Components (1-2 hours)
1. Update main AIInsights.tsx component
2. Create reusable styled wrapper components
3. Test theme switching functionality

### Phase 2: Tab Components (2-3 hours)
1. Update each tab component sequentially
2. Ensure consistent spacing and padding
3. Verify responsive behavior

### Phase 3: Charts and Visualizations (1-2 hours)
1. Update all Recharts components with theme colors
2. Update D3.js visualizations (Knowledge Graph)
3. Ensure accessibility with proper contrast ratios

### Phase 4: Testing and Polish (1 hour)
1. Test dark/light theme switching
2. Verify mobile responsiveness
3. Check for any hardcoded styles missed
4. Performance testing with theme changes

## Benefits of Universal Styling

1. **Consistency**: All components follow the same design language
2. **Maintainability**: Single source of truth for styles
3. **Theme Support**: Easy switching between light/dark themes
4. **Accessibility**: Centralized contrast and sizing controls
5. **Performance**: Reduced inline style calculations
6. **Developer Experience**: Cleaner, more readable components

## Testing Checklist

- [ ] All components render correctly with default theme
- [ ] Theme switching works without layout shifts
- [ ] Charts update colors dynamically with theme
- [ ] No console warnings about invalid styles
- [ ] Mobile responsive views maintain styling
- [ ] Loading states use universal skeleton styles
- [ ] Error states use universal error styling
- [ ] All text remains readable in both themes
- [ ] Focus states are properly styled
- [ ] Hover effects follow universal patterns

## Notes

- The universal styling system is already implemented in the codebase
- Focus on replacing inline styles rather than creating new style definitions
- Maintain existing component functionality while updating styles
- Document any edge cases or exceptions found during implementation

## References

- Universal Styling Hook: `/hooks/useUniversalStyling.ts`
- Theme Configuration: `/styles/theme.ts`
- Existing Examples: Analytics Dashboard components that already use universal styling
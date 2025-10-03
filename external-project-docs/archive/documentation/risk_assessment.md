# Risk Assessment - Database Field Naming Standardization

## Executive Summary

Based on the comprehensive audit of 122 Django models across 16 apps, we've identified significant field naming inconsistencies that impact development efficiency and increase error rates. This document assesses the risks of standardization and provides a migration strategy.

## Key Statistics

- **446 usages** of `created_at` across the codebase
- **54 usages** of non-standard `started_at` (should be `created_at`)
- **61 models** use standard `user` ForeignKey
- **97 boolean fields** with 3 different naming conventions
- **25 models** missing standard `created_at` field
- **92 models** missing standard `updated_at` field

## Risk Categories

### 🔴 HIGH RISK Changes (Extensive Usage)

These fields are used extensively and changes would require significant effort:

1. **`created_at` standardization**
   - Risk: Used in 446 locations
   - Impact: Order_by clauses (170), Serializers (126), Direct access (81)
   - Migration complexity: HIGH
   - Recommendation: Create compatibility layer first

2. **`user` field references**
   - Risk: 61 models with direct references
   - Impact: Authentication, permissions, all user-related queries
   - Migration complexity: VERY HIGH
   - Recommendation: Maintain current pattern

3. **Core timestamp fields in active models**
   - Models: agent_orchestra, ai_partner, core
   - Risk: Production data and active features
   - Impact: Could break running orchestrations
   - Recommendation: Phased migration with backwards compatibility

### 🟡 MEDIUM RISK Changes (Moderate Usage)

These changes have moderate impact and can be migrated with care:

1. **`started_at` → `created_at`**
   - Risk: 54 usages, mostly in agent_orchestra
   - Impact: Order_by queries (38), some serializers
   - Migration complexity: MEDIUM
   - Recommendation: Add property aliases during transition

2. **`completed_at` standardization**
   - Risk: 39 usages
   - Impact: Task completion logic
   - Migration complexity: MEDIUM
   - Recommendation: Can be migrated per-app

3. **Boolean field prefixes**
   - Risk: Mixed patterns (is_, has_, bare names)
   - Impact: Mostly cosmetic, some API contracts
   - Migration complexity: LOW-MEDIUM
   - Recommendation: Standardize new fields only

### 🟢 LOW RISK Changes (Limited Usage)

These can be changed with minimal impact:

1. **Rarely used timestamp variants**
   - Fields: `end_time` (7), `start_date` (3)
   - Impact: Minimal, localized to specific features
   - Migration complexity: LOW
   - Recommendation: Direct migration possible

2. **App-specific fields**
   - Apps: mythology_lab, shame, walking_companion
   - Impact: Isolated to specific features
   - Migration complexity: LOW
   - Recommendation: Can be migrated immediately

3. **Unused or deprecated fields**
   - Fields with 0-2 usages
   - Impact: None to minimal
   - Migration complexity: TRIVIAL
   - Recommendation: Clean up immediately

## Impact Analysis by App

### Critical Apps (DO NOT TOUCH without extensive testing)
1. **agent_orchestra** - Central to platform operation
2. **ai_partner** - Core user experience
3. **core** - Foundation models
4. **accounts** - Authentication system

### Safe to Migrate Apps
1. **mythology_lab** - Experimental feature
2. **shame** - Isolated gamification
3. **walking_companion** - Standalone feature
4. **ml_models** - Backend processing

## Database Migration Risks

### Data Integrity Risks
- **Foreign Key Constraints**: Renaming user reference fields
- **Unique Constraints**: May need recreation
- **Indexes**: Will need rebuilding (performance impact)
- **Triggers/Procedures**: May reference old column names

### Performance Risks
- **Large Tables**: Schema changes will lock tables
- **Index Rebuilds**: Can take hours on large tables
- **Query Plan Changes**: May need optimization

### Application Risks
- **ORM Queries**: All need updating
- **Raw SQL**: Harder to find and fix
- **API Contracts**: Breaking changes for clients
- **Serializers**: Field name changes break compatibility

## Migration Strategy

### Phase 1: Preparation (Week 1)
1. Create comprehensive test suite for affected models
2. Set up compatibility layer utilities
3. Document all API contracts
4. Create rollback procedures

### Phase 2: Low-Risk Changes (Week 2)
1. Fix unused/low-usage fields
2. Standardize new model creation
3. Update development guidelines
4. Create pre-commit hooks

### Phase 3: Compatibility Layer (Week 3-4)
1. Add property aliases for high-risk fields
2. Create dual-write mechanisms
3. Update serializers with both names
4. Test extensively in staging

### Phase 4: Gradual Migration (Week 5-8)
1. Migrate one app at a time
2. Start with low-risk apps
3. Monitor error rates
4. Keep compatibility layer active

### Phase 5: Cleanup (Week 9-10)
1. Remove compatibility layers
2. Update all documentation
3. Final testing
4. Archive old field names

## Recommended Quick Wins

### Immediate Actions (No Code Changes)
1. Document standard conventions
2. Create model templates
3. Set up linting rules
4. Train team on standards

### Low-Risk Improvements
1. Fix models with 0 usages
2. Standardize boolean prefixes in new code
3. Add missing `updated_at` to inactive models
4. Create model mixins for common patterns

### Developer Tools
1. Pre-commit hooks for new models
2. Django check command for validation
3. Auto-generation of compatibility properties
4. Migration impact analyzer

## Cost-Benefit Analysis

### Costs
- Development time: ~160 hours
- Testing time: ~80 hours  
- Risk of production issues
- Temporary performance impact
- API versioning complexity

### Benefits
- Reduced development errors
- Faster onboarding
- Cleaner codebase
- Better tooling support
- Consistent API design

### ROI Calculation
- Current error rate due to inconsistency: ~2-3 per week
- Time lost per error: ~2 hours
- Annual time savings: ~200-300 hours
- **Payback period: 6-8 months**

## Recommendation

**Proceed with phased migration focusing on:**

1. **Immediate**: Create standards and tooling
2. **Short-term**: Fix low-risk inconsistencies
3. **Medium-term**: Implement compatibility layers
4. **Long-term**: Gradual migration of high-risk fields

**Do NOT attempt:**
- Big-bang migration
- Changing user/auth fields without extensive planning
- Modifying production-critical models without compatibility layers

## Next Steps

1. Get stakeholder approval for migration plan
2. Create detailed technical design for compatibility layer
3. Set up monitoring for field-related errors
4. Begin with Phase 1 preparation tasks
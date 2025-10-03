# Service Consolidation Plan - Phase 7

## Current Situation Analysis

After reviewing the codebase, we have discovered:

1. **Heavy Service Interdependencies**: Many services are actively imported in critical files like `ai_partner/views.py`
2. **Active Usage**: Services we planned to delete are being used in production code
3. **Complex Import Chains**: Services import other services, creating dependency chains

## Revised Approach: Safe Incremental Consolidation

Instead of immediate deletion, we'll follow a safer approach:

### Step 1: Create Service Mapping (Migration Layer)

First, we'll create a service router that maps old service imports to new consolidated services without breaking existing code.

### Step 2: Services to Consolidate

#### Memory Search Services (Prioritized by Usage):
1. **enhanced_memory_service.py** → UnifiedMemorySearchService
   - 21 imports - most critical to handle carefully
   - Used in views, consumers, service registry
   
2. **reliable_memory_service.py** → BasicMemoryRetrieval
   - 2 imports - used as fallback
   
3. **fixed_memory_search.py** → UnifiedMemorySearchService
   - 6 imports - including agent_orchestra integration
   
4. **ukf_memory_service.py** → UnifiedMemorySearchService
   - 7 imports - already provides UKF integration
   
5. **memory_ranking_service.py** → Integrate into UnifiedMemorySearchService
   - 2 imports - ranking logic can be merged

6. **adaptive_retrieval_service.py** → Keep temporarily
   - 7 imports in learning services - needs special handling
   
7. **content_memory_service.py** → Keep temporarily  
   - 6 imports in content system - specialized functionality

8. **enhanced_memory_search_v2.py** → UnifiedMemorySearchService
   - 2 imports in views

#### Intelligent Prompting Services:
- Keep only `ai_partner/prompting_services/intelligent_prompt_service.py`
- Remove duplicates after updating imports

### Step 3: Services to Keep
1. **UnifiedMemorySearchService** - Primary search
2. **BasicMemoryRetrieval** - Fallback search
3. **intelligent_prompt_service.py** - Main prompting service

### Step 4: Migration Strategy

1. **Create Compatibility Layer** 
   - Add import redirects in `__init__.py` files
   - Maintain same API surface while routing to new services

2. **Update Critical Files First**
   - `ai_partner/views.py`
   - `ai_partner/consumers.py`
   - `agent_orchestra/memory_integration.py`

3. **Test Each Change**
   - Run tests after each service update
   - Verify no runtime errors

4. **Gradual Deprecation**
   - Mark old services as deprecated
   - Add warnings when used
   - Remove after verification period

## Implementation Order

1. Create backup directory
2. Set up import redirection
3. Update high-usage services first (enhanced_memory_service)
4. Test thoroughly
5. Continue with lower-usage services
6. Remove deprecated code only after all tests pass

## Risk Mitigation

- Keep all original files in backup
- Test each change incrementally
- Monitor error logs
- Have rollback plan ready

This approach will take longer but is much safer given the extensive interdependencies discovered.
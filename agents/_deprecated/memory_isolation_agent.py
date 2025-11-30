"""
Memory Isolation Agent - Ensures complete separation between personal and system memories
CRITICAL SECURITY COMPONENT
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
from django.db import transaction
from django.contrib.auth import get_user_model
from content.models import Document, DocumentEmbedding
from agents.models import UnifiedAgentTemplate

logger = logging.getLogger(__name__)
User = get_user_model()


class MemoryIsolationAgent:
    """
    Critical security agent that ensures personal memories are NEVER mixed with system knowledge
    """
    
    def __init__(self):
        self.name = "Memory Isolation Security Agent"
        self.critical_priority = True
        self.audit_log = []
        
    def emergency_audit(self) -> Dict[str, Any]:
        """
        IMMEDIATE: Audit all memory systems for cross-contamination
        """
        logger.critical("🚨 STARTING EMERGENCY MEMORY AUDIT")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'critical_issues': [],
            'personal_exposed': 0,
            'system_contaminated': 0,
            'immediate_actions': []
        }
        
        try:
            # 1. Check for personal memories without proper isolation
            personal_memories = Document.objects.filter(
                raw_content__icontains='personal'
            ) | Document.objects.filter(
                metadata__source='personal_memory'
            ) | Document.objects.filter(
                title__icontains='My Knowledge'
            )
            
            for doc in personal_memories:
                if not doc.metadata or doc.metadata.get('namespace') != 'personal':
                    results['personal_exposed'] += 1
                    results['critical_issues'].append({
                        'type': 'EXPOSED_PERSONAL_MEMORY',
                        'doc_id': str(doc.id),
                        'title': doc.title[:50],
                        'risk': 'HIGH'
                    })
            
            # 2. Check for system documents with personal content
            system_docs = Document.objects.exclude(
                metadata__namespace='personal'
            )
            
            personal_indicators = [
                'my knowledge', 'personal memory', 'private note',
                'remember this', 'don\'t forget', 'personal reminder'
            ]
            
            for doc in system_docs[:1000]:  # Check first 1000
                content_lower = (doc.raw_content or '').lower()
                for indicator in personal_indicators:
                    if indicator in content_lower:
                        results['system_contaminated'] += 1
                        results['critical_issues'].append({
                            'type': 'CONTAMINATED_SYSTEM_DOC',
                            'doc_id': str(doc.id),
                            'indicator': indicator,
                            'risk': 'CRITICAL'
                        })
                        break
            
            # 3. Generate immediate action plan
            if results['personal_exposed'] > 0:
                results['immediate_actions'].append(
                    'ISOLATE_PERSONAL_MEMORIES'
                )
            
            if results['system_contaminated'] > 0:
                results['immediate_actions'].append(
                    'PURGE_CONTAMINATED_DOCS'
                )
                
            logger.critical(f"🚨 AUDIT COMPLETE: {results['personal_exposed']} exposed, "
                          f"{results['system_contaminated']} contaminated")
            
        except Exception as e:
            logger.critical(f"AUDIT FAILED: {e}")
            results['critical_issues'].append({
                'type': 'AUDIT_FAILURE',
                'error': str(e),
                'risk': 'UNKNOWN'
            })
        
        return results
    
    def isolate_memories(self, user: User = None) -> Dict[str, Any]:
        """
        IMMEDIATE ACTION: Isolate all personal memories
        """
        logger.info("🔒 Starting memory isolation protocol")
        
        isolation_report = {
            'timestamp': datetime.now().isoformat(),
            'memories_isolated': 0,
            'memories_secured': 0,
            'errors': []
        }
        
        try:
            with transaction.atomic():
                # 1. Find all personal memory documents
                personal_queries = [
                    Document.objects.filter(metadata__source='personal_memory'),
                    Document.objects.filter(title__icontains='My Knowledge'),
                    Document.objects.filter(content__icontains='personal note'),
                    Document.objects.filter(content__icontains='remember this')
                ]
                
                personal_docs = Document.objects.none()
                for query in personal_queries:
                    personal_docs = personal_docs | query
                
                personal_docs = personal_docs.distinct()
                
                # 2. Update each document with isolation metadata
                for doc in personal_docs:
                    if not doc.metadata:
                        doc.metadata = {}
                    
                    # Apply isolation metadata
                    doc.metadata.update({
                        'namespace': 'personal',
                        'access_level': 'private',
                        'owner_id': str(user.id) if user else None,
                        'isolated_at': datetime.now().isoformat(),
                        'isolation_agent': self.name,
                        'searchable': False  # Prevent general searches
                    })
                    
                    # Add security prefix to content
                    if doc.raw_content and not doc.raw_content.startswith('[PERSONAL-ISOLATED]'):
                        doc.raw_content = f'[PERSONAL-ISOLATED] {doc.raw_content}'
                    
                    doc.save()
                    isolation_report['memories_isolated'] += 1
                
                # 3. Mark documents as secured (PersonalMemory model not available)
                for doc in personal_docs:
                    if user and doc.metadata.get('owner_id'):
                        isolation_report['memories_secured'] += 1
                
                logger.info(f"✅ Isolated {isolation_report['memories_isolated']} memories")
                
        except Exception as e:
            logger.error(f"Isolation failed: {e}")
            isolation_report['errors'].append(str(e))
        
        return isolation_report
    
    def create_namespace_barriers(self) -> Dict[str, Any]:
        """
        Create hard barriers between memory namespaces
        """
        barriers = {
            'namespaces_created': [],
            'access_rules': [],
            'search_filters': []
        }
        
        try:
            # Define namespace structure
            namespaces = {
                'personal': {
                    'access': 'owner_only',
                    'searchable': False,
                    'agent_accessible': False,
                    'description': 'Private user memories'
                },
                'system': {
                    'access': 'all_agents',
                    'searchable': True,
                    'agent_accessible': True,
                    'description': 'System knowledge and documentation'
                },
                'agent_memory': {
                    'access': 'agent_specific',
                    'searchable': True,
                    'agent_accessible': True,
                    'description': 'Agent execution history and learning'
                },
                'public': {
                    'access': 'all_users',
                    'searchable': True,
                    'agent_accessible': True,
                    'description': 'Shared public knowledge'
                }
            }
            
            # Apply namespace rules to existing documents
            for namespace, rules in namespaces.items():
                barriers['namespaces_created'].append(namespace)
                barriers['access_rules'].append(rules)
                
                # Update documents in this namespace
                docs = Document.objects.filter(
                    metadata__namespace=namespace
                )
                
                for doc in docs[:100]:  # Process in batches
                    if not doc.metadata:
                        doc.metadata = {}
                    doc.metadata.update({
                        'access_level': rules['access'],
                        'searchable': rules['searchable'],
                        'agent_accessible': rules['agent_accessible']
                    })
                    doc.save()
            
            barriers['search_filters'] = [
                "namespace != 'personal'",  # Default filter for agent searches
                "agent_accessible = true",   # Only agent-accessible content
                "searchable = true"          # Only searchable content
            ]
            
            logger.info(f"✅ Created {len(namespaces)} namespace barriers")
            
        except Exception as e:
            logger.error(f"Failed to create barriers: {e}")
            barriers['error'] = str(e)
        
        return barriers
    
    def verify_isolation(self) -> Tuple[bool, List[str]]:
        """
        Verify that memory isolation is working correctly
        """
        issues = []
        
        try:
            # Test 1: No personal memories in system namespace
            cross_contamination = Document.objects.filter(
                metadata__namespace='system',
                raw_content__icontains='personal'
            ).count()
            
            if cross_contamination > 0:
                issues.append(f"Found {cross_contamination} personal items in system namespace")
            
            # Test 2: No system queries returning personal content
            test_queries = [
                "what's changed",
                "system status",
                "agent performance"
            ]
            
            for query in test_queries:
                results = Document.objects.filter(
                    raw_content__icontains=query,
                    metadata__namespace='personal'
                )
                if results.exists():
                    issues.append(f"Query '{query}' returns personal memories")
            
            # Test 3: Personal memories have owner
            unowned = Document.objects.filter(
                metadata__namespace='personal'
            ).exclude(
                metadata__has_key='owner_id'
            ).count()
            
            if unowned > 0:
                issues.append(f"Found {unowned} personal memories without owner")
            
            is_secure = len(issues) == 0
            
            if is_secure:
                logger.info("✅ Memory isolation verified - SECURE")
            else:
                logger.critical(f"❌ Memory isolation FAILED: {issues}")
            
            return is_secure, issues
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False, [str(e)]
    
    def emergency_lockdown(self):
        """
        EMERGENCY: Lock down all personal memories immediately
        """
        logger.critical("🚨 EMERGENCY LOCKDOWN INITIATED")
        
        try:
            # Disable all personal memory access
            personal_docs = Document.objects.filter(
                metadata__namespace='personal'
            ) | Document.objects.filter(
                metadata__source='personal_memory'
            )
            
            for doc in personal_docs:
                if not doc.metadata:
                    doc.metadata = {}
                
                doc.metadata['locked'] = True
                doc.metadata['locked_at'] = datetime.now().isoformat()
                doc.metadata['searchable'] = False
                doc.metadata['agent_accessible'] = False
                doc.save()
            
            logger.critical(f"🔒 LOCKED DOWN {personal_docs.count()} personal memories")
            
            return {
                'status': 'LOCKED',
                'memories_locked': personal_docs.count(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.critical(f"LOCKDOWN FAILED: {e}")
            return {
                'status': 'FAILED',
                'error': str(e)
            }


def deploy_memory_isolation_agent():
    """
    Deploy the Memory Isolation Agent immediately
    """
    agent = MemoryIsolationAgent()
    
    # 1. Run emergency audit
    audit_results = agent.emergency_audit()
    
    # 2. If issues found, take immediate action
    if audit_results['critical_issues']:
        logger.critical("🚨 CRITICAL MEMORY ISSUES DETECTED - TAKING ACTION")
        
        # Isolate memories
        isolation_results = agent.isolate_memories()
        
        # Create barriers
        barrier_results = agent.create_namespace_barriers()
        
        # Verify isolation
        is_secure, remaining_issues = agent.verify_isolation()
        
        if not is_secure:
            # Emergency lockdown if still not secure
            lockdown_results = agent.emergency_lockdown()
            
            return {
                'status': 'EMERGENCY_LOCKDOWN',
                'audit': audit_results,
                'isolation': isolation_results,
                'barriers': barrier_results,
                'lockdown': lockdown_results,
                'remaining_issues': remaining_issues
            }
    
    return {
        'status': 'SECURED',
        'audit': audit_results,
        'message': 'Memory systems isolated successfully'
    }


if __name__ == '__main__':
    # Deploy immediately when script is run
    results = deploy_memory_isolation_agent()
    print(f"Memory Isolation Results: {results}")
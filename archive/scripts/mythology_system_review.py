#!/usr/bin/env python
"""
Mythology System Review for Unified Donkey Betz Platform
Detects and analyzes potential hallucinations, false claims, and mythology patterns
Based on the donkey_betz mythology lab system
"""

import os
import re
import json
import django
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
# Import models that exist
try:
    from core.models import UserProfile
except:
    UserProfile = None


class MythologySystemReview:
    """Review system for detecting mythology patterns in the unified platform"""
    
    # Known mythology patterns from the original system
    MYTHOLOGY_PATTERNS = {
        'numeric_inflation': r'\b\d{3,}\s*(deployments?|instances?|users?|systems?|agents?|embeddings?)\b',
        'false_authority': r'(studies show|experts confirm|research proves|scientists agree)',
        'context_loss': r'(we have|our system|the platform) (successfully|always|never)',
        'capability_exaggeration': r'(can do anything|unlimited|infinite|perfect|complete[ly]?)',
        'temporal_distortion': r'(has been|have been) .{0,20}(years?|months?|decades?)',
        'false_claims': r'(fitness dashboard|dart|flutter|main_navigation|dashboard_page)',
        'unverified_stats': r'(\d+%?\s*(success|accuracy|improvement|performance))',
    }
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'mythologies_found': [],
            'pattern_counts': defaultdict(int),
            'affected_components': set(),
            'risk_score': 0.0,
            'recommendations': []
        }
    
    def run_full_review(self) -> Dict[str, Any]:
        """Run comprehensive mythology review"""
        print("\n" + "="*60)
        print("🔍 MYTHOLOGY SYSTEM REVIEW - UNIFIED DONKEY BETZ")
        print("="*60 + "\n")
        
        # 1. Review embeddings for mythology
        print("1. Reviewing embeddings for mythology patterns...")
        self._review_embeddings()
        
        # 2. Review conversation logs
        print("\n2. Reviewing conversation logs...")
        self._review_conversations()
        
        # 3. Check for known false claims
        print("\n3. Checking for known false claims...")
        self._check_known_false_claims()
        
        # 4. Analyze system claims vs reality
        print("\n4. Analyzing system claims vs reality...")
        self._analyze_system_claims()
        
        # 5. Calculate risk score
        self._calculate_risk_score()
        
        # 6. Generate recommendations
        self._generate_recommendations()
        
        # Print results
        self._print_results()
        
        return self.results
    
    def _review_embeddings(self):
        """Review embeddings for mythology patterns"""
        try:
            # Check for embeddings table in PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '%embed%'
                """)
                tables = cursor.fetchall()
                
                if not tables:
                    print("  ℹ️ No embeddings table found")
                    return
                
                # Try to query embeddings - using unified_embeddings table
                cursor.execute("""
                    SELECT COUNT(*) FROM unified_embeddings
                """)
                total = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT id, content_text, created_at 
                    FROM unified_embeddings 
                    ORDER BY created_at DESC 
                    LIMIT 1000
                """)
                
                embeddings = cursor.fetchall()
                mythology_count = 0
                
                for emb_id, content, created_at in embeddings:
                    patterns_found = self._detect_patterns(content or '')
                    
                    if patterns_found:
                        mythology_count += 1
                        self.results['mythologies_found'].append({
                            'type': 'embedding',
                            'id': str(emb_id),
                            'patterns': patterns_found,
                            'content_preview': (content or '')[:200]
                        })
                        
                        for pattern in patterns_found:
                            self.results['pattern_counts'][pattern] += 1
                        
                        self.results['affected_components'].add('embeddings')
                
                print(f"  ✓ Reviewed {len(embeddings)} of {total} embeddings")
                if mythology_count > 0:
                    print(f"  ⚠️ Found mythology in {mythology_count} embeddings")
            
        except Exception as e:
            print(f"  ℹ️ Could not review embeddings: {e}")
    
    def _review_conversations(self):
        """Review conversation logs for mythology"""
        try:
            # Check if ConversationLog exists
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = 'core_conversationlog'
                """)
                if cursor.fetchone()[0] == 0:
                    print("  ℹ️ No conversation logs table found")
                    return
            
            # Get recent conversations
            cursor.execute("""
                SELECT id, user_message, assistant_response, created_at
                FROM core_conversationlog
                ORDER BY created_at DESC
                LIMIT 100
            """)
            
            conversations = cursor.fetchall()
            mythology_count = 0
            
            for conv_id, user_msg, assistant_msg, created_at in conversations:
                # Check assistant response for mythology
                patterns_found = self._detect_patterns(assistant_msg or '')
                
                if patterns_found:
                    mythology_count += 1
                    self.results['mythologies_found'].append({
                        'type': 'conversation',
                        'id': conv_id,
                        'patterns': patterns_found,
                        'timestamp': str(created_at),
                        'response_preview': (assistant_msg or '')[:200]
                    })
                    
                    for pattern in patterns_found:
                        self.results['pattern_counts'][pattern] += 1
                    
                    self.results['affected_components'].add('conversations')
            
            print(f"  ✓ Reviewed {len(conversations)} conversations")
            print(f"  ⚠️ Found mythology in {mythology_count} responses")
            
        except Exception as e:
            print(f"  ℹ️ Could not review conversations: {e}")
    
    def _check_known_false_claims(self):
        """Check for specific known false claims"""
        known_myths = {
            'fitness_dashboard': 'System claiming to be a fitness dashboard',
            'dart_flutter': 'References to Dart/Flutter (not used in this system)',
            '350_deployments': 'The mythical "350 deployments" claim',
            'unlimited_capabilities': 'Claims of unlimited or perfect capabilities'
        }
        
        try:
            with connection.cursor() as cursor:
                # Check embeddings for these specific myths
                for myth_key, myth_desc in known_myths.items():
                    count = 0
                    try:
                        if myth_key == 'fitness_dashboard':
                            cursor.execute("""
                                SELECT COUNT(*) FROM unified_embeddings 
                                WHERE content_text LIKE '%fitness dashboard%'
                            """)
                            count = cursor.fetchone()[0]
                        elif myth_key == 'dart_flutter':
                            cursor.execute("""
                                SELECT COUNT(*) FROM unified_embeddings 
                                WHERE content_text LIKE '%dart%' OR content_text LIKE '%flutter%'
                            """)
                            count = cursor.fetchone()[0]
                        elif myth_key == '350_deployments':
                            cursor.execute("""
                                SELECT COUNT(*) FROM unified_embeddings 
                                WHERE content_text LIKE '%350%' AND content_text LIKE '%deployment%'
                            """)
                            count = cursor.fetchone()[0]
                    except:
                        pass
                    
                    if count > 0:
                        print(f"  ⚠️ Found {count} instances of: {myth_desc}")
                        self.results['mythologies_found'].append({
                            'type': 'known_myth',
                            'myth': myth_key,
                            'description': myth_desc,
                            'count': count
                        })
        except Exception as e:
            print(f"  ℹ️ Could not check false claims: {e}")
    
    def _analyze_system_claims(self):
        """Analyze system claims vs reality"""
        claims_vs_reality = []
        
        try:
            with connection.cursor() as cursor:
                # Check claimed vs actual embeddings
                try:
                    cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
                    actual_embeddings = cursor.fetchone()[0]
                    print(f"\n  📊 Actual embeddings in database: {actual_embeddings}")
                    
                    # Check if system claims match reality
                    if actual_embeddings > 60000:
                        claims_vs_reality.append({
                            'claim': f'{actual_embeddings} embeddings',
                            'reality': 'Verified in database',
                            'status': 'accurate'
                        })
                except:
                    print("  ℹ️ Could not count embeddings")
                
                # Check for agent claims
                try:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT agent_name) 
                        FROM agents_agent
                    """)
                    actual_agents = cursor.fetchone()[0]
                    print(f"  📊 Actual agents in system: {actual_agents}")
                    
                    # Look for inflated agent claims in embeddings
                    cursor.execute("""
                        SELECT COUNT(*) FROM unified_embeddings
                        WHERE content_text LIKE '%74 agents%' 
                           OR content_text LIKE '%75 agents%'
                           OR content_text LIKE '%hundreds of agents%'
                    """)
                    inflated_claims = cursor.fetchone()[0]
                    
                    if inflated_claims > 0:
                        claims_vs_reality.append({
                            'claim': 'Inflated agent numbers',
                            'reality': f'Only {actual_agents} agents exist',
                            'status': 'mythology'
                        })
                except:
                    print("  ℹ️ Could not check agent claims")
                
        except Exception as e:
            print(f"  ℹ️ Could not analyze claims: {e}")
        
        self.results['claims_analysis'] = claims_vs_reality
    
    def _detect_patterns(self, text: str) -> List[str]:
        """Detect mythology patterns in text"""
        patterns_found = []
        
        for pattern_name, pattern_regex in self.MYTHOLOGY_PATTERNS.items():
            if re.search(pattern_regex, text, re.IGNORECASE):
                patterns_found.append(pattern_name)
        
        return patterns_found
    
    def _calculate_risk_score(self):
        """Calculate overall mythology risk score"""
        total_mythologies = len(self.results['mythologies_found'])
        pattern_diversity = len(self.results['pattern_counts'])
        
        # Base score on quantity and diversity of mythologies
        base_score = min(total_mythologies / 100, 0.5)  # Cap at 0.5
        diversity_score = min(pattern_diversity / 10, 0.3)  # Cap at 0.3
        
        # Add severity for specific patterns
        severity_boost = 0
        if 'false_claims' in self.results['pattern_counts']:
            severity_boost += 0.2
        if 'capability_exaggeration' in self.results['pattern_counts']:
            severity_boost += 0.1
        
        self.results['risk_score'] = min(base_score + diversity_score + severity_boost, 1.0)
    
    def _generate_recommendations(self):
        """Generate recommendations based on findings"""
        recommendations = []
        
        if self.results['risk_score'] > 0.7:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Immediate mythology cleanup required',
                'details': 'System has high mythology contamination'
            })
        
        if 'false_claims' in self.results['pattern_counts']:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Remove false claim embeddings',
                'details': 'Delete embeddings containing fitness/Dart references'
            })
        
        if 'numeric_inflation' in self.results['pattern_counts']:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Verify all numeric claims',
                'details': 'Audit and correct inflated statistics'
            })
        
        if len(self.results['affected_components']) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Implement mythology prevention',
                'details': f'Add guards to: {", ".join(self.results["affected_components"])}'
            })
        
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Deploy mythology monitoring',
            'details': 'Set up continuous mythology detection system'
        })
        
        self.results['recommendations'] = recommendations
    
    def _print_results(self):
        """Print formatted results"""
        print("\n" + "="*60)
        print("📋 MYTHOLOGY REVIEW RESULTS")
        print("="*60)
        
        # Risk score
        risk_level = "LOW" if self.results['risk_score'] < 0.3 else \
                     "MEDIUM" if self.results['risk_score'] < 0.7 else "HIGH"
        print(f"\n🎯 Overall Risk Score: {self.results['risk_score']:.2f} ({risk_level})")
        
        # Pattern summary
        print(f"\n📊 Mythology Patterns Found:")
        for pattern, count in sorted(self.results['pattern_counts'].items(), 
                                    key=lambda x: x[1], reverse=True):
            print(f"  • {pattern}: {count} instances")
        
        # Affected components
        if self.results['affected_components']:
            print(f"\n🔧 Affected Components:")
            for component in self.results['affected_components']:
                print(f"  • {component}")
        
        # Top mythologies
        if self.results['mythologies_found']:
            print(f"\n⚠️ Sample Mythologies Found:")
            for myth in self.results['mythologies_found'][:5]:
                print(f"  • Type: {myth['type']}")
                print(f"    Patterns: {', '.join(myth['patterns'])}")
                if 'content_preview' in myth:
                    preview = myth['content_preview'][:100]
                    print(f"    Preview: {preview}...")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        for rec in self.results['recommendations']:
            print(f"  [{rec['priority']}] {rec['action']}")
            print(f"         {rec['details']}")
        
        print("\n" + "="*60)
        print("Review complete!")
        
        # Save results to file
        output_file = 'mythology_review_results.json'
        with open(output_file, 'w') as f:
            # Convert set to list for JSON serialization
            results_copy = self.results.copy()
            results_copy['affected_components'] = list(results_copy['affected_components'])
            json.dump(results_copy, f, indent=2, default=str)
        print(f"\n📁 Results saved to: {output_file}")


if __name__ == '__main__':
    reviewer = MythologySystemReview()
    results = reviewer.run_full_review()
    
    # Return exit code based on risk level
    if results['risk_score'] > 0.7:
        exit(2)  # High risk
    elif results['risk_score'] > 0.3:
        exit(1)  # Medium risk
    else:
        exit(0)  # Low risk
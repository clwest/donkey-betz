#!/usr/bin/env python
"""
Enhanced Intelligent Routing Script
====================================

This script implements advanced routing strategies to reach 80%+ agent coverage:
1. Enhanced keyword matching (partial words, fuzzy matching, bi-directional)
2. Description-based routing (match spider data to agent descriptions)
3. Fallback category routing (broad categories for remaining agents)

Target: 142+ agents (80%+) from current 85 agents (48%)
"""

import os
import sys
import django
import re
from collections import defaultdict

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from persistence.models import SpiderData
from django.db.models import Count


# ============================================================================
# STRATEGY 1: Enhanced Keyword Matching
# ============================================================================

def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def fuzzy_match(word1, word2, max_distance=2):
    """Check if two words are similar using fuzzy matching"""
    # Exact match
    if word1 == word2:
        return True

    # One contains the other
    if word1 in word2 or word2 in word1:
        return True

    # Fuzzy match (Levenshtein distance)
    if len(word1) >= 4 and len(word2) >= 4:
        distance = levenshtein_distance(word1.lower(), word2.lower())
        return distance <= max_distance

    return False


def get_agent_keywords(agent_name, agent_description=""):
    """Extract keywords from agent name and description"""
    keywords = set()

    # Extract from name
    name_parts = re.split(r'[-_]', agent_name.lower())
    keywords.update(p for p in name_parts if len(p) > 2)

    # Extract from description (if available)
    if agent_description:
        # Extract meaningful words from description
        desc_words = re.findall(r'\b\w{4,}\b', agent_description.lower())
        # Filter common words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your',
                      'their', 'what', 'when', 'which', 'them', 'than', 'then', 'into'}
        keywords.update(w for w in desc_words if w not in stop_words)

    return keywords


SPIDER_KEYWORDS = {
    'patreon': ['content', 'monetization', 'creator', 'revenue', 'subscription', 'writer', 'income', 'digital', 'product'],
    'substack': ['content', 'monetization', 'creator', 'newsletter', 'writer', 'revenue', 'subscription', 'income'],
    'kaggle': ['data', 'ml', 'machine', 'learning', 'analytics', 'research', 'python', 'science', 'analysis'],
    'github': ['dev', 'code', 'software', 'programming', 'api', 'technical', 'development', 'engineer'],
    'huggingface': ['ai', 'ml', 'machine', 'learning', 'nlp', 'research', 'python', 'model', 'neural'],
    'stackoverflow': ['dev', 'code', 'technical', 'programming', 'software', 'api', 'development', 'engineer'],
    'innovation': ['research', 'trend', 'analysis', 'market', 'startup', 'business', 'innovation', 'tech'],
    'combat_sports': ['betting', 'sports', 'combat', 'ufc', 'mma', 'value', 'odds', 'fight', 'boxing'],
    'horse_racing': ['betting', 'sports', 'racing', 'horse', 'value', 'arbitrage', 'odds', 'track'],
    'guru': ['freelance', 'career', 'job', 'income', 'work', 'application', 'employment', 'gig'],
    'gumroad': ['product', 'digital', 'monetization', 'creator', 'revenue', 'sales', 'income', 'content'],
    'remoteok': ['job', 'career', 'remote', 'work', 'freelance', 'income', 'employment', 'tech'],
    'medium': ['content', 'writer', 'creator', 'monetization', 'seo', 'blog', 'article', 'writing'],
    'coingecko': ['crypto', 'blockchain', 'finance', 'trading', 'market', 'investment', 'bitcoin', 'ethereum'],
    'etherscan': ['crypto', 'blockchain', 'ethereum', 'smart', 'contract', 'defi', 'finance'],
    'seekingalpha': ['stock', 'finance', 'trading', 'investment', 'market', 'equity', 'portfolio'],
}


def enhanced_keyword_match(spider_name, agent_name, agent_description):
    """Enhanced keyword matching with partial and fuzzy matching"""
    # Get keywords
    spider_kw = []
    for key, keywords in SPIDER_KEYWORDS.items():
        if key in spider_name.lower():
            spider_kw.extend(keywords)

    if not spider_kw:
        spider_kw = re.split(r'[-_]', spider_name.lower())

    agent_kw = get_agent_keywords(agent_name, agent_description)

    # Match strategies
    for spider_keyword in spider_kw:
        for agent_keyword in agent_kw:
            # Exact match
            if spider_keyword == agent_keyword:
                return True

            # Partial word matching (either contains the other)
            if len(spider_keyword) >= 4 and len(agent_keyword) >= 4:
                if spider_keyword in agent_keyword or agent_keyword in spider_keyword:
                    return True

            # Fuzzy matching
            if fuzzy_match(spider_keyword, agent_keyword):
                return True

    return False


# ============================================================================
# STRATEGY 2: Description-Based Routing
# ============================================================================

def description_based_match(spider_name, agent_description):
    """Match based on agent description content"""
    if not agent_description:
        return False

    agent_desc_lower = agent_description.lower()
    spider_name_lower = spider_name.lower()

    # Direct spider name mention in description
    if spider_name_lower in agent_desc_lower:
        return True

    # Check if spider keywords are in description
    spider_kw = SPIDER_KEYWORDS.get(spider_name_lower, [])
    if not spider_kw:
        spider_kw = re.split(r'[-_]', spider_name_lower)

    # Count keyword matches
    matches = sum(1 for kw in spider_kw if kw in agent_desc_lower)

    # Require at least 2 keyword matches or 1 strong match
    if matches >= 2:
        return True

    # Strong single keyword matches
    strong_keywords = ['betting', 'sports', 'finance', 'crypto', 'trading', 'content',
                       'monetization', 'machine-learning', 'analytics', 'development']

    for kw in spider_kw:
        if kw in strong_keywords and kw in agent_desc_lower:
            return True

    return False


# ============================================================================
# STRATEGY 3: Fallback Category Routing
# ============================================================================

AGENT_CATEGORIES = {
    'development': ['dev', 'code', 'software', 'programming', 'api', 'backend', 'frontend',
                    'engineer', 'technical', 'python', 'javascript', 'react', 'django'],
    'content': ['content', 'writer', 'creator', 'blog', 'article', 'writing', 'copywriting',
                'seo', 'social', 'media'],
    'sports': ['sports', 'betting', 'odds', 'arbitrage', 'value', 'racing', 'combat', 'fight',
               'ufc', 'mma', 'horse', 'football', 'basketball'],
    'finance': ['finance', 'trading', 'investment', 'crypto', 'blockchain', 'stock', 'market',
                'portfolio', 'revenue', 'monetization'],
    'analytics': ['data', 'analytics', 'science', 'analysis', 'research', 'ml', 'machine',
                  'learning', 'ai', 'neural', 'model'],
    'career': ['job', 'career', 'freelance', 'work', 'employment', 'income', 'application',
               'resume', 'gig'],
    'infrastructure': ['system', 'platform', 'infrastructure', 'optimization', 'performance',
                       'cache', 'database', 'redis', 'celery', 'orchestration'],
    'general': ['agent', 'assistant', 'orchestrator', 'coordinator', 'integration', 'unification'],
}


SPIDER_CATEGORIES = {
    'patreon': ['content', 'finance'],
    'substack': ['content', 'finance'],
    'kaggle': ['analytics', 'development'],
    'github': ['development'],
    'huggingface': ['analytics', 'development'],
    'stackoverflow': ['development'],
    'innovation': ['analytics', 'finance'],
    'combat_sports': ['sports'],
    'horse_racing': ['sports'],
    'guru': ['career'],
    'gumroad': ['content', 'finance'],
    'remoteok': ['career'],
    'medium': ['content'],
    'coingecko': ['finance'],
    'etherscan': ['finance'],
    'seekingalpha': ['finance'],
}


def get_agent_category(agent_name, agent_description):
    """Determine agent's category based on keywords"""
    agent_kw = get_agent_keywords(agent_name, agent_description)

    category_scores = defaultdict(int)

    for category, keywords in AGENT_CATEGORIES.items():
        for kw in keywords:
            if kw in agent_kw:
                category_scores[category] += 1

    if category_scores:
        # Return category with highest score
        return max(category_scores.items(), key=lambda x: x[1])[0]

    return 'general'


def category_based_match(spider_name, agent_category):
    """Match based on broad category"""
    spider_categories = []

    for key, categories in SPIDER_CATEGORIES.items():
        if key in spider_name.lower():
            spider_categories.extend(categories)

    return agent_category in spider_categories


# ============================================================================
# COMBINED ROUTING LOGIC
# ============================================================================

def find_matching_agents(spider_name, all_agents):
    """Find all agents that match this spider using all strategies"""
    matched_agents = []

    for agent in all_agents:
        agent_description = agent.description or ""
        agent_category = get_agent_category(agent.name, agent_description)

        # Strategy 1: Enhanced keyword matching
        if enhanced_keyword_match(spider_name, agent.name, agent_description):
            matched_agents.append(agent.name)
            continue

        # Strategy 2: Description-based matching
        if description_based_match(spider_name, agent_description):
            matched_agents.append(agent.name)
            continue

        # Strategy 3: Category-based fallback
        if category_based_match(spider_name, agent_category):
            matched_agents.append(agent.name)
            continue

    return matched_agents


# ============================================================================
# ANALYSIS AND EXECUTION
# ============================================================================

def analyze_routing_improvements():
    """Analyze potential improvements from enhanced routing"""
    all_agents = list(UnifiedAgentTemplate.objects.filter(is_active=True))
    spider_names = SpiderData.objects.values_list('spider_name', flat=True).distinct()

    routing_table = {}
    all_matched_agents = set()

    for spider_name in spider_names:
        matched = find_matching_agents(spider_name, all_agents)
        routing_table[spider_name] = matched
        all_matched_agents.update(matched)

    # Get current agents with data using SQL aggregation (OPTIMIZED)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT unnest(routed_to_agents) as agent_name
            FROM persistence_spiderdata
            WHERE routed_to_agents IS NOT NULL
              AND routed_to_agents != '{}'
        """)
        current_agents_with_data = {row[0] for row in cursor.fetchall()}

    # Calculate improvements
    new_agents = all_matched_agents - current_agents_with_data

    return routing_table, len(current_agents_with_data), len(all_matched_agents), sorted(new_agents)


def apply_enhanced_routing(dry_run=True):
    """Apply enhanced routing to all spider data"""
    all_agents = list(UnifiedAgentTemplate.objects.filter(is_active=True))

    spider_counts = SpiderData.objects.values('spider_name').annotate(
        count=Count('id')
    ).order_by('-count')

    total_updated = 0
    routing_changes = []

    for sp in spider_counts:
        spider_name = sp['spider_name']
        count = sp['count']

        # Get matched agents using enhanced routing
        matched_agents = find_matching_agents(spider_name, all_agents)

        if not matched_agents:
            continue

        # Get existing routing
        sample = SpiderData.objects.filter(spider_name=spider_name).first()
        existing_agents = sample.routed_to_agents if sample else []

        # Combine existing + new agents (remove duplicates)
        combined_agents = list(set(existing_agents + matched_agents))

        routing_changes.append({
            'spider': spider_name,
            'count': count,
            'old_agents': len(existing_agents),
            'new_agents': len(combined_agents),
            'added': len(combined_agents) - len(existing_agents),
        })

        if not dry_run:
            # Update all entries for this spider
            SpiderData.objects.filter(spider_name=spider_name).update(
                routed_to_agents=combined_agents
            )
            total_updated += count

    return routing_changes, total_updated


def main():
    print("=" * 80)
    print("ENHANCED INTELLIGENT ROUTING - Reach 80% Target (142+ Agents)")
    print("=" * 80)

    # Analyze potential improvements
    print("\n📊 Analyzing enhanced routing strategies...")
    routing_table, current_count, potential_count, new_agents = analyze_routing_improvements()

    print(f"\n✅ Current State:")
    print(f"   Agents with data: {current_count} / 177 ({current_count/177*100:.1f}%)")

    print(f"\n🚀 After Enhanced Routing:")
    print(f"   Agents with data: {potential_count} / 177 ({potential_count/177*100:.1f}%)")
    print(f"   New agents unlocked: {len(new_agents)}")
    print(f"   Target: 142 agents (80%)")

    if potential_count >= 142:
        print(f"\n🎉 SUCCESS! Will exceed 80% target!")
    else:
        print(f"\n⚠️  Still {142 - potential_count} agents short of 80% target")

    # Show sample of new agents
    if new_agents:
        print(f"\n📋 Sample of newly matched agents (first 20):")
        for agent_name in new_agents[:20]:
            print(f"   - {agent_name}")

        if len(new_agents) > 20:
            print(f"   ... and {len(new_agents) - 20} more agents")

    # Show routing improvements
    print(f"\n\n📈 Applying Enhanced Routing (DRY RUN)...")
    changes, total = apply_enhanced_routing(dry_run=True)

    # Show changes with significant improvements
    significant_changes = [c for c in changes if c['added'] > 0]

    print(f"\n   Will update {len(significant_changes)} spider types with new agents:")
    for change in significant_changes[:15]:
        print(f"      {change['spider']:30} ({change['count']:>6,} entries): "
              f"{change['old_agents']:>2} → {change['new_agents']:>2} agents "
              f"(+{change['added']})")

    if len(significant_changes) > 15:
        print(f"      ... and {len(significant_changes) - 15} more spider types")

    # Ask for confirmation
    print("\n" + "=" * 80)
    response = input("\nApply enhanced routing? (yes/no): ").strip().lower()

    if response == 'yes':
        print("\n🚀 Applying enhanced routing...")
        changes, total_updated = apply_enhanced_routing(dry_run=False)

        print(f"\n✅ COMPLETE!")
        print(f"   Updated: {total_updated:,} spider data entries")
        print(f"   Modified: {len([c for c in changes if c['added'] > 0])} spider types")

        # Verify final state
        total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        agents_with_data = 0
        for agent in UnifiedAgentTemplate.objects.filter(is_active=True):
            if SpiderData.objects.filter(routed_to_agents__contains=[agent.name]).exists():
                agents_with_data += 1

        print(f"\n📊 Final State:")
        print(f"   Agents with data: {agents_with_data} / {total_agents} ({agents_with_data/total_agents*100:.1f}%)")
        print(f"   Target: 142 / 177 (80.0%)")

        if agents_with_data >= 142:
            print(f"\n🎉 SUCCESS! Reached 80%+ target!")
            print(f"   Improvement: {current_count} → {agents_with_data} (+{agents_with_data - current_count} agents)")
        else:
            print(f"\n📈 Progress made: {current_count} → {agents_with_data} (+{agents_with_data - current_count} agents)")
            print(f"   Still need: {142 - agents_with_data} more agents to reach 80% target")

    else:
        print("\n❌ Cancelled - no changes made")


if __name__ == '__main__':
    main()

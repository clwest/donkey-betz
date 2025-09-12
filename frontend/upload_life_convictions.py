#!/usr/bin/env python3
"""
Upload Life Convictions Knowledge to the Personal Knowledge Base
Transform the platform from sports betting to life decisions and unshakeable convictions
"""
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "993f8273f70877e23b5c7d2f92ed30562a089fe3"

# Life Convictions Knowledge Documents
LIFE_CONVICTIONS_KNOWLEDGE = [
    {
        "title": "The Philosophy of Donkey Bets: Unshakeable Life Convictions",
        "description": "Understanding what makes a conviction so strong that moving mountains is easier than changing your mind",
        "raw_content": """# The Philosophy of Donkey Bets: Unshakeable Life Convictions

## What is a Donkey Bet?

A "donkey bet" is not about sports, gambling, or financial speculation. It's something far more profound - a life conviction so deeply held that you would stake everything on it. These are the beliefs and decisions that define who you are at your core.

### Characteristics of a True Donkey Bet:

1. **Immovable Certainty**: You feel so strongly about it that moving a mountain would be easier than changing your mind
2. **Life-Defining**: These convictions shape your identity and life path
3. **Value-Driven**: Rooted in your deepest values, not external pressures
4. **Time-Tested**: They withstand doubt, criticism, and adversity
5. **Action-Oriented**: They drive real decisions and life changes

### Examples of Life Donkey Bets:

- **Career Pivots**: "I know I'm meant to be an artist, not an accountant"
- **Relationship Decisions**: "This person is my life partner, without question"
- **Life Philosophy**: "Kindness matters more than success"
- **Parenting Choices**: "My children's happiness is worth any sacrifice"
- **Personal Growth**: "I will overcome this addiction"
- **Purpose**: "I was born to teach and inspire others"

### The Power of Unshakeable Conviction

When you have a true donkey bet - a conviction that runs bone-deep - it becomes:
- Your North Star in decision-making
- Your strength in times of doubt
- Your identity when the world questions you
- Your legacy when you're gone

These aren't whims or preferences. They're the bedrock beliefs that you'd defend against any argument, any pressure, any temptation to compromise.""",
        "document_type": "betting_analysis",
        "category": "life-convictions",
        "tags": ["donkey-bet", "conviction", "life-philosophy", "decision-making", "values"],
        "is_public": True,
        "source": "upload"
    },
    {
        "title": "Identifying Your Core Life Convictions",
        "description": "A framework for discovering what you truly believe with unshakeable certainty",
        "raw_content": """# Identifying Your Core Life Convictions

## The Journey to Unshakeable Clarity

Not every strong opinion is a donkey bet. True life convictions emerge from deep self-knowledge and experience. Here's how to identify yours:

### The Five Tests of a True Conviction

1. **The Pressure Test**
   - Would you hold this belief if everyone you loved disagreed?
   - Would you maintain it if it cost you professionally?
   - Would you keep it if society mocked you for it?

2. **The Time Test**
   - Has this belief strengthened over years, not weakened?
   - Does it feel more true with each life experience?
   - Can you trace its roots deep into your past?

3. **The Action Test**
   - Have you made significant life decisions based on this?
   - Are you willing to sacrifice comfort for it?
   - Does it drive your daily choices?

4. **The Identity Test**
   - Is this belief part of who you are, not just what you think?
   - Would abandoning it feel like losing yourself?
   - Do others know you by this conviction?

5. **The Legacy Test**
   - Would you want to be remembered for this?
   - Would you teach this to your children?
   - Does it matter beyond your lifetime?

### Common Categories of Life Convictions

**Values-Based Convictions**
- "Integrity is non-negotiable"
- "Family comes first, always"
- "Truth matters more than comfort"

**Purpose-Based Convictions**
- "I'm here to create beauty"
- "My mission is to reduce suffering"
- "I exist to push boundaries"

**Relationship Convictions**
- "Love is a choice, not just a feeling"
- "Loyalty is earned through consistency"
- "People deserve second chances"

**Growth Convictions**
- "Every failure teaches something vital"
- "Comfort is the enemy of growth"
- "We're capable of more than we imagine"

### The Conviction Mapping Exercise

1. List your strongest beliefs
2. Apply the five tests to each
3. Identify which are truly unshakeable
4. Articulate why they're non-negotiable
5. Document how they guide your life""",
        "document_type": "betting_analysis",
        "category": "life-convictions",
        "tags": ["self-discovery", "conviction-testing", "values", "identity", "decision-framework"],
        "is_public": True,
        "source": "upload"
    },
    {
        "title": "Living by Your Convictions: From Belief to Action",
        "description": "How to align your daily life with your unshakeable convictions",
        "raw_content": """# Living by Your Convictions: From Belief to Action

## The Courage to Live Your Truth

Having unshakeable convictions is one thing. Living by them is another. This is where donkey bets transform from philosophy to practice.

### The Alignment Process

**Step 1: Audit Your Current Life**
- Where are you compromising your convictions?
- What fears keep you from full alignment?
- Which areas of life match your beliefs?

**Step 2: Identify the Gaps**
- Career misalignment with values
- Relationships that contradict your beliefs
- Daily habits that betray your convictions
- Time spent on things that don't matter to you

**Step 3: Create an Action Plan**
- Small steps toward alignment
- Major pivots that may be necessary
- Support systems you'll need
- Timeline for transformation

### Practical Strategies for Conviction-Based Living

**Daily Practices**
1. Morning intention setting based on convictions
2. Evening review of alignment
3. Decision-making through conviction lens
4. Regular conviction check-ins

**Relationship Management**
- Communicate your convictions clearly
- Set boundaries that protect your beliefs
- Seek relationships that honor your truth
- Release relationships that require compromise

**Career Alignment**
- Evaluate current role against convictions
- Identify conviction-aligned opportunities
- Plan transitions if necessary
- Build skills that support your beliefs

### Handling Resistance and Doubt

**External Resistance**
- Family pressure to conform
- Social judgment and isolation
- Professional consequences
- Financial challenges

**Internal Resistance**
- Fear of being wrong
- Comfort zone attachment
- Imposter syndrome
- Temporary wavering

**Staying Strong**
- Remember why this matters to you
- Find your conviction community
- Document your journey
- Celebrate alignment victories
- Accept that not everyone will understand

### The Reward of Authentic Living

When you fully align with your donkey bets:
- Decisions become clearer
- Anxiety decreases
- Purpose emerges
- Integrity strengthens
- Life becomes meaningful
- Regrets diminish
- Legacy forms naturally""",
        "document_type": "betting_analysis",
        "category": "life-convictions",
        "tags": ["authentic-living", "alignment", "action-plan", "courage", "life-design"],
        "is_public": True,
        "source": "upload"
    },
    {
        "title": "The AI-Assisted Life: Using 100+ Agents for Life Decisions",
        "description": "How to leverage AI agents to explore, test, and strengthen your life convictions",
        "raw_content": """# The AI-Assisted Life: Using 100+ Agents for Life Decisions

## Beyond Sports Betting: AI for Life's Biggest Decisions

While others use AI for trivial tasks, you can leverage 100+ specialized agents to navigate life's most important decisions and test your deepest convictions.

### Life Decision Agents at Your Service

**Values Exploration Agents**
- Value Hierarchy Analyzer: Map your true priorities
- Conflict Resolution Agent: When values clash
- Cultural Values Translator: Understanding different perspectives
- Historical Values Researcher: How beliefs evolved

**Decision Analysis Agents**
- Pro/Con Deep Analyzer: Beyond surface-level lists
- Scenario Simulator: Play out different paths
- Regret Minimization Calculator: Long-term perspective
- Opportunity Cost Evaluator: What you're really choosing

**Conviction Testing Agents**
- Devil's Advocate AI: Challenge your beliefs
- Perspective Multiplier: See from 100 viewpoints
- Conviction Strength Tester: Measure certainty
- Bias Detection Agent: Spot blind spots

**Life Planning Agents**
- Path Optimizer: Align actions with convictions
- Milestone Mapper: Break down big changes
- Resource Allocator: Time, money, energy alignment
- Risk Assessment Agent: Understand true stakes

### Practical AI Applications for Life Convictions

**Career Transition Example**
1. Values Alignment Agent analyzes current vs. desired
2. Financial Planning Agent models transition scenarios
3. Skill Gap Agent identifies learning needs
4. Network Builder Agent suggests connections
5. Timeline Optimizer creates realistic plan

**Relationship Decision Example**
1. Compatibility Analyzer examines core values
2. Communication Pattern Agent identifies dynamics
3. Future Scenario Agent projects long-term outcomes
4. Conflict Prediction Agent anticipates challenges
5. Growth Potential Agent assesses mutual development

**Life Philosophy Development**
1. Philosophy Research Agent explores frameworks
2. Contradiction Detector finds inconsistencies
3. Integration Agent synthesizes beliefs
4. Practice Designer creates daily applications
5. Evolution Tracker monitors belief changes

### The Synergy of Human Conviction and AI Intelligence

**What AI Brings**
- Unlimited perspectives
- Emotional neutrality
- Data processing power
- Pattern recognition
- Scenario modeling

**What You Bring**
- Deep personal knowledge
- Emotional intelligence
- Value judgments
- Life experience
- Final decision authority

### Building Your Personal AI Council

Create your advisory board of agents:
1. Select agents aligned with current challenges
2. Regular consultation on major decisions
3. Use agents to stress-test convictions
4. Let AI surface blind spots
5. Maintain human authority over final choices

Remember: AI doesn't make your decisions. It makes you better at making them.""",
        "document_type": "betting_analysis",
        "category": "life-convictions",
        "tags": ["ai-agents", "decision-support", "life-planning", "conviction-testing", "human-ai-collaboration"],
        "is_public": True,
        "source": "upload"
    }
]

def upload_documents():
    """Upload all life convictions knowledge documents"""
    
    headers = {
        "Authorization": f"Token {AUTH_TOKEN}"
    }
    
    success_count = 0
    
    for doc in LIFE_CONVICTIONS_KNOWLEDGE:
        print(f"\n📚 Uploading: {doc['title']}")
        
        # Create multipart form data
        files = {
            'title': (None, doc['title']),
            'description': (None, doc['description']),
            'content': (None, doc['raw_content']),
            'document_type': (None, doc['document_type']),
            'category': (None, doc['category']),
            'tags': (None, json.dumps(doc['tags'])),
            'is_public': (None, str(doc['is_public'])),
            'source': (None, doc['source'])
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/content/documents/",
                headers=headers,
                files=files
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Successfully uploaded: {doc['title']}")
                success_count += 1
            else:
                print(f"❌ Failed to upload: {doc['title']}")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error uploading {doc['title']}: {str(e)}")
    
    print(f"\n🎯 Upload Summary: {success_count}/{len(LIFE_CONVICTIONS_KNOWLEDGE)} documents uploaded successfully")
    
    # List knowledge bases
    print("\n📖 Available Knowledge Bases:")
    try:
        kb_response = requests.get(
            f"{API_BASE_URL}/api/v1/content/knowledge-bases/",
            headers=headers
        )
        if kb_response.ok:
            kbs = kb_response.json()
            for kb in kbs.get('results', []):
                print(f"   - {kb['name']}: {kb['document_count']} documents")
    except Exception as e:
        print(f"   Error fetching knowledge bases: {e}")

if __name__ == "__main__":
    print("🚀 Starting Life Convictions Knowledge Upload...")
    print("📝 Transforming platform from sports betting to life decisions...")
    upload_documents()
    print("\n✨ Done! Your Life Convictions knowledge base is ready!")
    print("🧭 This platform is now about unshakeable life convictions, not sports betting")
    print("💪 Visit http://localhost:3001/knowledge to explore your convictions")
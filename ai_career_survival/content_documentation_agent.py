"""
AI Project Documentation Agent
==============================

Automatically documents AI projects as they're being built,
creating sellable technical documentation and content.
"""

import os
import json
import redis
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProjectDocumentationAgent:
    """
    Monitors AI project development and creates documentation:
    - Technical specifications
    - API documentation
    - User guides
    - Case studies
    - Blog posts about the implementation
    - Tutorial content
    """

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.redis_learning = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.documented_projects = []

    def monitor_and_document(self):
        """
        Monitor AI project progress and create documentation
        """
        logger.info("📚 Starting AI Project Documentation Agent")

        while True:
            try:
                # Check for project updates
                project_updates = self.get_project_updates()

                for update in project_updates:
                    self.document_project_progress(update)

                # Check for completed features
                completed_features = self.get_completed_features()

                for feature in completed_features:
                    self.create_feature_documentation(feature)

                # Monitor agent collaborations
                collaborations = self.get_agent_collaborations()

                if collaborations:
                    self.document_agent_interactions(collaborations)

                import time
                time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                logger.info("Stopping documentation agent...")
                break
            except Exception as e:
                logger.error(f"Documentation error: {e}")
                import time
                time.sleep(5)

    def get_project_updates(self) -> List[Dict]:
        """
        Get recent project updates from Redis
        """
        updates = []

        # Check for freelance projects
        project_keys = self.redis_client.keys('freelance:project:*')
        for key in project_keys[-5:]:  # Last 5 projects
            if not self.redis_client.exists(f"{key}:documented"):
                project_data = self.redis_client.hgetall(key)
                if project_data:
                    updates.append({
                        'type': 'freelance_project',
                        'key': key,
                        'data': project_data
                    })

        # Check for agent tasks
        task_keys = self.redis_client.keys('agent:task:*')
        for key in task_keys[-5:]:
            if not self.redis_client.exists(f"{key}:documented"):
                task_data = self.redis_client.get(key)
                if task_data:
                    updates.append({
                        'type': 'agent_task',
                        'key': key,
                        'data': task_data
                    })

        return updates

    def get_completed_features(self) -> List[Dict]:
        """
        Get recently completed features
        """
        features = []

        # Check collaboration completions
        completed_keys = self.redis_client.keys('collaboration:completed:*')
        for key in completed_keys[-3:]:
            if not self.redis_client.exists(f"{key}:documented"):
                feature_data = self.redis_client.get(key)
                if feature_data:
                    features.append({
                        'key': key,
                        'data': feature_data
                    })

        return features

    def get_agent_collaborations(self) -> List[Dict]:
        """
        Get recent agent collaborations
        """
        collaborations = []

        # Check collaboration events
        event_keys = self.redis_client.keys('collaboration:events:*')
        for key in event_keys[-5:]:
            events = self.redis_client.lrange(key, 0, -1)
            if events:
                collaborations.append({
                    'key': key,
                    'events': events
                })

        return collaborations

    def document_project_progress(self, update: Dict):
        """
        Create documentation for project progress
        """
        try:
            logger.info(f"📝 Documenting project: {update['key']}")

            # Generate technical documentation
            prompt = f"""
            Create technical documentation for this AI project update:

            Type: {update['type']}
            Data: {json.dumps(update['data'], indent=2)}

            Create:
            1. Technical Overview (what was implemented)
            2. Architecture Details (how it works)
            3. API Endpoints (if applicable)
            4. Configuration Requirements
            5. Usage Examples
            6. Testing Approach

            Format as professional technical documentation.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a technical documentation expert for AI projects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )

            documentation = response.choices[0].message.content

            # Save documentation
            doc_entry = {
                'type': 'project_documentation',
                'project_key': update['key'],
                'documentation': documentation,
                'created_at': datetime.now().isoformat(),
                'value_estimate': 75,  # Technical docs are valuable
                'format': 'markdown'
            }

            self.save_documentation(doc_entry)

            # Mark as documented
            self.redis_client.set(f"{update['key']}:documented", "1", ex=86400)

            logger.info(f"✅ Created documentation for: {update['key']}")

        except Exception as e:
            logger.error(f"Error documenting project: {e}")

    def create_feature_documentation(self, feature: Dict):
        """
        Create documentation for completed features
        """
        try:
            logger.info(f"📖 Documenting completed feature: {feature['key']}")

            # Generate feature guide
            prompt = f"""
            Create a user guide for this completed AI feature:

            Feature Data: {feature['data']}

            Create:
            1. Feature Overview (what it does)
            2. How to Use It (step-by-step guide)
            3. Best Practices
            4. Common Use Cases
            5. Troubleshooting Tips

            Write in a clear, user-friendly style.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are creating user guides for AI features."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200
            )

            guide = response.choices[0].message.content

            # Save feature guide
            guide_entry = {
                'type': 'feature_guide',
                'feature_key': feature['key'],
                'guide': guide,
                'created_at': datetime.now().isoformat(),
                'value_estimate': 50,
                'format': 'markdown'
            }

            self.save_documentation(guide_entry)

            # Mark as documented
            self.redis_client.set(f"{feature['key']}:documented", "1", ex=86400)

            logger.info(f"✅ Created feature guide for: {feature['key']}")

        except Exception as e:
            logger.error(f"Error documenting feature: {e}")

    def document_agent_interactions(self, collaborations: List[Dict]):
        """
        Create case studies from agent collaborations
        """
        try:
            if not collaborations:
                return

            logger.info(f"💡 Creating case study from {len(collaborations)} collaborations")

            # Aggregate collaboration data
            all_events = []
            for collab in collaborations:
                all_events.extend(collab['events'])

            # Generate case study
            prompt = f"""
            Create a case study blog post about AI agents working together:

            Collaboration Events: {json.dumps(all_events[:10], indent=2)}

            Create an engaging blog post that includes:
            1. The Challenge (what problem was being solved)
            2. The AI Solution (how agents collaborated)
            3. Implementation Details (technical insights)
            4. Results and Benefits
            5. Lessons Learned
            6. Future Implications

            Write in an engaging, educational style for a technical audience.
            Target 800-1000 words.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are writing case studies about AI agent collaboration."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )

            case_study = response.choices[0].message.content

            # Save case study
            study_entry = {
                'type': 'case_study',
                'title': self.extract_title(case_study),
                'content': case_study,
                'collaborations': len(collaborations),
                'created_at': datetime.now().isoformat(),
                'value_estimate': 150,  # Case studies are very valuable
                'format': 'markdown',
                'ready_to_publish': True
            }

            self.save_documentation(study_entry)

            logger.info(f"✅ Created case study: {study_entry['title']}")

        except Exception as e:
            logger.error(f"Error creating case study: {e}")

    def extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('#'):
                return line.replace('#', '').strip()
        return "AI Agent Collaboration Case Study"

    def save_documentation(self, doc_entry: Dict):
        """
        Save documentation to file and Redis
        """
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"/tmp/ai_doc_{doc_entry['type']}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(doc_entry, f, indent=2)

        # Save reference in Redis
        doc_key = f"documentation:{doc_entry['type']}:{timestamp}"
        self.redis_client.hset(doc_key, mapping={
            'type': doc_entry['type'],
            'filename': filename,
            'value': str(doc_entry['value_estimate']),
            'created_at': doc_entry['created_at']
        })

        # Track in documented projects
        self.documented_projects.append(doc_entry)

        logger.info(f"💾 Saved documentation: {filename}")

    def create_project_summary(self) -> Dict:
        """
        Create a comprehensive project summary
        """
        if not self.documented_projects:
            return None

        try:
            logger.info("📊 Creating comprehensive project summary")

            # Aggregate all documentation
            total_docs = len(self.documented_projects)
            total_value = sum(d.get('value_estimate', 0) for d in self.documented_projects)

            doc_types = {}
            for doc in self.documented_projects:
                doc_type = doc['type']
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

            summary = {
                'title': 'AI Project Documentation Portfolio',
                'total_documents': total_docs,
                'total_value': total_value,
                'document_types': doc_types,
                'created_at': datetime.now().isoformat(),
                'documents': self.documented_projects[-10:]  # Last 10 docs
            }

            # Generate executive summary
            prompt = f"""
            Create an executive summary for this AI documentation portfolio:

            Total Documents: {total_docs}
            Total Value: ${total_value}
            Document Types: {json.dumps(doc_types, indent=2)}

            Write a professional executive summary (200-300 words) that highlights:
            1. The scope of documentation created
            2. Key technical achievements documented
            3. Value proposition for buyers
            4. Use cases for the documentation
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are creating an executive summary for AI documentation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )

            summary['executive_summary'] = response.choices[0].message.content

            # Save summary
            summary_file = f"/tmp/ai_documentation_portfolio_{datetime.now().strftime('%Y%m%d')}.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"✅ Created portfolio summary: {summary_file}")
            logger.info(f"💰 Total Documentation Value: ${total_value}")

            return summary

        except Exception as e:
            logger.error(f"Error creating summary: {e}")
            return None


def start_documentation_agent():
    """
    Start the AI project documentation agent
    """
    agent = AIProjectDocumentationAgent()

    logger.info("="*60)
    logger.info("AI PROJECT DOCUMENTATION AGENT")
    logger.info("="*60)
    logger.info("📚 Monitoring AI projects and creating documentation...")
    logger.info("📝 Will create: Technical docs, user guides, case studies")
    logger.info("💰 All documentation is ready to sell!")
    logger.info("="*60)

    try:
        agent.monitor_and_document()
    except KeyboardInterrupt:
        # Create final summary before exiting
        summary = agent.create_project_summary()
        if summary:
            print(f"\n📊 Final Summary:")
            print(f"   Documents Created: {summary['total_documents']}")
            print(f"   Total Value: ${summary['total_value']}")
            print(f"   Types: {summary['document_types']}")
        print("\n✅ Documentation agent stopped")


if __name__ == "__main__":
    start_documentation_agent()
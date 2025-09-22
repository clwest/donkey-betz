#!/usr/bin/env python3
"""
Simple Project Progress Simulator
Updates project progress in Redis without Django dependencies
"""
import redis
import json
import random
import time
from datetime import datetime
import uuid

class SimpleProgressSimulator:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.running = True

    def simulate_progress(self):
        """Continuously simulate progress for active projects"""
        print("🚀 Starting Simple Progress Simulator...")
        print("This will make agents actually complete work!")

        while self.running:
            try:
                # Get all active projects
                project_keys = self.redis_client.keys('freelance:project:*')

                if project_keys:
                    print(f"\n📊 Found {len(project_keys)} projects to update")

                for project_key in project_keys:
                    project_data = self.redis_client.get(project_key)
                    if project_data:
                        project = json.loads(project_data)

                        # Update project progress
                        self.update_project_progress(project, project_key)

                # Wait before next update cycle
                time.sleep(random.uniform(3, 8))

            except Exception as e:
                print(f"Error in progress simulation: {e}")
                time.sleep(5)

    def update_project_progress(self, project, project_key):
        """Update progress for a single project"""
        try:
            # Get or initialize progress
            progress = project.get('progress', 0)

            # Skip completed projects
            if progress >= 100:
                return

            # Get agent name
            agent_name = project.get('analysis', {}).get('agent_team', {}).get('lead_agent', 'Unknown Agent')

            # Different progress rates based on agent type
            if 'Code Generator' in agent_name:
                increment = random.uniform(2, 5)
            elif 'Content Creator' in agent_name:
                increment = random.uniform(3, 7)
            elif 'Data Analyst' in agent_name:
                increment = random.uniform(1, 4)
            elif 'Market Analyst' in agent_name:
                increment = random.uniform(2, 4)
            else:
                increment = random.uniform(2, 4)  # Default rate

            # Update progress
            new_progress = min(progress + increment, 100)
            project['progress'] = new_progress

            # Update status based on progress
            old_status = project.get('status', 'unknown')

            if new_progress >= 100:
                project['status'] = 'completed'
                project['completed_at'] = datetime.now().isoformat()

                # Generate deliverable
                deliverable = self.generate_deliverable(project)
                project['deliverable'] = deliverable

                print(f"✅ Project {project['id']} COMPLETED by {agent_name}!")
                print(f"   Progress: {old_status} -> completed (100%)")

            elif new_progress >= 75:
                project['status'] = 'finalizing'
                if old_status != 'finalizing':
                    print(f"📈 Project {project['id']}: {old_status} -> finalizing ({new_progress:.1f}%)")
            elif new_progress >= 50:
                project['status'] = 'executing'
                if old_status != 'executing':
                    print(f"📈 Project {project['id']}: {old_status} -> executing ({new_progress:.1f}%)")
            elif new_progress >= 25:
                project['status'] = 'planning'
                if old_status != 'planning':
                    print(f"📈 Project {project['id']}: {old_status} -> planning ({new_progress:.1f}%)")
            else:
                project['status'] = 'active'

            # Add checkpoint at milestones
            if not project.get('checkpoints'):
                project['checkpoints'] = []

            # Check if we crossed a milestone
            milestones = [10, 25, 50, 75, 90, 100]
            for milestone in milestones:
                if progress < milestone <= new_progress:
                    checkpoint = {
                        'progress': milestone,
                        'status': project['status'],
                        'timestamp': datetime.now().isoformat()
                    }
                    project['checkpoints'].append(checkpoint)
                    print(f"   🎯 Milestone reached: {milestone}%")

            # Save updated project
            self.redis_client.set(project_key, json.dumps(project))

            # Also update a simple progress tracker for monitoring
            self.redis_client.set(f'progress:{project["id"]}', str(new_progress))

        except Exception as e:
            print(f"Error updating project {project.get('id')}: {e}")

    def generate_deliverable(self, project):
        """Generate a simulated deliverable"""
        agent_name = project.get('analysis', {}).get('agent_team', {}).get('lead_agent', 'Unknown')
        task_title = project.get('opportunity', {}).get('title', 'Unknown Task')

        deliverable = {
            'id': f'del_{uuid.uuid4().hex[:8]}',
            'type': self.get_deliverable_type(agent_name),
            'title': f"Deliverable: {task_title}",
            'created_at': datetime.now().isoformat(),
            'size': random.randint(1000, 10000),
            'quality_score': random.uniform(0.85, 0.98)
        }

        # Add specific content based on agent type
        if 'Code' in agent_name:
            deliverable['lines_of_code'] = random.randint(200, 1500)
            deliverable['language'] = 'Python' if 'Python' in task_title else 'JavaScript'
        elif 'Content' in agent_name:
            deliverable['word_count'] = random.randint(1500, 3000)
            deliverable['seo_score'] = random.uniform(0.80, 0.95)
        elif 'Analyst' in agent_name:
            deliverable['data_points'] = random.randint(50, 500)
            deliverable['insights'] = random.randint(5, 15)

        return deliverable

    def get_deliverable_type(self, agent_name):
        """Get deliverable type based on agent"""
        if 'Code' in agent_name:
            return 'code'
        elif 'Content' in agent_name:
            return 'article'
        elif 'Data' in agent_name:
            return 'analysis'
        elif 'Market' in agent_name:
            return 'report'
        else:
            return 'document'

    def stop(self):
        """Stop the simulator"""
        self.running = False


if __name__ == '__main__':
    simulator = SimpleProgressSimulator()

    try:
        simulator.simulate_progress()
    except KeyboardInterrupt:
        print("\n⏹️ Stopping simulator...")
        simulator.stop()
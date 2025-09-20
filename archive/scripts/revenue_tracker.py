#!/usr/bin/env python3
"""
Revenue Tracking and Monitoring System
Real-time tracking of proposals, responses, and revenue generation
"""

import os
import sys
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

# Add project root to path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

class ProposalStatus(Enum):
    DRAFTED = "drafted"
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    RESPONDED = "responded"
    INTERVIEW = "interview"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"

class RevenueStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAID = "paid"

@dataclass
class ProposalTracking:
    """Track individual proposal lifecycle"""
    proposal_id: str
    opportunity_type: str
    platform: str
    client_name: str
    project_description: str
    proposal_value: float
    submitted_date: Optional[datetime] = None
    status: ProposalStatus = ProposalStatus.DRAFTED
    response_date: Optional[datetime] = None
    acceptance_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    actual_payment: Optional[float] = None
    notes: List[str] = field(default_factory=list)

@dataclass
class RevenueMetrics:
    """Real-time revenue metrics"""
    total_proposals_created: int = 0
    total_proposals_submitted: int = 0
    total_responses: int = 0
    total_accepted: int = 0
    total_completed: int = 0
    total_revenue_earned: float = 0.0

    # Conversion rates
    response_rate: float = 0.0
    acceptance_rate: float = 0.0
    completion_rate: float = 0.0

    # Daily tracking
    daily_proposals: int = 0
    daily_revenue: float = 0.0
    weekly_revenue: float = 0.0
    monthly_revenue: float = 0.0

    # Platform performance
    platform_stats: Dict[str, Dict] = field(default_factory=dict)

    # Goal tracking
    first_100_progress: float = 0.0
    days_to_first_100: Optional[int] = None

class RevenueTracker:
    """Comprehensive revenue tracking system"""

    def __init__(self, data_dir="/Users/donkeyking/development/unified-donkey-betz/revenue_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.proposals: List[ProposalTracking] = []
        self.metrics = RevenueMetrics()
        self.start_date = datetime.now()

        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load existing tracking data"""
        proposals_file = self.data_dir / "proposals.json"
        metrics_file = self.data_dir / "metrics.json"

        if proposals_file.exists():
            try:
                with open(proposals_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        # Convert date strings back to datetime objects
                        for date_field in ['submitted_date', 'response_date', 'acceptance_date', 'completion_date', 'payment_date']:
                            if item.get(date_field):
                                item[date_field] = datetime.fromisoformat(item[date_field])

                        proposal = ProposalTracking(**item)
                        proposal.status = ProposalStatus(proposal.status)
                        self.proposals.append(proposal)
            except Exception as e:
                print(f"Warning: Could not load proposals data: {e}")

        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics = RevenueMetrics(**data)
            except Exception as e:
                print(f"Warning: Could not load metrics data: {e}")

    def _save_data(self):
        """Save tracking data"""
        proposals_file = self.data_dir / "proposals.json"
        metrics_file = self.data_dir / "metrics.json"

        # Convert proposals to JSON-serializable format
        proposals_data = []
        for proposal in self.proposals:
            data = proposal.__dict__.copy()
            # Convert datetime objects to strings
            for date_field in ['submitted_date', 'response_date', 'acceptance_date', 'completion_date', 'payment_date']:
                if data.get(date_field):
                    data[date_field] = data[date_field].isoformat()
            data['status'] = proposal.status.value
            proposals_data.append(data)

        with open(proposals_file, 'w') as f:
            json.dump(proposals_data, f, indent=2, default=str)

        with open(metrics_file, 'w') as f:
            json.dump(self.metrics.__dict__, f, indent=2, default=str)

    def add_proposal(self, proposal_id: str, opportunity_type: str, platform: str,
                    client_name: str, project_description: str, proposal_value: float):
        """Add a new proposal to tracking"""
        proposal = ProposalTracking(
            proposal_id=proposal_id,
            opportunity_type=opportunity_type,
            platform=platform,
            client_name=client_name,
            project_description=project_description,
            proposal_value=proposal_value
        )

        self.proposals.append(proposal)
        self.metrics.total_proposals_created += 1
        self._update_metrics()
        self._save_data()

        return proposal

    def submit_proposal(self, proposal_id: str, platform: str = None):
        """Mark proposal as submitted"""
        proposal = self._find_proposal(proposal_id)
        if proposal:
            proposal.status = ProposalStatus.SUBMITTED
            proposal.submitted_date = datetime.now()
            if platform:
                proposal.platform = platform

            self.metrics.total_proposals_submitted += 1
            self.metrics.daily_proposals += 1
            self._update_metrics()
            self._save_data()

            print(f"✅ Proposal {proposal_id} submitted to {proposal.platform}")
            return True
        return False

    def record_response(self, proposal_id: str, notes: str = ""):
        """Record client response"""
        proposal = self._find_proposal(proposal_id)
        if proposal:
            proposal.status = ProposalStatus.RESPONDED
            proposal.response_date = datetime.now()
            if notes:
                proposal.notes.append(f"Response: {notes}")

            self.metrics.total_responses += 1
            self._update_metrics()
            self._save_data()

            print(f"📞 Response received for {proposal_id}")
            return True
        return False

    def accept_proposal(self, proposal_id: str, actual_value: float = None, notes: str = ""):
        """Mark proposal as accepted"""
        proposal = self._find_proposal(proposal_id)
        if proposal:
            proposal.status = ProposalStatus.ACCEPTED
            proposal.acceptance_date = datetime.now()
            if actual_value:
                proposal.actual_payment = actual_value
            if notes:
                proposal.notes.append(f"Accepted: {notes}")

            self.metrics.total_accepted += 1
            self._update_metrics()
            self._save_data()

            print(f"🎉 Proposal {proposal_id} ACCEPTED! Value: ${actual_value or proposal.proposal_value}")
            return True
        return False

    def complete_project(self, proposal_id: str, payment_received: float = None):
        """Mark project as completed and payment received"""
        proposal = self._find_proposal(proposal_id)
        if proposal:
            proposal.status = ProposalStatus.COMPLETED
            proposal.completion_date = datetime.now()
            proposal.payment_date = datetime.now()

            payment = payment_received or proposal.actual_payment or proposal.proposal_value
            proposal.actual_payment = payment

            self.metrics.total_completed += 1
            self.metrics.total_revenue_earned += payment
            self.metrics.daily_revenue += payment

            # Check first $100 milestone
            if self.metrics.total_revenue_earned >= 100 and not self.metrics.days_to_first_100:
                days_elapsed = (datetime.now() - self.start_date).days
                self.metrics.days_to_first_100 = days_elapsed

            self.metrics.first_100_progress = min(self.metrics.total_revenue_earned / 100, 1.0)

            self._update_metrics()
            self._save_data()

            print(f"💰 Project {proposal_id} COMPLETED! Payment: ${payment}")
            print(f"💸 Total revenue: ${self.metrics.total_revenue_earned}")

            if self.metrics.total_revenue_earned >= 100:
                print(f"🎯 MILESTONE: First $100 achieved in {self.metrics.days_to_first_100} days!")

            return True
        return False

    def _find_proposal(self, proposal_id: str) -> Optional[ProposalTracking]:
        """Find proposal by ID"""
        for proposal in self.proposals:
            if proposal.proposal_id == proposal_id:
                return proposal
        return None

    def _update_metrics(self):
        """Update calculated metrics"""
        if self.metrics.total_proposals_submitted > 0:
            self.metrics.response_rate = self.metrics.total_responses / self.metrics.total_proposals_submitted

        if self.metrics.total_responses > 0:
            self.metrics.acceptance_rate = self.metrics.total_accepted / self.metrics.total_responses

        if self.metrics.total_accepted > 0:
            self.metrics.completion_rate = self.metrics.total_completed / self.metrics.total_accepted

        # Update platform stats
        self.metrics.platform_stats = {}
        for proposal in self.proposals:
            platform = proposal.platform
            if platform not in self.metrics.platform_stats:
                self.metrics.platform_stats[platform] = {
                    'submitted': 0, 'responses': 0, 'accepted': 0, 'revenue': 0.0
                }

            if proposal.status in [ProposalStatus.SUBMITTED, ProposalStatus.VIEWED,
                                 ProposalStatus.RESPONDED, ProposalStatus.ACCEPTED,
                                 ProposalStatus.COMPLETED]:
                self.metrics.platform_stats[platform]['submitted'] += 1

            if proposal.status in [ProposalStatus.RESPONDED, ProposalStatus.ACCEPTED,
                                 ProposalStatus.COMPLETED]:
                self.metrics.platform_stats[platform]['responses'] += 1

            if proposal.status in [ProposalStatus.ACCEPTED, ProposalStatus.COMPLETED]:
                self.metrics.platform_stats[platform]['accepted'] += 1

            if proposal.status == ProposalStatus.COMPLETED and proposal.actual_payment:
                self.metrics.platform_stats[platform]['revenue'] += proposal.actual_payment

    def get_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive revenue dashboard"""
        self._update_metrics()

        # Calculate time-based metrics
        days_active = max((datetime.now() - self.start_date).days, 1)
        weekly_revenue = self.metrics.total_revenue_earned / (days_active / 7) if days_active >= 7 else 0
        monthly_revenue = self.metrics.total_revenue_earned / (days_active / 30) if days_active >= 30 else 0

        return {
            "overview": {
                "total_revenue": self.metrics.total_revenue_earned,
                "first_100_progress": f"{self.metrics.first_100_progress * 100:.1f}%",
                "days_to_first_100": self.metrics.days_to_first_100,
                "days_active": days_active
            },
            "proposals": {
                "created": self.metrics.total_proposals_created,
                "submitted": self.metrics.total_proposals_submitted,
                "responses": self.metrics.total_responses,
                "accepted": self.metrics.total_accepted,
                "completed": self.metrics.total_completed
            },
            "conversion_rates": {
                "response_rate": f"{self.metrics.response_rate * 100:.1f}%",
                "acceptance_rate": f"{self.metrics.acceptance_rate * 100:.1f}%",
                "completion_rate": f"{self.metrics.completion_rate * 100:.1f}%"
            },
            "revenue_projections": {
                "daily_average": self.metrics.total_revenue_earned / days_active,
                "weekly_projection": weekly_revenue,
                "monthly_projection": monthly_revenue,
                "path_to_first_100": f"{100 - self.metrics.total_revenue_earned:.0f} remaining"
            },
            "platform_performance": self.metrics.platform_stats,
            "recent_activity": self._get_recent_activity()
        }

    def _get_recent_activity(self, days: int = 7) -> List[Dict]:
        """Get recent proposal activity"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []

        for proposal in self.proposals:
            if proposal.submitted_date and proposal.submitted_date >= cutoff:
                recent.append({
                    "id": proposal.proposal_id,
                    "type": proposal.opportunity_type,
                    "platform": proposal.platform,
                    "status": proposal.status.value,
                    "value": proposal.proposal_value,
                    "date": proposal.submitted_date.strftime("%Y-%m-%d")
                })

        return sorted(recent, key=lambda x: x["date"], reverse=True)

    def generate_report(self) -> str:
        """Generate comprehensive revenue report"""
        dashboard = self.get_dashboard()

        report = f"""
🚀 REVENUE ACTIVATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================

💰 REVENUE OVERVIEW
• Total Revenue Earned: ${dashboard['overview']['total_revenue']:.2f}
• Progress to First $100: {dashboard['overview']['first_100_progress']}
• Days Active: {dashboard['overview']['days_active']}
• Days to First $100: {dashboard['overview']['days_to_first_100'] or 'In Progress'}

📊 PROPOSAL METRICS
• Created: {dashboard['proposals']['created']}
• Submitted: {dashboard['proposals']['submitted']}
• Responses: {dashboard['proposals']['responses']}
• Accepted: {dashboard['proposals']['accepted']}
• Completed: {dashboard['proposals']['completed']}

📈 CONVERSION RATES
• Response Rate: {dashboard['conversion_rates']['response_rate']}
• Acceptance Rate: {dashboard['conversion_rates']['acceptance_rate']}
• Completion Rate: {dashboard['conversion_rates']['completion_rate']}

🎯 PROJECTIONS
• Daily Average: ${dashboard['revenue_projections']['daily_average']:.2f}
• Weekly Projection: ${dashboard['revenue_projections']['weekly_projection']:.2f}
• Monthly Projection: ${dashboard['revenue_projections']['monthly_projection']:.2f}
• Path to First $100: ${dashboard['revenue_projections']['path_to_first_100']}

🏆 PLATFORM PERFORMANCE
"""

        for platform, stats in dashboard['platform_performance'].items():
            report += f"• {platform}: {stats['submitted']} submitted, {stats['responses']} responses, ${stats['revenue']:.2f} revenue\n"

        report += f"""
🕒 RECENT ACTIVITY (Last 7 days)
"""
        for activity in dashboard['recent_activity'][:5]:
            report += f"• {activity['date']}: {activity['type']} on {activity['platform']} - {activity['status']} (${activity['value']})\n"

        return report

    def export_data(self, format: str = "csv") -> str:
        """Export data to CSV or JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            filename = self.data_dir / f"revenue_export_{timestamp}.csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Proposal ID', 'Type', 'Platform', 'Client', 'Value',
                    'Status', 'Submitted', 'Response', 'Accepted', 'Completed', 'Payment'
                ])

                for proposal in self.proposals:
                    writer.writerow([
                        proposal.proposal_id,
                        proposal.opportunity_type,
                        proposal.platform,
                        proposal.client_name,
                        proposal.proposal_value,
                        proposal.status.value,
                        proposal.submitted_date.strftime('%Y-%m-%d') if proposal.submitted_date else '',
                        proposal.response_date.strftime('%Y-%m-%d') if proposal.response_date else '',
                        proposal.acceptance_date.strftime('%Y-%m-%d') if proposal.acceptance_date else '',
                        proposal.completion_date.strftime('%Y-%m-%d') if proposal.completion_date else '',
                        proposal.actual_payment or ''
                    ])

        return str(filename)

def simulate_real_revenue_flow():
    """Simulate a real revenue generation flow"""
    print("🚀 Revenue Tracking Simulation")
    print("=" * 50)

    tracker = RevenueTracker()

    # Day 1: Create and submit initial proposals
    print("\n📅 DAY 1: Initial Proposal Submissions")

    proposals = [
        ("prop_001", "content_writing", "Upwork", "TechCorp", "Blog posts about AI tools", 500),
        ("prop_002", "prompt_engineering", "LinkedIn", "Marketing Agency", "ChatGPT optimization", 800),
        ("prop_003", "ai_automation", "Fiverr", "E-commerce Store", "Order processing automation", 1200),
        ("prop_004", "social_media", "Facebook Groups", "Local Business", "Instagram management", 400),
        ("prop_005", "content_writing", "Upwork", "SaaS Startup", "Technical documentation", 600)
    ]

    for prop_id, opp_type, platform, client, description, value in proposals:
        tracker.add_proposal(prop_id, opp_type, platform, client, description, value)
        tracker.submit_proposal(prop_id)

    print(f"✅ Submitted {len(proposals)} proposals")

    # Day 3: First responses
    print("\n📅 DAY 3: First Responses")
    tracker.record_response("prop_001", "Interested, wants to see portfolio")
    tracker.record_response("prop_004", "Looks good, when can you start?")

    # Day 5: First acceptance
    print("\n📅 DAY 5: First Acceptance!")
    tracker.accept_proposal("prop_004", 400, "Accepted at full rate, starting Monday")

    # Day 7: More responses
    print("\n📅 DAY 7: More Activity")
    tracker.record_response("prop_002", "Very impressed with examples")
    tracker.accept_proposal("prop_002", 800, "Hired for 3-month project")

    # Day 10: First completion and payment
    print("\n📅 DAY 10: First Payment!")
    tracker.complete_project("prop_004", 400)

    # Day 14: Second payment
    print("\n📅 DAY 14: Major Milestone!")
    tracker.complete_project("prop_002", 800)

    # Generate final report
    print("\n" + "=" * 50)
    print(tracker.generate_report())

    # Export data
    export_file = tracker.export_data()
    print(f"\n📊 Data exported to: {export_file}")

    return tracker

if __name__ == "__main__":
    simulate_real_revenue_flow()
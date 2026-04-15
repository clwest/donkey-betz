"""
Spider Data Validator
====================

Validates and persists spider-collected data to ensure only real, valid data
flows through the system.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SpiderDataValidator:
    """Validates spider-collected data before persistence."""

    @staticmethod
    def validate_job(job_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a job opportunity from spiders.

        Args:
            job_data: Job data dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Required fields
        required_fields = ['title', 'company', 'description']

        # Check required fields
        for field in required_fields:
            if field not in job_data or not job_data[field]:
                return False, f"Missing required field: {field}"

        # Validate title
        if len(job_data['title']) < 3 or len(job_data['title']) > 200:
            return False, "Invalid title length"

        # Validate company (not placeholder)
        invalid_companies = ['unknown', 'n/a', 'not specified', 'company']
        if job_data['company'].lower() in invalid_companies:
            return False, "Invalid company name"

        # Validate description
        if len(job_data['description']) < 20:
            return False, "Description too short"

        # Validate URL if present
        if 'url' in job_data and job_data['url']:
            if not SpiderDataValidator._is_valid_url(job_data['url']):
                return False, "Invalid URL"

        # Validate salary if present
        if 'salary' in job_data and job_data['salary']:
            if not SpiderDataValidator._is_valid_salary(job_data['salary']):
                return False, "Invalid salary format"

        # Check for spam/fake indicators
        spam_keywords = ['make money fast', 'get rich quick', 'mlm', 'pyramid']
        description_lower = job_data['description'].lower()
        for keyword in spam_keywords:
            if keyword in description_lower:
                return False, f"Spam indicator detected: {keyword}"

        return True, None

    @staticmethod
    def validate_opportunity(opportunity_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate an income opportunity.

        Args:
            opportunity_data: Opportunity data dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Required fields for opportunities
        required_fields = ['title', 'stream_type', 'potential_monthly']

        for field in required_fields:
            if field not in opportunity_data or not opportunity_data[field]:
                return False, f"Missing required field: {field}"

        # Validate potential monthly income
        potential = opportunity_data['potential_monthly']
        if isinstance(potential, str):
            # Check if it contains dollar amounts
            if '$' not in potential and not any(c.isdigit() for c in potential):
                return False, "Invalid potential monthly format"

        # Validate stream type
        valid_stream_types = [
            'Freelance/Contract', 'AI Services', 'Automation',
            'Digital Products', 'Trading & Finance', 'Consulting',
            'Content Creation', 'E-commerce', 'SaaS'
        ]

        if opportunity_data['stream_type'] not in valid_stream_types:
            logger.warning(f"Unknown stream type: {opportunity_data['stream_type']}")

        # Validate success rate if present
        if 'success_rate' in opportunity_data:
            rate = opportunity_data['success_rate']
            if not isinstance(rate, (int, float)) or rate < 0 or rate > 100:
                return False, "Invalid success rate"

        return True, None

    @staticmethod
    def validate_batch(data_list: List[Dict[str, Any]], data_type: str = 'job') -> List[Dict[str, Any]]:
        """
        Validate a batch of data items.

        Args:
            data_list: List of data dictionaries
            data_type: 'job' or 'opportunity'

        Returns:
            List of valid data items
        """
        valid_items = []
        validation_func = (
            SpiderDataValidator.validate_job
            if data_type == 'job'
            else SpiderDataValidator.validate_opportunity
        )

        for item in data_list:
            is_valid, error = validation_func(item)
            if is_valid:
                # Add validation metadata
                item['validated'] = True
                item['validation_timestamp'] = datetime.now().isoformat()
                valid_items.append(item)
            else:
                logger.warning(f"Invalid {data_type}: {error} - {item.get('title', 'Unknown')}")

        logger.info(f"✅ Validated {len(valid_items)}/{len(data_list)} {data_type}s")
        return valid_items

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as _e:
            logger.warning(
                "spider_validator._is_valid_url: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    @staticmethod
    def _is_valid_salary(salary: str) -> bool:
        """Check if salary format is valid."""
        # Look for dollar signs or numbers
        if '$' in salary or '€' in salary or '£' in salary:
            return True

        # Check for numeric values
        numbers = re.findall(r'\d+', salary)
        return len(numbers) > 0


class SpiderDataPersistence:
    """Handles persistence of validated spider data."""

    @staticmethod
    def persist_jobs(jobs: List[Dict[str, Any]]) -> int:
        """
        Persist validated jobs to database.

        Args:
            jobs: List of validated job dictionaries

        Returns:
            Number of jobs persisted
        """
        # Session 1036: Use ActionPlan (not OpportunityActionPlan which requires FK)
        from intelligence.models import ActionPlan

        persisted_count = 0

        for job in jobs:
            try:
                # Extract salary amount for revenue potential
                salary_str = job.get('salary', '$0')
                salary_amount = SpiderDataPersistence._extract_salary_amount(salary_str)

                # Create or update in database
                obj, created = ActionPlan.objects.update_or_create(
                    opportunity_id=f"spider_{job.get('id', '')}_{job.get('source', 'unknown')}",
                    defaults={
                        'opportunity_title': job.get('title', 'Spider opportunity')[:255],
                        'opportunity_data': {
                            **job,
                            'ml_confidence': job.get('aiScore', 0.75),
                            'revenue_potential': str(salary_amount),
                        },
                        'status': 'created',
                    }
                )

                if created:
                    persisted_count += 1
                    logger.debug(f"Persisted job: {job.get('title')}")

            except Exception as e:
                logger.error(f"Failed to persist job: {e}")

        logger.info(f"💾 Persisted {persisted_count} new jobs to database")
        return persisted_count

    @staticmethod
    def persist_opportunities(opportunities: List[Dict[str, Any]]) -> int:
        """
        Persist validated opportunities to database.

        Args:
            opportunities: List of validated opportunity dictionaries

        Returns:
            Number of opportunities persisted
        """
        # Session 1036: Use ActionPlan (not OpportunityActionPlan which requires FK)
        from intelligence.models import ActionPlan

        persisted_count = 0

        for opp in opportunities:
            try:
                # Extract potential amount
                potential = opp.get('potential_monthly', '$0')
                potential_amount = SpiderDataPersistence._extract_salary_amount(potential)

                # Create or update
                _, created = ActionPlan.objects.update_or_create(
                    opportunity_id=f"opp_{opp.get('id', '')}_{opp.get('stream_type', 'unknown')}",
                    defaults={
                        'opportunity_title': opp.get('title', 'Income opportunity')[:255],
                        'opportunity_data': {
                            **opp,
                            'ml_confidence': opp.get('market_demand', 80) / 100,
                            'revenue_potential': str(potential_amount),
                        },
                        'status': 'created',
                    }
                )

                if created:
                    persisted_count += 1
                    logger.debug(f"Persisted opportunity: {opp.get('title')}")

            except Exception as e:
                logger.error(f"Failed to persist opportunity: {e}")

        logger.info(f"💾 Persisted {persisted_count} new opportunities to database")
        return persisted_count

    @staticmethod
    def _extract_salary_amount(salary_str: str) -> float:
        """Extract numeric amount from salary string."""
        import re

        # Remove currency symbols and commas
        clean_str = salary_str.replace('$', '').replace(',', '').replace('€', '').replace('£', '')

        # Find all numbers
        numbers = re.findall(r'\d+', clean_str)

        if numbers:
            # Take the first/largest reasonable number
            amount = float(numbers[0])

            # Check if it's hourly and convert to monthly
            if 'hour' in salary_str.lower() or '/hr' in salary_str.lower():
                amount = amount * 160  # Assume 160 hours/month

            # Check if it's yearly and convert to monthly
            elif 'year' in salary_str.lower() or '/yr' in salary_str.lower():
                amount = amount / 12

            return amount

        return 0.0


class SpiderOrchestrator:
    """Orchestrates spider data collection, validation, and persistence."""

    def __init__(self):
        self.validator = SpiderDataValidator()
        self.persistence = SpiderDataPersistence()

    def process_spider_data(self, raw_data: List[Dict[str, Any]], data_type: str = 'job') -> Dict[str, Any]:
        """
        Process raw spider data through validation and persistence.

        Args:
            raw_data: Raw data from spiders
            data_type: Type of data ('job' or 'opportunity')

        Returns:
            Processing results
        """
        logger.info(f"🕷️ Processing {len(raw_data)} {data_type}s from spiders")

        # Step 1: Validate data
        valid_data = SpiderDataValidator.validate_batch(raw_data, data_type)

        if not valid_data:
            logger.warning("⚠️ No valid data after validation")
            return {
                'success': False,
                'total': len(raw_data),
                'valid': 0,
                'persisted': 0
            }

        # Step 2: Persist valid data
        if data_type == 'job':
            persisted = SpiderDataPersistence.persist_jobs(valid_data)
        else:
            persisted = SpiderDataPersistence.persist_opportunities(valid_data)

        # Step 3: Cache valid data for immediate use
        from django.core.cache import cache

        cache_key = f'validated_{data_type}s'
        cache.set(cache_key, valid_data, 3600)  # Cache for 1 hour

        # Step 4: Trigger shared memory update
        self._update_shared_memory(valid_data, data_type)

        return {
            'success': True,
            'total': len(raw_data),
            'valid': len(valid_data),
            'persisted': persisted,
            'cached': True
        }

    def _update_shared_memory(self, data: List[Dict[str, Any]], data_type: str):
        """Update shared memory with new data."""
        try:
            from intelligence.shared_memory import shared_memory

            # Share as experience for all entities to learn from
            shared_memory.share_experience(
                'spider',
                'orchestrator',
                {
                    'type': f'new_{data_type}s_collected',
                    'count': len(data),
                    'timestamp': datetime.now().isoformat(),
                    'sample': data[:3] if data else []  # Share first 3 as samples
                }
            )

            logger.info(f"📚 Shared {len(data)} {data_type}s with all AI entities")

        except Exception as e:
            logger.error(f"Failed to update shared memory: {e}")


# Export main orchestrator
spider_orchestrator = SpiderOrchestrator()
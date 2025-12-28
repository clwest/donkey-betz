"""
Job Hunter Spider Army
Massive intelligence gathering for job opportunities across multiple platforms
"""

import scrapy
import re
from datetime import datetime
from urllib.parse import urljoin
from .base_spider import JobOpportunitySpider


class UpworkOpportunitiesSpider(JobOpportunitySpider):
    """
    Upwork job opportunities spider
    Targets freelance opportunities for income builders
    """

    name = 'upwork_opportunities'
    allowed_domains = ['upwork.com']

    # Target searches for high-value AI/tech opportunities
    search_queries = [
        'AI content writing',
        'machine learning',
        'data analysis',
        'python development',
        'web scraping',
        'automation',
        'AI chatbot',
        'content creation',
        'digital marketing',
        'wordpress development'
    ]

    def start_requests(self):
        """Generate search requests for different opportunity types"""
        base_url = "https://www.upwork.com/nx/search/jobs/"

        for query in self.search_queries:
            search_params = {
                'q': query,
                'sort': 'recency',
                'amount': '1000-',  # $1000+ projects
                'duration_v3': 'week,month',  # Short to medium term
                'client_hires': '1-9,10-',  # Experienced clients
                'proposals': '0-4'  # Less competition
            }

            # Build search URL
            param_string = '&'.join([f"{k}={v}" for k, v in search_params.items()])
            url = f"{base_url}?{param_string}"

            yield scrapy.Request(
                url=url,
                callback=self.parse_job_listings,
                meta={
                    'search_query': query,
                    'search_type': 'upwork_freelance'
                }
            )

    def parse_job_listings(self, response):
        """Parse Upwork job listing pages"""
        job_cards = response.css('article[data-test="JobTile"]')

        for job_card in job_cards:
            try:
                job_data = self.extract_upwork_job(job_card, response)
                if job_data:
                    # Process through intelligence pipeline
                    intelligence = self.process_item(job_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Upwork job: {e}")

        # Follow pagination
        next_page = response.css('a[aria-label="Next"]::attr(href)').get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_job_listings,
                meta=response.meta
            )

    def extract_upwork_job(self, job_card, response):
        """Extract job details from Upwork job card"""
        try:
            title = job_card.css('h4[data-test="JobTileTitle"] a::text').get()
            if not title:
                return None

            # Extract job details
            description = job_card.css('span[data-test="JobDescription"]::text').get() or ""
            budget_text = job_card.css('strong[data-test="JobBudget"]::text').get() or ""
            posted_time = job_card.css('small[data-test="JobDate"] span[title]::attr(title)').get()
            client_rating = job_card.css('div[data-test="ClientRating"] span::text').get()
            skills = job_card.css('a[data-test="JobSkill"]::text').getall()

            # Parse budget
            budget_amount = self.parse_budget(budget_text)

            # Extract job URL
            job_url = job_card.css('h4[data-test="JobTileTitle"] a::attr(href)').get()
            if job_url:
                job_url = urljoin(response.url, job_url)

            job_data = {
                'title': title.strip(),
                'description': description.strip(),
                'budget_text': budget_text.strip(),
                'budget_amount': budget_amount,
                'posted_time': posted_time,
                'client_rating': client_rating,
                'skills': skills,
                'job_url': job_url,
                'platform': 'upwork',
                'search_query': response.meta.get('search_query'),
                'opportunity_type': 'freelance',
                'scraped_at': datetime.now().isoformat()
            }

            return job_data

        except Exception as e:
            self.logger.error(f"Error extracting Upwork job details: {e}")
            return None

    def parse_budget(self, budget_text):
        """Parse budget text into numeric amount"""
        if not budget_text:
            return None

        # Extract numbers from budget text
        numbers = re.findall(r'\$?([\d,]+)', budget_text)
        if numbers:
            try:
                # Convert to float, removing commas
                amount = float(numbers[0].replace(',', ''))
                return amount
            except ValueError:
                pass

        return None


class FreelancerOpportunitiesSpider(JobOpportunitySpider):
    """
    Freelancer.com opportunities spider
    """

    name = 'freelancer_opportunities'
    allowed_domains = ['freelancer.com']

    search_queries = [
        'python',
        'web scraping',
        'data entry',
        'content writing',
        'AI development',
        'machine learning',
        'automation',
        'wordpress'
    ]

    def start_requests(self):
        """Generate search requests for Freelancer.com"""
        base_url = "https://www.freelancer.com/search/projects/"

        for query in self.search_queries:
            search_params = {
                'q': query,
                'w': 'f',  # Fixed price projects
                't': '0',  # All project types
                'min': '500',  # Minimum $500
                'max': '5000'  # Maximum $5000
            }

            param_string = '&'.join([f"{k}={v}" for k, v in search_params.items()])
            url = f"{base_url}?{param_string}"

            yield scrapy.Request(
                url=url,
                callback=self.parse_freelancer_listings,
                meta={'search_query': query}
            )

    def parse_freelancer_listings(self, response):
        """Parse Freelancer.com job listings"""
        project_cards = response.css('div.JobSearchCard-item')

        for card in project_cards:
            try:
                job_data = self.extract_freelancer_job(card, response)
                if job_data:
                    intelligence = self.process_item(job_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Freelancer job: {e}")

    def extract_freelancer_job(self, card, response):
        """Extract job details from Freelancer project card"""
        try:
            title = card.css('a.JobSearchCard-primary-heading-link::text').get()
            if not title:
                return None

            description = card.css('p.JobSearchCard-primary-description::text').get() or ""
            budget_text = card.css('div.JobSearchCard-primary-price::text').get() or ""
            bids_text = card.css('span.JobSearchCard-secondary-price::text').get() or ""
            skills = card.css('a.JobSearchCard-secondary-skill::text').getall()

            # Extract project URL
            project_url = card.css('a.JobSearchCard-primary-heading-link::attr(href)').get()
            if project_url:
                project_url = urljoin(response.url, project_url)

            # Parse budget
            budget_amount = self.parse_freelancer_budget(budget_text)

            job_data = {
                'title': title.strip(),
                'description': description.strip(),
                'budget_text': budget_text.strip(),
                'budget_amount': budget_amount,
                'bids_text': bids_text.strip() if bids_text else "",
                'skills': skills,
                'job_url': project_url,
                'platform': 'freelancer',
                'search_query': response.meta.get('search_query'),
                'opportunity_type': 'freelance',
                'scraped_at': datetime.now().isoformat()
            }

            return job_data

        except Exception as e:
            self.logger.error(f"Error extracting Freelancer job: {e}")
            return None

    def parse_freelancer_budget(self, budget_text):
        """Parse Freelancer budget text"""
        if not budget_text:
            return None

        # Extract currency amounts
        amounts = re.findall(r'\$(\d+)', budget_text)
        if amounts:
            try:
                return float(amounts[0])
            except ValueError:
                pass

        return None


class FiverrGigAnalyzerSpider(JobOpportunitySpider):
    """
    Fiverr marketplace analyzer
    Identifies trending services and pricing opportunities
    """

    name = 'fiverr_gig_analyzer'
    allowed_domains = ['fiverr.com']

    categories = [
        'writing-translation',
        'digital-marketing',
        'graphics-design',
        'programming-tech',
        'ai-services',
        'data'
    ]

    def start_requests(self):
        """Generate requests for Fiverr categories"""
        for category in self.categories:
            url = f"https://www.fiverr.com/categories/{category}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_category,
                meta={'category': category}
            )

    def parse_category(self, response):
        """Parse Fiverr category pages"""
        gig_cards = response.css('div.gig-card-layout')

        for card in gig_cards:
            try:
                gig_data = self.extract_fiverr_gig(card, response)
                if gig_data:
                    intelligence = self.process_item(gig_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Fiverr gig: {e}")

    def extract_fiverr_gig(self, card, response):
        """Extract gig details from Fiverr gig card"""
        try:
            title = card.css('h3 a::text').get()
            if not title:
                return None

            seller = card.css('span.seller-name::text').get()
            rating = card.css('span.gig-rating::text').get()
            price = card.css('span.price::text').get()
            orders = card.css('span.orders-in-queue::text').get()

            gig_url = card.css('h3 a::attr(href)').get()
            if gig_url:
                gig_url = urljoin(response.url, gig_url)

            gig_data = {
                'title': title.strip(),
                'seller': seller.strip() if seller else "",
                'rating': rating.strip() if rating else "",
                'price': price.strip() if price else "",
                'orders_in_queue': orders.strip() if orders else "",
                'gig_url': gig_url,
                'category': response.meta.get('category'),
                'platform': 'fiverr',
                'opportunity_type': 'service_template',
                'scraped_at': datetime.now().isoformat()
            }

            return gig_data

        except Exception as e:
            self.logger.error(f"Error extracting Fiverr gig: {e}")
            return None


class IndeedJobSpider(JobOpportunitySpider):
    """
    Indeed job opportunities spider
    Targets full-time and part-time opportunities
    """

    name = 'indeed_jobs'
    allowed_domains = ['indeed.com']

    job_queries = [
        'remote data analyst',
        'python developer remote',
        'content writer remote',
        'digital marketing remote',
        'AI engineer remote',
        'machine learning remote',
        'freelance writer',
        'contract developer'
    ]

    def start_requests(self):
        """Generate Indeed job search requests"""
        for query in self.job_queries:
            # Format query for URL
            formatted_query = query.replace(' ', '+')
            url = f"https://indeed.com/jobs?q={formatted_query}&l=Remote&radius=0&sort=date"

            yield scrapy.Request(
                url=url,
                callback=self.parse_indeed_jobs,
                meta={'search_query': query}
            )

    def parse_indeed_jobs(self, response):
        """Parse Indeed job listings"""
        job_cards = response.css('div[data-jk]')

        for card in job_cards:
            try:
                job_data = self.extract_indeed_job(card, response)
                if job_data:
                    intelligence = self.process_item(job_data, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting Indeed job: {e}")

        # Follow next page
        next_link = response.css('a[aria-label="Next Page"]::attr(href)').get()
        if next_link:
            yield response.follow(
                next_link,
                callback=self.parse_indeed_jobs,
                meta=response.meta
            )

    def extract_indeed_job(self, card, response):
        """Extract job details from Indeed job card"""
        try:
            title = card.css('h2 a span::text').get()
            if not title:
                return None

            company = card.css('span.companyName a::text').get() or card.css('span.companyName::text').get()
            location = card.css('div[data-testid="job-location"]::text').get()
            salary = card.css('span.salaryText::text').get()
            summary = card.css('div.job-snippet::text').get()

            job_url = card.css('h2 a::attr(href)').get()
            if job_url:
                job_url = urljoin(response.url, job_url)

            job_data = {
                'title': title.strip(),
                'company': company.strip() if company else "",
                'location': location.strip() if location else "",
                'salary': salary.strip() if salary else "",
                'summary': summary.strip() if summary else "",
                'job_url': job_url,
                'platform': 'indeed',
                'search_query': response.meta.get('search_query'),
                'opportunity_type': 'employment',
                'scraped_at': datetime.now().isoformat()
            }

            return job_data

        except Exception as e:
            self.logger.error(f"Error extracting Indeed job: {e}")
            return None
"""
Digital Services Spider Army
Intelligence gathering for online service opportunities
"""

import scrapy
import re
import json
from datetime import datetime
from urllib.parse import urljoin
from .base_spider import ContentOpportunitySpider


class OnlineCoachingSpider(ContentOpportunitySpider):
    """
    Online coaching and consulting opportunity spider
    Finds profitable coaching niches and market gaps
    """

    name = 'online_coaching'
    allowed_domains = ['coach.me', 'clarity.fm', 'thumbtack.com', 'udemy.com']

    coaching_niches = [
        'life coaching', 'business coaching', 'fitness coaching', 'career coaching',
        'relationship coaching', 'health coaching', 'financial coaching', 'productivity coaching',
        'mindfulness coaching', 'leadership coaching', 'sales coaching', 'marketing coaching'
    ]

    def start_requests(self):
        """Generate requests for coaching market research"""
        for niche in self.coaching_niches:
            # Udemy course research to see demand
            url = f"https://www.udemy.com/courses/search/?q={niche.replace(' ', '+')}&sort=most-reviewed"

            yield scrapy.Request(
                url=url,
                callback=self.parse_udemy_coaching_demand,
                meta={
                    'niche': niche,
                    'opportunity_type': 'online_coaching'
                }
            )

    def parse_udemy_coaching_demand(self, response):
        """Parse Udemy to understand coaching demand"""
        courses = response.css('[data-purpose="course-card-container"]')

        for course in courses[:10]:
            try:
                opportunity = self.extract_coaching_opportunity(course, response)
                if opportunity:
                    intelligence = self.process_item(opportunity, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting coaching opportunity: {e}")

    def extract_coaching_opportunity(self, course, response):
        """Extract coaching opportunity from course data"""
        try:
            title = course.css('[data-purpose="course-title-url"] span::text').get()
            if not title:
                return None

            price_elem = course.css('.price-text-container span::text').get()
            price = float(re.findall(r'[\d.]+', price_elem or '0')[0]) if price_elem else 0

            students_elem = course.css('[data-purpose="enrollment"]::text').get()
            students = self.parse_student_count(students_elem)

            rating_elem = course.css('[data-purpose="rating-number"]::text').get()
            rating = float(rating_elem) if rating_elem else 0

            return {
                'id': f"coaching_{hash(title + str(price))}",
                'title': title.strip(),
                'niche': response.meta['niche'],
                'course_price': price,
                'total_students': students,
                'rating': rating,
                'source': 'udemy_market_research',
                'opportunity_type': 'coaching_service',
                'market_demand': self.assess_coaching_demand(students, rating),
                'suggested_coaching_rate': self.calculate_coaching_rate(price, students),
                'competition_level': self.assess_coaching_competition(students),
                'income_potential': self.estimate_coaching_income(response.meta['niche']),
                'required_expertise': self.assess_required_expertise(response.meta['niche']),
                'startup_cost': 'low'  # Coaching has low startup costs
            }

        except Exception as e:
            self.logger.error(f"Error extracting coaching data: {e}")
            return None

    def parse_student_count(self, students_text):
        """Parse student count from text"""
        if not students_text:
            return 0

        # Handle formats like "1,234 students" or "12.5K students"
        if 'K' in students_text:
            return int(float(re.findall(r'[\d.]+', students_text)[0]) * 1000)
        else:
            return int(re.sub(r'[^\d]', '', students_text) or 0)

    def assess_coaching_demand(self, students, rating):
        """Assess market demand for coaching niche"""
        if students > 10000 and rating > 4.0:
            return 'high'
        elif students > 1000 and rating > 3.5:
            return 'medium'
        else:
            return 'low'

    def calculate_coaching_rate(self, course_price, students):
        """Calculate suggested hourly coaching rate"""
        # Base rate on course success
        base_rate = 50  # $50/hour baseline

        if students > 10000:
            multiplier = 2.0
        elif students > 5000:
            multiplier = 1.5
        elif students > 1000:
            multiplier = 1.2
        else:
            multiplier = 1.0

        return int(base_rate * multiplier)

    def assess_coaching_competition(self, students):
        """Assess competition level"""
        if students > 50000:
            return 'high'
        elif students > 10000:
            return 'medium'
        else:
            return 'low'

    def estimate_coaching_income(self, niche):
        """Estimate monthly income potential"""
        income_map = {
            'business coaching': {'min': 2000, 'max': 15000},
            'life coaching': {'min': 1500, 'max': 8000},
            'fitness coaching': {'min': 1000, 'max': 5000},
            'financial coaching': {'min': 2500, 'max': 12000},
            'career coaching': {'min': 1800, 'max': 9000}
        }
        return income_map.get(niche, {'min': 1000, 'max': 5000})

    def assess_required_expertise(self, niche):
        """Assess expertise level required"""
        high_expertise = ['business coaching', 'financial coaching', 'leadership coaching']
        medium_expertise = ['career coaching', 'health coaching', 'productivity coaching']

        if niche in high_expertise:
            return 'high'
        elif niche in medium_expertise:
            return 'medium'
        else:
            return 'beginner_friendly'


class OnlineTutoringSpider(ContentOpportunitySpider):
    """
    Online tutoring opportunity spider
    Finds high-demand tutoring subjects
    """

    name = 'online_tutoring'
    allowed_domains = ['tutor.com', 'wyzant.com', 'preply.com', 'italki.com']

    tutoring_subjects = [
        'mathematics', 'science', 'english', 'programming', 'languages',
        'test prep', 'music', 'art', 'business', 'accounting'
    ]

    def start_requests(self):
        """Generate requests for tutoring market research"""
        for subject in self.tutoring_subjects:
            # Wyzant tutor search to analyze market
            url = f"https://www.wyzant.com/tutors/{subject.replace(' ', '-')}"

            yield scrapy.Request(
                url=url,
                callback=self.parse_wyzant_tutoring,
                meta={
                    'subject': subject,
                    'opportunity_type': 'online_tutoring'
                }
            )

    def parse_wyzant_tutoring(self, response):
        """Parse Wyzant for tutoring opportunities"""
        tutors = response.css('.tutor-card')

        rates = []
        for tutor in tutors[:20]:
            try:
                rate_elem = tutor.css('.rate::text').get()
                if rate_elem:
                    rate = float(re.findall(r'[\d.]+', rate_elem)[0])
                    rates.append(rate)
            except:
                continue

        if rates:
            opportunity = {
                'id': f"tutoring_{response.meta['subject']}",
                'subject': response.meta['subject'],
                'source': 'wyzant_market_analysis',
                'opportunity_type': 'tutoring_service',
                'average_hourly_rate': sum(rates) / len(rates),
                'rate_range': {'min': min(rates), 'max': max(rates)},
                'market_saturation': self.assess_tutor_competition(len(tutors)),
                'demand_level': self.assess_tutoring_demand(response.meta['subject']),
                'required_qualifications': self.get_tutoring_requirements(response.meta['subject']),
                'flexibility': 'high',  # Online tutoring is very flexible
                'income_potential': self.calculate_tutoring_income(rates),
                'client_acquisition_difficulty': self.assess_client_acquisition(response.meta['subject'])
            }

            intelligence = self.process_item(opportunity, response)
            if intelligence:
                yield intelligence

    def assess_tutor_competition(self, tutor_count):
        """Assess competition level"""
        if tutor_count > 100:
            return 'high'
        elif tutor_count > 50:
            return 'medium'
        else:
            return 'low'

    def assess_tutoring_demand(self, subject):
        """Assess demand for tutoring subject"""
        high_demand = ['mathematics', 'science', 'english', 'test prep', 'programming']
        if subject in high_demand:
            return 'high'
        else:
            return 'medium'

    def get_tutoring_requirements(self, subject):
        """Get typical requirements for subject"""
        requirements_map = {
            'mathematics': 'Degree in Math/Engineering or strong math background',
            'science': 'Science degree or extensive science coursework',
            'programming': 'Professional programming experience or CS degree',
            'languages': 'Native speaker or advanced proficiency',
            'test prep': 'High test scores and tutoring experience',
            'music': 'Musical training and performance experience'
        }
        return requirements_map.get(subject, 'Subject expertise and teaching ability')

    def calculate_tutoring_income(self, rates):
        """Calculate potential monthly income"""
        if not rates:
            return {'min': 500, 'max': 2000}

        avg_rate = sum(rates) / len(rates)
        # Assume 10-30 hours per week
        min_monthly = avg_rate * 10 * 4
        max_monthly = avg_rate * 30 * 4

        return {'min': int(min_monthly), 'max': int(max_monthly)}

    def assess_client_acquisition(self, subject):
        """Assess how easy it is to get clients"""
        easy_subjects = ['test prep', 'mathematics', 'science']
        if subject in easy_subjects:
            return 'easy'
        else:
            return 'moderate'


class VirtualAssistantSpider(ContentOpportunitySpider):
    """
    Virtual assistant opportunity spider
    Finds VA service demands and niches
    """

    name = 'virtual_assistant'
    allowed_domains = ['belay.com', 'time-etc.com', 'fancy-hands.com', 'upwork.com']

    va_services = [
        'administrative', 'social media', 'content writing', 'customer service',
        'data entry', 'research', 'bookkeeping', 'email management',
        'appointment scheduling', 'lead generation', 'project management'
    ]

    def start_requests(self):
        """Generate requests for VA market research"""
        for service in self.va_services:
            # Upwork VA job search
            url = f"https://www.upwork.com/nx/search/jobs/?q=virtual+assistant+{service.replace(' ', '+')}"

            yield scrapy.Request(
                url=url,
                callback=self.parse_upwork_va_jobs,
                meta={
                    'service_type': service,
                    'opportunity_type': 'virtual_assistant'
                }
            )

    def parse_upwork_va_jobs(self, response):
        """Parse Upwork for VA opportunities"""
        jobs = response.css('[data-test="JobTile"]')

        budgets = []
        for job in jobs[:15]:
            try:
                budget_elem = job.css('[data-test="JobBudget"]::text').get()
                if budget_elem and '$' in budget_elem:
                    # Extract hourly rates
                    if '/hr' in budget_elem:
                        rate = float(re.findall(r'[\d.]+', budget_elem)[0])
                        budgets.append(rate)
            except:
                continue

        if budgets:
            opportunity = {
                'id': f"va_{response.meta['service_type']}",
                'service_type': response.meta['service_type'],
                'source': 'upwork_job_analysis',
                'opportunity_type': 'virtual_assistant_service',
                'average_hourly_rate': sum(budgets) / len(budgets),
                'rate_range': {'min': min(budgets), 'max': max(budgets)},
                'job_availability': len(jobs),
                'demand_level': self.assess_va_demand(len(jobs)),
                'skill_requirements': self.get_va_skill_requirements(response.meta['service_type']),
                'entry_barrier': self.assess_entry_barrier(response.meta['service_type']),
                'growth_potential': self.assess_va_growth_potential(response.meta['service_type']),
                'work_flexibility': 'very_high',
                'client_retention_potential': self.assess_retention_potential(response.meta['service_type'])
            }

            intelligence = self.process_item(opportunity, response)
            if intelligence:
                yield intelligence

    def assess_va_demand(self, job_count):
        """Assess demand based on job postings"""
        if job_count > 50:
            return 'high'
        elif job_count > 20:
            return 'medium'
        else:
            return 'low'

    def get_va_skill_requirements(self, service_type):
        """Get skill requirements for VA service"""
        skills_map = {
            'administrative': 'Organization, MS Office, communication',
            'social media': 'Social media platforms, content creation, analytics',
            'content writing': 'Writing skills, SEO knowledge, research',
            'bookkeeping': 'QuickBooks, Excel, accounting basics',
            'customer service': 'Communication, problem-solving, patience',
            'data entry': 'Accuracy, attention to detail, typing speed',
            'research': 'Internet research, data analysis, reporting'
        }
        return skills_map.get(service_type, 'Basic computer skills, communication')

    def assess_entry_barrier(self, service_type):
        """Assess how hard it is to get started"""
        low_barrier = ['data entry', 'administrative', 'customer service']
        high_barrier = ['bookkeeping', 'project management']

        if service_type in low_barrier:
            return 'low'
        elif service_type in high_barrier:
            return 'high'
        else:
            return 'medium'

    def assess_va_growth_potential(self, service_type):
        """Assess growth potential for service type"""
        high_growth = ['social media', 'content writing', 'lead generation']
        if service_type in high_growth:
            return 'high'
        else:
            return 'medium'

    def assess_retention_potential(self, service_type):
        """Assess how likely clients are to retain VA"""
        high_retention = ['administrative', 'bookkeeping', 'email management']
        if service_type in high_retention:
            return 'high'
        else:
            return 'medium'


class OnlineMarketplaceSpider(ContentOpportunitySpider):
    """
    Online marketplace opportunity spider
    Finds profitable selling opportunities on various platforms
    """

    name = 'online_marketplace'
    allowed_domains = ['ebay.com', 'facebook.com', 'poshmark.com', 'depop.com']

    marketplace_categories = [
        'electronics', 'clothing', 'collectibles', 'books', 'home_goods',
        'vintage', 'handmade', 'automotive', 'sports', 'toys'
    ]

    def start_requests(self):
        """Generate requests for marketplace research"""
        for category in self.marketplace_categories:
            # eBay sold listings to see what's profitable
            url = f"https://www.ebay.com/sch/i.html?_nkw={category}&LH_Sold=1&LH_Complete=1"

            yield scrapy.Request(
                url=url,
                callback=self.parse_ebay_sold_listings,
                meta={
                    'category': category,
                    'opportunity_type': 'marketplace_selling'
                }
            )

    def parse_ebay_sold_listings(self, response):
        """Parse eBay sold listings for profitable items"""
        listings = response.css('.s-item')

        for listing in listings[:20]:
            try:
                opportunity = self.extract_marketplace_opportunity(listing, response)
                if opportunity:
                    intelligence = self.process_item(opportunity, response)
                    if intelligence:
                        yield intelligence

            except Exception as e:
                self.logger.error(f"Error extracting marketplace opportunity: {e}")

    def extract_marketplace_opportunity(self, listing, response):
        """Extract marketplace selling opportunity"""
        try:
            title = listing.css('.s-item__title::text').get()
            if not title or 'Shop on eBay' in title:
                return None

            price_elem = listing.css('.s-item__price::text').get()
            if not price_elem:
                return None

            price = float(re.findall(r'[\d.]+', price_elem)[0])

            sold_date_elem = listing.css('.s-item__endedDate::text').get()

            return {
                'id': f"marketplace_{hash(title + str(price))}",
                'item_title': title.strip(),
                'sold_price': price,
                'category': response.meta['category'],
                'sold_date': sold_date_elem,
                'source': 'ebay_sold_listings',
                'opportunity_type': 'marketplace_item',
                'profit_potential': self.assess_profit_potential(price, response.meta['category']),
                'sourcing_difficulty': self.assess_sourcing_difficulty(response.meta['category']),
                'turnover_speed': self.assess_turnover_speed(response.meta['category']),
                'competition_level': self.assess_marketplace_competition(response.meta['category']),
                'capital_required': self.estimate_capital_required(price),
                'skill_level': self.assess_required_skills(response.meta['category'])
            }

        except Exception as e:
            self.logger.error(f"Error extracting marketplace data: {e}")
            return None

    def assess_profit_potential(self, price, category):
        """Assess profit potential for category"""
        profit_margins = {
            'electronics': 0.2,
            'clothing': 0.4,
            'collectibles': 0.6,
            'books': 0.3,
            'vintage': 0.5
        }
        margin = profit_margins.get(category, 0.3)
        profit = price * margin

        if profit > 50:
            return 'high'
        elif profit > 20:
            return 'medium'
        else:
            return 'low'

    def assess_sourcing_difficulty(self, category):
        """Assess how hard it is to source items"""
        easy_sourcing = ['books', 'clothing', 'home_goods']
        hard_sourcing = ['collectibles', 'vintage', 'electronics']

        if category in easy_sourcing:
            return 'easy'
        elif category in hard_sourcing:
            return 'difficult'
        else:
            return 'moderate'

    def assess_turnover_speed(self, category):
        """Assess how quickly items sell"""
        fast_categories = ['electronics', 'clothing', 'toys']
        if category in fast_categories:
            return 'fast'
        else:
            return 'moderate'

    def assess_marketplace_competition(self, category):
        """Assess competition level"""
        high_competition = ['electronics', 'clothing']
        if category in high_competition:
            return 'high'
        else:
            return 'medium'

    def estimate_capital_required(self, price):
        """Estimate capital needed to start"""
        if price <= 50:
            return 'low'
        elif price <= 200:
            return 'medium'
        else:
            return 'high'

    def assess_required_skills(self, category):
        """Assess skills needed for category"""
        skill_map = {
            'electronics': 'Product knowledge, testing ability',
            'collectibles': 'Authentication, market knowledge',
            'vintage': 'Authentication, restoration skills',
            'clothing': 'Fashion sense, condition assessment',
            'books': 'Condition grading, market knowledge'
        }
        return skill_map.get(category, 'Basic selling skills')
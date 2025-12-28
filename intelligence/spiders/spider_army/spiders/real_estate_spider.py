"""
Real Estate & Property Spider Army
Intelligence gathering for real estate investment and rental opportunities
"""

import scrapy
from .base_spider import ContentOpportunitySpider


class RentalPropertySpider(ContentOpportunitySpider):
    """
    Rental property investment opportunity spider
    Finds profitable rental properties and markets
    """

    name = 'rental_property'
    allowed_domains = ['zillow.com', 'realtor.com', 'rentometer.com', 'apartments.com']

    target_markets = [
        'Atlanta, GA', 'Austin, TX', 'Charlotte, NC', 'Columbus, OH',
        'Denver, CO', 'Kansas City, MO', 'Nashville, TN', 'Phoenix, AZ',
        'Raleigh, NC', 'Tampa, FL', 'Indianapolis, IN', 'Memphis, TN'
    ]

    def start_requests(self):
        """Generate requests for rental property research"""
        for market in self.target_markets:
            # Zillow search for investment properties
            city_state = market.replace(' ', '-').replace(',', '').lower()
            url = f"https://www.zillow.com/{city_state}/"

            yield scrapy.Request(
                url=url,
                callback=self.parse_zillow_market,
                meta={
                    'market': market,
                    'opportunity_type': 'rental_property'
                }
            )

    def parse_zillow_market(self, response):
        """Parse Zillow for rental property opportunities"""
        # This would parse property listings
        # For demo, we'll create sample opportunities
        market = response.meta['market']

        # Generate sample rental opportunities
        sample_properties = [
            {
                'price': 150000, 'rent': 1200, 'sqft': 1200, 'bedrooms': 3,
                'property_type': 'single_family', 'neighborhood': 'Downtown'
            },
            {
                'price': 85000, 'rent': 800, 'sqft': 900, 'bedrooms': 2,
                'property_type': 'condo', 'neighborhood': 'Suburbs'
            },
            {
                'price': 200000, 'rent': 1800, 'sqft': 1500, 'bedrooms': 4,
                'property_type': 'single_family', 'neighborhood': 'Family Area'
            }
        ]

        for prop in sample_properties:
            opportunity = self.create_rental_opportunity(prop, market)
            if opportunity and self.is_good_rental_investment(opportunity):
                intelligence = self.process_item(opportunity, response)
                if intelligence:
                    yield intelligence

    def create_rental_opportunity(self, prop_data, market):
        """Create rental property opportunity"""
        try:
            # Calculate key metrics
            cap_rate = (prop_data['rent'] * 12) / prop_data['price']
            cash_on_cash = self.calculate_cash_on_cash_return(prop_data)
            monthly_cashflow = self.calculate_monthly_cashflow(prop_data)

            return {
                'id': f"rental_{hash(str(prop_data) + market)}",
                'market': market,
                'property_type': prop_data['property_type'],
                'purchase_price': prop_data['price'],
                'monthly_rent': prop_data['rent'],
                'square_feet': prop_data['sqft'],
                'bedrooms': prop_data['bedrooms'],
                'neighborhood': prop_data['neighborhood'],
                'source': 'zillow_analysis',
                'opportunity_type': 'rental_investment',
                'cap_rate': round(cap_rate * 100, 2),  # Convert to percentage
                'cash_on_cash_return': round(cash_on_cash * 100, 2),
                'monthly_cashflow': monthly_cashflow,
                'annual_cashflow': monthly_cashflow * 12,
                'down_payment_required': prop_data['price'] * 0.25,  # 25% down
                'total_initial_investment': self.calculate_initial_investment(prop_data['price']),
                'roi_timeframe': self.calculate_roi_timeframe(prop_data),
                'market_appreciation_potential': self.assess_appreciation_potential(market),
                'rental_demand': self.assess_rental_demand(market, prop_data),
                'management_complexity': self.assess_management_complexity(prop_data['property_type']),
                'financing_difficulty': self.assess_financing_difficulty(prop_data['price'])
            }

        except Exception as e:
            self.logger.error(f"Error creating rental opportunity: {e}")
            return None

    def calculate_cash_on_cash_return(self, prop_data):
        """Calculate cash-on-cash return"""
        monthly_cashflow = self.calculate_monthly_cashflow(prop_data)
        annual_cashflow = monthly_cashflow * 12
        initial_investment = self.calculate_initial_investment(prop_data['price'])

        if initial_investment > 0:
            return annual_cashflow / initial_investment
        return 0

    def calculate_monthly_cashflow(self, prop_data):
        """Calculate monthly cashflow"""
        # Simplified calculation
        monthly_rent = prop_data['rent']

        # Estimate monthly expenses (property tax, insurance, maintenance, vacancy)
        monthly_expenses = prop_data['price'] * 0.012 / 12  # 1.2% annually

        # Mortgage payment (assuming 30-year loan at 7% with 25% down)
        loan_amount = prop_data['price'] * 0.75
        monthly_payment = loan_amount * 0.00665  # Approximate monthly payment factor

        return monthly_rent - monthly_expenses - monthly_payment

    def calculate_initial_investment(self, price):
        """Calculate total initial investment needed"""
        down_payment = price * 0.25  # 25% down
        closing_costs = price * 0.03  # 3% closing costs
        inspection_appraisal = 1500
        initial_repairs = price * 0.02  # 2% for initial repairs

        return down_payment + closing_costs + inspection_appraisal + initial_repairs

    def calculate_roi_timeframe(self, prop_data):
        """Calculate time to recoup initial investment"""
        monthly_cashflow = self.calculate_monthly_cashflow(prop_data)
        initial_investment = self.calculate_initial_investment(prop_data['price'])

        if monthly_cashflow > 0:
            months = initial_investment / monthly_cashflow
            return f"{int(months)} months"
        return "Never (negative cashflow)"

    def is_good_rental_investment(self, opportunity):
        """Determine if rental property is a good investment"""
        return (
            opportunity['cap_rate'] >= 6.0 and  # At least 6% cap rate
            opportunity['cash_on_cash_return'] >= 8.0 and  # At least 8% cash-on-cash
            opportunity['monthly_cashflow'] >= 200  # At least $200/month cashflow
        )

    def assess_appreciation_potential(self, market):
        """Assess property appreciation potential for market"""
        high_growth_markets = ['Austin, TX', 'Denver, CO', 'Nashville, TN', 'Phoenix, AZ']
        if market in high_growth_markets:
            return 'high'
        else:
            return 'moderate'

    def assess_rental_demand(self, market, prop_data):
        """Assess rental demand"""
        # College towns and tech cities have high demand
        high_demand_markets = ['Austin, TX', 'Denver, CO', 'Atlanta, GA']
        if market in high_demand_markets and prop_data['bedrooms'] >= 2:
            return 'high'
        else:
            return 'moderate'

    def assess_management_complexity(self, property_type):
        """Assess property management complexity"""
        if property_type == 'condo':
            return 'low'  # HOA handles exterior
        elif property_type == 'single_family':
            return 'medium'
        else:
            return 'high'

    def assess_financing_difficulty(self, price):
        """Assess how hard it is to get financing"""
        if price <= 100000:
            return 'difficult'  # Hard to finance cheap properties
        elif price <= 300000:
            return 'easy'
        else:
            return 'moderate'


class AirbnbOpportunitySpider(ContentOpportunitySpider):
    """
    Airbnb short-term rental opportunity spider
    Finds profitable short-term rental markets and properties
    """

    name = 'airbnb_opportunity'
    allowed_domains = ['airbnb.com', 'airdna.co', 'mashvisor.com']

    vacation_markets = [
        'Orlando, FL', 'Miami, FL', 'Las Vegas, NV', 'San Diego, CA',
        'Charleston, SC', 'Savannah, GA', 'Austin, TX', 'Nashville, TN',
        'Denver, CO', 'Gatlinburg, TN', 'Myrtle Beach, SC', 'Key West, FL'
    ]

    def start_requests(self):
        """Generate requests for Airbnb market research"""
        for market in self.vacation_markets:
            # Airbnb search for market analysis
            city_encoded = market.replace(' ', '%20').replace(',', '%2C')
            url = f"https://www.airbnb.com/s/{city_encoded}/homes"

            yield scrapy.Request(
                url=url,
                callback=self.parse_airbnb_market,
                meta={
                    'market': market,
                    'opportunity_type': 'airbnb_rental'
                }
            )

    def parse_airbnb_market(self, response):
        """Parse Airbnb for short-term rental opportunities"""
        # For demo, create sample Airbnb opportunities
        market = response.meta['market']

        sample_properties = [
            {
                'nightly_rate': 120, 'occupancy_rate': 70, 'bedrooms': 2,
                'property_type': 'condo', 'purchase_price': 180000
            },
            {
                'nightly_rate': 200, 'occupancy_rate': 85, 'bedrooms': 3,
                'property_type': 'house', 'purchase_price': 250000
            },
            {
                'nightly_rate': 80, 'occupancy_rate': 60, 'bedrooms': 1,
                'property_type': 'studio', 'purchase_price': 120000
            }
        ]

        for prop in sample_properties:
            opportunity = self.create_airbnb_opportunity(prop, market)
            if opportunity and self.is_good_airbnb_investment(opportunity):
                intelligence = self.process_item(opportunity, response)
                if intelligence:
                    yield intelligence

    def create_airbnb_opportunity(self, prop_data, market):
        """Create Airbnb opportunity"""
        try:
            # Calculate Airbnb metrics
            monthly_revenue = self.calculate_airbnb_revenue(prop_data)
            monthly_expenses = self.calculate_airbnb_expenses(prop_data)
            net_income = monthly_revenue - monthly_expenses

            return {
                'id': f"airbnb_{hash(str(prop_data) + market)}",
                'market': market,
                'property_type': prop_data['property_type'],
                'bedrooms': prop_data['bedrooms'],
                'nightly_rate': prop_data['nightly_rate'],
                'occupancy_rate': prop_data['occupancy_rate'],
                'purchase_price': prop_data['purchase_price'],
                'source': 'airbnb_analysis',
                'opportunity_type': 'airbnb_investment',
                'monthly_revenue': monthly_revenue,
                'monthly_expenses': monthly_expenses,
                'monthly_net_income': net_income,
                'annual_net_income': net_income * 12,
                'cap_rate': round((net_income * 12) / prop_data['purchase_price'] * 100, 2),
                'initial_investment': self.calculate_airbnb_initial_investment(prop_data['purchase_price']),
                'furnishing_cost': self.estimate_furnishing_cost(prop_data),
                'management_intensity': self.assess_airbnb_management_intensity(market),
                'seasonality_risk': self.assess_seasonality_risk(market),
                'regulation_risk': self.assess_regulation_risk(market),
                'competition_level': self.assess_airbnb_competition(market)
            }

        except Exception as e:
            self.logger.error(f"Error creating Airbnb opportunity: {e}")
            return None

    def calculate_airbnb_revenue(self, prop_data):
        """Calculate monthly Airbnb revenue"""
        nights_per_month = 30 * (prop_data['occupancy_rate'] / 100)
        return prop_data['nightly_rate'] * nights_per_month

    def calculate_airbnb_expenses(self, prop_data):
        """Calculate monthly Airbnb expenses"""
        # Mortgage (75% financing at 7%)
        loan_amount = prop_data['purchase_price'] * 0.75
        monthly_mortgage = loan_amount * 0.00665

        # Other expenses
        property_tax_insurance = prop_data['purchase_price'] * 0.015 / 12  # 1.5% annually
        utilities = 150  # Average utilities
        cleaning = prop_data['nightly_rate'] * 0.15 * 8  # 15% cleaning fee, 8 bookings/month
        maintenance = prop_data['purchase_price'] * 0.02 / 12  # 2% annually
        airbnb_fees = self.calculate_airbnb_revenue(prop_data) * 0.15  # 15% platform fees

        return monthly_mortgage + property_tax_insurance + utilities + cleaning + maintenance + airbnb_fees

    def calculate_airbnb_initial_investment(self, price):
        """Calculate initial investment for Airbnb"""
        down_payment = price * 0.25
        closing_costs = price * 0.03
        furnishing = self.estimate_furnishing_cost({'purchase_price': price})
        initial_marketing = 2000

        return down_payment + closing_costs + furnishing + initial_marketing

    def estimate_furnishing_cost(self, prop_data):
        """Estimate cost to furnish Airbnb"""
        base_cost = 15000  # Base furnishing
        per_bedroom = 5000  # Additional per bedroom
        return base_cost + (prop_data['bedrooms'] * per_bedroom)

    def is_good_airbnb_investment(self, opportunity):
        """Determine if Airbnb is a good investment"""
        return (
            opportunity['cap_rate'] >= 8.0 and  # At least 8% cap rate
            opportunity['monthly_net_income'] >= 500 and  # At least $500/month
            opportunity['occupancy_rate'] >= 60  # At least 60% occupancy
        )

    def assess_airbnb_management_intensity(self, market):
        """Assess management intensity required"""
        tourist_heavy = ['Orlando, FL', 'Miami, FL', 'Las Vegas, NV']
        if market in tourist_heavy:
            return 'high'  # Lots of turnover
        else:
            return 'moderate'

    def assess_seasonality_risk(self, market):
        """Assess seasonality risk"""
        seasonal_markets = ['Myrtle Beach, SC', 'Key West, FL', 'Gatlinburg, TN']
        if market in seasonal_markets:
            return 'high'
        else:
            return 'low'

    def assess_regulation_risk(self, market):
        """Assess risk of Airbnb regulations"""
        high_regulation = ['Miami, FL', 'San Diego, CA', 'Denver, CO']
        if market in high_regulation:
            return 'high'
        else:
            return 'moderate'

    def assess_airbnb_competition(self, market):
        """Assess competition level"""
        saturated_markets = ['Orlando, FL', 'Miami, FL', 'Las Vegas, NV']
        if market in saturated_markets:
            return 'high'
        else:
            return 'moderate'


class RealEstateWholesalingSpider(ContentOpportunitySpider):
    """
    Real estate wholesaling opportunity spider
    Finds distressed properties and motivated sellers
    """

    name = 'real_estate_wholesaling'
    allowed_domains = ['foreclosure.com', 'distressedpro.com', 'biggerselects.com']

    target_criteria = [
        'foreclosure', 'pre_foreclosure', 'estate_sale', 'divorce',
        'job_relocation', 'inherited_property', 'distressed_sale'
    ]

    def start_requests(self):
        """Generate requests for wholesaling opportunities"""
        for criteria in self.target_criteria:
            # Search for distressed properties
            url = f"https://www.foreclosure.com/search/{criteria.replace('_', '-')}"

            yield scrapy.Request(
                url=url,
                callback=self.parse_distressed_properties,
                meta={
                    'criteria': criteria,
                    'opportunity_type': 'wholesaling'
                }
            )

    def parse_distressed_properties(self, response):
        """Parse distressed property listings"""
        # For demo, create sample wholesaling opportunities
        criteria = response.meta['criteria']

        sample_deals = [
            {
                'property_value': 150000, 'asking_price': 100000, 'repair_estimate': 25000,
                'motivation_level': 'high', 'time_to_close': 30
            },
            {
                'property_value': 200000, 'asking_price': 140000, 'repair_estimate': 40000,
                'motivation_level': 'medium', 'time_to_close': 45
            },
            {
                'property_value': 120000, 'asking_price': 80000, 'repair_estimate': 15000,
                'motivation_level': 'high', 'time_to_close': 21
            }
        ]

        for deal in sample_deals:
            opportunity = self.create_wholesaling_opportunity(deal, criteria)
            if opportunity and self.is_good_wholesale_deal(opportunity):
                intelligence = self.process_item(opportunity, response)
                if intelligence:
                    yield intelligence

    def create_wholesaling_opportunity(self, deal_data, criteria):
        """Create wholesaling opportunity"""
        try:
            # Calculate wholesaling metrics
            max_offer = self.calculate_max_offer(deal_data)
            potential_assignment_fee = self.calculate_assignment_fee(deal_data)
            profit_margin = potential_assignment_fee / deal_data['asking_price'] * 100

            return {
                'id': f"wholesale_{hash(str(deal_data) + criteria)}",
                'criteria_type': criteria,
                'property_arv': deal_data['property_value'],  # After Repair Value
                'asking_price': deal_data['asking_price'],
                'repair_estimate': deal_data['repair_estimate'],
                'max_offer_price': max_offer,
                'source': 'distressed_property_analysis',
                'opportunity_type': 'wholesaling_deal',
                'potential_assignment_fee': potential_assignment_fee,
                'profit_margin_percent': round(profit_margin, 2),
                'motivation_level': deal_data['motivation_level'],
                'time_to_close': deal_data['time_to_close'],
                'cash_required': 1000,  # Earnest money
                'risk_level': self.assess_wholesale_risk(deal_data),
                'deal_quality': self.assess_deal_quality(deal_data),
                'buyer_appeal': self.assess_buyer_appeal(deal_data),
                'negotiation_leverage': self.assess_negotiation_leverage(deal_data['motivation_level']),
                'exit_strategy_options': self.identify_exit_strategies(deal_data)
            }

        except Exception as e:
            self.logger.error(f"Error creating wholesaling opportunity: {e}")
            return None

    def calculate_max_offer(self, deal_data):
        """Calculate maximum offer price for wholesale deal"""
        # 70% rule minus repairs minus wholesale fee
        arv = deal_data['property_value']
        repairs = deal_data['repair_estimate']
        wholesale_fee = 5000  # Target wholesale fee

        max_offer = (arv * 0.70) - repairs - wholesale_fee
        return max(max_offer, 0)

    def calculate_assignment_fee(self, deal_data):
        """Calculate potential assignment fee"""
        max_offer = self.calculate_max_offer(deal_data)
        asking_price = deal_data['asking_price']

        if max_offer > asking_price:
            return min(max_offer - asking_price, 15000)  # Cap at $15k
        return 0

    def is_good_wholesale_deal(self, opportunity):
        """Determine if wholesaling deal is good"""
        return (
            opportunity['potential_assignment_fee'] >= 3000 and  # At least $3k fee
            opportunity['profit_margin_percent'] >= 3.0 and  # At least 3% margin
            opportunity['motivation_level'] in ['high', 'medium']
        )

    def assess_wholesale_risk(self, deal_data):
        """Assess risk level of wholesale deal"""
        if deal_data['motivation_level'] == 'high' and deal_data['time_to_close'] <= 30:
            return 'low'
        elif deal_data['motivation_level'] == 'medium':
            return 'medium'
        else:
            return 'high'

    def assess_deal_quality(self, deal_data):
        """Assess overall deal quality"""
        value_ratio = deal_data['asking_price'] / deal_data['property_value']

        if value_ratio <= 0.65:
            return 'excellent'
        elif value_ratio <= 0.75:
            return 'good'
        else:
            return 'fair'

    def assess_buyer_appeal(self, deal_data):
        """Assess how appealing deal is to end buyers"""
        total_investment = deal_data['asking_price'] + deal_data['repair_estimate']
        potential_equity = deal_data['property_value'] - total_investment

        if potential_equity >= 30000:
            return 'high'
        elif potential_equity >= 15000:
            return 'medium'
        else:
            return 'low'

    def assess_negotiation_leverage(self, motivation_level):
        """Assess negotiation leverage based on seller motivation"""
        leverage_map = {
            'high': 'strong',
            'medium': 'moderate',
            'low': 'weak'
        }
        return leverage_map.get(motivation_level, 'weak')

    def identify_exit_strategies(self, deal_data):
        """Identify possible exit strategies"""
        strategies = []

        if deal_data['repair_estimate'] < 20000:
            strategies.append('fix_and_flip')

        if deal_data['property_value'] > 100000:
            strategies.append('buy_and_hold')

        strategies.append('wholesale_assignment')

        return strategies
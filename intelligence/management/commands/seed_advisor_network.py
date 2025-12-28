"""
Management command to seed the advisor network with 25+ expert advisors
python manage.py seed_advisor_network
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from intelligence.models.advisor_network import (
    Advisor, AdvisorCategory, AdvisorSpecialization,
    AdvisorVerification, AdvisorRecruitment
)


class Command(BaseCommand):
    help = 'Seeds the advisor network with 25+ expert advisors'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Seeding Advisor Network with 25+ Experts...\n')

        # Create categories
        self.create_categories()

        # Create specializations
        self.create_specializations()

        # Create expert advisors
        self.create_expert_advisors()

        self.stdout.write(self.style.SUCCESS('\n✅ Successfully seeded advisor network!'))

    def create_categories(self):
        """Create advisor categories"""

        categories = [
            ('SPORTS_BETTING', 'Sports Betting Experts', 'Expert sports handicappers and analysts', 'Trophy', '#10B981'),
            ('CRYPTO', 'Crypto Analysts', 'Cryptocurrency and DeFi specialists', 'Bitcoin', '#F59E0B'),
            ('OPTIONS', 'Options Traders', 'Options strategy and volatility experts', 'TrendingUp', '#8B5CF6'),
            ('REAL_ESTATE', 'Real Estate Specialists', 'Property market and REIT analysts', 'Home', '#3B82F6'),
        ]

        for name, display, desc, icon, color in categories:
            AdvisorCategory.objects.get_or_create(
                name=name,
                defaults={
                    'display_name': display,
                    'description': desc,
                    'icon': icon,
                    'color': color
                }
            )

        self.stdout.write('✓ Created advisor categories')

    def create_specializations(self):
        """Create specializations within categories"""

        specializations = {
            'SPORTS_BETTING': [
                ('NBA Line Movement', 'Specializes in NBA betting line movements and sharp money', 3),
                ('NFL Injury Impact', 'Analyzes NFL injury reports impact on spreads', 2),
                ('MLB Pitching Matchups', 'Expert in MLB pitcher vs team analytics', 3),
                ('Soccer Value Betting', 'Identifies value in international soccer markets', 2),
                ('College Basketball', 'Insider knowledge of college basketball', 2),
                ('Live Betting', 'Specializes in in-game betting opportunities', 3),
                ('Player Props', 'Expert in player performance prop bets', 2),
                ('Arbitrage Betting', 'Finds arbitrage opportunities across books', 4),
            ],
            'CRYPTO': [
                ('DeFi Yield Farming', 'Optimizes DeFi yield strategies', 2),
                ('Whale Tracking', 'Monitors large wallet movements', 3),
                ('NFT Markets', 'NFT valuation and trend analysis', 2),
                ('Layer 2 Solutions', 'Expert in L2 scaling solutions', 3),
                ('Stablecoin Arbitrage', 'Stablecoin and cross-chain arbitrage', 2),
                ('Mining Economics', 'Mining profitability and hardware ROI', 3),
                ('Altcoin Analysis', 'Small cap and emerging token analysis', 2),
            ],
            'OPTIONS': [
                ('Volatility Trading', 'IV crush and volatility arbitrage', 4),
                ('Earnings Plays', 'Pre and post earnings strategies', 3),
                ('Greeks Management', 'Delta, gamma, theta optimization', 3),
                ('Credit Spreads', 'Income generation through credit spreads', 2),
                ('Weekly Options', 'Short-term weekly options strategies', 2),
            ],
            'REAL_ESTATE': [
                ('Market Timing', 'Real estate cycle and timing analysis', 3),
                ('REITs Analysis', 'REIT valuation and selection', 2),
                ('Commercial Property', 'Commercial real estate investment', 4),
                ('Rental Income', 'Rental property cash flow optimization', 2),
                ('Crowdfunding', 'Real estate crowdfunding platforms', 2),
            ]
        }

        for category_name, specs in specializations.items():
            try:
                category = AdvisorCategory.objects.get(name=category_name)
                for name, desc, years in specs:
                    AdvisorSpecialization.objects.get_or_create(
                        category=category,
                        name=name,
                        defaults={
                            'description': desc,
                            'required_experience_years': years
                        }
                    )
            except AdvisorCategory.DoesNotExist:
                pass

        self.stdout.write('✓ Created specializations')

    def create_expert_advisors(self):
        """Create 25+ expert advisors with realistic profiles"""

        # Sports Betting Experts (8)
        sports_advisors = [
            {
                'name': 'Marcus "The Line" Johnson',
                'title': 'NBA Line Movement Specialist',
                'bio': '15+ years tracking NBA sharp money. Former oddsmaker at major Vegas sportsbook.',
                'expertise': ['NBA Line Movement', 'Sharp Money Tracking', 'Live Betting'],
                'success_rate': 0.73,
                'roi': 12.4,
                'decisions': 847,
                'tier': 'PLATINUM'
            },
            {
                'name': 'Sarah Mitchell',
                'title': 'NFL Injury Impact Analyst',
                'bio': 'Former NFL team analyst. Specializes in injury report analysis and line value.',
                'expertise': ['NFL Injury Impact', 'Player Props', 'Team Totals'],
                'success_rate': 0.68,
                'roi': 8.7,
                'decisions': 523,
                'tier': 'GOLD'
            },
            {
                'name': 'Roberto Silva',
                'title': 'Soccer Value Betting Expert',
                'bio': 'European soccer specialist. Focus on EPL, La Liga, and Champions League.',
                'expertise': ['Soccer Value Betting', 'Live Betting', 'Asian Handicaps'],
                'success_rate': 0.71,
                'roi': 9.3,
                'decisions': 412,
                'tier': 'GOLD'
            },
            {
                'name': 'Tommy Chen',
                'title': 'MLB Sabermetrics Analyst',
                'bio': 'MIT statistics graduate. Developer of proprietary MLB prediction models.',
                'expertise': ['MLB Pitching Matchups', 'Run Line Betting', 'Totals'],
                'success_rate': 0.69,
                'roi': 7.8,
                'decisions': 389,
                'tier': 'GOLD'
            },
            {
                'name': 'Mike "Professor" Williams',
                'title': 'College Basketball Insider',
                'bio': '20+ years covering college hoops. Network of coaches and insiders.',
                'expertise': ['College Basketball', 'Tournament Betting', 'Team Totals'],
                'success_rate': 0.72,
                'roi': 10.2,
                'decisions': 634,
                'tier': 'PLATINUM'
            },
            {
                'name': 'Alexandra Pierce',
                'title': 'Tennis Live Betting Specialist',
                'bio': 'Former WTA player. Expert in momentum shifts and live value.',
                'expertise': ['Tennis', 'Live Betting', 'Player Matchups'],
                'success_rate': 0.70,
                'roi': 11.1,
                'decisions': 298,
                'tier': 'GOLD'
            },
            {
                'name': 'James "Action" Roberts',
                'title': 'Player Props Expert',
                'bio': 'Data scientist specializing in player performance modeling.',
                'expertise': ['Player Props', 'NBA', 'NFL'],
                'success_rate': 0.74,
                'roi': 13.8,
                'decisions': 892,
                'tier': 'PLATINUM'
            },
            {
                'name': 'David Kim',
                'title': 'Arbitrage Betting Specialist',
                'bio': 'Automated systems for finding arbitrage across 50+ sportsbooks.',
                'expertise': ['Arbitrage Betting', 'Middle Opportunities', 'Line Shopping'],
                'success_rate': 0.96,
                'roi': 4.2,
                'decisions': 1247,
                'tier': 'PLATINUM'
            }
        ]

        # Crypto Analysts (7)
        crypto_advisors = [
            {
                'name': 'Ethereum Max',
                'title': 'DeFi Yield Strategist',
                'bio': 'Early DeFi adopter. $10M+ TVL managed across protocols.',
                'expertise': ['DeFi Yield Farming', 'Liquidity Provision', 'Impermanent Loss'],
                'success_rate': 0.71,
                'roi': 47.3,
                'decisions': 234,
                'tier': 'GOLD'
            },
            {
                'name': 'CryptoWhale',
                'title': 'Whale Movement Tracker',
                'bio': 'On-chain analyst tracking $100M+ wallet movements.',
                'expertise': ['Whale Tracking', 'On-chain Analysis', 'Exchange Flows'],
                'success_rate': 0.68,
                'roi': 82.4,
                'decisions': 167,
                'tier': 'GOLD'
            },
            {
                'name': 'NFT_Sage',
                'title': 'NFT Market Analyst',
                'bio': 'Early CryptoPunks holder. Expert in NFT valuation.',
                'expertise': ['NFT Markets', 'Metaverse Assets', 'Gaming Tokens'],
                'success_rate': 0.64,
                'roi': 124.7,
                'decisions': 89,
                'tier': 'SILVER'
            },
            {
                'name': 'Layer2Lord',
                'title': 'L2 Solutions Expert',
                'bio': 'Polygon and Arbitrum specialist. Focus on scaling opportunities.',
                'expertise': ['Layer 2 Solutions', 'Bridge Arbitrage', 'Gas Optimization'],
                'success_rate': 0.72,
                'roi': 38.9,
                'decisions': 198,
                'tier': 'GOLD'
            },
            {
                'name': 'StableMaster',
                'title': 'Stablecoin Arbitrage Pro',
                'bio': 'Algorithmic trader exploiting stablecoin inefficiencies.',
                'expertise': ['Stablecoin Arbitrage', 'Cross-chain Arb', 'Yield Optimization'],
                'success_rate': 0.89,
                'roi': 12.4,
                'decisions': 523,
                'tier': 'PLATINUM'
            },
            {
                'name': 'HashPower',
                'title': 'Mining Economics Expert',
                'bio': 'Industrial miner with 50MW+ operations experience.',
                'expertise': ['Mining Economics', 'Hardware ROI', 'Energy Markets'],
                'success_rate': 0.67,
                'roi': 28.3,
                'decisions': 134,
                'tier': 'SILVER'
            },
            {
                'name': 'AltcoinAlpha',
                'title': 'Small Cap Specialist',
                'bio': 'Early investor in 10+ unicorn projects. Focus on fundamentals.',
                'expertise': ['Altcoin Analysis', 'Token Economics', 'Team Assessment'],
                'success_rate': 0.58,
                'roi': 234.8,
                'decisions': 76,
                'tier': 'SILVER'
            }
        ]

        # Options Traders (5)
        options_advisors = [
            {
                'name': 'Dr. Volatility',
                'title': 'IV Crush Specialist',
                'bio': 'Former market maker. Expert in volatility arbitrage strategies.',
                'expertise': ['Volatility Trading', 'IV Crush', 'VIX Strategies'],
                'success_rate': 0.76,
                'roi': 34.2,
                'decisions': 423,
                'tier': 'PLATINUM'
            },
            {
                'name': 'EarningsEdge',
                'title': 'Earnings Play Expert',
                'bio': '10+ years trading earnings. Proprietary expected move models.',
                'expertise': ['Earnings Plays', 'Straddles', 'Binary Events'],
                'success_rate': 0.72,
                'roi': 28.7,
                'decisions': 312,
                'tier': 'GOLD'
            },
            {
                'name': 'GreekGod',
                'title': 'Greeks Management Pro',
                'bio': 'Quantitative trader. Focus on delta-neutral strategies.',
                'expertise': ['Greeks Management', 'Hedging', 'Portfolio Greeks'],
                'success_rate': 0.74,
                'roi': 22.3,
                'decisions': 567,
                'tier': 'PLATINUM'
            },
            {
                'name': 'ThetaGang',
                'title': 'Credit Spread Strategist',
                'bio': 'Consistent income through credit spreads and iron condors.',
                'expertise': ['Credit Spreads', 'Iron Condors', 'Theta Decay'],
                'success_rate': 0.81,
                'roi': 18.4,
                'decisions': 892,
                'tier': 'PLATINUM'
            },
            {
                'name': '0DTE_Master',
                'title': 'Weekly Options Scalper',
                'bio': 'High-frequency 0DTE SPX trader. 1000+ trades per year.',
                'expertise': ['Weekly Options', '0DTE', 'Scalping'],
                'success_rate': 0.67,
                'roi': 42.8,
                'decisions': 1823,
                'tier': 'GOLD'
            }
        ]

        # Real Estate Specialists (5)
        real_estate_advisors = [
            {
                'name': 'Austin Insider',
                'title': 'Austin Market Timing Expert',
                'bio': '15+ years in Austin real estate. $100M+ in transactions.',
                'expertise': ['Market Timing', 'Austin Market', 'Tech Migration'],
                'success_rate': 0.78,
                'roi': 24.3,
                'decisions': 143,
                'tier': 'PLATINUM'
            },
            {
                'name': 'REIT_Research',
                'title': 'REITs Analyst',
                'bio': 'Former REIT portfolio manager. Focus on dividend growth.',
                'expertise': ['REITs Analysis', 'Dividend Investing', 'Sector Rotation'],
                'success_rate': 0.71,
                'roi': 14.7,
                'decisions': 234,
                'tier': 'GOLD'
            },
            {
                'name': 'CommercialPro',
                'title': 'Commercial Property Specialist',
                'bio': 'Commercial broker with $500M+ in closed deals.',
                'expertise': ['Commercial Property', 'Cap Rate Analysis', 'Tenant Quality'],
                'success_rate': 0.73,
                'roi': 18.9,
                'decisions': 89,
                'tier': 'GOLD'
            },
            {
                'name': 'CashflowKing',
                'title': 'Rental Income Optimizer',
                'bio': 'Portfolio of 50+ rental properties. FIRE movement leader.',
                'expertise': ['Rental Income', 'Property Management', 'Tax Optimization'],
                'success_rate': 0.82,
                'roi': 21.4,
                'decisions': 267,
                'tier': 'PLATINUM'
            },
            {
                'name': 'CrowdFunder',
                'title': 'RE Crowdfunding Expert',
                'bio': 'Early adopter of RE crowdfunding. $5M+ invested across platforms.',
                'expertise': ['Crowdfunding', 'Platform Analysis', 'Deal Structure'],
                'success_rate': 0.69,
                'roi': 16.8,
                'decisions': 123,
                'tier': 'SILVER'
            }
        ]

        # Combine all advisors
        all_advisor_data = [
            ('SPORTS_BETTING', sports_advisors),
            ('CRYPTO', crypto_advisors),
            ('OPTIONS', options_advisors),
            ('REAL_ESTATE', real_estate_advisors)
        ]

        advisor_count = 0
        for category_name, advisors_list in all_advisor_data:
            try:
                category = AdvisorCategory.objects.get(name=category_name)

                for advisor_data in advisors_list:
                    # Create advisor
                    advisor = Advisor.objects.create(
                        external_id=f"ADV_{advisor_count + 1001}",
                        name=advisor_data['name'],
                        title=advisor_data['title'],
                        bio=advisor_data['bio'],
                        category=category,
                        expertise_tags=advisor_data['expertise'],
                        trust_level='VERIFIED' if advisor_data['tier'] in ['PLATINUM', 'GOLD'] else 'HIGH',
                        tier=advisor_data['tier'],
                        verification_date=timezone.now() - timedelta(days=random.randint(30, 365)),
                        reputation_score=round(4.0 + (advisor_data['success_rate'] - 0.5) * 2, 1),
                        success_rate=advisor_data['success_rate'],
                        total_decisions=advisor_data['decisions'],
                        successful_decisions=int(advisor_data['decisions'] * advisor_data['success_rate']),
                        roi_percentage=advisor_data['roi'],
                        is_active=True,
                        is_online=random.choice([True, True, False]),  # 66% online
                        base_fee=random.randint(50, 500),
                        performance_fee_percentage=random.randint(10, 30)
                    )

                    # Add domain performance
                    domains = ['SPORTS', 'CRYPTO', 'OPTIONS', 'STOCKS', 'REAL_ESTATE']
                    advisor.domain_performance = {
                        domain: {
                            'total': random.randint(20, 200),
                            'successful': random.randint(15, 150),
                            'rate': round(random.uniform(0.60, 0.85), 4)
                        }
                        for domain in random.sample(domains, random.randint(1, 3))
                    }
                    advisor.save()

                    # Add verification
                    AdvisorVerification.objects.create(
                        advisor=advisor,
                        verification_type='TRACK_RECORD',
                        platform=random.choice(['Action Network', 'Tipstrr', 'BetStamp', 'Verified Platform']),
                        verified_roi=advisor_data['roi'],
                        verified_win_rate=advisor_data['success_rate'],
                        verified_picks_count=advisor_data['decisions'],
                        time_period_days=random.randint(180, 730),
                        is_valid=True
                    )

                    advisor_count += 1

            except AdvisorCategory.DoesNotExist:
                self.stdout.write(f'Category {category_name} not found')

        self.stdout.write(f'✓ Created {advisor_count} expert advisors')

        # Add some advisors to recruitment pipeline
        recruitment_candidates = [
            ('MMA_Sharp', 'SPORTS_BETTING', ['MMA/UFC Betting', 'Fight Analytics']),
            ('CryptoQuant', 'CRYPTO', ['Quantitative Analysis', 'Market Making']),
            ('Condor_King', 'OPTIONS', ['Iron Condors', 'Risk Management']),
            ('Miami_RE', 'REAL_ESTATE', ['Miami Market', 'Luxury Properties']),
        ]

        for name, category_name, specs in recruitment_candidates:
            try:
                category = AdvisorCategory.objects.get(name=category_name)
                AdvisorRecruitment.objects.create(
                    name=name,
                    category=category,
                    specializations=specs,
                    status='EVALUATING',
                    source='Industry Referral',
                    verified_track_record={
                        'platform': 'Various',
                        'win_rate': round(random.uniform(0.60, 0.75), 2),
                        'sample_size': random.randint(50, 200)
                    }
                )
            except AdvisorCategory.DoesNotExist:
                pass

        self.stdout.write('✓ Added candidates to recruitment pipeline')
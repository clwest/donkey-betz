"""
Management command to deploy spider army
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
import redis
from ai_core.spiders.tasks import (
    deploy_full_army,
    quick_deploy,
    activate_spider_wave,
    clean_inactive_spiders
)
import json

class Command(BaseCommand):
    help = 'Deploy the spider army (1,770 spiders)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Deploy test batch (10 spiders)'
        )
        parser.add_argument(
            '--quick',
            type=int,
            help='Quick deploy N spiders'
        )
        parser.add_argument(
            '--wave',
            type=str,
            help='Deploy specific wave: income, financial, tech, content, social, realestate, specialized'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean inactive spiders first'
        )

    def handle(self, *args, **options):
        r = redis.Redis(host='localhost', port=6379, db=0)

        # Clean inactive spiders if requested
        if options['clean']:
            self.stdout.write('Cleaning inactive spiders...')
            result = clean_inactive_spiders.apply_async(queue='spider_queue')
            clean_result = result.get(timeout=30)
            self.stdout.write(
                self.style.SUCCESS(f"Removed {clean_result['removed']} inactive spiders")
            )

        # Check current status
        active = r.scard('active_spiders')
        self.stdout.write(f"Current active spiders: {active}")

        # Deploy based on options
        if options['test']:
            self.stdout.write('Deploying test batch (10 spiders)...')
            result = deploy_full_army.apply_async(
                args=[True],  # test_mode = True
                queue='spider_queue'
            )

        elif options['quick']:
            count = options['quick']
            self.stdout.write(f'Quick deploying {count} spiders...')
            result = quick_deploy.apply_async(
                args=[count],
                queue='spider_queue'
            )

        elif options['wave']:
            wave_type = options['wave']
            waves = {
                'income': {
                    'toptal': 50,
                    'upwork': 50,
                    'freelancer': 40,
                    'fiverr': 40,
                    'guru': 30,
                    'peopleperhour': 30,
                    'remoteok': 30,
                    'flexjobs': 30
                },
                'financial': {
                    'bloomberg': 30,
                    'reuters': 30,
                    'coinbase': 25,
                    'binance': 25,
                    'tradingview': 25,
                    'seekingalpha': 20,
                    'yahoo_finance': 20,
                    'coingecko': 25
                },
                'tech': {
                    'github': 40,
                    'stackoverflow': 30,
                    'kaggle': 25,
                    'huggingface': 25,
                    'producthunt': 20,
                    'hackernews': 20,
                    'devto': 20,
                    'medium': 20
                },
                'content': {
                    'youtube': 40,
                    'amazon': 50,
                    'etsy': 40,
                    'shopify': 40,
                    'gumroad': 30,
                    'patreon': 30,
                    'udemy': 30,
                    'teachable': 30
                }
            }

            if wave_type not in waves:
                self.stdout.write(
                    self.style.ERROR(f"Unknown wave: {wave_type}. Choose from: {', '.join(waves.keys())}")
                )
                return

            self.stdout.write(f'Deploying {wave_type} wave...')
            result = activate_spider_wave.apply_async(
                args=[waves[wave_type]],
                queue='spider_queue'
            )

        else:
            # Full deployment
            self.stdout.write(self.style.WARNING('Deploying FULL spider army (1,770 spiders)...'))
            self.stdout.write('This will take several minutes. Starting with Wave 1 (300 spiders)...')
            result = deploy_full_army.apply_async(
                args=[False],  # test_mode = False
                queue='spider_queue'
            )

        # Wait for result
        try:
            deployment = result.get(timeout=120)

            if 'error' in deployment:
                self.stdout.write(
                    self.style.ERROR(f"Deployment failed: {deployment['error']}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully deployed {deployment['total_deployed']} spiders!"
                    )
                )

                # Show current status
                active = r.scard('active_spiders')
                self.stdout.write(f"Total active spiders: {active}")

                # Show sample spider data
                sample_spiders = list(r.smembers('active_spiders'))[:5]
                if sample_spiders:
                    self.stdout.write("\nSample deployed spiders:")
                    for spider_id in sample_spiders:
                        spider_id = spider_id.decode() if isinstance(spider_id, bytes) else spider_id
                        data = r.hgetall(f'spider:{spider_id}')
                        if data:
                            platform = data.get(b'platform', b'unknown').decode()
                            self.stdout.write(f"  - {spider_id} (platform: {platform})")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Deployment failed with error: {str(e)}")
            )
            self.stdout.write("Make sure Celery workers are running with:")
            self.stdout.write("  celery -A core worker -l info -Q spider_queue")
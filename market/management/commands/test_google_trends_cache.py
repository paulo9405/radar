"""
Management command to test Google Trends caching system.

Usage:
    python manage.py test_google_trends_cache "Notebook Dell"
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from market.services import google_trends
from market.models import GoogleTrendsCache, GoogleTrendsCooldown


class Command(BaseCommand):
    help = 'Test Google Trends caching system with a product query'

    def add_arguments(self, parser):
        parser.add_argument(
            'query',
            type=str,
            help='Product name to search for'
        )
        parser.add_argument(
            '--force-fetch',
            action='store_true',
            help='Clear cache and force fresh fetch'
        )

    def handle(self, *args, **options):
        query = options['query']
        force_fetch = options['force_fetch']

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('GOOGLE TRENDS CACHE TEST'))
        self.stdout.write('=' * 70)
        self.stdout.write('')

        # Show initial state
        self.stdout.write(self.style.WARNING('1. Initial State'))
        self.stdout.write('-' * 70)

        # Check cooldown
        cooldown_status = GoogleTrendsCooldown.get_status()
        if cooldown_status['active']:
            self.stdout.write(self.style.ERROR(f'⏸️  Cooldown ACTIVE ({cooldown_status["remaining_minutes"]} min remaining)'))
            self.stdout.write(f'   Reason: {cooldown_status["reason"]}')
        else:
            self.stdout.write(self.style.SUCCESS('✅ Cooldown inactive'))

        # Check cache
        normalized = GoogleTrendsCache.normalize_query(query)
        cached = GoogleTrendsCache.get_cached(query)

        self.stdout.write(f'Query: "{query}"')
        self.stdout.write(f'Normalized: "{normalized}"')

        if cached:
            age_minutes = (timezone.now() - cached.fetched_at).seconds // 60
            remaining_hours = (cached.expires_at - timezone.now()).seconds // 3600
            self.stdout.write(self.style.SUCCESS('💾 Cache entry exists'))
            self.stdout.write(f'   Age: {age_minutes} minutes')
            self.stdout.write(f'   Expires in: {remaining_hours} hours')
            self.stdout.write(f'   Fresh: {cached.is_fresh()}')
        else:
            self.stdout.write(self.style.WARNING('💭 No cache entry found'))

        self.stdout.write('')

        # Force clear cache if requested
        if force_fetch and cached:
            self.stdout.write(self.style.WARNING('Clearing cache (--force-fetch)...'))
            cached.delete()
            self.stdout.write(self.style.SUCCESS('✅ Cache cleared'))
            self.stdout.write('')

        # Test 1: First fetch
        self.stdout.write(self.style.WARNING('2. First Fetch'))
        self.stdout.write('-' * 70)

        trends_data_1 = google_trends.get_trends_data(query)

        self.stdout.write('')
        self.stdout.write('Result:')
        self.stdout.write(f'  Source: {trends_data_1.get("source")}')
        self.stdout.write(f'  Provider: {trends_data_1.get("provider")}')
        self.stdout.write(f'  Trend Direction: {trends_data_1.get("trend_direction")}')
        self.stdout.write(f'  Growth 30d: {trends_data_1.get("growth_30d")}%')
        self.stdout.write(f'  Momentum: {trends_data_1.get("momentum_score")}/10')
        self.stdout.write('')

        # Test 2: Second fetch (should use cache)
        self.stdout.write(self.style.WARNING('3. Second Fetch (Testing Cache)'))
        self.stdout.write('-' * 70)

        trends_data_2 = google_trends.get_trends_data(query)

        self.stdout.write('')
        self.stdout.write('Result:')
        self.stdout.write(f'  Source: {trends_data_2.get("source")}')
        self.stdout.write(f'  Provider: {trends_data_2.get("provider")}')

        # Verify caching worked
        if trends_data_1 == trends_data_2:
            self.stdout.write(self.style.SUCCESS('✅ Cache working - identical results'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Results differ - cache may not be working'))

        self.stdout.write('')

        # Show final cache state
        self.stdout.write(self.style.WARNING('4. Final Cache State'))
        self.stdout.write('-' * 70)

        cached_after = GoogleTrendsCache.get_cached(query)
        if cached_after:
            age_minutes = (timezone.now() - cached_after.fetched_at).seconds // 60
            self.stdout.write(self.style.SUCCESS('💾 Cache entry exists'))
            self.stdout.write(f'   Age: {age_minutes} minutes')
            self.stdout.write(f'   Created: {cached_after.fetched_at.strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write(f'   Expires: {cached_after.expires_at.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            self.stdout.write(self.style.WARNING('💭 No cache entry'))

        # Show statistics
        total_cache = GoogleTrendsCache.objects.count()
        self.stdout.write(f'\nTotal cache entries: {total_cache}')

        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('TEST COMPLETE'))
        self.stdout.write('=' * 70)

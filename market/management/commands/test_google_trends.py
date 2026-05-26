"""
Management command to test Google Trends integration.

Usage:
    python manage.py test_google_trends "iPhone 15"
"""
from django.core.management.base import BaseCommand
from market.providers.google_trends import GoogleTrendsProvider
from market.services import google_trends


class Command(BaseCommand):
    help = 'Test Google Trends integration with a product query'

    def add_arguments(self, parser):
        parser.add_argument(
            'query',
            type=str,
            help='Product name to search for'
        )

    def handle(self, *args, **options):
        query = options['query']

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('GOOGLE TRENDS INTEGRATION TEST'))
        self.stdout.write('=' * 70)
        self.stdout.write('')

        # Test 1: Provider Status
        self.stdout.write(self.style.WARNING('1. Testing Provider Status'))
        self.stdout.write('-' * 70)

        provider = GoogleTrendsProvider()
        is_available = provider.is_available()
        status = provider.get_status()

        self.stdout.write(f'Provider Available: {is_available}')
        self.stdout.write(f'Provider Status: {status}')
        self.stdout.write('')

        if not is_available:
            self.stdout.write(self.style.ERROR('❌ Provider is NOT available'))
            self.stdout.write('Reason: pytrends client failed to initialize')
            return

        # Test 2: Direct Provider Call
        self.stdout.write(self.style.WARNING('2. Testing Direct Provider Call'))
        self.stdout.write('-' * 70)
        self.stdout.write(f'Query: "{query}"')
        self.stdout.write('')

        signals = provider.get_trend_signals(query)

        if signals:
            self.stdout.write(self.style.SUCCESS('✅ REAL GOOGLE TRENDS DATA RECEIVED'))
            self.stdout.write('')
            self.stdout.write('Trend Signals:')
            self.stdout.write(f'  Provider: {signals.get("provider")}')
            self.stdout.write(f'  Trend Direction: {signals.get("trend_direction")}')
            self.stdout.write(f'  Trend Strength: {signals.get("trend_strength"):.1f}/10')
            self.stdout.write(f'  Growth 30d: {signals.get("growth_30d"):.1f}%')
            self.stdout.write(f'  Growth 90d: {signals.get("growth_90d"):.1f}%')
            self.stdout.write(f'  Momentum Score: {signals.get("momentum_score"):.1f}/10')
            self.stdout.write(f'  Stability Score: {signals.get("stability_score"):.1f}/10')
            self.stdout.write(f'  Volatility: {signals.get("volatility"):.1f}%')
            self.stdout.write(f'  Current Interest: {signals.get("current_interest")}/100')
            self.stdout.write(f'  Peak Interest: {signals.get("peak_interest")}/100')
            self.stdout.write(f'  Average Interest: {signals.get("average_interest"):.1f}')
            self.stdout.write(f'  Seasonality: {signals.get("seasonality_detected")}')
            self.stdout.write(f'  Confidence: {signals.get("confidence"):.0%}')
            self.stdout.write(f'  Data Points: {signals.get("data_points")}')
            self.stdout.write('')

            # Related Queries
            related = signals.get('related_queries', [])
            if related:
                self.stdout.write('Related Queries:')
                for q in related[:5]:
                    self.stdout.write(f'  - {q}')
                self.stdout.write('')
            else:
                self.stdout.write(self.style.WARNING('  No related queries found'))
                self.stdout.write('')

            # Top Regions
            regions = signals.get('top_regions', [])
            if regions:
                self.stdout.write('Top Regions:')
                for r in regions[:5]:
                    self.stdout.write(f'  - {r["region"]}: {r["interest"]}/100')
                self.stdout.write('')
            else:
                self.stdout.write(self.style.WARNING('  No regional data found'))
                self.stdout.write('')

            # Raw Interest Over Time (sample)
            raw_data = signals.get('raw_data', {})
            interest_values = raw_data.get('interest_over_time', [])
            if interest_values:
                self.stdout.write('Interest Over Time (last 10 values):')
                sample = interest_values[-10:] if len(interest_values) > 10 else interest_values
                self.stdout.write(f'  {sample}')
                self.stdout.write('')
            else:
                self.stdout.write(self.style.WARNING('  No interest over time data'))
                self.stdout.write('')

        else:
            self.stdout.write(self.style.ERROR('❌ NO DATA FROM GOOGLE TRENDS'))
            self.stdout.write('Provider returned None (likely rate-limited or error)')
            self.stdout.write('')

        # Test 3: Service Layer Call (with fallback)
        self.stdout.write(self.style.WARNING('3. Testing Service Layer (with fallback)'))
        self.stdout.write('-' * 70)

        trends_data = google_trends.get_trends_data(query)

        source = trends_data.get('source', 'unknown')
        provider_name = trends_data.get('provider', 'unknown')

        if source == 'google_trends':
            self.stdout.write(self.style.SUCCESS('✅ Using REAL Google Trends data'))
        elif source == 'mock_fallback':
            self.stdout.write(self.style.ERROR('⚠️  FALLBACK: Using MOCK data'))
            self.stdout.write('Reason: Provider unavailable or rate-limited')
        else:
            self.stdout.write(self.style.WARNING(f'❓ Unknown source: {source}'))

        self.stdout.write('')
        self.stdout.write('Service Layer Response:')
        self.stdout.write(f'  Source: {source}')
        self.stdout.write(f'  Provider: {provider_name}')
        self.stdout.write(f'  Trend Direction: {trends_data.get("trend_direction")}')
        self.stdout.write(f'  Growth 30d: {trends_data.get("growth_30d")}%')
        self.stdout.write(f'  Growth 90d: {trends_data.get("growth_90d")}%')
        self.stdout.write(f'  Momentum Score: {trends_data.get("momentum_score")}/10')
        self.stdout.write(f'  Current Interest: {trends_data.get("current_interest")}/100')
        self.stdout.write('')

        # Summary
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('TEST COMPLETE'))
        self.stdout.write('=' * 70)
        self.stdout.write('')

        if signals and source == 'google_trends':
            self.stdout.write(self.style.SUCCESS('✅ VERDICT: Google Trends is working with REAL data!'))
        elif not signals:
            self.stdout.write(self.style.ERROR('❌ VERDICT: Google Trends provider failed (rate limit or error)'))
        elif source == 'mock_fallback':
            self.stdout.write(self.style.WARNING('⚠️  VERDICT: Using mock fallback (provider unavailable)'))
        else:
            self.stdout.write(self.style.WARNING('❓ VERDICT: Unclear - check logs above'))

        self.stdout.write('')

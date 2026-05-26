"""
Management command to clear Google Trends cache.

Usage:
    python manage.py clear_google_trends_cache
    python manage.py clear_google_trends_cache --expired-only
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from market.models import GoogleTrendsCache, GoogleTrendsCooldown


class Command(BaseCommand):
    help = 'Clear Google Trends cache and cooldown state'

    def add_arguments(self, parser):
        parser.add_argument(
            '--expired-only',
            action='store_true',
            help='Only delete expired cache entries'
        )
        parser.add_argument(
            '--clear-cooldown',
            action='store_true',
            help='Also clear cooldown state'
        )

    def handle(self, *args, **options):
        expired_only = options['expired_only']
        clear_cooldown = options['clear_cooldown']

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('CLEAR GOOGLE TRENDS CACHE'))
        self.stdout.write('=' * 70)
        self.stdout.write('')

        # Clear cache
        if expired_only:
            self.stdout.write('Clearing EXPIRED cache entries only...')
            deleted_count = GoogleTrendsCache.clear_expired()
            self.stdout.write(self.style.SUCCESS(f'✅ Deleted {deleted_count} expired cache entries'))
        else:
            self.stdout.write('Clearing ALL cache entries...')
            total_count = GoogleTrendsCache.objects.count()
            GoogleTrendsCache.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✅ Deleted {total_count} cache entries'))

        self.stdout.write('')

        # Show remaining cache
        remaining = GoogleTrendsCache.objects.count()
        if remaining > 0:
            self.stdout.write(f'Remaining cache entries: {remaining}')
            fresh_count = GoogleTrendsCache.objects.filter(expires_at__gt=timezone.now()).count()
            self.stdout.write(f'  - Fresh: {fresh_count}')
            self.stdout.write(f'  - Expired: {remaining - fresh_count}')
        else:
            self.stdout.write('Cache is now empty')

        # Clear cooldown
        if clear_cooldown:
            self.stdout.write('')
            self.stdout.write('Clearing cooldown state...')
            GoogleTrendsCooldown.deactivate()
            self.stdout.write(self.style.SUCCESS('✅ Cooldown cleared'))

        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('DONE'))
        self.stdout.write('=' * 70)

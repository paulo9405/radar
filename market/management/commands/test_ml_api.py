"""
Django management command to test Mercado Livre API requests.

Usage:
    python manage.py test_ml_api
    python manage.py test_ml_api --query "iPhone 15"
    python manage.py test_ml_api --authenticated
"""
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from market.models import MercadoLivreToken


class Command(BaseCommand):
    help = 'Test Mercado Livre API requests with detailed debugging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default='iPhone 15',
            help='Product search query'
        )
        parser.add_argument(
            '--authenticated',
            action='store_true',
            help='Use OAuth token authentication'
        )

    def handle(self, *args, **options):
        query = options['query']
        use_auth = options['authenticated']

        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(self.style.WARNING('MERCADO LIVRE API DEBUGGING'))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))

        # Test 1: Public request (no authentication)
        self.stdout.write(self.style.HTTP_INFO('\n[TEST 1] PUBLIC REQUEST (No Authentication)'))
        self.test_public_request(query)

        # Test 2: Authenticated request (with OAuth token)
        self.stdout.write(self.style.HTTP_INFO('\n[TEST 2] AUTHENTICATED REQUEST (With OAuth Token)'))
        self.test_authenticated_request(query)

        # Test 3: Browser-like headers
        self.stdout.write(self.style.HTTP_INFO('\n[TEST 3] BROWSER-LIKE HEADERS'))
        self.test_browser_headers(query)

        # Test 4: Minimal headers
        self.stdout.write(self.style.HTTP_INFO('\n[TEST 4] MINIMAL HEADERS'))
        self.test_minimal_headers(query)

        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(self.style.WARNING('TESTING COMPLETE'))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))

    def test_public_request(self, query):
        """Test public API request without authentication"""
        url = "https://api.mercadolibre.com/sites/MLB/search"
        params = {'q': query, 'limit': 10}
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'RadarTendencias/1.0'
        }

        self.stdout.write(f"URL: {url}")
        self.stdout.write(f"Params: {params}")
        self.stdout.write(f"Headers: {headers}")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            self.print_response(response)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception: {e}"))

    def test_authenticated_request(self, query):
        """Test authenticated API request with OAuth token"""
        # Get token from database
        token_record = MercadoLivreToken.get_current()

        if not token_record:
            self.stdout.write(self.style.WARNING("No OAuth token found in database"))
            self.stdout.write(self.style.WARNING("Run OAuth flow first: /market/mercadolivre/authorize/"))
            return

        if token_record.is_expired():
            self.stdout.write(self.style.WARNING("Token is expired"))
            self.stdout.write(self.style.WARNING("Token will be refreshed automatically on next OAuth use"))

        url = "https://api.mercadolibre.com/sites/MLB/search"
        params = {'q': query, 'limit': 10}
        headers = {
            'Authorization': f'Bearer {token_record.access_token}',
            'Accept': 'application/json',
            'User-Agent': 'RadarTendencias/1.0'
        }

        self.stdout.write(f"URL: {url}")
        self.stdout.write(f"Params: {params}")
        self.stdout.write(f"Headers: {{")
        self.stdout.write(f"  'Authorization': 'Bearer {token_record.masked_access_token()}',")
        self.stdout.write(f"  'Accept': 'application/json',")
        self.stdout.write(f"  'User-Agent': 'RadarTendencias/1.0'")
        self.stdout.write(f"}}")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            self.print_response(response)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception: {e}"))

    def test_browser_headers(self, query):
        """Test with browser-like headers"""
        url = "https://api.mercadolibre.com/sites/MLB/search"
        params = {'q': query, 'limit': 10}
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.mercadolivre.com.br/',
            'Origin': 'https://www.mercadolivre.com.br'
        }

        self.stdout.write(f"URL: {url}")
        self.stdout.write(f"Params: {params}")
        self.stdout.write(f"Headers: {headers}")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            self.print_response(response)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception: {e}"))

    def test_minimal_headers(self, query):
        """Test with minimal headers"""
        url = "https://api.mercadolibre.com/sites/MLB/search"
        params = {'q': query, 'limit': 10}
        headers = {}  # No custom headers at all

        self.stdout.write(f"URL: {url}")
        self.stdout.write(f"Params: {params}")
        self.stdout.write(f"Headers: {headers} (default requests headers)")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            self.print_response(response)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception: {e}"))

    def print_response(self, response):
        """Print detailed response information"""
        # Status
        status_style = self.style.SUCCESS if response.status_code == 200 else self.style.ERROR
        self.stdout.write(status_style(f"\nStatus Code: {response.status_code}"))

        # Response Headers
        self.stdout.write("\nResponse Headers:")
        for key, value in response.headers.items():
            self.stdout.write(f"  {key}: {value}")

        # Response Body
        self.stdout.write("\nResponse Body:")
        try:
            json_data = response.json()

            # If error, show full response
            if 'error' in json_data or response.status_code != 200:
                self.stdout.write(self.style.ERROR(str(json_data)))
            else:
                # If success, show summary
                results = json_data.get('results', [])
                paging = json_data.get('paging', {})

                self.stdout.write(self.style.SUCCESS(f"✅ Success!"))
                self.stdout.write(f"  Results in response: {len(results)}")
                self.stdout.write(f"  Total results: {paging.get('total', 0)}")
                self.stdout.write(f"  Limit: {paging.get('limit', 0)}")

                if results:
                    self.stdout.write(f"\n  First result:")
                    first = results[0]
                    self.stdout.write(f"    Title: {first.get('title', 'N/A')}")
                    self.stdout.write(f"    Price: R$ {first.get('price', 0):.2f}")
                    self.stdout.write(f"    Available: {first.get('available_quantity', 0)}")
                    self.stdout.write(f"    Sold: {first.get('sold_quantity', 0)}")

        except ValueError:
            # Not JSON
            body_preview = response.text[:500]
            self.stdout.write(f"(Not JSON) {body_preview}")

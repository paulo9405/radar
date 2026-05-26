"""
Mercado Livre data provider.

Integrates with official Mercado Livre API using OAuth.
Falls back to deterministic mock data if API fails or is not authorized.
"""
import hashlib
import requests
from typing import Optional
from django.conf import settings
from . import ml_oauth


def is_configured() -> bool:
    """
    Checks if Mercado Livre API credentials are configured.

    Returns:
        bool: True if credentials are set
    """
    return bool(
        settings.MERCADO_LIVRE_CLIENT_ID and
        settings.MERCADO_LIVRE_CLIENT_SECRET
    )


def is_authorized() -> bool:
    """
    Checks if we have OAuth authorization.

    Returns:
        bool: True if authorized
    """
    return ml_oauth.is_authorized()


def get_marketplace_data(query: str) -> dict:
    """
    Fetches marketplace data for a given product query.

    Mercado Livre search API requires OAuth authentication.
    Uses authenticated request if token is available, otherwise mock data.

    Args:
        query: Product search query

    Returns:
        dict: Marketplace data including:
            - total_listings: Number of active listings
            - avg_price: Average product price
            - price_range: (min_price, max_price)
            - top_sellers: Number of unique sellers
            - avg_rating: Average seller rating (estimated)
            - sold_quantity: Total sold (estimated)
            - competition_level: 'low', 'medium', or 'high'
            - price_war_indicator: Boolean
            - source: 'mercado_livre_api' or 'mock_fallback'
            - error: Error message if fallback (optional)
    """
    print(f"[ML API] Starting marketplace data fetch for: {query}")

    # Mercado Livre requires OAuth authentication for search endpoint
    if is_authorized():
        try:
            print("[ML API] Using authenticated API request (OAuth token available)...")
            api_data = _fetch_with_auth(query)
            if api_data:
                print("[ML API] ✅ Authenticated API request successful!")
                return api_data
        except Exception as e:
            print(f"[ML API] Authenticated API exception: {str(e)}")
    else:
        print("[ML API] ⚠️  No OAuth token - API requires authentication")
        print("[ML API] Authorize at: /market/mercadolivre/authorize/")

    # Fallback to mock data
    error_msg = "OAuth required" if is_configured() else "API not configured"
    print(f"[ML API] ❌ Using mock fallback: {error_msg}")
    return _get_mock_data(query, fallback=True, error=error_msg)


def _fetch_from_public_api(query: str, limit: int = 50) -> Optional[dict]:
    """
    Fetches data from public Mercado Livre API (no authentication required).

    Args:
        query: Search query
        limit: Max results to fetch (default 50)

    Returns:
        dict: Normalized marketplace data or None if failed
    """
    # Public Mercado Livre API search endpoint
    url = "https://api.mercadolibre.com/sites/MLB/search"

    params = {
        'q': query,
        'limit': limit
    }

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'RadarTendencias/1.0'
    }

    # Build full URL for logging
    param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{url}?{param_string}"

    print(f"[ML API] PUBLIC REQUEST")
    print(f"[ML API]   URL: {full_url}")
    print(f"[ML API]   Headers: {headers}")

    try:
        # Make request with timeout
        response = requests.get(url, params=params, headers=headers, timeout=10)

        # Log full response details
        print(f"[ML API] Response Status: {response.status_code}")
        print(f"[ML API] Response Headers: {dict(response.headers)}")

        # Check status
        if response.status_code != 200:
            # Log full failure details
            body_preview = response.text[:500] if response.text else "empty"
            print(f"[ML API] ❌ PUBLIC REQUEST FAILED")
            print(f"[ML API] Status: {response.status_code}")
            print(f"[ML API] Response body: {body_preview}")
            return None

        # Parse JSON
        data = response.json()

        # Log success
        results_count = len(data.get('results', []))
        total_results = data.get('paging', {}).get('total', 0)
        print(f"[ML API] ✅ PUBLIC REQUEST SUCCESS")
        print(f"[ML API] Results: {results_count} items fetched, {total_results} total available")

        # Normalize and return
        return _normalize_api_response(data, query)

    except requests.exceptions.Timeout:
        print("[ML API] ❌ Request timeout (10 seconds)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ML API] ❌ Request error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"[ML API] ❌ Parse error: {e}")
        return None


def _fetch_with_auth(query: str, limit: int = 50) -> Optional[dict]:
    """
    Fetches data from Mercado Livre API with OAuth authentication.

    Args:
        query: Search query
        limit: Max results to fetch (default 50)

    Returns:
        dict: Normalized marketplace data or None if failed
    """
    # Get valid access token
    access_token = ml_oauth.get_valid_token()

    if not access_token:
        print("[ML API] No valid OAuth token available")
        return None

    # Mercado Livre API search endpoint
    url = "https://api.mercadolibre.com/sites/MLB/search"

    params = {
        'q': query,
        'limit': limit
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'RadarTendencias/1.0'
    }

    # Build full URL for logging (without exposing full token)
    param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{url}?{param_string}"

    print(f"[ML API] AUTHENTICATED REQUEST")
    print(f"[ML API]   URL: {full_url}")
    print(f"[ML API]   Authorization: Bearer {access_token[:10]}...")

    try:
        # Make request with timeout
        response = requests.get(url, params=params, headers=headers, timeout=10)

        # Log response details
        print(f"[ML API] Response Status: {response.status_code}")

        # Check status
        if response.status_code != 200:
            # Log failure details
            body_preview = response.text[:500] if response.text else "empty"
            print(f"[ML API] ❌ AUTHENTICATED REQUEST FAILED")
            print(f"[ML API] Status: {response.status_code}")
            print(f"[ML API] Response body: {body_preview}")
            return None

        # Parse JSON
        data = response.json()

        # Log success
        results_count = len(data.get('results', []))
        total_results = data.get('paging', {}).get('total', 0)
        print(f"[ML API] ✅ AUTHENTICATED REQUEST SUCCESS")
        print(f"[ML API] Results: {results_count} items fetched, {total_results} total available")

        # Normalize and return
        return _normalize_api_response(data, query)

    except requests.exceptions.Timeout:
        print("[ML API] ❌ Request timeout (10 seconds)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ML API] ❌ Request error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"[ML API] ❌ Parse error: {e}")
        return None


def _normalize_api_response(api_response: dict, query: str) -> dict:
    """
    Normalizes Mercado Livre API response to internal format.

    Args:
        api_response: Raw API response
        query: Original search query

    Returns:
        dict: Normalized marketplace data
    """
    results = api_response.get('results', [])
    total_results = api_response.get('paging', {}).get('total', 0)

    if not results:
        # No results - return mock fallback
        return _get_mock_data(query, fallback=True, error="No results found")

    # Extract prices
    prices = [item.get('price', 0) for item in results if item.get('price')]

    if not prices:
        # No price data - fallback
        return _get_mock_data(query, fallback=True, error="No price data")

    # Calculate price statistics
    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)
    price_spread = (max_price - min_price) / max(avg_price, 1)

    # Count unique sellers
    seller_ids = set()
    for item in results:
        seller_id = item.get('seller', {}).get('id')
        if seller_id:
            seller_ids.add(seller_id)

    unique_sellers = len(seller_ids)

    # Estimate total sold quantity
    sold_quantity = 0
    for item in results:
        sold = item.get('sold_quantity', 0)
        sold_quantity += sold

    # Calculate competition level
    competition_level = _calculate_competition_level(total_results, unique_sellers)

    # Detect price war
    price_war = _detect_price_war(price_spread)

    return {
        'total_listings': total_results,
        'items_fetched': len(results),
        'avg_price': round(avg_price, 2),
        'price_range': {
            'min': round(min_price, 2),
            'max': round(max_price, 2)
        },
        'top_sellers': unique_sellers,
        'avg_rating': 4.2,  # TODO: Fetch real seller ratings (requires additional API calls)
        'sold_quantity': sold_quantity,
        'competition_level': competition_level,
        'price_war_indicator': price_war,
        'source': 'mercado_livre_api',
        'top_items': _extract_top_items(results[:10])  # Top 10 items
    }


def _extract_top_items(results: list) -> list:
    """
    Extracts basic info from top results.

    Args:
        results: List of API result items

    Returns:
        list: Simplified item data
    """
    items = []

    for item in results:
        items.append({
            'title': item.get('title', ''),
            'price': item.get('price', 0),
            'permalink': item.get('permalink', ''),
            'condition': item.get('condition', 'unknown'),
            'available_quantity': item.get('available_quantity', 0),
            'sold_quantity': item.get('sold_quantity', 0),
            'thumbnail': item.get('thumbnail', ''),
        })

    return items


def _get_mock_data(query: str, fallback: bool = False, error: str = '') -> dict:
    """
    Generates deterministic mock data based on query hash.

    Args:
        query: Product search query
        fallback: Whether this is a fallback due to API failure
        error: Error message if fallback

    Returns:
        dict: Mock marketplace data
    """
    # Generate deterministic values based on query hash
    # This ensures same query always returns same mock data
    query_hash = int(hashlib.md5(query.lower().encode()).hexdigest()[:8], 16)

    # Use hash to generate consistent mock data
    total_listings = 50 + (query_hash % 950)  # 50-999
    avg_price = 30 + (query_hash % 470)  # 30-499
    price_variation = (query_hash % 50) / 100  # 0-50% variation

    min_price = int(avg_price * (1 - price_variation))
    max_price = int(avg_price * (1 + price_variation))

    top_sellers = 10 + (query_hash % 190)  # 10-199
    avg_rating = 3.5 + ((query_hash % 25) / 10)  # 3.5-6.0
    avg_rating = min(5.0, avg_rating)  # Cap at 5.0

    sold_quantity = 100 + (query_hash % 4900)  # 100-4999

    data = {
        'total_listings': total_listings,
        'avg_price': avg_price,
        'price_range': {
            'min': min_price,
            'max': max_price
        },
        'top_sellers': top_sellers,
        'avg_rating': round(avg_rating, 1),
        'sold_quantity': sold_quantity,
        'competition_level': _calculate_competition_level(total_listings, top_sellers),
        'price_war_indicator': _detect_price_war(price_variation),
        'source': 'mock_fallback' if fallback else 'mock_data'
    }

    if error:
        data['error'] = error

    return data


def _calculate_competition_level(listings: int, sellers: int) -> str:
    """
    Determines competition level based on listings and sellers.

    Args:
        listings: Total number of listings
        sellers: Number of unique sellers

    Returns:
        str: 'low', 'medium', or 'high'
    """
    if sellers == 0:
        return 'low'

    ratio = listings / max(sellers, 1)

    if ratio < 3:
        return 'low'
    elif ratio < 7:
        return 'medium'
    else:
        return 'high'


def _detect_price_war(variation: float) -> bool:
    """
    Detects if there's a price war (extreme price variation).

    Args:
        variation: Price variation ratio

    Returns:
        bool: True if price war detected
    """
    return variation > 0.4  # More than 40% variation suggests price war

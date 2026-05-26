"""
Google Trends data provider - WITH CACHING AND RATE-LIMIT PROTECTION!

Phase 2.1 implementation with database caching to avoid rate limits.
Uses 24-hour cache TTL and cooldown protection after 429 errors.
Falls back to mock data if provider unavailable (resilient architecture).
"""
import hashlib
from typing import Dict, Optional
from django.utils import timezone
from market.providers.google_trends import GoogleTrendsProvider
from market.models import GoogleTrendsCache, GoogleTrendsCooldown


# Initialize provider (singleton pattern)
_trends_provider = GoogleTrendsProvider()


def get_trends_data(query: str) -> dict:
    """
    Fetches trend data for a given product query with caching.

    NOW WITH CACHING AND RATE-LIMIT PROTECTION!

    Flow:
    1. Check cooldown status (if HTTP 429 recently)
    2. Check cache (24-hour TTL)
    3. If cache miss and not in cooldown, fetch from Google Trends
    4. Store successful fetch in cache
    5. Activate cooldown on HTTP 429
    6. Fall back to mock if all else fails

    Args:
        query: Product search query

    Returns:
        dict: Trends data including source indicator:
            - source: 'google_trends' (live/cached) or 'mock_fallback'
    """
    print("=" * 70)
    print(f"[Google Trends Service] 🔍 Fetching data for: {query}")
    print("=" * 70)

    # Step 1: Check cooldown status
    if GoogleTrendsCooldown.is_in_cooldown():
        cooldown_status = GoogleTrendsCooldown.get_status()
        remaining = cooldown_status.get('remaining_minutes', 0)
        print(f"[Google Trends Service] ⏸️  COOLDOWN ACTIVE ({remaining} min remaining)")
        print(f"[Google Trends Service]   Reason: {cooldown_status.get('reason')}")

        # Check if we have cached data
        cached = GoogleTrendsCache.get_cached(query)
        if cached:
            print(f"[Google Trends Service] 💾 Using CACHED data (during cooldown)")
            normalized = _normalize_trends_signals(cached.raw_data)
            normalized['source'] = 'google_trends'  # Mark as real data (just cached)
            print("=" * 70)
            return normalized
        else:
            print(f"[Google Trends Service] ⚠️  No cached data available")
            print("=" * 70)
            print(f"[Google Trends Service] ⚠️  FALLBACK: Using MOCK data")
            print("=" * 70)
            return _get_mock_trends_data(query)

    # Step 2: Check cache
    cached = GoogleTrendsCache.get_cached(query)
    if cached and cached.is_fresh():
        age_minutes = (timezone.now() - cached.fetched_at).seconds // 60
        print(f"[Google Trends Service] 💾 CACHE HIT!")
        print(f"[Google Trends Service]   Age: {age_minutes} minutes old")
        print(f"[Google Trends Service]   Using cached Google Trends data")
        print("=" * 70)

        normalized = _normalize_trends_signals(cached.raw_data)
        normalized['source'] = 'google_trends'  # Mark as real data (cached)
        return normalized

    print(f"[Google Trends Service] 💭 Cache miss - fetching fresh data")

    # Step 3: Try real Google Trends
    if _trends_provider.is_available():
        try:
            signals = _trends_provider.get_trend_signals(query)

            if signals:
                # Convert to legacy format for compatibility
                normalized = _normalize_trends_signals(signals)

                # Store in cache
                GoogleTrendsCache.save_trends_data(query, signals, ttl_hours=24)

                print("=" * 70)
                print(f"[Google Trends Service] ✅ SUCCESS: Using REAL Google Trends data!")
                print(f"[Google Trends Service]   Source: pytrends API (live)")
                print(f"[Google Trends Service]   Cached for 24 hours")
                print("=" * 70)
                return normalized
            else:
                print("=" * 70)
                print(f"[Google Trends Service] ⚠️  Provider returned None")
                print(f"[Google Trends Service]   Reason: Likely rate-limited or empty results")

                # Check if it's a rate limit (activate cooldown)
                # Provider should have logged the error
                GoogleTrendsCooldown.activate(
                    reason="Provider returned None (likely HTTP 429)",
                    duration_minutes=15
                )

                print("=" * 70)

        except Exception as e:
            error_str = str(e)
            print("=" * 70)
            print(f"[Google Trends Service] ❌ Error with real provider: {e}")

            # Check if it's a rate limit error
            if "429" in error_str or "Too Many Requests" in error_str:
                GoogleTrendsCooldown.activate(
                    reason=f"HTTP 429: {error_str[:100]}",
                    duration_minutes=20
                )

            print("=" * 70)
    else:
        print("=" * 70)
        print(f"[Google Trends Service] ⚠️  Provider not available")
        print("=" * 70)

    # Step 4: Fallback to mock data
    print("=" * 70)
    print(f"[Google Trends Service] ⚠️  FALLBACK: Using MOCK data")
    print(f"[Google Trends Service]   Source: Deterministic mock generator")
    print(f"[Google Trends Service]   This is NOT real Google Trends data")
    print("=" * 70)
    return _get_mock_trends_data(query)


def _normalize_trends_signals(signals: Dict) -> Dict:
    """
    Normalize real Google Trends signals to expected format.

    Converts new provider format to format expected by analyzer/scoring.
    """
    return {
        # Trend analysis
        'trend_direction': signals.get('trend_direction', 'stable'),
        'trend_strength': signals.get('trend_strength', 5.0),

        # Growth metrics
        'growth_30d': signals.get('growth_30d', 0.0),
        'growth_90d': signals.get('growth_90d', 0.0),

        # Momentum and stability
        'momentum_score': signals.get('momentum_score', 5.0),
        'stability_score': signals.get('stability_score', 5.0),

        # Interest levels
        'current_interest': signals.get('current_interest', 0),
        'peak_interest': signals.get('peak_interest', 0),
        'average_interest': signals.get('average_interest', 0.0),

        # Seasonality
        'seasonality_detected': signals.get('seasonality_detected', False),
        'volatility': signals.get('volatility', 0.0),

        # Related data
        'related_queries': signals.get('related_queries', []),
        'top_regions': signals.get('top_regions', []),

        # Metadata
        'confidence': signals.get('confidence', 0.0),
        'provider': signals.get('provider', 'google_trends'),
        'source': 'google_trends',  # Mark as real data

        # Raw data for storage
        'raw_data': signals.get('raw_data', {})
    }


def _get_mock_trends_data(query: str) -> dict:
    """
    Generate deterministic mock trends data as fallback.

    Used when Google Trends is unavailable.
    Same algorithm as before for consistency.
    """
    # Generate deterministic values based on query hash
    query_hash = int(hashlib.md5(query.lower().encode()).hexdigest()[:8], 16)

    # Generate consistent interest
    base_interest = 30 + (query_hash % 40)  # 30-69

    # Generate trend metrics
    growth_30d_base = ((query_hash % 100) - 50) / 2  # -25 to +25
    growth_90d_base = ((query_hash % 80) - 40) / 2  # -20 to +20

    # Determine trend direction based on growth
    if growth_30d_base > 10:
        trend_direction = 'upward'
    elif growth_30d_base < -10:
        trend_direction = 'downward'
    else:
        trend_direction = 'stable'

    # Calculate momentum from growth
    momentum_score = 5.0 + (growth_30d_base / 5.0)  # Scale growth to 0-10
    momentum_score = max(0.0, min(10.0, momentum_score))

    return {
        'trend_direction': trend_direction,
        'trend_strength': 5.0 + (query_hash % 5),  # 5-9

        'growth_30d': round(growth_30d_base, 1),
        'growth_90d': round(growth_90d_base, 1),

        'momentum_score': round(momentum_score, 1),
        'stability_score': 5.0,  # Neutral

        'current_interest': base_interest,
        'peak_interest': base_interest + 20,
        'average_interest': base_interest,

        'seasonality_detected': (query_hash % 3) == 0,  # ~33% of products
        'volatility': 20.0 + (query_hash % 30),  # 20-50

        'related_queries': [
            f"{query} preço",
            f"{query} barato",
            f"melhor {query}"
        ],
        'top_regions': [
            {'region': 'São Paulo', 'interest': 100},
            {'region': 'Minas Gerais', 'interest': 75},
            {'region': 'Rio de Janeiro', 'interest': 65}
        ],

        'confidence': 0.3,  # Low confidence for mock
        'provider': 'mock',
        'source': 'mock_fallback',
        'raw_data': {}
    }


def get_provider_status() -> Dict:
    """
    Get current Google Trends provider status.

    Returns:
        dict: Provider status for UI display
    """
    return _trends_provider.get_status_for_display()

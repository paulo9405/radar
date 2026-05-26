"""
Google Trends data provider - NOW WITH REAL DATA!

Phase 2 implementation using pytrends for actual Google Trends signals.
Falls back to mock data if provider unavailable (resilient architecture).
"""
import hashlib
from typing import Dict, Optional
from market.providers.google_trends import GoogleTrendsProvider


# Initialize provider (singleton pattern)
_trends_provider = GoogleTrendsProvider()


def get_trends_data(query: str) -> dict:
    """
    Fetches trend data for a given product query.

    NOW USES REAL GOOGLE TRENDS DATA via pytrends!

    Falls back to mock data if:
    - Provider unavailable
    - Rate limit exceeded
    - Network error
    - Empty results

    Args:
        query: Product search query

    Returns:
        dict: Trends data including:
            - trend_direction: 'upward', 'stable', 'downward', 'volatile'
            - trend_strength: float (0-10)
            - growth_30d: Percentage growth in last 30 days
            - growth_90d: Percentage growth in last 90 days
            - momentum_score: float (0-10)
            - stability_score: float (0-10)
            - current_interest: int (0-100)
            - related_queries: list of related searches
            - top_regions: list of top regions
            - confidence: float (0-1)
            - source: 'google_trends' or 'mock_fallback'
    """
    print(f"[Google Trends Service] Fetching data for: {query}")

    # Try real Google Trends first
    if _trends_provider.is_available():
        try:
            signals = _trends_provider.get_trend_signals(query)

            if signals:
                # Convert to legacy format for compatibility
                normalized = _normalize_trends_signals(signals)
                print(f"[Google Trends Service] ✅ Using REAL Google Trends data")
                return normalized

        except Exception as e:
            print(f"[Google Trends Service] Error with real provider: {e}")

    # Fallback to mock data
    print(f"[Google Trends Service] ⚠️  Falling back to mock data")
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

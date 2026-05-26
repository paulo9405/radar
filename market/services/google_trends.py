"""
Google Trends data provider.

Currently using mock data for MVP.
Future: Integration with Google Trends API or pytrends.
"""
import hashlib
from datetime import datetime, timedelta


def get_trends_data(query: str) -> dict:
    """
    Fetches trend data for a given product query.

    Currently returns deterministic mock data based on query.

    TODO: Replace with real Google Trends integration
    - Option 1: Use pytrends library (free, unofficial)
      pip install pytrends
      from pytrends.request import TrendReq

    - Option 2: Use SerpAPI (paid, reliable)
      https://serpapi.com/google-trends-api

    - Option 3: Use DataForSEO (paid, comprehensive)
      https://dataforseo.com/apis/google-trends-api

    Recommended approach:
    1. Start with pytrends for MVP
    2. Migrate to SerpAPI/DataForSEO if scaling or reliability issues
    3. Monitor for rate limits and implement caching

    Args:
        query: Product search query

    Returns:
        dict: Trends data including:
            - interest_over_time: List of interest values (0-100)
            - growth_30d: Percentage growth in last 30 days
            - growth_90d: Percentage growth in last 90 days
            - trend_direction: 'rising', 'stable', or 'falling'
            - seasonality_detected: Boolean
            - peak_periods: List of high-interest months
    """
    # Generate deterministic values based on query hash
    query_hash = int(hashlib.md5(query.lower().encode()).hexdigest()[:8], 16)

    # Generate consistent interest over time (last 12 weeks)
    base_interest = 30 + (query_hash % 40)  # 30-69
    interest_values = []

    for i in range(12):
        # Add some variation but keep it deterministic
        variation = ((query_hash + i * 7) % 30) - 15  # -15 to +15
        value = max(0, min(100, base_interest + variation + (i * 2)))  # Slight upward trend
        interest_values.append(value)

    # Calculate growth metrics
    recent_avg = sum(interest_values[-4:]) / 4  # Last 30 days (4 weeks)
    older_avg = sum(interest_values[:4]) / 4    # 60-90 days ago

    growth_30d = ((recent_avg - older_avg) / max(older_avg, 1)) * 100

    # For 90d growth, compare overall trend
    growth_90d = ((interest_values[-1] - interest_values[0]) / max(interest_values[0], 1)) * 100

    # Determine trend direction
    if growth_30d > 15:
        trend_direction = 'rising'
    elif growth_30d < -15:
        trend_direction = 'falling'
    else:
        trend_direction = 'stable'

    # Simple seasonality detection (based on variance)
    variance = max(interest_values) - min(interest_values)
    seasonality_detected = variance > 40

    return {
        'interest_over_time': interest_values,
        'current_interest': interest_values[-1],
        'growth_30d': round(growth_30d, 1),
        'growth_90d': round(growth_90d, 1),
        'trend_direction': trend_direction,
        'seasonality_detected': seasonality_detected,
        'peak_periods': _get_mock_peak_periods(query_hash),
        'related_queries': _get_mock_related_queries(query),
        'source': 'mock_data'  # Will be replaced when real Google Trends API is integrated
    }


def _get_mock_peak_periods(query_hash: int) -> list:
    """
    Returns mock peak periods based on query hash.

    TODO: Replace with real seasonal data from Google Trends

    Args:
        query_hash: Integer hash of query

    Returns:
        list: Months with high interest
    """
    months = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    # Pick 2-3 months deterministically
    peak_count = 2 + (query_hash % 2)
    peaks = []

    for i in range(peak_count):
        month_index = (query_hash + i * 13) % 12
        peaks.append(months[month_index])

    return peaks


def _get_mock_related_queries(query: str) -> list:
    """
    Returns mock related queries.

    TODO: Replace with real related queries from Google Trends

    Args:
        query: Original search query

    Returns:
        list: Related search terms
    """
    # Simple mock - just variations of the query
    # In real implementation, this would come from Google Trends API
    related = [
        f"{query} preço",
        f"{query} comprar",
        f"{query} barato",
        f"melhor {query}",
    ]

    return related[:3]  # Return top 3

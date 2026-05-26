"""
Scoring engine for product analysis.

Implements the weighted formula from the roadmap:
- Demand (Tendência): 35%
- Competition (Concorrência): 30%
- Saturation (Saturação): 20%
- Price/Margin (Preço): 15%

All scores are normalized to a 0-10 scale.
"""


def calculate_demand_score(trends_data: dict) -> float:
    """
    Calculates demand score based on Google Trends data.

    NOW USES REAL GOOGLE TRENDS SIGNALS!

    Factors:
    - Current interest level (30%) - baseline demand
    - Momentum score (50%) - captures growth acceleration
    - Stability score (20%) - confidence in trend

    Args:
        trends_data: Dictionary from google_trends.get_trends_data()

    Returns:
        float: Demand score (0-10)
    """
    current_interest = trends_data['current_interest']

    # Use momentum_score if available (from real Google Trends)
    # Otherwise fall back to growth-based calculation (from mock data)
    if 'momentum_score' in trends_data and trends_data.get('source') == 'google_trends':
        momentum_score = trends_data['momentum_score']
        stability_score = trends_data.get('stability_score', 5.0)

        # Normalize current interest (0-100 -> 0-10)
        interest_score = current_interest / 10

        # Weighted average using real signals
        demand_score = (
            interest_score * 0.30 +
            momentum_score * 0.50 +
            stability_score * 0.20
        )
    else:
        # Fallback to growth-based calculation (mock data)
        growth_30d = trends_data['growth_30d']
        growth_90d = trends_data['growth_90d']

        # Normalize current interest (0-100 -> 0-10)
        interest_score = current_interest / 10

        # Normalize growth rates
        growth_30d_score = _normalize_growth(growth_30d)
        growth_90d_score = _normalize_growth(growth_90d)

        # Weighted average (legacy formula)
        demand_score = (
            interest_score * 0.40 +
            growth_30d_score * 0.35 +
            growth_90d_score * 0.25
        )

    return round(min(10.0, max(0.0, demand_score)), 1)


def calculate_competition_score(marketplace_data: dict) -> float:
    """
    Calculates competition score based on marketplace data.

    Lower competition = higher score (it's good for the seller)

    Factors:
    - Number of sellers (50%)
    - Competition level (30%)
    - Total listings (20%)

    Args:
        marketplace_data: Dictionary from mercado_livre.get_marketplace_data()

    Returns:
        float: Competition score (0-10)
    """
    top_sellers = marketplace_data['top_sellers']
    competition_level = marketplace_data['competition_level']
    total_listings = marketplace_data['total_listings']

    # Fewer sellers = better (inverse scoring)
    # Normalize: 200+ sellers = 0, <20 sellers = 10
    sellers_score = max(0, 10 - (top_sellers / 20))

    # Competition level scoring
    competition_scores = {
        'low': 10.0,
        'medium': 5.0,
        'high': 2.0,
    }
    level_score = competition_scores.get(competition_level, 5.0)

    # Fewer listings = better (inverse scoring)
    # Normalize: 1000+ listings = 0, <100 listings = 10
    listings_score = max(0, 10 - (total_listings / 100))

    # Weighted average
    competition_score = (
        sellers_score * 0.50 +
        level_score * 0.30 +
        listings_score * 0.20
    )

    return round(min(10.0, max(0.0, competition_score)), 1)


def calculate_saturation_score(marketplace_data: dict, trends_data: dict) -> float:
    """
    Calculates market saturation score.

    Lower saturation = higher score (better opportunity)

    NOW USES REAL GOOGLE TRENDS SIGNALS!

    Factors:
    - Price war indicator (40%)
    - Listings vs demand ratio (30%)
    - Trend direction (20%)
    - Volatility penalty (10%) - unstable markets are riskier

    Args:
        marketplace_data: Dictionary from mercado_livre.get_marketplace_data()
        trends_data: Dictionary from google_trends.get_trends_data()

    Returns:
        float: Saturation score (0-10)
    """
    price_war = marketplace_data['price_war_indicator']
    total_listings = marketplace_data['total_listings']
    current_interest = trends_data['current_interest']
    trend_direction = trends_data['trend_direction']

    # Price war is bad
    price_war_score = 2.0 if price_war else 8.0

    # Calculate supply/demand ratio
    # High listings with low interest = saturated (bad)
    if current_interest > 0:
        supply_demand_ratio = total_listings / (current_interest * 10)
    else:
        supply_demand_ratio = 10  # Assume high saturation if no interest

    # Normalize ratio: <0.5 = good, >2 = bad
    if supply_demand_ratio < 0.5:
        ratio_score = 10.0
    elif supply_demand_ratio < 1.0:
        ratio_score = 7.0
    elif supply_demand_ratio < 2.0:
        ratio_score = 4.0
    else:
        ratio_score = 1.0

    # Normalize trend direction (support both old and new formats)
    normalized_direction = _normalize_trend_direction(trend_direction)

    # Trend direction affects saturation
    trend_scores = {
        'rising': 8.0,     # Growing market, less saturated
        'stable': 5.0,     # Stable market
        'falling': 2.0,    # Declining market, likely saturated
        'volatile': 3.0,   # Unpredictable market, risky
    }
    trend_score = trend_scores.get(normalized_direction, 5.0)

    # Volatility penalty (if available from real Google Trends)
    volatility_score = 10.0  # Default: no penalty
    if 'volatility' in trends_data and trends_data.get('source') == 'google_trends':
        volatility = trends_data['volatility']
        # High volatility (>40) = risky/saturated market
        if volatility > 40:
            volatility_score = 4.0
        elif volatility > 25:
            volatility_score = 7.0
        else:
            volatility_score = 10.0

    # Weighted average
    saturation_score = (
        price_war_score * 0.40 +
        ratio_score * 0.30 +
        trend_score * 0.20 +
        volatility_score * 0.10
    )

    return round(min(10.0, max(0.0, saturation_score)), 1)


def calculate_price_score(marketplace_data: dict) -> float:
    """
    Calculates price/margin score.

    Factors:
    - Average price range (healthy margin) (60%)
    - Price stability (no extreme variation) (40%)

    Args:
        marketplace_data: Dictionary from mercado_livre.get_marketplace_data()

    Returns:
        float: Price score (0-10)
    """
    avg_price = marketplace_data['avg_price']
    price_range = marketplace_data['price_range']

    # Price sweet spot: R$50-300 (good margins, not too expensive)
    if 50 <= avg_price <= 300:
        price_level_score = 10.0
    elif 30 <= avg_price < 50 or 300 < avg_price <= 500:
        price_level_score = 6.0
    else:
        price_level_score = 3.0

    # Price stability (lower variation is better)
    price_variation = (price_range['max'] - price_range['min']) / max(avg_price, 1)

    if price_variation < 0.3:  # Less than 30% variation
        stability_score = 10.0
    elif price_variation < 0.5:  # 30-50% variation
        stability_score = 6.0
    else:  # More than 50% variation
        stability_score = 3.0

    # Weighted average
    price_score = (
        price_level_score * 0.60 +
        stability_score * 0.40
    )

    return round(min(10.0, max(0.0, price_score)), 1)


def calculate_final_score(demand: float, competition: float, saturation: float, price: float) -> float:
    """
    Calculates the weighted final score based on the roadmap formula.

    Formula:
    - Demand: 35%
    - Competition: 30%
    - Saturation: 20%
    - Price: 15%

    Args:
        demand: Demand score (0-10)
        competition: Competition score (0-10)
        saturation: Saturation score (0-10)
        price: Price score (0-10)

    Returns:
        float: Final weighted score (0-10)
    """
    final = (
        demand * 0.35 +
        competition * 0.30 +
        saturation * 0.20 +
        price * 0.15
    )

    return round(min(10.0, max(0.0, final)), 1)


def get_classification(final_score: float) -> str:
    """
    Returns classification based on final score.

    Ranges (from roadmap):
    - 0-3: Produto ruim
    - 4-6: Arriscado
    - 7-8: Boa oportunidade
    - 9-10: Alta oportunidade

    Args:
        final_score: Final score (0-10)

    Returns:
        str: Classification key ('bad', 'risky', 'good', 'excellent')
    """
    if final_score <= 3.0:
        return 'bad'
    elif final_score <= 6.0:
        return 'risky'
    elif final_score <= 8.0:
        return 'good'
    else:
        return 'excellent'


def _normalize_growth(growth_percentage: float) -> float:
    """
    Normalizes growth percentage to a 0-10 scale.

    Args:
        growth_percentage: Growth rate (-100 to +inf)

    Returns:
        float: Normalized score (0-10)
    """
    # Growth > +50% = 10
    # Growth 0% = 5
    # Growth < -50% = 0

    if growth_percentage >= 50:
        return 10.0
    elif growth_percentage >= 0:
        return 5.0 + (growth_percentage / 50) * 5.0
    else:
        # Negative growth
        return max(0.0, 5.0 + (growth_percentage / 50) * 5.0)


def _normalize_trend_direction(direction: str) -> str:
    """
    Normalizes trend direction to standard format.

    Maps Google Trends format to legacy format:
    - 'upward' -> 'rising'
    - 'downward' -> 'falling'
    - 'stable' -> 'stable'
    - 'volatile' -> 'volatile'

    Args:
        direction: Trend direction from Google Trends

    Returns:
        str: Normalized direction
    """
    direction_map = {
        'upward': 'rising',
        'downward': 'falling',
        'stable': 'stable',
        'volatile': 'volatile',
        'rising': 'rising',   # Support legacy format
        'falling': 'falling',  # Support legacy format
    }
    return direction_map.get(direction, 'stable')

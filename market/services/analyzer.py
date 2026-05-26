"""
Main product analyzer service - Multi-Provider Intelligence Engine.

Orchestrates data collection from multiple providers, aggregates signals,
calculates weighted scores, and generates market intelligence analysis.

Architecture:
- Provider-agnostic: Works with any data source (API, scraping, trends, etc.)
- Resilient: Graceful fallback if providers unavailable
- Extensible: Easy to add new data providers
- Never fails: Always returns valid analysis

Providers:
- Mercado Livre API (OAuth, currently policy-blocked)
- Google Trends (planned: Phase 2)
- SERP APIs (planned: Phase 3)
- Web scraping (planned: Phase 4)
- Mock fallback (always available)

Modes:
- 'basic' (free): Core scores and classification
- 'premium' (paid): Full data, historical trends, alerts

See: docs/provider_architecture.md for complete architecture documentation.
"""
from . import mercado_livre, google_trends, scoring


def analyze_product(query: str, mode: str = "basic") -> dict:
    """
    Main analysis function for a product query.

    This function:
    1. Collects data from all providers
    2. Calculates all scores
    3. Generates classification and summary
    4. Returns appropriate data based on mode

    Args:
        query: Product search query (e.g., "Luminária Sunset")
        mode: Analysis mode - "basic" (free) or "premium" (paid)

    Returns:
        dict: Complete analysis result with structure:
        {
            "query": str,
            "mode": str,
            "scores": {
                "demand": float (0-10),
                "competition": float (0-10),
                "saturation": float (0-10),
                "price": float (0-10),
                "final": float (0-10)
            },
            "classification": str,
            "classification_label": str,
            "summary": str,
            "confidence_level": int (0-100),
            "locked_fields": list (only in basic mode),
            "premium_data": dict (only in premium mode)
        }
    """
    # Step 1: Collect data from providers
    marketplace_data = mercado_livre.get_marketplace_data(query)
    trends_data = google_trends.get_trends_data(query)

    # Step 2: Calculate individual scores
    demand_score = scoring.calculate_demand_score(trends_data)
    competition_score = scoring.calculate_competition_score(marketplace_data)
    saturation_score = scoring.calculate_saturation_score(marketplace_data, trends_data)
    price_score = scoring.calculate_price_score(marketplace_data)

    # Step 3: Calculate final score and classification
    final_score = scoring.calculate_final_score(
        demand_score,
        competition_score,
        saturation_score,
        price_score
    )

    classification = scoring.get_classification(final_score)

    # Step 4: Generate summary
    summary = _generate_summary(
        query=query,
        classification=classification,
        final_score=final_score,
        trends_data=trends_data,
        marketplace_data=marketplace_data
    )

    # Step 5: Build base response
    result = {
        "query": query,
        "mode": mode,
        "scores": {
            "demand": demand_score,
            "competition": competition_score,
            "saturation": saturation_score,
            "price": price_score,
            "final": final_score
        },
        "classification": classification,
        "classification_label": _get_classification_label(classification),
        "summary": summary,
        "confidence_level": _calculate_confidence(marketplace_data, trends_data),
        "data_sources": {
            "marketplace": marketplace_data.get('source', 'unknown'),
            "trends": trends_data.get('source', 'mock_data')
        },
        "raw_data": {
            "marketplace": marketplace_data,
            "trends": trends_data
        }
    }

    # Step 6: Add mode-specific data
    if mode == "basic":
        result["locked_fields"] = _get_locked_fields()
    else:  # premium mode
        result["premium_data"] = _get_premium_data(marketplace_data, trends_data)

    return result


def _generate_summary(query: str, classification: str, final_score: float,
                     trends_data: dict, marketplace_data: dict) -> str:
    """
    Generates AI-like summary based on analysis data.

    This simulates an AI-generated summary. In future versions,
    this could be replaced with actual LLM integration (OpenAI, Anthropic, etc.)

    Args:
        query: Product name
        classification: Product classification
        final_score: Final score
        trends_data: Google Trends data
        marketplace_data: Mercado Livre data

    Returns:
        str: Human-readable summary
    """
    trend_direction = trends_data['trend_direction']
    growth_30d = trends_data['growth_30d']
    competition_level = marketplace_data['competition_level']
    total_listings = marketplace_data['total_listings']

    # Build summary based on classification
    if classification == 'excellent':
        opening = f"✓ {query.title()} apresenta alta oportunidade de mercado."
    elif classification == 'good':
        opening = f"✓ {query.title()} mostra boa oportunidade, mas requer atenção."
    elif classification == 'risky':
        opening = f"⚠ {query.title()} é um produto arriscado."
    else:  # bad
        opening = f"✗ {query.title()} não é recomendado no momento."

    # Add trend analysis
    if trend_direction == 'rising':
        trend_text = f"O interesse de busca está crescendo ({growth_30d:+.1f}% em 30 dias)"
    elif trend_direction == 'falling':
        trend_text = f"O interesse de busca está em queda ({growth_30d:+.1f}% em 30 dias)"
    else:
        trend_text = "O interesse de busca está estável"

    # Add competition analysis
    competition_texts = {
        'low': f"com baixa concorrência ({total_listings} anúncios ativos)",
        'medium': f"com concorrência moderada ({total_listings} anúncios ativos)",
        'high': f"com alta concorrência ({total_listings} anúncios ativos)"
    }
    competition_text = competition_texts.get(competition_level, "")

    # Add recommendation
    if final_score >= 7:
        recommendation = "Pode valer um teste inicial com estoque reduzido."
    elif final_score >= 4:
        recommendation = "Recomenda-se pesquisa adicional antes de investir."
    else:
        recommendation = "Não recomendamos investimento neste momento."

    summary = f"{opening} {trend_text} {competition_text}. {recommendation}"

    return summary


def _get_classification_label(classification: str) -> str:
    """Returns Portuguese label for classification."""
    labels = {
        'bad': 'Produto ruim',
        'risky': 'Arriscado',
        'good': 'Boa oportunidade',
        'excellent': 'Alta oportunidade'
    }
    return labels.get(classification, 'Desconhecido')


def _calculate_confidence(marketplace_data: dict, trends_data: dict) -> int:
    """
    Calculates confidence level of the analysis (0-100%).

    Based on data quality and consistency.
    In mock mode, returns simulated confidence.

    Args:
        marketplace_data: Marketplace data
        trends_data: Trends data

    Returns:
        int: Confidence percentage (0-100)
    """
    # In production, this would analyze:
    # - Data freshness
    # - Sample size
    # - Data consistency
    # - Provider reliability

    base_confidence = 70  # Mock data has moderate confidence

    # Adjust based on interest level (higher interest = more reliable data)
    if trends_data['current_interest'] > 50:
        base_confidence += 10

    # Adjust based on number of listings (more listings = more data)
    if marketplace_data['total_listings'] > 500:
        base_confidence += 10

    return min(95, base_confidence)  # Cap at 95% for mock data


def _get_locked_fields() -> list:
    """
    Returns list of premium features locked in basic mode.

    Returns:
        list: Premium feature descriptions
    """
    return [
        "Análise completa de marketplace (top vendedores, variação de preços)",
        "Gráfico detalhado de tendência histórica",
        "Análise de sazonalidade e melhores períodos",
        "Recomendação de faixa de preço ideal",
        "Produtos similares com menor concorrência",
        "Alertas de mudanças no mercado",
        "Exportação de relatório completo"
    ]


def _get_premium_data(marketplace_data: dict, trends_data: dict) -> dict:
    """
    Returns additional premium data not available in basic mode.

    This would include more detailed analysis, charts, and recommendations.

    Args:
        marketplace_data: Marketplace data
        trends_data: Trends data

    Returns:
        dict: Premium features data
    """
    return {
        "marketplace_breakdown": {
            "total_listings": marketplace_data['total_listings'],
            "top_sellers": marketplace_data['top_sellers'],
            "avg_rating": marketplace_data['avg_rating'],
            "sold_quantity": marketplace_data['sold_quantity'],
            "price_range": marketplace_data['price_range'],
            "competition_level": marketplace_data['competition_level']
        },
        "trend_details": {
            "interest_over_time": trends_data['interest_over_time'],
            "growth_metrics": {
                "30_days": trends_data['growth_30d'],
                "90_days": trends_data['growth_90d']
            },
            "seasonality": {
                "detected": trends_data['seasonality_detected'],
                "peak_periods": trends_data['peak_periods']
            },
            "related_queries": trends_data['related_queries']
        },
        "recommendations": {
            "ideal_price_range": {
                "min": marketplace_data['price_range']['min'],
                "max": marketplace_data['price_range']['max'],
                "suggested": marketplace_data['avg_price']
            },
            "best_entry_strategy": _get_entry_strategy(marketplace_data, trends_data),
            "risk_factors": _get_risk_factors(marketplace_data, trends_data)
        }
    }


def _get_entry_strategy(marketplace_data: dict, trends_data: dict) -> str:
    """Generates market entry strategy recommendation."""
    if trends_data['trend_direction'] == 'rising' and marketplace_data['competition_level'] == 'low':
        return "Entrada rápida recomendada - mercado em crescimento com baixa concorrência"
    elif marketplace_data['competition_level'] == 'high':
        return "Entrada cautelosa - focar em diferenciação e nicho específico"
    else:
        return "Entrada gradual - testar com estoque limitado e analisar resposta"


def _get_risk_factors(marketplace_data: dict, trends_data: dict) -> list:
    """Identifies main risk factors."""
    risks = []

    if marketplace_data['price_war_indicator']:
        risks.append("Guerra de preços detectada - margens podem ser comprimidas")

    if trends_data['trend_direction'] == 'falling':
        risks.append("Interesse em queda - demanda pode diminuir")

    if marketplace_data['competition_level'] == 'high':
        risks.append("Alta concorrência - difícil destacar-se")

    if not risks:
        risks.append("Riscos moderados - monitorar evolução do mercado")

    return risks

# Provider Architecture — Multi-Source Intelligence Engine

## Overview

Radar de Tendências uses a **multi-provider architecture** to aggregate market intelligence from multiple data sources. This design ensures resilience, data quality, and independence from any single platform.

## Core Principles

### 1. Provider Independence
No single data source can block the entire system. If one provider fails, others continue to work.

### 2. Graceful Degradation
System always returns valid analysis, even if some providers are unavailable.

### 3. Transparent Attribution
Users see which data sources contributed to the analysis.

### 4. Modular Design
Adding new providers doesn't require rewriting core logic.

### 5. Fail-Safe Fallback
Mock provider ensures system never crashes due to external API issues.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Analysis Engine                         │
│  (Aggregates signals, calculates scores, generates summary) │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Provider Abstraction Layer                │
│         (Normalizes data from different providers)          │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              │
        ┌─────────────────────┴─────────────────────┐
        │                     │                     │
┌───────▼───────┐    ┌───────▼───────┐    ┌───────▼───────┐
│  Marketplace  │    │     Trends    │    │     Search    │
│   Providers   │    │   Providers   │    │   Providers   │
│               │    │               │    │               │
│ MercadoLivre  │    │ GoogleTrends  │    │    SerpAPI    │
│    Shopee     │    │  TikTokTrends │    │  DataForSEO   │
│    Amazon     │    │ SocialSignals │    │   Scraping    │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              ↓
                     ┌────────────────┐
                     │ Mock Provider  │
                     │   (Fallback)   │
                     └────────────────┘
```

---

## Provider Interface

### Base Provider Contract

All providers implement the same interface:

```python
# market/services/providers/base.py

from abc import ABC, abstractmethod
from typing import Optional, Dict

class BaseProvider(ABC):
    """Base class for all data providers."""

    @abstractmethod
    def get_marketplace_data(self, query: str) -> Optional[Dict]:
        """
        Fetch marketplace data for a product query.

        Returns:
            dict: Normalized marketplace data
            None: If provider unavailable or request failed
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is currently available.

        Returns:
            bool: True if provider can be used
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """
        Get current provider status for monitoring.

        Returns:
            str: 'active', 'blocked', 'error', 'unavailable'
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging and display."""
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Type: 'api', 'scraping', 'mock', 'internal'."""
        pass
```

### Normalized Data Format

All providers must return data in this format:

```python
{
    'total_listings': int,           # Number of product listings
    'avg_price': float,              # Average price
    'price_range': {
        'min': float,
        'max': float
    },
    'top_sellers': int,              # Unique seller count
    'avg_rating': float,             # Average rating (0-5)
    'sold_quantity': int,            # Total units sold
    'competition_level': str,        # 'low', 'medium', 'high'
    'price_war_indicator': bool,     # Price volatility detected
    'source': str,                   # Provider identifier
    'confidence': float,             # Data confidence (0-1)
    'raw_data': dict,                # Original provider data
}
```

---

## Provider Implementations

### 1. Mock Provider (Fallback)

**Status:** ✅ Active
**Type:** Deterministic fallback
**Cost:** Free
**Priority:** Core (always available)

```python
# market/services/providers/mock_provider.py

class MockProvider(BaseProvider):
    """
    Deterministic mock data provider.
    Always available as fallback.
    """

    name = "Mock Data"
    source_type = "mock"

    def get_marketplace_data(self, query: str) -> Dict:
        # Generate deterministic data based on query hash
        # Same query always returns same data
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()

        return {
            'total_listings': self._generate_listing_count(query_hash),
            'avg_price': self._generate_avg_price(query_hash),
            # ... other fields
            'source': 'mock_fallback',
            'confidence': 0.3  # Low confidence for mock data
        }

    def is_available(self) -> bool:
        return True  # Always available

    def get_status(self) -> str:
        return 'active'
```

**Use Cases:**
- System fallback when all providers fail
- Development/testing
- Demo mode
- Rate limit exceeded scenarios

---

### 2. Mercado Livre Provider (OAuth)

**Status:** ⚠️ Blocked by policy
**Type:** OAuth API
**Cost:** Free
**Priority:** Medium

```python
# market/services/providers/mercado_livre_provider.py

class MercadoLivreProvider(BaseProvider):
    """
    Mercado Livre API provider using OAuth 2.0.
    Requires authenticated requests.
    """

    name = "Mercado Livre API"
    source_type = "api"

    def get_marketplace_data(self, query: str) -> Optional[Dict]:
        # Check if OAuth token available
        if not self._has_valid_token():
            print(f"[{self.name}] No valid OAuth token")
            return None

        # Make authenticated request
        try:
            response = self._fetch_with_auth(query)
            return self._normalize_response(response)
        except PolicyBlockedException:
            print(f"[{self.name}] Blocked by platform policy")
            return None
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return None

    def is_available(self) -> bool:
        return self._has_valid_token()

    def get_status(self) -> str:
        if not is_configured():
            return 'unavailable'
        if not self._has_valid_token():
            return 'unauthorized'
        if self._is_policy_blocked():
            return 'blocked'
        return 'active'
```

**Current Status:**
- OAuth implementation: ✅ Complete
- Token persistence: ✅ Working
- API communication: ✅ Working
- Endpoint access: ❌ Blocked by `PA_UNAUTHORIZED_RESULT_FROM_POLICIES`

**Future:**
When Mercado Livre policies allow, this provider will be re-enabled automatically.

---

### 3. Google Trends Provider (Planned)

**Status:** 📋 Planned (Phase 2)
**Type:** pytrends library
**Cost:** Free
**Priority:** High

```python
# market/services/providers/google_trends_provider.py

from pytrends.request import TrendReq

class GoogleTrendsProvider(BaseProvider):
    """
    Google Trends data provider using pytrends.
    Provides search interest over time.
    """

    name = "Google Trends"
    source_type = "api"

    def get_trends_data(self, query: str) -> Optional[Dict]:
        try:
            pytrend = TrendReq(hl='pt-BR', tz=360)
            pytrend.build_payload([query], timeframe='today 3-m')

            interest_over_time = pytrend.interest_over_time()

            return {
                'query': query,
                'trend_direction': self._calculate_trend_direction(interest_over_time),
                'growth_30d': self._calculate_growth(interest_over_time, days=30),
                'growth_90d': self._calculate_growth(interest_over_time, days=90),
                'current_interest': interest_over_time[query].iloc[-1],
                'peak_interest': interest_over_time[query].max(),
                'related_queries': pytrend.related_queries(),
                'source': 'google_trends',
                'confidence': 0.9  # High confidence
            }
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return None

    def is_available(self) -> bool:
        # Test if pytrends is working
        try:
            pytrend = TrendReq(timeout=(10, 25))
            return True
        except:
            return False
```

**Metrics Provided:**
- Trend direction (rising, falling, stable)
- 30-day growth percentage
- 90-day growth percentage
- Related search queries
- Regional interest
- Peak interest timing

---

### 4. SERP Provider (Planned)

**Status:** 📋 Planned (Phase 3)
**Type:** SerpAPI / DataForSEO
**Cost:** Paid (usage-based)
**Priority:** Medium

```python
# market/services/providers/serp_provider.py

class SerpProvider(BaseProvider):
    """
    Search engine results page (SERP) data provider.
    Uses SerpAPI or DataForSEO for shopping signals.
    """

    name = "SERP API"
    source_type = "api"

    def get_shopping_data(self, query: str) -> Optional[Dict]:
        try:
            # Query SerpAPI for Google Shopping results
            results = self._query_serpapi(query, search_type='shopping')

            return {
                'shopping_results_count': len(results),
                'merchant_count': self._count_unique_merchants(results),
                'price_range': self._extract_price_range(results),
                'ad_presence': self._detect_ads(results),
                'featured_snippet': self._extract_featured_snippet(results),
                'avg_rating': self._calculate_avg_rating(results),
                'source': 'serp_api',
                'confidence': 0.85
            }
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return None
```

**Metrics Provided:**
- Shopping results count
- Unique merchant count
- Price ranges
- Ad presence/competition
- Featured snippets
- Product ratings

---

### 5. Scraper Provider (Planned)

**Status:** 📋 Planned (Phase 4)
**Type:** Controlled web scraping
**Cost:** Free (infrastructure only)
**Priority:** High

```python
# market/services/providers/scraper_provider.py

class ScraperProvider(BaseProvider):
    """
    Web scraping provider for public marketplace data.
    Uses responsible scraping practices.
    """

    name = "Web Scraper"
    source_type = "scraping"

    def scrape_marketplace(self, query: str, marketplace: str) -> Optional[Dict]:
        # Rate limiting
        if not self._rate_limit_allows():
            print(f"[{self.name}] Rate limit exceeded")
            return None

        # Check cache first
        cached = self._get_cached_data(query, marketplace)
        if cached:
            return cached

        try:
            html = self._fetch_page(query, marketplace)
            parsed_data = self._parse_html(html, marketplace)

            # Cache result
            self._cache_data(query, marketplace, parsed_data)

            return parsed_data
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return None

    def _fetch_page(self, query, marketplace):
        headers = self._get_rotating_headers()
        # Implement request with retry logic
        # Respect robots.txt
        # Throttle requests
        pass
```

**Safety Features:**
- robots.txt compliance
- Rate limiting (max 1 req/second per domain)
- Request caching (24 hour TTL)
- User-agent rotation
- Retry with exponential backoff
- Graceful error handling

**Target Marketplaces:**
- Mercado Livre (public listings)
- Shopee
- Amazon.com.br
- Magazine Luiza
- Casas Bahia

---

## Signal Aggregation

### Aggregation Strategy

```python
# market/services/aggregator.py

class MarketIntelligence:
    """Aggregates signals from multiple providers."""

    def __init__(self):
        self.providers = [
            MercadoLivreProvider(),
            GoogleTrendsProvider(),
            SerpProvider(),
            ScraperProvider(),
            MockProvider()  # Fallback
        ]

    def analyze_product(self, query: str) -> Dict:
        """
        Aggregate data from all available providers.

        Algorithm:
        1. Query all providers in parallel
        2. Collect successful responses
        3. Calculate weighted scores
        4. Aggregate signals
        5. Generate final analysis
        """

        # Collect data from providers
        provider_data = {}
        for provider in self.providers:
            if provider.is_available():
                data = provider.get_data(query)
                if data:
                    provider_data[provider.name] = data

        # Ensure at least mock data
        if not provider_data:
            provider_data['Mock'] = MockProvider().get_data(query)

        # Aggregate signals
        aggregated = self._aggregate_signals(provider_data)

        # Calculate confidence based on provider count
        confidence = self._calculate_confidence(provider_data)

        # Generate analysis
        analysis = {
            'query': query,
            'scores': self._calculate_scores(aggregated),
            'classification': self._classify(aggregated),
            'summary': self._generate_summary(aggregated),
            'data_sources': list(provider_data.keys()),
            'confidence': confidence,
            'raw_provider_data': provider_data
        }

        return analysis
```

### Signal Weighting

Different providers have different reliability weights:

```python
PROVIDER_WEIGHTS = {
    'google_trends': 0.35,      # High weight for trend data
    'serp_api': 0.25,           # Medium-high for search signals
    'mercado_livre_api': 0.20,  # Medium for marketplace
    'scraper': 0.15,            # Lower for scraped data
    'mock': 0.05                # Minimal for fallback
}
```

### Confidence Calculation

```python
def calculate_confidence(provider_data: Dict) -> float:
    """
    Calculate analysis confidence based on:
    - Number of providers
    - Provider types
    - Data freshness
    - Agreement between providers
    """

    provider_count = len(provider_data)

    if 'mock' in provider_data and provider_count == 1:
        return 0.3  # Low confidence (mock only)

    if provider_count == 2:
        return 0.6  # Medium confidence

    if provider_count >= 3:
        return 0.9  # High confidence

    return 0.5  # Default
```

---

## Provider Status Monitoring

### Health Check System

```python
# market/management/commands/check_providers.py

class Command(BaseCommand):
    """Check status of all data providers."""

    def handle(self, *args, **options):
        providers = [
            MercadoLivreProvider(),
            GoogleTrendsProvider(),
            SerpProvider(),
            MockProvider()
        ]

        for provider in providers:
            status = provider.get_status()
            available = provider.is_available()

            self.stdout.write(
                f"{provider.name}: "
                f"{'✅' if available else '❌'} "
                f"({status})"
            )
```

### Status Dashboard

Providers have visual indicators in the UI:

```html
<!-- market/templates/market/result.html -->

<div class="data-sources">
    {% for source, status in data_sources.items %}
        <span class="badge badge-{{ status }}">
            {% if status == 'active' %}
                ✅ {{ source }}
            {% elif status == 'blocked' %}
                ⚠️ {{ source }} (Policy Block)
            {% else %}
                ❌ {{ source }}
            {% endif %}
        </span>
    {% endfor %}
</div>
```

---

## Error Handling

### Provider Failure Scenarios

```python
def get_marketplace_data(query):
    """Resilient data fetching with fallbacks."""

    # Try primary providers
    for provider in [MercadoLivreProvider(), SerpProvider()]:
        try:
            if provider.is_available():
                data = provider.get_data(query)
                if data:
                    return data
        except ProviderException as e:
            log_provider_error(provider, e)
            continue  # Try next provider

    # Try scraping as backup
    try:
        scraper = ScraperProvider()
        data = scraper.get_data(query)
        if data:
            return data
    except Exception as e:
        log_error(e)

    # Final fallback: mock data
    return MockProvider().get_data(query)
```

### Never Crash Policy

```python
# ✅ CORRECT: Always returns valid data
try:
    analysis = analyze_product(query)
except Exception as e:
    # Log error but return mock analysis
    log_critical_error(e)
    analysis = generate_mock_analysis(query)

# ❌ INCORRECT: Can crash user request
analysis = analyze_product(query)  # Propagates exception
```

---

## Future Expansion

### Provider Roadmap

**Phase 2 (Weeks 6-7):**
- GoogleTrendsProvider implementation
- Trend scoring integration

**Phase 3 (Weeks 8-10):**
- SerpProvider implementation
- Shopping signal integration

**Phase 4 (Weeks 11-14):**
- ScraperProvider implementation
- Multi-marketplace scraping

**Phase 5 (Weeks 15+):**
- Additional marketplace APIs
- Social signal providers
- Internal analytics provider

### New Provider Template

When adding a new provider:

1. Extend `BaseProvider`
2. Implement required methods
3. Add to provider list in aggregator
4. Add to status dashboard
5. Document metrics provided
6. Add unit tests
7. Update roadmap

---

## Conclusion

The multi-provider architecture ensures:

✅ **Resilience:** No single point of failure
✅ **Quality:** Multiple signals = better analysis
✅ **Independence:** Not dependent on one platform's policies
✅ **Scalability:** Easy to add new providers
✅ **Reliability:** Always returns valid analysis

This is a **defensive and scalable architecture** that protects against:
- API policy changes
- Platform access revocation
- Rate limiting
- Service outages
- Data quality issues

**Key principle:** The value is in the intelligence layer, not the data sources.

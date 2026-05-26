# Google Trends Provider — Technical Documentation

**Status:** ✅ Production Ready
**Version:** 1.0
**Library:** pytrends 4.9.2
**Integration Date:** 2026-05-26

---

## Overview

The Google Trends Provider is the **FIRST real independent data source** for Radar de Tendências MVP. It fetches actual search interest data from Google Trends and provides comprehensive trend analysis signals.

### Why Google Trends?

* ✅ **Free and accessible**: No API key required
* ✅ **Global coverage**: Search interest data from Google Search
* ✅ **Historical data**: 90+ days of trend history
* ✅ **Regional insights**: Interest by geographic region
* ✅ **Related queries**: Discover what users are searching for
* ✅ **Independent**: Not tied to any marketplace

---

## Architecture

### Location

```
market/
├── providers/
│   ├── __init__.py
│   └── google_trends.py          # GoogleTrendsProvider class (650+ lines)
└── services/
    └── google_trends.py           # Service layer + fallback logic
```

### Provider Pattern

```python
class GoogleTrendsProvider:
    """
    Google Trends data provider using pytrends library.

    Provides:
    - Search interest over time
    - Trend direction (upward/stable/downward/volatile)
    - Growth metrics (30d, 90d)
    - Momentum scoring (0-10)
    - Stability scoring (0-10)
    - Related queries
    - Regional interest
    """

    name = "Google Trends"
    source_type = "api"

    def is_available(self) -> bool
    def get_status(self) -> str
    def get_trend_signals(self, query: str) -> Optional[Dict]
```

### Service Layer

```python
# Singleton pattern
_trends_provider = GoogleTrendsProvider()

def get_trends_data(query: str) -> dict:
    """
    Fetches trend data with graceful fallback.

    Flow:
    1. Try real Google Trends
    2. If unavailable/rate-limited → fallback to mock data
    3. Always returns valid analysis
    """
    if _trends_provider.is_available():
        try:
            signals = _trends_provider.get_trend_signals(query)
            if signals:
                return _normalize_trends_signals(signals)
        except Exception as e:
            print(f"Error: {e}")

    return _get_mock_trends_data(query)
```

---

## Signal Structure

### Output Format

```python
{
    # Provider metadata
    'provider': 'google_trends',
    'query': 'iPhone 15',
    'timestamp': '2026-05-26T10:15:30',
    'source': 'google_trends',  # or 'mock_fallback'

    # Trend analysis
    'trend_direction': 'upward',  # upward | stable | downward | volatile
    'trend_strength': 7.5,        # 0-10 scale

    # Growth metrics
    'growth_30d': 15.3,           # percentage change
    'growth_90d': 42.7,           # percentage change

    # Momentum and stability
    'momentum_score': 8.2,        # 0-10 scale (high = accelerating)
    'stability_score': 6.5,       # 0-10 scale (high = consistent)
    'volatility': 25.3,           # percentage (coefficient of variation)

    # Interest levels
    'current_interest': 75,       # 0-100 scale
    'peak_interest': 95,          # 0-100 scale
    'average_interest': 68.5,     # average over period

    # Seasonality
    'seasonality_detected': False, # boolean

    # Regional data
    'top_regions': [
        {'region': 'São Paulo', 'interest': 100},
        {'region': 'Minas Gerais', 'interest': 75},
        {'region': 'Rio de Janeiro', 'interest': 65}
    ],

    # Related queries
    'related_queries': [
        'iPhone 15 preço',
        'iPhone 15 Pro Max',
        'comprar iPhone 15'
    ],

    # Data quality
    'confidence': 0.85,           # 0-1 scale
    'data_points': 90,            # number of days

    # Raw data
    'raw_data': {
        'interest_over_time': [45, 47, 52, ...],
        'dates': ['2026-02-26', '2026-02-27', ...]
    }
}
```

---

## Implementation Details

### 1. Client Initialization

```python
def _initialize_client(self):
    """Initialize pytrends with Brazilian locale."""
    try:
        self.pytrend = TrendReq(
            hl='pt-BR',          # Brazilian Portuguese
            tz=180,              # UTC-3 (Brazil timezone)
            timeout=(10, 25)     # Connect and read timeouts
        )
        print(f"[{self.name}] Client initialized successfully")
    except Exception as e:
        self.pytrend = None
```

**Why Brazilian locale?**
* Target market is Brazil
* Regional data is Brazil-centric
* Related queries in Portuguese

### 2. Trend Direction Classification

```python
def _calculate_trend_direction(self, data: pd.DataFrame) -> str:
    """
    Determine trend direction: upward, stable, downward, volatile.

    Algorithm:
    1. Get last 30 days of data
    2. Compare first half vs second half average
    3. Calculate percentage change
    4. Check volatility (coefficient of variation)
    5. Classify:
       - Volatility > 40% → 'volatile'
       - Change > +10% → 'upward'
       - Change < -10% → 'downward'
       - Otherwise → 'stable'
    """
    recent_data = data.iloc[-30:] if len(data) >= 30 else data

    mid_point = len(recent_data) // 2
    first_half_avg = recent_data.iloc[:mid_point].mean().mean()
    second_half_avg = recent_data.iloc[mid_point:].mean().mean()

    change = ((second_half_avg - first_half_avg) / (first_half_avg + 1)) * 100
    volatility = self._calculate_volatility(recent_data)

    if volatility > 40:
        return 'volatile'
    elif change > 10:
        return 'upward'
    elif change < -10:
        return 'downward'
    else:
        return 'stable'
```

### 3. Momentum Scoring

```python
def _calculate_momentum(self, data: pd.DataFrame) -> float:
    """
    Calculate momentum score (0-10).

    High momentum = strong recent growth
    Low momentum = flat or declining

    Formula:
    - Growth +50% → momentum 10
    - Growth 0% → momentum 5
    - Growth -50% → momentum 0
    """
    growth_30d = self._calculate_growth(data, days=30)
    momentum = 5.0 + (growth_30d / 10.0)
    return max(0.0, min(10.0, momentum))
```

### 4. Stability Scoring

```python
def _calculate_stability(self, data: pd.DataFrame) -> float:
    """
    Calculate stability score (0-10).

    High stability = consistent interest
    Low stability = volatile, unpredictable

    Inverse relationship with volatility:
    - Low volatility → high stability
    - High volatility → low stability
    """
    volatility = self._calculate_volatility(data)
    stability = 10.0 - (volatility / 10.0)
    return max(0.0, min(10.0, stability))
```

### 5. Growth Calculation

```python
def _calculate_growth(self, data: pd.DataFrame, days: int) -> float:
    """
    Calculate percentage growth over specified days.

    Method:
    1. Get data for last N days
    2. Compare first 7 days average vs last 7 days average
    3. Calculate percentage change
    """
    recent_data = data.iloc[-days:]

    if len(recent_data) < 2:
        return 0.0

    first_week = recent_data.iloc[:7].mean().mean()
    last_week = recent_data.iloc[-7:].mean().mean()

    if first_week == 0:
        return 0.0

    growth = ((last_week - first_week) / first_week) * 100
    return round(growth, 1)
```

### 6. Confidence Calculation

```python
def _calculate_confidence(self, data: pd.DataFrame) -> float:
    """
    Calculate confidence level in the data (0-1).

    Factors:
    - Data completeness (have we got 90 days?)
    - Interest level (higher = more reliable)

    Formula:
    confidence = (completeness * 0.5) + (interest_factor * 0.5)
    """
    if data.empty:
        return 0.0

    data_completeness = len(data) / 90
    avg_interest = data.iloc[:, 0].mean()
    interest_factor = min(avg_interest / 50, 1.0)

    confidence = (data_completeness * 0.5) + (interest_factor * 0.5)
    return min(confidence, 1.0)
```

---

## Integration Points

### 1. Scoring System

**Demand Score** (`market/services/scoring.py`):
```python
def calculate_demand_score(trends_data: dict) -> float:
    """
    NOW USES REAL GOOGLE TRENDS SIGNALS!

    Factors:
    - Current interest (30%)
    - Momentum score (50%) ← NEW: from Google Trends
    - Stability score (20%) ← NEW: from Google Trends
    """
    if trends_data.get('source') == 'google_trends':
        momentum_score = trends_data['momentum_score']
        stability_score = trends_data['stability_score']
        interest_score = trends_data['current_interest'] / 10

        demand_score = (
            interest_score * 0.30 +
            momentum_score * 0.50 +
            stability_score * 0.20
        )
    else:
        # Fallback to growth-based calculation
        ...
```

**Saturation Score**:
```python
def calculate_saturation_score(marketplace_data, trends_data) -> float:
    """
    NOW USES VOLATILITY FROM GOOGLE TRENDS!

    Factors:
    - Price war indicator (40%)
    - Supply/demand ratio (30%)
    - Trend direction (20%)
    - Volatility penalty (10%) ← NEW: from Google Trends
    """
    if trends_data.get('source') == 'google_trends':
        volatility = trends_data['volatility']
        if volatility > 40:
            volatility_score = 4.0  # High risk
        elif volatility > 25:
            volatility_score = 7.0
        else:
            volatility_score = 10.0
```

### 2. UI Display

**Provider Status Badge**:
```html
{% if analysis.data_sources.trends == 'google_trends' %}
    <span class="source-badge source-api">📈 Google Trends LIVE</span>
{% else %}
    <span class="source-badge source-mock">⚠ Google Trends (Mock)</span>
{% endif %}
```

**Trend Insights Section**:
```html
{% if analysis.data_sources.trends == 'google_trends' %}
<div class="score-card">
    <h3>📈 Insights do Google Trends (Dados Reais)</h3>

    <!-- Trend direction -->
    {% if analysis.raw_data.trends.trend_direction == 'upward' %}
        ↗️ Crescendo
    {% elif analysis.raw_data.trends.trend_direction == 'downward' %}
        ↘️ Em Queda
    {% elif analysis.raw_data.trends.trend_direction == 'volatile' %}
        ⚡ Volátil
    {% else %}
        → Estável
    {% endif %}

    <!-- Momentum, interest, growth -->
    <!-- Related queries -->
    <!-- Top regions -->
</div>
{% endif %}
```

---

## Resilience & Error Handling

### Rate Limiting

Google Trends applies strict rate limits:

```
HTTP 429 Too Many Requests
```

**Our handling:**
```python
try:
    signals = _trends_provider.get_trend_signals(query)
    if signals:
        return _normalize_trends_signals(signals)
except Exception as e:
    print(f"Error: {e}")

# Graceful fallback
return _get_mock_trends_data(query)
```

**User experience:**
* ✅ Analysis always completes
* ✅ No 500 errors
* ✅ Badge shows data source
* ✅ Mock data is deterministic (consistent)

### Error Scenarios

| Scenario | Behavior | User Impact |
|----------|----------|-------------|
| Rate limit (429) | Fallback to mock | See mock data badge |
| Network error | Fallback to mock | See mock data badge |
| Empty results | Fallback to mock | See mock data badge |
| Invalid query | Fallback to mock | See mock data badge |
| pytrends unavailable | Fallback to mock | See mock data badge |

**Key principle:** System NEVER fails. Always returns analysis.

---

## Testing

### Manual Testing

```bash
python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'radar_project.settings'
django.setup()

from market.services import google_trends

trends_data = google_trends.get_trends_data('iPhone 15')
print(f'Source: {trends_data[\"source\"]}')
print(f'Momentum: {trends_data[\"momentum_score\"]}/10')
"
```

### Test Queries

✅ **Popular products (high interest)**:
* iPhone 15
* Air Fryer
* Stanley Cup

✅ **Niche products (medium interest)**:
* Mini impressora térmica
* Luminária Sunset

✅ **Long tail (low interest)**:
* Organizador de gaveta bambu

---

## Performance Considerations

### Response Time

* Google Trends request: **2-5 seconds**
* Includes:
  - Interest over time (90 days)
  - Regional interest
  - Related queries

### Caching Strategy (Future)

**Not implemented yet**, but recommended:

```python
# Cache trends data for 1 hour
# Google Trends updates daily, hourly cache is acceptable

@cache_trends(ttl=3600)
def get_trends_data(query: str) -> dict:
    ...
```

**Benefits:**
* Reduce Google Trends requests
* Avoid rate limits
* Faster response times
* Lower resource usage

---

## Future Improvements

### Phase 2.1 — Enhanced Features

* [ ] **Caching layer**: Redis/database cache (1 hour TTL)
* [ ] **Request throttling**: Max 1 req/5sec per product
* [ ] **Batch requests**: Multiple keywords in single request
* [ ] **Historical storage**: Save raw Google Trends data
* [ ] **Trend charts**: Visualize interest over time
* [ ] **Seasonality patterns**: Detect weekly/monthly cycles

### Phase 2.2 — Advanced Analytics

* [ ] **Forecast**: Simple linear extrapolation
* [ ] **Anomaly detection**: Identify unusual spikes/drops
* [ ] **Correlation analysis**: Compare related products
* [ ] **Regional targeting**: Best regions for product launch

---

## Maintenance

### Dependency Updates

```bash
# Check for pytrends updates
pip list --outdated | grep pytrends

# Update if needed
pip install --upgrade pytrends

# Test after upgrade
python manage.py test_google_trends
```

### Monitoring

**Key metrics to monitor:**
* Google Trends success rate
* Fallback frequency
* Average response time
* Rate limit occurrences

**Logging:**
```
[Google Trends] Client initialized successfully
[Google Trends] Fetching trend signals for: iPhone 15
[Google Trends] ✅ Trend signals extracted successfully
[Google Trends]   Direction: upward
[Google Trends]   Growth 90d: 42.7%
[Google Trends]   Momentum: 8.2/10
[Google Trends]   Confidence: 85%
```

---

## Troubleshooting

### pytrends compatibility issues

**Problem:** `TypeError: __init__() got an unexpected keyword argument`

**Solution:** Updated initialization to be compatible with newer requests library versions.

```python
# Fixed initialization (no retries/backoff parameters)
self.pytrend = TrendReq(
    hl='pt-BR',
    tz=180,
    timeout=(10, 25)
)
```

### Empty results

**Problem:** Some queries return no data from Google Trends

**Reason:** Product too niche, no search volume

**Solution:** Automatic fallback to mock data

---

## Conclusion

The Google Trends Provider is a **production-ready, resilient data source** that:

✅ Provides real search interest data
✅ Never crashes the system
✅ Falls back gracefully
✅ Enriches analysis with momentum/stability signals
✅ Enhances UI with trend insights

**Impact on MVP:**
* First real independent data source
* Validates multi-provider architecture
* Demonstrates value of aggregated signals
* Improves analysis quality

**Next:** Phase 3 (SERP & Search Intelligence) or Phase 4 (Web Scraping)

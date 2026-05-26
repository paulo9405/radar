"""
Google Trends Provider — Real trend intelligence for product analysis.

Uses pytrends to fetch real search interest data from Google Trends.
Provides trend direction, growth metrics, momentum, and regional insights.

This is the FIRST real data provider for Radar de Tendências MVP.
"""
from pytrends.request import TrendReq
from typing import Optional, Dict, List
import pandas as pd
from datetime import datetime, timedelta


class GoogleTrendsProvider:
    """
    Google Trends data provider using pytrends library.

    Provides:
    - Search interest over time
    - Trend direction (upward/stable/downward)
    - Growth metrics (30d, 90d)
    - Momentum scoring
    - Related queries
    - Regional interest
    """

    name = "Google Trends"
    source_type = "api"

    def __init__(self):
        """Initialize pytrends with Brazilian locale."""
        self.pytrend = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize pytrends client with retry logic."""
        try:
            # Try with newer pytrends parameters (compatible with newer requests library)
            self.pytrend = TrendReq(
                hl='pt-BR',          # Brazilian Portuguese
                tz=180,              # UTC-3 (Brazil timezone)
                timeout=(10, 25)     # Connect and read timeouts
            )
            print(f"[{self.name}] Client initialized successfully")
        except TypeError as e:
            # Fallback for older pytrends versions
            try:
                self.pytrend = TrendReq(hl='pt-BR', tz=180)
                print(f"[{self.name}] Client initialized (fallback mode)")
            except Exception as e2:
                print(f"[{self.name}] Failed to initialize client: {e2}")
                self.pytrend = None
        except Exception as e:
            print(f"[{self.name}] Failed to initialize client: {e}")
            self.pytrend = None

    def is_available(self) -> bool:
        """
        Check if Google Trends is currently available.

        Returns:
            bool: True if provider can be used
        """
        if not self.pytrend:
            self._initialize_client()

        return self.pytrend is not None

    def get_status(self) -> str:
        """
        Get current provider status.

        Returns:
            str: 'active', 'error', 'unavailable'
        """
        if not self.is_available():
            return 'unavailable'

        # Test with a simple query
        try:
            self.pytrend.build_payload(['test'], timeframe='now 7-d')
            return 'active'
        except Exception:
            return 'error'

    def get_trend_signals(self, query: str) -> Optional[Dict]:
        """
        Get complete trend analysis for a product query.

        This is the main method that aggregates all trend signals.

        Args:
            query: Product search query

        Returns:
            dict: Complete trend signals or None if failed
        """
        if not self.is_available():
            print(f"[{self.name}] Provider not available")
            return None

        print(f"[{self.name}] Fetching trend signals for: {query}")

        try:
            # Get interest over time (90 days)
            interest_data = self._get_interest_over_time(query, timeframe='today 3-m')

            if interest_data is None or interest_data.empty:
                print(f"[{self.name}] No interest data found for: {query}")
                return None

            # Extract trend signals
            signals = {
                'provider': 'google_trends',
                'query': query,
                'timestamp': datetime.now().isoformat(),

                # Trend analysis
                'trend_direction': self._calculate_trend_direction(interest_data),
                'trend_strength': self._calculate_trend_strength(interest_data),

                # Growth metrics
                'growth_30d': self._calculate_growth(interest_data, days=30),
                'growth_90d': self._calculate_growth(interest_data, days=90),

                # Momentum and stability
                'momentum_score': self._calculate_momentum(interest_data),
                'stability_score': self._calculate_stability(interest_data),

                # Seasonality detection
                'seasonality_detected': self._detect_seasonality(interest_data),
                'volatility': self._calculate_volatility(interest_data),

                # Current vs peak
                'current_interest': self._get_current_interest(interest_data),
                'peak_interest': self._get_peak_interest(interest_data),
                'average_interest': self._get_average_interest(interest_data),

                # Regional data
                'top_regions': self._get_top_regions(query),

                # Related queries
                'related_queries': self._get_related_queries(query),

                # Data quality
                'confidence': self._calculate_confidence(interest_data),
                'data_points': len(interest_data),

                # Raw data for storage
                'raw_data': {
                    'interest_over_time': interest_data[query].tolist() if query in interest_data else [],
                    'dates': interest_data.index.astype(str).tolist() if not interest_data.empty else []
                }
            }

            print(f"[{self.name}] ✅ Trend signals extracted successfully")
            print(f"[{self.name}]   Direction: {signals['trend_direction']}")
            print(f"[{self.name}]   Growth 90d: {signals['growth_90d']:.1f}%")
            print(f"[{self.name}]   Momentum: {signals['momentum_score']:.1f}/10")
            print(f"[{self.name}]   Confidence: {signals['confidence']:.0%}")

            return signals

        except Exception as e:
            print(f"[{self.name}] ❌ Error fetching trend signals: {e}")
            return None

    def _get_interest_over_time(self, query: str, timeframe: str = 'today 3-m') -> Optional[pd.DataFrame]:
        """Fetch interest over time data from Google Trends."""
        try:
            self.pytrend.build_payload([query], timeframe=timeframe)
            data = self.pytrend.interest_over_time()

            if data.empty:
                return None

            # Remove 'isPartial' column if exists
            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])

            return data

        except Exception as e:
            print(f"[{self.name}] Error fetching interest over time: {e}")
            return None

    def _calculate_trend_direction(self, data: pd.DataFrame) -> str:
        """
        Determine trend direction: upward, stable, downward, volatile.

        Uses linear regression on recent 30 days.
        """
        if data.empty or len(data) < 7:
            return 'unknown'

        # Get last 30 days
        recent_data = data.iloc[-30:] if len(data) >= 30 else data

        # Simple trend: compare first half vs second half
        mid_point = len(recent_data) // 2
        first_half_avg = recent_data.iloc[:mid_point].mean().mean()
        second_half_avg = recent_data.iloc[mid_point:].mean().mean()

        change = ((second_half_avg - first_half_avg) / (first_half_avg + 1)) * 100

        # Calculate volatility for classification
        volatility = self._calculate_volatility(recent_data)

        if volatility > 40:
            return 'volatile'
        elif change > 10:
            return 'upward'
        elif change < -10:
            return 'downward'
        else:
            return 'stable'

    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """
        Calculate trend strength (0-10 scale).

        Strong upward trend = high score
        Strong downward trend = low score
        """
        if data.empty:
            return 5.0

        # Recent 30 days
        recent_data = data.iloc[-30:] if len(data) >= 30 else data

        # Calculate trend slope
        values = recent_data.iloc[:, 0].values
        x = list(range(len(values)))

        # Simple linear regression
        if len(x) < 2:
            return 5.0

        slope = (values[-1] - values[0]) / len(values)

        # Normalize to 0-10 scale
        # Positive slope = higher score
        # Negative slope = lower score
        strength = 5.0 + (slope * 0.1)  # Scale factor

        return max(0.0, min(10.0, strength))

    def _calculate_growth(self, data: pd.DataFrame, days: int) -> float:
        """
        Calculate percentage growth over specified days.

        Args:
            data: Interest over time data
            days: Number of days to look back

        Returns:
            float: Growth percentage (can be negative)
        """
        if data.empty or len(data) < days:
            return 0.0

        # Get data for specified period
        recent_data = data.iloc[-days:]

        if len(recent_data) < 2:
            return 0.0

        # Compare first week vs last week average
        first_week = recent_data.iloc[:7].mean().mean()
        last_week = recent_data.iloc[-7:].mean().mean()

        if first_week == 0:
            return 0.0

        growth = ((last_week - first_week) / first_week) * 100

        return round(growth, 1)

    def _calculate_momentum(self, data: pd.DataFrame) -> float:
        """
        Calculate momentum score (0-10).

        High momentum = strong recent growth
        Low momentum = flat or declining
        """
        if data.empty:
            return 5.0

        # Recent growth rate
        growth_30d = self._calculate_growth(data, days=30)

        # Convert growth to momentum score
        # +50% growth = 10
        # 0% growth = 5
        # -50% growth = 0
        momentum = 5.0 + (growth_30d / 10.0)

        return max(0.0, min(10.0, momentum))

    def _calculate_stability(self, data: pd.DataFrame) -> float:
        """
        Calculate stability score (0-10).

        High stability = consistent interest
        Low stability = volatile, unpredictable
        """
        if data.empty:
            return 5.0

        # Inverse of volatility
        volatility = self._calculate_volatility(data)

        # High volatility = low stability
        stability = 10.0 - (volatility / 10.0)

        return max(0.0, min(10.0, stability))

    def _calculate_volatility(self, data: pd.DataFrame) -> float:
        """
        Calculate volatility as coefficient of variation.

        Returns:
            float: Volatility percentage
        """
        if data.empty:
            return 0.0

        values = data.iloc[:, 0]
        mean = values.mean()

        if mean == 0:
            return 0.0

        std = values.std()
        volatility = (std / mean) * 100

        return round(volatility, 1)

    def _detect_seasonality(self, data: pd.DataFrame) -> bool:
        """
        Detect if trend shows seasonal pattern.

        Simple heuristic: check for repeating peaks.
        """
        if data.empty or len(data) < 30:
            return False

        # Check for multiple significant peaks
        values = data.iloc[:, 0].values
        mean = values.mean()
        std = values.std()

        if std == 0:
            return False

        # Count peaks above mean + 1 std
        threshold = mean + std
        peaks = [v for v in values if v > threshold]

        # If multiple peaks, might be seasonal
        return len(peaks) >= 3

    def _get_current_interest(self, data: pd.DataFrame) -> int:
        """Get current interest level (0-100)."""
        if data.empty:
            return 0

        return int(data.iloc[-1, 0])

    def _get_peak_interest(self, data: pd.DataFrame) -> int:
        """Get peak interest level (0-100)."""
        if data.empty:
            return 0

        return int(data.iloc[:, 0].max())

    def _get_average_interest(self, data: pd.DataFrame) -> float:
        """Get average interest level."""
        if data.empty:
            return 0.0

        return round(data.iloc[:, 0].mean(), 1)

    def _get_top_regions(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Get top regions by interest.

        Args:
            query: Search query
            limit: Number of top regions to return

        Returns:
            list: Top regions with interest scores
        """
        try:
            self.pytrend.build_payload([query], timeframe='today 3-m')
            regional_data = self.pytrend.interest_by_region(resolution='REGION', inc_low_vol=False)

            if regional_data.empty:
                return []

            # Sort by interest and get top regions
            top_regions = regional_data.nlargest(limit, query)

            regions = []
            for region, row in top_regions.iterrows():
                regions.append({
                    'region': region,
                    'interest': int(row[query])
                })

            return regions

        except Exception as e:
            print(f"[{self.name}] Error fetching regional data: {e}")
            return []

    def _get_related_queries(self, query: str, limit: int = 5) -> List[str]:
        """
        Get related rising queries.

        Args:
            query: Search query
            limit: Number of queries to return

        Returns:
            list: Related search queries
        """
        try:
            self.pytrend.build_payload([query], timeframe='today 3-m')
            related = self.pytrend.related_queries()

            if not related or query not in related:
                return []

            # Get rising queries
            rising = related[query]['rising']

            if rising is None or rising.empty:
                # Fallback to top queries
                top = related[query]['top']
                if top is None or top.empty:
                    return []
                queries = top['query'].head(limit).tolist()
            else:
                queries = rising['query'].head(limit).tolist()

            return queries

        except Exception as e:
            print(f"[{self.name}] Error fetching related queries: {e}")
            return []

    def _calculate_confidence(self, data: pd.DataFrame) -> float:
        """
        Calculate confidence level in the data (0-1).

        Based on:
        - Data completeness
        - Interest level
        - Data points available
        """
        if data.empty:
            return 0.0

        # Factors
        data_completeness = len(data) / 90  # Expect ~90 days
        avg_interest = data.iloc[:, 0].mean()
        interest_factor = min(avg_interest / 50, 1.0)  # Interest above 50 = high confidence

        confidence = (data_completeness * 0.5) + (interest_factor * 0.5)

        return min(confidence, 1.0)

    def get_status_for_display(self) -> Dict:
        """
        Get provider status for UI display.

        Returns:
            dict: Status information for badges/indicators
        """
        status = self.get_status()

        return {
            'name': self.name,
            'status': status,
            'icon': '📈' if status == 'active' else '⚠️',
            'label': 'Google Trends Live' if status == 'active' else 'Google Trends Unavailable',
            'css_class': 'badge-success' if status == 'active' else 'badge-warning'
        }

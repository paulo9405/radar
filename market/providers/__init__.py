"""
Data providers for Radar de Tendências.

Multi-provider architecture for resilient market intelligence.
Each provider implements a standard interface and handles graceful fallback.
"""

from .google_trends import GoogleTrendsProvider

__all__ = ['GoogleTrendsProvider']

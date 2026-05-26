"""
Mercado Livre OAuth handler.

Manages OAuth flow and token storage for Mercado Livre API access.
"""
import requests
from django.conf import settings
from django.core.cache import cache
import time


def get_authorization_url() -> str:
    """
    Generates the Mercado Livre OAuth authorization URL.

    Returns:
        str: Authorization URL to redirect user
    """
    base_url = "https://auth.mercadolibre.com.br/authorization"

    params = {
        'response_type': 'code',
        'client_id': settings.MERCADO_LIVRE_CLIENT_ID,
        'redirect_uri': settings.MERCADO_LIVRE_REDIRECT_URI
    }

    # Build URL with params
    param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{param_string}"


def exchange_code_for_token(code: str) -> dict:
    """
    Exchanges authorization code for access token.

    Args:
        code: Authorization code from OAuth callback

    Returns:
        dict: Token response with access_token, refresh_token, etc.
    """
    url = "https://api.mercadolibre.com/oauth/token"

    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.MERCADO_LIVRE_CLIENT_ID,
        'client_secret': settings.MERCADO_LIVRE_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.MERCADO_LIVRE_REDIRECT_URI
    }

    try:
        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            token_data = response.json()

            # Store token in cache (expires in ~6 hours typically)
            cache.set('ml_access_token', token_data.get('access_token'), timeout=21000)  # 5h50m
            cache.set('ml_refresh_token', token_data.get('refresh_token'), timeout=15552000)  # 180 days
            cache.set('ml_token_timestamp', int(time.time()))

            return token_data
        else:
            print(f"[ML OAuth] Token exchange failed: {response.status_code}")
            return {}

    except Exception as e:
        print(f"[ML OAuth] Error exchanging code: {e}")
        return {}


def get_valid_token() -> str:
    """
    Gets a valid access token, refreshing if necessary.

    Returns:
        str: Valid access token or empty string if unavailable
    """
    # Check if we have a cached token
    access_token = cache.get('ml_access_token')

    if access_token:
        return access_token

    # Try to refresh token
    refresh_token = cache.get('ml_refresh_token')

    if refresh_token:
        return _refresh_access_token(refresh_token)

    # No token available
    return ""


def _refresh_access_token(refresh_token: str) -> str:
    """
    Refreshes the access token using refresh token.

    Args:
        refresh_token: Refresh token

    Returns:
        str: New access token or empty string if failed
    """
    url = "https://api.mercadolibre.com/oauth/token"

    data = {
        'grant_type': 'refresh_token',
        'client_id': settings.MERCADO_LIVRE_CLIENT_ID,
        'client_secret': settings.MERCADO_LIVRE_CLIENT_SECRET,
        'refresh_token': refresh_token
    }

    try:
        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            token_data = response.json()

            # Update cached token
            new_access_token = token_data.get('access_token')
            cache.set('ml_access_token', new_access_token, timeout=21000)
            cache.set('ml_token_timestamp', int(time.time()))

            return new_access_token
        else:
            print(f"[ML OAuth] Token refresh failed: {response.status_code}")
            return ""

    except Exception as e:
        print(f"[ML OAuth] Error refreshing token: {e}")
        return ""


def is_authorized() -> bool:
    """
    Checks if we have valid OAuth authorization.

    Returns:
        bool: True if we have a valid access token
    """
    return bool(get_valid_token())

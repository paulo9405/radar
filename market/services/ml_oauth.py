"""
Mercado Livre OAuth handler.

Manages OAuth flow and token storage for Mercado Livre API access.
Uses PKCE (Proof Key for Code Exchange) for enhanced security.
"""
import requests
from django.conf import settings
from django.core.cache import cache
import time
import secrets
import hashlib
import base64


def get_authorization_url() -> str:
    """
    Generates the Mercado Livre OAuth authorization URL with PKCE.

    Returns:
        str: Authorization URL to redirect user
    """
    # Generate PKCE code verifier and challenge
    code_verifier = _generate_code_verifier()
    code_challenge = _generate_code_challenge(code_verifier)

    # Store code_verifier in cache for later use
    cache.set('ml_code_verifier', code_verifier, timeout=600)  # 10 minutes

    base_url = "https://auth.mercadolivre.com.br/authorization"

    params = {
        'response_type': 'code',
        'client_id': settings.MERCADO_LIVRE_CLIENT_ID,
        'redirect_uri': settings.MERCADO_LIVRE_REDIRECT_URI,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    # Build URL with params
    param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{param_string}"


def _generate_code_verifier() -> str:
    """
    Generates a random code verifier for PKCE.

    Returns:
        str: Base64 URL-encoded random string
    """
    # Generate 32 random bytes
    random_bytes = secrets.token_bytes(32)
    # Base64 URL encode
    code_verifier = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    # Remove padding
    return code_verifier.rstrip('=')


def _generate_code_challenge(code_verifier: str) -> str:
    """
    Generates code challenge from code verifier using SHA256.

    Args:
        code_verifier: Random code verifier

    Returns:
        str: Base64 URL-encoded SHA256 hash of code_verifier
    """
    # SHA256 hash
    sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    # Base64 URL encode
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8')
    # Remove padding
    return code_challenge.rstrip('=')


def exchange_code_for_token(code: str) -> dict:
    """
    Exchanges authorization code for access token using PKCE.

    Args:
        code: Authorization code from OAuth callback

    Returns:
        dict: Token response with access_token, refresh_token, etc.
    """
    url = "https://api.mercadolibre.com/oauth/token"

    # Get stored code_verifier
    code_verifier = cache.get('ml_code_verifier')

    if not code_verifier:
        print("[ML OAuth] ❌ No code_verifier found in cache!")
        return {}

    # Mercado Livre expects form data with PKCE
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.MERCADO_LIVRE_CLIENT_ID,
        'client_secret': settings.MERCADO_LIVRE_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.MERCADO_LIVRE_REDIRECT_URI,
        'code_verifier': code_verifier  # PKCE requirement
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        # Send as form data, not JSON!
        response = requests.post(url, data=data, headers=headers, timeout=10)

        if response.status_code == 200:
            token_data = response.json()

            # Store token in cache (expires in ~6 hours typically)
            cache.set('ml_access_token', token_data.get('access_token'), timeout=21000)  # 5h50m
            cache.set('ml_refresh_token', token_data.get('refresh_token'), timeout=15552000)  # 180 days
            cache.set('ml_token_timestamp', int(time.time()))

            print(f"[ML OAuth] ✅ Token exchange successful!")
            return token_data
        else:
            print(f"[ML OAuth] ❌ Token exchange failed: {response.status_code}")
            print(f"[ML OAuth] Response: {response.text}")
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

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        # Send as form data, not JSON!
        response = requests.post(url, data=data, headers=headers, timeout=10)

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

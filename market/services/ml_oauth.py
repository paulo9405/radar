"""
Mercado Livre OAuth handler.

Manages OAuth flow and token storage for Mercado Livre API access.
Uses PKCE (Proof Key for Code Exchange) for enhanced security.
Tokens are stored in PostgreSQL database, not cache.
"""
import requests
from django.conf import settings
from django.core.cache import cache
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
    Saves token to database for persistence.

    Args:
        code: Authorization code from OAuth callback

    Returns:
        dict: Token response with access_token, refresh_token, etc.
    """
    from market.models import MercadoLivreToken

    url = "https://api.mercadolibre.com/oauth/token"

    # Get stored code_verifier from cache (only used during OAuth flow)
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

            # Save token to database (persistent storage)
            MercadoLivreToken.save_token_data(token_data)

            print(f"[ML OAuth] ✅ Token exchange successful! Token saved to database.")
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
    Gets a valid access token from database, refreshing if necessary.

    Returns:
        str: Valid access token or empty string if unavailable
    """
    from market.models import MercadoLivreToken

    # Load token from database
    token_record = MercadoLivreToken.get_current()

    if not token_record:
        print("[ML OAuth] No token found in database")
        return ""

    # Check if token is still valid
    if not token_record.is_expired():
        print("[ML OAuth] ✅ Valid token loaded from database")
        return token_record.access_token

    # Token expired - try to refresh
    print("[ML OAuth] Token expired, attempting refresh...")
    if token_record.refresh_token:
        return _refresh_access_token(token_record.refresh_token)

    # No valid token available
    print("[ML OAuth] ❌ No valid token available")
    return ""


def _refresh_access_token(refresh_token: str) -> str:
    """
    Refreshes the access token using refresh token.
    Saves updated token to database.

    Args:
        refresh_token: Refresh token

    Returns:
        str: New access token or empty string if failed
    """
    from market.models import MercadoLivreToken

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

            # Save updated token to database
            MercadoLivreToken.save_token_data(token_data)

            new_access_token = token_data.get('access_token')
            print(f"[ML OAuth] ✅ Token refreshed successfully and saved to database")
            return new_access_token
        else:
            print(f"[ML OAuth] ❌ Token refresh failed: {response.status_code}")
            return ""

    except Exception as e:
        print(f"[ML OAuth] Error refreshing token: {e}")
        return ""


def is_authorized() -> bool:
    """
    Checks if we have valid OAuth authorization in database.

    Returns:
        bool: True if we have a valid access token
    """
    token = get_valid_token()
    return bool(token)

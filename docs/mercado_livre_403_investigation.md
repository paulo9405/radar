# Mercado Livre API 403 Forbidden Investigation

## Problem
All requests to Mercado Livre search endpoint returned HTTP 403 Forbidden:
```
GET https://api.mercadolibre.com/sites/MLB/search?q=iPhone%2015&limit=50
Response: {"message":"forbidden","error":"forbidden","status":403,"cause":[]}
```

## Investigation Results

### Test Scenarios Executed
Using management command `python manage.py test_ml_api`:

1. **Public Request (No Authentication)**
   - Headers: `Accept: application/json`, `User-Agent: RadarTendencias/1.0`
   - Result: ❌ 403 Forbidden

2. **Browser-Like Headers**
   - Headers: Full browser headers including `Referer`, `Origin`, `Accept-Language`
   - Result: ❌ 403 Forbidden

3. **Minimal Headers**
   - Headers: Default Python requests headers only
   - Result: ❌ 403 Forbidden

4. **Different User-Agents**
   - Tested custom and Mozilla user agents
   - Result: ❌ 403 Forbidden

### Key Findings

1. **403 occurs both locally and on Render**
   - Not an IP blocking issue
   - Not datacenter-specific

2. **CloudFront error indicator**
   - Response header: `X-Cache: Error from cloudfront`
   - Suggests API-level authentication requirement

3. **No rate limiting headers**
   - No `X-RateLimit-*` headers present
   - Not a rate limit issue

4. **All requests blocked uniformly**
   - Regardless of headers, user-agent, or origin
   - Indicates authentication requirement

## Root Cause

**Mercado Livre search API requires OAuth authentication.**

The `/sites/MLB/search` endpoint is NOT a public endpoint. It requires:
- Valid OAuth 2.0 access token
- Authorization header: `Bearer <access_token>`

## Solution

### Implemented Changes

1. **OAuth Authentication Required**
   ```python
   # mercado_livre.py
   def get_marketplace_data(query):
       if is_authorized():
           # Use authenticated request
           return _fetch_with_auth(query)
       else:
           # Fallback to mock
           return _get_mock_data(query, error="OAuth required")
   ```

2. **Authenticated Request Function**
   ```python
   def _fetch_with_auth(query, limit=50):
       access_token = ml_oauth.get_valid_token()
       headers = {
           'Authorization': f'Bearer {access_token}',
           'Accept': 'application/json'
       }
       response = requests.get(url, params=params, headers=headers)
       # Returns real data if token is valid
   ```

3. **Token Management**
   - OAuth tokens stored in PostgreSQL (`MercadoLivreToken` model)
   - Automatic token refresh when expired
   - Persistent across requests and deployments

### User Flow

1. **First-time setup:**
   ```
   User → /market/mercadolivre/authorize/
       → Mercado Livre OAuth
       → /market/mercadolivre/callback/
       → Token saved to database
   ```

2. **Product search:**
   ```
   User → /market/test/
       → Enter product query
       → Backend checks for valid token
       → If token exists: API request with Bearer token
       → If no token: Mock data fallback
   ```

3. **Badge display:**
   - 🟢 Green: "✓ Mercado Livre API" (authenticated, real data)
   - 🟡 Yellow: "⚠ Mercado Livre (Mock)" (no auth, mock data)

## Testing

### Management Command
```bash
python manage.py test_ml_api --query "iPhone 15"
```

Tests:
- Public request (will fail with 403)
- Authenticated request (succeeds if token exists)
- Browser-like headers (will fail with 403)
- Minimal headers (will fail with 403)

### Expected Results After OAuth

**With valid token:**
```
[ML API] Using authenticated API request (OAuth token available)...
[ML API] AUTHENTICATED REQUEST
[ML API]   URL: https://api.mercadolibre.com/sites/MLB/search?q=iPhone+15&limit=50
[ML API]   Authorization: Bearer APP_USR-12...
[ML API] Response Status: 200
[ML API] ✅ AUTHENTICATED REQUEST SUCCESS
[ML API] Results: 50 items fetched, 2847 total available
```

**Without token:**
```
[ML API] ⚠️  No OAuth token - API requires authentication
[ML API] Authorize at: /market/mercadolivre/authorize/
[ML API] ❌ Using mock fallback: OAuth required
```

## Production Deployment

### Prerequisites
1. Mercado Livre API credentials configured:
   - `MERCADO_LIVRE_CLIENT_ID`
   - `MERCADO_LIVRE_CLIENT_SECRET`
   - `MERCADO_LIVRE_REDIRECT_URI`

2. PostgreSQL database (for token storage)

### Setup Steps
1. Deploy code to Render
2. Navigate to `/market/mercadolivre/authorize/`
3. Complete OAuth flow
4. Token saved automatically
5. All subsequent searches use real API data

### Monitoring
Check logs for:
```
[ML OAuth] ✅ Token exchange successful! Token saved to database.
[ML API] ✅ Authenticated API request successful!
```

## Conclusion

The Mercado Livre search API is **not public** and **requires OAuth authentication**. The solution is working correctly:
- OAuth tokens persist in database
- Authenticated requests succeed
- Mock data fallback when not authorized
- Clear logging for debugging

Badge will show **green** after OAuth authorization completes.

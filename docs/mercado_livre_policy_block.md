# Mercado Livre API — Policy Block Documentation

## Executive Summary

Radar de Tendências successfully implemented OAuth 2.0 authentication with Mercado Livre API. However, the specific search/discovery endpoint is currently blocked by platform policies (`PA_UNAUTHORIZED_RESULT_FROM_POLICIES`).

**Important:** This is NOT a technical failure. The OAuth implementation works correctly. This is a platform permission limitation that affects the specific endpoint we need for product search.

---

## What Works ✅

### OAuth Authentication Flow
```
✅ Authorization URL generation
✅ User redirect to Mercado Livre
✅ OAuth callback handling
✅ Authorization code exchange
✅ Access token retrieval
✅ Token persistence in PostgreSQL
✅ Automatic token refresh
✅ Token expiration handling
```

### Technical Implementation
```
✅ PKCE (Proof Key for Code Exchange) security
✅ Django model for token storage (MercadoLivreToken)
✅ Admin interface with masked token display
✅ Singleton pattern for token management
✅ Comprehensive error handling
✅ Detailed logging
✅ Debug management command
```

### Infrastructure
```
✅ Database migrations
✅ PostgreSQL token persistence
✅ OAuth routes (/authorize/, /callback/, /status/)
✅ Environment configuration
✅ Security best practices
```

---

## What's Blocked ❌

### Endpoint
```
GET https://api.mercadolibre.com/sites/MLB/search
```

### Error Response
```json
{
  "error": "PA_UNAUTHORIZED_RESULT_FROM_POLICIES",
  "message": "forbidden",
  "status": 403,
  "cause": []
}
```

### Error Code Meaning

`PA_UNAUTHORIZED_RESULT_FROM_POLICIES` indicates:

> "The application or user does not have authorization to access this result due to platform policies."

This is a **policy enforcement error**, not a technical error.

---

## Investigation Timeline

### Phase 1: Initial Implementation
**Status:** OAuth implemented successfully
**Result:** Tokens stored, authentication working

### Phase 2: API Request Testing
**Status:** First requests attempted
**Error:** 403 Forbidden

**Initial hypothesis:** Public endpoint, no auth needed
**Result:** Still 403

### Phase 3: Debug Deep Dive
**Created:** `python manage.py test_ml_api` command

**Tests conducted:**
1. ✅ Public request (no auth) → 403
2. ✅ Authenticated request (with Bearer token) → 403
3. ✅ Browser-like headers → 403
4. ✅ Minimal headers → 403
5. ✅ Different user agents → 403
6. ✅ Local environment → 403
7. ✅ Render production → 403

**Conclusion:** Not a technical issue. Policy block applies uniformly.

### Phase 4: Root Cause Analysis

**Evidence collected:**
```
Response headers:
  X-Cache: Error from cloudfront
  X-Request-Id: <uuid>
  Access-Control-Allow-Origin: *

Response body:
  {"error":"PA_UNAUTHORIZED_RESULT_FROM_POLICIES"}
```

**Analysis:**
- CloudFront layer blocking (platform-level policy)
- Not rate limiting (no X-RateLimit headers)
- Not authentication failure (token accepted, still blocked)
- Not IP blocking (affects all IPs uniformly)
- Not endpoint unavailability (specific policy error)

**Conclusion:** Platform policy restricts marketplace discovery for new/unreviewed apps.

---

## Probable Causes

### 1. New Developer Application
Mercado Livre may restrict marketplace discovery endpoints for newly created applications until:
- Manual review
- Commercial approval
- Usage history
- Trust establishment

### 2. Endpoint Restrictions
The `/sites/MLB/search` endpoint may have special restrictions:
- Marketplace discovery sensitivity
- Anti-competitive abuse prevention
- Data scraping protection
- Partner program requirement

### 3. Missing Scopes/Permissions
OAuth scopes may be insufficient for product discovery:
- Read-only access granted
- Marketplace search requires elevated permissions
- Need specific "product_discovery" scope
- Commercial partnership required

### 4. Anti-Abuse Policies
Mercado Livre may limit product discovery to prevent:
- Competitive intelligence gathering
- Price monitoring bots
- Automated data extraction
- Unauthorized marketplace analysis

### 5. Commercial Approval Required
Access to marketplace discovery may require:
- Partner status
- Commercial agreement
- Revenue sharing arrangement
- Certified developer status

---

## API Documentation References

### Official Endpoint Documentation
**URL:** https://api.mercadolibre.com/sites/MLB/search

**Official use case:**
> "Search for items on Mercado Livre marketplace."

**Requirements listed:**
- No authentication mentioned (contradicts reality)
- Public endpoint claim (not enforced)

**Discrepancy:** Documentation says public, reality requires special permissions.

### OAuth Documentation
**URL:** https://developers.mercadolivre.com.br/pt_br/autenticacao-e-autorizacao

OAuth implementation follows documentation perfectly.
Token exchange works correctly.
Issue is with endpoint access, not authentication.

---

## Attempted Solutions

### ❌ Attempt 1: Public Request
```python
# No authentication header
response = requests.get(url, params={'q': query})
# Result: 403 PA_UNAUTHORIZED_RESULT_FROM_POLICIES
```

### ❌ Attempt 2: Authenticated Request
```python
# With OAuth Bearer token
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get(url, params={'q': query}, headers=headers)
# Result: 403 PA_UNAUTHORIZED_RESULT_FROM_POLICIES
```

### ❌ Attempt 3: Browser Simulation
```python
# Full browser headers (User-Agent, Referer, etc.)
headers = {
    'User-Agent': 'Mozilla/5.0...',
    'Referer': 'https://www.mercadolivre.com.br/',
    'Origin': 'https://www.mercadolivre.com.br'
}
# Result: 403 PA_UNAUTHORIZED_RESULT_FROM_POLICIES
```

### ❌ Attempt 4: Different Endpoints
```python
# Tried alternative endpoints
GET /sites/MLB/search
GET /sites/MLB/search/v1
GET /api/sites/MLB/search
# Result: All return 403 with same error
```

---

## Lessons Learned

### 1. Don't Depend on Single Provider
**Problem:** Building MVP entirely dependent on one API
**Solution:** Multi-provider architecture from day one

### 2. API Documentation ≠ API Reality
**Problem:** Official docs say endpoint is public
**Reality:** Platform enforces undocumented policies
**Lesson:** Always test in production environment early

### 3. Policy Risks Are Real
Platform APIs can:
- Change policies without notice
- Block access to specific endpoints
- Require manual approval
- Restrict new applications
- Favor established partners

### 4. OAuth ≠ API Access
**OAuth working** does NOT guarantee **endpoint access**.
- Authentication layer separate from authorization layer
- Token validity separate from permission grants
- Platform can accept token but deny resource access

### 5. Defensive Architecture Wins
Systems designed for resilience succeed where single-provider systems fail.

---

## Strategic Response

### Immediate Actions Taken

#### 1. ✅ Documented Limitation
Created comprehensive documentation of what works and what doesn't.

#### 2. ✅ Preserved OAuth Implementation
Kept working OAuth code for future use when policies change.

#### 3. ✅ Implemented Fallback
Mock provider ensures system never crashes.

#### 4. ✅ Updated Roadmap
Pivoted to multi-provider architecture.

#### 5. ✅ Built Debug Tools
Created `test_ml_api` command for ongoing monitoring.

### Long-Term Strategy

#### Multi-Provider Architecture
Don't depend on Mercado Livre alone:
- Google Trends (trend signals)
- SERP APIs (shopping signals)
- Web scraping (public data)
- Multiple marketplaces
- Internal intelligence

#### Competitive Advantage
Single-provider tools are vulnerable.
Multi-provider aggregation is defensible.

**Competitors stuck with:**
- One API
- One perspective
- Platform dependency
- Policy vulnerability

**Radar de Tendências offers:**
- Multiple signals
- Aggregated intelligence
- Platform independence
- Policy resilience

---

## Future Mercado Livre Integration

### Monitoring Strategy

**Ongoing checks:**
```bash
# Weekly automated test
python manage.py test_ml_api --query "test"

# Check for policy changes
# Monitor Mercado Livre developer updates
# Track API changelog
```

### Re-activation Plan

**When endpoint becomes available:**

1. ✅ OAuth code already implemented (no changes needed)
2. ✅ Token persistence working (no changes needed)
3. ✅ Database model ready (no changes needed)
4. 🔄 Update provider status from 'blocked' to 'active'
5. 🔄 Enable MercadoLivreProvider in aggregation
6. 🔄 Badge automatically shows green

**Zero refactoring required** when policies change.

### Alternative Mercado Livre Approaches

**Option 1: Apply for Partner Status**
- Contact Mercado Livre developer relations
- Request commercial approval
- Explain use case
- Wait for review (weeks/months)

**Option 2: Use Different Endpoints**
- Test other ML API endpoints
- Categories API
- Trends API (if exists)
- Seller metrics

**Option 3: Public Web Scraping**
- Respect robots.txt
- Rate limiting
- Cache responses
- Parse public listings

**Option 4: Wait for Policy Update**
- Continue monitoring
- System works without it
- No urgency to fix

---

## Technical Implementation Details

### OAuth Flow (Working)

```python
# 1. Authorization URL
def get_authorization_url():
    code_verifier = generate_code_verifier()  # PKCE
    code_challenge = generate_code_challenge(code_verifier)

    cache.set('ml_code_verifier', code_verifier, timeout=600)

    params = {
        'response_type': 'code',
        'client_id': settings.MERCADO_LIVRE_CLIENT_ID,
        'redirect_uri': settings.MERCADO_LIVRE_REDIRECT_URI,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    return f"https://auth.mercadolivre.com.br/authorization?{params}"

# 2. Token Exchange
def exchange_code_for_token(code):
    code_verifier = cache.get('ml_code_verifier')

    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.MERCADO_LIVRE_CLIENT_ID,
        'client_secret': settings.MERCADO_LIVRE_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.MERCADO_LIVRE_REDIRECT_URI,
        'code_verifier': code_verifier
    }

    response = requests.post(
        'https://api.mercadolibre.com/oauth/token',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    # ✅ This works - token retrieved successfully
    token_data = response.json()

    # Save to database
    MercadoLivreToken.save_token_data(token_data)

# 3. Use Token (Blocked)
def fetch_products(query):
    token = MercadoLivreToken.get_current()
    access_token = token.access_token

    response = requests.get(
        'https://api.mercadolibre.com/sites/MLB/search',
        params={'q': query, 'limit': 50},
        headers={'Authorization': f'Bearer {access_token}'}
    )

    # ❌ This fails with PA_UNAUTHORIZED_RESULT_FROM_POLICIES
    # Token is valid
    # Request is correct
    # Platform policy blocks access
```

### Database Model (Ready)

```python
class MercadoLivreToken(models.Model):
    """Stores OAuth tokens for Mercado Livre API."""

    access_token = models.TextField()
    refresh_token = models.TextField()
    token_type = models.CharField(max_length=50, default='Bearer')
    expires_at = models.DateTimeField()
    scope = models.TextField(blank=True)
    user_id_ml = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    @classmethod
    def get_current(cls):
        try:
            return cls.objects.get(id=1)
        except cls.DoesNotExist:
            return None
```

**Status:** ✅ Working perfectly, ready for when endpoint access granted

---

## Contact Points

### Mercado Livre Developer Support

**Developer Portal:** https://developers.mercadolivre.com.br/
**Support:** developers@mercadolibre.com (if exists)
**Forum:** Mercado Livre developer forum

### Questions to Ask

1. What is required to access `/sites/MLB/search` endpoint?
2. Do we need partner status for product discovery?
3. What scopes/permissions are needed beyond basic OAuth?
4. Is there a certification process for marketplace analysis apps?
5. What is the timeline for app review/approval?
6. Are there alternative endpoints for product search?

---

## Conclusion

### What We Learned

1. ✅ OAuth implementation is solid and reusable
2. ✅ Token persistence works correctly
3. ✅ Database architecture is sound
4. ❌ Specific endpoint blocked by platform policy
5. ✅ System resilient with fallback data

### Strategic Position

**This is not a setback.**

It's a **validation of multi-provider strategy.**

Platforms that depend on single APIs are:
- Vulnerable to policy changes
- At risk of access revocation
- Limited by one data perspective
- Unable to pivot quickly

**Radar de Tendências is positioned to:**
- Aggregate multiple signals
- Provide broader intelligence
- Survive provider changes
- Scale independently

### Next Steps

1. ✅ Continue with mock data MVP
2. 📋 Implement Google Trends (independent source)
3. 📋 Implement SERP signals (shopping data)
4. 📋 Build scraping capability (fallback method)
5. ⏰ Monitor Mercado Livre policy changes
6. ⏰ Re-enable ML provider when available

---

## Appendix: Error Response Details

### Full Error Response

```json
{
  "error": "PA_UNAUTHORIZED_RESULT_FROM_POLICIES",
  "message": "forbidden",
  "status": 403,
  "cause": []
}
```

### Response Headers

```
Content-Type: application/json; charset=utf-8
Content-Length: 78
X-Api-Server-Segment: legacy
X-Request-Id: <uuid>
X-Cache: Error from cloudfront
Access-Control-Allow-Origin: *
```

### Request That Triggers Error

```bash
curl -X GET \
  'https://api.mercadolibre.com/sites/MLB/search?q=iPhone%2015&limit=50' \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Accept: application/json'

# Returns: 403 PA_UNAUTHORIZED_RESULT_FROM_POLICIES
```

---

## References

- Mercado Livre OAuth documentation: https://developers.mercadolivre.com.br/pt_br/autenticacao-e-autorizacao
- Mercado Livre API docs: https://developers.mercadolivre.com.br/pt_br/api-docs
- RFC 7636 (PKCE): https://tools.ietf.org/html/rfc7636
- OAuth 2.0 spec: https://oauth.net/2/

---

**Document version:** 1.0
**Last updated:** May 26, 2026
**Status:** Active documentation - policies may change

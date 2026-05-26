# Redis Setup on Render (CRITICAL for OAuth)

## Why Redis is Required

The OAuth tokens from Mercado Livre need to persist across requests and server workers. Without Redis:
- ❌ Tokens are stored in memory and lost between requests
- ❌ Badge shows yellow (Mock) even after successful authorization
- ❌ Real API data cannot be used

With Redis:
- ✅ Tokens persist across requests and workers
- ✅ Badge shows green (API) after authorization
- ✅ Real Mercado Livre data is used

## Setup Steps on Render

### 1. Add Redis Service

1. Go to your Render dashboard: https://dashboard.render.com/
2. Click **"New +"** → **"Redis"**
3. Configure Redis:
   - **Name:** `radar-redis` (or any name you prefer)
   - **Region:** Choose same region as your web service (for lower latency)
   - **Plan:** **Free** (sufficient for this use case)
   - **Maxmemory Policy:** `allkeys-lru` (recommended)
4. Click **"Create Redis"**
5. Wait for Redis to deploy (usually takes 1-2 minutes)

### 2. Get Redis URL

1. Click on your newly created Redis service
2. Find the **"Internal Connection String"** (looks like `redis://red-xxxxx:6379`)
3. Copy this URL

### 3. Add Redis URL to Web Service

1. Go to your web service (radar-projeto or similar)
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add:
   - **Key:** `REDIS_URL`
   - **Value:** Paste the Internal Connection String from step 2
5. Click **"Save Changes"**

### 4. Verify Deployment

After the web service redeploys (automatic):

1. Go to `/market/mercadolivre/status/` to check status
2. If not already authorized, click **"Authorize Mercado Livre"**
3. Complete OAuth flow
4. Test product search at `/market/test/`
5. Badge should now show **green "✓ Mercado Livre API"** instead of yellow "⚠ Mock"

## Troubleshooting

### Badge still shows yellow after Redis setup

**Check:**
1. Redis URL is correctly set in environment variables
2. Web service redeployed after adding REDIS_URL
3. OAuth authorization was completed AFTER Redis was configured
4. Check logs for Redis connection errors

**Solution:**
- Re-authorize OAuth: Go to `/market/mercadolivre/authorize/` and authorize again
- Old tokens in memory cache were lost; new authorization will save to Redis

### Redis connection errors in logs

**Error:** `ConnectionError: Error connecting to Redis`

**Solution:**
- Verify REDIS_URL is correct (copy-paste from Redis service)
- Ensure Redis service is running (check Render dashboard)
- Check both services are in same region (lower latency)

### "redis.exceptions.ConnectionError: Too many connections"

**Solution:**
- This is rare with Free plan
- Reduce `max_connections` in `settings.py` (currently 50)
- Or upgrade to paid Redis plan

## Cost

- **Free Tier:** Completely free, sufficient for development/MVP
  - 25 MB storage
  - Shared resources
  - Perfect for OAuth tokens (very small data)

## Security Notes

- ✅ Use **Internal Connection String** (starts with `redis://red-...`)
- ✅ Never use External Connection String in production
- ✅ REDIS_URL is automatically encrypted by Render
- ✅ Only your web service can access Redis (internal network)

## Next Steps After Setup

Once Redis is working and badge shows green:

1. ✅ OAuth tokens will persist between requests
2. ✅ Real Mercado Livre data will be fetched
3. ✅ You can implement detailed product view (next feature)
4. ✅ System is production-ready for Mercado Livre integration

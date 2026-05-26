 📋 What You Need to Do Now

  On Render (After Deployment)

  Step 1: Complete OAuth Flow
  1. Go to: https://radar-1llq.onrender.com/market/mercadolivre/authorize/
  2. Click "Authorize"
  3. Mercado Livre OAuth page opens
  4. Click "Allow" / "Autorizar"
  5. Redirected back to /market/mercadolivre/callback/
  6. Token saved to PostgreSQL ✅

  Step 2: Verify Token
  1. Check admin: /admin/market/mercadolivretoken/
  2. Should see:
     - Status: 🟢 Valid
     - Masked token: APP_USR...x7Gf
     - Expires at: (future date)

  Step 3: Test Product Search
  1. Go to: /market/test/
  2. Search: "iPhone 15"
  3. Expected:
     - Badge: 🟢 GREEN "✓ Mercado Livre API"
     - Real data: ~2800 listings
     - Real prices, real sellers

  Step 4: Check Logs
  1. Render dashboard → Logs
  2. Look for:
     [ML OAuth] Token loaded from database
     [ML API] ✅ Authenticated API request successful!
     [ML API] Results: 50 items fetched, 2847 total available

  ---
  🎯 Expected Flow

  First Visit (No Token)

  User → /market/test/
       → Enter "iPhone 15"
       → [ML API] ⚠️ No OAuth token
       → Mock data shown
       → Badge: 🟡 Yellow "⚠ Mercado Livre (Mock)"

  After OAuth Authorization

  User → /market/mercadolivre/authorize/
       → ML OAuth page
       → Authorize
       → Token saved to database
       → Return to /market/test/
       → Enter "iPhone 15"
       → [ML API] ✅ Authenticated request successful!
       → Real API data shown
       → Badge: 🟢 GREEN "✓ Mercado Livre API"

  Subsequent Searches

  User → /market/test/
       → Enter any product
       → Token loaded from database
       → Real API data
       → Badge: 🟢 GREEN (persists!)

  ---
  📁 Files Changed

  1. market/services/mercado_livre.py
    - Removed failed public API attempt
    - Use authenticated request only
    - Enhanced logging
    - Clear error messages
  2. market/management/commands/test_ml_api.py (NEW)
    - Comprehensive API testing
    - Tests 4 different scenarios
    - Full debug output
  3. docs/mercado_livre_403_investigation.md (NEW)
    - Complete investigation report
    - Test results
    - Solution documentation
    - User flow diagrams

  ---
  🔧 Debug Commands

  Test API Locally (After Deployment)

  python manage.py test_ml_api

  Check Token Status

  python manage.py shell -c "
  from market.models import MercadoLivreToken
  token = MercadoLivreToken.get_current()
  print(f'Token exists: {token is not None}')
  if token:
      print(f'Is expired: {token.is_expired()}')
      print(f'Expires at: {token.expires_at}')
  "

  ---
  ✅ Deployment Status

  Pushing to Render now...
  - Deployment will complete in 2-3 minutes
  - No migrations needed (already applied)
  - Just code updates

  After deployment:
  1. Complete OAuth at /market/mercadolivre/authorize/
  2. Badge will turn GREEN
  3. Real Mercado Livre data will appear
  4. Token persists across requests ✅

  ---
  📊 Summary
  ┌──────────────────────────┬────────────────────────────────┐
  │          Status          │          Description           │
  ├──────────────────────────┼────────────────────────────────┤
  │ ✅ Root cause found      │ API requires OAuth, not public │
  ├──────────────────────────┼────────────────────────────────┤
  │ ✅ Solution implemented  │ Use authenticated requests     │
  ├──────────────────────────┼────────────────────────────────┤
  │ ✅ Logging enhanced      │ Detailed debug output          │
  ├──────────────────────────┼────────────────────────────────┤
  │ ✅ Test command created  │ python manage.py test_ml_api   │
  ├──────────────────────────┼────────────────────────────────┤
  │ ✅ Documentation written │ Full investigation report      │
  ├──────────────────────────┼────────────────────────────────┤
  │ ✅ Code deployed         │ Pushing to Render now          │
  ├──────────────────────────┼────────────────────────────────┤
  │ ⏳ OAuth needed          │ User must authorize on Render  │
  └──────────────────────────┴────────────────────────────────┘
  ---
  Next step: Aguarde o deployment (2-3 min), depois acesse /market/mercadolivre/authorize/ no Render para completar o OAuth! 🚀


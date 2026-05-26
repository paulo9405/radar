from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class ProductSearch(models.Model):
    """
    Stores product search queries.
    Tracks both public tests and authenticated user searches.
    """
    query = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    source = models.CharField(
        max_length=20,
        choices=[
            ('landing', 'Landing Page'),
            ('dashboard', 'Dashboard'),
            ('api', 'API'),
        ],
        default='landing'
    )
    is_public_test = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_searches'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product Search'
        verbose_name_plural = 'Product Searches'

    def __str__(self):
        return f"{self.query} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class MarketAnalysis(models.Model):
    """
    Stores the complete market analysis for a product search.
    Includes scores, classification, summary and raw data.
    """
    product_search = models.OneToOneField(
        ProductSearch,
        on_delete=models.CASCADE,
        related_name='analysis'
    )

    # Scores (0-10 scale)
    demand_score = models.DecimalField(max_digits=3, decimal_places=1)
    competition_score = models.DecimalField(max_digits=3, decimal_places=1)
    saturation_score = models.DecimalField(max_digits=3, decimal_places=1)
    price_score = models.DecimalField(max_digits=3, decimal_places=1)
    final_score = models.DecimalField(max_digits=3, decimal_places=1, db_index=True)

    # Classification based on final score
    classification = models.CharField(
        max_length=30,
        choices=[
            ('bad', 'Produto ruim'),
            ('risky', 'Arriscado'),
            ('good', 'Boa oportunidade'),
            ('excellent', 'Alta oportunidade'),
        ]
    )

    # Confidence level (0-100%)
    confidence_level = models.IntegerField(default=70)

    # AI-generated summary
    summary = models.TextField()

    # Raw data from providers (stored as JSON)
    raw_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Market Analysis'
        verbose_name_plural = 'Market Analyses'

    def __str__(self):
        return f"{self.product_search.query} - Score: {self.final_score}"

    def get_classification_display_color(self):
        """Returns Bootstrap color class based on classification"""
        colors = {
            'bad': 'danger',
            'risky': 'warning',
            'good': 'info',
            'excellent': 'success',
        }
        return colors.get(self.classification, 'secondary')


class MercadoLivreToken(models.Model):
    """
    Stores Mercado Livre OAuth tokens.

    Uses singleton approach - only one active token record exists (id=1).
    Tokens are persistent integration state, not cache data.
    """
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_type = models.CharField(max_length=50, blank=True, default='Bearer')
    expires_at = models.DateTimeField()
    scope = models.TextField(blank=True, default='')
    user_id_ml = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mercado Livre Token'
        verbose_name_plural = 'Mercado Livre Tokens'

    def __str__(self):
        status = "Valid" if not self.is_expired() else "Expired"
        return f"ML Token ({status}) - Expires: {self.expires_at.strftime('%Y-%m-%d %H:%M')}"

    def is_expired(self):
        """Check if access token is expired"""
        return timezone.now() >= self.expires_at

    def masked_access_token(self):
        """Returns masked access token for display"""
        if len(self.access_token) > 10:
            return f"{self.access_token[:6]}...{self.access_token[-4:]}"
        return "***"

    def masked_refresh_token(self):
        """Returns masked refresh token for display"""
        if len(self.refresh_token) > 10:
            return f"{self.refresh_token[:6]}...{self.refresh_token[-4:]}"
        return "***"

    @classmethod
    def get_current(cls):
        """Get the current active token (singleton pattern)"""
        try:
            return cls.objects.get(id=1)
        except cls.DoesNotExist:
            return None

    @classmethod
    def save_token_data(cls, token_data):
        """
        Save or update token data from OAuth response.

        Args:
            token_data: Dict with keys: access_token, refresh_token,
                       expires_in, token_type, scope, user_id (optional)

        Returns:
            MercadoLivreToken: The saved token instance
        """
        # Calculate expires_at from expires_in (seconds)
        expires_in = token_data.get('expires_in', 21600)  # Default 6 hours
        expires_at = timezone.now() + timedelta(seconds=expires_in)

        # Prepare data
        data = {
            'access_token': token_data.get('access_token', ''),
            'refresh_token': token_data.get('refresh_token', ''),
            'token_type': token_data.get('token_type', 'Bearer'),
            'expires_at': expires_at,
            'scope': token_data.get('scope', ''),
            'user_id_ml': token_data.get('user_id'),
        }

        # Use update_or_create with id=1 (singleton)
        token, created = cls.objects.update_or_create(
            id=1,
            defaults=data
        )

        action = "created" if created else "updated"
        print(f"[ML Token] Token {action} in database - Expires at: {expires_at}")

        return token


class GoogleTrendsCache(models.Model):
    """
    Caches Google Trends API responses to avoid rate limiting.

    Stores normalized queries and their trend data with 24-hour TTL.
    Implements cooldown protection after 429 errors.
    """
    # Query fields
    normalized_query = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Lowercase, trimmed, normalized query for cache lookup"
    )
    original_query = models.CharField(
        max_length=100,
        help_text="Original query as submitted"
    )

    # Data storage
    raw_data = models.JSONField(
        default=dict,
        help_text="Complete Google Trends response"
    )

    # Source tracking
    source = models.CharField(
        max_length=30,
        choices=[
            ('google_trends_live', 'Google Trends Live'),
            ('google_trends_error', 'Google Trends Error'),
        ],
        default='google_trends_live'
    )

    # Cache metadata
    fetched_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this data was fetched from Google Trends"
    )
    expires_at = models.DateTimeField(
        db_index=True,
        help_text="When this cached data expires (24 hours)"
    )

    # Error tracking
    last_error = models.TextField(
        blank=True,
        null=True,
        help_text="Last error message if fetch failed"
    )
    error_count = models.IntegerField(
        default=0,
        help_text="Number of consecutive errors"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fetched_at']
        verbose_name = 'Google Trends Cache'
        verbose_name_plural = 'Google Trends Cache'
        indexes = [
            models.Index(fields=['normalized_query', 'expires_at']),
        ]

    def __str__(self):
        status = "Valid" if not self.is_expired() else "Expired"
        return f"{self.original_query} ({status}) - {self.fetched_at.strftime('%Y-%m-%d %H:%M')}"

    def is_expired(self):
        """Check if cached data is expired"""
        return timezone.now() >= self.expires_at

    def is_fresh(self):
        """Check if cached data is still fresh (not expired)"""
        return not self.is_expired()

    @classmethod
    def normalize_query(cls, query: str) -> str:
        """
        Normalize query for cache lookup.

        - Lowercase
        - Strip whitespace
        - Collapse multiple spaces
        - Remove extra spaces
        """
        normalized = query.lower().strip()
        # Collapse multiple spaces
        normalized = ' '.join(normalized.split())
        return normalized

    @classmethod
    def get_cached(cls, query: str):
        """
        Get cached data for a query if it exists and is fresh.

        Args:
            query: Product search query

        Returns:
            GoogleTrendsCache instance or None
        """
        normalized = cls.normalize_query(query)

        try:
            cache = cls.objects.filter(
                normalized_query=normalized,
                expires_at__gt=timezone.now()
            ).order_by('-fetched_at').first()

            return cache
        except cls.DoesNotExist:
            return None

    @classmethod
    def save_trends_data(cls, query: str, trends_data: dict, ttl_hours: int = 24):
        """
        Save Google Trends data to cache.

        Args:
            query: Original query
            trends_data: Complete trends response
            ttl_hours: Time to live in hours (default 24)

        Returns:
            GoogleTrendsCache instance
        """
        normalized = cls.normalize_query(query)
        expires_at = timezone.now() + timedelta(hours=ttl_hours)

        cache, created = cls.objects.update_or_create(
            normalized_query=normalized,
            defaults={
                'original_query': query,
                'raw_data': trends_data,
                'source': 'google_trends_live',
                'expires_at': expires_at,
                'last_error': None,
                'error_count': 0,
            }
        )

        action = "cached" if created else "updated in cache"
        print(f"[Google Trends Cache] {query} {action} (expires: {expires_at})")

        return cache

    @classmethod
    def clear_expired(cls):
        """Delete all expired cache entries"""
        deleted_count, _ = cls.objects.filter(
            expires_at__lte=timezone.now()
        ).delete()
        return deleted_count


class GoogleTrendsCooldown(models.Model):
    """
    Tracks Google Trends API cooldown state after rate limiting.

    Singleton model - only one record exists (id=1).
    When HTTP 429 is detected, cooldown is activated for 15-30 minutes.
    """
    is_active = models.BooleanField(
        default=False,
        help_text="Whether cooldown is currently active"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When cooldown started"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When cooldown expires"
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason for cooldown (e.g., HTTP 429)"
    )
    request_count = models.IntegerField(
        default=0,
        help_text="Number of requests made during cooldown"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Google Trends Cooldown'
        verbose_name_plural = 'Google Trends Cooldown'

    def __str__(self):
        if self.is_active and self.expires_at:
            return f"Cooldown Active (expires: {self.expires_at.strftime('%H:%M:%S')})"
        return "Cooldown Inactive"

    @classmethod
    def is_in_cooldown(cls):
        """Check if Google Trends is currently in cooldown"""
        try:
            cooldown = cls.objects.get(id=1)
            if cooldown.is_active and cooldown.expires_at:
                if timezone.now() < cooldown.expires_at:
                    return True
                else:
                    # Cooldown expired, deactivate
                    cooldown.is_active = False
                    cooldown.save()
                    return False
            return False
        except cls.DoesNotExist:
            return False

    @classmethod
    def activate(cls, reason: str = "Rate limit exceeded", duration_minutes: int = 15):
        """
        Activate cooldown for specified duration.

        Args:
            reason: Reason for cooldown
            duration_minutes: Cooldown duration in minutes
        """
        started_at = timezone.now()
        expires_at = started_at + timedelta(minutes=duration_minutes)

        cooldown, created = cls.objects.update_or_create(
            id=1,
            defaults={
                'is_active': True,
                'started_at': started_at,
                'expires_at': expires_at,
                'reason': reason,
                'request_count': 0,
            }
        )

        print(f"[Google Trends Cooldown] ⏸️  ACTIVATED for {duration_minutes} min")
        print(f"[Google Trends Cooldown]   Reason: {reason}")
        print(f"[Google Trends Cooldown]   Expires at: {expires_at.strftime('%H:%M:%S')}")

        return cooldown

    @classmethod
    def deactivate(cls):
        """Deactivate cooldown"""
        try:
            cooldown = cls.objects.get(id=1)
            cooldown.is_active = False
            cooldown.save()
            print(f"[Google Trends Cooldown] ✅ Deactivated")
        except cls.DoesNotExist:
            pass

    @classmethod
    def get_status(cls):
        """Get current cooldown status for display"""
        try:
            cooldown = cls.objects.get(id=1)
            if cooldown.is_active and cooldown.expires_at:
                if timezone.now() < cooldown.expires_at:
                    remaining = (cooldown.expires_at - timezone.now()).seconds // 60
                    return {
                        'active': True,
                        'reason': cooldown.reason,
                        'remaining_minutes': remaining,
                        'expires_at': cooldown.expires_at,
                    }
        except cls.DoesNotExist:
            pass

        return {'active': False}

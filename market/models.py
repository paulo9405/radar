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

from django.db import models
from django.contrib.auth.models import User


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

from django.contrib import admin
from .models import ProductSearch, MarketAnalysis, MercadoLivreToken


@admin.register(ProductSearch)
class ProductSearchAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductSearch model.
    """
    list_display = [
        'query',
        'source',
        'is_public_test',
        'user',
        'created_at',
        'has_analysis'
    ]
    list_filter = [
        'source',
        'is_public_test',
        'created_at',
    ]
    search_fields = ['query', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def has_analysis(self, obj):
        """Check if this search has an associated analysis"""
        return hasattr(obj, 'analysis')
    has_analysis.boolean = True
    has_analysis.short_description = 'Has Analysis'


@admin.register(MarketAnalysis)
class MarketAnalysisAdmin(admin.ModelAdmin):
    """
    Admin configuration for MarketAnalysis model.
    """
    list_display = [
        'get_query',
        'final_score',
        'classification',
        'confidence_level',
        'demand_score',
        'competition_score',
        'saturation_score',
        'price_score',
        'created_at'
    ]
    list_filter = [
        'classification',
        'created_at',
    ]
    search_fields = ['product_search__query', 'summary']
    readonly_fields = [
        'created_at',
        'product_search',
        'demand_score',
        'competition_score',
        'saturation_score',
        'price_score',
        'final_score',
        'classification',
        'confidence_level',
        'summary',
        'raw_data'
    ]
    date_hierarchy = 'created_at'

    def get_query(self, obj):
        """Get the query from related ProductSearch"""
        return obj.product_search.query
    get_query.short_description = 'Query'
    get_query.admin_order_field = 'product_search__query'

    def has_add_permission(self, request):
        """Prevent manual creation of analyses through admin"""
        return False


@admin.register(MercadoLivreToken)
class MercadoLivreTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for MercadoLivreToken model.

    IMPORTANT: Tokens are masked for security - full tokens are never displayed.
    """
    list_display = [
        'id',
        'token_status',
        'masked_access_token',
        'expires_at',
        'user_id_ml',
        'updated_at'
    ]
    readonly_fields = [
        'id',
        'masked_access_token',
        'masked_refresh_token',
        'token_type',
        'expires_at',
        'scope',
        'user_id_ml',
        'created_at',
        'updated_at',
        'token_status'
    ]

    # Hide actual token fields from admin form
    exclude = ['access_token', 'refresh_token']

    def token_status(self, obj):
        """Display token status with icon"""
        if obj.is_expired():
            return "🔴 Expired"
        return "🟢 Valid"
    token_status.short_description = 'Status'

    def has_add_permission(self, request):
        """Prevent manual creation - tokens come from OAuth flow only"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion to reset OAuth"""
        return True

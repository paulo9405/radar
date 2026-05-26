from django.contrib import admin
from .models import Lead, WhatsAppLead, AnalysisFeedback


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin configuration for Lead model"""

    list_display = ['name', 'email', 'whatsapp', 'niche', 'price_range', 'created_at']
    list_filter = ['price_range', 'created_at']
    search_fields = ['name', 'email', 'niche', 'whatsapp']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações de Contato', {
            'fields': ('name', 'email', 'whatsapp')
        }),
        ('Informações de Negócio', {
            'fields': ('niche', 'price_range', 'main_difficulty')
        }),
        ('Metadados', {
            'fields': ('created_at',)
        }),
    )


class AnalysisFeedbackInline(admin.TabularInline):
    """Inline feedback display in WhatsAppLead admin"""
    model = AnalysisFeedback
    extra = 0
    readonly_fields = ['product_query', 'rating', 'comments', 'would_pay', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(WhatsAppLead)
class WhatsAppLeadAdmin(admin.ModelAdmin):
    """Admin configuration for WhatsApp Lead tracking"""

    list_display = [
        'whatsapp',
        'has_used_free_test',
        'analyzed_product',
        'submitted_feedback',
        'joined_waitlist',
        'free_test_used_at',
        'created_at'
    ]
    list_filter = [
        'has_used_free_test',
        'submitted_feedback',
        'joined_waitlist',
        'created_at',
        'free_test_used_at'
    ]
    search_fields = ['whatsapp', 'normalized_whatsapp', 'analyzed_product', 'ip_address']
    readonly_fields = ['normalized_whatsapp', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [AnalysisFeedbackInline]

    fieldsets = (
        ('WhatsApp', {
            'fields': ('whatsapp', 'normalized_whatsapp')
        }),
        ('Teste Grátis', {
            'fields': (
                'has_used_free_test',
                'free_test_used_at',
                'analyzed_product'
            )
        }),
        ('Conversão', {
            'fields': ('submitted_feedback', 'joined_waitlist')
        }),
        ('Anti-Abuso', {
            'fields': ('ip_address', 'session_key'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AnalysisFeedback)
class AnalysisFeedbackAdmin(admin.ModelAdmin):
    """Admin configuration for Analysis Feedback"""

    list_display = [
        'product_query',
        'whatsapp_lead',
        'rating',
        'would_pay',
        'created_at'
    ]
    list_filter = ['rating', 'would_pay', 'created_at']
    search_fields = ['product_query', 'comments', 'whatsapp_lead__whatsapp']
    readonly_fields = ['created_at', 'ip_address']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Produto Analisado', {
            'fields': ('whatsapp_lead', 'product_query')
        }),
        ('Feedback', {
            'fields': ('rating', 'comments', 'would_pay')
        }),
        ('Metadados', {
            'fields': ('ip_address', 'created_at')
        }),
    )

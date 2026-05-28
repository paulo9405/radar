from django.contrib import admin
from .models import Lead, WhatsAppLead, AnalysisFeedback, IPAnalysisLimit


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
    readonly_fields = ['product_query', 'rating', 'comments', 'would_pay_for_analyses', 'entered_waitlist', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(WhatsAppLead)
class WhatsAppLeadAdmin(admin.ModelAdmin):
    """Admin configuration for WhatsApp Lead tracking"""

    list_display = [
        'get_contact',
        'analyzed_product',
        'unlocked_analysis',
        'willingness_to_pay',
        'launch_interest',
        'unlocked_at',
        'created_at'
    ]
    list_filter = [
        'unlocked_analysis',
        'willingness_to_pay',
        'launch_interest',
        'submitted_feedback',
        'joined_waitlist',
        'has_used_free_test',
        'created_at',
        'unlocked_at'
    ]
    search_fields = ['whatsapp', 'email', 'normalized_whatsapp', 'analyzed_product', 'ip_address']
    readonly_fields = ['normalized_whatsapp', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [AnalysisFeedbackInline]

    def get_contact(self, obj):
        """Display email or WhatsApp"""
        return obj.email if obj.email else obj.whatsapp
    get_contact.short_description = 'Contato'

    fieldsets = (
        ('Contato', {
            'fields': ('whatsapp', 'email', 'normalized_whatsapp')
        }),
        ('Análise', {
            'fields': (
                'analyzed_product',
                'unlocked_analysis',
                'unlocked_at'
            )
        }),
        ('Validação MVP', {
            'fields': (
                'willingness_to_pay',
                'launch_interest',
                'submitted_feedback',
                'joined_waitlist'
            )
        }),
        ('Teste Grátis (Legacy)', {
            'fields': (
                'has_used_free_test',
                'free_test_used_at'
            ),
            'classes': ('collapse',)
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
        'would_pay_for_analyses',
        'entered_waitlist',
        'product_score',
        'confidence_level',
        'created_at'
    ]
    list_filter = ['rating', 'would_pay_for_analyses', 'entered_waitlist', 'created_at']
    search_fields = ['product_query', 'comments', 'whatsapp_lead__whatsapp']
    readonly_fields = ['created_at', 'ip_address']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Produto Analisado', {
            'fields': ('whatsapp_lead', 'product_query', 'product_score', 'confidence_level')
        }),
        ('Feedback', {
            'fields': ('rating', 'comments', 'would_pay_for_analyses', 'entered_waitlist')
        }),
        ('Metadados', {
            'fields': ('ip_address', 'created_at')
        }),
    )


@admin.register(IPAnalysisLimit)
class IPAnalysisLimitAdmin(admin.ModelAdmin):
    """Admin configuration for IP Analysis Limits"""

    list_display = [
        'ip_address',
        'analysis_count',
        'last_analysis_date',
        'created_at'
    ]
    list_filter = ['last_analysis_date', 'analysis_count']
    search_fields = ['ip_address']
    readonly_fields = ['created_at', 'last_analysis_date']
    date_hierarchy = 'created_at'

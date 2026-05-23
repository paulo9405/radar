from django.contrib import admin
from .models import Lead


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

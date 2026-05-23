from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    """Simplified form for early access leads - only 3 fields for maximum conversion"""

    class Meta:
        model = Lead
        fields = ['name', 'whatsapp', 'niche']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome',
                'required': True
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999',
                'required': True
            }),
            'niche': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Eletrônicos, Moda, Decoração, Fitness',
                'required': True
            }),
        }
        labels = {
            'name': 'Nome completo',
            'whatsapp': 'WhatsApp',
            'niche': 'Nicho ou produto que você vende',
        }

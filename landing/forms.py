from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    """Ultra-simplified form for maximum conversion - only WhatsApp required"""

    class Meta:
        model = Lead
        fields = ['whatsapp']
        widgets = {
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999',
                'required': True
            }),
        }
        labels = {
            'whatsapp': 'Seu WhatsApp',
        }

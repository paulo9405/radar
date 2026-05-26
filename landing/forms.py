from django import forms
from .models import Lead, WhatsAppLead


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


class WhatsAppLeadForm(forms.ModelForm):
    """
    Form for free analysis - captures only WhatsApp.
    Conversion-optimized for immediate value.
    """

    class Meta:
        model = WhatsAppLead
        fields = ['whatsapp']
        widgets = {
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '(11) 99999-9999',
                'required': True,
                'autocomplete': 'tel'
            }),
        }
        labels = {
            'whatsapp': 'Seu WhatsApp',
        }

    def clean_whatsapp(self):
        """Normalize and validate WhatsApp number"""
        whatsapp = self.cleaned_data.get('whatsapp')
        if whatsapp:
            # Normalize for duplicate checking
            normalized = WhatsAppLead.normalize_whatsapp(whatsapp)
            self.cleaned_data['normalized_whatsapp'] = normalized
        return whatsapp

from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    """Form for early access leads with Brazilian Portuguese labels"""

    class Meta:
        model = Lead
        fields = ['name', 'niche', 'whatsapp', 'email', 'price_range', 'main_difficulty']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome completo',
                'required': True
            }),
            'niche': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Eletrônicos, Moda, Decoração',
                'required': True
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(34) 99999-9999',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com',
                'required': True
            }),
            'price_range': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'main_difficulty': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva sua maior dificuldade ao escolher produtos (opcional)',
                'rows': 4,
                'required': False
            }),
        }
        labels = {
            'name': 'Nome',
            'niche': 'Nicho/Produto que vende ou pretende vender',
            'whatsapp': 'WhatsApp',
            'email': 'Email',
            'price_range': 'Quanto você pagaria por uma ferramenta assim?',
            'main_difficulty': 'Qual sua maior dificuldade hoje para encontrar produtos com potencial de venda? (opcional)',
        }

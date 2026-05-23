from django.db import models
from django.core.validators import RegexValidator


class Lead(models.Model):
    """Model to store early access leads"""

    PRICE_CHOICES = [
        ('29', 'R$29/mês'),
        ('49', 'R$49/mês'),
        ('99', 'R$99/mês'),
        ('annual', 'Pagaria plano anual com desconto'),
        ('free_first', 'Só testaria grátis primeiro'),
        ('other', 'Outro'),
    ]

    # Brazilian WhatsApp validation - accepts multiple formats
    # Examples: 34999999999, 34 99999-9999, (34) 99999-9999, +55 34 99999-9999
    whatsapp_regex = RegexValidator(
        regex=r'^(\+?55\s?)?(\(?\d{2}\)?\s?)?9?\d{4}-?\d{4}$',
        message="Número de WhatsApp inválido. Use o formato: (34) 99999-9999"
    )

    name = models.CharField(
        max_length=200,
        verbose_name='Nome'
    )

    niche = models.CharField(
        max_length=300,
        verbose_name='Nicho/Produto'
    )

    whatsapp = models.CharField(
        validators=[whatsapp_regex],
        max_length=20,
        verbose_name='WhatsApp'
    )

    email = models.EmailField(
        verbose_name='Email'
    )

    price_range = models.CharField(
        max_length=20,
        choices=PRICE_CHOICES,
        verbose_name='Faixa de Preço'
    )

    main_difficulty = models.TextField(
        blank=True,
        null=True,
        verbose_name='Principal Dificuldade',
        help_text='Qual sua maior dificuldade hoje para encontrar produtos com potencial de venda?'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Cadastro'
    )

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"

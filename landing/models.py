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
        verbose_name='Nome',
        blank=True,
        null=True
    )

    niche = models.CharField(
        max_length=300,
        verbose_name='Nicho/Produto',
        blank=True,
        null=True
    )

    whatsapp = models.CharField(
        validators=[whatsapp_regex],
        max_length=20,
        verbose_name='WhatsApp'
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email'
    )

    price_range = models.CharField(
        max_length=20,
        choices=PRICE_CHOICES,
        blank=True,
        null=True,
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
        return f"{self.name or 'Lead'} - {self.whatsapp}"


class WhatsAppLead(models.Model):
    """
    Tracks WhatsApp numbers for free product analysis test.
    Each WhatsApp can perform 1 free analysis.
    """

    # Brazilian WhatsApp validation
    whatsapp_regex = RegexValidator(
        regex=r'^(\+?55\s?)?(\(?\d{2}\)?\s?)?9?\d{4}-?\d{4}$',
        message="Número de WhatsApp inválido. Use o formato: (34) 99999-9999"
    )

    whatsapp = models.CharField(
        validators=[whatsapp_regex],
        max_length=20,
        verbose_name='WhatsApp',
        blank=True,
        default='',
        error_messages={
            'unique': 'Esse WhatsApp já utilizou a análise gratuita.'
        }
    )

    normalized_whatsapp = models.CharField(
        max_length=20,
        verbose_name='WhatsApp Normalizado',
        db_index=True,
        blank=True,
        default='',
        help_text='Somente dígitos para lookup'
    )

    # Free test tracking
    has_used_free_test = models.BooleanField(
        default=False,
        verbose_name='Usou Teste Grátis'
    )

    free_test_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data do Teste Grátis'
    )

    analyzed_product = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Produto Analisado'
    )

    # Anti-abuse tracking
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP'
    )

    session_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Session Key'
    )

    # Contact info (can be WhatsApp OR email)
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email'
    )

    # Analysis tracking
    analysis_count = models.IntegerField(
        default=1,
        verbose_name='Número de Análises'
    )

    # Conversion tracking
    unlocked_analysis = models.BooleanField(
        default=False,
        verbose_name='Desbloqueou Análise'
    )

    unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Desbloqueado em'
    )

    willingness_to_pay = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=[
            ('yes', 'Sim, pagaria'),
            ('maybe', 'Talvez'),
            ('no', 'Não pagaria')
        ],
        verbose_name='Pagaria pelo produto'
    )

    launch_interest = models.BooleanField(
        default=False,
        verbose_name='Quer saber do lançamento'
    )

    submitted_feedback = models.BooleanField(
        default=False,
        verbose_name='Enviou Feedback'
    )

    joined_waitlist = models.BooleanField(
        default=False,
        verbose_name='Entrou na Lista'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'WhatsApp Lead'
        verbose_name_plural = 'WhatsApp Leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['normalized_whatsapp']),
            models.Index(fields=['has_used_free_test']),
        ]

    def __str__(self):
        status = "Usado" if self.has_used_free_test else "Disponível"
        return f"{self.whatsapp} - {status}"

    @classmethod
    def normalize_whatsapp(cls, whatsapp):
        """Remove all non-digit characters from WhatsApp number"""
        import re
        return re.sub(r'\D', '', whatsapp)

    @classmethod
    def has_used_test(cls, whatsapp):
        """Check if this WhatsApp number already used the free test"""
        normalized = cls.normalize_whatsapp(whatsapp)
        return cls.objects.filter(
            normalized_whatsapp=normalized,
            has_used_free_test=True
        ).exists()

    def mark_test_as_used(self, product_query):
        """Mark that this WhatsApp used the free test"""
        from django.utils import timezone
        self.has_used_free_test = True
        self.free_test_used_at = timezone.now()
        self.analyzed_product = product_query
        self.save()


class IPAnalysisLimit(models.Model):
    """
    Tracks analysis count per IP for rate limiting.
    Resets daily.
    """
    ip_address = models.GenericIPAddressField(
        verbose_name='IP Address',
        unique=True
    )

    analysis_count = models.IntegerField(
        default=0,
        verbose_name='Analysis Count'
    )

    last_analysis_date = models.DateField(
        auto_now=True,
        verbose_name='Last Analysis Date'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )

    class Meta:
        verbose_name = 'IP Analysis Limit'
        verbose_name_plural = 'IP Analysis Limits'

    def __str__(self):
        return f"{self.ip_address} - {self.analysis_count} analyses"

    @classmethod
    def can_analyze(cls, ip_address):
        """Check if IP can perform another analysis (max 2 per day)"""
        from django.utils import timezone
        today = timezone.now().date()

        try:
            limit = cls.objects.get(ip_address=ip_address)
            # Reset if it's a new day
            if limit.last_analysis_date < today:
                limit.analysis_count = 0
                limit.save()
            return limit.analysis_count < 2
        except cls.DoesNotExist:
            return True

    @classmethod
    def increment_count(cls, ip_address):
        """Increment analysis count for IP"""
        from django.utils import timezone
        today = timezone.now().date()

        limit, created = cls.objects.get_or_create(
            ip_address=ip_address,
            defaults={'analysis_count': 1}
        )

        if not created:
            # Reset if new day
            if limit.last_analysis_date < today:
                limit.analysis_count = 1
            else:
                limit.analysis_count += 1
            limit.save()

        return limit.analysis_count


class AnalysisFeedback(models.Model):
    """
    Stores user feedback after seeing analysis results.
    Critical for MVP validation.
    """

    RATING_CHOICES = [
        ('very_useful', 'Muito útil'),
        ('interesting', 'Interessante'),
        ('confusing', 'Confuso'),
        ('not_trust', 'Não confiaria'),
        ('would_use_again', 'Usaria novamente'),
    ]

    whatsapp_lead = models.ForeignKey(
        WhatsAppLead,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        null=True,
        blank=True
    )

    product_query = models.CharField(
        max_length=200,
        verbose_name='Produto Analisado'
    )

    rating = models.CharField(
        max_length=20,
        choices=RATING_CHOICES,
        verbose_name='Avaliação'
    )

    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentários'
    )

    would_pay_for_analyses = models.BooleanField(
        default=False,
        verbose_name='Pagaria por análises assim'
    )

    entered_waitlist = models.BooleanField(
        default=False,
        verbose_name='Entrou na lista de espera'
    )

    product_score = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='Score Final'
    )

    confidence_level = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Nível de Confiança (%)'
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Feedback de Análise'
        verbose_name_plural = 'Feedbacks de Análise'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product_query} - {self.get_rating_display()}"

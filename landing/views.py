from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .forms import WhatsAppLeadForm
from .models import WhatsAppLead


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def index(request):
    """
    Landing page with free analysis CTA.

    Flow:
    1. User enters WhatsApp
    2. Check if already used free test
    3. If yes: show message
    4. If no: redirect to /market/test/ immediately
    """

    if request.method == 'POST':
        form = WhatsAppLeadForm(request.POST)

        if form.is_valid():
            whatsapp = form.cleaned_data['whatsapp']
            normalized = WhatsAppLead.normalize_whatsapp(whatsapp)

            # Check if this WhatsApp already used free test
            if WhatsAppLead.has_used_test(whatsapp):
                messages.warning(
                    request,
                    'Este WhatsApp já foi usado para uma análise grátis. '
                    'Quer acesso ilimitado? Cadastre-se na lista de espera!'
                )
                # Stay on landing page, show waitlist CTA
                return render(request, 'landing/index.html', {
                    'form': form,
                    'show_waitlist': True
                })

            # Create or get WhatsAppLead
            lead, created = WhatsAppLead.objects.get_or_create(
                normalized_whatsapp=normalized,
                defaults={
                    'whatsapp': whatsapp,
                    'ip_address': get_client_ip(request),
                    'session_key': request.session.session_key or ''
                }
            )

            # Store in session for analysis page
            request.session['whatsapp_lead_id'] = lead.id
            request.session['has_free_test'] = True

            # Immediate redirect to analysis page
            messages.success(
                request,
                '✅ Análise grátis desbloqueada! Digite o produto que quer analisar.'
            )
            return redirect('market:test')

    else:
        form = WhatsAppLeadForm()

    return render(request, 'landing/index.html', {'form': form})


def confirmation(request):
    """
    Confirmation page (legacy - kept for backward compatibility).
    New flow skips this page entirely.
    """
    lead_whatsapp = request.session.get('whatsapp_lead_id', '')

    context = {
        'whatsapp': lead_whatsapp
    }

    return render(request, 'landing/confirmation.html', context)

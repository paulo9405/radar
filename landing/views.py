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

            # Check if WhatsApp already exists (any previous submission)
            existing_lead = WhatsAppLead.objects.filter(normalized_whatsapp=normalized).first()

            if existing_lead:
                # Check if already used free test
                if existing_lead.has_used_free_test:
                    messages.error(
                        request,
                        'Esse WhatsApp já utilizou a análise gratuita. Em breve liberaremos novos acessos.'
                    )
                    return render(request, 'landing/index.html', {
                        'form': WhatsAppLeadForm(initial={'whatsapp': whatsapp}),
                        'scroll_to_form': True
                    })
                else:
                    # WhatsApp exists but hasn't used test yet - allow
                    lead = existing_lead
            else:
                # Create new WhatsAppLead
                try:
                    lead = WhatsAppLead.objects.create(
                        whatsapp=whatsapp,
                        normalized_whatsapp=normalized,
                        ip_address=get_client_ip(request),
                        session_key=request.session.session_key or ''
                    )
                except Exception as e:
                    messages.error(
                        request,
                        'Esse WhatsApp já utilizou a análise gratuita. Em breve liberaremos novos acessos.'
                    )
                    return render(request, 'landing/index.html', {
                        'form': WhatsAppLeadForm(initial={'whatsapp': whatsapp}),
                        'scroll_to_form': True
                    })

            # Store in session for analysis page
            request.session['whatsapp_lead_id'] = lead.id
            request.session['has_free_test'] = True

            # Immediate redirect to analysis page
            messages.success(
                request,
                '✅ Sua análise grátis foi liberada! Digite o produto que quer analisar.'
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

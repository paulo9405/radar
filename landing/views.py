from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .forms import WhatsAppLeadForm
from .models import WhatsAppLead, IPAnalysisLimit


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


@csrf_exempt
@require_http_methods(["GET"])
def check_analysis_limit(request):
    """
    API endpoint to check if user can perform another analysis.

    Checks both IP-based limit (backend) and returns status.
    """
    try:
        ip = get_client_ip(request)
        can_analyze = IPAnalysisLimit.can_analyze(ip)

        return JsonResponse({
            'can_analyze': can_analyze,
            'limit': 2
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_contact(request):
    """
    API endpoint to capture contact when user unlocks analysis.

    Called when user submits WhatsApp/email to unlock full analysis.
    """
    try:
        data = json.loads(request.body)
        contact = data.get('contact', '').strip()
        product = data.get('product', '').strip()

        if not contact or not product:
            return JsonResponse({'error': 'Missing contact or product'}, status=400)

        # Detect if email or phone
        is_email = '@' in contact

        if is_email:
            # Email submission
            normalized = contact.lower()

            # Try to find existing lead with this email
            try:
                lead = WhatsAppLead.objects.get(email=normalized)
                created = False
                # Update existing lead
                lead.analyzed_product = product
                lead.unlocked_analysis = True
                if not lead.unlocked_at:
                    lead.unlocked_at = timezone.now()
                lead.save()
            except WhatsAppLead.DoesNotExist:
                # Create new lead
                lead = WhatsAppLead.objects.create(
                    email=normalized,
                    whatsapp='',
                    normalized_whatsapp='',
                    analyzed_product=product,
                    unlocked_analysis=True,
                    unlocked_at=timezone.now(),
                    ip_address=get_client_ip(request),
                    session_key=request.session.session_key or ''
                )
                created = True
        else:
            # Phone submission
            normalized = WhatsAppLead.normalize_whatsapp(contact)

            # Try to find existing lead with this phone
            try:
                lead = WhatsAppLead.objects.get(normalized_whatsapp=normalized)
                created = False
                # Update existing lead
                lead.whatsapp = contact  # Update formatted version
                lead.analyzed_product = product
                lead.unlocked_analysis = True
                if not lead.unlocked_at:
                    lead.unlocked_at = timezone.now()
                lead.save()
            except WhatsAppLead.DoesNotExist:
                # Create new lead
                lead = WhatsAppLead.objects.create(
                    whatsapp=contact,
                    normalized_whatsapp=normalized,
                    analyzed_product=product,
                    unlocked_analysis=True,
                    unlocked_at=timezone.now(),
                    ip_address=get_client_ip(request),
                    session_key=request.session.session_key or ''
                )
                created = True

        # Store lead ID in session for future updates
        request.session['current_lead_id'] = lead.id

        # Increment IP analysis count for rate limiting
        ip = get_client_ip(request)
        IPAnalysisLimit.increment_count(ip)

        return JsonResponse({
            'success': True,
            'lead_id': lead.id
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_feedback(request):
    """
    API endpoint to capture feedback data.

    Updates the existing lead with willingness_to_pay and launch_interest.
    """
    try:
        data = json.loads(request.body)

        # Get lead ID from session or data
        lead_id = request.session.get('current_lead_id') or data.get('lead_id')

        if not lead_id:
            return JsonResponse({'error': 'No lead found'}, status=400)

        try:
            lead = WhatsAppLead.objects.get(id=lead_id)
        except WhatsAppLead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)

        # Update feedback data
        feedback_data = data.get('feedback', {})

        if 'purchaseIntent' in feedback_data:
            lead.willingness_to_pay = feedback_data['purchaseIntent']

        if 'launchInterest' in feedback_data:
            lead.launch_interest = feedback_data['launchInterest']
            lead.joined_waitlist = feedback_data['launchInterest']

        lead.submitted_feedback = True
        lead.save()

        return JsonResponse({
            'success': True,
            'lead_id': lead.id
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

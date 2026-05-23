from django.shortcuts import render, redirect
from .forms import LeadForm


def index(request):
    """Landing page view with lead capture form"""

    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            # Store lead name in session for personalization
            request.session['lead_name'] = lead.name
            return redirect('landing:confirmation')
    else:
        form = LeadForm()

    return render(request, 'landing/index.html', {'form': form})


def confirmation(request):
    """Confirmation page after successful form submission"""

    # Get lead name from session if available
    lead_name = request.session.get('lead_name', '')

    context = {
        'lead_name': lead_name
    }

    return render(request, 'landing/confirmation.html', context)

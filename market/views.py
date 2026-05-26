from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import ProductSearch, MarketAnalysis
from .services.analyzer import analyze_product


@require_http_methods(["GET", "POST"])
def test_analysis(request):
    """
    Test page for product analysis.

    GET: Shows the search form
    POST: Processes the search and shows results
    """
    if request.method == "POST":
        # Get and validate query
        query = request.POST.get('query', '').strip()

        # Validation
        error = _validate_query(query)
        if error:
            messages.error(request, error)
            return render(request, 'market/test.html', {'query': query})

        # Get client IP (for tracking public tests)
        ip_address = _get_client_ip(request)

        # Create ProductSearch record
        product_search = ProductSearch.objects.create(
            query=query,
            source='landing',
            is_public_test=True,
            ip_address=ip_address
        )

        # Run analysis in basic mode (free)
        analysis_result = analyze_product(query, mode="basic")

        # Save MarketAnalysis record
        market_analysis = MarketAnalysis.objects.create(
            product_search=product_search,
            demand_score=analysis_result['scores']['demand'],
            competition_score=analysis_result['scores']['competition'],
            saturation_score=analysis_result['scores']['saturation'],
            price_score=analysis_result['scores']['price'],
            final_score=analysis_result['scores']['final'],
            classification=analysis_result['classification'],
            confidence_level=analysis_result['confidence_level'],
            summary=analysis_result['summary'],
            raw_data=analysis_result['raw_data']
        )

        # Pass data to template
        context = {
            'query': query,
            'analysis': analysis_result,
            'search_id': product_search.id
        }

        return render(request, 'market/result.html', context)

    # GET request - show form
    return render(request, 'market/test.html')


def _validate_query(query: str) -> str:
    """
    Validates product search query.

    Args:
        query: User input query

    Returns:
        str: Error message if invalid, empty string if valid
    """
    if not query:
        return "Por favor, digite o nome de um produto."

    if len(query) < 2:
        return "O nome do produto deve ter pelo menos 2 caracteres."

    if len(query) > 100:
        return "O nome do produto deve ter no máximo 100 caracteres."

    # Check for valid characters (allow letters, numbers, spaces, hyphens)
    if not all(c.isalnum() or c.isspace() or c in '-_.,áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ' for c in query):
        return "O nome do produto contém caracteres inválidos."

    return ""  # Valid


def _get_client_ip(request) -> str:
    """
    Gets client IP address from request.

    Handles proxy headers (X-Forwarded-For) for production environments.

    Args:
        request: Django request object

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')

    return ip

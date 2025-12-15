from apps.core.models import Country

def website_global_data(request):
    """
    Ce processeur injecte des données globales (comme les pays)
    dans tous les templates du site (header, footer, etc.)
    """
    return {
        # On récupère les pays actifs, triés par nom
        'header_countries': Country.objects.filter(is_active=True).order_by('name')
    }
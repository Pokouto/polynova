from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.decorators.http import require_POST

# Imports des modèles
from apps.profiles.models import TutorProfile
from apps.marketplace.models import CourseRequest
from apps.core.models import Country
from apps.actualites.models import Article, Category

User = get_user_model()

# ==============================================================================
# 1. AUTHENTIFICATION
# ==============================================================================

def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff: return redirect('admin_dashboard')
        else: logout(request)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Accès refusé.")

    return render(request, 'custom_admin/login.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')


# ==============================================================================
# 2. DASHBOARD GLOBAL
# ==============================================================================

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def custom_admin_dashboard(request):
    # Stats
    stats = {
        'parents_count': User.objects.filter(role='parent').count(),
        'tutors_validated': TutorProfile.objects.filter(status='validated').count(),
        'tutors_pending': TutorProfile.objects.filter(status='pending').count(),
        'active_requests': CourseRequest.objects.filter(status='active').count(),
        'articles_count': Article.objects.count(),
    }

    context = {
        'stats': stats,
        
        # Listes séparées
        'recent_parents': User.objects.filter(role='parent').order_by('-date_joined')[:50],
        'tutors_list': TutorProfile.objects.select_related('user').order_by('-created_at')[:50],
        'pending_tutors': TutorProfile.objects.filter(status='pending').select_related('user'),
        'recent_requests': CourseRequest.objects.select_related('parent').order_by('-created_at')[:20],
        
        # Blog & Catégories
        'articles': Article.objects.select_related('category', 'author').order_by('-created_at'),
        'categories': Category.objects.all(),
        
        # Config
        'active_countries': Country.objects.all().order_by('name'),
        'admin_users': User.objects.filter(is_staff=True).order_by('-is_superuser'),
        'is_superuser': request.user.is_superuser,
    }
    return render(request, 'custom_admin/dashboard.html', context)


# ==============================================================================
# 3. GESTION BLOG (Articles & Catégories)
# ==============================================================================

@require_POST
@user_passes_test(lambda u: u.is_staff)
def create_article(request):
    try:
        cat_id = request.POST.get('category')
        category = Category.objects.get(pk=cat_id) if cat_id else None
        
        Article.objects.create(
            title=request.POST.get('title'),
            category=category,
            excerpt=request.POST.get('excerpt'),
            content=request.POST.get('content'),
            image=request.FILES.get('image'),
            author=request.user,
            is_published=True
        )
        messages.success(request, "Article publié avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur : {str(e)}")
    return redirect('admin_dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def edit_article(request, article_id):
    """ Modifie l'article sans passer par l'admin Django """
    article = get_object_or_404(Article, pk=article_id)
    try:
        article.title = request.POST.get('title')
        cat_id = request.POST.get('category')
        if cat_id: article.category = Category.objects.get(pk=cat_id)
        
        article.excerpt = request.POST.get('excerpt')
        article.content = request.POST.get('content')
        
        if request.FILES.get('image'):
            article.image = request.FILES.get('image')
            
        article.save()
        messages.success(request, "Article modifié avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur modification : {str(e)}")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_staff)
def toggle_article_publish(request, article_id):
    art = get_object_or_404(Article, pk=article_id)
    art.is_published = not art.is_published
    art.save()
    status = "en ligne" if art.is_published else "brouillon"
    messages.success(request, f"Article {status}.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_article(request, article_id):
    get_object_or_404(Article, pk=article_id).delete()
    messages.success(request, "Article supprimé.")
    return redirect('admin_dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def create_category(request):
    try:
        name = request.POST.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            messages.warning(request, "Cette catégorie existe déjà.")
        else:
            Category.objects.create(name=name)
            messages.success(request, f"Catégorie '{name}' ajoutée.")
    except Exception as e:
        messages.error(request, str(e))
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_staff)
def delete_category(request, category_id):
    cat = get_object_or_404(Category, pk=category_id)
    cat.delete()
    messages.success(request, "Catégorie supprimée.")
    return redirect('admin_dashboard')


# ==============================================================================
# 4. GESTION UTILISATEURS & ADMINS
# ==============================================================================

@user_passes_test(lambda u: u.is_superuser)
def create_sub_admin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not User.objects.filter(email=email).exists():
            u = User.objects.create_user(username=email, email=email, password=request.POST.get('password'))
            u.first_name = request.POST.get('first_name')
            u.last_name = request.POST.get('last_name')
            u.role = 'admin'
            u.is_staff = True
            u.save()
            messages.success(request, "Admin créé.")
    return redirect('admin_dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def update_user_status(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    action = request.POST.get('action')
    if action == 'delete' and not u.is_superuser:
        u.delete()
        messages.success(request, "Utilisateur supprimé.")
    elif action == 'toggle_active':
        u.is_active = not u.is_active
        u.save()
        messages.success(request, "Statut mis à jour.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    if not u.is_superuser: u.delete()
    messages.success(request, "Utilisateur supprimé.")
    return redirect('admin_dashboard')


# ==============================================================================
# 5. GESTION PAYS & MÉTIER
# ==============================================================================

@require_POST
@user_passes_test(lambda u: u.is_staff)
def add_country(request):
    Country.objects.create(
        name=request.POST.get('name'), code=request.POST.get('code'),
        currency_symbol=request.POST.get('currency'), is_active=True
    )
    messages.success(request, "Pays ajouté.")
    return redirect('admin_dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def update_country_config(request, country_id):
    c = get_object_or_404(Country, pk=country_id)
    c.subscription_price = int(request.POST.get('subscription_price'))
    c.min_budget_threshold = int(request.POST.get('min_budget_threshold'))
    c.contact_prices = request.POST.get('contact_prices')
    c.casier_delay_weeks = int(request.POST.get('casier_delay_weeks'))
    c.save()
    messages.success(request, "Config mise à jour.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_staff)
def toggle_country(request, country_id):
    c = get_object_or_404(Country, pk=country_id)
    c.is_active = not c.is_active
    c.save()
    messages.success(request, "Statut Pays changé.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_country(request, country_id):
    get_object_or_404(Country, pk=country_id).delete()
    messages.success(request, "Pays supprimé.")
    return redirect('admin_dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def validate_tutor(request, profile_id):
    p = get_object_or_404(TutorProfile, pk=profile_id)
    if request.POST.get('action') == 'validate':
        p.status = 'validated'
        messages.success(request, "Professeur validé.")
    else:
        p.status = 'rejected'
        p.admin_notes = request.POST.get('admin_notes', '')
        messages.warning(request, "Professeur rejeté.")
    p.save()
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_request(request, request_id):
    get_object_or_404(CourseRequest, pk=request_id).delete()
    messages.success(request, "Demande supprimée.")
    return redirect('admin_dashboard')
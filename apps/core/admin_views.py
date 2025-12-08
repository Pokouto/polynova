from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.decorators.http import require_POST

from apps.profiles.models import TutorProfile
from apps.marketplace.models import CourseRequest
from apps.core.models import Country, City

User = get_user_model()

# ==============================================================================
# 1. AUTHENTIFICATION ADMIN
# ==============================================================================

def admin_login_view(request):
    """ Page de connexion spécifique pour le Panel Admin. """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            logout(request) # Déconnexion forcée si non-admin

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Accès refusé. Compte non autorisé.")
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, 'custom_admin/login.html')

def admin_logout(request):
    """ Déconnexion et retour vers le login admin """
    logout(request)
    return redirect('admin_login')


# ==============================================================================
# 2. TABLEAU DE BORD (DASHBOARD)
# ==============================================================================

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def custom_admin_dashboard(request):
    # Statistiques
    stats = {
        'parents_count': User.objects.filter(role='parent').count(),
        'tutors_validated': TutorProfile.objects.filter(status='validated').count(),
        'tutors_pending': TutorProfile.objects.filter(status='pending').count(),
        'active_requests': CourseRequest.objects.filter(status='active').count(),
    }

    # Listes (avec select_related pour optimiser la base de données)
    recent_parents = User.objects.filter(role='parent').order_by('-date_joined')[:50]
    tutors_list = TutorProfile.objects.select_related('user').order_by('-created_at')[:50]
    pending_tutors = TutorProfile.objects.filter(status='pending').select_related('user')
    recent_requests = CourseRequest.objects.select_related('parent').order_by('-created_at')[:20]
    
    active_countries = Country.objects.all().order_by('name')
    admin_users = User.objects.filter(is_staff=True).order_by('-is_superuser')

    context = {
        'stats': stats,
        'recent_parents': recent_parents,
        'tutors_list': tutors_list,
        'pending_tutors': pending_tutors,
        'recent_requests': recent_requests,
        'active_countries': active_countries,
        'admin_users': admin_users,
        'is_superuser': request.user.is_superuser,
    }
    return render(request, 'custom_admin/dashboard.html', context)


# ==============================================================================
# 3. GESTION UTILISATEURS (Admins, Parents, Profs)
# ==============================================================================

@user_passes_test(lambda u: u.is_superuser)
def create_sub_admin(request):
    """ Créer un sous-administrateur avec des permissions spécifiques """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        can_validate = request.POST.get('perm_validation') == 'on'
        can_manage_users = request.POST.get('perm_users') == 'on'

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email existe déjà.")
            return redirect('admin_dashboard')

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = False
        user.save()

        # Attribution des permissions Django
        if can_validate:
            ct = ContentType.objects.get_for_model(TutorProfile)
            perm = Permission.objects.get(codename='change_tutorprofile', content_type=ct)
            user.user_permissions.add(perm)
        
        if can_manage_users:
            ct = ContentType.objects.get_for_model(User)
            perms = Permission.objects.filter(content_type=ct, codename__in=['change_customuser', 'delete_customuser'])
            for p in perms: user.user_permissions.add(p)

        messages.success(request, "Sous-admin créé avec succès !")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    """ Supprime n'importe quel utilisateur (C'est cette fonction qui manquait !) """
    u = get_object_or_404(User, pk=user_id)
    
    if u.is_superuser:
        messages.error(request, "Impossible de supprimer un Super Administrateur.")
    elif u == request.user:
        messages.error(request, "Vous ne pouvez pas vous supprimer vous-même.")
    else:
        u.delete()
        messages.success(request, "Utilisateur supprimé définitivement.")
        
    return redirect('admin_dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def update_user_status(request, user_id):
    """ Bloquer / Débloquer ou Supprimer via formulaire """
    u = get_object_or_404(User, pk=user_id)
    action = request.POST.get('action')
    
    if action == 'delete':
        if u.is_superuser or u == request.user:
            messages.error(request, "Action impossible sur cet utilisateur.")
        else:
            u.delete()
            messages.success(request, "Utilisateur supprimé.")
    elif action == 'toggle_active':
        u.is_active = not u.is_active
        u.save()
        status = "activé" if u.is_active else "désactivé"
        messages.success(request, f"Compte de {u.username} {status}.")
        
    return redirect('admin_dashboard')


# ==============================================================================
# 4. GESTION PAYS & CONFIGURATION
# ==============================================================================

@require_POST
@user_passes_test(lambda u: u.is_staff)
def add_country(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        currency = request.POST.get('currency')
        
        if Country.objects.filter(code=code).exists():
            messages.error(request, "Ce code pays existe déjà.")
        else:
            Country.objects.create(name=name, code=code.upper(), currency_symbol=currency, is_active=True)
            messages.success(request, f"Pays {name} ajouté !")
            
    return redirect('admin_dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def update_country_config(request, country_id):
    country = get_object_or_404(Country, pk=country_id)
    try:
        country.subscription_price = int(request.POST.get('subscription_price'))
        country.min_budget_threshold = int(request.POST.get('min_budget_threshold'))
        country.contact_prices = request.POST.get('contact_prices')
        country.casier_delay_weeks = int(request.POST.get('casier_delay_weeks'))
        country.save()
        messages.success(request, f"Config {country.name} mise à jour.")
    except ValueError:
        messages.error(request, "Erreur de format dans les chiffres.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_staff)
def toggle_country(request, country_id):
    country = get_object_or_404(Country, pk=country_id)
    country.is_active = not country.is_active
    country.save()
    status = "activé" if country.is_active else "désactivé"
    messages.success(request, f"Pays {country.name} {status}.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_country(request, country_id):
    country = get_object_or_404(Country, pk=country_id)
    country.delete()
    messages.success(request, "Pays supprimé.")
    return redirect('admin_dashboard')


# ==============================================================================
# 5. VALIDATION PROFESSEURS
# ==============================================================================

@require_POST
@user_passes_test(lambda u: u.is_staff)
def validate_tutor(request, profile_id):
    profile = get_object_or_404(TutorProfile, pk=profile_id)
    action = request.POST.get('action')
    
    if action == 'validate':
        profile.status = 'validated'
        messages.success(request, f"Professeur {profile.user.username} validé.")
    elif action == 'reject':
        profile.status = 'rejected'
        profile.admin_notes = request.POST.get('admin_notes', '')
        messages.warning(request, f"Professeur {profile.user.username} rejeté.")
    
    profile.save()
    return redirect('admin_dashboard')


# ==============================================================================
# 6. GESTION DEMANDES
# ==============================================================================

@user_passes_test(lambda u: u.is_superuser)
def delete_request(request, request_id):
    req = get_object_or_404(CourseRequest, pk=request_id)
    req.delete()
    messages.success(request, "Demande supprimée avec succès.")
    return redirect('admin_dashboard')
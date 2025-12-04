from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model, authenticate, login, logout

from apps.profiles.models import TutorProfile
from apps.marketplace.models import CourseRequest
from apps.core.models import Country, City

User = get_user_model()

# --- 1. AUTHENTIFICATION ADMIN ---

def admin_login_view(request):
    """
    Page de connexion spécifique pour le Panel Admin.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            # Si un parent essaie d'aller ici, on le déconnecte
            logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        passw = request.POST.get('password')
        user = authenticate(request, username=username, password=passw)
        
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
    """Déconnexion et retour vers le login admin"""
    logout(request)
    return redirect('admin_login')


# --- 2. TABLEAU DE BORD (DASHBOARD) ---

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

    # Listes pour les tableaux
    recent_parents = User.objects.filter(role='parent').order_by('-date_joined')[:50]
    tutors_list = TutorProfile.objects.select_related('user').order_by('-created_at')[:50]
    pending_tutors = TutorProfile.objects.filter(status='pending').select_related('user')
    recent_requests = CourseRequest.objects.select_related('parent').order_by('-created_at')[:20]
    
    # Géographie (Pays)
    active_countries = Country.objects.all().order_by('name')

    # Admins
    admin_users = User.objects.filter(is_staff=True).order_by('-is_superuser', 'date_joined')

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


# --- 3. GESTION UTILISATEURS (Création Admin / Suppression) ---

@user_passes_test(lambda u: u.is_superuser)
def create_sub_admin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Permissions
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

        # Attribution des droits spécifiques
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
    """ Supprime n'importe quel utilisateur (sauf soi-même ou un autre superuser) """
    u = get_object_or_404(User, pk=user_id)
    
    if u.is_superuser:
        messages.error(request, "Impossible de supprimer un Super Administrateur.")
    elif u == request.user:
        messages.error(request, "Vous ne pouvez pas vous supprimer vous-même.")
    else:
        u.delete()
        messages.success(request, "Utilisateur supprimé définitivement.")
        
    return redirect('admin_dashboard')


# --- 4. GESTION PAYS ---

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
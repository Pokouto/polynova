from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model, authenticate, login, logout

from apps.profiles.models import TutorProfile
from apps.marketplace.models import CourseRequest # Import important
from apps.core.models import Country, City

User = get_user_model()

# --- 1. AUTHENTIFICATION ---
def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff: return redirect('admin_dashboard')
        else: logout(request)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Accès refusé.")
    return render(request, 'custom_admin/login.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# --- 2. DASHBOARD ---
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def custom_admin_dashboard(request):
    
    # Stats
    stats = {
        'parents_count': User.objects.filter(role='parent').count(),
        'tutors_validated': TutorProfile.objects.filter(status='validated').count(),
        'tutors_pending': TutorProfile.objects.filter(status='pending').count(),
        'active_requests': CourseRequest.objects.filter(status='active').count(),
    }

    # Listes
    recent_parents = User.objects.filter(role='parent').order_by('-date_joined')[:50]
    tutors_list = TutorProfile.objects.select_related('user').order_by('-created_at')[:50]
    pending_tutors = TutorProfile.objects.filter(status='pending').select_related('user')
    
    # --- AJOUT : LISTE DES DEMANDES ---
    requests_list = CourseRequest.objects.select_related('parent', 'level', 'city').prefetch_related('subjects').order_by('-created_at')[:50]
    
    active_countries = Country.objects.all().order_by('name')
    admin_users = User.objects.filter(is_staff=True).order_by('-is_superuser')

    context = {
        'stats': stats,
        'recent_parents': recent_parents,
        'tutors_list': tutors_list,
        'pending_tutors': pending_tutors,
        'requests_list': requests_list, # La liste envoyée au template
        'active_countries': active_countries,
        'admin_users': admin_users,
        'is_superuser': request.user.is_superuser,
    }
    return render(request, 'custom_admin/dashboard.html', context)

# --- 3. ACTIONS (Suppression, Ajout) ---

@user_passes_test(lambda u: u.is_superuser)
def delete_request(request, request_id):
    """ Supprimer une demande de cours """
    req = get_object_or_404(CourseRequest, pk=request_id)
    req.delete()
    messages.success(request, "Demande supprimée avec succès.")
    return redirect('admin_dashboard')

# ... (Garde les autres fonctions : create_sub_admin, delete_user, add_country, toggle_country, delete_country inchangées) ...
@user_passes_test(lambda u: u.is_superuser)
def create_sub_admin(request):
    # (Code précédent pour créer admin...)
    if request.method == 'POST':
        # ... logique création ...
        messages.success(request, "Sous-admin créé.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    if not u.is_superuser and u != request.user:
        u.delete()
        messages.success(request, "Utilisateur supprimé.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_staff)
def add_country(request):
    if request.method == 'POST':
        # ... logique ajout pays ...
        pass
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_staff)
def toggle_country(request, country_id):
    c = get_object_or_404(Country, pk=country_id)
    c.is_active = not c.is_active
    c.save()
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_country(request, country_id):
    c = get_object_or_404(Country, pk=country_id)
    c.delete()
    return redirect('admin_dashboard')
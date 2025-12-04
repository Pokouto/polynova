from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Imports des Modèles
from .models import TutorProfile, ParentProfile
from apps.marketplace.models import CourseRequest

# Imports des Formulaires
from apps.accounts.forms import UserUpdateForm
from .forms import TutorUpdateForm, ParentUpdateForm

@login_required
def dashboard(request):
    """
    Vue principale du Tableau de Bord (Dashboard).
    Redirige vers le bon template selon le rôle de l'utilisateur.
    """
    user = request.user

    # --- CAS 0 : C'est un Administrateur (Super ou Sous-Admin) ---
    # Si l'utilisateur a accès au staff, on l'envoie vers le Panel Admin dédié
    if user.is_staff or user.is_superuser:
        return redirect('admin_dashboard')

    # --- CAS 1 : C'est un Professeur ---
    if user.role == 'tutor':
        # On récupère ou crée le profil (blindage contre les erreurs)
        try:
            profile = user.tutor_profile
        except TutorProfile.DoesNotExist:
            profile = TutorProfile.objects.create(user=user)

        if request.method == 'POST':
            # On charge les DEUX formulaires avec les données envoyées
            u_form = UserUpdateForm(request.POST, instance=user)
            p_form = TutorUpdateForm(request.POST, request.FILES, instance=profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save() # Sauvegarde Nom, Email, Tél
                
                profile_obj = p_form.save(commit=False)
                # Gestion du statut : si brouillon, on passe en attente de validation
                if profile_obj.status == 'draft':
                    profile_obj.status = 'pending'
                profile_obj.save()
                
                p_form.save_m2m() # Important pour les relations ManyToMany (Matières/Niveaux)
                
                messages.success(request, "Votre profil a été mis à jour avec succès !")
                return redirect('dashboard')
        else:
            # On charge les formulaires avec les données existantes
            u_form = UserUpdateForm(instance=user)
            p_form = TutorUpdateForm(instance=profile)

        context = {
            'u_form': u_form, # Formulaire User (Nom/Prénom/Tél)
            'p_form': p_form, # Formulaire Profil (Bio/Docs/Matières)
            'profile': profile
        }
        return render(request, 'profiles/dashboard_tutor.html', context)

    # --- CAS 2 : C'est un Parent ---
    elif user.role == 'parent':
        try:
            profile = user.parent_profile
        except ParentProfile.DoesNotExist:
            profile = ParentProfile.objects.create(user=user)

        # Récupération de l'historique des demandes (du plus récent au plus ancien)
        my_requests = CourseRequest.objects.filter(parent=user).order_by('-created_at')

        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=user)
            p_form = ParentUpdateForm(request.POST, instance=profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, "Vos informations ont été modifiées.")
                return redirect('dashboard')
        else:
            u_form = UserUpdateForm(instance=user)
            p_form = ParentUpdateForm(instance=profile)

        context = {
            'u_form': u_form,
            'p_form': p_form,
            'profile': profile,
            'my_requests': my_requests, # Liste des demandes pour l'historique
        }
        return render(request, 'profiles/dashboard_parent.html', context)

    # --- CAS 3 : Rôle inconnu ---
    return redirect('home')
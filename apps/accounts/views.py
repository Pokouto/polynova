from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    """
    Inscription des Parents et Enseignants (Public).
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Votre compte a été créé.")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def public_login_view(request):
    """
    Connexion PUBLIQUE (Parents & Profs uniquement).
    Interdit l'accès aux Administrateurs ici.
    """
    if request.user.is_authenticated:
        # Si c'est un admin déjà connecté, on le renvoie chez lui
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # --- SÉCURITÉ : FILTRE ANTI-ADMIN ---
            if user.is_staff or user.is_superuser:
                messages.error(request, "Ceci est l'espace public. Veuillez utiliser le portail Administration.")
                # On ne connecte PAS l'utilisateur
            else:
                # C'est un Parent ou un Prof -> OK
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})
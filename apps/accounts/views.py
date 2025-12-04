from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def register(request):
    """
    Page d'inscription.
    Si le formulaire est valide, on crée l'utilisateur et on le connecte directement.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Connexion automatique après inscription
            return redirect('home') # Retour à l'accueil
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})
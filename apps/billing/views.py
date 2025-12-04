from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.profiles.models import TutorProfile
from .models import ContactUnlock

@login_required
def fake_payment(request, tutor_id):
    """
    SIMULATION : Débloque le contact immédiatement sans payer.
    À remplacer plus tard par l'API CinetPay/Stripe.
    """
    if request.method == 'POST':
        tutor = get_object_or_404(TutorProfile, pk=tutor_id)
        
        # On vérifie si c'est déjà débloqué pour éviter les doublons
        if not ContactUnlock.objects.filter(parent_user=request.user, tutor_profile=tutor).exists():
            ContactUnlock.objects.create(
                parent_user=request.user,
                tutor_profile=tutor,
                amount_paid=2000 # Prix fixe pour le test
            )
            messages.success(request, f"Paiement accepté ! Voici les coordonnées de {tutor.user.username}.")
        
        # On renvoie vers la page du prof (où le numéro sera maintenant visible)
        return redirect('tutor_detail', pk=tutor_id)
    
    # Si on essaie d'accéder sans POST, on renvoie à l'accueil
    return redirect('home')